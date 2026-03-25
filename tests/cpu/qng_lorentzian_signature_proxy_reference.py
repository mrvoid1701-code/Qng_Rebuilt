from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_backreaction_closure_reference import backreaction_proxy
from qng_effective_field_reference import field_extract, l1_diff, mean
from qng_geometry_estimator_reference import geometry_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-lorentzian-signature-proxy-reference-v1"


# ── Original proxy (imported by qng_gr_linearized_assembly_reference) ────────

def lorentzian_signature_proxy(
    c_eff: list[float],
    phi: list[float],
    psi_geo: list[float],
    lambda_: float = 0.9,
    nu: float = 1.0,
):
    geo = geometry_proxy(c_eff)
    br = backreaction_proxy(c_eff, phi, psi_geo)
    t_sig = [
        1.0 + lambda_ * abs(q) + nu * h00
        for q, h00 in zip(br["q_ctr"], [2.0 * p for p in psi_geo])
    ]
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


# ── QNG-CPU-033 helpers ───────────────────────────────────────────────────────

def _correlation(a: list[float], b: list[float]) -> float:
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / n
    std_a = (sum((x - ma) ** 2 for x in a) / n) ** 0.5
    std_b = (sum((y - mb) ** 2 for y in b) / n) ** 0.5
    if std_a * std_b < 1e-15:
        return 0.0
    return cov / (std_a * std_b)


def _metric_from_fields(c_eff: list[float], phi: list[float]) -> dict:
    """Compute h_tt, h_xx directly from primitive proxies (no circular import)."""
    geo = geometry_proxy(c_eff)
    psi_geo = [0.5 * x - 0.5 for x in geo["g00"]]
    br = backreaction_proxy(c_eff, phi, psi_geo)
    h_tt = [-2.0 * p for p in br["psi_br"]]
    h_xx = [g - 1.0 for g in geo["g11"]]
    return {"h_tt": h_tt, "h_xx": h_xx}


def _signature_metrics(h_tt: list[float], h_xx: list[float]) -> dict:
    d_sig = [t * x for t, x in zip(h_tt, h_xx)]
    n = len(h_tt)
    return {
        "mean_d_sig": sum(d_sig) / n,
        "mean_h_tt": sum(h_tt) / n,
        "mean_h_xx": sum(h_xx) / n,
        "corr_h_tt_h_xx": _correlation(h_tt, h_xx),
        "frac_hxx_pos": sum(1 for x in h_xx if x > 0) / n,
        "frac_htt_neg": sum(1 for x in h_tt if x < 0) / n,
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


# ── QNG-CPU-033 main ──────────────────────────────────────────────────────────

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

    met_hist = _metric_from_fields(c_hist, hist_state.phi)
    met_nohist = _metric_from_fields(c_nohist, nohist_state.phi)

    sig_hist = _signature_metrics(met_hist["h_tt"], met_hist["h_xx"])
    sig_nohist = _signature_metrics(met_nohist["h_tt"], met_nohist["h_xx"])

    abs_dsig_hist = abs(sig_hist["mean_d_sig"])
    abs_dsig_nohist = abs(sig_nohist["mean_d_sig"])
    amplification = (
        abs_dsig_hist / abs_dsig_nohist if abs_dsig_nohist > 0 else float("inf")
    )

    checks = {
        "discriminant_negative_pass": sig_hist["mean_d_sig"] < 0,
        "anticorrelation_pass": sig_hist["corr_h_tt_h_xx"] < -0.5,
        "spacelike_robustness_pass": sig_hist["frac_hxx_pos"] > 0.90,
        "history_amplifies_discriminant_pass": amplification > 10.0,
        "history_sharpens_corr_pass": abs(sig_hist["corr_h_tt_h_xx"])
        > abs(sig_nohist["corr_h_tt_h_xx"]),
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-033",
        "decision": "pass" if decision else "fail",
        "history": sig_hist,
        "no_history": sig_nohist,
        "amplification_factor": amplification,
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Lorentzian Signature Proxy",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- mean_D_sig (history): `{sig_hist['mean_d_sig']:.6e}`",
        f"- mean_D_sig (no-history): `{sig_nohist['mean_d_sig']:.6e}`",
        f"- amplification factor: `{amplification:.1f}x`",
        f"- corr(h_tt, h_xx) history: `{sig_hist['corr_h_tt_h_xx']:.6f}`",
        f"- corr(h_tt, h_xx) no-history: `{sig_nohist['corr_h_tt_h_xx']:.6f}`",
        f"- frac(h_xx > 0): `{sig_hist['frac_hxx_pos']:.3f}`",
        f"- frac(h_tt < 0): `{sig_hist['frac_htt_neg']:.3f}`",
        f"- mean_h_tt (history): `{sig_hist['mean_h_tt']:.6f}`",
        f"- mean_h_xx (history): `{sig_hist['mean_h_xx']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_lorentzian_signature_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
