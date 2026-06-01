"""Gravitational redshift probe for v8 (Einstein test #3c, Pound-Rebka 1960 analog).

Pound-Rebka 1960: photon frequency shifts when climbing out of a
gravitational well. In v8, the phi field has a local dispersion
  omega^2 = c_phi^2 * k^2 + m^2(x)
with m^2(x) = (g/2) * deficit(x)^2 / mu_phi.

In a ring core, deficit > 0 so m^2 > 0: locally, a phi excitation
oscillates at frequency ~ m (the mass gap).  In vacuum far from any
ring, deficit = 0 so the phi gap is zero and a point perturbation
just spreads dispersively without a gap oscillation.

Protocol:
  1. Form R=4 ring at center of L=20 box (P1=300, P2=500 lu).
  2. Identify two nodes:
       - ring_core: the node with maximum deficit (on the ring).
       - vacuum:    a node far from the ring (corner of box).
  3. Run A (baseline): clone ring state, evolve T_probe lu, record
     phi_bg at both nodes every dt_sample lu.
  4. Run B (perturbed): clone ring state, apply simultaneous kicks:
       pi_phi[ring_core_idx] += A_kick
       pi_phi[vacuum_idx]    += A_kick
     Evolve T_probe lu, record phi_p at both nodes.
  5. Extract pulse signal: s(t) = phi_p(t) - phi_bg(t).
  6. FFT each signal, find peak frequency omega_core and omega_vac.
  7. Theory: omega_core_pred = sqrt((g/2)*deficit(core)^2/mu_phi)
     (small-k approximation — point kick has broad k support).

VERDICT:
  omega_core >> omega_vac, and omega_core matches theory to O(10%):
      gravitational redshift confirmed (mass gap sourced by deficit).
  omega_core ~= omega_vac:
      no redshift signal — ring core does not gap phi.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

import qng_v8_canonical_gpu as v8
from qng_v8_canonical_gpu import (
    SIGMA_M_REF, BETA_PHI, MU_PHI, G_V_COUPLE, K_BACK, CHI_DECAY_V7,
    yoshida4_step, ring_mass_deficit,
)
from qng_v8_ring_cache import form_ring_cached

DT = 0.025
C_PHI_SQ = float(BETA_PHI) / (6.0 * float(MU_PHI))
C_PHI = float(np.sqrt(C_PHI_SQ))


def clone_state(state):
    return {k: (v.copy() if v is not None else None) for k, v in state.items()}


def evolve_and_record(state, nb_idx, T, probe_idxs, dt_sample,
                      verbose=False, label=''):
    """Evolve v8 and record phi values at probe_idxs vs time."""
    n = int(T / DT)
    sample_every = max(1, int(dt_sample / DT))
    t_rec = []
    phi_rec = []  # list of lists (one per probe)
    t0 = time.time()
    for s in range(n):
        if s % sample_every == 0:
            t_rec.append(s * DT)
            phi_rec.append([float(state['phi'][idx]) for idx in probe_idxs])
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7)
    t_rec.append(n * DT)
    phi_rec.append([float(state['phi'][idx]) for idx in probe_idxs])
    wall = time.time() - t0
    if verbose:
        print(f"    evolved {label}: {n} steps done ({wall:.1f}s)")
    return np.array(t_rec), np.array(phi_rec)


def fft_peak_frequency(t, signal):
    """Return (omega, amp) of dominant frequency via parabolic peak fit."""
    sig = signal - signal.mean()
    dt_s = t[1] - t[0]
    fft = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(len(signal), d=dt_s)
    power = np.abs(fft) ** 2
    if len(power) <= 3:
        return 0.0, 0.0
    # skip DC, find peak
    pk = int(np.argmax(power[1:])) + 1
    if 1 < pk < len(power) - 1:
        y0, y1, y2 = power[pk - 1], power[pk], power[pk + 1]
        denom = (y0 - 2 * y1 + y2)
        offset = 0.5 * (y0 - y2) / denom if denom != 0 else 0.0
        fp = freqs[pk] + offset * (freqs[1] - freqs[0])
    else:
        fp = freqs[pk]
    omega = 2 * np.pi * fp
    return float(omega), float(np.sqrt(power[pk]))


def main():
    print("=" * 80)
    print("Einstein test #3c: Gravitational redshift (Pound-Rebka 1960 analog)")
    print("=" * 80)
    print(f"  c_phi   = {C_PHI:.5f}   (phi wave speed in vacuum)")
    print(f"  c_phi^2 = {C_PHI_SQ:.5f}")
    print(f"  g       = {G_V_COUPLE}   mu_phi = {MU_PHI:.4f}")
    print()

    L = 20
    R = 4
    T_probe = 200.0
    dt_sample = 0.5    # sample phi every 0.5 lu
    A_kick = 1.0       # amplitude of pi_phi kick (momentum units)

    # --- Form ring ---
    print(f"[1] Form R={R} ring at L={L} (P1=300, P2=500) [cache-backed]")
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=500.0,
                                           verbose=True)

    # Identify probe nodes
    sm = ring_state['sm']
    deficit = SIGMA_M_REF - sm
    # Ring core: node with maximum deficit
    core_idx = int(cp.argmax(deficit))
    deficit_core = float(deficit[core_idx])
    # Vacuum: node with minimum |deficit| (closest to zero)
    # Pick box corner to be safe: (1,1,1)
    vacuum_idx = 1 + 1 * L + 1 * L * L
    deficit_vac = float(deficit[vacuum_idx])

    # Node coordinates
    def idx2xyz(i):
        return (i % L, (i // L) % L, i // (L * L))
    core_xyz = idx2xyz(core_idx)
    vac_xyz  = idx2xyz(vacuum_idx)

    print(f"\n[2] Probe nodes:")
    print(f"    core:   idx={core_idx}  pos={core_xyz}  deficit={deficit_core:+.4f}")
    print(f"    vacuum: idx={vacuum_idx}  pos={vac_xyz}  deficit={deficit_vac:+.4f}")

    # Theory: omega_core_pred = sqrt((g/2)*deficit^2/mu_phi)
    omega_core_th = float(np.sqrt(0.5 * float(G_V_COUPLE) * deficit_core ** 2
                                  / float(MU_PHI)))
    omega_vac_th  = float(np.sqrt(0.5 * float(G_V_COUPLE) * deficit_vac ** 2
                                  / float(MU_PHI)))
    print(f"\n    omega_core theory = sqrt((g/2)*def^2/mu) = {omega_core_th:.5f}")
    print(f"    omega_vac  theory                         = {omega_vac_th:.5f}")

    probe_idxs = [core_idx, vacuum_idx]

    # --- Run A: baseline (no kick) ---
    print(f"\n[3] Baseline evolution (no kick, T={T_probe} lu)")
    state_A = clone_state(ring_state)
    t, phi_A = evolve_and_record(state_A, nb_idx, T_probe, probe_idxs,
                                  dt_sample, verbose=True, label='baseline')

    # --- Run B: perturbed ---
    print(f"\n[4] Perturbed evolution (pi_phi kick A={A_kick} at both nodes, T={T_probe})")
    state_B = clone_state(ring_state)
    # Apply kicks
    pi_phi_B = state_B['pi_phi'].copy()
    pi_phi_B[core_idx]   = pi_phi_B[core_idx]   + A_kick
    pi_phi_B[vacuum_idx] = pi_phi_B[vacuum_idx] + A_kick
    state_B['pi_phi'] = pi_phi_B
    _, phi_B = evolve_and_record(state_B, nb_idx, T_probe, probe_idxs,
                                  dt_sample, verbose=True, label='perturbed')

    # Perturbation signal: s(t) = phi_B - phi_A
    s = phi_B - phi_A     # shape (nt, 2)
    s_core = s[:, 0]
    s_vac  = s[:, 1]

    # --- FFT analysis ---
    omega_core, amp_core = fft_peak_frequency(t, s_core)
    omega_vac,  amp_vac  = fft_peak_frequency(t, s_vac)

    # Also report RMS and peak-to-peak for diagnostic
    rms_core = float(np.sqrt(np.mean(s_core ** 2)))
    rms_vac  = float(np.sqrt(np.mean(s_vac ** 2)))
    pp_core  = float(s_core.max() - s_core.min())
    pp_vac   = float(s_vac.max()  - s_vac.min())

    # Zero crossings
    def zero_crossings(y):
        return int(np.sum(np.diff(np.sign(y - y.mean())) != 0))
    zc_core = zero_crossings(s_core)
    zc_vac  = zero_crossings(s_vac)
    # Empirical omega from zero crossings: omega = pi * zc / T
    omega_zc_core = np.pi * zc_core / T_probe
    omega_zc_vac  = np.pi * zc_vac  / T_probe

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"  Probe signal s(t) = phi_perturbed - phi_baseline")
    print(f"  Length = {len(t)} samples over {T_probe} lu (dt_sample={dt_sample})")
    print()
    print(f"  {'':>18} {'core':>14} {'vacuum':>14}")
    print(f"  {'RMS':>18} {rms_core:>14.5f} {rms_vac:>14.5f}")
    print(f"  {'peak-to-peak':>18} {pp_core:>14.5f} {pp_vac:>14.5f}")
    print(f"  {'zero crossings':>18} {zc_core:>14d} {zc_vac:>14d}")
    print(f"  {'omega(FFT peak)':>18} {omega_core:>14.5f} {omega_vac:>14.5f}")
    print(f"  {'omega(ZC)':>18} {omega_zc_core:>14.5f} {omega_zc_vac:>14.5f}")
    print(f"  {'omega theory':>18} {omega_core_th:>14.5f} {omega_vac_th:>14.5f}")
    print()

    # Frequency ratio
    ratio = omega_core / max(abs(omega_vac), 1e-12)
    print(f"  Ratio omega_core/omega_vac (FFT) = {ratio:.3f}")
    if omega_core_th > 0:
        err_core = (omega_core - omega_core_th) / omega_core_th * 100.0
        print(f"  omega_core error vs theory       = {err_core:+.2f}%")
    print()

    # Save signals for plotting
    outdir = ROOT / "07_validation" / "audits" / "qng-v8-stability-probe-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    np.savez(outdir / "redshift_probe_signals.npz",
             t=t, s_core=s_core, s_vac=s_vac,
             omega_core=omega_core, omega_vac=omega_vac,
             omega_core_th=omega_core_th,
             deficit_core=deficit_core, deficit_vac=deficit_vac)
    print(f"  Signals saved to {outdir / 'redshift_probe_signals.npz'}")

    print()
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    if omega_core > 2.0 * omega_vac and omega_core > 0.05:
        err_frac = abs(omega_core - omega_core_th) / max(omega_core_th, 1e-6)
        if err_frac < 0.15:
            print("GRAV REDSHIFT CONFIRMED: omega_core >> omega_vac and matches theory.")
            print("  -> Ring core gaps the phi field with m = sqrt((g/2)*def^2/mu).")
            print("  -> Pound-Rebka 1960 analog PASS.")
        else:
            print("GRAV REDSHIFT PARTIAL: omega_core >> omega_vac but theory mismatch > 15%.")
            print("  -> Mass gap exists but local-amplitude theory insufficient.")
            print("  -> Possible corrections: gradient terms, deficit-neighbor mixing.")
    elif omega_core > 0.05:
        print(f"WEAK SIGNAL: omega_core = {omega_core:.4f}, only {ratio:.1f}x vacuum.")
        print("  -> Effect present but marginal. Run longer T_probe or larger A_kick.")
    else:
        print("NULL RESULT: no significant oscillation at core.")
        print("  -> Possible: nonlinear suppression, kick too weak, ring core moved.")


if __name__ == "__main__":
    main()
