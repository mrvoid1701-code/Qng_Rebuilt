from __future__ import annotations

"""
QNG Ether Visualizer — 3D view of the substrate.

Shows:
  - Sigma field (coherence): low-sigma nodes = vortex ring core (torus)
  - Chi field: gravitational potential cloud
  - Phi field: phase winding (optional slice)

Usage:
  py scripts/qng_visualize_ether_3d.py --mode ring
  py scripts/qng_visualize_ether_3d.py --mode two_rings
  py scripts/qng_visualize_ether_3d.py --mode chi_field
  py scripts/qng_visualize_ether_3d.py --mode phi_slice
"""

import math
import argparse
import sys
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    from mpl_toolkits.mplot3d import Axes3D   # noqa: F401
    import numpy as np
except ImportError:
    print("Need: pip install matplotlib numpy")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Substrate parameters (v5)
# ---------------------------------------------------------------------------
L: int = 24
N: int = L * L * L

SIGMA_REF: float = 0.5
ALPHA:     float = 0.005
BETA:      float = 0.35
BETA_PHI:  float = 0.02
DELTA:     float = 0.20
CHI_DECAY: float = 0.005
CHI_REL:   float = 0.35
GAMMA_PHI: float = 0.10
EPSILON:   float = 0.005

RING_R: float = 4.0
PHASE1: int = 300
PHASE2: int = 600   # short — just enough for a nice ring


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def idx3(x, y, z):
    return (x % L) * L * L + (y % L) * L + (z % L)

def coord3(i):
    x = i // (L * L); y = (i % (L * L)) // L; z = i % L
    return x, y, z

def _mi(d):
    while d > L / 2: d -= L
    while d < -L / 2: d += L
    return d

def wrap(a):
    a = a % (2 * math.pi)
    return a - 2 * math.pi if a > math.pi else a

def angle_diff(a, b):
    return wrap(a - b)

def circular_mean_weighted(phases, weights):
    sx = sum(w * math.cos(p) for w, p in zip(weights, phases))
    sy = sum(w * math.sin(p) for w, p in zip(weights, phases))
    return math.atan2(sy, sx)

def clip01(x):
    return max(0.0, min(1.0, x))


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

def init_phi_ring(r_z, ring_r, w=1):
    cx = cy = L / 2.0
    phi = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - cx); dy = _mi(y - cy)
        rho = math.sqrt(dx*dx + dy*dy)
        dz = _mi(z - r_z)
        phi.append(math.atan2(w * dz, rho - ring_r))
    return phi

def init_phi_two_rings(r1_z, r2_z, ring_r):
    cx = cy = L / 2.0
    phi = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - cx); dy = _mi(y - cy)
        rho = math.sqrt(dx*dx + dy*dy)
        dz1 = _mi(z - r1_z); dz2 = _mi(z - r2_z)
        d1 = math.sqrt(_mi(rho - ring_r)**2 + dz1**2)
        d2 = math.sqrt(_mi(rho - ring_r)**2 + dz2**2)
        # W+W- opposite chirality
        phi.append(math.atan2(dz1, rho - ring_r) if d1 <= d2
                   else math.atan2(-dz2, rho - ring_r))
    return phi


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def phase_disorder(phi, i):
    x, y, z = coord3(i)
    nb = [idx3(x-1,y,z),idx3(x+1,y,z),idx3(x,y-1,z),
          idx3(x,y+1,z),idx3(x,y,z-1),idx3(x,y,z+1)]
    sx = sum(math.cos(phi[j]) for j in nb) / 6.0
    sy = sum(math.sin(phi[j]) for j in nb) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx*sx + sy*sy))

