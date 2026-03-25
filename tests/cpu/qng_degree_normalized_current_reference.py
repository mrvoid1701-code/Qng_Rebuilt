"""QNG-CPU-048 — Degree-Normalized Multi-Channel Current.

Tests whether normalizing the divergence current by local degree restores
N-stability of R²_combined across N ∈ {8, 16, 32}.

Degree-normalized current:
    divN(J_X)_i = (1/deg_i) · C_eff_i · Σ_j C_eff_j · Δf_{ij}

Pass criteria (from prereg QNG-CPU-048):
    P1: mean R²_combined(N=32) ≥ 0.30 with normalization
    P2: cv_N(R²_norm) < cv_N(R²_std) = 0.369
    P3: multi-channel beats single at N=32, ≥4/5 seeds
    P4: mean R²_norm(N=32) > 0.269 (beats unnormalized)

Reference (QNG-CPU-047 unnormalized):
    N=8:  mean R²=0.586   N=16: mean R²=0.405   N=32: mean R²=0.269
    cv_N(unnormalized) = 0.369
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
    ROOT / "07_validation" / "audits" / "qng-degree-normalized-current-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]
N_VALUES = [8, 16, 32]

# Reference unnormalized means from QNG-CPU-047
R2_STD_BY_N = {8: 0.5864, 16: 0.4053, 32: 0.2688}
CV_N_STD = 0.369


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
    M = [A[i][:] + [b[i]] for i in range(3)]
    for col in range(3):
        max_row = max(range(col, 3), key=lambda r: abs(M[r][col]))
        M[col], M[max_row] = M[max_row], M[col]
        pivot = M[col][col]
        if abs(pivot) < 1e-20:
            return [0.0, 0.0, 0.0]
        for row in range(col + 1, 3):
            factor = M[row][col] / pivot
            for k in range(col, 4):
                M[row][k] -= factor * M[col][k]
    x = [0.0] * 3
    for i in range(2, -1, -1):
        x[i] = M[i][3]
        for j in range(i + 1, 3):
            x[i] -= M[i][j] * x[j]
        x[i] /= M[i][i] if abs(M[i][i]) > 1e-20 else 1.0
    return x


def divN_J_phase(
    c: list[float], phi: list[float], adj: list[list[int]]
) -> list[float]:
    """Degree-normalized phi divergence."""
    return [
        (c[i] / max(len(adj[i]), 1))
        * sum(c[j] * math.sin(phi[j] - phi[i]) for j in adj[i])
        for i in range(len(c))
    ]


def divN_J_grad(
    c: list[float], f: list[float], adj: list[list[int]]
) -> list[float]:
    """Degree-normalized gradient divergence (mismatch or mem)."""
    return [
        (c[i] / max(len(adj[i]), 1))
        * sum(c[j] * (f[j] - f[i]) for j in adj[i])
        for i in range(len(c))
    ]


def div_J_phase(
    c: list[float], phi: list[float], adj: list[list[int]]
) -> list[float]:
    """Standard (unnormalized) phi divergence."""
    return [
        c[i] * sum(c[j] * math.sin(phi[j] - phi[i]) for j in adj[i])
        for i in range(len(c))
    ]


def div_J_grad(
    c: list[float], f: list[float], adj: list[list[int]]
) -> list[float]:
    """Standard (unnormalized) gradient divergence."""
    return [
        c[i] * sum(c[j] * (f[j] - f[i]) for j in adj[i])
        for i in range(len(c))
    ]


def r2_single_best(drho, dj1, dj2, dj3) -> float:
    def r2_one(dj):
        den = dot(dj, dj)
        if abs(den) < 1e-20:
            return 0.0
        a = -dot(drho, dj) / den
        vd = variance(drho)
        if vd < 1e-30:
            return 0.0
        res = [dr + a * d for dr, d in zip(drho, dj)]
        return 1.0 - variance(res) / vd
    return max(r2_one(dj1), r2_one(dj2), r2_one(dj3))


def r2_multi(drho, dj1, dj2, dj3) -> tuple[list[float], float]:
    channels = [dj1, dj2, dj3]
    A = [[dot(channels[i], channels[j]) for j in range(3)] for i in range(3)]
    b = [dot(drho, channels[i]) for i in range(3)]
    alphas = solve_3x3(A, [-bi for bi in b])
    vd = variance(drho)
    if vd < 1e-30:
        return alphas, 0.0
    res = [drho[k] + alphas[0]*dj1[k] + alphas[1]*dj2[k] + alphas[2]*dj3[k]
           for k in range(len(drho))]
    return alphas, 1.0 - variance(res) / vd


def mean_degree(adj: list[list[int]]) -> float:
    return sum(len(a) for a in adj) / len(adj)


# ---------------------------------------------------------------------------
# Single (seed, n_nodes) run
# ---------------------------------------------------------------------------

def run_one(seed: int, n_nodes: int) -> dict:
    import random as _random
    cfg = dataclasses.replace(Config(), seed=seed, n_nodes=n_nodes)
    rng = _random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)

    for _ in range(cfg.steps - 1):
        state, history = one_step(state, history, adj, cfg, use_history=True)

    c_t, _ = field_extract(state, history)
    phi_t = state.phi[:]
    mismatch_t = history.mismatch[:]
    mem_t = history.mem[:]

    state2, history2 = one_step(state, history, adj, cfg, use_history=True)
    c_tp1, _ = field_extract(state2, history2)

    drho = [c1**2 - c0**2 for c0, c1 in zip(c_t, c_tp1)]

    # Degree-normalized currents
    dj_phi_n  = divN_J_phase(c_t, phi_t, adj)
    dj_mis_n  = divN_J_grad(c_t, mismatch_t, adj)
    dj_mem_n  = divN_J_grad(c_t, mem_t, adj)

    # Unnormalized (for comparison)
    dj_phi_u  = div_J_phase(c_t, phi_t, adj)
    dj_mis_u  = div_J_grad(c_t, mismatch_t, adj)
    dj_mem_u  = div_J_grad(c_t, mem_t, adj)

    alphas_n, r2_norm = r2_multi(drho, dj_phi_n, dj_mis_n, dj_mem_n)
    alphas_u, r2_std  = r2_multi(drho, dj_phi_u, dj_mis_u, dj_mem_u)

    r2_best_norm = r2_single_best(drho, dj_phi_n, dj_mis_n, dj_mem_n)
    r2_best_std  = r2_single_best(drho, dj_phi_u, dj_mis_u, dj_mem_u)

    deg = mean_degree(adj)

    return {
        "seed": seed,
        "n_nodes": n_nodes,
        "mean_degree": deg,
        "r2_norm": r2_norm,
        "r2_std": r2_std,
        "r2_best_norm": r2_best_norm,
        "r2_best_std": r2_best_std,
        "norm_beats_best": r2_norm > r2_best_norm,
        "norm_beats_std_multi": r2_norm > r2_std,
        "alpha_phi_n": alphas_n[0],
        "alpha_mis_n": alphas_n[1],
        "alpha_mem_n": alphas_n[2],
        "alpha_phi_u": alphas_u[0],
        "alpha_mis_u": alphas_u[1],
        "alpha_mem_u": alphas_u[2],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    all_results: dict[int, list[dict]] = {n: [] for n in N_VALUES}

    for n in N_VALUES:
        for s in SEEDS:
            all_results[n].append(run_one(s, n))

    print("=" * 80)
    print("QNG-CPU-048 — Degree-Normalized Multi-Channel Current")
    print("=" * 80)

    summary: dict[int, dict] = {}
    for n in N_VALUES:
        rows = all_results[n]
        r2_norm = [r["r2_norm"] for r in rows]
        r2_std  = [r["r2_std"]  for r in rows]
        mean_n = statistics.mean(r2_norm)
        mean_s = statistics.mean(r2_std)
        n_beats = sum(1 for r in rows if r["norm_beats_best"])
        summary[n] = {
            "mean_r2_norm": mean_n,
            "mean_r2_std": mean_s,
            "n_beats_best": n_beats,
            "mean_degree": statistics.mean(r["mean_degree"] for r in rows),
            "results": rows,
        }
        print(f"\n── N={n}  (mean_deg={summary[n]['mean_degree']:.2f}) ──")
        print(f"  {'Seed':>10}  {'R²_norm':>8}  {'R²_std':>8}  {'Δ':>8}  {'beats_best?':>11}")
        for r in rows:
            flag = "YES" if r["norm_beats_best"] else "---"
            print(
                f"  {r['seed']:>10}  {r['r2_norm']:>8.6f}  {r['r2_std']:>8.6f}  "
                f"  {r['r2_norm']-r['r2_std']:>+8.6f}  {flag:>11}"
            )
        print(f"  mean norm={mean_n:.4f}  mean std={mean_s:.4f}  beats_best={n_beats}/5")

    # N-stability metrics
    means_norm = [summary[n]["mean_r2_norm"] for n in N_VALUES]
    means_std  = [summary[n]["mean_r2_std"]  for n in N_VALUES]
    cv_norm = statistics.stdev(means_norm) / statistics.mean(means_norm)
    cv_std  = statistics.stdev(means_std)  / statistics.mean(means_std)

    # Pass criteria
    p1_pass = summary[32]["mean_r2_norm"] >= 0.30
    p2_pass = cv_norm < CV_N_STD
    p3_pass = summary[32]["n_beats_best"] >= 4
    p4_pass = summary[32]["mean_r2_norm"] > R2_STD_BY_N[32]

    n_pass = sum([p1_pass, p2_pass, p3_pass, p4_pass])
    decision = "pass" if n_pass >= 3 else ("partial" if n_pass >= 2 else "fail")

    print("\n" + "=" * 80)
    print("N-stability comparison:")
    print(f"  {'N':>4}  {'R²_norm':>10}  {'R²_std':>10}  {'mean_deg':>10}")
    for n in N_VALUES:
        print(f"  {n:>4}  {summary[n]['mean_r2_norm']:>10.4f}  {summary[n]['mean_r2_std']:>10.4f}  {summary[n]['mean_degree']:>10.2f}")
    print(f"\n  cv_N(normalized) = {cv_norm:.4f}   cv_N(standard) = {cv_std:.4f}")
    print(f"  {'normalized MORE stable' if cv_norm < cv_std else 'standard more stable'}")
    print()
    print(f"P1 (mean R²_norm(N=32) ≥ 0.30):         {'PASS' if p1_pass else 'FAIL'} ({summary[32]['mean_r2_norm']:.4f})")
    print(f"P2 (cv_N(norm) < cv_N(std)={CV_N_STD:.3f}): {'PASS' if p2_pass else 'FAIL'} ({cv_norm:.4f})")
    print(f"P3 (multi beats single at N=32, ≥4/5):  {'PASS' if p3_pass else 'FAIL'} ({summary[32]['n_beats_best']}/5)")
    print(f"P4 (R²_norm(N=32) > R²_std(N=32)=0.269):{'PASS' if p4_pass else 'FAIL'} ({summary[32]['mean_r2_norm']:.4f})")
    print(f"\nDecision: {decision.upper()} ({n_pass}/4 predictions)")

    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "test": "QNG-CPU-048",
        "theory": "DER-BRIDGE-030",
        "decision": decision,
        "n_pass": n_pass,
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "p3_pass": p3_pass,
        "p4_pass": p4_pass,
        "cv_norm": cv_norm,
        "cv_std": cv_std,
        "cv_n_std_ref": CV_N_STD,
        "n_values": N_VALUES,
        "summary_by_n": {
            str(n): {k: v for k, v in summary[n].items() if k != "results"}
            for n in N_VALUES
        },
        "all_results": {str(n): summary[n]["results"] for n in N_VALUES},
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
