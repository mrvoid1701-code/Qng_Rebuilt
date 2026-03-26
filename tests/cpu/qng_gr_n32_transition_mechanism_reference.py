"""QNG-CPU-062 — N=32 Topological Transition Mechanism.

Tests whether phi synchronization velocity (early Kuramoto slope, no-history)
peaks at N=32, explaining the cross-sector transition identified in CPU-061.

Also measures graph topology metrics (mean degree, clustering, mean path length).

Pass criteria (from prereg QNG-CPU-062):
    P1: v_sync (no-history) peaks at N=32 on >= 4/5 seeds
    P2: mean_degree k̄ increases monotonically with N
    P3: clustering C is non-monotone with N
    P4: Pearson(mean v_sync(N), Delta_nohist(N)) > 0.5 across N values
"""

from __future__ import annotations

import dataclasses
import json
import math
from pathlib import Path

from qng_native_update_reference import (
    Config,
    build_graph,
    init_state,
    one_step,
)
from qng_effective_field_reference import field_extract


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = (
    ROOT / "07_validation" / "audits"
    / "qng-gr-n32-transition-mechanism-reference-v1"
)

N_VALUES  = [8, 16, 32, 64]
SEEDS     = [20260325, 42, 137, 1729, 2718]
STEPS     = 24
EARLY_FIT = 12   # fit Kuramoto slope over steps 1..12

# From CPU-061 results (mean across seeds per N)
DELTA_NOHIST_REF = {8: 0.225, 16: 0.232, 32: 0.371, 64: 0.280}


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def mean(v: list[float]) -> float:
    return sum(v) / len(v) if v else 0.0


def pearson(a: list[float], b: list[float]) -> float:
    n = len(a)
    if n < 2:
        return 0.0
    ma, mb = mean(a), mean(b)
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    da  = math.sqrt(sum((x - ma) ** 2 for x in a))
    db  = math.sqrt(sum((x - mb) ** 2 for x in b))
    if da < 1e-15 or db < 1e-15:
        return 0.0
    return num / (da * db)


def linear_slope(xs: list[float], ys: list[float]) -> float:
    """OLS slope of y ~ a + b*x."""
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = mean(xs), mean(ys)
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if abs(den) > 1e-15 else 0.0


# ---------------------------------------------------------------------------
# Graph metric helpers
# ---------------------------------------------------------------------------

def graph_metrics(adj: list[list[int]]) -> dict:
    """Compute mean degree, degree CV, clustering coefficient, mean path length."""
    n = len(adj)
    degrees = [len(adj[i]) for i in range(n)]
    k_mean = mean(degrees)
    k_std  = math.sqrt(mean([(d - k_mean) ** 2 for d in degrees]))
    k_cv   = k_std / k_mean if k_mean > 1e-15 else 0.0

    # Clustering: fraction of closed triplets per node
    cluster_vals = []
    for i in range(n):
        nbrs = adj[i]
        ki = len(nbrs)
        if ki < 2:
            cluster_vals.append(0.0)
            continue
        # count edges among neighbors
        nbr_set = set(nbrs)
        edge_count = 0
        for j in nbrs:
            for k in adj[j]:
                if k in nbr_set and k != i:
                    edge_count += 1
        edge_count //= 2
        max_edges = ki * (ki - 1) // 2
        cluster_vals.append(edge_count / max_edges if max_edges > 0 else 0.0)
    clustering = mean(cluster_vals)

    # BFS mean path length
    total_dist = 0
    n_pairs = 0
    for src in range(n):
        dist = [-1] * n
        dist[src] = 0
        queue = [src]
        head = 0
        while head < len(queue):
            u = queue[head]; head += 1
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        for d in dist:
            if d > 0:
                total_dist += d
                n_pairs += 1
    mean_path = total_dist / n_pairs if n_pairs > 0 else float("nan")

    return {
        "mean_degree":    k_mean,
        "degree_cv":      k_cv,
        "clustering":     clustering,
        "mean_path_length": mean_path,
    }


