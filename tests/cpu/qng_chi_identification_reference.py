from __future__ import annotations

import argparse
import dataclasses
import json
import statistics
from pathlib import Path

from qng_effective_field_reference import field_extract
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_light_cone_proxy_reference import light_cone_proxy
from qng_matter_sector_proxy_reference import matter_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-chi-identification-reference-v1"

SEEDS = [20260325, 42, 137, 1729, 2718]


def corr(a: list[float], b: list[float]) -> float:
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / n
    sa = (sum((x - ma) ** 2 for x in a) / n) ** 0.5
    sb = (sum((y - mb) ** 2 for y in b) / n) ** 0.5
    return cov / (sa * sb) if sa * sb > 1e-15 else 0.0


def metrics_for_seed(seed: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)
    _, state, history, _ = run_rollout(cfg, use_history=True)
    c_eff_field, l_eff = field_extract(state, history)
    m_eff = matter_proxy(c_eff_field, l_eff, state.phi)["m_eff"]
    asm = assemble_linearized_metric(c_eff_field, state.phi)
    c_eff_lc = light_cone_proxy(asm["g_tt"], asm["g_xx"])
    m_over_c = [m / c for m, c in zip(m_eff, c_eff_lc)]
    chi = state.chi
    return {
        "seed": seed,
        "corr_chi_mc": corr(chi, m_over_c),
        "corr_chi_leff": corr(chi, l_eff),
        "corr_chi_meff": corr(chi, m_eff),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG chi identification CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = [metrics_for_seed(s) for s in SEEDS]

    default = results[0]
    corr_mc_vals = [r["corr_chi_mc"] for r in results]
    corr_leff_vals = [r["corr_chi_leff"] for r in results]
    std_mc = statistics.stdev(corr_mc_vals)

    checks = {
        "chi_mc_weak_default_pass": default["corr_chi_mc"] < 0.5,
        "chi_mc_not_universal_pass": std_mc > 0.15,
        "chi_leff_strong_default_pass": default["corr_chi_leff"] > 0.5,
        "leff_dominates_mc_default_pass": (
            default["corr_chi_leff"] - default["corr_chi_mc"] > 0.3
        ),
        "chi_leff_universal_pass": all(c > 0.5 for c in corr_leff_vals),
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-037",
        "decision": "pass" if decision else "fail",
        "verdict": (
            "chi = m/c FALSIFIED at proxy level; chi ∝ L_eff SUPPORTED"
            if decision
            else "inconclusive"
        ),
        "per_seed": results,
        "corr_mc_summary": {
            "values": corr_mc_vals,
            "std": std_mc,
        },
        "corr_leff_summary": {
            "values": corr_leff_vals,
            "min": min(corr_leff_vals),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Chi Identification",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- verdict: `{report['verdict']}`",
        "",
        "## corr(chi, m/c) per seed",
        *[f"  seed {r['seed']}: `{r['corr_chi_mc']:.4f}`" for r in results],
        f"  std: `{std_mc:.4f}` (> 0.15 required for non-universality)",
        "",
        "## corr(chi, L_eff) per seed",
        *[f"  seed {r['seed']}: `{r['corr_chi_leff']:.4f}`" for r in results],
        f"  min: `{min(corr_leff_vals):.4f}` (> 0.5 required for universality)",
        "",
        "## default seed dominance",
        f"  corr(chi, L_eff) - corr(chi, m/c) = "
        f"`{default['corr_chi_leff'] - default['corr_chi_mc']:.4f}` (> 0.3 required)",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_chi_identification_reference: {'PASS' if decision else 'FAIL'}")
    print(f"verdict: {report['verdict']}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
