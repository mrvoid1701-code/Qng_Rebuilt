"""QNG-CPU-047 — Multi-Channel Continuity Large-N Probe.

Tests whether the multi-channel continuity law established at N=16 (QNG-CPU-046)
is N-stable: runs the same multi-channel regression at N ∈ {8, 16, 32}.

Pass criteria (from prereg QNG-CPU-047):
    P1: R²_combined > R²_best_single at N=32, ≥4/5 seeds
    P2: mean R²_combined ≥ 0.30 at N=8 AND N=32
    P3: |α_phi/α_mis| decreases from N=8 to N=32 on ≥3/5 seeds
    P4: best_N (max R²_combined) ≠ N=8 on ≥4/5 seeds

Reference (QNG-CPU-046, N=16):
    mean R²_combined = 0.405  mean R²_best_single = 0.256
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
    ROOT / "07_validation" / "audits" / "qng-multichannel-large-n-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]
N_VALUES = [8, 16, 32]

# Reference R²_combined from QNG-CPU-046 (N=16)
R2_COMBINED_N16 = [0.147724, 0.535153, 0.601887, 0.239188, 0.502728]


# ---------------------------------------------------------------------------
# Math helpers (same as CPU-046)
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


def div_J_phase(c: list[float], phi: list[float], adj: list[list[int]]) -> list[float]:
    return [
        c[i] * sum(c[j] * math.sin(phi[j] - phi[i]) for j in adj[i])
        for i in range(len(c))
    ]


def div_J_grad(c: list[float], f: list[float], adj: list[list[int]]) -> list[float]:
    return [
        c[i] * sum(c[j] * (f[j] - f[i]) for j in adj[i])
        for i in range(len(c))
    ]


def r2_single_best(drho, dj_phi, dj_mis, dj_mem) -> float:
    def r2_one(dj):
        den = dot(dj, dj)
        if abs(den) < 1e-20:
            return 0.0
        alpha = -dot(drho, dj) / den
        var_d = variance(drho)
        if var_d < 1e-30:
            return 0.0
        res = [dr + alpha * d for dr, d in zip(drho, dj)]
        return 1.0 - variance(res) / var_d
    return max(r2_one(dj_phi), r2_one(dj_mis), r2_one(dj_mem))


def r2_multi_3(drho, dj1, dj2, dj3) -> tuple[list[float], float]:
    channels = [dj1, dj2, dj3]
    A = [[dot(channels[i], channels[j]) for j in range(3)] for i in range(3)]
    b = [dot(drho, channels[i]) for i in range(3)]
    alphas = solve_3x3(A, [-bi for bi in b])
    var_d = variance(drho)
    if var_d < 1e-30:
        return alphas, 0.0
    res = [drho[k] + alphas[0]*dj1[k] + alphas[1]*dj2[k] + alphas[2]*dj3[k]
           for k in range(len(drho))]
    return alphas, 1.0 - variance(res) / var_d


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
    dj_phi = div_J_phase(c_t, phi_t, adj)
    dj_mis  = div_J_grad(c_t, mismatch_t, adj)
    dj_mem  = div_J_grad(c_t, mem_t, adj)

    alphas, r2_comb = r2_multi_3(drho, dj_phi, dj_mis, dj_mem)
    r2_best = r2_single_best(drho, dj_phi, dj_mis, dj_mem)

    ratio_phi_mis = (abs(alphas[0]) / abs(alphas[1])
                     if abs(alphas[1]) > 1e-20 else float("inf"))

    return {
        "seed": seed,
        "n_nodes": n_nodes,
        "mean_degree": mean_degree(adj),
        "r2_combined": r2_comb,
        "r2_best_single": r2_best,
        "gain": r2_comb - r2_best,
        "beats_best": r2_comb > r2_best,
        "alpha_phi": alphas[0],
        "alpha_mis": alphas[1],
        "alpha_mem": alphas[2],
        "ratio_phi_mis": ratio_phi_mis,
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
    print("QNG-CPU-047 — Multi-Channel Continuity Large-N Probe")
    print("=" * 80)

    summary: dict[int, dict] = {}
    for n in N_VALUES:
        rows = all_results[n]
        r2c = [r["r2_combined"] for r in rows]
        r2b = [r["r2_best_single"] for r in rows]
        mean_c = statistics.mean(r2c)
        max_c  = max(r2c)
        n_beats = sum(1 for r in rows if r["beats_best"])
        mean_deg = statistics.mean(r["mean_degree"] for r in rows)
        summary[n] = {
            "mean_r2_combined": mean_c,
            "max_r2_combined": max_c,
            "mean_r2_best_single": statistics.mean(r2b),
            "n_beats_best": n_beats,
            "mean_degree": mean_deg,
            "results": rows,
        }
        print(f"\n── N={n}  (mean_degree={mean_deg:.2f}) ──")
        print(f"  {'Seed':>10}  {'R²_comb':>8}  {'R²_best':>8}  {'gain':>8}  {'α_phi':>10}  {'α_mis':>10}  {'beats':>5}")
        for r in rows:
            flag = "YES" if r["beats_best"] else "---"
            print(
                f"  {r['seed']:>10}  {r['r2_combined']:>8.6f}  {r['r2_best_single']:>8.6f}  "
                f"  {r['gain']:>+8.6f}  {r['alpha_phi']:>10.6f}  {r['alpha_mis']:>10.6f}  {flag:>5}"
            )
        print(f"  mean R²_combined={mean_c:.4f}  max={max_c:.4f}  beats_best={n_beats}/5")

    # Pass criteria
    p1_n32_beats = summary[32]["n_beats_best"]
    p1_pass = p1_n32_beats >= 4

    p2_mean_n8  = summary[8]["mean_r2_combined"]
    p2_mean_n32 = summary[32]["mean_r2_combined"]
    p2_pass = p2_mean_n8 >= 0.30 and p2_mean_n32 >= 0.30

    # P3: |α_phi/α_mis| decreases from N=8 to N=32 on ≥3/5 seeds
    n_p3 = 0
    for i, s in enumerate(SEEDS):
        r8  = all_results[8][i]
        r32 = all_results[32][i]
        if r8["ratio_phi_mis"] > r32["ratio_phi_mis"]:
            n_p3 += 1
    p3_pass = n_p3 >= 3

    # P4: best_N ≠ N=8 on ≥4/5 seeds
    n_p4 = 0
    for i in range(len(SEEDS)):
        r2s = {n: all_results[n][i]["r2_combined"] for n in N_VALUES}
        best_n = max(r2s, key=r2s.get)
        if best_n != 8:
            n_p4 += 1
    p4_pass = n_p4 >= 4

    n_pass = sum([p1_pass, p2_pass, p3_pass, p4_pass])
    decision = "pass" if n_pass >= 3 else ("partial" if n_pass >= 2 else "fail")

    print("\n" + "=" * 80)
    print("Summary across N values:")
    print(f"  {'N':>4}  {'mean R²_comb':>14}  {'mean R²_best':>14}  {'beats(5/5)':>10}  {'mean_deg':>10}")
    for n in N_VALUES:
        s = summary[n]
        print(
            f"  {n:>4}  {s['mean_r2_combined']:>14.6f}  {s['mean_r2_best_single']:>14.6f}  "
            f"  {s['n_beats_best']:>10}/5  {s['mean_degree']:>10.2f}"
        )
    print()
    print(f"P1 (R²_comb > best at N=32, ≥4/5): {'PASS' if p1_pass else 'FAIL'} ({p1_n32_beats}/5)")
    print(f"P2 (mean R²_comb ≥0.30 at N=8,32): {'PASS' if p2_pass else 'FAIL'} "
          f"(N=8: {p2_mean_n8:.4f}, N=32: {p2_mean_n32:.4f})")
    print(f"P3 (|α_phi/α_mis| decreases N8→N32 on ≥3/5): {'PASS' if p3_pass else 'FAIL'} ({n_p3}/5)")
    print(f"P4 (best_N ≠ N=8 on ≥4/5): {'PASS' if p4_pass else 'FAIL'} ({n_p4}/5)")
    print(f"\nDecision: {decision.upper()} ({n_pass}/4 predictions)")

    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "test": "QNG-CPU-047",
        "theory": "DER-BRIDGE-029",
        "decision": decision,
        "n_pass": n_pass,
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "p3_pass": p3_pass,
        "p4_pass": p4_pass,
        "p1_n32_beats": p1_n32_beats,
        "p2_mean_n8": p2_mean_n8,
        "p2_mean_n32": p2_mean_n32,
        "n_p3": n_p3,
        "n_p4": n_p4,
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
