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
    ROOT / "07_validation" / "audits" / "qng-madelung-amplitude-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]

# Reference R²_std from QNG-CPU-042
R2_STD = [0.045617, 0.138356, 0.572227, 0.034704, 0.207112]
ALPHA_STD_CV = 0.7612


def variance(a: list[float]) -> float:
    n = len(a)
    m = sum(a) / n
    return sum((x - m) ** 2 for x in a) / n


def div_J_madelung(
    c_eff: list[float], phi: list[float], adj: list[list[int]]
) -> list[float]:
    """div(J_M)_i = sqrt(C_i) · Σ_j sqrt(C_j) · sin(phi_j - phi_i)."""
    sqrt_c = [math.sqrt(max(c, 0.0)) for c in c_eff]
    return [
        sqrt_c[i] * sum(sqrt_c[j] * math.sin(phi[j] - phi[i]) for j in adj[i])
        for i in range(len(c_eff))
    ]


def div_J_standard(
    c_eff: list[float], phi: list[float], adj: list[list[int]]
) -> list[float]:
    """div(J_std)_i = C_i · Σ_j C_j · sin(phi_j - phi_i)."""
    return [
        c_eff[i] * sum(c_eff[j] * math.sin(phi[j] - phi[i]) for j in adj[i])
        for i in range(len(c_eff))
    ]


def optimal_alpha(drho: list[float], dj: list[float]) -> float:
    num = sum(dr * dj_ for dr, dj_ in zip(drho, dj))
    den = sum(dj_ * dj_ for dj_ in dj)
    return -num / den if abs(den) > 1e-20 else 0.0


def r2_calibrated(drho: list[float], dj: list[float], alpha: float) -> float:
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