def update_step(sigma, chi, phi, channel_f, epsilon):
    ns, nc, np_ = [], [], []
    for i in range(N):
        x, y, z = coord3(i)
        nb = [idx3(x-1,y,z),idx3(x+1,y,z),idx3(x,y-1,z),
              idx3(x,y+1,z),idx3(x,y,z-1),idx3(x,y,z+1)]
        sb = sum(sigma[j] for j in nb) / 6.0
        if channel_f:
            D_i = phase_disorder(phi, i)
            s = clip01(sigma[i]+ALPHA*(SIGMA_REF-sigma[i])+BETA*(sb-sigma[i])-GAMMA_PHI*D_i*sigma[i])
        else:
            s = clip01(sigma[i]+ALPHA*(SIGMA_REF-sigma[i])+BETA*(sb-sigma[i]))
        c = chi[i]*(1-CHI_DECAY)+CHI_REL*(sb-sigma[i])+DELTA*(SIGMA_REF-sigma[i])
        nph = [phi[j] for j in nb]; nwt = [sigma[j] for j in nb]; tw = sum(nwt)
        pm = circular_mean_weighted(nph, nwt) if tw > 1e-10 else phi[i]
        p = wrap(phi[i]+BETA_PHI*angle_diff(pm,phi[i])+epsilon*c)
        ns.append(s); nc.append(c); np_.append(p)
    return ns, nc, np_


# ---------------------------------------------------------------------------
# Simulate
# ---------------------------------------------------------------------------

def simulate(phi_init, steps1=PHASE1, steps2=PHASE2, epsilon=0.0):
    sigma = [SIGMA_REF] * N
    chi   = [0.0] * N
    phi   = phi_init[:]
    print(f"  Phase 1 ({steps1} steps)...", flush=True)
    for _ in range(steps1):
        sigma, chi, phi = update_step(sigma, chi, phi, False, 0.0)
    print(f"  Phase 2 ({steps2} steps)...", flush=True)
    for _ in range(steps2):
        sigma, chi, phi = update_step(sigma, chi, phi, True, epsilon)
    return sigma, chi, phi


# ---------------------------------------------------------------------------
# Coordinate arrays
# ---------------------------------------------------------------------------

def get_coords():
    xs = np.array([coord3(i)[0] for i in range(N)], dtype=float)
    ys = np.array([coord3(i)[1] for i in range(N)], dtype=float)
    zs = np.array([coord3(i)[2] for i in range(N)], dtype=float)
    return xs, ys, zs


# ---------------------------------------------------------------------------
# Plot helpers
# ---------------------------------------------------------------------------

