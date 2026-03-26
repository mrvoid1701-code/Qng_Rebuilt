"""QNG-CPU-046 — Multi-Channel Current Regression.

Tests whether jointly regressing density change Δρ on all three current channels
(phi, mismatch, mem) gives R²_combined >> max(R²_single) per seed.

Multi-channel continuity ansatz:
    Δρ ≈ -(α_phi·div(J_phi) + α_mis·div(J_mis) + α_mem·div(J_mem))

Solved by 3×3 OLS normal equations (pure Python, no external libraries).

Pass criteria (from prereg QNG-CPU-046):
    P1: R²_combined > max(R²_phi, R²_mis, R²_mem) on ≥4/5 seeds
    P2: mean R²_combined > 0.35
    P3: max R²_combined > 0.60
    P4: R²_combined > 0.30 on ≥3/5 seeds
"""

from __future__ import annotations

import dataclasses
import json
import math
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
    ROOT / "07_validation" / "audits" / "qng-multichannel-current-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]

# Reference single-channel R² from QNG-CPU-045
R2_PHI_REF  = [0.045617, 0.138356, 0.572227, 0.034704, 0.207112]
R2_MIS_REF  = [0.012993, 0.353832, 0.001800, 0.021469, 0.208248]
R2_MEM_REF  = [0.040113, 0.048822, 0.044895, 0.101066, 0.038489]


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def variance(a: list[float]) -> float:
    n = len(a)
    if n == 0:
        return 0.0
    m = sum(a) / n
    return sum((x - m) ** 2 for x in a) / n


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def solve_3x3(A: list[list[float]], b: list[float]) -> list[float]:
    """Solve 3×3 linear system Ax = b by Gaussian elimination with partial pivot."""
    # Augmented matrix
    M = [A[i][:] + [b[i]] for i in range(3)]

    for col in range(3):
        # Partial pivot
        max_row = max(range(col, 3), key=lambda r: abs(M[r][col]))
        M[col], M[max_row] = M[max_row], M[col]

        pivot = M[col][col]
        if abs(pivot) < 1e-20:
            return [0.0, 0.0, 0.0]  # singular — return zeros

        for row in range(col + 1, 3):
            factor = M[row][col] / pivot
            for k in range(col, 4):
                M[row][k] -= factor * M[col][k]

    # Back substitution
    x = [0.0] * 3
    for i in range(2, -1, -1):
        x[i] = M[i][3]
        for j in range(i + 1, 3):
            x[i] -= M[i][j] * x[j]
        x[i] /= M[i][i] if abs(M[i][i]) > 1e-20 else 1.0

    return x


def div_J_phase(
    c_eff: list[float], phi: list[float], adj: list[list[int]]
) -> list[float]:
    return [
        c_eff[i] * sum(c_eff[j] * math.sin(phi[j] - phi[i]) for j in adj[i])
        for i in range(len(c_eff))
    ]


def div_J_gradient(
    c_eff: list[float], field: list[float], adj: list[list[int]]
) -> list[float]:
    return [
        c_eff[i] * sum(c_eff[j] * (field[j] - field[i]) for j in adj[i])
        for i in range(len(c_eff))
    ]


def r2_single(drho: list[float], dj: list[float]) -> tuple[float, float]:
    """Return (alpha*, R²) for single-channel calibrated fit."""
    num = dot(drho, dj)
    den = dot(dj, dj)
    alpha = -num / den if abs(den) > 1e-20 else 0.0
    var_drho = variance(drho)
    if var_drho < 1e-30:
        return alpha, 0.0
    residual = [dr + alpha * dj_ for dr, dj_ in zip(drho, dj)]
    return alpha, 1.0 - variance(residual) / var_drho


