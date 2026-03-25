from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import centered_corr, field_extract, l1_diff, mean
from qng_native_update_reference import Config, run_rollout
from qng_qm_coherence_proxy_reference import coherence_proxy


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-matter-sector-proxy-reference-v1"


def clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def matter_proxy(c_eff: list[float], l_eff: list[float], phi: list[float], alpha: float = 1.6, gamma: float = 0.8):
    qm = coherence_proxy(c_eff, phi)
    m_eff = [
        clip01(alpha * l * (1.0 - c) + gamma * abs(j))
        for c, l, j in zip(c_eff, l_eff, qm["corr_im"])
    ]
    return {
        "m_eff": m_eff,
        "corr_im": qm["corr_im"],
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG matter-sector proxy CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, l_hist = field_extract(hist_state, hist_history)
    c_nohist, l_nohist = field_extract(nohist_state, nohist_history)

    matter_hist = matter_proxy(c_hist, l_hist, hist_state.phi)
    matter_nohist = matter_proxy(c_nohist, l_nohist, nohist_state.phi)
    matter_transport_off = matter_proxy(c_hist, l_hist, [0.0] * len(hist_state.phi))

    checks = {
        "bounded_pass": all(0.0 <= x <= 1.0 for x in matter_hist["m_eff"]),
        "memory_link_pass": centered_corr(matter_hist["m_eff"], l_hist) > 0.20,
        "transport_link_pass": centered_corr(matter_hist["m_eff"], [abs(x) for x in matter_hist["corr_im"]]) > 0.50,
        "geometry_separation_pass": centered_corr(matter_hist["m_eff"], c_hist) < 0.10,
        "history_imprint_pass": l1_diff(matter_hist["m_eff"], matter_nohist["m_eff"]) > 0.50,
        "transport_switch_pass": l1_diff(matter_hist["m_eff"], matter_transport_off["m_eff"]) > 0.25,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-013",
        "decision": "pass" if decision else "fail",
        "means": {
            "m_eff_history_mean": mean(matter_hist["m_eff"]),
            "m_eff_present_only_mean": mean(matter_nohist["m_eff"]),
            "corr_im_abs_history_mean": mean([abs(x) for x in matter_hist["corr_im"]]),
        },
        "max_abs": {
            "m_eff": max_abs(matter_hist["m_eff"]),
        },
        "correlations": {
            "corr_m_eff_l_eff": centered_corr(matter_hist["m_eff"], l_hist),
            "corr_m_eff_abs_corr_im": centered_corr(matter_hist["m_eff"], [abs(x) for x in matter_hist["corr_im"]]),
            "corr_m_eff_c_eff": centered_corr(matter_hist["m_eff"], c_hist),
        },
        "differences": {
            "m_eff_l1_history_vs_present_only": l1_diff(matter_hist["m_eff"], matter_nohist["m_eff"]),
            "m_eff_l1_transport_on_vs_off": l1_diff(matter_hist["m_eff"], matter_transport_off["m_eff"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Matter Sector Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- m_eff_history_mean: `{report['means']['m_eff_history_mean']:.6f}`",
        f"- m_eff_present_only_mean: `{report['means']['m_eff_present_only_mean']:.6f}`",
        f"- max_abs_m_eff: `{report['max_abs']['m_eff']:.6f}`",
        f"- corr_m_eff_l_eff: `{report['correlations']['corr_m_eff_l_eff']:.6f}`",
        f"- corr_m_eff_abs_corr_im: `{report['correlations']['corr_m_eff_abs_corr_im']:.6f}`",
        f"- corr_m_eff_c_eff: `{report['correlations']['corr_m_eff_c_eff']:.6f}`",
        f"- m_eff_l1(history vs present-only): `{report['differences']['m_eff_l1_history_vs_present_only']:.6f}`",
        f"- m_eff_l1(transport on vs off): `{report['differences']['m_eff_l1_transport_on_vs_off']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_matter_sector_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