def metrics_for_seed(seed: int, r2_std_ref: float) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)

    st_h, ht_h, stp1_h, htp1_h, adj = rollout_two_steps(cfg, use_history=True)
    c_t, _ = field_extract(st_h, ht_h)
    c_tp1, _ = field_extract(stp1_h, htp1_h)
    phi_t = st_h.phi

    # Madelung: ρ_M = C_eff
    drho_m = [c1 - c0 for c0, c1 in zip(c_t, c_tp1)]
    dj_m = div_J_madelung(c_t, phi_t, adj)
    alpha_m = optimal_alpha(drho_m, dj_m)
    r2_m = r2_calibrated(drho_m, dj_m, alpha_m)

    # Standard: ρ_std = C_eff² (recomputed for direct comparison)
    drho_s = [c1 * c1 - c0 * c0 for c0, c1 in zip(c_t, c_tp1)]
    dj_s = div_J_standard(c_t, phi_t, adj)
    alpha_s = optimal_alpha(drho_s, dj_s)
    r2_s = r2_calibrated(drho_s, dj_s, alpha_s)

    scale_ratio_m = (
        math.sqrt(sum(d * d for d in dj_m) / len(dj_m))
        / math.sqrt(sum(d * d for d in drho_m) / len(drho_m))
        if any(d != 0 for d in drho_m)
        else float("inf")
    )

    return {
        "seed": seed,
        "alpha_madelung": round(alpha_m, 8),
        "alpha_standard": round(alpha_s, 8),
        "r2_madelung": round(r2_m, 6),
        "r2_standard": round(r2_s, 6),
        "r2_std_reference": round(r2_std_ref, 6),
        "madelung_beats_standard": r2_m > r2_s,
        "alpha_m_positive": alpha_m > 0,
        "scale_ratio_madelung": round(scale_ratio_m, 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="QNG Madelung amplitude proxy CPU test."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = [metrics_for_seed(s, r2s) for s, r2s in zip(SEEDS, R2_STD)]

    alpha_m_vals = [r["alpha_madelung"] for r in results]
    r2_m_vals = [r["r2_madelung"] for r in results]
    r2_s_vals = [r["r2_standard"] for r in results]
    beats = [r["madelung_beats_standard"] for r in results]
    alpha_pos = [r["alpha_m_positive"] for r in results]

    alpha_abs = [abs(a) for a in alpha_m_vals]
    alpha_mean = statistics.mean(alpha_abs)
    alpha_cv = (
        statistics.stdev(alpha_abs) / alpha_mean
        if alpha_mean > 1e-15
        else float("inf")
    )
    mean_r2_m = statistics.mean(r2_m_vals)
    mean_r2_s = statistics.mean(r2_s_vals)

    # P1: α*_M > 0 on ≥4/5 seeds
    p1_pass = sum(alpha_pos) >= 4
    # P2: max(R²_M) > 0.5 on ≥1 seed
    p2_pass = any(r > 0.5 for r in r2_m_vals)
    # P3: mean R²_M > mean R²_std (= 0.200 from QNG-CPU-042)
    p3_pass = mean_r2_m > mean_r2_s
    # P4: cv(|α*_M|) ≤ 0.76
    p4_pass = alpha_cv <= ALPHA_STD_CV

    decision = p1_pass and p2_pass and (p3_pass or p4_pass)

    madelung_wins = sum(beats)
    verdict = (
        f"Madelung amplitude ψ_M=sqrt(C_eff)·exp(i·phi) SUPPORTED; "
        f"α*_M>0 on {sum(alpha_pos)}/5 seeds; "
        f"max R²_M={max(r2_m_vals):.3f}; "
        f"mean R²_M={mean_r2_m:.3f} vs mean R²_std={mean_r2_s:.3f}; "
        f"Madelung beats standard on {madelung_wins}/5 seeds; "
        f"mean|α*_M|={alpha_mean:.5f}, cv={alpha_cv:.2f}"
        if decision
        else "inconclusive"
    )

    report = {
        "test_id": "QNG-CPU-043",
        "decision": "pass" if decision else "fail",
        "verdict": verdict,
        "per_seed": results,
        "alpha_madelung_summary": {
            "values": alpha_m_vals,
            "abs_mean": round(alpha_mean, 8),
            "abs_cv": round(alpha_cv, 4),
            "count_positive": sum(alpha_pos),
        },
        "r2_comparison": {
            "madelung": r2_m_vals,
            "standard": r2_s_vals,
            "mean_madelung": round(mean_r2_m, 6),
            "mean_standard": round(mean_r2_s, 6),
            "count_madelung_beats": madelung_wins,
        },
        "checks": {
            "p1_alpha_m_positive_4of5_pass": p1_pass,
            "p2_max_r2_m_above_half_pass": p2_pass,
            "p3_mean_r2_m_beats_standard_pass": p3_pass,
            "p4_cv_alpha_m_not_worse_pass": p4_pass,
        },
    }

    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    summary_lines = [
        "# QNG Madelung Amplitude",
        "",
        f"- test_id: `QNG-CPU-043`",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- verdict: `{verdict}`",
        "",
        "## R²_calib comparison per seed",
        *[
            f"  seed {r['seed']}: Madelung=`{r['r2_madelung']:.4f}`, "
            f"standard=`{r['r2_standard']:.4f}`, "
            f"Madelung_wins=`{r['madelung_beats_standard']}`"
            for r in results
        ],
        f"  mean Madelung: `{mean_r2_m:.4f}`, mean standard: `{mean_r2_s:.4f}`",
        "",
        "## α*_M per seed",
        *[
            f"  seed {r['seed']}: α*_M=`{r['alpha_madelung']:.6f}`, "
            f"α*_std=`{r['alpha_standard']:.6f}`, pos=`{r['alpha_m_positive']}`"
            for r in results
        ],
        f"  mean|α*_M|: `{alpha_mean:.6f}`, cv: `{alpha_cv:.4f}`",
        "",
        "## Scale ratio |divJ|/|Δρ| per seed (Madelung)",
        *[
            f"  seed {r['seed']}: `{r['scale_ratio_madelung']:.1f}x`"
            for r in results
        ],
    ]
    (out_dir / "summary.md").write_text(
        "\n".join(summary_lines) + "\n", encoding="utf-8"
    )

    print(f"qng_madelung_amplitude_reference: {'PASS' if decision else 'FAIL'}")
    print(f"verdict: {verdict}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
