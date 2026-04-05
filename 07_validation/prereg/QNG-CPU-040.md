# QNG-CPU-040

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Sigma deficit stability — confirming the sigma channel is purely dissipative

## Purpose

Verify the claim from `DER-QNG-025` that the sigma channel alone cannot sustain stable
localized matter. A localized coherence deficit (no external source) must decay on
timescale ~1/alpha, regardless of chi coupling. This is a POSITIVE result: confirming
dissipation proves that stable matter requires topological protection (phi winding),
not just substrate relaxation.

If confirmed (decay matches prediction): the current v3/v4 substrate does not support
self-sustaining matter from sigma dynamics alone. The matter stability program requires
a phi vortex simulation (QNG-CPU-041).

## Inputs

- [qng-matter-stability-v1.md](../../04_qng_pure/qng-matter-stability-v1.md)
- [qng-native-update-law-v3.md](../../04_qng_pure/qng-native-update-law-v3.md)
- [qng_sigma_stability_reference.py](../../tests/cpu/qng_sigma_stability_reference.py)

## Experimental design

**Lattice:** 1D ring, N=200 nodes, periodic BC.

**Initial condition:** 3 center nodes (98,99,100) set to sigma_0 = 0.1 (deep coherence
deficit). All other nodes at sigma_ref = 0.5. No clamping — source is FREE to evolve.

**Parameters:** alpha=0.005, beta=0.35, delta=0.20, chi_decay=0.005, chi_rel=0.35.

**Protocol:**
1. Initialize state with localized sigma deficit (no source clamping).
2. Run 3000 steps.
3. Record at each step: max |delta_C| at center, integral |delta_C| over all nodes.
4. Fit decay of max |delta_C(center)| vs time to exp(-alpha_fit * t).
5. Compare alpha_fit to theoretical alpha=0.005.

## Checks

**Check 1 — Deficit decays to near-zero:**
```
max |delta_C(center)| after T=3000 steps < 0.01
```
(3000 * alpha = 15 decay times → final value < exp(-15) * 0.4 ≈ 3e-8, well below gate)

**Check 2 — Integral decay rate matches exp(-alpha*t) within 10%:**
```
|alpha_fit / alpha - 1| < 0.10
```
where alpha_fit is fitted to the TOTAL INTEGRAL Σ|delta_C(t)| over all nodes.
On a closed ring, the beta (diffusion) term sums to zero exactly, so the total
integral decays as exp(-alpha*t) with no diffusion correction. This gives a clean
measurement of alpha with no geometric bias.

**Check 3 — Total integral dissipates to near-zero:**
```
Σ|delta_C| at T=3000 < 0.001
```
(3000 steps = 15 decay times → predicted residual ~ initial × exp(-15) ≈ 5e-9)

**Check 4 — Chi coupling does not change sigma decay rate (within 5%):**
```
|alpha_fit_chi / alpha_fit_nochi - 1| < 0.05
```
Run with delta=0.20 (with chi) and delta=0 (no chi). The integral decay rate must
be nearly identical — confirming chi does not feed back into sigma in v3.

## Decision rule

**Overall PASS** if all four checks pass.

**Interpretation of PASS:**
The sigma channel is purely dissipative. Localized coherence deficits decay at rate
~alpha with or without chi coupling. Stable matter cannot arise from sigma dynamics
alone. This confirms the structural claim of DER-QNG-025: matter stability requires
topological protection (phi winding numbers), not substrate relaxation. This motivates
QNG-CPU-041 (phi vortex stability test).

**Interpretation of FAIL:**
- Check 1/2 fail: sigma deficit does not decay — unexpected stabilization exists in
  the current update law. Investigate whether chi→sigma feedback is accidentally present.
- Check 3 fails: coherence anomaly conserved (not dissipated) — check conservation laws.
- Check 4 fails: chi coupling affects sigma decay — v3 update law has accidental coupling.

## Artifact paths

- `07_validation/audits/qng-sigma-stability-reference-v1/report.json`
- `07_validation/audits/qng-sigma-stability-reference-v1/summary.md`
