from __future__ import annotations

"""v8 windowed mass measurement (QNG-GPU-010, GPU).

Same as GPU-009 but with Channel H active:
  bp_eff(i) = BETA_PHI_MIN + BETA_PHI_RING * depletion(i)
  depletion(i) = max(0, sigma_ref - sigma_m) / sigma_ref

Channel H keeps phi winding INSIDE the ring core.
phi does NOT diffuse into bulk => dep_outer stays near 0.
=> M_windowed should converge with L.

Gate: ratio_windowed converges (last-3 spread < 0.02) AND approaches SM=1.313.

Scan: L in {20, 30, 40, 50, 60, 80} for R=4 and R=5.
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-v8-windowed-mass-v1"

SIGMA_REF    = 0.5
ALPHA        = 0.005
BETA         = 0.35
DELTA_CHI    = 0.20
CHI_DECAY    = 0.020
CHI_REL      = 0.35
GAMMA_PHI    = 0.10

# Channel H parameters
# Inside ring: depletion ~ 0.3-0.6, so bp_eff ~ 0.0005 + 0.06*0.5 = 0.031
# In bulk:     depletion ~ 0,       so bp_eff ~ 0.0005 (nearly frozen)
BETA_PHI_MIN  = 0.0005
BETA_PHI_RING = 0.06

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
    """Phase 1: no Channel F, constant phi diffusion."""
    smb = nb_mean(sm, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm), 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    pm  = phi_wm(phi, sm, nb)
    np_ = wrap_gpu(phi + 0.02*wrap_gpu(pm - phi))  # constant 0.02 in Phase 1
    return nsm, nc, np_

def step2_v8(sm, chi, phi, nb):
    """Phase 2: Channel F + Channel H (depletion-weighted phi diffusion)."""
    smb = nb_mean(sm, nb)
    dis = disorder(phi, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm)
                     - GAMMA_PHI*dis*sm, 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    pm  = phi_wm(phi, sm, nb)
    # Channel H: phi diffuses fast inside ring, slow outside
    dep_norm = cp.maximum(0.0, SIGMA_REF - sm) / SIGMA_REF
    bp_eff   = BETA_PHI_MIN + BETA_PHI_RING * dep_norm
    np_ = wrap_gpu(phi + bp_eff * wrap_gpu(pm - phi))
    return nsm, nc, np_


def mean_depletion(sm, mask):
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
    for _ in range(PHASE2): sm, chi, phi = step2_v8(sm, chi, phi, nb)

    # Global mass
    M_global = float(N*SIGMA_REF - cp.sum(sm))

    # Windowed measurement
    R_inner     = R + 4
    R_outer_min = max(R_inner + 2, L//2 - 6)
    R_outer_max = L//2 - 1

    mask_inner = build_radial_mask(L, 0, R_inner)
    mask_outer = build_radial_mask(L, R_outer_min, R_outer_max)

    dep_inner = mean_depletion(sm, mask_inner)
    dep_outer = mean_depletion(sm, mask_outer)
    N_inner   = float(cp.sum(mask_inner))
    M_windowed = (dep_inner - dep_outer) * N_inner

    # Phi disorder diagnostics
    dis_field  = disorder(phi, nb)
    dis_bulk   = float(cp.mean(dis_field))
    dis_core   = float(cp.sum(dis_field * mask_inner) /
                       max(float(cp.sum(mask_inner)), 1))

    return {
        "L": L, "R": R,
        "M_global":   round(M_global, 2),
        "dep_inner":  round(dep_inner, 6),
        "dep_outer":  round(dep_outer, 6),
        "dep_excess": round(dep_inner - dep_outer, 6),
        "N_inner":    int(N_inner),
        "M_windowed": round(M_windowed, 3),
        "dis_bulk":   round(dis_bulk, 6),
        "dis_core":   round(dis_core, 6),
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("v8 windowed mass measurement (QNG-GPU-010)")
    print(f"L values: {L_VALUES}  Radii: {RADII}")
    print(f"Channel H: bp_min={BETA_PHI_MIN}  bp_ring={BETA_PHI_RING}")
    print(f"SM ratio Delta/N = {RATIO_SM:.4f}")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    all_results = []

    for L in L_VALUES:
        print(f"=== L={L} ===", flush=True)
        nb = build_nb(L)
        for R in RADII:
            res = run_L(L, R, nb)
            all_results.append(res)
            print(f"  R={R}: M_global={res['M_global']:.1f}  "
                  f"dep_inner={res['dep_inner']:.6f}  dep_outer={res['dep_outer']:.6f}  "
                  f"excess={res['dep_excess']:.6f}  M_win={res['M_windowed']:.2f}  "
                  f"dis_bulk={res['dis_bulk']:.5f}  dis_core={res['dis_core']:.5f}",
                  flush=True)

    print()
    print("="*75)
    print("v8 WINDOWED MASS CONVERGENCE")
    print("="*75)
    print(f"{'L':>4}  {'Mw(R4)':>9}  {'Mw(R5)':>9}  {'ratio_w':>8}  "
          f"{'vs_SM%':>7}  {'Mg(R4)':>9}  {'dis_bulk(R4)':>12}")
    print("-"*75)

    scan = []
    for L in L_VALUES:
        r4 = next(r for r in all_results if r["L"]==L and r["R"]==4)
        r5 = next(r for r in all_results if r["L"]==L and r["R"]==5)
        mw4 = r4["M_windowed"]; mw5 = r5["M_windowed"]
        ratio_w = mw5 / max(abs(mw4), 1e-6)
        vs_sm = (ratio_w - RATIO_SM) / RATIO_SM * 100
        print(f"{L:>4}  {mw4:>9.2f}  {mw5:>9.2f}  {ratio_w:>8.4f}  "
              f"{vs_sm:>+6.2f}%  {r4['M_global']:>9.1f}  {r4['dis_bulk']:>12.6f}")
        scan.append({"L": L, "M_win_R4": mw4, "M_win_R5": mw5,
                     "ratio_win": round(ratio_w, 5),
                     "M_global_R4": r4["M_global"],
                     "dis_bulk_R4": r4["dis_bulk"]})

    # Also print dep_excess ratio (simpler metric)
    print()
    print("Excess density ratio dep_excess(R5)/dep_excess(R4):")
    for L in L_VALUES:
        r4 = next(r for r in all_results if r["L"]==L and r["R"]==4)
        r5 = next(r for r in all_results if r["L"]==L and r["R"]==5)
        ex4 = r4["dep_excess"]; ex5 = r5["dep_excess"]
        ratio_ex = ex5 / max(abs(ex4), 1e-9)
        print(f"  L={L:>2}: excess(R4)={ex4:.6f}  excess(R5)={ex5:.6f}  ratio={ratio_ex:.4f}")

    # Convergence
    ratios = [s["ratio_win"] for s in scan]
    last3  = ratios[-3:]
    last3_spread = max(last3) - min(last3)
    converged = last3_spread < 0.02

    print()
    print(f"M_windowed ratio spread (last 3 L): {last3_spread:.4f}")
    print(f"CONVERGENCE: {'YES' if converged else 'NO'}")

    if converged:
        ratio_inf = scan[-1]["ratio_win"]
        diff_pct  = abs(ratio_inf - RATIO_SM) / RATIO_SM * 100
        if diff_pct < 5.0:
            verdict = "CONVERGED_TO_SM"
        else:
            verdict = "CONVERGED_NOT_SM"
        print(f"  ratio_inf ~ {ratio_inf:.4f}  SM = {RATIO_SM:.4f}  diff = {diff_pct:.2f}%")
    else:
        verdict = "NOT_CONVERGED"

    print(f"\nVERDICT: {verdict}")

    # Compare to v7 (GPU-009)
    print()
    print("Comparison v7 (GPU-009) vs v8 Channel H (GPU-010):")
    v7_ratios = {20: 2.2031, 30: 2.0222, 40: 1.9943, 60: 1.9724, 80: 1.9588}
    for s in scan:
        L = s["L"]
        v7 = v7_ratios.get(L, "?")
        v8 = s["ratio_win"]
        if isinstance(v7, float):
            print(f"  L={L:>2}: v7={v7:.4f}  v8={v8:.4f}  SM=1.3130  "
                  f"improvement={'YES' if abs(v8-RATIO_SM) < abs(v7-RATIO_SM) else 'NO'}")

    report = {
        "params": {"L_values": L_VALUES, "RADII": RADII,
                   "PHASE1": PHASE1, "PHASE2": PHASE2,
                   "GAMMA_PHI": GAMMA_PHI,
                   "BETA_PHI_MIN": BETA_PHI_MIN, "BETA_PHI_RING": BETA_PHI_RING},
        "SM_ratio": RATIO_SM,
        "results": all_results,
        "scan": scan,
        "converged": converged,
        "last3_spread": round(last3_spread, 6),
        "verdict": verdict,
    }
    with open(out/"report.json", "w") as f: json.dump(report, f, indent=2)

    lines = ["# v8 Windowed Mass Measurement (QNG-GPU-010)", "",
             f"Channel H: bp_min={BETA_PHI_MIN}  bp_ring={BETA_PHI_RING}",
             f"SM ratio Delta/N = {RATIO_SM:.4f}", "",
             "## Results", "",
             "| L | Mw(R4) | Mw(R5) | ratio_win | vs SM% | M_global(R4) | dis_bulk |",
             "|---|--------|--------|-----------|--------|-------------|----------|"]
    for s in scan:
        vs = (s["ratio_win"] - RATIO_SM) / RATIO_SM * 100
        r4 = next(r for r in all_results if r["L"]==s["L"] and r["R"]==4)
        lines.append(f"| {s['L']} | {s['M_win_R4']:.2f} | {s['M_win_R5']:.2f} | "
                     f"{s['ratio_win']:.4f} | {vs:+.2f}% | {s['M_global_R4']:.1f} | "
                     f"{r4['dis_bulk']:.6f} |")
    lines += ["", f"## Convergence: {'YES' if converged else 'NO'}",
              f"Last-3 spread: {last3_spread:.4f}",
              f"Verdict: {verdict}"]
    (out/"summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0 if converged else 1


if __name__ == "__main__":
    raise SystemExit(main())
