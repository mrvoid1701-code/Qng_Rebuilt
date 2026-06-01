"""QNG-CPU-128 -- Pioneer + flyby anomaly vs QNG Yukawa (Phase D, B3).

HONESTY CHECK: Pioneer 10/11 anomalous acceleration ~8.7e-10 m/s² sunward.
QNG Yukawa correction at 50 AU = ?

Pioneer at 50 AU: r/λ_screen = 7.5e12/1.4e26 ≈ 5e-14
=> Yukawa correction to gravity: |ΔF/F| ≈ r/λ ≈ 5e-14 (relative to Newton)
=> ΔF magnitude ≈ 5e-14 × GM_sun/r² ≈ 5e-14 × 2.4e-6 ≈ 1.3e-19 m/s²
=> Pioneer 8.7e-10 / QNG 1.3e-19 ≈ 7e9
=> QNG is 9 orders of magnitude TOO SMALL to explain Pioneer.

PLUS: QNG Yukawa makes gravity WEAKER (less bound), opposite to Pioneer
(extra sunward = more bound). Wrong sign too.

This test confirms QNG cannot explain Pioneer anomaly.
"""
import numpy as np
import csv
import os

# Constants
G_SI = 6.674e-11
M_sun = 1.989e30
c_SI = 2.998e8
H0_SI = 2.2e-18
R_Hubble_SI = c_SI / H0_SI
AU_to_M = 1.496e11

# QNG Yukawa screening
lam_screen_SI = R_Hubble_SI

print("=" * 80)
print("QNG-CPU-128: Pioneer + flyby vs QNG Yukawa")
print("=" * 80)
print(f"R_Hubble (= λ_screen per Paper 4): {R_Hubble_SI:.3e} m")
print()

# Load Pioneer data
script_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(script_dir))
pioneer_path = os.path.join(root, "data/trajectory/pioneer_ds005_anchor.csv")

print("=" * 80)
print("PIONEER DATA")
print("=" * 80)
print(f"{'mission':>10} {'r (AU)':>10} {'a_obs (m/s²)':>15} {'a_QNG_Yukawa':>18} {'ratio QNG/obs':>17}")
with open(pioneer_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        mission = row['mission_id']
        r_AU = float(row['r_au_mean'])
        a_obs = float(row['a_obs_m_s2'])
        # Newtonian acceleration at r from Sun
        r_m = r_AU * AU_to_M
        a_N = G_SI * M_sun / r_m**2
        # QNG Yukawa correction to acceleration
        # F_Y/F_N = exp(-r/λ) * (1 + r/λ)
        # For r << λ: 1 - r/λ + r²/λ²/2 + ... ≈ 1 - r²/(2λ²)
        # Wait let me redo: exp(-r/λ)(1+r/λ) = (1 - r/λ + r²/2λ² - ...)(1 + r/λ)
        #                                    = 1 + r/λ - r/λ - r²/λ² + r²/2λ² + O((r/λ)³)
        #                                    = 1 - r²/(2λ²) + O((r/λ)³)
        # So |ΔF/F| ≈ r²/(2λ²) — second order, even smaller!
        ratio = r_m / lam_screen_SI
        delta_F_over_F = ratio**2 / 2
        a_qng_correction = a_N * delta_F_over_F
        ratio_qng_obs = a_qng_correction / a_obs
        print(f"{mission:>10} {r_AU:>10.1f} {a_obs:>15.3e} {a_qng_correction:>18.3e} {ratio_qng_obs:>17.3e}")

print()
print("=" * 80)
print("FLYBY DATA")
print("=" * 80)
flyby_path = os.path.join(root, "data/trajectory/flyby_ds005_real.csv")

# Earth radius
R_earth_km = 6378.0
M_earth = 5.972e24

print(f"{'flyby':>15} {'r_per (km)':>12} {'Δv_obs (mm/s)':>15} {'r/λ_screen':>15} {'Δv_QNG (mm/s)':>17}")
with open(flyby_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            pid = row['pass_id']
            r_per_km = float(row['r_perigee_km'])
            dv_obs_mm_s = float(row['delta_v_obs_mm_s'])
        except (ValueError, KeyError):
            continue
        # At r_perigee, QNG correction:
        r_per_m = r_per_km * 1000
        ratio = r_per_m / lam_screen_SI
        delta_F_over_F = ratio**2 / 2  # incredibly tiny: (10^7/10^26)² ≈ 10^-38
        # Δv from a single flyby pass: roughly Δv ~ a * passage_time, but passage_time short ~hours
        # Order of magnitude: Δv_QNG ~ Δv_GR_total × (r/λ)² ≈ 10^-38 × Δv_GR
        # For comparison just multiply by some characteristic v
        v_char_mm_s = 1000 * 1000  # 1 km/s = 10^6 mm/s as characteristic deflection
        dv_qng = v_char_mm_s * delta_F_over_F
        print(f"{pid:>15} {r_per_km:>12.1f} {dv_obs_mm_s:>15.3f} {ratio:>15.3e} {dv_qng:>17.3e}")

print()
print("=" * 80)
print("VERDICT")
print("=" * 80)
print()
print("Pioneer anomaly (~8.7e-10 m/s² sunward):")
print("  QNG Yukawa correction at 50 AU: ~1.3e-19 × (r/λ) ≈ 10⁻³² m/s²")
print("  QNG/observed ratio: ~10⁻²² (QNG is 22 orders of magnitude too small)")
print("  Plus: QNG sign is OPPOSITE to Pioneer (Yukawa WEAKENS gravity at large r)")
print()
print("Flyby anomalies (~mm/s):")
print("  QNG Yukawa correction at perigee (~10⁴ km from Earth):")
print("  r/λ ~ 10⁻¹⁹, correction ~ 10⁻³⁸ relative — UTTERLY NEGLIGIBLE")
print()
print("CONCLUSION: QNG Yukawa cosmological screening CANNOT explain")
print("Pioneer anomaly OR flyby anomalies.")
print()
print("Note: the trajectory-lag prediction in legacy QNG (DER-TRJ-001) was a")
print("phenomenological proxy based on χ-as-memory interpretation. Under v10")
print("(Tesla U(1) gauge FALSIFIED), χ is matter-gravity responsiveness, NOT")
print("a memory field. The legacy lag prediction is structurally suspended;")
print("a v10/v11 derivation of any trajectory anomaly would require modeling")
print("χ-Channel-D dynamics for spacecraft trajectories, which is open work.")
print()
print("Solar-system anomalies remain UNEXPLAINED by QNG.")
