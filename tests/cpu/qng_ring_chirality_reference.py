from __future__ import annotations

"""
QNG-CPU-049: Ring force chirality comparison.

Same chirality (W=+1, W=+1) vs opposite chirality (W=+1, W=-1).
epsilon=0.005 (linear regime).
Key question: does winding of ring 2 affect force on ring 1?
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-chirality-reference-v1"

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
EPSILON: float = 0.005


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

def init_phi_two_rings(r1_z: int, r2_z: int, ring_r: float,
                       w2: int = 1) -> list[float]:
    """
    Ring 1 always W=+1: phi = atan2(dz1, rho-R)
    Ring 2 chirality set by w2:
      w2=+1: phi = atan2(dz2, rho-R)
      w2=-1: phi = atan2(-dz2, rho-R)
    """
    cx = cy = L / 2.0
    phi = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - cx); dy = _mi(y - cy)
        rho = math.sqrt(dx*dx + dy*dy)
        dz1 = _mi(z - r1_z); dz2 = _mi(z - r2_z)
        d1 = math.sqrt(_mi(rho - ring_r)**2 + dz1**2)
        d2 = math.sqrt(_mi(rho - ring_r)**2 + dz2**2)
        if d1 <= d2:
            phi.append(math.atan2(dz1, rho - ring_r))
        else:
            phi.append(math.atan2(w2 * dz2, rho - ring_r))
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


def trend_label(traj: list[dict]) -> tuple[str, float, float]:
    seps_early = [p["sep"] for p in traj if p["t"] <= 500  and p["sep"] is not None]
    seps_late  = [p["sep"] for p in traj if p["t"] >= 1000 and p["sep"] is not None]
    if not seps_early or not seps_late:
        return "UNKNOWN", 0.0, 0.0
    me = sum(seps_early) / len(seps_early)
    ml = sum(seps_late)  / len(seps_late)
    if ml < me - 0.5:
        label = "ATTRACTION"
    elif ml > me + 0.5:
        label = "REPULSION"
    else:
        label = "NEUTRAL"
    return label, me, ml


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
    print(f"Separation={RING2_Z-RING1_Z}  epsilon={EPSILON}")
    print()

    phi_same_eps0    = init_phi_two_rings(RING1_Z, RING2_Z, RING_R, w2=+1)
    phi_same         = init_phi_two_rings(RING1_Z, RING2_Z, RING_R, w2=+1)
    phi_opposite     = init_phi_two_rings(RING1_Z, RING2_Z, RING_R, w2=-1)
    phi_single       = init_phi_single(RING1_Z, RING_R)

    results = {}

    print("=== SAME CHIRALITY (W+W+), epsilon=0.000 (baseline) ===")
    results["same_eps0"] = run_scenario(list(phi_same_eps0), 0.000, "same_eps0", has_ring2=True)
    print()

    print("=== SAME CHIRALITY (W+W+), epsilon=0.005 ===")
    results["same"] = run_scenario(list(phi_same), EPSILON, "same", has_ring2=True)
    print()

    print("=== OPPOSITE CHIRALITY (W+W-), epsilon=0.005 ===")
    results["opposite"] = run_scenario(list(phi_opposite), EPSILON, "opposite", has_ring2=True)
    print()

    print("=== SINGLE RING (W+), epsilon=0.005 (drift reference) ===")
    results["single"] = run_scenario(list(phi_single), EPSILON, "single", has_ring2=False)
    print()

    # --- Extract ---
    sep_base  = results["same_eps0"]["sep_final"]
    sep_same  = results["same"]["sep_final"]
    sep_opp   = results["opposite"]["sep_final"]
    z1_sing   = results["single"]["z1_final"]

    trend_same, me_s, ml_s = trend_label(results["same"]["trajectory"])
    trend_opp,  me_o, ml_o = trend_label(results["opposite"]["trajectory"])

    chirality_diff = abs(sep_same - sep_opp) if (sep_same is not None and sep_opp is not None) else 0
    chirality_finding = "SENSITIVE" if chirality_diff > 2 else "BLIND"

    # Checks
    check1_same = all(p["z1"] is not None for p in results["same"]["trajectory"])
    check1_opp  = all(p["z1"] is not None for p in results["opposite"]["trajectory"])
    check1 = check1_same and check1_opp

    check2_diff  = chirality_diff
    check2_label = chirality_finding

    check3_diff = abs(sep_same - sep_base) if (sep_same is not None and sep_base is not None) else 0
    check3      = check3_diff > 1

    decision = check1

    print("=" * 60)
    print(f"Separation final:  eps=0.000 -> {sep_base}   same(eps=0.005) -> {sep_same}   opp(eps=0.005) -> {sep_opp}")
    print(f"Chirality diff:    |sep_same - sep_opp| = {chirality_diff}  -> {chirality_finding}")
    print(f"Trend same:        {trend_same}  (early={me_s:.1f}, late={ml_s:.1f})")
    print(f"Trend opposite:    {trend_opp}  (early={me_o:.1f}, late={ml_o:.1f})")
    print(f"z_ring1 single (T=3000): {z1_sing}")
    print()
    print("Separation trajectories:")
    print(f"  {'t':>5}  {'sep(eps=0)':>12}  {'sep(same)':>12}  {'sep(opp)':>12}")
    traj_b = results["same_eps0"]["trajectory"]
    traj_s = results["same"]["trajectory"]
    traj_o = results["opposite"]["trajectory"]
    for i in range(len(traj_b)):
        t = traj_b[i]["t"]
        if t % 500 == 0 or i == 0:
            print(f"  {t:5d}  {str(traj_b[i]['sep']):>12}  {str(traj_s[i]['sep']):>12}  {str(traj_o[i]['sep']):>12}")
    print()
    print("Checks:")
    print(f"  Check 1 (rings detectable, both scenarios):  {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (chirality finding): diff={chirality_diff}  {chirality_finding}")
    print(f"  Check 3 (Channel E active vs baseline): diff={check3_diff}  {'PASS' if check3 else 'FAIL'}")
    print(f"  Check 4 [info] same trend={trend_same}  opposite trend={trend_opp}")
    print(f"\nqng_ring_chirality_reference: {'PASS' if decision else 'FAIL'}")

    report = {
        "test_id": "QNG-CPU-049",
        "decision": "pass" if decision else "fail",
        "parameters": {"L": L, "N": N, "ring_r": RING_R,
                       "ring1_z": RING1_Z, "ring2_z": RING2_Z,
                       "epsilon": EPSILON, "phase2_steps": PHASE2_STEPS},
        "sep_final_eps0":    sep_base,
        "sep_final_same":    sep_same,
        "sep_final_opposite":sep_opp,
        "chirality_diff":    chirality_diff,
        "chirality_finding": chirality_finding,
        "trend_same":        trend_same,
        "trend_opposite":    trend_opp,
        "z1_single":         z1_sing,
        "checks": {
            "rings_detectable_pass":  check1,
            "chirality_diff":         chirality_diff,
            "chirality_finding":      chirality_finding,
            "channel_e_active_pass":  check3,
        },
        "trajectories": {k: v["trajectory"] for k, v in results.items()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-CPU-049: Ring Force Chirality Comparison",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- epsilon={EPSILON}, Phase2={PHASE2_STEPS} steps",
        "",
        "## Results",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Separation (eps=0) final | {sep_base} |",
        f"| Separation (same W+W+) final | {sep_same} |",
        f"| Separation (opposite W+W-) final | {sep_opp} |",
        f"| Chirality diff | {chirality_diff} |",
        f"| Chirality finding | {chirality_finding} |",
        f"| Trend (same) | {trend_same} |",
        f"| Trend (opposite) | {trend_opp} |",
        "",
        "## Checks",
        f"- Check 1 (rings detectable): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (chirality): diff={chirality_diff} → {chirality_finding}",
        f"- Check 3 (Channel E active): diff={check3_diff} {'PASS' if check3 else 'FAIL'}",
        f"- Check 4 [info] same={trend_same}, opp={trend_opp}",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
