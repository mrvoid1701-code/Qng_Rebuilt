from __future__ import annotations

"""QNG-GPU-017: Hopfion Q=1 vs vortex ring Q=0 disorder-profile L-scan.

Tests whether topology (linked vs unlinked phi winding) changes the IR
behaviour of the Goldstone halo. Baseline: GPU-012 measured alpha=2.37
for the ring at L=80. Savant-physics-reviewer (2026-04-18) predicts
alpha>=3.0 for Hopfion via Faddeev-Niemi analog (r^-4 far-field).

Protocol: v5 + Channel H (identical to GPU-015/GPU-016). Single change
vs GPU-012: toroidal twist `q_twist * atan2(dy, dx)` added to phi initial
condition; q_twist=0 reproduces GPU-012 control; q_twist=1 is the Hopfion.

Gates (pre-registered in QNG-GPU-017.md):
  G1 control: |alpha_{q=0}(L=80) - 2.37| < 0.20
  G2 Hopfion: alpha_{q=1}(L=80) >= 3.0 PASS / < 2.5 FAIL
  G3 L-indep: spread of alpha_{q=1} over L in {60,80,100} < 0.25
  G4 fit type: record R^2 for exponential vs power-law; exponential
               better by >0.05 indicates a true mass gap.
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-hopfion-disorder-l-scan-v1"

SIGMA_REF    = 0.5
ALPHA        = 0.005
BETA         = 0.35
DELTA_CHI    = 0.20
CHI_DECAY    = 0.020
CHI_REL      = 0.35
GAMMA_PHI    = 0.10
BETA_PHI_MIN  = 0.0005
BETA_PHI_RING = 0.06
K_GM         = 0.0

PHASE1 = 300
PHASE2 = 1500

L_VALUES = [40, 60, 80, 100]
R_RING   = 5
Q_TWISTS = [0, 1]  # 0 = vortex ring control, 1 = Hopfion Q=1

LAMBDA_SCREEN = math.sqrt(BETA / ALPHA)  # ~8.37 lu


# ---------------------------------------------------------------------------
# GPU geometry helpers
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


def build_phi_init(L, R, q_twist):
    """phi_ring + q_twist * phi_toroidal.
    q_twist=0 -> vortex ring Q=0
    q_twist=1 -> Hopfion Q=1 (linking number 1)
    """
    dx, dy, dz = _centered_coords(L)
    rho = np.sqrt(dx*dx + dy*dy)
    poloidal = np.arctan2(dz, rho-R)
    toroidal = np.arctan2(dy, dx)
    phi = poloidal + q_twist * toroidal
    # wrap to (-pi, pi]
    phi = (phi + math.pi) % (2*math.pi) - math.pi
    return cp.asarray(phi.ravel())


def build_r_shells(L):
    """Spherical distance from box center, binned into shells of width 1.
    Returns (shells, shell_centers) with n_shells = floor(L/2) - 2."""
    dx, dy, dz = _centered_coords(L)
    r = np.sqrt(dx*dx + dy*dy + dz*dz).ravel()
    n_shells = int(L//2) - 2
    shells = []
    for s in range(n_shells):
        mask = cp.asarray((r >= s) & (r < s+1))
        shells.append(mask)
    return shells, np.arange(n_shells) + 0.5


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
# Dynamics (identical to GPU-016)
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
# Radial profile + fits
# ---------------------------------------------------------------------------

def measure_profile(phi, sm, nb, shells):
    """Mean disorder and depletion in each radial shell."""
    dis_field = disorder_gpu(phi, nb)
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


def fit_powerlaw(r_vals, dis_vals):
    """Fit disorder(r) = A * r^(-alpha). Return (A, alpha>0, R2)."""
    try:
        log_r = np.log(r_vals)
        dv = np.maximum(dis_vals, 1e-12)
        log_d = np.log(dv)
        coeffs = np.polyfit(log_r, log_d, 1)
        alpha_fit = -coeffs[0]
        A_fit = math.exp(coeffs[1])
        pred = A_fit * r_vals**(-alpha_fit)
        ss_res = float(np.sum((dis_vals - pred)**2))
        ss_tot = float(np.sum((dis_vals - dis_vals.mean())**2))
        r2 = 1 - ss_res / max(ss_tot, 1e-12)
        return A_fit, float(alpha_fit), r2
    except Exception as e:
        return None, None, None


def fit_exponential(r_vals, dis_vals):
    """Fit disorder(r) = A * exp(-r/xi)."""
    try:
        def model(r, A, xi): return A * np.exp(-r / xi)
        p0 = [max(dis_vals[0], 1e-6), LAMBDA_SCREEN]
        popt, _ = curve_fit(model, r_vals, dis_vals, p0=p0,
                            bounds=([0, 0.1], [1, 200]), maxfev=10000)
        A, xi = popt
        pred = model(r_vals, A, xi)
        ss_res = float(np.sum((dis_vals - pred)**2))
        ss_tot = float(np.sum((dis_vals - dis_vals.mean())**2))
        r2 = 1 - ss_res / max(ss_tot, 1e-12)
        return float(A), float(xi), r2
    except Exception:
        return None, None, None


# ---------------------------------------------------------------------------
# Run one (L, q_twist)
# ---------------------------------------------------------------------------

def run_hopfion(L, q_twist, nb, shells, shell_centers):
    N = L*L*L
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi_init(L, R_RING, q_twist)

    for _ in range(PHASE1):
        sm, chi, phi = step_phase1(sm, chi, phi, nb)
    for _ in range(PHASE2):
        sm, chi, phi = step_phase2(sm, chi, phi, nb)

    profile = measure_profile(phi, sm, nb, shells)
    dis_arr = np.array([p[0] for p in profile])
    dep_arr = np.array([p[1] for p in profile])

    # Fit domain: r in [R+5, L/2 - 3]  (bulk tail, avoid core + box edge)
    r_min = R_RING + 5
    r_max = L/2 - 3
    fit_mask = (shell_centers >= r_min) & (shell_centers <= r_max) & (dis_arr > 0)
    r_fit = shell_centers[fit_mask]
    d_fit = dis_arr[fit_mask]

    A_pow, alpha_pow, r2_pow = fit_powerlaw(r_fit, d_fit) if len(r_fit) >= 3 else (None, None, None)
    A_exp, xi_exp, r2_exp   = fit_exponential(r_fit, d_fit) if len(r_fit) >= 3 else (None, None, None)

    return {
        "L": L, "q_twist": q_twist, "N": N,
        "r_centers": shell_centers.tolist(),
        "dis_profile": dis_arr.tolist(),
        "dep_profile": dep_arr.tolist(),
        "r_fit_min": float(r_min), "r_fit_max": float(r_max),
        "n_fit_points": int(len(r_fit)),
        "powerlaw": {"A": A_pow, "alpha": alpha_pow, "R2": r2_pow},
        "exponential": {"A": A_exp, "xi": xi_exp, "R2": r2_exp},
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

    print("QNG-GPU-017: Hopfion Q=1 vs ring Q=0 disorder-profile L-scan")
    print(f"v5 + Channel H, K_GM={K_GM}, R={R_RING}")
    print(f"L values: {L_VALUES}  q_twist: {Q_TWISTS}")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB", flush=True)
    print()

    all_results = []

    for L in L_VALUES:
        print(f"=== L={L} ===", flush=True)
        nb = build_nb(L)
        shells, centers = build_r_shells(L)

        for q in Q_TWISTS:
            res = run_hopfion(L, q, nb, shells, centers)
            all_results.append(res)
            label = "ring  " if q == 0 else "Hopf  "
            pw = res["powerlaw"]
            ex = res["exponential"]
            a_str = f"{pw['alpha']:.3f}" if pw["alpha"] is not None else "  nan"
            xi_str = f"{ex['xi']:.2f}" if ex["xi"] is not None else "  nan"
            r2p = f"{pw['R2']:.3f}" if pw["R2"] is not None else "  nan"
            r2e = f"{ex['R2']:.3f}" if ex["R2"] is not None else "  nan"
            print(f"  q={q} ({label}): alpha={a_str}  R2_pow={r2p}  xi={xi_str}  "
                  f"R2_exp={r2e}  n_fit={res['n_fit_points']}", flush=True)

        del nb
        cp.get_default_memory_pool().free_all_blocks()

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def get(L, q):
        return next(r for r in all_results if r["L"] == L and r["q_twist"] == q)

    alpha_q0 = {L: get(L, 0)["powerlaw"]["alpha"] for L in L_VALUES}
    alpha_q1 = {L: get(L, 1)["powerlaw"]["alpha"] for L in L_VALUES}
    r2p_q1   = {L: get(L, 1)["powerlaw"]["R2"]    for L in L_VALUES}
    r2e_q1   = {L: get(L, 1)["exponential"]["R2"] for L in L_VALUES}
    xi_q1    = {L: get(L, 1)["exponential"]["xi"] for L in L_VALUES}

    print()
    print("="*80)
    print("POWER-LAW ALPHA vs L")
    print("="*80)
    print(f"{'L':>4}  {'alpha(q=0) ring':>20}  {'alpha(q=1) Hopf':>20}")
    for L in L_VALUES:
        a0 = alpha_q0[L]; a1 = alpha_q1[L]
        a0s = f"{a0:.4f}" if a0 is not None else "  nan"
        a1s = f"{a1:.4f}" if a1 is not None else "  nan"
        print(f"{L:>4}  {a0s:>20}  {a1s:>20}")

    # Gates
    a0_80 = alpha_q0[80]
    a1_80 = alpha_q1[80]

    # G1: control reproducibility
    g1_val = abs(a0_80 - 2.37) if a0_80 is not None else float("inf")
    g1 = g1_val < 0.20

    # G2: Hopfion decay exponent
    if a1_80 is None:
        g2_status = "NAN"
    elif a1_80 >= 3.0:
        g2_status = "PASS"
    elif a1_80 < 2.5:
        g2_status = "FAIL"
    else:
        g2_status = "AMBIGUOUS"

    # G3: L-independence of Hopfion exponent (over L in {60,80,100})
    L_sub = [L for L in [60, 80, 100] if L in L_VALUES]
    a1_sub = [alpha_q1[L] for L in L_sub if alpha_q1[L] is not None]
    if len(a1_sub) >= 2:
        g3_spread = max(a1_sub) - min(a1_sub)
        g3 = g3_spread < 0.25
    else:
        g3_spread = float("nan")
        g3 = False

    # G4: power-law vs exponential
    if r2p_q1[80] is not None and r2e_q1[80] is not None:
        g4_delta = r2e_q1[80] - r2p_q1[80]
        g4_exponential_wins = g4_delta > 0.05
    else:
        g4_delta = float("nan")
        g4_exponential_wins = False

    print()
    print(f"Gate 1 (control, |alpha_ring(L=80) - 2.37| < 0.20): "
          f"value={g1_val:.4f}  {'PASS' if g1 else 'FAIL'}")
    if a1_80 is not None:
        print(f"Gate 2 (Hopfion alpha at L=80 = {a1_80:.4f}):")
        print(f"         threshold PASS >= 3.0, FAIL < 2.5  => {g2_status}")
    else:
        print(f"Gate 2: alpha(q=1,L=80) = NAN  => VOID")
    print(f"Gate 3 (Hopfion alpha L-spread over {L_sub}): "
          f"spread={g3_spread:.4f}  (threshold < 0.25)  {'PASS' if g3 else 'FAIL'}")
    print(f"Gate 4 (exponential vs power-law at L=80 for Hopfion):")
    print(f"         R2_pow={r2p_q1[80]}  R2_exp={r2e_q1[80]}  "
          f"delta={g4_delta}  "
          f"=> {'EXP wins (mass gap)' if g4_exponential_wins else 'power-law OK'}")
    if xi_q1[80] is not None:
        print(f"         xi_hopfion(L=80) = {xi_q1[80]:.2f} lu "
              f"(LAMBDA_SCREEN = {LAMBDA_SCREEN:.2f})")

    # Verdict
    if not g1:
        verdict = "VOID"
        interp = ("Control ring exponent drifted from GPU-012 value 2.37. "
                  "Dynamics comparison is invalid. Debug required.")
    elif g4_exponential_wins and g1:
        verdict = "PASS_STRONG"
        interp = (f"Hopfion disorder fits exponential BETTER than power-law "
                  f"(delta R^2 = {g4_delta:.3f}). Mass gap xi={xi_q1[80]:.2f} "
                  "dynamically generated. Option C (Hopfion mass carrier) strongly "
                  "preferred over Option B.")
    elif g2_status == "PASS" and g3 and g1:
        verdict = "PASS"
        interp = (f"Hopfion alpha(L=80)={a1_80:.3f} > 3.0, L-independent. "
                  "Topology changes IR decay; Hopfion viable mass carrier. "
                  "Follow-up: Hopfion mass L-scan.")
    elif g2_status == "FAIL" and g1:
        verdict = "FAIL"
        interp = (f"Hopfion alpha(L=80)={a1_80:.3f} < 2.5, similar to ring. "
                  "IR halo is universal; topology does not cure it. "
                  "Option C falsified at structural level; Option B "
                  "(add V(sigma_m)) is forced.")
    else:
        verdict = "AMBIGUOUS"
        interp = (f"Hopfion alpha(L=80)={a1_80} inconclusive between PASS and FAIL. "
                  "Secondary test required (e.g. Hopfion mass L-scan).")

    print()
    print(f"VERDICT: {verdict}")
    print(f"  {interp}")
    print()

    # JSON report
    report = {
        "test_id": "QNG-GPU-017",
        "status": verdict,
        "parameters": {
            "ALPHA": ALPHA, "BETA": BETA, "DELTA_CHI": DELTA_CHI,
            "CHI_DECAY": CHI_DECAY, "CHI_REL": CHI_REL, "GAMMA_PHI": GAMMA_PHI,
            "BETA_PHI_MIN": BETA_PHI_MIN, "BETA_PHI_RING": BETA_PHI_RING,
            "K_GM": K_GM, "PHASE1": PHASE1, "PHASE2": PHASE2,
            "R_RING": R_RING,
        },
        "L_values": L_VALUES, "Q_TWISTS": Q_TWISTS,
        "alpha_q0": {str(k): v for k, v in alpha_q0.items()},
        "alpha_q1": {str(k): v for k, v in alpha_q1.items()},
        "r2_powerlaw_q1":   {str(k): v for k, v in r2p_q1.items()},
        "r2_exponential_q1": {str(k): v for k, v in r2e_q1.items()},
        "xi_exponential_q1": {str(k): v for k, v in xi_q1.items()},
        "gates": {
            "G1_control": {"|alpha-2.37|": g1_val, "threshold": 0.20, "pass": g1},
            "G2_hopfion_alpha_L80": {"value": a1_80, "status": g2_status},
            "G3_L_independence": {"spread": g3_spread, "threshold": 0.25, "pass": g3,
                                   "L_sub": L_sub, "alphas": a1_sub},
            "G4_exponential_vs_powerlaw": {"delta_R2": g4_delta,
                                             "exponential_wins": g4_exponential_wins},
        },
        "verdict": verdict,
        "interpretation": interp,
        "raw_results": all_results,
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Summary.md
    with open(out / "summary.md", "w", encoding="utf-8") as f:
        f.write("# Hopfion Q=1 vs Ring Q=0 disorder profile L-scan (QNG-GPU-017)\n\n")
        f.write(f"v5 + Channel H, K_GM={K_GM}, R={R_RING}\n")
        f.write(f"LAMBDA_SCREEN = sqrt(BETA/ALPHA) = {LAMBDA_SCREEN:.2f} lu\n\n")
        f.write("## Power-law exponent alpha vs L\n\n")
        f.write("| L | alpha(ring, q=0) | alpha(Hopfion, q=1) | R2_pow(q=1) | R2_exp(q=1) | xi(q=1) |\n")
        f.write("|---|-----------------|---------------------|-------------|-------------|--------|\n")
        for L in L_VALUES:
            a0 = alpha_q0[L]; a1 = alpha_q1[L]
            r2p = r2p_q1[L];  r2e = r2e_q1[L]; xi = xi_q1[L]
            def _fmt(x, d=4): return f"{x:.{d}f}" if x is not None else "nan"
            f.write(f"| {L} | {_fmt(a0)} | {_fmt(a1)} | {_fmt(r2p,3)} | "
                    f"{_fmt(r2e,3)} | {_fmt(xi,2)} |\n")
        f.write("\n## Gates\n\n")
        f.write(f"- **G1 control** |alpha(ring, L=80) - 2.37| < 0.20 : "
                f"{g1_val:.4f}  -> {'PASS' if g1 else 'FAIL'}\n")
        f.write(f"- **G2 Hopfion exponent** alpha(Hopf,L=80) = "
                f"{a1_80 if a1_80 is None else f'{a1_80:.4f}'}  -> {g2_status}\n")
        f.write(f"- **G3 L-independence** spread over {L_sub} = "
                f"{g3_spread:.4f}  -> {'PASS' if g3 else 'FAIL'}\n")
        f.write(f"- **G4 power-law vs exponential** delta_R2 = "
                f"{g4_delta if isinstance(g4_delta, str) else f'{g4_delta:.4f}'}"
                f"  -> {'EXP wins' if g4_exponential_wins else 'power-law OK'}\n\n")
        f.write(f"## Verdict: **{verdict}**\n\n")
        f.write(f"{interp}\n")

    print(f"Reports written to {out}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