# ---------------------------------------------------------------------------
# Kuramoto order parameter
# ---------------------------------------------------------------------------

def kuramoto_order(phi: list[float]) -> float:
    n = len(phi)
    re = sum(math.cos(p) for p in phi) / n
    im = sum(math.sin(p) for p in phi) / n
    return math.sqrt(re * re + im * im)


# ---------------------------------------------------------------------------
# Per (seed, N)
# ---------------------------------------------------------------------------

def run_one(seed: int, n_nodes: int) -> dict:
    import random as _rng
    cfg = dataclasses.replace(Config(), seed=seed, n_nodes=n_nodes)
    rng = _rng.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)

    # Graph metrics (from adj)
    gm = graph_metrics(adj)

    # Phi sync trajectory WITHOUT history
    state, history = init_state(cfg.n_nodes, rng)
    kur_traj = []
    for t in range(1, STEPS + 1):
        state, history = one_step(state, history, adj, cfg, use_history=False)
        kur_traj.append({"step": t, "r": kuramoto_order(state.phi[:])})

    # Sync velocity: linear slope over steps 1..EARLY_FIT
    early_steps = [e["step"] for e in kur_traj[:EARLY_FIT]]
    early_r     = [e["r"]    for e in kur_traj[:EARLY_FIT]]
    v_sync = linear_slope(early_steps, early_r)

    # Also record final Kuramoto (step 24)
    r_final = kur_traj[-1]["r"]
    r_initial = kur_traj[0]["r"]

    return {
        "seed":         seed,
        "n_nodes":      n_nodes,
        "mean_degree":  gm["mean_degree"],
        "degree_cv":    gm["degree_cv"],
        "clustering":   gm["clustering"],
        "mean_path_length": gm["mean_path_length"],
        "v_sync":       v_sync,
        "r_initial":    r_initial,
        "r_final":      r_final,
        "kur_traj":     kur_traj,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_all(out_dir: Path = DEFAULT_OUT_DIR) -> dict:
    all_rows = []
    for n in N_VALUES:
        for s in SEEDS:
            print(f"  N={n:>2}, seed={s}...", flush=True)
            all_rows.append(run_one(s, n))

    by_n = {n: [r for r in all_rows if r["n_nodes"] == n] for n in N_VALUES}

    # Aggregate per N
    agg = {}
    for n in N_VALUES:
        rows = by_n[n]
        agg[n] = {
            "mean_v_sync":     mean([r["v_sync"]     for r in rows]),
            "mean_degree":     mean([r["mean_degree"] for r in rows]),
            "mean_clustering": mean([r["clustering"]  for r in rows]),
            "mean_path":       mean([r["mean_path_length"] for r in rows]),
            "mean_r_final":    mean([r["r_final"]    for r in rows]),
        }

    # --- P1: v_sync peaks at N=32 on >= 4/5 seeds ---
    # For each seed: find which N gives maximum v_sync
    p1_seeds_peak_at_32 = 0
    for s in SEEDS:
        seed_rows = {n: next(r for r in by_n[n] if r["seed"] == s) for n in N_VALUES}
        v_by_n = {n: seed_rows[n]["v_sync"] for n in N_VALUES}
        peak_n = max(N_VALUES, key=lambda n: v_by_n[n])
        if peak_n == 32:
            p1_seeds_peak_at_32 += 1
    p1_pass = p1_seeds_peak_at_32 >= 4

    # --- P2: mean_degree increases monotonically with N ---
    mean_degrees = [agg[n]["mean_degree"] for n in N_VALUES]
    p2_pass = all(mean_degrees[i] < mean_degrees[i+1] for i in range(len(N_VALUES)-1))

    # --- P3: clustering is non-monotone with N ---
    clusterings = [agg[n]["mean_clustering"] for n in N_VALUES]
    # Non-monotone = not strictly increasing and not strictly decreasing
    strictly_inc = all(clusterings[i] < clusterings[i+1] for i in range(len(N_VALUES)-1))
    strictly_dec = all(clusterings[i] > clusterings[i+1] for i in range(len(N_VALUES)-1))
    p3_pass = not strictly_inc and not strictly_dec

    # --- P4: Pearson(mean v_sync(N), Delta_nohist(N)) > 0.5 ---
    mean_vsync_by_n = [agg[n]["mean_v_sync"] for n in N_VALUES]
    delta_nohist_by_n = [DELTA_NOHIST_REF[n] for n in N_VALUES]
    p4_corr = pearson(mean_vsync_by_n, delta_nohist_by_n)
    p4_pass = p4_corr > 0.5

    overall = sum([p1_pass, p2_pass, p3_pass, p4_pass])

    # For compact storage, trim kur_traj from output
    compact_rows = []
    for r in all_rows:
        row = dict(r)
        row.pop("kur_traj", None)
        compact_rows.append(row)

    report = {
        "test_id":    "QNG-CPU-062",
        "theory_doc": "DER-BRIDGE-044",
        "n_values":   N_VALUES,
        "seeds":      SEEDS,
        "per_row":    compact_rows,
        "agg_by_n":   {str(n): agg[n] for n in N_VALUES},
        "p1_seeds_peak_at_32": p1_seeds_peak_at_32,
        "p4_corr_vsync_dnohist": p4_corr,
        "delta_nohist_ref":     DELTA_NOHIST_REF,
        "summary": {
            "p1_pass": p1_pass,
            "p2_pass": p2_pass,
            "p3_pass": p3_pass,
            "p4_pass": p4_pass,
            "overall": f"{overall}/4",
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print table
    print(f"\n=== QNG-CPU-062 N=32 Transition Mechanism ===")
    print(f"{'N':>4}  {'v_sync':>8}  {'k̄':>6}  {'C':>8}  {'L':>6}  {'r_fin':>6}")
    print("-" * 56)
    for n in N_VALUES:
        a = agg[n]
        print(f"{n:>4}  {a['mean_v_sync']:>8.5f}  {a['mean_degree']:>6.2f}  "
              f"{a['mean_clustering']:>8.5f}  {a['mean_path']:>6.3f}  "
              f"{a['mean_r_final']:>6.3f}")
    print("-" * 56)

    print(f"\nPer-seed N at peak v_sync (no-history):")
    for s in SEEDS:
        seed_rows = {n: next(r for r in by_n[n] if r["seed"] == s) for n in N_VALUES}
        v_by_n = {n: seed_rows[n]["v_sync"] for n in N_VALUES}
        peak_n = max(N_VALUES, key=lambda n: v_by_n[n])
        v_str = "  ".join(f"N={n}:{v_by_n[n]:.4f}" for n in N_VALUES)
        peak_mark = " ← PEAK=32" if peak_n == 32 else f" ← PEAK={peak_n}"
        print(f"  seed {s}: {v_str}{peak_mark}")

    print(f"\nP1 {'PASS' if p1_pass else 'FAIL'} ({p1_seeds_peak_at_32}/5 seeds peak at N=32)")
    k_bar_vals = [f"{agg[n]['mean_degree']:.2f}" for n in N_VALUES]
    clust_vals = [f"{agg[n]['mean_clustering']:.4f}" for n in N_VALUES]
    print(f"P2 {'PASS' if p2_pass else 'FAIL'} (k\u0304 monotone with N: {k_bar_vals})")
    print(f"P3 {'PASS' if p3_pass else 'FAIL'} (clustering non-monotone: {clust_vals})")
    print(f"P4 {'PASS' if p4_pass else 'FAIL'} (Pearson(v_sync,Δ_nohist)={p4_corr:.4f} {'> 0.5' if p4_pass else '<= 0.5'})")
    print(f"OVERALL: {overall}/4")

    return report


if __name__ == "__main__":
    import sys
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT_DIR
    run_all(out_dir)
