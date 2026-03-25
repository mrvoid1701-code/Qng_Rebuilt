from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from qng_effective_field_reference import field_extract, l1_diff, mean
from qng_native_update_reference import Config, build_graph, init_state, one_step
from qng_qm_coherence_proxy_reference import coherence_proxy


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-qm-continuity-assembly-reference-v1"


def rollout_pair(cfg: Config, use_history: bool):
    rng = random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)
    for _ in range(cfg.steps - 1):
        state, history = one_step(state, history, adj, cfg, use_history=use_history)
    state_t = state
    history_t = history
    state_tp1, history_tp1 = one_step(state_t, history_t, adj, cfg, use_history=use_history)
    return state_t, history_t, state_tp1, history_tp1


def current_divergence(edge_current: list[float]) -> list[float]:
    n = len(edge_current)
    return [edge_current[i] - edge_current[(i - 1) % n] for i in range(n)]


def continuity_fit(rho_t: list[float], rho_tp1: list[float], edge_current: list[float]):
    d_rho = [b - a for a, b in zip(rho_t, rho_tp1)]
    div_j = current_divergence(edge_current)
    denom = sum(x * x for x in div_j)
    kappa = 0.0 if denom == 0.0 else -sum(a * b for a, b in zip(d_rho, div_j)) / denom
    residual = [a + kappa * b for a, b in zip(d_rho, div_j)]
    raw_l2 = sum(x * x for x in d_rho) ** 0.5
    residual_l2 = sum(x * x for x in residual) ** 0.5
    return {
        "kappa": kappa,
        "d_rho": d_rho,
        "div_j": div_j,
        "residual": residual,
        "raw_l2": raw_l2,
        "residual_l2": residual_l2,
        "improvement_ratio": 0.0 if raw_l2 == 0.0 else residual_l2 / raw_l2,
    }


def centered(values: list[float]) -> list[float]:
    m = mean(values)
    return [x - m for x in values]


