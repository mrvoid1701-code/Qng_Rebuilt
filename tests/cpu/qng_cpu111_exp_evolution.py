"""QNG-CPU-111 -- What if classical energy grows 10% and vacuum decreases 5%?"""
import numpy as np

beta_phi_0 = 0.06
mu_phi = 0.857
z_coord = 6
L = 28
N_nodes = L**3

c_SI = 2.998e8; G_SI = 6.674e-11; hbar_SI = 1.055e-34
G_QNG_0 = 0.0583
l_P = 1.616e-35; m_P = 2.176e-8

print("=" * 80)
print("QNG-CPU-111: Exponential evolution of energy and vacuum")
print("=" * 80)
print()

# Scenario 1: Single step change
print("SCENARIO A: Single change (energy +10%, vacuum -5%)")
print("-" * 80)
print(f"{'beta':>8} {'vacuum':>10} {'hbar_QNG':>10} {'a_L (m)':>13} {'a_L/l_P':>10} {'a_M/m_P':>10}")
print()

# Reference (current)
def compute_state(beta, vacuum_total):
    """Compute hbar and Planck-scale ratios for given beta and vacuum."""
    # Sum omega_k scales with sqrt(beta) since omega ~ sqrt(beta/mu)
    # For finite L, recompute exactly:
    k_vals = 2*np.pi*np.arange(L)/L
    kx, ky, kz = np.meshgrid(k_vals, k_vals, k_vals, indexing='ij')
    omega_sq = (beta/(z_coord*mu_phi))*2.0*(3.0 - np.cos(kx) - np.cos(ky) - np.cos(kz))
    mask = omega_sq > 1e-20
    omega = np.sqrt(omega_sq[mask])
    sum_omega = float(np.sum(omega))

    hbar = (2*vacuum_total + beta*N_nodes) / sum_omega
    if hbar <= 0:
        return hbar, None, None

    c_QNG = np.sqrt(beta / (z_coord*mu_phi))
    G_QNG = beta * G_QNG_0/beta_phi_0  # if G also scales (assuming same dependence)
    # Actually G_QNG = beta_g/z, so depends on beta_g not beta_phi.
    # Let's keep G_QNG = G_QNG_0 (independent)
    G_QNG = G_QNG_0
    R = c_SI / c_QNG
    Q_h = hbar_SI / (hbar * R)
    Q_G = G_SI / (G_QNG * R**2)
    a_L = np.sqrt(Q_h * Q_G)
    a_M = np.sqrt(Q_h / Q_G)
    return hbar, a_L, a_M

# Reference
hbar_ref, aL_ref, aM_ref = compute_state(beta_phi_0, 0.0)
print(f"{beta_phi_0:>8.4f} {0.0:>10.2f} {hbar_ref:>10.4f} {aL_ref:>13.3e} {aL_ref/l_P:>10.3f} {aM_ref/m_P:>10.3f}")

# +10% beta, -5% vacuum (vacuum starts at 1 for definiteness)
hbar_1, aL_1, aM_1 = compute_state(beta_phi_0 * 1.10, 1.0 * 0.95)
print(f"{beta_phi_0*1.10:>8.4f} {1.0*0.95:>10.2f} {hbar_1:>10.4f} {aL_1:>13.3e} {aL_1/l_P:>10.3f} {aM_1/m_P:>10.3f}")

# More extreme - 50% beta, vacuum -50%
hbar_2, aL_2, aM_2 = compute_state(beta_phi_0 * 1.50, -0.5)
print(f"{beta_phi_0*1.50:>8.4f} {-0.5:>10.2f} {hbar_2:>10.4f} {aL_2:>13.3e} {aL_2/l_P:>10.3f} {aM_2/m_P:>10.3f}")

# Reference: change only in vacuum
hbar_v1, aL_v1, aM_v1 = compute_state(beta_phi_0, -10)
print(f"{beta_phi_0:>8.4f} {-10:>10.2f} {hbar_v1:>10.4f} {aL_v1:>13.3e} {aL_v1/l_P:>10.3f} {aM_v1/m_P:>10.3f}")

print()
print()
# Scenario 2: Iterative exponential evolution
print("SCENARIO B: Iterative evolution (each step: energy x 1.10, vacuum x 0.95)")
print("-" * 80)
print(f"{'iter':>4} {'beta':>8} {'vacuum':>10} {'hbar_QNG':>10} {'hbar/0.233':>10} {'a_L/l_P':>10}")
print()

beta = beta_phi_0
vacuum = 1.0  # start with vacuum = 1
for i in range(0, 51, 5):
    beta_i = beta_phi_0 * 1.10**i
    vacuum_i = 1.0 * 0.95**i
    hbar_i, aL_i, aM_i = compute_state(beta_i, vacuum_i)
    if hbar_i > 0:
        print(f"{i:>4} {beta_i:>8.4f} {vacuum_i:>10.4f} {hbar_i:>10.4f} {hbar_i/hbar_ref:>10.3f} {aL_i/l_P:>10.3f}")

print()
print("OBSERVATIONS:")
print(f"  Reference (now):     hbar = {hbar_ref:.4f}, a_L = {aL_ref/l_P:.3f} l_P")
print(f"  After 1 step (+10% beta, -5% vacuum):")
print(f"    hbar = {hbar_1:.4f} ({(hbar_1/hbar_ref-1)*100:+.2f}% change)")
print(f"    a_L = {aL_1/l_P:.3f} l_P ({(aL_1/aL_ref-1)*100:+.2f}% change)")
print()
print("  Key formula: hbar scales as sqrt(beta) approximately")
print("  10% increase in beta -> ~5% increase in hbar")
print("  5% decrease in vacuum -> negligible (vacuum is already small)")
print()
print("  After 50 iterations of exponential growth:")
print(f"    beta has multiplied by {1.10**50:.0f}x")
print(f"    hbar has multiplied by ~{np.sqrt(1.10**50):.0f}x")
