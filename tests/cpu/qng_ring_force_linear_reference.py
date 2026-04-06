from __future__ import annotations

"""
QNG-CPU-048: Two-ring force direction in linear epsilon regime.

epsilon=0.005 (linear: phi perturbation ~ 0.065 rad/step).
Measures SEPARATION S(t) = |z2 - z1| between rings over time.
Attraction = S decreases. Repulsion = S increases.
Ring-specific detection zones prevent confusion.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-force-linear-reference-v1"

L: int = 24
N: int = L * L * L
PHASE1_STEPS: int = 300
PHASE2_STEPS: int = 3000
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

EPSILONS = [0.000, 0.005]


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
# Init
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

def init_phi_single(r_z: int, ring_r: float) -> list[float]:
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
    nb = [idx3(x-1,y,z),idx3(x+1,y,z),idx3(x,y-1,z),idx3(x,y+1,z),idx3(x,y,z-1),idx3(x,y,z+1)]
    sx = sum(math.cos(phi[j]) for j in nb) / 6.0
    sy = sum(math.sin(phi[j]) for j in nb) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx*sx + sy*sy))

def update_step(sigma, chi, phi, channel_f: bool, epsilon: float):
    ns, nc, np_ = [], [], []
    for i in range(N):
        x, y, z = coord3(i)
        nb = [idx3(x-1,y,z),idx3(x+1,y,z),idx3(x,y-1,z),idx3(x,y+1,z),idx3(x,y,z-1),idx3(x,y,z+1)]
        sb = sum(sigma[j] for j in nb) / 6.0
        if channel_f:
            D_i = phase_disorder(phi, i)
            s = clip01(sigma[i] + ALPHA*(SIGMA_REF-sigma[i]) + BETA*(sb-sigma[i]) - GAMMA_PHI*D_i*sigma[i])
        else:
            s = clip01(sigma[i] + ALPHA*(SIGMA_REF-sigma[i]) + BETA*(sb-sigma[i]))
        c = chi[i]*(1-CHI_DECAY) + CHI_REL*(sb-sigma[i]) + DELTA*(SIGMA_REF-sigma[i])
        nph = [phi[j] for j in nb]; nwt = [sigma[j] for j in nb]; tw = sum(nwt)
        pm = circular_mean_weighted(nph, nwt) if tw > 1e-10 else phi[i]
        p = wrap(phi[i] + BETA_PHI*angle_diff(pm, phi[i]) + epsilon*c)
        ns.append(s); nc.append(c); np_.append(p)
    return ns, nc, np_


# ---------------------------------------------------------------------------
# Ring detection — zone-restricted
# ---------------------------------------------------------------------------

def find_ring_in_zone(sigma: list[float], ring_r: float,
                      z_min: int, z_max: int) -> tuple[int, float]:
    """Find z with min mean sigma in toroidal shell, restricted to z in [z_min, z_max]."""
    best_z, best_s = (z_min + z_max) // 2, 1e9
    for z in range(z_min, z_max + 1):
        tot, cnt = 0.0, 0
        for i in range(N):
            xi, yi, zi = coord3(i)
            if zi != z: continue
            dx = _mi(xi - L/2.0); dy = _mi(yi - L/2.0)
            rho = math.sqrt(dx*dx + dy*dy)
            if abs(rho - ring_r) <= 3:
                tot += sigma[i]; cnt += 1
        if cnt > 0 and tot/cnt < best_s:
            best_s = tot/cnt; best_z = z
    return best_z, best_s

def separation(z1: int, z2: int) -> int:
    d = abs(z2 - z1)
    return min(d, L - d)


# ---------------------------------------------------------------------------
# Run scenario
# ---------------------------------------------------------------------------

def run_scenario(phi_init: list[float], epsilon: float, label: str,
                 has_ring2: bool = True) -> dict:
    sigma = [SIGMA_REF] * N
    chi   = [0.0] * N
    phi   = phi_init[:]

    print(f"  [{label}] Phase 1...")
    for _ in range(PHASE1_STEPS):
        sigma, chi, phi = update_step(sigma, chi, phi, channel_f=False, epsilon=0.0)

    traj = []
    print(f"  [{label}] Phase 2 (eps={epsilon})...")
    for t in range(1, PHASE2_STEPS + 1):
        sigma, chi, phi = update_step(sigma, chi, phi, channel_f=True, epsilon=epsilon)
        if t % CHECK_INTERVAL == 0:
            z1, s1 = find_ring_in_zone(sigma, RING_R, 0, L//2 - 1)
            if has_ring2:
                z2, s2 = find_ring_in_zone(sigma, RING_R, L//2, L - 1)
                sep = separation(z1, z2)
                traj.append({"t": t, "z1": z1, "z2": z2, "sep": sep,
                             "sigma1": round(s1,4), "sigma2": round(s2,4)})
                if t % 500 == 0:
                    print(f"    T={t}: z1={z1} z2={z2} sep={sep}")
            else:
                traj.append({"t": t, "z1": z1, "z2": None, "sep": None,
                             "sigma1": round(s1,4)})
                if t % 500 == 0:
                    print(f"    T={t}: z1={z1}")

    return {"label": label, "epsilon": epsilon, "trajectory": traj,
            "z1_final": traj[-1]["z1"],
            "z2_final": traj[-1]["z2"],
            "sep_final": traj[-1]["sep"]}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    print(f"L={L}, N={N}  Ring1 z={RING1_Z} Ring2 z={RING2_Z} R={RING_R}")
    print(f"Separation={RING2_Z-RING1_Z}  lambda~3.41")
    print()

    phi_two    = init_phi_two_rings(RING1_Z, RING2_Z, RING_R)
    phi_single = init_phi_single(RING1_Z, RING_R)

    results = {}

    for eps in EPSILONS:
        label = f"two_eps{str(eps).replace('.','p')}"
        print(f"=== TWO RINGS, epsilon={eps} ===")
        results[label] = run_scenario(list(phi_two), eps, label, has_ring2=True)
        print()

    print("=== SINGLE RING, epsilon=0.005 (drift reference) ===")
    results["single_eps0p005"] = run_scenario(list(phi_single), 0.005, "single_eps0p005", has_ring2=False)
    print()

    # Extract
    r_base = results["two_eps0p0"]
    r_eps  = results["two_eps0p005"]
    r_sing = results["single_eps0p005"]

    sep_base  = r_base["sep_final"]
    sep_eps   = r_eps["sep_final"]
    z1_sing   = r_sing["z1_final"]

    sep_diff = abs(sep_eps - sep_base) if (sep_base is not None and sep_eps is not None) else 0

    # Trend: compare early vs late separation with eps=0.005
    traj_eps = r_eps["trajectory"]
    seps_late  = [p["sep"] for p in traj_eps if p["t"] >= 1000 and p["sep"] is not None]
    seps_early = [p["sep"] for p in traj_eps if p["t"] <= 500  and p["sep"] is not None]
    trend = "UNKNOWN"
    if seps_early and seps_late:
        mean_early = sum(seps_early) / len(seps_early)
        mean_late  = sum(seps_late)  / len(seps_late)
        if mean_late < mean_early - 0.5:
            trend = "ATTRACTION"
        elif mean_late > mean_early + 0.5:
            trend = "REPULSION"
        else:
            trend = "NEUTRAL"

    check1 = all(p["z1"] is not None for p in r_eps["trajectory"])
    check2 = sep_diff > 1
    check3_info = trend
    check4_info = abs(r_eps["z1_final"] - z1_sing) if (r_eps["z1_final"] and z1_sing) else None

    decision = check1 and check2

    print("=" * 60)
    print(f"Separation final:  eps=0.000 -> {sep_base}   eps=0.005 -> {sep_eps}")
    print(f"Separation diff:   {sep_diff}")
    print(f"Trend (eps=0.005): {trend}  (early mean={sum(seps_early)/len(seps_early) if seps_early else 0:.1f}, late mean={sum(seps_late)/len(seps_late) if seps_late else 0:.1f})")
    print(f"z_ring1 single (eps=0.005, T=3000): {z1_sing}")
    print()
    print("Separation trajectory (eps=0.000 vs eps=0.005):")
    print(f"  {'t':>5}  {'sep(eps=0)':>12}  {'sep(eps=0.005)':>15}")
    for i in range(len(r_base["trajectory"])):
        t   = r_base["trajectory"][i]["t"]
        s0  = r_base["trajectory"][i]["sep"]
        s1  = r_eps["trajectory"][i]["sep"]
        if t % 500 == 0 or i == 0:
            print(f"  {t:5d}  {str(s0):>12}  {str(s1):>15}")
    print()
    print("Checks:")
    print(f"  Check 1 (ring1 always detectable):     {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (sep diff > 1): {sep_diff}  {'PASS' if check2 else 'FAIL'}")
    print(f"  Check 3 [info] trend: {trend}")
    print(f"  Check 4 [info] ring2 effect on ring1: {check4_info}")
    print(f"\nqng_ring_force_linear_reference: {'PASS' if decision else 'FAIL'}")

    report = {
        "test_id": "QNG-CPU-048",
        "decision": "pass" if decision else "fail",
        "parameters": {"L": L, "N": N, "ring_r": RING_R, "ring1_z": RING1_Z,
                       "ring2_z": RING2_Z, "epsilons": EPSILONS,
                       "phase2_steps": PHASE2_STEPS},
        "sep_final_eps0":    sep_base,
        "sep_final_eps0p005":sep_eps,
        "sep_diff":          sep_diff,
        "trend":             trend,
        "z1_single_eps0p005":z1_sing,
        "ring2_effect_on_ring1": check4_info,
        "checks": {
            "ring1_always_detectable_pass": check1,
            "sep_diff_gt_1_pass":          check2,
            "trend_info":                  trend,
        },
        "trajectories": {k: v["trajectory"] for k, v in results.items()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-CPU-048: Ring Force Linear Reference",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- epsilon=0.005 (linear regime), Phase2={PHASE2_STEPS} steps",
        "",
        "## Results",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Separation (eps=0) final | {sep_base} |",
        f"| Separation (eps=0.005) final | {sep_eps} |",
        f"| Separation diff | {sep_diff} |",
        f"| Trend | {trend} |",
        "",
        "## Checks",
        f"- Check 1 (ring detectable): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (sep diff > 1): {'PASS' if check2 else 'FAIL'} ({sep_diff})",
        f"- Check 3 [info] trend: {trend}",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
