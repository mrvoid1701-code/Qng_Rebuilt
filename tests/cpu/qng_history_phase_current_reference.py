"""QNG-CPU-044 — History-Phase Current Proxy.

Tests whether using history.phase (accumulated local phase gradient memory)
instead of phi as the phase field gives better calibrated continuity balance.

Construction:
    J_hp_{i→j} = C_eff_i · C_eff_j · sin(history.phase_j - history.phase_i)
    div(J_hp)_i = C_eff_i · Σ_j C_eff_j · sin(history.phase_j - history.phase_i)
    α*_hp = -Σ(Δρ · div(J_hp)) / Σ(div(J_hp)²)
    R²_hp = 1 - Var(Δρ + α* · div(J_hp)) / Var(Δρ)  where ρ = C_eff²

Pass criteria (from prereg QNG-CPU-044):
    P1: R²_hp > R²_std on ≥3/5 seeds
    P2: α*_hp > 0 on ≥3/5 seeds
    P3: mean R²_hp > 0.20
    P4: max R²_hp > 0.50 on ≥1 seed

Reference R²_std from QNG-CPU-042:
    [0.045617, 0.138356, 0.572227, 0.034704, 0.207112]
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
    clone_history,
    clone_state,
    init_state,
    one_step,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = (
    ROOT / "07_validation" / "audits" / "qng-history-phase-current-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]

# Reference baseline from QNG-CPU-042
R2_STD = [0.045617, 0.138356, 0.572227, 0.034704, 0.207112]
ALPHA_STD_CV = 0.7612


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


def div_J_history_phase(
    c_eff: list[float], h_phase: list[float], adj: list[list[int]]
) -> list[float]:
    """div(J_hp)_i = C_eff_i · Σ_j C_eff_j · sin(h_phase_j - h_phase_i)."""
    return [
        c_eff[i] * sum(c_eff[j] * math.sin(h_phase[j] - h_phase[i]) for j in adj[i])
        for i in range(len(c_eff))
    ]


def div_J_standard(
    c_eff: list[float], phi: list[float], adj: list[list[int]]
) -> list[float]:
    """div(J_std)_i = C_eff_i · Σ_j C_eff_j · sin(phi_j - phi_i)."""
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
# Two-step rollout (to compute Δρ = ρ(t+1) - ρ(t))
# ---------------------------------------------------------------------------

def rollout_two_steps(cfg: Config, use_history: bool):
    """Return (c_eff_t, c_eff_tp1, phi_t, h_phase_t, adj) at the penultimate step."""
    import random as _random
    rng = _random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)

    # Run cfg.steps - 1 steps
    for _ in range(cfg.steps - 1):
        state, history = one_step(state, history, adj, cfg, use_history)

    # Snapshot at t
    c_t, _ = field_extract(state, history)
    phi_t = state.phi[:]
    h_phase_t = history.phase[:]

    # One more step
    state_tp1, history_tp1 = one_step(state, history, adj, cfg, use_history)
    c_tp1, _ = field_extract(state_tp1, history_tp1)

    return c_t, c_tp1, phi_t, h_phase_t, adj


# ---------------------------------------------------------------------------
# Per-seed metrics
# ---------------------------------------------------------------------------

def metrics_for_seed(seed: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)

    # With history
    c_t, c_tp1, phi_t, h_phase_t, adj = rollout_two_steps(cfg, use_history=True)

    # Density ρ = C_eff²
    rho_t = [c ** 2 for c in c_t]
    rho_tp1 = [c ** 2 for c in c_tp1]
    drho = [r1 - r0 for r0, r1 in zip(rho_t, rho_tp1)]

    # History-phase current
    dj_hp = div_J_history_phase(c_t, h_phase_t, adj)
    alpha_hp = optimal_alpha(drho, dj_hp)
    r2_hp = r2_calibrated(drho, dj_hp, alpha_hp)
    corr_hp = corr(drho, [-d for d in dj_hp])

    # Standard phi current (for per-seed comparison)
    dj_std = div_J_standard(c_t, phi_t, adj)
    alpha_std = optimal_alpha(drho, dj_std)
    r2_std_local = r2_calibrated(drho, dj_std, alpha_std)
    corr_std = corr(drho, [-d for d in dj_std])

    # Scale comparison
    rms_j_hp = math.sqrt(sum(d ** 2 for d in dj_hp) / len(dj_hp)) if dj_hp else 0.0
    rms_j_std = math.sqrt(sum(d ** 2 for d in dj_std) / len(dj_std)) if dj_std else 0.0
    rms_drho = math.sqrt(sum(d ** 2 for d in drho) / len(drho)) if drho else 0.0
    scale_ratio_hp = rms_j_hp / rms_drho if rms_drho > 1e-20 else 0.0
    scale_ratio_std = rms_j_std / rms_drho if rms_drho > 1e-20 else 0.0

    # Variance of phase fields
    var_phi = variance(phi_t)
    var_h_phase = variance(h_phase_t)

    # Corr between phi and history.phase
    corr_phi_hphase = corr(phi_t, h_phase_t)

    return {
        "seed": seed,
        "r2_hp": r2_hp,
        "r2_std_local": r2_std_local,
        "alpha_hp": alpha_hp,
        "alpha_std_local": alpha_std_local if False else alpha_std,
        "corr_hp": corr_hp,
        "corr_std": corr_std,
        "scale_ratio_hp": scale_ratio_hp,
        "scale_ratio_std": scale_ratio_std,
        "var_phi": var_phi,
        "var_h_phase": var_h_phase,
        "corr_phi_hphase": corr_phi_hphase,
        "r2_hp_beats_std": r2_hp > r2_std_local,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    results = [metrics_for_seed(s) for s in SEEDS]

    r2_hp_vals = [r["r2_hp"] for r in results]
    r2_std_vals = [r["r2_std_local"] for r in results]
    alpha_hp_vals = [r["alpha_hp"] for r in results]

    mean_r2_hp = statistics.mean(r2_hp_vals)
    mean_r2_std = statistics.mean(r2_std_vals)
    max_r2_hp = max(r2_hp_vals)
    mean_alpha_abs = statistics.mean(abs(a) for a in alpha_hp_vals)
    cv_alpha = (
        statistics.stdev([abs(a) for a in alpha_hp_vals]) / mean_alpha_abs
        if mean_alpha_abs > 1e-20
        else 0.0
    )

    # Pass criteria
    n_beats_std = sum(1 for r in results if r["r2_hp"] > r["r2_std_local"])
    n_alpha_pos = sum(1 for a in alpha_hp_vals if a > 0)

    p1_pass = n_beats_std >= 3
    p2_pass = n_alpha_pos >= 3
    p3_pass = mean_r2_hp > 0.20
    p4_pass = max_r2_hp > 0.50

    n_pass = sum([p1_pass, p2_pass, p3_pass, p4_pass])
    decision = "pass" if n_pass >= 3 else ("partial" if n_pass >= 2 else "fail")

    # Print summary
    print("=" * 60)
    print("QNG-CPU-044 — History-Phase Current Proxy")
    print("=" * 60)
    print(f"{'Seed':>10}  {'R²_hp':>8}  {'R²_std':>8}  {'Δ':>8}  {'α*_hp':>12}  {'beats':>5}")
    for r in results:
        delta = r["r2_hp"] - r["r2_std_local"]
        flag = "YES" if r["r2_hp_beats_std"] else "---"
        print(
            f"{r['seed']:>10}  {r['r2_hp']:>8.6f}  {r['r2_std_local']:>8.6f}  "
            f"{delta:>+8.6f}  {r['alpha_hp']:>12.6f}  {flag:>5}"
        )
    print()
    print(f"mean R²_hp = {mean_r2_hp:.6f}   mean R²_std = {mean_r2_std:.6f}")
    print(f"max  R²_hp = {max_r2_hp:.6f}")
    print(f"mean|α*_hp| = {mean_alpha_abs:.6f}   cv = {cv_alpha:.4f}")
    print()
    print(f"P1 (R²_hp beats std on ≥3/5): {'PASS' if p1_pass else 'FAIL'} ({n_beats_std}/5)")
    print(f"P2 (α*_hp > 0 on ≥3/5):      {'PASS' if p2_pass else 'FAIL'} ({n_alpha_pos}/5)")
    print(f"P3 (mean R²_hp > 0.20):       {'PASS' if p3_pass else 'FAIL'} ({mean_r2_hp:.4f})")
    print(f"P4 (max R²_hp > 0.50):        {'PASS' if p4_pass else 'FAIL'} ({max_r2_hp:.4f})")
    print(f"\nDecision: {decision.upper()} ({n_pass}/4 predictions)")

    # Phase field comparison
    print("\n--- Phase field diagnostics ---")
    print(f"{'Seed':>10}  {'var(phi)':>10}  {'var(h.phase)':>12}  {'corr(phi,hp)':>12}  {'scale_hp':>10}  {'scale_std':>10}")
    for r in results:
        print(
            f"{r['seed']:>10}  {r['var_phi']:>10.6f}  {r['var_h_phase']:>12.6f}  "
            f"{r['corr_phi_hphase']:>12.6f}  {r['scale_ratio_hp']:>10.2f}  {r['scale_ratio_std']:>10.2f}"
        )

    # Save report
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "test": "QNG-CPU-044",
        "theory": "DER-BRIDGE-026",
        "decision": decision,
        "n_pass": n_pass,
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "p3_pass": p3_pass,
        "p4_pass": p4_pass,
        "n_beats_std": n_beats_std,
        "n_alpha_pos": n_alpha_pos,
        "mean_r2_hp": mean_r2_hp,
        "mean_r2_std": mean_r2_std,
        "max_r2_hp": max_r2_hp,
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
