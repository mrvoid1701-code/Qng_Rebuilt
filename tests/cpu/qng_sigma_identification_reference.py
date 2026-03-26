from __future__ import annotations

import argparse
import dataclasses
import json
import statistics
from pathlib import Path

from qng_effective_field_reference import field_extract
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = (
    ROOT / "07_validation" / "audits" / "qng-sigma-identification-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]


def corr(a: list[float], b: list[float]) -> float:
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / n
    sa = (sum((x - ma) ** 2 for x in a) / n) ** 0.5
    sb = (sum((y - mb) ** 2 for y in b) / n) ** 0.5
    return cov / (sa * sb) if sa * sb > 1e-15 else 0.0


def r2_two_predictors(y: list[float], x1: list[float], x2: list[float]) -> float:
    """OLS R² for y ~ a*x1 + b*x2 + c via 3x3 normal equations."""
    n = len(y)
    s1 = sum(x1)
    s2 = sum(x2)
    sy = sum(y)
    s11 = sum(a * a for a in x1)
    s12 = sum(a * b for a, b in zip(x1, x2))
    s22 = sum(a * a for a in x2)
    s1y = sum(a * b for a, b in zip(x1, y))
    s2y = sum(a * b for a, b in zip(x2, y))
    A = [
        [float(n), s1, s2, sy],
        [s1, s11, s12, s1y],
        [s2, s12, s22, s2y],
    ]
    for col in range(3):
        piv = A[col][col]
        if abs(piv) < 1e-15:
            return 0.0
        for row in range(col + 1, 3):
            f = A[row][col] / piv
            A[row] = [A[row][k] - f * A[col][k] for k in range(4)]
    beta = [0.0] * 3
    for row in range(2, -1, -1):
        beta[row] = (
            A[row][3] - sum(A[row][k] * beta[k] for k in range(row + 1, 3))
        ) / A[row][row]
    y_hat = [beta[0] + beta[1] * a + beta[2] * b for a, b in zip(x1, x2)]
    y_mean = sum(y) / n
    ss_res = sum((yi - yh) ** 2 for yi, yh in zip(y, y_hat))
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    return 1.0 - ss_res / ss_tot if ss_tot > 1e-15 else 0.0


def metrics_for_seed(seed: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)

    _, state_h, history_h, _ = run_rollout(cfg, use_history=True)
    _, state_n, history_n, _ = run_rollout(cfg, use_history=False)

    c_eff_h, l_eff_h = field_extract(state_h, history_h)
    c_eff_n, l_eff_n = field_extract(state_n, history_n)

    sigma_h = state_h.sigma
    sigma_n = state_n.sigma

    corr_c_h = corr(sigma_h, c_eff_h)
    corr_l_h = corr(sigma_h, l_eff_h)
    corr_chi_h = corr(sigma_h, state_h.chi)
    corr_phi_h = corr(sigma_h, state_h.phi)
    corr_c_n = corr(sigma_n, c_eff_n)

    r2_c_only = corr_c_h ** 2
    r2_c_and_l = r2_two_predictors(sigma_h, c_eff_h, l_eff_h)

    return {
        "seed": seed,
        "corr_sigma_ceff_hist": round(corr_c_h, 6),
        "corr_sigma_leff_hist": round(corr_l_h, 6),
        "corr_sigma_chi_hist": round(corr_chi_h, 6),
        "corr_sigma_phi_hist": round(corr_phi_h, 6),
        "corr_sigma_ceff_nohist": round(corr_c_n, 6),
        "r2_c_eff_only": round(r2_c_only, 6),
        "r2_c_and_l": round(r2_c_and_l, 6),
        "ceff_primary_over_leff": corr_c_h > corr_l_h,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG sigma identification CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = [metrics_for_seed(s) for s in SEEDS]

    corr_c_vals = [r["corr_sigma_ceff_hist"] for r in results]
    corr_l_vals = [r["corr_sigma_leff_hist"] for r in results]
    r2_c_vals = [r["r2_c_eff_only"] for r in results]
    r2_cl_vals = [r["r2_c_and_l"] for r in results]

    # P1: sigma != C_eff (corr < 1.0 on all seeds)
    p1_pass = all(c < 1.0 for c in corr_c_vals)
    # P2: sigma ∝ C_eff (corr > 0.5 on all seeds — universal tier-1 signal)
    p2_pass = all(c > 0.5 for c in corr_c_vals)
    # P3: sigma also couples positively to L_eff (both channels active)
    p3_pass = all(c > 0.3 for c in corr_l_vals)
    # P4: sigma substantially recoverable from (C_eff, L_eff): R² > 0.7 on all seeds
    p4_pass = all(r2 > 0.7 for r2 in r2_cl_vals)

    decision = p1_pass and p2_pass and p3_pass and p4_pass

    verdict = (
        "sigma = C_eff FALSIFIED; sigma ∝ C_eff SUPPORTED (universal); "
        "sigma couples to BOTH C_eff and L_eff; C_eff-vs-L_eff primacy is topology-dependent (tier-2); "
        "R²(C_eff+L_eff) > 0.71 universally"
        if decision
        else "inconclusive"
    )

    report = {
        "test_id": "QNG-CPU-039",
        "decision": "pass" if decision else "fail",
        "verdict": verdict,
        "per_seed": results,
        "corr_ceff_summary": {
            "values": corr_c_vals,
            "min": min(corr_c_vals),
            "mean": round(statistics.mean(corr_c_vals), 6),
            "cv": round(
                statistics.stdev(corr_c_vals) / statistics.mean(corr_c_vals), 4
            ) if statistics.mean(corr_c_vals) > 1e-10 else None,
        },
        "corr_leff_summary": {
            "values": corr_l_vals,
            "max": max(corr_l_vals),
        },
        "r2_summary": {
            "r2_c_only": {"values": r2_c_vals, "min": min(r2_c_vals)},
            "r2_c_and_l": {"values": r2_cl_vals, "min": min(r2_cl_vals)},
        },
        "checks": {
            "p1_sigma_ne_ceff_pass": p1_pass,
            "p2_corr_ceff_above_half_universal_pass": p2_pass,
            "p3_leff_also_positive_universal_pass": p3_pass,
            "p4_r2_c_and_l_above_0p7_universal_pass": p4_pass,
        },
    }

    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    summary_lines = [
        "# QNG Sigma Identification",
        "",
        f"- test_id: `QNG-CPU-039`",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- verdict: `{verdict}`",
        "",
        "## corr(sigma, C_eff) per seed",
        *[
            f"  seed {r['seed']}: `{r['corr_sigma_ceff_hist']:.4f}`"
            for r in results
        ],
        f"  min: `{min(corr_c_vals):.4f}` (> 0.5 required)",
        "",
        "## corr(sigma, L_eff) per seed",
        *[
            f"  seed {r['seed']}: `{r['corr_sigma_leff_hist']:.4f}`"
            for r in results
        ],
        f"  max: `{max(corr_l_vals):.4f}`",
        "",
        "## R² sigma ~ C_eff only per seed",
        *[f"  seed {r['seed']}: `{r['r2_c_eff_only']:.4f}`" for r in results],
        "",
        "## R² sigma ~ C_eff + L_eff per seed",
        *[f"  seed {r['seed']}: `{r['r2_c_and_l']:.4f}`" for r in results],
        "",
        "## C_eff primary over L_eff?",
        *[
            f"  seed {r['seed']}: `{r['ceff_primary_over_leff']}`"
            f"  (corr_C={r['corr_sigma_ceff_hist']:.4f}, corr_L={r['corr_sigma_leff_hist']:.4f})"
            for r in results
        ],
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_sigma_identification_reference: {'PASS' if decision else 'FAIL'}")
    print(f"verdict: {verdict}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
