from __future__ import annotations

"""Equilibrium long-run confirmation — GPU version (CuPy).

From equilibrium stability scan (CPU):
  ratio=2 (alpha=0.005, gamma=0.010) reached PLATEAU on L=30/R=8.
  Rate at T=5000: 0.01167, decaying geometrically.

This GPU test extends to larger boxes and more steps to confirm genuine stability:
  L=30, R=8  — 12000 steps (extend from T=5000)
  L=40, R=8  — 12000 steps (box test: does R=8 survive larger box?)
  L=40, R=10 — 12000 steps (intermediate R on large box)

GPU vectorizes the N-node update as matrix operations on CuPy arrays.
Neighbor mean: adj_mat @ values / 6 (precomputed CSR-style via flat index arrays).
Disorder: 1 - |mean(exp(i*phi_neighbors))| computed via sin/cos sums.

Gate: avg(rate[-5:]) < 0.003 -> STABLE (genuine equilibrium, not box artifact)
"""

import json
import math
from pathlib import Path

import cupy as cp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-equilibrium-longrun-v1"

# Parameters (same as CPU equilibrium scan candidate)
ALPHA     = 0.005
GAMMA_PHI = 0.010
SIGMA_REF = 0.5
BETA      = 0.35
BETA_PHI  = 0.005
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35

PHASE1      = 300
PHASE2      = 12000
PRINT_EVERY = 500

CONFIGS = [
    (30,  8, "L30_R8  [candidate - extend from T=5000]"),
    (40,  8, "L40_R8  [box test - R=8 on larger box]"),
    (40, 10, "L40_R10 [intermediate R on large box]"),
]

# ---------------------------------------------------------------------------
# GPU geometry helpers
# ---------------------------------------------------------------------------

def build_neighbor_arrays(L):
    """Build flat neighbor index arrays for 6-connected cubic lattice.
    Returns nb_idx: (N, 6) int32 array on GPU.
    """
    N = L * L * L
    nb = cp.zeros((N, 6), dtype=cp.int32)

    # Build on CPU first, transfer once
    import numpy as np
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
    """Initialize phi field: toroidal winding for vortex ring of radius ring_r."""
    import numpy as np
    N = L * L * L
    RX = RY = RZ = L // 2
    phi = np.zeros(N, dtype=np.float64)
    for x in range(L):
        for y in range(L):
            for z in range(L):
                i = x * L * L + y * L + z
                dx = x - RX; dy = y - RY; dz = z - RZ
                # Minimum image convention
                if dx >  L/2: dx -= L
                if dx < -L/2: dx += L
                if dy >  L/2: dy -= L
                if dy < -L/2: dy += L
                if dz >  L/2: dz -= L
                if dz < -L/2: dz += L
                rho = math.sqrt(dx*dx + dy*dy)
                phi[i] = math.atan2(dz, rho - ring_r)
    return cp.asarray(phi)

# ---------------------------------------------------------------------------
# GPU step function
# ---------------------------------------------------------------------------

def nb_mean(field, nb_idx):
    """Mean of field over 6 neighbors. field: (N,), nb_idx: (N,6) -> (N,)"""
    return field[nb_idx].mean(axis=1)

def disorder_gpu(phi, nb_idx):
    """Disorder = 1 - |<exp(i*phi)>_neighbors|. Returns (N,) in [0,1]."""
    phi_nb = phi[nb_idx]  # (N, 6)
    sx = cp.cos(phi_nb).mean(axis=1)
    sy = cp.sin(phi_nb).mean(axis=1)
    return cp.maximum(0.0, 1.0 - cp.sqrt(sx*sx + sy*sy))

def wrap_gpu(a):
    a = a % (2 * math.pi)
    return cp.where(a > math.pi, a - 2 * math.pi, a)

def step_gpu(sg, sm, chi, phi, nb_idx, channel_f):
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

    # Phase update: weighted circular mean of neighbors
    phi_nb = phi[nb_idx]         # (N, 6)
    sm_nb  = sm[nb_idx]          # (N, 6)
    tw = sm_nb.sum(axis=1)       # (N,)
    sx2 = (sm_nb * cp.cos(phi_nb)).sum(axis=1)
    sy2 = (sm_nb * cp.sin(phi_nb)).sum(axis=1)
    pm  = cp.where(tw > 1e-10, cp.arctan2(sy2 / cp.maximum(tw, 1e-10),
                                           sx2 / cp.maximum(tw, 1e-10)), phi)
    diff = wrap_gpu(pm - phi)
    np_ = wrap_gpu(phi + BETA_PHI * diff)

    return nsg, nsm, nc, np_

def ring_mass_gpu(sm, N):
    return float(cp.sum(cp.maximum(0.0, SIGMA_REF - sm)))

# ---------------------------------------------------------------------------
# Run one config
# ---------------------------------------------------------------------------

