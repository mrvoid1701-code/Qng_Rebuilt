from __future__ import annotations

"""Windowed local mass measurement (QNG-GPU-009, GPU).

Problem: global M_ring = N*sigma_ref - sum(sigma_m) diverges with L
because phi diffuses into bulk and Channel F depletes sigma_m globally.

Solution: differential measurement
  M_real(R, L) = mean_depletion(r < R_inner) - mean_depletion(r > R_outer)

where:
  mean_depletion(region) = mean(sigma_ref - sigma_m | sites in region)
  R_inner = R + 4  (captures ring core)
  R_outer = L//2 - 4  (far background, same-volume shell)

Physical prediction:
  If phi bulk depletion is uniform, subtracting the far-background removes it.
  M_real should be L-INDEPENDENT => converges to true canonical ring mass.

If it converges: we have the true baryon masses.
If it still drifts: substrate has a deeper problem with phi confinement.

Scan: L in {20, 30, 40, 50, 60, 80} for R=4 and R=5.
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-windowed-mass-v1"

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

L_VALUES = [20, 30, 40, 50, 60, 80]
RADII    = [4, 5]

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


def build_radial_mask(L, r_min, r_max):
    """Boolean mask for sites with r_min <= |r| < r_max from center."""
    cx = cy = cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg-cx; dy = yg-cy; dz = zg-cz
    for d in [dx, dy, dz]:
        d[:] = np.where(d >  L/2, d-L, d)
        d[:] = np.where(d < -L/2, d+L, d)
    r2 = (dx*dx + dy*dy + dz*dz).ravel()
    return cp.asarray((r2 >= r_min*r_min) & (r2 < r_max*r_max))


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


def mean_depletion(sm, mask):
    """Mean depletion = mean(sigma_ref - sigma_m) over masked sites."""
    dep = cp.maximum(0.0, SIGMA_REF - sm)
    n = float(cp.sum(mask))
    if n < 1:
        return 0.0
    return float(cp.sum(dep * mask)) / n


def run_L(L, R, nb):
    N = L*L*L
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi_ring(L, R)

    for _ in range(PHASE1): sm, chi, phi = step1(sm, chi, phi, nb)
    for _ in range(PHASE2): sm, chi, phi = step2(sm, chi, phi, nb)

    # Global mass (old method)
    M_global = float(N*SIGMA_REF - cp.sum(sm))

    # Windowed measurement
    # Inner shell: sphere of radius R + 4 (captures ring core, tube, near field)
    R_inner = R + 4
    # Outer shell: annulus from (L//2 - 6) to (L//2 - 1) -- far background
    R_outer_min = max(R_inner + 2, L//2 - 6)
    R_outer_max = L//2 - 1

    mask_inner = build_radial_mask(L, 0, R_inner)
    mask_outer = build_radial_mask(L, R_outer_min, R_outer_max)

    dep_inner = mean_depletion(sm, mask_inner)
    dep_outer = mean_depletion(sm, mask_outer)

    # Differential: local excess depletion at ring vs bulk background
    # Scale by volume of inner region to get an extensive mass proxy
    N_inner = float(cp.sum(mask_inner))
    M_windowed = (dep_inner - dep_outer) * N_inner

    # Also measure bulk phi disorder for diagnostics
    dis_field = disorder(phi, nb)
    dis_bulk = float(cp.mean(dis_field))
    dis_core = float(cp.sum(dis_field * mask_inner) / max(float(cp.sum(mask_inner)), 1))

    return {
        "L": L, "R": R,
        "M_global": round(M_global, 2),
        "dep_inner": round(dep_inner, 6),
        "dep_outer": round(dep_outer, 6),
        "dep_excess": round(dep_inner - dep_outer, 6),
        "N_inner": int(N_inner),
        "M_windowed": round(M_windowed, 3),
        "dis_bulk": round(dis_bulk, 6),
        "dis_core": round(dis_core, 6),
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("Windowed local mass measurement (QNG-GPU-009)")
    print(f"L values: {L_VALUES}  Radii: {RADII}")
    print(f"SM ratio Delta/N = {RATIO_SM:.4f}")
    print(f"Method: M_windowed = (dep_inner - dep_outer) * N_inner")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    all_results = []

    for L in L_VALUES:
        print(f"=== L={L} ===", flush=True)
        nb = build_nb(L)
        row = {"L": L}
        for R in RADII:
            res = run_L(L, R, nb)
            all_results.append(res)
            row[f"R{R}"] = res
            print(f"  R={R}: M_global={res['M_global']:.1f}  "
                  f"dep_inner={res['dep_inner']:.6f}  dep_outer={res['dep_outer']:.6f}  "
                  f"excess={res['dep_excess']:.6f}  M_windowed={res['M_windowed']:.2f}  "
                  f"dis_bulk={res['dis_bulk']:.5f}", flush=True)

    print()
    print("="*70)
    print("WINDOWED MASS CONVERGENCE")
    print("="*70)
    print(f"{'L':>4}  {'M_win(R4)':>11}  {'M_win(R5)':>11}  "
          f"{'ratio_win':>10}  {'vs_SM%':>8}  {'M_glob(R4)':>11}")
    print("-"*70)

    scan = []
    for L in L_VALUES:
        r4 = next(r for r in all_results if r["L"]==L and r["R"]==4)
        r5 = next(r for r in all_results if r["L"]==L and r["R"]==5)
        mw4 = r4["M_windowed"]; mw5 = r5["M_windowed"]
        ratio_w = mw5 / max(mw4, 1e-6)
        vs_sm = (ratio_w - RATIO_SM) / RATIO_SM * 100
        print(f"{L:>4}  {mw4:>11.2f}  {mw5:>11.2f}  "
              f"{ratio_w:>10.4f}  {vs_sm:>+7.2f}%  {r4['M_global']:>11.1f}")
        scan.append({"L": L, "M_win_R4": mw4, "M_win_R5": mw5,
                     "ratio_win": round(ratio_w, 5),
                     "M_global_R4": r4["M_global"]})

    # Convergence check
    ratios = [s["ratio_win"] for s in scan]
    last3_spread = max(ratios[-3:]) - min(ratios[-3:])
    converged = last3_spread < 0.01

    print()
    print(f"Ratio spread (last 3 L): {last3_spread:.4f}")
    print(f"CONVERGENCE: {'YES' if converged else 'NO'}")
    if converged:
        ratio_inf = scan[-1]["ratio_win"]
        print(f"  True ratio ~ {ratio_inf:.4f}  SM = {RATIO_SM:.4f}  "
              f"diff = {abs(ratio_inf-RATIO_SM)/RATIO_SM*100:.2f}%")

    # Verdict
    if converged and abs(scan[-1]["ratio_win"] - RATIO_SM) < 0.05:
        verdict = "CONVERGED_TO_SM"
    elif converged:
        verdict = "CONVERGED_NOT_SM"
    else:
        verdict = "NOT_CONVERGED"

    print(f"\nVERDICT: {verdict}")

    report = {
        "params": {"L_values": L_VALUES, "RADII": RADII,
                   "PHASE1": PHASE1, "PHASE2": PHASE2,
                   "GAMMA_PHI": GAMMA_PHI, "BETA_PHI": BETA_PHI},
        "SM_ratio": RATIO_SM,
        "results": all_results,
        "scan": scan,
        "converged": converged,
        "last3_spread": round(last3_spread, 6),
        "verdict": verdict,
    }
    with open(out/"report.json", "w") as f: json.dump(report, f, indent=2)

    lines = ["# Windowed Mass Measurement (QNG-GPU-009)", "",
             f"SM ratio Delta/N = {RATIO_SM:.4f}", "",
             "## Method",
             "M_windowed = (dep_inner - dep_outer) * N_inner",
             "dep_inner = mean(sigma_ref - sigma_m | r < R+4)",
             "dep_outer = mean(sigma_ref - sigma_m | r > L/2-6)",
             "",
             "## Results", "",
             "| L | M_win(R4) | M_win(R5) | ratio_win | vs SM% | M_global(R4) |",
             "|---|-----------|-----------|-----------|--------|-------------|"]
    for s in scan:
        vs = (s["ratio_win"] - RATIO_SM) / RATIO_SM * 100
        lines.append(f"| {s['L']} | {s['M_win_R4']:.2f} | {s['M_win_R5']:.2f} | "
                     f"{s['ratio_win']:.4f} | {vs:+.2f}% | {s['M_global_R4']:.1f} |")
    lines += ["", f"## Convergence: {'YES' if converged else 'NO'}",
              f"Last-3 spread: {last3_spread:.4f}",
              f"Verdict: {verdict}"]
    (out/"summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0 if converged else 1


if __name__ == "__main__":
    raise SystemExit(main())
