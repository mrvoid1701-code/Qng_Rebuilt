"""QNG-GPU-036: Tesla 3D sine-Gordon breather test.

v8 V_couple = (g/2)(sigma_ref - sigma_m)^2 (1 - cos phi) gives phi the
1+1 sine-Gordon equation (with position-dependent mass). In 1+1 SG admits
exact breathers (Dashen-Hasslacher-Neveu mass spectrum). We test whether
a radial 3D breather approximation survives for multiple periods under
full v8 canonical dynamics on a cubic lattice.

Setup (uniform sigma_m deficit, flat sigma_g):
  sigma_m = SIGMA_M_REF - DELTA (uniform)
  m_eff^2 = (g/mu_phi) * DELTA^2
  m_eff   = sqrt(m_eff^2)

Breather parametrization: pick sub-luminal mass ratio 0 < theta < pi/2:
  omega = m * cos(theta)      oscillation frequency
  eta   = m * sin(theta)      spatial decay rate (inverse width)
  T_pred = 2*pi / omega
  A_max  = 4 * arctan(tan(theta))     max field amplitude at core

Initial condition (3D radial approx at t=0):
  phi(r, 0)   = 0
  dphi/dt|_0 = 4*eta*sech(eta*r)  (from 1+1 breather at t=0)
  pi_phi(r,0) = mu_phi * 4*eta*sech(eta*r)

Canonical v8 params: DELTA=0.20 -> m=0.1013.
theta = pi/3 -> omega=0.0507, eta=0.0877, T_pred=123.9 lu, width=11.4 lu.

Gates:
  G1: Central |phi(r=0,t)| reaches amplitude > 0.5 rad within first period.
  G2: Dominant oscillation period of phi(r=0, t) within 25% of T_pred.
  G3: Energy drift |dH/H_0| < 2% over full run.
  G4: Pulse remains localized (fraction of E_field in central ball r<L/4
      stays > 40% of initial at t=T_run).

Interpretation:
  All pass: 3D breather analog survives; v8 admits soliton-like nonlinear
  phi structures independent of ring sigma_m wells.
  G1+G2 pass, G4 fail: oscillates but radiates (no stable 3D breather).
  G1 fail: pulse dissolves -- no breather regime in v8.
"""
from __future__ import annotations

import argparse
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
    G_V_COUPLE, MU_PHI, BETA_PHI,
)

EXACT_A_MODE = 'r1'


def make_breather_state(L, delta, theta_rad):
    """Flat sigma_g, flat sigma_m=ref-delta, 3D radial breather IC for phi."""
    N = L * L * L
    m2 = (G_V_COUPLE / MU_PHI) * delta * delta
    m_val = float(np.sqrt(m2))
    omega = m_val * np.cos(theta_rad)
    eta = m_val * np.sin(theta_rad)
    T_pred = 2.0 * np.pi / omega if omega > 0 else float('inf')
    width = 1.0 / eta if eta > 0 else float('inf')

    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    cx = cy = cz = (L - 1) / 2.0
    r = np.sqrt((xg - cx) ** 2 + (yg - cy) ** 2 + (zg - cz) ** 2)

    phi = np.zeros_like(r)
    dphi_dt = 4.0 * eta / np.cosh(eta * r)
    pi_phi_np = MU_PHI * dphi_dt

    state = {
        'sg':  cp.full(N, SIGMA_G_REF, dtype=cp.float64),
        'sm':  cp.full(N, SIGMA_M_REF - delta, dtype=cp.float64),
        'chi': cp.zeros(N, dtype=cp.float64),
        'phi': cp.asarray(phi.ravel()),
        'pi_m':   cp.zeros(N, dtype=cp.float64),
        'pi_phi': cp.asarray(pi_phi_np.ravel()),
    }
    meta = {
        'm_eff': m_val, 'm_eff_sq': m2,
        'omega': float(omega), 'eta': float(eta),
        'T_pred_lu': float(T_pred), 'width_lu': float(width),
        'theta_rad': float(theta_rad),
    }
    return state, meta, r


def central_field(state, L):
    """Return phi at lattice center index."""
    cx = cy = cz = L // 2
    idx = (cx * L + cy) * L + cz
    return float(state['phi'][idx])


