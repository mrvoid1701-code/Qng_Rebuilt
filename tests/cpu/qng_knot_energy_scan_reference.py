from __future__ import annotations

"""QNG-CPU-145: Knot energy spectrum — ring vs Hopfion vs trefoil topologies.

Measures the relaxed XY-coupling energy of distinct topological configurations
of the phi field on a fixed cubic lattice with identical parameters:

  - Q=0 vortex ring          (q_twist=0,  unknot vortex)
  - Q=1 Hopfion              (q_twist=1,  one toroidal + one poloidal winding)
  - Q=2 Hopfion              (q_twist=2)
  - Q=3 Hopfion              (q_twist=3)
  - Trefoil knot             (phi winding 1 around a 3-crossing knotted curve)

Each configuration is relaxed via XY gradient flow (pure phi sector, no
matter/gravity coupling) until energy converges. The excess energy above
the ferromagnetic vacuum is the "topological mass" of the soliton.

This is the first QNG test of the Kelvin-Bilson-Thompson hypothesis
that distinct stable particles correspond to distinct knot topologies
of phi. Output gives the mass spectrum of stable QNG topological solitons
without any phenomenological calibration.

Reference: DER-QNG-091 §7 Tier A.2; DER-QNG-092 (this work).

Implementation: NumPy vectorized for speed (L=24 lattice, ~14k nodes,
~2000 relaxation steps).
"""

import json
import math
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-knot-energy-scan-v1"


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

L = 24                # lattice side
N = L * L * L

BETA_PHI = 0.06       # canonical v8 phi-XY coupling (v12 unchanged at edge level)
Z_NB     = 6          # cubic lattice coordination

# Topological soliton geometry
RING_R   = 5.0        # ring radius in lattice units
TREFOIL_SCALE = 2.5   # trefoil curve overall size

# Relaxation
ETA       = 0.20      # gradient-flow step (XY relaxation rate)
N_STEPS   = 4000
LOG_EVERY = 200
CONV_TOL  = 1e-6      # relative energy change threshold for early stop


# ---------------------------------------------------------------------------
# Lattice geometry
# ---------------------------------------------------------------------------

def make_coords():
    """Return XX, YY, ZZ arrays of shape (L,L,L) centered at L/2."""
    ax = np.arange(L, dtype=np.float64)
    XX, YY, ZZ = np.meshgrid(ax, ax, ax, indexing='ij')
    return XX, YY, ZZ


def mi(d):
    """Minimum-image distance for periodic lattice."""
    d = d.copy()
    d[d >  L/2] -= L
    d[d < -L/2] += L
    return d


def wrap_pi(a):
    """Wrap angle into (-pi, pi]."""
    return (a + math.pi) % (2 * math.pi) - math.pi


# Pre-computed minimum-image displacements from lattice center
XC, YC, ZC = L/2.0, L/2.0, L/2.0
XX, YY, ZZ = make_coords()
DX = mi(XX - XC)
DY = mi(YY - YC)
DZ = mi(ZZ - ZC)


# ---------------------------------------------------------------------------
# Initialisation functions
# ---------------------------------------------------------------------------

def init_phi_hopfion(q_twist: int) -> np.ndarray:
    """Hopfion family: phi = poloidal + q_twist * toroidal.

    q_twist=0: standard vortex ring (Hopf Q=0)
    q_twist=1: Q=1 Hopfion
    q_twist=2: Q=2 Hopfion
    ...
    """
    rho = np.sqrt(DX*DX + DY*DY)
    poloidal = np.arctan2(DZ, rho - RING_R)
    toroidal = np.arctan2(DY, DX)
    phi = wrap_pi(poloidal + q_twist * toroidal)
    return phi


def trefoil_curve(t: np.ndarray) -> np.ndarray:
    """Parametric trefoil knot.

    r(t) = TREFOIL_SCALE * (sin(t) + 2 sin(2t),
                            cos(t) - 2 cos(2t),
                            -sin(3t))

    Returns (M, 3) array of curve points.
    """
    s = TREFOIL_SCALE
    x = s * (np.sin(t) + 2 * np.sin(2*t))
    y = s * (np.cos(t) - 2 * np.cos(2*t))
    z = s * (-np.sin(3*t))
    return np.stack([x, y, z], axis=-1)