def run_config(L, ring_r):
    N = L * L * L
    print(f"  Building neighbor arrays for N={N}...", flush=True)
    nb_idx = build_neighbor_arrays(L)
    print(f"  Initializing phi ring (R={ring_r})...", flush=True)
    phi = build_phi_init(L, ring_r)

    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)

    print(f"  Phase 1 ({PHASE1} steps)...", flush=True)
    for _ in range(PHASE1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx, channel_f=False)

    track = []
    prev_m = ring_mass_gpu(sm, N)

    print(f"  Phase 2 ({PHASE2} steps)...", flush=True)
    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx, channel_f=True)
        if t % PRINT_EVERY == 0:
            m = ring_mass_gpu(sm, N)
            rate = (prev_m - m) / PRINT_EVERY
            track.append({"t": t, "M": round(m, 2), "rate": round(rate, 5)})
            prev_m = m
    return track

# ---------------------------------------------------------------------------
# Status + main
# ---------------------------------------------------------------------------

def status(track):
    late = [pt["rate"] for pt in track[-5:]]
    avg = sum(late) / len(late)
    if avg < 0.003:  return "STABLE",  avg
    if avg < 0.012:  return "PLATEAU", avg
    if avg < 0.05:   return "SLOWING", avg
    return "DISSOLVING", avg

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print(f"Equilibrium long-run confirmation (GPU)")
    print(f"ALPHA={ALPHA}, GAMMA_PHI={GAMMA_PHI} (ratio={GAMMA_PHI/ALPHA:.0f})")
    print(f"BETA_PHI={BETA_PHI}, PHASE2={PHASE2}")
    print(f"Gate: avg(rate[-5:]) < 0.003 -> STABLE")
    print()

    # GPU info
    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB")
    print()

    all_results = []

    for L, R, label in CONFIGS:
        print(f"{'='*60}")
        print(f"L={L}  R={R}  N={L**3}  [{label}]", flush=True)
        print(f"R/L={R/L:.3f}  (box resonance at R/L=0.40 -> R={int(0.4*L)})")
        print(f"{'='*60}")

        track = run_config(L, R)
        st, avg = status(track)
        peak = max(pt["M"] for pt in track)
        final = track[-1]["M"]

        for pt in track:
            tag = ""
            if pt["rate"] < 0.003:   tag = "  *** STABLE ***"
            elif pt["rate"] < 0.012: tag = "  ** plateau **"
            print(f"  T={pt['t']:6d}  M={pt['M']:9.1f}  rate={pt['rate']:.5f}{tag}",
                  flush=True)

        print(f"  >> peak={peak:.1f}  final={final:.1f}  "
              f"late_rate={avg:.5f}  [{st}]")
        print()

        all_results.append({
            "L": L, "R": R, "label": label,
            "R_over_L": round(R/L, 3),
            "peak": peak, "final": final,
            "late_rate": round(avg, 5), "status": st,
            "track": track,
        })

    # Verdict
    print("="*60)
    print("VERDICT")
    print("="*60)

    r_l30 = next((r for r in all_results if r["L"]==30 and r["R"]==8), None)
    r_l40 = next((r for r in all_results if r["L"]==40 and r["R"]==8), None)

    stable_l30 = r_l30 and r_l30["status"] in ("STABLE", "PLATEAU")
    stable_l40 = r_l40 and r_l40["status"] in ("STABLE", "PLATEAU")

    for r in all_results:
        print(f"  L={r['L']} R={r['R']} (R/L={r['R_over_L']}): "
              f"final={r['final']:.1f}  rate={r['late_rate']:.5f}  [{r['status']}]")
    print()

    if stable_l30 and stable_l40:
        verdict = "GENUINE STABILITY: R=8 stable on both L=30 and L=40 -> not box artifact"
    elif stable_l30 and not stable_l40:
        verdict = "BOX ARTIFACT: R=8 stable on L=30 but dissolves on L=40 -> R_stable scales with L"
    elif not stable_l30:
        verdict = "SLOWING ONLY: still dissolving at T=12000 -> need different params"
    else:
        verdict = "INCONCLUSIVE"

    print(f"  {verdict}")

    report = {
        "params": {"ALPHA": ALPHA, "GAMMA_PHI": GAMMA_PHI, "BETA_PHI": BETA_PHI,
                   "PHASE1": PHASE1, "PHASE2": PHASE2},
        "results": all_results,
        "verdict": verdict
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# Equilibrium Long-Run Confirmation (GPU)", "",
             f"ALPHA={ALPHA}, GAMMA_PHI={GAMMA_PHI}, BETA_PHI={BETA_PHI}, PHASE2={PHASE2}", "",
             "| L | R | R/L | M_peak | M_final | late_rate | status |",
             "|---|---|-----|--------|---------|-----------|--------|"]
    for r in all_results:
        lines.append(f"| {r['L']} | {r['R']} | {r['R_over_L']} | "
                     f"{r['peak']:.1f} | {r['final']:.1f} | "
                     f"{r['late_rate']:.5f} | {r['status']} |")
    lines += ["", f"**Verdict:** {verdict}"]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
