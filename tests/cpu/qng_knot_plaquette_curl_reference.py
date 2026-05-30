from __future__ import annotations

"""QNG-CPU-151: Plaquette curl analysis — gauge currents per knot type.

Direct prediction test: under v12 EM coupling, photon emission rate is
proportional to the gauge-invariant phi-flux density. Different knot
topologies have different flux distributions, so v12 should produce
topology-DEPENDENT decay rates (breaking the v7 universality observed
in CPU-148/149).

This test computes — for each knot configuration without running v12
dynamics — the plaquette curl:

   F_p = sum over plaquette edges of wrap_pi(phi_i - phi_j)

In continuum:
   F_p = oint_{plaquette} grad(phi) . dl = 2*pi * (vortex winding piercing plaquette)

In QNG v12 the photon emission rate from a phi-vortex configuration is
roughly proportional to sum_plaquettes F_p^2 (the "gauge field energy
density" that would be transferred to the A_ij field if A were dynamical).

Configurations tested:
- ring_Q0: vortex ring
- hopfion_Q1: Hopfion with 1 toroidal winding
- trefoil, figure_8, cinquefoil: knot vortices

Prediction (rope-length-based estimate):
- Unknot ring: rope length 2*pi*R ~ 31 at R=5
- Hopfion Q1: ring + toroidal => more flux plaquettes
- Trefoil: rope length ~ 16.4*r_min ~ knot-tube length
- Figure-8: ~21*r_min
- Cinquefoil: ~24*r_min

If observed N_flux scales like rope length, v12 should give knot-dependent
decay rates with spread factor ~2-4.

Reference: DER-QNG-091, DER-QNG-092 §E, DER-QNG-076 (v12 EM).
"""

import json
import math
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-knot-plaquette-curl-v1"


L = 24
N = L * L * L
RING_R = 5.0
KNOT_SCALE = 1.8


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


def init_phi_hopfion(q_twist: int) -> np.ndarray:
    rho = np.sqrt(DX*DX + DY*DY)
    poloidal = np.arctan2(DZ, rho - RING_R)
    toroidal = np.arctan2(DY, DX)
    return wrap_pi(poloidal + q_twist * toroidal)


def trefoil_curve(t):
    s = KNOT_SCALE
    x = s * (np.sin(t) + 2 * np.sin(2*t))
    y = s * (np.cos(t) - 2 * np.cos(2*t))
    z = s * (-np.sin(3*t))
    return np.stack([x, y, z], axis=-1)


def figure8_curve(t):
    s = KNOT_SCALE * 0.7
    x = s * ((2 + np.cos(2*t)) * np.cos(3*t))
    y = s * ((2 + np.cos(2*t)) * np.sin(3*t))
    z = s * (np.sin(4*t))
    return np.stack([x, y, z], axis=-1)


def cinquefoil_curve(t):
    s = KNOT_SCALE * 0.6
    R = 2.5 * s
    r = 1.0 * s
    x = (R + r * np.cos(5*t)) * np.cos(2*t)
    y = (R + r * np.cos(5*t)) * np.sin(2*t)
    z = r * np.sin(5*t)
    return np.stack([x, y, z], axis=-1)


def curve_length(curve_fn, n=10000):
    """Approximate length of a closed curve."""
    ts = np.linspace(0.0, 2*math.pi, n)
    pts = curve_fn(ts)
    diffs = pts[1:] - pts[:-1]
    return float(np.sum(np.linalg.norm(diffs, axis=1)))


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
# Plaquette curl computation
# ---------------------------------------------------------------------------