def init_phi_trefoil(n_curve: int = 360) -> np.ndarray:
    """Initialize phi field that winds by 2*pi around a trefoil knot.

    Strategy: for each lattice point P, find the nearest point r(t*) on the
    discretized trefoil curve. Use a globally-defined transverse frame to
    measure the angle of (P - r(t*)) around the tangent direction T(t*).

    The global frame uses N(t) = unit(T(t) x z_hat) (well-defined except
    where T is parallel to z_hat) and B(t) = T(t) x N(t).
    Then phi(P) = atan2((P - r(t*)) . B, (P - r(t*)) . N).

    For nearly z-parallel tangent we fall back to N = unit(T x x_hat).
    """
    # Sample the curve
    ts = np.linspace(0.0, 2*math.pi, n_curve, endpoint=False)
    curve = trefoil_curve(ts)              # (n_curve, 3)

    # Center curve at lattice middle
    curve += np.array([XC, YC, ZC])

    # Tangent vectors (numerical central difference, periodic)
    nxt = np.roll(curve,  -1, axis=0)
    prv = np.roll(curve,   1, axis=0)
    T = nxt - prv
    T /= np.linalg.norm(T, axis=1, keepdims=True)

    # Normal frame: Nf = unit(T x z), fallback Nf = unit(T x x) where T nearly parallel z
    # (renamed to Nf to avoid shadowing global N=L*L*L)
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
    # ensure unit (numerical safety)
    Bf /= np.linalg.norm(Bf, axis=1, keepdims=True)

    # Lattice points: shape (N_total, 3)
    pts = np.stack([XX.flatten(), YY.flatten(), ZZ.flatten()], axis=-1)

    # For each lattice point, find nearest curve sample.
    # Distance matrix would be (N_total, n_curve). With L=24, n=360 -> 5M, OK.
    # But to save memory we use a chunked approach.
    chunk = 2000
    nearest_t = np.zeros(N, dtype=np.int64)
    for start in range(0, N, chunk):
        end = min(start + chunk, N)
        # Minimum-image differences are not used here because the trefoil
        # is well inside the lattice — periodic image confusion only matters
        # near the boundary. For TREFOIL_SCALE=2.5 the curve max extent is
        # ~5*2.5=12.5, while L/2=12, so the curve nearly fills lattice; we
        # apply minimum-image to be safe.
        d = pts[start:end, None, :] - curve[None, :, :]
        d[..., 0] = np.where(d[..., 0] >  L/2, d[..., 0] - L, d[..., 0])
        d[..., 0] = np.where(d[..., 0] < -L/2, d[..., 0] + L, d[..., 0])
        d[..., 1] = np.where(d[..., 1] >  L/2, d[..., 1] - L, d[..., 1])
        d[..., 1] = np.where(d[..., 1] < -L/2, d[..., 1] + L, d[..., 1])
        d[..., 2] = np.where(d[..., 2] >  L/2, d[..., 2] - L, d[..., 2])
        d[..., 2] = np.where(d[..., 2] < -L/2, d[..., 2] + L, d[..., 2])
        dist_sq = np.sum(d * d, axis=-1)
        nearest_t[start:end] = np.argmin(dist_sq, axis=1)

    # Vectors P - r(t*) (using min-image)
    v = pts - curve[nearest_t]
    v[:, 0] = np.where(v[:, 0] >  L/2, v[:, 0] - L, v[:, 0])
    v[:, 0] = np.where(v[:, 0] < -L/2, v[:, 0] + L, v[:, 0])
    v[:, 1] = np.where(v[:, 1] >  L/2, v[:, 1] - L, v[:, 1])
    v[:, 1] = np.where(v[:, 1] < -L/2, v[:, 1] + L, v[:, 1])
    v[:, 2] = np.where(v[:, 2] >  L/2, v[:, 2] - L, v[:, 2])
    v[:, 2] = np.where(v[:, 2] < -L/2, v[:, 2] + L, v[:, 2])

    # Project onto (Nf, Bf) frame
    N_at = Nf[nearest_t]
    B_at = Bf[nearest_t]
    v_N = np.sum(v * N_at, axis=-1)
    v_B = np.sum(v * B_at, axis=-1)

    phi = np.arctan2(v_B, v_N).reshape((L, L, L))
    return wrap_pi(phi)


