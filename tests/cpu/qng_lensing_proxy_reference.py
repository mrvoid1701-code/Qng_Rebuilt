from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import centered_corr, field_extract, l1_diff, mean
from qng_geometry_estimator_reference import geometry_proxy, periodic_grad
from qng_gr_weakfield_proxy_reference import weakfield_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-lensing-proxy-reference-v1"


def lensing_proxy(c_eff: list[float]) -> dict[str, list[float] | float]:
    weak = weakfield_proxy(c_eff)
    geo = geometry_proxy(c_eff)
    phi_lens = [0.5 * (a + b) for a, b in zip(weak["h00"], weak["h11"])]
    alpha = [-x for x in periodic_grad(phi_lens)]
    d_lens = sum(abs(x) for x in alpha)
    return {
        "phi_lens": phi_lens,
        "alpha": alpha,
        "d_lens": d_lens,
        "kappa": geo["kappa"],
        "grad_kappa": periodic_grad(geo["kappa"]),
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG lensing proxy CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, _ = field_extract(hist_state, hist_history)
    c_nohist, _ = field_extract(nohist_state, nohist_history)

    lens_hist = lensing_proxy(c_hist)
    lens_nohist = lensing_proxy(c_nohist)

    checks = {
        "weakfield_bounded_pass": max_abs(lens_hist["phi_lens"]) < 0.10 and max_abs(lens_hist["alpha"]) < 0.05,
        "deflection_nontrivial_pass": lens_hist["d_lens"] > 0.01,
        "geometry_gradient_link_pass": centered_corr(lens_hist["alpha"], lens_hist["grad_kappa"]) < -0.20,
        "history_imprint_pass": abs(lens_hist["d_lens"] - lens_nohist["d_lens"]) > 0.01,
        "profile_history_pass": l1_diff(lens_hist["alpha"], lens_nohist["alpha"]) > 0.05,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-008",
        "decision": "pass" if decision else "fail",
        "max_abs": {
            "phi_lens": max_abs(lens_hist["phi_lens"]),
            "alpha": max_abs(lens_hist["alpha"]),
        },
        "means": {
            "phi_lens_history_mean": mean(lens_hist["phi_lens"]),
            "alpha_abs_history_mean": mean([abs(x) for x in lens_hist["alpha"]]),
        },
        "strength": {
            "d_lens_history": lens_hist["d_lens"],
            "d_lens_present_only": lens_nohist["d_lens"],
        },
        "correlations": {
            "corr_alpha_grad_kappa": centered_corr(lens_hist["alpha"], lens_hist["grad_kappa"]),
        },
        "differences": {
            "d_lens_abs_difference": abs(lens_hist["d_lens"] - lens_nohist["d_lens"]),
            "alpha_l1_history_vs_present_only": l1_diff(lens_hist["alpha"], lens_nohist["alpha"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Lensing Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- max_abs_phi_lens: `{report['max_abs']['phi_lens']:.6f}`",
        f"- max_abs_alpha: `{report['max_abs']['alpha']:.6f}`",
        f"- d_lens_history: `{report['strength']['d_lens_history']:.6f}`",
        f"- d_lens_present_only: `{report['strength']['d_lens_present_only']:.6f}`",
        f"- corr_alpha_grad_kappa: `{report['correlations']['corr_alpha_grad_kappa']:.6f}`",
        f"- d_lens_abs_difference: `{report['differences']['d_lens_abs_difference']:.6f}`",
        f"- alpha_l1(history vs present-only): `{report['differences']['alpha_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_lensing_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
