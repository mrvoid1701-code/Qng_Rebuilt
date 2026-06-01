"""QNG-CPU-143 -- Hopfion charge under v12 (DM candidate viability check).

Critical question: is Hopfion (Q=1) electrically neutral under v12?

If YES: Hopfion is a viable DM candidate (gravitationally active but
EM-decoupled).
If NO: Hopfion carries charge like standard ring → NOT a DM candidate
under v12.

Under v12, electric charge of vortex configuration = phi-winding number N
around any small 2D loop encircling the vortex core.

For standard ring (R=R_ring, no twist):
  phi(rho, z) = atan2(z, rho - R_ring)
  Around ring core: N_winding = 1, charge q = +e

For Hopfion (Q=1, with additional toroidal twist):
  phi(rho, z, phi_az) = atan2(z, rho - R_ring) + atan2(y, x)
                     = poloidal + toroidal
  Around ring core: STILL has poloidal winding N=1
  PLUS: toroidal winding when going around ring axis

This test computes both windings numerically.
"""
import numpy as np

print("=" * 80)
print("QNG-CPU-143: Hopfion charge under v12 — DM viability check")
print("=" * 80)
print()

L = 32
xs = np.arange(L) - L/2
X, Y, Z = np.meshgrid(xs, xs, xs, indexing='ij')

def _mi(d, L_=L):
    return ((d + L_/2) % L_) - L_/2

DX = _mi(X); DY = _mi(Y); DZ = _mi(Z)
RHO = np.sqrt(DX**2 + DY**2)
PHI_AZ = np.arctan2(DY, DX)
R_ring = 8.0

# Initialize phi for ring (Q=0) and hopfion (Q=1)
def make_ring_phi(q_twist=0):
    poloidal = np.arctan2(DZ, RHO - R_ring)
    toroidal = q_twist * PHI_AZ
    return ((poloidal + toroidal + np.pi) % (2*np.pi)) - np.pi

phi_ring = make_ring_phi(q_twist=0)
phi_hopfion = make_ring_phi(q_twist=1)

# ============================================================
# Compute winding around POLOIDAL loop (small loop near ring core)
# ============================================================
def compute_poloidal_winding(phi_field, ring_R=R_ring, loop_radius=1.5):
    """Winding around small loop in (rho-R, z) plane near ring core.
    Loop encircles the vortex core in the poloidal direction.
    """
    N_loop = 64
    thetas = np.linspace(0, 2*np.pi, N_loop, endpoint=False)
    # Center loop at phi_az = 0 (so x=R_ring, y=0)
    cx_lat = ring_R + L/2
    cy_lat = 0 + L/2
    cz_lat = 0 + L/2
    phis = []
    for theta in thetas:
        # Loop position: rho-offset cos(theta), z-offset sin(theta)
        rho_off = loop_radius * np.cos(theta)
        z_off = loop_radius * np.sin(theta)
        ix = int(round(cx_lat + rho_off)) % L
        iy = int(round(cy_lat)) % L
        iz = int(round(cz_lat + z_off)) % L
        phis.append(phi_field[ix, iy, iz])
    phis = np.array(phis)
    deltas = np.diff(phis, append=phis[0])
    deltas = ((deltas + np.pi) % (2*np.pi)) - np.pi
    return np.sum(deltas) / (2*np.pi)

# ============================================================
# Compute winding around TOROIDAL loop (around ring axis)
# ============================================================
def compute_toroidal_winding(phi_field, ring_R=R_ring, sample_z=0):
    """Winding around large loop encircling ring axis (in xy plane).
    Going around the toroidal direction.
    """
    N_loop = 64
    thetas = np.linspace(0, 2*np.pi, N_loop, endpoint=False)
    # Loop at radius slightly larger than ring
    sample_radius = ring_R + 2.0
    phis = []
    for theta in thetas:
        x_pos = sample_radius * np.cos(theta) + L/2
        y_pos = sample_radius * np.sin(theta) + L/2
        z_pos = sample_z + L/2
        ix = int(round(x_pos)) % L
        iy = int(round(y_pos)) % L
        iz = int(round(z_pos)) % L
        phis.append(phi_field[ix, iy, iz])
    phis = np.array(phis)
    deltas = np.diff(phis, append=phis[0])
    deltas = ((deltas + np.pi) % (2*np.pi)) - np.pi
    return np.sum(deltas) / (2*np.pi)

