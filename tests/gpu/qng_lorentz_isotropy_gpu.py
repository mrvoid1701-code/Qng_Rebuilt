from __future__ import annotations

"""
QNG-GPU-012 (candidate): Emergent Lorentz -- dispersion isotropy test (v2).

Tests DER-QNG-043 gates G1/G2/G3 on L=32 cubic lattice.

Design (v2 corrections):
  * Lattice-commensurate wavevectors: k = (2*pi/L) * (n_x, n_y, n_z)
    integer triple. axis=(n,0,0); face_diag=(n,n,0); body_diag=(n,n,n).
  * T=3000 steps to resolve slow modes (|k| = 2*pi/L gives T_period ~= 400).
  * ALPHA_G = 0 for sigma_g sector (massless cone test; avoids long-time
    amplitude decay that kills FFT signal).
  * ALPHA_M = 0 for sigma_m sector (same reason).
  * G_COUPLE_TEST = 0.01 for phi sector (reduced from DER-QNG-041 g=0.22
    so that c^2*k^2 is comparable to m_phi^2 within tested |k| range;
    a separate test validates g=0.22 mass spectrum).
  * Gates redesigned:
      G1: linear fit w^2 = c^2*|k|^2 + m^2 per (sector, direction),
          R^2 > 0.98 and fitted c^2 within 15% of c_pred^2.
      G2: c^2_axis vs c^2_face vs c^2_body within 5% per sector.
      G3: cross-sector c equality within 2%.

Hardware: GPU (cupy). Runtime: ~5 min on RTX 3060.
"""

import json
import math
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-lorentz-isotropy-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Parameters
# =============================================================================

L = 32
N = L * L * L

SIGMA_G_REF = 0.98
SIGMA_M_REF = 0.50

# sigma_g -- v7 wave; ALPHA_G=0 for cleanest dispersion
K_BACK     = 0.10
BETA_G     = 0.35
ALPHA_G    = 0.0       # m_g^2 = 0 in this test
CHI_REL    = 0.35
CHI_DECAY  = 0.0       # remove dissipation for dispersion purity

# sigma_m -- v8 canonical
BETA_M     = 0.35
ALPHA_M    = 0.0       # m_m^2 = 0 in this test
MU_M       = 10.0

# phi -- v8 canonical
BETA_PHI   = 0.06
MU_PHI     = 0.857
G_COUPLE_TEST = 0.01   # reduced from DER-QNG-041 (g=0.22) for c_phi measurability

# Predicted wave speed (shared by all sectors by construction of mu_m, mu_phi)
C2_PRED    = K_BACK * BETA_G / 6.0          # 5.833e-3
C_PRED     = math.sqrt(C2_PRED)             # 0.07638
M_G2_PRED  = K_BACK * ALPHA_G               # 0
M_M2_PRED  = ALPHA_M / MU_M                 # 0
M_PHI2_PRED = G_COUPLE_TEST * SIGMA_G_REF / MU_PHI  # 0.0114

# Integer n triples per direction
N_VALUES = [1, 2, 3]
DIRS = {
    "axis":      (1, 0, 0),     # n-vector (a,b,c); k = (2pi/L)*(a*n, b*n, c*n)
    "face_diag": (1, 1, 0),
    "body_diag": (1, 1, 1),
}

T_STEPS = 3000
DT = 1.0
AMP = 5e-3

# Gate thresholds
G1_R2_MIN    = 0.98
G1_C2_TOL    = 0.15
G2_SPREAD    = 0.05
G3_SPREAD    = 0.02

# =============================================================================
# Lattice
# =============================================================================


def make_coords():
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing="ij")
    return (
        cp.asarray(xg.ravel()),
        cp.asarray(yg.ravel()),
        cp.asarray(zg.ravel()),
    )


def laplacian_z6(f_flat):
    f3 = f_flat.reshape(L, L, L)
    return (
        cp.roll(f3, 1, 0) + cp.roll(f3, -1, 0)
        + cp.roll(f3, 1, 1) + cp.roll(f3, -1, 1)
        + cp.roll(f3, 1, 2) + cp.roll(f3, -1, 2)
        - 6.0 * f3
    ).ravel()


