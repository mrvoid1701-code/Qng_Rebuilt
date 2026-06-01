"""QNG-CPU-109 -- SI unit conversion with hbar_QNG FIXED at 0.233.

With hbar_QNG derived structurally (DER-QNG-065 via zero-point balance +
thermodynamic limit, CPU-108 L-scan verified), we now have 3 natural constants:
  c_QNG = 0.1080  (from Einstein correspondence, verified NOTE-QNG-025)
  G_QNG = 0.0583  (from Newtonian limit, DER-QNG-019)
  hbar_QNG = 0.2326  (from vacuum energy balance, DER-QNG-065)

Match these to SI values of c, G, hbar:
  c_SI = 2.998e8 m/s
  G_SI = 6.674e-11 m^3/(kg*s^2)
  hbar_SI = 1.055e-34 J*s = kg*m^2/s

This is 3 equations, 3 unknowns (a_L, a_T, a_M). System FULLY DETERMINED
if consistent.

If a_L comes out near Planck length (1.6e-35 m), strong confirmation.
If a_L is ~lattice-atomic scale, also meaningful.
If a_L is physically absurd, something is wrong.
"""
import numpy as np

# Natural units (QNG)
c_QNG = 0.1080  # from c_phi^2 = beta_phi/(6*mu_phi)
G_QNG = 0.0583  # from G = beta_g/z
hbar_QNG = 0.232637  # from DER-QNG-065 thermodynamic limit

# SI target values
c_SI = 2.998e8  # m/s
G_SI = 6.674e-11  # m^3/(kg*s^2)
hbar_SI = 1.055e-34  # J*s = kg*m^2/s

print("=" * 72)
print("QNG-CPU-109: SI conversion with hbar_QNG fixed at 0.233")
print("=" * 72)
print()
print(f"QNG natural:  c = {c_QNG}, G = {G_QNG}, hbar = {hbar_QNG}")
print(f"SI target:    c = {c_SI:.3e}, G = {G_SI:.3e}, hbar = {hbar_SI:.3e}")
print()

# System of 3 equations:
# c_SI = c_QNG * (a_L / a_T)           [eq 1]
# G_SI = G_QNG * (a_L^3 / (a_M * a_T^2))   [eq 2]
# hbar_SI = hbar_QNG * (a_M * a_L^2 / a_T)  [eq 3]

# From (1): a_L/a_T = c_SI/c_QNG = R
R = c_SI / c_QNG
print(f"R = c_SI / c_QNG = {R:.4e} m/s  (velocity scale)")

# From (3): a_M * a_L^2 / a_T = hbar_SI / hbar_QNG
# Equivalently: a_M * a_L * R = hbar_SI / hbar_QNG  (using a_L/a_T = R)
# So: a_M * a_L = (hbar_SI / hbar_QNG) / R = Q_h
Q_h = hbar_SI / hbar_QNG / R
print(f"Q_h = hbar_SI/(hbar_QNG*R) = a_M * a_L = {Q_h:.4e} kg*m")

# From (2): a_L^3 / (a_M * a_T^2) = G_SI / G_QNG
# Use a_T = a_L/R: a_T^2 = a_L^2/R^2
# a_L^3 / (a_M * a_L^2/R^2) = a_L * R^2 / a_M = G_SI/G_QNG
# So a_L / a_M = G_SI/(G_QNG * R^2) = Q_G
Q_G = G_SI / (G_QNG * R**2)
print(f"Q_G = G_SI/(G_QNG*R^2) = a_L/a_M = {Q_G:.4e} m/kg")

# Now we have:
# a_M * a_L = Q_h
# a_L / a_M = Q_G
# Multiplying: a_L^2 = Q_h * Q_G → a_L = sqrt(Q_h * Q_G)
# Dividing: a_M^2 = Q_h / Q_G → a_M = sqrt(Q_h / Q_G)
a_L = np.sqrt(Q_h * Q_G)
a_M = np.sqrt(Q_h / Q_G)
a_T = a_L / R

print()
print(f"SOLUTION:")
print(f"  a_L = {a_L:.4e} m")
print(f"  a_T = {a_T:.4e} s")
print(f"  a_M = {a_M:.4e} kg")

# Compare to Planck scale
l_P = 1.616e-35  # m
t_P = 5.391e-44  # s
m_P = 2.176e-8   # kg

print()
print(f"Planck scale comparison:")
print(f"  a_L / l_P = {a_L/l_P:.4f}  (expect ~1 if QNG lattice = Planck)")
print(f"  a_T / t_P = {a_T/t_P:.4f}")
print(f"  a_M / m_P = {a_M/m_P:.4e}")

# Compare to proton mass
m_proton = 1.673e-27  # kg
print(f"  a_M / m_proton = {a_M/m_proton:.4e}")

# Check: do these values self-consistently reproduce SI constants?
print()
print(f"Self-consistency check:")
c_recomputed = c_QNG * a_L / a_T
G_recomputed = G_QNG * a_L**3 / (a_M * a_T**2)
hbar_recomputed = hbar_QNG * a_M * a_L**2 / a_T
print(f"  c_recomputed  = {c_recomputed:.4e} m/s     (target {c_SI:.4e})  match: {c_recomputed/c_SI:.6f}")
print(f"  G_recomputed  = {G_recomputed:.4e} m^3/kg s^2  (target {G_SI:.4e})  match: {G_recomputed/G_SI:.6f}")
print(f"  hbar_recomp   = {hbar_recomputed:.4e} J*s     (target {hbar_SI:.4e})  match: {hbar_recomputed/hbar_SI:.6f}")

print()
print("Interpretation:")
print(f"  Lattice spacing: {a_L*1e15:.3f} fm = {a_L*1e9:.3e} nm")
print(f"  Time step: {a_T*1e18:.3f} as (attoseconds)")
print(f"  Mass per node: {a_M/m_proton:.4e} proton masses")

# Is this physically meaningful?
print()
print("Physical interpretation:")
if 1e-35 < a_L < 1e-20:
    print(f"  a_L is between Planck length ({l_P:.2e} m) and nuclear scale (1e-15 m)")
elif a_L < 1e-35:
    print(f"  a_L is sub-Planck — problematic")
else:
    print(f"  a_L is supra-nuclear — odd")

if a_M > 1e-60 and a_M < 1e60:
    print(f"  a_M is physically scaled")
else:
    print(f"  a_M extreme")
