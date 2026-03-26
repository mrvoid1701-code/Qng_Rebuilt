"""QNG-CPU-051 — GR 6-Channel Coupling Large-N Probe.

Tests whether the QM→GR 6-channel coupling (e_mis, f_mem) established at N=16
(CPU-050) persists or weakens at larger N — i.e., whether the sparse-graph law
from CPU-047 extends to the GR sector.

Runs 4-channel and 6-channel GR tensor fits across N ∈ {8, 16, 32} × 5 seeds.

Pass criteria (from prereg QNG-CPU-051):
    P1: 6-ch beats 4-ch at N=32 on ≥ 4/5 seeds
    P2: |e_mis(N=32)| < |e_mis(N=8)| on ≥ 3/5 seeds  (coupling weakens with N)
    P3: sign(e_mis_ett) consistent across all 3 N values on ≥ 4/5 seeds
    P4: |mean Δratio(N=32)| < |mean Δratio(N=8)|  (mean improvement shrinks with N)

Reference (CPU-050, N=16): mean Δratio_split = −0.0433, mean e_mis = −0.175
"""

from __future__ import annotations

import dataclasses
import json
import math
from pathlib import Path

from qng_backreaction_closure_reference import backreaction_proxy
from qng_bridge_closure_v2_reference import source_amp_from_rollout
from qng_effective_field_reference import field_extract, mean
from qng_geometry_estimator_reference import geometry_proxy
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_gr_tensorial_assembly_reference import tensorial_proxy
from qng_matter_sector_proxy_reference import matter_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = (
    ROOT / "07_validation" / "audits" / "qng-gr-coupling-large-n-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]
N_VALUES = [8, 16, 32]

# Reference from CPU-050 (N=16)
MEAN_DELTA_N16 = -0.0433
MEAN_E_MIS_N16 = -0.175


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def norm2(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def div_J_grad(
    c: list[float], f: list[float], adj: list[list[int]]
) -> list[float]:
    """Standard gradient divergence current: C_eff_i · Σ_j C_eff_j · (f_j - f_i)."""
    return [
        c[i] * sum(c[j] * (f[j] - f[i]) for j in adj[i])
        for i in range(len(c))
    ]


def ols_fit(y: list[float], cols: list[list[float]]) -> dict:
    """Solve OLS: minimize ‖y - X·β‖² with X = cols.

    Returns coefficients and residual ratio ‖y - X·β‖₂ / ‖y‖₂.
    """
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
            return {"coeffs": [0.0] * m, "ratio": 1.0, "singular": True}
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
    raw = norm2(y)
    residual = norm2([y[k] - pred[k] for k in range(n)])
    ratio = residual / raw if raw > 1e-15 else 0.0
    return {"coeffs": coeffs, "ratio": ratio, "singular": False}


# ---------------------------------------------------------------------------
# Per-(seed, N) fitting
# ---------------------------------------------------------------------------

def run_one(seed: int, n_nodes: int) -> dict:
    """Run 4-channel and 6-channel GR fits for a given (seed, n_nodes)."""
    cfg = dataclasses.replace(Config(), seed=seed, n_nodes=n_nodes)

    _, hist_state, hist_history, adj = run_rollout(cfg, use_history=True)

    c_hist, l_hist = field_extract(hist_state, hist_history)
    phi_hist = hist_state.phi
    mismatch_hist = hist_history.mismatch
    mem_hist = hist_history.mem

    asm_hist = assemble_linearized_metric(c_hist, phi_hist)
    ten_hist = tensorial_proxy(asm_hist)
    geo_hist = geometry_proxy(c_hist)
    psi_geo = [0.5 * x - 0.5 for x in geo_hist["g00"]]
    br_hist = backreaction_proxy(c_hist, phi_hist, psi_geo)
    src_hist = source_amp_from_rollout(cfg, use_history=True)
    m_hist = matter_proxy(c_hist, l_hist, phi_hist)["m_eff"]
    kappa = geo_hist["kappa"]

    dj_mis = div_J_grad(c_hist, mismatch_hist, adj)
    dj_mem = div_J_grad(c_hist, mem_hist, adj)

    names6 = ["kappa", "q_src", "src", "m_eff", "div_J_mis", "div_J_mem"]

    cols4 = [kappa, br_hist["q_src"], src_hist, m_hist]
    cols6 = [kappa, br_hist["q_src"], src_hist, m_hist, dj_mis, dj_mem]

    fit4_exx = ols_fit(ten_hist["e_xx"], cols4)
    fit4_ett = ols_fit(ten_hist["e_tt"], cols4)
    fit6_exx = ols_fit(ten_hist["e_xx"], cols6)
    fit6_ett = ols_fit(ten_hist["e_tt"], cols6)

    ratio4_split = (fit4_exx["ratio"] + fit4_ett["ratio"]) / 2.0
    ratio6_split = (fit6_exx["ratio"] + fit6_ett["ratio"]) / 2.0

    e_mis = fit6_ett["coeffs"][4]
    f_mem = fit6_ett["coeffs"][5]
    a_geom = fit6_ett["coeffs"][0]

    return {
        "seed": seed,
        "n_nodes": n_nodes,
        "ratio4_split": ratio4_split,
        "ratio6_split": ratio6_split,
        "delta_split": ratio6_split - ratio4_split,
        "improves": ratio6_split < ratio4_split,
        "e_mis_ett": e_mis,
        "f_mem_ett": f_mem,
        "a_geom_ett": a_geom,
        "e_mis_abs": abs(e_mis),
        "sign_e_mis": 1 if e_mis > 0 else -1,
        "fit6_ett_coeffs": dict(zip(names6, fit6_ett["coeffs"])),
        "fit6_exx_coeffs": dict(zip(["kappa", "q_src", "src", "m_eff", "div_J_mis", "div_J_mem"], fit6_exx["coeffs"])),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    # Run all 15 combinations
    all_results: dict[int, list[dict]] = {n: [] for n in N_VALUES}
    for n in N_VALUES:
        for s in SEEDS:
            r = run_one(s, n)
            all_results[n].append(r)

    # Per-N summary
    n_summary: dict[int, dict] = {}
    for n in N_VALUES:
        rs = all_results[n]
        n_improves = sum(r["improves"] for r in rs)
        mean_delta = sum(r["delta_split"] for r in rs) / len(rs)
        mean_e_mis = sum(r["e_mis_ett"] for r in rs) / len(rs)
        mean_e_mis_abs = sum(r["e_mis_abs"] for r in rs) / len(rs)
        n_summary[n] = {
            "n_improves": n_improves,
            "mean_delta": mean_delta,
            "mean_e_mis": mean_e_mis,
            "mean_e_mis_abs": mean_e_mis_abs,
        }

    # Evaluate predictions
    # P1: 6-ch beats 4-ch at N=32 on ≥ 4/5 seeds
    p1_pass = n_summary[32]["n_improves"] >= 4

    # P2: |e_mis(N=32)| < |e_mis(N=8)| on ≥ 3/5 seeds
    n_p2 = sum(
        1 for r8, r32 in zip(all_results[8], all_results[32])
        if r32["e_mis_abs"] < r8["e_mis_abs"]
    )
    p2_pass = n_p2 >= 3

    # P3: sign(e_mis_ett) consistent across all 3 N values on ≥ 4/5 seeds
    n_p3 = 0
    for i in range(len(SEEDS)):
        signs = [all_results[n][i]["sign_e_mis"] for n in N_VALUES]
        majority = 1 if sum(signs) > 0 else -1
        if all(s == majority for s in signs):
            n_p3 += 1
    p3_pass = n_p3 >= 4

    # P4: |mean Δratio(N=32)| < |mean Δratio(N=8)|
    p4_pass = abs(n_summary[32]["mean_delta"]) < abs(n_summary[8]["mean_delta"])

    n_pass = sum([p1_pass, p2_pass, p3_pass, p4_pass])
    decision = "pass" if n_pass >= 3 else ("partial" if n_pass >= 2 else "fail")

    if p1_pass and p3_pass:
        tier = "Tier-1-large-N"
    elif p1_pass:
        tier = "Tier-1.5"
    else:
        tier = "Tier-2"

    # Print table
    print("=" * 72)
    print("QNG-CPU-051 — GR 6-Channel Coupling Large-N Probe")
    print("=" * 72)
    print()
    for n in N_VALUES:
        print(f"N={n}:")
        print(f"  {'Seed':>10}  {'ratio4':>8}  {'ratio6':>8}  {'Δ':>8}  {'e_mis':>8}  {'sign':>5}")
        print(f"  {'-'*56}")
        for r in all_results[n]:
            print(
                f"  {r['seed']:>10}  {r['ratio4_split']:>8.4f}  "
                f"{r['ratio6_split']:>8.4f}  {r['delta_split']:>+8.4f}  "
                f"{r['e_mis_ett']:>+8.4f}  {r['sign_e_mis']:>+5d}"
            )
        s = n_summary[n]
        print(f"  mean:          {'':<8}  {'':<8}  {s['mean_delta']:>+8.4f}  {s['mean_e_mis']:>+8.4f}")
        print()

    print(f"N-scaling summary:")
    print(f"  N=8:  mean Δratio={n_summary[8]['mean_delta']:>+.4f}  mean|e_mis|={n_summary[8]['mean_e_mis_abs']:.4f}")
    print(f"  N=16: mean Δratio={n_summary[16]['mean_delta']:>+.4f}  mean|e_mis|={n_summary[16]['mean_e_mis_abs']:.4f}  (CPU-050 ref)")
    print(f"  N=32: mean Δratio={n_summary[32]['mean_delta']:>+.4f}  mean|e_mis|={n_summary[32]['mean_e_mis_abs']:.4f}")
    print()
    print(f"P1 (N=32 improves ≥ 4/5):                    {'PASS' if p1_pass else 'FAIL'} ({n_summary[32]['n_improves']}/5)")
    print(f"P2 (|e_mis(32)| < |e_mis(8)| on ≥ 3/5):     {'PASS' if p2_pass else 'FAIL'} ({n_p2}/5)")
    print(f"P3 (sign consistent across N on ≥ 4/5):      {'PASS' if p3_pass else 'FAIL'} ({n_p3}/5)")
    print(f"P4 (|mean Δ(N=32)| < |mean Δ(N=8)|):         {'PASS' if p4_pass else 'FAIL'}")
    print()
    print(f"Decision: {decision.upper()} ({n_pass}/4 predictions)")
    print(f"Tier classification: {tier}")

    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "test": "QNG-CPU-051",
        "theory": "DER-BRIDGE-033",
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