def neighbor_mean(f_flat):
    return (laplacian_z6(f_flat) + 6.0 * f_flat) / 6.0


def k_vector(n_vec, n_scale):
    k0 = 2 * math.pi / L
    return np.array([n_vec[0] * n_scale * k0,
                     n_vec[1] * n_scale * k0,
                     n_vec[2] * n_scale * k0])


def plane_wave_cos(k_vec, amp, xg, yg, zg):
    phase = k_vec[0] * xg + k_vec[1] * yg + k_vec[2] * zg
    return amp * cp.cos(phase)


def project_cos_mode(field, xg, yg, zg, k_vec):
    basis = cp.cos(k_vec[0] * xg + k_vec[1] * yg + k_vec[2] * zg)
    norm = cp.sum(basis * basis)
    return float(cp.sum(field * basis) / norm)


def discrete_lap_eigenvalue(k_vec):
    return 2 * (math.cos(k_vec[0]) + math.cos(k_vec[1]) + math.cos(k_vec[2])) - 6


# =============================================================================
# Sector evolutions
# =============================================================================


def evolve_sigma_g(k_vec, T, xg, yg, zg, amp=None):
    """v7 (sigma_g, chi) SYMPLECTIC LEAPFROG on H_v7 conservative limit.

    Hamiltonian (DER-QNG-036 gravitational sector, conservative limit):
      H_g = (K_BACK/2) chi^2 - (CHI_REL/12) x lap(x) + const

    Canonical EOMs:
      dx/dt   = K_BACK * chi            (drift)
      dchi/dt = (CHI_REL/6) * lap(x)    (kick)

    Produces d^2x/dt^2 = (K_BACK*CHI_REL/6) lap(x),
    wave speed c^2 = K_BACK*CHI_REL/6 = 5.83e-3 at baseline.

    Replaces the Euler-forward update used in v1: symplectic leapfrog has
    no systematic frequency underestimate, closing G3 gap.
    """
    if amp is None:
        amp = AMP
    sigma_g = SIGMA_G_REF + plane_wave_cos(k_vec, amp, xg, yg, zg)
    chi = cp.zeros(N, dtype=cp.float64)

    traj = np.zeros(T + 1)
    traj[0] = project_cos_mode(sigma_g - SIGMA_G_REF, xg, yg, zg, k_vec)

    def force_chi(x):
        return (CHI_REL / 6.0) * laplacian_z6(x)

    chi = chi + 0.5 * DT * force_chi(sigma_g)
    for t in range(T):
        sigma_g = sigma_g + DT * K_BACK * chi
        chi = chi + DT * force_chi(sigma_g)
        traj[t + 1] = project_cos_mode(sigma_g - SIGMA_G_REF, xg, yg, zg, k_vec)
    chi = chi - 0.5 * DT * force_chi(sigma_g)
    return traj


def evolve_sigma_m(k_vec, T, xg, yg, zg, amp=None):
    """v8 canonical (sigma_m, pi_m) leapfrog with ALPHA_M=0: pure wave."""
    if amp is None:
        amp = AMP
    sigma_m = SIGMA_M_REF + plane_wave_cos(k_vec, amp, xg, yg, zg)
    pi_m = cp.zeros(N, dtype=cp.float64)

    traj = np.zeros(T + 1)
    traj[0] = project_cos_mode(sigma_m - SIGMA_M_REF, xg, yg, zg, k_vec)

    def force(sm):
        return -ALPHA_M * (sm - SIGMA_M_REF) - BETA_M * (sm - neighbor_mean(sm))

    pi_m = pi_m + 0.5 * DT * force(sigma_m)
    for t in range(T):
        sigma_m = sigma_m + DT * pi_m / MU_M
        pi_m = pi_m + DT * force(sigma_m)
        traj[t + 1] = project_cos_mode(sigma_m - SIGMA_M_REF, xg, yg, zg, k_vec)
    return traj


