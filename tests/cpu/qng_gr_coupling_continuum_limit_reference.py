"""QNG-CPU-052 — GR Coupling Continuum Limit Probe (N=64).

Extends the N-scaling from CPU-051 to N=64, testing whether the QM→GR coupling
constant e_mis saturates (→ const) or vanishes (→ 0) in the continuum limit.

Full run: N ∈ {8, 16, 32, 64} × 5 seeds = 20 runs.

Pass criteria (from prereg QNG-CPU-052):
    P1: Δratio_split(N=64) < 0 on ≥ 4/5 seeds
    P2: mean|e_mis(N=64)| < 0.159  (continues to decrease from N=32)
    P3: mean|e_mis(N=64)| > 0.050  (non-vanishing)
    P4: sign(e_mis_ett) consistent across all 4 N values on ≥ 4/5 seeds

Reference (CPU-051):
    N=8:  mean|e_mis|=1.037  mean Δratio=−0.147
    N=16: mean|e_mis|=0.259  mean Δratio=−0.043
    N=32: mean|e_mis|=0.159  mean Δratio=−0.018
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
    ROOT / "07_validation" / "audits" / "qng-gr-coupling-continuum-limit-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]
N_VALUES = [8, 16, 32, 64]

# Reference from CPU-051
MEAN_E_MIS_N32 = 0.159
MEAN_DELTA_N32 = -0.018

# Saturation thresholds
SAT_HIGH = 0.120   # saturation regime
SAT_LOW  = 0.050   # vanishing threshold


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def norm2(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def div_J_grad(
    c: list[float], f: list[float], adj: list[list[int]]
) -> list[float]:
    return [
        c[i] * sum(c[j] * (f[j] - f[i]) for j in adj[i])
        for i in range(len(c))
    ]


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

    return {
        "seed": seed,
        "n_nodes": n_nodes,
        "ratio4_split": ratio4_split,
        "ratio6_split": ratio6_split,
        "delta_split": ratio6_split - ratio4_split,
        "improves": ratio6_split < ratio4_split,
        "e_mis_ett": e_mis,
        "f_mem_ett": f_mem,
        "e_mis_abs": abs(e_mis),
        "sign_e_mis": 1 if e_mis > 0 else -1,
        "fit6_ett_coeffs": dict(zip(names6, fit6_ett["coeffs"])),
    }


# ---------------------------------------------------------------------------
# Power-law fit helper
# ---------------------------------------------------------------------------

def fit_power_law(ns: list[int], vals: list[float]) -> dict:
    """Fit log(val) = a + b*log(N) via least squares."""
    log_n = [math.log(n) for n in ns]
    log_v = [math.log(max(v, 1e-15)) for v in vals]
    n = len(ns)
    mean_ln = sum(log_n) / n
    mean_lv = sum(log_v) / n
    b = sum((log_n[i] - mean_ln) * (log_v[i] - mean_lv) for i in range(n)) / \
        sum((log_n[i] - mean_ln) ** 2 for i in range(n))
    a = mean_lv - b * mean_ln
    return {"exponent": b, "prefactor": math.exp(a)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    all_results: dict[int, list[dict]] = {n: [] for n in N_VALUES}
    for n in N_VALUES:
        print(f"  Running N={n}...", flush=True)
        for s in SEEDS:
            r = run_one(s, n)
            all_results[n].append(r)

    # Per-N summary
    n_summary: dict[int, dict] = {}
    for n in N_VALUES:
        rs = all_results[n]
        n_summary[n] = {
            "n_improves": sum(r["improves"] for r in rs),
            "mean_delta": sum(r["delta_split"] for r in rs) / len(rs),
            "mean_e_mis": sum(r["e_mis_ett"] for r in rs) / len(rs),
            "mean_e_mis_abs": sum(r["e_mis_abs"] for r in rs) / len(rs),
        }

    # Power-law fit on all 4 points
    ns_for_fit = N_VALUES
    vals_for_fit = [n_summary[n]["mean_e_mis_abs"] for n in ns_for_fit]
    power_fit = fit_power_law(ns_for_fit, vals_for_fit)
    # Extrapolate to N=128, N=256
    extrap = {
        128: power_fit["prefactor"] * (128 ** power_fit["exponent"]),
        256: power_fit["prefactor"] * (256 ** power_fit["exponent"]),
        "inf_trend": "vanishing" if power_fit["exponent"] < -0.1 else "saturating",
    }

    # Evaluate predictions
    mean_e_mis_64 = n_summary[64]["mean_e_mis_abs"]
    n_improves_64 = n_summary[64]["n_improves"]
    p1_pass = n_improves_64 >= 4
    p2_pass = mean_e_mis_64 < MEAN_E_MIS_N32
    p3_pass = mean_e_mis_64 > SAT_LOW

    # P4: sign consistent across all 4 N values on ≥ 4/5 seeds
    n_p4 = 0
    for i in range(len(SEEDS)):
        signs = [all_results[n][i]["sign_e_mis"] for n in N_VALUES]
        majority = 1 if sum(signs) > 0 else -1
        if all(s == majority for s in signs):
            n_p4 += 1
    p4_pass = n_p4 >= 4

    n_pass = sum([p1_pass, p2_pass, p3_pass, p4_pass])
    decision = "pass" if n_pass >= 3 else ("partial" if n_pass >= 2 else "fail")

    # Saturation classification
    if mean_e_mis_64 > SAT_HIGH:
        sat_class = "SATURATION"
    elif mean_e_mis_64 > SAT_LOW:
        sat_class = "SLOW-DECAY (finite-limit plausible)"
    else:
        sat_class = "VANISHING (UV-only)"

    # Print
    print()
    print("=" * 72)
    print("QNG-CPU-052 — GR Coupling Continuum Limit Probe (N=64)")
    print("=" * 72)
    print()
    for n in N_VALUES:
        rs = all_results[n]
        s = n_summary[n]
        label = " ← CPU-051 ref" if n == 32 else (" ← NEW" if n == 64 else "")
        print(f"N={n}{label}:")
        print(f"  {'Seed':>10}  {'delta':>8}  {'e_mis':>8}  {'sign':>5}")
        print(f"  {'-'*40}")
        for r in rs:
            print(f"  {r['seed']:>10}  {r['delta_split']:>+8.4f}  {r['e_mis_ett']:>+8.4f}  {r['sign_e_mis']:>+5d}")
        print(f"  mean:  Δ={s['mean_delta']:>+8.4f}  |e_mis|={s['mean_e_mis_abs']:.4f}")
        print()

    print(f"N-scaling (mean|e_mis|):")
    for n in N_VALUES:
        ratio = n_summary[n]["mean_e_mis_abs"] / n_summary[8]["mean_e_mis_abs"]
        print(f"  N={n:>2}: {n_summary[n]['mean_e_mis_abs']:.4f}  ({ratio:.3f}× of N=8)")
    print()
    print(f"Power-law fit: |e_mis| ≈ {power_fit['prefactor']:.3f} × N^({power_fit['exponent']:.3f})")
    print(f"Extrapolations: N=128 → {extrap[128]:.4f},  N=256 → {extrap[256]:.4f}")
    print(f"Continuum trend: {extrap['inf_trend']}")
    print()
    print(f"Saturation class: {sat_class}")
    print(f"  mean|e_mis(N=64)|={mean_e_mis_64:.4f}  (thresholds: sat>{SAT_HIGH}, vanish<{SAT_LOW})")
    print()
    print(f"P1 (N=64 improves ≥ 4/5):                {'PASS' if p1_pass else 'FAIL'} ({n_improves_64}/5)")
    print(f"P2 (mean|e_mis(64)| < 0.159):             {'PASS' if p2_pass else 'FAIL'} ({mean_e_mis_64:.4f})")
    print(f"P3 (mean|e_mis(64)| > 0.050):             {'PASS' if p3_pass else 'FAIL'} ({mean_e_mis_64:.4f})")
    print(f"P4 (sign consistent 4N on ≥ 4/5):        {'PASS' if p4_pass else 'FAIL'} ({n_p4}/5)")
    print()
    print(f"Decision: {decision.upper()} ({n_pass}/4 predictions)")

    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "test": "QNG-CPU-052",
        "theory": "DER-BRIDGE-034",
        "decision": decision,
        "n_pass": n_pass,
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "p3_pass": p3_pass,
        "p4_pass": p4_pass,
        "p4_count": n_p4,
        "saturation_class": sat_class,
        "mean_e_mis_abs_n64": mean_e_mis_64,
        "power_law_fit": power_fit,
        "extrapolations": {"N128": extrap[128], "N256": extrap[256], "trend": extrap["inf_trend"]},
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
