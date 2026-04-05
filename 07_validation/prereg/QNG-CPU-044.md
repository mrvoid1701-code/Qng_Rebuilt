# QNG-CPU-044

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

3D vortex ring lifetime — measuring T_lifetime at BETA_PHI=0.02 in v5 substrate

## Purpose

QNG-CPU-043 confirmed that a phi vortex ring is dynamically stable for 700 Phase-2
steps (1000 total). But it did NOT measure T_lifetime — the time at which the ring
eventually collapses. This test extends Phase 2 from 700 to 4700 steps to find when
collapse occurs.

T_lifetime is a PRIMARY INPUT to the a_M fixing program: the ring must live long
enough to constitute a "stable" matter particle at the relevant physical timescale.
If T_lifetime is too short, the vortex ring cannot serve as matter — a different
stabilization mechanism is needed.

A PASS means: T_lifetime > 1000 Phase-2 steps AND is measurable (ring collapses
before Phase-2 T=4700). This gives a concrete number for the a_M fixing program
and confirms the ring is a long-lived (not transient) substrate structure.

## Inputs

- [qng-native-update-law-v5.md](../../04_qng_pure/qng-native-update-law-v5.md)
- [qng-matter-stability-v1.md](../../04_qng_pure/qng-matter-stability-v1.md)
- [qng_ring_lifetime_reference.py](../../tests/cpu/qng_ring_lifetime_reference.py)

## Experimental design

**Lattice:** L=20, N=8000, periodic BC — identical to QNG-CPU-043.

**Parameters:** Identical to QNG-CPU-043:
alpha=0.005, beta=0.35, beta_phi=0.02, delta=0.20, epsilon=0.0,
chi_decay=0.005, chi_rel=0.35, sigma_ref=0.5, gamma_phi=0.10.
Ring: center=(10,10,10), R=5.

**Protocol:**
1. Phase 1 (T=0..300): phi equilibration, GAMMA_PHI=0. Sigma autonomous.
2. Phase 2 (T=300..5000, up to 4700 steps): Channel F active (GAMMA_PHI=0.10).
3. Check every 200 Phase-2 steps:
   - z_ring (find z-plane of min sigma in rho ∈ [R-3, R+3])
   - R_t (mean rho of sigma < 0.35 nodes near z_ring)
   - n_wind (nonzero winding plaquettes, all 3 types)
   - core_sigma
4. Collapse criterion: R_t < R/4 = 1.25 for two consecutive checkpoints.
   T_lifetime = first checkpoint where R_t < R/4.
5. If ring has not collapsed by Phase-2 T=4700: report T_lifetime = "> 4700".

## Checks

**Check 1 — Ring alive at Phase-2 T=700 (QNG-CPU-043 window):**
```
R_t > 2.5 at Phase-2 T=700
```
Must reproduce QNG-CPU-043 result (R_t=4.84 at T=700). Gate is R_t > 2.5.

**Check 2 — T_lifetime measurable (ring collapses before T_max):**
```
T_lifetime < 4700 Phase-2 steps
```
The ring must eventually collapse within the extended simulation. If it never
collapses, T_lifetime = "> 4700" and Check 2 fails (the ring is meta-stable
for > 4700 steps — a strong result, reported as lower bound).

**Check 3 — Ring is long-lived (T_lifetime > 1000 Phase-2 steps):**
```
T_lifetime > 1000
```
The ring must survive at least 1000 Channel F steps to constitute a long-lived
substrate structure. Gate 1000 is the "matter stability threshold" — below this,
the ring is transient; above it, it qualifies as a dynamically stable particle.

**Check 4 — Decay is gradual (not sudden collapse):**
```
R_t at T_lifetime/2 > R_t at T_lifetime * 2
```
The ring should shrink gradually, not collapse discontinuously. R_t at the
midpoint of the lifetime should be at least twice R_t at collapse threshold.

## Decision rule

**Overall PASS** if Checks 1, 3, 4 pass (Check 2 may fail if ring never collapses —
that is actually a stronger result for the matter program).

**Interpretation of PASS:**
T_lifetime measured. The vortex ring constitutes a long-lived dynamical structure
in the v5 QNG substrate. This motivates:
- a_M fixing: T_lifetime enters the particle lifetime constraint
- QNG-CPU-045: ring self-velocity completes the kinematic characterization
- Together: ring mass, lifetime, velocity — the three kinematic quantities for matter

**Interpretation of FAIL:**
- Check 1 fails: QNG-CPU-043 result not reproduced — recheck implementation.
- Check 3 fails (T_lifetime < 1000): Ring is transient. Need larger R, smaller BETA_PHI,
  or a topologically stabilized geometry (vortex line, not ring).

## Artifact paths

- `07_validation/audits/qng-ring-lifetime-reference-v1/report.json`
- `07_validation/audits/qng-ring-lifetime-reference-v1/summary.md`
