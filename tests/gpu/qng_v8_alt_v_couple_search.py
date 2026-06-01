"""QNG-GPU-028: Alternate V_couple forms — can any coupling stabilize the 3D ring?

DER-QNG-047 established that v8 3D admits no static ring under the canonical
sine-Gordon V_couple = (g/2)*Delta^2*(1-cos phi). GPU-024d v2 ruled out both
V_couple-on (g=0.22) and V_couple-off (g=0). DER-QNG-048 topology analysis
suggests V_couple sine-Gordon is a GENERIC local obstruction that will act
the same way in 4D — making a 4D probe redundant until the 3D V_couple
question is settled.

This probe tests three alternate couplings + control, each via 30000 iter
gradient-flow relaxation from the cached L=28 R=4 ring:

  (a) phi-mass (quadratic):  V = (g/2)*Delta^2 * phi^2 / 2
       → F_phi contribution = -g*Delta^2*phi; preserves continuous U(1) as
         mass-type term, NO winding obstruction

  (b) doubled-pitch:          V = (g/2)*Delta^2 * (1-cos 2phi)
       → F_phi contribution ~ -g*Delta^2*sin(2phi); winding Z protected
         only modulo pi (π_1(S^1/Z_2)=Z_2), no single-2pi obstruction

  (c) quartic:                V = (g/4)*Delta^2 * (1-cos phi)^2
       → weaker local pull (linear in deficit vs phi deviation)

  (d) control:                V = 0 (matches GPU-024d v2 Run B)

Verdict per run:
  SURVIVES : M_final >= 50      (ring intact or nearly so)
  SHRUNK   : 1 <= M_final < 50  (partial survival)
  DISSOLVED: M_final < 1        (fully dissolved)

Overall:
  V_COUPLE_RESCUED : at least one of (a),(b),(c) SURVIVES
  V_COUPLE_SHRINKS : all dissolve but some significantly slower than (d)
  NO_RESCUE        : all behave like (d); obstruction is NOT V_couple-form
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
    SIGMA_M_REF, ALPHA, BETA_M, BETA_PHI, G_V_COUPLE,
    nb_mean, phi_wmean_gpu, wrap_gpu,
    ring_mass_deficit,
)
from qng_v8_ring_cache import form_ring_cached


# -------- common sigma_m force (no Channel F, for all four runs) --------
def F_sm_base(sm, phi, nb_idx):
    smb = nb_mean(sm, nb_idx)
    return ALPHA * (SIGMA_M_REF - sm) + BETA_M * (smb - sm)


# Each variant adds its own V_couple contribution to F_sm and F_phi.
# F_couple_sm = -dV/dsm; F_couple_phi_dot_factor added to F_phi
# Note: gradient-flow steps phi += dt * F_phi where F_phi = BETA_PHI*(pm-phi) + extra

def F_sm_a(sm, phi, nb_idx, g):
    """(a) phi-mass: V = (g/2)*Delta^2 * phi^2/2."""
    base = F_sm_base(sm, phi, nb_idx)
    deficit = SIGMA_M_REF - sm
    # dV/d sm = -g*deficit * phi^2/2 → F_sm adds +g*deficit*phi^2/2
    return base + 0.5 * g * deficit * phi * phi


def F_phi_a(sm, phi, nb_idx, g):
    pm = phi_wmean_gpu(phi, sm, nb_idx)
    deficit = SIGMA_M_REF - sm
    # dV/d phi = (g/2)*Delta^2 * phi → F_phi adds -g*Delta^2*phi
    return BETA_PHI * wrap_gpu(pm - phi) - 0.5 * g * deficit * deficit * phi


def F_sm_b(sm, phi, nb_idx, g):
    """(b) doubled-pitch: V = (g/2)*Delta^2*(1 - cos 2phi)."""
    base = F_sm_base(sm, phi, nb_idx)
    deficit = SIGMA_M_REF - sm
    return base + g * deficit * (1.0 - cp.cos(2.0 * phi))


def F_phi_b(sm, phi, nb_idx, g):
    pm = phi_wmean_gpu(phi, sm, nb_idx)
    deficit = SIGMA_M_REF - sm
    # dV/dphi = (g/2)*Delta^2 * 2 sin(2phi)
    return BETA_PHI * wrap_gpu(pm - phi) - g * deficit * deficit * cp.sin(2.0 * phi)


def F_sm_c(sm, phi, nb_idx, g):
    """(c) quartic: V = (g/4)*Delta^2*(1-cos phi)^2."""
    base = F_sm_base(sm, phi, nb_idx)
    deficit = SIGMA_M_REF - sm
    omc = 1.0 - cp.cos(phi)
    return base + 0.5 * g * deficit * omc * omc


def F_phi_c(sm, phi, nb_idx, g):
    pm = phi_wmean_gpu(phi, sm, nb_idx)
    deficit = SIGMA_M_REF - sm
    omc = 1.0 - cp.cos(phi)
    # dV/dphi = (g/4)*Delta^2 * 2*(1-cos phi)*sin phi = (g/2)*Delta^2*omc*sin phi
    return BETA_PHI * wrap_gpu(pm - phi) - 0.5 * g * deficit * deficit * omc * cp.sin(phi)


def F_sm_d(sm, phi, nb_idx):
    """(d) control: V = 0."""
    return F_sm_base(sm, phi, nb_idx)


def F_phi_d(sm, phi, nb_idx):
    pm = phi_wmean_gpu(phi, sm, nb_idx)
    return BETA_PHI * wrap_gpu(pm - phi)


def relax(sm_init, phi_init, nb_idx, label, F_sm_fn, F_phi_fn, dt_relax, N_ITER, log_every):
    sm = sm_init.copy(); phi = phi_init.copy()
    M0 = float(cp.sum(SIGMA_M_REF - sm))
    print(f"\n=== {label} ===  dt={dt_relax}  N={N_ITER}")
    print(f"  init M_ring = {M0:.4f}")
    hist = []
    t0 = time.time()
    for it in range(N_ITER + 1):
        if it % log_every == 0:
            F_sm = F_sm_fn(sm, phi, nb_idx)
            F_phi = F_phi_fn(sm, phi, nb_idx)
            rms_sm = float(cp.sqrt(cp.mean(F_sm ** 2)))
            rms_phi = float(cp.sqrt(cp.mean(F_phi ** 2)))
            M = float(cp.sum(SIGMA_M_REF - sm))
            hist.append({'iter': it, 'M': M, 'F_sm': rms_sm, 'F_phi': rms_phi})
            print(f"  {it:>6} M={M:>9.4f}  ||F_sm||={rms_sm:.3e}  ||F_phi||={rms_phi:.3e}")
            if rms_sm < 1e-7 and rms_phi < 1e-7:
                print("  CONVERGED"); break
            if abs(M) < 0.1:
                print("  DISSOLVED"); break
        if it == N_ITER: break
        F_sm = F_sm_fn(sm, phi, nb_idx)
        F_phi = F_phi_fn(sm, phi, nb_idx)
        sm = cp.clip(sm + dt_relax * F_sm, 0.0, 1.0)
        phi = wrap_gpu(phi + dt_relax * F_phi)
    wall = time.time() - t0
    M_final = float(cp.sum(SIGMA_M_REF - sm))
    F_sm_final = float(cp.sqrt(cp.mean(F_sm_fn(sm, phi, nb_idx) ** 2)))
    F_phi_final = float(cp.sqrt(cp.mean(F_phi_fn(sm, phi, nb_idx) ** 2)))
    print(f"  --- FINAL: M={M_final:.4f}  ||F_sm||={F_sm_final:.3e}  "
          f"||F_phi||={F_phi_final:.3e}  ({wall:.1f}s)")
    return {
        'label': label, 'M_initial': M0, 'M_final': M_final,
        'F_sm_final': F_sm_final, 'F_phi_final': F_phi_final,
        'history': hist, 'runtime_sec': wall,
    }


def main():
    print("=" * 80)
    print("QNG-GPU-028: Alternate V_couple forms — does any coupling stabilize the 3D ring?")
    print("=" * 80)

    g = G_V_COUPLE  # 0.22

    L = 28; R = 4
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0, verbose=True)
    M0 = float(ring_mass_deficit(ring_state['sm']))
    print(f"  cached M_ring = {M0:.4f}  g = {g}")
    sm_init = ring_state['sm']; phi_init = ring_state['phi']

    dt = 0.05; N = 30000; LOG = 3000

    configs = [
        ('a_phi_mass',  lambda s, p, n: F_sm_a(s, p, n, g), lambda s, p, n: F_phi_a(s, p, n, g)),
        ('b_double_pitch', lambda s, p, n: F_sm_b(s, p, n, g), lambda s, p, n: F_phi_b(s, p, n, g)),
        ('c_quartic',   lambda s, p, n: F_sm_c(s, p, n, g), lambda s, p, n: F_phi_c(s, p, n, g)),
        ('d_control_V0', F_sm_d, F_phi_d),
    ]

    results = {}
    for label, Fs, Fp in configs:
        results[label] = relax(sm_init, phi_init, nb_idx, label, Fs, Fp, dt, N, LOG)

    def classify(M):
        if M >= 50.0: return 'SURVIVES'
        if M < 1.0: return 'DISSOLVED'
        return 'SHRUNK'

    states = {k: classify(v['M_final']) for k, v in results.items()}

    survives = [k for k in ('a_phi_mass', 'b_double_pitch', 'c_quartic') if states[k] == 'SURVIVES']
    shrunk = [k for k in ('a_phi_mass', 'b_double_pitch', 'c_quartic') if states[k] == 'SHRUNK']

    if survives:
        verdict = 'V_COUPLE_RESCUED'
    elif shrunk:
        verdict = 'V_COUPLE_PARTIAL'
    else:
        verdict = 'NO_RESCUE'

    print("\n" + "=" * 80)
    print("GPU-028 SUMMARY")
    print("=" * 80)
    for k, v in results.items():
        print(f"  {k:20s}  M_final={v['M_final']:>9.4f}  [{states[k]}]  ({v['runtime_sec']:.1f}s)")
    print(f"\n  VERDICT: {verdict}")

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-alt-v-couple-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'g': g, 'dt': dt, 'N_ITER': N,
            'M_cached': M0,
            'results': results, 'states': states, 'verdict': verdict,
        }, f, indent=2)
    print(f"  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