def evolve_phi(k_vec, T, xg, yg, zg, amp=None):
    """v8 canonical (phi, pi_phi) leapfrog with reduced G_COUPLE_TEST."""
    if amp is None:
        amp = AMP
    phi = plane_wave_cos(k_vec, amp, xg, yg, zg)
    pi_phi = cp.zeros(N, dtype=cp.float64)

    traj = np.zeros(T + 1)
    traj[0] = project_cos_mode(phi, xg, yg, zg, k_vec)

    c2_spatial = BETA_PHI * SIGMA_M_REF * SIGMA_M_REF / 3.0
    mass_coeff = G_COUPLE_TEST * SIGMA_G_REF

    def force(p):
        return c2_spatial * laplacian_z6(p) - mass_coeff * cp.sin(p)

    pi_phi = pi_phi + 0.5 * DT * force(phi)
    for t in range(T):
        phi = phi + DT * pi_phi / MU_PHI
        pi_phi = pi_phi + DT * force(phi)
        traj[t + 1] = project_cos_mode(phi, xg, yg, zg, k_vec)
    return traj


# =============================================================================
# omega extraction: zero-mean, Hann, FFT, parabolic refinement
# =============================================================================


def extract_omega(traj, dt):
    A = np.asarray(traj, dtype=np.float64)
    A = A - np.mean(A)
    w = np.hanning(len(A))
    Aw = A * w
    spec = np.fft.rfft(Aw)
    freqs = np.fft.rfftfreq(len(A), d=dt)
    power = np.abs(spec) ** 2
    if len(power) < 3:
        return 0.0
    idx = int(np.argmax(power[1:])) + 1
    if 0 < idx < len(power) - 1:
        y0, y1, y2 = power[idx - 1], power[idx], power[idx + 1]
        denom = y0 - 2 * y1 + y2
        delta = 0.5 * (y0 - y2) / denom if abs(denom) > 1e-30 else 0.0
        f_peak = freqs[idx] + delta * (freqs[1] - freqs[0])
    else:
        f_peak = freqs[idx]
    return 2 * math.pi * f_peak


# =============================================================================
# Gate 1: per-(sector, dir) linear fit  w^2 = c^2 * |k|^2 + m^2
# =============================================================================


