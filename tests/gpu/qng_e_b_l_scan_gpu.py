from __future__ import annotations

"""QNG-GPU-016: e_B sigma-gradient energy extended L-scan.

Tests the Bogomolny/bag-model hypothesis for QNG vortex-ring mass after the
ADM-analog path was ruled out by savant review (2026-04-18).

Observable: e_B(i) = (beta/4) * sum_nb (sigma_m_j - sigma_m_i)^2

Three flavors measured per (L, R):
  e_B_global   : sum over all sites
  e_B_windowed : sphere of radius R+3 around box center
  e_B_core     : tube of radius 3 around the toroidal ring curve

Gates (pre-registered in QNG-GPU-016.md):
  G1: last-3-L spread of e_B_ratio_global (R=5/R=4) at L in {80,100,120} < 0.05
  G2: same for e_B_ratio_windowed                                         < 0.05
  G3: |e_B_ratio(L=120) - 1.3130| / 1.3130 < 0.03  for global AND windowed
  G4: fit competition — Model A (a+b/L) vs Model B (a+b*log L)
      Delta-AIC(B-A) > 4  AND asymptote `a` > 1.28
  G5: e_B_ratio_global(L=120) > 1.28  (reject geometric 5/4)

Same dynamics as GPU-015 / GPU-011: v5 + Channel H in BOTH Phase 1 and 2,
k_gm=0. No new parameters.
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-e-b-l-scan-v1"

SIGMA_REF    = 0.5
ALPHA        = 0.005
BETA         = 0.35
DELTA_CHI    = 0.20
CHI_DECAY    = 0.020
CHI_REL      = 0.35
GAMMA_PHI    = 0.10
BETA_PHI_MIN  = 0.0005
BETA_PHI_RING = 0.06
K_GM          = 0.0

PHASE1 = 300
PHASE2 = 1500

L_VALUES = [20, 40, 60, 80, 100, 120]
RADII    = [4, 5]
RATIO_SM = 1232.0 / 938.3  # 1.3131

W_WINDOW_OFFSET = 3.0
W_CORE          = 3.0


# ---------------------------------------------------------------------------
# GPU geometry helpers (reused from GPU-015)
# ---------------------------------------------------------------------------

def build_nb(L):
    xs = np.arange(L, dtype=np.int32)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel()
    nb = np.stack([
        ((xg-1)%L)*L*L + yg*L + zg, ((xg+1)%L)*L*L + yg*L + zg,
        xg*L*L + ((yg-1)%L)*L + zg,  xg*L*L + ((yg+1)%L)*L + zg,
        xg*L*L + yg*L + (zg-1)%L,    xg*L*L + yg*L + (zg+1)%L,
    ], axis=1).astype(np.int32)
    return cp.asarray(nb)


def _centered_coords(L):
    cx = cy = cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg-cx; dy = yg-cy; dz = zg-cz
    for d in [dx, dy, dz]:
        d[:] = np.where(d >  L/2, d-L, d)
        d[:] = np.where(d < -L/2, d+L, d)
    return dx, dy, dz


def build_phi_ring(L, R):
    dx, dy, dz = _centered_coords(L)
    rho = np.sqrt(dx*dx + dy*dy)
    return cp.asarray(np.arctan2(dz, rho-R).ravel())


def build_window_mask(L, W):
    """Sphere mask around box center: |r - center| <= W."""
    dx, dy, dz = _centered_coords(L)
    r = np.sqrt(dx*dx + dy*dy + dz*dz)
    return cp.asarray((r <= W).ravel())


def build_core_mask(L, R, Wc):
    """Tube mask around the toroidal ring curve at radius R (z=center plane).
    Distance to curve: sqrt((rho - R)^2 + dz^2) <= Wc."""
    dx, dy, dz = _centered_coords(L)
    rho = np.sqrt(dx*dx + dy*dy)
    dist_curve = np.sqrt((rho - R)**2 + dz*dz)
    return cp.asarray((dist_curve <= Wc).ravel())


def wrap_gpu(a):
    a = a % (2*math.pi)
    return cp.where(a > math.pi, a - 2*math.pi, a)

def nb_mean(f, nb): return f[nb].mean(axis=1)

def disorder_gpu(phi, nb):
    pnb = phi[nb]
    return cp.maximum(0.0, 1.0 - cp.sqrt(cp.cos(pnb).mean(axis=1)**2 +
                                          cp.sin(pnb).mean(axis=1)**2))

def phi_wm(phi, sm, nb):
    pnb = phi[nb]; snb = sm[nb]; tw = snb.sum(axis=1)
    sx = (snb*cp.cos(pnb)).sum(axis=1); sy = (snb*cp.sin(pnb)).sum(axis=1)
    return cp.where(tw>1e-10, cp.arctan2(sy/cp.maximum(tw,1e-10),
                                          sx/cp.maximum(tw,1e-10)), phi)

def channel_h_bp(sm):
    dep_norm = cp.maximum(0.0, SIGMA_REF - sm) / SIGMA_REF
    return BETA_PHI_MIN + BETA_PHI_RING * dep_norm


# ---------------------------------------------------------------------------
# Dynamics (same as GPU-011/015)
# ---------------------------------------------------------------------------

def step_phase1(sm, chi, phi, nb):
    smb = nb_mean(sm, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm), 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    bp_eff = channel_h_bp(sm)
    pm  = phi_wm(phi, sm, nb)
    np_ = wrap_gpu(phi + bp_eff * wrap_gpu(pm - phi))
    return nsm, nc, np_

def step_phase2(sm, chi, phi, nb):
    smb = nb_mean(sm, nb)
    dis = disorder_gpu(phi, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm)
                     - GAMMA_PHI*dis*sm, 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    bp_eff = channel_h_bp(sm)
    pm  = phi_wm(phi, sm, nb)
    np_ = wrap_gpu(phi + bp_eff * wrap_gpu(pm - phi))
    return nsm, nc, np_


# ---------------------------------------------------------------------------
# e_B and cross-check observables
# ---------------------------------------------------------------------------

def compute_e_B_per_site(sm, nb):
    """e_B(i) = (beta/4) * sum_nb (sm_j - sm_i)^2."""
    sm_nb = sm[nb]
    grad2 = ((sm_nb - sm[:, None])**2).sum(axis=1)
    return 0.25 * BETA * grad2


def compute_cross_checks(sm, chi, phi, nb):
    """Minimal set of cross-check observables: e_chi_rel (second-best from
    GPU-015 Gate 4) and M_ring_global (confirms geometric pathology persists)."""
    smb = nb_mean(sm, nb)
    e_chi_rel = 0.5 * CHI_REL * chi * (smb - sm)
    return {
        "e_chi_rel_global": float(cp.sum(e_chi_rel)),
        "M_ring_global": float(sm.size * SIGMA_REF - cp.sum(sm)),
    }


# ---------------------------------------------------------------------------
# Run one (L, R)
# ---------------------------------------------------------------------------

def run_ring(L, R, nb):
    N = L*L*L
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi_ring(L, R)

    for _ in range(PHASE1):
        sm, chi, phi = step_phase1(sm, chi, phi, nb)
    for _ in range(PHASE2):
        sm, chi, phi = step_phase2(sm, chi, phi, nb)

    e_B_site = compute_e_B_per_site(sm, nb)

    # Vacuum check: e_B at vacuum (sm = SIGMA_REF everywhere) is exactly zero
    # because all neighbor differences vanish. No vacuum subtraction needed.

    mask_window = build_window_mask(L, R + W_WINDOW_OFFSET)
    mask_core   = build_core_mask(L, R, W_CORE)

    e_B_global   = float(cp.sum(e_B_site))
    e_B_windowed = float(cp.sum(e_B_site[mask_window]))
    e_B_core     = float(cp.sum(e_B_site[mask_core]))

    cross = compute_cross_checks(sm, chi, phi, nb)

    # Size diagnostics
    N_window = int(cp.sum(mask_window))
    N_core   = int(cp.sum(mask_core))

    return {
        "L": L, "R": R, "N": N,
        "N_window": N_window, "N_core": N_core,
        "e_B_global": e_B_global,
        "e_B_windowed": e_B_windowed,
        "e_B_core": e_B_core,
        **cross,
    }


# ---------------------------------------------------------------------------
# Fit competition (Gate 4)
# ---------------------------------------------------------------------------

def fit_linear(X, y):
    """Least-squares fit y = a + b*X. Returns (a, b, sse)."""
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    A = np.column_stack([np.ones_like(X), X])
    coef, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    a, b = float(coef[0]), float(coef[1])
    resid = y - (a + b*X)
    sse = float(np.sum(resid*resid))
    return a, b, sse


def aic(n, k, sse):
    """Akaike information criterion for least-squares (Gaussian residuals)."""
    if sse <= 0:
        return -float('inf')
    return 2*k + n*math.log(sse/n)


def fit_competition(L_vals, ratios):
    """Fit both models, return AIC and asymptotes."""
    Ls = np.asarray(L_vals, dtype=np.float64)
    # Model A: ratio = a_A + b_A / L
    aA, bA, sseA = fit_linear(1.0 / Ls, ratios)
    # Model B: ratio = a_B + b_B * log(L)
    aB, bB, sseB = fit_linear(np.log(Ls), ratios)
    n = len(L_vals); k = 2
    aicA = aic(n, k, sseA)
    aicB = aic(n, k, sseB)
    return {
        "modelA": {"a": aA, "b": bA, "sse": sseA, "aic": aicA, "form": "a + b/L"},
        "modelB": {"a": aB, "b": bB, "sse": sseB, "aic": aicB, "form": "a + b*log(L)"},
        "delta_aic_B_minus_A": aicB - aicA,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("QNG-GPU-016: e_B extended L-scan")
    print(f"v5 + Channel H (Phase 1 and 2), K_GM={K_GM}")
    print(f"bp_min={BETA_PHI_MIN}  bp_ring={BETA_PHI_RING}")
    print(f"PHASE1={PHASE1}  PHASE2={PHASE2}")
    print(f"L values: {L_VALUES}  Radii: {RADII}")
    print(f"SM ratio Delta/N = {RATIO_SM:.4f}")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB", flush=True)
    print()

    all_results = []

    for L in L_VALUES:
        print(f"=== L={L} ===", flush=True)
        nb = build_nb(L)

        for R in RADII:
            res = run_ring(L, R, nb)
            all_results.append(res)
            print(f"  R={R}: e_B_glob={res['e_B_global']:.4e}  "
                  f"e_B_win={res['e_B_windowed']:.4e}  "
                  f"e_B_core={res['e_B_core']:.4e}  "
                  f"N_win={res['N_window']}  N_core={res['N_core']}  "
                  f"M_ring={res['M_ring_global']:.1f}", flush=True)

        del nb
        cp.get_default_memory_pool().free_all_blocks()

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    print()
    print("="*110)
    print("e_B RATIOS vs L")
    print("="*110)
    header = f"{'L':>4}  {'eB_g(R4)':>11}  {'eB_g(R5)':>11}  {'r_g':>6}  {'eB_w(R4)':>11}  {'eB_w(R5)':>11}  {'r_w':>6}  {'eB_c(R4)':>11}  {'eB_c(R5)':>11}  {'r_c':>6}"
    print(header)
    print("-"*len(header))

    scan = []
    for L in L_VALUES:
        r4 = next(r for r in all_results if r["L"]==L and r["R"]==4)
        r5 = next(r for r in all_results if r["L"]==L and r["R"]==5)
        ratio_g = (r5["e_B_global"]   / r4["e_B_global"])   if abs(r4["e_B_global"])   > 1e-12 else float('nan')
        ratio_w = (r5["e_B_windowed"] / r4["e_B_windowed"]) if abs(r4["e_B_windowed"]) > 1e-12 else float('nan')
        ratio_c = (r5["e_B_core"]     / r4["e_B_core"])     if abs(r4["e_B_core"])     > 1e-12 else float('nan')
        print(f"{L:>4}  {r4['e_B_global']:>11.4e}  {r5['e_B_global']:>11.4e}  {ratio_g:>6.4f}  "
              f"{r4['e_B_windowed']:>11.4e}  {r5['e_B_windowed']:>11.4e}  {ratio_w:>6.4f}  "
              f"{r4['e_B_core']:>11.4e}  {r5['e_B_core']:>11.4e}  {ratio_c:>6.4f}")
        scan.append({
            "L": L,
            "eB_R4_global": r4['e_B_global'], "eB_R5_global": r5['e_B_global'],
            "ratio_global": ratio_g,
            "eB_R4_windowed": r4['e_B_windowed'], "eB_R5_windowed": r5['e_B_windowed'],
            "ratio_windowed": ratio_w,
            "eB_R4_core": r4['e_B_core'], "eB_R5_core": r5['e_B_core'],
            "ratio_core": ratio_c,
        })

    # Gate 1: last-3-L spread of ratio_global (over L=80,100,120)
    idx_last3 = [L_VALUES.index(L) for L in [80, 100, 120] if L in L_VALUES]
    ratios_g_last3 = [scan[i]["ratio_global"] for i in idx_last3]
    spread_g = max(ratios_g_last3) - min(ratios_g_last3)

    # Gate 2: last-3-L spread of ratio_windowed
    ratios_w_last3 = [scan[i]["ratio_windowed"] for i in idx_last3]
    spread_w = max(ratios_w_last3) - min(ratios_w_last3)

    # Gate 3: SM ratio match at L=120
    i_last = L_VALUES.index(120)
    ratio_g_120 = scan[i_last]["ratio_global"]
    ratio_w_120 = scan[i_last]["ratio_windowed"]
    ratio_c_120 = scan[i_last]["ratio_core"]
    match_g = abs(ratio_g_120 - RATIO_SM) / RATIO_SM
    match_w = abs(ratio_w_120 - RATIO_SM) / RATIO_SM

    # Gate 4: fit competition on global ratio
    fit = fit_competition([s["L"] for s in scan], [s["ratio_global"] for s in scan])

    # Gate 5: geometric rejection
    gate5 = ratio_g_120 > 1.28

    # Decisions
    g1 = spread_g < 0.05
    g2 = spread_w < 0.05
    g3 = (match_g < 0.03) and (match_w < 0.03)
    g4 = (fit["delta_aic_B_minus_A"] > 4) and (fit["modelA"]["a"] > 1.28)
    g5 = gate5

    print()
    print(f"Gate 1 (e_B global L-spread over L=80,100,120): {spread_g:.4f}  (threshold < 0.05)  {'PASS' if g1 else 'FAIL'}")
    print(f"Gate 2 (e_B windowed L-spread):                 {spread_w:.4f}  (threshold < 0.05)  {'PASS' if g2 else 'FAIL'}")
    print(f"Gate 3 (SM match at L=120):")
    print(f"         global:   ratio={ratio_g_120:.4f}  SM={RATIO_SM:.4f}  dev={match_g*100:.2f}%  (gate < 3%)")
    print(f"         windowed: ratio={ratio_w_120:.4f}                     dev={match_w*100:.2f}%  (gate < 3%)")
    print(f"         core:     ratio={ratio_c_120:.4f}  (informational)")
    print(f"         => {'PASS' if g3 else 'FAIL'}")
    print(f"Gate 4 (fit competition):")
    print(f"         Model A (a + b/L):        a={fit['modelA']['a']:.4f}  b={fit['modelA']['b']:.4f}  AIC={fit['modelA']['aic']:.2f}")
    print(f"         Model B (a + b*log(L)):   a={fit['modelB']['a']:.4f}  b={fit['modelB']['b']:.4f}  AIC={fit['modelB']['aic']:.2f}")
    print(f"         Delta-AIC (B-A) = {fit['delta_aic_B_minus_A']:.2f}  (A preferred if > 4)")
    print(f"         asymptote `a` (Model A) = {fit['modelA']['a']:.4f}  (threshold > 1.28)")
    print(f"         => {'PASS' if g4 else 'FAIL'}")
    print(f"Gate 5 (geometric rejection, ratio(L=120) > 1.28): ratio_g={ratio_g_120:.4f}  {'PASS' if g5 else 'FAIL'}")
    print()

    # Verdict
    if g1 and g2 and g3 and g4 and g5:
        verdict = "PASS_STRONG"
        interp = ("e_B is an L-convergent mass observable matching SM. "
                  "DER-QNG-038 rehabilitated via Bogomolny/bag-model route.")
    elif g4 and g5 and not g3:
        verdict = "PASS_WEAK"
        interp = ("e_B converges but not to SM. Legitimate mass observable; "
                  "baryon ladder assignments need revision.")
    elif (not g5) or (fit["delta_aic_B_minus_A"] <= 4 and not g4):
        verdict = "FAIL_GEOMETRIC"
        interp = ("e_B exhibits geometric drift (ratio < 1.28 or Model B preferred). "
                  "Soliton rest-energy hypothesis falsified.")
    else:
        verdict = "AMBIGUOUS"
        interp = ("Convergence not decided at L=120. Requires L=160+ extension.")

    print(f"VERDICT: {verdict}")
    print(f"  {interp}")
    print()

    # JSON report
    report = {
        "test_id": "QNG-GPU-016",
        "status": verdict,
        "parameters": {
            "ALPHA": ALPHA, "BETA": BETA, "DELTA_CHI": DELTA_CHI,
            "CHI_DECAY": CHI_DECAY, "CHI_REL": CHI_REL, "GAMMA_PHI": GAMMA_PHI,
            "BETA_PHI_MIN": BETA_PHI_MIN, "BETA_PHI_RING": BETA_PHI_RING,
            "K_GM": K_GM, "PHASE1": PHASE1, "PHASE2": PHASE2,
            "W_WINDOW_OFFSET": W_WINDOW_OFFSET, "W_CORE": W_CORE,
        },
        "L_values": L_VALUES, "RADII": RADII, "RATIO_SM": RATIO_SM,
        "scan": scan,
        "raw_results": all_results,
        "fit_competition": fit,
        "gates": {
            "G1_eB_global_spread": {"value": spread_g, "threshold": 0.05, "pass": g1},
            "G2_eB_windowed_spread": {"value": spread_w, "threshold": 0.05, "pass": g2},
            "G3_SM_match": {
                "ratio_global_L120": ratio_g_120,
                "ratio_windowed_L120": ratio_w_120,
                "ratio_core_L120": ratio_c_120,
                "dev_global": match_g, "dev_windowed": match_w,
                "threshold": 0.03, "pass": g3,
            },
            "G4_fit_competition": {
                "delta_aic_B_minus_A": fit["delta_aic_B_minus_A"],
                "asymptote_A": fit["modelA"]["a"],
                "threshold_delta_aic": 4, "threshold_asymptote": 1.28,
                "pass": g4,
            },
            "G5_geometric_rejection": {
                "ratio_global_L120": ratio_g_120,
                "threshold": 1.28, "pass": g5,
            },
        },
        "verdict": verdict,
        "interpretation": interp,
    }

    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Summary.md
    with open(out / "summary.md", "w", encoding="utf-8") as f:
        f.write("# e_B Extended L-Scan (QNG-GPU-016)\n\n")
        f.write(f"Protocol: v5 + Channel H (Phase 1 and 2), K_GM={K_GM}\n")
        f.write(f"bp_min={BETA_PHI_MIN}  bp_ring={BETA_PHI_RING}\n")
        f.write(f"SM ratio Delta/N = {RATIO_SM:.4f}\n\n")
        f.write("## e_B ratios vs L\n\n")
        f.write("| L | eB_g(R4) | eB_g(R5) | r_g | eB_w(R4) | eB_w(R5) | r_w | eB_c(R4) | eB_c(R5) | r_c |\n")
        f.write("|---|---------|---------|-----|---------|---------|-----|---------|---------|----|\n")
        for s in scan:
            f.write(f"| {s['L']} | {s['eB_R4_global']:.3e} | {s['eB_R5_global']:.3e} | {s['ratio_global']:.4f} | "
                    f"{s['eB_R4_windowed']:.3e} | {s['eB_R5_windowed']:.3e} | {s['ratio_windowed']:.4f} | "
                    f"{s['eB_R4_core']:.3e} | {s['eB_R5_core']:.3e} | {s['ratio_core']:.4f} |\n")
        f.write("\n## Gates\n\n")
        f.write(f"- **Gate 1** (e_B global L-spread, L=80..120): {spread_g:.4f}  threshold < 0.05  -> {'PASS' if g1 else 'FAIL'}\n")
        f.write(f"- **Gate 2** (e_B windowed L-spread): {spread_w:.4f}  threshold < 0.05  -> {'PASS' if g2 else 'FAIL'}\n")
        f.write(f"- **Gate 3** (SM match at L=120):\n")
        f.write(f"   - global:   ratio={ratio_g_120:.4f}  dev={match_g*100:.2f}%\n")
        f.write(f"   - windowed: ratio={ratio_w_120:.4f}  dev={match_w*100:.2f}%\n")
        f.write(f"   - core:     ratio={ratio_c_120:.4f}  (informational)\n")
        f.write(f"   -> {'PASS' if g3 else 'FAIL'}\n")
        f.write(f"- **Gate 4** (fit competition):\n")
        f.write(f"   - Model A (a+b/L):  a={fit['modelA']['a']:.4f}, AIC={fit['modelA']['aic']:.2f}\n")
        f.write(f"   - Model B (a+b*log L): a={fit['modelB']['a']:.4f}, AIC={fit['modelB']['aic']:.2f}\n")
        f.write(f"   - Delta-AIC (B-A) = {fit['delta_aic_B_minus_A']:.2f}  (A preferred if > 4)\n")
        f.write(f"   - A asymptote > 1.28 required: a={fit['modelA']['a']:.4f}\n")
        f.write(f"   -> {'PASS' if g4 else 'FAIL'}\n")
        f.write(f"- **Gate 5** (geometric rejection): ratio(L=120)={ratio_g_120:.4f} > 1.28  -> {'PASS' if g5 else 'FAIL'}\n\n")
        f.write(f"## Verdict: **{verdict}**\n\n")
        f.write(f"{interp}\n")

    print(f"Reports written to {out}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
