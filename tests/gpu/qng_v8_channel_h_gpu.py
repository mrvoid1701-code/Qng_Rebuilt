from __future__ import annotations

"""v8 Channel H: depletion-weighted phi diffusion — GPU.

ROOT CAUSE of ring dissolution (confirmed by ratio scan):
  Channel F erodes sigma_m at ring boundary at CONSTANT rate proportional to gamma.
  Rate never -> 0 regardless of ratio. Late-time rate = 0.0044*ratio (linear scaling).

MECHANISM: phi field (BETA_PHI) diffuses outward from ring core into bulk.
  As winding spreads, disorder becomes non-zero over larger region.
  Channel F depletes sigma_m over this growing region -> constant erosion.

SOLUTION (Channel H): depletion-weighted phi diffusion.
  bp_eff(i) = BETA_PHI_MIN + BETA_PHI_RING * depletion(i)
  depletion(i) = max(0, sigma_ref - sigma_m(i)) / sigma_ref  [0=bulk, ~0.33=ring core]

  phi diffuses fast INSIDE ring (depletion > 0) and barely moves in bulk (depletion~0).
  Winding stays localized -> ring boundary stays sharp -> erosion -> 0.

Physical motivation (Ginzburg-Landau analogy):
  phi = internal phase of vortex (order parameter).
  Order parameter has dynamics only where condensate exists (sigma_m depleted).
  In vacuum (sigma_m = sigma_ref), phi is frozen.

Test matrix (all L=40, R=8, alpha=0.005, gamma=0.005 [ratio=1], 20000 steps):
  v8a: BETA_PHI_MIN=0.0005, BETA_PHI_RING=0.005   [strong localization]
  v8b: BETA_PHI_MIN=0.001,  BETA_PHI_RING=0.005   [moderate localization]
  v8c: BETA_PHI_MIN=0.000,  BETA_PHI_RING=0.010   [full localization, faster ring]
  v8d: BETA_PHI_MIN=0.002,  BETA_PHI_RING=0.005   [weak localization]
  v5:  BETA_PHI=0.005 (constant)                  [baseline — PLATEAU at 0.0044]

Also test ratio=2 with v8b to see if Channel H rescues higher gamma:
  v8b_r2: BETA_PHI_MIN=0.001, BETA_PHI_RING=0.005, gamma=0.010 (ratio=2)

Gate: avg(rate[-8:]) < 0.002 AND decreasing -> PLATEAU->STABLE
      avg(rate[-8:]) < 0.0005             -> STABLE
"""

import json
import math
from pathlib import Path

import cupy as cp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-v8-channel-h-v1"

SIGMA_REF = 0.5
BETA      = 0.35
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35

PHASE1      = 300
PHASE2      = 20000
PRINT_EVERY = 1000

L = 40
R = 8
ALPHA = 0.005

# (label, gamma, bp_min, bp_ring, channel_h)
CONFIGS = [
    ("v5_baseline",  0.005, 0.005,  0.000,  False),  # v5: constant BETA_PHI=0.005
    ("v8a_strong",   0.005, 0.0005, 0.005,  True),   # strong localization
    ("v8b_moderate", 0.005, 0.001,  0.005,  True),   # moderate
    ("v8c_full",     0.005, 0.000,  0.010,  True),   # full localization
    ("v8d_weak",     0.005, 0.002,  0.005,  True),   # weak
    ("v8b_ratio2",   0.010, 0.001,  0.005,  True),   # ratio=2 with Channel H
]

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

def step_gpu(sg, sm, chi, phi, nb_idx, gamma_phi, bp_min, bp_ring, channel_h, channel_f):
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)

    nsg = cp.clip(sg + ALPHA*(SIGMA_REF - sg) + BETA*(sgb - sg), 0.0, 1.0)

    if channel_f:
        dis = disorder_gpu(phi, nb_idx)
        dsm = ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm) - gamma_phi * dis * sm
    else:
        dsm = ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
    nsm = cp.clip(sm + dsm, 0.0, 1.0)

    nc = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA*(SIGMA_REF - sg)

    # Phase update
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

    if channel_h:
        # Channel H: depletion-weighted phi diffusion
        depletion = cp.maximum(0.0, SIGMA_REF - sm) / SIGMA_REF
        bp_eff = bp_min + bp_ring * depletion
    else:
        bp_eff = bp_min  # bp_min = constant BETA_PHI for v5 baseline

    np_ = wrap_gpu(phi + bp_eff * diff)
    return nsg, nsm, nc, np_

def ring_mass_gpu(sm):
    return float(cp.sum(cp.maximum(0.0, SIGMA_REF - sm)))

# ---------------------------------------------------------------------------
# Run one config
# ---------------------------------------------------------------------------

def run_config(gamma_phi, bp_min, bp_ring, channel_h, nb_idx, phi_init):
    N = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = phi_init.copy()

    # Phase 1: no Channel F, constant BETA_PHI (ring formation)
    for _ in range(PHASE1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx,
                                     gamma_phi, bp_min=0.005, bp_ring=0.0,
                                     channel_h=False, channel_f=False)

    track = []; prev_m = ring_mass_gpu(sm)
    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx,
                                     gamma_phi, bp_min, bp_ring,
                                     channel_h, channel_f=True)
        if t % PRINT_EVERY == 0:
            m = ring_mass_gpu(sm)
            rate = (prev_m - m) / PRINT_EVERY
            track.append({"t": t, "M": round(m, 2), "rate": round(rate, 6)})
            prev_m = m
    return track

