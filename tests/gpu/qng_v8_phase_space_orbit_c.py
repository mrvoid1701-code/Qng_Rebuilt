"""QNG-GPU-031c: Phase-space orbit re-run with DER-QNG-050 exact canonical F_A.

GPU-031 (DT=0.025, T=1000 lu, uniform-sigma_m approx Channel A):
   M_ring_0 = 177 -> [40, 1673], mean 701
   breathing mode T ~ 129 lu (ac=0.46, Fourier peaks 125/143/167)
   corr(M, H) = +0.934
   H drift: secular +12.5%/1000 lu + oscillation 0.47x secular
   Verdict: G1/G2/G3 FAIL (pre-registered H_DIVERGENT),
            honest verdict H_INTEGRATOR_LIMITED.

GPU-031b (DT=0.005, T=200 lu, same F_A approx):
   Trajectory byte-identical to 031 sampled stride -> Yoshida4 is CONVERGED.
   The drift is NOT an integrator step-size effect; it is structural:
   the uniform-sigma_m F_A approximation is NOT -dE_phi/dphi in a
   non-uniform ring core.

GPU-031c (THIS RUN): exact_a=True via DER-QNG-050.
   F_A_exact_k = -(2*beta_DER/z) * sm_k * R_k * sin(phi_k - Theta_k)
   F_sm_XY_k   = +(2*beta_DER/z) * R_k * cos(phi_k - Theta_k)
   where Z_k = R_k e^{i Theta_k} = sum_{j in N(k)} sm_j * exp(i phi_j).

Finite-diff verified <1e-7 rel err vs -dE_phi/dphi and -dE_phi/dsm
(qng_v8_der050_finite_diff.py PASS 2026-04-21).

Expected outcomes if F_A approximation was the drift source:
  * secular dH/H0 drops from +12.5% to <1% per 1000 lu
  * breathing mode survives (period ~129 lu, corr(M,H) preserved)
  * G1/G2/G3 move toward PASS
  * Scenario A (particle = bounded v8 orbit) gains empirical support.

Expected if drift is structural (not F_A):
  * dH/H0 stays > 2%
  * new verdict needed (probably canonical kinetic terms on sigma_g or chi).
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
    hamiltonian_v8, yoshida4_step,
    SIGMA_M_REF, MU_M, MU_PHI,
)
from qng_v8_ring_cache import form_ring_cached


def m_ring(sm, sm_ref=SIGMA_M_REF):
    return float(sm_ref * sm.size - cp.sum(sm))


def core_observables(sm, phi, pi_m, pi_phi):
    return {
        'sm_min':    float(cp.min(sm)),
        'sm_max':    float(cp.max(sm)),
        'sm_core':   float(cp.mean(sm[cp.argsort(sm)[:64]])),
        'pim_max':   float(cp.max(cp.abs(pi_m))),
        'piphi_max': float(cp.max(cp.abs(pi_phi))),
        'T_m':       float((1.0/(2.0*MU_M))*cp.sum(pi_m*pi_m)),
        'T_phi':     float((1.0/(2.0*MU_PHI))*cp.sum(pi_phi*pi_phi)),
        'phi_std':   float(cp.std(phi)),
    }


def main():
    print("=" * 80)
    print("QNG-GPU-031c: phase-space orbit with DER-QNG-050 exact_a=True")
    print("=" * 80)

    L = 28
    R = 4
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0, verbose=False)
    N = L ** 3

    K_GM       = 0.0
    CHI_DECAY  = 0.0
    DAMPING    = 0.0
    DT_RUN     = 0.025
    T_PHYS     = 1000.0
    N_STEPS    = int(round(T_PHYS / DT_RUN))
    LOG_LU     = 1.0
    SNAP_LU    = 50.0
    STRIDE_LOG = int(round(LOG_LU / DT_RUN))
    STRIDE_SNAP = int(round(SNAP_LU / DT_RUN))

    state = {
        'sg':     ring_state['sg'].copy(),
        'sm':     ring_state['sm'].copy(),
        'chi':    ring_state['chi'].copy(),
        'phi':    ring_state['phi'].copy(),
        'pi_m':   cp.zeros(N, dtype=cp.float64),
        'pi_phi': cp.zeros(N, dtype=cp.float64),
    }

    print(f"  L={L}, R={R}, N={N}, DT={DT_RUN}, T={T_PHYS} lu, N_steps={N_STEPS}")
    print(f"  mode: k_gm={K_GM}, chi_decay={CHI_DECAY}, damping={DAMPING}")
    print(f"         channel_f=True, v_couple=True, exact_a=True (DER-QNG-050)")
    print(f"  log every {LOG_LU} lu, snapshot every {SNAP_LU} lu")
    print()

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-phase-space-orbit-c-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "snapshots").mkdir(exist_ok=True)

    H0 = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=K_GM)
    M0 = m_ring(state['sm'])
    c0 = core_observables(state['sm'], state['phi'], state['pi_m'], state['pi_phi'])

    print(f"  H_0     = {H0:+.4f}")
    print(f"  M_ring_0 = {M0:+.4f}")
    print(f"  sm_min_0 = {c0['sm_min']:.4f}  sm_max_0 = {c0['sm_max']:.4f}")
    print()
    print(f"  {'t':>6s} {'H':>11s} {'dH/H0':>10s} {'M_ring':>10s} "
          f"{'dM/M0':>10s} {'sm_min':>8s} {'T_m':>8s} {'T_phi':>8s}")

    log = []
    log.append({
        't': 0.0, 'H': H0, 'M_ring': M0, 'dH_over_H0': 0.0,
        'dM_over_M0': 0.0, **c0,
    })

    np.savez(outdir / "snapshots" / "snap_t0000.npz",
             sm=cp.asnumpy(state['sm']), phi=cp.asnumpy(state['phi']),
             pi_m=cp.asnumpy(state['pi_m']), pi_phi=cp.asnumpy(state['pi_phi']))

    t_start = time.time()
    c = c0
    try:
        for step in range(1, N_STEPS + 1):
            state = yoshida4_step(
                state, DT_RUN, nb_idx,
                k_gm=K_GM, damping_gamma=DAMPING, chi_decay=CHI_DECAY,
                v_couple_on=True, channel_f=True, exact_a=True,
            )
            if step % STRIDE_LOG == 0:
                t_phys = step * DT_RUN
                H = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=K_GM)
                M = m_ring(state['sm'])
                c = core_observables(state['sm'], state['phi'],
                                     state['pi_m'], state['pi_phi'])
                dH = (H - H0) / abs(H0) if abs(H0) > 1e-10 else 0.0
                dM = (M - M0) / abs(M0) if abs(M0) > 1e-10 else 0.0
                log.append({
                    't': t_phys, 'H': H, 'M_ring': M,
                    'dH_over_H0': dH, 'dM_over_M0': dM, **c,
                })
                if step % (STRIDE_LOG * 20) == 0:
                    print(f"  {t_phys:6.1f} {H:+11.3f} {dH:+10.2e} {M:+10.3f} "
                          f"{dM:+10.2e} {c['sm_min']:8.4f} "
                          f"{c['T_m']:8.4f} {c['T_phi']:8.4f}", flush=True)
            if step % STRIDE_SNAP == 0:
                t_phys = step * DT_RUN
                tag = f"snap_t{int(round(t_phys)):04d}.npz"
                np.savez(outdir / "snapshots" / tag,
                         sm=cp.asnumpy(state['sm']),
                         phi=cp.asnumpy(state['phi']),
                         pi_m=cp.asnumpy(state['pi_m']),
                         pi_phi=cp.asnumpy(state['pi_phi']))
            if step % STRIDE_LOG == 0:
                if c['sm_min'] < -2.0 or c['sm_max'] > 2.0:
                    print(f"  ABORT at t={t_phys}: sigma_m out of bounds "
                          f"[{c['sm_min']:.2f}, {c['sm_max']:.2f}]")
                    break
    except KeyboardInterrupt:
        print(f"\n  KeyboardInterrupt at step {step}, t={step*DT_RUN:.1f} lu")

    wall = time.time() - t_start
    print(f"\n  wall = {wall/60:.1f} min")

    ts = np.array([e['t'] for e in log])
    Hs = np.array([e['H'] for e in log])
    Ms = np.array([e['M_ring'] for e in log])
    dHs = np.array([e['dH_over_H0'] for e in log])
    dMs = np.array([e['dM_over_M0'] for e in log])

    max_abs_dH = float(np.max(np.abs(dHs)))
    max_abs_dM = float(np.max(np.abs(dMs)))

    mid_idx = len(ts) // 2
    recur = float(abs(Ms[-1] - Ms[mid_idx]) / abs(M0)) if abs(M0) > 1e-10 else 0.0

    G1_pass = max_abs_dH < 0.02
    G2_pass = max_abs_dM < 1.0
    G3_pass = recur < 0.5

    if G2_pass and G3_pass and G1_pass:
        verdict = "H_BOUNDED"
        diag = ("Scenario A corroborated with exact DER-QNG-050 canonical F_A. "
                "Particle = bounded v8 orbit has empirical content.")
    elif G2_pass and G1_pass:
        verdict = "H_CHAOTIC_BOUNDED"
        diag = "Bounded but no recurrence - chaotic attractor."
    elif G2_pass:
        verdict = "H_BOUNDED_H_NONCONS"
        diag = "M_ring bounded but H still drifts - investigate residual channels."
    else:
        verdict = "H_DIVERGENT"
        diag = "Ring still diverges with exact F_A - problem is not Channel A."

    print("\n" + "=" * 80)
    print("VERDICT (GPU-031c)")
    print("=" * 80)
    print(f"  G1 (|dH/H0| < 0.02):      max={max_abs_dH:.3e}  {'PASS' if G1_pass else 'FAIL'}")
    print(f"  G2 (|dM/M0| < 1.0):       max={max_abs_dM:.3e}  {'PASS' if G2_pass else 'FAIL'}")
    print(f"  G3 (|M(T) - M(T/2)|/M0 < 0.5): {recur:.3e}  {'PASS' if G3_pass else 'FAIL'}")
    print(f"\n  Verdict: {verdict}")
    print(f"  Diagnosis: {diag}")

    np.savez(outdir / "trajectory.npz",
             t=ts, H=Hs, M_ring=Ms, dH=dHs, dM=dMs,
             sm_min=np.array([e['sm_min'] for e in log]),
             sm_max=np.array([e['sm_max'] for e in log]),
             sm_core=np.array([e['sm_core'] for e in log]),
             T_m=np.array([e['T_m'] for e in log]),
             T_phi=np.array([e['T_phi'] for e in log]))

    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R,
            'k_gm': K_GM, 'chi_decay': CHI_DECAY, 'damping': DAMPING,
            'DT': DT_RUN, 'T_phys': T_PHYS, 'N_steps': N_STEPS,
            'exact_a': True, 'der_ref': 'DER-QNG-050',
            'H0': H0, 'M0': M0,
            'max_abs_dH': max_abs_dH,
            'max_abs_dM': max_abs_dM,
            'recurrence_proxy': recur,
            'G1_conservation_pass': bool(G1_pass),
            'G2_boundedness_pass':  bool(G2_pass),
            'G3_recurrence_pass':   bool(G3_pass),
            'verdict': verdict,
            'diagnosis': diag,
            'wall_minutes': wall / 60,
            'log_sampled_first_20': log[:20],
            'log_sampled_last_20':  log[-20:],
        }, f, indent=2)
    print(f"\n  Report:     {outdir / 'report.json'}")
    print(f"  Trajectory: {outdir / 'trajectory.npz'}")
    print(f"  Snapshots:  {outdir / 'snapshots'}/")


if __name__ == "__main__":
    main()
