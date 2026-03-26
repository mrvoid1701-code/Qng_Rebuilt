"""QNG-CPU-061 — History Signature Preservation: Anti-Ordering N-Scaling.

Compares Lorentzian signature decay (|corr(E_tt,E_xx)| step1→step24) between
history-on and history-off rollouts across N={8,16,32,64}.

Pass criteria (from prereg QNG-CPU-061):
    P1: decay_nohist > decay_hist at each N in {8,16,32,64}
    P2: |corr_24_hist| > |corr_24_nohist| at each N
    P3: Δ_nohist follows power law (R² > 0.9 across N)
    P4: benefit = decay_nohist − decay_hist positive on ≥ 4/5 seeds at N=32
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
    / "qng-gr-history-signature-preservation-reference-v1"
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


def abs_corr_ett_exx(c: list[float], phi: list[float]) -> float:
    asm = assemble_linearized_metric(c, phi)
    ten = tensorial_proxy(asm)
    return abs(pearson(ten["e_tt"], ten["e_xx"]))


def power_law_fit(ns: list[int], vals: list[float]):
    """Fit log(val) = a + b*log(N) via OLS."""
    log_n = [math.log(n) for n in ns]
    log_v = [math.log(max(v, 1e-15)) for v in vals]
    n = len(log_n)
    mn, mv = mean(log_n), mean(log_v)
    num = sum((log_n[i] - mn) * (log_v[i] - mv) for i in range(n))
    den = sum((x - mn) ** 2 for x in log_n)
    b = num / den if abs(den) > 1e-15 else 0.0
    a = mv - b * mn
    pred = [a + b * x for x in log_n]
    r2 = 1.0 - sum((log_v[i] - pred[i]) ** 2 for i in range(n)) / \
         sum((x - mv) ** 2 for x in log_v) if sum((x - mv) ** 2 for x in log_v) > 1e-15 else 0.0
    return {"exponent": b, "prefactor": math.exp(a), "r2": r2}


# ---------------------------------------------------------------------------
# Metric anticorrelation at a specific step (no trajectory needed)
# ---------------------------------------------------------------------------

def abs_corr_at_step(seed: int, n_nodes: int, target_step: int, use_history: bool) -> float:
    import random as _rng
    cfg = dataclasses.replace(Config(), seed=seed, n_nodes=n_nodes)
    rng = _rng.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)
    for _ in range(target_step):
        state, history = one_step(state, history, adj, cfg, use_history=use_history)
    c, _ = field_extract(state, history)
    return abs_corr_ett_exx(c, state.phi[:])


# ---------------------------------------------------------------------------
# Per (seed, N)
# ---------------------------------------------------------------------------

def run_one(seed: int, n_nodes: int) -> dict:
    c1_h   = abs_corr_at_step(seed, n_nodes, 1,     use_history=True)
    c24_h  = abs_corr_at_step(seed, n_nodes, STEPS, use_history=True)
    c1_nh  = abs_corr_at_step(seed, n_nodes, 1,     use_history=False)
    c24_nh = abs_corr_at_step(seed, n_nodes, STEPS, use_history=False)

    decay_h  = c1_h  - c24_h
    decay_nh = c1_nh - c24_nh
    benefit  = decay_nh - decay_h   # positive = history helps

    return {
        "seed":          seed,
        "n_nodes":       n_nodes,
        "corr1_hist":    c1_h,
        "corr24_hist":   c24_h,
        "corr1_nohist":  c1_nh,
        "corr24_nohist": c24_nh,
        "decay_hist":    decay_h,
        "decay_nohist":  decay_nh,
        "benefit":       benefit,
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

    # Aggregate per N
    agg = {}
    for n in N_VALUES:
        rows = by_n[n]
        agg[n] = {
            "mean_decay_hist":    mean([r["decay_hist"]    for r in rows]),
            "mean_decay_nohist":  mean([r["decay_nohist"]  for r in rows]),
            "mean_corr24_hist":   mean([r["corr24_hist"]   for r in rows]),
            "mean_corr24_nohist": mean([r["corr24_nohist"] for r in rows]),
            "mean_benefit":       mean([r["benefit"]       for r in rows]),
            "n_benefit_pos":      sum(1 for r in rows if r["benefit"] > 0),
        }

    # P1: decay_nohist > decay_hist at each N
    p1_pass = all(agg[n]["mean_decay_nohist"] > agg[n]["mean_decay_hist"] for n in N_VALUES)

    # P2: |corr_24_hist| > |corr_24_nohist| at each N
    p2_pass = all(agg[n]["mean_corr24_hist"] > agg[n]["mean_corr24_nohist"] for n in N_VALUES)

    # P3: no-history decay follows power law (R² > 0.9)
    nh_decays = [agg[n]["mean_decay_nohist"] for n in N_VALUES]
    fit_nh = power_law_fit(N_VALUES, nh_decays)
    p3_pass = fit_nh["r2"] > 0.9

    # Also fit history decay for comparison
    h_decays = [agg[n]["mean_decay_hist"] for n in N_VALUES]
    fit_h = power_law_fit(N_VALUES, h_decays)

    # P4: benefit consistent sign at N=32
    n_benefit_pos_32 = agg[32]["n_benefit_pos"]
    p4_pass = n_benefit_pos_32 >= 4

    overall = sum([p1_pass, p2_pass, p3_pass, p4_pass])

    report = {
        "test_id":    "QNG-CPU-061",
        "theory_doc": "DER-BRIDGE-043",
        "n_values":   N_VALUES,
        "seeds":      SEEDS,
        "per_row":    all_rows,
        "agg_by_n":   {str(n): agg[n] for n in N_VALUES},
        "power_law_hist":   fit_h,
        "power_law_nohist": fit_nh,
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

    print(f"\n=== QNG-CPU-061 History Signature Preservation ===")
    print(f"{'N':>4}  {'Δ_hist':>8}  {'Δ_nohist':>10}  {'benefit':>9}  "
          f"{'|c|24_h':>8}  {'|c|24_nh':>9}  P1  P2  (+ben)")
    print("-" * 76)
    for n in N_VALUES:
        a = agg[n]
        p1n = a["mean_decay_nohist"] > a["mean_decay_hist"]
        p2n = a["mean_corr24_hist"]  > a["mean_corr24_nohist"]
        print(f"{n:>4}  {a['mean_decay_hist']:>8.6f}  {a['mean_decay_nohist']:>10.6f}  "
              f"{a['mean_benefit']:>9.6f}  {a['mean_corr24_hist']:>8.6f}  "
              f"{a['mean_corr24_nohist']:>9.6f}  "
              f"{'✓' if p1n else '✗'}   {'✓' if p2n else '✗'}   "
              f"{a['n_benefit_pos']}/5")
    print("-" * 76)
    print(f"P1 {'PASS' if p1_pass else 'FAIL'}  P2 {'PASS' if p2_pass else 'FAIL'}  "
          f"P3 {'PASS' if p3_pass else 'FAIL'} (R²={fit_nh['r2']:.4f})  "
          f"P4 {'PASS' if p4_pass else 'FAIL'} ({n_benefit_pos_32}/5 at N=32)")
    print(f"OVERALL: {overall}/4")
    print(f"\nPower-law fits:")
    print(f"  Δ_hist   ~ N^({fit_h['exponent']:+.3f})  "
          f"(prefactor={fit_h['prefactor']:.4f}, R²={fit_h['r2']:.4f})")
    print(f"  Δ_nohist ~ N^({fit_nh['exponent']:+.3f})  "
          f"(prefactor={fit_nh['prefactor']:.4f}, R²={fit_nh['r2']:.4f})")
    ratio_exp = fit_nh["exponent"] - fit_h["exponent"]
    print(f"  Exponent difference (nh−h): {ratio_exp:+.3f}")
    if abs(ratio_exp) < 0.1:
        print(f"  → Same decay law; history reduces PREFACTOR only")
    elif ratio_exp < 0:
        print(f"  → No-history decays SLOWER at large N (smaller |exponent|)")
    else:
        print(f"  → No-history decays FASTER at large N (larger |exponent|)")

    return report


if __name__ == "__main__":
    import sys
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT_DIR
    run_all(out_dir)
