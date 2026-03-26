"""QNG-CPU-057 — Self-Consistent Back-Reaction: Nonlinear Fixed-Point.

Tests whether the CPU-056 result (δρ ∝ E_tt) holds when E_tt is re-evaluated
at each iteration step rather than held fixed (linearized approximation).

Two GR iterations compared:
    Linear:           E_tt fixed at rollout state; ρ_{k+1} = ρ_k + η·(a_mis·dJ_mis + a_mem·dJ_mem + γ_tt·E_tt_0)
    Self-consistent:  E_tt(ρ_k) re-evaluated each step

Pass criteria (from prereg QNG-CPU-057):
    P1: self-consistent δ_norms decreasing on ≥ 4/5 seeds
    P2: ||ρ*_sc − ρ*_lin||₂ < 0.005 on ≥ 4/5 seeds
    P3: |Pearson(δρ_sc, E_tt_final)| > 0.5 on ≥ 4/5 seeds
    P4: E_tt_drift > 0.001 on ≥ 3/5 seeds
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
    / "qng-gr-selfconsistent-backreaction-reference-v1"
)

SEEDS  = [20260325, 42, 137, 1729, 2718]
ETA    = 0.05
K_MAX  = 30

# Pass thresholds
P2_ATTRACTOR_CLOSE = 0.005
P3_MIN_PEARSON     = 0.5
P4_ETT_DRIFT       = 0.001


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def norm2(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


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


def variance(a: list[float]) -> float:
    m = mean(a)
    return sum((x - m) ** 2 for x in a) / len(a) if a else 0.0


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


def get_e_tt(c, phi):
    asm = assemble_linearized_metric(c, phi)
    return tensorial_proxy(asm)["e_tt"]


# ---------------------------------------------------------------------------
# Rollout
# ---------------------------------------------------------------------------

def rollout_final(cfg: Config):
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
    drho   = [c_tp1[i] ** 2 - c_t[i] ** 2 for i in range(len(c_t))]
    dj_mis = div_J_grad(c_t, mismatch_t, adj)
    dj_mem = div_J_grad(c_t, mem_t, adj)
    e_tt   = get_e_tt(c_t, phi_t)
    fit4   = ols_fit(drho, [dj_mis, dj_mem, e_tt])
    a_mis, a_mem, g_tt = fit4["coeffs"]
    return {"a_mis": a_mis, "a_mem": a_mem, "g_tt": g_tt, "e_tt_0": e_tt}


# ---------------------------------------------------------------------------
# Three iteration variants
# ---------------------------------------------------------------------------

def iterate_qm_only(rho0, phi, mismatch, mem, adj, a_mis, a_mem):
    """QM-only fixed-point iteration (no GR)."""
    rho = rho0[:]
    delta_norms = []
    for _ in range(K_MAX):
        c      = [math.sqrt(clip01(r)) for r in rho]
        dj_mis = div_J_grad(c, mismatch, adj)
        dj_mem = div_J_grad(c, mem, adj)
        update = [ETA * (a_mis * dj_mis[i] + a_mem * dj_mem[i]) for i in range(len(rho))]
        delta_norms.append(norm2(update))
        rho = [clip01(rho[i] + update[i]) for i in range(len(rho))]
    return rho, delta_norms


def iterate_linear_gr(rho0, phi, mismatch, mem, adj, a_mis, a_mem, g_tt, e_tt_fixed):
    """Linear GR iteration: E_tt held fixed at initial value."""
    rho = rho0[:]
    delta_norms = []
    for _ in range(K_MAX):
        c      = [math.sqrt(clip01(r)) for r in rho]
        dj_mis = div_J_grad(c, mismatch, adj)
        dj_mem = div_J_grad(c, mem, adj)
        update = [ETA * (a_mis * dj_mis[i] + a_mem * dj_mem[i] + g_tt * e_tt_fixed[i])
                  for i in range(len(rho))]
        delta_norms.append(norm2(update))
        rho = [clip01(rho[i] + update[i]) for i in range(len(rho))]
    return rho, delta_norms


def iterate_selfconsistent_gr(rho0, phi, mismatch, mem, adj, a_mis, a_mem, g_tt):
    """Self-consistent GR iteration: E_tt re-computed from current ρ each step."""
    rho = rho0[:]
    delta_norms = []
    e_tt_history = []
    for k in range(K_MAX):
        c      = [math.sqrt(clip01(r)) for r in rho]
        dj_mis = div_J_grad(c, mismatch, adj)
        dj_mem = div_J_grad(c, mem, adj)
        e_tt_k = get_e_tt(c, phi)              # <-- re-evaluated each step
        if k == 0 or k == K_MAX - 1:
            e_tt_history.append(e_tt_k[:])
        update = [ETA * (a_mis * dj_mis[i] + a_mem * dj_mem[i] + g_tt * e_tt_k[i])
                  for i in range(len(rho))]
        delta_norms.append(norm2(update))
        rho = [clip01(rho[i] + update[i]) for i in range(len(rho))]
    e_tt_final = e_tt_history[-1]
    e_tt_init  = e_tt_history[0]
    return rho, delta_norms, e_tt_init, e_tt_final


# ---------------------------------------------------------------------------
# Per-seed
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)
    c_t, c_tp1, phi_t, mismatch_t, mem_t, adj = rollout_final(cfg)

    coeffs  = estimate_coeffs(c_t, c_tp1, phi_t, mismatch_t, mem_t, adj)
    a_mis   = coeffs["a_mis"]
    a_mem   = coeffs["a_mem"]
    g_tt    = coeffs["g_tt"]
    e_tt_0  = coeffs["e_tt_0"]

    rho0 = [c_t[i] ** 2 for i in range(len(c_t))]

    # Three runs
    rho_qm,  dn_qm  = iterate_qm_only(rho0, phi_t, mismatch_t, mem_t, adj, a_mis, a_mem)
    rho_lin, dn_lin = iterate_linear_gr(rho0, phi_t, mismatch_t, mem_t, adj,
                                         a_mis, a_mem, g_tt, e_tt_0)
    rho_sc, dn_sc, e_tt_sc_init, e_tt_sc_final = iterate_selfconsistent_gr(
        rho0, phi_t, mismatch_t, mem_t, adj, a_mis, a_mem, g_tt)

    # Metrics
    sc_converges    = dn_sc[-1] < dn_sc[0]   # δ_norms decreasing

    drho_lin = [rho_lin[i] - rho_qm[i] for i in range(len(rho_qm))]
    drho_sc  = [rho_sc[i]  - rho_qm[i] for i in range(len(rho_qm))]

    attractor_dist  = norm2([rho_sc[i] - rho_lin[i] for i in range(len(rho_sc))])
    corr_sc         = pearson(drho_sc, e_tt_sc_final)

    norm_ett0       = norm2(e_tt_sc_init)
    ett_change      = norm2([e_tt_sc_final[i] - e_tt_sc_init[i] for i in range(len(e_tt_sc_init))])
    e_tt_drift      = ett_change / norm_ett0 if norm_ett0 > 1e-15 else 0.0

    # For context: linear correlation still
    corr_lin = pearson(drho_lin, e_tt_0)

    return {
        "seed":             seed,
        "g_tt":             g_tt,
        "sc_converges":     sc_converges,
        "attractor_dist":   attractor_dist,
        "corr_sc":          corr_sc,
        "corr_lin":         corr_lin,
        "e_tt_drift":       e_tt_drift,
        "dn_sc_0":          dn_sc[0],
        "dn_sc_final":      dn_sc[-1],
        "p1_pass":          sc_converges,
        "p2_pass":          attractor_dist < P2_ATTRACTOR_CLOSE,
        "p3_pass":          abs(corr_sc) > P3_MIN_PEARSON,
        "p4_pass":          e_tt_drift > P4_ETT_DRIFT,
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
    p4_pass = n_p4 >= 3

    overall = sum([p1_pass, p2_pass, p3_pass, p4_pass])

    report = {
        "test_id":    "QNG-CPU-057",
        "theory_doc": "DER-BRIDGE-039",
        "seeds":      SEEDS,
        "per_seed":   results,
        "summary": {
            "n_p1": n_p1, "p1_pass": p1_pass,
            "n_p2": n_p2, "p2_pass": p2_pass,
            "n_p3": n_p3, "p3_pass": p3_pass,
            "n_p4": n_p4, "p4_pass": p4_pass,
            "overall": f"{overall}/4",
        },
        "key_values": {
            "mean_attractor_dist":  sum(r["attractor_dist"] for r in results) / len(results),
            "mean_corr_sc":         sum(r["corr_sc"]        for r in results) / len(results),
            "mean_corr_lin":        sum(r["corr_lin"]       for r in results) / len(results),
            "mean_e_tt_drift":      sum(r["e_tt_drift"]     for r in results) / len(results),
            "mean_g_tt":            sum(r["g_tt"]           for r in results) / len(results),
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n=== QNG-CPU-057 Self-Consistent Back-Reaction ===")
    print(f"{'Seed':>10}  {'γ_tt':>8}  {'att_dist':>9}  {'r_sc':>7}  {'r_lin':>7}  {'E_tt_drift':>11}  P1  P2  P3  P4")
    print("-" * 88)
    for r in results:
        print(f"{r['seed']:>10}  {r['g_tt']:>8.5f}  {r['attractor_dist']:>9.6f}  "
              f"{r['corr_sc']:>7.4f}  {r['corr_lin']:>7.4f}  "
              f"{r['e_tt_drift']:>11.6f}  "
              f"{'✓' if r['p1_pass'] else '✗'}   "
              f"{'✓' if r['p2_pass'] else '✗'}   "
              f"{'✓' if r['p3_pass'] else '✗'}   "
              f"{'✓' if r['p4_pass'] else '✗'}")
    print("-" * 88)
    print(f"P1 {'PASS' if p1_pass else 'FAIL'} ({n_p1}/5)  "
          f"P2 {'PASS' if p2_pass else 'FAIL'} ({n_p2}/5)  "
          f"P3 {'PASS' if p3_pass else 'FAIL'} ({n_p3}/5)  "
          f"P4 {'PASS' if p4_pass else 'FAIL'} ({n_p4}/5, need ≥3)")
    print(f"OVERALL: {overall}/4")
    print(f"\nKey values:")
    kv = report["key_values"]
    print(f"  mean attractor dist (sc vs lin)  = {kv['mean_attractor_dist']:.6f}")
    print(f"  mean Pearson(δρ_sc,  E_tt_final) = {kv['mean_corr_sc']:.4f}")
    print(f"  mean Pearson(δρ_lin, E_tt_0)     = {kv['mean_corr_lin']:.4f}")
    print(f"  mean E_tt relative drift         = {kv['mean_e_tt_drift']:.6f}")

    return report


if __name__ == "__main__":
    import sys
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT_DIR
    run_all(out_dir)
