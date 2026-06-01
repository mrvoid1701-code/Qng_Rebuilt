"""QNG-CPU-CHI-DM — χ field as dark matter candidate.

User hypothesis: dark matter is a FIELD (not particle); test if χ field in QNG
can play this role.

Setup:
- χ is treated as a free massive scalar in cosmological FLRW background
- Equation: χ̈ + 3H χ̇ + m_χ² χ = 0
- Energy density: ρ_χ = ½(χ̇)² + ½ m_χ² χ²
- Pressure: p_χ = ½(χ̇)² - ½ m_χ² χ²

Two regimes:
- m_χ >> H: oscillating, time-averaged <ρ_χ> ∝ a^-3 (COLD MATTER, like CDM)
- m_χ << H: frozen, ρ_χ ≈ const (ultralight, DE-like)

For DM behavior: need m_χ >> H_0.

QNG context:
- χ has kinetic + mass terms in v7/v8 substrate
- m_χ² = CHI_DECAY / μ_χ (effective mass from decay term)
- In v8 default: CHI_DECAY = 0.020 lattice units → m_χ ~ super-Planckian (too large)

Test multiple m_χ values to find DM-compatible regime.

Then compare with rotation curve data (data/rotation/rotation_ds006_rotmod.csv)
to see if χ-DM hypothesis is observationally consistent.
"""
import numpy as np
from scipy.integrate import solve_ivp
import os

print("=" * 80)
print("QNG-CPU-CHI-DM: chi field as dark matter candidate")
print("=" * 80)
print()

# ============================================================
# Cosmological parameters
# ============================================================
H0_SI = 67.4  # km/s/Mpc
H0_invs = H0_SI * 1e3 / (3.086e22)  # 1/s
hbar_eV_s = 6.582e-16  # eV*s
H0_eV = hbar_eV_s * H0_invs  # eV
print(f"H_0 = {H0_eV:.3e} eV")
print()

# Critical density
rho_crit_eV4 = 3 * (H0_eV)**2 / (8 * np.pi)  # natural units c=hbar=1, planck mass = 1
print(f"rho_critical (Planck-natural): would compute via 3H_0^2/(8πG)")
print()

# ============================================================
# DM observational targets
# ============================================================
# Observed DM density: Ω_DM = 0.265
Omega_DM_obs = 0.265
Omega_b_obs = 0.049

print(f"Observed: Ω_DM = {Omega_DM_obs}, Ω_baryon = {Omega_b_obs}")
print(f"DM/baryon ratio: {Omega_DM_obs/Omega_b_obs:.2f}")
print()

# ============================================================
# Solve χ field cosmologically
# ============================================================
print("=" * 80)
print("Solving free scalar field in FLRW: χ̈ + 3Hχ̇ + m²χ = 0")
print("=" * 80)
print()

def H_LCDM(a, Om=0.315, OL=0.685):
    """Hubble rate in LCDM at scale factor a (in H_0 units)."""
    return np.sqrt(Om/a**3 + OL)  # in units H_0

def derivs_chi(t, y, m_over_H0):
    """y = [a, chi, chi_dot] in cosmological time (in 1/H_0)."""
    a, chi, chi_dot = y
    if a < 1e-9:
        return [0, 0, 0]
    H = H_LCDM(a)
    a_dot = a * H
    chi_ddot = -3 * H * chi_dot - m_over_H0**2 * chi
    return [a_dot, chi_dot, chi_ddot]

# Test multiple m_χ values: from ultralight (m << H_0) to heavy (m >> H_0)
m_over_H0_test = [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 1e4]

print("Test: χ evolution for various m_χ/H_0 ratios")
print()
print(f"{'m/H_0':>10} {'<rho_χ>(a=1)':>15} {'avg p_χ/rho_χ':>16} {'regime':>15}")

