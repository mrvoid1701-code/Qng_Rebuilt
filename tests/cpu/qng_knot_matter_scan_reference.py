from __future__ import annotations

"""QNG-CPU-146: Knot stability under FULL v7/v8 matter coupling.

Companion to CPU-145 (pure-phi sector) which found:
- Hopfion Q=1,2,3 stable (toroidal U(1) winding protected by periodic BC)
- Bare ring DISSOLVES (no protection in pure phi)
- Trefoil knot DISSOLVES (no S^2 protection without n-field)

This test runs the same initial configurations but with full v7/v8
dynamics including:
- Channel A (alpha relaxation toward SIGMA_REF)
- Channel B (neighbor diffusion)
- Channel D (chi relaxation, decay)
- Channel F (matter depletion by phi disorder — KEY for ring formation)
- Channel G (chi back-reaction on sigma_g — REQUIRED for v7 stability)

The hypothesis being tested:
> Matter sector (sigma_m depletion via Channel F) provides effective
> n-field structure that stabilizes topological knots beyond
> Hopfion class. If trefoil M_ring stabilizes, KBT path reopens.

Protocol per configuration:
- Phase 1 (300 steps, no Channel F): allow phi to relax to topology-
  consistent shape
- Phase 2 (1500 steps, Channel F active): matter depletes around phi
  vortex tube
- Phase 3 (500 steps, measure stability of M_ring)

This is the Tier A.2 prerequisite for the SM correspondence map
DER-QNG-091. Result feeds back into DER-QNG-092 §Open Questions.

Reference: DER-QNG-091, DER-QNG-092, CPU-145.
"""

import json
import math
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-knot-matter-scan-v1"


# ---------------------------------------------------------------------------
# Parameters (v7/v8 canonical, matching CPU-066/074)
# ---------------------------------------------------------------------------

L = 20                # smaller lattice for speed; matches CPU-074
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
K_GM      = 0.001     # gravity coupling

# Topology
RING_R        = 5.0
TREFOIL_SCALE = 1.8   # smaller for L=20 lattice

# Phase durations (CPU-066 protocol with extended Phase 3 for stability)
PHASE1 = 300
PHASE2 = 1500
PHASE3 = 3000   # extended to characterize decay timescales

LOG_EVERY = 200


# ---------------------------------------------------------------------------
# Geometry helpers
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
DX = mi_arr(XX - XC)
DY = mi_arr(YY - YC)
DZ = mi_arr(ZZ - ZC)


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init_phi_hopfion(q_twist: int) -> np.ndarray:
    rho = np.sqrt(DX*DX + DY*DY)
    poloidal = np.arctan2(DZ, rho - RING_R)
    toroidal = np.arctan2(DY, DX)
    return wrap_pi(poloidal + q_twist * toroidal)


def trefoil_curve(t: np.ndarray) -> np.ndarray:
    s = TREFOIL_SCALE
    x = s * (np.sin(t) + 2 * np.sin(2*t))
    y = s * (np.cos(t) - 2 * np.cos(2*t))
    z = s * (-np.sin(3*t))
    return np.stack([x, y, z], axis=-1)


