"""QNG-CPU-FLRW-2 — DYNAMIC σ_g regime (cosmological α << H²).

KEY INSIGHT: for cosmological alpha ~ 10^{-124} (Planck units), and Hubble
rate H_0 ~ 10^{-60} (Planck units), we have α/μ_g << H². So σ_g is NOT
in adiabatic/static limit — it has independent slow evolution.

In this regime: σ_g equation becomes
  μ_g σ_g'' + α(σ_g - σ_ref) = -k_gm ρ_m
                                ≈ -k_gm ρ_m  (α negligible at ρ_m large)

For matter dominated phase (a ∝ t^(2/3)):
  ρ_m ∝ t^-2
  σ_g'' ∝ t^-2
  σ_g'(t) = C/t + D  (D = integration constant)
  σ_g(t) = C ln(t) + D*t + E

Energy in σ_g sector:
  ρ_σg = (μ_g/2)(σ_g')² + (α/2)(σ_g - σ_ref)²
       ≈ (μ_g/2)(C/t + D)²

As t → ∞: ρ_σg → (μ_g/2)D² (CONSTANT, like Λ!)

This is a candidate mechanism for QNG cosmological constant.

Goal: verify numerically + check scales.
"""
import numpy as np
from scipy.integrate import solve_ivp

print("=" * 80)
print("QNG-CPU-FLRW-2: Dynamic σ_g regime — Λ from late-time D constant")
print("=" * 80)
print()

# In Planck units:
# alpha ~ 10^{-124}, mu_g ~ 1 (set by canonical structure)
# k_gm ~ 1 (set by σ_g - σ_m coupling normalization)
# H_0 ~ 10^{-60} (current Hubble rate)
# Universe age ~ 10^60 (Planck times)

# But for numerical work, use rescaled units:
# - Work in cosmological time units (1/H_0)
# - Scale alpha so alpha/mu_g matches the scale ratio

# Key dimensionless ratio: alpha/(mu_g * H_0^2)
# = 10^{-124} / 10^{-120} = 10^{-4}
# So alpha/mu_g = 10^{-4} * H_0^2

# In cosmological units (H_0 = 1, time in 1/H_0):
# alpha/mu_g = 10^{-4}

mu_g = 1.0
alpha_cosmological = 1e-4  # alpha/(mu_g H_0^2) ratio
k_gm = 1.0
sigma_ref = 1.0
Omega_m_today = 0.315  # matter density today (in critical density units)

# H_0 in cosmological units = 1 by definition
H0 = 1.0

# ============================================================
# Use a-grid as primary parameter
# ============================================================
# For matter+something dominated universe, a(t) determined by
# Friedmann eq once we know energy content.
# We'll INTEGRATE the QNG equation directly

# Matter density: rho_m(a) = Omega_m_today / a^3 (in critical density units = 3 H_0^2/(8 pi G))
# For H_0=1: rho_critical = 3/(8 pi G) ≈ const, set to rho_m_0 = Omega_m_today

# Standard matter-only cosmology:
# H^2 = (8 pi G / 3) rho_m = rho_m / rho_critical = Omega_m_today / a^3
# Note: in units H_0=1, this gives H = sqrt(Om/a^3), and at a=1: H = sqrt(Om) ≠ 1 unless Om=1.
# To have H_0=1 exactly: need Om_total = 1 in our units. So set:
Omega_m_use = 1.0  # all energy is matter (no Λ in baseline)
rho_m_0 = 1.0  # in units 3H_0^2/(8πG)

# In these units: H^2 = rho/rho_crit  (with rho_crit = 1)

# QNG σ_g equation in dimensionless form:
#   sigma_g'' + alpha_dim (sigma_g - 1) = -k_gm_dim * rho_m
# where alpha_dim = alpha/(mu_g H_0^2), k_gm_dim = k_gm/(mu_g H_0^2)