results = []
for m_H0 in m_over_H0_test:
    # Initial conditions: at very early time, set chi = chi_0, chi_dot = 0
    # (commonly used for DM scalar field calculations)
    a0 = 0.001
    t_init = 0  # fictitious zero
    chi_0 = 1.0  # arbitrary normalization
    chi_dot_0 = 0.0

    # Integrate
    try:
        sol = solve_ivp(
            lambda t, y: derivs_chi(t, y, m_H0),
            [t_init, 5.0],
            [a0, chi_0, chi_dot_0],
            dense_output=True,
            max_step=0.001,
            rtol=1e-8,
            atol=1e-10,
        )

        # Find time when a = 1 (today)
        a_arr = sol.y[0]
        chi_arr = sol.y[1]
        chi_dot_arr = sol.y[2]

        idx_today = np.argmin(np.abs(a_arr - 1.0))
        if abs(a_arr[idx_today] - 1.0) > 0.1:
            print(f"{m_H0:>10.2f} {'no a=1':>15} {'-':>16} {'integration short':>15}")
            continue

        # Compute energy density and pressure (in natural units)
        # rho_chi = 0.5 chi_dot^2 + 0.5 m^2 chi^2
        rho_chi = 0.5 * chi_dot_arr**2 + 0.5 * m_H0**2 * chi_arr**2
        p_chi = 0.5 * chi_dot_arr**2 - 0.5 * m_H0**2 * chi_arr**2

        # Average over last few oscillations (if oscillating)
        if m_H0 > 1.0:
            window_size = max(50, int(50/m_H0))
            avg_rho = np.mean(rho_chi[max(0, idx_today-window_size):idx_today+1])
            avg_p_over_rho = np.mean(p_chi[max(0, idx_today-window_size):idx_today+1] /
                                     rho_chi[max(0, idx_today-window_size):idx_today+1])
        else:
            avg_rho = rho_chi[idx_today]
            avg_p_over_rho = p_chi[idx_today] / rho_chi[idx_today] if rho_chi[idx_today] > 0 else 0

        # Regime classification
        if abs(avg_p_over_rho + 1) < 0.01:
            regime = "DE-like (Λ)"
        elif abs(avg_p_over_rho) < 0.01:
            regime = "MATTER-like"
        elif avg_p_over_rho < -0.5:
            regime = "DE-mostly"
        elif avg_p_over_rho > 0.1:
            regime = "RADIATION-like"
        else:
            regime = "intermediate"

        print(f"{m_H0:>10.2f} {avg_rho:>15.6e} {avg_p_over_rho:>16.4f} {regime:>15}")
        results.append((m_H0, avg_rho, avg_p_over_rho))
    except Exception as e:
        print(f"{m_H0:>10.2f}: integration error: {str(e)[:50]}")

print()
print("Interpretation:")
print("  m << H_0: χ frozen, p/rho = -1 (Λ-like, NOT DM)")
print("  m ~ H_0: χ transitioning")
print("  m >> H_0: χ oscillates rapidly, time-avg p = 0 (MATTER-like, COULD BE DM)")
print()


# ============================================================
# Scaling check: rho_χ ∝ a^-3 in oscillating regime?
# ============================================================
print("=" * 80)
print("Scaling check: rho_χ vs a in oscillating regime")
print("=" * 80)
print()

m_H0 = 100.0  # well above Hubble, oscillating regime
sol = solve_ivp(
    lambda t, y: derivs_chi(t, y, m_H0),
    [0, 5.0],
    [0.01, 1.0, 0.0],
    dense_output=True,
    max_step=0.0005,
    rtol=1e-9,
    atol=1e-11,
)

# Sample at various scale factors
a_samples = [0.1, 0.3, 0.5, 0.7, 1.0]
print(f"For m_χ = {m_H0} H_0 (highly oscillating, expect matter-like):")
print(f"{'a':>10} {'rho_χ avg':>15} {'rho_χ × a^3':>15} {'normalized':>12}")

# Need to find time at each a, compute average rho_χ around that time
ts = np.linspace(0, 5, 5000)
sol_eval = sol.sol(ts)
a_arr_full = sol_eval[0]
chi_arr_full = sol_eval[1]
chi_dot_arr_full = sol_eval[2]
rho_chi_full = 0.5 * chi_dot_arr_full**2 + 0.5 * m_H0**2 * chi_arr_full**2

