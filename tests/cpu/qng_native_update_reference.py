from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-native-update-reference-v1"


@dataclass(frozen=True)
class Config:
    n_nodes: int = 16
    steps: int = 24
    seed: int = 20260325
    sigma_self_gain: float = 0.08
    sigma_rel_gain: float = 0.18
    sigma_hist_gain: float = 0.12
    chi_decay: float = 0.10
    chi_rel_gain: float = 0.14
    chi_hist_gain: float = 0.08
    phi_rel_gain: float = 0.22
    phi_hist_gain: float = 0.10
    hist_m_rate: float = 0.30
    hist_d_rate: float = 0.25
    hist_p_rate: float = 0.35


@dataclass
class State:
    sigma: list[float]
    chi: list[float]
    phi: list[float]


@dataclass
class History:
    mem: list[float]
    mismatch: list[float]
    phase: list[float]


def clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def wrap_angle(x: float) -> float:
    y = (x + math.pi) % (2.0 * math.pi) - math.pi
    if y <= -math.pi:
        return y + 2.0 * math.pi
    return y


def angle_diff(a: float, b: float) -> float:
    return wrap_angle(a - b)


def mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def neigh_mean(values: list[float], neighbors: list[int], fallback: float) -> float:
    if not neighbors:
        return fallback
    return sum(values[j] for j in neighbors) / len(neighbors)


def circular_mean(values: list[float], neighbors: list[int], fallback: float) -> float:
    if not neighbors:
        return fallback
    s = sum(math.sin(values[j]) for j in neighbors)
    c = sum(math.cos(values[j]) for j in neighbors)
    if abs(s) < 1e-12 and abs(c) < 1e-12:
        return fallback
    return math.atan2(s, c)


def build_graph(n_nodes: int, rng: random.Random) -> list[list[int]]:
    adj = [set() for _ in range(n_nodes)]
    for i in range(n_nodes):
        j = (i + 1) % n_nodes
        adj[i].add(j)
        adj[j].add(i)
    for i in range(n_nodes):
        for j in range(i + 2, n_nodes):
            if rng.random() < 0.18:
                adj[i].add(j)
                adj[j].add(i)
    return [sorted(v) for v in adj]


def init_state(n_nodes: int, rng: random.Random) -> tuple[State, History]:
    sigma = [clip01(0.45 + 0.25 * rng.uniform(-1.0, 1.0)) for _ in range(n_nodes)]
    chi = [0.4 * rng.uniform(-1.0, 1.0) for _ in range(n_nodes)]
    phi = [rng.uniform(-math.pi, math.pi) for _ in range(n_nodes)]
    mem = [0.10 * rng.random() for _ in range(n_nodes)]
    mismatch = [0.10 * rng.random() for _ in range(n_nodes)]
    phase = [rng.uniform(-0.3, 0.3) for _ in range(n_nodes)]
    return State(sigma, chi, phi), History(mem, mismatch, phase)


def clone_state(state: State) -> State:
    return State(state.sigma[:], state.chi[:], state.phi[:])


def clone_history(history: History) -> History:
    return History(history.mem[:], history.mismatch[:], history.phase[:])


def one_step(state: State, history: History, adj: list[list[int]], cfg: Config, use_history: bool) -> tuple[State, History]:
    next_sigma: list[float] = []
    next_chi: list[float] = []
    next_phi: list[float] = []
    next_mem: list[float] = []
    next_mismatch: list[float] = []
    next_phase: list[float] = []

    for i, neighbors in enumerate(adj):
        sigma_i = state.sigma[i]
        chi_i = state.chi[i]
        phi_i = state.phi[i]

        sigma_neigh = neigh_mean(state.sigma, neighbors, sigma_i)
        chi_neigh = neigh_mean(state.chi, neighbors, chi_i)
        phi_neigh = circular_mean(state.phi, neighbors, phi_i)

        hist_drive = 0.0
        if use_history:
            hist_drive = history.mem[i] - history.mismatch[i] + 0.25 * math.cos(history.phase[i])

        sigma_raw = (
            sigma_i
            + cfg.sigma_self_gain * (0.5 - sigma_i)
            + cfg.sigma_rel_gain * (sigma_neigh - sigma_i)
            + cfg.sigma_hist_gain * hist_drive
        )
        sigma_new = clip01(sigma_raw)

        chi_new = (
            chi_i
            - cfg.chi_decay * chi_i
            + cfg.chi_rel_gain * (sigma_neigh - sigma_i)
            + (cfg.chi_hist_gain * hist_drive if use_history else 0.0)
        )

        phi_new = wrap_angle(
            phi_i
            + cfg.phi_rel_gain * angle_diff(phi_neigh, phi_i)
            + (cfg.phi_hist_gain * history.phase[i] if use_history else 0.0)
        )

        mem_new = clip01((1.0 - cfg.hist_m_rate) * history.mem[i] + cfg.hist_m_rate * abs(chi_new - chi_neigh))
        mismatch_new = clip01(
            (1.0 - cfg.hist_d_rate) * history.mismatch[i] + cfg.hist_d_rate * abs(sigma_new - sigma_neigh)
        )
        phase_new = wrap_angle(
            (1.0 - cfg.hist_p_rate) * history.phase[i] + cfg.hist_p_rate * angle_diff(phi_new, phi_neigh)
        )

        next_sigma.append(sigma_new)
        next_chi.append(chi_new)
        next_phi.append(phi_new)
        next_mem.append(mem_new)
        next_mismatch.append(mismatch_new)
        next_phase.append(phase_new)

    return State(next_sigma, next_chi, next_phi), History(next_mem, next_mismatch, next_phase)