def plot_sigma_ring(sigma, chi, phi, title="QNG Vortex Ring — Sigma Field"):
    xs, ys, zs = get_coords()
    sig = np.array(sigma)
    ch  = np.array(chi)

    fig = plt.figure(figsize=(16, 6))
    fig.patch.set_facecolor('#0a0a0a')

    # --- Panel 1: sigma isosurface (low sigma = ring core) ---
    ax1 = fig.add_subplot(131, projection='3d')
    ax1.set_facecolor('#0a0a0a')
    mask = sig < 0.38
    sc = ax1.scatter(xs[mask], ys[mask], zs[mask],
                     c=sig[mask], cmap='plasma_r',
                     vmin=0.15, vmax=0.40, s=8, alpha=0.8)
    plt.colorbar(sc, ax=ax1, label='sigma', shrink=0.6, pad=0.1)
    ax1.set_title('Sigma depletion\n(vortex ring core)', color='white', fontsize=10)
    _style_ax(ax1)

    # --- Panel 2: chi field (gravitational potential) ---
    ax2 = fig.add_subplot(132, projection='3d')
    ax2.set_facecolor('#0a0a0a')
    ch_max = max(abs(ch.min()), ch.max()) + 1e-10
    mask2 = np.abs(ch) > ch_max * 0.15
    sc2 = ax2.scatter(xs[mask2], ys[mask2], zs[mask2],
                      c=ch[mask2], cmap='RdBu_r',
                      vmin=-ch_max, vmax=ch_max, s=6, alpha=0.6)
    plt.colorbar(sc2, ax=ax2, label='chi', shrink=0.6, pad=0.1)
    ax2.set_title('Chi field\n(gravitational potential)', color='white', fontsize=10)
    _style_ax(ax2)

    # --- Panel 3: phi phase (mid-z slice) ---
    ax3 = fig.add_subplot(133, projection='3d')
    ax3.set_facecolor('#0a0a0a')
    ph = np.array(phi)
    # show nodes within 2 units of ring plane
    cx = cy = L / 2.0
    mask3 = np.array([abs(_mi(coord3(i)[2] - L//2)) < 3 for i in range(N)])
    sc3 = ax3.scatter(xs[mask3], ys[mask3], zs[mask3],
                      c=ph[mask3], cmap='hsv',
                      vmin=-math.pi, vmax=math.pi, s=10, alpha=0.7)
    plt.colorbar(sc3, ax=ax3, label='phi (rad)', shrink=0.6, pad=0.1)
    ax3.set_title('Phi phase field\n(topological winding)', color='white', fontsize=10)
    _style_ax(ax3)

    fig.suptitle(title, color='white', fontsize=13, y=1.01)
    plt.tight_layout()
    return fig


def plot_two_rings(sigma, chi, title="QNG Two Vortex Rings — W+W- Opposite Chirality"):
    xs, ys, zs = get_coords()
    sig = np.array(sigma)
    ch  = np.array(chi)

    fig = plt.figure(figsize=(16, 7))
    fig.patch.set_facecolor('#080808')

    # --- Panel 1: sigma ring cores (strict threshold) ---
    ax1 = fig.add_subplot(131, projection='3d')
    ax1.set_facecolor('#080808')
    mask = sig < 0.36   # strict: only deep depletion
    sc = ax1.scatter(xs[mask], ys[mask], zs[mask],
                     c=sig[mask], cmap='plasma_r',
                     vmin=0.15, vmax=0.37, s=18, alpha=0.9)
    plt.colorbar(sc, ax=ax1, label='sigma', shrink=0.6, pad=0.1)
    ax1.set_title('Two ring cores\n(sigma < 0.36)', color='white', fontsize=10)
    _style_ax(ax1)

    # --- Panel 2: chi field — top 20% only ---
    ax2 = fig.add_subplot(132, projection='3d')
    ax2.set_facecolor('#080808')
    ch_arr = np.array(chi)
    ch_thresh = np.percentile(ch_arr, 80)   # top 20% of chi values
    mask2 = ch_arr > ch_thresh
    sc2 = ax2.scatter(xs[mask2], ys[mask2], zs[mask2],
                      c=ch_arr[mask2], cmap='hot',
                      vmin=ch_thresh, vmax=ch_arr.max(), s=8, alpha=0.5)
    plt.colorbar(sc2, ax=ax2, label='chi (top 20%)', shrink=0.6, pad=0.1)
    ax2.set_title('Chi field\n(top 20% — between rings)', color='white', fontsize=10)
    _style_ax(ax2)

    # --- Panel 3: sigma + chi overlay on xz midplane ---
    ax3 = fig.add_subplot(133)
    ax3.set_facecolor('#080808')
    # xz slice at y = L//2
    y_mid = L // 2
    grid_sig = np.full((L, L), SIGMA_REF)
    grid_chi = np.zeros((L, L))
    for i in range(N):
        xi, yi, zi = coord3(i)
        if abs(yi - y_mid) <= 1:
            grid_sig[zi, xi] = min(grid_sig[zi, xi], sig[i])
            grid_chi[zi, xi] = max(grid_chi[zi, xi], ch_arr[i])

    # sigma as background (blue = low sigma = ring)
    im = ax3.imshow(grid_sig, origin='lower', cmap='plasma_r',
                    vmin=0.20, vmax=0.50, aspect='auto',
                    extent=[0, L, 0, L])
    plt.colorbar(im, ax=ax3, label='sigma (min in slice)', shrink=0.8)
    # chi as contour overlay
    X = np.arange(L); Z = np.arange(L)
    ax3.contour(X, Z, grid_chi, levels=8, cmap='hot', alpha=0.7)
    ax3.set_title('XZ slice (y=L/2)\nsigma + chi contours', color='white', fontsize=10)
    ax3.tick_params(colors='#888888'); ax3.set_xlabel('x', color='#888888'); ax3.set_ylabel('z', color='#888888')
    ax3.spines[['bottom','top','left','right']].set_color('#333333')

    fig.suptitle(title, color='white', fontsize=13, y=1.01)
    plt.tight_layout()
    return fig


def plot_phi_winding(phi, title="QNG Phi Phase — Topological Winding"):
    xs, ys, zs = get_coords()
    ph = np.array(phi)

    fig = plt.figure(figsize=(13, 5))
    fig.patch.set_facecolor('#080808')

    slices = [L//4, L//2, 3*L//4]
    for idx, z_slice in enumerate(slices):
        ax = fig.add_subplot(1, 3, idx+1, projection='3d')
        ax.set_facecolor('#080808')
        mask = np.array([coord3(i)[2] == z_slice for i in range(N)])
        sc = ax.scatter(xs[mask], ys[mask], zs[mask],
                        c=ph[mask], cmap='hsv',
                        vmin=-math.pi, vmax=math.pi, s=25, alpha=0.9)
        if idx == 2:
            plt.colorbar(sc, ax=ax, label='phi (rad)', shrink=0.7)
        ax.set_title(f'z = {z_slice}', color='white', fontsize=10)
        _style_ax(ax)

    fig.suptitle(title, color='white', fontsize=13, y=1.01)
    plt.tight_layout()
    return fig


def _style_ax(ax):
    ax.tick_params(colors='#888888', labelsize=7)
    for pane in [ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane]:
        pane.fill = False
        pane.set_edgecolor('#333333')
    ax.set_xlabel('x', color='#888888', fontsize=8)
    ax.set_ylabel('y', color='#888888', fontsize=8)
    ax.set_zlabel('z', color='#888888', fontsize=8)
    ax.set_xlim(0, L); ax.set_ylim(0, L); ax.set_zlim(0, L)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="QNG Ether 3D Visualizer")
    parser.add_argument("--mode", default="ring",
                        choices=["ring", "two_rings", "chi_field", "phi_slice"],
                        help="What to visualize")
    parser.add_argument("--save", default=None, help="Save to PNG file instead of showing")
    parser.add_argument("--steps2", type=int, default=PHASE2, help="Phase 2 steps")
    args = parser.parse_args()

    print(f"QNG Ether Visualizer — mode={args.mode}  L={L}")

    if args.mode == "ring":
        print("Simulating single vortex ring (W=+1, z=12)...")
        phi0 = init_phi_ring(L//2, RING_R, w=1)
        sigma, chi, phi = simulate(phi0, steps2=args.steps2, epsilon=0.0)
        fig = plot_sigma_ring(sigma, chi, phi,
                              title=f"QNG Substrate — Single Vortex Ring (L={L}, R={RING_R})")

    elif args.mode == "two_rings":
        print("Simulating two vortex rings (W+W-, z=6 and z=18)...")
        phi0 = init_phi_two_rings(6, 18, RING_R)
        sigma, chi, phi = simulate(phi0, steps2=args.steps2, epsilon=EPSILON)
        fig = plot_two_rings(sigma, chi,
                             title=f"QNG Substrate — Two Rings W+W- (eps={EPSILON}, L={L})")

    elif args.mode == "chi_field":
        print("Simulating single ring, visualizing chi field evolution...")
        phi0 = init_phi_ring(L//2, RING_R)
        sigma, chi, phi = simulate(phi0, steps2=args.steps2, epsilon=0.0)
        fig = plot_sigma_ring(sigma, chi, phi,
                              title=f"QNG Chi Field — Single Ring (L={L})")

    elif args.mode == "phi_slice":
        print("Simulating two rings, visualizing phi winding slices...")
        phi0 = init_phi_two_rings(6, 18, RING_R)
        sigma, chi, phi = simulate(phi0, steps2=200, epsilon=0.0)
        fig = plot_phi_winding(phi,
                               title=f"QNG Phi Phase Winding — Two Rings W+W- (L={L})")

    print("Rendering...", flush=True)
    if args.save:
        fig.savefig(args.save, dpi=150, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        print(f"Saved: {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
