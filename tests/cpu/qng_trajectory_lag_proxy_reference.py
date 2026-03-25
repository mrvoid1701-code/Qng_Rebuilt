from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import field_extract, l1_diff
from qng_gr_weakfield_proxy_reference import weakfield_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-trajectory-lag-proxy-reference-v1"


def edge_mean(values: list[float]) -> list[float]:
    n = len(values)
    return [0.5 * (values[i] + values[(i + 1) % n]) for i in range(n)]


def trajectory_proxy(l_eff: list[float], accel: list[float]) -> dict[str, float | list[float]]:
    l_edge = edge_mean(l_eff)
    a_edge = edge_mean(accel)
    r_edge = [l * a for l, a in zip(l_edge, a_edge)]
    a_trj = sum(r_edge)
    s_trj = sum(abs(x) for x in r_edge)
    return {
        "l_edge": l_edge,
        "a_edge": a_edge,
        "r_edge": r_edge,
        "a_trj": a_trj,
        "s_trj": s_trj,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG trajectory lag proxy CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    _, l_hist = field_extract(hist_state, hist_history)
    _, l_nohist = field_extract(nohist_state, nohist_history)

    weak_hist = weakfield_proxy(field_extract(hist_state, hist_history)[0])
    weak_nohist = weakfield_proxy(field_extract(nohist_state, nohist_history)[0])

    trj_hist = trajectory_proxy(l_hist, weak_hist["accel"])
    trj_nohist = trajectory_proxy(l_nohist, weak_nohist["accel"])
    trj_reversed = trajectory_proxy(l_hist, [-x for x in weak_hist["accel"]])

    checks = {
        "lag_strength_nontrivial_pass": trj_hist["s_trj"] > 1e-3,
        "history_imprint_pass": abs(trj_hist["s_trj"] - trj_nohist["s_trj"]) > 5e-4,
        "direction_reversal_pass": abs(trj_hist["a_trj"] + trj_reversed["a_trj"]) < 1e-12,
        "bounded_inputs_pass": max(l_hist) <= 1.0 and max(abs(x) for x in weak_hist["accel"]) < 0.1,
        "edge_pattern_history_pass": l1_diff(trj_hist["r_edge"], trj_nohist["r_edge"]) > 1e-3,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-007",
        "decision": "pass" if decision else "fail",
        "trajectory": {
            "a_trj_history": trj_hist["a_trj"],
            "a_trj_present_only": trj_nohist["a_trj"],
            "a_trj_reversed": trj_reversed["a_trj"],
            "s_trj_history": trj_hist["s_trj"],
            "s_trj_present_only": trj_nohist["s_trj"],
        },
        "differences": {
            "s_trj_abs_difference": abs(trj_hist["s_trj"] - trj_nohist["s_trj"]),
            "r_edge_l1_history_vs_present_only": l1_diff(trj_hist["r_edge"], trj_nohist["r_edge"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Trajectory Lag Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- a_trj_history: `{report['trajectory']['a_trj_history']:.12e}`",
        f"- a_trj_present_only: `{report['trajectory']['a_trj_present_only']:.12e}`",
        f"- a_trj_reversed: `{report['trajectory']['a_trj_reversed']:.12e}`",
        f"- s_trj_history: `{report['trajectory']['s_trj_history']:.12e}`",
        f"- s_trj_present_only: `{report['trajectory']['s_trj_present_only']:.12e}`",
        f"- s_trj_abs_difference: `{report['differences']['s_trj_abs_difference']:.12e}`",
        f"- r_edge_l1(history vs present-only): `{report['differences']['r_edge_l1_history_vs_present_only']:.12e}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_trajectory_lag_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
