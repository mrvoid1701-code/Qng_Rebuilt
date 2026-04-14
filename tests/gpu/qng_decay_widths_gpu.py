from __future__ import annotations

"""Decay width test: dissolution rates vs physical decay widths.

HYPOTHESIS: For metastable rings (R=5,6,7), the late-time dissolution rate
maps to the physical decay width Gamma of the corresponding baryon resonance.

Physical decay widths (PDG):
  R=4 N(938):     Gamma = 0 MeV        (stable proton)
  R=5 Delta(1232): Gamma = 118 MeV
  R=6 N*(1520):   Gamma = 115 MeV
  R=7 Delta(1700): Gamma = 300 MeV

Zero-parameter test: do the RATIOS of dissolution rates match the RATIOS of Gamma?
  rate(R=5) / rate(R=6) should equal 118/115 = 1.026
  rate(R=7) / rate(R=5) should equal 300/118 = 2.542
  rate(R=7) / rate(R=6) should equal 300/115 = 2.609

Protocol: run all rings WITHOUT Channel H stabilization (since Delta/N* ARE unstable).
Use v7 back-reaction k_gm=0.01 but NO Channel H -> metastable rings dissolve.
Also run R=4 WITH Channel H to confirm proton stability.

Measure: plateau dissolution rate (T=10000-30000, where rate is roughly constant).
Compare ratios to physical Gamma ratios.

L=40, R in {4,5,6,7}, 30000 Phase-2 steps.
"""

import json
import math
from pathlib import Path

import cupy as cp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-decay-widths-v1"

SIGMA_REF = 0.5
BETA      = 0.35
BETA_G    = 0.35
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
ALPHA     = 0.005
ALPHA_G   = 0.005
GAMMA_PHI = 0.005
K_GM      = 0.010

PHASE1      = 300
PHASE2      = 30000
PRINT_EVERY = 1000

L = 40

# Physical decay widths (PDG 2024, MeV)
GAMMA_PDG = {
    4: 0.0,    # proton - stable
    5: 118.0,  # Delta(1232) P33
    6: 115.0,  # N*(1520) D13
    7: 300.0,  # Delta(1700) D33
}
MASSES_PDG = {
    4: 938.272,
    5: 1232.0,
    6: 1520.0,
    7: 1700.0,
}

# Config: (R, use_channel_h, bp_min, bp_ring)
# R=4: stabilized with Channel H (proton is stable)
# R=5,6,7: no Channel H (they ARE unstable in nature)
CONFIGS = [
    (4, True,  0.001, 0.005),   # proton: stable
    (5, False, 0.005, 0.000),   # Delta(1232): metastable
    (6, False, 0.005, 0.000),   # N*(1520): metastable
    (7, False, 0.005, 0.000),   # Delta(1700): metastable
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

def step_gpu(sg, sm, chi, phi, nb_idx, channel_h, bp_min, bp_ring, channel_f):
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)

    nsg = cp.clip(
        sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg)
           - K_GM * cp.maximum(0.0, SIGMA_REF - sm),
        0.0, 1.0
    )

    if channel_f:
        dis = disorder_gpu(phi, nb_idx)
        dsm = (ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
               - GAMMA_PHI * dis * sm
               + K_GM * cp.maximum(0.0, SIGMA_REF - sg))
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

def run_ring(R, channel_h, bp_min, bp_ring, nb_idx, phi_init):
    N = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = phi_init.copy()

    for _ in range(PHASE1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx,
                                     channel_h=False, bp_min=0.005, bp_ring=0.0,
                                     channel_f=False)

    track = []; prev_m = ring_mass_gpu(sm)
    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx,
                                     channel_h, bp_min, bp_ring, channel_f=True)
        if t % PRINT_EVERY == 0:
            m = ring_mass_gpu(sm)
            rate = (prev_m - m) / PRINT_EVERY
            track.append({"t": t, "M": round(m, 4), "rate": round(rate, 7)})
            prev_m = m
    return track