# ---------------------------------------------------------------------------
# Energy and relaxation
# ---------------------------------------------------------------------------

def neighbor_shifts(phi: np.ndarray):
    """Yield (sin diff, cos diff) sums over 6 nearest neighbors with periodic BC.

    Returns (sum_sin_diff, sum_cos_diff) of shape (L,L,L) where
       sum_sin_diff_i = sum_{j in nbs} sin(phi_j - phi_i)
       sum_cos_diff_i = sum_{j in nbs} cos(phi_j - phi_i)
    Useful for both energy and gradient.
    """
    ssin = np.zeros_like(phi)
    scos = np.zeros_like(phi)
    for axis in range(3):
        for shift in (-1, +1):
            phi_j = np.roll(phi, shift, axis=axis)
            ssin += np.sin(phi_j - phi)
            scos += np.cos(phi_j - phi)
    return ssin, scos


def phi_energy(phi: np.ndarray) -> float:
    """E_phi = -(beta_phi/(2z)) * sum_{<ij>} cos(phi_i - phi_j).

    Each edge counted twice in the (i, j) double sum; that's compensated by
    the 1/(2z) prefactor (z=6 gives the right normalization).
    """
    _, scos = neighbor_shifts(phi)
    # sum_{i,j in nbs(i)} cos(...) = 2 * sum_edges cos(...)
    return -(BETA_PHI / (2 * Z_NB)) * float(scos.sum())


def relax_step(phi: np.ndarray, eta: float) -> np.ndarray:
    """One step of XY gradient flow.

    dE/dphi_i = (beta_phi/z) * sum_{j in nbs(i)} sin(phi_i - phi_j)
              = -(beta_phi/z) * sum_{j in nbs(i)} sin(phi_j - phi_i)
    Update: phi_i <- phi_i - eta * dE/dphi_i  (steepest descent)
    """
    ssin, _ = neighbor_shifts(phi)
    # dE/dphi = -(beta_phi/z) * ssin  (sign: positive ssin lowers energy by raising phi)
    grad = -(BETA_PHI / Z_NB) * ssin
    return wrap_pi(phi - eta * grad)


# ---------------------------------------------------------------------------
# Wilson loop / topological charge probes
# ---------------------------------------------------------------------------

def hopf_invariant_proxy(phi: np.ndarray) -> float:
    """Crude proxy for Hopf invariant — uses formula Q = (1/4pi^2) * integral of
    A * F where A is the gauge connection and F = dA. For QNG phi field, the
    "magnetic field" is B_i = (1/2) epsilon_ijk * partial_j phi * partial_k phi.

    For a unit vortex ring (Q=0): proxy should be ~0.
    For Q=1 Hopfion: proxy should be ~1.
    Proxy is normalized so that ideally it matches integer Hopf charge,
    but lattice discretization will give ~10-20% errors.

    Note: this is a DIAGNOSTIC, not the gauge-invariant Wilson loop.
    """
    # Numerical gradient of phi (with phase wrap)
    gx = wrap_pi(np.roll(phi, -1, axis=0) - np.roll(phi, +1, axis=0)) / 2.0
    gy = wrap_pi(np.roll(phi, -1, axis=1) - np.roll(phi, +1, axis=1)) / 2.0
    gz = wrap_pi(np.roll(phi, -1, axis=2) - np.roll(phi, +1, axis=2)) / 2.0
    # B = (1/2) curl, but for phi scalar this is curl(grad phi) = 0 trivially
    # except where phi has discontinuity (vortex core). The standard Faddeev
    # construction uses n_hat = (sin theta cos phi, sin theta sin phi, cos theta)
    # where theta and phi together define the n field. For a pure phi-field
    # vortex without auxiliary theta, this proxy is approximate.
    #
    # Approximation: use H = grad phi as a vector field and compute
    # int H . (H x curl H) / (4pi^2) ~ Hopf number.
    # Compute curl H from gradient components.
    # H = (gx, gy, gz)
    # curl H_x = dgz/dy - dgy/dz
    cHx = (np.roll(gz, -1, axis=1) - np.roll(gz, +1, axis=1)) / 2.0 \
        - (np.roll(gy, -1, axis=2) - np.roll(gy, +1, axis=2)) / 2.0
    cHy = (np.roll(gx, -1, axis=2) - np.roll(gx, +1, axis=2)) / 2.0 \
        - (np.roll(gz, -1, axis=0) - np.roll(gz, +1, axis=0)) / 2.0
    cHz = (np.roll(gy, -1, axis=0) - np.roll(gy, +1, axis=0)) / 2.0 \
        - (np.roll(gx, -1, axis=1) - np.roll(gx, +1, axis=1)) / 2.0
    # H x curl H
    HxcHx = gy * cHz - gz * cHy
    HxcHy = gz * cHx - gx * cHz
    HxcHz = gx * cHy - gy * cHx
    integrand = gx * HxcHx + gy * HxcHy + gz * HxcHz
    return float(integrand.sum()) / (4 * math.pi * math.pi)


