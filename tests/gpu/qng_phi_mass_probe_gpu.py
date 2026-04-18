from __future__ import annotations

"""Phi effective mass probe (QNG-GPU-012, GPU).

Einstein-mind suggestion: check whether Channel F back-reaction generates
effective m_phi at mean-field level.

If phi has an effective mass m_phi_eff from Channel F feedback, then the
disorder profile should decay EXPONENTIALLY from the ring core:
  disorder(r) ~ exp(-r / xi)   where xi = 1/m_phi_eff

If phi is truly massless (Goldstone), disorder decays as a POWER LAW:
  disorder(r) ~ 1/r^2   (dipole falloff from vortex ring)

Method:
  1. Run v7 protocol (GAMMA_PHI=0.10, BETA_PHI=0.02) to form ring at R=5, L=80.
  2. After Phase 2, measure mean disorder(phi) in radial shells r=1..35 from ring center.
  3. Fit both exponential and power-law to the bulk tail (r > R+5).
  4. If exponential fits better AND xi ~ lambda_screen (8.37 lu) -> self-generated gap.
     If power law fits better -> phi is gapless, L=20 is a coincidence.

Uses L=80 for large bulk region to distinguish the decay modes.
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-phi-mass-probe-v1"

SIGMA_REF = 0.5
ALPHA     = 0.005
BETA      = 0.35
BETA_PHI  = 0.02
DELTA_CHI = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
GAMMA_PHI = 0.10

PHASE1 = 300
PHASE2 = 1500

L      = 80
R_RING = 5

LAMBDA_SCREEN = math.sqrt(BETA / ALPHA)  # ~8.37 lu


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


def build_phi_ring(L, R):
    cx = cy = cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg-cx; dy = yg-cy; dz = zg-cz
    for d in [dx, dy, dz]:
        d[:] = np.where(d >  L/2, d-L, d)
        d[:] = np.where(d < -L/2, d+L, d)
    rho = np.sqrt(dx*dx + dy*dy)
    return cp.asarray(np.arctan2(dz, rho-R).ravel())


def build_r_shells(L, n_shells=38):
    """Spherical distance from center, binned into shells of width 1."""
    cx = cy = cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg-cx; dy = yg-cy; dz = zg-cz
    for d in [dx, dy, dz]:
        d[:] = np.where(d >  L/2, d-L, d)
        d[:] = np.where(d < -L/2, d+L, d)
    r = np.sqrt(dx*dx + dy*dy + dz*dz).ravel()
    shells = []
    for s in range(n_shells):
        mask = cp.asarray((r >= s) & (r < s+1))
        shells.append(mask)
    return shells, np.arange(n_shells) + 0.5  # shell centers


def wrap_gpu(a):
    a = a % (2*math.pi)
    return cp.where(a > math.pi, a - 2*math.pi, a)

def nb_mean(f, nb): return f[nb].mean(axis=1)

def disorder(phi, nb):
    pnb = phi[nb]
    return cp.maximum(0.0, 1.0 - cp.sqrt(cp.cos(pnb).mean(axis=1)**2 +
                                          cp.sin(pnb).mean(axis=1)**2))

def phi_wm(phi, sm, nb):
    pnb = phi[nb]; snb = sm[nb]; tw = snb.sum(axis=1)
    sx = (snb*cp.cos(pnb)).sum(axis=1); sy = (snb*cp.sin(pnb)).sum(axis=1)
    return cp.where(tw>1e-10, cp.arctan2(sy/cp.maximum(tw,1e-10),
                                          sx/cp.maximum(tw,1e-10)), phi)

def step1(sm, chi, phi, nb):
    smb = nb_mean(sm, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm), 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    np_ = wrap_gpu(phi + BETA_PHI*wrap_gpu(phi_wm(phi,sm,nb)-phi))
    return nsm, nc, np_

def step2(sm, chi, phi, nb):
    smb = nb_mean(sm, nb)
    dis = disorder(phi, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm)
                     - GAMMA_PHI*dis*sm, 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    np_ = wrap_gpu(phi + BETA_PHI*wrap_gpu(phi_wm(phi,sm,nb)-phi))
    return nsm, nc, np_


def measure_profile(phi, sm, nb, shells):
    """Mean disorder and depletion in each radial shell."""
    dis_field = disorder(phi, nb)
    dep_field = cp.maximum(0.0, SIGMA_REF - sm)
    profile = []
    for mask in shells:
        n = float(cp.sum(mask))
        if n < 1:
            profile.append((0.0, 0.0))
            continue
        d = float(cp.sum(dis_field * mask)) / n
        s = float(cp.sum(dep_field * mask)) / n
        profile.append((d, s))
    return profile


def fit_exponential(r_vals, dis_vals):
    """Fit disorder(r) = A * exp(-r / xi)."""
    try:
        def model(r, A, xi): return A * np.exp(-r / xi)
        p0 = [dis_vals[0], LAMBDA_SCREEN]
        popt, _ = curve_fit(model, r_vals, dis_vals, p0=p0,
                            bounds=([0, 0.1], [1, 100]), maxfev=5000)
        A, xi = popt
        residuals = dis_vals - model(r_vals, A, xi)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((dis_vals - dis_vals.mean())**2)
        r2 = 1 - ss_res / max(ss_tot, 1e-12)
        return A, xi, r2
    except Exception:
        return None, None, None


def fit_powerlaw(r_vals, dis_vals):
    """Fit disorder(r) = A * r^(-alpha)."""
    try:
        log_r = np.log(r_vals)
        log_d = np.log(np.maximum(dis_vals, 1e-10))
        # Linear fit in log-log space
        coeffs = np.polyfit(log_r, log_d, 1)
        alpha_fit = -coeffs[0]
        A_fit = math.exp(coeffs[1])
        pred = A_fit * r_vals**(-alpha_fit)
        residuals = dis_vals - pred
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((dis_vals - dis_vals.mean())**2)
        r2 = 1 - ss_res / max(ss_tot, 1e-12)
        return A_fit, alpha_fit, r2
    except Exception:
        return None, None, None


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("Phi effective mass probe (QNG-GPU-012)")
    print(f"L={L}, R={R_RING}, GAMMA_PHI={GAMMA_PHI}, BETA_PHI={BETA_PHI}")
    print(f"lambda_screen = {LAMBDA_SCREEN:.2f} lu")
    print(f"Question: does disorder(r) decay as exp(-r/xi) [massive] or 1/r^2 [massless]?")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    nb = build_nb(L)
    shells, r_centers = build_r_shells(L, n_shells=L//2)

    N = L*L*L
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi_ring(L, R_RING)

    print("Running Phase 1...", flush=True)
    for _ in range(PHASE1): sm, chi, phi = step1(sm, chi, phi, nb)

    print("Running Phase 2...", flush=True)
    for _ in range(PHASE2): sm, chi, phi = step2(sm, chi, phi, nb)

    print("Measuring radial profile...", flush=True)
    profile = measure_profile(phi, sm, nb, shells)

    print()
    print("="*70)
    print("RADIAL DISORDER PROFILE")
    print("="*70)
    print(f"{'r':>5}  {'disorder':>10}  {'depletion':>10}  {'log(dis)':>10}")
    print("-"*50)
    for i, (r, (dis, dep)) in enumerate(zip(r_centers, profile)):
        log_dis = math.log(max(dis, 1e-10))
        marker = " <-- ring core" if abs(r - R_RING) < 2 else ""
        print(f"{r:>5.1f}  {dis:>10.6f}  {dep:>10.6f}  {log_dis:>10.4f}{marker}")

    # Fit in the bulk region (r > R_RING + 5, r < L/2 - 2)
    r_min_fit = R_RING + 5
    r_max_fit = L//2 - 2
    mask_fit = (r_centers > r_min_fit) & (r_centers < r_max_fit)
    r_fit  = r_centers[mask_fit]
    dis_fit = np.array([profile[i][0] for i in range(len(r_centers))])[mask_fit]
    dis_fit = np.maximum(dis_fit, 1e-10)

    print()
    print(f"Fitting bulk region: r in [{r_min_fit:.0f}, {r_max_fit:.0f}] lu")
    print(f"Number of points in fit: {len(r_fit)}")

    A_exp, xi_exp, r2_exp = fit_exponential(r_fit, dis_fit)
    A_pow, alpha_pow, r2_pow = fit_powerlaw(r_fit, dis_fit)

    print()
    print("FIT RESULTS:")
    if A_exp is not None:
        print(f"  Exponential:  A={A_exp:.6f}  xi={xi_exp:.3f} lu  R^2={r2_exp:.4f}")
        print(f"                xi vs lambda_screen: xi/lambda = {xi_exp/LAMBDA_SCREEN:.3f}")
    else:
        print("  Exponential: fit failed")

    if A_pow is not None:
        print(f"  Power law:    A={A_pow:.6f}  alpha={alpha_pow:.3f}  R^2={r2_pow:.4f}")
        print(f"                (vortex ring: expected alpha ~ 2-3)")
    else:
        print("  Power law: fit failed")

    # Verdict
    print()
    if r2_exp is None and r2_pow is None:
        verdict = "FIT_FAILED"
        detail  = "both fits failed"
        m_phi_eff = None
    elif r2_exp is not None and r2_pow is not None:
        if r2_exp > r2_pow + 0.05:
            verdict = "MASSIVE_PHI"
            m_phi_eff = 1.0 / xi_exp
            detail  = (f"exponential decay wins (R^2_exp={r2_exp:.3f} > R^2_pow={r2_pow:.3f}), "
                       f"xi={xi_exp:.2f} lu, m_phi_eff={m_phi_eff:.4f} lu^-1, "
                       f"xi/lambda={xi_exp/LAMBDA_SCREEN:.2f}")
        elif r2_pow > r2_exp + 0.05:
            verdict = "MASSLESS_PHI"
            m_phi_eff = None
            detail  = (f"power law wins (R^2_pow={r2_pow:.3f} > R^2_exp={r2_exp:.3f}), "
                       f"alpha={alpha_pow:.2f} (expected ~2 for vortex ring)")
        else:
            verdict = "AMBIGUOUS"
            m_phi_eff = None
            detail  = f"fits comparable: R^2_exp={r2_exp:.3f}  R^2_pow={r2_pow:.3f}"
    else:
        verdict = "PARTIAL_FIT"
        m_phi_eff = None
        detail = "only one fit succeeded"

    print(f"VERDICT: {verdict}")
    print(f"  {detail}")

    if verdict == "MASSIVE_PHI":
        print()
        print("  => Channel F DOES generate effective m_phi")
        print(f"  => phi is confined within xi={xi_exp:.2f} lu of ring")
        print(f"  => L=20 ≈ {20/xi_exp:.1f}*xi is the natural canonical scale")
        if abs(xi_exp - LAMBDA_SCREEN) < 2:
            print(f"  => xi ~ lambda_screen ({LAMBDA_SCREEN:.2f}) -- theory self-consistent!")
        else:
            print(f"  => xi != lambda_screen (xi={xi_exp:.2f}, lambda={LAMBDA_SCREEN:.2f})")
    elif verdict == "MASSLESS_PHI":
        print()
        print("  => phi is gapless, no self-generated mass")
        print("  => L=20 ratio agreement is a coincidence (halo crossing)")
        print("  => Fix requires explicit V(phi) = 1-cos(phi) mass term")

    # Save profile data
    profile_data = [{"r": float(r), "disorder": float(d), "depletion": float(s)}
                    for r, (d, s) in zip(r_centers, profile)]
    report = {
        "params": {"L": L, "R_RING": R_RING, "LAMBDA_SCREEN": LAMBDA_SCREEN,
                   "GAMMA_PHI": GAMMA_PHI, "BETA_PHI": BETA_PHI,
                   "PHASE1": PHASE1, "PHASE2": PHASE2},
        "profile": profile_data,
        "fit_range": [float(r_min_fit), float(r_max_fit)],
        "fit_exponential": {"A": A_exp, "xi": xi_exp, "R2": r2_exp},
        "fit_powerlaw": {"A": A_pow, "alpha": alpha_pow, "R2": r2_pow},
        "verdict": verdict, "detail": detail,
        "m_phi_eff": m_phi_eff,
    }
    with open(out/"report.json", "w") as f: json.dump(report, f, indent=2)

    lines = ["# Phi Effective Mass Probe (QNG-GPU-012)", "",
             f"L={L}, R={R_RING}, GAMMA_PHI={GAMMA_PHI}, lambda_screen={LAMBDA_SCREEN:.2f}", "",
             "## Radial Disorder Profile", "",
             "| r | disorder | depletion |",
             "|---|----------|-----------|"]
    for r, (d, s) in zip(r_centers, profile):
        lines.append(f"| {r:.1f} | {d:.6f} | {s:.6f} |")
    lines += ["", "## Fit Results", ""]
    if A_exp:
        lines.append(f"Exponential: A={A_exp:.6f}  xi={xi_exp:.3f} lu  R2={r2_exp:.4f}")
    if A_pow:
        lines.append(f"Power law:   A={A_pow:.6f}  alpha={alpha_pow:.3f}  R2={r2_pow:.4f}")
    lines += ["", f"## Verdict: {verdict}", "", detail]
    (out/"summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0 if verdict in ("MASSIVE_PHI", "MASSLESS_PHI") else 1


if __name__ == "__main__":
    raise SystemExit(main())
