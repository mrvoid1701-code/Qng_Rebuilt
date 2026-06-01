"""Quick CPU visualization of bi-ring bound state (options F+G+H).

(F) 3D volume slices of sigma_m for bound d=4 state
(G) Side-by-side single vs bi XZ-plane snapshots (sigma_m + phi)
(H) Fourier decomposition of M_total(t) series for single vs d=3,4,6
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

SIGMA_M_REF = 0.5


def load_final(path):
    return dict(np.load(path))


def load_m_series(path):
    npz = np.load(path)
    return {k: npz[k] for k in npz.files}


def plot_bound_state_3d(st_bi_d4, L, outpath):
    """Option F: show sigma_m depletion as 3 orthogonal slices + X-integrated projection."""
    sm3d = st_bi_d4['sm'].reshape(L, L, L)
    phi3d = st_bi_d4['phi'].reshape(L, L, L)
    dep = np.maximum(0.0, SIGMA_M_REF - sm3d)

    c = L // 2

    fig = plt.figure(figsize=(14, 10))

    # Row 1: three orthogonal slices of sigma_m deficit
    ax1 = plt.subplot2grid((3, 4), (0, 0))
    im1 = ax1.imshow(dep[c, :, :].T, origin='lower', cmap='inferno', aspect='equal')
    ax1.set_title(f'sigma_m deficit, X=L/2 slice (YZ plane)', fontsize=10)
    ax1.set_xlabel('Y'); ax1.set_ylabel('Z')
    plt.colorbar(im1, ax=ax1, shrink=0.8)

    ax2 = plt.subplot2grid((3, 4), (0, 1))
    im2 = ax2.imshow(dep[:, c, :].T, origin='lower', cmap='inferno', aspect='equal')
    ax2.set_title(f'sigma_m deficit, Y=L/2 slice (XZ plane)', fontsize=10)
    ax2.set_xlabel('X'); ax2.set_ylabel('Z')
    plt.colorbar(im2, ax=ax2, shrink=0.8)

    ax3 = plt.subplot2grid((3, 4), (0, 2))
    im3 = ax3.imshow(dep[:, :, c].T, origin='lower', cmap='inferno', aspect='equal')
    ax3.set_title(f'sigma_m deficit, Z=L/2 slice (XY plane)', fontsize=10)
    ax3.set_xlabel('X'); ax3.set_ylabel('Y')
    plt.colorbar(im3, ax=ax3, shrink=0.8)

    # Row 1, col 3: X-integrated projection (shows both rings as two "moons")
    ax4 = plt.subplot2grid((3, 4), (0, 3))
    proj = dep.sum(axis=0)  # integrate along X (ring axis)
    im4 = ax4.imshow(proj.T, origin='lower', cmap='inferno', aspect='equal')
    ax4.set_title('sigma_m deficit, X-projected (along ring axis)', fontsize=10)
    ax4.set_xlabel('Y'); ax4.set_ylabel('Z')
    plt.colorbar(im4, ax=ax4, shrink=0.8)

    # Row 2: phi (wrapped) on same slices
    norm = TwoSlopeNorm(vmin=-np.pi, vcenter=0, vmax=np.pi)

    ax5 = plt.subplot2grid((3, 4), (1, 0))
    im5 = ax5.imshow(phi3d[c, :, :].T, origin='lower', cmap='twilight', norm=norm, aspect='equal')
    ax5.set_title('phi, X=L/2 slice', fontsize=10)
    plt.colorbar(im5, ax=ax5, shrink=0.8)

    ax6 = plt.subplot2grid((3, 4), (1, 1))
    im6 = ax6.imshow(phi3d[:, c, :].T, origin='lower', cmap='twilight', norm=norm, aspect='equal')
    ax6.set_title('phi, Y=L/2 slice', fontsize=10)
    plt.colorbar(im6, ax=ax6, shrink=0.8)

    ax7 = plt.subplot2grid((3, 4), (1, 2))
    im7 = ax7.imshow(phi3d[:, :, c].T, origin='lower', cmap='twilight', norm=norm, aspect='equal')
    ax7.set_title('phi, Z=L/2 slice', fontsize=10)
    plt.colorbar(im7, ax=ax7, shrink=0.8)

    # Phi winding diagnostic: gradient magnitude projected along X
    ax8 = plt.subplot2grid((3, 4), (1, 3))
    gx, gy, gz = np.gradient(phi3d)
    # wrap gradient in case of branch cuts
    for g in (gx, gy, gz):
        g[:] = (g + np.pi) % (2*np.pi) - np.pi
    grad_mag = np.sqrt(gx*gx + gy*gy + gz*gz)
    proj_g = grad_mag.sum(axis=0)
    im8 = ax8.imshow(proj_g.T, origin='lower', cmap='viridis', aspect='equal')
    ax8.set_title('|grad phi| X-projected', fontsize=10)
    plt.colorbar(im8, ax=ax8, shrink=0.8)

    # Row 3: 1D lineouts through ring axis and perpendicular
    ax9 = plt.subplot2grid((3, 4), (2, 0), colspan=2)
    # Along Y at Z=L/2, X=L/2: should see two ring cross-sections
    lineout_Y = dep[c, :, c]
    ax9.plot(np.arange(L), lineout_Y, 'o-', color='#d62728')
    ax9.set_xlabel('Y (lu)'); ax9.set_ylabel('sigma_m deficit')
    ax9.set_title(f'Lineout: dep along Y at (X=L/2, Z=L/2) — should show 2 peaks at d=4 separation', fontsize=10)
    ax9.grid(alpha=0.3)
    ax9.axvline(L/2 - 2, color='gray', linestyle='--', alpha=0.5, label='ring centers (d=4)')
    ax9.axvline(L/2 + 2, color='gray', linestyle='--', alpha=0.5)
    ax9.legend()

    ax10 = plt.subplot2grid((3, 4), (2, 2), colspan=2)
    # Along X at Y=L/2, Z=L/2: should see ring "depth"
    lineout_X = dep[:, c, c]
    ax10.plot(np.arange(L), lineout_X, 'o-', color='#1f77b4')
    ax10.set_xlabel('X (lu)'); ax10.set_ylabel('sigma_m deficit')
    ax10.set_title(f'Lineout: dep along X at (Y=L/2, Z=L/2) — ring thickness along axis', fontsize=10)
    ax10.grid(alpha=0.3)

    fig.suptitle(f'Bound state GPU-032b (d=4, W+W-, L={L}, T=5000 lu) — Option F + lineouts',
                 fontsize=12, y=0.995)
    fig.tight_layout()
    fig.savefig(outpath, dpi=130, bbox_inches='tight')
    plt.close(fig)


def plot_single_vs_bi(st_single, L_single, st_bi_d4, L_bi, outpath):
    """Option G: side-by-side single vs bi XZ snapshots."""
    sm_single = st_single['sm'].reshape(L_single, L_single, L_single)
    phi_single = st_single['phi'].reshape(L_single, L_single, L_single)
    sm_bi = st_bi_d4['sm'].reshape(L_bi, L_bi, L_bi)
    phi_bi = st_bi_d4['phi'].reshape(L_bi, L_bi, L_bi)

    dep_s = np.maximum(0.0, SIGMA_M_REF - sm_single)
    dep_b = np.maximum(0.0, SIGMA_M_REF - sm_bi)

    fig, ax = plt.subplots(2, 4, figsize=(15, 8))

    cs = L_single // 2
    cb = L_bi // 2

    # Row 1: sigma_m deficit
    im = ax[0, 0].imshow(dep_s[:, cs, :].T, origin='lower', cmap='inferno', aspect='equal')
    ax[0, 0].set_title(f'Single ring, XZ-slice (L={L_single})', fontsize=10)
    plt.colorbar(im, ax=ax[0, 0], shrink=0.7)
    ax[0, 0].set_xlabel('X'); ax[0, 0].set_ylabel('Z')

    im = ax[0, 1].imshow(dep_s.sum(axis=0).T, origin='lower', cmap='inferno', aspect='equal')
    ax[0, 1].set_title('Single, X-projected', fontsize=10)
    plt.colorbar(im, ax=ax[0, 1], shrink=0.7)

    im = ax[0, 2].imshow(dep_b[:, cb, :].T, origin='lower', cmap='inferno', aspect='equal')
    ax[0, 2].set_title(f'Bi-ring d=4, XZ-slice (L={L_bi})', fontsize=10)
    plt.colorbar(im, ax=ax[0, 2], shrink=0.7)
    ax[0, 2].set_xlabel('X'); ax[0, 2].set_ylabel('Z')

    im = ax[0, 3].imshow(dep_b.sum(axis=0).T, origin='lower', cmap='inferno', aspect='equal')
    ax[0, 3].set_title('Bi-ring, X-projected', fontsize=10)
    plt.colorbar(im, ax=ax[0, 3], shrink=0.7)

    # Row 2: phi
    norm = TwoSlopeNorm(vmin=-np.pi, vcenter=0, vmax=np.pi)
    im = ax[1, 0].imshow(phi_single[:, cs, :].T, origin='lower', cmap='twilight', norm=norm, aspect='equal')
    ax[1, 0].set_title('Single phi, XZ-slice', fontsize=10)
    plt.colorbar(im, ax=ax[1, 0], shrink=0.7)

    gx, gy, gz = np.gradient(phi_single)
    for g in (gx, gy, gz):
        g[:] = (g + np.pi) % (2*np.pi) - np.pi
    gmag = np.sqrt(gx*gx + gy*gy + gz*gz)
    im = ax[1, 1].imshow(gmag.sum(axis=1).T, origin='lower', cmap='viridis', aspect='equal')
    ax[1, 1].set_title('Single |grad phi|, Y-projected', fontsize=10)
    plt.colorbar(im, ax=ax[1, 1], shrink=0.7)

    im = ax[1, 2].imshow(phi_bi[:, cb, :].T, origin='lower', cmap='twilight', norm=norm, aspect='equal')
    ax[1, 2].set_title('Bi phi, XZ-slice', fontsize=10)
    plt.colorbar(im, ax=ax[1, 2], shrink=0.7)

    gx, gy, gz = np.gradient(phi_bi)
    for g in (gx, gy, gz):
        g[:] = (g + np.pi) % (2*np.pi) - np.pi
    gmag = np.sqrt(gx*gx + gy*gy + gz*gz)
    im = ax[1, 3].imshow(gmag.sum(axis=1).T, origin='lower', cmap='viridis', aspect='equal')
    ax[1, 3].set_title('Bi |grad phi|, Y-projected', fontsize=10)
    plt.colorbar(im, ax=ax[1, 3], shrink=0.7)

    fig.suptitle('Single ring (GPU-031f, R=4, L=20) vs Bi-ring bound (GPU-032b, d=4, L=24) — Option G',
                 fontsize=12, y=0.995)
    fig.tight_layout()
    fig.savefig(outpath, dpi=130, bbox_inches='tight')
    plt.close(fig)


def fft_analysis(series, dt, label):
    """Return (freqs, power, dominant_freq, dominant_power_frac)."""
    n = len(series)
    f = np.fft.rfftfreq(n, d=dt)
    F = np.fft.rfft(series - np.mean(series))
    P = np.abs(F) ** 2
    # Skip DC
    idx_max = 1 + np.argmax(P[1:])
    dom_f = f[idx_max]
    dom_power_frac = P[idx_max] / P[1:].sum()
    return f, P, dom_f, dom_power_frac


def plot_fourier(series_dict, outpath):
    """Option H: Fourier spectra of M_total series for single vs bi d=3,4,6."""
    fig, ax = plt.subplots(2, 1, figsize=(11, 7))

    colors = {'single_R4': '#000000', 'bi_d3': '#1f77b4',
              'bi_d4': '#d62728', 'bi_d6': '#2ca02c'}
    labels = {'single_R4': 'Single R=4 (ref)', 'bi_d3': 'Bi d=3',
              'bi_d4': 'Bi d=4 (bound)', 'bi_d6': 'Bi d=6 (near unbound)'}

    results = {}
    for name, data in series_dict.items():
        t = data['t']; m = data['m']
        dt = float(t[1] - t[0])
        f, P, dom_f, dom_frac = fft_analysis(m, dt, name)
        dom_period = 1.0 / dom_f if dom_f > 0 else float('inf')
        results[name] = {
            'dominant_freq': float(dom_f),
            'dominant_period_lu': float(dom_period),
            'dominant_power_frac': float(dom_frac),
            'mean_M': float(np.mean(m)),
            'std_M': float(np.std(m)),
        }

        # Plot time series (top)
        ax[0].plot(t, m, color=colors[name], alpha=0.6, linewidth=0.8,
                   label=f'{labels[name]} (mean={np.mean(m):.0f})')

        # Plot power spectrum, x in period domain (bottom)
        # avoid f=0; x-axis is period = 1/f
        mask = (f > 0.001) & (f < 0.05)  # period range 20..1000 lu
        periods = 1.0 / f[mask]
        ax[1].semilogy(periods, P[mask], color=colors[name], linewidth=1.3,
                       label=f'{labels[name]} (T_peak={dom_period:.1f} lu, frac={dom_frac:.2f})')

    ax[0].set_xlabel('t (lu)'); ax[0].set_ylabel('M_total')
    ax[0].set_title('M_total(t) time series — single vs bi')
    ax[0].grid(alpha=0.3); ax[0].legend(fontsize=9, loc='upper right')

    ax[1].set_xlabel('Period (lu)'); ax[1].set_ylabel('Power (log)')
    ax[1].set_title('Fourier power spectrum — dominant periods')
    ax[1].grid(alpha=0.3); ax[1].legend(fontsize=9, loc='upper right')
    ax[1].set_xlim([20, 1000])
    ax[1].invert_xaxis()

    fig.suptitle('Option H — Spectral signature: single vs bi-ring (bound vs unbound)',
                 fontsize=12, y=0.995)
    fig.tight_layout()
    fig.savefig(outpath, dpi=130, bbox_inches='tight')
    plt.close(fig)
    return results


def main():
    root = Path(__file__).resolve().parents[2]
    outdir = root / "07_validation" / "audits" / "qng-bi-ring-quick-analysis-v1"
    outdir.mkdir(parents=True, exist_ok=True)

    # Paths
    single_final = root / "07_validation/audits/qng-v8-r1-long-time-v1/final_state.npz"
    bi_d3_final = root / "07_validation/audits/qng-v8-r1-bi-ring-v3-d3/final_state.npz"
    bi_d4_final = root / "07_validation/audits/qng-v8-r1-bi-ring-v2-d4/final_state.npz"
    bi_d6_final = root / "07_validation/audits/qng-v8-r1-bi-ring-v1/final_state.npz"

    single_series = root / "07_validation/audits/qng-v8-r1-long-time-v1/m_series.npz"
    bi_d3_series  = root / "07_validation/audits/qng-v8-r1-bi-ring-v3-d3/m_series.npz"
    bi_d4_series  = root / "07_validation/audits/qng-v8-r1-bi-ring-v2-d4/m_series.npz"
    bi_d6_series  = root / "07_validation/audits/qng-v8-r1-bi-ring-v1/m_series.npz"

    # (F) 3D bound state
    print("[F] Plotting 3D bound state (d=4)...")
    st_bi_d4 = load_final(bi_d4_final)
    plot_bound_state_3d(st_bi_d4, L=24, outpath=outdir / "F_bound_state_d4_3d.png")
    print(f"    saved {outdir / 'F_bound_state_d4_3d.png'}")

    # (G) side-by-side single vs bi
    print("[G] Plotting single vs bi comparison...")
    st_single = load_final(single_final)
    plot_single_vs_bi(st_single, L_single=20, st_bi_d4=st_bi_d4, L_bi=24,
                      outpath=outdir / "G_single_vs_bi.png")
    print(f"    saved {outdir / 'G_single_vs_bi.png'}")

    # (H) Fourier
    print("[H] Computing Fourier spectra...")
    # Load time series: single has m_p1, m_p2 (GPU-031f schema)
    single_s = load_m_series(single_series)
    bi_d3_s  = load_m_series(bi_d3_series)
    bi_d4_s  = load_m_series(bi_d4_series)
    bi_d6_s  = load_m_series(bi_d6_series)

    # Use Phase 2 only (the long run)
    series_dict = {
        'single_R4': {'t': single_s['t_p2'], 'm': single_s['m_p2']},
        'bi_d3':     {'t': bi_d3_s['t_p2'],  'm': bi_d3_s['m_p2']},
        'bi_d4':     {'t': bi_d4_s['t_p2'],  'm': bi_d4_s['m_p2']},
        'bi_d6':     {'t': bi_d6_s['t_p2'],  'm': bi_d6_s['m_p2']},
    }
    fft_results = plot_fourier(series_dict, outpath=outdir / "H_fourier.png")
    print(f"    saved {outdir / 'H_fourier.png'}")

    print("\n[H] Fourier summary:")
    print(f"{'run':>12s}  {'mean':>9s}  {'std':>7s}  {'peak_period(lu)':>16s}  {'power_frac':>10s}")
    print("-" * 70)
    for name, r in fft_results.items():
        print(f"{name:>12s}  {r['mean_M']:>+9.2f}  {r['std_M']:>7.1f}  "
              f"{r['dominant_period_lu']:>16.1f}  {r['dominant_power_frac']:>10.3f}")

    with open(outdir / "fourier_report.json", "w") as f:
        json.dump(fft_results, f, indent=2)

    print("\nAll outputs in:", outdir)


if __name__ == "__main__":
    main()
