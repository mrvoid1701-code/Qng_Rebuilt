"""Sanity-check: verify init_phi_three_rings places 3 rings correctly."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))


def centered_coords_np(L, cx=None, cy=None, cz=None):
    if cx is None: cx = L / 2.0
    if cy is None: cy = L / 2.0
    if cz is None: cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg - cx; dy = yg - cy; dz = zg - cz
    for d in (dx, dy, dz):
        d[:] = np.where(d > L / 2, d - L, d)
        d[:] = np.where(d < -L / 2, d + L, d)
    return dx, dy, dz


def init_phi_three_rings_np(L, R, d, pattern="+++"):
    """CPU version for verification."""
    assert len(pattern) == 3
    r_tri = d / np.sqrt(3.0)
    cx_mid = L / 2.0
    cy_mid = L / 2.0

    phi_total = None
    for i, sign_char in enumerate(pattern):
        theta = 2.0 * np.pi * i / 3.0
        cx = cx_mid + r_tri * np.cos(theta)
        cy = cy_mid + r_tri * np.sin(theta)
        dx, dy, dz = centered_coords_np(L, cx=cx, cy=cy)
        rho = np.sqrt(dy * dy + dz * dz)
        phi_i = np.arctan2(dx, rho - R)
        if sign_char == '-':
            phi_i = -phi_i
        phi_total = phi_i if phi_total is None else (phi_total + phi_i)
    return phi_total


def main():
    L = 24
    R = 4
    d = 4
    r_tri = d / np.sqrt(3.0)
    print(f"L={L}, R={R}, d={d}, r_tri={r_tri:.3f}")
    print(f"Triangle vertices (XY):")
    for i in range(3):
        theta = 2.0 * np.pi * i / 3.0
        cx = L / 2 + r_tri * np.cos(theta)
        cy = L / 2 + r_tri * np.sin(theta)
        print(f"  ring {i}: ({cx:.2f}, {cy:.2f})")

    # Verify equilateral triangle: pairwise distances should all equal d
    vertices = [(L / 2 + r_tri * np.cos(2 * np.pi * i / 3.0),
                 L / 2 + r_tri * np.sin(2 * np.pi * i / 3.0)) for i in range(3)]
    for i in range(3):
        for j in range(i + 1, 3):
            d_ij = np.hypot(vertices[i][0] - vertices[j][0],
                            vertices[i][1] - vertices[j][1])
            print(f"  dist ring{i}-ring{j} = {d_ij:.3f}  (target d={d})")

    # Phase map check
    for pattern in ("+++", "++-", "+-+"):
        phi = init_phi_three_rings_np(L, R, d, pattern=pattern)
        print(f"\n  pattern='{pattern}': phi shape={phi.shape}, "
              f"range=[{phi.min():+.3f}, {phi.max():+.3f}], "
              f"mean={phi.mean():+.3f}")

    # Winding check along midplane z=L/2 loop encircling the full triangle
    # For +++ pattern, total winding around a loop enclosing all 3 rings should be 3
    # (or -3 for ---)
    phi_ppp = init_phi_three_rings_np(L, R, d, pattern="+++")
    phi_ppm = init_phi_three_rings_np(L, R, d, pattern="++-")
    # Loop: circle of radius r_big in XY plane at z=L/2
    r_big = r_tri + R + 2  # enclose all 3 rings
    n_theta = 64
    thetas = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    xs = L / 2 + r_big * np.cos(thetas)
    ys = L / 2 + r_big * np.sin(thetas)
    z0 = L / 2
    # Sample phi at these points using nearest-neighbor
    ix = np.clip(np.round(xs).astype(int), 0, L - 1)
    iy = np.clip(np.round(ys).astype(int), 0, L - 1)
    iz = int(z0)
    phi_loop_ppp = phi_ppp[ix, iy, iz]
    phi_loop_ppm = phi_ppm[ix, iy, iz]

    def winding(phi_loop):
        dphi = np.diff(np.concatenate([phi_loop, [phi_loop[0]]]))
        dphi = np.where(dphi > np.pi, dphi - 2 * np.pi, dphi)
        dphi = np.where(dphi < -np.pi, dphi + 2 * np.pi, dphi)
        return dphi.sum() / (2 * np.pi)

    # This loop encircles triangle in XY plane but rings wind in XZ/YZ...
    # Actual topology is more subtle. For now just print winding values.
    print(f"\n  Winding check (loop radius r_big={r_big:.2f} at z={z0}):")
    print(f"    pattern='+++' : winding = {winding(phi_loop_ppp):+.3f}")
    print(f"    pattern='++-' : winding = {winding(phi_loop_ppm):+.3f}")


if __name__ == "__main__":
    main()
