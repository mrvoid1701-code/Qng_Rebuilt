"""QNG visualization — what exists below Planck (vs other theories).

Generates: fig9_subplanck_ontology.png
Shows the radical QNG position: nothing exists below a_L.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

OUTDIR = "scripts/figures_2026_04_26"
os.makedirs(OUTDIR, exist_ok=True)

fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# Left: comparison of theories
ax = axes[0]
theories = ['GR\n(continuum)', 'String\ntheory', 'LQG', 'CDT', 'QNG']
colors = ['lightblue', 'lightyellow', 'lightgreen', 'lightcoral', 'gold']
y_positions = [4, 3, 2, 1, 0]

# Length scales (log)
scales_data = [
    # (theory_idx, scales_visible)
    (4, ['nothing\nbelow a_L', 'a_L = 0.305 ℓ_P', 'lattice nodes', 'continuum emerges']),  # QNG
    (1, ['Big Bang', 'Singularities', 'all scales', 'Smooth continuum']),  # GR
    (3, ['vibrating strings', 'l_string ~ ℓ_P', 'stringy regime', 'continuum approx']),  # String
    (2, ['discrete spin nets', 'area cuant', 'discrete', 'continuum approx']),  # LQG
    (1, ['triangulations', 'discrete', 'discrete', 'continuum emerges']),  # CDT
]

ax.set_xlim(-37, -29)
ax.set_ylim(-0.5, 4.5)
ax.set_xlabel('log₁₀(length) [m]', fontsize=12)
ax.set_yticks(y_positions)
ax.set_yticklabels(theories, fontsize=12)
ax.axvline(np.log10(1.616e-35), color='black', linestyle='--', linewidth=2, label='Planck length')
ax.axvline(np.log10(4.93e-36), color='red', linestyle='--', linewidth=2, label='QNG a_L = 0.305 ℓ_P')

# Shading
ax.axvspan(-37, np.log10(4.93e-36), alpha=0.2, color='red')
ax.text(-36.5, 4.5, 'NOTHING\n(in QNG)', ha='center', va='top', fontsize=11, color='darkred', fontweight='bold')

ax.axvspan(np.log10(4.93e-36), np.log10(1.616e-35), alpha=0.15, color='gold')
ax.text(np.log10(1e-35), 4.5, 'QNG\nlattice', ha='center', va='top', fontsize=10, color='goldenrod')

ax.axvspan(np.log10(1.616e-35), -29, alpha=0.05, color='blue')
ax.text(-31, 4.5, 'continuum\nemergent', ha='center', va='top', fontsize=10, color='darkblue')

ax.legend(loc='lower right', fontsize=9)
ax.set_title('Theories: what exists below Planck?', fontsize=12)
ax.grid(alpha=0.3)


# Right: QNG-specific Lego analogy
ax = axes[1]
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Draw lattice nodes (Lego analogy)
for x in [2, 4, 6, 8]:
    for y in [2, 4, 6, 8]:
        circle = plt.Circle((x, y), 0.35, color='steelblue', alpha=0.8, ec='black')
        ax.add_patch(circle)
        # Connection to right neighbor
        if x < 8:
            ax.plot([x+0.35, x+1.65], [y, y], 'gray', linewidth=1)
        if y < 8:
            ax.plot([x, x], [y+0.35, y+1.65], 'gray', linewidth=1)

# Label one node
ax.annotate('Node\n(σ_g, σ_m, χ, φ)', xy=(2, 2), xytext=(0.5, 0.5),
            arrowprops=dict(arrowstyle='->', lw=1.5),
            fontsize=10, color='darkblue')

# Label space "between" nodes
ax.annotate('NOTHING\n(no ontology\nbelow a_L)', xy=(3, 3), xytext=(5.5, 3.5),
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
            fontsize=11, color='darkred', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='mistyrose', edgecolor='red'))

# Lattice scale annotation
ax.annotate('', xy=(2, 1), xytext=(4, 1),
            arrowprops=dict(arrowstyle='<->', lw=1.5, color='green'))
ax.text(3, 0.6, 'a_L = 0.305 ℓ_P', ha='center', fontsize=10, color='darkgreen', fontweight='bold')

ax.set_title('QNG Ontology: Lattice IS Reality\nBetween nodes = no concept of space', fontsize=12)

plt.tight_layout()
plt.savefig(f"{OUTDIR}/fig9_subplanck_ontology.png", dpi=120)
plt.close()

print(f"Generated: {OUTDIR}/fig9_subplanck_ontology.png")
print()
print("Visualization shows:")
print("  Left: comparison of QG theories — what each says about sub-Planck")
print("  Right: QNG Lego analogy — lattice IS reality, between nodes = NOTHING")
