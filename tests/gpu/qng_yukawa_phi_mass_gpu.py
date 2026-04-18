from __future__ import annotations

"""QNG-GPU-019: Yukawa phi-mass coupling — test DER-QNG-041.

Adds V_couple = g * sigma_g * (1 - cos phi) to the v7 two-field Hamiltonian.
The goal is to break the global U(1) shift symmetry phi -> phi + c and give
phi a bulk mass m^2_phi = g * sigma_g_ref, thereby curing the Goldstone halo
that universally falsified GPU-009..018.

Pre-registration: 07_validation/prereg/QNG-GPU-019.md

Savant's falsification integrity contract:
  1. g-scan committed pre-run: {0.009, 0.03, 0.08, 0.22, 0.6}
  2. Lowest-g passing all three gates wins
  3. All of Gate A, Gate C, Gate E required for PASS
  4. g labeled Gap 9 EFT coupling; test FORM not VALUE
  5. FAIL triggers DER-QNG-042 (Anderson-Higgs alternative), not scan widening

Three stages:

  Stage A: IR halo shape (exponential vs power-law) at L=80, R=5, per g.
           Gate A: alpha(M1 fit) > 3.5 AND AIC(M2 Yukawa) - AIC(M1 power-law) < -6.
  Stage C: Yukawa self-consistency at L=80, per g.
           Single ring -> lambda_phi from halo.
           Two rings W+W- -> lambda_F from inter-ring force exp(-d/lambda_F)/d^2.
           Gate C: |lambda_phi - lambda_F| / lambda_phi < 0.20.
  Stage E: Mass ratio L-convergence at L in {60,80,100}, R in {4,5}, per g.
           Gate E: spread < 0.03 AND ratio(L=100) in [1.18, 1.45].

Runtime estimate: ~3 hours on GPU at committed scan.
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-yukawa-phi-mass-v1"

# ---------------------------------------------------------------------------
# v7 substrate parameters (frozen)
# ---------------------------------------------------------------------------
SIGMA_REF     = 0.5
ALPHA         = 0.005   # sigma drift
BETA          = 0.35    # sigma relational smoothing
DELTA_CHI     = 0.20
CHI_DECAY     = 0.020
CHI_REL       = 0.35
GAMMA_PHI     = 0.10    # Channel F strength
BETA_PHI_MIN  = 0.0005  # phi bulk smoothing
BETA_PHI_RING = 0.06    # phi smoothing boost in ring core
K_GM          = 0.0     # gravity off (not testing gravity here)

# Yukawa channel gradient-flow rate (DER-QNG-041 §5.1).
# Natural choice = 1.0 (pure gradient descent per step).
# Stability: eta_phi * g * SIGMA_REF < 1 => g < 2. All scan values safe.
# BUG FIX 2026-04-18: earlier version accidentally used bp_eff (~0.0005 in bulk,
# ~0.06 in core) as eta, which suppressed the Yukawa term to noise level in the
# bulk where it is required. Restored to fixed eta_phi = 1.0.
ETA_PHI_YUKAWA = 1.0

# ---------------------------------------------------------------------------
# Pre-registered g scan (DER-QNG-041, labeled Gap 9 EFT)
# ---------------------------------------------------------------------------
G_SCAN = [0.009, 0.03, 0.08, 0.22, 0.6]

# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------
PHASE1 = 300
PHASE2 = 1500

STAGE_A_L = 80
STAGE_A_R = 5

STAGE_C_L = 80
STAGE_C_R_SINGLE = 5
STAGE_C_SEPARATIONS = [6, 8, 10, 12, 14, 16, 18]

STAGE_E_L = [60, 80, 100]
STAGE_E_R = [4, 5]


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def build_nb(L):
    xs = np.arange(L, dtype=np.int32)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel()
    nb = np.stack([
        ((xg - 1) % L) * L * L + yg * L + zg, ((xg + 1) % L) * L * L + yg * L + zg,
        xg * L * L + ((yg - 1) % L) * L + zg, xg * L * L + ((yg + 1) % L) * L + zg,
        xg * L * L + yg * L + (zg - 1) % L,  xg * L * L + yg * L + (zg + 1) % L,
    ], axis=1).astype(np.int32)
    return cp.asarray(nb)


def _centered_coords(L, cx=None, cy=None, cz=None):
    if cx is None: cx = L / 2.0
    if cy is None: cy = L / 2.0
    if cz is None: cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg - cx; dy = yg - cy; dz = zg - cz
    for d in (dx, dy, dz):
        d[:] = np.where(d >  L / 2, d - L, d)
        d[:] = np.where(d < -L / 2, d + L, d)
    return dx, dy, dz


def build_phi_single_ring(L, R):
    dx, dy, dz = _centered_coords(L)
    rho = np.sqrt(dx * dx + dy * dy)
    return cp.asarray(np.arctan2(dz, rho - R).ravel())


def build_phi_two_rings(L, R, d):
    """Two coaxial rings W+ (at x=cx-d/2) and W- (at x=cx+d/2), both radius R in yz plane.

    W+ has phi = atan2(dz, rho - R); W- has the OPPOSITE winding phi = -atan2(dz, rho - R).
    The rings are separated along the x-axis by distance d.
    """
    cx = L / 2.0
    shift = d / 2.0
    # Ring 1 at x = cx - shift
    dx1, dy1, dz1 = _centered_coords(L, cx=cx - shift)
    rho1 = np.sqrt(dy1 * dy1 + dz1 * dz1)
    phi1 = np.arctan2(dx1, rho1 - R)  # winding in x-rho plane, axis = y-z average

    # Ring 2 at x = cx + shift, opposite winding
    dx2, dy2, dz2 = _centered_coords(L, cx=cx + shift)
    rho2 = np.sqrt(dy2 * dy2 + dz2 * dz2)
    phi2 = -np.arctan2(dx2, rho2 - R)  # opposite winding

    # Combine: use the closer ring's phase (mask by which is closer)
    # Actually better: sum the phase windings (superposition of line vortices)
    phi = phi1 + phi2
    return cp.asarray(phi.ravel())


def build_core_mask(L, R, Wc):
    dx, dy, dz = _centered_coords(L)
    rho = np.sqrt(dx * dx + dy * dy)
    dist_curve = np.sqrt((rho - R) ** 2 + dz * dz)
    return cp.asarray((dist_curve <= Wc).ravel())


def wrap_gpu(a):
    a = a % (2 * math.pi)
    return cp.where(a > math.pi, a - 2 * math.pi, a)


def nb_mean(f, nb):
    return f[nb].mean(axis=1)


def disorder_gpu(phi, nb):
    pnb = phi[nb]
    return cp.maximum(0.0, 1.0 - cp.sqrt(cp.cos(pnb).mean(axis=1) ** 2 +
                                          cp.sin(pnb).mean(axis=1) ** 2))


def phi_wm(phi, sm, nb):
    pnb = phi[nb]; snb = sm[nb]; tw = snb.sum(axis=1)
    sx = (snb * cp.cos(pnb)).sum(axis=1); sy = (snb * cp.sin(pnb)).sum(axis=1)
    return cp.where(tw > 1e-10,
                    cp.arctan2(sy / cp.maximum(tw, 1e-10),
                               sx / cp.maximum(tw, 1e-10)),
                    phi)


def channel_h_bp(sm):
    dep_norm = cp.maximum(0.0, SIGMA_REF - sm) / SIGMA_REF
    return BETA_PHI_MIN + BETA_PHI_RING * dep_norm


# ---------------------------------------------------------------------------
# Dynamics with V_couple = g * sigma_g * (1 - cos phi)
# ---------------------------------------------------------------------------

def step_phase1(sg, sm, chi, phi, nb, g):
    """Phase 1: no Channel F (phi seed), NO V_couple yet (let ring form)."""
    sgb = nb_mean(sg, nb)
    smb = nb_mean(sm, nb)
    nsg = cp.clip(sg + ALPHA * (SIGMA_REF - sg) + BETA * (sgb - sg), 0.0, 1.0)
    nsm = cp.clip(sm + ALPHA * (SIGMA_REF - sm) + BETA * (smb - sm), 0.0, 1.0)
    nc  = chi * (1 - CHI_DECAY) + CHI_REL * (sgb - sg) + DELTA_CHI * (SIGMA_REF - sg)
    bp_eff = channel_h_bp(sm)
    pm  = phi_wm(phi, sm, nb)
    np_ = wrap_gpu(phi + bp_eff * wrap_gpu(pm - phi))
    return nsg, nsm, nc, np_


def step_phase2(sg, sm, chi, phi, nb, g):
    """Phase 2: Channel F ON, V_couple ON at committed g.

    V_couple = g * sg * (1 - cos phi) contributes:
      dV / dphi   = g * sg * sin phi           (phi acquires mass via this)
      dV / dsg    = g * (1 - cos phi)          (sg feels Yukawa back-reaction)
    """
    sgb = nb_mean(sg, nb)
    smb = nb_mean(sm, nb)
    dis = disorder_gpu(phi, nb)

    # sigma_g: relational smoothing + Yukawa back-reaction from V_couple
    dsg_yukawa = -g * (1.0 - cp.cos(phi))
    nsg = cp.clip(sg + ALPHA * (SIGMA_REF - sg) + BETA * (sgb - sg) + dsg_yukawa,
                  0.0, 1.0)

    # sigma_m: Channel F depletion (as usual)
    nsm = cp.clip(sm + ALPHA * (SIGMA_REF - sm) + BETA * (smb - sm)
                  - GAMMA_PHI * dis * sm, 0.0, 1.0)

    # chi: unchanged (depends on sg only)
    nc  = chi * (1 - CHI_DECAY) + CHI_REL * (sgb - sg) + DELTA_CHI * (SIGMA_REF - sg)

    # phi: relational smoothing + Yukawa mass term
    bp_eff = channel_h_bp(sm)
    pm  = phi_wm(phi, sm, nb)
    dphi_rel = bp_eff * wrap_gpu(pm - phi)
    # Yukawa term uses its own gradient-flow rate ETA_PHI_YUKAWA (NOT bp_eff).
    # bp_eff is the relational-smoothing rate; Yukawa is separate physics
    # (equation of motion d phi/dt = -dV/dphi with eta = 1.0).
    dphi_yukawa = -ETA_PHI_YUKAWA * g * sg * cp.sin(phi)
    np_ = wrap_gpu(phi + dphi_rel + dphi_yukawa)

    return nsg, nsm, nc, np_


# ---------------------------------------------------------------------------
# Observables
# ---------------------------------------------------------------------------

def compute_radial_disorder(phi, sm, L):
    """dis(r) weighted by sigma_m on spherical shells around box center."""
    dx, dy, dz = _centered_coords(L)
    r_host = np.sqrt(dx * dx + dy * dy + dz * dz).ravel()

    nb = build_nb(L)
    pnb = phi[nb]
    dis = cp.maximum(0.0, 1.0 - cp.sqrt(cp.cos(pnb).mean(axis=1) ** 2
                                         + cp.sin(pnb).mean(axis=1) ** 2))
    dis_host = cp.asnumpy(dis * sm)
    del nb

    r_max = L / 2.0 - 3.0
    r_bins = np.arange(0.5, r_max, 1.0)
    profile = np.zeros_like(r_bins)
    counts  = np.zeros_like(r_bins)
    for i, rc in enumerate(r_bins):
        mask = (r_host >= rc - 0.5) & (r_host < rc + 0.5)
        if mask.sum() > 0:
            profile[i] = dis_host[mask].mean()
            counts[i]  = int(mask.sum())
    return r_bins, profile, counts


def fit_powerlaw(r, y, r_min, r_max):
    mask = (r >= r_min) & (r <= r_max) & (y > 1e-12)
    if mask.sum() < 4:
        return {"alpha": float('nan'), "A": float('nan'), "R2": 0.0, "n": int(mask.sum()),
                "ss_res_log": float('nan')}
    logr = np.log(r[mask]); logy = np.log(y[mask])
    A_mat = np.column_stack([np.ones_like(logr), logr])
    coef, _, _, _ = np.linalg.lstsq(A_mat, logy, rcond=None)
    logA, slope = coef
    alpha = -float(slope)
    pred = logA + slope * logr
    ss_res = float(np.sum((logy - pred) ** 2))
    ss_tot = float(np.sum((logy - logy.mean()) ** 2))
    R2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {"alpha": alpha, "A": float(math.exp(logA)), "R2": R2, "n": int(mask.sum()),
            "ss_res_log": ss_res}


def fit_yukawa_halo(r, y, r_min, r_max):
    """Fit y = A * exp(-r / lambda_phi) / r by linearizing:
       ln(y * r) = ln A - r / lambda_phi.
    """
    mask = (r >= r_min) & (r <= r_max) & (y > 1e-12)
    if mask.sum() < 4:
        return {"lambda_phi": float('nan'), "A": float('nan'), "R2": 0.0,
                "n": int(mask.sum()), "ss_res_log": float('nan')}
    r_m = r[mask]; y_m = y[mask]
    ln_yr = np.log(y_m * r_m)
    A_mat = np.column_stack([np.ones_like(r_m), r_m])
    coef, _, _, _ = np.linalg.lstsq(A_mat, ln_yr, rcond=None)
    logA, slope = coef
    lambda_phi = -1.0 / float(slope) if slope != 0 else float('inf')
    pred = logA + slope * r_m
    ss_res = float(np.sum((ln_yr - pred) ** 2))
    # For AIC comparison with power-law, compare residuals of ln y directly
    # (not ln(y*r)). Convert: ln y = ln(y*r) - ln r
    pred_lny = pred - np.log(r_m)
    ln_y_obs = np.log(y_m)
    ss_res_lny = float(np.sum((ln_y_obs - pred_lny) ** 2))
    ss_tot = float(np.sum((ln_y_obs - ln_y_obs.mean()) ** 2))
    R2 = 1.0 - ss_res_lny / ss_tot if ss_tot > 0 else 0.0
    return {"lambda_phi": lambda_phi, "A": float(math.exp(logA)), "R2": R2,
            "n": int(mask.sum()), "ss_res_log": ss_res_lny}


def compute_aic(ss_res, n, k):
    """Small-sample AIC (AICc) for Gaussian residuals:
       AICc = n * ln(ss_res/n) + 2*k + 2*k*(k+1)/(n-k-1)
    """
    if n - k - 1 <= 0 or ss_res <= 0:
        return float('inf')
    return n * math.log(ss_res / n) + 2 * k + 2 * k * (k + 1) / (n - k - 1)


def compute_inter_ring_force(L, R, d, g, nb):
    """Two rings W+ W- separated by d along x. After equilibration,
    compute the sigma_m asymmetry gradient along x which gives the
    inter-ring pull (proxy for force).

    Returns the mean |d(sm)/dx| in the gap region between the rings.
    """
    N = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi_two_rings(L, R, d)

    for _ in range(PHASE1):
        sg, sm, chi, phi = step_phase1(sg, sm, chi, phi, nb, g)
    for _ in range(PHASE2):
        sg, sm, chi, phi = step_phase2(sg, sm, chi, phi, nb, g)

    sm_host = cp.asnumpy(sm).reshape(L, L, L)
    cx = L // 2
    cy = L // 2
    cz = L // 2
    # Take the ring-axis line profile along x
    # Gap region = x in [cx - d/2 + 1, cx + d/2 - 1]
    x_lo = int(cx - d / 2 + 1)
    x_hi = int(cx + d / 2 - 1)
    if x_hi <= x_lo:
        return {"F_proxy": 0.0, "d": d, "valid": False}
    line = sm_host[x_lo:x_hi + 1, cy, cz]  # sigma_m along axis in the gap
    # Force proxy: max |d sigma_m / dx| in the gap.
    dsm = np.diff(line)
    F_proxy = float(np.max(np.abs(dsm))) if len(dsm) > 0 else 0.0
    # Sigma_m depression in gap (integrated deficit)
    sm_deficit = float(np.sum(SIGMA_REF - line))

    del sg, sm, chi, phi
    cp.get_default_memory_pool().free_all_blocks()

    return {"F_proxy": F_proxy, "sm_deficit": sm_deficit, "d": d, "valid": True}


# ---------------------------------------------------------------------------
# Stage runs (per g)
# ---------------------------------------------------------------------------

def run_single_ring(L, R, g, nb):
    N = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi_single_ring(L, R)

    for _ in range(PHASE1):
        sg, sm, chi, phi = step_phase1(sg, sm, chi, phi, nb, g)
    for _ in range(PHASE2):
        sg, sm, chi, phi = step_phase2(sg, sm, chi, phi, nb, g)

    return sg, sm, chi, phi


def stage_A_for_g(g, nb_cache):
    """Stage A: halo fit at L=80, R=5."""
    L = STAGE_A_L; R = STAGE_A_R
    nb = nb_cache[L]
    sg, sm, chi, phi = run_single_ring(L, R, g, nb)
    r_bins, profile, counts = compute_radial_disorder(phi, sm, L)
    r_min = R + 2.0
    r_max = L / 2.0 - 3.0
    pl = fit_powerlaw(r_bins, profile, r_min, r_max)
    yk = fit_yukawa_halo(r_bins, profile, r_min, r_max)
    aic_pl = compute_aic(pl["ss_res_log"], pl["n"], 2)
    aic_yk = compute_aic(yk["ss_res_log"], yk["n"], 2)
    dAIC = aic_yk - aic_pl
    core_mask = build_core_mask(L, R, 3.0)
    sm_core = float(cp.mean(sm[core_mask]))
    sg_core = float(cp.mean(sg[core_mask]))

    profile_log = []
    for rc, pr, ct in zip(r_bins, profile, counts):
        profile_log.append({"r": float(rc), "D": float(pr), "n": int(ct)})

    del sg, sm, chi, phi
    cp.get_default_memory_pool().free_all_blocks()

    return {
        "g": g, "L": L, "R": R,
        "powerlaw": pl,
        "yukawa": yk,
        "aic_pl": aic_pl, "aic_yk": aic_yk, "dAIC_yk_minus_pl": dAIC,
        "sm_core": sm_core, "sg_core": sg_core,
        "profile": profile_log,
    }


def stage_C_for_g(g, nb_cache, lambda_phi_halo):
    """Stage C: inter-ring force fit at L=80, R=5, d in SEPARATIONS."""
    L = STAGE_C_L; R = STAGE_C_R_SINGLE
    nb = nb_cache[L]
    force_pts = []
    for d in STAGE_C_SEPARATIONS:
        res = compute_inter_ring_force(L, R, d, g, nb)
        force_pts.append(res)
        print(f"    g={g:.3f} d={d:>3}: F_proxy={res['F_proxy']:.5f}  sm_deficit={res.get('sm_deficit', 0):.3f}",
              flush=True)

    # Fit F(d) = A * exp(-d/lambda_F) / d^2  =>  ln(F*d^2) = lnA - d/lambda_F
    ds = np.asarray([p["d"] for p in force_pts], dtype=np.float64)
    Fs = np.asarray([p["F_proxy"] for p in force_pts], dtype=np.float64)
    mask = (Fs > 1e-8)
    lambda_F = float('nan'); R2 = 0.0
    if mask.sum() >= 4:
        d_m = ds[mask]; F_m = Fs[mask]
        ln_Fd2 = np.log(F_m * d_m * d_m)
        A_mat = np.column_stack([np.ones_like(d_m), d_m])
        coef, _, _, _ = np.linalg.lstsq(A_mat, ln_Fd2, rcond=None)
        logA, slope = coef
        lambda_F = -1.0 / float(slope) if slope != 0 else float('inf')
        pred = logA + slope * d_m
        ss_res = float(np.sum((ln_Fd2 - pred) ** 2))
        ss_tot = float(np.sum((ln_Fd2 - ln_Fd2.mean()) ** 2))
        R2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    if not math.isfinite(lambda_phi_halo) or lambda_phi_halo <= 0:
        consistency = float('nan')
    else:
        consistency = abs(lambda_F - lambda_phi_halo) / lambda_phi_halo

    return {
        "g": g,
        "force_points": force_pts,
        "lambda_F": lambda_F,
        "R2_F": R2,
        "lambda_phi_halo": lambda_phi_halo,
        "consistency_err": consistency,
    }


def stage_E_for_g(g, nb_cache):
    """Stage E: mass ratio L-convergence."""
    results = []
    for L in STAGE_E_L:
        nb = nb_cache[L]
        row = {"g": g, "L": L}
        for R in STAGE_E_R:
            sg, sm, chi, phi = run_single_ring(L, R, g, nb)
            M = float(L * L * L * SIGMA_REF - cp.sum(sm))
            row[f"M_R{R}"] = M
            print(f"    g={g:.3f} L={L:>3} R={R}: M_ring = {M:.3f}", flush=True)
            del sg, sm, chi, phi
            cp.get_default_memory_pool().free_all_blocks()
        row["ratio"] = row["M_R5"] / row["M_R4"] if row["M_R4"] > 0 else float('nan')
        results.append(row)
    ratios = [r["ratio"] for r in results]
    spread = abs(ratios[-1] - ratios[0]) / ratios[1] if ratios[1] > 0 else float('inf')
    return {
        "g": g,
        "rows": results,
        "ratios": ratios,
        "spread": spread,
        "ratio_L100": ratios[-1],
    }


# ---------------------------------------------------------------------------
# Gate evaluation
# ---------------------------------------------------------------------------

def evaluate_gates_single_g(A_res, C_res, E_res):
    alpha_pl = A_res["powerlaw"]["alpha"]
    dAIC = A_res["dAIC_yk_minus_pl"]
    gateA_pass = (alpha_pl > 3.5) and (dAIC < -6.0)
    gateA_fail_clear = (alpha_pl < 3.0)

    consistency = C_res["consistency_err"]
    gateC_pass = math.isfinite(consistency) and (consistency < 0.20)

    spread = E_res["spread"]
    ratio_final = E_res["ratio_L100"]
    gateE_pass = (spread < 0.03) and (1.18 <= ratio_final <= 1.45)

    all_pass = gateA_pass and gateC_pass and gateE_pass

    return {
        "g": A_res["g"],
        "gateA": {"pass": bool(gateA_pass), "alpha_pl": alpha_pl, "dAIC": dAIC,
                   "fail_clear": bool(gateA_fail_clear)},
        "gateC": {"pass": bool(gateC_pass), "consistency_err": consistency,
                   "lambda_phi": A_res["yukawa"]["lambda_phi"],
                   "lambda_F": C_res["lambda_F"]},
        "gateE": {"pass": bool(gateE_pass), "spread": spread, "ratio_final": ratio_final},
        "all_pass": bool(all_pass),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    out_dir = DEFAULT_OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    print("QNG-GPU-019: Yukawa phi-mass coupling test (DER-QNG-041)", flush=True)
    print(f"g-scan (pre-committed): {G_SCAN}", flush=True)
    print(f"v7 params: alpha={ALPHA}, beta={BETA}, gamma_phi={GAMMA_PHI}, chi_decay={CHI_DECAY}", flush=True)
    print(f"PHASE1={PHASE1}, PHASE2={PHASE2}", flush=True)
    try:
        mem_free, mem_total = cp.cuda.runtime.memGetInfo()
        print(f"\nGPU: free mem = {mem_free / 1e9:.2f} GB / {mem_total / 1e9:.2f} GB total", flush=True)
    except Exception as exc:
        print(f"\nGPU info probe failed: {exc}", flush=True)

    Ls_needed = sorted(set([STAGE_A_L, STAGE_C_L] + STAGE_E_L))
    print(f"\nPre-building neighbor lists for L in {Ls_needed}", flush=True)
    nb_cache = {L: build_nb(L) for L in Ls_needed}

    per_g_report = []

    for g in G_SCAN:
        print(f"\n{'='*78}\n  SCAN POINT: g = {g}\n{'='*78}", flush=True)

        print(f"\n--- Stage A (halo) @ g={g} ---", flush=True)
        A_res = stage_A_for_g(g, nb_cache)
        print(f"    alpha_PL = {A_res['powerlaw']['alpha']:.3f}  R2_PL = {A_res['powerlaw']['R2']:.4f}",
              flush=True)
        print(f"    lambda_phi = {A_res['yukawa']['lambda_phi']:.3f}  R2_YK = {A_res['yukawa']['R2']:.4f}",
              flush=True)
        print(f"    dAIC (Yukawa - PowerLaw) = {A_res['dAIC_yk_minus_pl']:.3f}  "
              f"sm_core = {A_res['sm_core']:.4f}", flush=True)

        print(f"\n--- Stage C (force self-consistency) @ g={g} ---", flush=True)
        lambda_halo = A_res["yukawa"]["lambda_phi"]
        C_res = stage_C_for_g(g, nb_cache, lambda_halo)
        print(f"    lambda_F = {C_res['lambda_F']:.3f}  consistency_err = {C_res['consistency_err']:.3f}",
              flush=True)

        print(f"\n--- Stage E (mass ratio L-convergence) @ g={g} ---", flush=True)
        E_res = stage_E_for_g(g, nb_cache)
        print(f"    ratios = {E_res['ratios']}  spread = {E_res['spread']:.4f}", flush=True)

        gates = evaluate_gates_single_g(A_res, C_res, E_res)
        print(f"\n    Gate A: {'PASS' if gates['gateA']['pass'] else 'FAIL'}  "
              f"alpha_PL={gates['gateA']['alpha_pl']:.3f}  dAIC={gates['gateA']['dAIC']:.3f}", flush=True)
        print(f"    Gate C: {'PASS' if gates['gateC']['pass'] else 'FAIL'}  "
              f"err={gates['gateC']['consistency_err']:.3f}", flush=True)
        print(f"    Gate E: {'PASS' if gates['gateE']['pass'] else 'FAIL'}  "
              f"spread={gates['gateE']['spread']:.4f}  "
              f"ratio_L100={gates['gateE']['ratio_final']:.4f}", flush=True)
        print(f"    Overall at g={g}: {'ALL PASS' if gates['all_pass'] else 'FAIL'}", flush=True)

        per_g_report.append({"A": A_res, "C": C_res, "E": E_res, "gates": gates})

    print(f"\n{'='*78}\nFINAL VERDICT\n{'='*78}", flush=True)
    passing_gs = [r["gates"]["g"] for r in per_g_report if r["gates"]["all_pass"]]
    if len(passing_gs) > 0:
        g_star = min(passing_gs)
        verdict = "PASS_H1"
        verdict_text = f"DER-QNG-041 form confirmed. Lowest g passing all gates: g* = {g_star}."
    else:
        any_A_pass = any(r["gates"]["gateA"]["pass"] for r in per_g_report)
        if any_A_pass:
            verdict = "FAIL_H2_PARTIAL"
            verdict_text = ("Gate A passed at some g, but Gate C or E failed at all g. "
                            "Form correct but incomplete; advance to DER-QNG-042 augmentation.")
        else:
            verdict = "FAIL_H3_STRUCTURAL"
            verdict_text = "Gate A failed at all g. Yukawa form structurally wrong. Advance to DER-QNG-042."
        g_star = None
    print(f"  VERDICT: {verdict}", flush=True)
    print(f"  {verdict_text}", flush=True)

    report = {
        "test_id": "QNG-GPU-019",
        "status": verdict,
        "verdict_text": verdict_text,
        "g_star": g_star,
        "parameters": {
            "ALPHA": ALPHA, "BETA": BETA, "DELTA_CHI": DELTA_CHI, "CHI_DECAY": CHI_DECAY,
            "CHI_REL": CHI_REL, "GAMMA_PHI": GAMMA_PHI,
            "BETA_PHI_MIN": BETA_PHI_MIN, "BETA_PHI_RING": BETA_PHI_RING,
            "K_GM": K_GM, "SIGMA_REF": SIGMA_REF,
            "G_SCAN": G_SCAN, "PHASE1": PHASE1, "PHASE2": PHASE2,
        },
        "per_g": per_g_report,
    }

    out_path = out_dir / "report.json"
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nWrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
