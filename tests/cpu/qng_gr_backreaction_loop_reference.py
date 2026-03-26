"""QNG-CPU-053 — QM↔GR Back-Reaction Loop Closure.

Tests whether the GR tensor E_tt (established QM→GR output) feeds back into
QM density evolution ∂_t(C_eff²) — closing the QM↔GR back-reaction loop.

Uses two-step rollout (same as CPU-046):
    step t:   c_t, phi_t, mismatch_t, mem_t, E_tt_t, E_xx_t
    step t+1: c_{t+1}
    drho_i = c_{t+1,i}² - c_{t,i}²

Fit comparison:
    3ch baseline: drho ≈ -(α_phi·dJ_phi + α_mis·dJ_mis + α_mem·dJ_mem)
    5ch extended: drho ≈ -(α_phi·dJ_phi + α_mis·dJ_mis + α_mem·dJ_mem) + γ_tt·E_tt + γ_xx·E_xx

Pass criteria (from prereg QNG-CPU-053):
    P1: R²(3ch + E_tt) > R²(3ch) on ≥ 4/5 seeds  (GR→QM signal exists)
    P2: sign(γ_tt) consistent on ≥ 4/5 seeds       (coherent feedback direction)
    P3: R²(3ch+E_tt) > R²(3ch+E_xx) on ≥ 3/5      (E_tt stronger than E_xx)
    P4: mean(R²_5ch - R²_3ch) > 0.010              (non-trivial improvement)

Reference (CPU-046): mean R²_3ch = 0.405
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
    ROOT / "07_validation" / "audits" / "qng-gr-backreaction-loop-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def variance(a: list[float]) -> float:
    n = len(a)
    if n == 0:
        return 0.0
    m = sum(a) / n
    return sum((x - m) ** 2 for x in a) / n


def norm2(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def div_J_phase(c: list[float], phi: list[float], adj: list[list[int]]) -> list[float]:
    return [c[i] * sum(c[j] * math.sin(phi[j] - phi[i]) for j in adj[i])
            for i in range(len(c))]


def div_J_grad(c: list[float], f: list[float], adj: list[list[int]]) -> list[float]:
    return [c[i] * sum(c[j] * (f[j] - f[i]) for j in adj[i])
            for i in range(len(c))]


def ols_fit(y: list[float], cols: list[list[float]]) -> dict:
    """OLS fit: minimize ‖y - X·β‖². Returns R², coefficients."""
    m = len(cols)
    n = len(y)
    A = [[sum(cols[i][k] * cols[j][k] for k in range(n)) for j in range(m)]
         for i in range(m)]
    b = [sum(y[k] * cols[i][k] for k in range(n)) for i in range(m)]
    aug = [A[i][:] + [b[i]] for i in range(m)]
    for col in range(m):
        max_row = max(range(col, m), key=lambda r: abs(aug[r][col]))
        aug[col], aug[max_row] = aug[max_row], aug[col]
        p = aug[col][col]
        if abs(p) < 1e-15:
            return {"coeffs": [0.0] * m, "r2": 0.0, "singular": True}
        for k in range(col, m + 1):
            aug[col][k] /= p
        for r in range(m):
            if r == col:
                continue
            fac = aug[r][col]
            for k in range(col, m + 1):
                aug[r][k] -= fac * aug[col][k]
    coeffs = [aug[i][m] for i in range(m)]
    pred = [sum(coeffs[j] * cols[j][k] for j in range(m)) for k in range(n)]
    var_y = variance(y)
    if var_y < 1e-30:
        return {"coeffs": coeffs, "r2": 0.0, "singular": False}
    residual = [y[k] - pred[k] for k in range(n)]
    r2 = 1.0 - variance(residual) / var_y
    return {"coeffs": coeffs, "r2": r2, "singular": False}


# ---------------------------------------------------------------------------
# Two-step rollout (same pattern as CPU-046)
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

def metrics_for_seed(seed: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)
    c_t, c_tp1, phi_t, mismatch_t, mem_t, adj = rollout_two_steps(cfg)

    # QM density change (target)
    drho = [c_tp1[i] ** 2 - c_t[i] ** 2 for i in range(len(c_t))]

    # QM current channels at time t
    dj_phi = div_J_phase(c_t, phi_t, adj)
    dj_mis = div_J_grad(c_t, mismatch_t, adj)
    dj_mem = div_J_grad(c_t, mem_t, adj)

    # GR tensor channels at time t
    # Note: sign convention — drho is the target; GR channels enter as corrections
    asm = assemble_linearized_metric(c_t, phi_t)
    ten = tensorial_proxy(asm)
    e_tt = ten["e_tt"]
    e_xx = ten["e_xx"]

    # Fits
    # 3-channel baseline (CPU-046): drho ≈ α_phi·dJ_phi + α_mis·dJ_mis + α_mem·dJ_mem
    fit3 = ols_fit(drho, [dj_phi, dj_mis, dj_mem])

    # 4-channel with E_tt only
    fit4_ett = ols_fit(drho, [dj_phi, dj_mis, dj_mem, e_tt])

    # 4-channel with E_xx only (comparison)
    fit4_exx = ols_fit(drho, [dj_phi, dj_mis, dj_mem, e_xx])

    # 5-channel with both E_tt and E_xx
    fit5 = ols_fit(drho, [dj_phi, dj_mis, dj_mem, e_tt, e_xx])

    gamma_tt = fit4_ett["coeffs"][3]   # E_tt coefficient in 4ch fit
    gamma_xx = fit4_exx["coeffs"][3]   # E_xx coefficient in 4ch fit

    return {
        "seed": seed,
        "r2_3ch": fit3["r2"],
        "r2_4ch_ett": fit4_ett["r2"],
        "r2_4ch_exx": fit4_exx["r2"],
        "r2_5ch": fit5["r2"],
        "delta_r2_ett": fit4_ett["r2"] - fit3["r2"],
        "delta_r2_5ch": fit5["r2"] - fit3["r2"],
        "gamma_tt": gamma_tt,
        "gamma_xx": gamma_xx,
        "sign_gamma_tt": 1 if gamma_tt > 0 else -1,
        "ett_beats_exx": fit4_ett["r2"] > fit4_exx["r2"],
        "ett_improves": fit4_ett["r2"] > fit3["r2"],
        "coeffs_3ch": fit3["coeffs"],
        "coeffs_4ch_ett": fit4_ett["coeffs"],
        "coeffs_5ch": fit5["coeffs"],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    results = [metrics_for_seed(s) for s in SEEDS]

    # Evaluate predictions
    n_ett_improves = sum(r["ett_improves"] for r in results)
    n_ett_beats_exx = sum(r["ett_beats_exx"] for r in results)

    signs = [r["sign_gamma_tt"] for r in results]
    majority_sign = 1 if sum(signs) >= 0 else -1
    n_sign_consistent = sum(1 for s in signs if s == majority_sign)

    mean_delta_5ch = sum(r["delta_r2_5ch"] for r in results) / len(results)
    mean_delta_ett = sum(r["delta_r2_ett"] for r in results) / len(results)

    p1_pass = n_ett_improves >= 4
    p2_pass = n_sign_consistent >= 4
    p3_pass = n_ett_beats_exx >= 3
    p4_pass = mean_delta_5ch > 0.010

    n_pass = sum([p1_pass, p2_pass, p3_pass, p4_pass])
    decision = "pass" if n_pass >= 3 else ("partial" if n_pass >= 2 else "fail")

    if p1_pass and p2_pass:
        tier = "Tier-1 (loop closes)"
    elif p1_pass:
        tier = "Tier-2 (signal exists, direction topology-dependent)"
    else:
        tier = "no-signal"

    # Print
    print("=" * 72)
    print("QNG-CPU-053 — QM↔GR Back-Reaction Loop Closure")
    print("=" * 72)
    print()
    print(f"{'Seed':>10}  {'R²_3ch':>8}  {'R²_4ch(tt)':>10}  {'Δ(tt)':>8}  {'R²_5ch':>8}  {'γ_tt':>8}  {'sign':>5}")
    print("-" * 70)
    for r in results:
        print(
            f"{r['seed']:>10}  {r['r2_3ch']:>8.4f}  {r['r2_4ch_ett']:>10.4f}  "
            f"{r['delta_r2_ett']:>+8.4f}  {r['r2_5ch']:>8.4f}  "
            f"{r['gamma_tt']:>+8.4f}  {r['sign_gamma_tt']:>+5d}"
        )
    print()
    print(f"mean R²_3ch: {sum(r['r2_3ch'] for r in results)/len(results):.4f}")
    print(f"mean R²_5ch: {sum(r['r2_5ch'] for r in results)/len(results):.4f}")
    print(f"mean Δ(E_tt):  {mean_delta_ett:>+.4f}")
    print(f"mean Δ(5ch):   {mean_delta_5ch:>+.4f}")
    print()
    print(f"P1 (E_tt improves ≥ 4/5):              {'PASS' if p1_pass else 'FAIL'} ({n_ett_improves}/5)")
    print(f"P2 (sign(γ_tt) consistent ≥ 4/5):      {'PASS' if p2_pass else 'FAIL'} ({n_sign_consistent}/5, majority={majority_sign:+d})")
    print(f"P3 (E_tt > E_xx on ≥ 3/5):             {'PASS' if p3_pass else 'FAIL'} ({n_ett_beats_exx}/5)")
    print(f"P4 (mean Δ_5ch > 0.010):               {'PASS' if p4_pass else 'FAIL'} ({mean_delta_5ch:.4f})")
    print()
    print(f"Decision: {decision.upper()} ({n_pass}/4 predictions)")
    print(f"Tier: {tier}")

    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "test": "QNG-CPU-053",
        "theory": "DER-BRIDGE-035",
        "decision": decision,
        "tier": tier,
        "n_pass": n_pass,
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "p3_pass": p3_pass,
        "p4_pass": p4_pass,
        "n_ett_improves": n_ett_improves,
        "n_sign_consistent": n_sign_consistent,
        "n_ett_beats_exx": n_ett_beats_exx,
        "majority_sign_gamma_tt": majority_sign,
        "mean_delta_r2_ett": mean_delta_ett,
        "mean_delta_r2_5ch": mean_delta_5ch,
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
