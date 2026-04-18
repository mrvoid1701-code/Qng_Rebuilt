from __future__ import annotations

"""Ring angular momentum proxy (QNG-GPU-008, GPU).

Does QNG ring radius encode spin/angular momentum?

In QM: J^2 = J(J+1)*hbar^2
  N(938):    J=1/2  -> J(J+1) = 3/4
  Delta(1232): J=3/2  -> J(J+1) = 15/4
  Ratio: J^2(Delta)/J^2(N) = 5.0

QNG empirical: R=4 -> I=1/2, R=5 -> I=3/2 (from baryon resonance ladder)

Test: measure phi field angular momentum L_z, L_x, L_y for rings R=4,5,6,7
  L_alpha = sum_i [ (r x grad_phi)_alpha ]_i * dep_i
  where dep_i = max(0, sigma_ref - sigma_m_i)  (depletion weight)

Physical interpretation:
  If L^2(R=5)/L^2(R=4) ~ 5.0 -> phi winding encodes QM spin structure
  If ratio ~ R^2 -> angular momentum scales with ring area (classical vortex)
  If ratio ~ 1   -> angular momentum is phi-topology independent (just Q=1)

Rings tested: R=3,4,5,6,7 (full baryon ladder)
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-angular-momentum-v1"

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

L      = 50   # large enough for screening, smaller than 60 for speed
RADII  = [3, 4, 5, 6, 7]

# QM J(J+1) values from baryon ladder
JJ1_QM = {3: None, 4: 0.75, 5: 3.75, 6: 0.75, 7: 3.75}
# (R=3 unknown; R=4,6=N-family J=1/2; R=5,7=Delta-family J=3/2)


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


def build_coords(L):
    cx = cy = cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg.ravel() - cx; dy = yg.ravel() - cy; dz = zg.ravel() - cz
    # Wrap to nearest image
    dx = np.where(dx >  L/2, dx-L, dx); dx = np.where(dx < -L/2, dx+L, dx)
    dy = np.where(dy >  L/2, dy-L, dy); dy = np.where(dy < -L/2, dy+L, dy)
    dz = np.where(dz >  L/2, dz-L, dz); dz = np.where(dz < -L/2, dz+L, dz)
    return cp.asarray(dx), cp.asarray(dy), cp.asarray(dz)


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


def measure_angular_momentum(phi, sm, nb, dx, dy, dz):
    """Depletion-weighted angular momentum of phi gradient field.

    grad_phi computed from neighbor differences (central differences).
    L = r x grad_phi, weighted by depletion dep = max(0, sigma_ref - sm).
    """
    dep = cp.maximum(0.0, SIGMA_REF - sm)
    norm = float(cp.sum(dep)) + 1e-12

    # Central differences for phi gradient (wrapped)
    nb_xp = phi[nb[:, 1]]; nb_xm = phi[nb[:, 0]]
    nb_yp = phi[nb[:, 3]]; nb_ym = phi[nb[:, 2]]
    nb_zp = phi[nb[:, 5]]; nb_zm = phi[nb[:, 4]]

    dphi_dx = wrap_gpu(nb_xp - nb_xm) / 2.0
    dphi_dy = wrap_gpu(nb_yp - nb_ym) / 2.0
    dphi_dz = wrap_gpu(nb_zp - nb_zm) / 2.0

    # L = r x grad_phi
    Lx = dy * dphi_dz - dz * dphi_dy
    Ly = dz * dphi_dx - dx * dphi_dz
    Lz = dx * dphi_dy - dy * dphi_dx

    # Depletion-weighted averages
    Lx_mean = float(cp.sum(Lx * dep)) / norm
    Ly_mean = float(cp.sum(Ly * dep)) / norm
    Lz_mean = float(cp.sum(Lz * dep)) / norm

    L2 = Lx_mean**2 + Ly_mean**2 + Lz_mean**2

    # Also measure raw phi winding (topological charge proxy)
    dis = disorder(phi, nb)
    Q_proxy = float(cp.sum(dis * dep)) / norm

    return Lx_mean, Ly_mean, Lz_mean, L2, Q_proxy


def run_ring(R, nb, dx, dy, dz):
    N = L*L*L
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi_ring(L, R)

    for _ in range(PHASE1): sm, chi, phi = step1(sm, chi, phi, nb)
    for _ in range(PHASE2): sm, chi, phi = step2(sm, chi, phi, nb)

    Lx, Ly, Lz, L2, Q = measure_angular_momentum(phi, sm, nb, dx, dy, dz)
    M = float(N*SIGMA_REF - cp.sum(sm))

    print(f"  R={R}: M={M:.1f}  Lx={Lx:.4f}  Ly={Ly:.4f}  Lz={Lz:.4f}  "
          f"L^2={L2:.6f}  Q={Q:.5f}", flush=True)
    return {"R": R, "M": round(M, 2),
            "Lx": round(Lx, 6), "Ly": round(Ly, 6), "Lz": round(Lz, 6),
            "L2": round(L2, 8), "Q": round(Q, 6)}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("Ring angular momentum proxy (QNG-GPU-008)")
    print(f"L={L}, Radii={RADII}")
    print(f"QM prediction: J(J+1) ratio Delta/N = 5.0")
    print(f"Classical vortex: L^2 ~ R^2 -> ratio R=5/R=4 = {(5/4)**2:.2f}")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    nb = build_nb(L)
    dx, dy, dz = build_coords(L)

    results = []
    for R in RADII:
        results.append(run_ring(R, nb, dx, dy, dz))
    print()

    # Analysis
    print("="*70)
    print("ANGULAR MOMENTUM ANALYSIS")
    print("="*70)
    print(f"{'R':>3}  {'L^2':>10}  {'L^2/L^2(R4)':>12}  "
          f"{'QM J(J+1)':>10}  {'match':>8}")
    print("-"*70)

    r4 = next(r for r in results if r["R"] == 4)
    L2_r4 = r4["L2"]

    for res in results:
        ratio = res["L2"] / max(L2_r4, 1e-12)
        jj1   = JJ1_QM.get(res["R"])
        jj1_ratio = jj1 / JJ1_QM[4] if jj1 and JJ1_QM[4] else None
        if jj1_ratio:
            match_pct = abs(ratio - jj1_ratio) / jj1_ratio * 100
            match_str = f"{match_pct:.1f}%"
        else:
            match_str = "?"
        print(f"{res['R']:>3}  {res['L2']:>10.6f}  {ratio:>12.4f}  "
              f"{str(jj1_ratio) if jj1_ratio else '?':>10}  {match_str:>8}")

    # Check if L^2 scales as R^2 (classical) or J(J+1) (quantum)
    r5 = next(r for r in results if r["R"] == 5)
    ratio_54 = r5["L2"] / max(L2_r4, 1e-12)
    classical_pred = (5/4)**2   # 1.5625
    quantum_pred   = 5.0        # J(J+1) ratio Delta/N
    r2_pred        = (5/4)**2   # same as classical for L~R

    print()
    print(f"Observed L^2(R=5)/L^2(R=4) = {ratio_54:.4f}")
    print(f"Classical vortex prediction (L~R): {classical_pred:.4f}")
    print(f"QM spin prediction (J(J+1)):       {quantum_pred:.4f}")
    print()

    if abs(ratio_54 - quantum_pred) < abs(ratio_54 - classical_pred):
        verdict = "QM_SPIN_LIKE"
        detail  = f"L^2 ratio {ratio_54:.3f} closer to QM J(J+1)=5 than classical"
    elif abs(ratio_54 - 1.0) < 0.1:
        verdict = "TOPOLOGY_ONLY"
        detail  = f"L^2 nearly equal for R=4,5 -> angular momentum = phi topology (Q=1 both)"
    else:
        verdict = "CLASSICAL_VORTEX"
        detail  = f"L^2 ratio {ratio_54:.3f} closer to classical R^2 scaling"

    print(f"VERDICT: {verdict}")
    print(f"  {detail}")

    report = {"params": {"L": L, "RADII": RADII, "PHASE1": PHASE1, "PHASE2": PHASE2},
              "results": results,
              "ratio_L2_54": round(ratio_54, 5),
              "classical_pred": classical_pred, "quantum_pred": quantum_pred,
              "verdict": verdict, "detail": detail}
    with open(out/"report.json", "w") as f: json.dump(report, f, indent=2)

    lines = ["# Ring Angular Momentum Proxy (QNG-GPU-008)", "",
             f"L={L}, Radii={RADII}", "",
             "| R | L^2 | L^2/L^2(R=4) | QM J(J+1)/J(J+1)(R=4) |",
             "|---|-----|-------------|------------------------|"]
    for res in results:
        ratio = res["L2"] / max(L2_r4, 1e-12)
        jj1 = JJ1_QM.get(res["R"])
        jj1r = jj1/JJ1_QM[4] if jj1 and JJ1_QM[4] else "?"
        lines.append(f"| {res['R']} | {res['L2']:.6f} | {ratio:.4f} | {jj1r} |")
    lines += ["", f"## Verdict: {verdict}", "", detail]
    (out/"summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
