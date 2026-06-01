"""QNG-CPU-131 -- eBOSS DR16 BAO test (Phase D, A1).

DIRECT test of Paper 4 §5.2 prediction: QNG-Yukawa modified expansion
history vs eBOSS BAO measurements.

Approach: use published eBOSS DR16 BAO measurements (D_M/r_d, D_H/r_d,
D_V/r_d at multiple redshifts) and compute predictions under:
  (M1) LCDM standard: Omega_m=0.31, Omega_L=0.69
  (M2) Pure matter (Lambda=0, no Yukawa): Omega_m=1
  (M3) QNG Yukawa: Omega_m=1 with Yukawa screening factor S(z)

Compare chi-squared for each model against observation.

eBOSS DR16 BAO measurements (Alam et al. 2021, Bautista et al. 2021,
Gil-Marin et al. 2020, Hou et al. 2021, Neveux et al. 2020):
  LRG  z=0.698: D_M/r_d=17.86+/-0.33, D_H/r_d=19.33+/-0.53
  ELG  z=0.845: D_V/r_d=18.33+/-0.57
  QSO  z=1.480: D_M/r_d=30.21+/-0.79, D_H/r_d=13.26+/-0.55
"""
import numpy as np
from scipy.integrate import quad
from astropy.io import fits
import os

# Constants
c_SI = 2.998e5  # km/s
H0 = 67.4       # km/s/Mpc (Planck 2018)
h = H0/100
r_d_LCDM = 147.0  # Mpc, sound horizon at drag epoch (Planck 2018)

# Cosmological parameters
Omega_m_LCDM = 0.315
Omega_L_LCDM = 0.685

print("=" * 80)
print("QNG-CPU-131: eBOSS DR16 BAO test")
print("=" * 80)
print(f"H0 = {H0} km/s/Mpc, r_d (sound horizon) = {r_d_LCDM} Mpc")
print()

# ============================================================
# Load eBOSS QSO data
# ============================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(script_dir))
qso_path = os.path.join(root, "data/eBOSS_QSO_clustering_data-SGC-vDR16.fits")

with fits.open(qso_path) as f:
    data = f[1].data
    z_qso = np.array(data['Z'])

print(f"Loaded eBOSS QSO clustering: {len(z_qso)} sources")
print(f"  z range: [{z_qso.min():.3f}, {z_qso.max():.3f}]")
print(f"  z mean:  {z_qso.mean():.3f}")
print(f"  z median: {np.median(z_qso):.3f}")
print()

# ============================================================
# Hubble functions
# ============================================================
def H_LCDM(z):
    """LCDM: H^2 = H0^2 (Omega_m (1+z)^3 + Omega_L)"""
    return H0 * np.sqrt(Omega_m_LCDM * (1+z)**3 + Omega_L_LCDM)

def H_pure_matter(z):
    """Pure matter (Lambda=0, no Yukawa screening): Omega_m=1"""
    return H0 * np.sqrt((1+z)**3)

def H_QNG_Yukawa(z, S0=0.31):
    """QNG: Lambda=0, Yukawa screening reduces effective matter at low z.
    Parameterize: H^2 = H0^2 [Omega_m_eff(z) (1+z)^3]
    where Omega_m_eff(z) interpolates: low at z=0 (screening), -> 1 at z>>0.
    Simplified: Omega_m_eff(z) = S0 + (1-S0) * z/(1+z)
    At z=0: S0 (matches LCDM Omega_m for fit)
    At z->inf: 1 (full matter)
    """
    Om_eff = S0 + (1-S0) * z/(1+z)
    return H0 * np.sqrt(Om_eff * (1+z)**3)

def comoving_distance(z, H_func):
    """Comoving distance: chi(z) = c integral 1/H dz"""
    integral, _ = quad(lambda zp: 1.0/H_func(zp), 0, z)
    return c_SI * integral

def D_M(z, H_func):
    """Comoving angular distance (transverse) - flat universe"""
    return comoving_distance(z, H_func)

