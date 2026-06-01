"""
QNG-CPU-099: Graph-cohomology / topological-winding probe on V9-A orbital attractor.

Load GPU-100 snapshots at R in {3, 4, 5}. For each snapshot, compute integer
winding numbers n_x, n_y, n_z of phi along each of the three non-contractible
1-cycles of T^3. Test (A) non-triviality, (B) cycle-invariance, (C) R-universality,
(D) action-dimensional candidate universality.

Writes JSON report to 07_validation/audits/qng-cpu099-graph-winding-v1/.
"""

import json
import math
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "07_validation" / "audits" / "qng-v9a-phase-space-v1"
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-cpu099-graph-winding-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

L = 20
N = L * L * L


def wrap_pi(x):
    return ((x + math.pi) % (2.0 * math.pi)) - math.pi


def winding_numbers(phi_flat):
    """
    Compute integer-valued winding numbers along each principal T^3 cycle.

    phi_flat: shape (N,) with indexing (i, j, k) -> i + L*j + L*L*k  (C-order from
      how the GPU module writes snapshots — verify against 3D reshape orientation).

    Returns three arrays:
      n_x: shape (L, L)  — indexed (j, k); sum of wrapped delta-phi along i
      n_y: shape (L, L)  — indexed (i, k); sum of wrapped delta-phi along j
      n_z: shape (L, L)  — indexed (i, j); sum of wrapped delta-phi along k
    """
    phi = phi_flat.reshape(L, L, L)
    # deltas wrapped to (-pi, pi]
    dx = wrap_pi(np.roll(phi, -1, axis=0) - phi)      # (L, L, L) — delta along i
    dy = wrap_pi(np.roll(phi, -1, axis=1) - phi)
    dz = wrap_pi(np.roll(phi, -1, axis=2) - phi)
    # sum along the 1-cycle direction, divide by 2pi -> integer (for a smooth field)
    n_x = dx.sum(axis=0) / (2.0 * math.pi)  # shape (L, L) indexed by (j, k)
    n_y = dy.sum(axis=1) / (2.0 * math.pi)  # shape (L, L) indexed by (i, k)
    n_z = dz.sum(axis=2) / (2.0 * math.pi)  # shape (L, L) indexed by (i, j)
    return n_x, n_y, n_z


def nearest_int_residual(a):
    """RMS residual from nearest integer (tests smoothness / well-definedness)."""
    r = a - np.round(a)
    return float(np.sqrt(np.mean(r * r)))


def analyze_R(R):
    snap_path = DATA_DIR / f"R{R}" / "snapshots.npz"
    if not snap_path.exists():
        return None
    print(f"[R={R}] loading {snap_path} ...")
    d = np.load(snap_path)
    phi = d["phi"]           # (500, 8000) float32
    pi_phi = d["pi_phi"]     # (500, 8000) float32
    t_snap = d["t_snap"]     # (500,) float64
    nsnap = phi.shape[0]
    print(f"[R={R}] {nsnap} snapshots, t in [{t_snap[0]:.1f}, {t_snap[-1]:.1f}]")

    # Collect winding stats per snapshot
    nx_mean, ny_mean, nz_mean = [], [], []
    nx_abs_max, ny_abs_max, nz_abs_max = [], [], []
    nx_nonzero_frac, ny_nonzero_frac, nz_nonzero_frac = [], [], []
    int_residual_max = 0.0

    # Also collect an action-dimensional candidate: sum_i pi_phi_i per snapshot
    # weighted by local phi-winding defect density (proxy).
    S_top_candidate = []

    for s in range(nsnap):
        nx, ny, nz = winding_numbers(phi[s].astype(np.float64))
        rx = nearest_int_residual(nx)
        ry = nearest_int_residual(ny)
        rz = nearest_int_residual(nz)
        int_residual_max = max(int_residual_max, rx, ry, rz)

        nx_int = np.round(nx).astype(np.int64)
        ny_int = np.round(ny).astype(np.int64)
        nz_int = np.round(nz).astype(np.int64)

        nx_mean.append(float(nx_int.mean()))
        ny_mean.append(float(ny_int.mean()))
        nz_mean.append(float(nz_int.mean()))
        nx_abs_max.append(int(np.abs(nx_int).max()))
        ny_abs_max.append(int(np.abs(ny_int).max()))
        nz_abs_max.append(int(np.abs(nz_int).max()))
        nx_nonzero_frac.append(float((nx_int != 0).mean()))
        ny_nonzero_frac.append(float((ny_int != 0).mean()))
        nz_nonzero_frac.append(float((nz_int != 0).mean()))

        # action candidate: sum pi_phi_i weighted by |grad phi| (no topology yet — trivial)
        # only meaningful if windings are non-zero
        total_abs_winding = int(np.abs(nx_int).sum() + np.abs(ny_int).sum() + np.abs(nz_int).sum())
        S_top_candidate.append(float(pi_phi[s].sum() * total_abs_winding))

    def stat(arr):
        a = np.asarray(arr, dtype=np.float64)
        return {
            "mean": float(a.mean()),
            "std": float(a.std()),
            "min": float(a.min()),
            "max": float(a.max()),
        }

    out = {
        "R": R,
        "n_snapshots": nsnap,
        "int_residual_max": int_residual_max,  # smaller = smoother field
        "nx_mean_per_snap": stat(nx_mean),
        "ny_mean_per_snap": stat(ny_mean),
        "nz_mean_per_snap": stat(nz_mean),
        "nx_abs_max_per_snap": stat(nx_abs_max),
        "ny_abs_max_per_snap": stat(ny_abs_max),
        "nz_abs_max_per_snap": stat(nz_abs_max),
        "nx_nonzero_frac_mean": float(np.mean(nx_nonzero_frac)),
        "ny_nonzero_frac_mean": float(np.mean(ny_nonzero_frac)),
        "nz_nonzero_frac_mean": float(np.mean(nz_nonzero_frac)),
        "S_top_candidate": stat(S_top_candidate),
        "nx_series": nx_mean,
        "ny_series": ny_mean,
        "nz_series": nz_mean,
    }
    return out


