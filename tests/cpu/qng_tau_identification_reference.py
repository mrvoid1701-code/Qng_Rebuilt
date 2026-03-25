from __future__ import annotations

import argparse
import dataclasses
import json
import statistics
from pathlib import Path

from qng_effective_field_reference import field_extract
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-tau-identification-reference-v1"

SEEDS = [20260325, 42, 137, 1729, 2718]


def mean(v: list[float]) -> float:
    return sum(v) / len(v) if v else 0.0


def cv(v: list[float]) -> float:
    m = mean(v)
    return statistics.stdev(v) / m if m != 0 and len(v) > 1 else 0.0


def corr(a: list[float], b: list[float]) -> float:
    n = len(a)
    ma, mb = mean(a), mean(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / n
    sa = (sum((x - ma) ** 2 for x in a) / n) ** 0.5
    sb = (sum((y - mb) ** 2 for y in b) / n) ** 0.5
    return cov / (sa * sb) if sa * sb > 1e-15 else 0.0


def tau_node(c_eff: list[float], l_eff: list[float]) -> list[float]:
    return [l / c if abs(c) > 1e-8 else 0.0 for l, c in zip(l_eff, c_eff)]


def metrics_for_seed(seed: int, cfg_base: Config) -> dict:
    cfg = dataclasses.replace(cfg_base, seed=seed)
    _, hs, hh, _ = run_rollout(cfg, use_history=True)
    _, ns, nh, _ = run_rollout(cfg, use_history=False)
    c_h, l_h = field_extract(hs, hh)
    c_n, l_n = field_extract(ns, nh)
    tau_h = tau_node(c_h, l_h)
    tau_n = tau_node(c_n, l_n)
    mean_h = mean(tau_h)
    mean_n = mean(tau_n)
    return {
        "seed": seed,
        "mean_tau_hist": mean_h,
        "mean_tau_nohist": mean_n,
        "hist_nohist_ratio": mean_h / mean_n if mean_n > 0 else float("inf"),
        "cv_tau_node": cv(tau_h),
        "corr_tau_mem": corr(tau_h, list(hh.mem)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG tau identification CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()

    # config-level tau values
    tau_p = 1.0 / cfg.hist_p_rate
    tau_m = 1.0 / cfg.hist_m_rate
    tau_d = 1.0 / cfg.hist_d_rate
    tau_config = [tau_p, tau_m, tau_d]
    cv_config = cv(tau_config)

    results = [metrics_for_seed(s, cfg) for s in SEEDS]
    default = results[0]

    mean_tau_hist_vals = [r["mean_tau_hist"] for r in results]
    cv_mean_tau_hist = cv(mean_tau_hist_vals)

    checks = {
        "universal_tau_falsified_config_pass": cv_config > 0.1,
        "per_node_tau_not_constant_pass": default["cv_tau_node"] > 0.1,
        "corr_tau_mem_universal_pass": all(r["corr_tau_mem"] > 0.6 for r in results),
        "history_amplifies_tau_all_seeds_pass": all(
            r["mean_tau_hist"] > 2.0 * r["mean_tau_nohist"] for r in results
        ),
        "mean_tau_stable_across_seeds_pass": cv_mean_tau_hist < 0.10,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-038",
        "decision": "pass" if decision else "fail",
        "verdict": (
            "universal tau FALSIFIED; per-node history-driven tau SUPPORTED"
            if decision
            else "inconclusive"
        ),
        "config_timescales": {
            "tau_p": tau_p,
            "tau_m": tau_m,
            "tau_d": tau_d,
            "cv": cv_config,
        },
        "per_seed": results,
        "mean_tau_hist_summary": {
            "values": mean_tau_hist_vals,
            "mean": mean(mean_tau_hist_vals),
            "cv": cv_mean_tau_hist,
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Tau Identification",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- verdict: `{report['verdict']}`",
        "",
        "## Config timescales",
        f"  tau_p={tau_p:.3f}  tau_m={tau_m:.3f}  tau_d={tau_d:.3f}",
        f"  cv = `{cv_config:.4f}` (> 0.1 required)",
        "",
        "## Per-node tau (default seed)",
        f"  cv_tau_node = `{default['cv_tau_node']:.4f}` (> 0.1 required)",
        "",
        "## History amplification",
        *[
            f"  seed {r['seed']}: hist/nohist = `{r['hist_nohist_ratio']:.2f}x`"
            f"  corr(tau,mem) = `{r['corr_tau_mem']:.4f}`"
            for r in results
        ],
        "",
        "## Mean tau stability across seeds",
        f"  values: {[round(v, 4) for v in mean_tau_hist_vals]}",
        f"  cv = `{cv_mean_tau_hist:.4f}` (< 0.10 required)",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_tau_identification_reference: {'PASS' if decision else 'FAIL'}")
    print(f"verdict: {report['verdict']}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