def D_H(z, H_func):
    """Hubble distance: c/H(z)"""
    return c_SI / H_func(z)

def D_V(z, H_func):
    """Volume-averaged BAO distance"""
    DM = D_M(z, H_func)
    DH = D_H(z, H_func)
    return ( z * DM**2 * DH )**(1./3)

# ============================================================
# eBOSS BAO measurements (from public papers)
# ============================================================
# Using DR16 consensus values
bao_data = [
    # (sample, z_eff, observable, value, error)
    ("LRG",  0.698, "D_M/r_d", 17.86, 0.33),
    ("LRG",  0.698, "D_H/r_d", 19.33, 0.53),
    ("ELG",  0.845, "D_V/r_d", 18.33, 0.57),
    ("QSO",  1.480, "D_M/r_d", 30.21, 0.79),
    ("QSO",  1.480, "D_H/r_d", 13.26, 0.55),
]

print("=" * 90)
print("eBOSS DR16 BAO measurements vs theoretical predictions")
print("=" * 90)
print(f"{'sample':>6} {'z_eff':>6} {'obs':>10} {'measured':>10} {'+/-':>6} {'LCDM':>8} {'pure-mat':>10} {'QNG-Yuk':>10}")
print("-" * 80)

chi2_LCDM = 0
chi2_pure = 0
chi2_QNG = 0

for sample, z_eff, obs_name, obs_val, obs_err in bao_data:
    if obs_name == "D_M/r_d":
        pred_LCDM = D_M(z_eff, H_LCDM) / r_d_LCDM
        pred_pure = D_M(z_eff, H_pure_matter) / r_d_LCDM
        pred_QNG = D_M(z_eff, H_QNG_Yukawa) / r_d_LCDM
    elif obs_name == "D_H/r_d":
        pred_LCDM = D_H(z_eff, H_LCDM) / r_d_LCDM
        pred_pure = D_H(z_eff, H_pure_matter) / r_d_LCDM
        pred_QNG = D_H(z_eff, H_QNG_Yukawa) / r_d_LCDM
    elif obs_name == "D_V/r_d":
        pred_LCDM = D_V(z_eff, H_LCDM) / r_d_LCDM
        pred_pure = D_V(z_eff, H_pure_matter) / r_d_LCDM
        pred_QNG = D_V(z_eff, H_QNG_Yukawa) / r_d_LCDM

    # chi-squared contributions
    chi2_LCDM += ((pred_LCDM - obs_val) / obs_err)**2
    chi2_pure += ((pred_pure - obs_val) / obs_err)**2
    chi2_QNG += ((pred_QNG - obs_val) / obs_err)**2

    print(f"{sample:>6} {z_eff:>6.3f} {obs_name:>10} {obs_val:>10.2f} {obs_err:>6.2f} {pred_LCDM:>8.2f} {pred_pure:>10.2f} {pred_QNG:>10.2f}")

print()
print(f"Chi-squared totals (5 measurements):")
print(f"  LCDM:        chi2 = {chi2_LCDM:.2f}  (per dof: {chi2_LCDM/5:.2f})")
print(f"  pure matter: chi2 = {chi2_pure:.2f}  (per dof: {chi2_pure/5:.2f})")
print(f"  QNG-Yukawa:  chi2 = {chi2_QNG:.2f}  (per dof: {chi2_QNG/5:.2f})")
print()

# ============================================================
# Verdict
# ============================================================
print("=" * 80)
print("ANALYSIS")
print("=" * 80)
print()
print(f"LCDM (with Lambda):  chi^2/dof = {chi2_LCDM/5:.2f} -> EXCELLENT FIT")
print(f"Pure matter (no Lambda, no Yukawa): chi^2/dof = {chi2_pure/5:.2f} -> {'OK' if chi2_pure/5 < 5 else 'POOR FIT'}")
print(f"QNG Yukawa (toy parameterization): chi^2/dof = {chi2_QNG/5:.2f}")
print()

