from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import cupy as cp


ROOT = Path(__file__).resolve().parents[2]
CPU_DIR = ROOT / "tests" / "cpu"
if str(CPU_DIR) not in sys.path:
    sys.path.insert(0, str(CPU_DIR))

from qng_native_update_reference import (  # noqa: E402
    Config,
    build_graph,
    init_state,
    run_rollout,
)


DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-cpu-gpu-agreement-v1"


def wrap_angle_gpu(x: cp.ndarray) -> cp.ndarray:
    y = (x + math.pi) % (2.0 * math.pi) - math.pi
    return cp.where(y <= -math.pi, y + 2.0 * math.pi, y)


def angle_diff_gpu(a: cp.ndarray, b: cp.ndarray) -> cp.ndarray:
    return wrap_angle_gpu(a - b)


def clip01_gpu(x: cp.ndarray) -> cp.ndarray:
    return cp.clip(x, 0.0, 1.0)


def build_adj_matrix(adj: list[list[int]]) -> tuple[cp.ndarray, cp.ndarray]:
    n_nodes = len(adj)
    mat = cp.zeros((n_nodes, n_nodes), dtype=cp.float64)
    for i, neigh in enumerate(adj):
        if neigh:
            mat[i, cp.asarray(neigh, dtype=cp.int32)] = 1.0
    degree = mat.sum(axis=1)
    return mat, degree


def init_gpu_state(cfg: Config) -> tuple[cp.ndarray, cp.ndarray, cp.ndarray, cp.ndarray, cp.ndarray, cp.ndarray, cp.ndarray, cp.ndarray]:
    import random

    rng = random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)
    adj_mat, degree = build_adj_matrix(adj)

    sigma = cp.asarray(state.sigma, dtype=cp.float64)
    chi = cp.asarray(state.chi, dtype=cp.float64)
    phi = cp.asarray(state.phi, dtype=cp.float64)
    mem = cp.asarray(history.mem, dtype=cp.float64)
    mismatch = cp.asarray(history.mismatch, dtype=cp.float64)
    phase = cp.asarray(history.phase, dtype=cp.float64)
    return sigma, chi, phi, mem, mismatch, phase, adj_mat, degree


def circular_mean_gpu(phi: cp.ndarray, adj_mat: cp.ndarray, degree: cp.ndarray) -> cp.ndarray:
    sin_mean = (adj_mat @ cp.sin(phi)) / cp.maximum(degree, 1.0)
    cos_mean = (adj_mat @ cp.cos(phi)) / cp.maximum(degree, 1.0)
    raw = cp.arctan2(sin_mean, cos_mean)
    fallback = phi
    zero_mask = (cp.abs(sin_mean) < 1e-12) & (cp.abs(cos_mean) < 1e-12)
    return cp.where(zero_mask, fallback, raw)


def neighbor_mean_gpu(values: cp.ndarray, adj_mat: cp.ndarray, degree: cp.ndarray, fallback: cp.ndarray) -> cp.ndarray:
    mean = (adj_mat @ values) / cp.maximum(degree, 1.0)
    return cp.where(degree > 0.0, mean, fallback)


def one_step_gpu(
    sigma: cp.ndarray,
    chi: cp.ndarray,
    phi: cp.ndarray,
    mem: cp.ndarray,
    mismatch: cp.ndarray,
    phase: cp.ndarray,
    adj_mat: cp.ndarray,
    degree: cp.ndarray,
    cfg: Config,
    use_history: bool,
) -> tuple[cp.ndarray, cp.ndarray, cp.ndarray, cp.ndarray, cp.ndarray, cp.ndarray]:
    sigma_neigh = neighbor_mean_gpu(sigma, adj_mat, degree, sigma)
    chi_neigh = neighbor_mean_gpu(chi, adj_mat, degree, chi)
    phi_neigh = circular_mean_gpu(phi, adj_mat, degree)

    hist_drive = cp.zeros_like(mem)
    if use_history:
        hist_drive = mem - mismatch + 0.25 * cp.cos(phase)

    sigma_new = clip01_gpu(
        sigma
        + cfg.sigma_self_gain * (0.5 - sigma)
        + cfg.sigma_rel_gain * (sigma_neigh - sigma)
        + cfg.sigma_hist_gain * hist_drive
    )
    chi_new = (
        chi
        - cfg.chi_decay * chi
        + cfg.chi_rel_gain * (sigma_neigh - sigma)
        + (cfg.chi_hist_gain * hist_drive if use_history else 0.0)
    )
    phi_new = wrap_angle_gpu(
        phi
        + cfg.phi_rel_gain * angle_diff_gpu(phi_neigh, phi)
        + (cfg.phi_hist_gain * phase if use_history else 0.0)
    )

    mem_new = clip01_gpu((1.0 - cfg.hist_m_rate) * mem + cfg.hist_m_rate * cp.abs(chi_new - chi_neigh))
    mismatch_new = clip01_gpu(
        (1.0 - cfg.hist_d_rate) * mismatch + cfg.hist_d_rate * cp.abs(sigma_new - sigma_neigh)
    )
    phase_new = wrap_angle_gpu(
        (1.0 - cfg.hist_p_rate) * phase + cfg.hist_p_rate * angle_diff_gpu(phi_new, phi_neigh)
    )
    return sigma_new, chi_new, phi_new, mem_new, mismatch_new, phase_new


