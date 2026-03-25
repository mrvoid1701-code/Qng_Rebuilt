from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from qng_effective_field_reference import field_extract, l1_diff, mean
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-qm-coherence-proxy-reference-v1"


def coherence_proxy(c_eff: list[float], phi: list[float]) -> dict[str, list[float]]:
    n = len(c_eff)
    amp = [math.sqrt(max(0.0, x)) for x in c_eff]
    corr_mag: list[float] = []
    corr_re: list[float] = []
    corr_im: list[float] = []
    phase_step: list[float] = []

    for i in range(n):
        j = (i + 1) % n
        mag = amp[i] * amp[j]
        dphi = phi[i] - phi[j]
        corr_mag.append(mag)
        corr_re.append(mag * math.cos(dphi))
        corr_im.append(mag * math.sin(dphi))
        phase_step.append(dphi)

    return {
        "amp": amp,
        "corr_mag": corr_mag,
        "corr_re": corr_re,
        "corr_im": corr_im,
        "phase_step": phase_step,
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG to QM coherence proxy CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, _ = field_extract(hist_state, hist_history)
    c_nohist, _ = field_extract(nohist_state, nohist_history)

    qm_hist = coherence_proxy(c_hist, hist_state.phi)
    qm_nohist = coherence_proxy(c_nohist, nohist_state.phi)
    phase_frozen_hist = coherence_proxy(c_hist, [0.0] * len(hist_state.phi))

    checks = {
        "corr_mag_bounds_pass": all(0.0 <= x <= 1.0 for x in qm_hist["corr_mag"]),
        "corr_parts_bounds_pass": max(max_abs(qm_hist["corr_re"]), max_abs(qm_hist["corr_im"])) <= 1.0,
        "transport_nontrivial_pass": mean([abs(x) for x in qm_hist["corr_im"]]) > 0.05,
        "phase_sensitivity_pass": l1_diff(qm_hist["corr_re"], phase_frozen_hist["corr_re"]) > 0.25,
        "history_imprint_pass": (
            l1_diff(qm_hist["corr_re"], qm_nohist["corr_re"]) + l1_diff(qm_hist["corr_im"], qm_nohist["corr_im"])
        )
        > 0.50,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-006",
        "decision": "pass" if decision else "fail",
        "means": {
            "corr_mag_history_mean": mean(qm_hist["corr_mag"]),
            "corr_re_history_mean": mean(qm_hist["corr_re"]),
            "corr_im_abs_history_mean": mean([abs(x) for x in qm_hist["corr_im"]]),
            "corr_re_present_only_mean": mean(qm_nohist["corr_re"]),
        },
        "max_abs": {
            "corr_re": max_abs(qm_hist["corr_re"]),
            "corr_im": max_abs(qm_hist["corr_im"]),
        },
        "differences": {
            "corr_re_l1_phase_vs_frozen": l1_diff(qm_hist["corr_re"], phase_frozen_hist["corr_re"]),
            "corr_re_l1_history_vs_present_only": l1_diff(qm_hist["corr_re"], qm_nohist["corr_re"]),
            "corr_im_l1_history_vs_present_only": l1_diff(qm_hist["corr_im"], qm_nohist["corr_im"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG To QM Coherence Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- corr_mag_history_mean: `{report['means']['corr_mag_history_mean']:.6f}`",
        f"- corr_re_history_mean: `{report['means']['corr_re_history_mean']:.6f}`",
        f"- corr_im_abs_history_mean: `{report['means']['corr_im_abs_history_mean']:.6f}`",
        f"- max_abs_corr_re: `{report['max_abs']['corr_re']:.6f}`",
        f"- max_abs_corr_im: `{report['max_abs']['corr_im']:.6f}`",
        f"- corr_re_l1(phase vs frozen): `{report['differences']['corr_re_l1_phase_vs_frozen']:.6f}`",
        f"- corr_re_l1(history vs present-only): `{report['differences']['corr_re_l1_history_vs_present_only']:.6f}`",
        f"- corr_im_l1(history vs present-only): `{report['differences']['corr_im_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_qm_coherence_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
