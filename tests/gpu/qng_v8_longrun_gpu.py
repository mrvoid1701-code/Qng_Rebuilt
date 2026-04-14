from __future__ import annotations

"""v8 Channel H long-run confirmation — GPU.

v8b_moderate (bp_min=0.001, bp_ring=0.005, gamma=0.005, ratio=1.0) showed
PLATEAU-> (decreasing) at T=20000, rate=0.002038 and still falling geometrically.

Extrapolation: rate * 0.87 per 2000 steps -> STABLE gate (0.0005) at T~45000-50000.

This test runs:
  v8b_moderate to T=60000  [primary candidate]
  v8d_weak     to T=60000  [secondary candidate, bp_min=0.002]

If rate crosses 0.0005 -> first genuine stable ring in infinite-volume limit.
"""

import json
import math
from pathlib import Path

import cupy as cp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-v8-longrun-v1"

SIGMA_REF = 0.5
BETA      = 0.35
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
ALPHA     = 0.005
GAMMA_PHI = 0.005   # ratio=1

PHASE1      = 300
PHASE2      = 60000
PRINT_EVERY = 2000

L = 40
R = 8

CONFIGS = [
    ("v8b_moderate", 0.001, 0.005),  # best from previous test
    ("v8d_weak",     0.002, 0.005),  # second best
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

def step_gpu(sg, sm, chi, phi, nb_idx, bp_min, bp_ring, channel_f, channel_h):
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)

    nsg = cp.clip(sg + ALPHA*(SIGMA_REF - sg) + BETA*(sgb - sg), 0.0, 1.0)

    if channel_f:
        dis = disorder_gpu(phi, nb_idx)
        dsm = ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm) - GAMMA_PHI * dis * sm
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

    if channel_h:
        depletion = cp.maximum(0.0, SIGMA_REF - sm) / SIGMA_REF
        bp_eff = bp_min + bp_ring * depletion
    else:
        bp_eff = bp_min

    np_ = wrap_gpu(phi + bp_eff * diff)
    return nsg, nsm, nc, np_

def ring_mass_gpu(sm):
    return float(cp.sum(cp.maximum(0.0, SIGMA_REF - sm)))

def run_config(bp_min, bp_ring, nb_idx, phi_init):
    N = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = phi_init.copy()

    for _ in range(PHASE1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx,
                                     bp_min=0.005, bp_ring=0.0,
                                     channel_f=False, channel_h=False)

    track = []; prev_m = ring_mass_gpu(sm)
    first_stable_t = None

    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx,
                                     bp_min, bp_ring,
                                     channel_f=True, channel_h=True)
        if t % PRINT_EVERY == 0:
            m = ring_mass_gpu(sm)
            rate = (prev_m - m) / PRINT_EVERY
            track.append({"t": t, "M": round(m, 2), "rate": round(rate, 6)})
            prev_m = m
            if rate < 0.0005 and first_stable_t is None:
                first_stable_t = t
                print(f"  *** STABLE GATE REACHED at T={t} ***", flush=True)
    return track, first_stable_t

def status(track):
    late = [pt["rate"] for pt in track[-8:]]
    avg = sum(late) / len(late)
    first4 = sum(late[:4]) / 4
    last4  = sum(late[4:]) / 4
    dec = last4 < first4 * 0.92
    if avg < 0.0005:             return "STABLE",   avg, dec
    if avg < 0.002 and dec:      return "->STABLE",  avg, dec
    if avg < 0.002:              return "NEAR-STAB", avg, dec
    if avg < 0.010 and dec:      return "PLATEAU->", avg, dec
    if avg < 0.010:              return "PLATEAU",   avg, dec
    return "SLOWING", avg, dec

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("v8 Channel H long-run (GPU)")
    print(f"L={L}, R={R}, ALPHA={ALPHA}, GAMMA={GAMMA_PHI} (ratio=1), PHASE2={PHASE2}")
    print("Gate STABLE: rate < 0.0005")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    print("Building geometry...", flush=True)
    nb_idx   = build_neighbor_arrays(L)
    phi_init = build_phi_init(L, R)
    print("Done.\n", flush=True)

    all_results = []

    for label, bp_min, bp_ring in CONFIGS:
        print(f"{'='*60}")
        print(f"{label}  bp_min={bp_min}  bp_ring={bp_ring}", flush=True)
        print(f"{'='*60}")

        track, stable_t = run_config(bp_min, bp_ring, nb_idx, phi_init)
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
        stable_str = f"  STABLE at T={stable_t}" if stable_t else "  not yet stable"
        print(f"  >> peak={peak:.1f}  final={final:.1f}  "
              f"late_rate={avg:.6f}  trend={dec_str}  [{st}]{stable_str}")
        print()

        all_results.append({
            "label": label, "bp_min": bp_min, "bp_ring": bp_ring,
            "peak": peak, "final": final, "late_rate": round(avg, 6),
            "status": st, "decreasing": dec,
            "first_stable_t": stable_t, "track": track,
        })

    print("="*60)
    print("VERDICT")
    print("="*60)
    for r in all_results:
        tr = "dec" if r["decreasing"] else "flat"
        stab = f"stable@T={r['first_stable_t']}" if r["first_stable_t"] else "not reached"
        print(f"  {r['label']}: rate={r['late_rate']:.6f} [{r['status']}]  {stab}")

    stable = [r for r in all_results if r["status"] == "STABLE"]
    approaching = [r for r in all_results if r["status"] in ("->STABLE", "NEAR-STAB")]

    if stable:
        print(f"\n*** STABLE RING CONFIRMED — proton candidate ***")
        for r in stable:
            print(f"  {r['label']}: M_stable={r['final']:.1f}  stable from T={r['first_stable_t']}")
    elif approaching:
        best = min(approaching, key=lambda r: r["late_rate"])
        print(f"\nApproaching stability: {best['label']} rate={best['late_rate']:.6f}")
        print("Run longer or reduce bp_min further.")
    else:
        best = min(all_results, key=lambda r: r["late_rate"])
        print(f"\nBest: {best['label']}  rate={best['late_rate']:.6f}  [{best['status']}]")

    report = {"params": {"L": L, "R": R, "ALPHA": ALPHA, "GAMMA": GAMMA_PHI,
                          "PHASE1": PHASE1, "PHASE2": PHASE2},
              "results": all_results}
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# v8 Channel H Long-Run (GPU)", "",
             f"L={L}, R={R}, ALPHA={ALPHA}, GAMMA={GAMMA_PHI}, PHASE2={PHASE2}", "",
             "| label | bp_min | M_final | late_rate | status | stable_at |",
             "|-------|--------|---------|-----------|--------|-----------|"]
    for r in all_results:
        st_t = str(r["first_stable_t"]) if r["first_stable_t"] else "-"
        lines.append(f"| {r['label']} | {r['bp_min']} | {r['final']:.1f} | "
                     f"{r['late_rate']:.6f} | {r['status']} | {st_t} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
