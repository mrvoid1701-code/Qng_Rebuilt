"""QNG-CPU-125 -- Extend M_ring measurement to R=8, 9, 10.

Phase C1 / Gap 13 discrimination test.

Question: is the M_ring(R) ratio pattern matching hadron mass ratios
a structural feature of QNG (continues smoothly to higher R) or a
4-point coincidence (breaks at R>7)?

Existing data (CPU-074/075):
  R=3: 474.15
  R=4: 728.92
  R=5: 954.88
  R=6: 1172.13
  R=7: 1328.10

Predicted continuation if pattern is structural:
  R=8: ?
  R=9: ?
  R=10: ?

Hadron candidates above Delta(1700):
  N(1675), Delta(1905), N(1990), Delta(2200) — many possibilities

If M_ring(R=8..10) follows similar quasi-linear progression in R, the
pattern is reinforced as structural. If not, DER-QNG-038 ladder is
4-point coincidence.

Implementation:
  - Same protocol as CPU-074/075, but L=28 to fit larger rings
  - NumPy vectorized for speed
  - PHASE1 = 300, PHASE2 = 1500, canonical snapshot at T_P2=1000
"""
import numpy as np
import time

# Parameters (identical to CPU-074/075)
L = 28
N = L**3

SIGMA_REF = 0.5
ALPHA     = 0.005
BETA      = 0.35
BETA_PHI  = 0.02
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
GAMMA_PHI = 0.10
K_BACK    = 0.10  # not used in conservative protocol

PHASE1 = 300
PHASE2 = 1500

# Build coord arrays
xs = np.arange(L)
X, Y, Z = np.meshgrid(xs, xs, xs, indexing='ij')

# Center
RC = L // 2
DX = ((X - RC) + L//2) % L - L//2  # signed distance with periodic wrapping
DY = ((Y - RC) + L//2) % L - L//2
DZ = ((Z - RC) + L//2) % L - L//2

RHO = np.sqrt(DX.astype(float)**2 + DY.astype(float)**2)

def init_phi(R):
    """phi_init = atan2(z, rho - R)"""
    return np.arctan2(DZ.astype(float), RHO - R)

def neighbor_sum(field):
    """Sum over 6 neighbors with periodic BC."""
    return (np.roll(field, 1, axis=0) + np.roll(field, -1, axis=0) +
            np.roll(field, 1, axis=1) + np.roll(field, -1, axis=1) +
            np.roll(field, 1, axis=2) + np.roll(field, -1, axis=2))

def neighbor_avg(field):
    return neighbor_sum(field) / 6.0

def wrap(x):
    """Wrap angle to (-pi, pi]"""
    return ((x + np.pi) % (2*np.pi)) - np.pi

def disorder(phi):
    """1 - |neighbor avg of e^{i phi}|"""
    cs = neighbor_sum(np.cos(phi)) / 6.0
    sn = neighbor_sum(np.sin(phi)) / 6.0
    return np.maximum(0.0, 1.0 - np.sqrt(cs**2 + sn**2))

def mean_phi_neighbor(phi, sm):
    """Sigma_m-weighted angular average of neighbor phi."""
    # Sum sm_j * cos(phi_j) over neighbors
    csm = (np.roll(sm*np.cos(phi), 1, axis=0) + np.roll(sm*np.cos(phi), -1, axis=0) +
           np.roll(sm*np.cos(phi), 1, axis=1) + np.roll(sm*np.cos(phi), -1, axis=1) +
           np.roll(sm*np.cos(phi), 1, axis=2) + np.roll(sm*np.cos(phi), -1, axis=2))
    ssm = (np.roll(sm*np.sin(phi), 1, axis=0) + np.roll(sm*np.sin(phi), -1, axis=0) +
           np.roll(sm*np.sin(phi), 1, axis=1) + np.roll(sm*np.sin(phi), -1, axis=1) +
           np.roll(sm*np.sin(phi), 1, axis=2) + np.roll(sm*np.sin(phi), -1, axis=2))
    tw = neighbor_sum(sm)
    safe = tw > 1e-10
    pm = np.zeros_like(phi)
    pm[safe] = np.arctan2(ssm[safe]/tw[safe], csm[safe]/tw[safe])
    pm[~safe] = phi[~safe]
    return pm

def step_phase1(sg, sm, chi, phi):
    sgb = neighbor_avg(sg)
    smb = neighbor_avg(sm)
    nsg = np.clip(sg + ALPHA*(SIGMA_REF-sg) + BETA*(sgb-sg), 0, 1)
    nsm = np.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm), 0, 1)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(sgb-sg) + DELTA*(SIGMA_REF-sg)
    pm = mean_phi_neighbor(phi, sm)
    np_ = wrap(phi + BETA_PHI*wrap(pm - phi))
    return nsg, nsm, nc, np_

def step_phase2(sg, sm, chi, phi):
    sgb = neighbor_avg(sg)
    smb = neighbor_avg(sm)
    nsg = np.clip(sg + ALPHA*(SIGMA_REF-sg) + BETA*(sgb-sg), 0, 1)
    dsm = ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm) - GAMMA_PHI*disorder(phi)*sm
    nsm = np.clip(sm + dsm, 0, 1)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(sgb-sg) + DELTA*(SIGMA_REF-sg)
    pm = mean_phi_neighbor(phi, sm)
    np_ = wrap(phi + BETA_PHI*wrap(pm - phi))
    return nsg, nsm, nc, np_

def ring_mass(sm):
    return float(np.sum(np.maximum(0.0, SIGMA_REF - sm)))

