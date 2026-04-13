from __future__ import annotations

"""
QNG v7 Hopfion Ether Renderer.

Builds the latest two-field substrate candidate (sigma_g, sigma_m, chi, phi),
simulates a ring or Hopfion in the v7 dissipative regime, then renders a single
cinematic PNG using volumetric point splats.

Usage:
  py scripts/qng_render_hopfion_ether.py
  py scripts/qng_render_hopfion_ether.py --variant ring
  py scripts/qng_render_hopfion_ether.py --save scripts/ether_hopfion_v7.png
"""

import argparse
import math
import sys
from pathlib import Path

try:
    import cupy as cp
    xp = cp
    DEVICE = "GPU (CuPy)"
except ImportError:
    import numpy as cp  # type: ignore
    xp = cp
    DEVICE = "CPU (numpy fallback)"

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LightSource
    import numpy as np
except ImportError:
    print("Need: pip install matplotlib numpy")
    sys.exit(1)

from scipy.ndimage import gaussian_filter


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "scripts" / "ether_hopfion_v7.png"


# ---------------------------------------------------------------------------
# v7 substrate parameters
# ---------------------------------------------------------------------------

L = 36
SIGMA_REF = 0.5
ALPHA = 0.005
BETA = 0.35
BETA_PHI = 0.02
DELTA = 0.20
CHI_DECAY = 0.020
CHI_REL = 0.35
GAMMA_PHI = 0.10
K_BACK = 0.10
K_GM = 0.020

PHASE1 = 300
PHASE2_DISS = 1500
RING_R = 8.0
RX = L / 2.0
RY = L / 2.0
RZ = L / 2.0
PI = math.pi


# ---------------------------------------------------------------------------
# Substrate simulation
# ---------------------------------------------------------------------------

def make_coord_grids():
    xs = xp.arange(L, dtype=xp.float32)
    x3 = xp.broadcast_to(xs[:, None, None], (L, L, L))
    y3 = xp.broadcast_to(xs[None, :, None], (L, L, L))
    z3 = xp.broadcast_to(xs[None, None, :], (L, L, L))
    return x3, y3, z3


def _mi_arr(d):
    return d - xp.round(d / L) * L


def wrap_arr(a):
    a = a % (2 * PI)
    return xp.where(a > PI, a - 2 * PI, a)


def adiff_arr(a, b):
    return wrap_arr(a - b)


def nb6(arr):
    return (
        xp.roll(arr, 1, 0) + xp.roll(arr, -1, 0) +
        xp.roll(arr, 1, 1) + xp.roll(arr, -1, 1) +
        xp.roll(arr, 1, 2) + xp.roll(arr, -1, 2)
    ) / 6.0


def nb6_sum(arr):
    return (
        xp.roll(arr, 1, 0) + xp.roll(arr, -1, 0) +
        xp.roll(arr, 1, 1) + xp.roll(arr, -1, 1) +
        xp.roll(arr, 1, 2) + xp.roll(arr, -1, 2)
    )


def init_phi(q_twist: int):
    x3, y3, z3 = make_coord_grids()
    dx = _mi_arr(x3 - RX)
    dy = _mi_arr(y3 - RY)
    dz = _mi_arr(z3 - RZ)
    rho = xp.sqrt(dx * dx + dy * dy)
    return wrap_arr(xp.arctan2(dz, rho - RING_R) + q_twist * xp.arctan2(dy, dx))


def dis_arr(phi):
    sx = nb6(xp.cos(phi))
    sy = nb6(xp.sin(phi))
    return xp.maximum(xp.zeros_like(phi), 1.0 - xp.sqrt(sx * sx + sy * sy))


def phi_align(sm, phi):
    tw = nb6_sum(sm)
    safe = xp.where(tw > 1e-10, tw, xp.ones_like(tw))
    sx = nb6_sum(sm * xp.cos(phi)) / safe
    sy = nb6_sum(sm * xp.sin(phi)) / safe
    pm = xp.where(tw > 1e-10, xp.arctan2(sy, sx), phi)
    return wrap_arr(phi + BETA_PHI * adiff_arr(pm, phi))


