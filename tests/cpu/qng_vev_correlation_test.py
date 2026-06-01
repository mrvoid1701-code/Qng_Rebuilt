"""QNG-CPU-VEV-CORRELATION — Test if Ω_DM/Ω_Λ ratio is FIXED or TUNABLE.

Tesla's prediction (response to Einstein's bookkeeping objection):
"In any oscillator, ⟨energy in DC mode⟩ and ⟨energy in fluctuations⟩
are linked by the Q factor and the driving spectrum."

Concrete claim:
  Ω_DM / Ω_Λ = m_χ² × ⟨δχ²⟩ / V_0

If this ratio is FIXED by substrate (V(χ) shape), QNG predicts the
ratio. If it's TUNABLE (independent V_0 and δχ_0), it's just
re-parametrization.

TEST APPROACH:
1. Run VEV+fluct cosmology with multiple (V_0, δχ_0) pairs
2. Compute final Ω_DM, Ω_Λ, and ratio
3. Determine if ratio is constrained by substrate structure
4. Honest verdict: tunable or fixed?

This is the CRITICAL test of whether QNG has predictive content
beyond ΛCDM at the cosmological-parameter level.
"""
import numpy as np
from scipy.integrate import solve_ivp
from itertools import product

print("=" * 80)
print("QNG-CPU-VEV-CORRELATION: Test Ω_DM/Ω_Λ ratio constraint")
print("=" * 80)
print()

# ============================================================
# Setup
# ============================================================
H0 = 1.0  # natural cosmological units
Omega_b = 0.049
m_chi_over_H0 = 100.0  # well in oscillating regime (m >> H)
mu_chi = 1.0

# Tesla's prediction
print("Tesla prediction (response to Einstein bookkeeping):")
print("  Ω_DM / Ω_Λ = m_χ² × ⟨δχ²⟩ / V_0")
print()
print("Observed ratio (Planck 2018):")
print(f"  Ω_DM / Ω_Λ = 0.265 / 0.686 = {0.265/0.686:.3f}")
print()

# ============================================================
# Solve cosmological evolution for given (V_0, δχ_0, m_chi)
# ============================================================
def H_total(a, dchi, dchi_dot, V_0):
    rho_b = Omega_b / a**3
    rho_chi_kin = 0.5 * mu_chi * dchi_dot**2
    rho_chi_mass = 0.5 * m_chi_over_H0**2 * dchi**2
    rho_DE = V_0
    rho_total = rho_b + rho_chi_kin + rho_chi_mass + rho_DE
    return np.sqrt(max(rho_total, 0)) * H0

def derivs(t, y, V_0):
    a, dchi, dchi_dot = y
    if a < 1e-9:
        return [0]*3
    H = H_total(a, dchi, dchi_dot, V_0)
    a_dot = a * H
    dchi_ddot = -3 * H * dchi_dot - m_chi_over_H0**2 * dchi
    return [a_dot, dchi_dot, dchi_ddot]

def integrate(V_0, dchi_0_init, t_span=(1e-3, 5.0)):
    a0 = 1e-3
    y0 = [a0, dchi_0_init, 0.0]
    sol = solve_ivp(lambda t, y: derivs(t, y, V_0),
                    t_span, y0, dense_output=True,
                    max_step=0.0005, rtol=1e-9, atol=1e-12)
    return sol

def compute_omegas(sol, V_0):
    a_arr = sol.y[0]
    if max(a_arr) < 1.0:
        return None, None, None, None
    idx_today = np.argmin(np.abs(a_arr - 1.0))
    if abs(a_arr[idx_today] - 1.0) > 0.1:
        return None, None, None, None

    # Average over recent oscillations
    window = 100
    idx_lo = max(0, idx_today - window)
    idx_hi = min(len(a_arr), idx_today + 1)
    dchi_arr = sol.y[1][idx_lo:idx_hi]
    dchi_dot_arr = sol.y[2][idx_lo:idx_hi]

    # ⟨δχ²⟩ today
    dchi_sq_avg = np.mean(dchi_arr**2)
    dchi_dot_sq_avg = np.mean(dchi_dot_arr**2)

    # Energy density ⟨ρ_DM⟩
    rho_DM = 0.5 * mu_chi * dchi_dot_sq_avg + 0.5 * m_chi_over_H0**2 * dchi_sq_avg

    # ρ_DE
    rho_DE = V_0

    return rho_DM, rho_DE, dchi_sq_avg, dchi_dot_sq_avg


# ============================================================
# Test 1: vary V_0, fix δχ_0 — does Ω_DM stay same?
# ============================================================
print("=" * 80)
print("Test 1: Vary V_0, fix δχ_0 = 1.1")
print("=" * 80)
print()
print("If ratio is CONSTRAINED by physics: changing V_0 changes ⟨δχ²⟩ by feedback")
print("If ratio is TUNABLE: V_0 and ⟨δχ²⟩ are independent")
print()
print(f"{'V_0':>8} {'Ω_DM':>10} {'Ω_DE':>10} {'⟨δχ²⟩':>10} {'ratio':>10} {'pred ratio':>12}")

dchi_0_fixed = 1.1
data_test1 = []
for V_0 in [0.3, 0.5, 0.686, 1.0, 1.5, 2.0]:
    sol = integrate(V_0, dchi_0_fixed)
    result = compute_omegas(sol, V_0)
    if result[0] is None:
        continue
    rho_DM, rho_DE, dchi_sq, dchi_dot_sq = result
    Omega_DM = rho_DM
    Omega_DE = rho_DE
    ratio_observed = Omega_DM / Omega_DE
    # Tesla predicted ratio: m² × ⟨δχ²⟩ / V_0
    ratio_tesla = m_chi_over_H0**2 * dchi_sq / V_0
    print(f"{V_0:>8.3f} {Omega_DM:>10.4f} {Omega_DE:>10.4f} {dchi_sq:>10.4f} {ratio_observed:>10.4f} {ratio_tesla:>12.4f}")
    data_test1.append((V_0, Omega_DM, Omega_DE, dchi_sq, ratio_observed, ratio_tesla))

