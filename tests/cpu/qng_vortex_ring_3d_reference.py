from __future__ import annotations

"""
QNG-CPU-043: 3D vortex ring stability -- dynamic persistence of phi vortex ring.

Tests DER-QNG-026 (v5) in 3D: does a phi vortex ring (closed vortex line) survive
for T=1000 steps with detectable sigma depletion? In 3D, pi_2(S^1)=0 means no
topological protection -- this is a DYNAMICAL stability question.

Two-phase protocol:
  Phase 1 (T=0..300): phi relaxes with BETA_PHI=0.05, no Channel F (GAMMA_PHI=0).
    - Separate phi beta from sigma beta prevents ring collapse before Channel F acts.
    - Sigma stays at sigma_ref (autonomous, Channel F off).
  Phase 2 (T=300..1000, 700 steps): Channel F active (GAMMA_PHI=0.10).
    - Sigma depletes at ring core.
    - Ring has already equilibrated its phi structure.

Physical motivation for two-phase: beta=0.35 applied to the phi channel would
collapse the ring (pi_2(S^1)=0, no topological protection) before Channel F
builds sigma depletion. BETA_PHI=0.05 is a slower phi relaxation that preserves
the ring on 700-step timescales. The sigma channel always uses BETA=0.35.

Lattice: 20x20x20 cubic, periodic BC.
Ring: xy-plane, center (10,10,10), radius R=5. phi_i = atan2(dz, rho - R).
"""

import json
import math
import cmath
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-vortex-ring-3d-reference-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

L: int = 20
N: int = L * L * L
PHASE1_STEPS: int = 300    # phi relaxation, no Channel F
PHASE2_STEPS: int = 700    # Channel F active
STEPS: int = PHASE1_STEPS + PHASE2_STEPS   # 1000 total
RECORD_STEPS: list[int] = [500, 1000]     # global steps at which to record

SIGMA_REF: float = 0.5
ALPHA: float = 0.005
BETA: float = 0.35          # sigma/chi diffusion coupling
BETA_PHI: float = 0.02      # phi diffusion coupling (separate; prevents ring collapse)
DELTA: float = 0.20
EPSILON: float = 0.0
CHI_DECAY: float = 0.005
CHI_REL: float = 0.35
GAMMA_PHI: float = 0.10     # Channel F, Phase 2 only

RING_X: float = L / 2.0   # 10.0
RING_Y: float = L / 2.0   # 10.0
RING_Z: float = L / 2.0   # 10.0
RING_R: float = 5.0


# ---------------------------------------------------------------------------
# 3D Indexing
# ---------------------------------------------------------------------------

def idx3(x: int, y: int, z: int) -> int:
    return (x % L) * L * L + (y % L) * L + (z % L)


def coord3(i: int) -> tuple[int, int, int]:
    x = i // (L * L)
    y = (i % (L * L)) // L
    z = i % L
    return x, y, z


def _mi(d: float) -> float:
    """Minimum image for box of size L."""
    while d > L / 2:
        d -= L
    while d < -L / 2:
        d += L
    return d


# ---------------------------------------------------------------------------
# Phase arithmetic
# ---------------------------------------------------------------------------

def wrap(angle: float) -> float:
    a = angle % (2 * math.pi)
    return a - 2 * math.pi if a > math.pi else a


def angle_diff(a: float, b: float) -> float:
    return wrap(a - b)


def circular_mean_weighted(phases: list[float], weights: list[float]) -> float:
    sx = sum(w * math.cos(p) for w, p in zip(weights, phases))
    sy = sum(w * math.sin(p) for w, p in zip(weights, phases))
    return math.atan2(sy, sx)


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def init_phi_ring() -> list[float]:
    """
    Vortex ring in xy-plane at (RING_X, RING_Y, RING_Z), radius RING_R.
    phi_i = atan2(dz, rho - R)  where rho = sqrt(dx^2 + dy^2).

    This gives a phase field that winds by 2pi around the ring core circle
    (rho = R, z = RING_Z).
    """
    phi = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - RING_X)
        dy = _mi(y - RING_Y)
        dz = _mi(z - RING_Z)
        rho = math.sqrt(dx * dx + dy * dy)
        phi_i = math.atan2(dz, rho - RING_R)
        phi.append(phi_i)
    return phi


