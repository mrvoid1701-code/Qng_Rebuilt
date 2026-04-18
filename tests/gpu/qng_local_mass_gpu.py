from __future__ import annotations

"""Local ring mass via background subtraction (QNG-GPU-007, GPU).

Fixes the box-size artifact in global M_ring measurement.

Problem: M_ring = N*sigma_ref - sum(sigma_m) grows with L because bulk
sigma_m is depleted globally by residual phi disorder diffusing from ring.

Fix: subtract a control run (no ring, phi=0) at each L:
  M_real(R, L) = M_global(ring, L) - M_global(control, L)

Physical prediction: M_real should be L-INDEPENDENT (converges to true ring mass).
If it converges -> we have the true canonical baryon mass.
If it still drifts -> measurement protocol has deeper issue.

Scan: L in {20, 30, 40, 50, 60, 80} for R=4 and R=5.
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-local-mass-v1"

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
PHASE3 = 1000

L_VALUES = [20, 30, 40, 50, 60, 80]
RADII    = [4, 5]

# SM reference ratio
RATIO_SM = 1232.0 / 938.3  # Delta / proton = 1.3131


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


def wrap_gpu(a):
    a = a % (2*math.pi)
    return cp.where(a > math.pi, a - 2*math.pi, a)

def nb_mean(f, nb): return f[nb].mean(axis=1)

def disorder(phi, nb):
    pnb = phi[nb]
    return cp.maximum(0.0, 1.0 - cp.sqrt(cp.cos(pnb).mean(axis=1)**2 +
                                          cp.sin(pnb).mean(axis=1)**2))

def phi_wm(phi, sm, nb):
    pnb = phi[nb]; snb = sm[nb]
    tw = snb.sum(axis=1)
    sx = (snb*cp.cos(pnb)).sum(axis=1); sy = (snb*cp.sin(pnb)).sum(axis=1)
    return cp.where(tw > 1e-10, cp.arctan2(sy/cp.maximum(tw,1e-10),
                                            sx/cp.maximum(tw,1e-10)), phi)

def step1(sm, chi, phi, nb):
    smb = nb_mean(sm, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm), 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    np_ = wrap_gpu(phi + BETA_PHI*wrap_gpu(phi_wm(phi,sm,nb) - phi))
    return nsm, nc, np_

def step2(sm, chi, phi, nb):
    smb = nb_mean(sm, nb)
    dis = disorder(phi, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm)
                     - GAMMA_PHI*dis*sm, 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    np_ = wrap_gpu(phi + BETA_PHI*wrap_gpu(phi_wm(phi,sm,nb) - phi))
    return nsm, nc, np_

def step3(sm, phi, nb):
    smb = nb_mean(sm, nb)
    nsm = cp.clip(sm + BETA*(smb-sm), 0.0, 1.0)
    np_ = wrap_gpu(phi + BETA_PHI*wrap_gpu(phi_wm(phi,sm,nb) - phi))
    return nsm, np_

def run_sim(L, phi_init, nb):
    N = L*L*L
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = phi_init.copy()
    for _ in range(PHASE1): sm, chi, phi = step1(sm, chi, phi, nb)
    for _ in range(PHASE2): sm, chi, phi = step2(sm, chi, phi, nb)
    for _ in range(PHASE3): sm, phi = step3(sm, phi, nb)
    return float(N*SIGMA_REF - cp.sum(sm))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("Local ring mass via background subtraction (QNG-GPU-007)")
    print(f"L values: {L_VALUES}  Radii: {RADII}")
    print(f"SM ratio Delta/N = {RATIO_SM:.4f}")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    scan = []
    for L in L_VALUES:
        print(f"=== L={L} ===", flush=True)
        nb = build_nb(L)
        phi_ctrl = cp.zeros(L*L*L, dtype=cp.float64)

        M_ctrl = run_sim(L, phi_ctrl, nb)
        print(f"  Control (no ring): M_ctrl={M_ctrl:.3f}", flush=True)

        row = {"L": L, "M_ctrl": round(M_ctrl, 3)}
        for R in RADII:
            phi_ring = build_phi_ring(L, R)
            M_ring = run_sim(L, phi_ring, nb)
            M_local = M_ring - M_ctrl
            print(f"  R={R}: M_global={M_ring:.2f}  M_local={M_local:.2f}", flush=True)
            row[f"M_global_R{R}"] = round(M_ring, 3)
            row[f"M_local_R{R}"]  = round(M_local, 3)

        ratio_global = row[f"M_global_R5"] / max(row[f"M_global_R4"], 1e-6)
        ratio_local  = row[f"M_local_R5"]  / max(row[f"M_local_R4"],  1e-6)
        row["ratio_global"] = round(ratio_global, 5)
        row["ratio_local"]  = round(ratio_local, 5)
        print(f"  ratio_global={ratio_global:.4f}  ratio_local={ratio_local:.4f}  "
              f"SM={RATIO_SM:.4f}", flush=True)
        print()
        scan.append(row)

    # Convergence analysis
    print("="*70)
    print("CONVERGENCE ANALYSIS")
    print("="*70)
    print(f"{'L':>4}  {'M_local(R4)':>12}  {'M_local(R5)':>12}  "
          f"{'ratio_local':>12}  {'vs_SM%':>8}")
    print("-"*70)
    for r in scan:
        m4 = r[f"M_local_R4"]; m5 = r[f"M_local_R5"]
        rl = r["ratio_local"]
        vs_sm = (rl - RATIO_SM) / RATIO_SM * 100
        print(f"{r['L']:>4}  {m4:>12.2f}  {m5:>12.2f}  {rl:>12.4f}  {vs_sm:>+7.2f}%")

    local_ratios = [r["ratio_local"] for r in scan]
    spread = max(local_ratios) - min(local_ratios)
    last3_spread = max(local_ratios[-3:]) - min(local_ratios[-3:])
    converged = last3_spread < 0.01

    print()
    print(f"Ratio spread (all L): {spread:.4f}")
    print(f"Ratio spread (last 3 L): {last3_spread:.4f}")
    print(f"CONVERGENCE: {'YES' if converged else 'NO'}")
    if converged:
        m4_inf = scan[-1]["M_local_R4"]
        m5_inf = scan[-1]["M_local_R5"]
        ratio_inf = scan[-1]["ratio_local"]
        print(f"  True M(R=4) ~ {m4_inf:.1f}  M(R=5) ~ {m5_inf:.1f}")
        print(f"  True ratio ~ {ratio_inf:.4f}  SM = {RATIO_SM:.4f}  "
              f"diff = {abs(ratio_inf-RATIO_SM)/RATIO_SM*100:.2f}%")

    report = {"params": {"L_values": L_VALUES, "RADII": RADII,
                         "ALPHA": ALPHA, "BETA": BETA,
                         "GAMMA_PHI": GAMMA_PHI, "BETA_PHI": BETA_PHI},
              "SM_ratio": RATIO_SM, "scan": scan,
              "converged": converged, "last3_spread": round(last3_spread, 6)}
    with open(out/"report.json", "w") as f: json.dump(report, f, indent=2)

    lines = ["# Local Ring Mass via Background Subtraction (QNG-GPU-007)", "",
             f"SM ratio Delta/N = {RATIO_SM:.4f}", "",
             "## Results", "",
             "| L | M_ctrl | M_local(R=4) | M_local(R=5) | ratio_local | vs SM% |",
             "|---|--------|-------------|-------------|-------------|--------|"]
    for r in scan:
        m4 = r["M_local_R4"]; m5 = r["M_local_R5"]; rl = r["ratio_local"]
        vs = (rl - RATIO_SM)/RATIO_SM*100
        lines.append(f"| {r['L']} | {r['M_ctrl']:.1f} | {m4:.2f} | {m5:.2f} | "
                     f"{rl:.4f} | {vs:+.2f}% |")
    lines += ["", f"## Convergence: {'YES' if converged else 'NO'}",
              f"Last-3 ratio spread: {last3_spread:.4f}"]
    (out/"summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0 if converged else 1

if __name__ == "__main__":
    raise SystemExit(main())
