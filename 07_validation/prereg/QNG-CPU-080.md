# QNG-CPU-080

Type: `prereg`
Status: `diagnostic_pass`
Author: `C.D Gabriel`
Date: `2026-04-20`
test_class: `derivation_verification`

## Title

Winding-number diagnostic on cached v8 vortex rings: is the 2pi poloidal
topology preserved by Phase-1 + Phase-2 evolution?

## Purpose

QNG-CPU-079 (DER-QNG-046 cancellation test) failed because the cached
ring's phi appeared quadrupolar, not a 2pi vortex. That was a visual
observation. This test measures the winding number directly by sampling
phi on closed loops and integrating phi differences with the correct
angle-periodic wrap.

Key question: does Phase-1 (300 lu, no V_couple) + Phase-2 (1000 lu,
V_couple on) preserve the 2pi poloidal winding installed by
`init_phi_single_ring`?

If YES: CPU-079 would need a finer loop geometry but DER-QNG-046 § 5
cancellation is still testable.
If NO:  the winding is destroyed by v8 dynamics, and DER-QNG-046 § 5
cancellation is meaningless for v8 rings because the premise (O(2)
vortex) does not apply — v8 is sine-Gordon and has no U(1) invariance.

## Upstream

- DER-QNG-046 (§5 cancellation assumes 2pi winding)
- DER-QNG-042 (v8 canonical, V_couple = (g/2)(dsigma_m)^2(1-cos phi))
- QNG-CPU-079 (diagnostic_fail; visual observation of quadrupolar phi)
- Memory: project_tesla_gauge_falsified.md — v8 has only Z winding
  symmetry; V_couple is sine-Gordon (explicit U(1)->Z breaking)

## Experimental design

Load the cached `ring_L28_R4_P1_300_P2_1000_*.npz` (MISS of CPU-079).
Compare with a fresh evaluation of `init_phi_single_ring(L=28, R=4)`
— the Phase-1 initial condition.

For each field compute the winding number on four loop families:

Loop A -- poloidal at azimuth 0 (plane (x, z) at y = y_c),
         radii r_loop in {1.0, 1.5, 2.0, 2.5}.
Loop B -- poloidal at azimuth pi/2 (plane (y, z) at x = x_c).
Loop C -- axial line through the ring hole along z (reference).
Loop D -- equatorial loop in plane z = z_c, radius R+r.

Each loop is sampled at 128 points using angle-safe interpolation
(cos and sin interpolated separately, then reconstructed via arctan2
— naive phi interpolation averages across the +-pi branch cut and
destroys winding at the singularity).

Winding formula:
    W = (1 / 2pi) * ( sum_k wrap(phi[k+1] - phi[k]) + wrap(phi[0] - phi[N-1]) )

where `wrap(d)` maps differences into (-pi, pi].

## Gates (diagnostic)

| ID | Criterion |
|----|-----------|
| G1 | |W_A|, |W_B| on initial condition >= 0.95 at all r_loop (validates algorithm) |
| G2 | |W_A|, |W_B| on cached ring >= 0.95 at r_loop = 2.0 (topology preserved) |
| G3 | W_D on cached ring ~ 0 (no spurious toroidal winding) |

## Result

| Gate | Evaluation | Pass/Fail |
|------|------------|-----------|
| G1   | Initial condition W_A = W_B = +1.000 at r_loop in {1.0, 1.5, 2.0, 2.5} | PASS |
| G2   | Cached ring W_A = W_B = 0.000 at ALL r_loop; phi_range = [-0.48, +0.94] at r=2 | **FAIL** |
| G3   | Cached W_D = 0 (consistent, no toroidal winding injected or generated) | PASS |

### Ring phi stats (cached)

- `phi.min() = -2.312`, `phi.max() = +2.159`, `|phi|_max = 2.312 < pi`
- The full cached field never reaches +-pi anywhere.

### Initial phi stats (reference)

- `phi.min() = -2.897`, `phi.max() = +3.142` (= +pi, as expected at ring core)

## Verdict

**DIAGNOSTIC_PASS** (the diagnostic itself ran correctly and delivered a
definitive answer); result is **topology_lost**: v8 Phase-1 + Phase-2
evolution destroys the 2pi poloidal winding installed by
`init_phi_single_ring`.

## Interpretation

This is the expected behavior in v8. V_couple has the sine-Gordon form
`(1 - cos phi)` — explicit reduction U(1) -> Z. The vacuum manifold is
the discrete set of points `phi mod 2pi = 0`, not a circle. Therefore
phi is really a real-valued field (the lift of the angle), and a "2pi
winding" configuration is smoothly deformable to phi=0 by paying
gradient + potential energy. This is exactly what the Phase-1
relaxation does: phi relaxes from the initial vortex toward a smooth
quadrupolar pattern with |phi| < pi everywhere.

Consequences:

1. The "vortex ring" structure in v8 is a SIGMA_M structure only
   (topological sigma_m deficit, conserved by Channel F balance) — the
   phi part is a soft sine-Gordon "dimple", not a protected vortex.
2. DER-QNG-046 §5 cancellation via u -> -u antisymmetry of cos(phi_bg)
   requires phi_bg = arctan2(dy, dx) with 2pi winding around the tube.
   The cached phi_bg is quadrupolar with |phi|<1.1, cos(phi_bg) ~
   0.5..0.88, no zero-crossings along in-plane paths. Cancellation
   does NOT occur.
3. The 100x gap between scalar V_couple prediction (alpha ~ 10 rad)
   and measured alpha (~10^-2 rad) cannot be explained by cos(phi_bg)
   cancellation at ALL — the mechanism is absent by construction.
4. DER-QNG-038 baryon ladder identification must be reinterpreted:
   what is conserved is the sigma_m mass deficit (Channel F balance),
   NOT the phase topology.

Alternative mechanisms remain on the table and now carry the full
weight of explaining the measurement:

- **Eikonal breakdown**: lambda_pkt = 2pi/k_pkt = 8 lu ~ R = 4 lu.
  Pulse is in diffraction regime, not geometric optics.
- **Amplitude modulation**: measured Delta y of pulse includes
  amplitude growth 0.035 -> 0.040, not pure deflection.
- **O(A^2) back-reaction**: 2.5e-3 matches measured 10^-2 order.

## Next steps

1. DER-QNG-046 §5 cancellation mechanism: **formally retracted** as
   applicable to v8. The EOM §1-§4 remain correct structurally.
2. DER-QNG-038 baryon ladder: needs a "conservation-charge-first"
   rewrite — M_ring is a Noether charge from Channel F balance, and
   the spin-isospin identification must come from the deficit profile
   shape, not phase topology.
3. Forcing winding via pinning would require an explicit U(1)-invariant
   sector, which v8 does not have. No `CPU-081 force-winding` test is
   viable without modifying v8. Would have to add a separate U(1) gauge
   field or abandon V_couple's (1-cos phi) form. Record as blocked.

## Artifact paths

- `tests/cpu/qng_ring_winding_diagnostic.py`
- `07_validation/audits/qng-ring-winding-diag-v1/report.json`
