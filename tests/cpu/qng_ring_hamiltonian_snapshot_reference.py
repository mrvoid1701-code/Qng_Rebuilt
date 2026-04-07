from __future__ import annotations

"""
QNG-CPU-057: Vortex ring physical mass -- snapshot Hamiltonian H(k_back).

Protocol: run full v5 ring (no Channel G), then evaluate
  H(k_back) = k_back/2 * sum(chi^2)  +  E_ring
as a FUNCTIONAL on the v5 state at each checkpoint.

No v6 time evolution -- purely evaluates the v6 Hamiltonian on the v5 ring.
Decouples mass measurement from Channel G ring-stability problem (CPU-056).
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-hamiltonian-snapshot-v1"

# ---------------------------------------------------------------------------
# Parameters (identical to CPU-055 / CPU-044)
# ---------------------------------------------------------------------------

L: int = 20
N: int = L * L * L
PHASE1_STEPS: int = 300
PHASE2_STEPS: int = 2500
CHECK_INTERVAL: int = 200

SIGMA_REF: float = 0.5
ALPHA:     float = 0.005
BETA:      float = 0.35
BETA_PHI:  float = 0.02
DELTA:     float = 0.20
EPSILON:   float = 0.0
CHI_DECAY: float = 0.005
CHI_REL:   float = 0.35
GAMMA_PHI: float = 0.10

RING_X: float = L / 2.0
RING_Y: float = L / 2.0
RING_Z: float = L / 2.0
RING_R: float = 5.0

# k_back values for snapshot evaluation (no time evolution)
K_BACKS: list[float] = [0.0, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.00]


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
# v5 update step (no Channel G)
# ---------------------------------------------------------------------------

def update_step_v5(sigma: list[float], chi: list[float], phi: list[float],
                   channel_f: bool) -> tuple[list, list, list]:
    ns, nc, np_ = [], [], []
    for i in range(N):
        x, y, z = coord3(i)
        nb = neighbors(x, y, z)
        sigma_bar = sum(sigma[j] for j in nb) / 6.0
        si = sigma[i]; ci = chi[i]; pi = phi[i]

        # Sigma: Channels A + B + D(cross) + F(disorder) — no Channel G
        ds = ALPHA*(SIGMA_REF - si) + BETA*(sigma_bar - si)
        if channel_f:
            D_i = phase_disorder(phi, i)
            ds -= GAMMA_PHI * D_i * si
        ns.append(clip01(si + ds))

        # Chi: chi_decay + chi_rel Laplacian + DELTA cross-coupling
        nc.append(ci*(1-CHI_DECAY)
                  + CHI_REL*(sigma_bar - si)
                  + DELTA*(SIGMA_REF - si))

        # Phi: weighted circular mean alignment
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
# Hamiltonian functional (DER-QNG-032)
# ---------------------------------------------------------------------------

def compute_E(sigma: list[float], chi: list[float], phi: list[float]) -> float:
    """Free energy E[sigma, chi, phi] (DER-QNG-032)."""
    E = 0.0
    for i in range(N):
        x, y, z = coord3(i)
        nb = neighbors(x, y, z)
        sbar = sum(sigma[j] for j in nb) / 6.0
        si = sigma[i]; ci = chi[i]; pi = phi[i]
        ds = si - SIGMA_REF

        E += ALPHA / 2.0 * ds*ds
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
    """E at phi=0, sigma=sigma_ref, chi=0."""
    s = [SIGMA_REF]*N; c = [0.0]*N; p = [0.0]*N
    return compute_E(s, c, p)

def compute_snapshot_H(chi: list[float], E_ring: float,
                       k_backs: list[float]) -> dict[float, float]:
    """Evaluate H(k_back) = k_back/2 * sum(chi^2) + E_ring for all k_backs."""
    sum_chi2 = sum(c*c for c in chi)
    return {kb: kb / 2.0 * sum_chi2 + E_ring for kb in k_backs}

def compute_m_ring(sigma: list[float]) -> float:
    return sum(max(0.0, SIGMA_REF - sigma[i]) for i in range(N))

def chi_rms(chi: list[float]) -> float:
    return math.sqrt(sum(c*c for c in chi) / N)


# ---------------------------------------------------------------------------
# Physical unit conversion (C3 + C4, k_back=1, m_u=m_Planck)
# ---------------------------------------------------------------------------

def phys_mass_kg(H_substrate: float, k_back_ref: float = 1.0) -> float:
    """
    Convert H in substrate units to kg via C3+C4.
    C4: m_u * k_back * tau = hbar  =>  m_u ~ Planck mass for k_back=1
    C3: tau/a = v_meas/c
    C1: a ~ 1.113e-27 * m_u (from G matching)

    Energy unit: E_phys = H_substrate * m_u * (a/tau)^2
               = H_substrate * m_u * (c/v_meas)^2
    Mass unit:   m = E_phys / c^2 = H_substrate * m_u * c^2 / (v_meas^2 * c^2)
               = H_substrate * m_u / v_meas^2     (c cancels)

    Wait: (a/tau)^2 = (c/v_meas)^2 (from C3: tau = a * v_meas/c)
    E_phys = H_substrate * m_u * (c/v_meas)^2    [Joules, if m_u in kg, c in m/s]
    m_phys = E_phys / c^2 = H_substrate * m_u / v_meas^2

    With m_u = m_Planck = 2.18e-8 kg, v_meas = 0.2286:
    """
    m_planck = 2.18e-8    # kg
    v_meas   = 0.2286     # from CPU-054
    # m_u depends on k_back (C4: m_u^2 = hbar*v_meas/(k_back*c*1.113e-27))
    # For k_back_ref=1: m_u = m_planck
    # For other k_back: m_u = m_planck / sqrt(k_back_ref)  [from C4 scaling]
    m_u = m_planck / math.sqrt(k_back_ref) if k_back_ref > 0 else m_planck
    return H_substrate * m_u / (v_meas ** 2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    print("QNG-CPU-057: Ring Hamiltonian snapshot H(k_back) on v5 ring")
    print(f"L={L}  R={RING_R}  Phase2={PHASE2_STEPS}  "
          f"k_back snapshot values={K_BACKS}")
    print()

    E_vac = E_vacuum_ref()
    print(f"E_vacuum (phi=0, sigma=sigma_ref) = {E_vac:.4f}")
    print()

    # Init
    sigma = [SIGMA_REF]*N
    chi   = [0.0]*N
    phi   = init_phi_ring()

    # Phase 1 (form ring, no Channel F, no Channel G)
    print("Phase 1 (forming ring, 300 steps) ...", flush=True)
    for _ in range(PHASE1_STEPS):
        sigma, chi, phi = update_step_v5(sigma, chi, phi, channel_f=False)
    print(f"  Phase 1 done. M_ring={compute_m_ring(sigma):.1f}  "
          f"chi_rms={chi_rms(chi):.4f}")
    print()

    # Phase 2: v5 dynamics, record snapshots
    print("Phase 2 (v5 dynamics with Channel F):", flush=True)
    print(f"  {'t':>5}  {'M':>8}  {'E_ring':>10}  {'chi_rms':>8}  "
          f"{'sum_chi2':>10}  {'k_min':>8}  "
          + "  ".join(f"H(k={kb:.3f})" for kb in K_BACKS))

    trajectory = []  # list of checkpoint dicts

    for t in range(1, PHASE2_STEPS + 1):
        sigma, chi, phi = update_step_v5(sigma, chi, phi, channel_f=True)

        if t % CHECK_INTERVAL == 0 or t == 1:
            E_full = compute_E(sigma, chi, phi)
            E_ring = E_full - E_vac
            M_val  = compute_m_ring(sigma)
            cr     = chi_rms(chi)
            sum_c2 = sum(c*c for c in chi)
            k_min  = 2.0 * abs(E_ring) / sum_c2 if sum_c2 > 1e-10 else float("inf")

            H_snap = compute_snapshot_H(chi, E_ring, K_BACKS)

            row = {
                "t": t,
                "M": round(M_val, 2),
                "E_ring": round(E_ring, 3),
                "chi_rms": round(cr, 4),
                "sum_chi2": round(sum_c2, 2),
                "k_min": round(k_min, 5),
                "H": {round(kb, 4): round(hv, 3) for kb, hv in H_snap.items()},
            }
            trajectory.append(row)

            H_str = "  ".join(f"{H_snap[kb]:>12.2f}" for kb in K_BACKS)
            print(f"  t={t:5d}  M={M_val:8.1f}  E_ring={E_ring:10.2f}  "
                  f"chi_rms={cr:8.4f}  sum_chi2={sum_c2:10.1f}  "
                  f"k_min={k_min:8.5f}  {H_str}", flush=True)

    print()

    # --- Checks at T=1000 ---
    def get_at_t(t_target: int) -> dict | None:
        for row in trajectory:
            if row["t"] >= t_target:
                return row
        return trajectory[-1] if trajectory else None

    row1000 = get_at_t(1000)
    M_1000    = row1000["M"] if row1000 else 0.0
    H_1000    = row1000["H"] if row1000 else {}
    k_min_1000 = row1000["k_min"] if row1000 else float("inf")

    check1 = M_1000 > 50
    check2 = H_1000.get(0.05, -1.0) > 0.0
    check3 = k_min_1000 < 0.10

    # Physical mass at k_back=1.0, T=1000
    H_at_k1 = H_1000.get(1.0, 0.0)
    m_kg  = phys_mass_kg(H_at_k1, k_back_ref=1.0)
    c_light = 3e8
    GeV_per_kg = c_light**2 / 1.602e-10   # 1 kg*c^2 in GeV
    m_GeV = m_kg * GeV_per_kg

    print("=" * 70)
    print(f"At T=1000: M={M_1000:.1f}  k_min={k_min_1000:.5f}  "
          f"H(k=0.05)={H_1000.get(0.05, 0):.2f}  H(k=1.0)={H_at_k1:.2f}")
    print()
    print("Checks:")
    print(f"  Check 1 (ring survives, M>50 at T=1000): {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (H>0 at k_back=0.05, T=1000):   {'PASS' if check2 else 'FAIL'}")
    print(f"  Check 3 (k_min < 0.10 at T=1000):        {'PASS' if check3 else 'FAIL'}")
    print()
    print(f"Physical mass (k_back=1.0, m_u=m_Planck, C3+C4):")
    print(f"  H_ring = {H_at_k1:.2f} substrate units")
    print(f"  m_ring = {m_kg:.4e} kg = {m_GeV:.4e} GeV")
    print(f"  (proton = 1.67e-27 kg = 0.938 GeV for comparison)")

    overall = "pass" if (check1 and check2 and check3) else "fail"
    print()
    print(f"qng_ring_hamiltonian_snapshot_reference: {overall.upper()}")

    # --- Report ---
    report = {
        "test_id": "QNG-CPU-057",
        "decision": overall,
        "E_vacuum": E_vac,
        "k_min_at_T1000": k_min_1000,
        "checks": {
            "ring_survives_T1000": check1,
            "H_positive_k005_T1000": check2,
            "k_min_lt_010": check3,
        },
        "physical_mass": {
            "H_substrate": H_at_k1,
            "m_ring_kg": m_kg,
            "m_ring_GeV": m_GeV,
            "k_back_ref": 1.0,
            "m_u": "m_Planck",
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
