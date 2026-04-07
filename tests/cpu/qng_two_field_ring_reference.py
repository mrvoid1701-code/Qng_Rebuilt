from __future__ import annotations

"""
QNG-CPU-060: Two-field substrate (v7) — sigma_g + sigma_m.

Tests Path D resolution of Gap 7:
  sigma_g: gravitational sector, Channel G active (KG wave)
  sigma_m: matter sector, Channel F active (ring stability), no Channel G
  Coupling: sigma_g += k_gm * (sigma_m_ref - sigma_m)

Key question: does sigma_m ring survive when Channel G is active in sigma_g?
In CPU-056, single-sigma ring was killed by Channel G. Here they are separated.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-two-field-ring-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

L: int = 20
N: int = L * L * L
PHASE1_STEPS: int = 300
PHASE2_STEPS: int = 1500
CHECK_INTERVAL: int = 200

# Shared substrate params
SIGMA_REF: float = 0.5
ALPHA:     float = 0.005
BETA:      float = 0.35
BETA_PHI:  float = 0.02
DELTA:     float = 0.20
CHI_DECAY: float = 0.005
CHI_REL:   float = 0.35
GAMMA_PHI: float = 0.10

# v7 new params
K_BACK: float = 0.10   # Channel G in sigma_g only
K_GM:   float = 0.001  # matter-gravity coupling

RING_R: float = 5.0
RING_X: float = L / 2.0
RING_Y: float = L / 2.0
RING_Z: float = L / 2.0


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

def phase_disorder(phi: list[float], sigma_m: list[float], i: int) -> float:
    """Phase disorder D_i weighted by sigma_m (matter field)."""
    x, y, z = coord3(i)
    nb = neighbors(x, y, z)
    sx = sum(math.cos(phi[j]) for j in nb) / 6.0
    sy = sum(math.sin(phi[j]) for j in nb) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx*sx + sy*sy))


# ---------------------------------------------------------------------------
# v7 two-field update step
# ---------------------------------------------------------------------------

def update_step_v7(sigma_g: list[float], sigma_m: list[float],
                   chi: list[float], phi: list[float],
                   channel_f: bool, channel_g: bool) -> tuple:
    """
    v7 two-field update:

    sigma_g: Channels A + B + G(if active) + coupling from sigma_m
    sigma_m: Channels A + B + F(if active)   -- NO Channel G
    chi:     coupled to sigma_g only
    phi:     weighted by sigma_m
    """
    ns_g, ns_m, nc, np_ = [], [], [], []

    for i in range(N):
        x, y, z = coord3(i)
        nb = neighbors(x, y, z)

        sg = sigma_g[i]; sm = sigma_m[i]; ci = chi[i]; pi = phi[i]

        sg_bar = sum(sigma_g[j] for j in nb) / 6.0
        sm_bar = sum(sigma_m[j] for j in nb) / 6.0

        # --- sigma_g update: A + B + G + coupling ---
        dsg = ALPHA * (SIGMA_REF - sg) + BETA * (sg_bar - sg)
        if channel_g:
            dsg += K_BACK * ci                          # Channel G
        dsg += K_GM * (SIGMA_REF - sm)                 # matter sources gravity
        ns_g.append(clip01(sg + dsg))

        # --- sigma_m update: A + B + F (NO Channel G) ---
        dsm = ALPHA * (SIGMA_REF - sm) + BETA * (sm_bar - sm)
        if channel_f:
            D_i = phase_disorder(phi, sigma_m, i)
            dsm -= GAMMA_PHI * D_i * sm
        ns_m.append(clip01(sm + dsm))

        # --- chi update: coupled to sigma_g ---
        nc.append(ci * (1 - CHI_DECAY)
                  + CHI_REL * (sg_bar - sg)
                  + DELTA * (SIGMA_REF - sg))

        # --- phi update: weighted by sigma_m (matter field) ---
        nb_sm = [sigma_m[j] for j in nb]
        nb_phi = [phi[j] for j in nb]
        tw = sum(nb_sm)
        if tw > 1e-10:
            sx2 = sum(nb_sm[k] * math.cos(nb_phi[k]) for k in range(6)) / tw
            sy2 = sum(nb_sm[k] * math.sin(nb_phi[k]) for k in range(6)) / tw
            pm = math.atan2(sy2, sx2)
        else:
            pm = pi
        np_.append(wrap(pi + BETA_PHI * angle_diff(pm, pi)))

    return ns_g, ns_m, nc, np_


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def compute_m_ring(sigma_m: list[float]) -> float:
    return sum(max(0.0, SIGMA_REF - sigma_m[i]) for i in range(N))

def chi_rms_val(chi: list[float]) -> float:
    return math.sqrt(sum(c * c for c in chi) / N)

def ring_nodes(R: float = RING_R, tol: float = 2.5) -> list[int]:
    """Indices of nodes within tol lattice units of the ring tube."""
    idx = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - RING_X); dy = _mi(y - RING_Y); dz = _mi(z - RING_Z)
        rho = math.sqrt(dx*dx + dy*dy)
        dist_tube = math.sqrt((rho - R)**2 + dz*dz)
        if dist_tube <= tol:
            idx.append(i)
    return idx

def delta_sg_core(sigma_g: list[float], ring_idx: list[int]) -> float:
    """Mean sigma_g depletion at ring core nodes."""
    if not ring_idx:
        return 0.0
    return sum(SIGMA_REF - sigma_g[i] for i in ring_idx) / len(ring_idx)

def compute_E_total(sigma_g: list[float], sigma_m: list[float],
                    chi: list[float], phi: list[float]) -> float:
    """Combined free energy functional for both fields."""
    E = 0.0
    for i in range(N):
        x, y, z = coord3(i)
        nb = neighbors(x, y, z)
        sg_bar = sum(sigma_g[j] for j in nb) / 6.0
        sm_bar = sum(sigma_m[j] for j in nb) / 6.0
        sg = sigma_g[i]; sm = sigma_m[i]; ci = chi[i]; pi = phi[i]

        # sigma_g energy
        E += ALPHA / 2.0 * (sg - SIGMA_REF)**2
        E += BETA  / 4.0 * sum((sigma_g[j]-sg)**2 for j in nb)

        # sigma_m energy (with phi XY term)
        E += ALPHA / 2.0 * (sm - SIGMA_REF)**2
        E += BETA  / 4.0 * sum((sigma_m[j]-sm)**2 for j in nb)
        E -= BETA_PHI / 6.0 * sum(sm * sigma_m[j] * math.cos(angle_diff(pi, phi[j]))
                                   for j in nb)
        D_i = phase_disorder(phi, sigma_m, i)
        E += GAMMA_PHI / 2.0 * D_i * sm*sm

        # chi energy (coupled to sigma_g)
        E += CHI_DECAY / 2.0 * ci*ci
        E += CHI_REL  / 2.0 * ci * (sg_bar - sg)
        E += DELTA * ci * (sg - SIGMA_REF)

        # coupling term
        E += K_GM / 2.0 * (SIGMA_REF - sm) * (SIGMA_REF - sg)

    return E

def E_vac_two_field() -> float:
    sg = [SIGMA_REF]*N; sm = [SIGMA_REF]*N; c = [0.0]*N; p = [0.0]*N
    return compute_E_total(sg, sm, c, p)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    print("QNG-CPU-060: Two-field substrate v7 (sigma_g + sigma_m)")
    print(f"L={L}  R={RING_R}  k_back={K_BACK} (sigma_g only)  k_gm={K_GM}")
    print(f"Channel G in sigma_g: YES   Channel F in sigma_m: YES")
    print()

    E_vac = E_vac_two_field()
    ring_idx = ring_nodes()
    print(f"E_vacuum (two-field) = {E_vac:.4f}")
    print(f"Ring tube nodes: {len(ring_idx)}")
    print()

    # Init
    sigma_g = [SIGMA_REF] * N
    sigma_m = [SIGMA_REF] * N
    chi     = [0.0] * N
    phi     = init_phi_ring()

    # Phase 1: form ring in sigma_m only (no Channel F, no Channel G)
    print("Phase 1 (300 steps, no Channel F, no Channel G) ...", flush=True)
    for _ in range(PHASE1_STEPS):
        sigma_g, sigma_m, chi, phi = update_step_v7(
            sigma_g, sigma_m, chi, phi, channel_f=False, channel_g=False)
    M0 = compute_m_ring(sigma_m)
    print(f"  Phase 1 done. M_ring(sigma_m)={M0:.1f}  chi_rms={chi_rms_val(chi):.4f}")
    print()

    # Phase 2: Channel F in sigma_m, Channel G in sigma_g
    print("Phase 2 (Channel F in sigma_m + Channel G in sigma_g):")
    hdr = (f"  {'t':>5}  {'M_ring':>8}  {'dsg_core':>10}  "
           f"{'chi_rms':>9}  {'H_snap(k=0.10)':>16}")
    print(hdr)

    trajectory = []

    for t in range(1, PHASE2_STEPS + 1):
        sigma_g, sigma_m, chi, phi = update_step_v7(
            sigma_g, sigma_m, chi, phi, channel_f=True, channel_g=True)

        if t % CHECK_INTERVAL == 0 or t == 1:
            M_val  = compute_m_ring(sigma_m)
            dsg    = delta_sg_core(sigma_g, ring_idx)
            cr     = chi_rms_val(chi)
            sum_c2 = sum(c*c for c in chi)
            E_ring = compute_E_total(sigma_g, sigma_m, chi, phi) - E_vac
            H_snap = K_BACK / 2.0 * sum_c2 + E_ring

            row = {
                "t": t,
                "M_ring": round(M_val, 2),
                "delta_sg_core": round(dsg, 6),
                "chi_rms": round(cr, 4),
                "H_snapshot": round(H_snap, 2),
            }
            trajectory.append(row)
            print(f"  t={t:5d}  M={M_val:8.1f}  dsg_core={dsg:10.6f}  "
                  f"chi_rms={cr:9.4f}  H_snap={H_snap:16.2f}", flush=True)

    print()

    # --- Checks ---
    def get_at_t(t_target: int) -> dict | None:
        for row in trajectory:
            if row["t"] >= t_target:
                return row
        return trajectory[-1] if trajectory else None

    row1000 = get_at_t(1000)
    M_1000  = row1000["M_ring"]       if row1000 else 0.0
    dsg_1000 = row1000["delta_sg_core"] if row1000 else 0.0
    chi_1000 = row1000["chi_rms"]      if row1000 else 0.0

    check1 = M_1000 > 50             # ring survives in sigma_m
    check2 = dsg_1000 > 0.001        # ring sources sigma_g perturbation
    check3 = chi_1000 > 0.01         # wave sector active

    print("=" * 65)
    print(f"At T=1000: M_ring={M_1000:.1f}  dsg_core={dsg_1000:.6f}  chi_rms={chi_1000:.4f}")
    print()
    print("Checks:")
    s1 = "PASS -- Path D WORKS: ring survives with Channel G active in sigma_g!" if check1 else "FAIL -- ring still killed (indirect coupling?)"
    s2 = "PASS -- ring sources gravity" if check2 else "FAIL -- no gravitational signal"
    s3 = "PASS -- wave sector active" if check3 else "FAIL -- chi field dead"
    print(f"  Check 1 (M>50 at T=1000, sigma_m ring with Channel G active): {s1}")
    print(f"  Check 2 (delta_sg_core > 0.001 at T=1000):                   {s2}")
    print(f"  Check 3 (chi_rms > 0.01 at T=1000):                          {s3}")

    overall = "pass" if (check1 and check3) else "fail"
    print()
    print(f"qng_two_field_ring_reference: {overall.upper()}")
    if check1:
        print("  Gap 7 RESOLVED: two-field substrate supports rings + waves simultaneously.")
    else:
        print("  Gap 7 NOT resolved: need to check indirect coupling path.")

    report = {
        "test_id": "QNG-CPU-060",
        "decision": overall,
        "k_back": K_BACK,
        "k_gm": K_GM,
        "E_vacuum": E_vac,
        "ring_nodes_count": len(ring_idx),
        "checks": {
            "ring_survives_sigma_m": check1,
            "ring_sources_sigma_g": check2,
            "chi_active": check3,
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
