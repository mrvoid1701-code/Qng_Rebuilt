from __future__ import annotations

"""Ring decay emission test (QNG-GPU-003, GPU).

When a vortex ring dissolves, does it emit localized field excitations?
  - sigma_g has KG wave dynamics (v_s = sqrt(k_back*chi_rel/6) ~ 0.076 lu/step)
  - phi has diffusion dynamics
  - sigma_m is overdamped (gradient flow)

Protocol:
  1. Form single R=5 ring at center of L=60 box (Phase1 + Phase2_form)
  2. Let ring dissolve under v7 dynamics -- no Channel H (Phase3_decay)
  3. Monitor 6 concentric shells around ring center
  4. Look for propagating perturbations in sigma_g and phi disorder

Shell edges (lu from center): 0-8 (inner/ring), 8-12, 12-16, 16-20, 20-24, 24-28

Gate WAVE_EMISSION: peak of delta_sg(r) moves outward at ~ v_s = 0.076 lu/step
Gate DIFFUSION:     sigma_m/sigma_g perturbation spreads as sqrt(t) uniformly
Gate NO_EMISSION:   perturbations stay in inner shell only

Physical interpretation:
  WAVE_EMISSION => sigma_g is the QNG "pion" carrier -- ring emits gravitational wave packet
  NO_EMISSION   => dissolution is purely dissipative, no meson analog in current v7
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-decay-emission-v1"

# v7 parameters (matched to CPU-074: GAMMA_PHI=0.10, BETA_PHI=0.02)
SIGMA_REF  = 0.5
BETA       = 0.35
BETA_G     = 0.35
BETA_PHI   = 0.02   # phi diffusion rate (separate from BETA -- matches CPU-074)
DELTA_CHI  = 0.20
CHI_DECAY  = 0.020
CHI_REL    = 0.35
ALPHA      = 0.005
ALPHA_G    = 0.005
GAMMA_PHI  = 0.10   # Channel F depletion rate -- matches CPU-074 (was 0.005, wrong)
K_BACK     = 0.10
K_GM       = 0.010

# Predicted wave speed (from DER-QNG-032 / CPU-054)
V_SOUND_PRED = math.sqrt(K_BACK * CHI_REL / 6.0)  # ~0.0764 lu/step

PHASE1       = 300
PHASE2_FORM  = 1500   # matches CPU-074 formation protocol
PHASE3_DECAY = 30000
PRINT_EVERY  = 500

L  = 60
R  = 5   # Delta(1232)
CX, CY, CZ = 30, 30, 30  # center of box

# Shell edges (inner radius, outer radius)
SHELLS = [(0, 8), (8, 12), (12, 16), (16, 20), (20, 24), (24, 28)]
SHELL_LABELS = ["r0-8", "r8-12", "r12-16", "r16-20", "r20-24", "r24-28"]


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def build_neighbor_arrays(L):
    xs = np.arange(L, dtype=np.int32)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel()
    nb = np.stack([
        ((xg - 1) % L) * L * L + yg * L + zg,
        ((xg + 1) % L) * L * L + yg * L + zg,
        xg * L * L + ((yg - 1) % L) * L + zg,
        xg * L * L + ((yg + 1) % L) * L + zg,
        xg * L * L + yg * L + (zg - 1) % L,
        xg * L * L + yg * L + (zg + 1) % L,
    ], axis=1).astype(np.int32)
    return cp.asarray(nb)


def build_phi_ring(L, R, cx, cy, cz):
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg - cx; dy = yg - cy; dz = zg - cz
    dx = np.where(dx >  L/2, dx - L, dx)
    dx = np.where(dx < -L/2, dx + L, dx)
    dy = np.where(dy >  L/2, dy - L, dy)
    dy = np.where(dy < -L/2, dy + L, dy)
    dz = np.where(dz >  L/2, dz - L, dz)
    dz = np.where(dz < -L/2, dz + L, dz)
    rho = np.sqrt(dx*dx + dy*dy)
    phi = np.arctan2(dz, rho - R)
    return cp.asarray(phi.ravel())


def build_shell_masks(L, cx, cy, cz, shells):
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg - cx; dy = yg - cy; dz = zg - cz
    dx = np.where(dx >  L/2, dx - L, dx)
    dx = np.where(dx < -L/2, dx + L, dx)
    dy = np.where(dy >  L/2, dy - L, dy)
    dy = np.where(dy < -L/2, dy + L, dy)
    dz = np.where(dz >  L/2, dz - L, dz)
    dz = np.where(dz < -L/2, dz + L, dz)
    r2 = (dx*dx + dy*dy + dz*dz).ravel()
    masks = []
    for (r_in, r_out) in shells:
        m = (r2 >= r_in*r_in) & (r2 < r_out*r_out)
        masks.append(cp.asarray(m))
    return masks


# ---------------------------------------------------------------------------
# GPU dynamics (v7, no Channel H)
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
    tw = sm_nb.sum(axis=1)
    sx = (sm_nb * cp.cos(phi_nb)).sum(axis=1)
    sy = (sm_nb * cp.sin(phi_nb)).sum(axis=1)
    return cp.where(tw > 1e-10,
                    cp.arctan2(sy / cp.maximum(tw, 1e-10),
                               sx / cp.maximum(tw, 1e-10)),
                    phi)


def step_formation(sg, sm, chi, phi, nb_idx):
    """Channel F only, no k_gm, no Channel G. BETA_PHI=0.02 matches CPU-074."""
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)
    sg  = cp.clip(sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg), 0.0, 1.0)
    dis = disorder_gpu(phi, nb_idx)
    sm  = cp.clip(sm + ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
                     - GAMMA_PHI * dis * sm, 0.0, 1.0)
    chi = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA_CHI*(SIGMA_REF - sg)
    pm  = phi_weighted_mean(phi, sm, nb_idx)
    phi = wrap_gpu(phi + BETA_PHI * wrap_gpu(pm - phi))
    return sg, sm, chi, phi


def step_decay(sg, sm, chi, phi, nb_idx):
    """v7 full dynamics: Channel F + Channel G (k_gm) + back-reaction.
    No Channel H -- natural dissolution."""
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)

    # sigma_g: Channel A + Channel B + Channel G (k_gm)
    nsg = cp.clip(
        sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg)
           + K_BACK*(chi - sg)  # Channel G: chi back-reaction on sigma_g
           - K_GM * cp.maximum(0.0, SIGMA_REF - sm),
        0.0, 1.0
    )
    # sigma_m: Channel A + Channel B + Channel F
    dis = disorder_gpu(phi, nb_idx)
    nsm = cp.clip(
        sm + ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
           - GAMMA_PHI * dis * sm
           + K_GM * cp.maximum(0.0, SIGMA_REF - sg),
        0.0, 1.0
    )
    # chi: Channel C
    nc = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA_CHI*(SIGMA_REF - sg)
    # phi: Channel B-phi (constant bp -- no Channel H)
    pm  = phi_weighted_mean(phi, sm, nb_idx)
    np_ = wrap_gpu(phi + BETA_PHI * wrap_gpu(pm - phi))
    return nsg, nsm, nc, np_


# ---------------------------------------------------------------------------
# Measurements
# ---------------------------------------------------------------------------

def ring_mass(sm, mask):
    return float(cp.sum(cp.maximum(0.0, SIGMA_REF - sm) * mask))


def shell_metrics(sg, sm, phi, nb_idx, mask):
    """Returns (delta_sg, delta_sm, phi_disorder) for a shell mask."""
    n = float(cp.sum(mask)) + 1e-12
    d_sg = float(SIGMA_REF - cp.sum(sg * mask) / n)   # positive = well / wave above ref
    d_sm = float(SIGMA_REF - cp.sum(sm * mask) / n)   # positive = depletion in shell
    dis  = disorder_gpu(phi, nb_idx)
    phi_d = float(cp.sum(dis * mask) / n)
    return d_sg, d_sm, phi_d


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

    print("Ring decay emission test (QNG-GPU-003)")
    print(f"L={L}, R={R} single ring at ({CX},{CY},{CZ})")
    print(f"Phase1={PHASE1}, Phase2_form={PHASE2_FORM}, Phase3_decay={PHASE3_DECAY}")
    print(f"Predicted sound speed v_s = sqrt(k_back*chi_rel/6) = {V_SOUND_PRED:.4f} lu/step")
    print(f"Shells: {SHELL_LABELS}")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    print("Building geometry...", flush=True)
    nb_idx    = build_neighbor_arrays(L)
    shell_masks = build_shell_masks(L, CX, CY, CZ, SHELLS)
    shell_counts = [int(cp.sum(m)) for m in shell_masks]
    for lbl, cnt in zip(SHELL_LABELS, shell_counts):
        print(f"  Shell {lbl}: {cnt} nodes")

    N   = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi_ring(L, R, CX, CY, CZ)
    print("Done.\n", flush=True)

    # --- Phase 1: phi imprinting ---
    print(f"Phase 1: {PHASE1} steps...", flush=True)
    for _ in range(PHASE1):
        sgb = nb_mean(sg, nb_idx)
        smb = nb_mean(sm, nb_idx)
        sg  = cp.clip(sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg), 0.0, 1.0)
        sm  = cp.clip(sm + ALPHA  *(SIGMA_REF - sm) + BETA  *(smb - sm), 0.0, 1.0)
        chi = chi*(1-CHI_DECAY) + CHI_REL*(sgb-sg) + DELTA_CHI*(SIGMA_REF-sg)
        pm  = phi_weighted_mean(phi, sm, nb_idx)
        phi = wrap_gpu(phi + 0.005 * wrap_gpu(pm - phi))
    print("Phase 1 done.\n", flush=True)

    # --- Phase 2-form: ring formation ---
    print(f"Phase 2-form: {PHASE2_FORM} steps (Channel F, no k_gm)...", flush=True)
    for _ in range(PHASE2_FORM):
        sg, sm, chi, phi = step_formation(sg, sm, chi, phi, nb_idx)

    M_canonical = ring_mass(sm, shell_masks[0])
    print(f"Canonical ring mass (inner shell): M={M_canonical:.3f}")
    print(f"CPU-074 reference for R=5: 954.88")
    print(f"Ratio: {M_canonical/954.88:.3f}")
    print()

    # Baseline shell metrics measured AFTER formation (correct reference point)
    print("Baseline shell metrics (post Phase2_form -- correct reference):")
    print(f"  {'Shell':<10} {'delta_sg':>10} {'delta_sm':>10} {'phi_dis':>10}")
    base_sg = []; base_sm = []; base_pd = []
    for lbl, mask in zip(SHELL_LABELS, shell_masks):
        d_sg, d_sm, phi_d = shell_metrics(sg, sm, phi, nb_idx, mask)
        base_sg.append(d_sg); base_sm.append(d_sm); base_pd.append(phi_d)
        print(f"  {lbl:<10} {d_sg:>10.6f} {d_sm:>10.6f} {phi_d:>10.6f}")
    print()

    # --- Phase 3-decay: dissolution + emission measurement ---
    print(f"Phase 3-decay: {PHASE3_DECAY} steps (v7 full, no Ch_H)...", flush=True)
    print()

    # Header
    hdr = (f"{'T':>7}  {'M_ring':>8}  " +
           "  ".join(f"dsg_{lbl:6s} dsm_{lbl:6s} pd_{lbl:6s}" for lbl in SHELL_LABELS))
    print(hdr, flush=True)

    track = []
    prev_M = M_canonical

    for t in range(1, PHASE3_DECAY + 1):
        sg, sm, chi, phi = step_decay(sg, sm, chi, phi, nb_idx)

        if t % PRINT_EVERY == 0:
            M  = ring_mass(sm, shell_masks[0])
            dM = (prev_M - M) / PRINT_EVERY
            prev_M = M

            metrics = []
            for mask in shell_masks:
                d_sg, d_sm, phi_d = shell_metrics(sg, sm, phi, nb_idx, mask)
                metrics.append((d_sg, d_sm, phi_d))

            # Find shell with largest sigma_g perturbation (wave peak location)
            sg_vals = [m[0] for m in metrics]
            peak_shell_idx = int(np.argmax(sg_vals))
            peak_r = (SHELLS[peak_shell_idx][0] + SHELLS[peak_shell_idx][1]) / 2.0

            row = {"t": t, "M_ring": round(M, 3), "dM_per_step": round(dM, 7),
                   "peak_shell": SHELL_LABELS[peak_shell_idx],
                   "peak_r": peak_r,
                   "shells": []}
            for lbl, (d_sg, d_sm, phi_d) in zip(SHELL_LABELS, metrics):
                row["shells"].append({"label": lbl,
                                      "delta_sg": round(d_sg, 7),
                                      "delta_sm": round(d_sm, 7),
                                      "phi_disorder": round(phi_d, 7)})

            track.append(row)

            line = (f"{t:7d}  {M:8.2f}  " +
                    "  ".join(f"{d_sg:.5f}  {d_sm:.5f}  {phi_d:.5f}"
                              for (d_sg, d_sm, phi_d) in metrics))
            print(line, flush=True)

    # ---------------------------------------------------------------------------
    # Analysis
    # ---------------------------------------------------------------------------
    print()
    print("="*70)
    print("EMISSION ANALYSIS")
    print("="*70)

    M_final = track[-1]["M_ring"]
    M_diss_frac = (M_canonical - M_final) / max(M_canonical, 1e-6)
    print(f"Ring mass: canonical={M_canonical:.2f}  final={M_final:.2f}  "
          f"dissolved={M_diss_frac*100:.1f}%")
    print()

    # Check if sigma_g perturbation in outer shells correlates with dissolution
    # Compare outer shell (r=20-24) delta_sg at early vs late dissolution phase
    outer_idx = 4  # r=20-24
    mid_idx   = 2  # r=12-16
    inner_idx = 0  # r=0-8

    early_pts = track[:6]
    late_pts  = track[-6:]

    def avg_dsg(pts, shell_i):
        return sum(p["shells"][shell_i]["delta_sg"] for p in pts) / len(pts)

    def avg_pd(pts, shell_i):
        return sum(p["shells"][shell_i]["phi_disorder"] for p in pts) / len(pts)

    print(f"delta_sg comparison (inner vs outer):")
    print(f"  {'Shell':<10}  {'early':>10}  {'late':>10}  {'ratio':>8}")
    for i, lbl in enumerate(SHELL_LABELS):
        e = avg_dsg(early_pts, i)
        l = avg_dsg(late_pts, i)
        ratio = l / max(e, 1e-10)
        print(f"  {lbl:<10}  {e:>10.6f}  {l:>10.6f}  {ratio:>8.3f}x")
    print()

    print(f"phi_disorder comparison:")
    print(f"  {'Shell':<10}  {'early':>10}  {'late':>10}")
    for i, lbl in enumerate(SHELL_LABELS):
        e = avg_pd(early_pts, i)
        l = avg_pd(late_pts, i)
        print(f"  {lbl:<10}  {e:>10.6f}  {l:>10.6f}")
    print()

    # Wave propagation check:
    # Real signal = change in delta_sg relative to post-formation baseline.
    # A wave would cause outer shells to deviate from their baseline value.
    # Inner shell should decrease (ring dissolves -> sigma_g well fills in).
    # Outer shells should increase IF a sigma_g wave propagates outward.
    inner_change = avg_dsg(early_pts, inner_idx) - avg_dsg(late_pts, inner_idx)
    mid_change   = avg_dsg(late_pts, mid_idx)   - base_sg[mid_idx]
    outer_change = avg_dsg(late_pts, outer_idx) - base_sg[outer_idx]

    print(f"Inner shell (r0-8) delta_sg change (ring dissolving): {inner_change:.6f}")
    print(f"Mid shell   (r12-16) delta_sg change vs baseline:     {mid_change:.6f}")
    print(f"Outer shell (r20-24) delta_sg change vs baseline:     {outer_change:.6f}")
    print()

    # Verdict based on differential signal
    if outer_change > 1e-5 and outer_change > 0.05 * inner_change:
        verdict = "WAVE_EMISSION"
        detail  = (f"sigma_g perturbation propagates to outer shell: "
                   f"outer_change={outer_change:.2e}, "
                   f"inner_change={inner_change:.2e} "
                   f"({outer_change/max(inner_change,1e-10)*100:.1f}% of inner)")
    elif mid_change > 1e-5 and mid_change > 0.05 * inner_change:
        verdict = "PARTIAL_EMISSION"
        detail  = (f"sigma_g reaches mid shell only: mid_change={mid_change:.2e}, "
                   f"outer_change={outer_change:.2e}")
    elif inner_change > 1e-4:
        verdict = "NO_EMISSION"
        detail  = (f"Ring dissolved (inner_change={inner_change:.4f}) but "
                   f"sigma_g perturbation stays local. Dissolution is dissipative.")
    else:
        verdict = "RING_STABLE"
        detail  = f"Ring did not dissolve significantly (inner_change={inner_change:.6f})"

    print(f"VERDICT: {verdict}")
    print(f"  {detail}")
    print()
    print(f"Predicted sound speed (sigma_g KG): {V_SOUND_PRED:.4f} lu/step")
    print(f"For emission to reach r=24 in {PHASE3_DECAY} steps: possible "
          f"(max reach = {V_SOUND_PRED*PHASE3_DECAY:.0f} lu)")

    # Save artifacts
    report = {
        "params": {
            "L": L, "R": R, "center": [CX, CY, CZ],
            "PHASE1": PHASE1, "PHASE2_FORM": PHASE2_FORM,
            "PHASE3_DECAY": PHASE3_DECAY,
            "K_BACK": K_BACK, "K_GM": K_GM, "GAMMA_PHI": GAMMA_PHI,
            "CHI_DECAY": CHI_DECAY, "V_SOUND_PRED": round(V_SOUND_PRED, 5),
        },
        "canonical_mass": round(M_canonical, 3),
        "final_mass": round(M_final, 3),
        "dissolved_frac": round(M_diss_frac, 4),
        "baseline_sg": {lbl: round(v, 8) for lbl, v in zip(SHELL_LABELS, base_sg)},
        "baseline_sm": {lbl: round(v, 8) for lbl, v in zip(SHELL_LABELS, base_sm)},
        "verdict": verdict,
        "detail": detail,
        "track": track,
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = [
        "# Ring Decay Emission Test (QNG-GPU-003)", "",
        f"L={L}, R={R}, single ring at center, v7 dynamics (no Channel H)", "",
        f"Predicted sound speed v_s = {V_SOUND_PRED:.4f} lu/step", "",
        "## Ring Mass", "",
        f"| canonical | final | dissolved% |",
        f"|-----------|-------|-----------|",
        f"| {M_canonical:.2f} | {M_final:.2f} | {M_diss_frac*100:.1f}% |", "",
        "## Shell delta_sg (sigma_g perturbation): early vs late", "",
        "| shell | early | late | ratio |",
        "|-------|-------|------|-------|",
    ]
    for i, lbl in enumerate(SHELL_LABELS):
        e = avg_dsg(early_pts, i)
        l = avg_dsg(late_pts, i)
        ratio = l / max(e, 1e-10)
        lines.append(f"| {lbl} | {e:.6f} | {l:.6f} | {ratio:.3f}x |")
    lines += [
        "", f"## Verdict: {verdict}", "", f"{detail}", "",
        "## Time Series (selected shells)", "",
        "| t | M_ring | dsg_r0-8 | dsg_r8-12 | dsg_r12-16 | dsg_r16-20 | dsg_r20-24 | dsg_r24-28 |",
        "|---|--------|----------|-----------|------------|------------|------------|------------|",
    ]
    for pt in track[::2]:  # every other point to keep summary compact
        sg_vals = " | ".join(f"{s['delta_sg']:.5f}" for s in pt["shells"])
        lines.append(f"| {pt['t']} | {pt['M_ring']:.2f} | {sg_vals} |")

    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0 if verdict == "WAVE_EMISSION" else 1


if __name__ == "__main__":
    raise SystemExit(main())
