"""
Winding number diagnostic for cached v8 vortex rings.

Question: does the cached L=28 R=4 ring still have 2pi poloidal winding,
or did the Phase-1/Phase-2 evolution slip the topology?

Initial condition: phi_init = arctan2(dz, rho - R) with rho = sqrt(dx^2+dy^2).
This is POLOIDAL 2pi winding: traversing a small loop in the (rho, z) plane
around the ring core (rho=R, z=0) accumulates 2pi.

Diagnostic: compute integer winding number around multiple loops:

  Loop A -- poloidal loop at fixed azimuth (phi_az = 0), circling the ring
            tube in the (x, z) plane at y = y_c
  Loop B -- poloidal loop at fixed azimuth (phi_az = pi/2), in the (y, z)
            plane at x = x_c
  Loop C -- axial line through the ring hole along z-axis at (x_c, y_c)
            (expected winding 0 for a pure poloidal ring)
  Loop D -- equatorial loop in the z = z_c plane, radius R+R/2, centered
            on ring axis (expected winding 0 for pure poloidal)

Winding number = (1/2pi) * sum_k wrap(phi[k+1] - phi[k]) where wrap maps
into (-pi, pi].

A true 2pi-winding vortex ring has |W_A| = |W_B| = 1 and W_C = W_D = 0.
A quadrupolar relaxed pattern has |W_A| <= ... (more than one 2pi jump
could still give integer winding, but amplitude |phi| < pi rules that out).
"""
from __future__ import annotations

import json
import os
import sys
import numpy as np


def _wrap(d: float) -> float:
    """Map into (-pi, pi]."""
    while d > np.pi:
        d -= 2 * np.pi
    while d <= -np.pi:
        d += 2 * np.pi
    return d


def winding_along_path(phi_path: np.ndarray) -> float:
    """Integer winding number along a closed 1D path in phi space."""
    total = 0.0
    for k in range(len(phi_path) - 1):
        total += _wrap(phi_path[k + 1] - phi_path[k])
    # close the loop
    total += _wrap(phi_path[0] - phi_path[-1])
    return total / (2 * np.pi)


def _trilinear_raw(arr: np.ndarray, x: float, y: float, z: float) -> float:
    """Tri-linear interpolation on a 3D scalar array."""
    L = arr.shape[0]
    x = max(0.0, min(L - 1 - 1e-9, x))
    y = max(0.0, min(L - 1 - 1e-9, y))
    z = max(0.0, min(L - 1 - 1e-9, z))
    xi, yi, zi = int(x), int(y), int(z)
    fx, fy, fz = x - xi, y - yi, z - zi
    c000 = arr[xi,     yi,     zi]
    c100 = arr[xi + 1, yi,     zi]
    c010 = arr[xi,     yi + 1, zi]
    c110 = arr[xi + 1, yi + 1, zi]
    c001 = arr[xi,     yi,     zi + 1]
    c101 = arr[xi + 1, yi,     zi + 1]
    c011 = arr[xi,     yi + 1, zi + 1]
    c111 = arr[xi + 1, yi + 1, zi + 1]
    c00 = c000 * (1 - fx) + c100 * fx
    c10 = c010 * (1 - fx) + c110 * fx
    c01 = c001 * (1 - fx) + c101 * fx
    c11 = c011 * (1 - fx) + c111 * fx
    c0 = c00 * (1 - fy) + c10 * fy
    c1 = c01 * (1 - fy) + c11 * fy
    return c0 * (1 - fz) + c1 * fz


_COS_CACHE = {}
_SIN_CACHE = {}

def _trilinear(arr: np.ndarray, x: float, y: float, z: float) -> float:
    """Tri-linear interpolation respecting angle periodicity.

    If arr is a phase field (values in [-pi, pi]), naive interpolation
    averages across the +-pi branch cut and destroys winding. Interpolate
    cos and sin separately, then reconstruct with arctan2.
    Detection is heuristic: if arr's absolute max is <= pi, treat it as a
    phase; otherwise do plain trilinear.
    """
    aid = id(arr)
    if aid not in _COS_CACHE:
        _COS_CACHE[aid] = np.cos(arr)
        _SIN_CACHE[aid] = np.sin(arr)
    c = _trilinear_raw(_COS_CACHE[aid], x, y, z)
    s = _trilinear_raw(_SIN_CACHE[aid], x, y, z)
    return float(np.arctan2(s, c))


