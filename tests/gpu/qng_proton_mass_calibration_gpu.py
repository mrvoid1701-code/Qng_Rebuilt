from __future__ import annotations

"""Proton mass calibration: find k_gm such that M_stable(R=4)/M_stable(R=5) = 0.7616.

From v8+v7 combined test:
  v7h_a (k_gm=0.01, R=8): M_stable=36.0, STABLE
  v7h_b (k_gm=0.05, R=8): M_stable=2.4,  STABLE
  v7h_c (k_gm=0.10, R=8): M_stable=0.7,  STABLE

Now test R=4 (proton candidate) and R=5 (Delta candidate) at each k_gm.

Physical constraint:
  M_stable(R=4) / M_stable(R=5) = m_proton / m_Delta = 938.27 / 1232.0 = 0.7616

If ratio is preserved under gravitational compression:
  -> k_gm is free, only a_M changes (ratio test PASS)
If ratio depends on k_gm:
  -> k_gm is fixed by physics (ratio selects k_gm)

k_gm scan: {0.005, 0.010, 0.020, 0.050}
For each k_gm: run R=4 and R=5 to T=40000 with Channel H + back-reaction.
Measure M_stable and ratio.

Also extract: does M_stable(R=4)/M_stable(R=5) match 0.7616?
And: a_M = m_proton_MeV / M_stable(R=4) (in substrate units)
"""

import json
import math
from pathlib import Path

import cupy as cp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-proton-mass-calibration-v1"

SIGMA_REF = 0.5
BETA      = 0.35
BETA_G    = 0.35
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
ALPHA     = 0.005
ALPHA_G   = 0.005
GAMMA_PHI = 0.005   # ratio=1
BP_MIN    = 0.001
BP_RING   = 0.005

PHASE1      = 300
PHASE2      = 40000
PRINT_EVERY = 2000

L = 40

# Physical target
M_PROTON_MEV  = 938.272
M_DELTA_MEV   = 1232.0
RATIO_TARGET  = M_PROTON_MEV / M_DELTA_MEV   # 0.7616

K_GM_SCAN = [0.005, 0.010, 0.020, 0.050]
RADII     = [4, 5]

# ---------------------------------------------------------------------------
# GPU geometry
# ---------------------------------------------------------------------------

def build_neighbor_arrays(L):
    import numpy as np
    N = L * L * L
    nb_cpu = np.zeros((N, 6), dtype=np.int32)
    for x in range(L):
        for y in range(L):
            for z in range(L):
                i = x * L * L + y * L + z
                nb_cpu[i, 0] = ((x-1) % L) * L * L + y * L + z
                nb_cpu[i, 1] = ((x+1) % L) * L * L + y * L + z
                nb_cpu[i, 2] = x * L * L + ((y-1) % L) * L + z
                nb_cpu[i, 3] = x * L * L + ((y+1) % L) * L + z
                nb_cpu[i, 4] = x * L * L + y * L + (z-1) % L
                nb_cpu[i, 5] = x * L * L + y * L + (z+1) % L
    return cp.asarray(nb_cpu)

def build_phi_init(L, ring_r):
    import numpy as np
    N = L * L * L
    RX = RY = RZ = L // 2
    phi = np.zeros(N, dtype=np.float64)
    for x in range(L):
        for y in range(L):
            for z in range(L):
                i = x * L * L + y * L + z
                dx = x - RX; dy = y - RY; dz = z - RZ
                if dx >  L/2: dx -= L
                if dx < -L/2: dx += L
                if dy >  L/2: dy -= L
                if dy < -L/2: dy += L
                if dz >  L/2: dz -= L
                if dz < -L/2: dz += L
                rho = math.sqrt(dx*dx + dy*dy)
                phi[i] = math.atan2(dz, rho - ring_r)
    return cp.asarray(phi)

def wrap_gpu(a):
    a = a % (2 * math.pi)
    return cp.where(a > math.pi, a - 2 * math.pi, a)

def nb_mean(field, nb_idx):
    return field[nb_idx].mean(axis=1)

def disorder_gpu(phi, nb_idx):
    phi_nb = phi[nb_idx]
    sx = cp.cos(phi_nb).mean(axis=1)
    sy = cp.sin(phi_nb).mean(axis=1)
    return cp.maximum(0.0, 1.0 - cp.sqrt(sx*sx + sy*sy))