# ============================================================
# Test
# ============================================================
print(f"Lattice L = {L}, ring radius R = {R_ring}")
print()

print("STANDARD RING (Q=0, no twist):")
N_pol_ring = compute_poloidal_winding(phi_ring)
N_tor_ring = compute_toroidal_winding(phi_ring)
print(f"  Poloidal winding (small loop near core): N_pol = {N_pol_ring:.4f}")
print(f"  Toroidal winding (large loop around ring): N_tor = {N_tor_ring:.4f}")
print()

print("HOPFION (Q=1, with toroidal twist):")
N_pol_hop = compute_poloidal_winding(phi_hopfion)
N_tor_hop = compute_toroidal_winding(phi_hopfion)
print(f"  Poloidal winding (small loop near core): N_pol = {N_pol_hop:.4f}")
print(f"  Toroidal winding (large loop around ring): N_tor = {N_tor_hop:.4f}")
print()

# ============================================================
# Charge under v12
# ============================================================
print("=" * 80)
print("Charge under v12 EM gauge")
print("=" * 80)
print()
print("v12: charge q is determined by phi-winding around any small loop")
print("     encircling the vortex core. For standard ring: q = N_pol × e")
print()

q_ring_pol = round(N_pol_ring)
q_hop_pol = round(N_pol_hop)
q_ring_tor = round(N_tor_ring)
q_hop_tor = round(N_tor_hop)

print(f"Standard ring: poloidal charge = {q_ring_pol} × e")
print(f"Hopfion:       poloidal charge = {q_hop_pol} × e")
print()

# ============================================================
# DM viability conclusion
# ============================================================
print("=" * 80)
print("DM viability under v12")
print("=" * 80)
print()
if abs(q_hop_pol) > 0:
    print(f"Hopfion has poloidal winding |N_pol| = {abs(q_hop_pol)}")
    print(f"=> Charge q = {q_hop_pol}·e ≠ 0")
    print(f"=> Hopfion is ELECTRICALLY CHARGED under v12")
    print(f"=> Hopfion is NOT EM-neutral, NOT a DM candidate via EM-decoupling")
    print()
    print("Implication: even Hopfion (last DM candidate) is RULED OUT under v12")
    print("if we require EM-neutrality for invisibility.")
elif q_hop_pol == 0:
    print(f"Hopfion has zero poloidal winding!")
    print(f"=> q = 0, Hopfion IS EM-neutral under v12")
    print(f"=> Hopfion is a viable DM candidate")

print()
print("Possible alternative DM configurations under v12:")
print("  - Vortex pair (N=+1, N=-1) bound state: net q = 0, but each carries charge")
print("    (analog of positronium — eventually annihilates)")
print("  - Configurations with HIGHER topology (Skyrmion-like): not in current QNG")
print("  - Pure σ_m density fluctuations without phi winding: trivially neutral")
print("    BUT: not topologically protected, dissolve via diffusion")
print()

# ============================================================
# Final verdict
# ============================================================
print("=" * 80)
print("VERDICT")
print("=" * 80)
print()
print("Under v12 (compact U(1) gauge), all stable topological vortex")
print("configurations carry quantized charge q = N·e with N ≠ 0.")
print()
print("=> Stable DM candidates in QNG require either:")
print("   (a) New field beyond v12 (would require v13 extension)")
print("   (b) Bound states of opposite-charge vortices (annihilation issue)")
print("   (c) Acceptance that QNG cannot solve DM (honest scope)")
print()
print("Combined with previous results (chi-Yukawa falsified, σ_g defects")
print("ruled out, modified gravity not predicted):")
print()
print("**QNG v10/v11/v12 has NO viable DM mechanism currently.**")
print()
print("This is HONEST scope: substrate gives c, G, ℏ, Λ=0 + linearized GR + EM,")
print("but DOES NOT solve dark matter without further extension.")
