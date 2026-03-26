"""QNG-CPU-058 — Back-Reaction Metric Signature Correction.

Tests whether the GR back-reaction correction ρ*(QM) → ρ*(QM+GR) shifts the
assembled metric components E_tt and E_xx in the direction of Lorentzian
signature (more negative h_tt, more positive h_xx).

Baseline from CPU-033: h_tt ≈ −0.009, h_xx ≈ +0.014, corr(h_tt,h_xx) ≈ −0.97.

Pass criteria (from prereg QNG-CPU-058):
    P1: sign(ΔE_tt) consistent across seeds (≥ 4/5 same sign)
    P2: sign(ΔE_xx) consistent across seeds (≥ 4/5 same sign)
    P3: sign(ΔE_tt) ≠ sign(ΔE_xx) on ≥ 4/5 seeds (Lorentzian correction)
    P4: |ΔE_tt| > 1e-5 on ≥ 4/5 seeds
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
    / "qng-gr-metric-signature-correction-reference-v1"
)

SEEDS  = [20260325, 42, 137, 1729, 2718]
ETA    = 0.05
K_MAX  = 30
P4_MIN_SHIFT = 1e-5


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def mean(v: list[float]) -> float:
    return sum(v) / len(v) if v else 0.0


def variance(a: list[float]) -> float:
    m = mean(a)
    return sum((x - m) ** 2 for x in a) / len(a) if a else 0.0


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


def norm2(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


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
    return {"coeffs": coeffs}


# ---------------------------------------------------------------------------
# Rollout and coefficient estimation
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
    asm    = assemble_linearized_metric(c_t, phi_t)
    e_tt   = tensorial_proxy(asm)["e_tt"]
    fit4   = ols_fit(drho, [dj_mis, dj_mem, e_tt])
    a_mis, a_mem, g_tt = fit4["coeffs"]
    return {"a_mis": a_mis, "a_mem": a_mem, "g_tt": g_tt}


# ---------------------------------------------------------------------------
# Metric diagnostics
# ---------------------------------------------------------------------------

def metric_diagnostics(c: list[float], phi: list[float]) -> dict:
    """Compute E_tt and E_xx nodewise and derive signature metrics."""
    asm   = assemble_linearized_metric(c, phi)
    ten   = tensorial_proxy(asm)
    e_tt  = ten["e_tt"]
    e_xx  = ten["e_xx"]
    return {
        "e_tt":           e_tt,
        "e_xx":           e_xx,
        "mean_e_tt":      mean(e_tt),
        "mean_e_xx":      mean(e_xx),
        "frac_htt_neg":   sum(1 for x in e_tt if x < 0) / len(e_tt),
        "frac_hxx_pos":   sum(1 for x in e_xx if x > 0) / len(e_xx),
        "corr_tt_xx":     pearson(e_tt, e_xx),
    }


# ---------------------------------------------------------------------------
# Fixed-point iterations
# ---------------------------------------------------------------------------

def iterate_qm_only(rho0, phi, mismatch, mem, adj, a_mis, a_mem):
    rho = rho0[:]
    for _ in range(K_MAX):
        c      = [math.sqrt(clip01(r)) for r in rho]
        dj_mis = div_J_grad(c, mismatch, adj)
        dj_mem = div_J_grad(c, mem, adj)
        update = [ETA * (a_mis * dj_mis[i] + a_mem * dj_mem[i]) for i in range(len(rho))]
        rho = [clip01(rho[i] + update[i]) for i in range(len(rho))]
    return rho


def iterate_gr(rho0, phi, mismatch, mem, adj, a_mis, a_mem, g_tt):
    """Self-consistent GR iteration (same as CPU-057)."""
    rho = rho0[:]
    for _ in range(K_MAX):
        c      = [math.sqrt(clip01(r)) for r in rho]
        dj_mis = div_J_grad(c, mismatch, adj)
        dj_mem = div_J_grad(c, mem, adj)
        asm    = assemble_linearized_metric(c, phi)
        e_tt_k = tensorial_proxy(asm)["e_tt"]
        update = [ETA * (a_mis * dj_mis[i] + a_mem * dj_mem[i] + g_tt * e_tt_k[i])
                  for i in range(len(rho))]
        rho = [clip01(rho[i] + update[i]) for i in range(len(rho))]
    return rho


# ---------------------------------------------------------------------------
# Per-seed
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)
    c_t, c_tp1, phi_t, mismatch_t, mem_t, adj = rollout_final(cfg)

    coeffs = estimate_coeffs(c_t, c_tp1, phi_t, mismatch_t, mem_t, adj)
    a_mis  = coeffs["a_mis"]
    a_mem  = coeffs["a_mem"]
    g_tt   = coeffs["g_tt"]

    rho0 = [c_t[i] ** 2 for i in range(len(c_t))]

    # Attractor densities
    rho_qm = iterate_qm_only(rho0, phi_t, mismatch_t, mem_t, adj, a_mis, a_mem)
    rho_gr = iterate_gr(rho0, phi_t, mismatch_t, mem_t, adj, a_mis, a_mem, g_tt)

    # Attractor amplitudes
    c_qm = [math.sqrt(clip01(r)) for r in rho_qm]
    c_gr = [math.sqrt(clip01(r)) for r in rho_gr]

    # Metric at rollout state (baseline)
    met_base = metric_diagnostics(c_t,  phi_t)
    # Metric at QM attractor
    met_qm   = metric_diagnostics(c_qm, phi_t)
    # Metric at GR attractor
    met_gr   = metric_diagnostics(c_gr, phi_t)

    # Corrections
    d_e_tt       = met_gr["mean_e_tt"]       - met_qm["mean_e_tt"]
    d_e_xx       = met_gr["mean_e_xx"]       - met_qm["mean_e_xx"]
    d_frac_neg   = met_gr["frac_htt_neg"]    - met_qm["frac_htt_neg"]
    d_frac_pos   = met_gr["frac_hxx_pos"]    - met_qm["frac_hxx_pos"]
    d_corr       = met_gr["corr_tt_xx"]      - met_qm["corr_tt_xx"]

    # Sign consistency checks (pre-registered)
    lorentzian_dir = (d_e_tt < 0 and d_e_xx > 0)  # more timelike + more spacelike

    return {
        "seed":             seed,
        "g_tt":             g_tt,
        # Baseline metric
        "base_mean_e_tt":   met_base["mean_e_tt"],
        "base_mean_e_xx":   met_base["mean_e_xx"],
        "base_corr":        met_base["corr_tt_xx"],
        # QM attractor metric
        "qm_mean_e_tt":     met_qm["mean_e_tt"],
        "qm_mean_e_xx":     met_qm["mean_e_xx"],
        "qm_corr":          met_qm["corr_tt_xx"],
        "qm_frac_neg":      met_qm["frac_htt_neg"],
        # GR attractor metric
        "gr_mean_e_tt":     met_gr["mean_e_tt"],
        "gr_mean_e_xx":     met_gr["mean_e_xx"],
        "gr_corr":          met_gr["corr_tt_xx"],
        "gr_frac_neg":      met_gr["frac_htt_neg"],
        # Corrections
        "d_e_tt":           d_e_tt,
        "d_e_xx":           d_e_xx,
        "d_frac_neg":       d_frac_neg,
        "d_frac_pos":       d_frac_pos,
        "d_corr":           d_corr,
        "lorentzian_dir":   lorentzian_dir,
        # P-criteria
        "p1_pass":          True,   # filled in aggregate (sign consistency)
        "p2_pass":          True,   # filled in aggregate
        "p3_pass":          (d_e_tt * d_e_xx < 0),       # opposite signs
        "p4_pass":          abs(d_e_tt) > P4_MIN_SHIFT,
    }


# ---------------------------------------------------------------------------
# Aggregate and report
# ---------------------------------------------------------------------------

def run_all(out_dir: Path = DEFAULT_OUT_DIR) -> dict:
    results = [run_seed(s) for s in SEEDS]

    # P1: sign(ΔE_tt) consistent (all same sign)
    signs_dett = [1 if r["d_e_tt"] >= 0 else -1 for r in results]
    n_pos_dett = sum(1 for s in signs_dett if s > 0)
    n_neg_dett = len(signs_dett) - n_pos_dett
    n_p1 = max(n_pos_dett, n_neg_dett)
    p1_pass = n_p1 >= 4

    # P2: sign(ΔE_xx) consistent
    signs_dexx = [1 if r["d_e_xx"] >= 0 else -1 for r in results]
    n_pos_dexx = sum(1 for s in signs_dexx if s > 0)
    n_neg_dexx = len(signs_dexx) - n_pos_dexx
    n_p2 = max(n_pos_dexx, n_neg_dexx)
    p2_pass = n_p2 >= 4

    # Update per-seed P1/P2 with aggregate answer
    dominant_sign_tt = 1 if n_pos_dett >= n_neg_dett else -1
    dominant_sign_xx = 1 if n_pos_dexx >= n_neg_dexx else -1
    for r in results:
        r["p1_pass"] = (1 if r["d_e_tt"] >= 0 else -1) == dominant_sign_tt
        r["p2_pass"] = (1 if r["d_e_xx"] >= 0 else -1) == dominant_sign_xx

    n_p3 = sum(r["p3_pass"] for r in results)
    n_p4 = sum(r["p4_pass"] for r in results)
    p3_pass = n_p3 >= 4
    p4_pass = n_p4 >= 4

    overall = sum([p1_pass, p2_pass, p3_pass, p4_pass])

    # Direction summary
    lorentzian_count = sum(r["lorentzian_dir"] for r in results)

    report = {
        "test_id":    "QNG-CPU-058",
        "theory_doc": "DER-BRIDGE-040",
        "seeds":      SEEDS,
        "per_seed":   results,
        "summary": {
            "n_p1": n_p1, "p1_pass": p1_pass,
            "n_p2": n_p2, "p2_pass": p2_pass,
            "n_p3": n_p3, "p3_pass": p3_pass,
            "n_p4": n_p4, "p4_pass": p4_pass,
            "overall": f"{overall}/4",
            "lorentzian_direction_seeds": lorentzian_count,
        },
        "key_values": {
            "mean_d_e_tt":      sum(r["d_e_tt"]       for r in results) / len(results),
            "mean_d_e_xx":      sum(r["d_e_xx"]       for r in results) / len(results),
            "mean_d_corr":      sum(r["d_corr"]       for r in results) / len(results),
            "mean_d_frac_neg":  sum(r["d_frac_neg"]   for r in results) / len(results),
            "mean_g_tt":        sum(r["g_tt"]          for r in results) / len(results),
            "baseline_e_tt":    sum(r["base_mean_e_tt"] for r in results) / len(results),
            "baseline_e_xx":    sum(r["base_mean_e_xx"] for r in results) / len(results),
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n=== QNG-CPU-058 Metric Signature Correction ===")
    print(f"{'Seed':>10}  {'γ_tt':>8}  {'ΔE_tt':>9}  {'ΔE_xx':>9}  {'Δcorr':>8}  {'Δfrac_neg':>10}  P1  P2  P3  P4  Lor")
    print("-" * 96)
    for r in results:
        print(f"{r['seed']:>10}  {r['g_tt']:>8.5f}  {r['d_e_tt']:>9.6f}  {r['d_e_xx']:>9.6f}  "
              f"{r['d_corr']:>8.5f}  {r['d_frac_neg']:>10.4f}  "
              f"{'✓' if r['p1_pass'] else '✗'}   "
              f"{'✓' if r['p2_pass'] else '✗'}   "
              f"{'✓' if r['p3_pass'] else '✗'}   "
              f"{'✓' if r['p4_pass'] else '✗'}  "
              f"{'✓' if r['lorentzian_dir'] else '✗'}")
    print("-" * 96)
    print(f"P1 {'PASS' if p1_pass else 'FAIL'} ({n_p1}/5)  "
          f"P2 {'PASS' if p2_pass else 'FAIL'} ({n_p2}/5)  "
          f"P3 {'PASS' if p3_pass else 'FAIL'} ({n_p3}/5)  "
          f"P4 {'PASS' if p4_pass else 'FAIL'} ({n_p4}/5)")
    print(f"Lorentzian direction (ΔE_tt<0 AND ΔE_xx>0): {lorentzian_count}/5")
    print(f"OVERALL: {overall}/4")
    kv = report["key_values"]
    print(f"\nBaseline: E_tt={kv['baseline_e_tt']:.6f}, E_xx={kv['baseline_e_xx']:.6f}")
    print(f"Mean corrections: ΔE_tt={kv['mean_d_e_tt']:.6f}, ΔE_xx={kv['mean_d_e_xx']:.6f}")
    print(f"Mean Δcorr(E_tt,E_xx) = {kv['mean_d_corr']:.6f}")
    print(f"Mean Δfrac_htt_neg    = {kv['mean_d_frac_neg']:.4f}")

    return report


if __name__ == "__main__":
    import sys
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT_DIR
    run_all(out_dir)
