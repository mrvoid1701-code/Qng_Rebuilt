from __future__ import annotations

"""QNG-CPU-152: Full v12 EM dynamics — confirm CPU-151 topology-dependent decay prediction.

CPU-151 computed static plaquette curls for various knot configurations
and predicted that under v12 with dynamic A_ij gauge field:
- Ring (lowest E_gauge) has slowest decay
- Cinquefoil (highest E_gauge) has fastest decay
- Spread factor 2.5 across knot types
- Hopfion Q=1 saturates with Q=2 (~1% E_gauge agreement)

CPU-152 implements the full v12 dynamics:
- All v7 sectors (sigma_g, sigma_m, chi, phi) with matter coupling
- Added: edge gauge field A_ij with Maxwell plaquette term
- phi update uses gauge-invariant phase: phi_i - phi_j - e*A_ij
- A_ij dynamics: gradient flow including Maxwell curvature + phi coupling

Goal: measure decay timescale of M_ring for each knot under full v12
and confirm/refute the static-curl prediction of factor 2.5 spread.

Reference: DER-QNG-076 (v12 EM), DER-QNG-092 §F (CPU-151).
"""

import json
import math
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-v12-dynamics-v1"


# ---------------------------------------------------------------------------
# Parameters
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

# v12 EM parameters (canonical)
# DER-QNG-076: e ~ 0.3 (QED analog), mu_A = z*mu_phi/beta_phi.
# v7 has no explicit mu_phi; we set mu_A=1.0 as a reasonable substitute.
# BETA_A constrained by stability: BETA_A < 2*mu_A/k_max^2 ~ 0.2 for L=20.
E_CHARGE = 0.3
MU_A     = 1.0
BETA_A   = 0.05
Z_NB     = 6

# Topology
RING_R        = 5.0
KNOT_SCALE    = 1.8

# Phases
PHASE1 = 300
PHASE2 = 1500
PHASE3 = 3000
LOG_EVERY = 200


# ---------------------------------------------------------------------------
# Lattice geometry
# ---------------------------------------------------------------------------

XC, YC, ZC = L/2.0, L/2.0, L/2.0


