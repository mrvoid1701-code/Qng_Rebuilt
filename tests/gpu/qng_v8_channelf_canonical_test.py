"""QNG-GPU-030: does v8 with CANONICAL Channel F (DER-QNG-049) admit a
Hamiltonian ring equilibrium?

Context. Pilot v1/v2 (GPU-029) both ran with channel_f=False, interpreting that
as "turning off the dissipator to get pure Hamiltonian dynamics". Re-reading
qng_v8_canonical_gpu.py exposed that as wrong: Channel F as implemented adds
  -GAMMA_PHI * disorder * sm
to F_sm but has no matching term in force_phi or in H. It is therefore neither
Hamiltonian nor gradient-flow -- it is a ONE-SIDED dissipator. channel_f=False
removes the ring stabilizer without replacement; channel_f=True (with the old
code) injects energy. Neither mode is a clean v8 Hamiltonian test.

DER-QNG-049 derives the unique canonical completion. Treating
  E_F = (GAMMA_PHI/2) * sum_i disorder_i * sigma_m_i^2
as the Channel F potential:
  * -dE_F/dsigma_m_i = -GAMMA_PHI * disorder_i * sigma_m_i  (matches existing code)
  * -dE_F/dphi_j     = +(GAMMA_PHI/(2z)) * sum_{i in N(j)} sin(theta_i - phi_j) * sigma_m_i^2  (new)
where theta_i = arg(Z_i) with Z_i = (1/z) sum_{k in N(i)} exp(i phi_k).

Both terms are now wired into force_phi_v8 and hamiltonian_v8 behind
channel_f=True (default).

Protocol.
  1. Load cached L=28 R=4 ring (Phase-1 + Phase-2 of v7-symmetric gradient flow).
  2. Evolve with v8 Yoshida4, channel_f=True (now canonical), T=100 lu, DT=0.01.
     All other settings match qng_v8_orbit_pilot.py: K_GM=0, damping=0, chi_decay=0,
     V_couple=True.
  3. Sample M_ring, H_v8, sigma_m extrema, phi_std every 2 lu.

Gates.
  G1 energy conservation:  max |dH/H_0| < 1%          (ring is Hamiltonian)
  G2 boundedness:          M_ring in [100, 250]       (ring doesn't dissolve/blow)
  G3 non-dissolve (weaker): M_ring(T=100) > 0.5 * M_ring(T=10)

Decision matrix.
  G1 PASS, G2 PASS  -> v8 DOES have a ring equilibrium; DER-QNG-047 was
                       an artifact of broken Channel F; re-open ring-as-
                       static-soliton; DER-QNG-044 E=mc^2 probe gets new input.
  G1 PASS, G2 FAIL  -> canonical form correct BUT ring is not a local min of
                       the full E_v8 + E_F + V_couple potential -> Scenario A
                       (dynamic orbit) remains, DER-QNG-047 strengthened.
  G1 FAIL           -> DER-QNG-049 derivation has a bug; debug against finite
                       differences before any further interpretation.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

from qng_v8_canonical_gpu import (
    SIGMA_M_REF,
    yoshida4_step,
    hamiltonian_v8,
    ring_mass_deficit,
    ring_radius,
)
from qng_v8_ring_cache import form_ring_cached


def main():
    print("=" * 80)
    print("QNG-GPU-030: v8 + CANONICAL Channel F (DER-QNG-049) on cached ring")
    print("=" * 80)

    L = 28
    R = 4
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0, verbose=True)
    M0 = float(ring_mass_deficit(ring_state['sm']))
    print(f"  cached M_ring = {M0:.4f}  (target band [100, 250])")

    N = L ** 3
    state = {
        'sg':     ring_state['sg'].copy(),
        'sm':     ring_state['sm'].copy(),
        'chi':    ring_state['chi'].copy(),
        'phi':    ring_state['phi'].copy(),
        'pi_m':   cp.zeros(N, dtype=cp.float64),
        'pi_phi': cp.zeros(N, dtype=cp.float64),
    }

    DT = 0.01
    T_PHYS = 100.0
    N_STEPS = int(round(T_PHYS / DT))
    SAMPLE_EVERY = 2.0
    STRIDE = int(round(SAMPLE_EVERY / DT))

    CHANNEL_F = True
    V_COUPLE_ON = True
    K_GM = 0.0
    CHI_DECAY = 0.0
    DAMPING = 0.0

    print(f"  config: v8 Yoshida4, DT={DT}, T={T_PHYS} lu ({N_STEPS} substeps)")
    print(f"  V_couple={V_COUPLE_ON}, Channel F={CHANNEL_F} (CANONICAL), "
          f"k_gm={K_GM}, chi_decay={CHI_DECAY}, damping={DAMPING}")

    H0 = hamiltonian_v8(state, nb_idx, channel_f=CHANNEL_F)
    M_hist = [M0]
    H_hist = [H0]
    R_hist = [ring_radius(state['sm'], L)]
    sm_min_hist = [float(cp.min(state['sm']))]
    sm_max_hist = [float(cp.max(state['sm']))]
    phi_std_hist = [float(cp.std(state['phi']))]
    t_hist = [0.0]

    print(f"  H_0 = {H0:.4f}")
    print()

    t0 = time.time()
    for step in range(1, N_STEPS + 1):
        state = yoshida4_step(
            state, DT, nb_idx,
            k_gm=K_GM, damping_gamma=DAMPING, chi_decay=CHI_DECAY,
            v_couple_on=V_COUPLE_ON, channel_f=CHANNEL_F,
        )
        if step % STRIDE == 0:
            t_phys = step * DT
            M = float(ring_mass_deficit(state['sm']))
            H = float(hamiltonian_v8(state, nb_idx, channel_f=CHANNEL_F))
            Rr = ring_radius(state['sm'], L)
            smn = float(cp.min(state['sm']))
            smx = float(cp.max(state['sm']))
            pst = float(cp.std(state['phi']))
            t_hist.append(t_phys)
            M_hist.append(M)
            H_hist.append(H)
            R_hist.append(Rr)
            sm_min_hist.append(smn)
            sm_max_hist.append(smx)
            phi_std_hist.append(pst)
            if step % (10 * STRIDE) == 0:
                dH = (H - H0) / abs(H0) if abs(H0) > 1e-10 else 0.0
                print(f"  t={t_phys:6.1f}  M={M:8.3f}  H={H:10.3f}  "
                      f"dH/H={dH:+.2e}  R={Rr:5.2f}  "
                      f"sm=[{smn:.3f},{smx:.3f}]  phi_std={pst:.3f}",
                      flush=True)

    wall = time.time() - t0
    print(f"\n  wall = {wall:.1f}s")

    # -------- Gate evaluation --------
    M_arr = np.asarray(M_hist)
    H_arr = np.asarray(H_hist)

    M_min = float(np.min(M_arr))
    M_max = float(np.max(M_arr))
    dH_max = float(np.max(np.abs(H_arr - H0) / abs(H0))) if abs(H0) > 1e-10 else float('inf')

    G1_thresh = 0.01
    G1_pass = dH_max < G1_thresh

    G2_lo = 100.0
    G2_hi = 250.0
    G2_pass = (M_min > G2_lo) and (M_max < G2_hi)

    M_at_10 = float(M_hist[5]) if len(M_hist) > 5 else float(M_hist[-1])
    M_final = float(M_hist[-1])
    persistence_ratio = M_final / M_at_10 if abs(M_at_10) > 1e-6 else 0.0
    G3_pass = persistence_ratio > 0.5

    print("\n" + "=" * 80)
    print("GATES")
    print("=" * 80)
    print(f"  G1 H conservation:    max |dH/H| = {dH_max:.3e} "
          f"(need <{G1_thresh})        -> {'PASS' if G1_pass else 'FAIL'}")
    print(f"  G2 bounded M_ring:    M in [{M_min:.3f}, {M_max:.3f}] "
          f"(need in [{G2_lo},{G2_hi}])  -> {'PASS' if G2_pass else 'FAIL'}")
    print(f"  G3 non-dissolve:      M_final/M_at_10 = {persistence_ratio:.2f} "
          f"(need >0.5)             -> {'PASS' if G3_pass else 'FAIL'}")

    # -------- Verdict --------
    if G1_pass and G2_pass:
        verdict = 'V8_RING_EQUILIBRIUM_CONFIRMED'
        interp = ('Canonical Channel F restores ring as Hamiltonian equilibrium. '
                  'DER-QNG-047 was an artifact of broken implementation. '
                  'Re-open ring-as-static-soliton. DER-QNG-044 E=mc^2 gets new input.')
    elif G1_pass and not G2_pass:
        verdict = 'V8_NO_STATIC_RING_CONFIRMED_CANONICAL'
        interp = ('Canonical form is numerically correct (H conserved) but ring '
                  'is NOT a local min of full v8 + canonical F potential. '
                  'DER-QNG-047 STRENGTHENED: not an implementation artifact; '
                  'v8 genuinely has no static ring in 3D even with canonical F. '
                  'Scenario A (dynamic orbit) remains load-bearing.')
    else:
        verdict = 'DER_QNG_049_SUSPECTED_BUG'
        interp = ('H not conserved under channel_f=True in canonical mode. '
                  'DER-QNG-049 derivation likely has a sign or index error. '
                  'Debug F_phi_F_j against finite differences of E_F before '
                  'any further interpretation.')

    print(f"\n  VERDICT: {verdict}")
    print(f"  Interpretation: {interp}")
    print("=" * 80)

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-channelf-canonical-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "report.json", "w") as f:
        json.dump({
            'test_id': 'QNG-GPU-030',
            'derivation': 'DER-QNG-049',
            'L': L, 'R': R, 'DT': DT, 'T_PHYS': T_PHYS,
            'channel_f': CHANNEL_F, 'v_couple_on': V_COUPLE_ON,
            'k_gm': K_GM, 'chi_decay': CHI_DECAY, 'damping': DAMPING,
            'M_0': M0, 'H_0': H0,
            'M_min': M_min, 'M_max': M_max, 'dH_max': dH_max,
            'persistence_ratio': persistence_ratio,
            'G1_H_conservation_pass': G1_pass,
            'G2_bounded_M_pass': G2_pass,
            'G3_non_dissolve_pass': G3_pass,
            'verdict': verdict,
            'interpretation': interp,
            'runtime_sec': wall,
            't_samples':       [float(x) for x in t_hist],
            'M_samples':       [float(x) for x in M_hist],
            'H_samples':       [float(x) for x in H_hist],
            'R_samples':       [float(x) for x in R_hist],
            'sm_min_samples':  [float(x) for x in sm_min_hist],
            'sm_max_samples':  [float(x) for x in sm_max_hist],
            'phi_std_samples': [float(x) for x in phi_std_hist],
        }, f, indent=2)
    print(f"  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