def step_dissipative(sg, sm, chi, phi):
    sgb = nb6(sg)
    smb = nb6(sm)

    dsg = (
        ALPHA * (SIGMA_REF - sg)
        + BETA * (sgb - sg)
        + K_BACK * chi
        - K_GM * (SIGMA_REF - sm)
    )
    sg = xp.clip(sg + dsg, 0.0, 1.0)

    dsm = (
        ALPHA * (SIGMA_REF - sm)
        + BETA * (smb - sm)
        - GAMMA_PHI * dis_arr(phi) * sm
    )
    sm = xp.clip(sm + dsm, 0.0, 1.0)

    chi = chi * (1.0 - CHI_DECAY) + CHI_REL * (sgb - sg) + DELTA * (SIGMA_REF - sg)
    phi = phi_align(sm, phi)
    return sg, sm, chi, phi


def get_np(arr):
    if xp.__name__ == "cupy":
        return arr.get()
    return np.array(arr)


def build_structure(variant: str):
    q_twist = 1 if variant == "hopfion" else 0
    phi = init_phi(q_twist)
    sg = xp.full((L, L, L), SIGMA_REF, dtype=xp.float32)
    sm = xp.full((L, L, L), SIGMA_REF, dtype=xp.float32)
    chi = xp.zeros((L, L, L), dtype=xp.float32)

    print(f"Device: {DEVICE}")
    print(f"Building {variant} in v7 substrate (L={L}, K_GM={K_GM})...", flush=True)

    for _ in range(PHASE1):
        sgb = nb6(sg)
        smb = nb6(sm)
        sg = xp.clip(sg + ALPHA * (SIGMA_REF - sg) + BETA * (sgb - sg), 0.0, 1.0)
        sm = xp.clip(sm + ALPHA * (SIGMA_REF - sm) + BETA * (smb - sm), 0.0, 1.0)
        chi = chi * (1.0 - CHI_DECAY) + CHI_REL * (sgb - sg) + DELTA * (SIGMA_REF - sg)
        phi = phi_align(sm, phi)

    for step in range(1, PHASE2_DISS + 1):
        sg, sm, chi, phi = step_dissipative(sg, sm, chi, phi)
        if step % 500 == 0:
            matter = float(xp.sum(xp.maximum(xp.zeros_like(sm), SIGMA_REF - sm)).get()
                           if xp.__name__ == "cupy" else xp.sum(xp.maximum(xp.zeros_like(sm), SIGMA_REF - sm)))
            print(f"  phase2={step:4d}  matter={matter:7.1f}", flush=True)

    return get_np(sg), get_np(sm), get_np(chi), get_np(phi)


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def normalize01(arr):
    arr = np.asarray(arr, dtype=np.float32)
    lo = float(arr.min())
    hi = float(arr.max())
    if hi - lo < 1e-9:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def build_background(width, height):
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    nx = (xx - width / 2.0) / width
    ny = (yy - height / 2.0) / height
    r = np.sqrt(nx * nx + ny * ny)

    bg = np.zeros((height, width, 3), dtype=np.float32)
    bg[..., 0] = 0.004 + 0.010 * np.exp(-r * 5.5)
    bg[..., 1] = 0.006 + 0.016 * np.exp(-r * 4.0)
    bg[..., 2] = 0.010 + 0.026 * np.exp(-r * 3.0)

    waves = (
        0.5 * np.sin(9.0 * nx + 4.0 * ny)
        + 0.35 * np.sin(16.0 * ny - 5.5 * nx)
        + 0.25 * np.sin(23.0 * (nx + ny))
    )
    waves = normalize01(waves)
    haze = 0.008 * waves * np.exp(-r * 2.8)
    bg[..., 1] += haze * 0.8
    bg[..., 2] += haze * 1.1

    vignette = np.clip(1.0 - r * 1.15, 0.12, 1.0)[..., None]
    return np.clip(bg * vignette, 0.0, 1.0)


