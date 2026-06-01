# QNG-CPU-080 audit summary — Ring winding-number diagnostic

Type: `evidence`
Status: `diagnostic_pass` (result: topology_lost)
Author: `C.D Gabriel`
Date: `2026-04-20`
Upstream: `DER-QNG-046`, `QNG-CPU-079`

## Purpose

Measure the 2pi poloidal winding number on the cached v8 L=28 R=4 ring
and compare with the initial condition `init_phi_single_ring`.

## Gates

| Gate | Criterion | Result |
|------|-----------|--------|
| G1 algorithm validity | |W| >= 0.95 on initial at all r_loop | PASS (W = +1.000 at all r) |
| G2 topology preserved | |W_A|, |W_B| >= 0.95 on cached at r=2  | **FAIL** (W = 0.000) |
| G3 no toroidal winding | W_D ~ 0 on cached | PASS |

## Quantitative results

Initial condition `init_phi_single_ring(28, 4)`:
- Poloidal W at r_loop in {1.0, 1.5, 2.0, 2.5}: +1.000, +1.000, +1.000, +1.000
- phi_range on r=2 loop: [-3.10, +3.14]
- Full 2pi winding intact (as designed).

Cached ring after Phase-1 (300 lu) + Phase-2 (1000 lu) under v8 dynamics:
- Poloidal W at r_loop in {1.0, 1.5, 2.0, 2.5}: 0.000 (all)
- phi_range on r=2 loop: [-0.48, +0.94]
- Global field stats: min=-2.312, max=+2.159, |phi|_max=2.312 < pi
- No 2pi winding anywhere; field is fully in the principal branch.

Axial line (z-axis through hole):
- Initial: total phase change +3.74 (crosses +-pi once)
- Cached:  total phase change +2.32 (smooth, no crossing)

## Root cause

V_couple = (g/2) (sigma_m_ref - sigma_m)^2 (1 - cos phi) is **sine-Gordon**.
The vacuum manifold of V_couple is the DISCRETE set {phi = 0 mod 2pi},
not a U(1) circle. Therefore phi is a real-valued field (lift of the
angle) and "2pi winding" is smoothly deformable to phi=0 by paying a
finite energy cost. Phase-1 relaxation makes the phi field shed the
vortex by Goldstone-like relaxation into the principal branch.

This is the Z winding symmetry noted in the Tesla-gauge falsification
memory (`project_tesla_gauge_falsified.md`): v8 chi is not a U(1) gauge
connection, and phi is not a U(1) phase — it is a real scalar with a
periodic potential.

## Implications

1. **DER-QNG-046 §5 cancellation** (u -> -u antisymmetry of cos(phi_bg)
   integrated against Delta * d_y Delta on a loop around a 2pi vortex):
   the premise is absent from v8. Cancellation is NOT a candidate
   mechanism for the measured 100x alpha gap.
2. **v8 "vortex rings" are sigma_m structures**, not phi vortices. What
   is conserved is the Channel-F-balanced mass deficit, not phase
   topology.
3. **DER-QNG-038 baryon ladder** must be reinterpreted: M_ring is a
   Noether charge of the sigma_m sector, not a topological charge of
   phi. Spin-isospin identification via ring radius R remains open
   (no longer has a phase-winding underpinning).
4. **The 100x alpha gap** in DER-QNG-044 Test 3f is now carried by
   the remaining candidates only:
     - Eikonal breakdown (lambda ~ R)
     - Amplitude modulation (not pure deflection)
     - O(A^2) back-reaction (matches magnitude)
5. **Forcing a 2pi winding in v8 is unphysical**: would require adding
   an explicit U(1) gauge sector, which contradicts DER-QNG-042.
   CPU-081 "force winding" is recorded as BLOCKED at the theory level.

## Surviving vs falsified

| Item | Status |
|------|--------|
| DER-QNG-046 §1-§4 EOM derivation | surviving |
| DER-QNG-046 §5 cancellation for v8 rings | **retracted** |
| DER-QNG-046 m_eff^2 = (g/(2mu_phi)) Delta^2 cos(phi_bg) formula | still correct, but phi_bg is now a quadrupolar soft pattern, not arctan2 |
| DER-QNG-038 baryon M_ring conservation | surviving (Channel F deficit, unchanged) |
| DER-QNG-038 "vortex ring topology" framing | **needs rewrite** — sigma_m deficit, not phi winding |

## Files

- `tests/cpu/qng_ring_winding_diagnostic.py`
- `07_validation/audits/qng-ring-winding-diag-v1/report.json`
- `07_validation/prereg/QNG-CPU-080.md`
