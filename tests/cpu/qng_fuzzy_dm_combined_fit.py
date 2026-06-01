"""QNG-CPU-FUZZY-DM-COMBINED — Combined soliton + NFW fit on 175 galaxies.

Part A of user-requested follow-up: address the r_c vs M_b sign issue
from the soliton-only fit by using the proper combined fuzzy DM model.

For real fuzzy DM:
- Inside r ~ 3 r_c: soliton core dominates (flat density, fuzzy nature)
- Outside r ~ 3 r_c: NFW envelope (cosmological halo)

V_DM²_total(r) = V_soliton²(r) + V_NFW²(r)

4 parameters per galaxy: rho_c, r_c (soliton), rho_s, r_s (NFW envelope).

Goal: see if combined model:
1. Fits better than NFW-only or soliton-only
2. Gives r_c ∝ M_b^{-1/3} as fuzzy DM predicts
3. Provides quantitative confirmation of fuzzy DM hypothesis
"""
import numpy as np
from scipy.optimize import least_squares
import csv

print("=" * 80)
print("QNG-CPU-FUZZY-DM-COMBINED: soliton + NFW combined fits on 175 galaxies")
print("=" * 80)
print()

# Constants
G_kpc_kms2_Msun = 4.302e-6  # kpc·(km/s)²/M_sun

