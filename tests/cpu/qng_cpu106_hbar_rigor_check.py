"""QNG-CPU-106c -- rigor check on hbar candidate convergence.

Tests whether the 2.4% gap between:
  hbar_zero_point = beta_phi / <omega_k>_BZ = 0.0950
  hbar_per_edge   = |H|T / (2pi * N_edges) = 0.0973
can be closed by improving the numerics or identifying structural factor.
"""
import numpy as np

beta_phi = 0.06
mu_phi = 0.857
L = 28
N_nodes = L**3  # 21952
N_edges = 3*N_nodes  # cubic z=6, N_edges = zN/2 = 3N

# Compute <omega_k>_BZ with higher precision
L_bz = 200  # finer grid
k = np.linspace(0, 2*np.pi, L_bz, endpoint=False)
kx, ky, kz = np.meshgrid(k, k, k, indexing='ij')
omega_sq = (beta_phi/mu_phi) * 2.0 * (3.0 - np.cos(kx) - np.cos(ky) - np.cos(kz))
mask = omega_sq > 1e-20
omega = np.sqrt(omega_sq[mask])
omega_mean = float(np.mean(omega))
print(f"<omega_k>_BZ (L_bz=200) = {omega_mean:.6f}")

hbar_zp = beta_phi / omega_mean
print(f"hbar_zero_point = {hbar_zp:.6f}")

# From data CPU-100 (average over R={3,4,5}):
# |H|*T values: {39858, 40102, 40886} mean = 40282
HT_mean = (39858 + 40102 + 40886) / 3
hbar_edge = HT_mean / (2 * np.pi * N_edges)
print(f"|H|*T mean = {HT_mean:.1f}")
print(f"hbar_per_edge = {hbar_edge:.6f}")

print(f"\nRatio per-edge/zero-point = {hbar_edge/hbar_zp:.6f}")

# Test: maybe factor is exactly (z/2+1)/z? or specific lattice factor
factors_to_try = [
    ('1', 1),
    ('z/6 = 1', 6/6),
    ('z/(z-1) = 6/5', 6/5),
    ('(z+1)/z', 7/6),
    ('5/6', 5/6),
    ('sqrt(z/6) = 1', np.sqrt(1)),
    ('2/(z-1)', 2/5),
    ('pi/3 = 1.047', np.pi/3),
    ('omega_mean in units of <omega²>_BZ^½', 0.632 / 0.648),
]

print(f"\nSearch for exact structural factor:")
for name, f in factors_to_try:
    prod = hbar_zp * f
    diff = abs(prod - hbar_edge) / hbar_edge * 100
    print(f"  hbar_zp * ({name}) = {prod:.6f}  (diff from hbar_edge: {diff:.2f}%)")

# Maybe the "right" formula involves <omega_k^2>^½ instead of <omega_k>?
omega_rms = float(np.sqrt(np.mean(omega_sq[mask])))
print(f"\n<omega_k^2>_BZ^½ = {omega_rms:.6f}")
hbar_rms = beta_phi / omega_rms
print(f"hbar_zp (rms) = {hbar_rms:.6f}")
print(f"Ratio edge/zp(rms) = {hbar_edge/hbar_rms:.6f}")

# Check if edge formula = rms-based formula
diff_rms = abs(hbar_rms - hbar_edge) / hbar_edge * 100
print(f"Diff between hbar_edge and hbar_zp_rms: {diff_rms:.2f}%")

# Also check <omega> averaged with proper lattice weight (integrating over reduced BZ)
# For z=6 cubic, each k-mode weight is 1 (uniform)
# Something more specific?

# Alternative: use exact k-sum over finite lattice L=28 instead of BZ integral
print(f"\n--- Finite-lattice exact sum (L=28) ---")
L_lat = 28
k_vals = 2*np.pi * np.arange(L_lat) / L_lat
kx, ky, kz = np.meshgrid(k_vals, k_vals, k_vals, indexing='ij')
omega_sq_lat = (beta_phi/mu_phi) * 2.0 * (3.0 - np.cos(kx) - np.cos(ky) - np.cos(kz))
mask_lat = omega_sq_lat > 1e-20
omega_lat = np.sqrt(omega_sq_lat[mask_lat])
omega_mean_lat = float(np.mean(omega_lat))
omega_sum_lat = float(np.sum(omega_lat))
N_modes_lat = len(omega_lat)
print(f"N_modes = {N_modes_lat}  (expected {L_lat**3 - 1} = {L_lat**3-1})")
print(f"<omega_k>_lattice = {omega_mean_lat:.6f}")
print(f"Σ omega_k = {omega_sum_lat:.2f}")

hbar_lat = beta_phi / omega_mean_lat
print(f"hbar (exact lattice) = {hbar_lat:.6f}")

# Zero-point balance exactly per-lattice
# E_classical = -beta_phi * N / 2
# E_quantum zero-point = (hbar/2) * sum(omega_k)
# For E_ground = 0: sum(hbar*omega/2) = beta_phi * N / 2
# hbar * Σomega = beta_phi * N
# hbar = beta_phi * N / Σomega
hbar_exact = beta_phi * L_lat**3 / omega_sum_lat
print(f"hbar from exact zero-point balance = {hbar_exact:.6f}")
print(f"Match with hbar_per_edge 0.0973? diff = "
      f"{abs(hbar_exact - hbar_edge)/hbar_edge*100:.2f}%")