# We use alpha_dim = 1e-4 (cosmological), k_gm_dim = 1 (matched to ρ_m units)

# ============================================================
# Numerical integration: σ_g(t) given LCDM-matter background a(t)
# ============================================================
def H_pure_matter(a, Om_total=Omega_m_use):
    return np.sqrt(Om_total / a**3) * H0

def rho_m_of_a(a):
    return rho_m_0 / a**3

# Integrate σ_g'' + alpha (σ_g - 1) = -k_gm ρ_m
# Use a as proxy for time? Or use t directly?
# For matter-only: a(t) = (3 H_0 t / 2)^(2/3), so t = (2/3 H_0) a^(3/2)
def t_of_a(a):
    return (2.0/3.0) * a**(1.5) / H0

def da_dt(a):
    return a * H_pure_matter(a)

# Equations of motion in t:
def derivs(t, y):
    """y = [a, sigma_g, sigma_g_dot]"""
    a, sg, sg_dot = y
    if a < 1e-6:  # avoid singularity
        return [0, 0, 0]
    H = H_pure_matter(a)
    rho_m = rho_m_of_a(a)
    a_dot = a * H
    sg_ddot = -alpha_cosmological * (sg - sigma_ref) - k_gm * rho_m / mu_g
    return [a_dot, sg_dot, sg_ddot]

# Initial conditions at very early matter era
t0 = 1e-3  # in 1/H_0 units (very early)
a0 = (1.5 * H0 * t0)**(2.0/3.0)  # consistent with matter-dominated
sg0 = sigma_ref  # start at reference
sg_dot0 = 0.0  # start at rest (boundary condition)

print(f"Initial conditions at t = {t0}: a = {a0:.4f}, σ_g = {sg0}, σ_g_dot = {sg_dot0}")
print(f"Cosmological alpha_dim = {alpha_cosmological}")
print()

# Integrate from t0 to t_max (well past today)
t_max = 5.0
sol = solve_ivp(derivs, [t0, t_max], [a0, sg0, sg_dot0], dense_output=True,
                max_step=0.01, rtol=1e-10, atol=1e-13)

# Identify "today" as the time when a = 1
ts_eval = np.linspace(t0, t_max, 1000)
a_arr = sol.sol(ts_eval)[0]
sg_arr = sol.sol(ts_eval)[1]
sg_dot_arr = sol.sol(ts_eval)[2]

# Find t_today = t when a = 1
t_today_idx = np.argmin(np.abs(a_arr - 1.0))
t_today = ts_eval[t_today_idx]
print(f"t_today (when a=1): {t_today:.4f}")
print()

# ============================================================
# Compute energy density of σ_g sector
# ============================================================
print("=" * 80)
print("Energy density evolution: matter vs σ_g sector")
print("=" * 80)
print()

rho_m_arr = rho_m_0 / a_arr**3
rho_sg_kinetic = 0.5 * mu_g * sg_dot_arr**2
rho_sg_potential = 0.5 * alpha_cosmological * (sg_arr - sigma_ref)**2
rho_sg_total = rho_sg_kinetic + rho_sg_potential

print(f"{'a':>10} {'t':>10} {'rho_m':>12} {'rho_sg_kin':>12} {'rho_sg_pot':>12} {'rho_sg_tot':>12}")
for idx in [50, 200, t_today_idx, 800, 999]:
    print(f"{a_arr[idx]:>10.4f} {ts_eval[idx]:>10.4f} {rho_m_arr[idx]:>12.4e} {rho_sg_kinetic[idx]:>12.4e} {rho_sg_potential[idx]:>12.4e} {rho_sg_total[idx]:>12.4e}")
print()