def step_gpu(sg, sm, chi, phi, nb_idx, k_gm, channel_f):
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)

    nsg = cp.clip(
        sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg)
           - k_gm * cp.maximum(0.0, SIGMA_REF - sm),
        0.0, 1.0
    )

    if channel_f:
        dis = disorder_gpu(phi, nb_idx)
        dsm = (ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
               - GAMMA_PHI * dis * sm
               + k_gm * cp.maximum(0.0, SIGMA_REF - sg))
    else:
        dsm = ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
    nsm = cp.clip(sm + dsm, 0.0, 1.0)

    nc = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA*(SIGMA_REF - sg)

    phi_nb = phi[nb_idx]
    sm_nb  = sm[nb_idx]
    tw  = sm_nb.sum(axis=1)
    sx2 = (sm_nb * cp.cos(phi_nb)).sum(axis=1)
    sy2 = (sm_nb * cp.sin(phi_nb)).sum(axis=1)
    pm  = cp.where(tw > 1e-10,
                   cp.arctan2(sy2 / cp.maximum(tw, 1e-10),
                              sx2 / cp.maximum(tw, 1e-10)),
                   phi)
    diff = wrap_gpu(pm - phi)
    depletion = cp.maximum(0.0, SIGMA_REF - sm) / SIGMA_REF
    bp_eff = BP_MIN + BP_RING * depletion
    np_ = wrap_gpu(phi + bp_eff * diff)

    return nsg, nsm, nc, np_

def ring_mass_gpu(sm):
    return float(cp.sum(cp.maximum(0.0, SIGMA_REF - sm)))

def run_ring(k_gm, ring_r, nb_idx, phi_init):
    N = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = phi_init.copy()

    for _ in range(PHASE1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx,
                                     k_gm=0.0, channel_f=False)

    track = []; prev_m = ring_mass_gpu(sm)
    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx,
                                     k_gm, channel_f=True)
        if t % PRINT_EVERY == 0:
            m = ring_mass_gpu(sm)
            rate = (prev_m - m) / PRINT_EVERY
            track.append({"t": t, "M": round(m, 4), "rate": round(rate, 7)})
            prev_m = m
    return track

def stable_mass(track):
    """Average M over last 5 points as stable mass estimate."""
    late = [pt["M"] for pt in track[-5:]]
    return sum(late) / len(late)

def late_rate(track):
    late = [pt["rate"] for pt in track[-5:]]
    return sum(late) / len(late)

