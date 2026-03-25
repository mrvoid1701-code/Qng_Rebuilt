from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from qng_native_update_reference import Config, History, State, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-effective-field-reference-v1"


def clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def field_extract(state: State, history: History) -> tuple[list[float], list[float]]:
    c_eff: list[float] = []
    l_eff: list[float] = []

    for sigma_i, chi_i, _, mem_i, mismatch_i, phase_i in zip(
        state.sigma,
        state.chi,
        state.phi,
        history.mem,
        history.mismatch,
        history.phase,
    ):
        coherence = clip01(
            0.45 * sigma_i
            + 0.35 * (1.0 - mismatch_i)
            + 0.20 * (1.0 + math.cos(phase_i)) / 2.0
        )
        load = clip01(0.60 * mem_i + 0.40 * min(abs(chi_i), 1.0))
        c_eff.append(coherence)
        l_eff.append(load)

    return c_eff, l_eff


def centered_corr(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    ma = mean(a)
    mb = mean(b)
    da = [x - ma for x in a]
    db = [y - mb for y in b]
    num = sum(x * y for x, y in zip(da, db))
    den_a = math.sqrt(sum(x * x for x in da))
    den_b = math.sqrt(sum(y * y for y in db))
    if den_a == 0.0 or den_b == 0.0:
        return 0.0
    return num / (den_a * den_b)


def l1_diff(a: list[float], b: list[float]) -> float:
    return sum(abs(x - y) for x, y in zip(a, b))


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG effective field reference CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, l_hist = field_extract(hist_state, hist_history)
    c_nohist, l_nohist = field_extract(nohist_state, nohist_history)

    checks = {
        "c_eff_bounds_pass": all(0.0 <= x <= 1.0 for x in c_hist),
        "l_eff_bounds_pass": all(0.0 <= x <= 1.0 for x in l_hist),
        "c_eff_sigma_positive_pass": centered_corr(c_hist, hist_state.sigma) > 0.25,
        "c_eff_mismatch_negative_pass": centered_corr(c_hist, hist_history.mismatch) < -0.25,
        "l_eff_mem_positive_pass": centered_corr(l_hist, hist_history.mem) > 0.25,
        "history_imprint_pass": l1_diff(c_hist, c_nohist) + l1_diff(l_hist, l_nohist) > 0.25,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-003",
        "decision": "pass" if decision else "fail",
        "means": {
            "c_eff_history_mean": mean(c_hist),
            "c_eff_present_only_mean": mean(c_nohist),
            "l_eff_history_mean": mean(l_hist),
            "l_eff_present_only_mean": mean(l_nohist),
        },
        "correlations": {
            "corr_c_eff_sigma": centered_corr(c_hist, hist_state.sigma),
            "corr_c_eff_mismatch": centered_corr(c_hist, hist_history.mismatch),
            "corr_l_eff_mem": centered_corr(l_hist, hist_history.mem),
        },
        "differences": {
            "c_eff_l1_history_vs_present_only": l1_diff(c_hist, c_nohist),
            "l_eff_l1_history_vs_present_only": l1_diff(l_hist, l_nohist),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Effective Field Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- c_eff_history_mean: `{report['means']['c_eff_history_mean']:.6f}`",
        f"- c_eff_present_only_mean: `{report['means']['c_eff_present_only_mean']:.6f}`",
        f"- l_eff_history_mean: `{report['means']['l_eff_history_mean']:.6f}`",
        f"- l_eff_present_only_mean: `{report['means']['l_eff_present_only_mean']:.6f}`",
        f"- corr_c_eff_sigma: `{report['correlations']['corr_c_eff_sigma']:.6f}`",
        f"- corr_c_eff_mismatch: `{report['correlations']['corr_c_eff_mismatch']:.6f}`",
        f"- corr_l_eff_mem: `{report['correlations']['corr_l_eff_mem']:.6f}`",
        f"- c_eff_l1(history vs present-only): `{report['differences']['c_eff_l1_history_vs_present_only']:.6f}`",
        f"- l_eff_l1(history vs present-only): `{report['differences']['l_eff_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_effective_field_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