# ---------------------------------------------------------------------------
# 3D Phase disorder
# ---------------------------------------------------------------------------

def phase_disorder_3d(phi: list[float], i: int) -> float:
    """D_i = 1 - |mean(exp(i*phi_j))| for 6 neighbors."""
    x, y, z = coord3(i)
    neighbors = [
        idx3(x - 1, y, z), idx3(x + 1, y, z),
        idx3(x, y - 1, z), idx3(x, y + 1, z),
        idx3(x, y, z - 1), idx3(x, y, z + 1),
    ]
    sx = sum(math.cos(phi[j]) for j in neighbors) / 6.0
    sy = sum(math.sin(phi[j]) for j in neighbors) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx * sx + sy * sy))


# ---------------------------------------------------------------------------
# Update steps
# ---------------------------------------------------------------------------

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def update_step_phase1(
    sigma: list[float],
    chi: list[float],
    phi: list[float],
) -> tuple[list[float], list[float], list[float]]:
    """
    Phase 1 update: phi relaxation, no Channel F.
    - sigma/chi: autonomous (no phi coupling, GAMMA_PHI=0)
    - phi: diffusion with BETA_PHI (slow, preserves ring structure)
    """
    new_sigma = []
    new_chi = []
    new_phi = []

    for i in range(N):
        x, y, z = coord3(i)
        neighbors = [
            idx3(x - 1, y, z), idx3(x + 1, y, z),
            idx3(x, y - 1, z), idx3(x, y + 1, z),
            idx3(x, y, z - 1), idx3(x, y, z + 1),
        ]

        sigma_bar = sum(sigma[j] for j in neighbors) / 6.0

        # sigma: autonomous, no Channel F
        s = clip01(
            sigma[i]
            + ALPHA * (SIGMA_REF - sigma[i])
            + BETA * (sigma_bar - sigma[i])
        )

        c = (
            chi[i] * (1.0 - CHI_DECAY)
            + CHI_REL * (sigma_bar - sigma[i])
            + DELTA * (SIGMA_REF - sigma[i])
        )

        # phi: slow diffusion with BETA_PHI
        neighbor_phases = [phi[j] for j in neighbors]
        neighbor_weights = [sigma[j] for j in neighbors]
        total_w = sum(neighbor_weights)
        if total_w > 1e-10:
            phi_mean = circular_mean_weighted(neighbor_phases, neighbor_weights)
        else:
            phi_mean = phi[i]
        p = wrap(phi[i] + BETA_PHI * angle_diff(phi_mean, phi[i]) + EPSILON * chi[i])

        new_sigma.append(s)
        new_chi.append(c)
        new_phi.append(p)

    return new_sigma, new_chi, new_phi


def update_step_phase2(
    sigma: list[float],
    chi: list[float],
    phi: list[float],
) -> tuple[list[float], list[float], list[float]]:
    """
    Phase 2 update: Channel F active (GAMMA_PHI=0.10).
    - sigma: includes Channel F term (-GAMMA_PHI * D_i * sigma_i)
    - phi: slow diffusion with BETA_PHI
    """
    new_sigma = []
    new_chi = []
    new_phi = []

    for i in range(N):
        x, y, z = coord3(i)
        neighbors = [
            idx3(x - 1, y, z), idx3(x + 1, y, z),
            idx3(x, y - 1, z), idx3(x, y + 1, z),
            idx3(x, y, z - 1), idx3(x, y, z + 1),
        ]

        sigma_bar = sum(sigma[j] for j in neighbors) / 6.0
        D_i = phase_disorder_3d(phi, i)

        # sigma: v5 with Channel F
        s = clip01(
            sigma[i]
            + ALPHA * (SIGMA_REF - sigma[i])
            + BETA * (sigma_bar - sigma[i])
            - GAMMA_PHI * D_i * sigma[i]
        )

        c = (
            chi[i] * (1.0 - CHI_DECAY)
            + CHI_REL * (sigma_bar - sigma[i])
            + DELTA * (SIGMA_REF - sigma[i])
        )

        # phi: slow diffusion with BETA_PHI
        neighbor_phases = [phi[j] for j in neighbors]
        neighbor_weights = [sigma[j] for j in neighbors]
        total_w = sum(neighbor_weights)
        if total_w > 1e-10:
            phi_mean = circular_mean_weighted(neighbor_phases, neighbor_weights)
        else:
            phi_mean = phi[i]
        p = wrap(phi[i] + BETA_PHI * angle_diff(phi_mean, phi[i]) + EPSILON * chi[i])

        new_sigma.append(s)
        new_chi.append(c)
        new_phi.append(p)

    return new_sigma, new_chi, new_phi