# ---------------------------------------------------------------------------
# Status + main
# ---------------------------------------------------------------------------

def status(track):
    late = [pt["rate"] for pt in track[-8:]]
    avg = sum(late) / len(late)
    first4 = sum(late[:4]) / 4
    last4  = sum(late[4:]) / 4
    decreasing = last4 < first4 * 0.92
    if avg < 0.0005:                     return "STABLE",         avg, decreasing
    if avg < 0.002 and decreasing:       return "->STABLE",       avg, decreasing
    if avg < 0.002:                      return "NEAR-STABLE",    avg, decreasing
    if avg < 0.010 and decreasing:       return "PLATEAU->",      avg, decreasing
    if avg < 0.010:                      return "PLATEAU",        avg, decreasing
    if avg < 0.05:                       return "SLOWING",        avg, decreasing
    return "DISSOLVING", avg, decreasing

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("v8 Channel H: depletion-weighted phi diffusion (GPU)")
    print(f"L={L}, R={R}, N={L**3}, ALPHA={ALPHA}, PHASE2={PHASE2}")
    print("Channel H: bp_eff = bp_min + bp_ring * depletion(sigma_m)")
    print("Gate STABLE: avg(rate[-8:]) < 0.0005")
    print("Gate ->STABLE: avg < 0.002 AND decreasing")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB")
    print()

    print("Building geometry...", flush=True)
    nb_idx   = build_neighbor_arrays(L)
    phi_init = build_phi_init(L, R)
    print("Done.\n", flush=True)

    all_results = []

    for label, gamma, bp_min, bp_ring, ch in CONFIGS:
        ratio = gamma / ALPHA
        print(f"{'='*60}")
        print(f"{label}  gamma={gamma}  ratio={ratio:.1f}  "
              f"bp_min={bp_min}  bp_ring={bp_ring}  ch_h={ch}", flush=True)
        print(f"{'='*60}")

        track = run_config(gamma, bp_min, bp_ring, ch, nb_idx, phi_init)
        st, avg, dec = status(track)
        peak  = max(pt["M"] for pt in track)
        final = track[-1]["M"]

        for pt in track:
            tag = ""
            if pt["rate"] < 0.0005:   tag = "  *** STABLE ***"
            elif pt["rate"] < 0.002:  tag = "  ** near-stable **"
            elif pt["rate"] < 0.010:  tag = "  * plateau *"
            print(f"  T={pt['t']:6d}  M={pt['M']:9.1f}  rate={pt['rate']:.6f}{tag}",
                  flush=True)

        dec_str = "dec" if dec else "flat"
        print(f"  >> peak={peak:.1f}  final={final:.1f}  "
              f"late_rate={avg:.6f}  trend={dec_str}  [{st}]")
        print()

        all_results.append({
            "label": label, "gamma": gamma, "ratio": ratio,
            "bp_min": bp_min, "bp_ring": bp_ring, "channel_h": ch,
            "peak": peak, "final": final,
            "late_rate": round(avg, 6), "status": st,
            "decreasing": dec, "track": track,
        })

    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'label':<18} {'ratio':>5} {'bp_min':>7} {'late_rate':>10} {'trend':>6} {'status'}")
    print("-"*65)
    for r in all_results:
        tr = "dec" if r["decreasing"] else "flat"
        print(f"  {r['label']:<16} {r['ratio']:4.1f}   {r['bp_min']:.4f}   "
              f"{r['late_rate']:.6f}   {tr:>4}   {r['status']}")

    best = min(all_results, key=lambda r: r["late_rate"])
    print(f"\nBest: {best['label']}  rate={best['late_rate']:.6f}  [{best['status']}]")

    # Verdict
    stable = [r for r in all_results if r["status"] in ("STABLE", "->STABLE")]
    if stable:
        print(f"\n*** CHANNEL H WORKS: {len(stable)} config(s) approach stability ***")
        for r in stable:
            print(f"  {r['label']}: rate={r['late_rate']:.6f}  [{r['status']}]")
    else:
        baseline = next(r for r in all_results if r["label"] == "v5_baseline")
        improvements = [r for r in all_results if r["late_rate"] < baseline["late_rate"] * 0.5]
        if improvements:
            print(f"\nChannel H reduces rate significantly (>2x) in {len(improvements)} config(s):")
            for r in improvements:
                ratio_improvement = baseline["late_rate"] / r["late_rate"]
                print(f"  {r['label']}: rate={r['late_rate']:.6f} ({ratio_improvement:.1f}x better than v5)")
        else:
            print(f"\nChannel H does not significantly improve stability. Need different approach.")

    report = {
        "params": {"L": L, "R": R, "ALPHA": ALPHA, "PHASE1": PHASE1, "PHASE2": PHASE2},
        "results": all_results,
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# v8 Channel H: Depletion-Weighted Phi Diffusion (GPU)", "",
             f"L={L}, R={R}, ALPHA={ALPHA}, PHASE2={PHASE2}", "",
             "| label | ratio | bp_min | bp_ring | M_final | late_rate | trend | status |",
             "|-------|-------|--------|---------|---------|-----------|-------|--------|"]
    for r in all_results:
        tr = "dec" if r["decreasing"] else "flat"
        lines.append(f"| {r['label']} | {r['ratio']:.1f} | {r['bp_min']} | {r['bp_ring']} | "
                     f"{r['final']:.1f} | {r['late_rate']:.6f} | {tr} | {r['status']} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
