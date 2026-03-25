from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import field_extract, l1_diff, mean
from qng_gr_weakfield_proxy_reference import weakfield_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-timing-delay-proxy-reference-v1"


def edge_mean(values: list[float]) -> list[float]:
    n = len(values)
    return [0.5 * (values[i] + values[(i + 1) % n]) for i in range(n)]


def timing_proxy(l_eff: list[float], psi: list[float]) -> dict[str, list[float] | float]:
    l_edge = edge_mean(l_eff)
    psi_edge = edge_mean([abs(x) for x in psi])
    t_edge = [l * p for l, p in zip(l_edge, psi_edge)]
    d_time = sum(t_edge)
    w_time = sum(abs(t_edge[(i + 1) % len(t_edge)] - t_edge[i]) for i in range(len(t_edge)))
    return {
        "l_edge": l_edge,
        "psi_edge": psi_edge,
        "t_edge": t_edge,
        "d_time": d_time,
        "w_time": w_time,
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG timing delay proxy CPU test.")
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

    time_hist = timing_proxy(l_hist, weak_hist["psi"])
    time_nohist = timing_proxy(l_nohist, weak_nohist["psi"])
    time_mem_off = timing_proxy([0.0] * len(l_hist), weak_hist["psi"])

    checks = {
        "bounded_pass": max_abs(time_hist["t_edge"]) < 0.05,
        "delay_nontrivial_pass": time_hist["d_time"] > 1e-3,
        "memory_switch_pass": l1_diff(time_hist["t_edge"], time_mem_off["t_edge"]) > 1e-3,
        "history_imprint_pass": abs(time_hist["d_time"] - time_nohist["d_time"]) > 1e-3,
        "distortion_nontrivial_pass": time_hist["w_time"] > 1e-3,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-010",
        "decision": "pass" if decision else "fail",
        "timing": {
            "d_time_history": time_hist["d_time"],
            "d_time_present_only": time_nohist["d_time"],
            "d_time_memory_off": time_mem_off["d_time"],
            "w_time_history": time_hist["w_time"],
            "w_time_present_only": time_nohist["w_time"],
        },
        "means": {
            "t_edge_history_mean": mean(time_hist["t_edge"]),
            "psi_edge_history_mean": mean(time_hist["psi_edge"]),
        },
        "max_abs": {
            "t_edge": max_abs(time_hist["t_edge"]),
        },
        "differences": {
            "t_edge_l1_history_vs_present_only": l1_diff(time_hist["t_edge"], time_nohist["t_edge"]),
            "t_edge_l1_memory_on_vs_off": l1_diff(time_hist["t_edge"], time_mem_off["t_edge"]),
            "d_time_abs_difference_history_vs_present_only": abs(time_hist["d_time"] - time_nohist["d_time"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Timing Delay Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- d_time_history: `{report['timing']['d_time_history']:.12e}`",
        f"- d_time_present_only: `{report['timing']['d_time_present_only']:.12e}`",
        f"- d_time_memory_off: `{report['timing']['d_time_memory_off']:.12e}`",
        f"- w_time_history: `{report['timing']['w_time_history']:.12e}`",
        f"- w_time_present_only: `{report['timing']['w_time_present_only']:.12e}`",
        f"- max_abs_t_edge: `{report['max_abs']['t_edge']:.12e}`",
        f"- t_edge_l1(history vs present-only): `{report['differences']['t_edge_l1_history_vs_present_only']:.12e}`",
        f"- t_edge_l1(memory on vs off): `{report['differences']['t_edge_l1_memory_on_vs_off']:.12e}`",
        f"- d_time_abs_difference(history vs present-only): `{report['differences']['d_time_abs_difference_history_vs_present_only']:.12e}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_timing_delay_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
