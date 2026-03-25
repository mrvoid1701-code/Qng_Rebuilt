from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import field_extract, l1_diff, mean
from qng_geometry_estimator_reference import geometry_proxy
from qng_native_update_reference import Config, run_rollout
from qng_backreaction_closure_reference import backreaction_proxy


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-lorentzian-signature-proxy-reference-v1"


def lorentzian_signature_proxy(c_eff: list[float], phi: list[float], psi_geo: list[float], lambda_: float = 0.9, nu: float = 1.0):
    geo = geometry_proxy(c_eff)
    br = backreaction_proxy(c_eff, phi, psi_geo)
    t_sig = [1.0 + lambda_ * abs(q) + nu * h00 for q, h00 in zip(br["q_ctr"], [2.0 * p for p in psi_geo])]
    g_tt = [-x for x in t_sig]
    g_xx = geo["g11"]
    det = [a * b for a, b in zip(g_tt, g_xx)]
    return {
        "q_ctr": br["q_ctr"],
        "t_sig": t_sig,
        "g_tt": g_tt,
        "g_xx": g_xx,
        "det": det,
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG Lorentzian signature proxy CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, _ = field_extract(hist_state, hist_history)
    c_nohist, _ = field_extract(nohist_state, nohist_history)
    psi_hist = [0.5 * x for x in geometry_proxy(c_hist)["g00"]]
    psi_hist = [x - 0.5 for x in psi_hist]
    psi_nohist = [0.5 * x for x in geometry_proxy(c_nohist)["g00"]]
    psi_nohist = [x - 0.5 for x in psi_nohist]

    sig_hist = lorentzian_signature_proxy(c_hist, hist_state.phi, psi_hist)
    sig_nohist = lorentzian_signature_proxy(c_nohist, nohist_state.phi, psi_nohist)
    sig_phase_frozen = lorentzian_signature_proxy(c_hist, [0.0] * len(hist_state.phi), psi_hist)

    checks = {
        "sign_pattern_pass": max(sig_hist["g_tt"]) < 0.0 and min(sig_hist["g_xx"]) > 0.0,
        "det_negative_pass": max(sig_hist["det"]) < 0.0,
        "bounded_temporal_modulation_pass": max_abs(sig_hist["t_sig"]) < 2.0,
        "phase_sensitivity_pass": l1_diff(sig_hist["t_sig"], sig_phase_frozen["t_sig"]) > 0.05,
        "history_imprint_pass": l1_diff(sig_hist["t_sig"], sig_nohist["t_sig"]) > 0.05,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-014",
        "decision": "pass" if decision else "fail",
        "mins_maxs": {
            "g_tt_max": max(sig_hist["g_tt"]),
            "g_xx_min": min(sig_hist["g_xx"]),
            "det_max": max(sig_hist["det"]),
            "t_sig_max_abs": max_abs(sig_hist["t_sig"]),
        },
        "means": {
            "t_sig_history_mean": mean(sig_hist["t_sig"]),
            "q_ctr_history_mean": mean(sig_hist["q_ctr"]),
        },
        "differences": {
            "t_sig_l1_phase_vs_frozen": l1_diff(sig_hist["t_sig"], sig_phase_frozen["t_sig"]),
            "t_sig_l1_history_vs_present_only": l1_diff(sig_hist["t_sig"], sig_nohist["t_sig"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Lorentzian Signature Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- g_tt_max: `{report['mins_maxs']['g_tt_max']:.6f}`",
        f"- g_xx_min: `{report['mins_maxs']['g_xx_min']:.6f}`",
        f"- det_max: `{report['mins_maxs']['det_max']:.6f}`",
        f"- t_sig_max_abs: `{report['mins_maxs']['t_sig_max_abs']:.6f}`",
        f"- t_sig_l1(phase vs frozen): `{report['differences']['t_sig_l1_phase_vs_frozen']:.6f}`",
        f"- t_sig_l1(history vs present-only): `{report['differences']['t_sig_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_lorentzian_signature_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
