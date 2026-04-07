from __future__ import annotations

"""
QNG-CPU-058: Vortex ring mass spectrum H_ring(R) for R=2,3,4,5.

Uses snapshot protocol (CPU-057): run v5 ring, evaluate H(k_back) functionally.
Checks if H_ring(R) ratios match known hadron mass ratios.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-mass-spectrum-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

L: int = 20
N: int = L * L * L
PHASE1_STEPS: int = 300
PHASE2_STEPS: int = 1500
SNAPSHOT_T: int = 1000    # Phase-2 step at which we read the snapshot

SIGMA_REF: float = 0.5
ALPHA:     float = 0.005
BETA:      float = 0.35
BETA_PHI:  float = 0.02
DELTA:     float = 0.20
CHI_DECAY: float = 0.005
CHI_REL:   float = 0.35
GAMMA_PHI: float = 0.10

RING_X: float = L / 2.0
RING_Y: float = L / 2.0
RING_Z: float = L / 2.0

RING_RADII: list[float] = [2.0, 3.0, 4.0, 5.0]
SNAP_K_BACKS: list[float] = [0.005, 0.01, 0.02, 0.05, 0.10, 1.00]

# Reference hadron mass ratios (PDG, relative to proton=938.3 MeV)
HADRON_RATIOS = {
    "pi(140)": 140.0 / 938.3,
    "K(494)":  494.0 / 938.3,
    "rho(770)": 770.0 / 938.3,
    "proton(938)": 1.000,
    "Delta(1232)": 1232.0 / 938.3,
}


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
# Initialization (ring in XY plane, winding along Z)
# ---------------------------------------------------------------------------

def init_phi_ring(R: float) -> list[float]:
    phi = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - RING_X); dy = _mi(y - RING_Y); dz = _mi(z - RING_Z)
        rho = math.sqrt(dx*dx + dy*dy)
        phi.append(math.atan2(dz, rho - R))
    return phi

def phase_disorder(phi: list[float], i: int) -> float:
    x, y, z = coord3(i)
    nb = neighbors(x, y, z)
    sx = sum(math.cos(phi[j]) for j in nb) / 6.0
    sy = sum(math.sin(phi[j]) for j in nb) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx*sx + sy*sy))


# ---------------------------------------------------------------------------
# v5 update (no Channel G)
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
# Hamiltonian functional
# ---------------------------------------------------------------------------

def compute_E(sigma: list[float], chi: list[float], phi: list[float]) -> float:
    E = 0.0
    for i in range(N):
        x, y, z = coord3(i)
        nb = neighbors(x, y, z)
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

def compute_snapshot_H(chi: list[float], E_ring: float,
                       k_backs: list[float]) -> dict[float, float]:
    sum_c2 = sum(c*c for c in chi)
    return {kb: kb / 2.0 * sum_c2 + E_ring for kb in k_backs}

def compute_m_ring(sigma: list[float]) -> float:
    return sum(max(0.0, SIGMA_REF - sigma[i]) for i in range(N))

def chi_rms(chi: list[float]) -> float:
    return math.sqrt(sum(c*c for c in chi) / N)


# ---------------------------------------------------------------------------
# Run one ring radius
# ---------------------------------------------------------------------------

def run_radius(R: float, E_vac: float) -> dict:
    print(f"\n  R={R:.0f}", flush=True)

    sigma = [SIGMA_REF]*N
    chi   = [0.0]*N
    phi   = init_phi_ring(R)

    # Phase 1
    for _ in range(PHASE1_STEPS):
        sigma, chi, phi = update_step_v5(sigma, chi, phi, channel_f=False)
    M0 = compute_m_ring(sigma)
    print(f"    Phase1 done: M={M0:.1f}", flush=True)

    # Phase 2 -- run to SNAPSHOT_T, report every 200 steps
    snap = None
    for t in range(1, PHASE2_STEPS + 1):
        sigma, chi, phi = update_step_v5(sigma, chi, phi, channel_f=True)

        if t % 200 == 0 or t == 1:
            E_full = compute_E(sigma, chi, phi)
            E_ring = E_full - E_vac
            M_val  = compute_m_ring(sigma)
            cr     = chi_rms(chi)
            sum_c2 = sum(c*c for c in chi)
            k_min  = 2*abs(E_ring)/sum_c2 if sum_c2 > 1e-10 else float("inf")
            print(f"    t={t:5d}: M={M_val:7.1f}  E_ring={E_ring:9.2f}  "
                  f"chi_rms={cr:.4f}  k_min={k_min:.5f}", flush=True)

        if t == SNAPSHOT_T:
            E_full = compute_E(sigma, chi, phi)
            E_ring = E_full - E_vac
            M_val  = compute_m_ring(sigma)
            cr     = chi_rms(chi)
            sum_c2 = sum(c*c for c in chi)
            k_min  = 2*abs(E_ring)/sum_c2 if sum_c2 > 1e-10 else float("inf")
            H_snap = compute_snapshot_H(chi, E_ring, SNAP_K_BACKS)
            snap = {
                "t": t, "R": R,
                "M": round(M_val, 2),
                "E_ring": round(E_ring, 3),
                "chi_rms": round(cr, 4),
                "sum_chi2": round(sum_c2, 2),
                "k_min": round(k_min, 6),
                "H": {round(kb, 4): round(hv, 3) for kb, hv in H_snap.items()},
            }

    return snap if snap else {}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    print("QNG-CPU-058: Ring mass spectrum H_ring(R) for R=2,3,4,5")
    print(f"L={L}  Phase2={PHASE2_STEPS}  snapshot at T={SNAPSHOT_T}")
    print(f"k_back snapshot values: {SNAP_K_BACKS}")
    print()

    E_vac = E_vacuum_ref()
    print(f"E_vacuum = {E_vac:.4f}")

    results = {}
    for R in RING_RADII:
        snap = run_radius(R, E_vac)
        results[R] = snap

    print()
    print("=" * 70)
    print("Mass spectrum at T=1000:")
    print()

    # Reference: R=5
    snap5 = results.get(5.0, {})
    H_ref = snap5.get("H", {}).get(0.10, 1.0)
    M_ref = snap5.get("M", 1.0)

    print(f"  {'R':>3}  {'M_ring':>8}  {'E_ring':>10}  {'sum_chi2':>10}  "
          f"{'k_min':>8}  {'H(k=0.10)':>12}  {'H/H(R=5)':>10}")
    rows = []
    for R in RING_RADII:
        s = results.get(R, {})
        M_val  = s.get("M", 0.0)
        E_ring = s.get("E_ring", 0.0)
        sum_c2 = s.get("sum_chi2", 0.0)
        k_min  = s.get("k_min", float("inf"))
        H_010  = s.get("H", {}).get(0.10, 0.0)
        ratio  = H_010 / H_ref if H_ref != 0 else 0.0
        rows.append((R, M_val, E_ring, sum_c2, k_min, H_010, ratio))
        print(f"  R={R:.0f}  M={M_val:8.1f}  E_ring={E_ring:10.2f}  "
              f"sum_chi2={sum_c2:10.1f}  k_min={k_min:8.5f}  "
              f"H(k=0.10)={H_010:12.2f}  ratio={ratio:.4f}")

    print()
    print("Mass ratios vs hadron PDG:")
    print(f"  {'R':>3}  {'H/H(R=5)':>10}  ", end="")
    for name in HADRON_RATIOS:
        print(f"  {name:>14}", end="")
    print()
    for R, *_, ratio in rows:
        matches = []
        print(f"  R={R:.0f}  ratio={ratio:.4f}  ", end="")
        for name, hr in HADRON_RATIOS.items():
            diff = abs(ratio - hr) / hr if hr > 0 else 999
            flag = " <-- MATCH" if diff < 0.10 else ""
            print(f"  {hr:.4f}({diff:.2f}){flag:10}", end="")
            if diff < 0.10:
                matches.append(name)
        print(f"  matches={matches}")

    print()
    print("Scaling check: H ~ R^n?")
    if len(rows) >= 2:
        for i in range(len(rows)):
            for j in range(i+1, len(rows)):
                R1, *_, H1, _ = rows[i]
                R2, *_, H2, _ = rows[j]
                if H1 > 0 and H2 > 0 and R1 > 0 and R2 > 0:
                    n = math.log(H2/H1) / math.log(R2/R1)
                    print(f"  H(R={R2:.0f})/H(R={R1:.0f}) = {H2/H1:.3f}  "
                          f"-> H ~ R^{n:.2f}")

    # Checks
    check1 = all(results.get(R, {}).get("M", 0) > 10 for R in RING_RADII)

    # Check 2: H does NOT scale as R^n for n=1,2,3 within 10%
    H_vals = [results.get(R, {}).get("H", {}).get(0.10, 0.0) for R in RING_RADII]
    check2_note = "see scaling table above"
    # Trivially: check if ratio(R=2)/ratio(R=5) is far from (2/5)^n for n=1,2,3
    if H_vals[-1] > 0 and H_vals[0] > 0:
        obs_ratio = H_vals[0] / H_vals[-1]
        trivial_n1 = abs(obs_ratio - (2/5)**1) / ((2/5)**1)
        trivial_n2 = abs(obs_ratio - (2/5)**2) / ((2/5)**2)
        trivial_n3 = abs(obs_ratio - (2/5)**3) / ((2/5)**3)
        check2 = min(trivial_n1, trivial_n2, trivial_n3) > 0.10
        check2_note = (f"H(R=2)/H(R=5)={obs_ratio:.4f}; "
                       f"deviations from R^1={trivial_n1:.2f} R^2={trivial_n2:.2f} "
                       f"R^3={trivial_n3:.2f}")
    else:
        check2 = False

    print()
    print("Checks:")
    print(f"  Check 1 (all rings survive M>10): {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (non-trivial H scaling): {'PASS' if check2 else 'FAIL (trivial)'}  {check2_note}")
    print("  Check 3 (hadron ratio matches): informational -- see table above")

    overall = "pass" if check1 else "fail"
    print()
    print(f"qng_ring_mass_spectrum_reference: {overall.upper()}")

    report = {
        "test_id": "QNG-CPU-058",
        "decision": overall,
        "E_vacuum": E_vac,
        "snapshot_T": SNAPSHOT_T,
        "checks": {
            "all_rings_survive": check1,
            "nontrivial_scaling": check2,
            "scaling_note": check2_note,
        },
        "results": {
            str(R): results.get(R, {}) for R in RING_RADII
        },
        "mass_ratios_vs_R5": {
            str(R): (results.get(R, {}).get("H", {}).get(0.10, 0.0) / H_ref
                     if H_ref else 0.0)
            for R in RING_RADII
        },
        "hadron_ratios_PDG": HADRON_RATIOS,
    }
    rpath = out_dir / "report.json"
    with open(rpath, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rpath}")
    return 0 if overall == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
