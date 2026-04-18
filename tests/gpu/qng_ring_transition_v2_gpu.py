from __future__ import annotations

"""Ring-to-ring transition test v2: pre-formed rings at canonical mass (GPU).

IMPROVEMENT over v1 (QNG-GPU-002):
  v1 problem: phi_a + phi_b superposition -> bulk disorder everywhere ->
    both rings form with tiny mass (~13-14 vs canonical ~730-955).
    At small mass, gravitational self-trapping is negligible.
    Result: both rings coexist but Ring A more stable (inverted hierarchy).

  v2 fix:
    1. Phi initialized by NEAREST RING REGION (no superposition, no bulk disorder)
    2. Phase 2-form (1000 steps, no k_gm, no Ch_H): both rings form at canonical mass
    3. Phase 2-transition (60000 steps, full v8): measure transition

NEW MEASUREMENT: gravitational well depth G_well
  G_A(t) = sigma_ref - mean(sigma_g in W_A)
  G_B(t) = sigma_ref - mean(sigma_g in W_B)
  Tracks whether gravitational self-trapping is active (G > 0) or negligible.

HYPOTHESIS: At canonical mass, gravitational well is deep enough (~0.0025 vs
~0.00005 at small mass) for self-trapping to dominate. Ring B (R=4, Ch_H)
should be stable while Ring A (R=5, no Ch_H) dissolves.

Protocol:
  L=60, Phase1=300, Phase2_form=1000, Phase2_transition=60000
  Ring A (R=5, Delta): center=(15,30,30), NO Channel H during transition
  Ring B (R=4, proton): center=(45,30,30), WITH Channel H during transition
  k_gm=0.01 active only during Phase2_transition (not during formation)
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-transition-v2"

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

PHASE1          = 300
PHASE2_FORM     = 1000   # ring formation at canonical mass (no k_gm, no Ch_H)
PHASE2_TRANS    = 60000  # transition measurement (full v8)
PRINT_EVERY     = 2000

L  = 60
RA = 5   # Delta(1232) -- metastable
RB = 4   # N(938)      -- stable

CX_A, CY_A, CZ_A = 15, 30, 30
CX_B, CY_B, CZ_B = 45, 30, 30

WIN_R_A = 12
WIN_R_B = 10

# ---------------------------------------------------------------------------
# Vectorized geometry builders
# ---------------------------------------------------------------------------

def build_neighbor_arrays(L):
    xs = np.arange(L, dtype=np.int32)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel()
    nb = np.stack([
        ((xg-1) % L)*L*L + yg*L + zg,
        ((xg+1) % L)*L*L + yg*L + zg,
        xg*L*L + ((yg-1) % L)*L + zg,
        xg*L*L + ((yg+1) % L)*L + zg,
        xg*L*L + yg*L + (zg-1) % L,
        xg*L*L + yg*L + (zg+1) % L,
    ], axis=1).astype(np.int32)
    return cp.asarray(nb)


def build_phi_region(L, ra, ca, rb, cb):
    """Each node gets phi from its NEAREST ring center (no superposition).

    This prevents bulk disorder from phi interference, allowing both rings
    to form at their canonical mass independently.
    """
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')

    # Compute phi for Ring A
    dx_a = xg - ca[0]; dy_a = yg - ca[1]; dz_a = zg - ca[2]
    dx_a = np.where(dx_a >  L/2, dx_a - L, dx_a)
    dx_a = np.where(dx_a < -L/2, dx_a + L, dx_a)
    dy_a = np.where(dy_a >  L/2, dy_a - L, dy_a)
    dy_a = np.where(dy_a < -L/2, dy_a + L, dy_a)
    dz_a = np.where(dz_a >  L/2, dz_a - L, dz_a)
    dz_a = np.where(dz_a < -L/2, dz_a + L, dz_a)
    rho_a = np.sqrt(dx_a*dx_a + dy_a*dy_a)
    phi_a = np.arctan2(dz_a, rho_a - ra)
    dist_a = dx_a*dx_a + dy_a*dy_a + dz_a*dz_a

    # Compute phi for Ring B
    dx_b = xg - cb[0]; dy_b = yg - cb[1]; dz_b = zg - cb[2]
    dx_b = np.where(dx_b >  L/2, dx_b - L, dx_b)
    dx_b = np.where(dx_b < -L/2, dx_b + L, dx_b)
    dy_b = np.where(dy_b >  L/2, dy_b - L, dy_b)
    dy_b = np.where(dy_b < -L/2, dy_b + L, dy_b)
    dz_b = np.where(dz_b >  L/2, dz_b - L, dz_b)
    dz_b = np.where(dz_b < -L/2, dz_b + L, dz_b)
    rho_b = np.sqrt(dx_b*dx_b + dy_b*dy_b)
    phi_b = np.arctan2(dz_b, rho_b - rb)
    dist_b = dx_b*dx_b + dy_b*dy_b + dz_b*dz_b

    # Assign: each node gets phi from nearest ring center
    phi = np.where(dist_a <= dist_b, phi_a, phi_b)
    return phi.ravel()


def build_window_mask(L, cx, cy, cz, win_r):
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
# GPU dynamics
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


def phi_weighted_mean(phi, sm, nb_idx):
    phi_nb = phi[nb_idx]
    sm_nb  = sm[nb_idx]
    tw  = sm_nb.sum(axis=1)
    sx2 = (sm_nb * cp.cos(phi_nb)).sum(axis=1)
    sy2 = (sm_nb * cp.sin(phi_nb)).sum(axis=1)
    pm  = cp.where(tw > 1e-10,
                   cp.arctan2(sy2 / cp.maximum(tw, 1e-10),
                              sx2 / cp.maximum(tw, 1e-10)),
                   phi)
    return pm


def step_formation(sg, sm, chi, phi, nb_idx):
    """Phase 2-form: Channel F only, no k_gm, no Channel H, constant bp=0.005."""
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)
    sg  = cp.clip(sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg), 0.0, 1.0)
    dis = disorder_gpu(phi, nb_idx)
    sm  = cp.clip(sm + ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
                     - GAMMA_PHI * dis * sm, 0.0, 1.0)
    chi = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA_CHI*(SIGMA_REF - sg)
    pm   = phi_weighted_mean(phi, sm, nb_idx)
    diff = wrap_gpu(pm - phi)
    phi  = wrap_gpu(phi + 0.005 * diff)
    return sg, sm, chi, phi


def step_transition(sg, sm, chi, phi, nb_idx, mask_b):
    """Phase 2-trans: full v8. Channel H active only in Ring B window."""
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)

    nsg = cp.clip(
        sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg)
           - K_GM * cp.maximum(0.0, SIGMA_REF - sm),
        0.0, 1.0
    )
    dis = disorder_gpu(phi, nb_idx)
    dsm = (ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
           - GAMMA_PHI * dis * sm
           + K_GM * cp.maximum(0.0, SIGMA_REF - sg))
    nsm = cp.clip(sm + dsm, 0.0, 1.0)
    nc  = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA_CHI*(SIGMA_REF - sg)

    pm   = phi_weighted_mean(phi, sm, nb_idx)
    diff = wrap_gpu(pm - phi)
    depletion = cp.maximum(0.0, SIGMA_REF - sm) / SIGMA_REF
    bp_eff = cp.where(mask_b,
                      BP_MIN + BP_RING * depletion,
                      BP_MIN)
    np_ = wrap_gpu(phi + bp_eff * diff)
    return nsg, nsm, nc, np_

# ---------------------------------------------------------------------------
# Measurements
# ---------------------------------------------------------------------------

def ring_mass(sm, mask):
    return float(cp.sum(cp.maximum(0.0, SIGMA_REF - sm) * mask))


def grav_well_depth(sg, mask):
    """sigma_ref - mean(sigma_g in window). Positive = well present."""
    n = float(cp.sum(mask))
    if n < 1: return 0.0
    return float(SIGMA_REF - cp.sum(sg * mask) / n)


def winding_proxy(phi, sm, nb_idx, mask):
    dis = disorder_gpu(phi, nb_idx)
    dep = cp.maximum(0.0, SIGMA_REF - sm)
    norm = float(cp.sum(dep * mask)) + 1e-12
    return float(cp.sum(dis * dep * mask)) / norm

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

    print("Ring-to-ring transition test v2 (QNG-GPU-002 redesign)")
    print(f"L={L}, RA={RA} (no Ch_H), RB={RB} (Ch_H), k_gm={K_GM}")
    print(f"Phase1={PHASE1}, Phase2_form={PHASE2_FORM}, Phase2_trans={PHASE2_TRANS}")
    print(f"Ring A: ({CX_A},{CY_A},{CZ_A})  Ring B: ({CX_B},{CY_B},{CZ_B})")
    print(f"Phi init: nearest-ring assignment (no superposition)")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    print("Building geometry...", flush=True)
    nb_idx = build_neighbor_arrays(L)
    phi_np = build_phi_region(L, RA, (CX_A,CY_A,CZ_A), RB, (CX_B,CY_B,CZ_B))
    mask_a = build_window_mask(L, CX_A, CY_A, CZ_A, WIN_R_A)
    mask_b = build_window_mask(L, CX_B, CY_B, CZ_B, WIN_R_B)
    n_a = int(cp.sum(mask_a)); n_b = int(cp.sum(mask_b))
    print(f"  Window A: {n_a} nodes  Window B: {n_b} nodes")
    print("Done.\n", flush=True)

    N = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = cp.asarray(phi_np)

    # --- Phase 1: phi imprinting ---
    print(f"Phase 1: {PHASE1} steps (phi imprinting)...", flush=True)
    for _ in range(PHASE1):
        sgb = nb_mean(sg, nb_idx)
        smb = nb_mean(sm, nb_idx)
        sg  = cp.clip(sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg), 0.0, 1.0)
        sm  = cp.clip(sm + ALPHA  *(SIGMA_REF - sm) + BETA  *(smb - sm), 0.0, 1.0)
        chi = chi*(1-CHI_DECAY) + CHI_REL*(sgb-sg) + DELTA_CHI*(SIGMA_REF-sg)
        pm   = phi_weighted_mean(phi, sm, nb_idx)
        diff = wrap_gpu(pm - phi)
        phi  = wrap_gpu(phi + 0.005 * diff)
    print("Phase 1 done.\n", flush=True)

    # --- Phase 2-form: ring formation at canonical mass ---
    print(f"Phase 2-form: {PHASE2_FORM} steps (Channel F, no k_gm)...", flush=True)
    for t in range(PHASE2_FORM):
        sg, sm, chi, phi = step_formation(sg, sm, chi, phi, nb_idx)

    m_a_canonical = ring_mass(sm, mask_a)
    m_b_canonical = ring_mass(sm, mask_b)
    g_a_form = grav_well_depth(sg, mask_a)
    g_b_form = grav_well_depth(sg, mask_b)
    print(f"Canonical masses at T_form={PHASE2_FORM}:")
    print(f"  Ring A (R={RA}): M={m_a_canonical:.3f}  G_well={g_a_form:.6f}")
    print(f"  Ring B (R={RB}): M={m_b_canonical:.3f}  G_well={g_b_form:.6f}")
    print()

    # Compare to CPU-074 canonical values
    cpu074 = {4: 728.92, 5: 954.88}
    for R, M_canon, label in [(RA, m_a_canonical, "A"), (RB, m_b_canonical, "B")]:
        if R in cpu074:
            ratio = M_canon / cpu074[R]
            print(f"  Ring {label}: M={M_canon:.1f}  CPU-074 canonical={cpu074[R]:.1f}  "
                  f"ratio={ratio:.3f}")
    print()

    # --- Phase 2-transition: full v8 dynamics ---
    print(f"Phase 2-transition: {PHASE2_TRANS} steps (full v8)...", flush=True)
    track = []
    prev_ma = m_a_canonical
    prev_mb = m_b_canonical

    print(f"  T={0:6d}  "
          f"M_A={m_a_canonical:7.3f} G_A={g_a_form:.5f}  "
          f"M_B={m_b_canonical:7.3f} G_B={g_b_form:.5f}", flush=True)

    for t in range(1, PHASE2_TRANS + 1):
        sg, sm, chi, phi = step_transition(sg, sm, chi, phi, nb_idx, mask_b)

        if t % PRINT_EVERY == 0:
            ma = ring_mass(sm, mask_a)
            mb = ring_mass(sm, mask_b)
            ga = grav_well_depth(sg, mask_a)
            gb = grav_well_depth(sg, mask_b)
            rate_a = (prev_ma - ma) / PRINT_EVERY
            rate_b = (prev_mb - mb) / PRINT_EVERY
            qa = winding_proxy(phi, sm, nb_idx, mask_a)
            qb = winding_proxy(phi, sm, nb_idx, mask_b)
            prev_ma = ma; prev_mb = mb

            tag_a = ""
            if 0 <= rate_a < 0.0005:  tag_a = "STABLE"
            elif rate_a < 0.002:      tag_a = "near-stab"
            elif rate_a < 0.010:      tag_a = "plateau"

            tag_b = ""
            if 0 <= rate_b < 0.0005:  tag_b = "STABLE"
            elif rate_b < 0.002:      tag_b = "near-stab"
            elif rate_b < 0.010:      tag_b = "plateau"

            print(f"  T={t:6d}  "
                  f"M_A={ma:7.2f} rate_A={rate_a:.6f} G_A={ga:.5f} Q_A={qa:.4f} {tag_a:9s}  "
                  f"M_B={mb:7.2f} rate_B={rate_b:.6f} G_B={gb:.5f} Q_B={qb:.4f} {tag_b}",
                  flush=True)

            track.append({
                "t": t,
                "M_A": round(ma, 3), "rate_A": round(rate_a, 7),
                "G_A": round(ga, 6), "Q_A": round(qa, 5),
                "M_B": round(mb, 3), "rate_B": round(rate_b, 7),
                "G_B": round(gb, 6), "Q_B": round(qb, 5),
            })

    # Analysis
    print()
    print("="*70)
    print("TRANSITION ANALYSIS")
    print("="*70)

    M_A_final = track[-1]["M_A"]
    M_B_final = track[-1]["M_B"]
    G_A_final = track[-1]["G_A"]
    G_B_final = track[-1]["G_B"]
    frac_A = (m_a_canonical - M_A_final) / max(m_a_canonical, 1e-6)
    frac_B = (m_b_canonical - M_B_final) / max(m_b_canonical, 1e-6)
    late_rate_A = sum(pt["rate_A"] for pt in track[-5:]) / 5
    late_rate_B = sum(pt["rate_B"] for pt in track[-5:]) / 5
    B_mass_retained = M_B_final / max(m_b_canonical, 1e-6)

    print(f"Ring A (R={RA}, Delta): M_canonical={m_a_canonical:.2f}  "
          f"M_final={M_A_final:.2f}  dissolved={frac_A*100:.1f}%  "
          f"late_rate={late_rate_A:.7f}  G_final={G_A_final:.5f}")
    print(f"Ring B (R={RB}, proton): M_canonical={m_b_canonical:.2f}  "
          f"M_final={M_B_final:.2f}  dissolved={frac_B*100:.1f}%  "
          f"late_rate={late_rate_B:.7f}  G_final={G_B_final:.5f}")
    print()

    # G_well correlation check
    G_A_early = sum(pt["G_A"] for pt in track[:3]) / 3
    G_A_late  = sum(pt["G_A"] for pt in track[-3:]) / 3
    G_B_early = sum(pt["G_B"] for pt in track[:3]) / 3
    G_B_late  = sum(pt["G_B"] for pt in track[-3:]) / 3
    print(f"Gravitational well: G_A: {G_A_early:.5f} -> {G_A_late:.5f}  "
          f"G_B: {G_B_early:.5f} -> {G_B_late:.5f}")
    print(f"G_well tracks mass: A_corr={G_A_late/G_A_early:.3f}x  "
          f"B_corr={G_B_late/G_B_early:.3f}x")
    print()

    A_dissolved = frac_A > 0.50
    B_stable    = late_rate_B < 0.001 and B_mass_retained > 0.10

    if A_dissolved and B_stable:
        verdict = "TRANSITION"
        detail = (f"R=5 dissolved {frac_A*100:.1f}% while R=4 retained "
                  f"{B_mass_retained*100:.1f}% -- transition signature")
    elif A_dissolved and B_mass_retained < 0.10:
        verdict = "NO_TRANSITION"
        detail = f"Both dissolved. phi interference dominates."
    elif A_dissolved and not B_stable:
        verdict = "NO_TRANSITION"
        detail = f"R=5 dissolved but R=4 also dissolved."
    elif not A_dissolved:
        verdict = "INCOMPLETE"
        detail = f"R=5 only dissolved {frac_A*100:.1f}% -- extend run or increase gamma"
    else:
        verdict = "INDETERMINATE"
        detail = "Results inconclusive"

    print(f"VERDICT: {verdict}")
    print(f"  {detail}")

    # Save
    report = {
        "params": {"L": L, "RA": RA, "RB": RB, "K_GM": K_GM,
                   "ALPHA": ALPHA, "GAMMA": GAMMA_PHI,
                   "PHASE1": PHASE1, "PHASE2_FORM": PHASE2_FORM,
                   "PHASE2_TRANS": PHASE2_TRANS,
                   "center_A": [CX_A, CY_A, CZ_A],
                   "center_B": [CX_B, CY_B, CZ_B]},
        "canonical": {"M_A": round(m_a_canonical, 3),
                      "M_B": round(m_b_canonical, 3),
                      "G_A_form": round(g_a_form, 6),
                      "G_B_form": round(g_b_form, 6)},
        "final": {"M_A": round(M_A_final, 3), "M_B": round(M_B_final, 3),
                  "G_A": round(G_A_final, 6), "G_B": round(G_B_final, 6),
                  "frac_A_dissolved": round(frac_A, 4),
                  "frac_B_dissolved": round(frac_B, 4),
                  "late_rate_A": round(late_rate_A, 7),
                  "late_rate_B": round(late_rate_B, 7)},
        "grav_well": {"G_A_early": round(G_A_early, 6), "G_A_late": round(G_A_late, 6),
                      "G_B_early": round(G_B_early, 6), "G_B_late": round(G_B_late, 6)},
        "verdict": verdict,
        "detail": detail,
        "track": track,
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = [
        "# Ring-to-Ring Transition Test v2 (GPU)", "",
        f"L={L}, RA={RA}, RB={RB}, k_gm={K_GM}, phi=nearest-region", "",
        "## Canonical Masses (Phase 2-form)", "",
        f"| Ring | R | M_canonical | G_well_form | CPU-074 ref |",
        f"|------|---|------------|-------------|-------------|",
        f"| A (Delta) | {RA} | {m_a_canonical:.2f} | {g_a_form:.6f} | 954.88 |",
        f"| B (proton) | {RB} | {m_b_canonical:.2f} | {g_b_form:.6f} | 728.92 |",
        "", "## Final State", "",
        f"| Ring | M_final | dissolved% | late_rate | G_final | retained% |",
        f"|------|---------|-----------|-----------|---------|----------|",
        f"| A | {M_A_final:.2f} | {frac_A*100:.1f}% | {late_rate_A:.7f} | {G_A_final:.5f} | {(1-frac_A)*100:.1f}% |",
        f"| B | {M_B_final:.2f} | {frac_B*100:.1f}% | {late_rate_B:.7f} | {G_B_final:.5f} | {(1-frac_B)*100:.1f}% |",
        "", f"## Verdict: {verdict}", "", f"{detail}", "",
        "## Time Series", "",
        "| t | M_A | rate_A | G_A | Q_A | M_B | rate_B | G_B | Q_B |",
        "|---|-----|--------|-----|-----|-----|--------|-----|-----|",
    ]
    for pt in track:
        lines.append(f"| {pt['t']} | {pt['M_A']:.2f} | {pt['rate_A']:.6f} | "
                     f"{pt['G_A']:.5f} | {pt['Q_A']:.4f} | "
                     f"{pt['M_B']:.2f} | {pt['rate_B']:.6f} | "
                     f"{pt['G_B']:.5f} | {pt['Q_B']:.4f} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0 if verdict in ("TRANSITION",) else 1


if __name__ == "__main__":
    raise SystemExit(main())
