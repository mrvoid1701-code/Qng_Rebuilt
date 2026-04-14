from __future__ import annotations

"""Equilibrium ratio=1 scan — GPU version.

From long-run test (GPU): ratio=2 (alpha=0.005, gamma=0.010) gives PLATEAU
with late rate ~0.006-0.009, stabilizing but NOT decaying to zero.
Rate plateaus at ~0.007 from T=7000 onward — metastable, not truly stable.

Hypothesis: true stability (rate -> 0) requires ratio <= 1.
At ratio=1: sigma* = 0.5/(1 + 1*D) ~ 0.5/(1+0.5) = 0.333 -> healthy ring core.

Test matrix (all L=40, R=8, 20000 steps):
  ratio=1.0  alpha=0.005, gamma=0.005
  ratio=0.5  alpha=0.005, gamma=0.0025
  ratio=1.5  alpha=0.005, gamma=0.0075  [bracket]
  ratio=2.0  alpha=0.005, gamma=0.010   [control from previous]

Also test alpha scaling at ratio=1:
  ratio=1.0  alpha=0.002, gamma=0.002   [slower dynamics]
  ratio=1.0  alpha=0.010, gamma=0.010   [faster dynamics]

Gate for TRUE STABLE: avg(rate[-8:]) < 0.002 AND d(rate)/dt < 0 (still decreasing)
Gate for PLATEAU:     avg(rate[-8:]) < 0.010 AND rate roughly constant
"""

import json
import math
from pathlib import Path

import cupy as cp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-equilibrium-ratio1-v1"

SIGMA_REF = 0.5
BETA      = 0.35
BETA_PHI  = 0.005
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35

PHASE1      = 300
PHASE2      = 20000
PRINT_EVERY = 1000

L = 40
R = 8

CONFIGS = [
    (0.005, 0.0025, "ratio=0.5 [below equilibrium]"),
    (0.005, 0.0050, "ratio=1.0 [target]"),
    (0.005, 0.0075, "ratio=1.5 [bracket]"),
    (0.005, 0.0100, "ratio=2.0 [control - previous PLATEAU]"),
    (0.002, 0.0020, "ratio=1.0 [slower alpha]"),
    (0.010, 0.0100, "ratio=1.0 [faster alpha]"),
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

def step_gpu(sg, sm, chi, phi, nb_idx, alpha, gamma_phi, channel_f):
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)

    nsg = cp.clip(sg + alpha*(SIGMA_REF - sg) + BETA*(sgb - sg), 0.0, 1.0)

    if channel_f:
        dis = disorder_gpu(phi, nb_idx)
        dsm = alpha*(SIGMA_REF - sm) + BETA*(smb - sm) - gamma_phi * dis * sm
    else:
        dsm = alpha*(SIGMA_REF - sm) + BETA*(smb - sm)
    nsm = cp.clip(sm + dsm, 0.0, 1.0)

    nc = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA*(SIGMA_REF - sg)

    phi_nb = phi[nb_idx]
    sm_nb  = sm[nb_idx]
    tw = sm_nb.sum(axis=1)
    sx2 = (sm_nb * cp.cos(phi_nb)).sum(axis=1)
    sy2 = (sm_nb * cp.sin(phi_nb)).sum(axis=1)
    pm  = cp.where(tw > 1e-10,
                   cp.arctan2(sy2 / cp.maximum(tw, 1e-10),
                              sx2 / cp.maximum(tw, 1e-10)),
                   phi)
    np_ = wrap_gpu(phi + BETA_PHI * wrap_gpu(pm - phi))

    return nsg, nsm, nc, np_

def ring_mass_gpu(sm):
    return float(cp.sum(cp.maximum(0.0, SIGMA_REF - sm)))

# ---------------------------------------------------------------------------
# Run + status
# ---------------------------------------------------------------------------

def run_config(alpha, gamma_phi, nb_idx, phi_init):
    N = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = phi_init.copy()

    for _ in range(PHASE1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx, alpha, gamma_phi, channel_f=False)

    track = []; prev_m = ring_mass_gpu(sm)
    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx, alpha, gamma_phi, channel_f=True)
        if t % PRINT_EVERY == 0:
            m = ring_mass_gpu(sm)
            rate = (prev_m - m) / PRINT_EVERY
            track.append({"t": t, "M": round(m, 2), "rate": round(rate, 6)})
            prev_m = m
    return track