def is_stable(track):
    return late_rate(track) < 0.001

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("Proton mass calibration (GPU)")
    print(f"L={L}, ALPHA={ALPHA}, GAMMA={GAMMA_PHI}, PHASE2={PHASE2}")
    print(f"Target ratio M(R=4)/M(R=5) = {RATIO_TARGET:.4f} (proton/Delta)")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    print("Building geometry...", flush=True)
    nb_idx = build_neighbor_arrays(L)
    phi_inits = {R: build_phi_init(L, R) for R in RADII}
    print("Done.\n", flush=True)

    all_results = []

    for k_gm in K_GM_SCAN:
        print(f"{'='*60}")
        print(f"k_gm={k_gm}", flush=True)
        print(f"{'='*60}")

        ring_results = {}

        for R in RADII:
            print(f"\n  R={R}  (proton=R4, delta=R5)", flush=True)
            track = run_ring(k_gm, R, nb_idx, phi_inits[R])
            ring_results[R] = track

            for pt in track:
                tag = ""
                if 0.0 <= pt["rate"] < 0.0005:   tag = "  *** STABLE ***"
                elif pt["rate"] < 0.002:           tag = "  ** near-stable **"
                elif pt["rate"] < 0.010:           tag = "  * plateau *"
                print(f"    T={pt['t']:6d}  M={pt['M']:9.4f}  "
                      f"rate={pt['rate']:.7f}{tag}", flush=True)

            M_s = stable_mass(track)
            lr  = late_rate(track)
            stab = "STABLE" if is_stable(track) else "DISSOLVING"
            print(f"  >> R={R}  M_stable={M_s:.4f}  late_rate={lr:.7f}  [{stab}]")

        # Compute ratio
        M4 = stable_mass(ring_results[4])
        M5 = stable_mass(ring_results[5])
        ratio = M4 / M5 if M5 > 0 else float("nan")
        ratio_err = abs(ratio - RATIO_TARGET) / RATIO_TARGET * 100
        stab4 = is_stable(ring_results[4])
        stab5 = is_stable(ring_results[5])

        # a_M calibration: m_proton_MeV = a_M * M_stable(R=4)
        a_M = M_PROTON_MEV / M4 if M4 > 0 else float("nan")
        M5_pred = M_PROTON_MEV / a_M * (M_DELTA_MEV / M_PROTON_MEV) if M4 > 0 else 0

        print(f"\n  k_gm={k_gm}:")
        print(f"    M_stable(R=4) = {M4:.4f}")
        print(f"    M_stable(R=5) = {M5:.4f}")
        print(f"    ratio = {ratio:.4f}  (target={RATIO_TARGET:.4f}  err={ratio_err:.2f}%)")
        print(f"    a_M = {a_M:.6e} MeV/substrate_unit")
        print(f"    both stable: {stab4 and stab5}")
        print()

        all_results.append({
            "k_gm": k_gm,
            "M4": round(M4, 4), "M5": round(M5, 4),
            "ratio": round(ratio, 6),
            "ratio_target": RATIO_TARGET,
            "ratio_err_pct": round(ratio_err, 3),
            "a_M": a_M,
            "stable4": stab4, "stable5": stab5,
            "tracks": {str(R): ring_results[R] for R in RADII},
        })

    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'k_gm':>8} {'M(R=4)':>10} {'M(R=5)':>10} "
          f"{'ratio':>8} {'err%':>7} {'stable':>8} {'a_M (MeV/unit)'}")
    print("-"*75)
    for r in all_results:
        stab = "BOTH" if (r["stable4"] and r["stable5"]) else ("R4" if r["stable4"] else "NONE")
        print(f"  {r['k_gm']:6.3f}   {r['M4']:9.4f}   {r['M5']:9.4f}   "
              f"{r['ratio']:7.4f}   {r['ratio_err_pct']:5.2f}%   {stab:>6}   "
              f"{r['a_M']:.4e}")

    # Best match
    stable_both = [r for r in all_results if r["stable4"] and r["stable5"]]
    if stable_both:
        best = min(stable_both, key=lambda r: r["ratio_err_pct"])
        print(f"\nBest ratio match: k_gm={best['k_gm']}")
        print(f"  ratio={best['ratio']:.4f} (err={best['ratio_err_pct']:.2f}%)")
        print(f"  a_M = {best['a_M']:.4e} MeV/substrate_unit")
        print(f"  M_stable(R=4) = {best['M4']:.4f} -> m_proton = {best['a_M']*best['M4']:.1f} MeV")
        print(f"  M_stable(R=5) = {best['M5']:.4f} -> m_Delta  = {best['a_M']*best['M5']:.1f} MeV")

        # Check conservation: same ratio as before?
        print(f"\n  Previous a_M (CPU-074/075 protocol): 1.373e-3 substrate units")
        print(f"  New a_M with back-reaction: {best['a_M']:.4e} MeV/substrate_unit")

    report = {
        "params": {"L": L, "ALPHA": ALPHA, "GAMMA": GAMMA_PHI,
                   "BP_MIN": BP_MIN, "BP_RING": BP_RING,
                   "PHASE1": PHASE1, "PHASE2": PHASE2},
        "ratio_target": RATIO_TARGET,
        "results": [{k: v for k, v in r.items() if k != "tracks"}
                    for r in all_results],
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# Proton Mass Calibration (GPU)", "",
             f"L={L}, ALPHA={ALPHA}, GAMMA={GAMMA_PHI}, PHASE2={PHASE2}",
             f"Target ratio M(R=4)/M(R=5) = {RATIO_TARGET:.4f}", "",
             "| k_gm | M(R=4) | M(R=5) | ratio | err% | stable | a_M |",
             "|------|--------|--------|-------|------|--------|-----|"]
    for r in all_results:
        stab = "BOTH" if (r["stable4"] and r["stable5"]) else "partial"
        lines.append(f"| {r['k_gm']} | {r['M4']:.4f} | {r['M5']:.4f} | "
                     f"{r['ratio']:.4f} | {r['ratio_err_pct']:.2f}% | "
                     f"{stab} | {r['a_M']:.4e} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