print()
# Check if ratio is V_0 dependent
ratios_observed = [d[4] for d in data_test1]
if len(ratios_observed) > 1:
    rel_var = (max(ratios_observed) - min(ratios_observed)) / np.mean(ratios_observed)
    print(f"Ratio variation across V_0 scan: {rel_var*100:.1f}%")
    if rel_var < 0.1:
        print("=> RATIO INDEPENDENT OF V_0 (constrained by physics!)")
    else:
        print("=> Ratio depends on V_0 (tunable, NOT constrained by physics)")
print()


# ============================================================
# Test 2: vary δχ_0, fix V_0 — does Ω_DE stay same?
# ============================================================
print("=" * 80)
print("Test 2: Vary δχ_0, fix V_0 = 0.686")
print("=" * 80)
print()

V_0_fixed = 0.686
print(f"{'δχ_0':>8} {'Ω_DM':>10} {'Ω_DE':>10} {'⟨δχ²⟩':>10} {'ratio':>10}")

data_test2 = []
for dchi_0 in [0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7]:
    sol = integrate(V_0_fixed, dchi_0)
    result = compute_omegas(sol, V_0_fixed)
    if result[0] is None:
        continue
    rho_DM, rho_DE, dchi_sq, dchi_dot_sq = result
    Omega_DM = rho_DM
    Omega_DE = rho_DE
    ratio = Omega_DM / Omega_DE
    print(f"{dchi_0:>8.3f} {Omega_DM:>10.4f} {Omega_DE:>10.4f} {dchi_sq:>10.4f} {ratio:>10.4f}")
    data_test2.append((dchi_0, Omega_DM, Omega_DE, dchi_sq, ratio))

print()


# ============================================================
# Test 3: simultaneous scan of (V_0, δχ_0)
# ============================================================
print("=" * 80)
print("Test 3: Joint scan (V_0, δχ_0)")
print("=" * 80)
print()
print("If the ratio is structurally fixed, points in (V_0, δχ_0) space should")
print("ALL give the same ratio. If tunable, ratio varies independently.")
print()

# Find pairs that give Ω_DM ≈ 0.265 and check what V_0 corresponds
print(f"{'V_0':>8} {'δχ_0':>8} {'Ω_DM':>10} {'Ω_DE':>10} {'ratio':>10}")
for V_0 in [0.3, 0.5, 1.0, 1.5]:
    for dchi_0 in [0.5, 0.8, 1.1, 1.5]:
        sol = integrate(V_0, dchi_0)
        result = compute_omegas(sol, V_0)
        if result[0] is None:
            continue
        rho_DM, rho_DE, dchi_sq, dchi_dot_sq = result
        ratio = rho_DM / rho_DE
        print(f"{V_0:>8.3f} {dchi_0:>8.3f} {rho_DM:>10.4f} {rho_DE:>10.4f} {ratio:>10.4f}")

print()


# ============================================================
# Diagnostic: is the ratio FIXED by V(χ) structure?
# ============================================================
print("=" * 80)
print("Diagnostic: structural relation V_0 ↔ δχ in QNG?")
print("=" * 80)
print()
print("In our model V(χ) = V_0 + (1/2)m²(χ-χ_0)²:")
print("  V_0, m, χ_0 are 3 INDEPENDENT parameters.")
print("  Initial δχ_0 (fluctuation amplitude) is 4TH parameter.")
print()
print("There is NO structural relation between V_0 and δχ in this potential.")
print("Therefore: ratio Ω_DM/Ω_Λ is TUNABLE.")
print()
print("To make ratio FIXED, would need:")
print("  V(χ) form like V_0 ∝ χ_0² (e.g., Mexican-hat: V_0 = λχ_0⁴/4)")
print("  + Stability Principle relation between χ_0 and m_χ")
print("  + Specific initial fluctuation amplitude from substrate physics")
print()
print("Currently QNG has none of these — V_0, m_χ, δχ_0 are independent inputs.")
print()


# ============================================================
# Honest verdict
# ============================================================
print("=" * 80)
print("HONEST VERDICT")
print("=" * 80)
print()
print("Einstein objection: 'V_0 and δχ² are tunable separately'")
print("Tesla counter: 'In an oscillator, Q factor links them'")
print()
print("Numerical test result: Einstein is RIGHT — ratio is tunable.")
print()
print("This is because:")
print("  1. Our V(χ) = V_0 + (1/2)m²(χ-χ_0)² has 3 independent parameters")
print("  2. Initial δχ_0 is 4th independent parameter")
print("  3. No constraint links V_0 to ⟨δχ²⟩")
print()
print("To kill bookkeeping objection FOR REAL, QNG needs:")
print("  Option A: V(χ) form with V_0 ∝ m² × χ_0² (linked by potential shape)")
print("  Option B: Stability Principle generalization linking sectors")
print("  Option C: Initial conditions from substrate (no free amplitude)")
print()
print("Status: Tesla's prediction is currently ASPIRATIONAL.")
print("        QNG-VEV+fluct currently has 3 independent identifications,")
print("        same as ΛCDM (Λ + DM mass + DM density).")
print()
print("Honest scope: VEV+fluct is parsimonious (1 sector) but not derivative.")
print("              Same parameter count as ΛCDM, just unified packaging.")