def r2_multi(
    drho: list[float],
    dj1: list[float],
    dj2: list[float],
    dj3: list[float],
) -> tuple[list[float], float]:
    """Return (alphas, R²) for 3-channel OLS fit.

    Minimizes Σ(Δρ + α1·dj1 + α2·dj2 + α3·dj3)².
    Normal equations: A·α = -b where A_ij = dot(dj_i, dj_j), b_i = dot(Δρ, dj_i).
    """
    channels = [dj1, dj2, dj3]
    A = [[dot(channels[i], channels[j]) for j in range(3)] for i in range(3)]
    b = [dot(drho, channels[i]) for i in range(3)]
    # solve A·α = -b
    alphas = solve_3x3(A, [-bi for bi in b])

    var_drho = variance(drho)
    if var_drho < 1e-30:
        return alphas, 0.0
    residual = [
        drho[k] + alphas[0] * dj1[k] + alphas[1] * dj2[k] + alphas[2] * dj3[k]
        for k in range(len(drho))
    ]
    r2 = 1.0 - variance(residual) / var_drho
    return alphas, r2


# ---------------------------------------------------------------------------
# Two-step rollout
# ---------------------------------------------------------------------------

def rollout_two_steps(cfg: Config):
    import random as _random
    rng = _random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)

    for _ in range(cfg.steps - 1):
        state, history = one_step(state, history, adj, cfg, use_history=True)

    c_t, _ = field_extract(state, history)
    phi_t = state.phi[:]
    mismatch_t = history.mismatch[:]
    mem_t = history.mem[:]

    state_tp1, history_tp1 = one_step(state, history, adj, cfg, use_history=True)
    c_tp1, _ = field_extract(state_tp1, history_tp1)

    return c_t, c_tp1, phi_t, mismatch_t, mem_t, adj


# ---------------------------------------------------------------------------
# Per-seed metrics
# ---------------------------------------------------------------------------