def run_radius(R):
    sg = np.full((L, L, L), SIGMA_REF)
    sm = np.full((L, L, L), SIGMA_REF)
    chi = np.zeros((L, L, L))
    phi = init_phi(R)
    t0 = time.time()
    for _ in range(PHASE1):
        sg, sm, chi, phi = step_phase1(sg, sm, chi, phi)
    track = []
    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_phase2(sg, sm, chi, phi)
        if t in (500, 1000, PHASE2):
            track.append((t, ring_mass(sm)))
    elapsed = time.time() - t0
    M_canonical = track[1][1]  # T_P2=1000
    return M_canonical, track, elapsed

print("=" * 80)
print("QNG-CPU-125: M_ring extension to R=8, 9, 10")
print("=" * 80)
print(f"L = {L}, PHASE1 = {PHASE1}, PHASE2 = {PHASE2}")
print()

# First verify protocol by reproducing R=4 (should be 728.92 +/- some)
print("Reproducibility check: re-running R=4 (CPU-074 gave 728.92 at L=20)...")
M4, track4, elapsed4 = run_radius(4)
print(f"  M(R=4, L={L}) = {M4:.2f} (CPU-074 gave 728.92 at L=20)")
print(f"  Elapsed: {elapsed4:.1f} s")
print(f"  Track: {track4}")
print()

# L=28 may give different M than L=20 due to lattice size effect
# Let me also compare R=6, 7 to existing data at L=20
print("Reproducibility at L=28 (existing data was L=20):")
for R in [3, 5, 6, 7]:
    M_R, track_R, elapsed_R = run_radius(R)
    print(f"  R={R}: M = {M_R:.2f}, elapsed = {elapsed_R:.1f} s")
    print(f"    track: {track_R}")
print()

print("=" * 80)
print("New measurements R=8, 9, 10 at L=28")
print("=" * 80)
results = {}
for R in [8, 9, 10]:
    print(f"--- R={R} ---", flush=True)
    M_R, track_R, elapsed_R = run_radius(R)
    results[R] = M_R
    print(f"  M(R={R}) = {M_R:.2f}, elapsed = {elapsed_R:.1f} s")
    print(f"    track: {track_R}")
    print()

# ============================================================
# Pattern analysis
# ============================================================
print("=" * 80)
print("Pattern analysis")
print("=" * 80)
print()

# Combine new + existing CPU-074/075 (at L=20)
M_all_L20 = {3: 474.15, 4: 728.92, 5: 954.88, 6: 1172.13, 7: 1328.10}
M_all_L28_new = results.copy()
M_all_L28_new[4] = M4

print("Existing CPU-074/075 data (L=20):")
print(f"{'R':>4} {'M_ring':>10} {'M(R)/M(R=4)':>14}")
for R, M in M_all_L20.items():
    ratio = M / M_all_L20[4]
    print(f"{R:>4} {M:>10.2f} {ratio:>14.4f}")
print()

print("New L=28 data:")
print(f"{'R':>4} {'M_ring':>10} {'M(R)/M(R=4)_L28':>16}")
for R, M in sorted(M_all_L28_new.items()):
    ratio = M / M_all_L28_new[4]
    print(f"{R:>4} {M:>10.2f} {ratio:>16.4f}")
print()

# Check linearity: is M(R) approximately linear in R?
import numpy as np
R_arr = np.array([3, 4, 5, 6, 7])
M_arr = np.array([M_all_L20[r] for r in R_arr])
slope, intercept = np.polyfit(R_arr, M_arr, 1)
print(f"L=20 linear fit: M(R) = {slope:.2f} * R + {intercept:.2f}")
predicted_R = slope * np.array([8, 9, 10]) + intercept
print(f"  Predicted M(R=8, 9, 10) at L=20: {predicted_R}")
print()

# Predict L=28 from quasi-linear pattern
R_arr_L28 = np.array(sorted(M_all_L28_new.keys()))
M_arr_L28 = np.array([M_all_L28_new[r] for r in R_arr_L28])
if len(R_arr_L28) >= 3:
    slope28, intercept28 = np.polyfit(R_arr_L28, M_arr_L28, 1)
    print(f"L=28 linear fit (across R=4 + new R=8,9,10): M(R) = {slope28:.2f} * R + {intercept28:.2f}")
    print(f"  This relies on consistency between L=20 R=4 and L=28 R=4 measurements.")
print()

# Verdict
print("=" * 80)
print("VERDICT")
print("=" * 80)
print()
# Hadron progression: D(1700), N*(1675), N(1875), Delta(1905), N(1900) etc.
# Above R=7, the hadron spectrum becomes denser and ambiguous to identify.
# Key check: does M(R) continue to grow quasi-linearly?
if 8 in results:
    growth_8 = results[8] - M_all_L28_new.get(7, M_all_L20[7])
    growth_typical = (M_all_L20[7] - M_all_L20[3]) / 4  # avg per R step in L=20 data
    print(f"Growth M(R=8) - M(R=7) = {growth_8:.1f}")
    print(f"Average growth per R step in L=20 data = {growth_typical:.1f}")
    print()
    if abs(growth_8 - growth_typical)/growth_typical < 0.3:
        print(f"=> Pattern CONTINUES quasi-linearly at R=8.")
        print("   Likely structural, not coincidental.")
    else:
        print(f"=> Pattern BREAKS at R=8 (growth differs by >30%).")
        print("   Could be coincidence or finite-size artifact.")

print()
print("Detailed analysis pending: compare with PDG hadron resonance spectrum")
print("and check if R-progression matches a quantum-number ladder.")
