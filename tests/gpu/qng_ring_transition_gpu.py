from __future__ import annotations

"""Ring-to-ring transition test: R=5 -> R=4 + phi-wave (GPU).

HYPOTHESIS (QNG-GPU-002): When an R=5 ring (Delta(1232), metastable) dissolves
in the presence of a stable R=4 ring (N(938)), the phi winding migrates to the
R=4 ring rather than dispersing uniformly — the QNG analog of Delta -> N + pi.

Physical basis (from Einstein-mind review, 2026-04-14):
  Dissolution rate != decay width Gamma.
  Gamma requires: (1) continuum of final states, (2) coupling operator.
  In QNG, Delta -> N + pi = R=5 -> R=4 + phi-wave packet.
  Test: can phi winding migrate from R=5 topology to R=4 topology?

Protocol:
  L=60 box. Two rings in same substrate:
    Ring A (R=5, Delta): center=(15,30,30), NO Channel H -> metastable
    Ring B (R=4, proton): center=(45,30,30), WITH Channel H -> stable
  Both share the same sigma_g, sigma_m, chi, phi fields.
  v7 back-reaction k_gm=0.01 (creates gravitational wells around both rings).

Measurements:
  M_A(t): ring mass in window W_A (sphere r<12 around A)
  M_B(t): ring mass in window W_B (sphere r<10 around B)
  Q_A(t): phi winding proxy in W_A — mean disorder in ring cross-section
  Q_B(t): phi winding proxy in W_B
  dM_total(t): total mass change (energy not conserved — monitors leakage)

Gates:
  TRANSITION: M_B stable (late_rate<0.001) after M_A decreased >50%
  NO_TRANSITION: M_B dissolves at similar rate as M_A
  INDEPENDENT: M_A and M_B evolve independently (no correlation)

L=60, PHASE2=60000, k_gm=0.01.
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-transition-v1"

# --- Substrate parameters (v8 canonical) ---
SIGMA_REF  = 0.5
BETA       = 0.35
BETA_G     = 0.35
DELTA_CHI  = 0.20
CHI_DECAY  = 0.020
CHI_REL    = 0.35
ALPHA      = 0.005
ALPHA_G    = 0.005
GAMMA_PHI  = 0.005
K_GM       = 0.010
BP_MIN     = 0.001
BP_RING    = 0.005

PHASE1      = 300
PHASE2      = 60000
PRINT_EVERY = 2000

L  = 60
RA = 5   # Delta(1232) — metastable
RB = 4   # N(938)      — stable

# Ring centers (periodic box)
CX_A, CY_A, CZ_A = 15, 30, 30
CX_B, CY_B, CZ_B = 45, 30, 30

# Measurement windows: spherical radius around each ring center
WIN_R_A = 12
WIN_R_B = 10

# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def build_neighbor_arrays(L):
    xs = np.arange(L, dtype=np.int32)
    # meshgrid: x, y, z
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')  # each (L,L,L)
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel()
    idx = xg * L * L + yg * L + zg
    nb = np.stack([
        ((xg-1) % L) * L*L + yg*L + zg,
        ((xg+1) % L) * L*L + yg*L + zg,
        xg*L*L + ((yg-1) % L)*L + zg,
        xg*L*L + ((yg+1) % L)*L + zg,
        xg*L*L + yg*L + (zg-1) % L,
        xg*L*L + yg*L + (zg+1) % L,
    ], axis=1).astype(np.int32)
    return cp.asarray(nb)


def build_phi_init(L, ring_r, cx, cy, cz):
    """phi = atan2(dz, rho - R) for a vortex ring at (cx,cy,cz) in XY plane."""
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg - cx; dy = yg - cy; dz = zg - cz
    # periodic wrapping
    dx = np.where(dx >  L/2, dx - L, dx)
    dx = np.where(dx < -L/2, dx + L, dx)
    dy = np.where(dy >  L/2, dy - L, dy)
    dy = np.where(dy < -L/2, dy + L, dy)
    dz = np.where(dz >  L/2, dz - L, dz)
    dz = np.where(dz < -L/2, dz + L, dz)
    rho = np.sqrt(dx*dx + dy*dy)
    phi = np.arctan2(dz, rho - ring_r)
    return phi.ravel()


def build_window_mask(L, cx, cy, cz, win_r):
    """Boolean mask for nodes within win_r of center (cx,cy,cz), periodic."""
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg - cx; dy = yg - cy; dz = zg - cz
    dx = np.where(dx >  L/2, dx - L, dx)
    dx = np.where(dx < -L/2, dx + L, dx)
    dy = np.where(dy >  L/2, dy - L, dy)
    dy = np.where(dy < -L/2, dy + L, dy)
    dz = np.where(dz >  L/2, dz - L, dz)
    dz = np.where(dz < -L/2, dz + L, dz)
    mask = (dx*dx + dy*dy + dz*dz) <= win_r*win_r
    return cp.asarray(mask.ravel())


# ---------------------------------------------------------------------------
# Update step (v8: Channel F + H + G + back-reaction)
# Per-node channel_h flag: nodes in Ring B region use Channel H, others don't.
# ---------------------------------------------------------------------------

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


def step_gpu(sg, sm, chi, phi, nb_idx, mask_b):
    """One v8 step. Channel H active only in mask_b (Ring B region)."""
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)

    # sigma_g: Channel A_g + diffusion + Channel G (matter -> gravity well)
    nsg = cp.clip(
        sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg)
           - K_GM * cp.maximum(0.0, SIGMA_REF - sm),
        0.0, 1.0
    )

    # sigma_m: Channel A + diffusion + Channel F + back-reaction
    dis = disorder_gpu(phi, nb_idx)
    dsm = (ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
           - GAMMA_PHI * dis * sm                         # Channel F
           + K_GM * cp.maximum(0.0, SIGMA_REF - sg))      # back-reaction
    nsm = cp.clip(sm + dsm, 0.0, 1.0)

    # chi
    nc = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA_CHI*(SIGMA_REF - sg)

    # phi update — Channel H active only where mask_b is True
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
    # Channel H only in B window; everywhere else use bp_min (no localization)
    bp_eff = cp.where(mask_b,
                      BP_MIN + BP_RING * depletion,
                      BP_MIN)

    np_ = wrap_gpu(phi + bp_eff * diff)
    return nsg, nsm, nc, np_


# ---------------------------------------------------------------------------
# Measurements
# ---------------------------------------------------------------------------

def ring_mass_window(sm, mask):
    """Ring mass (depletion integral) restricted to a spatial window."""
    return float(cp.sum(cp.maximum(0.0, SIGMA_REF - sm) * mask))


def winding_proxy(phi, sm, nb_idx, mask):
    """Phi winding proxy: mean disorder weighted by depletion in window.

    A high value means phi is winding in the depleted region — ring topology
    present. Decreases as the ring dissolves or winding disperses.
    """
    dis = disorder_gpu(phi, nb_idx)
    dep = cp.maximum(0.0, SIGMA_REF - sm)
    weighted = dis * dep * mask
    norm = float(cp.sum(dep * mask)) + 1e-12
    return float(cp.sum(weighted)) / norm


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("Ring-to-ring transition test (QNG-GPU-002)")
    print(f"L={L}, RA={RA} (no Ch_H), RB={RB} (Ch_H), k_gm={K_GM}, PHASE2={PHASE2}")
    print(f"Ring A: center=({CX_A},{CY_A},{CZ_A})  Ring B: center=({CX_B},{CY_B},{CZ_B})")
    print(f"Separation: {CX_B - CX_A} lattice units")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    print("Building geometry...", flush=True)
    nb_idx = build_neighbor_arrays(L)
    print("  neighbor arrays done", flush=True)

    # Build phi initial conditions: superposition of two vortex rings
    phi_a = build_phi_init(L, RA, CX_A, CY_A, CZ_A)
    phi_b = build_phi_init(L, RB, CX_B, CY_B, CZ_B)
    # Combine: use Ring A phi near A, Ring B phi near B, interpolate elsewhere
    phi_np = phi_a + phi_b   # superpose phases (approximate for separated rings)
    print("  phi init done", flush=True)

    # Spatial windows
    mask_a = build_window_mask(L, CX_A, CY_A, CZ_A, WIN_R_A)
    mask_b = build_window_mask(L, CX_B, CY_B, CZ_B, WIN_R_B)
    n_a = int(cp.sum(mask_a)); n_b = int(cp.sum(mask_b))
    print(f"  Window A: {n_a} nodes  Window B: {n_b} nodes")
    print("Done.\n", flush=True)

    # Initialize fields
    N = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = cp.asarray(phi_np)

    # Phase 1: phi vortex imprinting (no Channel F, constant bp)
    print("Phase 1: imprinting phi vortex...", flush=True)
    for t in range(PHASE1):
        sgb = nb_mean(sg, nb_idx)
        smb = nb_mean(sm, nb_idx)
        sg  = cp.clip(sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg), 0.0, 1.0)
        sm  = cp.clip(sm + ALPHA  *(SIGMA_REF - sm) + BETA  *(smb - sm), 0.0, 1.0)
        chi = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA_CHI*(SIGMA_REF - sg)
        # constant bp=0.005, no Channel H
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
        phi = wrap_gpu(phi + 0.005 * diff)
    print("Phase 1 done.\n", flush=True)

    # Phase 2: full v8 dynamics
    print(f"Phase 2: {PHASE2} steps...", flush=True)
    track = []
    prev_ma = ring_mass_window(sm, mask_a)
    prev_mb = ring_mass_window(sm, mask_b)
    M_A_init = prev_ma
    M_B_init = prev_mb

    print(f"  T=     0  M_A={prev_ma:.3f}  M_B={prev_mb:.3f}  "
          f"(init)", flush=True)

    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_gpu(sg, sm, chi, phi, nb_idx, mask_b)

        if t % PRINT_EVERY == 0:
            ma = ring_mass_window(sm, mask_a)
            mb = ring_mass_window(sm, mask_b)
            rate_a = (prev_ma - ma) / PRINT_EVERY
            rate_b = (prev_mb - mb) / PRINT_EVERY
            qa = winding_proxy(phi, sm, nb_idx, mask_a)
            qb = winding_proxy(phi, sm, nb_idx, mask_b)
            prev_ma = ma; prev_mb = mb

            tag_a = ""
            if 0 <= rate_a < 0.0005:  tag_a = "***STABLE***"
            elif rate_a < 0.002:      tag_a = "near-stab"
            elif rate_a < 0.010:      tag_a = "plateau"

            tag_b = ""
            if 0 <= rate_b < 0.0005:  tag_b = "***STABLE***"
            elif rate_b < 0.002:      tag_b = "near-stab"
            elif rate_b < 0.010:      tag_b = "plateau"

            print(f"  T={t:6d}  "
                  f"M_A={ma:7.3f} rate_A={rate_a:.6f} Q_A={qa:.4f} {tag_a:12s}  "
                  f"M_B={mb:7.3f} rate_B={rate_b:.6f} Q_B={qb:.4f} {tag_b}",
                  flush=True)

            track.append({
                "t": t,
                "M_A": round(ma, 4), "rate_A": round(rate_a, 7),
                "Q_A": round(qa, 6),
                "M_B": round(mb, 4), "rate_B": round(rate_b, 7),
                "Q_B": round(qb, 6),
            })

    # Analysis
    print()
    print("="*60)
    print("TRANSITION ANALYSIS")
    print("="*60)

    M_A_final = track[-1]["M_A"]
    M_B_final = track[-1]["M_B"]
    frac_A_dissolved = (M_A_init - M_A_final) / max(M_A_init, 1e-6)
    late_rate_B = sum(pt["rate_B"] for pt in track[-5:]) / 5

    print(f"Ring A (R=5, Delta): M_init={M_A_init:.3f}  M_final={M_A_final:.3f}  "
          f"dissolved={frac_A_dissolved*100:.1f}%")
    print(f"Ring B (R=4, proton): M_init={M_B_init:.3f}  M_final={M_B_final:.3f}  "
          f"late_rate={late_rate_B:.7f}")
    print()

    # Winding proxy comparison: early vs late
    Q_A_early = sum(pt["Q_A"] for pt in track[:3]) / 3
    Q_A_late  = sum(pt["Q_A"] for pt in track[-3:]) / 3
    Q_B_early = sum(pt["Q_B"] for pt in track[:3]) / 3
    Q_B_late  = sum(pt["Q_B"] for pt in track[-3:]) / 3

    print(f"Winding proxy Q_A: early={Q_A_early:.4f} -> late={Q_A_late:.4f}  "
          f"(change {Q_A_late-Q_A_early:+.4f})")
    print(f"Winding proxy Q_B: early={Q_B_early:.4f} -> late={Q_B_late:.4f}  "
          f"(change {Q_B_late-Q_B_early:+.4f})")
    print()

    # Verdict — B_stable requires both small rate AND substantial mass retained
    # (prevents false positive when ring has nearly dissolved to near-zero)
    A_dissolved    = frac_A_dissolved > 0.50
    B_mass_retained = M_B_final / max(M_B_init, 1e-6)
    B_stable       = late_rate_B < 0.001 and B_mass_retained > 0.10
    Q_B_grew       = Q_B_late > Q_B_early * 1.10   # 10% increase

    if A_dissolved and B_stable:
        verdict = "TRANSITION"
        detail = (f"R=5 dissolved >50% while R=4 retained {B_mass_retained*100:.1f}% "
                  f"of mass and remained stable -- transition signature")
    elif A_dissolved and B_mass_retained < 0.10:
        verdict = "NO_TRANSITION"
        detail = (f"Both rings dissolved. R=4 retained only {B_mass_retained*100:.1f}% "
                  f"of mass. phi spreading from R=5 (no Ch_H) disrupted R=4 topology.")
    elif A_dissolved and not B_stable:
        verdict = "NO_TRANSITION"
        detail = "R=5 dissolved >50% but R=4 also dissolved -- no selectivity"
    elif not A_dissolved:
        verdict = "INCOMPLETE"
        detail = "R=5 not yet dissolved >50% -- extend run"
    else:
        verdict = "INDETERMINATE"
        detail = "Results inconclusive"

    winding_note = "Q_B GREW (+transition support)" if Q_B_grew else "Q_B unchanged"

    print(f"VERDICT: {verdict}")
    print(f"  {detail}")
    print(f"  Winding: {winding_note}")

    # Save
    report = {
        "params": {
            "L": L, "RA": RA, "RB": RB, "K_GM": K_GM,
            "ALPHA": ALPHA, "GAMMA": GAMMA_PHI,
            "PHASE1": PHASE1, "PHASE2": PHASE2,
            "center_A": [CX_A, CY_A, CZ_A],
            "center_B": [CX_B, CY_B, CZ_B],
            "win_r_A": WIN_R_A, "win_r_B": WIN_R_B,
        },
        "M_A_init": round(M_A_init, 4),
        "M_B_init": round(M_B_init, 4),
        "M_A_final": round(M_A_final, 4),
        "M_B_final": round(M_B_final, 4),
        "frac_A_dissolved": round(frac_A_dissolved, 4),
        "late_rate_B": round(late_rate_B, 7),
        "Q_A_early": round(Q_A_early, 6),
        "Q_A_late": round(Q_A_late, 6),
        "Q_B_early": round(Q_B_early, 6),
        "Q_B_late": round(Q_B_late, 6),
        "verdict": verdict,
        "detail": detail,
        "winding_note": winding_note,
        "track": track,
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = [
        "# Ring-to-Ring Transition Test (QNG-GPU-002)", "",
        f"L={L}, RA={RA} (no Ch_H), RB={RB} (Ch_H), k_gm={K_GM}, PHASE2={PHASE2}", "",
        "## Summary", "",
        f"| Metric | Ring A (R=5, Delta) | Ring B (R=4, proton) |",
        f"|--------|--------------------|--------------------|",
        f"| M_init | {M_A_init:.3f} | {M_B_init:.3f} |",
        f"| M_final | {M_A_final:.3f} | {M_B_final:.3f} |",
        f"| dissolved% | {frac_A_dissolved*100:.1f}% | - |",
        f"| late_rate | - | {late_rate_B:.7f} |",
        f"| Q_early | {Q_A_early:.4f} | {Q_B_early:.4f} |",
        f"| Q_late | {Q_A_late:.4f} | {Q_B_late:.4f} |",
        "", f"## Verdict: {verdict}", "",
        f"{detail}", "",
        f"Winding: {winding_note}", "",
        "## Time Series", "",
        "| t | M_A | rate_A | Q_A | M_B | rate_B | Q_B |",
        "|---|-----|--------|-----|-----|--------|-----|",
    ]
    for pt in track:
        lines.append(f"| {pt['t']} | {pt['M_A']:.3f} | {pt['rate_A']:.6f} | "
                     f"{pt['Q_A']:.4f} | {pt['M_B']:.3f} | {pt['rate_B']:.6f} | "
                     f"{pt['Q_B']:.4f} |")

    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0 if verdict in ("TRANSITION", "INDEPENDENT") else 1


if __name__ == "__main__":
    raise SystemExit(main())
