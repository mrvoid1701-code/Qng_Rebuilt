from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import field_extract, l1_diff, mean
from qng_geometry_estimator_reference import geometry_proxy, periodic_grad
from qng_backreaction_closure_reference import backreaction_proxy
from qng_lorentzian_signature_proxy_reference import lorentzian_signature_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gr-linearized-assembly-reference-v1"


def assemble_linearized_metric(c_eff: list[float], phi: list[float]) -> dict[str, list[float]]:
    geo = geometry_proxy(c_eff)
    psi_geo = [0.5 * x - 0.5 for x in geo["g00"]]
    br = backreaction_proxy(c_eff, phi, psi_geo)
    sig = lorentzian_signature_proxy(c_eff, phi, psi_geo)

    h_tt = [-2.0 * p for p in br["psi_br"]]
    h_xx = [g - 1.0 for g in geo["g11"]]
    g_tt = [-1.0 + h for h in h_tt]
    g_xx = [1.0 + h for h in h_xx]
    a_metric = [0.5 * x for x in periodic_grad(h_tt)]
    return {
        "h_tt": h_tt,
        "h_xx": h_xx,
        "a_metric": a_metric,
        "g_tt": g_tt,
        "g_xx": g_xx,
        "det": [a * b for a, b in zip(g_tt, g_xx)],
        "sig_t": sig["t_sig"],
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG linearized GR assembly CPU test.")
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
    psi_geo_hist = [0.5 * x - 0.5 for x in geometry_proxy(c_hist)["g00"]]
    br_hist = backreaction_proxy(c_hist, hist_state.phi, psi_geo_hist)

    checks = {
        "sign_pattern_pass": max(asm_hist["g_tt"]) < 0.0 and min(asm_hist["g_xx"]) > 0.0 and max(asm_hist["det"]) < 0.0,
        "weakfield_smallness_pass": max(max_abs(asm_hist["h_tt"]), max_abs(asm_hist["h_xx"])) < 0.25,
        "metric_accel_consistency_pass": l1_diff(asm_hist["a_metric"], br_hist["a_br"]) < 0.05,
        "history_imprint_pass": l1_diff(asm_hist["h_tt"], asm_nohist["h_tt"]) + l1_diff(asm_hist["h_xx"], asm_nohist["h_xx"]) > 0.05,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-015",
        "decision": "pass" if decision else "fail",
        "mins_maxs": {
            "g_tt_max": max(asm_hist["g_tt"]),
            "g_xx_min": min(asm_hist["g_xx"]),
            "det_max": max(asm_hist["det"]),
            "max_abs_h_tt": max_abs(asm_hist["h_tt"]),
            "max_abs_h_xx": max_abs(asm_hist["h_xx"]),
        },
        "means": {
            "h_tt_history_mean": mean(asm_hist["h_tt"]),
            "h_xx_history_mean": mean(asm_hist["h_xx"]),
        },
        "differences": {
            "a_metric_l1_vs_a_br": l1_diff(asm_hist["a_metric"], br_hist["a_br"]),
            "h_tt_l1_history_vs_present_only": l1_diff(asm_hist["h_tt"], asm_nohist["h_tt"]),
            "h_xx_l1_history_vs_present_only": l1_diff(asm_hist["h_xx"], asm_nohist["h_xx"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG GR Linearized Assembly v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- g_tt_max: `{report['mins_maxs']['g_tt_max']:.6f}`",
        f"- g_xx_min: `{report['mins_maxs']['g_xx_min']:.6f}`",
        f"- det_max: `{report['mins_maxs']['det_max']:.6f}`",
        f"- max_abs_h_tt: `{report['mins_maxs']['max_abs_h_tt']:.6f}`",
        f"- max_abs_h_xx: `{report['mins_maxs']['max_abs_h_xx']:.6f}`",
        f"- a_metric_l1(vs a_br): `{report['differences']['a_metric_l1_vs_a_br']:.6f}`",
        f"- h_tt_l1(history vs present-only): `{report['differences']['h_tt_l1_history_vs_present_only']:.6f}`",
        f"- h_xx_l1(history vs present-only): `{report['differences']['h_xx_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_gr_linearized_assembly_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
