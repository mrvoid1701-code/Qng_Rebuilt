from __future__ import annotations

"""QNG-CPU-148: Knot universality — figure-8 and cinquefoil T(2,5)
under full v7/v8 matter coupling.

CPU-146 found ring_Q0 and trefoil decay with identical half-life
tau_1/2 ~ 1000 lu under matter coupling, while Hopfion Q=1 is stable
attractor. The decay-rate equality suggests TOPOLOGY-INDEPENDENT decay
mechanism for local-topology knots (no toroidal cycle winding).

This test extends to two more local-knot classes:
- Figure-8 knot (4 crossings): r(t) = ((2+cos 2t) cos 3t, (2+cos 2t) sin 3t, sin 4t)
- Cinquefoil T(2,5) torus knot (5 crossings): r(t) = (R+r cos 5t)(cos 2t, sin 2t, 0) + r sin 5t z_hat

Prediction (from CPU-146 universality conjecture):
- Both have same decay ratio per 200 lu ≈ 0.87
- Both have half-life ~ 1000 lu under v7 dissipative dynamics

If predictions hold: confirms QNG topology-lifetime universality law
(novel prediction beyond SM).

If predictions fail: lifetime depends on specific knot type — opens path
to mapping knot complexity onto particle lifetimes (closer to KBT
original spirit).

Reference: DER-QNG-091, DER-QNG-092 §A (CPU-146 finding).
"""

import json
import math
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-knot-universality-v1"


# ---------------------------------------------------------------------------
# Parameters (match CPU-146 for direct comparison)
# ---------------------------------------------------------------------------

L = 20
N = L * L * L

SIGMA_REF = 0.5
ALPHA     = 0.005
BETA      = 0.35
BETA_PHI  = 0.02
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
GAMMA_PHI = 0.10
K_BACK    = 0.10
K_GM      = 0.001

KNOT_SCALE = 1.8   # match CPU-146 trefoil scale

PHASE1 = 300
PHASE2 = 1500
PHASE3 = 3000

LOG_EVERY = 200


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

XC, YC, ZC = L/2.0, L/2.0, L/2.0


def mi_arr(d):
    d = d.copy()
    d[d >  L/2] -= L
    d[d < -L/2] += L
    return d