def estimate_geometry(sm, sg):
    matter = np.clip(SIGMA_REF - sm, 0.0, None)
    weights = matter / (matter.max() + 1e-9)
    mask = weights > np.percentile(weights, 85)
    xs, ys, zs = np.indices(sm.shape, dtype=np.float32)
    dx = xs[mask] - RX
    dy = ys[mask] - RY
    dz = zs[mask] - RZ
    ww = weights[mask] + 1e-6
    rho = np.sqrt(dx * dx + dy * dy)
    major = float(np.average(rho, weights=ww))
    minor = float(np.sqrt(np.average((rho - major) ** 2 + dz ** 2, weights=ww)))
    minor = max(1.6, minor)

    gravity = np.clip(SIGMA_REF - sg, 0.0, None)
    halo_strength = float(np.percentile(gravity, 99))
    halo_scale = 2.4 + 20.0 * halo_strength
    return major, minor, halo_scale


def torus_mesh(major, minor, nu=220, nv=120, twist=0.0, filament=False):
    u = np.linspace(0.0, 2.0 * np.pi, nu)
    v = np.linspace(0.0, 2.0 * np.pi, nv)
    uu, vv = np.meshgrid(u, v, indexing="ij")

    local_minor = minor * (1.0 + 0.08 * np.cos(3.0 * uu + 2.0 * vv))
    if filament:
        local_minor = minor * (0.18 + 0.06 * np.cos(2.0 * vv))

    twist_term = twist * uu
    cos_v = np.cos(vv + twist_term)
    sin_v = np.sin(vv + twist_term)

    x = (major + local_minor * cos_v) * np.cos(uu)
    y = (major + local_minor * cos_v) * np.sin(uu)
    z = local_minor * sin_v
    return x, y, z


def rotated_projection(x, y, z, yaw=42.0, pitch=25.0):
    yaw_r = math.radians(yaw)
    pitch_r = math.radians(pitch)
    cy, sy = math.cos(yaw_r), math.sin(yaw_r)
    cp_, sp = math.cos(pitch_r), math.sin(pitch_r)

    xr = cy * x + sy * z
    zr = -sy * x + cy * z
    yr = cp_ * y - sp * zr
    return xr, yr, zr


def make_shaded_colors(shape, base_rgb, blend_rgb, amount):
    amt = normalize01(amount)[..., None]
    base = np.ones(shape + (3,), dtype=np.float32)
    base[..., 0] = base_rgb[0]
    base[..., 1] = base_rgb[1]
    base[..., 2] = base_rgb[2]
    lit = base * (0.45 + 0.75 * amt)
    tint = 0.72 + 0.28 * blend_rgb
    return np.clip(lit * tint, 0.0, 1.0)


def build_gravity_backdrop(sg):
    gravity = np.clip(SIGMA_REF - sg, 0.0, None)
    gravity = gravity.sum(axis=1)
    gravity = gaussian_filter(gravity, sigma=3.0)
    gravity = normalize01(gravity)
    return gravity


