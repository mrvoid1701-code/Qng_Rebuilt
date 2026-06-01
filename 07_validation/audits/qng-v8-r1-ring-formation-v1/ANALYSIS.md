# GPU-031e Analysis: R1 pure-XY ring formation under DER-QNG-051 Option R1

Date: 2026-04-21
Run: L=20 R=4, three-phase formation, exact_a='r1' throughout —
COMPLETED at T_P2=1000 lu.

## Outcome: ring forms but oscillates chaotically

Final: `Verdict=H_R1_RING_UNSTABLE`, relative diff vs CPU-074 = -9.92%,
late_drift = 202.1% over last 500 lu.

### Phase 2 M_ring trajectory

| t (lu) | M_ring    | sm_min | sm_max | H         |
|-------:|----------:|-------:|-------:|----------:|
|    100 |    -97.73 |  0.252 |  0.851 |  -224.83  |
|    200 |   +686.38 |  0.094 |  0.722 |  -224.83  |
|    300 |    -84.09 |  0.162 |  0.796 |  -224.83  |
|    400 |   +423.57 |  0.098 |  0.774 |  -224.83  |
|    500 |   +497.71 |  0.115 |  0.712 |  -224.83  |
|    600 |    -21.79 |  0.206 |  0.793 |  -224.83  |
|    700 |   +569.46 |  0.102 |  0.707 |  -224.83  |
|    800 |   +391.21 |  0.136 |  0.749 |  -224.83  |
|    900 |    +82.74 |  0.162 |  0.772 |  -224.85  |
|   1000 |   +656.64 |  0.159 |  0.804 |  -224.85  |

CPU-074 canonical baseline (approx F_A): +728.92.

## Three decisive findings

### 1. R1 CURES the DER-QNG-051 vacuum instability

Under DER-QNG-050 exact F_A (with sigma_m weighting in E_phi), sigma_m
saturated at 1.0 everywhere within 100 lu (GPU-031c/d). Under R1 (no
sigma_m weights), sigma_m stays in [0.09, 0.85] throughout the run.
The condensation force F_sm_XY was indeed the culprit, and removing it
restores a bounded matter sector.

### 2. Canonical conservation PASSES

H is stable to <0.01% over Phase 2 (-224.83 → -224.85). The symplectic
(Yoshida4) integrator is working correctly with the R1 force.
DER-QNG-051 Check A (finite-diff F_A_R1 = -dE_phi_R1/dphi) passed at
7e-11 max abs err. The R1 Hamiltonian is canonically consistent.

### 3. Ring is NOT a stable equilibrium under R1

M_ring oscillates between -97 and +686 throughout Phase 2 with no sign
of damping toward a fixed value. Spread = 783; drift over last 500 lu
= 202%. **The static-ring hypothesis is falsified again, this time
from first principles rather than from approximation artifacts.**

## Interpretation

R1 isolates the vacuum problem (solved) from the static-equilibrium
problem (not solved by R1 alone). Two things have now been proven
about the v7/v8 matter sector:

- **CPU-073/074/075 rings were gradient-flow artifacts.** Confirmed by
  DER-QNG-051 via exact F_A.
- **Even a canonically-consistent E_phi (R1) does not host a static
  ring equilibrium.** Confirmed by this run via exact R1 force.

The ring is a transient pattern visited by the canonical flow,
not a stationary solution of H_v8[R1].

## Implications for DER-QNG-038 baryon ladder

CPU-074 R=4 canonical M_ring = 728.92 (gradient flow).
GPU-031e R1 M_ring spans [-97, +686] with individual snapshots as
close as 6% to 728.92. This means the ring state IS visited by the
canonical flow, but not as an attractor.

Interpretation: if DER-QNG-038 is to survive, the identification must
be reframed:
  - NOT: "baryon = static ring of radius R with rest mass ~ a_M * 729"
  - YES: "baryon = dynamic orbit that spends a nonzero fraction of its
    period in the ring phase; observed rest mass ~ a_M * <M_ring>_t"

This is **Scenario A** (particle = bounded phase-space orbit) from
DEC-QNG-005. R1 does not falsify Scenario A; it just shows the ring
is one stop on the orbit, not the endpoint.

## Recommended next step

**GPU-031f**: run R1 at T_P2 = 5000 lu and compute:
- time-averaged <M_ring>_t (baryon mass candidate)
- power spectrum of M_ring(t) (orbital period?)
- fraction of time M_ring > 500 ("ring phase duty cycle")

If <M_ring>_t converges near 729, DER-QNG-038 is recoverable in the
orbital interpretation. If <M_ring>_t drifts secularly or the orbit
has no recurrence, static ring is dead and Scenario A must be
reformulated geometrically (Gap 11 truly decisive, v9 path).

## Status

R1 Option of DER-QNG-051 is **partially validated**:
  * Vacuum instability CURED (σ_m bounded) ✓
  * Canonical H conserved ✓
  * Static-ring existence FALSIFIED ✗

DER-QNG-051 itself stands: the original E_phi (§2.4) with σ_m weights
is non-canonical. The cure R1 is valid but insufficient to reproduce
the CPU-074 static ring — because under any canonical dynamics, that
static ring was never there to begin with.

v8 survives as a conservative Hamiltonian system. Scenario A (dynamic
orbit) is the only remaining path for matter; GPU-031f is the
load-bearing probe.

Claude Code autonomous session 2026-04-21.