def verdict(results):
    """
    Apply V9-TOP gates across R in {3,4,5}.
    """
    any_nonzero = False
    for r in results.values():
        if r is None:
            continue
        any_nonzero |= (
            abs(r["nx_mean_per_snap"]["mean"]) >= 0.5
            or abs(r["ny_mean_per_snap"]["mean"]) >= 0.5
            or abs(r["nz_mean_per_snap"]["mean"]) >= 0.5
        )

    # also check max absolute winding anywhere (might catch local defects without mean shift)
    any_local_defect = False
    for r in results.values():
        if r is None:
            continue
        any_local_defect |= (
            r["nx_abs_max_per_snap"]["max"] >= 1
            or r["ny_abs_max_per_snap"]["max"] >= 1
            or r["nz_abs_max_per_snap"]["max"] >= 1
        )

    if not any_nonzero and not any_local_defect:
        return "V9-TOP-TRIVIAL", "All winding numbers are zero everywhere across all R and all snapshots."
    if any_local_defect and not any_nonzero:
        return "V9-TOP-LOCAL_DEFECTS_ONLY", "Local winding defects present but net winding zero (contractible pairs)."

    # check R-universality
    r3 = results.get(3); r4 = results.get(4); r5 = results.get(5)
    if all(r is not None for r in (r3, r4, r5)):
        means = [
            (r3["nx_mean_per_snap"]["mean"], r4["nx_mean_per_snap"]["mean"], r5["nx_mean_per_snap"]["mean"]),
            (r3["ny_mean_per_snap"]["mean"], r4["ny_mean_per_snap"]["mean"], r5["ny_mean_per_snap"]["mean"]),
            (r3["nz_mean_per_snap"]["mean"], r4["nz_mean_per_snap"]["mean"], r5["nz_mean_per_snap"]["mean"]),
        ]
        universal = True
        for triple in means:
            if max(triple) - min(triple) > 0.1 * max(1.0, max(abs(x) for x in triple)):
                universal = False
                break
        if universal:
            return "V9-TOP-PASS", f"Non-zero winding universal across R: {means}"
        else:
            return "V9-TOP-R_DEPENDENT", f"Non-zero winding but R-dependent: {means}"

    return "V9-TOP-INCOMPLETE", "Not all R available."


def main():
    results = {}
    for R in (3, 4, 5):
        r = analyze_R(R)
        results[R] = r
        if r is not None:
            print(f"[R={R}] nx: {r['nx_mean_per_snap']['mean']:+.4f} "
                  f"+/- {r['nx_mean_per_snap']['std']:.4f} "
                  f"| ny: {r['ny_mean_per_snap']['mean']:+.4f} "
                  f"| nz: {r['nz_mean_per_snap']['mean']:+.4f}")
            print(f"  |n|_max: x={r['nx_abs_max_per_snap']['max']}, "
                  f"y={r['ny_abs_max_per_snap']['max']}, "
                  f"z={r['nz_abs_max_per_snap']['max']}")
            print(f"  nonzero frac: x={r['nx_nonzero_frac_mean']:.4f}, "
                  f"y={r['ny_nonzero_frac_mean']:.4f}, "
                  f"z={r['nz_nonzero_frac_mean']:.4f}")
            print(f"  int residual max: {r['int_residual_max']:.6f}")

    verd, msg = verdict(results)
    print(f"\nVERDICT: {verd}\n{msg}")

    report = {
        "test_id": "QNG-CPU-099",
        "verdict": verd,
        "message": msg,
        "per_R": results,
    }
    with open(OUT_DIR / "report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nWrote {OUT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