def render_scene(sg, sm, chi, phi, variant: str, out_path: Path):
    major, minor, halo_scale = estimate_geometry(sm, sg)

    bg = build_background(1400, 1400)

    fig = plt.figure(figsize=(10.5, 10.5), facecolor="black")
    ax_bg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=0)
    ax_bg.imshow(bg, interpolation="bilinear")
    ax_bg.set_axis_off()

    gravity_map = build_gravity_backdrop(sg)
    ax_bg.imshow(
        gravity_map,
        cmap="Greens",
        alpha=np.clip(0.55 * gravity_map, 0.0, 0.42),
        interpolation="bilinear",
        extent=[200, 1200, 1200, 200],
    )

    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96], projection="3d", zorder=2)
    ax.set_facecolor((0, 0, 0, 0))

    twist = 1.0 if variant == "hopfion" else 0.0
    xh, yh, zh = torus_mesh(major, minor * halo_scale, nu=180, nv=90, twist=0.0)
    xm, ym, zm = torus_mesh(major, minor, nu=240, nv=140, twist=0.18 if variant == "hopfion" else 0.0)
    xf, yf, zf = torus_mesh(major, minor * 0.92, nu=220, nv=12, twist=0.95 if variant == "hopfion" else 0.25, filament=True)

    _, _, zh_r = rotated_projection(xh, yh, zh)
    _, _, zm_r = rotated_projection(xm, ym, zm)
    _, _, zf_r = rotated_projection(xf, yf, zf)

    halo_colors = make_shaded_colors(xh.shape, np.array([0.18, 0.72, 0.38], dtype=np.float32), np.array([0.70, 1.00, 0.82], dtype=np.float32), normalize01(zh_r))
    matter_colors = make_shaded_colors(xm.shape, np.array([0.58, 0.84, 0.98], dtype=np.float32), np.array([0.95, 0.98, 1.00], dtype=np.float32), normalize01(zm_r))
    filament_colors = make_shaded_colors(xf.shape, np.array([0.95, 0.82, 0.44], dtype=np.float32), np.array([1.00, 0.95, 0.70], dtype=np.float32), normalize01(zf_r))

    ax.plot_surface(
        xh, yh, zh,
        facecolors=halo_colors,
        linewidth=0,
        antialiased=True,
        shade=False,
        alpha=0.12,
        zorder=1,
    )
    ax.plot_surface(
        xm, ym, zm,
        facecolors=matter_colors,
        linewidth=0,
        antialiased=True,
        shade=False,
        alpha=0.96,
        zorder=4,
    )
    ax.plot_surface(
        xf, yf, zf,
        facecolors=filament_colors,
        linewidth=0,
        antialiased=True,
        shade=False,
        alpha=0.55,
        zorder=5,
    )

    ax.view_init(elev=23, azim=36)
    span = major + minor * halo_scale + 4.0
    ax.set_xlim(-span, span)
    ax.set_ylim(-span, span)
    ax.set_zlim(-span * 0.78, span * 0.78)
    ax.set_axis_off()
    ax.dist = 7.2

    title = "QNG v7 Ether — Hopfion in the Gravitational Medium"
    subtitle = "smooth toroidal matter excitation with twisted topological phase lines"
    if variant == "ring":
        title = "QNG v7 Ether — Ring Excitation in the Gravitational Medium"
        subtitle = "baseline untwisted ring for comparison with the Hopfion state"

    ax_bg.text(
        0.03, 0.965, title,
        transform=ax_bg.transAxes,
        color="#d9faef",
        fontsize=14,
        ha="left",
        va="top",
        alpha=0.95,
        family="DejaVu Sans",
    )
    ax_bg.text(
        0.03, 0.935,
        "sigma_g: green ether well   |   sigma_m + phi: blue-white core   |   gold: phase filaments",
        transform=ax_bg.transAxes,
        color="#a5bcc9",
        fontsize=9.5,
        ha="left",
        va="top",
        alpha=0.88,
        family="DejaVu Sans",
    )
    ax_bg.text(
        0.03, 0.907,
        subtitle,
        transform=ax_bg.transAxes,
        color="#8297a3",
        fontsize=8.6,
        ha="left",
        va="top",
        alpha=0.82,
        family="DejaVu Sans",
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.0)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Render a cinematic QNG v7 hopfion ether image.")
    parser.add_argument("--variant", choices=["hopfion", "ring"], default="hopfion")
    parser.add_argument("--save", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    out_path = Path(args.save)
    sg, sm, chi, phi = build_structure(args.variant)
    print("Rendering final image...", flush=True)
    render_scene(sg, sm, chi, phi, args.variant, out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
