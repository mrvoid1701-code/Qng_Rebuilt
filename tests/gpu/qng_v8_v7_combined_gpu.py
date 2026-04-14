from __future__ import annotations

"""v8 + v7 combined: Channel H (phi localization) + two-field substrate + back-reaction.

ROOT CAUSE ANALYSIS:
  - v5 baseline: rate=0.0044 FLAT (phi spreads, ring erodes at constant rate)
  - Channel H alone: rate minimum ~0.001 at T=50000, then bounces back
    -> phi stays localized but ring still SHRINKS because sigma_m has no restoring force
  - Missing: gravitational back-reaction (v7-symmetric)

THREE MECHANISMS COMBINED:
  1. Channel F: -gamma * disorder * sigma_m  (ring formation via phi winding)
  2. Channel H: bp_eff = bp_min + bp_ring * depletion  (phi stays at ring)
  3. Channel G (v7): sigma_g -= k_gm * (sigma_m_ref - sigma_m)  (matter sources gravity)
     + back-reaction: sigma_m += k_gm * (sigma_g - sigma_g_ref)  (gravity traps matter)

PHYSICAL PICTURE:
  - Ring depletes sigma_m -> sigma_g develops a well (Channel G)
  - sigma_g well pulls sigma_m back into depletion (back-reaction)
  - Channel H keeps phi winding localized at the ring
  - Result: ring is trapped in its own gravitational well, cannot shrink

Test matrix (L=40, R=8, alpha=0.005, gamma=0.005, 60000 steps):
  v7h_a: k_gm=0.01  + Channel H (bp_min=0.001, bp_ring=0.005)
  v7h_b: k_gm=0.05  + Channel H
  v7h_c: k_gm=0.10  + Channel H  [standard k_gm from CPU-064+]
  v7h_d: k_gm=0.10  + no Channel H  [v7 alone, no phi localization]
  v8_ref: k_gm=0    + Channel H  [Channel H alone, reference]

Gate STABLE: avg(rate[-10:]) < 0.0005 AND |d(rate)/dt| < 0.0001 (flat near zero)
"""

import json
import math
from pathlib import Path

import cupy as cp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-v8-v7-combined-v1"

SIGMA_REF   = 0.5
BETA        = 0.35
BETA_G      = 0.35
DELTA       = 0.20
CHI_DECAY   = 0.020
CHI_REL     = 0.35
ALPHA       = 0.005
GAMMA_PHI   = 0.005   # ratio=1
ALPHA_G     = 0.005

PHASE1      = 300
PHASE2      = 60000
PRINT_EVERY = 2000

L = 40
R = 8

# (label, k_gm, bp_min, bp_ring, channel_h)
CONFIGS = [
    ("v8_ref",   0.000, 0.001, 0.005, True),   # Channel H only, no gravity
    ("v7h_a",    0.010, 0.001, 0.005, True),    # weak gravity + Channel H
    ("v7h_b",    0.050, 0.001, 0.005, True),    # medium gravity + Channel H
    ("v7h_c",    0.100, 0.001, 0.005, True),    # standard gravity + Channel H
    ("v7_only",  0.100, 0.005, 0.000, False),   # v7 back-reaction, no Channel H
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

def step_gpu(sg, sm, chi, phi, nb_idx,
             k_gm, bp_min, bp_ring, channel_h, channel_f):
    N = sg.shape[0]

    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)

    # sigma_g update (Channel A_g + diffusion + Channel G coupling)
    nsg = cp.clip(
        sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg)
           - k_gm * cp.maximum(0.0, SIGMA_REF - sm),   # Channel G: matter -> gravity well
        0.0, 1.0
    )

    # sigma_m update (Channel A_m + diffusion + Channel F + back-reaction)
    if channel_f:
        dis = disorder_gpu(phi, nb_idx)
        dsm = (ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
               - GAMMA_PHI * dis * sm                          # Channel F
               + k_gm * cp.maximum(0.0, SIGMA_REF - sg))      # back-reaction: gravity traps matter
    else:
        dsm = ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
    nsm = cp.clip(sm + dsm, 0.0, 1.0)

    # chi (couples to sigma_g)
    nc = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA*(SIGMA_REF - sg)

    # phi update with optional Channel H
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
        depletion = cp.maximum(0.0, SIGMA_REF - sm) / SIGMA_REF
        bp_eff = bp_min + bp_ring * depletion
    else:
        bp_eff = bp_min  # constant BETA_PHI

    np_ = wrap_gpu(phi + bp_eff * diff)
    return nsg, nsm, nc, np_

def ring_mass_gpu(sm):
    return float(cp.sum(cp.maximum(0.0, SIGMA_REF - sm)))

def run_config(k_gm, bp_min, bp_ring, channel_h, nb_idx, phi_init):
    N = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = phi_init.copy()

    # Phase 1: no Channel F, constant bp, no k_gm coupling
    for _ in range(PHASE1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx,
                                     k_gm=0.0, bp_min=0.005, bp_ring=0.0,
                                     channel_h=False, channel_f=False)

    track = []
    prev_m = ring_mass_gpu(sm)
    first_stable_t = None

    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx,
                                     k_gm, bp_min, bp_ring,
                                     channel_h, channel_f=True)
        if t % PRINT_EVERY == 0:
            m = ring_mass_gpu(sm)
            rate = (prev_m - m) / PRINT_EVERY
            track.append({"t": t, "M": round(m, 2), "rate": round(rate, 6)})
            prev_m = m
            if rate < 0.0005 and rate >= 0.0 and first_stable_t is None:
                first_stable_t = t
                print(f"  *** STABLE GATE at T={t} rate={rate:.6f} ***", flush=True)

    return track, first_stable_t

