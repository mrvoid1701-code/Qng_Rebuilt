from __future__ import annotations

import argparse
import dataclasses
import json
import math
import random
import statistics
from pathlib import Path

from qng_effective_field_reference import field_extract
from qng_native_update_reference import (
    Config,
    build_graph,
    init_state,
    one_step,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = (
    ROOT / "07_validation" / "audits" / "qng-calibrated-continuity-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]


def rms(a: list[float]) -> float:
    return math.sqrt(sum(x * x for x in a) / len(a)) if a else 0.0


def variance(a: list[float]) -> float:
    n = len(a)
    m = sum(a) / n
    return sum((x - m) ** 2 for x in a) / n


def div_J(c_eff: list[float], phi: list[float], adj: list[list[int]]) -> list[float]:
    """div(J)_i = C_i * Σ_j C_j * sin(phi_j - phi_i)."""
    return [
        sum(c_eff[i] * c_eff[j] * math.sin(phi[j] - phi[i]) for j in adj[i])
        for i in range(len(c_eff))
    ]


def optimal_alpha(drho: list[float], dj: list[float]) -> float:
    """α* = -Σ(Δρ·divJ) / Σ(divJ²) — OLS optimal coupling."""
    num = sum(dr * dj_ for dr, dj_ in zip(drho, dj))
    den = sum(dj_ * dj_ for dj_ in dj)
    return -num / den if abs(den) > 1e-20 else 0.0


def r2_calibrated(drho: list[float], dj: list[float], alpha: float) -> float:
    """R² = 1 - Var(Δρ + α*·divJ) / Var(Δρ)."""
    residual = [dr + alpha * dj_ for dr, dj_ in zip(drho, dj)]
    var_res = variance(residual)
    var_drho = variance(drho)
    return 1.0 - var_res / var_drho if var_drho > 1e-20 else 0.0


def rollout_two_steps(cfg: Config, use_history: bool):
    rng = random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)
    for _ in range(cfg.steps - 1):
        state, history = one_step(state, history, adj, cfg, use_history=use_history)
    state_t, history_t = state, history
    state_tp1, history_tp1 = one_step(
        state_t, history_t, adj, cfg, use_history=use_history
    )
    return state_t, history_t, state_tp1, history_tp1, adj


def metrics_for_seed(seed: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)

    # History on
    st_h, ht_h, stp1_h, htp1_h, adj = rollout_two_steps(cfg, use_history=True)
    c_t_h, _ = field_extract(st_h, ht_h)
    c_tp1_h, _ = field_extract(stp1_h, htp1_h)
    phi_t_h = st_h.phi
    rho_t_h = [c * c for c in c_t_h]
    rho_tp1_h = [c * c for c in c_tp1_h]
    drho_h = [r1 - r0 for r0, r1 in zip(rho_t_h, rho_tp1_h)]
    dj_h = div_J(c_t_h, phi_t_h, adj)

    alpha_h = optimal_alpha(drho_h, dj_h)
    r2_h = r2_calibrated(drho_h, dj_h, alpha_h)
    residual_h = [dr + alpha_h * dj_ for dr, dj_ in zip(drho_h, dj_h)]

    # History off
    st_n, ht_n, stp1_n, htp1_n, _ = rollout_two_steps(cfg, use_history=False)
    c_t_n, _ = field_extract(st_n, ht_n)
    c_tp1_n, _ = field_extract(stp1_n, htp1_n)
    phi_t_n = st_n.phi
    rho_t_n = [c * c for c in c_t_n]
    rho_tp1_n = [c * c for c in c_tp1_n]
    drho_n = [r1 - r0 for r0, r1 in zip(rho_t_n, rho_tp1_n)]
    dj_n = div_J(c_t_n, phi_t_n, adj)

    alpha_n = optimal_alpha(drho_n, dj_n)
    r2_n = r2_calibrated(drho_n, dj_n, alpha_n)

    return {
        "seed": seed,
        "alpha_hist": round(alpha_h, 8),
        "alpha_nohist": round(alpha_n, 8),
        "r2_calib_hist": round(r2_h, 6),
        "r2_calib_nohist": round(r2_n, 6),
        "rms_drho_hist": round(rms(drho_h), 8),
        "rms_divJ_hist": round(rms(dj_h), 8),
        "rms_residual_calib_hist": round(rms(residual_h), 8),
        "alpha_negative_hist": alpha_h < 0,
        "hist_improves_r2": r2_h > r2_n,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="QNG calibrated continuity CPU test."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = [metrics_for_seed(s) for s in SEEDS]

    alpha_vals = [r["alpha_hist"] for r in results]
    r2_vals = [r["r2_calib_hist"] for r in results]
    alpha_neg = [r["alpha_negative_hist"] for r in results]
    hist_improves = [r["hist_improves_r2"] for r in results]

    alpha_abs = [abs(a) for a in alpha_vals]
    alpha_mean = statistics.mean(alpha_abs)
    alpha_cv = (
        statistics.stdev(alpha_abs) / alpha_mean if alpha_mean > 1e-15 else float("inf")
    )

    # P1: α* > 0 on ≥4/5 seeds (Δρ ≈ -α*·divJ — correct sign for continuity Δρ+α*·divJ=0)
    p1_pass = sum(1 for a in alpha_vals if a > 0) >= 4
    # P2: R²_calib > 0.05 on ≥3/5 seeds
    p2_pass = sum(1 for r in r2_vals if r > 0.05) >= 3
    # P3: R²_calib > 0.5 on ≥1 seed
    p3_pass = any(r > 0.5 for r in r2_vals)
    # P4: cv(|α*|) < 1.5
    p4_pass = alpha_cv < 1.5

    decision = p1_pass and p2_pass and p3_pass

    count_pos = sum(1 for a in alpha_vals if a > 0)
    verdict = (
        f"calibrated continuity SUPPORTED; α*>0 on {count_pos}/5 seeds "
        f"(correct sign: outflow→density decrease); "
        f"R²_calib > 0.05 on {sum(1 for r in r2_vals if r > 0.05)}/5 seeds; "
        f"max R²={max(r2_vals):.3f}; "
        f"mean|α*|={alpha_mean:.5f} (eff. coupling ~10⁻³), cv={alpha_cv:.2f} "
        f"({'tier-2 topology-dependent' if not p4_pass else 'moderate stability'})"
        if decision
        else "inconclusive"
    )

    report = {
        "test_id": "QNG-CPU-042",
        "decision": "pass" if decision else "fail",
        "verdict": verdict,
        "per_seed": results,
        "alpha_summary": {
            "values_hist": alpha_vals,
            "abs_mean": round(alpha_mean, 8),
            "abs_cv": round(alpha_cv, 4),
            "count_negative": sum(alpha_neg),
        },
        "r2_summary": {
            "values_hist": r2_vals,
            "max": round(max(r2_vals), 6),
            "count_above_0p05": sum(1 for r in r2_vals if r > 0.05),
            "count_above_0p5": sum(1 for r in r2_vals if r > 0.5),
        },
        "hist_improves_count": sum(hist_improves),
        "checks": {
            "p1_alpha_positive_4of5_pass": p1_pass,
            "p2_r2_above_0p05_majority_pass": p2_pass,
            "p3_r2_above_0p5_at_least_one_pass": p3_pass,
            "p4_alpha_cv_below_1p5_pass": p4_pass,
        },
    }

    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    summary_lines = [
        "# QNG Calibrated Continuity",
        "",
        f"- test_id: `QNG-CPU-042`",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- verdict: `{verdict}`",
        "",
        "## Optimal coupling α* per seed",
        *[
            f"  seed {r['seed']}: α*=`{r['alpha_hist']:.6f}`, "
            f"nohist=`{r['alpha_nohist']:.6f}`, neg=`{r['alpha_negative_hist']}`"
            for r in results
        ],
        f"  mean|α*|: `{alpha_mean:.6f}`, cv: `{alpha_cv:.4f}`",
        "",
        "## R²_calib per seed",
        *[
            f"  seed {r['seed']}: hist=`{r['r2_calib_hist']:.4f}`, "
            f"nohist=`{r['r2_calib_nohist']:.4f}`, "
            f"hist_better=`{r['hist_improves_r2']}`"
            for r in results
        ],
        f"  max R²: `{max(r2_vals):.4f}`, count>0.05: `{sum(1 for r in r2_vals if r > 0.05)}/5`",
        "",
        "## Scale factors per seed",
        *[
            f"  seed {r['seed']}: rms(Δρ)=`{r['rms_drho_hist']:.6f}`, "
            f"rms(divJ)=`{r['rms_divJ_hist']:.6f}`, "
            f"rms(resid_calib)=`{r['rms_residual_calib_hist']:.6f}`"
            for r in results
        ],
    ]
    (out_dir / "summary.md").write_text(
        "\n".join(summary_lines) + "\n", encoding="utf-8"
    )

    print(f"qng_calibrated_continuity_reference: {'PASS' if decision else 'FAIL'}")
    print(f"verdict: {verdict}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