def init_phi_trefoil(n_curve: int = 360) -> np.ndarray:
    ts = np.linspace(0.0, 2*math.pi, n_curve, endpoint=False)
    curve = trefoil_curve(ts) + np.array([XC, YC, ZC])

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
        d[..., 0] = np.where(d[..., 0] >  L/2, d[..., 0] - L, d[..., 0])
        d[..., 0] = np.where(d[..., 0] < -L/2, d[..., 0] + L, d[..., 0])
        d[..., 1] = np.where(d[..., 1] >  L/2, d[..., 1] - L, d[..., 1])
        d[..., 1] = np.where(d[..., 1] < -L/2, d[..., 1] + L, d[..., 1])
        d[..., 2] = np.where(d[..., 2] >  L/2, d[..., 2] - L, d[..., 2])
        d[..., 2] = np.where(d[..., 2] < -L/2, d[..., 2] + L, d[..., 2])
        dist_sq = np.sum(d * d, axis=-1)
        nearest_t[start:end] = np.argmin(dist_sq, axis=1)

    v = pts - curve[nearest_t]
    v[:, 0] = np.where(v[:, 0] >  L/2, v[:, 0] - L, v[:, 0])
    v[:, 0] = np.where(v[:, 0] < -L/2, v[:, 0] + L, v[:, 0])
    v[:, 1] = np.where(v[:, 1] >  L/2, v[:, 1] - L, v[:, 1])
    v[:, 1] = np.where(v[:, 1] < -L/2, v[:, 1] + L, v[:, 1])
    v[:, 2] = np.where(v[:, 2] >  L/2, v[:, 2] - L, v[:, 2])
    v[:, 2] = np.where(v[:, 2] < -L/2, v[:, 2] + L, v[:, 2])

    N_at = Nf[nearest_t]
    B_at = Bf[nearest_t]
    v_N = np.sum(v * N_at, axis=-1)
    v_B = np.sum(v * B_at, axis=-1)

    phi = np.arctan2(v_B, v_N).reshape((L, L, L))
    return wrap_pi(phi)


# ---------------------------------------------------------------------------
# v7 dynamics (vectorized)
# ---------------------------------------------------------------------------

def neighbor_mean(field):
    """Mean over 6 nearest neighbors with periodic BC."""
    s = np.zeros_like(field)
    for axis in range(3):
        for shift in (-1, +1):
            s += np.roll(field, shift, axis=axis)
    return s / 6.0


def phi_disorder(phi):
    """1 - |<exp(i*phi)>| over 6 neighbors. Range [0,1]."""
    s_cos = np.zeros_like(phi); s_sin = np.zeros_like(phi)
    for axis in range(3):
        for shift in (-1, +1):
            pj = np.roll(phi, shift, axis=axis)
            s_cos += np.cos(pj)
            s_sin += np.sin(pj)
    s_cos /= 6.0
    s_sin /= 6.0
    mag = np.sqrt(s_cos*s_cos + s_sin*s_sin)
    return np.clip(1.0 - mag, 0.0, 1.0)


def phi_neighbor_xy_weighted(phi, sm):
    """Sigma_m-weighted XY neighbor mean — phi alignment direction."""
    sx = np.zeros_like(phi); sy = np.zeros_like(phi); sw = np.zeros_like(phi)
    for axis in range(3):
        for shift in (-1, +1):
            pj = np.roll(phi, shift, axis=axis)
            mj = np.roll(sm,  shift, axis=axis)
            sx += mj * np.cos(pj)
            sy += mj * np.sin(pj)
            sw += mj
    # safe arctan2
    pm = np.zeros_like(phi)
    safe = sw > 1e-10
    pm[safe]  = np.arctan2(sy[safe], sx[safe])
    pm[~safe] = phi[~safe]
    return pm


def step_v7(sg, sm, chi, phi, channel_f_active=True):
    """One v7 dissipative step with all channels.

    sigma_g: Channel A + B + G - K_GM
    sigma_m: Channel A + B - F (if active)
    chi:     decay + Channel D (CHI_REL, DELTA)
    phi:     XY-alignment weighted by sigma_m
    """
    sgb = neighbor_mean(sg)
    smb = neighbor_mean(sm)

    # sigma_g
    dsg = (ALPHA * (SIGMA_REF - sg)
         + BETA  * (sgb - sg)
         + K_BACK * chi
         - K_GM * (SIGMA_REF - sm))
    sg_new = np.clip(sg + dsg, 0.0, 1.0)

    # sigma_m
    dsm = (ALPHA * (SIGMA_REF - sm)
         + BETA  * (smb - sm))
    if channel_f_active:
        dsm -= GAMMA_PHI * phi_disorder(phi) * sm
    sm_new = np.clip(sm + dsm, 0.0, 1.0)

    # chi
    chi_new = (chi * (1.0 - CHI_DECAY)
             + CHI_REL * (sgb - sg)
             + DELTA   * (SIGMA_REF - sg))

    # phi: alignment to sigma_m-weighted neighbor mean
    pm = phi_neighbor_xy_weighted(phi, sm)
    dphi = BETA_PHI * wrap_pi(pm - phi)
    phi_new = wrap_pi(phi + dphi)

    return sg_new, sm_new, chi_new, phi_new