def poloidal_loop(phi3d: np.ndarray, cx: float, cy: float, cz: float,
                  R: float, azimuth: float, r_loop: float = 2.0,
                  n_samples: int = 128) -> np.ndarray:
    """Sample phi on a poloidal loop around the ring core at given azimuth.
    Core center at (cx + R cos(az), cy + R sin(az), cz)."""
    ax = cx + R * np.cos(azimuth)
    ay = cy + R * np.sin(azimuth)
    az = cz
    ts = np.linspace(0.0, 2 * np.pi, n_samples, endpoint=False)
    path = np.empty(n_samples)
    # Loop is in the plane containing the ring axis and the azimuthal point.
    # In that plane, radial direction = (cos(az), sin(az), 0); axial = (0,0,1).
    for i, t in enumerate(ts):
        dr = r_loop * np.cos(t)  # radial offset from tube center
        dz = r_loop * np.sin(t)  # axial offset
        x = ax + dr * np.cos(azimuth)
        y = ay + dr * np.sin(azimuth)
        z = az + dz
        path[i] = _trilinear(phi3d, x, y, z)
    return path


def axial_line(phi3d: np.ndarray, cx: float, cy: float, L: int,
               n_samples: int = 64) -> np.ndarray:
    """Sample phi along the z-axis through the ring hole."""
    zs = np.linspace(0.5, L - 1.5, n_samples)
    return np.array([_trilinear(phi3d, cx, cy, z) for z in zs])


def equatorial_loop(phi3d: np.ndarray, cx: float, cy: float, cz: float,
                    r_outer: float, n_samples: int = 128) -> np.ndarray:
    """Sample phi on a loop in the z=cz plane, radius r_outer around ring axis."""
    ts = np.linspace(0.0, 2 * np.pi, n_samples, endpoint=False)
    path = np.empty(n_samples)
    for i, t in enumerate(ts):
        x = cx + r_outer * np.cos(t)
        y = cy + r_outer * np.sin(t)
        path[i] = _trilinear(phi3d, x, y, cz)
    return path


def _load_cached_ring(L: int = 28, R: int = 4):
    cache_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..",
        "07_validation", "audits", "qng-v8-stability-probe-v1", "ring_cache"
    ))
    for fn in os.listdir(cache_root):
        if fn.startswith(f"ring_L{L}_R{R}_") and fn.endswith(".npz"):
            path = os.path.join(cache_root, fn)
            data = np.load(path)
            out = {k: np.asarray(data[k]).reshape(L, L, L) for k in data.files}
            out["_filename"] = fn
            return out
    return None


def _summary_stats(phi: np.ndarray) -> dict:
    return {
        "min": float(phi.min()),
        "max": float(phi.max()),
        "mean": float(phi.mean()),
        "std": float(phi.std()),
        "abs_max": float(np.abs(phi).max()),
    }


def _initial_condition_reference(L: int, R: int) -> np.ndarray:
    """Reproduce init_phi_single_ring for comparison (integer grid, no offset)."""
    cx = cy = cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    X, Y, Z = np.meshgrid(xs, xs, xs, indexing="ij")
    dx = X - cx; dy = Y - cy; dz = Z - cz
    # match centered_coords periodic wrap
    for d in (dx, dy, dz):
        d[:] = np.where(d > L / 2, d - L, d)
        d[:] = np.where(d < -L / 2, d + L, d)
    rho = np.sqrt(dx * dx + dy * dy)
    return np.arctan2(dz, rho - R)


