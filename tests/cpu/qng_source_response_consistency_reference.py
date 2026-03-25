from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import field_extract, l1_diff
from qng_geometry_estimator_reference import geometry_proxy
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_gr_linearized_curvature_reference import curvature_proxy
from qng_backreaction_closure_reference import backreaction_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-source-response-consistency-reference-v1"


def fit_one(y: list[float], x: list[float]) -> dict[str, float | list[float]]:
    xx = sum(v * v for v in x)
    a = 0.0 if xx == 0.0 else sum(u * v for u, v in zip(y, x)) / xx
    pred = [a * v for v in x]
    raw = sum(v * v for v in y) ** 0.5
    residual = sum((u - v) ** 2 for u, v in zip(y, pred)) ** 0.5
    return {
        "a": a,
        "pred": pred,
        "raw_l2": raw,
        "residual_l2": residual,
        "ratio": 0.0 if raw == 0.0 else residual / raw,
    }


def fit_two(y: list[float], x: list[float], z: list[float]) -> dict[str, float | list[float]]:
    xx = sum(v * v for v in x)
    zz = sum(v * v for v in z)
    xz = sum(a * b for a, b in zip(x, z))
    yx = sum(a * b for a, b in zip(y, x))
    yz = sum(a * b for a, b in zip(y, z))
    det = xx * zz - xz * xz
    if abs(det) < 1e-15:
        a = 0.0
        b = 0.0
    else:
        a = (yx * zz - xz * yz) / det
        b = (xx * yz - xz * yx) / det
    pred = [a * u + b * v for u, v in zip(x, z)]
    raw = sum(v * v for v in y) ** 0.5
    residual = sum((u - v) ** 2 for u, v in zip(y, pred)) ** 0.5
    return {
        "a": a,
        "b": b,
        "pred": pred,
        "raw_l2": raw,
        "residual_l2": residual,
        "ratio": 0.0 if raw == 0.0 else residual / raw,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG source-response consistency CPU test.")
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
    br_hist = backreaction_proxy(c_hist, hist_state.phi, psi_geo_hist)
    br_nohist = backreaction_proxy(c_nohist, nohist_state.phi, psi_geo_nohist)

    fit_geom_hist = fit_one(curv_hist["r_lin"], geo_hist["kappa"])
    fit_geom_nohist = fit_one(curv_nohist["r_lin"], geo_nohist["kappa"])
    fit_src_hist = fit_two(curv_hist["r_lin"], geo_hist["kappa"], br_hist["q_src"])
    fit_src_nohist = fit_two(curv_nohist["r_lin"], geo_nohist["kappa"], br_nohist["q_src"])

    checks = {
        "baseline_meaningful_pass": fit_geom_hist["ratio"] < 0.85,
        "source_augmented_improvement_pass": fit_src_hist["ratio"] < fit_geom_hist["ratio"] - 0.10,
        "source_coefficient_pass": abs(fit_src_hist["b"]) > 1e-3,
        "history_imprint_pass": abs(fit_src_hist["b"] - fit_src_nohist["b"]) > 1e-3 or l1_diff(curv_hist["r_lin"], curv_nohist["r_lin"]) > 0.25,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-020",
        "decision": "pass" if decision else "fail",
        "history_geometry_only": {
            "a": fit_geom_hist["a"],
            "ratio": fit_geom_hist["ratio"],
        },
        "history_with_source": {
            "a": fit_src_hist["a"],
            "b": fit_src_hist["b"],
            "ratio": fit_src_hist["ratio"],
        },
        "present_only_geometry_only": {
            "a": fit_geom_nohist["a"],
            "ratio": fit_geom_nohist["ratio"],
        },
        "present_only_with_source": {
            "a": fit_src_nohist["a"],
            "b": fit_src_nohist["b"],
            "ratio": fit_src_nohist["ratio"],
        },
        "differences": {
            "ratio_improvement_history": fit_geom_hist["ratio"] - fit_src_hist["ratio"],
            "ratio_improvement_present_only": fit_geom_nohist["ratio"] - fit_src_nohist["ratio"],
            "r_lin_l1_history_vs_present_only": l1_diff(curv_hist["r_lin"], curv_nohist["r_lin"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Source-Response Consistency v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- geom_only_ratio_history: `{report['history_geometry_only']['ratio']:.6f}`",
        f"- with_source_ratio_history: `{report['history_with_source']['ratio']:.6f}`",
        f"- source_coeff_b_history: `{report['history_with_source']['b']:.6f}`",
        f"- geom_only_ratio_present_only: `{report['present_only_geometry_only']['ratio']:.6f}`",
        f"- with_source_ratio_present_only: `{report['present_only_with_source']['ratio']:.6f}`",
        f"- ratio_improvement_history: `{report['differences']['ratio_improvement_history']:.6f}`",
        f"- ratio_improvement_present_only: `{report['differences']['ratio_improvement_present_only']:.6f}`",
        f"- r_lin_l1(history vs present-only): `{report['differences']['r_lin_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_source_response_consistency_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