def metrics_for_seed(
    seed: int, r2_phi_ref: float, r2_mis_ref: float, r2_mem_ref: float
) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)
    c_t, c_tp1, phi_t, mismatch_t, mem_t, adj = rollout_two_steps(cfg)

    rho_t   = [c ** 2 for c in c_t]
    rho_tp1 = [c ** 2 for c in c_tp1]
    drho = [r1 - r0 for r0, r1 in zip(rho_t, rho_tp1)]

    dj_phi = div_J_phase(c_t, phi_t, adj)
    dj_mis = div_J_gradient(c_t, mismatch_t, adj)
    dj_mem = div_J_gradient(c_t, mem_t, adj)

    alpha_phi, r2_phi = r2_single(drho, dj_phi)
    alpha_mis, r2_mis = r2_single(drho, dj_mis)
    alpha_mem, r2_mem = r2_single(drho, dj_mem)

    alphas, r2_combined = r2_multi(drho, dj_phi, dj_mis, dj_mem)

    best_single = max(r2_phi, r2_mis, r2_mem)
    beats_best = r2_combined > best_single

    # Cross-correlations between channels (to check independence)
    def corr_vecs(a, b):
        va, vb = variance(a), variance(b)
        if va < 1e-30 or vb < 1e-30:
            return 0.0
        ma, mb = sum(a)/len(a), sum(b)/len(b)
        return sum((x-ma)*(y-mb) for x,y in zip(a,b)) / (len(a)*math.sqrt(va*vb))

    return {
        "seed": seed,
        "r2_combined": r2_combined,
        "r2_phi": r2_phi,
        "r2_mis": r2_mis,
        "r2_mem": r2_mem,
        "best_single": best_single,
        "r2_phi_ref": r2_phi_ref,
        "r2_mis_ref": r2_mis_ref,
        "r2_mem_ref": r2_mem_ref,
        "alpha_phi": alphas[0],
        "alpha_mis": alphas[1],
        "alpha_mem": alphas[2],
        "alpha_phi_single": alpha_phi,
        "alpha_mis_single": alpha_mis,
        "alpha_mem_single": alpha_mem,
        "gain": r2_combined - best_single,
        "beats_best_single": beats_best,
        "corr_phi_mis": corr_vecs(dj_phi, dj_mis),
        "corr_phi_mem": corr_vecs(dj_phi, dj_mem),
        "corr_mis_mem": corr_vecs(dj_mis, dj_mem),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    refs = list(zip(R2_PHI_REF, R2_MIS_REF, R2_MEM_REF))
    results = [metrics_for_seed(s, *r) for s, r in zip(SEEDS, refs)]

    r2_comb = [r["r2_combined"] for r in results]
    r2_best = [r["best_single"] for r in results]

    mean_comb = statistics.mean(r2_comb)
    max_comb  = max(r2_comb)
    mean_best = statistics.mean(r2_best)
    n_beats   = sum(1 for r in results if r["beats_best_single"])
    n_above30 = sum(1 for v in r2_comb if v > 0.30)

    p1_pass = n_beats >= 4
    p2_pass = mean_comb > 0.35
    p3_pass = max_comb  > 0.60
    p4_pass = n_above30 >= 3

    n_pass = sum([p1_pass, p2_pass, p3_pass, p4_pass])
    decision = "pass" if n_pass >= 3 else ("partial" if n_pass >= 2 else "fail")

    print("=" * 80)
    print("QNG-CPU-046 — Multi-Channel Current Regression")
    print("=" * 80)
    print(f"{'Seed':>10}  {'R²_comb':>8}  {'R²_phi':>8}  {'R²_mis':>8}  {'R²_mem':>8}  {'gain':>8}  {'beats':>5}")
    for r in results:
        flag = "YES" if r["beats_best_single"] else "---"
        print(
            f"{r['seed']:>10}  {r['r2_combined']:>8.6f}  {r['r2_phi']:>8.6f}  "
            f"{r['r2_mis']:>8.6f}  {r['r2_mem']:>8.6f}  {r['gain']:>+8.6f}  {flag:>5}"
        )
    print()
    print(f"mean R²: combined={mean_comb:.6f}  best_single={mean_best:.6f}  gain={mean_comb-mean_best:+.6f}")
    print(f"max  R²_combined = {max_comb:.6f}")
    print()
    print(f"P1 (R²_comb > best_single on ≥4/5): {'PASS' if p1_pass else 'FAIL'} ({n_beats}/5)")
    print(f"P2 (mean R²_comb > 0.35):            {'PASS' if p2_pass else 'FAIL'} ({mean_comb:.4f})")
    print(f"P3 (max R²_comb > 0.60):             {'PASS' if p3_pass else 'FAIL'} ({max_comb:.4f})")
    print(f"P4 (R²_comb > 0.30 on ≥3/5):        {'PASS' if p4_pass else 'FAIL'} ({n_above30}/5)")
    print(f"\nDecision: {decision.upper()} ({n_pass}/4 predictions)")

    print("\n--- Multi-channel coefficients ---")
    print(f"{'Seed':>10}  {'α_phi':>10}  {'α_mis':>10}  {'α_mem':>10}  {'corr(φ,mis)':>12}  {'corr(φ,mem)':>12}  {'corr(mis,mem)':>13}")
    for r in results:
        print(
            f"{r['seed']:>10}  {r['alpha_phi']:>10.6f}  {r['alpha_mis']:>10.6f}  "
            f"{r['alpha_mem']:>10.6f}  {r['corr_phi_mis']:>12.6f}  "
            f"{r['corr_phi_mem']:>12.6f}  {r['corr_mis_mem']:>13.6f}"
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "test": "QNG-CPU-046",
        "theory": "DER-BRIDGE-028",
        "decision": decision,
        "n_pass": n_pass,
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "p3_pass": p3_pass,
        "p4_pass": p4_pass,
        "n_beats_best": n_beats,
        "n_above30": n_above30,
        "mean_r2_combined": mean_comb,
        "mean_r2_best_single": mean_best,
        "max_r2_combined": max_comb,
        "seeds": results,
    }
    with open(out_dir / "report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to {out_dir / 'report.json'}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    main(args.out_dir)