# ---------------------------------------------------------------------------
# Status + main
# ---------------------------------------------------------------------------

def status(track):
    # Use last 10 points
    late = [pt["rate"] for pt in track[-10:]]
    avg  = sum(late) / len(late)
    first5 = sum(late[:5]) / 5
    last5  = sum(late[5:]) / 5
    dec = last5 < first5 * 0.92
    flat_near_zero = avg < 0.0008 and not dec

    if avg < 0.0005:                  return "STABLE",     avg, dec
    if avg < 0.0015 and dec:          return "->STABLE",   avg, dec
    if flat_near_zero:                return "NEAR-ZERO",  avg, dec
    if avg < 0.002 and dec:           return "->STABLE",   avg, dec
    if avg < 0.002:                   return "NEAR-STAB",  avg, dec
    if avg < 0.010 and dec:           return "PLATEAU->",  avg, dec
    if avg < 0.010:                   return "PLATEAU",    avg, dec
    return "SLOWING", avg, dec

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("v8 + v7 combined: Channel H + two-field + back-reaction (GPU)")
    print(f"L={L}, R={R}, N={L**3}, ALPHA={ALPHA}, GAMMA={GAMMA_PHI}, PHASE2={PHASE2}")
    print("Gate STABLE: rate < 0.0005 (positive)")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    print("Building geometry...", flush=True)
    nb_idx   = build_neighbor_arrays(L)
    phi_init = build_phi_init(L, R)
    print("Done.\n", flush=True)

    all_results = []

    for label, k_gm, bp_min, bp_ring, ch_h in CONFIGS:
        print(f"{'='*60}")
        print(f"{label}  k_gm={k_gm}  bp_min={bp_min}  "
              f"bp_ring={bp_ring}  ch_h={ch_h}", flush=True)
        print(f"{'='*60}")

        track, stable_t = run_config(k_gm, bp_min, bp_ring, ch_h, nb_idx, phi_init)
        st, avg, dec = status(track)
        peak  = max(pt["M"] for pt in track)
        final = track[-1]["M"]

        for pt in track:
            tag = ""
            if   0.0 <= pt["rate"] < 0.0005:  tag = "  *** STABLE ***"
            elif pt["rate"] < 0.002:           tag = "  ** near-stable **"
            elif pt["rate"] < 0.010:           tag = "  * plateau *"
            print(f"  T={pt['t']:6d}  M={pt['M']:9.1f}  rate={pt['rate']:.6f}{tag}",
                  flush=True)

        dec_str  = "dec" if dec else "flat"
        stab_str = f"  STABLE@T={stable_t}" if stable_t else ""
        print(f"  >> peak={peak:.1f}  final={final:.1f}  "
              f"late_rate={avg:.6f}  [{dec_str}]  [{st}]{stab_str}")
        print()

        all_results.append({
            "label": label, "k_gm": k_gm,
            "bp_min": bp_min, "bp_ring": bp_ring, "channel_h": ch_h,
            "peak": peak, "final": final,
            "late_rate": round(avg, 6), "status": st,
            "decreasing": dec, "first_stable_t": stable_t,
            "track": track,
        })

    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'label':<12} {'k_gm':>6} {'ch_h':>5} {'M_final':>9} "
          f"{'late_rate':>10} {'trend':>5} {'status'}")
    print("-"*65)
    for r in all_results:
        tr = "dec" if r["decreasing"] else "flat"
        st_t = f"T={r['first_stable_t']}" if r["first_stable_t"] else "-"
        print(f"  {r['label']:<12} {r['k_gm']:5.3f}  {'Y' if r['channel_h'] else 'N':>4}  "
              f"{r['final']:8.1f}   {r['late_rate']:.6f}  {tr:>4}   "
              f"{r['status']}  stable:{st_t}")

    stable   = [r for r in all_results if r["status"] == "STABLE"]
    approach = [r for r in all_results if r["status"] in ("->STABLE", "NEAR-ZERO")]

    print()
    if stable:
        print("*** STABLE RING CONFIRMED ***")
        for r in stable:
            print(f"  {r['label']}: k_gm={r['k_gm']}  M_stable~{r['final']:.1f}"
                  f"  first_stable@T={r['first_stable_t']}")
    elif approach:
        best = min(approach, key=lambda r: r["late_rate"])
        print(f"Approaching: {best['label']}  k_gm={best['k_gm']}"
              f"  rate={best['late_rate']:.6f}  [{best['status']}]")
        print("Extend run or increase k_gm.")
    else:
        best = min(all_results, key=lambda r: r["late_rate"])
        print(f"Best: {best['label']}  rate={best['late_rate']:.6f}  [{best['status']}]")

    report = {
        "params": {"L": L, "R": R, "ALPHA": ALPHA, "GAMMA": GAMMA_PHI,
                   "PHASE1": PHASE1, "PHASE2": PHASE2},
        "results": all_results,
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# v8 + v7 Combined: Channel H + Two-Field + Back-Reaction (GPU)", "",
             f"L={L}, R={R}, ALPHA={ALPHA}, GAMMA={GAMMA_PHI}, PHASE2={PHASE2}", "",
             "| label | k_gm | ch_h | M_final | late_rate | status | stable_at |",
             "|-------|------|------|---------|-----------|--------|-----------|"]
    for r in all_results:
        st_t = str(r["first_stable_t"]) if r["first_stable_t"] else "-"
        lines.append(f"| {r['label']} | {r['k_gm']} | {'Y' if r['channel_h'] else 'N'} | "
                     f"{r['final']:.1f} | {r['late_rate']:.6f} | {r['status']} | {st_t} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
