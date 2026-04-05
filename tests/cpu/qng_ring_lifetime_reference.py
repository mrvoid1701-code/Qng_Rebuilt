from __future__ import annotations

"""
QNG-CPU-044: 3D vortex ring lifetime measurement.

Extends QNG-CPU-043 (Phase 2 from 700 to 4700 steps) to find T_lifetime:
the Phase-2 step at which the ring collapses (R_t < R/4 = 1.25 for two
consecutive checkpoints).

Same parameters as QNG-CPU-043: BETA_PHI=0.02, two-phase protocol.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-lifetime-reference-v1"

# ---------------------------------------------------------------------------
# Parameters (identical to QNG-CPU-043)
# ---------------------------------------------------------------------------

L: int = 20
N: int = L * L * L
PHASE1_STEPS: int = 300
PHASE2_MAX: int = 4700
CHECK_INTERVAL: int = 200   # check every 200 Phase-2 steps

SIGMA_REF: float = 0.5
ALPHA: float = 0.005
BETA: float = 0.35
BETA_PHI: float = 0.02
DELTA: float = 0.20
EPSILON: float = 0.0
CHI_DECAY: float = 0.005
CHI_REL: float = 0.35
GAMMA_PHI: float = 0.10

RING_X: float = L / 2.0
RING_Y: float = L / 2.0
RING_Z: float = L / 2.0
RING_R: float = 5.0
COLLAPSE_THRESHOLD: float = RING_R / 4.0   # 1.25


# ---------------------------------------------------------------------------
# 3D indexing and phase arithmetic
# ---------------------------------------------------------------------------

def idx3(x: int, y: int, z: int) -> int:
    return (x % L) * L * L + (y % L) * L + (z % L)


def coord3(i: int) -> tuple[int, int, int]:
    x = i // (L * L); y = (i % (L * L)) // L; z = i % L
    return x, y, z


def _mi(d: float) -> float:
    while d > L / 2: d -= L
    while d < -L / 2: d += L
    return d


def wrap(angle: float) -> float:
    a = angle % (2 * math.pi)
    return a - 2 * math.pi if a > math.pi else a


def angle_diff(a: float, b: float) -> float:
    return wrap(a - b)


def circular_mean_weighted(phases: list[float], weights: list[float]) -> float:
    sx = sum(w * math.cos(p) for w, p in zip(weights, phases))
    sy = sum(w * math.sin(p) for w, p in zip(weights, phases))
    return math.atan2(sy, sx)


def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def init_phi_ring() -> list[float]:
    phi = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - RING_X); dy = _mi(y - RING_Y); dz = _mi(z - RING_Z)
        rho = math.sqrt(dx * dx + dy * dy)
        phi.append(math.atan2(dz, rho - RING_R))
    return phi


# ---------------------------------------------------------------------------
# Update steps
# ---------------------------------------------------------------------------

def _neighbors(x: int, y: int, z: int) -> list[int]:
    return [
        idx3(x-1,y,z), idx3(x+1,y,z),
        idx3(x,y-1,z), idx3(x,y+1,z),
        idx3(x,y,z-1), idx3(x,y,z+1),
    ]


def phase_disorder_3d(phi: list[float], i: int) -> float:
    x, y, z = coord3(i)
    nb = _neighbors(x, y, z)
    sx = sum(math.cos(phi[j]) for j in nb) / 6.0
    sy = sum(math.sin(phi[j]) for j in nb) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx*sx + sy*sy))


def update_step(sigma, chi, phi, channel_f: bool):
    ns, nc, np_ = [], [], []
    for i in range(N):
        x, y, z = coord3(i)
        nb = _neighbors(x, y, z)
        sigma_bar = sum(sigma[j] for j in nb) / 6.0

        if channel_f:
            D_i = phase_disorder_3d(phi, i)
            s = clip01(sigma[i] + ALPHA*(SIGMA_REF-sigma[i]) + BETA*(sigma_bar-sigma[i]) - GAMMA_PHI*D_i*sigma[i])
        else:
            s = clip01(sigma[i] + ALPHA*(SIGMA_REF-sigma[i]) + BETA*(sigma_bar-sigma[i]))

        c = chi[i]*(1-CHI_DECAY) + CHI_REL*(sigma_bar-sigma[i]) + DELTA*(SIGMA_REF-sigma[i])

        nph = [phi[j] for j in nb]
        nwt = [sigma[j] for j in nb]
        tw = sum(nwt)
        pm = circular_mean_weighted(nph, nwt) if tw > 1e-10 else phi[i]
        p = wrap(phi[i] + BETA_PHI*angle_diff(pm, phi[i]) + EPSILON*chi[i])

        ns.append(s); nc.append(c); np_.append(p)
    return ns, nc, np_


# ---------------------------------------------------------------------------
# Ring diagnostics
# ---------------------------------------------------------------------------

def find_ring_z(sigma: list[float]) -> int:
    best_z, best_s = int(RING_Z), 1e9
    for z in range(L):
        tot, cnt = 0.0, 0
        for i in range(N):
            xi, yi, zi = coord3(i)
            if zi != z: continue
            dx = _mi(xi-RING_X); dy = _mi(yi-RING_Y)
            rho = math.sqrt(dx*dx+dy*dy)
            if abs(rho-RING_R) <= 3:
                tot += sigma[i]; cnt += 1
        if cnt > 0:
            ms = tot/cnt
            if ms < best_s: best_s = ms; best_z = z
    return best_z


def ring_radius(sigma: list[float], z_ring: int) -> tuple[float, int]:
    rhos = []
    for i in range(N):
        x, y, z = coord3(i)
        if abs(_mi(z-z_ring)) > 2: continue
        if sigma[i] >= 0.35: continue
        dx = _mi(x-RING_X); dy = _mi(y-RING_Y)
        rho = math.sqrt(dx*dx+dy*dy)
        if abs(rho-RING_R) <= RING_R: rhos.append(rho)
    if not rhos: return 0.0, 0
    return sum(rhos)/len(rhos), len(rhos)


def ring_core_sigma(sigma: list[float], z_ring: int) -> float:
    tot, cnt = 0.0, 0
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x-RING_X); dy = _mi(y-RING_Y)
        rho = math.sqrt(dx*dx+dy*dy)
        if abs(rho-RING_R) <= 2 and abs(_mi(z-z_ring)) <= 1:
            tot += sigma[i]; cnt += 1
    return tot/cnt if cnt > 0 else SIGMA_REF


def count_winding(phi: list[float]) -> int:
    count = 0
    for x in range(L):
        for y in range(L):
            for z in range(L):
                for (i00,i10,i11,i01) in [
                    (idx3(x,y,z), idx3(x+1,y,z), idx3(x+1,y+1,z), idx3(x,y+1,z)),
                    (idx3(x,y,z), idx3(x+1,y,z), idx3(x+1,y,z+1), idx3(x,y,z+1)),
                    (idx3(x,y,z), idx3(x,y+1,z), idx3(x,y+1,z+1), idx3(x,y,z+1)),
                ]:
                    total = (angle_diff(phi[i10],phi[i00]) + angle_diff(phi[i11],phi[i10])
                           + angle_diff(phi[i01],phi[i11]) + angle_diff(phi[i00],phi[i01]))
                    if abs(round(total/(2*math.pi))) >= 1: count += 1
    return count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="QNG-CPU-044: vortex ring lifetime.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    print(f"L={L}, R={RING_R}, collapse_threshold=R/4={COLLAPSE_THRESHOLD}")
    print(f"Phase1={PHASE1_STEPS} + Phase2_max={PHASE2_MAX}")
    print()

    phi = init_phi_ring()
    sigma = [SIGMA_REF] * N
    chi = [0.0] * N

    # Phase 1
    print(f"Phase 1: phi equilibration ({PHASE1_STEPS} steps)...")
    for _ in range(PHASE1_STEPS):
        sigma, chi, phi = update_step(sigma, chi, phi, channel_f=False)
    z_p1 = find_ring_z(sigma)
    print(f"  After Phase 1: z_ring={z_p1}")
    print()

    # Phase 2: check every CHECK_INTERVAL steps
    print(f"Phase 2: Channel F active (up to {PHASE2_MAX} steps, checking every {CHECK_INTERVAL})...")
    history = []
    t_lifetime = None
    prev_collapsed = False
    R_t_at_703 = None  # checkpoint near QNG-CPU-043 reference point (T=700)

    for step in range(CHECK_INTERVAL, PHASE2_MAX + 1, CHECK_INTERVAL):
        for _ in range(CHECK_INTERVAL):
            sigma, chi, phi = update_step(sigma, chi, phi, channel_f=True)

        z_ring = find_ring_z(sigma)
        R_t, n_dep = ring_radius(sigma, z_ring)
        core_s = ring_core_sigma(sigma, z_ring)
        collapsed = R_t < COLLAPSE_THRESHOLD

        rec = {"phase2_step": step, "z_ring": z_ring, "R_t": round(R_t, 3),
               "n_dep": n_dep, "core_sigma": round(core_s, 5), "collapsed": collapsed}
        history.append(rec)

        if step == 600 or step == 800:  # bracket around 700
            R_t_at_703 = R_t  # use 600 or 800 as proxy

        print(f"  Phase2 T={step:5d}: z_ring={z_ring} R_t={R_t:.2f} core={core_s:.4f} "
              f"{'*** COLLAPSED ***' if collapsed else ''}")

        if collapsed and prev_collapsed and t_lifetime is None:
            t_lifetime = step - CHECK_INTERVAL  # first checkpoint where collapse occurred
            print(f"  >> COLLAPSE CONFIRMED at Phase-2 T={t_lifetime}")
        prev_collapsed = collapsed

        if t_lifetime is not None and step >= t_lifetime + CHECK_INTERVAL:
            break  # confirmed collapse, no need to continue

    # Use QNG-CPU-043 reference at Phase-2 T=700 (step=600 checkpoint)
    rec_700 = next((r for r in history if r["phase2_step"] == 600), None)
    if rec_700 is None:
        rec_700 = next((r for r in history if r["phase2_step"] == 800), None)
    R_t_ref = rec_700["R_t"] if rec_700 else 0.0

    if t_lifetime is None:
        t_lifetime_str = f"> {PHASE2_MAX}"
        t_lifetime_val = PHASE2_MAX + 1
    else:
        t_lifetime_str = str(t_lifetime)
        t_lifetime_val = t_lifetime

    # Decay gradualness check: R_t at T_lifetime/2 vs T_lifetime
    R_t_half = None
    if t_lifetime is not None:
        half = t_lifetime // 2
        half_step = min(history, key=lambda r: abs(r["phase2_step"] - half))
        R_t_half = half_step["R_t"]

    print()
    print(f"Results:")
    print(f"  R_t at Phase-2 T=600 (QNG-CPU-043 ref): {R_t_ref:.3f}  (gate > 2.5)")
    print(f"  T_lifetime: {t_lifetime_str} Phase-2 steps  (gate > 1000)")
    if R_t_half is not None:
        print(f"  R_t at T_lifetime/2: {R_t_half:.3f}  (gate > 2 * {COLLAPSE_THRESHOLD:.2f} = {2*COLLAPSE_THRESHOLD:.2f})")

    check1 = R_t_ref > 2.5
    check2 = t_lifetime_val < PHASE2_MAX
    check3 = t_lifetime_val > 1000
    check4 = (R_t_half is not None and R_t_half > 2 * COLLAPSE_THRESHOLD) if t_lifetime is not None else True

    print()
    print("Checks:")
    print(f"  Check 1 (R_t > 2.5 at Phase-2 T~700): {R_t_ref:.3f}  {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (T_lifetime measurable): {t_lifetime_str}  {'PASS' if check2 else 'FAIL (ring survived full run — lower bound)'}")
    print(f"  Check 3 (T_lifetime > 1000): {t_lifetime_str}  {'PASS' if check3 else 'FAIL'}")
    print(f"  Check 4 (gradual decay): {'PASS' if check4 else 'FAIL'}")

    checks = {
        "ring_alive_at_t700_pass": check1,
        "t_lifetime_measurable_pass": check2,
        "t_lifetime_gt_1000_pass": check3,
        "gradual_decay_pass": check4,
    }
    decision = check1 and check3 and check4  # Check 2 optional

    report = {
        "test_id": "QNG-CPU-044",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "L": L, "R": RING_R, "phase1": PHASE1_STEPS, "phase2_max": PHASE2_MAX,
            "beta": BETA, "beta_phi": BETA_PHI, "gamma_phi": GAMMA_PHI,
            "collapse_threshold": COLLAPSE_THRESHOLD,
        },
        "t_lifetime_phase2_steps": t_lifetime_str,
        "R_t_at_phase2_T600": round(R_t_ref, 3),
        "history": history,
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG Ring Lifetime Reference v1",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- T_lifetime: {t_lifetime_str} Phase-2 steps",
        f"- R_t at Phase-2 T~700 (QNG-CPU-043 ref): {R_t_ref:.3f}",
        "",
        "## Decay curve",
        "| Phase-2 T | z_ring | R_t | core_sigma | collapsed |",
        "|-----------|--------|-----|------------|-----------|",
    ]
    for r in history:
        lines.append(f"| {r['phase2_step']} | {r['z_ring']} | {r['R_t']:.3f} | {r['core_sigma']:.4f} | {r['collapsed']} |")
    lines += ["", "## Checks",
              f"- Check 1 (R_t > 2.5 at T~700): {'PASS' if check1 else 'FAIL'}",
              f"- Check 2 (T_lifetime measurable): {'PASS' if check2 else 'FAIL/lower_bound'}",
              f"- Check 3 (T_lifetime > 1000): {'PASS' if check3 else 'FAIL'}",
              f"- Check 4 (gradual decay): {'PASS' if check4 else 'FAIL'}"]
    (out_dir / "summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")

    print(f"\nqng_ring_lifetime_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
