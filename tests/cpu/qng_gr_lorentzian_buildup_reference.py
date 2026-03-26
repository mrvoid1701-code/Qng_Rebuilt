"""QNG-CPU-059 — Lorentzian Signature Buildup via Phi Dynamics.

Tracks how the metric anti-correlation corr(E_tt, E_xx) evolves step-by-step
through the rollout (t=1..24), testing whether Lorentzian signature emerges
dynamically and whether phi synchronization drives it.

Pass criteria (from prereg QNG-CPU-059):
    P1: |corr(E_tt,E_xx)| at step 24 > step 1 on ≥ 4/5 seeds
    P2: mean_t(|corr_hist(t)|) > mean_t(|corr_nohist(t)|) on ≥ 4/5 seeds
    P3: Pearson(r(t), |corr(t)|) across t > 0.2 on ≥ 3/5 seeds
    P4: |corr_24|−|corr_12| < |corr_12|−|corr_1| on ≥ 4/5 seeds (convergence)
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
    / "qng-gr-lorentzian-buildup-reference-v1"
)

SEEDS  = [20260325, 42, 137, 1729, 2718]
STEPS  = 24   # default Config steps


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


def kuramoto_order(phi: list[float]) -> float:
    """Kuramoto order parameter: |Σ exp(i·phi_k)| / N."""
    n = len(phi)
    re = sum(math.cos(p) for p in phi) / n
    im = sum(math.sin(p) for p in phi) / n
    return math.sqrt(re * re + im * im)


# ---------------------------------------------------------------------------
# Metric diagnostics at a single state
# ---------------------------------------------------------------------------

def metric_at_state(c: list[float], phi: list[float]) -> dict:
    asm  = assemble_linearized_metric(c, phi)
    ten  = tensorial_proxy(asm)
    e_tt = ten["e_tt"]
    e_xx = ten["e_xx"]
    return {
        "corr_tt_xx":   pearson(e_tt, e_xx),
        "frac_htt_neg": sum(1 for x in e_tt if x < 0) / len(e_tt),
        "frac_hxx_pos": sum(1 for x in e_xx if x > 0) / len(e_xx),
    }


# ---------------------------------------------------------------------------
# Full-trajectory rollout
# ---------------------------------------------------------------------------

def run_trajectory(cfg: Config, use_history: bool) -> list[dict]:
    """Run rollout for STEPS steps; record metric at each step."""
    import random as _rng
    rng = _rng.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)

    trajectory = []
    for t in range(1, STEPS + 1):
        state, history = one_step(state, history, adj, cfg, use_history=use_history)
        c, _ = field_extract(state, history)
        phi  = state.phi[:]
        met  = metric_at_state(c, phi)
        kord = kuramoto_order(phi)
        trajectory.append({
            "step":         t,
            "corr_tt_xx":   met["corr_tt_xx"],
            "frac_htt_neg": met["frac_htt_neg"],
            "frac_hxx_pos": met["frac_hxx_pos"],
            "kuramoto":     kord,
            "abs_corr":     abs(met["corr_tt_xx"]),
        })
    return trajectory


# ---------------------------------------------------------------------------
# Per-seed
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)

    traj_hist   = run_trajectory(cfg, use_history=True)
    traj_nohist = run_trajectory(cfg, use_history=False)

    abs_corr_hist   = [s["abs_corr"] for s in traj_hist]
    abs_corr_nohist = [s["abs_corr"] for s in traj_nohist]
    kuramoto_hist   = [s["kuramoto"] for s in traj_hist]

    # P1: |corr| at step 24 > step 1
    p1_pass = abs_corr_hist[-1] > abs_corr_hist[0]

    # P2: mean_t(|corr_hist|) > mean_t(|corr_nohist|)
    p2_pass = mean(abs_corr_hist) > mean(abs_corr_nohist)

    # P3: Pearson(kuramoto(t), |corr_hist(t)|) across t > 0.2
    corr_kur_sig = pearson(kuramoto_hist, abs_corr_hist)
    p3_pass = corr_kur_sig > 0.2

    # P4: convergence — |corr_24|−|corr_12| < |corr_12|−|corr_1|
    half = STEPS // 2
    delta_late  = abs(abs_corr_hist[-1]      - abs_corr_hist[half - 1])
    delta_early = abs(abs_corr_hist[half - 1] - abs_corr_hist[0])
    p4_pass = delta_late < delta_early

    return {
        "seed":             seed,
        "abs_corr_step1":   abs_corr_hist[0],
        "abs_corr_step12":  abs_corr_hist[half - 1],
        "abs_corr_step24":  abs_corr_hist[-1],
        "abs_corr_nohist_mean": mean(abs_corr_nohist),
        "abs_corr_hist_mean":   mean(abs_corr_hist),
        "corr_kur_sig":     corr_kur_sig,
        "kuramoto_final":   kuramoto_hist[-1],
        "frac_htt_neg_final": traj_hist[-1]["frac_htt_neg"],
        "frac_hxx_pos_final": traj_hist[-1]["frac_hxx_pos"],
        "delta_early":      delta_early,
        "delta_late":       delta_late,
        "p1_pass":          p1_pass,
        "p2_pass":          p2_pass,
        "p3_pass":          p3_pass,
        "p4_pass":          p4_pass,
        # Keep trajectory for report
        "trajectory_hist":   traj_hist,
        "trajectory_nohist": traj_nohist,
    }


# ---------------------------------------------------------------------------
# Aggregate and report
# ---------------------------------------------------------------------------

def run_all(out_dir: Path = DEFAULT_OUT_DIR) -> dict:
    results = [run_seed(s) for s in SEEDS]

    n_p1 = sum(r["p1_pass"] for r in results)
    n_p2 = sum(r["p2_pass"] for r in results)
    n_p3 = sum(r["p3_pass"] for r in results)
    n_p4 = sum(r["p4_pass"] for r in results)

    p1_pass = n_p1 >= 4
    p2_pass = n_p2 >= 4
    p3_pass = n_p3 >= 3
    p4_pass = n_p4 >= 4

    overall = sum([p1_pass, p2_pass, p3_pass, p4_pass])

    # Strip trajectories from per_seed for compact report
    per_seed_compact = []
    for r in results:
        rc = {k: v for k, v in r.items() if k not in ("trajectory_hist", "trajectory_nohist")}
        per_seed_compact.append(rc)

    report = {
        "test_id":    "QNG-CPU-059",
        "theory_doc": "DER-BRIDGE-041",
        "seeds":      SEEDS,
        "per_seed":   per_seed_compact,
        "summary": {
            "n_p1": n_p1, "p1_pass": p1_pass,
            "n_p2": n_p2, "p2_pass": p2_pass,
            "n_p3": n_p3, "p3_pass": p3_pass,
            "n_p4": n_p4, "p4_pass": p4_pass,
            "overall": f"{overall}/4",
        },
        "key_values": {
            "mean_abs_corr_step1":   mean([r["abs_corr_step1"]  for r in results]),
            "mean_abs_corr_step24":  mean([r["abs_corr_step24"] for r in results]),
            "mean_corr_kur_sig":     mean([r["corr_kur_sig"]    for r in results]),
            "mean_kuramoto_final":   mean([r["kuramoto_final"]  for r in results]),
            "mean_frac_htt_neg_final": mean([r["frac_htt_neg_final"] for r in results]),
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Console output
    print(f"\n=== QNG-CPU-059 Lorentzian Signature Buildup ===")
    print(f"{'Seed':>10}  {'|c|_1':>7}  {'|c|_12':>7}  {'|c|_24':>7}  "
          f"{'r(kur,sig)':>11}  {'kur_f':>7}  {'htt_neg':>8}  P1  P2  P3  P4")
    print("-" * 96)
    for r in results:
        print(f"{r['seed']:>10}  {r['abs_corr_step1']:>7.4f}  {r['abs_corr_step12']:>7.4f}  "
              f"{r['abs_corr_step24']:>7.4f}  {r['corr_kur_sig']:>11.4f}  "
              f"{r['kuramoto_final']:>7.4f}  {r['frac_htt_neg_final']:>8.4f}  "
              f"{'✓' if r['p1_pass'] else '✗'}   "
              f"{'✓' if r['p2_pass'] else '✗'}   "
              f"{'✓' if r['p3_pass'] else '✗'}   "
              f"{'✓' if r['p4_pass'] else '✗'}")
    print("-" * 96)
    print(f"P1 {'PASS' if p1_pass else 'FAIL'} ({n_p1}/5)  "
          f"P2 {'PASS' if p2_pass else 'FAIL'} ({n_p2}/5)  "
          f"P3 {'PASS' if p3_pass else 'FAIL'} ({n_p3}/5, need ≥3)  "
          f"P4 {'PASS' if p4_pass else 'FAIL'} ({n_p4}/5)")
    print(f"OVERALL: {overall}/4")
    kv = report["key_values"]
    print(f"\nKey values:")
    print(f"  mean |corr| step 1  → step 24: {kv['mean_abs_corr_step1']:.4f} → {kv['mean_abs_corr_step24']:.4f}")
    print(f"  mean Pearson(kuramoto, |corr|)  = {kv['mean_corr_kur_sig']:.4f}")
    print(f"  mean kuramoto final             = {kv['mean_kuramoto_final']:.4f}")
    print(f"  mean frac_htt_neg final         = {kv['mean_frac_htt_neg_final']:.4f}")

    # Step-by-step table for first seed
    print(f"\nStep-by-step trajectory for seed {SEEDS[0]} (with history):")
    print(f"  {'t':>3}  {'|corr|':>8}  {'kuramoto':>9}  {'htt_neg':>8}")
    traj = results[0]["trajectory_hist"]
    for s in traj[::4]:   # every 4 steps
        print(f"  {s['step']:>3}  {s['abs_corr']:>8.5f}  {s['kuramoto']:>9.5f}  {s['frac_htt_neg']:>8.4f}")

    return report


if __name__ == "__main__":
    import sys
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT_DIR
    run_all(out_dir)
