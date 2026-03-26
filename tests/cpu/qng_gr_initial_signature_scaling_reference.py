"""QNG-CPU-060 — Initial Metric Anticorrelation: Statistical Origin and N-Scaling.

Tests whether |corr(E_tt,E_xx)| ≈ 1.000 at rollout step 1 is universal across
N = {8, 16, 32, 64}, and whether signature decay decreases with N.

Pass criteria (from prereg QNG-CPU-060):
    P1: mean|corr_1| > 0.95 at each N in {8,16,32,64}
    P2: mean|corr_1| > mean|corr_24| at each N
    P3: mean decay Δ decreases from N=8 to N=64
    P4: |corr_1| > 0.90 on ≥ 4/5 seeds at N=64
"""

from __future__ import annotations

import dataclasses
import json
import math
from pathlib import Path

from qng_effective_field_reference import field_extract
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_gr_tensorial_assembly_reference import tensorial_proxy
from qng_native_update_reference import (
    Config,
    build_graph,
    init_state,
    one_step,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = (
    ROOT / "07_validation" / "audits"
    / "qng-gr-initial-signature-scaling-reference-v1"
)

N_VALUES = [8, 16, 32, 64]
SEEDS    = [20260325, 42, 137, 1729, 2718]
STEPS    = 24


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


# ---------------------------------------------------------------------------
# Metric anticorrelation at a given step
# ---------------------------------------------------------------------------

def abs_corr_at_step(cfg: Config, target_step: int) -> float:
    import random as _rng
    rng = _rng.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)
    for _ in range(target_step):
        state, history = one_step(state, history, adj, cfg, use_history=True)
    c, _ = field_extract(state, history)
    phi  = state.phi[:]
    asm  = assemble_linearized_metric(c, phi)
    ten  = tensorial_proxy(asm)
    return abs(pearson(ten["e_tt"], ten["e_xx"]))


# ---------------------------------------------------------------------------
# Per (seed, N)
# ---------------------------------------------------------------------------

def run_one(seed: int, n_nodes: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed, n_nodes=n_nodes)
    c1  = abs_corr_at_step(cfg, 1)
    c24 = abs_corr_at_step(cfg, STEPS)
    return {
        "seed":        seed,
        "n_nodes":     n_nodes,
        "abs_corr_1":  c1,
        "abs_corr_24": c24,
        "decay":       c1 - c24,
    }


# ---------------------------------------------------------------------------
# Aggregate per N
# ---------------------------------------------------------------------------

def stats_for_n(rows: list[dict]) -> dict:
    c1s   = [r["abs_corr_1"]  for r in rows]
    c24s  = [r["abs_corr_24"] for r in rows]
    decs  = [r["decay"]        for r in rows]
    return {
        "mean_corr_1":  mean(c1s),
        "mean_corr_24": mean(c24s),
        "mean_decay":   mean(decs),
        "min_corr_1":   min(c1s),
        "n_above_090":  sum(1 for x in c1s if x > 0.90),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_all(out_dir: Path = DEFAULT_OUT_DIR) -> dict:
    all_rows = []
    for n in N_VALUES:
        for s in SEEDS:
            all_rows.append(run_one(s, n))

    by_n = {n: [r for r in all_rows if r["n_nodes"] == n] for n in N_VALUES}
    stats = {n: stats_for_n(by_n[n]) for n in N_VALUES}

    # Pass criteria
    p1_pass = all(stats[n]["mean_corr_1"] > 0.95 for n in N_VALUES)
    p2_pass = all(stats[n]["mean_corr_1"] > stats[n]["mean_corr_24"] for n in N_VALUES)
    p3_pass = stats[64]["mean_decay"] < stats[8]["mean_decay"]
    p4_pass = stats[64]["n_above_090"] >= 4

    overall = sum([p1_pass, p2_pass, p3_pass, p4_pass])

    report = {
        "test_id":    "QNG-CPU-060",
        "theory_doc": "DER-BRIDGE-042",
        "n_values":   N_VALUES,
        "seeds":      SEEDS,
        "per_row":    all_rows,
        "stats_by_n": {str(n): stats[n] for n in N_VALUES},
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

    print(f"\n=== QNG-CPU-060 Initial Signature N-Scaling ===")
    print(f"{'N':>4}  {'mean|c|_1':>10}  {'mean|c|_24':>11}  {'mean decay':>11}  {'≥0.90':>6}  P1  P2")
    print("-" * 64)
    for n in N_VALUES:
        s = stats[n]
        p1_n = s["mean_corr_1"] > 0.95
        p2_n = s["mean_corr_1"] > s["mean_corr_24"]
        print(f"{n:>4}  {s['mean_corr_1']:>10.6f}  {s['mean_corr_24']:>11.6f}  "
              f"{s['mean_decay']:>11.6f}  {s['n_above_090']:>6}/5  "
              f"{'✓' if p1_n else '✗'}   {'✓' if p2_n else '✗'}")
    print("-" * 64)
    print(f"P1 {'PASS' if p1_pass else 'FAIL'} (mean|corr_1|>0.95 at all N)  "
          f"P2 {'PASS' if p2_pass else 'FAIL'} (corr_1>corr_24 at all N)")
    print(f"P3 {'PASS' if p3_pass else 'FAIL'} "
          f"(decay N=8→64: {stats[8]['mean_decay']:.6f}→{stats[64]['mean_decay']:.6f})")
    print(f"P4 {'PASS' if p4_pass else 'FAIL'} "
          f"(N=64: {stats[64]['n_above_090']}/5 seeds above 0.90)")
    print(f"OVERALL: {overall}/4")

    print(f"\nPer-seed at N=64:")
    print(f"  {'seed':>10}  {'|corr|_1':>9}  {'|corr|_24':>10}  {'decay':>8}")
    for r in by_n[64]:
        print(f"  {r['seed']:>10}  {r['abs_corr_1']:>9.6f}  {r['abs_corr_24']:>10.6f}  "
              f"{r['decay']:>8.6f}")

    return report


if __name__ == "__main__":
    import sys
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT_DIR
    run_all(out_dir)