def status(track):
    late = [pt["rate"] for pt in track[-8:]]
    avg = sum(late) / len(late)
    # Check if rate still decreasing or has flattened
    first_half = sum(late[:4]) / 4
    second_half = sum(late[4:]) / 4
    decreasing = second_half < first_half * 0.95
    if avg < 0.002:              return "STABLE",  avg, decreasing
    if avg < 0.010 and decreasing: return "PLATEAU->STABLE", avg, decreasing
    if avg < 0.010:              return "PLATEAU", avg, decreasing
    if avg < 0.05:               return "SLOWING", avg, decreasing
    return "DISSOLVING", avg, decreasing

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print(f"Equilibrium ratio=1 scan (GPU)")
    print(f"L={L}, R={R}, N={L**3}, PHASE2={PHASE2}")
    print(f"Gate STABLE: avg(rate[-8:]) < 0.002")
    print(f"Gate PLATEAU->STABLE: avg < 0.010 AND still decreasing")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB")
    print()

    print("Building geometry...", flush=True)
    nb_idx   = build_neighbor_arrays(L)
    phi_init = build_phi_init(L, R)
    print("Done.\n", flush=True)

    all_results = []

    for alpha, gamma, label in CONFIGS:
        ratio = gamma / alpha
        D_est = 0.5
        sigma_pred = 0.5 / (1 + ratio * D_est)

        print(f"{'='*60}")
        print(f"alpha={alpha}  gamma={gamma}  ratio={ratio:.2f}  [{label}]")
        print(f"Predicted sigma*~{sigma_pred:.3f}", flush=True)
        print(f"{'='*60}")

        track = run_config(alpha, gamma, nb_idx, phi_init)
        st, avg, dec = status(track)
        peak  = max(pt["M"] for pt in track)
        final = track[-1]["M"]

        for pt in track:
            tag = ""
            if pt["rate"] < 0.002:   tag = "  *** STABLE ***"
            elif pt["rate"] < 0.010: tag = "  ** plateau **"
            print(f"  T={pt['t']:6d}  M={pt['M']:9.1f}  rate={pt['rate']:.6f}{tag}",
                  flush=True)

        dec_str = "decreasing" if dec else "flat"
        print(f"  >> peak={peak:.1f}  final={final:.1f}  "
              f"late_rate={avg:.6f}  trend={dec_str}  [{st}]")
        print()

        all_results.append({
            "alpha": alpha, "gamma": gamma, "ratio": ratio,
            "label": label, "sigma_pred": round(sigma_pred, 3),
            "peak": peak, "final": final,
            "late_rate": round(avg, 6), "status": st,
            "decreasing": dec, "track": track,
        })

    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'ratio':>6} {'alpha':>7} {'gamma':>8} {'sigma*':>7} "
          f"{'M_final':>9} {'late_rate':>10} {'trend':>11} {'status'}")
    print("-"*75)
    for r in all_results:
        tr = "decreasing" if r["decreasing"] else "flat"
        print(f"  {r['ratio']:4.1f}   {r['alpha']:.3f}   {r['gamma']:.4f}   "
              f"{r['sigma_pred']:.3f}   {r['final']:8.1f}   {r['late_rate']:.6f}"
              f"   {tr:>10}   {r['status']}")

    stable = [r for r in all_results if r["status"] in ("STABLE", "PLATEAU->STABLE")]
    if stable:
        best = min(stable, key=lambda r: r["late_rate"])
        print(f"\n*** BEST CANDIDATE: ratio={best['ratio']:.2f}  "
              f"alpha={best['alpha']}  gamma={best['gamma']}  "
              f"rate={best['late_rate']:.6f}  [{best['status']}]")
    else:
        best = min(all_results, key=lambda r: r["late_rate"])
        print(f"\nNo STABLE found. Lowest rate: ratio={best['ratio']:.2f}  "
              f"rate={best['late_rate']:.6f}  [{best['status']}]")

    report = {
        "params": {"L": L, "R": R, "BETA_PHI": BETA_PHI,
                   "PHASE1": PHASE1, "PHASE2": PHASE2},
        "results": all_results,
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# Equilibrium Ratio=1 Scan (GPU)", "",
             f"L={L}, R={R}, PHASE2={PHASE2}", "",
             "| ratio | alpha | gamma | sigma* | M_final | late_rate | trend | status |",
             "|-------|-------|-------|--------|---------|-----------|-------|--------|"]
    for r in all_results:
        tr = "dec" if r["decreasing"] else "flat"
        lines.append(f"| {r['ratio']:.1f} | {r['alpha']} | {r['gamma']} | "
                     f"{r['sigma_pred']:.3f} | {r['final']:.1f} | "
                     f"{r['late_rate']:.6f} | {tr} | {r['status']} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
