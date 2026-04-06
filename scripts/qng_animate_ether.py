from __future__ import annotations

"""
QNG Ether Animator — saves animated GIF of the substrate in action.

Shows the XZ slice (y=L/2) with:
  - sigma field as heatmap (dark = ring core / low coherence)
  - chi field as glowing contours (gravitational potential)

Modes:
  --mode two_rings   : W+W- attraction, Channel E active
  --mode single      : single ring, chi field building up
  --mode birth       : ring forming from Phase 1 chaos

Usage:
  py scripts/qng_animate_ether.py --mode two_rings --save scripts/ether_two_rings.gif
  py scripts/qng_animate_ether.py --mode single    --save scripts/ether_single.gif
"""

import math
import argparse
import sys
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
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

def init_phi_ring(r_z, ring_r):
    cx = cy = L / 2.0
    phi = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - cx); dy = _mi(y - cy)
        rho = math.sqrt(dx*dx + dy*dy)
        dz = _mi(z - r_z)
        phi.append(math.atan2(dz, rho - ring_r))
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
# Extract XZ slice
# ---------------------------------------------------------------------------

def xz_slice(sigma, chi, phi, y_mid=None):
    if y_mid is None:
        y_mid = L // 2
    grid_sig = np.full((L, L), SIGMA_REF)
    grid_chi = np.zeros((L, L))
    grid_phi = np.zeros((L, L))
    for i in range(N):
        xi, yi, zi = coord3(i)
        if abs(yi - y_mid) <= 1:
            if sigma[i] < grid_sig[zi, xi]:
                grid_sig[zi, xi] = sigma[i]
                grid_phi[zi, xi] = phi[i]
            grid_chi[zi, xi] = max(grid_chi[zi, xi], chi[i])
    return grid_sig, grid_chi, grid_phi


# ---------------------------------------------------------------------------
# Simulate and collect frames
# ---------------------------------------------------------------------------

def collect_frames(phi_init, phase1, phase2, epsilon, capture_every,
                   also_phase1=False):
    sigma = [SIGMA_REF] * N
    chi   = [0.0] * N
    phi   = phi_init[:]

    frames = []

    print(f"  Phase 1 ({phase1} steps)...", flush=True)
    for t in range(phase1):
        sigma, chi, phi = update_step(sigma, chi, phi, False, 0.0)
        if also_phase1 and t % capture_every == 0:
            gs, gc, gp = xz_slice(sigma, chi, phi)
            frames.append((t - phase1, gs.copy(), gc.copy(), gp.copy()))

    # always capture state at end of phase 1
    gs, gc, gp = xz_slice(sigma, chi, phi)
    frames.append((0, gs.copy(), gc.copy(), gp.copy()))

    print(f"  Phase 2 ({phase2} steps, capturing every {capture_every})...", flush=True)
    for t in range(1, phase2 + 1):
        sigma, chi, phi = update_step(sigma, chi, phi, True, epsilon)
        if t % capture_every == 0:
            gs, gc, gp = xz_slice(sigma, chi, phi)
            frames.append((t, gs.copy(), gc.copy(), gp.copy()))
            if t % (capture_every * 5) == 0:
                print(f"    T={t}/{phase2}", flush=True)

    return frames


# ---------------------------------------------------------------------------
# Build animation
# ---------------------------------------------------------------------------

