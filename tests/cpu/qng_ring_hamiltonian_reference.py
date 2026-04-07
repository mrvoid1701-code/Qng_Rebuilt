from __future__ import annotations

"""
QNG-CPU-056: Vortex ring physical mass from Hamiltonian H = T + E in v6.

In v5 (k_back=0): T=0, H=E < 0 (ring below phi=0 vacuum -- bound state).
In v6 (k_back>0): T = k_back/2 * sum(chi^2) > 0.
For k_back > k_min ~ 0.05: H = T + E > 0 (positive physical mass).

Mass identification: m_ring = H_ring / c^2  (in physical units via C3+C4).
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-hamiltonian-v1"

# ---------------------------------------------------------------------------
# Parameters (identical to CPU-055 / CPU-044)
# ---------------------------------------------------------------------------

L: int = 20
N: int = L * L * L
PHASE1_STEPS: int = 300
PHASE2_STEPS: int = 1500
CHECK_INTERVAL: int = 300

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

# k_back scan: 0.0 = v5 baseline, higher = v6 with Channel G
K_BACKS: list[float] = [0.0, 0.02, 0.05, 0.10, 0.20]


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
# Update step: v5 (k_back=0) or v6 (k_back>0)
# ---------------------------------------------------------------------------

def update_step(sigma: list[float], chi: list[float], phi: list[float],
                k_back: float, channel_f: bool) -> tuple[list, list, list]:
    ns, nc, np_ = [], [], []
    for i in range(N):
        x, y, z = coord3(i)
        nb = neighbors(x, y, z)
        sigma_bar = sum(sigma[j] for j in nb) / 6.0
        si = sigma[i]; ci = chi[i]; pi = phi[i]

        # Sigma: Channels A + B + D(cross) + F(disorder) + G(back-reaction)
        ds = ALPHA*(SIGMA_REF - si) + BETA*(sigma_bar - si)
        if channel_f:
            D_i = phase_disorder(phi, i)
            ds -= GAMMA_PHI * D_i * si
        ds += k_back * ci          # Channel G (v6 only if k_back>0)
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
        np_.append(wrap(pi + BETA_PHI*angle_diff(pm, pi) + EPSILON*ci))

    return ns, nc, np_


# ---------------------------------------------------------------------------
# Hamiltonian: H = T + E (DER-QNG-032)
# ---------------------------------------------------------------------------

def compute_T(chi: list[float], k_back: float) -> float:
    """Kinetic energy: T = k_back/2 * sum(chi_i^2)"""
    if k_back == 0.0:
        return 0.0
    return k_back / 2.0 * sum(c*c for c in chi)


def compute_E(sigma: list[float], chi: list[float], phi: list[float]) -> float:
    """
    Free energy E[sigma,chi,phi] (DER-QNG-032):
      sum_i { alpha/2*(si-sref)^2
              + beta/4*sum_nb(sj-si)^2
              + chi_decay/2*ci^2
              + chi_rel/2*ci*(sbar-si)
              + delta*ci*(si-sref)
              - beta_phi/6*sum_nb si*sj*cos(phi_ij)
              + gamma_phi/2*D_i*si^2 }
    """
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


# Vacuum energy reference: sigma=sigma_ref, chi=0, phi=0 everywhere
def E_vacuum_ref() -> float:
    s = [SIGMA_REF]*N; c = [0.0]*N; p = [0.0]*N
    return compute_E(s, c, p)


# ---------------------------------------------------------------------------
# Ring diagnostics
# ---------------------------------------------------------------------------

def compute_m_ring(sigma: list[float]) -> float:
    return sum(max(0.0, SIGMA_REF - sigma[i]) for i in range(N))

def chi_rms(chi: list[float]) -> float:
    return math.sqrt(sum(c*c for c in chi) / N)


# ---------------------------------------------------------------------------
# Run one k_back scenario
# ---------------------------------------------------------------------------

def run_kback(k_back: float, E_vac: float) -> dict:
    print(f"  k_back={k_back:.2f}", flush=True)

    # Init
    sigma = [SIGMA_REF]*N
    chi   = [0.0]*N
    phi   = init_phi_ring()

    # Phase 1 (form ring, no Channel F, no Channel G even in v6)
    for _ in range(PHASE1_STEPS):
        sigma, chi, phi = update_step(sigma, chi, phi, k_back=0.0, channel_f=False)

    trajectory = []

    for t in range(1, PHASE2_STEPS + 1):
        sigma, chi, phi = update_step(sigma, chi, phi, k_back=k_back, channel_f=True)

        if t % CHECK_INTERVAL == 0 or t == 1:
            T_val = compute_T(chi, k_back)
            E_val = compute_E(sigma, chi, phi) - E_vac
            H_val = T_val + E_val
            M_val = compute_m_ring(sigma)
            chi_r = chi_rms(chi)

            trajectory.append({
                "t": t,
                "T": round(T_val, 3),
                "E": round(E_val, 3),
                "H": round(H_val, 3),
                "M": round(M_val, 2),
                "chi_rms": round(chi_r, 4),
            })
            print(f"    T={t:5d}: T={T_val:8.2f}  E={E_val:9.2f}  H={H_val:9.2f}  "
                  f"M={M_val:7.1f}  chi_rms={chi_r:.4f}", flush=True)

    return {
        "k_back": k_back,
        "trajectory": trajectory,
        "H_final": trajectory[-1]["H"] if trajectory else 0.0,
        "M_final": trajectory[-1]["M"] if trajectory else 0.0,
        "ring_survives": trajectory[-1]["M"] > 50 if trajectory else False,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--k-backs", nargs="+", type=float, default=K_BACKS)
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    print("QNG-CPU-056: Ring Hamiltonian H = T + E (v5/v6)")
    print(f"L={L}  R={RING_R}  Phase2={PHASE2_STEPS}  k_back scan={args.k_backs}")
    print()

    E_vac = E_vacuum_ref()
    print(f"E_vacuum (phi=0, sigma=sigma_ref) = {E_vac:.4f}")
    print()

    results = {}
    for kb in args.k_backs:
        results[kb] = run_kback(kb, E_vac)
        r = results[kb]
        print(f"  -> k_back={kb:.2f}  H_final={r['H_final']:.2f}  "
              f"M_final={r['M_final']:.1f}  ring={'OK' if r['ring_survives'] else 'DEAD'}")
        print()

    # Checks
    r0   = results.get(0.0,  {})
    r005 = results.get(0.05, {})
    r010 = results.get(0.10, {})

    # Get T=600 H for check 2 (index where t=600 in trajectory)
    def get_H_at(r: dict, t_target: int) -> float:
        for p in r.get("trajectory", []):
            if p["t"] >= t_target:
                return p["H"]
        return r.get("H_final", 0.0)

    H_at600_k0   = get_H_at(r0, 600)
    H_at600_k005 = get_H_at(r005, 600)

    check1 = r0.get("ring_survives", False)
    check2 = H_at600_k005 > H_at600_k0   # H increases with k_back (kinetic energy dominates)
    check3 = r010.get("ring_survives", False)

    # Find k_min where H first crosses 0
    k_min_positive = None
    for kb in sorted(results.keys()):
        H_f = results[kb]["H_final"]
        if H_f > 0:
            k_min_positive = kb
            break

    decision = check1 and check2 and check3

    print("=" * 70)
    print("Hamiltonian summary at T=final:")
    print(f"{'k_back':>8}  {'T':>10}  {'E':>10}  {'H':>10}  {'M':>8}  ring")
    for kb in sorted(results.keys()):
        r = results[kb]
        traj = r["trajectory"]
        last = traj[-1] if traj else {}
        ring_ok = "OK" if r["ring_survives"] else "DEAD"
        print(f"  {kb:>6.2f}  {last.get('T',0):>10.2f}  {last.get('E',0):>10.2f}  "
              f"{last.get('H',0):>10.2f}  {last.get('M',0):>8.1f}  {ring_ok}")
    print()

    if k_min_positive is not None:
        print(f"k_min (H > 0) = {k_min_positive:.2f}")
    else:
        print("H never positive in this k_back range — need larger k_back")
    print()

    print("Checks:")
    print(f"  Check 1 (ring survives k_back=0, v5): {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (H increases with k_back at T=600): {'PASS' if check2 else 'FAIL'}  "
          f"H(k=0)={H_at600_k0:.1f}  H(k=0.05)={H_at600_k005:.1f}")
    print(f"  Check 3 (ring survives k_back=0.10, v6): {'PASS' if check3 else 'FAIL'}")
    print(f"\nqng_ring_hamiltonian_reference: {'PASS' if decision else 'FAIL'}")

    # Physical mass estimate (C3+C4, k_back=0.10, m_node=m_Planck)
    kb_phys = 0.10
    if kb_phys in results and results[kb_phys]["H_final"] > 0:
        H_phys = results[kb_phys]["H_final"]
        v_meas = math.sqrt(kb_phys * CHI_REL / 6.0)
        c = 2.998e8; hbar = 1.055e-34
        m_planck = 2.176e-8  # kg
        # C4: m_u ~ Planck mass, C3: tau/a = v_meas/c
        # H in substrate units -> physical: H_phys * (m_u * a^2 / tau^2)
        # With C3+C4: m_u*a^2/tau^2 = m_u * c^2 / v_meas^2
        # m_ring = H_phys * m_u * c^2 / v_meas^2  [in Joules]
        m_ring_J = H_phys * m_planck * c**2 / v_meas**2
        m_ring_eV = m_ring_J / 1.602e-19 / 1e9  # GeV
        print()
        print(f"Physical mass estimate (k_back={kb_phys}, m_node=m_Planck, C3+C4):")
        print(f"  H_ring = {H_phys:.2f} substrate units")
        print(f"  m_ring = {m_ring_J:.3e} kg = {m_ring_eV:.3e} GeV")
        print(f"  (proton = 1.67e-27 kg = 0.938 GeV for comparison)")

    report = {
        "test_id": "QNG-CPU-056",
        "decision": "pass" if decision else "fail",
        "E_vacuum": round(E_vac, 4),
        "k_min_positive_H": k_min_positive,
        "checks": {
            "ring_survives_v5": check1,
            "H_increases_with_kback": check2,
            "ring_survives_v6_k010": check3,
        },
        "results": {
            str(kb): {
                "H_final": r["H_final"],
                "M_final": r["M_final"],
                "ring_survives": r["ring_survives"],
                "trajectory": r["trajectory"],
            }
            for kb, r in results.items()
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-CPU-056: Ring Hamiltonian H = T + E",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- k_min (H > 0) = {k_min_positive}",
        "",
        "## H = T + E at final timestep",
        "| k_back | T | E | H | M | ring |",
        "|--------|---|---|---|---|------|",
    ]
    for kb in sorted(results.keys()):
        r = results[kb]
        last = r["trajectory"][-1] if r["trajectory"] else {}
        lines.append(f"| {kb:.2f} | {last.get('T',0):.2f} | {last.get('E',0):.2f} | "
                     f"{last.get('H',0):.2f} | {last.get('M',0):.1f} | "
                     f"{'OK' if r['ring_survives'] else 'DEAD'} |")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nReport: {(out_dir / 'report.json').as_posix()}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