def continuity_fit_with_source(rho_t: list[float], rho_tp1: list[float], edge_current: list[float], source: list[float]):
    d_rho = [b - a for a, b in zip(rho_t, rho_tp1)]
    div_j = current_divergence(edge_current)
    src = centered(source)

    aa = sum(x * x for x in div_j)
    bb = sum(x * y for x, y in zip(div_j, src))
    cc = sum(y * y for y in src)
    rhs_a = -sum(x * y for x, y in zip(d_rho, div_j))
    rhs_c = -sum(x * y for x, y in zip(d_rho, src))
    det = aa * cc - bb * bb

    if abs(det) < 1e-15:
        kappa = 0.0
        sigma = 0.0
    else:
        kappa = (rhs_a * cc - bb * rhs_c) / det
        sigma = (aa * rhs_c - bb * rhs_a) / det

    residual = [a + kappa * b + sigma * s for a, b, s in zip(d_rho, div_j, src)]
    raw_l2 = sum(x * x for x in d_rho) ** 0.5
    residual_l2 = sum(x * x for x in residual) ** 0.5
    return {
        "kappa": kappa,
        "sigma": sigma,
        "d_rho": d_rho,
        "div_j": div_j,
        "source": src,
        "residual": residual,
        "raw_l2": raw_l2,
        "residual_l2": residual_l2,
        "improvement_ratio": 0.0 if raw_l2 == 0.0 else residual_l2 / raw_l2,
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG QM continuity assembly CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    state_t, hist_t, state_tp1, hist_tp1 = rollout_pair(cfg, use_history=True)
    state_nt, hist_nt, state_ntp1, hist_ntp1 = rollout_pair(cfg, use_history=False)

    rho_t, _ = field_extract(state_t, hist_t)
    rho_tp1, _ = field_extract(state_tp1, hist_tp1)
    rho_nt, _ = field_extract(state_nt, hist_nt)
    rho_ntp1, _ = field_extract(state_ntp1, hist_ntp1)

    qm_t = coherence_proxy(rho_t, state_t.phi)
    qm_nt = coherence_proxy(rho_nt, state_nt.phi)
    qm_phase_frozen = coherence_proxy(rho_t, [0.0] * len(state_t.phi))

    fit_hist = continuity_fit(rho_t, rho_tp1, qm_t["corr_im"])
    fit_nohist = continuity_fit(rho_nt, rho_ntp1, qm_nt["corr_im"])
    _, l_hist_t = field_extract(state_t, hist_t)
    _, l_nohist_t = field_extract(state_nt, hist_nt)
    fit_hist_src = continuity_fit_with_source(rho_t, rho_tp1, qm_t["corr_im"], l_hist_t)
    fit_nohist_src = continuity_fit_with_source(rho_nt, rho_ntp1, qm_nt["corr_im"], l_nohist_t)

    checks = {
        "density_bounds_pass": all(0.0 <= x <= 1.0 for x in rho_t) and all(0.0 <= x <= 1.0 for x in rho_tp1),
        "current_nontrivial_pass": mean([abs(x) for x in qm_t["corr_im"]]) > 0.05,
        "continuity_improvement_pass": fit_hist_src["improvement_ratio"] < fit_hist["improvement_ratio"] - 0.10,
        "source_augmented_pass": fit_hist_src["improvement_ratio"] < 0.80 and abs(fit_hist_src["sigma"]) > 1e-4,
        "phase_sensitivity_pass": l1_diff(qm_t["corr_im"], qm_phase_frozen["corr_im"]) > 0.50,
        "history_imprint_pass": abs(fit_hist_src["sigma"] - fit_nohist_src["sigma"]) > 0.01 or l1_diff(rho_t, rho_nt) > 0.50,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-016",
        "decision": "pass" if decision else "fail",
        "fit_history_source_free": {
            "kappa": fit_hist["kappa"],
            "raw_l2": fit_hist["raw_l2"],
            "residual_l2": fit_hist["residual_l2"],
            "improvement_ratio": fit_hist["improvement_ratio"],
        },
        "fit_present_only_source_free": {
            "kappa": fit_nohist["kappa"],
            "raw_l2": fit_nohist["raw_l2"],
            "residual_l2": fit_nohist["residual_l2"],
            "improvement_ratio": fit_nohist["improvement_ratio"],
        },
        "fit_history_with_source": {
            "kappa": fit_hist_src["kappa"],
            "sigma": fit_hist_src["sigma"],
            "raw_l2": fit_hist_src["raw_l2"],
            "residual_l2": fit_hist_src["residual_l2"],
            "improvement_ratio": fit_hist_src["improvement_ratio"],
        },
        "fit_present_only_with_source": {
            "kappa": fit_nohist_src["kappa"],
            "sigma": fit_nohist_src["sigma"],
            "raw_l2": fit_nohist_src["raw_l2"],
            "residual_l2": fit_nohist_src["residual_l2"],
            "improvement_ratio": fit_nohist_src["improvement_ratio"],
        },
        "means": {
            "rho_t_mean": mean(rho_t),
            "rho_tp1_mean": mean(rho_tp1),
            "corr_im_abs_mean": mean([abs(x) for x in qm_t["corr_im"]]),
        },
        "max_abs": {
            "corr_im": max_abs(qm_t["corr_im"]),
            "residual": max_abs(fit_hist["residual"]),
        },
        "differences": {
            "corr_im_l1_phase_vs_frozen": l1_diff(qm_t["corr_im"], qm_phase_frozen["corr_im"]),
            "rho_l1_history_vs_present_only": l1_diff(rho_t, rho_nt),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG QM Continuity Assembly v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- kappa_history_source_free: `{report['fit_history_source_free']['kappa']:.6f}`",
        f"- kappa_history_with_source: `{report['fit_history_with_source']['kappa']:.6f}`",
        f"- sigma_history_with_source: `{report['fit_history_with_source']['sigma']:.6f}`",
        f"- improvement_ratio_history_source_free: `{report['fit_history_source_free']['improvement_ratio']:.6f}`",
        f"- improvement_ratio_history_with_source: `{report['fit_history_with_source']['improvement_ratio']:.6f}`",
        f"- corr_im_abs_mean: `{report['means']['corr_im_abs_mean']:.6f}`",
        f"- max_abs_corr_im: `{report['max_abs']['corr_im']:.6f}`",
        f"- corr_im_l1(phase vs frozen): `{report['differences']['corr_im_l1_phase_vs_frozen']:.6f}`",
        f"- rho_l1(history vs present-only): `{report['differences']['rho_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_qm_continuity_assembly_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