def plaquette_curls(phi: np.ndarray):
    """Compute the gauge-invariant plaquette flux for all plaquettes.

    For each plaquette in xy, yz, xz planes:
       F_p = sum of wrap_pi(phi_i - phi_j) around the plaquette boundary

    Returns three arrays of shape (L, L, L) for plaquettes oriented in
    the xy, yz, xz directions respectively, indexed by their corner node.
    """
    # phi_x_step[i,j,k] = wrap_pi(phi[i+1,j,k] - phi[i,j,k])
    phi_x_step = wrap_pi(np.roll(phi, -1, axis=0) - phi)
    phi_y_step = wrap_pi(np.roll(phi, -1, axis=1) - phi)
    phi_z_step = wrap_pi(np.roll(phi, -1, axis=2) - phi)

    # F_xy plaquette indexed by corner (i,j,k):
    #   (i,j,k) -> (i+1,j,k) -> (i+1,j+1,k) -> (i,j+1,k) -> (i,j,k)
    # phi(i+1,j,k)-phi(i,j,k)      = phi_x_step[i,j,k]
    # phi(i+1,j+1,k)-phi(i+1,j,k)  = phi_y_step[i+1,j,k] = np.roll(phi_y_step, -1, axis=0)[i,j,k]
    # phi(i,j+1,k)-phi(i+1,j+1,k)  = -phi_x_step[i,j+1,k] = -np.roll(phi_x_step, -1, axis=1)[i,j,k]
    # phi(i,j,k)-phi(i,j+1,k)      = -phi_y_step[i,j,k]
    F_xy = (phi_x_step + np.roll(phi_y_step, -1, axis=0)
            - np.roll(phi_x_step, -1, axis=1) - phi_y_step)
    F_yz = (phi_y_step + np.roll(phi_z_step, -1, axis=1)
            - np.roll(phi_y_step, -1, axis=2) - phi_z_step)
    F_xz = (phi_x_step + np.roll(phi_z_step, -1, axis=0)
            - np.roll(phi_x_step, -1, axis=2) - phi_z_step)
    return F_xy, F_yz, F_xz


