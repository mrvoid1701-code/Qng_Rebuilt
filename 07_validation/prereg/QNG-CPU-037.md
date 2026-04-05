# QNG-CPU-037

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Gap 1 — 3D isotropy: spherical Yukawa profile on cubic lattice (z=6)

## Purpose

Provide the first numerical evidence for Assumption D2 (`AX-QNG-004`): the QNG
discrete graph Laplacian converges to the isotropic 3D continuum Laplacian on a
cubic lattice with z=6.

The 1D ring tests (QNG-CPU-029 through QNG-CPU-036) confirm the screened Poisson
model and its parameter dependences, but they cannot test 3D isotropy. This test
runs the v3 quasi-static update law on a 20³ cubic lattice, places a sigma source
at the center, and verifies that the equilibrium delta_C profile:

1. Fits a 3D Yukawa profile: delta_C(r) ~ A * exp(-r/lambda) / r
2. Matches the predicted screening length lambda_pred = sqrt(beta/(z*alpha))
3. Is isotropic: same lambda in the (1,0,0), (1,1,0), (1,1,1) directions

## Inputs

- [qng-graph-isotropy-assumption-v1.md](../../04_qng_pure/qng-graph-isotropy-assumption-v1.md)
- [qng-native-update-law-v3.md](../../04_qng_pure/qng-native-update-law-v3.md)
- [qng-poisson-assembly-v1.md](../../04_qng_pure/qng-poisson-assembly-v1.md)
- [qng_3d_isotropy_reference.py](../../tests/cpu/qng_3d_isotropy_reference.py)

## Experimental design

**Lattice:** 20³ = 8000 nodes, periodic boundary conditions, z=6 cubic neighbors.

**Parameters:** beta=0.35, z=6, alpha=0.005, delta=0.20, chi_decay=0.005,
chi_rel=0.35, phi_rel=0.20, sigma_ref=0.5.

**Predicted screening length:**
```
lambda_pred = sqrt(beta / (z * alpha)) = sqrt(0.35 / (6 * 0.005)) = sqrt(11.667) ~= 3.416
```

**Protocol:**
1. Initialize sigma near sigma_ref (±0.02 noise), chi=0, phi random.
2. Clamp source node at (10,10,10): sigma_source = 0.05 every step.
3. Run 3000 equilibration steps using v3 update law.
4. Measure equilibrium delta_C(x,y,z) = sigma(x,y,z) - sigma_ref.

**Profile measurements:**

*Spherically averaged:* bin all nodes by distance r from source (bin width 0.5).
Compute mean delta_C in each bin. Fit 3D Yukawa:
```
log(r * |mean_delta_C(r)|) = log(A) - r / lambda_sphere
```
over r in [1.5, 7.5].

*Directional profiles:*
- Along (1,0,0): nodes (10+r, 10, 10), r=1,...,8; fit as above.
- Along (1,1,0)/sqrt(2): nodes (10+r, 10+r, 10), r=1,...,6; actual distance r*sqrt(2).
- Along (1,1,1)/sqrt(3): nodes (10+r, 10+r, 10+r), r=1,...,5; actual distance r*sqrt(3).

## Checks

**Check 1 — 3D Yukawa fit quality:**
```
R^2_sphere > 0.97
```
The spherically-averaged profile must fit r*delta_C ~ A*exp(-r/lambda) well.

**Check 2 — Screening length matches prediction:**
```
|lambda_sphere / lambda_pred - 1| < 0.15
```

**Check 3 — Isotropy: all three directional lambdas within 15% of each other:**
```
max(lambda_x, lambda_xy, lambda_xyz) / min(lambda_x, lambda_xy, lambda_xyz) < 1.20
```

**Check 4 — Directional lambdas each within 20% of lambda_pred:**
```
|lambda_d / lambda_pred - 1| < 0.20  for d in {x, xy, xyz}
```

**Check 5 — Delta_C is negative everywhere (coherence depletion, not injection):**
```
mean_delta_C(r) < 0  for r in [1, 8]
```

## Decision rule

**Overall PASS** if all five checks pass.

**Interpretation of PASS:**
The 3D cubic QNG substrate produces an isotropic screened Poisson profile. Assumption
D2 is numerically supported for z=6. Gap 1 of the Newtonian limit program is partially
closed: the cubic lattice (one specific graph satisfying D2's sufficient conditions)
produces isotropic emergent gravity.

**Interpretation of FAIL:**
- Check 1 fails: profile is not Yukawa. Increase N or equilibration steps.
  Check that lambda_pred << N/2 = 10.
- Check 2 fails: wrong functional dependence on z. Verify z=6 in code.
  Note: the 1D ring used z=2; the 3D cubic uses z=6 — lambda changes by sqrt(3).
- Check 3 fails: anisotropy detected. The cubic lattice should be isotropic at leading
  order; anisotropy at order (Delta_u/lambda)^2 is expected but sub-percent for
  lambda >> 1. If lambda ~ 1, the lattice anisotropy is not suppressed.
- Check 4 fails: systematic offset. Check fit range.
- Check 5 fails: sign error in source setup or potential convention.

## Artifact paths

- `07_validation/audits/qng-3d-isotropy-reference-v1/report.json`
- `07_validation/audits/qng-3d-isotropy-reference-v1/summary.md`
