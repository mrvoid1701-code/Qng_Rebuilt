from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from qng_effective_field_reference import field_extract
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-light-cone-proxy-reference-v1"


def mean(v: list[float]) -> float:
    return sum(v) / len(v) if v else 0.0


def std(v: list[float]) -> float:
    m = mean(v)
    return (sum((x - m) ** 2 for x in v) / len(v)) ** 0.5 if len(v) > 1 else 0.0


def light_cone_proxy(g_tt: list[float], g_xx: list[float]) -> list[float]:
    """Per-node effective speed of light from null condition."""
    return [math.sqrt(-gt / gx) for gt, gx in zip(g_tt, g_xx)]


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG light cone proxy CPU test.")
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

    c_eff_hist = light_cone_proxy(asm_hist["g_tt"], asm_hist["g_xx"])
    c_eff_nohist = light_cone_proxy(asm_nohist["g_tt"], asm_nohist["g_xx"])

    mean_hist = mean(c_eff_hist)
    mean_nohist = mean(c_eff_nohist)
    std_hist = std(c_eff_hist)
    std_nohist = std(c_eff_nohist)

    checks = {
        "null_cone_defined_pass": all(c > 0 for c in c_eff_hist),
        "near_normalized_pass": 0.9 < mean_hist < 1.1,
        "spatial_variation_pass": std_hist > 1e-3,
        "history_shifts_mean_pass": abs(mean_hist - mean_nohist) > 1e-3,
        "history_amplifies_variation_pass": std_hist > std_nohist,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-034",
        "decision": "pass" if decision else "fail",
        "history": {
            "c_eff": c_eff_hist,
            "mean": mean_hist,
            "std": std_hist,
            "min": min(c_eff_hist),
            "max": max(c_eff_hist),
        },
        "no_history": {
            "mean": mean_nohist,
            "std": std_nohist,
        },
        "differences": {
            "mean_shift": abs(mean_hist - mean_nohist),
            "std_ratio": std_hist / std_nohist if std_nohist > 0 else float("inf"),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Light Cone Proxy",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- mean c_eff (history): `{mean_hist:.6f}`",
        f"- std c_eff (history): `{std_hist:.6f}`",
        f"- mean c_eff (no-history): `{mean_nohist:.6f}`",
        f"- std c_eff (no-history): `{std_nohist:.6f}`",
        f"- mean shift (history vs nohist): `{abs(mean_hist - mean_nohist):.6f}`",
        f"- std ratio (history/nohist): `{report['differences']['std_ratio']:.2f}x`",
        f"- c_eff range: [{min(c_eff_hist):.6f}, {max(c_eff_hist):.6f}]",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_light_cone_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
