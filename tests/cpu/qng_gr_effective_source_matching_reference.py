from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_bridge_closure_v2_reference import fit_three, source_amp_from_rollout
from qng_backreaction_closure_reference import backreaction_proxy
from qng_effective_field_reference import field_extract, l1_diff
from qng_geometry_estimator_reference import geometry_proxy
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_gr_linearized_curvature_reference import curvature_proxy
from qng_matter_sector_proxy_reference import matter_proxy
from qng_native_update_reference import Config, run_rollout
from qng_source_response_consistency_reference import fit_two


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gr-effective-source-matching-reference-v1"


def fit_four(y: list[float], x: list[float], z: list[float], w: list[float], u: list[float]):
    cols = [x, z, w, u]
    m = 4
    n = len(y)
    mat = [[sum(cols[i][k] * cols[j][k] for k in range(n)) for j in range(m)] for i in range(m)]
    rhs = [sum(y[k] * cols[i][k] for k in range(n)) for i in range(m)]
    aug = [row[:] + [b] for row, b in zip(mat, rhs)]
    for i in range(m):
        piv = max(range(i, m), key=lambda r: abs(aug[r][i]))
        aug[i], aug[piv] = aug[piv], aug[i]
        if abs(aug[i][i]) < 1e-15:
            return {"a": 0.0, "b": 0.0, "c": 0.0, "d": 0.0, "ratio": 1.0}
        p = aug[i][i]
        for j in range(i, m + 1):
            aug[i][j] /= p
        for r in range(m):
            if r == i:
                continue
            f = aug[r][i]
            for j in range(i, m + 1):
                aug[r][j] -= f * aug[i][j]
    a, b, c, d = [aug[i][m] for i in range(m)]
    pred = [a * p + b * q + c * s + d * t for p, q, s, t in zip(x, z, w, u)]
    raw = sum(v * v for v in y) ** 0.5
    residual = sum((u0 - v0) ** 2 for u0, v0 in zip(y, pred)) ** 0.5
    return {"a": a, "b": b, "c": c, "d": d, "ratio": 0.0 if raw == 0.0 else residual / raw}


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG GR effective source matching CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, l_hist = field_extract(hist_state, hist_history)
    c_nohist, l_nohist = field_extract(nohist_state, nohist_history)
    asm_hist = assemble_linearized_metric(c_hist, hist_state.phi)
    asm_nohist = assemble_linearized_metric(c_nohist, nohist_state.phi)
    curv_hist = curvature_proxy(asm_hist)
    curv_nohist = curvature_proxy(asm_nohist)
    geo_hist = geometry_proxy(c_hist)
    geo_nohist = geometry_proxy(c_nohist)
    psi_geo_hist = [0.5 * x - 0.5 for x in geo_hist["g00"]]
    psi_geo_nohist = [0.5 * x - 0.5 for x in geo_nohist["g00"]]
    br_hist = backreaction_proxy(c_hist, hist_state.phi, psi_geo_hist)
    br_nohist = backreaction_proxy(c_nohist, nohist_state.phi, psi_geo_nohist)
    src_hist = source_amp_from_rollout(cfg, use_history=True)
    src_nohist = source_amp_from_rollout(cfg, use_history=False)
    m_hist = matter_proxy(c_hist, l_hist, hist_state.phi)["m_eff"]
    m_nohist = matter_proxy(c_nohist, l_nohist, nohist_state.phi)["m_eff"]

    fit_g_hist = fit_two(curv_hist["r_lin"], geo_hist["kappa"], [0.0] * len(c_hist))
    fit_v1_hist = fit_two(curv_hist["r_lin"], geo_hist["kappa"], br_hist["q_src"])
    fit_v2_hist = fit_three(curv_hist["r_lin"], geo_hist["kappa"], br_hist["q_src"], src_hist)
    fit_v3_hist = fit_four(curv_hist["r_lin"], geo_hist["kappa"], br_hist["q_src"], src_hist, m_hist)

    fit_g_nohist = fit_two(curv_nohist["r_lin"], geo_nohist["kappa"], [0.0] * len(c_nohist))
    fit_v1_nohist = fit_two(curv_nohist["r_lin"], geo_nohist["kappa"], br_nohist["q_src"])
    fit_v2_nohist = fit_three(curv_nohist["r_lin"], geo_nohist["kappa"], br_nohist["q_src"], src_nohist)
    fit_v3_nohist = fit_four(curv_nohist["r_lin"], geo_nohist["kappa"], br_nohist["q_src"], src_nohist, m_nohist)

    checks = {
        "improves_over_geometry_only_pass": fit_v3_hist["ratio"] < fit_g_hist["ratio"] - 0.10,
        "improves_over_v1_pass": fit_v3_hist["ratio"] < fit_v1_hist["ratio"] - 0.05,
        "improves_over_v2_pass": fit_v3_hist["ratio"] < fit_v2_hist["ratio"] - 0.03,
        "matter_coeff_nonzero_pass": abs(fit_v3_hist["d"]) > 1e-3,
        "history_imprint_pass": abs(fit_v3_hist["d"] - fit_v3_nohist["d"]) > 1e-3 or l1_diff(curv_hist["r_lin"], curv_nohist["r_lin"]) > 0.25,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-026",
        "decision": "pass" if decision else "fail",
        "history_ratios": {
            "geometry_only": fit_g_hist["ratio"],
            "v1": fit_v1_hist["ratio"],
            "v2": fit_v2_hist["ratio"],
            "v3": fit_v3_hist["ratio"],
        },
        "present_only_ratios": {
            "geometry_only": fit_g_nohist["ratio"],
            "v1": fit_v1_nohist["ratio"],
            "v2": fit_v2_nohist["ratio"],
            "v3": fit_v3_nohist["ratio"],
        },
        "history_coeffs_v3": {
            "a": fit_v3_hist["a"],
            "b": fit_v3_hist["b"],
            "c": fit_v3_hist["c"],
            "d": fit_v3_hist["d"],
        },
        "present_only_coeffs_v3": {
            "a": fit_v3_nohist["a"],
            "b": fit_v3_nohist["b"],
            "c": fit_v3_nohist["c"],
            "d": fit_v3_nohist["d"],
        },
        "differences": {
            "v3_improvement_over_geometry_only": fit_g_hist["ratio"] - fit_v3_hist["ratio"],
            "v3_improvement_over_v1": fit_v1_hist["ratio"] - fit_v3_hist["ratio"],
            "v3_improvement_over_v2": fit_v2_hist["ratio"] - fit_v3_hist["ratio"],
            "r_lin_l1_history_vs_present_only": l1_diff(curv_hist["r_lin"], curv_nohist["r_lin"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG GR Effective Source Matching v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- ratio_geometry_only: `{report['history_ratios']['geometry_only']:.6f}`",
        f"- ratio_v1: `{report['history_ratios']['v1']:.6f}`",
        f"- ratio_v2: `{report['history_ratios']['v2']:.6f}`",
        f"- ratio_v3: `{report['history_ratios']['v3']:.6f}`",
        f"- coeff_d_history: `{report['history_coeffs_v3']['d']:.6f}`",
        f"- improve_over_geometry_only: `{report['differences']['v3_improvement_over_geometry_only']:.6f}`",
        f"- improve_over_v1: `{report['differences']['v3_improvement_over_v1']:.6f}`",
        f"- improve_over_v2: `{report['differences']['v3_improvement_over_v2']:.6f}`",
        f"- r_lin_l1(history vs present-only): `{report['differences']['r_lin_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_gr_effective_source_matching_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