# ============================================================
# Load galaxies
# ============================================================
rotation_path = "data/rotation/rotation_ds006_rotmod.csv"
galaxies = {}
with open(rotation_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        gname = row['system_id'].strip()
        if gname not in galaxies:
            galaxies[gname] = {'r': [], 'v_obs': [], 'v_err': [], 'V_b2': []}
        try:
            r = float(row['radius'])
            v_obs = float(row['v_obs'])
            v_err = float(row.get('v_err', '1.0'))
            baryon = float(row['baryon_term'])
            galaxies[gname]['r'].append(r)
            galaxies[gname]['v_obs'].append(v_obs)
            galaxies[gname]['v_err'].append(v_err)
            galaxies[gname]['V_b2'].append(baryon)
        except (ValueError, KeyError):
            continue

galaxies_filt = {k: v for k, v in galaxies.items() if len(v['r']) >= 5}
print(f"Loaded {len(galaxies_filt)} galaxies with ≥5 data points")
print()


# ============================================================
# DM profile models
# ============================================================
def V_NFW_squared(r, rho_s, r_s):
    """V²(r) for NFW DM."""
    x = np.maximum(r / r_s, 1e-9)
    M = 4 * np.pi * rho_s * r_s**3 * (np.log(1 + x) - x/(1 + x))
    V2 = G_kpc_kms2_Msun * M / np.maximum(r, 1e-9)
    return V2

def V_soliton_squared(r, rho_c, r_c):
    """V²(r) for fuzzy-DM soliton."""
    if r_c <= 0 or rho_c <= 0:
        return np.full_like(r, np.inf)
    M = np.zeros_like(r)
    for i, ri in enumerate(r):
        if ri <= 0:
            continue
        n_pts = 100
        rs_int = np.linspace(0, ri, n_pts)
        rho_int = rho_c / (1 + 0.091 * (rs_int/r_c)**2)**8
        M[i] = np.trapz(4 * np.pi * rs_int**2 * rho_int, rs_int)
    return G_kpc_kms2_Msun * M / np.maximum(r, 1e-9)

def V_combined_squared(r, rho_c, r_c, rho_s, r_s):
    """Combined fuzzy DM: soliton + NFW envelope."""
    return V_soliton_squared(r, rho_c, r_c) + V_NFW_squared(r, rho_s, r_s)


# ============================================================
# Combined fit
# ============================================================
def fit_combined(g):
    """Fit combined soliton + NFW to V_DM(r)."""
    r = np.array(g['r'])
    V_obs = np.array(g['v_obs'])
    V_b2 = np.array(g['V_b2'])
    V_err = np.array(g['v_err'])
    V_DM2_obs = np.maximum(0, V_obs**2 - V_b2)

    if np.all(V_DM2_obs <= 0):
        return None, None, None

    # Initial guess
    x0 = [1e8, 1.0, 1e7, 5.0]  # rho_c, r_c, rho_s, r_s
    try:
        def residuals(params, r, V_DM2_obs, V_err):
            rho_c, r_c, rho_s, r_s = params
            if any(p <= 0 for p in params):
                return 1e10 * np.ones_like(r)
            V_pred2 = V_combined_squared(r, rho_c, r_c, rho_s, r_s)
            V_pred = np.sqrt(np.maximum(V_pred2, 0))
            V_obs_dm = np.sqrt(np.maximum(V_DM2_obs, 0))
            return (V_pred - V_obs_dm) / np.maximum(V_err, 0.1)
        result = least_squares(residuals, x0, args=(r, V_DM2_obs, V_err),
                               bounds=([1e3, 0.05, 1e3, 0.5],
                                       [1e12, 30, 1e12, 200]),
                               max_nfev=2000)
        return result.x, np.sum(result.fun**2), len(r)
    except Exception as e:
        return None, None, None


# ============================================================
# Run fits
# ============================================================
print("Running combined fits on all DM-requiring galaxies...")
results_combined = []
for gname, g in galaxies_filt.items():
    fit_result, chi2, n_pts = fit_combined(g)
    if fit_result is None:
        continue

    rho_c, r_c, rho_s, r_s = fit_result

    # Galaxy mass estimate
    V_b_max = np.sqrt(np.max(g['V_b2']))
    r_max_g = np.max(g['r'])
    M_b_estimate = V_b_max**2 * r_max_g / G_kpc_kms2_Msun

    # Soliton mass M_sol = (mass enclosed in 3 r_c)
    rs_int = np.linspace(0.01, 3*r_c, 200)
    rho_int = rho_c / (1 + 0.091 * (rs_int/r_c)**2)**8
    M_soliton = np.trapz(4 * np.pi * rs_int**2 * rho_int, rs_int)

    # NFW total halo mass (within virial radius ~ 200 r_s typically)
    x_vir = 50  # virial radius in r_s units (rough)
    M_NFW_vir = 4 * np.pi * rho_s * r_s**3 * (np.log(1 + x_vir) - x_vir/(1 + x_vir))

    results_combined.append({
        'name': gname,
        'n_pts': n_pts,
        'M_b_est': M_b_estimate,
        'rho_c': rho_c,
        'r_c': r_c,
        'rho_s': rho_s,
        'r_s': r_s,
        'M_soliton': M_soliton,
        'M_NFW_vir': M_NFW_vir,
        'chi2': chi2,
        'chi2_dof': chi2 / (n_pts - 4),
    })

print(f"Galaxies fitted: {len(results_combined)}")
print()


# ============================================================
# Statistics
# ============================================================
print("=" * 80)
print("Combined fit statistics")
print("=" * 80)
print()

chi2_arr = np.array([r['chi2_dof'] for r in results_combined])
print(f"Combined χ²/dof: median = {np.median(chi2_arr):.2f}, mean = {np.mean(chi2_arr):.2f}")
print(f"Galaxies with χ²/dof < 5: {np.sum(chi2_arr < 5)} / {len(chi2_arr)}")
print(f"Galaxies with χ²/dof < 2: {np.sum(chi2_arr < 2)} / {len(chi2_arr)}")
print()

# ============================================================
# r_c vs M_b scaling — KEY test
# ============================================================
print("=" * 80)
print("r_c vs M_b scaling — fuzzy DM prediction r_c ∝ M_halo^(-1/3)")
print("=" * 80)
print()

# Use only well-fitted galaxies
good = [r for r in results_combined if r['chi2_dof'] < 10]
print(f"Well-fitted galaxies (chi2/dof<10): {len(good)}")

if len(good) > 10:
    log_Mb = np.log10([r['M_b_est'] for r in good])
    log_rc = np.log10([r['r_c'] for r in good])

    # Outlier removal: drop galaxies with very large r_c (likely failed fits)
    mask_reasonable = (np.array([r['r_c'] for r in good]) > 0.05) & \
                      (np.array([r['r_c'] for r in good]) < 30)
    log_Mb_clean = log_Mb[mask_reasonable]
    log_rc_clean = log_rc[mask_reasonable]

    coef = np.polyfit(log_Mb_clean, log_rc_clean, 1)
    slope = coef[0]

    print(f"Linear fit on log-log: log r_c = {slope:.3f} * log M_b + {coef[1]:.3f}")
    print(f"Slope: {slope:.3f}")
    print(f"Predicted (fuzzy DM): -0.333")
    print(f"Match? {abs(slope + 0.333) < 0.2}")
    print(f"Sign correct (negative)? {slope < 0}")
print()


# ============================================================
# M_soliton vs M_halo — Schive scaling test
# ============================================================
print("=" * 80)
print("Soliton mass vs halo mass — Schive 2014 prediction")
print("=" * 80)
print()
print("Schive: M_soliton / M_min ~ (M_halo / M_min)^(1/3)")
print("    where M_min ~ 4.4e7 M_sun (m_chi/1e-22 eV)^{-3/2}")
print()

good = [r for r in results_combined if r['chi2_dof'] < 10 and r['M_soliton'] > 0]
print(f"Good fits: {len(good)}")

if len(good) > 10:
    log_M_halo = np.log10([r['M_NFW_vir'] for r in good if r['M_NFW_vir'] > 0])
    log_M_sol = np.log10([r['M_soliton'] for r in good if r['M_NFW_vir'] > 0])

    coef = np.polyfit(log_M_halo, log_M_sol, 1)
    slope_sol = coef[0]
    print(f"Linear fit: log M_sol = {slope_sol:.3f} * log M_halo + {coef[1]:.3f}")
    print(f"Predicted slope (Schive 2014): 0.333")
    print(f"Match? {abs(slope_sol - 0.333) < 0.2}")
print()


# ============================================================
# Compare three models on dwarf galaxies
# ============================================================
print("=" * 80)
print("Three-way comparison on dwarf galaxies (M_b < 10^9 M_sun)")
print("=" * 80)
print()

# Need NFW-only and soliton-only chi2 for comparison
# Re-import them here (or just rerun)
def fit_NFW_only(g):
    r = np.array(g['r'])
    V_obs = np.array(g['v_obs'])
    V_b2 = np.array(g['V_b2'])
    V_err = np.array(g['v_err'])
    V_DM2 = np.maximum(0, V_obs**2 - V_b2)
    if np.all(V_DM2 <= 0): return None
    try:
        def res(params, r, V_DM2, V_err):
            rho_s, r_s = params
            if rho_s <= 0 or r_s <= 0:
                return 1e10*np.ones_like(r)
            V2p = V_NFW_squared(r, rho_s, r_s)
            return (np.sqrt(np.maximum(V2p,0)) - np.sqrt(np.maximum(V_DM2,0))) / np.maximum(V_err,0.1)
        result = least_squares(res, [1e7, 5.0], args=(r, V_DM2, V_err),
                               bounds=([1e3, 0.1], [1e12, 100]))
        return np.sum(result.fun**2) / (len(r)-2)
    except:
        return None

def fit_sol_only(g):
    r = np.array(g['r'])
    V_obs = np.array(g['v_obs'])
    V_b2 = np.array(g['V_b2'])
    V_err = np.array(g['v_err'])
    V_DM2 = np.maximum(0, V_obs**2 - V_b2)
    if np.all(V_DM2 <= 0): return None
    try:
        def res(params, r, V_DM2, V_err):
            rho_c, r_c = params
            if rho_c <= 0 or r_c <= 0:
                return 1e10*np.ones_like(r)
            V2p = V_soliton_squared(r, rho_c, r_c)
            return (np.sqrt(np.maximum(V2p,0)) - np.sqrt(np.maximum(V_DM2,0))) / np.maximum(V_err,0.1)
        result = least_squares(res, [1e8, 1.0], args=(r, V_DM2, V_err),
                               bounds=([1e4, 0.05], [1e12, 50]))
        return np.sum(result.fun**2) / (len(r)-2)
    except:
        return None

# Compute all three for each dwarf
dwarf_results = []
for gname, g in galaxies_filt.items():
    V_b_max = np.sqrt(np.max(g['V_b2']))
    r_max = np.max(g['r'])
    M_b = V_b_max**2 * r_max / G_kpc_kms2_Msun
    if M_b > 1e9:
        continue

    chi2_NFW = fit_NFW_only(g)
    chi2_sol = fit_sol_only(g)
    chi2_combined = None
    for r in results_combined:
        if r['name'] == gname:
            chi2_combined = r['chi2_dof']
            break

    if all(c is not None for c in [chi2_NFW, chi2_sol, chi2_combined]):
        dwarf_results.append({
            'name': gname,
            'M_b': M_b,
            'NFW': chi2_NFW,
            'soliton': chi2_sol,
            'combined': chi2_combined,
        })

print(f"Dwarfs with all three fits: {len(dwarf_results)}")
print()
if dwarf_results:
    print(f"{'Median χ²/dof:':>20}")
    chi2_NFW = np.median([d['NFW'] for d in dwarf_results])
    chi2_sol = np.median([d['soliton'] for d in dwarf_results])
    chi2_comb = np.median([d['combined'] for d in dwarf_results])
    print(f"  NFW only:     {chi2_NFW:.2f}")
    print(f"  Soliton only: {chi2_sol:.2f}")
    print(f"  Combined:     {chi2_comb:.2f}")
    print()
    # Best model per galaxy
    n_combined_best = 0
    n_sol_best = 0
    n_nfw_best = 0
    for d in dwarf_results:
        m = min(d['NFW'], d['soliton'], d['combined'])
        if m == d['combined']:
            n_combined_best += 1
        elif m == d['soliton']:
            n_sol_best += 1
        else:
            n_nfw_best += 1
    print(f"Best model by galaxy:")
    print(f"  Combined: {n_combined_best}")
    print(f"  Soliton only: {n_sol_best}")
    print(f"  NFW only: {n_nfw_best}")
    print()

# Massives
print("Massive galaxies (M_b > 10^10 M_sun):")
massive_results = []
for gname, g in galaxies_filt.items():
    V_b_max = np.sqrt(np.max(g['V_b2']))
    r_max = np.max(g['r'])
    M_b = V_b_max**2 * r_max / G_kpc_kms2_Msun
    if M_b < 1e10:
        continue

    chi2_NFW = fit_NFW_only(g)
    chi2_sol = fit_sol_only(g)
    chi2_combined = None
    for r in results_combined:
        if r['name'] == gname:
            chi2_combined = r['chi2_dof']
            break

    if all(c is not None for c in [chi2_NFW, chi2_sol, chi2_combined]):
        massive_results.append({
            'M_b': M_b,
            'NFW': chi2_NFW,
            'soliton': chi2_sol,
            'combined': chi2_combined,
        })

if massive_results:
    chi2_NFW = np.median([d['NFW'] for d in massive_results])
    chi2_sol = np.median([d['soliton'] for d in massive_results])
    chi2_comb = np.median([d['combined'] for d in massive_results])
    print(f"  NFW only:     {chi2_NFW:.2f}")
    print(f"  Soliton only: {chi2_sol:.2f}")
    print(f"  Combined:     {chi2_comb:.2f}")
    print()
print()


# ============================================================
# Verdict
# ============================================================
print("=" * 80)
print("VERDICT — Combined soliton + NFW fits")
print("=" * 80)
print()
print(f"Total galaxies fitted: {len(results_combined)}")
print(f"Median χ²/dof: {np.median(chi2_arr):.2f}")
print(f"χ²/dof < 5: {np.sum(chi2_arr < 5)} galaxies ({100*np.sum(chi2_arr < 5)/len(chi2_arr):.0f}%)")
print()
print("Test for fuzzy DM signature (r_c ∝ M_halo^(-1/3)):")
if 'slope' in dir():
    print(f"  Measured slope: {slope:.3f}")
    print(f"  Predicted: -0.333")
    if slope < 0:
        print(f"  Sign match: ✓ (correct direction)")
    else:
        print(f"  Sign match: ✗ (wrong direction)")
print()
print("Comparison vs single-component fits documented above.")
