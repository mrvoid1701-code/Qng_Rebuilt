"""QNG-CPU-054 — GR→QM Back-Reaction Coupling Large-N Probe.

Tests whether the GR→QM coupling γ_tt from CPU-053 follows the same
sparse-graph N-attenuation law as e_mis (CPU-051/052).

N_VALUES = [8, 16, 32] × 5 seeds = 15 runs.
Also computes loop_strength(N) = mean|γ_tt| × mean|e_mis| to assess
whether the back-reaction loop closes in the continuum.

Pass criteria (from prereg QNG-CPU-054):
    P1: R²(3ch+E_tt) > R²(3ch) at N=32 on ≥ 4/5 seeds
    P2: mean γ_tt(N=32) < mean γ_tt(N=8) on ≥ 3/5 seeds
    P3: sign(γ_tt) consistent across N ∈ {8,16,32} on ≥ 4/5 seeds
    P4: mean γ_tt(N=32) > 0.001  (non-vanishing)

Reference (CPU-053, N=16): mean γ_tt ≈ +0.005, R²_3ch=0.405, R²_5ch=0.461

e_mis reference (CPU-051):
    N=8:  mean|e_mis|=1.037
    N=16: mean|e_mis|=0.259
    N=32: mean|e_mis|=0.159
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
    ROOT / "07_validation" / "audits" / "qng-gr-backreaction-large-n-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]
N_VALUES = [8, 16, 32]

# e_mis reference values from CPU-051 (for loop_strength calculation)
E_MIS_REF = {8: 1.037, 16: 0.259, 32: 0.159}


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def variance(a: list[float]) -> float:
    n = len(a)
    if n == 0:
        return 0.0
    m = sum(a) / n
    return sum((x - m) ** 2 for x in a) / n


def div_J_phase(c: list[float], phi: list[float], adj: list[list[int]]) -> list[float]:
    return [c[i] * sum(c[j] * math.sin(phi[j] - phi[i]) for j in adj[i])
            for i in range(len(c))]


def div_J_grad(c: list[float], f: list[float], adj: list[list[int]]) -> list[float]:
    return [c[i] * sum(c[j] * (f[j] - f[i]) for j in adj[i])
            for i in range(len(c))]


def ols_fit(y: list[float], cols: list[list[float]]) -> dict:
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
# Two-step rollout
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
# Per-(seed, N) metrics
# ---------------------------------------------------------------------------

def run_one(seed: int, n_nodes: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed, n_nodes=n_nodes)
    c_t, c_tp1, phi_t, mismatch_t, mem_t, adj = rollout_two_steps(cfg)

    drho = [c_tp1[i] ** 2 - c_t[i] ** 2 for i in range(len(c_t))]

    dj_phi = div_J_phase(c_t, phi_t, adj)
    dj_mis = div_J_grad(c_t, mismatch_t, adj)
    dj_mem = div_J_grad(c_t, mem_t, adj)

    asm = assemble_linearized_metric(c_t, phi_t)
    ten = tensorial_proxy(asm)
    e_tt = ten["e_tt"]

    fit3 = ols_fit(drho, [dj_phi, dj_mis, dj_mem])
    fit4 = ols_fit(drho, [dj_phi, dj_mis, dj_mem, e_tt])

    gamma_tt = fit4["coeffs"][3]

    return {
        "seed": seed,
        "n_nodes": n_nodes,
        "r2_3ch": fit3["r2"],
        "r2_4ch": fit4["r2"],
        "delta_r2": fit4["r2"] - fit3["r2"],
        "gamma_tt": gamma_tt,
        "gamma_tt_abs": abs(gamma_tt),
        "sign_gamma_tt": 1 if gamma_tt > 0 else -1,
        "ett_improves": fit4["r2"] > fit3["r2"],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    all_results: dict[int, list[dict]] = {n: [] for n in N_VALUES}
    for n in N_VALUES:
        for s in SEEDS:
            all_results[n].append(run_one(s, n))

    # Per-N summary
    n_summary: dict[int, dict] = {}
    for n in N_VALUES:
        rs = all_results[n]
        mean_gamma = sum(r["gamma_tt"] for r in rs) / len(rs)
        mean_gamma_abs = sum(r["gamma_tt_abs"] for r in rs) / len(rs)
        n_summary[n] = {
            "n_improves": sum(r["ett_improves"] for r in rs),
            "mean_r2_3ch": sum(r["r2_3ch"] for r in rs) / len(rs),
            "mean_r2_4ch": sum(r["r2_4ch"] for r in rs) / len(rs),
            "mean_delta_r2": sum(r["delta_r2"] for r in rs) / len(rs),
            "mean_gamma": mean_gamma,
            "mean_gamma_abs": mean_gamma_abs,
            "loop_strength": mean_gamma_abs * E_MIS_REF[n],
        }

    # Evaluate predictions
    p1_pass = n_summary[32]["n_improves"] >= 4

    n_p2 = sum(
        1 for r8, r32 in zip(all_results[8], all_results[32])
        if r32["gamma_tt_abs"] < r8["gamma_tt_abs"]
    )
    p2_pass = n_p2 >= 3

    n_p3 = 0
    for i in range(len(SEEDS)):
        signs = [all_results[n][i]["sign_gamma_tt"] for n in N_VALUES]
        majority = 1 if sum(signs) > 0 else -1
        if all(s == majority for s in signs):
            n_p3 += 1
    p3_pass = n_p3 >= 4

    p4_pass = n_summary[32]["mean_gamma_abs"] > 0.001

    n_pass = sum([p1_pass, p2_pass, p3_pass, p4_pass])
    decision = "pass" if n_pass >= 3 else ("partial" if n_pass >= 2 else "fail")

    if p1_pass and p3_pass:
        tier = "Tier-1-large-N"
    elif p1_pass:
        tier = "Tier-1.5"
    else:
        tier = "Tier-2"

    # Print
    print("=" * 72)
    print("QNG-CPU-054 — GR→QM Back-Reaction Coupling Large-N Probe")
    print("=" * 72)
    print()
    for n in N_VALUES:
        s = n_summary[n]
        print(f"N={n}:")
        print(f"  {'Seed':>10}  {'R²_3ch':>8}  {'R²_4ch':>8}  {'Δ':>8}  {'γ_tt':>10}  {'sign':>5}")
        print(f"  {'-'*56}")
        for r in all_results[n]:
            print(f"  {r['seed']:>10}  {r['r2_3ch']:>8.4f}  {r['r2_4ch']:>8.4f}  "
                  f"{r['delta_r2']:>+8.4f}  {r['gamma_tt']:>+10.5f}  {r['sign_gamma_tt']:>+5d}")
        print(f"  mean: R²_3ch={s['mean_r2_3ch']:.4f}  R²_4ch={s['mean_r2_4ch']:.4f}  "
              f"Δ={s['mean_delta_r2']:>+.4f}  γ_tt={s['mean_gamma']:>+.5f}  "
              f"loop={s['loop_strength']:.5f}")
        print()

    print(f"Loop strength (mean|γ_tt| × mean|e_mis|):")
    for n in N_VALUES:
        s = n_summary[n]
        print(f"  N={n:>2}: γ_tt={s['mean_gamma_abs']:.5f}  × e_mis={E_MIS_REF[n]:.3f}  = loop={s['loop_strength']:.5f}")
    print()
    print(f"P1 (N=32 improves ≥ 4/5):           {'PASS' if p1_pass else 'FAIL'} ({n_summary[32]['n_improves']}/5)")
    print(f"P2 (γ_tt(32) < γ_tt(8) on ≥ 3/5):   {'PASS' if p2_pass else 'FAIL'} ({n_p2}/5)")
    print(f"P3 (sign consistent N on ≥ 4/5):     {'PASS' if p3_pass else 'FAIL'} ({n_p3}/5)")
    print(f"P4 (mean γ_tt(32) > 0.001):          {'PASS' if p4_pass else 'FAIL'} ({n_summary[32]['mean_gamma_abs']:.5f})")
    print()
    print(f"Decision: {decision.upper()} ({n_pass}/4 predictions)")
    print(f"Tier: {tier}")

    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "test": "QNG-CPU-054",
        "theory": "DER-BRIDGE-036",
        "decision": decision,
        "tier": tier,
        "n_pass": n_pass,
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "p3_pass": p3_pass,
        "p4_pass": p4_pass,
        "p2_count": n_p2,
        "p3_count": n_p3,
        "n_scaling": {str(n): n_summary[n] for n in N_VALUES},
        "all_results": {str(n): all_results[n] for n in N_VALUES},
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
