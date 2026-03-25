from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from qng_backreaction_closure_reference import backreaction_proxy
from qng_effective_field_reference import field_extract, l1_diff, mean
from qng_geometry_estimator_reference import geometry_proxy, periodic_grad
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_gr_linearized_curvature_reference import curvature_proxy
from qng_native_update_reference import Config, run_rollout
from qng_qm_generator_assembly_reference import generator_proxy, psi_from_state, rollout_pair
from qng_source_response_consistency_reference import fit_two


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-bridge-closure-v2-reference-v1"


def fit_three(y: list[float], x: list[float], z: list[float], w: list[float]):
    sxx = sum(a * a for a in x)
    szz = sum(a * a for a in z)
    sww = sum(a * a for a in w)
    sxz = sum(a * b for a, b in zip(x, z))
    sxw = sum(a * b for a, b in zip(x, w))
    szw = sum(a * b for a, b in zip(z, w))
    syx = sum(a * b for a, b in zip(y, x))
    syz = sum(a * b for a, b in zip(y, z))
    syw = sum(a * b for a, b in zip(y, w))

    mat = [
        [sxx, sxz, sxw, syx],
        [sxz, szz, szw, syz],
        [sxw, szw, sww, syw],
    ]
    n = 3
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(mat[r][i]))
        mat[i], mat[piv] = mat[piv], mat[i]
        if abs(mat[i][i]) < 1e-15:
            return {"a": 0.0, "b": 0.0, "c": 0.0, "ratio": 1.0}
        p = mat[i][i]
        for j in range(i, n + 1):
            mat[i][j] /= p
        for r in range(n):
            if r == i:
                continue
            f = mat[r][i]
            for j in range(i, n + 1):
                mat[r][j] -= f * mat[i][j]
    a, b, c = [mat[i][n] for i in range(n)]
    pred = [a * u + b * v + c * q for u, v, q in zip(x, z, w)]
    raw = sum(v * v for v in y) ** 0.5
    residual = sum((u - v) ** 2 for u, v in zip(y, pred)) ** 0.5
    return {
        "a": a,
        "b": b,
        "c": c,
        "ratio": 0.0 if raw == 0.0 else residual / raw,
    }


def bridge_v2(c_eff: list[float], phi: list[float], psi_geo: list[float], source_amp: list[float], beta_q: float = 0.02, beta_s: float = 0.06):
    br1 = backreaction_proxy(c_eff, phi, psi_geo)
    s_mean = mean(source_amp)
    s_ctr = [s - s_mean for s in source_amp]
    psi_br2 = [p + beta_s * s for p, s in zip(br1["psi_br"], s_ctr)]
    a_br2 = [-x for x in periodic_grad(psi_br2)]
    return {
        "q_src": br1["q_src"],
        "source_amp": source_amp,
        "source_ctr": s_ctr,
        "psi_br1": br1["psi_br"],
        "psi_br2": psi_br2,
        "a_br2": a_br2,
    }


