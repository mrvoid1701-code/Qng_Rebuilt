from __future__ import annotations

"""
QNG-CPU-047: Two-ring attraction/repulsion — does chi-field force move matter?

Compares epsilon=0 (chi inert) vs epsilon=0.1 (chi drives phi).
Measures whether chi-phi coupling mediates a force between vortex rings.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-force-reference-v1"

L: int = 24
N: int = L * L * L
PHASE1_STEPS: int = 300
PHASE2_STEPS: int = 2000
CHECK_INTERVAL: int = 100

SIGMA_REF: float = 0.5
ALPHA:     float = 0.005
BETA:      float = 0.35
BETA_PHI:  float = 0.02
DELTA:     float = 0.20
CHI_DECAY: float = 0.005
CHI_REL:   float = 0.35
GAMMA_PHI: float = 0.10

RING_R:  float = 4.0
RING1_Z: int   = 6
RING2_Z: int   = 18

EPSILON_OFF: float = 0.0
EPSILON_ON:  float = 0.1


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
# Initialization
# ---------------------------------------------------------------------------

def init_phi_two_rings(r1_z: int, r2_z: int, ring_r: float) -> list[float]:
    cx = cy = L / 2.0
    phi = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - cx); dy = _mi(y - cy)
        rho = math.sqrt(dx*dx + dy*dy)
        dz1 = _mi(z - r1_z); dz2 = _mi(z - r2_z)
        d1 = math.sqrt(_mi(rho - ring_r)**2 + dz1**2)
        d2 = math.sqrt(_mi(rho - ring_r)**2 + dz2**2)
        phi.append(math.atan2(dz1, rho - ring_r) if d1 <= d2
                   else math.atan2(dz2, rho - ring_r))
    return phi

def init_phi_single_ring(r_z: int, ring_r: float) -> list[float]:
    cx = cy = L / 2.0
    return [math.atan2(_mi(coord3(i)[2] - r_z),
                       math.sqrt(_mi(coord3(i)[0]-cx)**2 + _mi(coord3(i)[1]-cy)**2) - ring_r)
            for i in range(N)]


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def phase_disorder(phi: list[float], i: int) -> float:
    x, y, z = coord3(i)
    nb = [idx3(x-1,y,z),idx3(x+1,y,z),idx3(x,y-1,z),idx3(x,y+1,z),idx3(x,y,z-1),idx3(x,y,z+1)]
    sx = sum(math.cos(phi[j]) for j in nb) / 6.0
    sy = sum(math.sin(phi[j]) for j in nb) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx*sx + sy*sy))

def update_step(sigma, chi, phi, channel_f: bool, epsilon: float):
    ns, nc, np_ = [], [], []
    for i in range(N):
        x, y, z = coord3(i)
        nb = [idx3(x-1,y,z),idx3(x+1,y,z),idx3(x,y-1,z),idx3(x,y+1,z),idx3(x,y,z-1),idx3(x,y,z+1)]
        sigma_bar = sum(sigma[j] for j in nb) / 6.0
        if channel_f:
            D_i = phase_disorder(phi, i)
            s = clip01(sigma[i] + ALPHA*(SIGMA_REF-sigma[i]) + BETA*(sigma_bar-sigma[i]) - GAMMA_PHI*D_i*sigma[i])
        else:
            s = clip01(sigma[i] + ALPHA*(SIGMA_REF-sigma[i]) + BETA*(sigma_bar-sigma[i]))
        c = chi[i]*(1-CHI_DECAY) + CHI_REL*(sigma_bar-sigma[i]) + DELTA*(SIGMA_REF-sigma[i])
        nph = [phi[j] for j in nb]; nwt = [sigma[j] for j in nb]; tw = sum(nwt)
        pm = circular_mean_weighted(nph, nwt) if tw > 1e-10 else phi[i]
        p = wrap(phi[i] + BETA_PHI*angle_diff(pm, phi[i]) + epsilon*chi[i])
        ns.append(s); nc.append(c); np_.append(p)
    return ns, nc, np_


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------

def find_ring_z(sigma: list[float], ring_r: float, z_hint: int) -> int:
    best_z, best_s = z_hint, 1e9
    for z in range(L):
        if abs(_mi(float(z - z_hint))) > 8:
            continue   # only search near expected position
        tot, cnt = 0.0, 0
        for i in range(N):
            xi, yi, zi = coord3(i)
            if zi != z: continue
            dx = _mi(xi - L/2.0); dy = _mi(yi - L/2.0)
            if abs(math.sqrt(dx*dx+dy*dy) - ring_r) <= 3:
                tot += sigma[i]; cnt += 1
        if cnt > 0 and tot/cnt < best_s:
            best_s = tot/cnt; best_z = z
    return best_z


# ---------------------------------------------------------------------------
# Run one scenario
# ---------------------------------------------------------------------------

def run_scenario(phi_init: list[float], epsilon: float, label: str,
                 z1_hint: int = RING1_Z, z2_hint: int | None = None) -> dict:
    sigma = [SIGMA_REF] * N
    chi   = [0.0] * N
    phi   = phi_init[:]

    for _ in range(PHASE1_STEPS):
        sigma, chi, phi = update_step(sigma, chi, phi, channel_f=False, epsilon=0.0)

    trajectory_r1, trajectory_r2 = [], []
    z1_track = z1_hint
    z2_track = z2_hint if z2_hint is not None else RING2_Z

    for t in range(1, PHASE2_STEPS + 1):
        sigma, chi, phi = update_step(sigma, chi, phi, channel_f=True, epsilon=epsilon)
        if t % CHECK_INTERVAL == 0:
            z1 = find_ring_z(sigma, RING_R, z1_track)
            trajectory_r1.append({"t": t, "z": z1})
            z1_track = z1
            if z2_hint is not None:
                z2 = find_ring_z(sigma, RING_R, z2_track)
                trajectory_r2.append({"t": t, "z": z2})
                z2_track = z2

    return {
        "label":        label,
        "epsilon":      epsilon,
        "trajectory_r1": trajectory_r1,
        "trajectory_r2": trajectory_r2,
        "z_r1_final": trajectory_r1[-1]["z"] if trajectory_r1 else None,
        "z_r2_final": trajectory_r2[-1]["z"] if trajectory_r2 else None,
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

    print(f"L={L}, N={N}, Phase1={PHASE1_STEPS}, Phase2={PHASE2_STEPS}")
    print(f"Ring1 z={RING1_Z}, Ring2 z={RING2_Z}, R={RING_R}")
    print(f"Separation={RING2_Z-RING1_Z}, lambda~3.41, Yukawa~{math.exp(-(RING2_Z-RING1_Z)/3.41):.4f}")
    print()

    phi_two = init_phi_two_rings(RING1_Z, RING2_Z, RING_R)
    phi_one = init_phi_single_ring(RING1_Z, RING_R)

    # 1. Two rings, epsilon=0 (chi inert baseline)
    print("=== TWO RINGS, epsilon=0 (baseline) ===")
    r_two_off = run_scenario(list(phi_two), EPSILON_OFF, "two_eps0",
                             z1_hint=RING1_Z, z2_hint=RING2_Z)

    # 2. Two rings, epsilon=0.1 (chi drives phi)
    print("=== TWO RINGS, epsilon=0.1 (channel E on) ===")
    r_two_on = run_scenario(list(phi_two), EPSILON_ON, "two_eps01",
                            z1_hint=RING1_Z, z2_hint=RING2_Z)

    # 3. Single ring, epsilon=0.1 (isolation reference)
    print("=== SINGLE RING, epsilon=0.1 (reference) ===")
    r_one_on = run_scenario(list(phi_one), EPSILON_ON, "one_eps01",
                            z1_hint=RING1_Z, z2_hint=None)

    # Extract final positions
    z1_two_off = r_two_off["z_r1_final"]
    z1_two_on  = r_two_on["z_r1_final"]
    z1_one_on  = r_one_on["z_r1_final"]
    z2_two_off = r_two_off["z_r2_final"]
    z2_two_on  = r_two_on["z_r2_final"]

    diff_eps    = abs(_mi(float(z1_two_on  - z1_two_off)))   # epsilon effect on ring 1
    diff_ring2  = abs(_mi(float(z1_two_on  - z1_one_on )))   # ring 2 presence effect

    # Direction of ring 1 motion with epsilon=0.1 vs baseline
    dz1_toward = _mi(float(z1_two_on - z1_two_off))   # +ve = toward ring2 (z=18)
    direction = "ATTRACTION" if dz1_toward > 0 else ("REPULSION" if dz1_toward < 0 else "NONE")

    check1 = (z1_two_off is not None and z2_two_off is not None and
              z1_two_on  is not None and z2_two_on  is not None)
    check2 = diff_eps   > 1
    check3 = diff_ring2 > 1
    decision = check1 and check2 and check3

    print()
    print("=" * 60)
    print("Final positions:")
    print(f"  z_ring1 two-rings eps=0  : {z1_two_off}")
    print(f"  z_ring1 two-rings eps=0.1: {z1_two_on}   (ring2 present)")
    print(f"  z_ring1 single   eps=0.1 : {z1_one_on}   (ring2 absent)")
    print(f"  z_ring2 two-rings eps=0  : {z2_two_off}")
    print(f"  z_ring2 two-rings eps=0.1: {z2_two_on}")
    print()
    print(f"  |z1(eps=0.1) - z1(eps=0)|    = {diff_eps:.1f}  (epsilon effect)")
    print(f"  |z1_two(eps=0.1) - z1_one(eps=0.1)| = {diff_ring2:.1f}  (ring2 presence effect)")
    print(f"  Direction of z_ring1 shift: {direction}  (dz={dz1_toward:.1f})")
    print()
    print("Trajectory ring 1 (two rings, epsilon comparison):")
    print(f"  {'t':>5}  {'z(eps=0)':>10}  {'z(eps=0.1)':>12}  {'diff':>6}")
    for i in range(len(r_two_off["trajectory_r1"])):
        t   = r_two_off["trajectory_r1"][i]["t"]
        zo  = r_two_off["trajectory_r1"][i]["z"]
        zon = r_two_on["trajectory_r1"][i]["z"]
        print(f"  {t:5d}  {zo:10d}  {zon:12d}  {zon-zo:6d}")
    print()
    print("Checks:")
    print(f"  Check 1 (both rings detected T=2000): {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (epsilon changes z_ring1 > 1): {diff_eps:.1f}  {'PASS' if check2 else 'FAIL'}")
    print(f"  Check 3 (ring2 changes z_ring1 > 1):  {diff_ring2:.1f}  {'PASS' if check3 else 'FAIL'}")
    print(f"  Check 4 [info] direction: {direction}")
    print(f"\nqng_ring_force_reference: {'PASS' if decision else 'FAIL'}")

    report = {
        "test_id": "QNG-CPU-047",
        "decision": "pass" if decision else "fail",
        "parameters": {"L": L, "N": N, "ring_r": RING_R, "ring1_z": RING1_Z,
                       "ring2_z": RING2_Z, "epsilon_on": EPSILON_ON,
                       "phase2_steps": PHASE2_STEPS},
        "z_ring1_two_eps0":    z1_two_off,
        "z_ring1_two_eps01":   z1_two_on,
        "z_ring1_single_eps01":z1_one_on,
        "z_ring2_two_eps0":    z2_two_off,
        "z_ring2_two_eps01":   z2_two_on,
        "diff_epsilon_effect":  round(diff_eps, 2),
        "diff_ring2_presence":  round(diff_ring2, 2),
        "direction_ring1":      direction,
        "dz1_toward_ring2":     round(dz1_toward, 2),
        "checks": {
            "both_rings_survived_pass":       check1,
            "epsilon_changes_position_pass":  check2,
            "ring2_changes_position_pass":    check3,
            "direction_info":                 direction,
        },
        "trajectory_r1_two_eps0":  r_two_off["trajectory_r1"],
        "trajectory_r1_two_eps01": r_two_on["trajectory_r1"],
        "trajectory_r1_single_eps01": r_one_on["trajectory_r1"],
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-CPU-047: Ring Force Reference",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- epsilon=0 vs epsilon={EPSILON_ON}, Phase2={PHASE2_STEPS} steps",
        "",
        "## Final Positions",
        f"| Scenario | z_ring1 | z_ring2 |",
        f"|----------|---------|---------|",
        f"| Two rings eps=0   | {z1_two_off} | {z2_two_off} |",
        f"| Two rings eps=0.1 | {z1_two_on} | {z2_two_on} |",
        f"| Single ring eps=0.1 | {z1_one_on} | — |",
        "",
        f"- Epsilon effect on ring1: {diff_eps:.1f} lattice units",
        f"- Ring2 presence effect:   {diff_ring2:.1f} lattice units",
        f"- Direction: {direction}",
        "",
        "## Checks",
        f"- Check 1 (rings survived): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (epsilon effect > 1): {'PASS' if check2 else 'FAIL'} ({diff_eps:.1f})",
        f"- Check 3 (ring2 presence > 1): {'PASS' if check3 else 'FAIL'} ({diff_ring2:.1f})",
        f"- Check 4 [info] direction: {direction}",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
