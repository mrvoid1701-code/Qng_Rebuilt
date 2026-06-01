"""Shapiro anisotropy probe — Einstein's suggested tensorial-signature test.

Einstein (2026-04-20): 'Run the pulse parallel vs transverse to the ring
axis.  A scalar delay has no preferred direction beyond the deficit
profile, but a real geometric coupling will show a quadrupolar signature
because the ring has a characteristic plane.'

Ring geometry (v8 init_phi_single_ring):
  rho = sqrt(dx^2 + dy^2),  phi = arctan2(dz, rho-R)
  -> ring lies in xy plane, axis along z.

Two Shapiro geometries (cached L=28 R=4 ring):
  (T) Transverse: pulse along +x at y=y_c+R (in ring plane, through rim) -- ORIGINAL
  (P) Parallel:   pulse along +z at x=y_c, y=y_c (through ring center, along axis)

Per geometry: 1 vacuum + 1 ring_only + 1 ring+pulse.

VERDICT:
  |dt_T - dt_P| / mean < 5%   -> SCALAR coupling (isotropic, 1911-like)
  |dt_T - dt_P| / mean > 20%  -> TENSORIAL quadrupolar coupling (GR-like)
  5-20%                        -> MARGINAL: investigate with rotated geometries

NOTE: Path lengths are equal (both 20 nodes, x_source=z_source=4 to
x_detect=z_detect=L-4) so delays are directly comparable.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

from qng_v8_canonical_gpu import (
    SIGMA_M_REF, BETA_PHI, MU_PHI, G_V_COUPLE, K_BACK, CHI_DECAY_V7,
    build_nb, make_state, yoshida4_step, ring_mass_deficit,
)
from qng_v8_ring_cache import form_ring_cached

DT = 0.025
C_PHI_SQ = float(BETA_PHI) / (6.0 * float(MU_PHI))
C_PHI    = float(np.sqrt(C_PHI_SQ))


def make_coords(L):
    N = L * L * L
    idx = cp.arange(N, dtype=cp.int64)
    x = (idx % L).astype(cp.float64)
    y = ((idx // L) % L).astype(cp.float64)
    z = (idx // (L * L)).astype(cp.float64)
    return x, y, z


def inject_pulse_xdir(state, xc, yc, zc, x0, y0, z0, sigma, k, A):
    """+x propagating pulse."""
    omega = C_PHI * k
    env = cp.exp(-(((xc - x0) ** 2 + (yc - y0) ** 2 + (zc - z0) ** 2)
                   / (2.0 * sigma ** 2)))
    state['phi']    = state['phi']    + A * env * cp.cos(k * (xc - x0))
    state['pi_phi'] = state['pi_phi'] - MU_PHI * omega * A * env \
                                         * cp.sin(k * (xc - x0))


def inject_pulse_zdir(state, xc, yc, zc, x0, y0, z0, sigma, k, A):
    """+z propagating pulse (along ring axis)."""
    omega = C_PHI * k
    env = cp.exp(-(((xc - x0) ** 2 + (yc - y0) ** 2 + (zc - z0) ** 2)
                   / (2.0 * sigma ** 2)))
    state['phi']    = state['phi']    + A * env * cp.cos(k * (zc - z0))
    state['pi_phi'] = state['pi_phi'] - MU_PHI * omega * A * env \
                                         * cp.sin(k * (zc - z0))


def clone_state(state):
    return {k: (v.copy() if v is not None else None) for k, v in state.items()}


def evolve_record(state, nb_idx, T, det_idx, sample_every,
                  verbose=False, label=''):
    n = int(T / DT)
    t_rec = []
    phi_rec = []
    t0 = time.time()
    for s in range(n):
        if s % sample_every == 0:
            t_rec.append(s * DT)
            phi_rec.append(float(state['phi'][det_idx]))
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7)
    t_rec.append(n * DT)
    phi_rec.append(float(state['phi'][det_idx]))
    if verbose:
        print(f"    evolved {label}: {n} steps ({time.time()-t0:.1f}s)")
    return np.array(t_rec), np.array(phi_rec)


def find_peak_arrival(t, phi):
    abs_sig = np.abs(phi)
    window = 3
    env = np.convolve(abs_sig, np.ones(window) / window, mode='same')
    i_peak = int(np.argmax(env))
    return float(t[i_peak]), float(env[i_peak])


def run_geometry(geom_label, pulse_inject_fn, src, det, state_ring,
                 nb_idx, T_track, sample_every, xc, yc, zc, L, k_pkt,
                 sigma_pkt, A_pkt):
    """Run vacuum + ring_only + ring+pulse for one geometry.

    src, det: (x, y, z) tuples.
    pulse_inject_fn: inject_pulse_xdir or inject_pulse_zdir.
    Returns dict with t_peak_vac, t_peak_ring, dt.
    """
    xd, yd, zd = det
    xd_i, yd_i, zd_i = int(round(xd)), int(round(yd)), int(round(zd))
    det_idx = xd_i + yd_i * L + zd_i * L * L

    # Vacuum
    vac = make_state(L, phi_init=None)
    pulse_inject_fn(vac, xc, yc, zc, *src, sigma_pkt, k_pkt, A_pkt)
    t_v, phi_v = evolve_record(vac, nb_idx, T_track, det_idx,
                                sample_every, verbose=True,
                                label=f'{geom_label} vacuum')
    tp_v, amp_v = find_peak_arrival(t_v, phi_v)
    print(f"    vac  peak t={tp_v:.2f}  amp={amp_v:.5f}")

    # Ring-only bg
    bg = clone_state(state_ring)
    _, phi_bg = evolve_record(bg, nb_idx, T_track, det_idx,
                               sample_every, verbose=True,
                               label=f'{geom_label} ring_only')

    # Ring+pulse
    rp = clone_state(state_ring)
    pulse_inject_fn(rp, xc, yc, zc, *src, sigma_pkt, k_pkt, A_pkt)
    t_r, phi_r = evolve_record(rp, nb_idx, T_track, det_idx,
                                sample_every, verbose=True,
                                label=f'{geom_label} ring+pulse')
    phi_pulse = phi_r - phi_bg
    tp_r, amp_r = find_peak_arrival(t_r, phi_pulse)
    print(f"    ring peak t={tp_r:.2f}  amp={amp_r:.5f}")
    dt = tp_r - tp_v
    print(f"    -> dt = {dt:+.3f} lu   ({dt/tp_v*100:+.2f}%)")
    return {
        'label': geom_label, 'tp_vac': tp_v, 'tp_ring': tp_r, 'dt': dt,
        'amp_vac': amp_v, 'amp_ring': amp_r,
        't_vec': t_v, 'phi_vac': phi_v, 'phi_pulse': phi_pulse,
    }


def main():
    print("=" * 80)
    print("Shapiro anisotropy probe — Einstein's tensorial-signature test")
    print("  (parallel vs transverse to ring axis)")
    print("=" * 80)

    L = 28
    R = 4
    T_track = 250.0
    DT_sample = 1.0
    sample_every = int(DT_sample / DT)

    sigma_pkt = 2.0
    k_pkt     = np.pi / 4.0
    A_pkt     = 0.05

    xc, yc, zc = make_coords(L)
    c_pos = 0.5 * L           # ring center coord (= 14)
    offset_rim = R            # = 4

    # --- Ring cache ---
    print(f"  L={L}  R={R}  T_track={T_track} lu")
    print(f"  c_phi={C_PHI:.5f}")
    print()
    print("[0] Load cached ring")
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0,
                                           verbose=True)
    M_ring0 = float(ring_mass_deficit(ring_state['sm']))
    print(f"    ring loaded, M_ring={M_ring0:.2f}")
    print()

    # --- Geometry T: transverse (pulse along +x at y=L/2+R, z=L/2) ---
    print("-" * 60)
    print("(T) Transverse geometry  [pulse +x, y=L/2+R, z=L/2]")
    print("-" * 60)
    src_T = (4.0,          c_pos + offset_rim, c_pos)
    det_T = (L - 4.0,      c_pos + offset_rim, c_pos)
    res_T = run_geometry('T', inject_pulse_xdir, src_T, det_T,
                          ring_state, nb_idx, T_track, sample_every,
                          xc, yc, zc, L, k_pkt, sigma_pkt, A_pkt)
    print()

    # --- Geometry P: parallel to axis (pulse along +z at x=L/2, y=L/2) ---
    print("-" * 60)
    print("(P) Parallel geometry    [pulse +z, x=L/2, y=L/2]  (through axis)")
    print("-" * 60)
    src_P = (c_pos, c_pos, 4.0)
    det_P = (c_pos, c_pos, L - 4.0)
    res_P = run_geometry('P', inject_pulse_zdir, src_P, det_P,
                          ring_state, nb_idx, T_track, sample_every,
                          xc, yc, zc, L, k_pkt, sigma_pkt, A_pkt)
    print()

    # --- Analysis ---
    print("=" * 80)
    print("ANISOTROPY RESULTS")
    print("=" * 80)
    dt_T = res_T['dt']
    dt_P = res_P['dt']
    mean = 0.5 * (dt_T + dt_P)
    asym = abs(dt_T - dt_P) / max(abs(mean), 1e-6)
    print(f"  dt_Transverse (through rim, +x)        = {dt_T:+.3f} lu")
    print(f"  dt_Parallel   (through axis, +z)       = {dt_P:+.3f} lu")
    print(f"  mean |dt|                              = {abs(mean):.3f} lu")
    print(f"  anisotropy = |dt_T - dt_P| / mean      = {asym*100:.2f}%")
    print()
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    if asym < 0.05:
        print(f"ISOTROPIC: anisotropy {asym*100:.2f}% < 5% noise floor.")
        print("  -> Shapiro coupling is SCALAR (1911-like).  No tensor signature.")
        print("  -> Pulse cannot distinguish ring orientation.")
    elif asym < 0.20:
        print(f"MARGINAL: anisotropy {asym*100:.2f}% in 5-20% band.")
        print("  -> Possible tensorial structure; repeat at higher S/N (L=40).")
    else:
        print(f"TENSORIAL: anisotropy {asym*100:.2f}% >= 20%.")
        print("  -> Ring direction couples to pulse — QUADRUPOLAR signature.")
        print("  -> Consistent with spin-2-like mediator, not pure scalar.")
        print("  -> STRONG evidence AGAINST 1911 dead-end interpretation.")

    # Save
    outdir = ROOT / "07_validation" / "audits" / "qng-v8-stability-probe-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    np.savez(outdir / "anisotropy_probe_signals.npz",
             L=L, R=R, c_phi=C_PHI, M_ring0=M_ring0,
             dt_T=dt_T, dt_P=dt_P, asym=asym,
             t_T=res_T['t_vec'], phi_vac_T=res_T['phi_vac'],
             phi_pulse_T=res_T['phi_pulse'],
             t_P=res_P['t_vec'], phi_vac_P=res_P['phi_vac'],
             phi_pulse_P=res_P['phi_pulse'])
    print(f"\n  Signals saved to {outdir / 'anisotropy_probe_signals.npz'}")


if __name__ == "__main__":
    main()
