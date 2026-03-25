from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import centered_corr, field_extract, l1_diff, mean
from qng_geometry_estimator_reference import geometry_proxy, periodic_grad
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gr-weakfield-proxy-reference-v1"


def weakfield_proxy(c_eff: list[float]) -> dict[str, list[float]]:
    geo = geometry_proxy(c_eff)
    h00 = [x - 1.0 for x in geo["g00"]]
    h11 = [x - 1.0 for x in geo["g11"]]
    psi = [0.5 * x for x in h00]
    accel = [-x for x in periodic_grad(psi)]
    grad_kappa = periodic_grad(geo["kappa"])
    return {
        "h00": h00,
        "h11": h11,
        "psi": psi,
        "accel": accel,
        "kappa": geo["kappa"],
        "grad_kappa": grad_kappa,
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG to GR weak-field proxy CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, _ = field_extract(hist_state, hist_history)
    c_nohist, _ = field_extract(nohist_state, nohist_history)

    weak_hist = weakfield_proxy(c_hist)
    weak_nohist = weakfield_proxy(c_nohist)

    checks = {
        "weakfield_smallness_pass": max(max_abs(weak_hist["h00"]), max_abs(weak_hist["h11"])) < 0.10,
        "accel_nontrivial_pass": l1_diff(weak_hist["accel"], [0.0] * len(weak_hist["accel"])) > 0.01,
        "accel_curvature_link_pass": centered_corr(weak_hist["accel"], weak_hist["grad_kappa"]) < -0.20,
        "history_imprint_pass": (
            l1_diff(weak_hist["h11"], weak_nohist["h11"]) + l1_diff(weak_hist["accel"], weak_nohist["accel"])
        )
        > 0.05,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-005",
        "decision": "pass" if decision else "fail",
        "max_abs": {
            "h00": max_abs(weak_hist["h00"]),
            "h11": max_abs(weak_hist["h11"]),
            "psi": max_abs(weak_hist["psi"]),
            "accel": max_abs(weak_hist["accel"]),
        },
        "means": {
            "h00_history_mean": mean(weak_hist["h00"]),
            "h11_history_mean": mean(weak_hist["h11"]),
            "psi_history_mean": mean(weak_hist["psi"]),
            "accel_abs_history_mean": mean([abs(x) for x in weak_hist["accel"]]),
        },
        "correlations": {
            "corr_accel_grad_kappa": centered_corr(weak_hist["accel"], weak_hist["grad_kappa"]),
        },
        "differences": {
            "h11_l1_history_vs_present_only": l1_diff(weak_hist["h11"], weak_nohist["h11"]),
            "accel_l1_history_vs_present_only": l1_diff(weak_hist["accel"], weak_nohist["accel"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG To GR Weak-Field Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- max_abs_h00: `{report['max_abs']['h00']:.6f}`",
        f"- max_abs_h11: `{report['max_abs']['h11']:.6f}`",
        f"- max_abs_psi: `{report['max_abs']['psi']:.6f}`",
        f"- max_abs_accel: `{report['max_abs']['accel']:.6f}`",
        f"- corr_accel_grad_kappa: `{report['correlations']['corr_accel_grad_kappa']:.6f}`",
        f"- h11_l1(history vs present-only): `{report['differences']['h11_l1_history_vs_present_only']:.6f}`",
        f"- accel_l1(history vs present-only): `{report['differences']['accel_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_gr_weakfield_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