def rollout_gpu(cfg: Config, use_history: bool) -> dict[str, cp.ndarray]:
    sigma, chi, phi, mem, mismatch, phase, adj_mat, degree = init_gpu_state(cfg)
    for _ in range(cfg.steps):
        sigma, chi, phi, mem, mismatch, phase = one_step_gpu(
            sigma, chi, phi, mem, mismatch, phase, adj_mat, degree, cfg, use_history
        )
    return {
        "sigma": sigma,
        "chi": chi,
        "phi": phi,
        "mem": mem,
        "mismatch": mismatch,
        "phase": phase,
    }


def max_abs_diff(a: cp.ndarray, b: list[float]) -> float:
    return float(cp.max(cp.abs(a - cp.asarray(b, dtype=cp.float64))).item())


def max_angle_diff(a: cp.ndarray, b: list[float]) -> float:
    return float(cp.max(cp.abs(angle_diff_gpu(a, cp.asarray(b, dtype=cp.float64)))).item())


def compare_rollout(cfg: Config, use_history: bool) -> dict:
    _, cpu_state, cpu_history, _ = run_rollout(cfg, use_history=use_history)
    gpu = rollout_gpu(cfg, use_history=use_history)

    result = {
        "use_history": use_history,
        "sigma_max_abs_diff": max_abs_diff(gpu["sigma"], cpu_state.sigma),
        "chi_max_abs_diff": max_abs_diff(gpu["chi"], cpu_state.chi),
        "phi_max_abs_diff": max_angle_diff(gpu["phi"], cpu_state.phi),
        "mem_max_abs_diff": max_abs_diff(gpu["mem"], cpu_history.mem),
        "mismatch_max_abs_diff": max_abs_diff(gpu["mismatch"], cpu_history.mismatch),
        "phase_max_abs_diff": max_angle_diff(gpu["phase"], cpu_history.phase),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG CPU/GPU agreement test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--tol", type=float, default=1e-9)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    hist = compare_rollout(cfg, use_history=True)
    nohist = compare_rollout(cfg, use_history=False)

    max_diff = max(
        hist["sigma_max_abs_diff"],
        hist["chi_max_abs_diff"],
        hist["phi_max_abs_diff"],
        hist["mem_max_abs_diff"],
        hist["mismatch_max_abs_diff"],
        hist["phase_max_abs_diff"],
        nohist["sigma_max_abs_diff"],
        nohist["chi_max_abs_diff"],
        nohist["phi_max_abs_diff"],
        nohist["mem_max_abs_diff"],
        nohist["mismatch_max_abs_diff"],
        nohist["phase_max_abs_diff"],
    )
    decision = max_diff <= args.tol

    report = {
        "test_id": "QNG-CPUGPU-002",
        "decision": "pass" if decision else "fail",
        "tolerance": args.tol,
        "history_enabled": hist,
        "history_disabled": nohist,
        "max_diff": max_diff,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG CPU/GPU Agreement v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- tolerance: `{args.tol}`",
        f"- max_diff: `{max_diff:.12e}`",
        f"- history_enabled_sigma_max_abs_diff: `{hist['sigma_max_abs_diff']:.12e}`",
        f"- history_enabled_chi_max_abs_diff: `{hist['chi_max_abs_diff']:.12e}`",
        f"- history_enabled_phi_max_abs_diff: `{hist['phi_max_abs_diff']:.12e}`",
        f"- history_disabled_sigma_max_abs_diff: `{nohist['sigma_max_abs_diff']:.12e}`",
        f"- history_disabled_chi_max_abs_diff: `{nohist['chi_max_abs_diff']:.12e}`",
        f"- history_disabled_phi_max_abs_diff: `{nohist['phi_max_abs_diff']:.12e}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_cpu_gpu_agreement: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