def run_rollout(cfg: Config, use_history: bool) -> tuple[dict, State, History, list[list[int]]]:
    rng = random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)

    sigma_min = min(state.sigma)
    sigma_max = max(state.sigma)
    max_abs_phi = max(abs(v) for v in state.phi)
    max_hist_mem = max(history.mem)
    max_hist_mismatch = max(history.mismatch)

    for _ in range(cfg.steps):
        state, history = one_step(state, history, adj, cfg, use_history=use_history)
        sigma_min = min(sigma_min, min(state.sigma))
        sigma_max = max(sigma_max, max(state.sigma))
        max_abs_phi = max(max_abs_phi, max(abs(v) for v in state.phi))
        max_hist_mem = max(max_hist_mem, max(history.mem))
        max_hist_mismatch = max(max_hist_mismatch, max(history.mismatch))

    metrics = {
        "sigma_min": sigma_min,
        "sigma_max": sigma_max,
        "max_abs_phi": max_abs_phi,
        "max_hist_mem": max_hist_mem,
        "max_hist_mismatch": max_hist_mismatch,
        "mean_final_sigma": mean(state.sigma),
        "mean_final_abs_chi": mean([abs(v) for v in state.chi]),
    }
    return metrics, state, history, adj


def locality_test(cfg: Config) -> dict:
    rng = random.Random(cfg.seed + 99)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)
    pert_state = clone_state(state)
    pert_hist = clone_history(history)

    source = 3
    pert_state.sigma[source] = clip01(pert_state.sigma[source] + 0.2)
    pert_state.chi[source] += 0.1
    pert_hist.mem[source] = clip01(pert_hist.mem[source] + 0.15)

    base_next, _ = one_step(state, history, adj, cfg, use_history=True)
    pert_next, _ = one_step(pert_state, pert_hist, adj, cfg, use_history=True)

    changed = []
    for i in range(cfg.n_nodes):
        delta = (
            abs(base_next.sigma[i] - pert_next.sigma[i])
            + abs(base_next.chi[i] - pert_next.chi[i])
            + abs(angle_diff(base_next.phi[i], pert_next.phi[i]))
        )
        if delta > 1e-10:
            changed.append(i)

    allowed = sorted({source, *adj[source]})
    passed = set(changed).issubset(set(allowed))
    return {
        "source_node": source,
        "changed_nodes": changed,
        "allowed_nodes": allowed,
        "locality_pass": passed,
    }


def memory_sensitivity_test(cfg: Config) -> dict:
    hist_metrics, hist_state, _, _ = run_rollout(cfg, use_history=True)
    nohist_metrics, nohist_state, _, _ = run_rollout(cfg, use_history=False)

    sigma_l1 = sum(abs(a - b) for a, b in zip(hist_state.sigma, nohist_state.sigma))
    chi_l1 = sum(abs(a - b) for a, b in zip(hist_state.chi, nohist_state.chi))
    phi_l1 = sum(abs(angle_diff(a, b)) for a, b in zip(hist_state.phi, nohist_state.phi))

    passed = sigma_l1 + chi_l1 + phi_l1 > 0.10
    return {
        "sigma_l1": sigma_l1,
        "chi_l1": chi_l1,
        "phi_l1": phi_l1,
        "memory_sensitivity_pass": passed,
        "history_mean_final_sigma": hist_metrics["mean_final_sigma"],
        "present_only_mean_final_sigma": nohist_metrics["mean_final_sigma"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG native update reference CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    cfg = Config()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rollout_metrics, _, _, _ = run_rollout(cfg, use_history=True)
    locality = locality_test(cfg)
    memory = memory_sensitivity_test(cfg)

    checks = {
        "sigma_bounds_pass": 0.0 <= rollout_metrics["sigma_min"] <= rollout_metrics["sigma_max"] <= 1.0,
        "phi_bounds_pass": rollout_metrics["max_abs_phi"] <= math.pi + 1e-12,
        "history_bounds_pass": rollout_metrics["max_hist_mem"] <= 1.0 and rollout_metrics["max_hist_mismatch"] <= 1.0,
        "locality_pass": locality["locality_pass"],
        "memory_sensitivity_pass": memory["memory_sensitivity_pass"],
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-002",
        "decision": "pass" if decision else "fail",
        "config": cfg.__dict__,
        "rollout_metrics": rollout_metrics,
        "locality": locality,
        "memory": memory,
        "checks": checks,
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Native Update Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- sigma_bounds_pass: `{checks['sigma_bounds_pass']}`",
        f"- phi_bounds_pass: `{checks['phi_bounds_pass']}`",
        f"- history_bounds_pass: `{checks['history_bounds_pass']}`",
        f"- locality_pass: `{checks['locality_pass']}`",
        f"- memory_sensitivity_pass: `{checks['memory_sensitivity_pass']}`",
        f"- sigma_range: `[{rollout_metrics['sigma_min']:.6f}, {rollout_metrics['sigma_max']:.6f}]`",
        f"- max_abs_phi: `{rollout_metrics['max_abs_phi']:.6f}`",
        f"- sigma_l1(history vs present-only): `{memory['sigma_l1']:.6f}`",
        f"- chi_l1(history vs present-only): `{memory['chi_l1']:.6f}`",
        f"- phi_l1(history vs present-only): `{memory['phi_l1']:.6f}`",
        f"- changed_nodes(locality): `{locality['changed_nodes']}`",
        f"- allowed_nodes(locality): `{locality['allowed_nodes']}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_native_update_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
