"""Einstein B1: Gaussian sigma_m well — trap vs repel diagnostic.

Tests whether a localized sigma_m deficit (Gaussian bump) traps phi in a
bound-state cavity, or expels phi like a Meissner-effect analog.

Physics: effective mass m_phi^2(x) = (g/(2*mu_phi)) * (sigma_ref - sigma_m(x))^2
is a positive BUMP at the well center, not a potential well. Standard KG
dispersion says this should REPEL phi (mass barrier, not trap).

Protocol (freeze_sm=True throughout):
  sigma_m(r) = SIGMA_M_REF - Delta_0 * exp(-r^2 / w_sm^2),  Delta_0=0.20, w_sm=3
  Config A: phi uniform = 0.05 everywhere (standing waves, reference)
  Config B: phi Gaussian centered on well, same width (localized pulse)
  Evolve T=400 lu with Yoshida4 symplectic.
  Track phi^2 energy inside ball r<r_in vs outside.

Verdicts:
  B1_TRAPPED:   Gauss-center retention > 80% at t=T
                -> ring cavity is a phi bound-state trap (Jackiw-Rebbi binding)
  B1_EXPELLED:  retention < 30%
                -> ring cavity pushes phi OUT (Meissner / Tesla-like)
  B1_DISPERSED: 30-80% retention
                -> mass barrier, phi leaks at KG wave speed
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
    build_nb, yoshida4_step, hamiltonian_v8,
    SIGMA_G_REF, SIGMA_M_REF, CHI_DECAY_V7,
    G_V_COUPLE, MU_PHI, BETA_PHI, DT,
)

EXACT_A_MODE = 'r1'


def gaussian_sm_well(L, w, delta_0):
    xs = np.arange(L)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    cx = cy = cz = (L - 1) / 2.0
    r2 = (xg - cx) ** 2 + (yg - cy) ** 2 + (zg - cz) ** 2
    return (SIGMA_M_REF - delta_0 * np.exp(-r2 / (w * w))).astype(np.float64)


def phi_gaussian_center(L, amp, w):
    xs = np.arange(L)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    cx = cy = cz = (L - 1) / 2.0
    r2 = (xg - cx) ** 2 + (yg - cy) ** 2 + (zg - cz) ** 2
    return (amp * np.exp(-r2 / (w * w))).astype(np.float64)


def make_state_well(L, sm_profile, phi_mode, phi_amp, phi_w):
    N = L * L * L
    state = {
        'sg':     cp.full(N, SIGMA_G_REF, dtype=cp.float64),
        'sm':     cp.asarray(sm_profile.ravel()),
        'chi':    cp.zeros(N, dtype=cp.float64),
        'pi_m':   cp.zeros(N, dtype=cp.float64),
        'pi_phi': cp.zeros(N, dtype=cp.float64),
    }
    if phi_mode == 'uniform':
        phi = cp.full(N, phi_amp, dtype=cp.float64)
    elif phi_mode == 'gauss_center':
        phi_np = phi_gaussian_center(L, phi_amp, phi_w)
        phi = cp.asarray(phi_np.ravel())
    else:
        raise ValueError(f"unknown phi_mode {phi_mode}")
    state['phi'] = phi
    return state


def measure_phi2_in_out(state, L, r_in):
    phi_np = cp.asnumpy(state['phi']).reshape(L, L, L)
    xs = np.arange(L)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    cx = cy = cz = (L - 1) / 2.0
    r2 = (xg - cx) ** 2 + (yg - cy) ** 2 + (zg - cz) ** 2
    mask_in = r2 < r_in * r_in
    phi2 = phi_np * phi_np
    in_sum = float(phi2[mask_in].sum())
    out_sum = float(phi2[~mask_in].sum())
    return in_sum, out_sum


def run_config(L, phi_mode, phi_amp, phi_w, sm_profile_cp,
               sm_profile_np, T_run, r_in, freeze_sm=True):
    n_steps = int(T_run / DT)
    sample_every = max(1, int(5.0 / DT))
    nb_idx = build_nb(L)
    state = make_state_well(L, sm_profile_np, phi_mode, phi_amp, phi_w)

    H0 = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                        exact_a=EXACT_A_MODE)

    times = [0.0]
    i0, o0 = measure_phi2_in_out(state, L, r_in)
    in_list, out_list, tot_list = [i0], [o0], [i0 + o0]

    t_start = time.time()
    for s in range(1, n_steps + 1):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7,
                              exact_a=EXACT_A_MODE)
        if freeze_sm:
            state['sm'] = sm_profile_cp.copy()
            state['pi_m'].fill(0.0)
        if s % sample_every == 0:
            t_phys = s * DT
            times.append(t_phys)
            i, o = measure_phi2_in_out(state, L, r_in)
            in_list.append(i)
            out_list.append(o)
            tot_list.append(i + o)
    wall = time.time() - t_start
    H1 = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                        exact_a=EXACT_A_MODE)

    in_frac_t0 = in_list[0] / tot_list[0] if tot_list[0] > 0 else 0.0
    in_frac_tT = in_list[-1] / tot_list[-1] if tot_list[-1] > 0 else 0.0

    return {
        'phi_mode': phi_mode, 'L': L, 'phi_amp': phi_amp, 'phi_w': phi_w,
        'T_run': T_run, 'r_in': r_in, 'freeze_sm': freeze_sm,
        'times': times, 'in': in_list, 'out': out_list, 'tot': tot_list,
        'in_frac_t0': in_frac_t0, 'in_frac_tT': in_frac_tT,
        'H0': float(H0), 'H1': float(H1),
        'H_drift_frac': abs(H1 - H0) / abs(H0) if abs(H0) > 1e-10 else 0.0,
        'wall_s': wall,
    }


def main():
    L = 28
    phi_amp = 0.05
    phi_w = 3.0
    sm_w = 3.0
    sm_delta = 0.20
    T_run = 400.0
    r_in = 4.0

    print("=" * 80)
    print("Einstein B1: Gaussian sigma_m well — trap vs repel")
    print("=" * 80)
    print(f"  L={L}, g={G_V_COUPLE}, mu_phi={MU_PHI:.4f}, BETA_PHI={BETA_PHI}")
    print(f"  sigma_m well: Delta_0={sm_delta}, w={sm_w} (Gaussian at center)")
    print(f"  phi_amp={phi_amp}, freeze_sm=True, T_run={T_run} lu, DT={DT}")
    print(f"  Inside-ball radius r_in={r_in}")
    print(f"  m^2_center = (g/(2*mu_phi))*Delta^2 = "
          f"{(G_V_COUPLE/(2*MU_PHI))*sm_delta*sm_delta:.5f}")
    print(f"  T_center    = 2*pi/m      = "
          f"{2*np.pi/np.sqrt((G_V_COUPLE/(2*MU_PHI))*sm_delta*sm_delta):.2f} lu")

    sm_profile_np = gaussian_sm_well(L, sm_w, sm_delta)
    sm_profile_cp = cp.asarray(sm_profile_np.ravel())
    print(f"  sigma_m: min={sm_profile_np.min():.4f} (center), "
          f"max={sm_profile_np.max():.4f} (far field)")

    configs = [
        ('uniform',      'Config A: phi uniform 0.05 everywhere (reference)'),
        ('gauss_center', 'Config B: phi Gaussian w=3 centered on well'),
    ]

    results = []
    for mode, desc in configs:
        print(f"\n{desc}")
        r = run_config(L=L, phi_mode=mode, phi_amp=phi_amp, phi_w=phi_w,
                       sm_profile_cp=sm_profile_cp,
                       sm_profile_np=sm_profile_np,
                       T_run=T_run, r_in=r_in)
        print(f"  wall={r['wall_s']:.1f}s  H drift={r['H_drift_frac']:.2e}")
        print(f"  phi^2 inside frac: t=0: {r['in_frac_t0']:.3f} -> "
              f"t=T: {r['in_frac_tT']:.3f}")
        print(f"  phi^2 inside: {r['in'][0]:.3e} -> {r['in'][-1]:.3e}")
        print(f"  phi^2 outside: {r['out'][0]:.3e} -> {r['out'][-1]:.3e}")
        print(f"  phi^2 total: {r['tot'][0]:.3e} -> {r['tot'][-1]:.3e}  "
              f"(conservation ratio {r['tot'][-1]/r['tot'][0]:.4f})")
        results.append(r)

    # Verdict on Config B (gauss_center)
    g_center = results[1]
    frac_T = g_center['in_frac_tT']
    frac_0 = g_center['in_frac_t0']
    decay = (frac_0 - frac_T) / frac_0 if frac_0 > 0 else 0.0

    if frac_T > 0.80:
        verdict = 'B1_TRAPPED'
    elif frac_T < 0.30:
        verdict = 'B1_EXPELLED'
    else:
        verdict = 'B1_DISPERSED'

    print("\n" + "=" * 80)
    print(f"VERDICT: {verdict}")
    print("=" * 80)
    print(f"  Config B phi retention in ball(r<{r_in}): "
          f"{frac_0:.1%} -> {frac_T:.1%}  (decay {decay:.1%})")
    print(f"  TRAPPED (>80%): ring is a phi bound-state cavity (JR-like)")
    print(f"  EXPELLED (<30%): ring is a phi MEISSNER CAVITY (Tesla-like)")
    print(f"  DISPERSED (30-80%): mass barrier, phi leaks at KG speed")

    audit = ROOT / "07_validation" / "audits" / "qng-v8-b1-sm-well-v1"
    audit.mkdir(parents=True, exist_ok=True)

    def _js(d):
        out = {}
        for k, v in d.items():
            if isinstance(v, (np.floating, np.integer)):
                out[k] = v.item()
            else:
                out[k] = v
        return out

    with open(audit / "report.json", "w") as f:
        json.dump({
            'L': L, 'g': G_V_COUPLE, 'mu_phi': MU_PHI,
            'beta_phi': BETA_PHI, 'sigma_m_ref': SIGMA_M_REF,
            'sm_delta_0': sm_delta, 'sm_w': sm_w,
            'phi_amp': phi_amp, 'phi_w': phi_w, 'r_in': r_in,
            'configs': [_js({k: v for k, v in r.items()
                             if k not in ('times', 'in', 'out', 'tot')})
                        for r in results],
            'verdict': verdict,
            'center_retention_decay_frac': decay,
        }, f, indent=2)

    np.savez(audit / "phi2_traces.npz",
             **{f"times_{r['phi_mode']}": r['times'] for r in results},
             **{f"in_{r['phi_mode']}": r['in'] for r in results},
             **{f"out_{r['phi_mode']}": r['out'] for r in results},
             **{f"tot_{r['phi_mode']}": r['tot'] for r in results})

    print(f"\n  Report: {audit / 'report.json'}")


if __name__ == "__main__":
    main()
