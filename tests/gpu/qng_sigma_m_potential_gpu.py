from __future__ import annotations

"""QNG-GPU-018: V(sigma_m) Ginzburg-Landau term — test DER-QNG-040.

Adds V(sigma_m) = (LAMBDA/4) * (sigma_m^2 - sigma_ref^2)^2 to the sigma_m
update in v5+Channel H dynamics. LAMBDA is committed pre-run from DER-QNG-040
saturation of the marginal-stability condition:

    LAMBDA = (GAMMA_PHI - ALPHA_m) / (2 * sigma_ref^2)
           = (0.10 - 0.005) / (2 * 0.25)
           = 0.19

Predicted healing length:
    xi = sqrt(BETA / (2 * LAMBDA * sigma_ref^2))
       = sqrt(0.35 / (2 * 0.19 * 0.25))
       = 1.92 lu
    FWHM_pred = 2 * sqrt(2*ln 2) * xi = 4.52 lu

Four stages / gates (pre-reg QNG-GPU-018.md):

  Stage A: IR halo scan. L in {40,60,80,100}, R=5.
           Gate A: alpha(L=80,R=5) >= 3.5.
  Stage B: R-independent core FWHM. L=80, R in {4,5,6,7}.
           Gate B: spread_R(FWHM)/mean(FWHM) < 0.30, mean near 4.52 lu.
  Stage C: L-converged mass ratio. L in {60,80,100,120}, R in {4,5}.
           Gate C: spread_L(ratio) < 0.08, mean in [1.25, 1.40].
  Stage D: linearized damping rate test.
           Gate D: |r_eff - 0.100| / 0.100 < 0.20.

"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-sigma-m-potential-v1"

# v7 / v5+H baseline parameters (frozen)
SIGMA_REF     = 0.5
ALPHA         = 0.005
BETA          = 0.35
DELTA_CHI     = 0.20
CHI_DECAY     = 0.020
CHI_REL       = 0.35
GAMMA_PHI     = 0.10
BETA_PHI_MIN  = 0.0005
BETA_PHI_RING = 0.06
K_GM          = 0.0

# DER-QNG-040 committed coupling (not a fit parameter)
LAMBDA_V      = (GAMMA_PHI - ALPHA) / (2.0 * SIGMA_REF * SIGMA_REF)
XI_PRED       = math.sqrt(BETA / (2.0 * LAMBDA_V * SIGMA_REF * SIGMA_REF))
FWHM_PRED     = 2.0 * math.sqrt(2.0 * math.log(2.0)) * XI_PRED
R_EFF_PRED    = ALPHA + 2.0 * LAMBDA_V * SIGMA_REF * SIGMA_REF  # = GAMMA_PHI

PHASE1 = 300
PHASE2 = 1500

# Stage protocols
STAGE_A_L = [40, 60, 80, 100]
STAGE_A_R = 5
STAGE_B_L = 80
STAGE_B_R = [4, 5, 6, 7]
STAGE_C_L = [60, 80, 100, 120]
STAGE_C_R = [4, 5]
STAGE_D_L = 40
STAGE_D_STEPS = 200  # linearized decay window


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def build_nb(L):
    xs = np.arange(L, dtype=np.int32)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel()
    nb = np.stack([
        ((xg-1) % L)*L*L + yg*L + zg, ((xg+1) % L)*L*L + yg*L + zg,
        xg*L*L + ((yg-1) % L)*L + zg,  xg*L*L + ((yg+1) % L)*L + zg,
        xg*L*L + yg*L + (zg-1) % L,    xg*L*L + yg*L + (zg+1) % L,
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


def build_core_mask(L, R, Wc):
    dx, dy, dz = _centered_coords(L)
    rho = np.sqrt(dx*dx + dy*dy)
    dist_curve = np.sqrt((rho - R)**2 + dz*dz)
    return cp.asarray((dist_curve <= Wc).ravel())


def wrap_gpu(a):
    a = a % (2*math.pi)
    return cp.where(a > math.pi, a - 2*math.pi, a)


def nb_mean(f, nb):
    return f[nb].mean(axis=1)


def disorder_gpu(phi, nb):
    pnb = phi[nb]
    return cp.maximum(0.0, 1.0 - cp.sqrt(cp.cos(pnb).mean(axis=1)**2 +
                                          cp.sin(pnb).mean(axis=1)**2))


def phi_wm(phi, sm, nb):
    pnb = phi[nb]; snb = sm[nb]; tw = snb.sum(axis=1)
    sx = (snb*cp.cos(pnb)).sum(axis=1); sy = (snb*cp.sin(pnb)).sum(axis=1)
    return cp.where(tw > 1e-10,
                    cp.arctan2(sy / cp.maximum(tw, 1e-10),
                               sx / cp.maximum(tw, 1e-10)),
                    phi)


def channel_h_bp(sm):
    dep_norm = cp.maximum(0.0, SIGMA_REF - sm) / SIGMA_REF
    return BETA_PHI_MIN + BETA_PHI_RING * dep_norm


# ---------------------------------------------------------------------------
# Dynamics with V(sigma_m)
# ---------------------------------------------------------------------------

def dV_dsm(sm):
    """dV/dsigma_m = LAMBDA * sm * (sm^2 - sigma_ref^2)."""
    return LAMBDA_V * sm * (sm*sm - SIGMA_REF*SIGMA_REF)


def step_phase1(sm, chi, phi, nb):
    smb = nb_mean(sm, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
                     - dV_dsm(sm), 0.0, 1.0)
    nc  = chi*(1 - CHI_DECAY) + CHI_REL*(smb - sm) + DELTA_CHI*(SIGMA_REF - sm)
    bp_eff = channel_h_bp(sm)
    pm  = phi_wm(phi, sm, nb)
    np_ = wrap_gpu(phi + bp_eff * wrap_gpu(pm - phi))
    return nsm, nc, np_


def step_phase2(sm, chi, phi, nb):
    smb = nb_mean(sm, nb)
    dis = disorder_gpu(phi, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
                     - GAMMA_PHI*dis*sm
                     - dV_dsm(sm), 0.0, 1.0)
    nc  = chi*(1 - CHI_DECAY) + CHI_REL*(smb - sm) + DELTA_CHI*(SIGMA_REF - sm)
    bp_eff = channel_h_bp(sm)
    pm  = phi_wm(phi, sm, nb)
    np_ = wrap_gpu(phi + bp_eff * wrap_gpu(pm - phi))
    return nsm, nc, np_


# ---------------------------------------------------------------------------
# Observables
# ---------------------------------------------------------------------------

def compute_radial_disorder(phi, sm, L):
    """dis(r) weighted by sigma_m on spherical shells around box center."""
    dx, dy, dz = _centered_coords(L)
    r_host = np.sqrt(dx*dx + dy*dy + dz*dz).ravel()

    nb = build_nb(L)
    pnb = phi[nb]
    dis = cp.maximum(0.0, 1.0 - cp.sqrt(cp.cos(pnb).mean(axis=1)**2
                                         + cp.sin(pnb).mean(axis=1)**2))
    dis_host = cp.asnumpy(dis * sm)  # weight by sm so halo is measured in matter sector
    del nb

    r_max = L / 2.0 - 3.0
    r_bins = np.arange(0.5, r_max, 1.0)
    profile = np.zeros_like(r_bins)
    for i, rc in enumerate(r_bins):
        mask = (r_host >= rc - 0.5) & (r_host < rc + 0.5)
        if mask.sum() > 0:
            profile[i] = dis_host[mask].mean()
    return r_bins, profile


def fit_powerlaw(r, y, r_min, r_max):
    """Fit y = A * r^(-alpha) via log-log linear regression."""
    mask = (r >= r_min) & (r <= r_max) & (y > 1e-12)
    if mask.sum() < 3:
        return {"alpha": float('nan'), "A": float('nan'), "R2": 0.0, "n": int(mask.sum())}
    logr = np.log(r[mask])
    logy = np.log(y[mask])
    A_mat = np.column_stack([np.ones_like(logr), logr])
    coef, _, _, _ = np.linalg.lstsq(A_mat, logy, rcond=None)
    logA, slope = coef
    alpha = -float(slope)
    pred = logA + slope * logr
    ss_res = float(np.sum((logy - pred)**2))
    ss_tot = float(np.sum((logy - logy.mean())**2))
    R2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {"alpha": alpha, "A": float(math.exp(logA)), "R2": R2, "n": int(mask.sum())}


def compute_core_fwhm(sm_host, L, R):
    """Measure the FWHM of the sigma_m core profile along the rho axis,
    crossing the ring at z = box center.

    Takes a 2D slice at z = L/2, rho-axis through the ring; sm_m drops from
    SIGMA_REF (vacuum) to some minimum at rho = R (core), then rises back.

    FWHM is measured from the dip profile: half-max = (sm_ref + sm_min)/2.
    Width = span of rho values where sm < half-max.
    """
    sm3d = sm_host.reshape(L, L, L)
    z_c = L // 2
    y_c = L // 2
    # Take a profile along x at fixed y=y_c, z=z_c — crosses the ring at
    # x = y_c +/- R. Use x >= y_c side.
    profile = sm3d[:, y_c, z_c]  # shape (L,)
    # Ring centers at x = y_c - R and x = y_c + R; take the right side (x > y_c)
    x_axis = np.arange(L, dtype=np.float64) - y_c  # distance from center along x
    # Focus on the range x in [-(R+5), (R+5)] around the right ring core
    # Ring core expected at x = +R.
    dip_mask = (x_axis >= 0) & (x_axis <= R + 6)
    x_dip = x_axis[dip_mask]
    p_dip = profile[dip_mask]
    if len(p_dip) < 5:
        return float('nan'), float('nan'), float('nan')
    sm_min = float(p_dip.min())
    # Baseline = value at the outer end of window (far from core)
    sm_far = float(p_dip[-1])
    half_max = 0.5 * (sm_far + sm_min)
    # FWHM = span where p_dip < half_max
    below = p_dip < half_max
    if below.sum() == 0:
        return float('nan'), sm_min, sm_far
    xs_below = x_dip[below]
    fwhm = float(xs_below.max() - xs_below.min())
    return fwhm, sm_min, sm_far


# ---------------------------------------------------------------------------
# Stage runs
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

    return sm, chi, phi


def stage_A(nb_cache):
    """Stage A: IR halo scan at fixed R=5 across L."""
    print("\n=== Stage A: IR halo L-scan, R=5 ===", flush=True)
    results = []
    for L in STAGE_A_L:
        nb = nb_cache[L]
        sm, chi, phi = run_ring(L, STAGE_A_R, nb)
        r_bins, profile = compute_radial_disorder(phi, sm, L)
        fit = fit_powerlaw(r_bins, profile, STAGE_A_R + 5.0, L/2.0 - 3.0)
        core_mask = build_core_mask(L, STAGE_A_R, 3.0)
        sm_core = float(cp.mean(sm[core_mask]))
        print(f"  L={L:>3}: alpha={fit['alpha']:.3f}  R^2={fit['R2']:.4f}  n_fit={fit['n']}  sm_core={sm_core:.4f}", flush=True)
        results.append({
            "L": L, "R": STAGE_A_R,
            "alpha": fit["alpha"], "A": fit["A"], "R2": fit["R2"], "n_fit": fit["n"],
            "sm_core": sm_core,
        })
        del sm, chi, phi
        cp.get_default_memory_pool().free_all_blocks()
    return results


def stage_B(nb_cache):
    """Stage B: R-independent core FWHM at L=80."""
    print("\n=== Stage B: core FWHM R-scan, L=80 ===", flush=True)
    results = []
    nb = nb_cache[STAGE_B_L]
    for R in STAGE_B_R:
        sm, chi, phi = run_ring(STAGE_B_L, R, nb)
        sm_host = cp.asnumpy(sm)
        fwhm, sm_min, sm_far = compute_core_fwhm(sm_host, STAGE_B_L, R)
        core_mask = build_core_mask(STAGE_B_L, R, 3.0)
        sm_core = float(cp.mean(sm[core_mask]))
        print(f"  R={R}: FWHM={fwhm:.3f} lu  sm_min={sm_min:.4f}  sm_far={sm_far:.4f}  sm_core_avg={sm_core:.4f}", flush=True)
        results.append({
            "L": STAGE_B_L, "R": R,
            "FWHM": fwhm, "sm_min": sm_min, "sm_far": sm_far, "sm_core_avg": sm_core,
        })
        del sm, chi, phi
        cp.get_default_memory_pool().free_all_blocks()
    return results


def stage_C(nb_cache):
    """Stage C: M_ring ratio L-convergence."""
    print("\n=== Stage C: M_ring ratio L-scan, R in {4,5} ===", flush=True)
    results = []
    for L in STAGE_C_L:
        nb = nb_cache[L]
        row = {"L": L}
        for R in STAGE_C_R:
            sm, chi, phi = run_ring(L, R, nb)
            M = float(L*L*L * SIGMA_REF - cp.sum(sm))
            row[f"M_R{R}"] = M
            print(f"  L={L:>3}, R={R}: M_ring = {M:.3f}", flush=True)
            del sm, chi, phi
            cp.get_default_memory_pool().free_all_blocks()
        row["ratio"] = row["M_R5"] / row["M_R4"] if row["M_R4"] > 0 else float('nan')
        print(f"  L={L:>3}: M(R=5)/M(R=4) = {row['ratio']:.4f}", flush=True)
        results.append(row)
    return results


def stage_D(nb_cache):
    """Stage D: linearized damping rate of a uniform sigma_m perturbation.

    No ring (no Channel F because phi is irrelevant); perturb sigma_m by
    s0=0.01 uniformly above sigma_ref; measure d ln|s| / dt.
    """
    print(f"\n=== Stage D: linearized damping rate, L={STAGE_D_L} ===", flush=True)
    N = STAGE_D_L**3
    s0 = 0.01
    sm  = cp.full(N, SIGMA_REF + s0, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = cp.zeros(N, dtype=cp.float64)
    nb = nb_cache[STAGE_D_L]

    times = []
    dev   = []
    for t in range(STAGE_D_STEPS):
        smb = nb_mean(sm, nb)
        # Pure sigma_m dynamics with V, no Channel F (phi=0 -> |Z|=1 -> no depletion)
        sm = cp.clip(sm + ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm) - dV_dsm(sm), 0.0, 1.0)
        # chi / phi irrelevant — keep them zero
        s_mean = float(cp.mean(sm)) - SIGMA_REF
        times.append(t)
        dev.append(abs(s_mean))
        if abs(s_mean) < 1e-8:
            break

    times = np.asarray(times, dtype=np.float64)
    dev = np.asarray(dev, dtype=np.float64)
    # Fit ln|s| = ln(s0) - r_eff * t in the exponential regime
    mask = dev > 1e-6
    if mask.sum() < 5:
        r_eff = float('nan')
        R2 = 0.0
    else:
        t_fit = times[mask]
        ln_dev = np.log(dev[mask])
        A_mat = np.column_stack([np.ones_like(t_fit), t_fit])
        coef, _, _, _ = np.linalg.lstsq(A_mat, ln_dev, rcond=None)
        r_eff = -float(coef[1])
        pred = coef[0] + coef[1] * t_fit
        ss_res = float(np.sum((ln_dev - pred)**2))
        ss_tot = float(np.sum((ln_dev - ln_dev.mean())**2))
        R2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    print(f"  measured r_eff = {r_eff:.4f}  predicted = {R_EFF_PRED:.4f}  R^2 = {R2:.4f}  n = {int(mask.sum())}", flush=True)
    return {"r_eff": r_eff, "r_eff_pred": R_EFF_PRED, "R2": R2, "n_fit": int(mask.sum())}


# ---------------------------------------------------------------------------
# Gate evaluation
# ---------------------------------------------------------------------------

def evaluate_gates(A, B, C, D):
    # Gate A: alpha(L=80, R=5) >= 3.5 and L-independence
    alpha_80 = next(r["alpha"] for r in A if r["L"] == 80)
    alphas_all = [r["alpha"] for r in A if r["L"] >= 60]
    alpha_spread = max(alphas_all) - min(alphas_all)
    gateA_pass = (alpha_80 >= 3.5) and (alpha_spread < 0.25)
    gateA_fail = (alpha_80 < 3.0)

    # Gate B: FWHM R-independence AND mean near 4.52
    fwhms = [r["FWHM"] for r in B if not math.isnan(r["FWHM"])]
    if fwhms:
        fwhm_mean = sum(fwhms) / len(fwhms)
        fwhm_spread = (max(fwhms) - min(fwhms)) / fwhm_mean if fwhm_mean > 0 else float('inf')
        fwhm_err = abs(fwhm_mean - FWHM_PRED) / FWHM_PRED
        gateB_pass = (fwhm_spread < 0.30) and (fwhm_err < 0.30)
    else:
        fwhm_mean = float('nan'); fwhm_spread = float('nan'); fwhm_err = float('nan')
        gateB_pass = False

    # Gate C: ratio L-convergence AND physical window
    ratios = [r["ratio"] for r in C if not math.isnan(r["ratio"])]
    if ratios:
        ratio_spread = max(ratios) - min(ratios)
        ratio_mean = sum(ratios) / len(ratios)
        gateC_pass = (ratio_spread < 0.08) and (1.25 <= ratio_mean <= 1.40)
    else:
        ratio_spread = float('nan'); ratio_mean = float('nan')
        gateC_pass = False

    # Gate D: |r_eff - predicted| / predicted < 0.20
    if not math.isnan(D["r_eff"]) and D["r_eff_pred"] > 0:
        r_err = abs(D["r_eff"] - D["r_eff_pred"]) / D["r_eff_pred"]
        gateD_pass = r_err < 0.20
    else:
        r_err = float('nan'); gateD_pass = False

    # Verdict
    if gateA_pass and gateB_pass and gateC_pass and gateD_pass:
        verdict = "PASS_H1"
        interp = "DER-QNG-040 saturation confirmed. All four gates pass."
    elif not gateD_pass:
        verdict = "VOID"
        interp = "Gate D (linearized damping) failed. Implementation vs analytics mismatch — debug before physics."
    elif gateA_fail:
        verdict = "FAIL_H3_STRUCTURAL"
        interp = "V(sigma_m) does not cure the halo. Mass identification halted."
    elif gateA_pass and gateD_pass and (not gateB_pass or not gateC_pass):
        verdict = "FAIL_H2_LAMBDA"
        interp = "Structural form right; saturation value wrong. Re-open as Gap 9 (Yukawa-analog)."
    else:
        verdict = "AMBIGUOUS"
        interp = "Partial pass — requires secondary test."

    return {
        "verdict": verdict, "interpretation": interp,
        "gateA": {"pass": gateA_pass, "alpha_80_R5": alpha_80, "alpha_spread": alpha_spread, "fail_clear": gateA_fail},
        "gateB": {"pass": gateB_pass, "FWHM_mean": fwhm_mean, "FWHM_pred": FWHM_PRED, "FWHM_spread_rel": fwhm_spread, "FWHM_err": fwhm_err},
        "gateC": {"pass": gateC_pass, "ratio_mean": ratio_mean, "ratio_spread": ratio_spread, "window": [1.25, 1.40]},
        "gateD": {"pass": gateD_pass, "r_eff": D["r_eff"], "r_eff_pred": D["r_eff_pred"], "r_err": r_err},
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--stages", default="ABCD", help="subset of 'ABCD' to run")
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("QNG-GPU-018: V(sigma_m) test (DER-QNG-040)")
    print(f"LAMBDA_V (committed) = {LAMBDA_V:.6f}")
    print(f"xi predicted       = {XI_PRED:.4f} lu")
    print(f"FWHM predicted     = {FWHM_PRED:.4f} lu")
    print(f"r_eff predicted    = {R_EFF_PRED:.4f}")
    print(f"v5+H params: alpha={ALPHA}, beta={BETA}, gamma_phi={GAMMA_PHI}, chi_decay={CHI_DECAY}")
    print(f"PHASE1={PHASE1}, PHASE2={PHASE2}")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB", flush=True)

    # Pre-build nb arrays for all L values (shared between stages to save GPU mem)
    all_L = sorted(set(STAGE_A_L) | {STAGE_B_L} | set(STAGE_C_L) | {STAGE_D_L})
    print(f"Pre-building neighbor lists for L in {all_L}", flush=True)
    nb_cache = {L: build_nb(L) for L in all_L}

    A_results = stage_A(nb_cache) if "A" in args.stages else []
    B_results = stage_B(nb_cache) if "B" in args.stages else []
    C_results = stage_C(nb_cache) if "C" in args.stages else []
    D_results = stage_D(nb_cache) if "D" in args.stages else {"r_eff": float('nan'), "r_eff_pred": R_EFF_PRED, "R2": 0.0, "n_fit": 0}

    gates = evaluate_gates(A_results, B_results, C_results, D_results) if all(s in args.stages for s in "ABCD") else {"verdict": "PARTIAL", "interpretation": f"stages run: {args.stages}"}

    print()
    print("="*80)
    print("GATE SUMMARY")
    print("="*80)
    if "gateA" in gates:
        print(f"Gate A (halo decay):     alpha(L=80,R=5)={gates['gateA']['alpha_80_R5']:.3f}  "
              f"spread={gates['gateA']['alpha_spread']:.3f}  "
              f"{'PASS' if gates['gateA']['pass'] else 'FAIL'}")
        print(f"Gate B (FWHM R-indep):   mean={gates['gateB']['FWHM_mean']:.3f}  pred={gates['gateB']['FWHM_pred']:.3f}  "
              f"rel_spread={gates['gateB']['FWHM_spread_rel']:.3f}  err={gates['gateB']['FWHM_err']:.3f}  "
              f"{'PASS' if gates['gateB']['pass'] else 'FAIL'}")
        print(f"Gate C (ratio converge): mean={gates['gateC']['ratio_mean']:.4f}  spread={gates['gateC']['ratio_spread']:.4f}  "
              f"window=[1.25,1.40]  {'PASS' if gates['gateC']['pass'] else 'FAIL'}")
        print(f"Gate D (damping rate):   r_eff={gates['gateD']['r_eff']:.4f}  pred={gates['gateD']['r_eff_pred']:.4f}  "
              f"err={gates['gateD']['r_err']:.3f}  {'PASS' if gates['gateD']['pass'] else 'FAIL'}")
    print()
    print(f"VERDICT: {gates['verdict']}")
    print(f"  {gates['interpretation']}")

    report = {
        "test_id": "QNG-GPU-018",
        "status": gates["verdict"],
        "parameters": {
            "ALPHA": ALPHA, "BETA": BETA, "DELTA_CHI": DELTA_CHI,
            "CHI_DECAY": CHI_DECAY, "CHI_REL": CHI_REL, "GAMMA_PHI": GAMMA_PHI,
            "BETA_PHI_MIN": BETA_PHI_MIN, "BETA_PHI_RING": BETA_PHI_RING,
            "K_GM": K_GM, "SIGMA_REF": SIGMA_REF,
            "LAMBDA_V": LAMBDA_V, "XI_PRED": XI_PRED, "FWHM_PRED": FWHM_PRED, "R_EFF_PRED": R_EFF_PRED,
            "PHASE1": PHASE1, "PHASE2": PHASE2,
        },
        "stageA_halo": A_results,
        "stageB_fwhm": B_results,
        "stageC_ratio": C_results,
        "stageD_damping": D_results,
        "gates": gates,
    }
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nWrote {out/'report.json'}")


if __name__ == "__main__":
    main()