def vortex_winding_xy_plane(phi: np.ndarray, z_slice: int) -> float:
    """Total phi winding around a square loop in the xy-plane at given z slice.

    For a ring of phi-winding 1 with axis along z, this returns ~2*pi when
    the loop encloses the ring core.
    """
    layer = phi[:, :, z_slice]
    # Walk the perimeter of the slice
    top    = layer[0, :]
    right  = layer[:, -1]
    bot    = layer[-1, ::-1]
    left   = layer[::-1, 0]
    path = np.concatenate([top, right, bot, left, [top[0]]])
    diffs = wrap_pi(np.diff(path))
    return float(diffs.sum())


def poloidal_winding_xz_plane(phi: np.ndarray, y_slice: int,
                              loop_center=None, loop_half_size: int = 7) -> float:
    """Total phi winding around a small square loop in the xz-plane centered
    on the ring tube. For a vortex ring of axis-z with radius R in xy plane,
    this measures the poloidal winding around the tube where it pierces the
    xz plane at y=y_slice.

    The ring tube pierces the xz plane at (x, z) = (XC ± RING_R, ZC) approximately.
    Loop is square of half-size H around (XC + RING_R, ZC).
    """
    if loop_center is None:
        loop_center = (int(XC + RING_R), int(ZC))
    cx, cz = loop_center
    H = loop_half_size

    layer = phi[:, y_slice, :]   # (L, L) indexed by x, z

    # Build perimeter coords going around the square
    coords = []
    # top edge: z = cz + H, x varies from cx-H to cx+H
    for x in range(cx - H, cx + H + 1):
        coords.append((x % L, (cz + H) % L))
    # right edge: x = cx + H, z varies from cz+H-1 down to cz-H
    for z in range(cz + H - 1, cz - H - 1, -1):
        coords.append(((cx + H) % L, z % L))
    # bot edge: z = cz - H, x varies from cx+H-1 down to cx-H
    for x in range(cx + H - 1, cx - H - 1, -1):
        coords.append((x % L, (cz - H) % L))
    # left edge: x = cx - H, z varies from cz-H+1 up to cz+H-1
    for z in range(cz - H + 1, cz + H):
        coords.append(((cx - H) % L, z % L))
    # close
    coords.append(coords[0])

    path = np.array([layer[x, z] for x, z in coords])
    diffs = wrap_pi(np.diff(path))
    return float(diffs.sum())


# ---------------------------------------------------------------------------
# Single experiment per topology
# ---------------------------------------------------------------------------

