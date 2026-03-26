"""QNG-CPU-056 — Attractor Geometry: Degree-Density Law and GR Correction Profile.

Characterizes the spatial structure of the QNG back-reaction attractor.

Two questions:
    1. Does ρ*(QM) correlate with node degree? (topological structure)
    2. Does δρ = ρ*(GR)−ρ*(QM) correlate with E_tt? (gravitational imprint)

Pass criteria (from prereg QNG-CPU-056):
    P1: Pearson(ρ*(QM), k) > 0.2 on ≥ 4/5 seeds
    P2: |Pearson(δρ, E_tt)| > 0.05 on ≥ 4/5 seeds
    P3: sign(Pearson(δρ, E_tt)) = sign(γ_tt) on ≥ 4/5 seeds
    P4: std(δρ) / mean(|δρ|) > 0.1 on ≥ 4/5 seeds
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
    / "qng-gr-attractor-geometry-reference-v1"
)

SEEDS  = [20260325, 42, 137, 1729, 2718]
ETA    = 0.05
K_MAX  = 30

# Pass thresholds
P1_PEARSON_RHO_DEGREE = 0.2
P2_ABS_PEARSON_DRH_ETT = 0.05
P4_STD_RATIO = 0.1


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def norm2(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def mean(v: list[float]) -> float:
    return sum(v) / len(v) if v else 0.0


def std(v: list[float]) -> float:
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / len(v)) if len(v) > 1 else 0.0


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


def div_J_grad(c, f, adj):
    return [c[i] * sum(c[j] * (f[j] - f[i]) for j in adj[i])
            for i in range(len(c))]


def variance(a: list[float]) -> float:
    m = mean(a)
    return sum((x - m) ** 2 for x in a) / len(a) if a else 0.0


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
# Rollout helpers
# ---------------------------------------------------------------------------

def rollout_final(cfg: Config):
    """Run full rollout, return final state + adj."""
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

    # One more step for coefficient estimation
    state_tp1, hist_tp1 = one_step(state, history, adj, cfg, use_history=True)
    c_tp1, _ = field_extract(state_tp1, hist_tp1)

    return c_t, c_tp1, phi_t, mismatch_t, mem_t, adj


def estimate_coeffs(c_t, c_tp1, phi_t, mismatch_t, mem_t, adj):
    drho   = [c_tp1[i] ** 2 - c_t[i] ** 2 for i in range(len(c_t))]
    dj_mis = div_J_grad(c_t, mismatch_t, adj)
    dj_mem = div_J_grad(c_t, mem_t, adj)
    asm    = assemble_linearized_metric(c_t, phi_t)
    e_tt   = tensorial_proxy(asm)["e_tt"]

    fit3 = ols_fit(drho, [dj_mis, dj_mem])
    fit4 = ols_fit(drho, [dj_mis, dj_mem, e_tt])
    a_mis, a_mem     = fit3["coeffs"]
    a_mis4, a_mem4, g_tt = fit4["coeffs"]

    return {"a_mis": a_mis, "a_mem": a_mem, "g_tt": g_tt, "e_tt": e_tt}


# ---------------------------------------------------------------------------
# Fixed-point iteration
# ---------------------------------------------------------------------------

def iterate(rho0, phi, mismatch, mem, adj, a_mis, a_mem, g_tt, use_gr):
    rho = rho0[:]
    for _ in range(K_MAX):
        c      = [math.sqrt(clip01(r)) for r in rho]
        dj_mis = div_J_grad(c, mismatch, adj)
        dj_mem = div_J_grad(c, mem, adj)
        if use_gr:
            asm   = assemble_linearized_metric(c, phi)
            e_tt  = tensorial_proxy(asm)["e_tt"]
            update = [ETA * (a_mis * dj_mis[i] + a_mem * dj_mem[i] + g_tt * e_tt[i])
                      for i in range(len(rho))]
        else:
            update = [ETA * (a_mis * dj_mis[i] + a_mem * dj_mem[i])
                      for i in range(len(rho))]
        rho = [clip01(rho[i] + update[i]) for i in range(len(rho))]
    return rho


# ---------------------------------------------------------------------------
# Per-seed metrics
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)
    c_t, c_tp1, phi_t, mismatch_t, mem_t, adj = rollout_final(cfg)

    coeffs = estimate_coeffs(c_t, c_tp1, phi_t, mismatch_t, mem_t, adj)
    a_mis  = coeffs["a_mis"]
    a_mem  = coeffs["a_mem"]
    g_tt   = coeffs["g_tt"]
    e_tt   = coeffs["e_tt"]

    # Initial ρ from rollout state
    rho0 = [c_t[i] ** 2 for i in range(len(c_t))]

    # Fixed-point attractors
    rho_qm = iterate(rho0, phi_t, mismatch_t, mem_t, adj, a_mis, a_mem, g_tt, use_gr=False)
    rho_gr = iterate(rho0, phi_t, mismatch_t, mem_t, adj, a_mis, a_mem, g_tt, use_gr=True)

    # GR correction
    drho = [rho_gr[i] - rho_qm[i] for i in range(len(rho_qm))]

    # Node degrees
    degrees = [float(len(adj[i])) for i in range(len(adj))]

    # Correlations
    corr_rho_degree = pearson(rho_qm, degrees)
    corr_drho_ett   = pearson(drho, e_tt)

    # Spatial structure of δρ
    abs_drho = [abs(x) for x in drho]
    mean_abs = mean(abs_drho)
    std_drho = std(drho)
    ratio    = std_drho / mean_abs if mean_abs > 1e-15 else 0.0

    fp_shift = norm2(drho)

    return {
        "seed":              seed,
        "g_tt":              g_tt,
        "corr_rho_degree":   corr_rho_degree,
        "corr_drho_ett":     corr_drho_ett,
        "std_drho":          std_drho,
        "mean_abs_drho":     mean_abs,
        "std_ratio":         ratio,
        "fp_shift":          fp_shift,
        "mean_rho_qm":       mean(rho_qm),
        "mean_rho_gr":       mean(rho_gr),
        "p1_pass":           corr_rho_degree > P1_PEARSON_RHO_DEGREE,
        "p2_pass":           abs(corr_drho_ett) > P2_ABS_PEARSON_DRH_ETT,
        "p3_pass":           (corr_drho_ett > 0) == (g_tt > 0),
        "p4_pass":           ratio > P4_STD_RATIO,
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
    p3_pass = n_p3 >= 4
    p4_pass = n_p4 >= 4

    overall = sum([p1_pass, p2_pass, p3_pass, p4_pass])

    report = {
        "test_id":     "QNG-CPU-056",
        "theory_doc":  "DER-BRIDGE-038",
        "seeds":       SEEDS,
        "per_seed":    results,
        "summary": {
            "n_p1":    n_p1,  "p1_pass": p1_pass,
            "n_p2":    n_p2,  "p2_pass": p2_pass,
            "n_p3":    n_p3,  "p3_pass": p3_pass,
            "n_p4":    n_p4,  "p4_pass": p4_pass,
            "overall": f"{overall}/4",
        },
        "key_values": {
            "mean_corr_rho_degree": sum(r["corr_rho_degree"] for r in results) / len(results),
            "mean_corr_drho_ett":   sum(r["corr_drho_ett"]   for r in results) / len(results),
            "mean_std_ratio":       sum(r["std_ratio"]        for r in results) / len(results),
            "mean_fp_shift":        sum(r["fp_shift"]         for r in results) / len(results),
            "mean_g_tt":            sum(r["g_tt"]             for r in results) / len(results),
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n=== QNG-CPU-056 Attractor Geometry ===")
    print(f"{'Seed':>10}  {'γ_tt':>8}  {'r(ρ*,k)':>9}  {'r(δρ,E_tt)':>11}  {'std_ratio':>10}  {'fp_shift':>9}  P1  P2  P3  P4")
    print("-" * 90)
    for r in results:
        print(f"{r['seed']:>10}  {r['g_tt']:>8.5f}  {r['corr_rho_degree']:>9.4f}  "
              f"{r['corr_drho_ett']:>11.4f}  {r['std_ratio']:>10.4f}  "
              f"{r['fp_shift']:>9.6f}  "
              f"{'✓' if r['p1_pass'] else '✗'}   "
              f"{'✓' if r['p2_pass'] else '✗'}   "
              f"{'✓' if r['p3_pass'] else '✗'}   "
              f"{'✓' if r['p4_pass'] else '✗'}")
    print("-" * 90)
    print(f"P1 {'PASS' if p1_pass else 'FAIL'} ({n_p1}/5)  "
          f"P2 {'PASS' if p2_pass else 'FAIL'} ({n_p2}/5)  "
          f"P3 {'PASS' if p3_pass else 'FAIL'} ({n_p3}/5)  "
          f"P4 {'PASS' if p4_pass else 'FAIL'} ({n_p4}/5)")
    print(f"OVERALL: {overall}/4")
    print(f"\nKey values:")
    kv = report["key_values"]
    print(f"  mean Pearson(ρ*, degree) = {kv['mean_corr_rho_degree']:.4f}")
    print(f"  mean Pearson(δρ, E_tt)  = {kv['mean_corr_drho_ett']:.4f}")
    print(f"  mean std(δρ)/mean|δρ|   = {kv['mean_std_ratio']:.4f}")
    print(f"  mean FP shift norm      = {kv['mean_fp_shift']:.6f}")
    print(f"  mean γ_tt               = {kv['mean_g_tt']:.5f}")

    return report


if __name__ == "__main__":
    import sys
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT_DIR
    run_all(out_dir)
