"""QNG-CPU-045 — Mismatch-Gradient Current Proxy.

Tests whether replacing sin(Δφ) with (mismatch_j - mismatch_i) as the
current driver gives better calibrated continuity balance.

Also tests memory-gradient current (mem_j - mem_i) for comparison.

Pass criteria (from prereg QNG-CPU-045):
    P1: R²_mis > R²_std on ≥4/5 seeds
    P2: mean R²_mis > 0.40
    P3: max R²_mis > 0.57
    P4: R²_mis > R²_mem on ≥3/5 seeds

Reference R²_std from QNG-CPU-042:
    seed 20260325: 0.045617
    seed 42:       0.138356
    seed 137:      0.572227
    seed 1729:     0.034704
    seed 2718:     0.207112
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
    ROOT / "07_validation" / "audits" / "qng-mismatch-current-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]

# Reference baseline from QNG-CPU-042 (phi current)
R2_STD = [0.045617, 0.138356, 0.572227, 0.034704, 0.207112]


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def variance(a: list[float]) -> float:
    n = len(a)
    if n == 0:
        return 0.0
    m = sum(a) / n
    return sum((x - m) ** 2 for x in a) / n


def corr(a: list[float], b: list[float]) -> float:
    va = variance(a)
    vb = variance(b)
    if va < 1e-30 or vb < 1e-30:
        return 0.0
    ma = sum(a) / len(a)
    mb = sum(b) / len(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / len(a)
    return cov / (math.sqrt(va) * math.sqrt(vb))


def div_J_gradient(
    c_eff: list[float], field: list[float], adj: list[list[int]]
) -> list[float]:
    """div(J_X)_i = C_eff_i · Σ_j C_eff_j · (field_j - field_i).

    Works for any scalar gradient-based current (mismatch, mem, etc.)
    Anti-symmetric by construction: field_j - field_i = -(field_i - field_j).
    """
    return [
        c_eff[i] * sum(c_eff[j] * (field[j] - field[i]) for j in adj[i])
        for i in range(len(c_eff))
    ]


def div_J_phase(
    c_eff: list[float], phi: list[float], adj: list[list[int]]
) -> list[float]:
    """Standard phi-based current for comparison."""
    return [
        c_eff[i] * sum(c_eff[j] * math.sin(phi[j] - phi[i]) for j in adj[i])
        for i in range(len(c_eff))
    ]


def optimal_alpha(drho: list[float], dj: list[float]) -> float:
    """α* = -Σ(Δρ·divJ) / Σ(divJ²)."""
    num = sum(dr * dj_ for dr, dj_ in zip(drho, dj))
    den = sum(dj_ * dj_ for dj_ in dj)
    return -num / den if abs(den) > 1e-20 else 0.0


def r2_calibrated(drho: list[float], dj: list[float], alpha: float) -> float:
    var_drho = variance(drho)
    if var_drho < 1e-30:
        return 0.0
    residual = [dr + alpha * dj_ for dr, dj_ in zip(drho, dj)]
    return 1.0 - variance(residual) / var_drho


# ---------------------------------------------------------------------------
# Two-step rollout
# ---------------------------------------------------------------------------

def rollout_two_steps(cfg: Config, use_history: bool):
    """Return (c_t, c_tp1, phi_t, mismatch_t, mem_t, adj) at penultimate step."""
    import random as _random
    rng = _random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)

    for _ in range(cfg.steps - 1):
        state, history = one_step(state, history, adj, cfg, use_history)

    c_t, _ = field_extract(state, history)
    phi_t = state.phi[:]
    mismatch_t = history.mismatch[:]
    mem_t = history.mem[:]

    state_tp1, history_tp1 = one_step(state, history, adj, cfg, use_history)
    c_tp1, _ = field_extract(state_tp1, history_tp1)

    return c_t, c_tp1, phi_t, mismatch_t, mem_t, adj


# ---------------------------------------------------------------------------
# Per-seed metrics
# ---------------------------------------------------------------------------

def metrics_for_seed(seed: int, r2_std_ref: float) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)
    c_t, c_tp1, phi_t, mismatch_t, mem_t, adj = rollout_two_steps(cfg, use_history=True)

    # Density ρ = C_eff²
    rho_t = [c ** 2 for c in c_t]
    rho_tp1 = [c ** 2 for c in c_tp1]
    drho = [r1 - r0 for r0, r1 in zip(rho_t, rho_tp1)]

    # Mismatch-gradient current
    dj_mis = div_J_gradient(c_t, mismatch_t, adj)
    alpha_mis = optimal_alpha(drho, dj_mis)
    r2_mis = r2_calibrated(drho, dj_mis, alpha_mis)
    corr_mis = corr(drho, [-d for d in dj_mis])

    # Memory-gradient current
    dj_mem = div_J_gradient(c_t, mem_t, adj)
    alpha_mem = optimal_alpha(drho, dj_mem)
    r2_mem = r2_calibrated(drho, dj_mem, alpha_mem)
    corr_mem = corr(drho, [-d for d in dj_mem])

    # Phi current (local recompute for same seed/step)
    dj_phi = div_J_phase(c_t, phi_t, adj)
    alpha_phi = optimal_alpha(drho, dj_phi)
    r2_phi = r2_calibrated(drho, dj_phi, alpha_phi)

    # Scale ratios
    def rms(v):
        return math.sqrt(sum(x ** 2 for x in v) / len(v)) if v else 0.0

    rms_drho = rms(drho)
    scale_mis = rms(dj_mis) / rms_drho if rms_drho > 1e-20 else 0.0
    scale_mem = rms(dj_mem) / rms_drho if rms_drho > 1e-20 else 0.0
    scale_phi = rms(dj_phi) / rms_drho if rms_drho > 1e-20 else 0.0

    # Field stats
    var_mis = variance(mismatch_t)
    var_mem = variance(mem_t)
    mean_mis = sum(mismatch_t) / len(mismatch_t)
    mean_mem = sum(mem_t) / len(mem_t)

    return {
        "seed": seed,
        "r2_mis": r2_mis,
        "r2_mem": r2_mem,
        "r2_phi": r2_phi,
        "r2_std_ref": r2_std_ref,
        "alpha_mis": alpha_mis,
        "alpha_mem": alpha_mem,
        "alpha_phi": alpha_phi,
        "corr_mis": corr_mis,
        "corr_mem": corr_mem,
        "scale_mis": scale_mis,
        "scale_mem": scale_mem,
        "scale_phi": scale_phi,
        "var_mismatch": var_mis,
        "var_mem": var_mem,
        "mean_mismatch": mean_mis,
        "mean_mem": mean_mem,
        "r2_mis_beats_std": r2_mis > r2_std_ref,
        "r2_mis_beats_mem": r2_mis > r2_mem,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    results = [metrics_for_seed(s, r) for s, r in zip(SEEDS, R2_STD)]

    r2_mis_vals = [r["r2_mis"] for r in results]
    r2_mem_vals = [r["r2_mem"] for r in results]
    r2_phi_vals = [r["r2_phi"] for r in results]
    alpha_mis_vals = [r["alpha_mis"] for r in results]

    mean_r2_mis = statistics.mean(r2_mis_vals)
    mean_r2_mem = statistics.mean(r2_mem_vals)
    mean_r2_phi = statistics.mean(r2_phi_vals)
    max_r2_mis = max(r2_mis_vals)
    mean_alpha_abs = statistics.mean(abs(a) for a in alpha_mis_vals)
    cv_alpha = (
        statistics.stdev([abs(a) for a in alpha_mis_vals]) / mean_alpha_abs
        if mean_alpha_abs > 1e-20
        else 0.0
    )

    n_mis_beats_std = sum(1 for r in results if r["r2_mis_beats_std"])
    n_mis_beats_mem = sum(1 for r in results if r["r2_mis_beats_mem"])

    p1_pass = n_mis_beats_std >= 4
    p2_pass = mean_r2_mis > 0.40
    p3_pass = max_r2_mis > 0.57
    p4_pass = n_mis_beats_mem >= 3

    n_pass = sum([p1_pass, p2_pass, p3_pass, p4_pass])
    decision = "pass" if n_pass >= 3 else ("partial" if n_pass >= 2 else "fail")

    print("=" * 72)
    print("QNG-CPU-045 — Mismatch-Gradient Current Proxy")
    print("=" * 72)
    print(f"{'Seed':>10}  {'R²_mis':>8}  {'R²_mem':>8}  {'R²_phi':>8}  {'R²_ref':>8}  {'Δ(mis-ref)':>10}")
    for r in results:
        delta = r["r2_mis"] - r["r2_std_ref"]
        print(
            f"{r['seed']:>10}  {r['r2_mis']:>8.6f}  {r['r2_mem']:>8.6f}  "
            f"{r['r2_phi']:>8.6f}  {r['r2_std_ref']:>8.6f}  {delta:>+10.6f}"
        )
    print()
    print(f"mean R²: mis={mean_r2_mis:.6f}  mem={mean_r2_mem:.6f}  phi={mean_r2_phi:.6f}")
    print(f"max  R²_mis = {max_r2_mis:.6f}")
    print(f"mean|α*_mis| = {mean_alpha_abs:.6f}   cv = {cv_alpha:.4f}")
    print()
    print(f"P1 (R²_mis > R²_std on ≥4/5): {'PASS' if p1_pass else 'FAIL'} ({n_mis_beats_std}/5)")
    print(f"P2 (mean R²_mis > 0.40):       {'PASS' if p2_pass else 'FAIL'} ({mean_r2_mis:.4f})")
    print(f"P3 (max R²_mis > 0.57):        {'PASS' if p3_pass else 'FAIL'} ({max_r2_mis:.4f})")
    print(f"P4 (R²_mis > R²_mem on ≥3/5): {'PASS' if p4_pass else 'FAIL'} ({n_mis_beats_mem}/5)")
    print(f"\nDecision: {decision.upper()} ({n_pass}/4 predictions)")

    print("\n--- Field diagnostics ---")
    print(f"{'Seed':>10}  {'var(mis)':>10}  {'var(mem)':>10}  {'scale_mis':>10}  {'scale_mem':>10}  {'scale_phi':>10}")
    for r in results:
        print(
            f"{r['seed']:>10}  {r['var_mismatch']:>10.6f}  {r['var_mem']:>10.6f}  "
            f"{r['scale_mis']:>10.2f}  {r['scale_mem']:>10.2f}  {r['scale_phi']:>10.2f}"
        )

    # Save report
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "test": "QNG-CPU-045",
        "theory": "DER-BRIDGE-027",
        "decision": decision,
        "n_pass": n_pass,
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "p3_pass": p3_pass,
        "p4_pass": p4_pass,
        "n_mis_beats_std": n_mis_beats_std,
        "n_mis_beats_mem": n_mis_beats_mem,
        "mean_r2_mis": mean_r2_mis,
        "mean_r2_mem": mean_r2_mem,
        "mean_r2_phi": mean_r2_phi,
        "max_r2_mis": max_r2_mis,
        "mean_alpha_abs": mean_alpha_abs,
        "cv_alpha": cv_alpha,
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