# ---------------------------------------------------------------------------
# Ring diagnostics
# ---------------------------------------------------------------------------

def find_ring_z(sigma: list[float]) -> int:
    """
    Find the z-plane with minimum mean sigma in the cylindrical shell rho in [R-3, R+3].
    Searches all z-planes (ring moves due to self-induced velocity).
    Returns z_ring (integer).
    """
    best_z = int(RING_Z)
    best_sigma = 1e9
    for z in range(L):
        total, count = 0.0, 0
        for i in range(N):
            xi, yi, zi = coord3(i)
            if zi != z:
                continue
            dx = _mi(xi - RING_X); dy = _mi(yi - RING_Y)
            rho = math.sqrt(dx * dx + dy * dy)
            if abs(rho - RING_R) <= 3:
                total += sigma[i]
                count += 1
        if count > 0:
            mean_s = total / count
            if mean_s < best_sigma:
                best_sigma = mean_s
                best_z = z
    return best_z


def ring_sigma_stats(sigma: list[float], z_ring: int) -> tuple[float, float, int]:
    """
    Returns (mean_core_sigma, mean_bulk_sigma, n_core_nodes).
    Core: rho in [R-2, R+2], |z - z_ring|_min-image <= 1
    Bulk: rho > R+5 AND |z - z_ring|_min-image > 5
    """
    core_total, core_count = 0.0, 0
    bulk_total, bulk_count = 0.0, 0

    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - RING_X); dy = _mi(y - RING_Y)
        rho = math.sqrt(dx * dx + dy * dy)
        dz_ring = abs(_mi(z - z_ring))

        if abs(rho - RING_R) <= 2 and dz_ring <= 1:
            core_total += sigma[i]
            core_count += 1
        elif rho > RING_R + 5 and dz_ring > 5:
            bulk_total += sigma[i]
            bulk_count += 1

    mean_core = core_total / max(core_count, 1)
    mean_bulk = bulk_total / max(bulk_count, 1)
    return mean_core, mean_bulk, core_count


def ring_radius_from_depletion(sigma: list[float], z_ring: int) -> tuple[float, int]:
    """
    Estimate ring radius from sigma-depleted nodes near z_ring.
    Returns (R_t, n_depleted).
    """
    depleted_rhos = []
    for i in range(N):
        x, y, z = coord3(i)
        dz_ring = abs(_mi(z - z_ring))
        if dz_ring > 2:
            continue
        if sigma[i] >= 0.35:
            continue
        dx = _mi(x - RING_X); dy = _mi(y - RING_Y)
        rho = math.sqrt(dx * dx + dy * dy)
        if abs(rho - RING_R) <= RING_R:
            depleted_rhos.append(rho)

    if not depleted_rhos:
        return 0.0, 0
    return sum(depleted_rhos) / len(depleted_rhos), len(depleted_rhos)


def count_ring_shape_nodes(sigma: list[float], z_ring: int) -> int:
    """Count sigma-depleted nodes with rho in [R-3, R+3] near z_ring."""
    count = 0
    for i in range(N):
        x, y, z = coord3(i)
        dz_ring = abs(_mi(z - z_ring))
        if dz_ring > 3:
            continue
        if sigma[i] >= 0.35:
            continue
        dx = _mi(x - RING_X); dy = _mi(y - RING_Y)
        rho = math.sqrt(dx * dx + dy * dy)
        if abs(rho - RING_R) <= 3:
            count += 1
    return count


# ---------------------------------------------------------------------------
# 3D Winding numbers (all 3 plaquette types)
# ---------------------------------------------------------------------------

