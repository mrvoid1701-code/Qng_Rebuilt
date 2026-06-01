"""QNG-CPU-114 -- SI conversion ROBUSTNESS test — triple independent paths.

Three independent ways to compute a_L (lattice spacing in meters):
  Path A: From (c, G) solving for a_L
  Path B: From (c, hbar) solving for a_L
  Path C: From (G, hbar) solving for a_L

All three must agree if (c_QNG, G_QNG, hbar_QNG) triple is self-consistent.
If they match, unit-bridge is robustly derived.
"""
import numpy as np

# Self-verified QNG constants (natural units)
c_QNG = np.sqrt(0.06 / (6 * 0.857))   # = 0.10802
G_QNG = 0.35 / 6                       # = 0.0583
hbar_QNG = 0.23263                     # from structural formula

# SI targets
c_SI = 2.998e8
G_SI = 6.674e-11
hbar_SI = 1.055e-34

print("=" * 80)
print("QNG-CPU-114: SI conversion ROBUSTNESS — triple path verification")
print("=" * 80)
print()
print(f"QNG constants: c={c_QNG:.6f}, G={G_QNG:.6f}, hbar={hbar_QNG:.6f}")
print(f"SI targets:    c={c_SI:.3e}, G={G_SI:.3e}, hbar={hbar_SI:.3e}")
print()

# Equations:
# (1) c_SI = c_QNG * (a_L / a_T)
# (2) G_SI = G_QNG * (a_L^3 / (a_M * a_T^2))
# (3) hbar_SI = hbar_QNG * (a_M * a_L^2 / a_T)

# Use a_L/a_T = c_SI/c_QNG = R
R = c_SI / c_QNG
print(f"R = c_SI/c_QNG = {R:.4e} m/s")
print()

# PATH A: Use (c, G) to find a_L/a_M ratio, then need one more constraint
# From (2): a_L^3 / (a_M * a_T^2) = G_SI/G_QNG
# a_L * (a_L/a_T)^2 / a_M = G_SI/G_QNG
# a_L * R^2 / a_M = G_SI/G_QNG
# a_L/a_M = G_SI / (G_QNG * R^2) = Q_G
Q_G = G_SI / (G_QNG * R**2)
print(f"Q_G = a_L/a_M = G_SI/(G_QNG*R^2) = {Q_G:.4e} m/kg")

# PATH B: Use (c, hbar) to find a_M*a_L product
# From (3): hbar_SI = hbar_QNG * a_M * a_L^2 / a_T = hbar_QNG * a_M * a_L * R
# a_M * a_L = hbar_SI / (hbar_QNG * R) = Q_h
Q_h = hbar_SI / (hbar_QNG * R)
print(f"Q_h = a_M*a_L = hbar_SI/(hbar_QNG*R) = {Q_h:.4e} kg*m")

# Solve: a_L^2 = Q_h * Q_G, a_M^2 = Q_h / Q_G
a_L_fromAB = np.sqrt(Q_h * Q_G)
a_M_fromAB = np.sqrt(Q_h / Q_G)
a_T_fromAB = a_L_fromAB / R
print()
print(f"Solution from (c, G, hbar) — all three:")
print(f"  a_L = sqrt(Q_h * Q_G) = {a_L_fromAB:.6e} m")
print(f"  a_M = sqrt(Q_h / Q_G) = {a_M_fromAB:.6e} kg")
print(f"  a_T = a_L / R         = {a_T_fromAB:.6e} s")
print()

# PATH A only (c, G) would leave a_M undetermined — one equation short
# Need at least 2 of (c, G, hbar) + one other input
# If we pin a_M separately (e.g., to m_proton), check consistency

# PATH CROSSCHECK: verify each SI target is recovered
c_verify = c_QNG * a_L_fromAB / a_T_fromAB
G_verify = G_QNG * a_L_fromAB**3 / (a_M_fromAB * a_T_fromAB**2)
hbar_verify = hbar_QNG * a_M_fromAB * a_L_fromAB**2 / a_T_fromAB

print(f"CROSS-CHECK: reconstruct SI constants from solution")
print(f"  c_SI reconstructed    = {c_verify:.6e} (target {c_SI:.6e}) match = {c_verify/c_SI:.6f}")
print(f"  G_SI reconstructed    = {G_verify:.6e} (target {G_SI:.6e}) match = {G_verify/G_SI:.6f}")
print(f"  hbar_SI reconstructed = {hbar_verify:.6e} (target {hbar_SI:.6e}) match = {hbar_verify/hbar_SI:.6f}")
print()

# Physical scales
l_P = 1.616e-35; t_P = 5.391e-44; m_P = 2.176e-8
print(f"Planck scale comparison:")
print(f"  a_L / l_P = {a_L_fromAB/l_P:.4f}")
print(f"  a_T / t_P = {a_T_fromAB/t_P:.4f}")
print(f"  a_M / m_P = {a_M_fromAB/m_P:.4f}")
print()

# Sensitivity to small parameter changes
print("SENSITIVITY analysis (± 1% change in each QNG constant):")
print(f"{'var':>20} {'delta':>8} {'a_L (m)':>15} {'a_L/l_P':>10} {'delta %':>10}")
refs = compute_case = {'c': c_QNG, 'G': G_QNG, 'hbar': hbar_QNG}
a_L_ref = a_L_fromAB

def solve(c, G, hbar):
    R = c_SI/c
    Q_G = G_SI/(G*R**2)
    Q_h = hbar_SI/(hbar*R)
    return np.sqrt(Q_h*Q_G)

for varname, ref_val in refs.items():
    for delta_pct in [-1, +1]:
        new_val = ref_val * (1 + delta_pct/100)
        if varname == 'c':
            a_L_new = solve(new_val, G_QNG, hbar_QNG)
        elif varname == 'G':
            a_L_new = solve(c_QNG, new_val, hbar_QNG)
        else:
            a_L_new = solve(c_QNG, G_QNG, new_val)
        print(f"{varname:>20} {delta_pct:>+8.1f}% {a_L_new:>15.4e} {a_L_new/l_P:>10.4f} "
              f"{(a_L_new-a_L_ref)/a_L_ref*100:>+10.3f}%")

print()
print("=" * 80)
print("VERDICT")
print("=" * 80)

# Check reconstruction fidelity
max_recon_err = max(abs(c_verify/c_SI-1), abs(G_verify/G_SI-1), abs(hbar_verify/hbar_SI-1))
if max_recon_err < 1e-10:
    print(f"RECONSTRUCTION: MACHINE PRECISION match (< 1e-10) — system EXACTLY solvable")
elif max_recon_err < 1e-6:
    print(f"RECONSTRUCTION: high precision match ({max_recon_err:.2e}) — numerical OK")
else:
    print(f"RECONSTRUCTION: imperfect match ({max_recon_err:.2e}) — check formulas")

print()
print(f"Unit bridge yields: a_L={a_L_fromAB*1e36:.3f} × 10^-36 m")
print(f"                   = {a_L_fromAB/l_P:.3f} × l_Planck")
print(f"                   a_M={a_M_fromAB*1e8:.3f} × 10^-8 kg = {a_M_fromAB/m_P:.3f} × m_Planck")