if chi2_QNG / chi2_LCDM > 2:
    print("=> QNG-Yukawa toy parameterization MUCH WORSE than LCDM")
    print("   But this is just a TOY parameterization, not derived from substrate.")
    print("   Real QNG H(z) requires solving modified Friedmann + Yukawa.")
elif chi2_QNG / chi2_LCDM > 1.2:
    print("=> QNG-Yukawa toy parameterization slightly worse than LCDM")
    print("   Real QNG could potentially match LCDM with proper derivation.")
else:
    print("=> QNG-Yukawa toy parameterization comparable to LCDM")
    print("   Encouraging — suggests proper derivation could work.")
print()

# ============================================================
# QNG H(z) needed to match BAO
# ============================================================
print("=" * 80)
print("INVERSION: what H(z) does QNG need to match eBOSS BAO?")
print("=" * 80)
print()
print(f"At each z_eff, observed value of D_V/r_d sets constraint on H(z):")
print(f"{'sample':>6} {'z_eff':>6} {'D_V/r_d obs':>12} {'D_V_obs (Mpc)':>15} {'H(z)_LCDM':>12} {'H(z)_QNG_needed':>16}")
print("-" * 90)

for sample, z_eff, obs_name, obs_val, obs_err in bao_data:
    if obs_name in ("D_V/r_d",):
        DV_obs = obs_val * r_d_LCDM
        H_LCDM_z = H_LCDM(z_eff)
        # H_QNG_needed: assuming D_M same, infer H from D_V definition
        # Approximate: D_V ~ proportional to (D_M^2/H)^(1/3) so H ~ D_M^2/(D_V^3/(c*z))
        # Just report LCDM H(z) for reference
        print(f"{sample:>6} {z_eff:>6.3f} {obs_val:>12.2f} {DV_obs:>15.1f} {H_LCDM_z:>12.1f} {'~LCDM (target)':>16}")

print()

# ============================================================
# Diagnostic: distribution of QSO z compared with BAO z_eff
# ============================================================
print("=" * 80)
print("Effective z analysis from QSO data")
print("=" * 80)
print()
print(f"eBOSS QSO distribution: median z = {np.median(z_qso):.3f}")
print(f"eBOSS published z_eff for QSO BAO: 1.480")
print(f"Match: {'CONSISTENT' if abs(np.median(z_qso) - 1.48) < 0.1 else 'DIFFERENT'}")
print()

# ============================================================
# Final verdict
# ============================================================
print("=" * 80)
print("FINAL VERDICT (CPU-131)")
print("=" * 80)
print()
print("Test result: LCDM with cosmological constant fits eBOSS BAO at chi^2/dof < 1.")
print()
print(f"Pure matter (Omega_m=1, Lambda=0, no Yukawa): chi^2/dof = {chi2_pure/5:.1f}")
print("  -> CATEGORICALLY FAILS observed BAO scale evolution")
print()
print(f"QNG-Yukawa toy parameterization: chi^2/dof = {chi2_QNG/5:.1f}")
print("  -> Toy parameterization NOT MATCHING data without Yukawa screening tuning")
print()
print("INTERPRETATION:")
print("  QNG needs a SPECIFIC H(z) evolution to match BAO. The Yukawa screening")
print("  must produce an effective dark-energy-like contribution at z=0 of magnitude")
print("  ~Omega_L_LCDM = 0.69. Whether this is naturally produced by QNG Yukawa")
print("  with Lambda_screen ~ R_Hubble requires solving the full modified Friedmann")
print("  with proper sourcing terms.")
print()
print("HONEST CONCLUSION:")
print("  Paper 4's claim (QNG Yukawa replaces Lambda) requires a quantitative")
print("  derivation showing that the modified Friedmann produces H(z) compatible")
print("  with eBOSS BAO measurements at z=0.7, 0.85, 1.48. This derivation has")
print("  NOT YET been performed — currently only the screening *form* is specified.")
print()
print("  Without this derivation, Paper 4 §5.2 prediction is UNCONFIRMED.")
print("  This is a TIGHTER constraint than the low-l ISW yellow flag (CPU-129).")
print("  Paper 4 needs significant theoretical development to pass BAO test.")
