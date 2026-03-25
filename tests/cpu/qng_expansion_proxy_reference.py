from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import centered_corr, field_extract, l1_diff, mean
from qng_gr_weakfield_proxy_reference import weakfield_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-expansion-proxy-reference-v1"


def expansion_proxy(c_eff: list[float], l_eff: list[float], psi: list[float], eta: float = 0.75) -> dict[str, list[float] | float]:
    x_cos = [c * (1.0 + eta * l) * (1.0 - abs(p)) for c, l, p in zip(c_eff, l_eff, psi)]
    h_cos = mean(x_cos)
    c_cos = max(x_cos) - min(x_cos) if x_cos else 0.0
    return {
        "x_cos": x_cos,
        "h_cos": h_cos,
        "c_cos": c_cos,
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG expansion proxy CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, l_hist = field_extract(hist_state, hist_history)
    c_nohist, l_nohist = field_extract(nohist_state, nohist_history)
    weak_hist = weakfield_proxy(c_hist)
    weak_nohist = weakfield_proxy(c_nohist)

    cos_hist = expansion_proxy(c_hist, l_hist, weak_hist["psi"])
    cos_nohist = expansion_proxy(c_nohist, l_nohist, weak_nohist["psi"])
    cos_mem_off = expansion_proxy(c_hist, [0.0] * len(l_hist), weak_hist["psi"])

    checks = {
        "bounded_pass": max_abs(cos_hist["x_cos"]) < 2.0,
        "activation_positive_pass": cos_hist["h_cos"] > 0.1 and cos_hist["c_cos"] > 1e-3,
        "coherence_sensitivity_pass": centered_corr(cos_hist["x_cos"], c_hist) > 0.50,
        "memory_switch_pass": l1_diff(cos_hist["x_cos"], cos_mem_off["x_cos"]) > 0.05,
        "history_imprint_pass": abs(cos_hist["h_cos"] - cos_nohist["h_cos"]) > 0.05,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-011",
        "decision": "pass" if decision else "fail",
        "cosmology": {
            "h_cos_history": cos_hist["h_cos"],
            "h_cos_present_only": cos_nohist["h_cos"],
            "h_cos_memory_off": cos_mem_off["h_cos"],
            "c_cos_history": cos_hist["c_cos"],
            "c_cos_present_only": cos_nohist["c_cos"],
        },
        "means": {
            "x_cos_history_mean": mean(cos_hist["x_cos"]),
        },
        "max_abs": {
            "x_cos": max_abs(cos_hist["x_cos"]),
        },
        "correlations": {
            "corr_x_cos_c_eff": centered_corr(cos_hist["x_cos"], c_hist),
        },
        "differences": {
            "x_cos_l1_memory_on_vs_off": l1_diff(cos_hist["x_cos"], cos_mem_off["x_cos"]),
            "x_cos_l1_history_vs_present_only": l1_diff(cos_hist["x_cos"], cos_nohist["x_cos"]),
            "h_cos_abs_difference_history_vs_present_only": abs(cos_hist["h_cos"] - cos_nohist["h_cos"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Expansion Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- h_cos_history: `{report['cosmology']['h_cos_history']:.12e}`",
        f"- h_cos_present_only: `{report['cosmology']['h_cos_present_only']:.12e}`",
        f"- h_cos_memory_off: `{report['cosmology']['h_cos_memory_off']:.12e}`",
        f"- c_cos_history: `{report['cosmology']['c_cos_history']:.12e}`",
        f"- max_abs_x_cos: `{report['max_abs']['x_cos']:.12e}`",
        f"- corr_x_cos_c_eff: `{report['correlations']['corr_x_cos_c_eff']:.6f}`",
        f"- x_cos_l1(memory on vs off): `{report['differences']['x_cos_l1_memory_on_vs_off']:.12e}`",
        f"- x_cos_l1(history vs present-only): `{report['differences']['x_cos_l1_history_vs_present_only']:.12e}`",
        f"- h_cos_abs_difference(history vs present-only): `{report['differences']['h_cos_abs_difference_history_vs_present_only']:.12e}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_expansion_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
