"""QNG-CPU-050 — GR Coupling Covariance (Multi-Seed).

Tests whether the QM→GR 6-channel coupling coefficients (e_mis, f_mem)
from CPU-049 are Tier-1 universal or Tier-2 topology-dependent.

Runs the same 6-channel GR tensor fitting as CPU-049 across 5 seeds.

Pass criteria (from prereg QNG-CPU-050):
    P1: 6-channel beats 4-channel (Δratio_split < 0) on ≥ 4/5 seeds
    P2: |e_mis_ett| > |f_mem_ett| on ≥ 4/5 seeds
    P3: sign(e_mis_ett) consistent on ≥ 4/5 seeds
    P4: max(|e_mis|,|f_mem|) > 0.1·|a_geom| in E_tt on ≥ 3/5 seeds

Tier-1 if P1 + P3 both pass.
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
    ROOT / "07_validation" / "audits" / "qng-gr-coupling-covariance-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]


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
            f = aug[r][col]
            for k in range(col, m + 1):
                aug[r][k] -= f * aug[col][k]

    coeffs = [aug[i][m] for i in range(m)]
    pred = [sum(coeffs[j] * cols[j][k] for j in range(m)) for k in range(n)]
    raw = norm2(y)
    residual = norm2([y[k] - pred[k] for k in range(n)])
    ratio = residual / raw if raw > 1e-15 else 0.0
    return {"coeffs": coeffs, "ratio": ratio, "singular": False}


# ---------------------------------------------------------------------------
# Per-seed fitting
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> dict:
    """Run 4-channel and 6-channel GR fits for a given seed."""
    cfg = dataclasses.replace(Config(), seed=seed)

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

    names4 = ["kappa", "q_src", "src", "m_eff"]
    names6 = ["kappa", "q_src", "src", "m_eff", "div_J_mis", "div_J_mem"]

    cols4 = [kappa, br_hist["q_src"], src_hist, m_hist]
    cols6 = [kappa, br_hist["q_src"], src_hist, m_hist, dj_mis, dj_mem]

    fit4_exx = ols_fit(ten_hist["e_xx"], cols4)
    fit4_ett = ols_fit(ten_hist["e_tt"], cols4)
    fit6_exx = ols_fit(ten_hist["e_xx"], cols6)
    fit6_ett = ols_fit(ten_hist["e_tt"], cols6)

    ratio4_split = (fit4_exx["ratio"] + fit4_ett["ratio"]) / 2.0
    ratio6_split = (fit6_exx["ratio"] + fit6_ett["ratio"]) / 2.0
    delta_split = ratio6_split - ratio4_split

    # QM coupling metrics in E_tt
    e_mis = fit6_ett["coeffs"][4]
    f_mem = fit6_ett["coeffs"][5]
    a_geom = fit6_ett["coeffs"][0]

    e_mis_abs = abs(e_mis)
    f_mem_abs = abs(f_mem)
    a_geom_abs = abs(a_geom)
    max_qm = max(e_mis_abs, f_mem_abs)
    sig_ratio = max_qm / a_geom_abs if a_geom_abs > 1e-10 else 0.0

    return {
        "seed": seed,
        "ratio4_split": ratio4_split,
        "ratio6_split": ratio6_split,
        "delta_split": delta_split,
        "improves": delta_split < 0,
        "e_mis_ett": e_mis,
        "f_mem_ett": f_mem,
        "a_geom_ett": a_geom,
        "e_mis_abs": e_mis_abs,
        "f_mem_abs": f_mem_abs,
        "a_geom_abs": a_geom_abs,
        "mis_dominant": e_mis_abs > f_mem_abs,
        "sig_ratio": sig_ratio,
        "significant": sig_ratio > 0.1,
        "sign_e_mis": 1 if e_mis > 0 else -1,
        "fit4_exx_ratio": fit4_exx["ratio"],
        "fit4_ett_ratio": fit4_ett["ratio"],
        "fit6_exx_ratio": fit6_exx["ratio"],
        "fit6_ett_ratio": fit6_ett["ratio"],
        "fit6_exx_coeffs": dict(zip(names6, fit6_exx["coeffs"])),
        "fit6_ett_coeffs": dict(zip(names6, fit6_ett["coeffs"])),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    results = []
    for seed in SEEDS:
        r = run_seed(seed)
        results.append(r)

    # Evaluate predictions
    n_improves = sum(r["improves"] for r in results)
    n_mis_dominant = sum(r["mis_dominant"] for r in results)
    n_significant = sum(r["significant"] for r in results)

    # Sign coherence: majority sign
    signs = [r["sign_e_mis"] for r in results]
    majority_sign = 1 if sum(signs) >= 0 else -1
    n_sign_consistent = sum(1 for s in signs if s == majority_sign)

    p1_pass = n_improves >= 4
    p2_pass = n_mis_dominant >= 4
    p3_pass = n_sign_consistent >= 4
    p4_pass = n_significant >= 3

    n_pass = sum([p1_pass, p2_pass, p3_pass, p4_pass])
    decision = "pass" if n_pass >= 3 else ("partial" if n_pass >= 2 else "fail")

    # Tier classification
    if p1_pass and p3_pass:
        tier = "Tier-1"
    elif p1_pass:
        tier = "Tier-1.5"
    else:
        tier = "Tier-2"

    # Print results
    print("=" * 72)
    print("QNG-CPU-050 — GR Coupling Covariance (Multi-Seed)")
    print("=" * 72)
    print()
    print(f"{'Seed':>10}  {'ratio4':>8}  {'ratio6':>8}  {'Δ':>8}  {'improves':>8}  {'e_mis':>8}  {'f_mem':>8}  {'sig':>6}  {'sign':>5}")
    print("-" * 84)
    for r in results:
        print(
            f"{r['seed']:>10}  {r['ratio4_split']:>8.4f}  {r['ratio6_split']:>8.4f}  "
            f"{r['delta_split']:>+8.4f}  {'YES' if r['improves'] else 'NO':>8}  "
            f"{r['e_mis_ett']:>+8.4f}  {r['f_mem_ett']:>+8.4f}  "
            f"{r['sig_ratio']:>6.3f}  {r['sign_e_mis']:>+5d}"
        )
    print()
    print(f"P1 (improves ≥ 4/5):           {'PASS' if p1_pass else 'FAIL'} ({n_improves}/5)")
    print(f"P2 (mis_dominant ≥ 4/5):        {'PASS' if p2_pass else 'FAIL'} ({n_mis_dominant}/5)")
    print(f"P3 (sign_consistent ≥ 4/5):     {'PASS' if p3_pass else 'FAIL'} ({n_sign_consistent}/5, majority sign={majority_sign:+d})")
    print(f"P4 (significant ≥ 3/5):         {'PASS' if p4_pass else 'FAIL'} ({n_significant}/5)")
    print()
    print(f"Decision: {decision.upper()} ({n_pass}/4 predictions)")
    print(f"Tier classification: {tier}")
    print()

    # Mean improvement
    mean_delta = sum(r["delta_split"] for r in results) / len(results)
    mean_e_mis = sum(r["e_mis_ett"] for r in results) / len(results)
    mean_f_mem = sum(r["f_mem_ett"] for r in results) / len(results)
    print(f"Mean Δratio_split: {mean_delta:+.4f}")
    print(f"Mean e_mis_ett: {mean_e_mis:+.4f}")
    print(f"Mean f_mem_ett: {mean_f_mem:+.4f}")

    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "test": "QNG-CPU-050",
        "theory": "DER-BRIDGE-032",
        "decision": decision,
        "tier": tier,
        "n_pass": n_pass,
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "p3_pass": p3_pass,
        "p4_pass": p4_pass,
        "n_improves": n_improves,
        "n_mis_dominant": n_mis_dominant,
        "n_sign_consistent": n_sign_consistent,
        "n_significant": n_significant,
        "majority_sign_e_mis": majority_sign,
        "mean_delta_split": mean_delta,
        "mean_e_mis_ett": mean_e_mis,
        "mean_f_mem_ett": mean_f_mem,
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
