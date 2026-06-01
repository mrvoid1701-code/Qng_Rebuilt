"""QNG emergence chain visualization — from substrate to reality."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

OUTDIR = "scripts/figures_2026_04_26"
os.makedirs(OUTDIR, exist_ok=True)

fig, ax = plt.subplots(figsize=(14, 10))
ax.axis('off')

# Define layers from bottom (substrate) to top (cosmos)
layers = [
    (0, "LAYER 0: SUBSTRAT\nLattice cubic z=6 + 4 câmpuri (σ_g, σ_m, χ, φ)\nScale: a_L = 4.93×10⁻³⁶ m", '#1f4e79', 'white'),
    (1, "LAYER 1: COARSE-GRAINING\nCâmpuri continue (medierea peste noduri)\nScale: 10⁻³⁰ - 10⁻²⁰ m", '#2e75b6', 'white'),
    (2, "LAYER 2: SPAȚIU-TIMP EMERGENT\nMetric g_μν, Lorentz emergent (theorem)\nScale: 10⁻²⁰ - 10⁻¹⁵ m", '#5b9bd5', 'white'),
    (3, "LAYER 3: PARTICULE FUNDAMENTALE\nExcitații cuantice (graviton, photon, fermioni)\nScale: 10⁻¹⁵ m (Compton)", '#9dc3e6', 'black'),
    (4, "LAYER 4: ATOMI\nBound states + chimie\nScale: 10⁻¹⁰ m (Bohr)", '#bdd7ee', 'black'),
    (5, "LAYER 5: MATERIE MACROSCOPICĂ\nMolecule, solide, lichide, gaze\nScale: 10⁻⁹ m → 1 m", '#deebf7', 'black'),
    (6, "LAYER 6: ASTROFIZICĂ\nPlanete, stele, galaxii (Newton + GR + DM)\nScale: 10⁶ - 10²² m", '#fff2cc', 'black'),
    (7, "LAYER 7: UNIVERS OBSERVABIL\nCosmologie, structuri largi, CMB\nScale: 10²⁶ m (Hubble radius)", '#ffd966', 'black'),
]

# Draw layers as stacked rectangles
y_step = 0.115
y_start = 0.02

for layer_idx, (i, text, color, text_color) in enumerate(layers):
    y = y_start + i * y_step
    box = plt.Rectangle((0.05, y), 0.9, y_step * 0.9, facecolor=color, edgecolor='black', linewidth=1.5)
    ax.add_patch(box)
    ax.text(0.5, y + y_step*0.45, text, ha='center', va='center', fontsize=10, color=text_color, weight='bold' if i == 0 or i == 7 else 'normal')

# Add arrows on the right side showing emergence direction
for i in range(7):
    y1 = y_start + i * y_step + y_step * 0.9
    y2 = y_start + (i+1) * y_step
    ax.annotate('', xy=(0.97, y2 + 0.02), xytext=(0.97, y1 + 0.02),
                arrowprops=dict(arrowstyle='->', color='red', lw=2))

# Labels for emergence mechanisms (on the left)
mechanisms = [
    (0.05, "discrete cubic lattice"),
    (0.115, "long-wavelength averaging"),
    (0.230, "Lorentz emergence theorem"),
    (0.345, "QFT excitations + path integral"),
    (0.460, "QED + nuclear physics"),
    (0.575, "decoherence + thermodynamics"),
    (0.690, "GR + Newton + DM"),
    (0.805, "FLRW + structure formation"),
]

for y, mech in mechanisms[:-1]:
    next_y = mechanisms[mechanisms.index((y, mech)) + 1][0] if mechanisms.index((y, mech)) + 1 < len(mechanisms) else None

# Title and labels
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.text(0.5, 0.97, 'QNG Emergence Chain — From Lattice Substrate to Observed Reality',
        ha='center', va='center', fontsize=14, weight='bold')
ax.text(0.97, 0.5, '↑ EMERGENCE ↑', rotation=90, ha='center', va='center',
        fontsize=12, color='red', weight='bold')

# Side labels
ax.text(0.02, 0.05, 'Fundamental\nontology', rotation=90, ha='center', va='center',
        fontsize=10, style='italic', color='darkblue')
ax.text(0.02, 0.93, 'Observed\nreality', rotation=90, ha='center', va='center',
        fontsize=10, style='italic', color='goldenrod')

plt.tight_layout()
plt.savefig(f"{OUTDIR}/fig10_emergence_chain.png", dpi=120, bbox_inches='tight')
plt.close()

print(f"Generated: {OUTDIR}/fig10_emergence_chain.png")
print()
print("Visualization shows:")
print("  Bottom: QNG substrate (lattice cubic + 4 fields)")
print("  Top: Observed reality (universe, galaxies, planets, us)")
print("  7 layers of emergence with specific mechanisms each")
