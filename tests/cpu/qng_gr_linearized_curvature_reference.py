from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import centered_corr, field_extract, l1_diff, mean
from qng_geometry_estimator_reference import geometry_proxy, periodic_grad, periodic_lap
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gr-linearized-curvature-reference-v1"


def curvature_proxy(asm: dict[str, list[float]]) -> dict[str, list[float]]:
    lap_t = periodic_lap(asm["h_tt"])
    lap_x = periodic_lap(asm["h_xx"])
    r_lin = [a - b for a, b in zip(lap_t, lap_x)]
    grad_a = periodic_grad(asm["a_metric"])
    return {
        "lap_t": lap_t,
        "lap_x": lap_x,
        "r_lin": r_lin,
        "grad_a": grad_a,
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG GR linearized curvature CPU test.")
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
    geo_hist = geometry_proxy(c_hist)

    curv_hist = curvature_proxy(asm_hist)
    curv_nohist = curvature_proxy(asm_nohist)

    checks = {
        "bounded_pass": max_abs(curv_hist["r_lin"]) < 0.25,
        "geometry_link_pass": centered_corr(curv_hist["r_lin"], geo_hist["kappa"]) > 0.50,
        "accel_gradient_link_pass": centered_corr(curv_hist["r_lin"], curv_hist["grad_a"]) > 0.40,
        "history_imprint_pass": l1_diff(curv_hist["r_lin"], curv_nohist["r_lin"]) > 0.25,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-019",
        "decision": "pass" if decision else "fail",
        "max_abs": {
            "r_lin": max_abs(curv_hist["r_lin"]),
        },
        "means": {
            "r_lin_history_mean": mean(curv_hist["r_lin"]),
        },
        "correlations": {
            "corr_r_lin_kappa": centered_corr(curv_hist["r_lin"], geo_hist["kappa"]),
            "corr_r_lin_grad_a": centered_corr(curv_hist["r_lin"], curv_hist["grad_a"]),
        },
        "differences": {
            "r_lin_l1_history_vs_present_only": l1_diff(curv_hist["r_lin"], curv_nohist["r_lin"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG GR Linearized Curvature v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- max_abs_r_lin: `{report['max_abs']['r_lin']:.6f}`",
        f"- corr_r_lin_kappa: `{report['correlations']['corr_r_lin_kappa']:.6f}`",
        f"- corr_r_lin_grad_a: `{report['correlations']['corr_r_lin_grad_a']:.6f}`",
        f"- r_lin_l1(history vs present-only): `{report['differences']['r_lin_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_gr_linearized_curvature_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