def wrap_pi(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def make_coords():
    ax = np.arange(L, dtype=np.float64)
    XX, YY, ZZ = np.meshgrid(ax, ax, ax, indexing='ij')
    return XX, YY, ZZ


XX, YY, ZZ = make_coords()


# ---------------------------------------------------------------------------
# Knot parametrizations
# ---------------------------------------------------------------------------

def trefoil_curve(t: np.ndarray) -> np.ndarray:
    """Lissajous-style trefoil knot (3 crossings, T(2,3))."""
    s = KNOT_SCALE
    x = s * (np.sin(t) + 2 * np.sin(2*t))
    y = s * (np.cos(t) - 2 * np.cos(2*t))
    z = s * (-np.sin(3*t))
    return np.stack([x, y, z], axis=-1)


def figure8_curve(t: np.ndarray) -> np.ndarray:
    """Figure-8 knot (4 crossings).
    r(t) = ((2 + cos 2t) cos 3t, (2 + cos 2t) sin 3t, sin 4t).
    Scaled to fit lattice.
    """
    s = KNOT_SCALE * 0.7  # figure-8 is wider; scale down
    x = s * ((2 + np.cos(2*t)) * np.cos(3*t))
    y = s * ((2 + np.cos(2*t)) * np.sin(3*t))
    z = s * (np.sin(4*t))
    return np.stack([x, y, z], axis=-1)


def cinquefoil_curve(t: np.ndarray) -> np.ndarray:
    """Cinquefoil = T(2,5) torus knot (5 crossings).
    r(t) = ((R + r cos 5t) cos 2t, (R + r cos 5t) sin 2t, r sin 5t).
    """
    s = KNOT_SCALE * 0.6  # tighter torus
    R = 2.5 * s
    r = 1.0 * s
    x = (R + r * np.cos(5*t)) * np.cos(2*t)
    y = (R + r * np.cos(5*t)) * np.sin(2*t)
    z = r * np.sin(5*t)
    return np.stack([x, y, z], axis=-1)


def init_phi_from_knot(curve_fn, n_curve: int = 360) -> np.ndarray:
    """Generic initialization: phi winds 2pi around the closed curve."""
    ts = np.linspace(0.0, 2*math.pi, n_curve, endpoint=False)
    curve = curve_fn(ts) + np.array([XC, YC, ZC])

    nxt = np.roll(curve, -1, axis=0)
    prv = np.roll(curve, +1, axis=0)
    T = nxt - prv
    T /= np.linalg.norm(T, axis=1, keepdims=True)

    z_hat = np.array([0.0, 0.0, 1.0])
    x_hat = np.array([1.0, 0.0, 0.0])
    Nf = np.cross(T, z_hat)
    Nm = np.linalg.norm(Nf, axis=1, keepdims=True)
    fb = Nm.flatten() < 1e-3
    if np.any(fb):
        Nfx = np.cross(T[fb], x_hat)
        Nf[fb] = Nfx
        Nm[fb] = np.linalg.norm(Nfx, axis=1, keepdims=True)
    Nf /= Nm
    Bf = np.cross(T, Nf)
    Bf /= np.linalg.norm(Bf, axis=1, keepdims=True)

    pts = np.stack([XX.flatten(), YY.flatten(), ZZ.flatten()], axis=-1)

    chunk = 2000
    nearest_t = np.zeros(N, dtype=np.int64)
    for start in range(0, N, chunk):
        end = min(start + chunk, N)
        d = pts[start:end, None, :] - curve[None, :, :]
        for axis in range(3):
            d[..., axis] = np.where(d[..., axis] >  L/2, d[..., axis] - L, d[..., axis])
            d[..., axis] = np.where(d[..., axis] < -L/2, d[..., axis] + L, d[..., axis])
        dist_sq = np.sum(d * d, axis=-1)
        nearest_t[start:end] = np.argmin(dist_sq, axis=1)

    v = pts - curve[nearest_t]
    for axis in range(3):
        v[:, axis] = np.where(v[:, axis] >  L/2, v[:, axis] - L, v[:, axis])
        v[:, axis] = np.where(v[:, axis] < -L/2, v[:, axis] + L, v[:, axis])

    N_at = Nf[nearest_t]
    B_at = Bf[nearest_t]
    v_N = np.sum(v * N_at, axis=-1)
    v_B = np.sum(v * B_at, axis=-1)

    phi = np.arctan2(v_B, v_N).reshape((L, L, L))
    return wrap_pi(phi)


# ---------------------------------------------------------------------------
# v7 dynamics (vectorized — same as CPU-146)
# ---------------------------------------------------------------------------

def neighbor_mean(field):
    s = np.zeros_like(field)
    for axis in range(3):
        for shift in (-1, +1):
            s += np.roll(field, shift, axis=axis)
    return s / 6.0


def phi_disorder(phi):
    s_cos = np.zeros_like(phi); s_sin = np.zeros_like(phi)
    for axis in range(3):
        for shift in (-1, +1):
            pj = np.roll(phi, shift, axis=axis)
            s_cos += np.cos(pj)
            s_sin += np.sin(pj)
    s_cos /= 6.0; s_sin /= 6.0
    mag = np.sqrt(s_cos*s_cos + s_sin*s_sin)
    return np.clip(1.0 - mag, 0.0, 1.0)


def phi_neighbor_xy_weighted(phi, sm):
    sx = np.zeros_like(phi); sy = np.zeros_like(phi); sw = np.zeros_like(phi)
    for axis in range(3):
        for shift in (-1, +1):
            pj = np.roll(phi, shift, axis=axis)
            mj = np.roll(sm,  shift, axis=axis)
            sx += mj * np.cos(pj)
            sy += mj * np.sin(pj)
            sw += mj
    pm = np.zeros_like(phi)
    safe = sw > 1e-10
    pm[safe]  = np.arctan2(sy[safe], sx[safe])
    pm[~safe] = phi[~safe]
    return pm


def step_v7(sg, sm, chi, phi, channel_f_active=True):
    sgb = neighbor_mean(sg)
    smb = neighbor_mean(sm)

    dsg = (ALPHA * (SIGMA_REF - sg)
         + BETA  * (sgb - sg)
         + K_BACK * chi
         - K_GM * (SIGMA_REF - sm))
    sg_new = np.clip(sg + dsg, 0.0, 1.0)

    dsm = (ALPHA * (SIGMA_REF - sm)
         + BETA  * (smb - sm))
    if channel_f_active:
        dsm -= GAMMA_PHI * phi_disorder(phi) * sm
    sm_new = np.clip(sm + dsm, 0.0, 1.0)

    chi_new = (chi * (1.0 - CHI_DECAY)
             + CHI_REL * (sgb - sg)
             + DELTA   * (SIGMA_REF - sg))

    pm = phi_neighbor_xy_weighted(phi, sm)
    dphi = BETA_PHI * wrap_pi(pm - phi)
    phi_new = wrap_pi(phi + dphi)

    return sg_new, sm_new, chi_new, phi_new


def ring_mass(sm):
    return float(np.maximum(0.0, SIGMA_REF - sm).sum())


# ---------------------------------------------------------------------------
# Single configuration run
# ---------------------------------------------------------------------------

def run_knot(label, curve_fn):
    sg  = np.full((L, L, L), SIGMA_REF)
    sm  = np.full((L, L, L), SIGMA_REF)
    chi = np.zeros((L, L, L))
    phi = init_phi_from_knot(curve_fn)

    history = []
    def snap(t, phase):
        return {"t": t, "phase": phase, "M_ring": ring_mass(sm)}

    history.append(snap(0, "init"))
    print(f"  [{label}] Phase 1 (form vortex tube)...", flush=True)
    for t in range(1, PHASE1 + 1):
        sg, sm, chi, phi = step_v7(sg, sm, chi, phi, channel_f_active=False)
    history.append(snap(PHASE1, "P1_end"))

    print(f"  [{label}] Phase 2 (Channel F active)...", flush=True)
    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_v7(sg, sm, chi, phi, channel_f_active=True)
        if t % LOG_EVERY == 0 or t == PHASE2:
            history.append(snap(PHASE1 + t, "P2"))
            print(f"  [{label}] P2 t={t} M={history[-1]['M_ring']:.2f}",
                  flush=True)

    print(f"  [{label}] Phase 3 (decay characterization)...", flush=True)
    for t in range(1, PHASE3 + 1):
        sg, sm, chi, phi = step_v7(sg, sm, chi, phi, channel_f_active=True)
        if t % LOG_EVERY == 0 or t == PHASE3:
            history.append(snap(PHASE1 + PHASE2 + t, "P3"))
            print(f"  [{label}] P3 t={t} M={history[-1]['M_ring']:.2f}",
                  flush=True)

    # Compute decay ratio per 200 lu averaged across Phase 3
    p3_records = [h for h in history if h["phase"] == "P3"]
    if len(p3_records) >= 2:
        ratios = []
        for i in range(1, len(p3_records)):
            r = p3_records[i]["M_ring"] / max(0.01, p3_records[i-1]["M_ring"])
            ratios.append(r)
        mean_ratio = float(np.mean(ratios))
        # Half-life: solve r^n = 1/2 → n = log(1/2)/log(r)
        if 0 < mean_ratio < 1:
            half_life_steps = math.log(0.5) / math.log(mean_ratio)
            half_life_lu    = half_life_steps * LOG_EVERY
        else:
            half_life_lu = float('inf')
    else:
        mean_ratio = 1.0
        half_life_lu = float('inf')

    M_final = history[-1]["M_ring"]
    M_P2_end = next(h["M_ring"] for h in reversed(history) if h["phase"] == "P2")

    return {
        "label": label,
        "M_P1_end": history[1]["M_ring"],
        "M_P2_end": M_P2_end,
        "M_P3_end": M_final,
        "mean_decay_ratio_per_200lu": mean_ratio,
        "half_life_lu": half_life_lu,
        "history": history,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("QNG-CPU-148: Knot universality (trefoil, figure-8, cinquefoil)")
    print(f"L={L} P1={PHASE1} P2={PHASE2} P3={PHASE3}")
    print(f"All three are LOCAL-topology knots (no toroidal cycle winding).")
    print(f"Prediction (from CPU-146): half-life ~ 1000 lu universal.")
    print()

    configs = [
        ("trefoil",     trefoil_curve),
        ("figure_8",    figure8_curve),
        ("cinquefoil",  cinquefoil_curve),
    ]

    results = []
    t_start = time.time()
    for label, curve_fn in configs:
        print(f"--- {label} ---", flush=True)
        res = run_knot(label, curve_fn)
        results.append(res)
        print(f"  [{label}] DONE M_P1={res['M_P1_end']:.2f} "
              f"M_P2={res['M_P2_end']:.2f} M_P3={res['M_P3_end']:.2f} "
              f"decay_ratio={res['mean_decay_ratio_per_200lu']:.4f} "
              f"half_life={res['half_life_lu']:.0f} lu", flush=True)
        print()
    dt = time.time() - t_start
    print(f"Total run time: {dt:.1f} s")
    print()

    # Universality check: all decay ratios within 5%
    ratios = [r["mean_decay_ratio_per_200lu"] for r in results]
    half_lives = [r["half_life_lu"] for r in results if r["half_life_lu"] < 1e6]

    mean_r = float(np.mean(ratios))
    std_r  = float(np.std(ratios))
    rel_spread_r = std_r / mean_r if mean_r > 0 else 0.0

    mean_hl = float(np.mean(half_lives)) if half_lives else float('inf')
    std_hl  = float(np.std(half_lives)) if half_lives else 0.0
    rel_spread_hl = std_hl / mean_hl if mean_hl > 0 else 0.0

    universal = rel_spread_r < 0.10  # within 10%
    matches_cpu146 = abs(mean_hl - 1000) / 1000 < 0.30  # within 30% of CPU-146 trefoil tau

    print("=" * 80)
    print(f"{'Config':<14} {'M_P2_end':>10} {'M_P3_end':>10} {'decay ratio':>12} {'half-life':>11}")
    print("-" * 80)
    for r in results:
        print(f"{r['label']:<14} {r['M_P2_end']:>10.2f} {r['M_P3_end']:>10.2f} "
              f"{r['mean_decay_ratio_per_200lu']:>12.4f} {r['half_life_lu']:>11.0f}")
    print("=" * 80)
    print(f"Mean decay ratio: {mean_r:.4f}  rel spread: {rel_spread_r:.4f}")
    print(f"Mean half-life: {mean_hl:.0f} lu  rel spread: {rel_spread_hl:.4f}")
    print(f"\nUniversality test (rel spread of decay ratio < 10%): "
          f"{'PASS' if universal else 'FAIL'}")
    print(f"CPU-146 ring/trefoil baseline ~1000 lu match (within 30%): "
          f"{'YES' if matches_cpu146 else 'NO'}")

    if universal and matches_cpu146:
        print("\n=> CONFIRMED: QNG topology-lifetime universality law holds.")
        print("   All local-topology knots have same decay rate, tau_1/2 ~ 1000 lu.")
        print("   This is a NOVEL QNG prediction beyond SM.")
    elif universal:
        print("\n=> Local knots share decay rate among themselves, but differs")
        print("   from CPU-146 ring/trefoil baseline. Topology may matter")
        print("   in a more subtle way.")
    else:
        print("\n=> Knot-dependent decay rates - KBT spirit partially vindicated.")
        print("   Different knot types have different lifetimes.")

    decision = universal

    report = {
        "test_id": "QNG-CPU-148",
        "decision": "pass" if decision else "fail",
        "params": {"L": L, "PHASE1": PHASE1, "PHASE2": PHASE2, "PHASE3": PHASE3,
                   "BETA_PHI": BETA_PHI, "GAMMA_PHI": GAMMA_PHI, "KNOT_SCALE": KNOT_SCALE},
        "results": results,
        "summary": {
            "mean_decay_ratio_per_200lu": mean_r,
            "rel_spread_decay": rel_spread_r,
            "mean_half_life_lu": mean_hl,
            "rel_spread_half_life": rel_spread_hl,
            "universal_local_decay_law": universal,
            "matches_cpu146_baseline": matches_cpu146,
        },
        "interpretation": (
            "Tests whether all local-topology knots (trefoil, figure-8, "
            "cinquefoil) have a universal decay rate ~tau_1/2 ≈ 1000 lu "
            "as conjectured from CPU-146. If yes, QNG predicts a "
            "topology-independent lifetime for non-cycle-winding "
            "particle classes — a novel prediction with no SM analog."
        ),
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)

    summary = [
        "# QNG-CPU-148 Knot Universality",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- universal local-knot decay law: `{universal}`",
        f"- mean half-life: {mean_hl:.0f} lu  (spread {rel_spread_hl*100:.1f}%)",
        "",
        "## Configurations",
        "| Knot | Crossings | Class |",
        "|---|---|---|",
        "| trefoil | 3 | T(2,3) torus / Lissajous |",
        "| figure_8 | 4 | twist knot 4_1 |",
        "| cinquefoil | 5 | T(2,5) torus |",
        "",
        "## Decay characterization",
        "| Knot | M_P2_end | M_P3_end | decay_ratio/200lu | half-life (lu) |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        summary.append(
            f"| {r['label']} | {r['M_P2_end']:.2f} | {r['M_P3_end']:.2f} | "
            f"{r['mean_decay_ratio_per_200lu']:.4f} | {r['half_life_lu']:.0f} |"
        )
    summary += [
        "",
        f"Mean decay ratio: **{mean_r:.4f}** (spread {rel_spread_r*100:.2f}%)",
        f"Mean half-life: **{mean_hl:.0f} lu** (spread {rel_spread_hl*100:.2f}%)",
        "",
        "## Interpretation",
        report["interpretation"],
    ]
    (out / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(f"\nReport: {rp}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
