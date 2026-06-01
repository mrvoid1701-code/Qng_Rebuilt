"""QNG-CPU-137 -- Charge quantization + Dark Matter via neutral rings (v12).

Under v12, lattice U(1) gauge theory predicts:
  - Vortex configurations with phase winding N around core have charge q = N e
  - Wilson loop quantization: charges are INTEGERS

Test:
  A. Compute winding number of standard QNG vortex ring (canonical CPU-074 init)
  B. Check if zero-winding vortex configurations exist
  C. If yes: identify them as DM candidates (gravity yes, EM no)
  D. Compute DM/baryon ratio prediction in v12 cosmology

Connection to DM Phase 2:
  Primordial vortex rings have:
    - Charged (winding=1, 2, ...) -> visible matter (electron-like, etc.)
    - Neutral (winding=0) -> DARK MATTER (couples only via gravity)

If QNG primordial cosmology produces both types in roughly equal numbers,
DM/baryon ratio could naturally arise.
"""
import numpy as np

print("=" * 80)
print("QNG-CPU-137: Charge quantization + DM via neutral rings (v12)")
print("=" * 80)
print()

# ==============================================================
# A. Standard QNG vortex winding number
# ==============================================================
print("=" * 80)
print("A. Winding number of standard QNG vortex ring")
print("=" * 80)
print()
print("Standard CPU-074 ring init:")
print("  phi_init(rho, z) = atan2(dz, rho - R)")
print()
print("This produces phi varying as theta around the (rho-R, z) plane.")
print("As you traverse a small loop around the ring core:")
print("  theta goes from 0 to 2pi, phi winds by 2pi -> winding N = 1")
print()

# Verify numerically
L = 16
xs = np.arange(L) - L/2
X, Y, Z = np.meshgrid(xs, xs, xs, indexing='ij')
RX = RY = RZ = 0
def _mi(d, L_=L):
    return ((d + L_/2) % L_) - L_/2
DX = _mi(X - RX); DY = _mi(Y - RY); DZ = _mi(Z - RZ)
RHO = np.sqrt(DX**2 + DY**2)
R_ring = 4.0
phi_init = np.arctan2(DZ, RHO - R_ring)

# Compute winding around a small loop near ring core
# Pick a point near ring (e.g., at z=0, rho=R+1) and loop in (rho, z) plane
center_rho = R_ring + 0.1
center_z = 0.0
# Sample loop of 8 points around (rho=center_rho, z=center_z)
loop_radius = 1.0
N_loop = 32
thetas = np.linspace(0, 2*np.pi, N_loop, endpoint=False)
phis_along_loop = []
for theta in thetas:
    rho_pt = center_rho + loop_radius * np.cos(theta)
    z_pt = center_z + loop_radius * np.sin(theta)
    # Convert to lattice index
    # Place at x = rho_pt (assume y=0), z = z_pt
    ix = int(round(rho_pt + L/2)) % L
    iy = int(round(0 + L/2)) % L
    iz = int(round(z_pt + L/2)) % L
    phis_along_loop.append(phi_init[ix, iy, iz])
phis_along_loop = np.array(phis_along_loop)

# Compute total winding
delta_phis = np.diff(phis_along_loop, append=phis_along_loop[0])
# Wrap to (-pi, pi)
delta_phis = ((delta_phis + np.pi) % (2*np.pi)) - np.pi
winding = np.sum(delta_phis) / (2*np.pi)
print(f"Numerical winding around loop near ring core: N = {winding:.3f}")
print(f"  (expected ≈ ±1 for standard ring init)")
print()

# ==============================================================
# B. Zero-winding configurations
# ==============================================================
print("=" * 80)
print("B. Zero-winding vortex configurations")
print("=" * 80)
print()
print("Configurations with winding N = 0:")
print("  - phi = const (trivial, no vortex at all)")
print("  - phi = phi_0(r) (radial, no angular dependence) — also trivial")
print("  - Counter-rotating pairs: ring with N=+1 + ring with N=-1 nearby")
print("    Net winding = 0 at large scales, locally each has nonzero")
print("  - 'Hopfion' (Q=1 topology): winding around its core can be nonzero")
print("    but globally Q=1 is a different topological invariant (Hopf)")
print()
print("KEY INSIGHT: a single ring with phi-winding N gives charge q = N e")
print("  - Standard ring: N=1, q = +e (electron-like? or proton-like?)")
print("  - Anti-ring:    N=-1, q = -e")
print("  - Trivial:      N=0, q = 0  (dark matter candidate!)")
print()

