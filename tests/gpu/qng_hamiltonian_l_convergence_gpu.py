from __future__ import annotations

"""QNG-GPU-015: Hamiltonian energy L-convergence and SM ratio.

Decisive test for DER-QNG-038 rehabilitation: does the Hamiltonian energy
functional H_v7 (evaluated on the final ring state) give an L-convergent mass
observable whose R=5/R=4 ratio matches SM = 1.3130?

GPU-011 FAILED with M_ring (depletion integral, IR-divergent). This test uses
the energy functional (DER-QNG-036, CPU-057) — a distinct, variationally
defined observable that should be localized if Channel H confines phi.

Observables computed per (L, R) after Phase 1 + Phase 2:
  E_total_global     : full-box Hamiltonian energy
  E_vac              : same energy on vacuum (sm=SIGMA_REF, chi=0, phi=0)
  E_ring_global      : E_total - E_vac  (ring excess energy)
  E_ring_windowed    : sphere window around box center, background-subtracted
  Component breakdown: E_A, E_B, E_chi_dec, E_chi_rel, E_delta, E_phi, E_dis
  M_ring_global      : N*SIGMA_REF - sum(sigma_m)  (old observable, cross-check)

Gates (pre-registered in QNG-GPU-015.md):
  G1: last-3-L spread of ratio E_ring_global(R=5)/E_ring_global(R=4) < 0.03
  G2: same for E_ring_windowed                                       < 0.03
  G3: |ratio_L80 - 1.3130| / 1.3130 < 0.05 for BOTH global and windowed
  G4: informational — which component is L-convergent

Parameters are identical to GPU-011 (v5 + Channel H active in Phase 1 AND 2,
k_gm=0).
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-hamiltonian-l-convergence-v1"

SIGMA_REF    = 0.5
ALPHA        = 0.005
BETA         = 0.35
DELTA_CHI    = 0.20
CHI_DECAY    = 0.020
CHI_REL      = 0.35
GAMMA_PHI    = 0.10
BETA_PHI_MIN  = 0.0005
BETA_PHI_RING = 0.06
K_GM          = 0.0

PHASE1 = 300
PHASE2 = 1500

L_VALUES = [20, 30, 40, 60, 80]
RADII    = [4, 5]
RATIO_SM = 1232.0 / 938.3  # 1.3131


# ---------------------------------------------------------------------------
# GPU geometry helpers (reused from GPU-011)
# ---------------------------------------------------------------------------

def build_nb(L):
    xs = np.arange(L, dtype=np.int32)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel()
    nb = np.stack([
        ((xg-1)%L)*L*L + yg*L + zg, ((xg+1)%L)*L*L + yg*L + zg,
        xg*L*L + ((yg-1)%L)*L + zg,  xg*L*L + ((yg+1)%L)*L + zg,
        xg*L*L + yg*L + (zg-1)%L,    xg*L*L + yg*L + (zg+1)%L,
    ], axis=1).astype(np.int32)
    return cp.asarray(nb)


def build_phi_ring(L, R):
    cx = cy = cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg-cx; dy = yg-cy; dz = zg-cz
    for d in [dx, dy, dz]:
        d[:] = np.where(d >  L/2, d-L, d)
        d[:] = np.where(d < -L/2, d+L, d)
    rho = np.sqrt(dx*dx + dy*dy)
    return cp.asarray(np.arctan2(dz, rho-R).ravel())


def build_window_mask(L, R_ring, W):
    """Sphere mask around box center: True where |r - center| <= W.
    Uses minimum-image convention consistent with simulation periodicity."""
    cx = cy = cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg-cx; dy = yg-cy; dz = zg-cz
    for d in [dx, dy, dz]:
        d[:] = np.where(d >  L/2, d-L, d)
        d[:] = np.where(d < -L/2, d+L, d)
    r = np.sqrt(dx*dx + dy*dy + dz*dz)
    return cp.asarray((r <= W).ravel())


def wrap_gpu(a):
    a = a % (2*math.pi)
    return cp.where(a > math.pi, a - 2*math.pi, a)

def nb_mean(f, nb): return f[nb].mean(axis=1)

def disorder_gpu(phi, nb):
    pnb = phi[nb]
    return cp.maximum(0.0, 1.0 - cp.sqrt(cp.cos(pnb).mean(axis=1)**2 +
                                          cp.sin(pnb).mean(axis=1)**2))

def phi_wm(phi, sm, nb):
    pnb = phi[nb]; snb = sm[nb]; tw = snb.sum(axis=1)
    sx = (snb*cp.cos(pnb)).sum(axis=1); sy = (snb*cp.sin(pnb)).sum(axis=1)
    return cp.where(tw>1e-10, cp.arctan2(sy/cp.maximum(tw,1e-10),
                                          sx/cp.maximum(tw,1e-10)), phi)

def channel_h_bp(sm):
    """Channel H: bp_eff = bp_min + bp_ring * depletion_normalized."""
    dep_norm = cp.maximum(0.0, SIGMA_REF - sm) / SIGMA_REF
    return BETA_PHI_MIN + BETA_PHI_RING * dep_norm


# ---------------------------------------------------------------------------
# Dynamics (same as GPU-011)
# ---------------------------------------------------------------------------

def step_phase1(sm, chi, phi, nb):
    smb = nb_mean(sm, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm), 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    bp_eff = channel_h_bp(sm)
    pm  = phi_wm(phi, sm, nb)
    np_ = wrap_gpu(phi + bp_eff * wrap_gpu(pm - phi))
    return nsm, nc, np_

def step_phase2(sm, chi, phi, nb):
    smb = nb_mean(sm, nb)
    dis = disorder_gpu(phi, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm)
                     - GAMMA_PHI*dis*sm, 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    bp_eff = channel_h_bp(sm)
    pm  = phi_wm(phi, sm, nb)
    np_ = wrap_gpu(phi + bp_eff * wrap_gpu(pm - phi))
    return nsm, nc, np_


# ---------------------------------------------------------------------------
# Hamiltonian functional — per-site energy densities
# ---------------------------------------------------------------------------

def energy_densities(sm, chi, phi, nb):
    """Compute per-site energy densities (7 components). Returns dict of arrays.

    Matches CPU-057 functional, with bp_eff(sm) for phi term (Channel H).
    """
    smb = nb_mean(sm, nb)
    ds = sm - SIGMA_REF
    sm_nb = sm[nb]   # shape (N, 6)
    phi_nb = phi[nb]

    # E_A: (alpha/2) * (sm-sigma_ref)^2
    e_A = 0.5 * ALPHA * ds*ds

    # E_B: (beta/4) * sum_nb (sm_j - sm_i)^2    per-site (each bond counted twice)
    grad2 = ((sm_nb - sm[:, None])**2).sum(axis=1)
    e_B = 0.25 * BETA * grad2

    # E_chi_dec: (chi_decay/2) * chi^2
    e_chi_dec = 0.5 * CHI_DECAY * chi*chi

    # E_chi_rel: (chi_rel/2) * chi * (smbar - sm)
    e_chi_rel = 0.5 * CHI_REL * chi * (smb - sm)

    # E_delta: delta_chi * chi * (sm - sigma_ref)
    e_delta = DELTA_CHI * chi * ds

    # E_phi: -(bp_eff/6) * sum_nb sm_i * sm_j * cos(phi_i - phi_j)
    bp_eff = channel_h_bp(sm)
    align = (sm[:, None] * sm_nb * cp.cos(phi[:, None] - phi_nb)).sum(axis=1)
    e_phi = -(bp_eff / 6.0) * align

    # E_disorder: (gamma_phi/2) * disorder * sm^2
    dis = disorder_gpu(phi, nb)
    e_dis = 0.5 * GAMMA_PHI * dis * sm*sm

    return {
        "e_A": e_A, "e_B": e_B, "e_chi_dec": e_chi_dec,
        "e_chi_rel": e_chi_rel, "e_delta": e_delta,
        "e_phi": e_phi, "e_dis": e_dis,
    }


def sum_components(eds):
    return sum(float(cp.sum(v)) for v in eds.values())


def vacuum_energy(L, nb):
    """Energy at phi=0, sm=SIGMA_REF, chi=0. Only e_phi is nonzero."""
    N = L*L*L
    sm = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = cp.zeros(N, dtype=cp.float64)
    eds = energy_densities(sm, chi, phi, nb)
    return {k: float(cp.sum(v)) for k, v in eds.items()}


# ---------------------------------------------------------------------------
# Run one (L, R)
# ---------------------------------------------------------------------------

def run_ring(L, R, nb):
    N = L*L*L
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi_ring(L, R)

    for _ in range(PHASE1):
        sm, chi, phi = step_phase1(sm, chi, phi, nb)
    for _ in range(PHASE2):
        sm, chi, phi = step_phase2(sm, chi, phi, nb)

    # Energy densities on final ring state
    eds_ring = energy_densities(sm, chi, phi, nb)

    # Global component sums
    comp_ring = {k: float(cp.sum(v)) for k, v in eds_ring.items()}
    E_total_ring = sum(comp_ring.values())

    # Windowed (sphere around box center, r <= R + 5)
    W = R + 5.0
    mask = build_window_mask(L, R, W)
    N_inner = int(cp.sum(mask))

    # Per-component windowed sums
    comp_inner = {k: float(cp.sum(v[mask])) for k, v in eds_ring.items()}
    E_inner = sum(comp_inner.values())

    # Background subtraction: outer-shell energy density per site
    N_outer = N - N_inner
    E_outer = E_total_ring - E_inner
    E_bg_per_site = E_outer / max(N_outer, 1)
    E_ring_windowed = E_inner - E_bg_per_site * N_inner

    # M_ring (cross-check with old observable)
    M_ring_global = float(N*SIGMA_REF - cp.sum(sm))

    # dis_bulk diagnostic
    dis = disorder_gpu(phi, nb)
    dis_bulk = float(cp.mean(dis))

    return {
        "L": L, "R": R,
        "N": N, "N_inner": N_inner, "W": W,
        "E_total_ring": E_total_ring,
        "comp_ring_global": comp_ring,
        "comp_ring_windowed_raw": comp_inner,
        "E_inner_raw": E_inner,
        "E_bg_per_site": E_bg_per_site,
        "E_ring_windowed": E_ring_windowed,
        "M_ring_global": M_ring_global,
        "dis_bulk": dis_bulk,
    }


def subtract_vacuum(raw_results, vac_energies):
    """Add ring-excess fields: E_ring_global and per-component E_comp_ring_global.

    raw_results is the dict from run_ring. vac_energies is from vacuum_energy(L).
    """
    E_vac_total = sum(vac_energies.values())
    res = dict(raw_results)
    res["E_vac_total"] = E_vac_total
    res["comp_vac"] = vac_energies
    res["E_ring_global"] = raw_results["E_total_ring"] - E_vac_total
    res["comp_ring_global_subtracted"] = {
        k: raw_results["comp_ring_global"][k] - vac_energies[k]
        for k in vac_energies
    }
    return res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("QNG-GPU-015: Hamiltonian energy L-convergence test")
    print(f"v5 dynamics + Channel H in BOTH Phase 1 and Phase 2, K_GM={K_GM}")
    print(f"bp_min={BETA_PHI_MIN}  bp_ring={BETA_PHI_RING}")
    print(f"PHASE1={PHASE1}  PHASE2={PHASE2}")
    print(f"L values: {L_VALUES}  Radii: {RADII}")
    print(f"SM ratio Delta/N = {RATIO_SM:.4f}")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB", flush=True)
    print()

    all_results = []

    for L in L_VALUES:
        print(f"=== L={L} ===", flush=True)
        nb = build_nb(L)
        vac = vacuum_energy(L, nb)
        print(f"  vacuum E_total = {sum(vac.values()):.4e}", flush=True)

        for R in RADII:
            raw = run_ring(L, R, nb)
            res = subtract_vacuum(raw, vac)
            all_results.append(res)
            print(f"  R={R}: E_ring_global={res['E_ring_global']:.4e}  "
                  f"E_ring_windowed={res['E_ring_windowed']:.4e}  "
                  f"M_ring={res['M_ring_global']:.2f}  "
                  f"dis_bulk={res['dis_bulk']:.6f}", flush=True)

        del nb
        cp.get_default_memory_pool().free_all_blocks()

    # ------------------------------------------------------------------
    # Analysis: gate evaluation
    # ------------------------------------------------------------------

    print()
    print("="*90)
    print("HAMILTONIAN ENERGY L-CONVERGENCE (E_ring_global, E_ring_windowed)")
    print("="*90)
    header = f"{'L':>4}  {'E_glob(R4)':>12}  {'E_glob(R5)':>12}  {'ratio_g':>7}  {'E_win(R4)':>12}  {'E_win(R5)':>12}  {'ratio_w':>7}  {'M_R4':>8}  {'M_R5':>8}  {'ratio_M':>7}"
    print(header)
    print("-"*len(header))

    scan = []
    for L in L_VALUES:
        r4 = next(r for r in all_results if r["L"]==L and r["R"]==4)
        r5 = next(r for r in all_results if r["L"]==L and r["R"]==5)
        ratio_g = (abs(r5["E_ring_global"])   / abs(r4["E_ring_global"])   if abs(r4["E_ring_global"])   > 1e-12 else float('nan'))
        ratio_w = (abs(r5["E_ring_windowed"]) / abs(r4["E_ring_windowed"]) if abs(r4["E_ring_windowed"]) > 1e-12 else float('nan'))
        ratio_M = r5["M_ring_global"]   / max(r4["M_ring_global"], 1e-6)
        print(f"{L:>4}  {r4['E_ring_global']:>12.4e}  {r5['E_ring_global']:>12.4e}  "
              f"{ratio_g:>7.4f}  "
              f"{r4['E_ring_windowed']:>12.4e}  {r5['E_ring_windowed']:>12.4e}  "
              f"{ratio_w:>7.4f}  "
              f"{r4['M_ring_global']:>8.1f}  {r5['M_ring_global']:>8.1f}  "
              f"{ratio_M:>7.4f}")
        scan.append({
            "L": L,
            "E_R4_global": r4['E_ring_global'], "E_R5_global": r5['E_ring_global'],
            "ratio_global": ratio_g,
            "E_R4_windowed": r4['E_ring_windowed'], "E_R5_windowed": r5['E_ring_windowed'],
            "ratio_windowed": ratio_w,
            "M_R4": r4['M_ring_global'], "M_R5": r5['M_ring_global'],
            "ratio_M": ratio_M,
        })

    # Gate 1: global E-ratio last-3 spread
    ratios_g = [s["ratio_global"] for s in scan]
    last3_g = ratios_g[-3:]
    spread_g = max(last3_g) - min(last3_g)

    # Gate 2: windowed E-ratio last-3 spread
    ratios_w = [s["ratio_windowed"] for s in scan]
    last3_w = ratios_w[-3:]
    spread_w = max(last3_w) - min(last3_w)

    # Gate 3: ratio match at L=L_max
    ratio_g_last = scan[-1]["ratio_global"]
    ratio_w_last = scan[-1]["ratio_windowed"]
    match_g = abs(ratio_g_last - RATIO_SM) / RATIO_SM
    match_w = abs(ratio_w_last - RATIO_SM) / RATIO_SM

    # Gate 4: per-component convergence (informational)
    comp_scan = {}
    for key in ["e_A", "e_B", "e_chi_dec", "e_chi_rel", "e_delta", "e_phi", "e_dis"]:
        comp_scan[key] = []
        for L in L_VALUES:
            r4 = next(r for r in all_results if r["L"]==L and r["R"]==4)
            r5 = next(r for r in all_results if r["L"]==L and r["R"]==5)
            c4 = r4["comp_ring_global_subtracted"][key]
            c5 = r5["comp_ring_global_subtracted"][key]
            ratio = c5 / max(abs(c4), 1e-12) if abs(c4)>1e-12 else float('nan')
            comp_scan[key].append({"L": L, "R4": c4, "R5": c5, "ratio": ratio})

    print()
    print(f"Gate 1 (E_global L-spread): {spread_g:.4f}  (threshold < 0.03)")
    print(f"Gate 2 (E_window L-spread): {spread_w:.4f}  (threshold < 0.03)")
    print(f"Gate 3 (SM match at L={L_VALUES[-1]}):")
    print(f"         global:   ratio={ratio_g_last:.4f}  SM={RATIO_SM:.4f}  dev={match_g*100:.2f}%  (gate <5%)")
    print(f"         windowed: ratio={ratio_w_last:.4f}  SM={RATIO_SM:.4f}  dev={match_w*100:.2f}%  (gate <5%)")
    print()

    print("Gate 4 (per-component ratios, informational):")
    print(f"{'comp':>10}  " + "  ".join(f"L={L}:r" for L in L_VALUES))
    for key, rows in comp_scan.items():
        r_str = "  ".join(f"{r['ratio']:>7.3f}" for r in rows)
        print(f"{key:>10}  {r_str}")
    print()

    # Decision
    g1 = spread_g < 0.03
    g2 = spread_w < 0.03
    g3 = (match_g < 0.05) and (match_w < 0.05)

    if g1 and g2 and g3:
        verdict = "PASS"
        interp = ("Hamiltonian energy is L-convergent AND matches SM. "
                  "DER-QNG-038 is rehabilitated via the energy observable.")
    elif g1 and g2 and not g3:
        verdict = "PASS_WEAK"
        interp = ("Energy is L-safe but ratio != SM. Legitimate new observable, "
                  "but baryon ladder needs reinterpretation.")
    else:
        verdict = "FAIL"
        interp = ("Energy observable does not converge (G1 or G2 failed). "
                  "Channel H insufficient for energy localization. "
                  "Report shows which component dominates divergence.")

    print(f"VERDICT: {verdict}")
    print(f"  {interp}")
    print()

    # Write JSON report
    report = {
        "test_id": "QNG-GPU-015",
        "status": verdict,
        "parameters": {
            "ALPHA": ALPHA, "BETA": BETA, "DELTA_CHI": DELTA_CHI,
            "CHI_DECAY": CHI_DECAY, "CHI_REL": CHI_REL, "GAMMA_PHI": GAMMA_PHI,
            "BETA_PHI_MIN": BETA_PHI_MIN, "BETA_PHI_RING": BETA_PHI_RING,
            "K_GM": K_GM, "PHASE1": PHASE1, "PHASE2": PHASE2,
        },
        "L_values": L_VALUES, "RADII": RADII, "RATIO_SM": RATIO_SM,
        "scan": scan,
        "per_component_scan": comp_scan,
        "gates": {
            "G1_Eglobal_spread": {"value": spread_g, "threshold": 0.03, "pass": g1},
            "G2_Ewindow_spread": {"value": spread_w, "threshold": 0.03, "pass": g2},
            "G3_SM_match": {
                "ratio_global_at_Lmax": ratio_g_last,
                "ratio_windowed_at_Lmax": ratio_w_last,
                "deviation_global": match_g,
                "deviation_windowed": match_w,
                "threshold": 0.05,
                "pass": g3,
            },
        },
        "verdict": verdict,
        "interpretation": interp,
    }

    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Write summary.md
    with open(out / "summary.md", "w", encoding="utf-8") as f:
        f.write("# Hamiltonian Energy L-Convergence (QNG-GPU-015)\n\n")
        f.write(f"Protocol: v5 dynamics + Channel H (Phase 1 and 2), K_GM={K_GM}\n")
        f.write(f"bp_min={BETA_PHI_MIN}  bp_ring={BETA_PHI_RING}\n")
        f.write(f"SM ratio Delta/N = {RATIO_SM:.4f}\n\n")
        f.write("## Results -- global and windowed energy ratios\n\n")
        f.write("| L | E_glob(R4) | E_glob(R5) | ratio_g | E_win(R4) | E_win(R5) | ratio_w | M_R4 | M_R5 | ratio_M |\n")
        f.write("|---|-----------|-----------|---------|-----------|-----------|---------|------|------|--------|\n")
        for s in scan:
            f.write(f"| {s['L']} | {s['E_R4_global']:.3e} | {s['E_R5_global']:.3e} | {s['ratio_global']:.4f} | "
                    f"{s['E_R4_windowed']:.3e} | {s['E_R5_windowed']:.3e} | {s['ratio_windowed']:.4f} | "
                    f"{s['M_R4']:.1f} | {s['M_R5']:.1f} | {s['ratio_M']:.4f} |\n")
        f.write("\n## Gates\n\n")
        f.write(f"- **Gate 1** (E_global L-spread): {spread_g:.4f}  threshold < 0.03  -> {'PASS' if g1 else 'FAIL'}\n")
        f.write(f"- **Gate 2** (E_windowed L-spread): {spread_w:.4f}  threshold < 0.03  -> {'PASS' if g2 else 'FAIL'}\n")
        f.write(f"- **Gate 3** (SM match at L={L_VALUES[-1]}):\n")
        f.write(f"   - global:   ratio={ratio_g_last:.4f}  dev={match_g*100:.2f}%  (gate < 5%)\n")
        f.write(f"   - windowed: ratio={ratio_w_last:.4f}  dev={match_w*100:.2f}%  (gate < 5%)\n")
        f.write(f"   -> {'PASS' if g3 else 'FAIL'}\n\n")
        f.write("## Per-component L-behaviour (informational, Gate 4)\n\n")
        f.write("Component ratio E_comp(R=5)/E_comp(R=4) at each L:\n\n")
        f.write(f"| comp | " + " | ".join(f"L={L}" for L in L_VALUES) + " |\n")
        f.write("|---" * (len(L_VALUES)+1) + "|\n")
        for key, rows in comp_scan.items():
            r_str = " | ".join(f"{r['ratio']:.4f}" for r in rows)
            f.write(f"| {key} | {r_str} |\n")
        f.write("\n")
        f.write(f"## Verdict: **{verdict}**\n\n")
        f.write(f"{interp}\n")

    print(f"Reports written to {out}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