def run(L: int = 28, R: int = 4):
    print(f"=== Ring winding diagnostic  L={L}  R={R} ===")
    ring = _load_cached_ring(L, R)
    if ring is None:
        print(f"ERROR: no cached ring at L={L} R={R}")
        return 2
    phi = ring["phi"]
    print(f"Loaded:  {ring['_filename']}")
    stats = _summary_stats(phi)
    print(f"phi stats: min={stats['min']:.3f}  max={stats['max']:.3f}  "
          f"abs_max={stats['abs_max']:.3f}  std={stats['std']:.3f}")

    cx = cy = cz = L / 2.0
    results = {"cached": {}, "initial": {}}

    for tag, field in [("cached", phi), ("initial", _initial_condition_reference(L, R))]:
        print(f"\n--- {tag} phi field ---")
        r_loops = [1.0, 1.5, 2.0, 2.5]
        for r_loop in r_loops:
            path_A = poloidal_loop(field, cx, cy, cz, R, azimuth=0.0, r_loop=r_loop)
            path_B = poloidal_loop(field, cx, cy, cz, R, azimuth=np.pi/2, r_loop=r_loop)
            W_A = winding_along_path(path_A)
            W_B = winding_along_path(path_B)
            print(f"  poloidal r_loop={r_loop}:  W_A(az=0)={W_A:+.3f}  "
                  f"W_B(az=pi/2)={W_B:+.3f}  phi_range=[{path_A.min():.2f},{path_A.max():.2f}]")
            results[tag][f"poloidal_r{r_loop}"] = {
                "W_A": W_A, "W_B": W_B,
                "phi_range_A": [float(path_A.min()), float(path_A.max())],
            }

        path_C = axial_line(field, cx, cy, L)
        W_C = winding_along_path(path_C)  # open path so this treats as periodic — reference only
        print(f"  axial line (z-axis through hole):  total_phase_change="
              f"{path_C[-1]-path_C[0]:+.3f}  phi_range=[{path_C.min():.2f},{path_C.max():.2f}]")
        results[tag]["axial"] = {
            "phase_change": float(path_C[-1] - path_C[0]),
            "phi_range": [float(path_C.min()), float(path_C.max())],
        }

        for r_outer in [R + 1.0, R + 2.0, R + 3.0]:
            path_D = equatorial_loop(field, cx, cy, cz, r_outer)
            W_D = winding_along_path(path_D)
            print(f"  equatorial r_outer={r_outer}:  W_D={W_D:+.3f}  "
                  f"phi_range=[{path_D.min():.2f},{path_D.max():.2f}]")
            results[tag][f"equatorial_r{r_outer}"] = {
                "W_D": W_D,
                "phi_range": [float(path_D.min()), float(path_D.max())],
            }

    print("\n=== Verdict ===")
    # Reference: initial condition should give |W_A|=|W_B|=1 at r_loop=2
    init_wa = abs(results["initial"]["poloidal_r2.0"]["W_A"])
    init_wb = abs(results["initial"]["poloidal_r2.0"]["W_B"])
    cached_wa = abs(results["cached"]["poloidal_r2.0"]["W_A"])
    cached_wb = abs(results["cached"]["poloidal_r2.0"]["W_B"])
    print(f"  initial poloidal winding (r=2): |W_A|={init_wa:.3f} |W_B|={init_wb:.3f}")
    print(f"  cached  poloidal winding (r=2): |W_A|={cached_wa:.3f} |W_B|={cached_wb:.3f}")

    preserved = (cached_wa > 0.8) and (cached_wb > 0.8)
    print(f"\n  TOPOLOGY {'PRESERVED' if preserved else 'LOST'}")
    if not preserved:
        print("  -> cached ring has no poloidal 2pi winding; DER-QNG-046 cancellation is untestable.")
    else:
        print("  -> cached ring retains poloidal winding; DER-QNG-046 cancellation can be tested at proper loop.")

    # Save report
    out_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..",
        "07_validation", "audits", "qng-ring-winding-diag-v1"
    ))
    os.makedirs(out_dir, exist_ok=True)
    report = {
        "L": L, "R": R,
        "cache_file": ring["_filename"],
        "phi_stats": stats,
        "results": results,
        "verdict": "topology_preserved" if preserved else "topology_lost",
    }
    with open(os.path.join(out_dir, "report.json"), "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {out_dir}/report.json")
    return 0 if preserved else 1


if __name__ == "__main__":
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 28
    R = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    sys.exit(run(L, R))
