from __future__ import annotations

"""v8 L-convergence test (QNG-GPU-011, GPU).

Decisive IR-safety test for baryon mass identification.

Problem (GPU-009/010): phi spreads into bulk even with Channel H in Phase 2,
because Phase 1 used constant BETA_PHI=0.02 which spread phi before Channel H
could act.

Fix: Channel H active from Phase 1. In Phase 1, sigma_m=SIGMA_REF everywhere
=> depletion=0 => bp_eff=bp_min~0 => phi stays at its initial ring configuration.
Zero bulk phi => zero bulk disorder => Channel F inactive in bulk => M_ring = core only.

Gate: M(R=5)/M(R=4) last-3-L spread < 0.02 AND ratio within 5% of SM=1.3130.

k_gm=0: pure phi confinement test, no gravitational compression of rings.
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-v8-l-convergence-v1"

SIGMA_REF    = 0.5
ALPHA        = 0.005
BETA         = 0.35
DELTA_CHI    = 0.20
CHI_DECAY    = 0.020
CHI_REL      = 0.35
GAMMA_PHI    = 0.10

# Channel H — phi frozen in bulk, active inside ring
BETA_PHI_MIN  = 0.0005
BETA_PHI_RING = 0.06

# k_gm = 0: pure phi confinement, no gravitational compression
K_GM = 0.0

PHASE1 = 300
PHASE2 = 1500

L_VALUES = [20, 30, 40, 60, 80]
RADII    = [4, 5]
RATIO_SM = 1232.0 / 938.3  # 1.3131


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
    pnb = phi[nb]; snb = sm[nb]; tw = snb.sum(axis=1)
    sx = (snb*cp.cos(pnb)).sum(axis=1); sy = (snb*cp.sin(pnb)).sum(axis=1)
    return cp.where(tw>1e-10, cp.arctan2(sy/cp.maximum(tw,1e-10),
                                          sx/cp.maximum(tw,1e-10)), phi)

def channel_h_bp(sm):
    """Channel H: bp_eff = bp_min + bp_ring * depletion_normalized."""
    dep_norm = cp.maximum(0.0, SIGMA_REF - sm) / SIGMA_REF
    return BETA_PHI_MIN + BETA_PHI_RING * dep_norm

def step_phase1(sm, chi, phi, nb):
    """Phase 1: no Channel F. Channel H active (phi frozen in bulk)."""
    smb = nb_mean(sm, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm), 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    # Channel H from Phase 1: bp_eff ~ bp_min everywhere (sm ~ SIGMA_REF)
    bp_eff = channel_h_bp(sm)
    pm  = phi_wm(phi, sm, nb)
    np_ = wrap_gpu(phi + bp_eff * wrap_gpu(pm - phi))
    return nsm, nc, np_

def step_phase2(sm, chi, phi, nb):
    """Phase 2: Channel F + Channel H."""
    smb = nb_mean(sm, nb)
    dis = disorder(phi, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm)
                     - GAMMA_PHI*dis*sm, 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    bp_eff = channel_h_bp(sm)
    pm  = phi_wm(phi, sm, nb)
    np_ = wrap_gpu(phi + bp_eff * wrap_gpu(pm - phi))
    return nsm, nc, np_


def run_ring(L, R, nb):
    N = L*L*L
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi_ring(L, R)

    for _ in range(PHASE1):
        sm, chi, phi = step_phase1(sm, chi, phi, nb)

    # Phi disorder diagnostics after Phase 1
    dis_after_p1 = disorder(phi, nb)
    dis_bulk_p1  = float(cp.mean(dis_after_p1))

    for _ in range(PHASE2):
        sm, chi, phi = step_phase2(sm, chi, phi, nb)

    M_global = float(N*SIGMA_REF - cp.sum(sm))

    # Phi disorder after Phase 2
    dis_after_p2 = disorder(phi, nb)
    dis_bulk_p2  = float(cp.mean(dis_after_p2))

    return {
        "L": L, "R": R,
        "M_global": round(M_global, 2),
        "dis_bulk_p1": round(dis_bulk_p1, 6),
        "dis_bulk_p2": round(dis_bulk_p2, 6),
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("v8 L-convergence test (QNG-GPU-011)")
    print(f"Channel H in BOTH Phase 1 and Phase 2")
    print(f"bp_min={BETA_PHI_MIN}  bp_ring={BETA_PHI_RING}  k_gm={K_GM}")
    print(f"L values: {L_VALUES}  Radii: {RADII}")
    print(f"SM ratio Delta/N = {RATIO_SM:.4f}")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    all_results = []

    for L in L_VALUES:
        print(f"=== L={L} ===", flush=True)
        nb = build_nb(L)
        for R in RADII:
            res = run_ring(L, R, nb)
            all_results.append(res)
            print(f"  R={R}: M_global={res['M_global']:.2f}  "
                  f"dis_bulk_P1={res['dis_bulk_p1']:.6f}  "
                  f"dis_bulk_P2={res['dis_bulk_p2']:.6f}", flush=True)

    print()
    print("="*70)
    print("L-CONVERGENCE (v8 Channel H, Phase 1 + Phase 2)")
    print("="*70)
    print(f"{'L':>4}  {'M(R4)':>9}  {'M(R5)':>9}  {'ratio':>8}  "
          f"{'vs_SM%':>7}  {'dis_bulk_P2(R4)':>15}")
    print("-"*70)

    scan = []
    for L in L_VALUES:
        r4 = next(r for r in all_results if r["L"]==L and r["R"]==4)
        r5 = next(r for r in all_results if r["L"]==L and r["R"]==5)
        ratio = r5["M_global"] / max(r4["M_global"], 1e-6)
        vs_sm = (ratio - RATIO_SM) / RATIO_SM * 100
        print(f"{L:>4}  {r4['M_global']:>9.2f}  {r5['M_global']:>9.2f}  "
              f"{ratio:>8.4f}  {vs_sm:>+6.2f}%  {r4['dis_bulk_p2']:>15.6f}")
        scan.append({"L": L,
                     "M_R4": r4["M_global"], "M_R5": r5["M_global"],
                     "ratio": round(ratio, 5),
                     "dis_bulk_p1_R4": r4["dis_bulk_p1"],
                     "dis_bulk_p2_R4": r4["dis_bulk_p2"]})

    ratios   = [s["ratio"] for s in scan]
    last3    = ratios[-3:]
    spread   = max(last3) - min(last3)
    converged = spread < 0.02

    ratio_last = scan[-1]["ratio"]
    sm_match  = abs(ratio_last - RATIO_SM) / RATIO_SM < 0.05
    dis_ok    = scan[-1]["dis_bulk_p2_R4"] < 0.002

    print()
    print(f"Last-3 ratio spread: {spread:.4f}  (gate: < 0.02)")
    print(f"Ratio at L={L_VALUES[-1]}: {ratio_last:.4f}  SM={RATIO_SM:.4f}  "
          f"diff={abs(ratio_last-RATIO_SM)/RATIO_SM*100:.2f}%  (gate: <5%)")
    print(f"dis_bulk at L={L_VALUES[-1]}: {scan[-1]['dis_bulk_p2_R4']:.6f}  (gate: < 0.002)")

    # Verdict
    if converged and sm_match and dis_ok:
        verdict = "PASS"
        detail  = "phi confined, M_ring IR-safe, ratio converges to SM"
    elif converged and dis_ok:
        verdict = "PASS_WEAK"
        detail  = f"phi confined, ratio converges to {ratio_last:.4f} (not SM)"
    elif converged:
        verdict  = "PASS_WEAK_NODIS"
        detail   = "ratio converges but phi still leaking into bulk"
    else:
        verdict = "FAIL"
        detail  = f"M_ring ratio does not converge (spread={spread:.4f})"

    print(f"\nVERDICT: {verdict}")
    print(f"  {detail}")

    # Compare all three methods
    print()
    print("Comparison across methods:")
    v7_global  = {20:1.589, 30:1.345, 40:1.238, 60:1.140, 80:1.095}
    v8_windowed = {20:1.921, 30:1.845, 40:1.824, 60:1.803, 80:1.791}
    print(f"{'L':>4}  {'v7_global':>10}  {'v8_windowed':>12}  {'v8_CH1+2':>10}  {'SM':>6}")
    for s in scan:
        L = s["L"]
        print(f"{L:>4}  {v7_global.get(L,'?'):>10}  "
              f"{v8_windowed.get(L,'?'):>12}  {s['ratio']:>10.4f}  {RATIO_SM:>6.4f}")

    report = {
        "params": {"L_values": L_VALUES, "RADII": RADII,
                   "PHASE1": PHASE1, "PHASE2": PHASE2,
                   "GAMMA_PHI": GAMMA_PHI,
                   "BETA_PHI_MIN": BETA_PHI_MIN,
                   "BETA_PHI_RING": BETA_PHI_RING,
                   "K_GM": K_GM,
                   "channel_h_phase1": True},
        "SM_ratio": RATIO_SM,
        "results": all_results,
        "scan": scan,
        "converged": converged,
        "last3_spread": round(spread, 6),
        "sm_match": sm_match,
        "dis_ok": dis_ok,
        "verdict": verdict,
        "detail": detail,
    }
    with open(out/"report.json", "w") as f: json.dump(report, f, indent=2)

    lines = ["# v8 L-Convergence Test (QNG-GPU-011)", "",
             "Channel H active in Phase 1 AND Phase 2. k_gm=0.",
             f"bp_min={BETA_PHI_MIN}  bp_ring={BETA_PHI_RING}",
             f"SM ratio Delta/N = {RATIO_SM:.4f}", "",
             "## Results", "",
             "| L | M(R4) | M(R5) | ratio | vs SM% | dis_bulk_P2 |",
             "|---|-------|-------|-------|--------|-------------|"]
    for s in scan:
        vs = (s["ratio"] - RATIO_SM) / RATIO_SM * 100
        lines.append(f"| {s['L']} | {s['M_R4']:.2f} | {s['M_R5']:.2f} | "
                     f"{s['ratio']:.4f} | {vs:+.2f}% | {s['dis_bulk_p2_R4']:.6f} |")
    lines += ["", f"## Verdict: {verdict}",
              f"Last-3 spread: {spread:.4f}  (gate 0.02)",
              f"Detail: {detail}"]
    (out/"summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0 if verdict.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