def source_amp_from_rollout(cfg: Config, use_history: bool):
    state_t, hist_t, state_tp1, hist_tp1 = rollout_pair(cfg, use_history=use_history)
    c_t, _ = field_extract(state_t, hist_t)
    c_tp1, _ = field_extract(state_tp1, hist_tp1)
    psi_t = psi_from_state(c_t, state_t.phi)
    psi_tp1 = psi_from_state(c_tp1, state_tp1.phi)
    gen = generator_proxy(psi_t, psi_tp1)
    return [r * (math.exp(2.0 * a) - 1.0) for a, r in zip(gen["a_loc"], c_t)]


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG bridge closure v2 CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, _ = field_extract(hist_state, hist_history)
    c_nohist, _ = field_extract(nohist_state, nohist_history)
    asm_hist = assemble_linearized_metric(c_hist, hist_state.phi)
    asm_nohist = assemble_linearized_metric(c_nohist, nohist_state.phi)
    curv_hist = curvature_proxy(asm_hist)
    curv_nohist = curvature_proxy(asm_nohist)
    geo_hist = geometry_proxy(c_hist)
    geo_nohist = geometry_proxy(c_nohist)
    psi_geo_hist = [0.5 * x - 0.5 for x in geo_hist["g00"]]
    psi_geo_nohist = [0.5 * x - 0.5 for x in geo_nohist["g00"]]

    source_hist = source_amp_from_rollout(cfg, use_history=True)
    source_nohist = source_amp_from_rollout(cfg, use_history=False)

    br1_hist = backreaction_proxy(c_hist, hist_state.phi, psi_geo_hist)
    br1_nohist = backreaction_proxy(c_nohist, nohist_state.phi, psi_geo_nohist)
    br2_hist = bridge_v2(c_hist, hist_state.phi, psi_geo_hist, source_hist)
    br2_nohist = bridge_v2(c_nohist, nohist_state.phi, psi_geo_nohist, source_nohist)
    br2_phase_frozen = bridge_v2(c_hist, [0.0] * len(hist_state.phi), psi_geo_hist, source_hist)

    fit_v1_hist = fit_two(curv_hist["r_lin"], geo_hist["kappa"], br1_hist["q_src"])
    fit_v1_nohist = fit_two(curv_nohist["r_lin"], geo_nohist["kappa"], br1_nohist["q_src"])
    fit_v2_hist = fit_three(curv_hist["r_lin"], geo_hist["kappa"], br2_hist["q_src"], br2_hist["source_amp"])
    fit_v2_nohist = fit_three(curv_nohist["r_lin"], geo_nohist["kappa"], br2_nohist["q_src"], br2_nohist["source_amp"])

    checks = {
        "bounded_pass": max_abs(br2_hist["psi_br2"]) < 0.1 and max_abs(br2_hist["a_br2"]) < 0.1,
        "closure_upgrade_nontrivial_pass": l1_diff(br2_hist["psi_br2"], br2_hist["psi_br1"]) > 5e-4,
        "phase_sensitivity_pass": l1_diff(br2_hist["psi_br2"], br2_phase_frozen["psi_br2"]) > 0.01,
        "history_imprint_pass": l1_diff(br2_hist["psi_br2"], br2_nohist["psi_br2"]) > 0.05,
        "fit_upgrade_pass": fit_v2_hist["ratio"] < fit_v1_hist["ratio"] - 0.05,
        "second_source_nonzero_pass": abs(fit_v2_hist["c"]) > 1e-3,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-025",
        "decision": "pass" if decision else "fail",
        "max_abs": {
            "psi_br2": max_abs(br2_hist["psi_br2"]),
            "a_br2": max_abs(br2_hist["a_br2"]),
        },
        "fits_history": {
            "v1_ratio": fit_v1_hist["ratio"],
            "v2_ratio": fit_v2_hist["ratio"],
            "a": fit_v2_hist["a"],
            "b": fit_v2_hist["b"],
            "c": fit_v2_hist["c"],
        },
        "fits_present_only": {
            "v1_ratio": fit_v1_nohist["ratio"],
            "v2_ratio": fit_v2_nohist["ratio"],
            "a": fit_v2_nohist["a"],
            "b": fit_v2_nohist["b"],
            "c": fit_v2_nohist["c"],
        },
        "differences": {
            "psi_br2_l1_vs_br1": l1_diff(br2_hist["psi_br2"], br2_hist["psi_br1"]),
            "psi_br2_l1_phase_vs_frozen": l1_diff(br2_hist["psi_br2"], br2_phase_frozen["psi_br2"]),
            "psi_br2_l1_history_vs_present_only": l1_diff(br2_hist["psi_br2"], br2_nohist["psi_br2"]),
            "fit_ratio_improvement_history": fit_v1_hist["ratio"] - fit_v2_hist["ratio"],
            "fit_ratio_improvement_present_only": fit_v1_nohist["ratio"] - fit_v2_nohist["ratio"],
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Bridge Closure v2",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- psi_br2_max_abs: `{report['max_abs']['psi_br2']:.6f}`",
        f"- a_br2_max_abs: `{report['max_abs']['a_br2']:.6f}`",
        f"- v1_ratio_history: `{report['fits_history']['v1_ratio']:.6f}`",
        f"- v2_ratio_history: `{report['fits_history']['v2_ratio']:.6f}`",
        f"- coeff_b_history: `{report['fits_history']['b']:.6f}`",
        f"- coeff_c_history: `{report['fits_history']['c']:.6f}`",
        f"- psi_br2_l1(vs br1): `{report['differences']['psi_br2_l1_vs_br1']:.6f}`",
        f"- psi_br2_l1(phase vs frozen): `{report['differences']['psi_br2_l1_phase_vs_frozen']:.6f}`",
        f"- psi_br2_l1(history vs present-only): `{report['differences']['psi_br2_l1_history_vs_present_only']:.6f}`",
        f"- fit_ratio_improvement_history: `{report['differences']['fit_ratio_improvement_history']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_bridge_closure_v2_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