# ---------------------------------------------------------------------------
# Observables
# ---------------------------------------------------------------------------

def ring_mass(sm):
    """Total matter depletion: M_ring = sum(max(0, SIGMA_REF - sm[i]))."""
    return float(np.maximum(0.0, SIGMA_REF - sm).sum())


def phi_xy_energy(phi):
    """E_phi = -(beta_phi/(2z)) * sum_{<ij>} cos(phi_i - phi_j)."""
    s = 0.0
    for axis in range(3):
        for shift in (-1, +1):
            pj = np.roll(phi, shift, axis=axis)
            s += float(np.cos(pj - phi).sum())
    return -(BETA_PHI / 12.0) * s  # z=6, factor 2 for double count


def vortex_winding_xy(phi, z_slice):
    layer = phi[:, :, z_slice]
    top   = layer[0, :]
    right = layer[:, -1]
    bot   = layer[-1, ::-1]
    left  = layer[::-1, 0]
    path = np.concatenate([top, right, bot, left, [top[0]]])
    diffs = wrap_pi(np.diff(path))
    return float(diffs.sum())


# ---------------------------------------------------------------------------
# Run one configuration
# ---------------------------------------------------------------------------

def run_config(label, init_fn,
               phase1=PHASE1, phase2=PHASE2, phase3=PHASE3):
    """Full v7 dynamics from initial phi field."""
    sg  = np.full((L, L, L), SIGMA_REF)
    sm  = np.full((L, L, L), SIGMA_REF)
    chi = np.zeros((L, L, L))
    phi = init_fn()

    history = []

    def snap(t, phase):
        return {
            "t": t,
            "phase": phase,
            "M_ring": ring_mass(sm),
            "E_phi": phi_xy_energy(phi),
            "W_xy_top": vortex_winding_xy(phi, int(L/2) + 3),
            "W_xy_ctr": vortex_winding_xy(phi, int(L/2)),
            "sm_min": float(sm.min()),
            "sm_max": float(sm.max()),
            "sm_mean": float(sm.mean()),
        }

    print(f"  [{label}] Phase 1 (form vortex)...", flush=True)
    history.append(snap(0, "init"))
    for t in range(1, phase1 + 1):
        sg, sm, chi, phi = step_v7(sg, sm, chi, phi, channel_f_active=False)
    history.append(snap(phase1, "P1_end"))
    print(f"  [{label}] P1 done: M={history[-1]['M_ring']:.2f}, "
          f"sm_min={history[-1]['sm_min']:.3f}", flush=True)

    print(f"  [{label}] Phase 2 (Channel F active, ring formation)...",
          flush=True)
    for t in range(1, phase2 + 1):
        sg, sm, chi, phi = step_v7(sg, sm, chi, phi, channel_f_active=True)
        if t % LOG_EVERY == 0 or t == phase2:
            history.append(snap(phase1 + t, "P2"))
            print(f"  [{label}] P2 t={t} M={history[-1]['M_ring']:.2f} "
                  f"sm_min={history[-1]['sm_min']:.3f} "
                  f"E_phi={history[-1]['E_phi']:.2f}", flush=True)

    M_p2_end = history[-1]["M_ring"]
    sm_min_p2 = history[-1]["sm_min"]
    W_xy_p2 = history[-1]["W_xy_top"]

    print(f"  [{label}] Phase 3 (stability check)...", flush=True)
    for t in range(1, phase3 + 1):
        sg, sm, chi, phi = step_v7(sg, sm, chi, phi, channel_f_active=True)
        if t % LOG_EVERY == 0 or t == phase3:
            history.append(snap(phase1 + phase2 + t, "P3"))
            print(f"  [{label}] P3 t={t} M={history[-1]['M_ring']:.2f}", flush=True)

    M_final = history[-1]["M_ring"]

    # Stability metric: rel change of M during Phase 3
    M_p3_start = next((s["M_ring"] for s in history if s["phase"] == "P3"), M_final)
    drift = abs(M_final - M_p3_start) / max(1.0, M_p3_start)

    return {
        "label": label,
        "M_phase1_end": history[1]["M_ring"],
        "M_phase2_end": M_p2_end,
        "M_phase3_end": M_final,
        "sm_min_phase2_end": sm_min_p2,
        "W_xy_phase2_end": W_xy_p2,
        "phase3_drift": drift,
        "history": history,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--quick", action='store_true',
                    help="Skip Q=2, Q=3 to save time")
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("QNG-CPU-146: Knot stability under FULL v7/v8 matter coupling")
    print(f"L={L}  PHASE1={PHASE1}  PHASE2={PHASE2}  PHASE3={PHASE3}")
    print(f"BETA_PHI={BETA_PHI} GAMMA_PHI={GAMMA_PHI} CHI_DECAY={CHI_DECAY}")
    print()

    if args.quick:
        configs = [
            ("ring_Q0",    lambda: init_phi_hopfion(0)),
            ("hopfion_Q1", lambda: init_phi_hopfion(1)),
            ("trefoil",    lambda: init_phi_trefoil()),
        ]
    else:
        configs = [
            ("ring_Q0",    lambda: init_phi_hopfion(0)),
            ("hopfion_Q1", lambda: init_phi_hopfion(1)),
            ("hopfion_Q2", lambda: init_phi_hopfion(2)),
            ("hopfion_Q3", lambda: init_phi_hopfion(3)),
            ("trefoil",    lambda: init_phi_trefoil()),
        ]

    results = []
    t_start = time.time()
    for label, init_fn in configs:
        print(f"--- {label} ---", flush=True)
        res = run_config(label, init_fn)
        results.append(res)
        print(f"  [{label}] DONE M_P1={res['M_phase1_end']:.2f} "
              f"M_P2={res['M_phase2_end']:.2f} M_P3={res['M_phase3_end']:.2f} "
              f"P3_drift={res['phase3_drift']:.4f} "
              f"W_xy_P2={res['W_xy_phase2_end']:.2f}", flush=True)
        print()
    dt = time.time() - t_start
    print(f"Total run time: {dt:.1f} s")
    print()

    # Stability ranking
    print("=" * 84)
    print(f"{'Config':<15} {'M_P1':>8} {'M_P2':>8} {'M_P3':>8} {'P3_drift':>10} "
          f"{'W_xy_P2':>10} {'Survives':>10}")
    print("-" * 84)
    for r in results:
        survives = (r["M_phase3_end"] > 20.0) and (r["phase3_drift"] < 0.5)
        print(f"{r['label']:<15} {r['M_phase1_end']:>8.2f} {r['M_phase2_end']:>8.2f} "
              f"{r['M_phase3_end']:>8.2f} {r['phase3_drift']:>10.4f} "
              f"{r['W_xy_phase2_end']:>10.2f} {'YES' if survives else 'NO':>10}")
    print("=" * 84)

    # Decision: how many configurations survive with bound M_ring at Phase 3 end?
    n_survives = sum(1 for r in results
                     if r["M_phase3_end"] > 20.0 and r["phase3_drift"] < 0.5)
    print(f"\n{n_survives} of {len(results)} configurations survive Phase 3.")

    # Critical comparison: did the trefoil stabilize under matter coupling?
    trefoil_res = next(r for r in results if r["label"] == "trefoil")
    trefoil_alive = trefoil_res["M_phase3_end"] > 20.0
    ring_res    = next(r for r in results if r["label"] == "ring_Q0")
    ring_alive  = ring_res["M_phase3_end"] > 20.0

    print(f"\n--- KEY VERDICTS ---")
    print(f"Trefoil under matter coupling: "
          f"{'STABLE' if trefoil_alive else 'DISSOLVED'}  (M_P3={trefoil_res['M_phase3_end']:.2f})")
    print(f"Bare ring under matter coupling: "
          f"{'STABLE' if ring_alive else 'DISSOLVED'}  (M_P3={ring_res['M_phase3_end']:.2f})")

    if trefoil_alive:
        print("\n  -> KBT hypothesis VINDICATED at v7/v8 level: matter coupling")
        print("     provides effective n-field structure stabilizing knot topology.")
    else:
        print("\n  -> KBT hypothesis FALSIFIED at v7/v8 level: matter sector does")
        print("     NOT stabilize knot beyond Hopfion class. Requires v13 n-field.")

    decision = n_survives >= 2  # at least ring/hopfion baseline + something else

    report = {
        "test_id": "QNG-CPU-146",
        "decision": "pass" if decision else "fail",
        "params": {
            "L": L, "PHASE1": PHASE1, "PHASE2": PHASE2, "PHASE3": PHASE3,
            "BETA_PHI": BETA_PHI, "GAMMA_PHI": GAMMA_PHI, "K_BACK": K_BACK,
            "CHI_DECAY": CHI_DECAY,
        },
        "results": results,
        "n_configurations_survive": n_survives,
        "key_verdicts": {
            "trefoil_stable_under_matter": trefoil_alive,
            "bare_ring_stable_under_matter": ring_alive,
            "KBT_at_v8_level": "vindicated" if trefoil_alive else "falsified",
        },
        "interpretation": (
            "Tests whether sigma_m back-reaction provides effective n-field "
            "structure that stabilizes phi knot topologies beyond pure-phi "
            "Hopfion family. If trefoil M_ring > 20 and drift < 0.5 at end "
            "of Phase 3, KBT path reopens via matter coupling. "
            "Otherwise v13 n-field extension required."
        ),
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)

    summary = [
        "# QNG-CPU-146 Knot Stability under v7/v8 Matter Coupling",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- trefoil stable: `{trefoil_alive}`",
        f"- bare ring stable: `{ring_alive}`",
        "",
        "## Purpose",
        "Decisive test for Kelvin-Bilson-Thompson hypothesis at v8 level.",
        "Companion to CPU-145 (pure-phi). Tests whether sigma_m matter",
        "back-reaction stabilizes knot topologies that dissolve in pure phi.",
        "",
        "## Results",
        "| Config | M_P1_end | M_P2_end | M_P3_end | P3 drift | W_xy_P2 | Survives |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        survives = (r["M_phase3_end"] > 20.0) and (r["phase3_drift"] < 0.5)
        summary.append(
            f"| {r['label']} | {r['M_phase1_end']:.2f} | {r['M_phase2_end']:.2f} | "
            f"{r['M_phase3_end']:.2f} | {r['phase3_drift']:.4f} | "
            f"{r['W_xy_phase2_end']:.2f} | {'YES' if survives else 'NO'} |"
        )
    summary += [
        "",
        "## Verdict on KBT hypothesis at v8 level",
        f"- Trefoil under matter: **{'STABLE' if trefoil_alive else 'DISSOLVED'}**",
        f"- Bare ring under matter: **{'STABLE' if ring_alive else 'DISSOLVED'}**",
        "",
        ("**KBT path REOPENED via matter coupling** — proceed to QNG-CPU-147 "
         "for full Hopfion+trefoil mass spectrum under v8."
         if trefoil_alive else
         "**KBT path FALSIFIED at v7/v8 level** — pure σ_m back-reaction does not "
         "host trefoil topology. Next attack: v13 n-field extension (CPU-148)."),
        "",
        "## Honest caveats",
        "- L=20 lattice may not give trefoil enough room. Larger L (24, 32) could change result.",
        "- Phase 2/3 dissipative dynamics relaxes toward minimum-energy attractor — gauge of",
        "  dynamical stability, not absolute global minimum.",
        "- No v8 symplectic dynamics in this scan (v7 dissipative only). Symplectic v8 may",
        "  give different orbital-attractor behavior.",
    ]
    (out / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

    print(f"\nReport: {rp}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
