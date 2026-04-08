# QNG-CPU-071

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-08`
test_class: `hopfion_candidate`

## Title

Hopfion Q=1 vs ring Q=0 — gravitational field sigma_g profile

## Purpose

CPU-067..070 tested conservative stability and shape in the sigma_m/phi sector.
Now we turn on the gravitational coupling K_GM and measure the sigma_g field
around both structures.

Key question: does the sigma_g depletion around the ring/Hopfion look like a
Newtonian/Yukawa gravitational potential? Does the Hopfion produce a qualitatively
different (e.g. bipolar) gravitational signature compared to the ring?

This is the "short path" to checking whether the Hopfion is a viable particle
candidate: not just stable, but also sourcing the right kind of gravitational field.

## Upstream

- DER-QNG-033: v7 two-field substrate
- DER-QNG-035: double-Yukawa gravitational potential
- QNG-CPU-069: PASS — both structures are effective conservative solitons
- QNG-CPU-070: Hopfion core fills 2x slower (topological protection in shape)

## Experimental design

- Build ring Q=0 and Hopfion Q=1 in dissipative mode WITH K_GM=0.001 (gravity on)
- Phase1=300 + Phase2=1500 dissipative steps
- Measure sigma_g profile at end of Phase 2:
  1. Z-axis profile: delta_sigma_g(RX, RY, z) along z-axis through ring center
     (shows bipolar "above/below" structure if present)
  2. Radial equatorial profile: delta_sigma_g(x, RY, RZ) along x-axis
     (shows gravitational well profile in equatorial plane)
  3. Radial shell average: delta_sigma_g(r) averaged over spherical shells
     centered on ring center (RX, RY, RZ)
- Fit radial profile to Yukawa: A * exp(-r/lambda) / r

## Checks

**Check 1 — Gravitational well exists (attractive potential):**
min(delta_sigma_g) < 0 at ring/Hopfion location. Gate: min < -1e-4.

**Check 2 — Hopfion signal stronger than ring:**
|min(delta_sg_hopfion)| > |min(delta_sg_ring)|.
Gate: Hopfion gravitational well deeper than ring.

**Check 3 — Yukawa fit lambda > 0:**
Fit of radial shell average to A*exp(-r/lambda)/r gives lambda in [1, L/2].
Gate: lambda is finite and positive.

**Check 4 — Bipolar structure (informational):**
Compare delta_sigma_g at z > RZ+3 vs z < RZ-3 (north vs south of ring plane).
Informational: records whether asymmetry exists.

## Decision rule

PASS if Check 1 and Check 2 pass.

## Artifact paths

- `07_validation/audits/qng-hopfion-gravity-v1/report.json`
- `07_validation/audits/qng-hopfion-gravity-v1/summary.md`
