"""QNG-CPU-055 — Back-Reaction Fixed-Point Iteration.

Iterates the back-reaction equation from the rollout final state, testing
whether the QM↔GR system converges to a non-trivial fixed point ρ*.

Two iterations compared:
    QM-only:   ρ_{k+1} = ρ_k + η·(-(α_mis·dJ_mis + α_mem·dJ_mem))
    QM+GR:     ρ_{k+1} = ρ_k + η·(-(α_mis·dJ_mis + α_mem·dJ_mem) + γ_tt·E_tt)

Pass criteria (from prereg QNG-CPU-055):
    P1: QM-only ||Δρ|| decreases k=0→29 on ≥ 4/5 seeds
    P2: QM+GR  ||Δρ|| decreases on ≥ 4/5 seeds
    P3: ||ρ*_QM+GR − ρ*_QM|| > 0.001 on ≥ 3/5 seeds
    P4: ||Δρ_29||_QM+GR < ||Δρ_29||_QM on ≥ 3/5 seeds
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
    / "qng-gr-backreaction-fixedpoint-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]
ETA   = 0.05   # iteration step size
K_MAX = 30     # number of iterations


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


def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def div_J_phase(c, phi, adj):
    return [c[i] * sum(c[j] * math.sin(phi[j] - phi[i]) for j in adj[i])
            for i in range(len(c))]


def div_J_grad(c, f, adj):
    return [c[i] * sum(c[j] * (f[j] - f[i]) for j in adj[i])
            for i in range(len(c))]


def ols_fit(y, cols):
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
            return {"coeffs": [0.0] * m, "r2": 0.0}
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
    r2 = 1.0 - variance([y[k] - pred[k] for k in range(n)]) / var_y if var_y > 1e-30 else 0.0
    return {"coeffs": coeffs, "r2": r2}


# ---------------------------------------------------------------------------
# Rollout + coefficient estimation
# ---------------------------------------------------------------------------

def rollout_two_steps(cfg):
    import random as _rng
    rng = _rng.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)

    for _ in range(cfg.steps - 1):
        state, history = one_step(state, history, adj, cfg, use_history=True)

    c_t, _ = field_extract(state, history)
    phi_t      = state.phi[:]
    mismatch_t = history.mismatch[:]
    mem_t      = history.mem[:]

    state_tp1, hist_tp1 = one_step(state, history, adj, cfg, use_history=True)
    c_tp1, _ = field_extract(state_tp1, hist_tp1)

    return c_t, c_tp1, phi_t, mismatch_t, mem_t, adj


def estimate_coeffs(c_t, c_tp1, phi_t, mismatch_t, mem_t, adj):
    """Estimate α_phi, α_mis, α_mem (3-ch) and γ_tt (4-ch) from two-step data."""
    drho = [c_tp1[i] ** 2 - c_t[i] ** 2 for i in range(len(c_t))]

    dj_phi = div_J_phase(c_t, phi_t, adj)
    dj_mis = div_J_grad(c_t, mismatch_t, adj)
    dj_mem = div_J_grad(c_t, mem_t, adj)

    asm = assemble_linearized_metric(c_t, phi_t)
    e_tt = tensorial_proxy(asm)["e_tt"]

    fit3 = ols_fit(drho, [dj_phi, dj_mis, dj_mem])
    fit4 = ols_fit(drho, [dj_phi, dj_mis, dj_mem, e_tt])

    # Convention: drho ≈ α_phi·dJ_phi + α_mis·dJ_mis + α_mem·dJ_mem + γ_tt·e_tt
    a_phi, a_mis, a_mem = fit3["coeffs"]
    _, _, _, g_tt = fit4["coeffs"]

    return {"a_phi": a_phi, "a_mis": a_mis, "a_mem": a_mem, "g_tt": g_tt}


# ---------------------------------------------------------------------------
# Fixed-point iteration
# ---------------------------------------------------------------------------

def iterate(
    rho0: list[float],
    phi: list[float],
    mismatch: list[float],
    mem: list[float],
    adj: list[list[int]],
    a_mis: float,
    a_mem: float,
    g_tt: float,
    use_gr: bool,
    eta: float = ETA,
    k_max: int = K_MAX,
) -> dict:
    """Run fixed-point iteration, return convergence history."""
    rho = rho0[:]
    delta_norms = []

    for _ in range(k_max):
        c = [math.sqrt(clip01(r)) for r in rho]

        dj_mis = div_J_grad(c, mismatch, adj)
        dj_mem = div_J_grad(c, mem, adj)

        if use_gr:
            asm = assemble_linearized_metric(c, phi)
            e_tt = tensorial_proxy(asm)["e_tt"]
            update = [eta * (a_mis * dj_mis[i] + a_mem * dj_mem[i] + g_tt * e_tt[i])
                      for i in range(len(rho))]
        else:
            update = [eta * (a_mis * dj_mis[i] + a_mem * dj_mem[i])
                      for i in range(len(rho))]

        delta_norms.append(norm2(update))
        rho = [clip01(rho[i] + update[i]) for i in range(len(rho))]

    return {"rho_final": rho, "delta_norms": delta_norms}


# ---------------------------------------------------------------------------
# Per-seed
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)
    c_t, c_tp1, phi_t, mismatch_t, mem_t, adj = rollout_two_steps(cfg)

    coeffs = estimate_coeffs(c_t, c_tp1, phi_t, mismatch_t, mem_t, adj)
    a_mis = coeffs["a_mis"]
    a_mem = coeffs["a_mem"]
    g_tt  = coeffs["g_tt"]

    rho0 = [c ** 2 for c in c_t]

    res_qm   = iterate(rho0, phi_t, mismatch_t, mem_t, adj, a_mis, a_mem, 0.0,  use_gr=False)
    res_qmgr = iterate(rho0, phi_t, mismatch_t, mem_t, adj, a_mis, a_mem, g_tt, use_gr=True)

    dn_qm   = res_qm["delta_norms"]
    dn_qmgr = res_qmgr["delta_norms"]

    rho_star_qm   = res_qm["rho_final"]
    rho_star_qmgr = res_qmgr["rho_final"]

    fp_shift = norm2([rho_star_qmgr[i] - rho_star_qm[i] for i in range(len(rho0))])

    return {
        "seed": seed,
        "a_mis": a_mis, "a_mem": a_mem, "g_tt": g_tt,
        "qm_converges":   dn_qm[-1] < dn_qm[0],
        "qmgr_converges": dn_qmgr[-1] < dn_qmgr[0],
        "fp_shift": fp_shift,
        "fp_shift_significant": fp_shift > 0.001,
        "gr_faster": dn_qmgr[-1] < dn_qm[-1],
        "delta_0_qm":   dn_qm[0],
        "delta_29_qm":  dn_qm[-1],
        "delta_0_qmgr": dn_qmgr[0],
        "delta_29_qmgr": dn_qmgr[-1],
        "ratio_qm":   dn_qm[-1] / dn_qm[0]   if dn_qm[0] > 1e-15 else 1.0,
        "ratio_qmgr": dn_qmgr[-1] / dn_qmgr[0] if dn_qmgr[0] > 1e-15 else 1.0,
        "delta_norms_qm":   dn_qm,
        "delta_norms_qmgr": dn_qmgr,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    results = [run_seed(s) for s in SEEDS]

    n_p1 = sum(r["qm_converges"]         for r in results)
    n_p2 = sum(r["qmgr_converges"]       for r in results)
    n_p3 = sum(r["fp_shift_significant"] for r in results)
    n_p4 = sum(r["gr_faster"]            for r in results)

    p1_pass = n_p1 >= 4
    p2_pass = n_p2 >= 4
    p3_pass = n_p3 >= 3
    p4_pass = n_p4 >= 3

    n_pass = sum([p1_pass, p2_pass, p3_pass, p4_pass])
    decision = "pass" if n_pass >= 3 else ("partial" if n_pass >= 2 else "fail")

    print("=" * 72)
    print("QNG-CPU-055 — Back-Reaction Fixed-Point Iteration")
    print("=" * 72)
    print()
    print(f"{'Seed':>10}  {'a_mis':>8}  {'g_tt':>8}  "
          f"{'QM r0':>7}  {'QM r29':>7}  {'QM conv':>8}  "
          f"{'GR r29':>7}  {'FP shift':>9}  {'GR fast':>8}")
    print("-" * 80)
    for r in results:
        print(
            f"{r['seed']:>10}  {r['a_mis']:>+8.4f}  {r['g_tt']:>+8.5f}  "
            f"{r['delta_0_qm']:>7.4f}  {r['delta_29_qm']:>7.4f}  "
            f"{'YES' if r['qm_converges'] else 'NO':>8}  "
            f"{r['delta_29_qmgr']:>7.4f}  {r['fp_shift']:>9.5f}  "
            f"{'YES' if r['gr_faster'] else 'NO':>8}"
        )
    print()
    print(f"P1 (QM-only converges ≥ 4/5):      {'PASS' if p1_pass else 'FAIL'} ({n_p1}/5)")
    print(f"P2 (QM+GR converges ≥ 4/5):        {'PASS' if p2_pass else 'FAIL'} ({n_p2}/5)")
    print(f"P3 (FP shift > 0.001 on ≥ 3/5):    {'PASS' if p3_pass else 'FAIL'} ({n_p3}/5)")
    print(f"P4 (GR faster on ≥ 3/5):           {'PASS' if p4_pass else 'FAIL'} ({n_p4}/5)")
    print()
    print(f"Decision: {decision.upper()} ({n_pass}/4 predictions)")

    # Convergence summary
    mean_ratio_qm   = sum(r["ratio_qm"]   for r in results) / len(results)
    mean_ratio_qmgr = sum(r["ratio_qmgr"] for r in results) / len(results)
    mean_fp_shift   = sum(r["fp_shift"]   for r in results) / len(results)
    print(f"\nMean convergence ratio (Δ_29/Δ_0):")
    print(f"  QM-only: {mean_ratio_qm:.4f}")
    print(f"  QM+GR:   {mean_ratio_qmgr:.4f}")
    print(f"Mean FP shift: {mean_fp_shift:.5f}")

    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "test": "QNG-CPU-055",
        "theory": "DER-BRIDGE-037",
        "decision": decision,
        "n_pass": n_pass,
        "p1_pass": p1_pass, "p2_pass": p2_pass,
        "p3_pass": p3_pass, "p4_pass": p4_pass,
        "n_p1": n_p1, "n_p2": n_p2, "n_p3": n_p3, "n_p4": n_p4,
        "mean_ratio_qm": mean_ratio_qm,
        "mean_ratio_qmgr": mean_ratio_qmgr,
        "mean_fp_shift": mean_fp_shift,
        "eta": ETA, "k_max": K_MAX,
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