def linear_fit(ks2, omegas2):
    ks2 = np.asarray(ks2, dtype=np.float64)
    omegas2 = np.asarray(omegas2, dtype=np.float64)
    n = len(ks2)
    k_mean = np.mean(ks2)
    o_mean = np.mean(omegas2)
    num = np.sum((ks2 - k_mean) * (omegas2 - o_mean))
    den = np.sum((ks2 - k_mean) ** 2)
    slope = num / den if abs(den) > 1e-30 else 0.0
    intercept = o_mean - slope * k_mean
    pred = slope * ks2 + intercept
    ss_res = np.sum((omegas2 - pred) ** 2)
    ss_tot = np.sum((omegas2 - o_mean) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 1e-30 else 0.0
    return slope, intercept, r2


# =============================================================================
# Main
# =============================================================================


def print_banner(s):
    bar = "=" * 78
    print(bar); print(s); print(bar)


def main():
    dev = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
    print_banner(f"QNG-GPU-012 v2: Emergent Lorentz dispersion on {dev}")
    print(f"Lattice L={L}^3={N} | T={T_STEPS} steps | amplitude={AMP}")
    print(f"Output directory: {OUT_DIR}")
    print()

    # -------- STAGE 1 --------
    print_banner("STAGE 1 -- analytical predictions")
    print(f"  c_pred      = {C_PRED:.5f} lu/step")
    print(f"  c^2_pred    = {C2_PRED:.5e}")
    print(f"  m_g^2_pred  = {M_G2_PRED:.5e}  (ALPHA_G=0 in this test)")
    print(f"  m_m^2_pred  = {M_M2_PRED:.5e}  (ALPHA_M=0 in this test)")
    print(f"  m_phi^2_pred= {M_PHI2_PRED:.5e}  (G_TEST=0.01)")
    print()
    print("  Integer n triples per direction:")
    for d, nv in DIRS.items():
        print(f"    {d:10s}: base direction {nv}; k_vec = (2pi/L)*{nv}*n  for n in {N_VALUES}")
    print()

    xg, yg, zg = make_coords()

    # -------- STAGE 2 --------
    print_banner("STAGE 2 -- plane-wave evolution & omega extraction")
    sectors = {
        "A": ("sigma_g (v7 symplectic)", evolve_sigma_g, M_G2_PRED),
        "B": ("sigma_m (v8 massless)",   evolve_sigma_m, M_M2_PRED),
        "C": ("phi    (v8 g=0.01)",      evolve_phi,     M_PHI2_PRED),
    }
    results = {k: {"label": v[0], "m2_pred": v[2], "runs": {}}
               for k, v in sectors.items()}

    t_all0 = time.time()
    for sec_tag, (label, evolver, m2_pred) in sectors.items():
        print(f"[{sec_tag}] {label}")
        for dir_name, nv in DIRS.items():
            for n in N_VALUES:
                k_vec = k_vector(nv, n)
                k_mag = float(np.linalg.norm(k_vec))
                k2 = k_mag ** 2
                # predicted omega^2 using CONTINUUM c^2*k^2 + m^2
                w2_pred_cont = C2_PRED * k2 + m2_pred
                # predicted omega^2 using DISCRETE lattice Laplacian eigenvalue
                e_k = discrete_lap_eigenvalue(k_vec)  # negative
                w2_pred_disc = -C2_PRED * e_k * 6 / 6 + m2_pred  # k_back*beta_g/6 * eig_lap /(-1)
                # Actually: w^2 = -c^2 * e_k + m^2 (since e_k is negative, -c^2 e_k > 0)
                w2_pred_disc = -C2_PRED * e_k + m2_pred
                t0 = time.time()
                traj = evolver(k_vec, T_STEPS, xg, yg, zg)
                w = extract_omega(traj, DT)
                dt_run = time.time() - t0
                w2 = w * w
                err_cont = abs(w2 - w2_pred_cont) / max(w2_pred_cont, 1e-12)
                err_disc = abs(w2 - w2_pred_disc) / max(w2_pred_disc, 1e-12)
                key = f"{dir_name}_n{n}"
                results[sec_tag]["runs"][key] = {
                    "dir": dir_name, "n": n,
                    "k_vec": k_vec.tolist(), "k_mag": k_mag, "k2": k2,
                    "eig_lap": e_k,
                    "omega": w, "omega2": w2,
                    "w2_pred_continuum": w2_pred_cont,
                    "w2_pred_discrete": w2_pred_disc,
                    "err_continuum": err_cont,
                    "err_discrete": err_disc,
                    "wall_s": dt_run,
                }
                print(
                    f"    dir={dir_name:10s} n={n}  |k|={k_mag:.4f}  eig_lap={e_k:+.4f}  "
                    f"w={w:.5f}  w2={w2:.4e}  "
                    f"pred_disc={w2_pred_disc:.4e}  err={err_disc*100:5.2f}%  ({dt_run:.1f}s)",
                    flush=True,
                )
        print()
    wall_total = time.time() - t_all0
    print(f"Total evolution wall time: {wall_total:.1f}s")
    print()

    # -------- STAGE 2b: amplitude scan (item iii non-linear corrections) --------
    print_banner("STAGE 2b -- amplitude scan (DER-QNG-043 item iii)")
    amps_scan = [1e-3, 5e-3, 2.5e-2]  # 25x span
    amp_scan_results = {}
    for sec_tag, (label, evolver, m2_pred) in sectors.items():
        print(f"[{sec_tag}] {label}  (axis n=1, k={2*math.pi/L:.4f})")
        amp_scan_results[sec_tag] = {}
        k_vec = k_vector(DIRS["axis"], 1)
        k2 = float(np.linalg.norm(k_vec)) ** 2
        e_k = discrete_lap_eigenvalue(k_vec)
        w2_pred = -C2_PRED * e_k + m2_pred
        for amp in amps_scan:
            t0 = time.time()
            traj = evolver(k_vec, T_STEPS, xg, yg, zg, amp=amp)
            w = extract_omega(traj, DT)
            dt_run = time.time() - t0
            w2 = w * w
            err = abs(w2 - w2_pred) / max(w2_pred, 1e-12)
            amp_scan_results[sec_tag][amp] = {
                "omega": w, "omega2": w2, "w2_pred": w2_pred,
                "rel_err": err, "wall_s": dt_run,
            }
            print(f"    amp={amp:.4f}  w={w:.5f}  w2={w2:.4e}  "
                  f"pred={w2_pred:.4e}  err={err*100:5.2f}%  ({dt_run:.1f}s)",
                  flush=True)
        # Relative change of omega across amplitudes (target: <1% for linear sector)
        omegas = [amp_scan_results[sec_tag][a]["omega"] for a in amps_scan]
        o_mean = np.mean(omegas)
        o_spread = max(abs(o - o_mean) for o in omegas) / o_mean
        print(f"    -> omega spread across 25x amp range: {o_spread*100:.2f}%"
              f"  {'(amplitude-independent = linear)' if o_spread < 0.02 else '(non-linear)'}")
        amp_scan_results[sec_tag]["spread"] = o_spread
    print()

    # -------- STAGE 3: per-(sector, dir) fit w^2 = c^2_fit * |k|^2 + m^2_fit --------
    print_banner("STAGE 3 -- linear fit w^2 vs |k|^2 per (sector, direction)")
    fits = {}
    for sec_tag, sec in results.items():
        sec_fits = {}
        for dir_name in DIRS:
            ks2 = [sec["runs"][f"{dir_name}_n{n}"]["k2"] for n in N_VALUES]
            ws2 = [sec["runs"][f"{dir_name}_n{n}"]["omega2"] for n in N_VALUES]
            c2, m2, r2 = linear_fit(ks2, ws2)
            sec_fits[dir_name] = {"c2": c2, "m2": m2, "R2": r2,
                                   "c": math.sqrt(max(c2, 0))}
            print(f"  [{sec_tag}] {dir_name:10s} "
                  f"c^2_fit={c2:.4e}  m^2_fit={m2:+.4e}  "
                  f"c_fit={math.sqrt(max(c2,0)):.5f}  R^2={r2:.4f}")
        fits[sec_tag] = sec_fits
    print()

    # -------- STAGE 4: gates --------
    print_banner("STAGE 4 -- gate evaluation")

    # G1: per (sector, dir) R^2 > 0.98 and |c^2_fit - c^2_pred|/c^2_pred < 15%
    print(f"G1 -- dispersion linear fit, per sector per direction:")
    print(f"      PASS: R^2 > {G1_R2_MIN} AND |c^2_fit - c^2_pred|/c^2_pred < {G1_C2_TOL*100:.0f}%")
    g1_pass = {}
    for sec_tag, sec_fits in fits.items():
        sec_pass = True
        for d in DIRS:
            f = sec_fits[d]
            r2_ok = f["R2"] > G1_R2_MIN
            c2_err = abs(f["c2"] - C2_PRED) / C2_PRED
            c2_ok = c2_err < G1_C2_TOL
            row = r2_ok and c2_ok
            sec_pass = sec_pass and row
            print(f"  [{sec_tag}] {d:10s}  R^2={f['R2']:.4f} ({'OK' if r2_ok else 'FAIL'})  "
                  f"c^2_err={c2_err*100:5.2f}% ({'OK' if c2_ok else 'FAIL'})  "
                  f"=> {'PASS' if row else 'FAIL'}")
        g1_pass[sec_tag] = sec_pass
    print()

    # G2: direction isotropy per sector -- c_fit spread across 3 directions < 5%
    print(f"G2 -- direction isotropy: spread of c_fit across directions < {G2_SPREAD*100:.0f}%")
    g2_pass = {}
    for sec_tag, sec_fits in fits.items():
        cs = [sec_fits[d]["c"] for d in DIRS]
        c_mean = np.mean(cs)
        spread = max(abs(c - c_mean) for c in cs) / c_mean if c_mean > 1e-12 else float('inf')
        passed = spread < G2_SPREAD
        g2_pass[sec_tag] = passed
        print(f"  [{sec_tag}] {results[sec_tag]['label']:28s} "
              f"c_axis={sec_fits['axis']['c']:.5f}  "
              f"c_face={sec_fits['face_diag']['c']:.5f}  "
              f"c_body={sec_fits['body_diag']['c']:.5f}  "
              f"spread={spread*100:5.2f}%  "
              f"{'PASS' if passed else 'FAIL'}")
    print()

    # G3: cross-sector cone equality -- mean c per sector, then spread < 2%
    print(f"G3 -- cross-sector cone equality: spread of mean(c) across sectors < {G3_SPREAD*100:.0f}%")
    cs_per_sector = {s: np.mean([fits[s][d]["c"] for d in DIRS]) for s in fits}
    c_all_mean = np.mean(list(cs_per_sector.values()))
    g3_spread = max(abs(c - c_all_mean) for c in cs_per_sector.values()) / c_all_mean
    g3_pass = g3_spread < G3_SPREAD
    for s, c in cs_per_sector.items():
        diff = abs(c - c_all_mean) / c_all_mean
        print(f"  [{s}] c_mean={c:.5f}  diff_from_overall={diff*100:5.2f}%")
    print(f"  c_overall_mean={c_all_mean:.5f}  c_pred={C_PRED:.5f}  "
          f"spread={g3_spread*100:.2f}%  "
          f"{'PASS' if g3_pass else 'FAIL'}")
    print()

    # -------- STAGE 5: verdict --------
    print_banner("STAGE 5 -- VERDICT")
    g1_all = all(g1_pass.values())
    g2_all = all(g2_pass.values())
    print(f"  G1 (dispersion fit):        {'PASS' if g1_all else 'FAIL'}   per-sector: {g1_pass}")
    print(f"  G2 (direction isotropy):    {'PASS' if g2_all else 'FAIL'}   per-sector: {g2_pass}")
    print(f"  G3 (cross-sector cone):     {'PASS' if g3_pass else 'FAIL'}")
    overall = g1_all and g2_all and g3_pass
    print()
    if overall:
        print("  >>> EMERGENT LORENTZ (linear order) -- CONFIRMED.")
        print(f"      3 sectors share cone c = {c_all_mean:.5f} lu/step (pred {C_PRED:.5f}).")
        print("      NOTE-QNG-013 L1 discharged numerically on z=6 cubic lattice.")
    else:
        print("  >>> Partial or failure -- inspect gate details above.")

    out = {
        "test_id": "QNG-GPU-012-candidate-v2",
        "L": L, "T": T_STEPS, "amplitude": AMP,
        "params": {
            "K_BACK": K_BACK, "BETA_G": BETA_G, "ALPHA_G": ALPHA_G,
            "CHI_REL": CHI_REL, "CHI_DECAY": CHI_DECAY,
            "BETA_M": BETA_M, "ALPHA_M": ALPHA_M, "MU_M": MU_M,
            "BETA_PHI": BETA_PHI, "MU_PHI": MU_PHI,
            "G_COUPLE_TEST": G_COUPLE_TEST,
            "SIGMA_G_REF": SIGMA_G_REF, "SIGMA_M_REF": SIGMA_M_REF,
        },
        "predictions": {
            "c_pred": C_PRED, "c2_pred": C2_PRED,
            "m_g2_pred": M_G2_PRED, "m_m2_pred": M_M2_PRED,
            "m_phi2_pred": M_PHI2_PRED,
        },
        "runs": results,
        "fits": fits,
        "gates": {
            "G1_R2_min": G1_R2_MIN, "G1_c2_tol": G1_C2_TOL, "G1_pass": g1_pass,
            "G2_spread": G2_SPREAD, "G2_pass": g2_pass,
            "G3_spread_tol": G3_SPREAD, "G3_spread_meas": g3_spread, "G3_pass": g3_pass,
            "overall": overall,
        },
        "c_per_sector": cs_per_sector,
        "c_overall_mean": c_all_mean,
        "wall_time_s": wall_total,
    }
    out_path = OUT_DIR / "qng-lorentz-isotropy-v1.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nArtifact: {out_path}")


if __name__ == "__main__":
    main()