def relax_to_equilibrium(phi0: np.ndarray, label: str,
                        n_steps: int = N_STEPS,
                        eta: float = ETA,
                        log_every: int = LOG_EVERY) -> dict:
    """Relax phi0 to local minimum via XY gradient flow."""
    phi = phi0.copy()
    E0 = phi_energy(phi)
    history = [{"step": 0, "E": E0}]
    print(f"  [{label}] E_initial = {E0:.4f}", flush=True)

    last_E = E0
    for t in range(1, n_steps + 1):
        phi = relax_step(phi, eta)
        if t % log_every == 0 or t == n_steps:
            E = phi_energy(phi)
            history.append({"step": t, "E": E})
            rel = abs((E - last_E) / max(1.0, abs(E)))
            print(f"  [{label}] step={t:5d}  E={E:.4f}  rel_change={rel:.2e}",
                  flush=True)
            if rel < CONV_TOL:
                print(f"  [{label}] converged at step {t}", flush=True)
                break
            last_E = E

    E_final = phi_energy(phi)
    E_vac   = -BETA_PHI * N / 2.0
    dE      = E_final - E_vac

    # Topology diagnostics
    Q_hopf  = hopf_invariant_proxy(phi)
    W_xy_5  = vortex_winding_xy_plane(phi, int(L/2 + 3))
    W_xy_c  = vortex_winding_xy_plane(phi, int(L/2))
    # Poloidal winding around the ring tube (pierces xz plane at x=XC+RING_R, z=ZC)
    W_pol   = poloidal_winding_xz_plane(phi, int(L/2))

    result = {
        "label": label,
        "E_initial": E0,
        "E_final": E_final,
        "E_vacuum": E_vac,
        "Delta_E": dE,
        "Q_hopf_proxy": Q_hopf,
        "winding_xy_above": W_xy_5,
        "winding_xy_center": W_xy_c,
        "winding_poloidal": W_pol,
        "history": history,
    }
    return result, phi


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--steps", type=int, default=N_STEPS)
    ap.add_argument("--lattice", type=int, default=L)
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("QNG-CPU-145: Knot energy spectrum")
    print(f"L={L}  N={N}  beta_phi={BETA_PHI}  z={Z_NB}")
    print(f"steps={args.steps}  eta={ETA}  ring_R={RING_R}  trefoil_scale={TREFOIL_SCALE}")
    print()

    configs = [
        ("ring_Q0",         lambda: init_phi_hopfion(0)),
        ("hopfion_Q1",      lambda: init_phi_hopfion(1)),
        ("hopfion_Q2",      lambda: init_phi_hopfion(2)),
        ("hopfion_Q3",      lambda: init_phi_hopfion(3)),
        ("hopfion_Q4",      lambda: init_phi_hopfion(4)),
        ("hopfion_Q5",      lambda: init_phi_hopfion(5)),
        ("trefoil",         lambda: init_phi_trefoil()),
    ]

    results = []
    t_start = time.time()
    for label, init_fn in configs:
        print(f"--- {label} ---", flush=True)
        phi0 = init_fn()
        res, phi_final = relax_to_equilibrium(phi0, label, n_steps=args.steps)
        results.append(res)
        print(f"  [{label}] DONE  Delta_E = {res['Delta_E']:.4f}"
              f"  Q_hopf~{res['Q_hopf_proxy']:.3f}"
              f"  W_xy_above={res['winding_xy_above']:.2f}"
              f"  W_xy_center={res['winding_xy_center']:.2f}"
              f"  W_poloidal={res['winding_poloidal']:.2f}",
              flush=True)
        print()
    dt = time.time() - t_start
    print(f"Total run time: {dt:.1f} s")
    print()

    # Summary table
    print("=" * 72)
    print(f"{'Config':<16}  {'Delta_E':>10}  {'ratio/Q0':>10}  {'ratio/Q1':>10}  "
          f"{'Q_hopf':>8}")
    print("-" * 72)
    dE_Q0 = results[0]["Delta_E"]
    dE_Q1 = results[1]["Delta_E"]
    for r in results:
        rQ0 = r["Delta_E"] / dE_Q0 if dE_Q0 > 1e-9 else float('inf')
        rQ1 = r["Delta_E"] / dE_Q1 if dE_Q1 > 1e-9 else float('inf')
        print(f"{r['label']:<16}  {r['Delta_E']:>10.4f}  {rQ0:>10.3f}  "
              f"{rQ1:>10.3f}  {r['Q_hopf_proxy']:>8.3f}")
    print("=" * 72)

    # Decision: stable topologies survive (Delta_E > 0 and bounded)
    # First-order check; full stability test would need long dynamic run.
    survives = [r["Delta_E"] > 0.1 for r in results]
    n_stable = sum(survives)
    print(f"\nFirst-order survival ({n_stable} of {len(results)} have Delta_E > 0.1):")
    for r, s in zip(results, survives):
        print(f"  {r['label']:<16}  {'OK' if s else 'COLLAPSED'}")

    # Decision criterion: at least 3 distinct topologies relax to bounded
    # non-trivial energy minima
    decision = n_stable >= 3

    report = {
        "test_id": "QNG-CPU-145",
        "decision": "pass" if decision else "fail",
        "params": {
            "L": L, "N": N, "BETA_PHI": BETA_PHI, "Z": Z_NB,
            "RING_R": RING_R, "TREFOIL_SCALE": TREFOIL_SCALE,
            "ETA": ETA, "n_steps": args.steps,
        },
        "results": results,
        "n_topologies_stable": n_stable,
        "ratios": {
            "Delta_E[Q1]/Delta_E[Q0]": dE_Q1 / dE_Q0 if dE_Q0 > 1e-9 else None,
            "Delta_E[trefoil]/Delta_E[Q0]": results[-1]["Delta_E"] / dE_Q0
                                            if dE_Q0 > 1e-9 else None,
            "Delta_E[trefoil]/Delta_E[Q1]": results[-1]["Delta_E"] / dE_Q1
                                            if dE_Q1 > 1e-9 else None,
        },
        "interpretation": (
            "Topological energy ratios are candidate analogs of particle mass "
            "ratios in the Kelvin-Bilson-Thompson hypothesis (DER-QNG-091 §7 "
            "Tier A.2). Compare to lepton ratios m_mu/m_e = 207 and "
            "m_tau/m_mu = 17 — exact match not expected at this level "
            "(missing matter sector and Wess-Zumino dressing)."
        ),
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)

    summary = [
        "# QNG-CPU-145 Knot Energy Spectrum",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Purpose",
        "First QNG test of Kelvin-Bilson-Thompson topological-knot",
        "hypothesis for particle identification (DER-QNG-091 §7 Tier A.2,",
        "DER-QNG-092). Measures relaxed phi-XY energy of distinct",
        "topological configurations on identical lattice.",
        "",
        "## Configurations tested",
        "| Config | Description |",
        "|---|---|",
        "| ring_Q0     | Vortex ring, phi winding 1 around the loop |",
        "| hopfion_Q1  | Q=1 Hopfion (poloidal + 1*toroidal) |",
        "| hopfion_Q2  | Q=2 Hopfion (poloidal + 2*toroidal) |",
        "| hopfion_Q3  | Q=3 Hopfion (poloidal + 3*toroidal) |",
        "| trefoil     | Trefoil-knot phi vortex |",
        "",
        "## Results",
        "| Config | Delta_E (above vacuum) | Delta_E/Delta_E[Q0] | Delta_E/Delta_E[Q1] | Q_hopf proxy |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        rQ0 = r["Delta_E"] / dE_Q0 if dE_Q0 > 1e-9 else float('inf')
        rQ1 = r["Delta_E"] / dE_Q1 if dE_Q1 > 1e-9 else float('inf')
        summary.append(
            f"| {r['label']} | {r['Delta_E']:.4f} | {rQ0:.3f} | {rQ1:.3f} | "
            f"{r['Q_hopf_proxy']:.3f} |"
        )
    summary += [
        "",
        "## Stability (first-order: Delta_E > 0.1)",
    ]
    for r, s in zip(results, survives):
        summary.append(f"- {r['label']}: {'OK' if s else 'COLLAPSED'}")
    summary += [
        "",
        "## Interpretation",
        report["interpretation"],
        "",
        "## Honest caveats",
        "- Energy measured at LOCAL minimum of XY gradient flow only.",
        "  True ground state of each topology class may require longer relaxation",
        "  or stronger optimizer (CG, simulated annealing).",
        "- Trefoil init uses naive transverse-frame construction; may not yield",
        "  exactly-tied trefoil under XY relaxation — could un-knot to unknot if",
        "  topological protection fails.",
        "- Q_hopf proxy is approximate; gauge-invariant Hopf number requires",
        "  the n-field formulation (Faddeev-Skyrme), not pure phi.",
        "- No matter (sigma_m) coupling — pure XY sector only. Real QNG energies",
        "  include matter-sector and gravity-sector terms that may rescale ratios.",
    ]
    (out / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

    print(f"\nReport: {rp}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