def wrap_pi(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def mi_arr(d):
    d = d.copy()
    d[d >  L/2] -= L
    d[d < -L/2] += L
    return d


def make_coords():
    ax = np.arange(L, dtype=np.float64)
    XX, YY, ZZ = np.meshgrid(ax, ax, ax, indexing='ij')
    return XX, YY, ZZ


XX, YY, ZZ = make_coords()
DX = mi_arr(XX - XC)
DY = mi_arr(YY - YC)
DZ = mi_arr(ZZ - ZC)


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def init_phi_hopfion(q_twist: int) -> np.ndarray:
    rho = np.sqrt(DX*DX + DY*DY)
    poloidal = np.arctan2(DZ, rho - RING_R)
    toroidal = np.arctan2(DY, DX)
    return wrap_pi(poloidal + q_twist * toroidal)


def trefoil_curve(t):
    s = KNOT_SCALE
    return np.stack([
        s * (np.sin(t) + 2 * np.sin(2*t)),
        s * (np.cos(t) - 2 * np.cos(2*t)),
        s * (-np.sin(3*t)),
    ], axis=-1)


def figure8_curve(t):
    s = KNOT_SCALE * 0.7
    return np.stack([
        s * ((2 + np.cos(2*t)) * np.cos(3*t)),
        s * ((2 + np.cos(2*t)) * np.sin(3*t)),
        s * (np.sin(4*t)),
    ], axis=-1)


def cinquefoil_curve(t):
    s = KNOT_SCALE * 0.6
    R = 2.5 * s
    r = 1.0 * s
    return np.stack([
        (R + r * np.cos(5*t)) * np.cos(2*t),
        (R + r * np.cos(5*t)) * np.sin(2*t),
        r * np.sin(5*t),
    ], axis=-1)


def init_phi_from_knot(curve_fn, n_curve=360):
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
        for ax in range(3):
            d[..., ax] = np.where(d[..., ax] >  L/2, d[..., ax] - L, d[..., ax])
            d[..., ax] = np.where(d[..., ax] < -L/2, d[..., ax] + L, d[..., ax])
        nearest_t[start:end] = np.argmin(np.sum(d*d, axis=-1), axis=1)
    v = pts - curve[nearest_t]
    for ax in range(3):
        v[:, ax] = np.where(v[:, ax] >  L/2, v[:, ax] - L, v[:, ax])
        v[:, ax] = np.where(v[:, ax] < -L/2, v[:, ax] + L, v[:, ax])
    N_at = Nf[nearest_t]
    B_at = Bf[nearest_t]
    v_N = np.sum(v * N_at, axis=-1)
    v_B = np.sum(v * B_at, axis=-1)
    return wrap_pi(np.arctan2(v_B, v_N).reshape((L, L, L)))


# ---------------------------------------------------------------------------
# v12 dynamics
# ---------------------------------------------------------------------------

def neighbor_mean(field):
    s = np.zeros_like(field)
    for axis in range(3):
        for shift in (-1, +1):
            s += np.roll(field, shift, axis=axis)
    return s / 6.0


def phi_neighbor_xy_weighted_gauge(phi, sm, A_x, A_y, A_z):
    """Sigma_m-weighted XY-like neighbor mean — phi alignment direction
    with gauge correction phi_j -> phi_j + e*A_ij.

    For each edge from node i to node j (j is +x, +y, +z or -x, -y, -z
    neighbor), the gauge-invariant "neighbor phi" seen by i is:
        phi_j + e * A_ij  (i.e., subtract gauge field connecting i to j)
    Wait, actually: cos(phi_i - phi_j - e*A_ij) means phi_j appears with
    +e*A_ij. So when computing the angle that minimizes (phi_i - target)^2
    in the cos energy, the "target" is phi_j + e*A_ij.
    For i looking at its neighbor j at +x: target = phi[i+1,j,k] + e*A_x[i,j,k]
    For i looking at its neighbor j at -x: target = phi[i-1,j,k] - e*A_x[i-1,j,k]
    """
    sx = np.zeros_like(phi); sy = np.zeros_like(phi); sw = np.zeros_like(phi)

    # +x neighbor: phi[i+1] + e*A_x[i]
    pj_px = np.roll(phi, -1, axis=0) + E_CHARGE * A_x
    mj_px = np.roll(sm,  -1, axis=0)
    sx += mj_px * np.cos(pj_px); sy += mj_px * np.sin(pj_px); sw += mj_px
    # -x neighbor: phi[i-1] - e*A_x[i-1]
    pj_mx = np.roll(phi, +1, axis=0) - E_CHARGE * np.roll(A_x, +1, axis=0)
    mj_mx = np.roll(sm,  +1, axis=0)
    sx += mj_mx * np.cos(pj_mx); sy += mj_mx * np.sin(pj_mx); sw += mj_mx
    # +y neighbor
    pj_py = np.roll(phi, -1, axis=1) + E_CHARGE * A_y
    mj_py = np.roll(sm,  -1, axis=1)
    sx += mj_py * np.cos(pj_py); sy += mj_py * np.sin(pj_py); sw += mj_py
    # -y neighbor
    pj_my = np.roll(phi, +1, axis=1) - E_CHARGE * np.roll(A_y, +1, axis=1)
    mj_my = np.roll(sm,  +1, axis=1)
    sx += mj_my * np.cos(pj_my); sy += mj_my * np.sin(pj_my); sw += mj_my
    # +z neighbor
    pj_pz = np.roll(phi, -1, axis=2) + E_CHARGE * A_z
    mj_pz = np.roll(sm,  -1, axis=2)
    sx += mj_pz * np.cos(pj_pz); sy += mj_pz * np.sin(pj_pz); sw += mj_pz
    # -z neighbor
    pj_mz = np.roll(phi, +1, axis=2) - E_CHARGE * np.roll(A_z, +1, axis=2)
    mj_mz = np.roll(sm,  +1, axis=2)
    sx += mj_mz * np.cos(pj_mz); sy += mj_mz * np.sin(pj_mz); sw += mj_mz

    pm = np.zeros_like(phi)
    safe = sw > 1e-10
    pm[safe]  = np.arctan2(sy[safe], sx[safe])
    pm[~safe] = phi[~safe]
    return pm


def phi_disorder_gauge(phi, A_x, A_y, A_z):
    """Gauge-invariant phi disorder: 1 - |<exp(i * gauge_phi_neighbor)>|"""
    s_cos = np.zeros_like(phi); s_sin = np.zeros_like(phi)

    pj = np.roll(phi, -1, axis=0) + E_CHARGE * A_x
    s_cos += np.cos(pj); s_sin += np.sin(pj)
    pj = np.roll(phi, +1, axis=0) - E_CHARGE * np.roll(A_x, +1, axis=0)
    s_cos += np.cos(pj); s_sin += np.sin(pj)
    pj = np.roll(phi, -1, axis=1) + E_CHARGE * A_y
    s_cos += np.cos(pj); s_sin += np.sin(pj)
    pj = np.roll(phi, +1, axis=1) - E_CHARGE * np.roll(A_y, +1, axis=1)
    s_cos += np.cos(pj); s_sin += np.sin(pj)
    pj = np.roll(phi, -1, axis=2) + E_CHARGE * A_z
    s_cos += np.cos(pj); s_sin += np.sin(pj)
    pj = np.roll(phi, +1, axis=2) - E_CHARGE * np.roll(A_z, +1, axis=2)
    s_cos += np.cos(pj); s_sin += np.sin(pj)

    s_cos /= 6.0; s_sin /= 6.0
    # Adjust to phi reference: disorder = 1 - |<exp(i*(neighbor - phi))>|
    cos_phi = np.cos(phi); sin_phi = np.sin(phi)
    mag = np.sqrt((s_cos*cos_phi + s_sin*sin_phi)**2
                  + (s_sin*cos_phi - s_cos*sin_phi)**2)
    return np.clip(1.0 - mag, 0.0, 1.0)


def step_v12(sg, sm, chi, phi, A_x, A_y, A_z, channel_f_active=True):
    """One v12 dissipative step.

    sigma_g, sigma_m, chi same as v7.
    phi update uses gauge-invariant neighbor target.
    A_x, A_y, A_z update: gradient flow on combined phi-coupling + Maxwell.
    """
    sgb = neighbor_mean(sg)
    smb = neighbor_mean(sm)

    dsg = (ALPHA * (SIGMA_REF - sg) + BETA * (sgb - sg)
         + K_BACK * chi - K_GM * (SIGMA_REF - sm))
    sg_new = np.clip(sg + dsg, 0.0, 1.0)

    dsm = ALPHA * (SIGMA_REF - sm) + BETA * (smb - sm)
    if channel_f_active:
        dsm -= GAMMA_PHI * phi_disorder_gauge(phi, A_x, A_y, A_z) * sm
    sm_new = np.clip(sm + dsm, 0.0, 1.0)

    chi_new = (chi * (1.0 - CHI_DECAY) + CHI_REL * (sgb - sg)
             + DELTA * (SIGMA_REF - sg))

    # phi update — gauge-invariant XY alignment
    pm = phi_neighbor_xy_weighted_gauge(phi, sm, A_x, A_y, A_z)
    dphi = BETA_PHI * wrap_pi(pm - phi)
    phi_new = wrap_pi(phi + dphi)

    # A update — first-order Maxwell + phi coupling
    # phi_grad_x[i] = phi[i+1] - phi[i] - e*A_x[i]
    phi_grad_x = wrap_pi(np.roll(phi, -1, axis=0) - phi - E_CHARGE * A_x)
    phi_grad_y = wrap_pi(np.roll(phi, -1, axis=1) - phi - E_CHARGE * A_y)
    phi_grad_z = wrap_pi(np.roll(phi, -1, axis=2) - phi - E_CHARGE * A_z)

    # Plaquette field strengths
    F_xy = A_x + np.roll(A_y, -1, axis=0) - np.roll(A_x, -1, axis=1) - A_y
    F_yz = A_y + np.roll(A_z, -1, axis=1) - np.roll(A_y, -1, axis=2) - A_z
    F_xz = A_x + np.roll(A_z, -1, axis=0) - np.roll(A_x, -1, axis=2) - A_z

    # dH/dA_x[i,j,k]:
    #   phi coupling: -(BETA_PHI/(2*Z))*sin(phi_grad_x[i,j,k]) * (-e)
    #               = (E*BETA_PHI/(2*Z)) * sin(phi_grad_x)
    # No wait: dH_phi/dA_x[i,j,k] = -(BETA_PHI/(2*Z)) * d/dA_x[cos(phi_grad_x)]
    #         = -(BETA_PHI/(2*Z)) * sin(phi_grad_x) * (-E)
    #         = (E*BETA_PHI/(2*Z)) * sin(phi_grad_x)
    # Gradient flow: dA/dt = -dH/dA → dA_x = -BETA_A * (E*BETA_PHI/(2*Z)) * sin(phi_grad_x)
    # Wait, the sign of the gauge coupling matters. Let me re-derive:
    #   H_phi = -(BETA_PHI/(2Z)) * cos(phi_i - phi_j - E*A_ij)
    #   dH_phi/dA_ij = -(BETA_PHI/(2Z)) * sin(phi_i - phi_j - E*A_ij) * (-(-E))
    #                = -(BETA_PHI/(2Z)) * sin(phi_i - phi_j - E*A_ij) * (E)
    # phi_grad_x = phi[i+1] - phi[i] - E*A_x[i]  (= -(phi_i - phi_j - E*A_ij)
    #                                              with i=current node, j=+x neighbor)
    # So sin(phi_grad_x) = -sin(phi_i - phi[i+1] - E*A_x)
    # dH_phi/dA_x = -(BETA_PHI/(2Z)) * (-sin(phi_grad_x)) * E
    #             = (E*BETA_PHI/(2Z)) * sin(phi_grad_x)

    # Maxwell: dH_A/dA_x = (1/(2*mu_A)) * (F_xy - F_xy[j-1] + F_xz - F_xz[k-1])
    div_F_at_Ax = (1.0/(2.0*MU_A)) * (
        F_xy - np.roll(F_xy, +1, axis=1)
      + F_xz - np.roll(F_xz, +1, axis=2)
    )
    div_F_at_Ay = (1.0/(2.0*MU_A)) * (
      - F_xy + np.roll(F_xy, +1, axis=0)  # A_y appears with sign -1 in F_xy at corner [i,j,k]
      + F_yz - np.roll(F_yz, +1, axis=2)
    )
    div_F_at_Az = (1.0/(2.0*MU_A)) * (
      - F_yz + np.roll(F_yz, +1, axis=1)
      - F_xz + np.roll(F_xz, +1, axis=0)
    )

    phi_coupling_x = (E_CHARGE * BETA_PHI / (2.0 * Z_NB)) * np.sin(phi_grad_x)
    phi_coupling_y = (E_CHARGE * BETA_PHI / (2.0 * Z_NB)) * np.sin(phi_grad_y)
    phi_coupling_z = (E_CHARGE * BETA_PHI / (2.0 * Z_NB)) * np.sin(phi_grad_z)

    A_x_new = A_x - BETA_A * (phi_coupling_x + div_F_at_Ax)
    A_y_new = A_y - BETA_A * (phi_coupling_y + div_F_at_Ay)
    A_z_new = A_z - BETA_A * (phi_coupling_z + div_F_at_Az)

    return sg_new, sm_new, chi_new, phi_new, A_x_new, A_y_new, A_z_new


# ---------------------------------------------------------------------------
# Observables
# ---------------------------------------------------------------------------

def ring_mass(sm):
    return float(np.maximum(0.0, SIGMA_REF - sm).sum())


def E_gauge_total(A_x, A_y, A_z):
    F_xy = A_x + np.roll(A_y, -1, axis=0) - np.roll(A_x, -1, axis=1) - A_y
    F_yz = A_y + np.roll(A_z, -1, axis=1) - np.roll(A_y, -1, axis=2) - A_z
    F_xz = A_x + np.roll(A_z, -1, axis=0) - np.roll(A_x, -1, axis=2) - A_z
    return float((F_xy*F_xy + F_yz*F_yz + F_xz*F_xz).sum())


# ---------------------------------------------------------------------------
# Run one configuration
# ---------------------------------------------------------------------------

def run_v12(label, init_fn):
    sg  = np.full((L, L, L), SIGMA_REF)
    sm  = np.full((L, L, L), SIGMA_REF)
    chi = np.zeros((L, L, L))
    phi = init_fn()
    # A_ij initialized to zero — gauge field starts in vacuum
    A_x = np.zeros((L, L, L))
    A_y = np.zeros((L, L, L))
    A_z = np.zeros((L, L, L))

    history = []
    def snap(t, phase):
        return {
            "t": t, "phase": phase,
            "M_ring": ring_mass(sm),
            "E_gauge": E_gauge_total(A_x, A_y, A_z),
        }

    history.append(snap(0, "init"))
    print(f"  [{label}] Phase 1 (form vortex tube)...", flush=True)
    for t in range(1, PHASE1 + 1):
        sg, sm, chi, phi, A_x, A_y, A_z = step_v12(sg, sm, chi, phi, A_x, A_y, A_z,
                                                    channel_f_active=False)
    history.append(snap(PHASE1, "P1_end"))
    print(f"  [{label}] P1 done M={history[-1]['M_ring']:.2f} "
          f"E_gauge={history[-1]['E_gauge']:.6f}  "
          f"|A_x|_max={float(np.abs(A_x).max()):.6f}  "
          f"|A_x|_mean={float(np.abs(A_x).mean()):.6f}", flush=True)

    print(f"  [{label}] Phase 2 (Channel F + A_ij dynamics)...", flush=True)
    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi, A_x, A_y, A_z = step_v12(sg, sm, chi, phi, A_x, A_y, A_z,
                                                    channel_f_active=True)
        if t % LOG_EVERY == 0 or t == PHASE2:
            history.append(snap(PHASE1 + t, "P2"))
            print(f"  [{label}] P2 t={t} M={history[-1]['M_ring']:.2f} "
                  f"E_gauge={history[-1]['E_gauge']:.2f}", flush=True)

    print(f"  [{label}] Phase 3 (decay characterization)...", flush=True)
    for t in range(1, PHASE3 + 1):
        sg, sm, chi, phi, A_x, A_y, A_z = step_v12(sg, sm, chi, phi, A_x, A_y, A_z,
                                                    channel_f_active=True)
        if t % LOG_EVERY == 0 or t == PHASE3:
            history.append(snap(PHASE1 + PHASE2 + t, "P3"))

    p3 = [h for h in history if h["phase"] == "P3"]
    ratios = [p3[i]["M_ring"] / max(0.01, p3[i-1]["M_ring"])
              for i in range(1, len(p3))]
    mean_ratio = float(np.mean(ratios))
    if 0 < mean_ratio < 1:
        half_life_lu = math.log(0.5) / math.log(mean_ratio) * LOG_EVERY
    else:
        half_life_lu = float('inf')

    M_P2_end = next(h["M_ring"] for h in reversed(history) if h["phase"] == "P2")
    E_gauge_P2_end = next(h["E_gauge"] for h in reversed(history) if h["phase"] == "P2")

    return {
        "label": label,
        "M_P1_end": history[1]["M_ring"],
        "M_P2_end": M_P2_end,
        "M_P3_end": history[-1]["M_ring"],
        "E_gauge_P1_end": history[1]["E_gauge"],
        "E_gauge_P2_end": E_gauge_P2_end,
        "E_gauge_P3_end": history[-1]["E_gauge"],
        "mean_decay_ratio": mean_ratio,
        "half_life_lu": half_life_lu,
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--knots", choices=["all", "minimal"], default="minimal")
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f"QNG-CPU-152: Full v12 EM dynamics")
    print(f"L={L} P1={PHASE1} P2={PHASE2} P3={PHASE3}")
    print(f"E_CHARGE={E_CHARGE} MU_A={MU_A} BETA_A={BETA_A}")
    print(f"Mode: {args.knots}")
    print()

    if args.knots == "minimal":
        configs = [
            ("ring_Q0",     lambda: init_phi_hopfion(0)),
            ("hopfion_Q1",  lambda: init_phi_hopfion(1)),
            ("trefoil",     lambda: init_phi_from_knot(trefoil_curve)),
        ]
    else:
        configs = [
            ("ring_Q0",     lambda: init_phi_hopfion(0)),
            ("hopfion_Q1",  lambda: init_phi_hopfion(1)),
            ("hopfion_Q2",  lambda: init_phi_hopfion(2)),
            ("trefoil",     lambda: init_phi_from_knot(trefoil_curve)),
            ("figure_8",    lambda: init_phi_from_knot(figure8_curve)),
            ("cinquefoil",  lambda: init_phi_from_knot(cinquefoil_curve)),
        ]

    results = []
    t_start = time.time()
    for label, init_fn in configs:
        print(f"--- {label} ---", flush=True)
        res = run_v12(label, init_fn)
        results.append(res)
        print(f"  [{label}] DONE M_P2={res['M_P2_end']:.2f} "
              f"M_P3={res['M_P3_end']:.2f} "
              f"E_gauge_P2={res['E_gauge_P2_end']:.2f} "
              f"half_life={res['half_life_lu']:.0f} lu",
              flush=True)
        print()
    dt = time.time() - t_start
    print(f"Total time: {dt:.1f} s")
    print()

    # Cross-knot table
    print("=" * 100)
    print(f"{'Config':<14} {'M_P2_end':>10} {'M_P3_end':>10} "
          f"{'E_gauge_P2':>12} {'decay_ratio':>12} {'half_life':>10}")
    print("-" * 100)
    for r in results:
        print(f"{r['label']:<14} {r['M_P2_end']:>10.2f} "
              f"{r['M_P3_end']:>10.2f} {r['E_gauge_P2_end']:>12.2f} "
              f"{r['mean_decay_ratio']:>12.4f} {r['half_life_lu']:>10.0f}")
    print("=" * 100)

    # Check CPU-151 prediction
    if len(results) > 1:
        # Compare ring half-life to other knots
        ring_hl = next((r["half_life_lu"] for r in results if "ring" in r["label"]), None)
        if ring_hl is not None and ring_hl < 1e6:
            print()
            print("CPU-152 vs CPU-151 prediction (factor 2.5 spread):")
            for r in results:
                if r["half_life_lu"] < 1e6:
                    relative = ring_hl / r["half_life_lu"]
                    print(f"  {r['label']:<14}: tau_ring/tau = {relative:.3f} "
                          f"(CPU-151 predicted varies 1-2.5)")

    report = {
        "test_id": "QNG-CPU-152",
        "params": {"L": L, "E_CHARGE": E_CHARGE, "MU_A": MU_A, "BETA_A": BETA_A,
                   "PHASE1": PHASE1, "PHASE2": PHASE2, "PHASE3": PHASE3},
        "results": results,
        "interpretation": (
            "Full v12 EM dynamics with A_ij Maxwell term coupled to phi via "
            "gauge-invariant cosine. Tests CPU-151 static prediction of "
            "topology-dependent decay rate spread factor 2.5 under v12. "
            "If observed spread > v7 baseline (CPU-148 universality), "
            "v12 EM channel is the source of topology-dependent decay."
        ),
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