# At late time, what's the ratio rho_sg / rho_critical_total?
print("=" * 80)
print("Late-time analysis: does σ_g produce effective Λ?")
print("=" * 80)
print()
print("At late times, if σ_g_dot → constant D, then:")
print("  rho_sg_kinetic = (μ_g/2) D²  (CONSTANT, Λ-like)")
print()
print(f"σ_g_dot at late times (a > 5):")
late_times = ts_eval > 4.5
late_sg_dots = sg_dot_arr[late_times]
print(f"  Mean: {np.mean(late_sg_dots):.6e}")
print(f"  Std:  {np.std(late_sg_dots):.6e}")
print(f"  Approaching constant? {np.std(late_sg_dots) < 0.1 * abs(np.mean(late_sg_dots))}")
print()

# ============================================================
# Compute "effective Λ" if σ_g_dot were constant at late times
# ============================================================
sg_dot_late_avg = np.mean(late_sg_dots)
rho_sg_kinetic_late = 0.5 * mu_g * sg_dot_late_avg**2

print(f"Inferred late-time σ_g_dot ≈ {sg_dot_late_avg:.4e}")
print(f"Inferred Λ-like contribution (μ_g σ_g_dot²/2) ≈ {rho_sg_kinetic_late:.4e}")
print()

# Compare to ρ_m_today
rho_m_at_today = rho_m_0  # at a=1
print(f"Compare to ρ_m at a=1: {rho_m_at_today:.4f}")
print(f"Ratio (rho_sg_kin_late / rho_m_today): {rho_sg_kinetic_late/rho_m_at_today:.4e}")
print()

# Compare with observed Ω_Λ/Ω_m = 0.685/0.315 = 2.17
print("Observed: Ω_Λ/Ω_m = 0.685/0.315 = 2.17")
print(f"QNG inferred: rho_sg/rho_m_today = {rho_sg_kinetic_late/rho_m_at_today:.4e}")
print()

# ============================================================
# Physical interpretation
# ============================================================
print("=" * 80)
print("PHYSICAL INTERPRETATION")
print("=" * 80)
print()
print("σ_g obeys: μ_g σ_g'' + α(σ_g - σ_ref) = -k_gm ρ_m(t)")
print()
print("Two distinct regimes:")
print()
print("1. EARLY UNIVERSE (matter era): ρ_m large, dominates equation.")
print("   σ_g pumped by matter gradient, σ_g_dot grows.")
print()
print("2. LATE UNIVERSE (matter dilutes): ρ_m → 0, equation becomes")
print("   μ_g σ_g'' + α(σ_g - σ_ref) ≈ 0  (free oscillation)")
print()
print("   With cosmological α = 10^{-4} H_0² (very small),")
print("   σ_g oscillates SLOWLY compared to Hubble.")
print("   σ_g_dot at end of matter era is ~ MEMORY of past matter forcing.")
print()
print("3. RESIDUAL ENERGY: (μ_g/2)(σ_g_dot)² acts as effective Λ.")
print("   This is INTRINSIC to QNG dynamics — not added by hand.")
print()

# ============================================================
# Status and next steps
# ============================================================
print("=" * 80)
print("STATUS — QNG-FLRW-2 CANDIDATE MECHANISM")
print("=" * 80)
print()
print("CANDIDATE: late-time σ_g_dot constant produces effective Λ")
print()
print("STILL TO DETERMINE:")
print("  (a) Numerical value of σ_g_dot_late and its dependence on")
print("      initial conditions, alpha, k_gm")
print("  (b) Whether this matches observed Ω_Λ ~ 0.685")
print("  (c) Whether this gives correct H(z) evolution")
print()
print("CRITICAL: σ_g_dot late-time value depends on the MATTER FORCING HISTORY.")
print("  Different initial conditions give different DE today.")
print("  Could be a clean prediction OR a fine-tuning problem.")
print()
print("NEXT STEPS:")
print("  - QNG-FLRW-3: scan over initial conditions, alpha, k_gm")
print("  - Compare predicted H(z) with eBOSS BAO")
print("  - Check if mechanism works WITHOUT fine-tuning")
print()
print("This is a PROMISING new direction for QNG cosmology.")