def analyze_curl(F_xy, F_yz, F_xz):
    """Compute summary statistics of the curl distributions."""
    all_F = np.concatenate([F_xy.flatten(), F_yz.flatten(), F_xz.flatten()])
    # Flux-carrying plaquette: |F_p| > pi (carries vortex flux quantum)
    n_flux = int(np.sum(np.abs(all_F) > math.pi))
    # Gauge energy (proportional to (1/4) sum F^2 in v12)
    E_gauge = float(np.sum(all_F * all_F))
    max_F = float(np.max(np.abs(all_F)))
    mean_F_abs = float(np.mean(np.abs(all_F)))
    # Plaquettes with very small flux (vacuum)
    n_vacuum = int(np.sum(np.abs(all_F) < 0.1))
    return {
        "n_plaquettes_total": int(all_F.size),
        "n_flux_above_pi": n_flux,
        "n_vacuum_below_0.1": n_vacuum,
        "fraction_flux": n_flux / all_F.size,
        "E_gauge": E_gauge,
        "max_abs_F": max_F,
        "mean_abs_F": mean_F_abs,
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    configs = [
        ("ring_Q0",     lambda: init_phi_hopfion(0),    2 * math.pi * RING_R),
        ("hopfion_Q1",  lambda: init_phi_hopfion(1),    2 * math.pi * RING_R * 2),
        ("hopfion_Q2",  lambda: init_phi_hopfion(2),    2 * math.pi * RING_R * 3),
        ("trefoil",     lambda: init_phi_from_knot(trefoil_curve),
                                                       curve_length(trefoil_curve)),
        ("figure_8",    lambda: init_phi_from_knot(figure8_curve),
                                                       curve_length(figure8_curve)),
        ("cinquefoil",  lambda: init_phi_from_knot(cinquefoil_curve),
                                                       curve_length(cinquefoil_curve)),
    ]

    print(f"QNG-CPU-151: Plaquette curl analysis (would-be v12 gauge currents)")
    print(f"L={L}  N={N}  total plaquettes = 3*N = {3*N}")
    print()

    results = []
    t_start = time.time()
    for label, init_fn, rope_len in configs:
        phi = init_fn()
        F_xy, F_yz, F_xz = plaquette_curls(phi)
        stats = analyze_curl(F_xy, F_yz, F_xz)
        stats["label"] = label
        stats["rope_length"] = rope_len
        results.append(stats)
        print(f"  [{label}] rope_len={rope_len:.2f}  N_flux={stats['n_flux_above_pi']}  "
              f"E_gauge={stats['E_gauge']:.1f}  max|F|={stats['max_abs_F']:.3f}",
              flush=True)
    dt = time.time() - t_start
    print(f"\nTotal time: {dt:.1f} s")
    print()

    # Tabulate
    print("=" * 90)
    print(f"{'Config':<14} {'rope':>8} {'N_flux':>8} {'frac_flux':>12} "
          f"{'E_gauge':>10} {'max|F|':>8} {'mean|F|':>9}")
    print("-" * 90)
    for r in results:
        print(f"{r['label']:<14} {r['rope_length']:>8.2f} "
              f"{r['n_flux_above_pi']:>8d} {r['fraction_flux']:>12.5f} "
              f"{r['E_gauge']:>10.1f} {r['max_abs_F']:>8.3f} {r['mean_abs_F']:>9.4f}")
    print("=" * 90)

    # Reference: ring (Q=0) — predicted lifetime under v12 is fastest
    base = results[0]  # ring
    print()
    print("Predicted v12 photon-emission rate (proportional to E_gauge):")
    print(f"{'Config':<14} {'E_gauge/E_gauge[ring]':>22} {'expected tau_v12_relative':>26}")
    print("-" * 64)
    for r in results:
        rel_E = r["E_gauge"] / base["E_gauge"] if base["E_gauge"] > 0 else float('inf')
        tau_rel = 1.0 / rel_E if rel_E > 0 else float('inf')
        print(f"{r['label']:<14} {rel_E:>22.3f} {tau_rel:>26.4f}")
    print()

    # Correlation between rope length and E_gauge
    rope_lens = [r["rope_length"] for r in results]
    E_gauges = [r["E_gauge"] for r in results]
    if len(rope_lens) > 1:
        rope_array = np.array(rope_lens)
        E_array = np.array(E_gauges)
        # Pearson correlation
        rho = float(np.corrcoef(rope_array, E_array)[0, 1])
        print(f"Pearson correlation (rope length, E_gauge): rho = {rho:.4f}")

        # Linear fit E_gauge = a + b * rope
        b = float(np.cov(rope_array, E_array)[0, 1] / np.var(rope_array))
        a = float(np.mean(E_array) - b * np.mean(rope_array))
        print(f"Linear fit: E_gauge = {a:.2f} + {b:.3f} * rope_length")

    # Verdict
    # Plaquette curl spread → v12 photon emission spread
    rel_E_max = max(r["E_gauge"] / base["E_gauge"] for r in results)
    rel_E_min = min(r["E_gauge"] / base["E_gauge"] for r in results)
    spread = rel_E_max / rel_E_min
    print()
    print(f"E_gauge spread across knots: factor {spread:.2f}")
    print("This is the EXPECTED tau spread under v12 EM if photon emission")
    print("dominates the decay channel.")

    decision = spread > 1.5  # at least 50% spread predicted

    report = {
        "test_id": "QNG-CPU-151",
        "decision": "pass" if decision else "fail",
        "params": {"L": L, "RING_R": RING_R, "KNOT_SCALE": KNOT_SCALE},
        "results": results,
        "predicted_tau_spread_v12": spread,
        "interpretation": (
            "Plaquette curl F_p = sum(wrap_pi(phi_diffs)) around each plaquette "
            "is the gauge-invariant flux that would source A_ij dynamics in v12. "
            "Total E_gauge = sum F_p^2 is proportional to (a) total vortex line "
            "length, (b) expected photon-emission rate when A_ij is made dynamical. "
            "Different knot topologies have different E_gauge, predicting a "
            "topology-dependent decay rate under v12 (breaking the v7 universality "
            "observed in CPU-148/149)."
        ),
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