def central_ball_energy_fraction(state, r_flat, r_cut):
    """Fraction of pi_phi^2 + grad terms inside radius r_cut. Approximated as
    fraction of pi_phi^2 energy (kinetic), which dominates breather energy."""
    pi_phi_np = cp.asnumpy(state['pi_phi'])
    e_density = 0.5 * pi_phi_np * pi_phi_np / MU_PHI
    mask = r_flat < r_cut
    if mask.sum() == 0:
        return 0.0
    total = e_density.sum()
    if total <= 0:
        return 0.0
    return float(e_density[mask].sum() / total)


def fit_oscillation_period(times, values, max_n_periods=10):
    v = np.asarray(values, dtype=np.float64)
    t = np.asarray(times, dtype=np.float64)
    v_centered = v - np.mean(v)
    zc = []
    for i in range(1, len(v_centered)):
        if v_centered[i - 1] < 0 and v_centered[i] >= 0:
            t_cross = t[i - 1] + (t[i] - t[i - 1]) * (
                -v_centered[i - 1]) / (v_centered[i] - v_centered[i - 1])
            zc.append(t_cross)
    if len(zc) < 2:
        return None, 0
    n_use = min(len(zc), max_n_periods + 1)
    periods = np.diff(zc[:n_use])
    if len(periods) == 0:
        return None, 0
    return float(np.mean(periods)), len(periods)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--L", type=int, default=32)
    parser.add_argument("--delta", type=float, default=0.20)
    parser.add_argument("--theta_deg", type=float, default=60.0,
                        help="breather angle in degrees (0<theta<90)")
    parser.add_argument("--T_run", type=float, default=600.0)
    parser.add_argument("--DT", type=float, default=0.025)
    parser.add_argument("--audit_name", type=str,
                        default="qng-v8-sg-breather-v1")
    args = parser.parse_args()

    L = args.L
    DT = args.DT
    T_run = args.T_run
    theta_rad = np.radians(args.theta_deg)
    n_steps = int(T_run / DT)
    sample_every = int(1.0 / DT)

    outdir = ROOT / "07_validation" / "audits" / args.audit_name
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("QNG-GPU-036: Tesla 3D sine-Gordon breather test")
    print("=" * 80)

    nb_idx = build_nb(L)
    state, meta, r_flat = make_breather_state(L, args.delta, theta_rad)
    r_flat = r_flat.ravel()

    print(f"  L={L}, delta={args.delta}, theta={args.theta_deg:.1f} deg")
    print(f"  m_eff  = {meta['m_eff']:.4f}")
    print(f"  omega  = {meta['omega']:.4f}")
    print(f"  eta    = {meta['eta']:.4f}  (width={meta['width_lu']:.2f} lu)")
    print(f"  T_pred = {meta['T_pred_lu']:.2f} lu")
    print(f"  T_run  = {T_run} lu  ({n_steps} Yoshida4 steps)")

    r_cut = L / 4.0
    E0_frac = central_ball_energy_fraction(state, r_flat, r_cut)

    H0 = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                              exact_a=EXACT_A_MODE))
    phi_central_t0 = central_field(state, L)

    times = [0.0]
    phi_central = [phi_central_t0]
    phi_max_abs = [float(cp.max(cp.abs(state['phi'])))]
    H_trace = [H0]
    ball_frac = [E0_frac]

    t0 = time.time()
    last_print = time.time()
    for s in range(1, n_steps + 1):
        state = yoshida4_step(state, DT, nb_idx,
                              v_couple_on=True, chi_decay=CHI_DECAY_V7,
                              exact_a=EXACT_A_MODE)
        if s % sample_every == 0:
            t_phys = s * DT
            times.append(t_phys)
            phi_central.append(central_field(state, L))
            phi_max_abs.append(float(cp.max(cp.abs(state['phi']))))
            if s % (sample_every * 50) == 0:
                H = float(hamiltonian_v8(state, nb_idx, channel_f=True,
                                         k_gm=0.0, exact_a=EXACT_A_MODE))
                bf = central_ball_energy_fraction(state, r_flat, r_cut)
                H_trace.append(H)
                ball_frac.append(bf)
                now = time.time()
                if now - last_print > 8.0:
                    print(f"    t={t_phys:7.1f}  phi_c={phi_central[-1]:+.3f}  "
                          f"|phi|_max={phi_max_abs[-1]:.3f}  "
                          f"H={H:.3f}  dH/H0={abs(H-H0)/abs(H0):.1e}  "
                          f"ball={bf:.2f}")
                    last_print = now
    wall = time.time() - t0

    H1 = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                              exact_a=EXACT_A_MODE))
    E1_frac = central_ball_energy_fraction(state, r_flat, r_cut)
    H_drift = abs(H1 - H0) / abs(H0) if abs(H0) > 1e-10 else 0.0

    # Peak amplitude in first predicted period
    t_arr = np.asarray(times)
    pc_arr = np.asarray(phi_central)
    first_period_mask = t_arr <= meta['T_pred_lu']
    if first_period_mask.sum() > 0:
        amp_first_period = float(np.max(np.abs(pc_arr[first_period_mask])))
    else:
        amp_first_period = 0.0
    amp_total = float(np.max(np.abs(pc_arr)))

    T_meas, n_per = fit_oscillation_period(times, phi_central)

    # Gates
    G1 = amp_first_period > 0.5
    G2 = False
    if T_meas is not None and meta['T_pred_lu'] < float('inf'):
        G2 = abs(T_meas / meta['T_pred_lu'] - 1.0) < 0.25
    G3 = H_drift < 0.02
    G4 = E1_frac / E0_frac > 0.4 if E0_frac > 0 else False

    all_pass = G1 and G2 and G3 and G4
    verdict = "SG_BREATHER_SURVIVES" if all_pass else (
        "SG_BREATHER_RADIATES" if (G1 and G2 and not G4) else (
            "SG_BREATHER_DISSOLVES" if not G1 else "SG_BREATHER_INCONCLUSIVE"))

    print("\n" + "=" * 80)
    print("TESLA BREATHER RESULTS")
    print("=" * 80)
    print(f"  amp in first period   = {amp_first_period:.3f} rad")
    print(f"  amp overall           = {amp_total:.3f} rad")
    print(f"  T_measured            = {T_meas if T_meas else 'n/a'} lu (n={n_per})")
    print(f"  T_predicted           = {meta['T_pred_lu']:.2f} lu")
    if T_meas is not None:
        print(f"  ratio T_meas/T_pred   = {T_meas/meta['T_pred_lu']:+.3f}")
    print(f"  H drift               = {H_drift:.2e}")
    print(f"  ball_frac  t=0        = {E0_frac:.3f}")
    print(f"  ball_frac  t=T        = {E1_frac:.3f}")
    print(f"  retention ratio       = {E1_frac/E0_frac if E0_frac>0 else 0:.3f}")
    print(f"\n  G1 (amp > 0.5 in 1st period): {G1}")
    print(f"  G2 (T within 25% of pred):    {G2}")
    print(f"  G3 (dH/H < 2%):                {G3}")
    print(f"  G4 (ball retention > 40%):    {G4}")
    print(f"\n  VERDICT: {verdict}")
    print(f"  Wall: {wall:.1f} s")

    # JSON report
    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L,
            'delta': args.delta,
            'theta_deg': args.theta_deg,
            'T_run': T_run, 'DT': DT,
            'exact_a_mode': EXACT_A_MODE,
            'meta': meta,
            'H0': H0, 'H1': H1, 'H_drift': H_drift,
            'amp_first_period': amp_first_period,
            'amp_total': amp_total,
            'T_measured_lu': T_meas,
            'n_periods': n_per,
            'ball_frac_t0': E0_frac,
            'ball_frac_tT': E1_frac,
            'retention_ratio': E1_frac/E0_frac if E0_frac>0 else 0,
            'gates': {'G1': G1, 'G2': G2, 'G3': G3, 'G4': G4},
            'verdict': verdict,
            'wall_s': wall,
        }, f, indent=2)

    np.savez(outdir / "breather_traces.npz",
             times=np.asarray(times),
             phi_central=np.asarray(phi_central),
             phi_max_abs=np.asarray(phi_max_abs),
             H_trace=np.asarray(H_trace),
             ball_frac=np.asarray(ball_frac))

    print(f"\n  Report: {outdir / 'report.json'}")


if __name__ == "__main__":
    main()