def plateau_rate(track):
    """Average rate over plateau window T=10000-30000."""
    plateau = [pt["rate"] for pt in track if 10000 <= pt["t"] <= 30000 and pt["rate"] >= 0]
    if not plateau:
        return float("nan")
    return sum(plateau) / len(plateau)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("Decay width test (GPU)")
    print(f"L={L}, K_GM={K_GM}, GAMMA={GAMMA_PHI}, PHASE2={PHASE2}")
    print(f"Zero-param test: rate(R_i)/rate(R_j) vs Gamma(i)/Gamma(j) from PDG")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    print("Building geometry...", flush=True)
    nb_idx   = build_neighbor_arrays(L)
    phi_inits = {R: build_phi_init(L, R) for R in [4,5,6,7]}
    print("Done.\n", flush=True)

    results = {}

    for R, ch_h, bp_min, bp_ring in CONFIGS:
        particle = {4:"N(938)", 5:"Delta(1232)", 6:"N*(1520)", 7:"Delta(1700)"}[R]
        print(f"{'='*60}")
        print(f"R={R}  {particle}  ch_h={ch_h}", flush=True)
        print(f"{'='*60}")

        track = run_ring(R, ch_h, bp_min, bp_ring, nb_idx, phi_inits[R])
        pr = plateau_rate(track)
        final_M = track[-1]["M"]
        peak_M  = max(pt["M"] for pt in track)

        for pt in track:
            tag = ""
            if 0 <= pt["rate"] < 0.0005:  tag = "  *** STABLE ***"
            elif pt["rate"] < 0.002:       tag = "  ** near-stable **"
            elif pt["rate"] < 0.010:       tag = "  * plateau *"
            print(f"  T={pt['t']:6d}  M={pt['M']:9.4f}  rate={pt['rate']:.7f}{tag}",
                  flush=True)

        print(f"  >> {particle}: plateau_rate={pr:.7f}  M_final={final_M:.4f}")
        print()
        results[R] = {"particle": particle, "track": track,
                      "plateau_rate": pr, "final_M": final_M, "peak_M": peak_M}

    # Ratio comparison
    print("="*60)
    print("DECAY WIDTH RATIO TEST")
    print("="*60)
    print(f"{'Pair':<20} {'rate_ratio':>12} {'Gamma_ratio':>12} {'err%':>8} {'match?'}")
    print("-"*60)

    ratio_results = []
    pairs = [(5,6), (5,7), (6,7), (4,5), (4,6), (4,7)]
    for Ra, Rb in pairs:
        rA = results[Ra]["plateau_rate"]
        rB = results[Rb]["plateau_rate"]
        gA = GAMMA_PDG[Ra]
        gB = GAMMA_PDG[Rb]

        if rB > 0 and gB > 0:
            sim_ratio  = rA / rB
            pdg_ratio  = gA / gB
            err_pct    = abs(sim_ratio - pdg_ratio) / pdg_ratio * 100
            match = "MATCH" if err_pct < 20 else ("CLOSE" if err_pct < 40 else "MISS")
        elif Ra == 4:
            sim_ratio = 0.0
            pdg_ratio = 0.0
            err_pct = 0.0
            match = "STABLE"
        else:
            sim_ratio = pdg_ratio = err_pct = float("nan")
            match = "?"

        pname_A = results[Ra]["particle"]
        pname_B = results[Rb]["particle"]
        label = f"{pname_A}/{pname_B}"
        print(f"  {label:<20} {sim_ratio:>12.4f} {pdg_ratio:>12.4f} "
              f"{err_pct:>7.1f}%  {match}")

        ratio_results.append({
            "pair": f"R{Ra}/R{Rb}",
            "sim_ratio": round(sim_ratio, 6),
            "pdg_ratio": round(pdg_ratio, 6) if not math.isnan(pdg_ratio) else None,
            "err_pct": round(err_pct, 2) if not math.isnan(err_pct) else None,
            "match": match,
        })

    print()
    print("Plateau rates (substrate units):")
    for R in [4,5,6,7]:
        pr = results[R]["plateau_rate"]
        g  = GAMMA_PDG[R]
        print(f"  R={R} {results[R]['particle']:<15}: rate={pr:.7f}  "
              f"Gamma_PDG={g:.1f} MeV")

    # Overall verdict
    matches = [r for r in ratio_results if r["match"] == "MATCH"
               and r["pair"] not in ("R4/R5","R4/R6","R4/R7")]
    print(f"\nRatio matches (err<20%): {len(matches)}/3 non-trivial pairs")

    if len(matches) >= 2:
        print("*** DECAY WIDTH RATIOS CONFIRMED — zero free parameters ***")
    elif len(matches) == 1:
        print("Partial match — one ratio confirmed")
    else:
        print("No ratio matches — dissolution rates do not map to decay widths")

    # Save
    report = {
        "params": {"L": L, "K_GM": K_GM, "ALPHA": ALPHA, "GAMMA": GAMMA_PHI,
                   "PHASE1": PHASE1, "PHASE2": PHASE2},
        "gamma_pdg": GAMMA_PDG,
        "ring_results": {str(R): {k: v for k, v in results[R].items() if k != "track"}
                         for R in results},
        "ratio_results": ratio_results,
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# Decay Width Ratio Test (GPU)", "",
             f"K_GM={K_GM}, GAMMA={GAMMA_PHI}, L={L}, PHASE2={PHASE2}", "",
             "## Plateau Rates vs PDG Decay Widths", "",
             "| R | Particle | plateau_rate | Gamma_PDG (MeV) |",
             "|---|----------|-------------|-----------------|"]
    for R in [4,5,6,7]:
        lines.append(f"| {R} | {results[R]['particle']} | "
                     f"{results[R]['plateau_rate']:.7f} | {GAMMA_PDG[R]:.1f} |")
    lines += ["", "## Ratio Comparison", "",
              "| Pair | sim_ratio | PDG_ratio | err% | match |",
              "|------|-----------|-----------|------|-------|"]
    for r in ratio_results:
        lines.append(f"| {r['pair']} | {r['sim_ratio']:.4f} | "
                     f"{r['pdg_ratio'] or '-'} | {r['err_pct'] or '-'} | {r['match']} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