def build_animation(frames, title, fps=8):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5))
    fig.patch.set_facecolor('#050505')
    for ax in axes:
        ax.set_facecolor('#050505')

    ax_sig, ax_chi, ax_phi = axes

    t0, gs0, gc0, gp0 = frames[0]
    X = np.arange(L); Z = np.arange(L)

    # Sigma panel
    im_sig = ax_sig.imshow(gs0, origin='lower', cmap='magma',
                           vmin=0.20, vmax=0.50, aspect='auto',
                           extent=[0, L, 0, L], interpolation='bilinear')
    cb1 = plt.colorbar(im_sig, ax=ax_sig, shrink=0.8)
    cb1.ax.tick_params(colors='#aaaaaa', labelsize=8)
    ax_sig.set_title('Sigma (coherence)\ndark = ring core', color='white', fontsize=10)

    # Chi panel
    im_chi = ax_chi.imshow(gc0, origin='lower', cmap='inferno',
                           vmin=0, vmax=max(gc0.max(), 0.1), aspect='auto',
                           extent=[0, L, 0, L], interpolation='bilinear')
    cb2 = plt.colorbar(im_chi, ax=ax_chi, shrink=0.8)
    cb2.ax.tick_params(colors='#aaaaaa', labelsize=8)
    ax_chi.set_title('Chi field\n(gravitational potential)', color='white', fontsize=10)

    # Phi panel
    im_phi = ax_phi.imshow(gp0, origin='lower', cmap='hsv',
                           vmin=-math.pi, vmax=math.pi, aspect='auto',
                           extent=[0, L, 0, L], interpolation='bilinear')
    cb3 = plt.colorbar(im_phi, ax=ax_phi, shrink=0.8)
    cb3.ax.tick_params(colors='#aaaaaa', labelsize=8)
    ax_phi.set_title('Phi (phase winding)\nW=+1 / W=-1 topology', color='white', fontsize=10)

    for ax in axes:
        ax.tick_params(colors='#666666', labelsize=8)
        ax.set_xlabel('x', color='#666666', fontsize=8)
        ax.set_ylabel('z', color='#666666', fontsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor('#333333')

    time_text = fig.text(0.5, 0.97, '', ha='center', color='#cccccc',
                         fontsize=11, fontfamily='monospace')
    fig.suptitle(title, color='white', fontsize=12, y=1.04)
    plt.tight_layout()

    chi_max_global = max(gc.max() for _, _, gc, _ in frames) + 1e-6

    def update(frame_idx):
        t, gs, gc, gp = frames[frame_idx]
        im_sig.set_data(gs)
        im_chi.set_data(gc)
        im_chi.set_clim(0, chi_max_global)
        im_phi.set_data(gp)
        label = f"T = {t:+5d}" if t < 0 else f"T = {t:5d}"
        phase = "Phase 1 (equilibration)" if t <= 0 else "Phase 2 (force active)"
        time_text.set_text(f"{label}   |   {phase}")
        return im_sig, im_chi, im_phi, time_text

    anim = animation.FuncAnimation(fig, update, frames=len(frames),
                                   interval=1000 // fps, blit=False)
    return fig, anim


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="two_rings",
                        choices=["two_rings", "single", "birth"])
    parser.add_argument("--save", default="scripts/ether_animation.gif")
    parser.add_argument("--phase2", type=int, default=3000)
    parser.add_argument("--every", type=int, default=100,
                        help="Capture frame every N steps")
    parser.add_argument("--fps", type=int, default=8)
    args = parser.parse_args()

    print(f"QNG Ether Animator — mode={args.mode}  L={L}", flush=True)
    print(f"Phase2={args.phase2}  capture_every={args.every}  fps={args.fps}", flush=True)

    if args.mode == "two_rings":
        print("Two rings W+W- (opposite chirality, attraction)...", flush=True)
        phi0 = init_phi_two_rings(6, 18, 4.0)
        title = f"QNG Substrate — Two Vortex Rings W+W- (eps={EPSILON}, L={L})"
        frames = collect_frames(phi0, phase1=300, phase2=args.phase2,
                                epsilon=EPSILON, capture_every=args.every,
                                also_phase1=False)

    elif args.mode == "single":
        print("Single ring W+1...", flush=True)
        phi0 = init_phi_ring(L//2, 4.0)
        title = f"QNG Substrate — Single Vortex Ring (eps=0, L={L})"
        frames = collect_frames(phi0, phase1=300, phase2=args.phase2,
                                epsilon=0.0, capture_every=args.every)

    elif args.mode == "birth":
        print("Ring birth from Phase 1...", flush=True)
        phi0 = init_phi_ring(L//2, 4.0)
        title = f"QNG Substrate — Vortex Ring Birth (L={L})"
        frames = collect_frames(phi0, phase1=300, phase2=args.phase2,
                                epsilon=0.0, capture_every=50,
                                also_phase1=True)

    print(f"Collected {len(frames)} frames. Building animation...", flush=True)
    fig, anim = build_animation(frames, title, fps=args.fps)

    save_path = Path(args.save)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving to {save_path} ...", flush=True)

    writer = animation.PillowWriter(fps=args.fps)
    anim.save(str(save_path), writer=writer, dpi=110)
    print(f"Done! {save_path}", flush=True)
    plt.close(fig)


if __name__ == "__main__":
    main()
