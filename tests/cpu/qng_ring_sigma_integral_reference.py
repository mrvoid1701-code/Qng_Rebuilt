from __future__ import annotations

"""
QNG-CPU-051: Ring sigma-depletion integral — numerical M_ring measurement.

Measures M_ring = sum_i max(0, sigma_ref - sigma_i) for rings R=2,4,6.
Evaluates rho_0 constraint: rho_0 = m_particle / (a_M * M_ring).
Checks stability of M_ring over Phase-2 steps.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-sigma-integral-v1"

L: int = 24
N: int = L * L * L
RING_Z: int = L // 2   # centre all rings at z=12
PHASE1_STEPS: int = 300
PHASE2_STEPS: int = 2000
CHECK_STEPS  = [500, 1000, 1500, 2000]

SIGMA_REF: float = 0.5
ALPHA:     float = 0.005
BETA:      float = 0.35
BETA_PHI:  float = 0.02
DELTA:     float = 0.20
CHI_DECAY: float = 0.005
CHI_REL:   float = 0.35
GAMMA_PHI: float = 0.10
EPSILON:   float = 0.0   # no Channel E — measure ring alone

A_VORTEX:  float = 0.225  # from CPU-043 / DER-QNG-027

RING_RADII = [2, 4, 6]

# Physical mass hypotheses (kg)
MASS_HYPOTHESES = {
    "proton":   1.673e-27,
    "electron": 9.109e-31,
    "planck":   2.176e-8,
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
    while d > L / 2:  d -= L
    while d < -L / 2: d += L
    return d

def wrap(a: float) -> float:
    a = a % (2 * math.pi)
    return a - 2 * math.pi if a > math.pi else a

def angle_diff(a: float, b: float) -> float:
    return wrap(a - b)

def circular_mean_weighted(phases, weights):
    sx = sum(w * math.cos(p) for w, p in zip(weights, phases))
    sy = sum(w * math.sin(p) for w, p in zip(weights, phases))
    return math.atan2(sy, sx)

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---------------------------------------------------------------------------
# Init single ring
# ---------------------------------------------------------------------------

def init_phi_ring(r_z: int, ring_r: float) -> list[float]:
    cx = cy = L / 2.0
    phi = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - cx); dy = _mi(y - cy)
        rho = math.sqrt(dx*dx + dy*dy)
        dz = _mi(z - r_z)
        phi.append(math.atan2(dz, rho - ring_r))
    return phi


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def phase_disorder(phi: list[float], i: int) -> float:
    x, y, z = coord3(i)
    nb = [idx3(x-1,y,z), idx3(x+1,y,z), idx3(x,y-1,z),
          idx3(x,y+1,z), idx3(x,y,z-1), idx3(x,y,z+1)]
    sx = sum(math.cos(phi[j]) for j in nb) / 6.0
    sy = sum(math.sin(phi[j]) for j in nb) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx*sx + sy*sy))

def update_step(sigma, chi, phi, channel_f: bool):
    ns, nc, np_ = [], [], []
    for i in range(N):
        x, y, z = coord3(i)
        nb = [idx3(x-1,y,z), idx3(x+1,y,z), idx3(x,y-1,z),
              idx3(x,y+1,z), idx3(x,y,z-1), idx3(x,y,z+1)]
        sb = sum(sigma[j] for j in nb) / 6.0
        if channel_f:
            D_i = phase_disorder(phi, i)
            s = clip01(sigma[i] + ALPHA*(SIGMA_REF-sigma[i]) + BETA*(sb-sigma[i])
                       - GAMMA_PHI*D_i*sigma[i])
        else:
            s = clip01(sigma[i] + ALPHA*(SIGMA_REF-sigma[i]) + BETA*(sb-sigma[i]))
        c = chi[i]*(1-CHI_DECAY) + CHI_REL*(sb-sigma[i]) + DELTA*(SIGMA_REF-sigma[i])
        nph = [phi[j] for j in nb]; nwt = [sigma[j] for j in nb]; tw = sum(nwt)
        pm = circular_mean_weighted(nph, nwt) if tw > 1e-10 else phi[i]
        p = wrap(phi[i] + BETA_PHI*angle_diff(pm, phi[i]) + EPSILON*c)
        ns.append(s); nc.append(c); np_.append(p)
    return ns, nc, np_


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------

def measure_ring(sigma: list[float], ring_r: float, r_z: int) -> dict:
    """
    Measure sigma statistics for a ring at (cx,cy,r_z) with radius ring_r.
    Returns: M_ring (total deficit), M_ring_shell (shell-restricted), sigma_core, sigma_bulk.
    """
    cx = cy = L / 2.0
    shell_width = 4.0

    total_deficit = 0.0
    shell_deficit = 0.0
    core_sigmas   = []
    bulk_sigmas   = []

    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - cx); dy = _mi(y - cy); dz = _mi(z - r_z)
        rho = math.sqrt(dx*dx + dy*dy)
        dist_to_ring = math.sqrt(_mi(rho - ring_r)**2 + dz**2)

        deficit = max(0.0, SIGMA_REF - sigma[i])
        total_deficit += deficit

        if abs(rho - ring_r) < shell_width and abs(dz) < shell_width:
            shell_deficit += deficit
            if dist_to_ring < 2.0:
                core_sigmas.append(sigma[i])
            elif dist_to_ring < shell_width:
                bulk_sigmas.append(sigma[i])

    sigma_core = sum(core_sigmas) / len(core_sigmas) if core_sigmas else SIGMA_REF
    sigma_bulk = sum(bulk_sigmas) / len(bulk_sigmas) if bulk_sigmas else SIGMA_REF

    return {
        "M_ring":       round(total_deficit, 4),
        "M_ring_shell": round(shell_deficit, 4),
        "sigma_core":   round(sigma_core, 4),
        "sigma_bulk":   round(sigma_bulk, 4),
        "n_core":       len(core_sigmas),
        "n_bulk":       len(bulk_sigmas),
    }


def effective_radius(sigma: list[float], ring_r: float, r_z: int) -> float:
    """Estimate effective ring radius from minimum-sigma toroidal shell."""
    cx = cy = L / 2.0
    best_rho, best_s = ring_r, 1e9
    for rho_test in [float(k) * 0.5 for k in range(2, 2 * L)]:
        tot, cnt = 0.0, 0
        for i in range(N):
            x, y, z = coord3(i)
            dx = _mi(x - cx); dy = _mi(y - cy); dz = _mi(z - r_z)
            rho = math.sqrt(dx*dx + dy*dy)
            if abs(rho - rho_test) < 0.5 and abs(dz) < 2:
                tot += sigma[i]; cnt += 1
        if cnt > 0 and tot / cnt < best_s:
            best_s = tot / cnt; best_rho = rho_test
    return best_rho


# ---------------------------------------------------------------------------
# Run one ring
# ---------------------------------------------------------------------------

def run_ring(ring_r: float) -> dict:
    phi   = init_phi_ring(RING_Z, ring_r)
    sigma = [SIGMA_REF] * N
    chi   = [0.0] * N

    print(f"  [R={ring_r:.0f}] Phase 1 ({PHASE1_STEPS} steps)...")
    for _ in range(PHASE1_STEPS):
        sigma, chi, phi = update_step(sigma, chi, phi, channel_f=False)

    snapshots = []
    t = 0
    next_check = set(CHECK_STEPS)
    print(f"  [R={ring_r:.0f}] Phase 2 ({PHASE2_STEPS} steps)...")
    for step in range(1, PHASE2_STEPS + 1):
        sigma, chi, phi = update_step(sigma, chi, phi, channel_f=True)
        if step in next_check:
            m = measure_ring(sigma, ring_r, RING_Z)
            m["t"] = step
            snapshots.append(m)
            print(f"    T={step}: M_ring={m['M_ring']:.2f}  "
                  f"M_ring_shell={m['M_ring_shell']:.2f}  "
                  f"sigma_core={m['sigma_core']:.3f}")

    vals = [s["M_ring_shell"] for s in snapshots]
    mean_m = sum(vals) / len(vals)
    std_m  = math.sqrt(sum((v - mean_m)**2 for v in vals) / len(vals))
    cv     = std_m / mean_m if mean_m > 0 else 999.0

    return {
        "R": ring_r,
        "snapshots": snapshots,
        "M_ring_mean":  round(mean_m, 4),
        "M_ring_std":   round(std_m, 4),
        "M_ring_cv":    round(cv, 4),
        "M_ring_final": snapshots[-1]["M_ring_shell"],
        "sigma_core":   snapshots[-1]["sigma_core"],
        "sigma_bulk":   snapshots[-1]["sigma_bulk"],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    print(f"L={L}, N={N}  RING_Z={RING_Z}  Phase2={PHASE2_STEPS}")
    print()

    results = {}
    for R in RING_RADII:
        print(f"=== Ring R={R} ===")
        results[R] = run_ring(float(R))
        print()

    # --- Checks ---
    M_r2 = results[2]["M_ring_mean"]
    M_r4 = results[4]["M_ring_mean"]
    M_r6 = results[6]["M_ring_mean"]

    check1 = all(results[R]["M_ring_cv"] < 0.10 for R in RING_RADII)
    check2 = all(results[R]["M_ring_mean"] > 0   for R in RING_RADII)
    check3 = M_r4 / M_r2 > 1.5 if M_r2 > 0 else False

    decision = check1 and check2 and check3

    # --- rho_0 constraint table ---
    M_standard = M_r4  # use R=4 as standard ring (CPU-043 baseline)
    print("=" * 60)
    print(f"M_ring (R=2): {M_r2:.3f}")
    print(f"M_ring (R=4): {M_r4:.3f}  <-- standard (CPU-043)")
    print(f"M_ring (R=6): {M_r6:.3f}")
    print(f"Ratio R4/R2:  {M_r4/M_r2:.3f}" if M_r2 > 0 else "")
    print()
    print("rho_0 constraint: rho_0 = m_particle / (a_M * M_ring_R4)")
    print(f"  (a_M=1 normalized; M_ring_R4={M_standard:.3f})")
    print()
    print(f"{'Particle':>10}  {'m (kg)':>12}  {'rho_0/a_M':>15}  {'f/a_M (km/s)^2/lu':>20}")

    rho0_table = {}
    f_target = 43000.0  # from OBS-002 empirical: f = rho_0 * A_VORTEX ~ 43000
    for name, m_kg in MASS_HYPOTHESES.items():
        rho0_over_aM = m_kg / M_standard if M_standard > 0 else float("nan")
        # f has units (km/s)^2 / lattice-unit; we can't compute it without a
        # but we can report the ratio rho_0/a_M in kg/lattice-unit
        rho0_table[name] = {
            "m_kg": m_kg,
            "rho0_over_aM_kg_per_lu": rho0_over_aM,
        }
        print(f"  {name:>10}  {m_kg:>12.3e}  {rho0_over_aM:>15.3e}")

    print()
    print(f"Empirical target: rho_0 * A_VORTEX ~ {f_target:.0f} (km/s)^2/lu")
    print(f"  => rho_0_empirical ~ {f_target/A_VORTEX:.0f} (km/s)^2/lu")
    print(f"  => to match proton: a_M needs ~ {MASS_HYPOTHESES['proton']/(M_standard * f_target/A_VORTEX):.3e} (kg*lu/(km/s)^2)")
    print()
    print("Checks:")
    print(f"  Check 1 (M_ring stable, CV<10%):   {'PASS' if check1 else 'FAIL'}  "
          f"CVs={[round(results[R]['M_ring_cv'],3) for R in RING_RADII]}")
    print(f"  Check 2 (M_ring > 0):              {'PASS' if check2 else 'FAIL'}")
    print(f"  Check 3 (M_ring R4/R2 > 1.5):      {'PASS' if check3 else 'FAIL'}  ratio={M_r4/M_r2:.3f}" if M_r2 > 0 else "  Check 3: R2 ring failed")
    print(f"\nqng_ring_sigma_integral_reference: {'PASS' if decision else 'FAIL'}")

    report = {
        "test_id": "QNG-CPU-051",
        "decision": "pass" if decision else "fail",
        "parameters": {"L": L, "N": N, "ring_z": RING_Z,
                       "alpha": ALPHA, "beta": BETA, "gamma_phi": GAMMA_PHI,
                       "A_VORTEX": A_VORTEX},
        "ring_results": {
            str(R): {
                "M_ring_mean": results[R]["M_ring_mean"],
                "M_ring_cv":   results[R]["M_ring_cv"],
                "sigma_core":  results[R]["sigma_core"],
                "sigma_bulk":  results[R]["sigma_bulk"],
                "snapshots":   results[R]["snapshots"],
            } for R in RING_RADII
        },
        "M_ring_standard_R4": M_standard,
        "rho0_constraint": {
            "formula": "rho_0 = m_particle / (a_M * M_ring_R4)",
            "M_ring_R4": M_standard,
            "A_VORTEX":  A_VORTEX,
            "f_empirical_km2_s2_per_lu": f_target,
            "rho0_empirical": round(f_target / A_VORTEX, 1),
            "per_particle": rho0_table,
        },
        "checks": {
            "M_ring_stable_pass":   check1,
            "M_ring_positive_pass": check2,
            "M_ring_scales_pass":   check3,
            "ratio_R4_R2":          round(M_r4/M_r2, 3) if M_r2 > 0 else None,
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-CPU-051: Ring Sigma-Depletion Integral",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## M_ring by Radius",
        "| R | M_ring_mean | M_ring_cv | sigma_core | sigma_bulk |",
        "|---|-------------|-----------|------------|------------|",
    ] + [
        f"| {R} | {results[R]['M_ring_mean']} | {results[R]['M_ring_cv']} | "
        f"{results[R]['sigma_core']} | {results[R]['sigma_bulk']} |"
        for R in RING_RADII
    ] + [
        "",
        "## rho_0 Constraint",
        f"- M_ring (R=4, standard): {M_standard}",
        f"- Formula: `rho_0 = m_particle / (a_M * {M_standard})`",
        f"- Empirical rho_0 (from OBS-002): ~{round(f_target/A_VORTEX, 0)}  (km/s)^2/lu",
        "",
        "## Checks",
        f"- Check 1 (stable): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (positive): {'PASS' if check2 else 'FAIL'}",
        f"- Check 3 (scales with R): {'PASS' if check3 else 'FAIL'}",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
