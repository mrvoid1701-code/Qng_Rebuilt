from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import centered_corr, field_extract, l1_diff, mean
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-geometry-estimator-reference-v1"


def periodic_grad(values: list[float]) -> list[float]:
    n = len(values)
    return [0.5 * (values[(i + 1) % n] - values[(i - 1) % n]) for i in range(n)]


def periodic_lap(values: list[float]) -> list[float]:
    n = len(values)
    return [values[(i + 1) % n] - 2.0 * values[i] + values[(i - 1) % n] for i in range(n)]


def geometry_proxy(c_eff: list[float]) -> dict[str, list[float]]:
    grad = periodic_grad(c_eff)
    lap = periodic_lap(c_eff)
    kappa = [max(0.0, -x) for x in lap]
    g00 = [1.0 + 1.60 * k for k in kappa]
    g11 = [1.0 + 2.40 * k + 1.10 * (g * g) for k, g in zip(kappa, grad)]
    det = [a * b for a, b in zip(g00, g11)]
    return {
        "grad": grad,
        "lap": lap,
        "kappa": kappa,
        "g00": g00,
        "g11": g11,
        "det": det,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG geometry estimator reference CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, l_hist = field_extract(hist_state, hist_history)
    c_nohist, _ = field_extract(nohist_state, nohist_history)

    geo_hist = geometry_proxy(c_hist)
    geo_nohist = geometry_proxy(c_nohist)

    checks = {
        "g00_positive_pass": min(geo_hist["g00"]) > 0.0,
        "g11_positive_pass": min(geo_hist["g11"]) > 0.0,
        "det_positive_pass": min(geo_hist["det"]) > 0.0,
        "curvature_sensitivity_pass": centered_corr(geo_hist["g11"], geo_hist["kappa"]) > 0.25,
        "coherence_over_load_pass": centered_corr(geo_hist["g11"], c_hist) >= centered_corr(geo_hist["g11"], l_hist) - 0.15,
        "history_imprint_pass": l1_diff(geo_hist["g11"], geo_nohist["g11"]) > 0.10,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-004",
        "decision": "pass" if decision else "fail",
        "means": {
            "g00_history_mean": mean(geo_hist["g00"]),
            "g11_history_mean": mean(geo_hist["g11"]),
            "g11_present_only_mean": mean(geo_nohist["g11"]),
            "kappa_history_mean": mean(geo_hist["kappa"]),
        },
        "mins": {
            "g00_min": min(geo_hist["g00"]),
            "g11_min": min(geo_hist["g11"]),
            "det_min": min(geo_hist["det"]),
        },
        "correlations": {
            "corr_g11_kappa": centered_corr(geo_hist["g11"], geo_hist["kappa"]),
            "corr_g11_c_eff": centered_corr(geo_hist["g11"], c_hist),
            "corr_g11_l_eff": centered_corr(geo_hist["g11"], l_hist),
        },
        "differences": {
            "g11_l1_history_vs_present_only": l1_diff(geo_hist["g11"], geo_nohist["g11"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Geometry Estimator Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- g00_min: `{report['mins']['g00_min']:.6f}`",
        f"- g11_min: `{report['mins']['g11_min']:.6f}`",
        f"- det_min: `{report['mins']['det_min']:.6f}`",
        f"- g11_history_mean: `{report['means']['g11_history_mean']:.6f}`",
        f"- g11_present_only_mean: `{report['means']['g11_present_only_mean']:.6f}`",
        f"- corr_g11_kappa: `{report['correlations']['corr_g11_kappa']:.6f}`",
        f"- corr_g11_c_eff: `{report['correlations']['corr_g11_c_eff']:.6f}`",
        f"- corr_g11_l_eff: `{report['correlations']['corr_g11_l_eff']:.6f}`",
        f"- g11_l1(history vs present-only): `{report['differences']['g11_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_geometry_estimator_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