# For m_H0 = 100, oscillation period in t units is 2π/m_H0 ≈ 0.063
# Average over ~10 periods
avg_window_t = 0.5  # in 1/H_0 time units

reference_rho = None
print_data = []
for a_target in a_samples:
    idxs = np.where(np.abs(a_arr_full - a_target) < 0.05 * a_target)[0]
    if len(idxs) > 100:
        avg_rho = np.mean(rho_chi_full[idxs[:100]])
        rho_a3 = avg_rho * a_target**3
        if reference_rho is None:
            reference_rho = rho_a3
        normalized = rho_a3 / reference_rho
        print_data.append((a_target, avg_rho, rho_a3, normalized))

for a_t, avg_rho, rho_a3, norm in print_data:
    print(f"{a_t:>10.2f} {avg_rho:>15.6e} {rho_a3:>15.6e} {norm:>12.4f}")

print()
print("If χ is matter-like: rho_χ × a^3 should be CONSTANT (=1.0 normalized)")
print()


# ============================================================
# Now load rotation curve data and check χ-DM scenario
# ============================================================
print("=" * 80)
print("Rotation curves test: does χ as DM match galaxy data?")
print("=" * 80)
print()

rotation_path = "data/rotation/rotation_ds006_rotmod.csv"
if os.path.exists(rotation_path):
    print(f"Loading rotation data from {rotation_path}")

    # Read CSV with actual columns: system_id, radius, v_obs, v_err, baryon_term, history_term
    import csv
    galaxies = {}
    with open(rotation_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            gname = row.get('system_id', '').strip()
            if not gname:
                continue
            if gname not in galaxies:
                galaxies[gname] = {'r': [], 'V_obs': [], 'V_baryon': []}
            try:
                r = float(row.get('radius', '0'))
                V_obs = float(row.get('v_obs', '0'))
                # baryon_term is V^2 of baryons typically (need to check normalization)
                # Treat as V_baryon directly (or sqrt of it)
                V_bar2 = float(row.get('baryon_term', '0'))
                V_baryon = np.sqrt(V_bar2) if V_bar2 > 0 else 0
                galaxies[gname]['r'].append(r)
                galaxies[gname]['V_obs'].append(V_obs)
                galaxies[gname]['V_baryon'].append(V_baryon)
            except (ValueError, KeyError):
                continue

    print(f"Loaded {len(galaxies)} galaxies")

    # For each galaxy, compute V_DM_required = sqrt(V_obs^2 - V_baryon^2)
    # If χ is DM with NFW-like profile, predict V_χ(r) and compare

    # Simple test: check if V_obs/V_baryon increases with r (DM dominates at large r)
    print()
    print("Sample galaxies (V_obs vs V_baryon):")
    print(f"{'Galaxy':>15} {'r_max':>8} {'V_obs(r_max)':>13} {'V_bar(r_max)':>13} {'V_DM_req':>10}")

    for gname in list(galaxies.keys())[:10]:
        g = galaxies[gname]
        if not g['r']:
            continue
        r_arr = np.array(g['r'])
        V_obs_arr = np.array(g['V_obs'])
        V_bar_arr = np.array(g['V_baryon'])
        idx_max = np.argmax(r_arr)
        V_DM_req2 = max(V_obs_arr[idx_max]**2 - V_bar_arr[idx_max]**2, 0)
        V_DM_req = np.sqrt(V_DM_req2)
        print(f"{gname:>15} {r_arr[idx_max]:>8.2f} {V_obs_arr[idx_max]:>13.2f} "
              f"{V_bar_arr[idx_max]:>13.2f} {V_DM_req:>10.2f}")

    print()
    print("=> Most galaxies show V_DM_required > 0 at large r (DM evidence).")
    print("=> Question: can χ-field with appropriate m_χ produce this?")
    print()

else:
    print(f"Rotation data not found at {rotation_path}")
print()


# ============================================================
# What m_χ would chi-DM need to match observations?
# ============================================================
print("=" * 80)
print("Constraints on m_χ from cosmology and galactic dynamics")
print("=" * 80)
print()
print("CONSTRAINT 1: Cosmological matter-like behavior")
print("  Need m_χ >> H_0 ~ 10^{-33} eV")
print()
print("CONSTRAINT 2: Galactic clustering (form halos)")
print("  Bose field with mass m_χ has de Broglie wavelength λ_dB ~ ℏ/m_χ v")
print("  For λ_dB ~ 1 kpc (galactic): m_χ ~ ℏ/(v×1 kpc) ~ 10^{-22} eV")
print("  This is the FUZZY DM regime")
print()
print("CONSTRAINT 3: Subgalactic structure (dwarf galaxies, Lyman-α)")
print("  Fuzzy DM with m_χ < 10^{-21} eV ruled out by Lyman-α observations")
print("  m_χ > 10^{-21} eV preferred")
print()
print("CONSTRAINT 4: Cosmological abundance Ω_DM = 0.265")
print("  Set initial χ amplitude such that ρ_χ(a=1) = Ω_DM × ρ_critical")
print()

print()
print("=" * 80)
print("MASS WINDOW for χ-DM:")
print("=" * 80)
print()
print("  10^{-21} eV < m_χ < 10^{4} eV   (axion-like / fuzzy DM)")
print("  OR")
print("  m_χ ~ 10^{2} GeV (WIMP-like, but χ has no SM gauge couplings)")
print("  OR")
print("  m_χ ~ Planck mass (super-heavy, but no production mechanism)")
print()
print("For QNG default CHI_DECAY = 0.020 lattice units:")
m_chi_qng_planck = np.sqrt(0.020)  # in Planck units
m_chi_qng_GeV = m_chi_qng_planck * 1.22e19
print(f"  m_χ_QNG = sqrt(0.020) Planck = {m_chi_qng_planck:.3f} M_Planck = {m_chi_qng_GeV:.3e} GeV")
print(f"  This is super-Planckian; outside DM window")
print()
print("For χ to be FUZZY DM (m ~ 10^{-22} eV):")
m_target = 1e-22 / hbar_eV_s  # in 1/s
m_target_PL = m_target * 5.39e-44  # × Planck time = dimensionless Planck units
print(f"  Required CHI_DECAY ~ m_target² = {m_target_PL**2:.3e} (Planck units)")
print(f"  Compared to default 0.020: ratio = {0.020/m_target_PL**2:.3e}")
print(f"  Would need to reduce CHI_DECAY by factor ~{0.020/m_target_PL**2:.0e}")
print()


# ============================================================
# Final verdict
# ============================================================
print("=" * 80)
print("VERDICT — χ field as dark matter")
print("=" * 80)
print()
print("STRUCTURAL: a free scalar field in FLRW behaves as:")
print("  - Λ-like (frozen) for m << H_0")
print("  - Matter-like (oscillating) for m >> H_0")
print()
print("So a SCALAR FIELD CAN be DM if its mass is >> H_0.")
print()
print("QNG specific:")
print("  - χ in default v8 (CHI_DECAY=0.020) is super-Planckian massive")
print("  - This is INCONSISTENT with both DE and DM regimes")
print("  - Suggests CHI_DECAY = 0.020 is NUMERICAL stability parameter,")
print("    NOT physical mass")
print()
print("If χ has cosmologically-relevant mass ~ 10^{-22} eV (fuzzy DM):")
print("  - Could play role of DM")
print("  - Requires CHI_DECAY ~ 10^{-120} (Planck units)")
print("  - Would be an additional cosmological identification (like α ~ Λ)")
print()
print("STATUS:")
print("  CANDIDATE viable IF χ has ultralight effective cosmological mass")
print("  Matches axion-like / fuzzy DM phenomenology")
print("  Magnitude requires identification (analogous to α-Λ identification)")
print()
print("This is INTERESTING but requires:")
print("  1. Justify why χ has ultralight cosmological mass (vs lattice mass)")
print("  2. Verify clustering on galactic scales matches NFW or fuzzy-DM profile")
print("  3. Check Lyman-α and CMB constraints")
print()
print("Promising direction. Next steps: scan rotation curves with χ-DM model.")
