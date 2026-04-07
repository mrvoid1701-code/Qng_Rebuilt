from __future__ import annotations

"""
QNG-CPU-059: Conservative Hamiltonian ring dynamics.

Tests whether the v5 ring survives under pure Hamilton's equations
(no dissipation: no Channel A, no Channel F, no chi_decay).

If ring dissolves: it is NOT a soliton of H -- Gap 7 confirmed.
If ring survives: surprising finding requiring re-examination.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-conservative-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

L: int = 20
N: int = L * L * L
PHASE1_STEPS: int = 300
PHASE2_STEPS: int = 1500
SNAPSHOT_T: int = 1000    # Phase-2 step at which we switch to conservative dynamics

K_BACK: float = 0.10      # k_back for conservative Hamiltonian

SIGMA_REF: float = 0.5
ALPHA:     float = 0.005
BETA:      float = 0.35
BETA_PHI:  float = 0.02
DELTA:     float = 0.20
CHI_DECAY: float = 0.005
CHI_REL:   float = 0.35
GAMMA_PHI: float = 0.10

RING_R: float = 5.0
RING_X: float = L / 2.0
RING_Y: float = L / 2.0
RING_Z: float = L / 2.0

# Conservative dynamics parameters
DT_HAM: float = 0.005    # Hamiltonian time step
HAM_STEPS: int = 500     # Total conservative steps
HAM_CHECK: int = 25      # Report every N steps


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def idx3(x: int, y: int, z: int) -> int:
    return (x % L) * L * L + (y % L) * L + (z % L)

def coord3(i: int) -> tuple[int, int, int]:
    x = i // (L * L); y = (i % (L * L)) // L; z = i % L
    return x, y, z

def _mi(d: float) -> float:
    while d >  L / 2: d -= L
    while d < -L / 2: d += L
    return d

def wrap(a: float) -> float:
    a = a % (2 * math.pi)
    return a - 2 * math.pi if a > math.pi else a

def angle_diff(a: float, b: float) -> float:
    return wrap(a - b)

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))

def neighbors(x: int, y: int, z: int) -> list[int]:
    return [idx3(x-1,y,z), idx3(x+1,y,z),
            idx3(x,y-1,z), idx3(x,y+1,z),
            idx3(x,y,z-1), idx3(x,y,z+1)]


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def init_phi_ring() -> list[float]:
    phi = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - RING_X); dy = _mi(y - RING_Y); dz = _mi(z - RING_Z)
        rho = math.sqrt(dx*dx + dy*dy)
        phi.append(math.atan2(dz, rho - RING_R))
    return phi

def phase_disorder(phi: list[float], i: int) -> float:
    x, y, z = coord3(i)
    nb = neighbors(x, y, z)
    sx = sum(math.cos(phi[j]) for j in nb) / 6.0
    sy = sum(math.sin(phi[j]) for j in nb) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx*sx + sy*sy))


# ---------------------------------------------------------------------------
# v5 dissipative update (used to form the ring)
# ---------------------------------------------------------------------------

def update_step_v5(sigma: list[float], chi: list[float], phi: list[float],
                   channel_f: bool) -> tuple[list, list, list]:
    ns, nc, np_ = [], [], []
    for i in range(N):
        x, y, z = coord3(i)
        nb = neighbors(x, y, z)
        sigma_bar = sum(sigma[j] for j in nb) / 6.0
        si = sigma[i]; ci = chi[i]; pi = phi[i]

        ds = ALPHA*(SIGMA_REF - si) + BETA*(sigma_bar - si)
        if channel_f:
            D_i = phase_disorder(phi, i)
            ds -= GAMMA_PHI * D_i * si
        ns.append(clip01(si + ds))

        nc.append(ci*(1-CHI_DECAY)
                  + CHI_REL*(sigma_bar - si)
                  + DELTA*(SIGMA_REF - si))

        nb_sig = [sigma[j] for j in nb]
        nb_phi = [phi[j] for j in nb]
        tw = sum(nb_sig)
        if tw > 1e-10:
            sx2 = sum(nb_sig[k]*math.cos(nb_phi[k]) for k in range(6)) / tw
            sy2 = sum(nb_sig[k]*math.sin(nb_phi[k]) for k in range(6)) / tw
            pm = math.atan2(sy2, sx2)
        else:
            pm = pi
        np_.append(wrap(pi + BETA_PHI*angle_diff(pm, pi)))

    return ns, nc, np_


# ---------------------------------------------------------------------------
# Conservative Hamiltonian update (Hamilton's equations, no dissipation)
# ---------------------------------------------------------------------------

def hamiltonian_step(sigma: list[float], chi: list[float], phi: list[float],
                     dt: float) -> tuple[list, list, list]:
    """
    Single explicit Euler step of Hamilton's equations.

    H = k_back/2 * sum(chi^2) + E[sigma, chi, phi]

    sigma_dot = +dH/dchi = k_back*chi + chi_rel/2*(sbar-si) + delta*(si-sref)
                           [NO chi_decay -- that's dissipative]

    chi_dot = -dH/dsigma = -alpha*(si-sref) + beta*z*(sbar-si) - delta*chi
                            [NO Channel A with correct sign -- alpha term is
                             from dE/dsigma, sign gives restoring force]

    phi_dot = -dH/dphi = beta_phi/6 * sum_nb sigma_i*sigma_j*sin(phi_j-phi_i)
              [conservative XY dynamics]

    NOTE: sigma is NOT clipped -- conservative dynamics can push sigma outside [0,1].
    This is intentional: clipping is dissipative.
    """
    z = 6  # coordination number

    ns = list(sigma)
    nc = list(chi)
    np_ = list(phi)

    for i in range(N):
        x, y, z_c = coord3(i)
        nb = neighbors(x, y, z_c)
        sbar = sum(sigma[j] for j in nb) / 6.0
        si = sigma[i]; ci = chi[i]; pi = phi[i]

        # sigma_dot = dH/dchi (conservative)
        # dE/dchi_i = chi_decay*chi_i + chi_rel/2*(sbar-si) + delta*(si-sref)
        # But chi_decay is dissipative -- omit it in conservative limit
        sigma_dot = (K_BACK * ci
                     + CHI_REL / 2.0 * (sbar - si)
                     + DELTA * (si - SIGMA_REF))
        ns[i] = sigma[i] + dt * sigma_dot

        # chi_dot = -dH/dsigma (conservative)
        # dE/dsigma_i = alpha*(si-sref) - beta*z*(sbar-si) + delta*chi_i
        #               + phi gradient terms (approximate: ignore for sigma update)
        dE_dsigma = (ALPHA * (si - SIGMA_REF)
                     - BETA * z * (sbar - si)   # beta gradient: -z*beta*(sbar-si)
                     + DELTA * ci)
        chi_dot = -dE_dsigma
        nc[i] = chi[i] + dt * chi_dot

        # phi_dot = -dH/dphi (conservative XY dynamics)
        # dH/dphi_i = beta_phi/6 * sum_nb sigma_i*sigma_j*sin(phi_i-phi_j)
        dH_dphi = sum(
            BETA_PHI / 6.0 * si * sigma[j] * math.sin(angle_diff(pi, phi[j]))
            for j in nb
        )
        phi_dot = -dH_dphi
        np_[i] = wrap(phi[i] + dt * phi_dot)

    return ns, nc, np_


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def compute_E(sigma: list[float], chi: list[float], phi: list[float]) -> float:
    E = 0.0
    for i in range(N):
        x, y, z_c = coord3(i)
        nb = neighbors(x, y, z_c)
        sbar = sum(sigma[j] for j in nb) / 6.0
        si = sigma[i]; ci = chi[i]; pi = phi[i]
        E += ALPHA / 2.0 * (si - SIGMA_REF)**2
        E += BETA  / 4.0 * sum((sigma[j]-si)**2 for j in nb)
        E += CHI_DECAY / 2.0 * ci*ci
        E += CHI_REL / 2.0 * ci * (sbar - si)
        E += DELTA * ci * (si - SIGMA_REF)
        E -= BETA_PHI / 6.0 * sum(si*sigma[j]*math.cos(angle_diff(pi, phi[j]))
                                   for j in nb)
        D_i = phase_disorder(phi, i)
        E += GAMMA_PHI / 2.0 * D_i * si*si
    return E

def E_vacuum_ref() -> float:
    s = [SIGMA_REF]*N; c = [0.0]*N; p = [0.0]*N
    return compute_E(s, c, p)

def compute_H(sigma: list[float], chi: list[float], phi: list[float],
              E_vac: float, k_back: float) -> float:
    T = k_back / 2.0 * sum(c*c for c in chi)
    E = compute_E(sigma, chi, phi) - E_vac
    return T + E

def compute_m_ring(sigma: list[float]) -> float:
    return sum(max(0.0, SIGMA_REF - sigma[i]) for i in range(N))

def chi_rms_val(chi: list[float]) -> float:
    return math.sqrt(sum(c*c for c in chi) / N)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    print("QNG-CPU-059: Conservative Hamiltonian ring dynamics")
    print(f"L={L}  R={RING_R}  k_back={K_BACK}  dt={DT_HAM}  ham_steps={HAM_STEPS}")
    print()

    E_vac = E_vacuum_ref()
    print(f"E_vacuum = {E_vac:.4f}")
    print()

    # --- Phase 0: Form ring with v5 ---
    sigma = [SIGMA_REF]*N
    chi   = [0.0]*N
    phi   = init_phi_ring()

    print("Phase 1 (forming ring, v5, 300 steps) ...", flush=True)
    for _ in range(PHASE1_STEPS):
        sigma, chi, phi = update_step_v5(sigma, chi, phi, channel_f=False)

    print(f"  Phase 1 done. M={compute_m_ring(sigma):.1f}", flush=True)
    print()
    print(f"Phase 2 (v5 dynamics, Channel F, running to T={SNAPSHOT_T}) ...", flush=True)

    for t in range(1, PHASE2_STEPS + 1):
        sigma, chi, phi = update_step_v5(sigma, chi, phi, channel_f=True)
        if t == SNAPSHOT_T:
            M0 = compute_m_ring(sigma)
            H0 = compute_H(sigma, chi, phi, E_vac, K_BACK)
            cr0 = chi_rms_val(chi)
            print(f"  Phase 2 T={SNAPSHOT_T}: M={M0:.1f}  H={H0:.2f}  chi_rms={cr0:.4f}")
            break

    print()
    print("Switching to CONSERVATIVE Hamiltonian dynamics (no dissipation):")
    print(f"  sigma_dot = k_back*chi + chi_rel/2*(sbar-si) + delta*(si-sref)")
    print(f"  chi_dot   = -alpha*(si-sref) + beta*z*(sbar-si) - delta*chi")
    print(f"  phi_dot   = beta_phi/6 * sum_nb sigma*sigma_j*sin(phi_j-phi_i)")
    print()
    print(f"  {'step':>5}  {'M_ring':>9}  {'H_total':>10}  {'dH/H0':>8}  {'chi_rms':>9}")

    trajectory = []
    M_init = M0
    H_init = H0

    for step in range(HAM_STEPS + 1):
        if step % HAM_CHECK == 0:
            M_val = compute_m_ring(sigma)
            H_val = compute_H(sigma, chi, phi, E_vac, K_BACK)
            cr    = chi_rms_val(chi)
            dH_rel = (H_val - H_init) / abs(H_init) if H_init != 0 else 0.0
            print(f"  step={step:5d}  M={M_val:9.2f}  H={H_val:10.2f}  "
                  f"dH/H0={dH_rel:+8.4f}  chi_rms={cr:.4f}", flush=True)
            trajectory.append({
                "ham_step": step,
                "M": round(M_val, 3),
                "H": round(H_val, 3),
                "dH_rel": round(dH_rel, 5),
                "chi_rms": round(cr, 4),
            })

        if step < HAM_STEPS:
            sigma, chi, phi = hamiltonian_step(sigma, chi, phi, DT_HAM)

    print()

    # --- Checks ---
    M_final = trajectory[-1]["M"]
    H_final = trajectory[-1]["H"]
    dH_final = trajectory[-1]["dH_rel"]

    check1 = M_final < M_init / 2.0   # ring lost >50% depletion (expected: dissolves)
    check2 = abs(dH_final) < 0.20     # H conserved to 20%

    # Ring half-life
    t_half = None
    for row in trajectory:
        if row["M"] < M_init / 2.0:
            t_half = row["ham_step"]
            break

    print("=" * 65)
    print(f"Initial state (v5 T=1000): M={M_init:.1f}  H={H_init:.2f}")
    print(f"Final state (ham step={HAM_STEPS}): M={M_final:.1f}  H={H_final:.2f}")
    print(f"M reduction: {M_final/M_init:.3f}  (threshold 0.5 for Check 1)")
    print(f"H drift: {dH_final:+.4f}  (threshold 0.20 for Check 2)")
    print(f"Ring half-life: {t_half if t_half else '>'+str(HAM_STEPS)} Hamiltonian steps")
    print()
    print("Checks:")
    s1 = "PASS (ring dissolves -- NOT a H-soliton)" if check1 else "FAIL (ring survives -- IS a H-soliton!)"
    s2 = "PASS" if check2 else "FAIL (unstable -- reduce dt)"
    print(f"  Check 1 (M < M0/2 at ham_step={HAM_STEPS}): {s1}")
    print(f"  Check 2 (H conserved to 20%):               {s2}")

    overall = "pass" if check2 else "fail"
    print()
    print(f"qng_ring_conservative_reference: {overall.upper()}")
    if check1:
        print("  Interpretation: ring is NOT a soliton of H -- Gap 7 confirmed.")
    else:
        print("  Interpretation: UNEXPECTED -- ring survives under conservative dynamics!")
        print("  This contradicts Derrick scaling argument; requires further analysis.")

    report = {
        "test_id": "QNG-CPU-059",
        "decision": overall,
        "E_vacuum": E_vac,
        "k_back": K_BACK,
        "dt_ham": DT_HAM,
        "initial_state": {"M": round(M_init, 2), "H": round(H_init, 2), "chi_rms": round(cr0, 4)},
        "checks": {
            "ring_dissolves_check1": check1,
            "H_conserved_check2": check2,
            "ring_half_life_ham_steps": t_half,
        },
        "trajectory": trajectory,
    }
    rpath = out_dir / "report.json"
    with open(rpath, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rpath}")
    return 0 if overall == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