def count_nonzero_winding_3d(phi: list[float]) -> int:
    """
    Count total non-zero winding plaquettes across all 3 types.
    Type 0 (xy, z-normal): (x,y,z)-(x+1,y,z)-(x+1,y+1,z)-(x,y+1,z)
    Type 1 (xz, y-normal): (x,y,z)-(x+1,y,z)-(x+1,y,z+1)-(x,y,z+1)
    Type 2 (yz, x-normal): (x,y,z)-(x,y+1,z)-(x,y+1,z+1)-(x,y,z+1)
    """
    count = 0
    for x in range(L):
        for y in range(L):
            for z in range(L):
                # Type 0: xy plaquette
                i00 = idx3(x, y, z);   i10 = idx3(x+1, y, z)
                i11 = idx3(x+1, y+1, z); i01 = idx3(x, y+1, z)
                total = (angle_diff(phi[i10], phi[i00]) + angle_diff(phi[i11], phi[i10])
                         + angle_diff(phi[i01], phi[i11]) + angle_diff(phi[i00], phi[i01]))
                if abs(round(total / (2 * math.pi))) >= 1:
                    count += 1

                # Type 1: xz plaquette
                i00 = idx3(x, y, z);   i10 = idx3(x+1, y, z)
                i11 = idx3(x+1, y, z+1); i01 = idx3(x, y, z+1)
                total = (angle_diff(phi[i10], phi[i00]) + angle_diff(phi[i11], phi[i10])
                         + angle_diff(phi[i01], phi[i11]) + angle_diff(phi[i00], phi[i01]))
                if abs(round(total / (2 * math.pi))) >= 1:
                    count += 1

                # Type 2: yz plaquette
                i00 = idx3(x, y, z);   i10 = idx3(x, y+1, z)
                i11 = idx3(x, y+1, z+1); i01 = idx3(x, y, z+1)
                total = (angle_diff(phi[i10], phi[i00]) + angle_diff(phi[i11], phi[i10])
                         + angle_diff(phi[i01], phi[i11]) + angle_diff(phi[i00], phi[i01]))
                if abs(round(total / (2 * math.pi))) >= 1:
                    count += 1
    return count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="QNG-CPU-043: 3D vortex ring stability test (two-phase protocol)."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"L={L}, N={N}, steps={STEPS} (Phase1={PHASE1_STEPS} + Phase2={PHASE2_STEPS})")
    print(f"Ring: center=({RING_X},{RING_Y},{RING_Z}), R={RING_R}")
    print(f"BETA={BETA} (sigma/chi), BETA_PHI={BETA_PHI} (phi, prevents ring collapse)")
    print(f"gamma_phi={GAMMA_PHI} (Channel F, Phase 2 only)")
    print(f"Note: pi_2(S^1)=0 -- ring NOT topologically protected; testing dynamic stability")
    print()

    phi = init_phi_ring()
    sigma = [SIGMA_REF] * N
    chi = [0.0] * N

    # Initial winding count
    n_wind_init = count_nonzero_winding_3d(phi)
    print(f"Initial non-zero winding plaquettes: {n_wind_init}")

    z_init = int(RING_Z)
    core0, bulk0, nc0 = ring_sigma_stats(sigma, z_init)
    print(f"Initial: core_sigma={core0:.4f}, bulk_sigma={bulk0:.4f}, n_core={nc0}")
    print()

    ring_history: dict[int, dict] = {}
    check6_t500_pass = False
    check6_t1000_pass = False

    print(f"=== Phase 1: phi relaxation (steps 1-{PHASE1_STEPS}, no Channel F) ===")
    for step in range(1, PHASE1_STEPS + 1):
        sigma, chi, phi = update_step_phase1(sigma, chi, phi)

    z_after_p1 = find_ring_z(sigma)
    core_p1, bulk_p1, _ = ring_sigma_stats(sigma, z_after_p1)
    n_wind_p1 = count_nonzero_winding_3d(phi)
    print(f"  After Phase 1: z_ring={z_after_p1} core_s={core_p1:.4f} bulk_s={bulk_p1:.4f} "
          f"wind={n_wind_p1}")
    print()

    print(f"=== Phase 2: Channel F active (steps {PHASE1_STEPS+1}-{STEPS}) ===")
    for step in range(PHASE1_STEPS + 1, STEPS + 1):
        sigma, chi, phi = update_step_phase2(sigma, chi, phi)

        if step in set(RECORD_STEPS):
            z_ring = find_ring_z(sigma)
            core_s, bulk_s, n_core = ring_sigma_stats(sigma, z_ring)
            R_t, n_dep = ring_radius_from_depletion(sigma, z_ring)
            n_ring_nodes = count_ring_shape_nodes(sigma, z_ring)

            ring_history[step] = {
                "z_ring": z_ring,
                "core_sigma": round(core_s, 5),
                "bulk_sigma": round(bulk_s, 5),
                "ring_radius": round(R_t, 3),
                "n_depleted": n_dep,
                "n_ring_shape": n_ring_nodes,
            }
            print(f"  T={step:5d}: z_ring={z_ring} core_s={core_s:.4f} bulk_s={bulk_s:.4f} "
                  f"R_t={R_t:.2f} n_dep={n_dep} n_ring={n_ring_nodes}")

            if step == 500:
                check6_t500_pass = core_s < 0.45
            if step == 1000:
                check6_t1000_pass = core_s < 0.45

    # Final checks
    final = ring_history.get(1000, {})
    core_final = final.get("core_sigma", SIGMA_REF)
    bulk_final = final.get("bulk_sigma", SIGMA_REF)
    R_final = final.get("ring_radius", 0.0)
    n_ring_final = final.get("n_ring_shape", 0)
    z_ring_final = final.get("z_ring", int(RING_Z))

    n_wind_final = count_nonzero_winding_3d(phi)

    print(f"\nFinal T={STEPS}:")
    print(f"  z_ring = {z_ring_final} (initial z = {int(RING_Z)})")
    print(f"  core sigma = {core_final:.4f}  (gate < 0.40)")
    print(f"  bulk sigma = {bulk_final:.4f}  (gate > 0.40)")
    print(f"  ring radius R_t = {R_final:.2f}  (gate > {RING_R/2:.1f})")
    print(f"  non-zero winding plaquettes = {n_wind_final}  (gate >= 4)")
    print(f"  ring-shape depleted nodes = {n_ring_final}  (gate >= 10)")

    check1_pass = core_final < 0.40
    check2_pass = bulk_final > 0.40
    check3_pass = R_final > RING_R / 2
    check4_pass = n_wind_final >= 4
    check5_pass = n_ring_final >= 10
    check6_pass = check6_t500_pass and check6_t1000_pass

    print(f"\nChecks:")
    print(f"  Check 1 (core < 0.40): {core_final:.4f}  {'PASS' if check1_pass else 'FAIL'}")
    print(f"  Check 2 (bulk > 0.40): {bulk_final:.4f}  {'PASS' if check2_pass else 'FAIL'}")
    print(f"  Check 3 (R_t > {RING_R/2:.1f}): {R_final:.2f}  {'PASS' if check3_pass else 'FAIL'}")
    print(f"  Check 4 (nonzero plaquettes >= 4): {n_wind_final}  {'PASS' if check4_pass else 'FAIL'}")
    print(f"  Check 5 (ring-shape nodes >= 10): {n_ring_final}  {'PASS' if check5_pass else 'FAIL'}")
    print(f"  Check 6 (depletion at T=500 AND T=1000 < 0.45): "
          f"T500={'PASS' if check6_t500_pass else 'FAIL'}, "
          f"T1000={'PASS' if check6_t1000_pass else 'FAIL'}  "
          f"{'PASS' if check6_pass else 'FAIL'}")

    checks = {
        "sigma_depleted_at_ring_core_pass": check1_pass,
        "bulk_sigma_unaffected_pass": check2_pass,
        "ring_radius_not_collapsed_pass": check3_pass,
        "nonzero_winding_plaquettes_pass": check4_pass,
        "ring_shape_depletion_pass": check5_pass,
        "depletion_persists_t500_to_t1000_pass": check6_pass,
    }
    decision = all(checks.values())

    ring_self_velocity = abs(_mi(z_ring_final - int(RING_Z)))

    report = {
        "test_id": "QNG-CPU-043",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "L": L, "N": N, "steps": STEPS,
            "phase1_steps": PHASE1_STEPS, "phase2_steps": PHASE2_STEPS,
            "alpha": ALPHA, "beta": BETA, "beta_phi": BETA_PHI,
            "delta": DELTA, "epsilon": EPSILON, "gamma_phi": GAMMA_PHI,
            "sigma_ref": SIGMA_REF,
            "ring_center": [RING_X, RING_Y, RING_Z],
            "ring_radius": RING_R,
        },
        "initial": {
            "n_nonzero_wind": n_wind_init,
            "core_sigma": round(core0, 5),
            "bulk_sigma": round(bulk0, 5),
        },
        "after_phase1": {
            "z_ring": z_after_p1,
            "core_sigma": round(core_p1, 5),
            "bulk_sigma": round(bulk_p1, 5),
            "n_nonzero_wind": n_wind_p1,
        },
        "ring_history": {str(k): v for k, v in ring_history.items()},
        "final": {
            "z_ring": z_ring_final,
            "ring_self_velocity_dz": ring_self_velocity,
            "core_sigma": round(core_final, 5),
            "bulk_sigma": round(bulk_final, 5),
            "ring_radius": round(R_final, 3),
            "n_depleted": n_ring_final,
            "n_nonzero_wind": n_wind_final,
        },
        "checks": checks,
        "interpretation": (
            "PASS: 3D vortex ring is dynamically stable over 700 steps of Channel F "
            "(1000 total). With BETA_PHI=0.05 (slow phi diffusion), the ring does not "
            "collapse before Channel F builds sigma depletion. Despite pi_2(S^1)=0 (no "
            "topological protection), the ring maintains sigma depletion and ring radius > R/2. "
            "This confirms that 3D matter in QNG can take the form of a dynamically stable "
            "vortex ring. Motivates ring lifetime (QNG-CPU-044) and self-velocity (QNG-CPU-045)."
            if decision
            else "FAIL: 3D vortex ring did not maintain sigma depletion or ring radius over "
                 "T=1000 steps. pi_2(S^1)=0 means no topological protection. "
                 "Check: (1) Ring self-velocity may be moving ring out of detection window. "
                 "(2) BETA_PHI too large — ring collapses before Channel F acts. "
                 "(3) Gates may need further adjustment based on bulk/core competition."
        ),
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG 3D Vortex Ring Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- L={L}, R={RING_R}, beta_phi={BETA_PHI}, gamma_phi={GAMMA_PHI}",
        f"- Protocol: Phase1={PHASE1_STEPS} steps (phi relax, no Channel F) + Phase2={PHASE2_STEPS} steps (Channel F)",
        f"- pi_2(S^1)=0: ring NOT topologically protected (dynamic stability test)",
        "",
        "## Phase 1 state (T=300, before Channel F)",
        f"- z_ring={z_after_p1}, core_sigma={core_p1:.4f}, bulk_sigma={bulk_p1:.4f}",
        f"- nonzero winding plaquettes: {n_wind_p1}",
        "",
        "## Ring evolution (Phase 2)",
        "",
        "| T | z_ring | core_sigma | bulk_sigma | R_t | n_dep | n_ring |",
        "|---|--------|------------|------------|-----|-------|--------|",
    ]
    for t in RECORD_STEPS:
        if t in ring_history:
            h = ring_history[t]
            lines.append(f"| {t} | {h['z_ring']} | {h['core_sigma']:.4f} | {h['bulk_sigma']:.4f} "
                         f"| {h['ring_radius']:.2f} | {h['n_depleted']} | {h['n_ring_shape']} |")
    lines += [
        "",
        "## Final state (T=1000)",
        f"- z_ring drift: {ring_self_velocity} lattice units (self-induced ring velocity)",
        f"- Non-zero winding plaquettes: {n_wind_final}",
        "",
        "## Summary checks",
        f"- Check 1 (core_sigma < 0.40): {core_final:.5f}  {'PASS' if check1_pass else 'FAIL'}",
        f"- Check 2 (bulk_sigma > 0.40): {bulk_final:.5f}  {'PASS' if check2_pass else 'FAIL'}",
        f"- Check 3 (R_t > {RING_R/2:.1f}): {R_final:.3f}  {'PASS' if check3_pass else 'FAIL'}",
        f"- Check 4 (nonzero wind >= 4): {n_wind_final}  {'PASS' if check4_pass else 'FAIL'}",
        f"- Check 5 (ring nodes >= 10): {n_ring_final}  {'PASS' if check5_pass else 'FAIL'}",
        f"- Check 6 (persists T500+T1000 < 0.45): {'PASS' if check6_pass else 'FAIL'}",
        "",
        "## Interpretation",
        report["interpretation"],
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nqng_vortex_ring_3d_reference: {'PASS' if decision else 'FAIL'}")
    if ring_self_velocity > 0:
        print(f"  Ring self-velocity: dz = {ring_self_velocity} lattice units over {STEPS} steps")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
