"""QNG time visualization — status and structure of time."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

OUTDIR = "scripts/figures_2026_04_26"
os.makedirs(OUTDIR, exist_ok=True)

fig = plt.figure(figsize=(15, 10))

# Subplot 1: Lattice + continuous time (top-left)
ax1 = fig.add_subplot(2, 2, 1)
ax1.set_title('QNG Current: Discrete Space, Continuous Time', fontsize=11, weight='bold')

# Draw lattice nodes (5x5)
for x in range(5):
    for y in range(5):
        ax1.plot(x, y, 'o', color='steelblue', markersize=12)
        if x < 4:
            ax1.plot([x, x+1], [y, y], 'gray', alpha=0.3, linewidth=1)
        if y < 4:
            ax1.plot([x, x], [y, y+1], 'gray', alpha=0.3, linewidth=1)

# Time axis on right
ax1.annotate('', xy=(5, 4.5), xytext=(5, 0),
             arrowprops=dict(arrowstyle='->', color='red', lw=3))
ax1.text(5.3, 2.5, 'TIME\n(continuum)', rotation=270, ha='center', va='center',
         fontsize=11, color='darkred', weight='bold')

ax1.set_xlim(-0.5, 6)
ax1.set_ylim(-0.5, 5)
ax1.set_xlabel('x (lattice)', fontsize=10)
ax1.set_ylabel('y (lattice)', fontsize=10)
ax1.text(2, -0.3, 'Δx = a_L = 0.305 ℓ_P', ha='center', fontsize=9, color='darkblue')
ax1.set_aspect('equal')


# Subplot 2: Light cone emergent (top-right)
ax2 = fig.add_subplot(2, 2, 2)
ax2.set_title('QNG Light Cone (emergent at large scales)', fontsize=11, weight='bold')

# Future light cone
t = np.linspace(0, 2, 100)
ax2.fill_between([-2, 2], -2, 2, alpha=0.05, color='gray')
ax2.fill_betweenx(t, -t, t, alpha=0.3, color='blue', label='Future light cone')
ax2.fill_betweenx(-t, -t, t, alpha=0.3, color='red', label='Past light cone')
ax2.plot([0], [0], 'ko', markersize=12, label='YOU NOW')

ax2.set_xlim(-2, 2)
ax2.set_ylim(-2, 2)
ax2.set_xlabel('x (space, comoving)', fontsize=10)
ax2.set_ylabel('t (time)', fontsize=10)
ax2.legend(loc='lower left', fontsize=9)
ax2.axhline(0, color='black', linewidth=0.5)
ax2.axvline(0, color='black', linewidth=0.5)
ax2.set_aspect('equal')
ax2.text(0, 1.5, 'c emergent\nfrom β_φ/(zμ_φ)', ha='center', va='center',
         fontsize=9, style='italic', color='darkblue')


# Subplot 3: Big Bang regularization (bottom-left)
ax3 = fig.add_subplot(2, 2, 3)
ax3.set_title('Big Bang in QNG: Lattice Regulates Singularity', fontsize=11, weight='bold')

t_log = np.linspace(-50, 18, 300)
# Standard density
rho_standard = 1 / np.maximum(t_log + 50, 1e-10)**2
# QNG with cutoff
rho_QNG = np.copy(rho_standard)
rho_QNG[t_log < -45.2] = np.nan  # cutoff at log(a_T)

ax3.semilogy(t_log, rho_standard, 'b--', label='Standard GR (singular)', linewidth=2)
ax3.semilogy(t_log, rho_QNG, 'r-', label='QNG (lattice cutoff)', linewidth=2)
ax3.axvline(-45.2, color='red', linestyle=':', linewidth=2, label='a_T = 1.78×10⁻⁴⁵ s')
ax3.axvline(0, color='gray', linestyle='--', alpha=0.5, label='1 second')
ax3.axvline(17, color='black', linestyle='--', alpha=0.5, label='today (4×10¹⁷ s)')

ax3.set_xlabel('log₁₀(t) [seconds since Big Bang]', fontsize=10)
ax3.set_ylabel('Density (arbitrary)', fontsize=10)
ax3.legend(fontsize=9, loc='upper right')
ax3.text(-30, 1e30, 'Sub-a_T:\nNO PHYSICS\n(time undefined)', ha='center', va='center',
         fontsize=10, color='darkred', weight='bold',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='mistyrose', edgecolor='red'))
ax3.grid(alpha=0.3)


# Subplot 4: Time scales (bottom-right)
ax4 = fig.add_subplot(2, 2, 4)
ax4.set_title('Time Scales — Planck to Cosmological', fontsize=11, weight='bold')

scales = [
    ('a_T (QNG)', 1.78e-45, 'red'),
    ('Planck time', 5.39e-44, 'red'),
    ('GUT epoch', 1e-37, 'orange'),
    ('Electroweak', 1e-12, 'orange'),
    ('1 microsecond', 1e-6, 'green'),
    ('1 second', 1, 'green'),
    ('1 day', 86400, 'blue'),
    ('1 year', 3.15e7, 'blue'),
    ('Solar System age', 1.4e17, 'darkblue'),
    ('Universe age', 4.35e17, 'purple'),
    ('Heat death (~10^100 yr)', 3e107, 'magenta'),
]

y = 0
for name, t_s, color in scales:
    ax4.barh(y, t_s, left=t_s*0.1, height=0.6, color=color, alpha=0.7)
    log_t = np.log10(t_s)
    ax4.text(t_s*5, y, f'{name} ({t_s:.2e} s)', va='center', fontsize=8)
    y += 1

ax4.set_xscale('log')
ax4.set_xlim(1e-46, 1e110)
ax4.set_yticks([])
ax4.set_xlabel('time (seconds)', fontsize=10)
ax4.axvline(1.78e-45, color='red', linestyle='--', linewidth=1.5, label='QNG a_T')
ax4.axvline(4.35e17, color='black', linestyle='--', linewidth=1.5, label='today')
ax4.legend(loc='upper right', fontsize=8)


# Overall title
fig.suptitle('QNG: Status and Structure of Time', fontsize=14, weight='bold', y=0.99)

plt.tight_layout()
plt.savefig(f"{OUTDIR}/fig11_time_in_QNG.png", dpi=120, bbox_inches='tight')
plt.close()

print(f"Generated: {OUTDIR}/fig11_time_in_QNG.png")
print()
print("Visualization shows:")
print("  Top-left: discrete space + continuous time (current QNG)")
print("  Top-right: light cone emergent at large scales")
print("  Bottom-left: Big Bang regularization (a_T cutoff)")
print("  Bottom-right: time scale ladder Planck → heat death")
