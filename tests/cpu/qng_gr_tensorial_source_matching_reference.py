from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_backreaction_closure_reference import backreaction_proxy
from qng_bridge_closure_v2_reference import source_amp_from_rollout
from qng_effective_field_reference import field_extract, l1_diff
from qng_geometry_estimator_reference import geometry_proxy
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_gr_linearized_curvature_reference import curvature_proxy
from qng_gr_tensorial_assembly_reference import tensorial_proxy
from qng_matter_sector_proxy_reference import matter_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gr-tensorial-source-matching-reference-v1"


def fit_four(y: list[float], x: list[float], z: list[float], w: list[float], u: list[float]) -> dict:
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
    parser = argparse.ArgumentParser(description="QNG GR tensorial source matching CPU test.")
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

    ten_hist = tensorial_proxy(asm_hist)
    ten_nohist = tensorial_proxy(asm_nohist)
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

    kappa_hist = geo_hist["kappa"]
    kappa_nohist = geo_nohist["kappa"]

    # individual component fits
    fit_exx_hist = fit_four(ten_hist["e_xx"], kappa_hist, br_hist["q_src"], src_hist, m_hist)
    fit_ett_hist = fit_four(ten_hist["e_tt"], kappa_hist, br_hist["q_src"], src_hist, m_hist)
    fit_exx_nohist = fit_four(ten_nohist["e_xx"], kappa_nohist, br_nohist["q_src"], src_nohist, m_nohist)

    # scalar R_lin fit (same 4 sources, for comparison)
    fit_rlin_hist = fit_four(curv_hist["r_lin"], kappa_hist, br_hist["q_src"], src_hist, m_hist)

    ratio_split = (fit_exx_hist["ratio"] + fit_ett_hist["ratio"]) / 2.0
    b_xx = fit_exx_hist["b"]   # transport coefficient for E_xx
    b_tt = fit_ett_hist["b"]   # transport coefficient for E_tt

    # history imprint: predicted E_xx values with hist vs nohist fits
    pred_exx_hist = [
        fit_exx_hist["a"] * k + fit_exx_hist["b"] * q + fit_exx_hist["c"] * s + fit_exx_hist["d"] * m
        for k, q, s, m in zip(kappa_hist, br_hist["q_src"], src_hist, m_hist)
    ]
    pred_exx_nohist = [
        fit_exx_nohist["a"] * k + fit_exx_nohist["b"] * q + fit_exx_nohist["c"] * s + fit_exx_nohist["d"] * m
        for k, q, s, m in zip(kappa_nohist, br_nohist["q_src"], src_nohist, m_nohist)
    ]

    a_xx = fit_exx_hist["a"]   # geometry coefficient for E_xx
    a_tt = fit_ett_hist["a"]   # geometry coefficient for E_tt

    checks = {
        "e_xx_fits_well_pass": fit_exx_hist["ratio"] < 0.90,
        "a_xx_positive_pass": a_xx > 0.0,
        "a_tt_negative_pass": a_tt < 0.0,
        "geometry_sign_separation_pass": a_xx - a_tt > 1.0,
        "split_improves_scalar_pass": ratio_split < fit_rlin_hist["ratio"],
        "history_imprint_pass": l1_diff(pred_exx_hist, pred_exx_nohist) > 0.05,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-030",
        "decision": "pass" if decision else "fail",
        "fit_ratios": {
            "ratio_e_xx": fit_exx_hist["ratio"],
            "ratio_e_tt": fit_ett_hist["ratio"],
            "ratio_r_lin": fit_rlin_hist["ratio"],
            "ratio_split_mean": ratio_split,
        },
        "geometry_coefficients": {
            "a_xx": a_xx,
            "a_tt": a_tt,
            "a_xx_minus_a_tt": a_xx - a_tt,
        },
        "transport_coefficients": {
            "b_xx": b_xx,
            "b_tt": b_tt,
        },
        "e_xx_coeffs": {
            "a": fit_exx_hist["a"],
            "b": b_xx,
            "c": fit_exx_hist["c"],
            "d": fit_exx_hist["d"],
        },
        "e_tt_coeffs": {
            "a": fit_ett_hist["a"],
            "b": b_tt,
            "c": fit_ett_hist["c"],
            "d": fit_ett_hist["d"],
        },
        "differences": {
            "pred_e_xx_history_vs_nohist_l1": l1_diff(pred_exx_hist, pred_exx_nohist),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG GR Tensorial Source Matching Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- ratio_e_xx: `{report['fit_ratios']['ratio_e_xx']:.6f}`",
        f"- ratio_e_tt: `{report['fit_ratios']['ratio_e_tt']:.6f}`",
        f"- ratio_r_lin (scalar): `{report['fit_ratios']['ratio_r_lin']:.6f}`",
        f"- ratio_split_mean: `{report['fit_ratios']['ratio_split_mean']:.6f}`",
        f"- a_xx (geometry, E_xx): `{report['geometry_coefficients']['a_xx']:.6f}`",
        f"- a_tt (geometry, E_tt): `{report['geometry_coefficients']['a_tt']:.6f}`",
        f"- a_xx - a_tt: `{report['geometry_coefficients']['a_xx_minus_a_tt']:.6f}`",
        f"- b_xx (transport, E_xx): `{report['transport_coefficients']['b_xx']:.6f}`",
        f"- b_tt (transport, E_tt): `{report['transport_coefficients']['b_tt']:.6f}`",
        f"- pred_e_xx_history_l1: `{report['differences']['pred_e_xx_history_vs_nohist_l1']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_gr_tensorial_source_matching_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