# Test: build a ring with N=0 (no phase winding)
print("Construct N=0 'ring' (no phase winding):")
print("  Method: phi = const, but localized sigma_m depletion")
print("  This is just a localized matter blob, not a vortex.")
print()
print("Q: Is a localized sigma_m depletion stable in QNG?")
print("  - Without phi winding: trivial topology, can dissolve into background")
print("  - Per CPU-051 etc.: stable rings need non-trivial winding")
print("  - Solitons without topological protection are unstable")
print()

# ==============================================================
# C. Stable neutral configurations
# ==============================================================
print("=" * 80)
print("C. Search for stable neutral (q=0) configurations")
print("=" * 80)
print()
print("Possibilities for stable q=0 (neutral) DM in QNG v12:")
print()
print("1. Ring-antiring bound state (N=+1 + N=-1 = 0 net charge)")
print("   - Each component is gravitationally active via sigma_m deficit")
print("   - Net EM coupling = 0")
print("   - QNG-MEMORY notes: GPU-032d showed W+W- at d=4 NOT bound (transient)")
print("   - W+W+ at d=4 also unbound (GPU-032e)")
print("   - 3-ring +++ gave anomalous mean (GPU-033a) - not understood")
print("   - Status: UNCONFIRMED stable bound state")
print()
print("2. Hopfion (Q=1 topology, but zero phi-winding around any single loop)")
print("   - QNG-MEMORY: tested in CPU-066..072 hopfion lane")
print("   - Hopfion exists but stability over long times unclear")
print("   - Could be DM candidate")
print()
print("3. sigma_g topological defects")
print("   - Independent of phi winding")
print("   - Pure gravity defects, EM-neutral by construction")
print("   - NOT YET INVESTIGATED")
print()
print("4. sigma_m fluctuation packets")
print("   - Localized sigma_m enhancements without vortex topology")
print("   - Marginally stable (decay through diffusion)")
print("   - Lifetime depends on chi-decay parameters")
print()

# ==============================================================
# D. DM/baryon ratio prediction
# ==============================================================
print("=" * 80)
print("D. DM/baryon ratio prediction in v12 cosmology")
print("=" * 80)
print()
Omega_m_obs = 0.315  # total matter
Omega_b_obs = 0.0493  # baryons
Omega_DM_obs = Omega_m_obs - Omega_b_obs  # 0.266
ratio_DM_b = Omega_DM_obs / Omega_b_obs
print(f"Observed (Planck 2018):")
print(f"  Omega_baryon = {Omega_b_obs:.4f}")
print(f"  Omega_DM     = {Omega_DM_obs:.4f}")
print(f"  DM/baryon ratio = {ratio_DM_b:.2f}")
print()
print("In QNG v12 primordial cosmology:")
print("  Each phi-winding event creates one (charged or neutral) vortex configuration")
print("  Statistically, in random field configurations:")
print("    P(N = +1) + P(N = -1) ≈ 50% (each)")
print("    P(N = 0) ≈ small fraction (typically) for SO(2)-symmetric init")
print()
print("  PROBLEM: random initial conditions favor charged (N≠0) configurations")
print("  Need MECHANISM that produces preference for neutral configs by ratio 5:1")
print()
print("  No such mechanism is currently derived from QNG.")
print()

# ==============================================================
# E. Verdict
# ==============================================================
print("=" * 80)
print("VERDICT")
print("=" * 80)
print()
print("v12 provides:")
print("  - Charge quantization (q = N e for vortex with winding N)")
print("  - Theoretical possibility of neutral DM configurations (N=0)")
print()
print("BUT:")
print("  - Stable N=0 configurations not confirmed in QNG dynamics")
print("  - DM/baryon ratio 5:1 not derived (random would favor charged)")
print("  - Hopfions tested but stability inconclusive")
print()
print("HONEST STATUS: v12 OPENS the door to DM via neutral configurations,")
print("but doesn't yet PROVIDE a working DM mechanism.")
print()
print("Next steps for DM closure in v12:")
print("  1. Verify hopfion stability over long times (extend CPU-068)")
print("  2. Search for sigma_g topological defects (new test)")
print("  3. Investigate primordial cosmology mechanism for DM/baryon = 5:1")
print()
print("Gap 15 (EM): closed structurally via v12")
print("Gap 16 (charge quantization): formal solution via v12 winding-charge correspondence")
print("DM problem: STILL OPEN, but v12 provides framework for solution.")
