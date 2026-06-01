"""
QNG-CPU-100: Verlinde-entropic / holographic probe on V9-A orbital attractor.

Compute classical Shannon entropies, Bekenstein-like entropy/area ratios,
and orbit-action candidates across R in {3, 4, 5}. Test for R-universality
as a candidate hbar.
"""

import json
import math
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "07_validation" / "audits" / "qng-v9a-phase-space-v1"
BERRY_DIR = ROOT / "07_validation" / "audits" / "qng-v9a-berry-analysis-v1"
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-cpu100-verlinde-entropic-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

L = 20
N = L * L * L
BINS = 40


def shannon_entropy_2d(x, y, bins=BINS):
    """Compute Shannon entropy of 2D distribution of (x, y) samples."""
    H, _, _ = np.histogram2d(x.ravel(), y.ravel(), bins=bins)
    H = H.astype(np.float64)
    total = H.sum()
    if total <= 0:
        return 0.0
    p = H / total
    mask = p > 0
    return float(-(p[mask] * np.log(p[mask])).sum())


def analyze_R(R):
    snap_path = DATA_DIR / f"R{R}" / "snapshots.npz"
    red_path = DATA_DIR / f"R{R}" / "reduced_series.npz"
    if not snap_path.exists() or not red_path.exists():
        return None

    print(f"[R={R}] loading data")
    d = np.load(snap_path)
    sm = d["sm"]        # (500, N)
    pi_m = d["pi_m"]
    phi = d["phi"]
    pi_phi = d["pi_phi"]
    t_snap = d["t_snap"]
    nsnap = sm.shape[0]

    r = np.load(red_path)
    t = r["t"]
    H = r["H"]
    M_ring = r["M_ring"]

    # === C1/C2: pooled Shannon entropies over ALL snapshots ===
    S_sm_pooled = shannon_entropy_2d(sm, pi_m, bins=BINS)
    S_phi_pooled = shannon_entropy_2d(phi, pi_phi, bins=BINS)

    # === Per-snapshot (instantaneous) entropies: measure how each snapshot's spatial distribution is spread ===
    S_sm_inst = np.array([shannon_entropy_2d(sm[s], pi_m[s], bins=BINS) for s in range(nsnap)])
    S_phi_inst = np.array([shannon_entropy_2d(phi[s], pi_phi[s], bins=BINS) for s in range(nsnap)])

    # === Cycle period ===
    # Use mean M_ring crossing rate
    M_mean = M_ring.mean()
    crossings = np.where(np.diff(np.sign(M_ring - M_mean)) > 0)[0]
    if len(crossings) >= 2:
        T_cycle = float((t[crossings[-1]] - t[crossings[0]]) / (len(crossings) - 1))
    else:
        T_cycle = float(t[-1] - t[0])
    n_cycles = len(crossings) - 1 if len(crossings) >= 2 else 0

    # === C3: ring area proxy ===
    A_ring = 4.0 * math.pi * math.pi * R * R   # torus surface for tube radius ~ 1

    # === C4/C5: Bekenstein-like ratios ===
    rho1 = S_sm_pooled / A_ring if A_ring > 0 else 0.0  # [nats / area]
    rho2 = S_phi_pooled / A_ring if A_ring > 0 else 0.0

    # === C6: orbit-action candidate ===
    S_total = S_sm_pooled + S_phi_pooled
    S_orbit = S_total * T_cycle   # nats * lu (dimensional: if S nats are converted to action via some scale, this is the action candidate)

    # === C7: entropy production per cycle ===
    if nsnap >= 4:
        early_idx = slice(0, nsnap // 4)
        late_idx = slice(3 * nsnap // 4, nsnap)
        dS = float(S_sm_inst[late_idx].mean() - S_sm_inst[early_idx].mean())
        sigma_prod = dS / T_cycle if T_cycle > 0 else 0.0
    else:
        sigma_prod = 0.0

    # === Auxiliary: Liouville check (phase-space volume occupied) ===
    # Use per-dimension std as crude proxy
    vol_proxy = float(np.std(sm) * np.std(pi_m) * np.std(phi) * np.std(pi_phi))

    # === H, energy scale ===
    H_mean = float(H.mean())
    H_cv = float(H.std() / abs(H.mean())) if H.mean() != 0 else 0.0

    return {
        "R": R,
        "n_snapshots": nsnap,
        "T_cycle": T_cycle,
        "n_cycles_full": int(n_cycles),
        "A_ring_proxy": float(A_ring),
        "S_sm_pooled": float(S_sm_pooled),
        "S_phi_pooled": float(S_phi_pooled),
        "S_sm_inst_mean": float(S_sm_inst.mean()),
        "S_sm_inst_std": float(S_sm_inst.std()),
        "S_phi_inst_mean": float(S_phi_inst.mean()),
        "S_phi_inst_std": float(S_phi_inst.std()),
        "rho1_Ssm_over_A": float(rho1),
        "rho2_Sphi_over_A": float(rho2),
        "S_orbit_total_times_T": float(S_orbit),
        "sigma_prod_per_lu": float(sigma_prod),
        "vol_proxy_liouville": vol_proxy,
        "H_mean": H_mean,
        "H_cv": H_cv,
    }


def cv(values):
    a = np.asarray(values, dtype=np.float64)
    if np.all(a == 0) or a.mean() == 0:
        return 0.0
    return float(a.std() / abs(a.mean()))


def verdict(results):
    Rs = sorted(k for k in results if results[k] is not None)
    if len(Rs) < 3:
        return "VERLINDE-INCOMPLETE", {}

    tests = {
        "S_sm_pooled": [results[R]["S_sm_pooled"] for R in Rs],
        "S_phi_pooled": [results[R]["S_phi_pooled"] for R in Rs],
        "rho1_Ssm_over_A": [results[R]["rho1_Ssm_over_A"] for R in Rs],
        "rho2_Sphi_over_A": [results[R]["rho2_Sphi_over_A"] for R in Rs],
        "S_orbit_total_times_T": [results[R]["S_orbit_total_times_T"] for R in Rs],
        "sigma_prod_per_lu": [results[R]["sigma_prod_per_lu"] for R in Rs],
    }

    cvs = {k: cv(v) for k, v in tests.items()}
    best_key = min(cvs, key=lambda k: cvs[k])
    best_cv = cvs[best_key]

    if best_cv < 0.05:
        status = "VERLINDE-PASS"
    elif best_cv < 0.20:
        status = "VERLINDE-MARGINAL"
    else:
        status = "VERLINDE-FAIL"

    return status, {"cvs": cvs, "best_candidate": best_key, "best_cv": best_cv, "values": tests}


def main():
    results = {}
    for R in (3, 4, 5):
        r = analyze_R(R)
        results[R] = r
        if r is not None:
            print(f"[R={R}] S_sm={r['S_sm_pooled']:.3f}  S_phi={r['S_phi_pooled']:.3f}  "
                  f"T_cycle={r['T_cycle']:.2f}  rho1={r['rho1_Ssm_over_A']:.5f}  "
                  f"rho2={r['rho2_Sphi_over_A']:.5f}  S_orbit={r['S_orbit_total_times_T']:.1f}  "
                  f"H={r['H_mean']:.1f}(cv {r['H_cv']:.2%})")

    status, summary = verdict(results)
    print(f"\nVERDICT: {status}")
    print("Per-candidate CV (smallest = most R-universal):")
    if "cvs" in summary:
        for k, v in sorted(summary["cvs"].items(), key=lambda kv: kv[1]):
            print(f"  {k}: CV={v:.4f}  values={summary['values'][k]}")
        print(f"Best candidate: {summary['best_candidate']} (CV={summary['best_cv']:.4f})")

    report = {
        "test_id": "QNG-CPU-100",
        "verdict": status,
        "summary": summary,
        "per_R": results,
    }
    with open(OUT_DIR / "report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nWrote {OUT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
