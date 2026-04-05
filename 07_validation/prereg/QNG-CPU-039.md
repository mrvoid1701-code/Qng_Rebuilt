# QNG-CPU-039

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Gap 1 closure — D2 holds on perturbed cubic lattice (second-moment condition test)

## Purpose

Verify that Assumption D2 (AX-QNG-004) holds approximately for an irregular graph,
specifically a cubic lattice with random node-position perturbations of amplitude
0.3 lattice spacings. This tests the claim from `DER-QNG-024` that:

1. The second-moment condition `Σ_j ê_ij ⊗ ê_ij ≈ (z/3)·I` holds per node with
   small (< 0.30) deviation for modest perturbations.
2. The resulting Yukawa profile remains approximately isotropic despite graph
   irregularity, with isotropy ratio < 1.35.

If confirmed: Gap 1 of `DER-QNG-011` is formally closed for any graph satisfying the
second-moment condition approximately, with quantitative bound on residual anisotropy.
The cubic lattice is not special — any statistically isotropic graph with bounded
coordination number produces an approximately isotropic Laplacian at physical scales.

## Inputs

- [qng-graph-isotropy-formal-v1.md](../../04_qng_pure/qng-graph-isotropy-formal-v1.md)
- [qng-graph-isotropy-assumption-v1.md](../../04_qng_pure/qng-graph-isotropy-assumption-v1.md)
- [qng_perturbed_lattice_isotropy_reference.py](../../tests/cpu/qng_perturbed_lattice_isotropy_reference.py)

## Experimental design

**Lattice:** 20³ = 8000 nodes. Each node at grid position (ix, iy, iz) is displaced
by a random vector (δx, δy, δz) with each component drawn from Uniform[-0.3, 0.3]
lattice spacings. Connectivity: each node connected to its 6 nearest Euclidean
neighbors under periodic boundary conditions.

**Parameters:** alpha=0.005, beta=0.35, z=6, delta=0.20, sigma_ref=0.5,
sigma_source=0.05. Same as QNG-CPU-037.

**Perturbation amplitude:** 0.3 lattice spacings (each component independently).

**Protocol:**
1. Build perturbed lattice (positions + nearest-neighbor adjacency).
2. Compute second-moment tensor per node; record mean and max anisotropy deviation.
3. Clamp source at center node. Run 3000 equilibration steps.
4. Compute δ_C = sigma - sigma_ref profile.
5. Fit 3D Yukawa profile (spherical average).
6. Extract directional λ fits along (1,0,0), (1,1,0), (1,1,1).

## Checks

**Check 1 — Yukawa fit quality:**
```
R² of spherical Yukawa fit > 0.95
```

**Check 2 — λ within 20% of prediction:**
```
|λ_sphere / λ_pred - 1| < 0.20
where λ_pred = sqrt(beta/(z*alpha)) = sqrt(0.35/(6*0.005)) ≈ 3.416
```

**Check 3 — Isotropy ratio < 1.35:**
```
max(λ_100, λ_110, λ_111) / min(λ_100, λ_110, λ_111) < 1.35
```
(Wider tolerance than cubic's 1.20, reflecting graph irregularity)

**Check 4 — Angular octant isotropy < 1.45:**
```
max(λ_octant) / min(λ_octant) < 1.45
```
where λ is fit independently in each of 4 angular octants (physical distances).
Tolerance reflects theoretical prediction: per-sector anisotropy scales as ε_max=0.3,
giving expected λ spread of ±15% (ratio ~1.3–1.4).

**Check 5 — δ_C < 0 in far field:**
```
delta_C(r) < 0  for all 1 ≤ r ≤ 8  (coherence depletion, not enhancement)
```

**Check 6 — Mean off-diagonal elements ≈ 0 (statistical isotropy):**
```
max |mean(T_ab)| < 0.05   for a ≠ b in {x,y,z}
```
where T_i = Σ_j ê_ij ⊗ ê_ij and the mean is over all nodes. Tests that off-diagonal
contributions cancel on average (statistical isotropy), even though individual nodes
may have large off-diagonal terms of order ε. Tests DER-QNG-024 §3.

Note: the per-node Frobenius deviation ||T_i - (z/3)I||_F is expected to be large
(~1.0–2.0) for perturbation 0.3 — this is normal and does not indicate a problem.
Only the node-averaged quantities are physically relevant for the coarse-grained Laplacian.

**Check 7 — Mean diagonal of second-moment tensor ≈ z/3:**
```
|mean(T_aa) - z/3| / (z/3) < 0.05   for each a in {x,y,z}
```
Tests that on average, the diagonal of the SMC holds to within 5%.

## Decision rule

**Overall PASS** if all seven checks pass.

**Interpretation of PASS:**
Assumption D2 holds approximately for the perturbed cubic lattice. The second-moment
condition is satisfied with per-node deviation consistent with DER-QNG-024's prediction
(~ε_max for perturbation ε_max=0.3). Gap 1 is formally closed for statistically
isotropic graphs with bounded perturbations — the cubic lattice is not a special case.

**Interpretation of FAIL:**
- Check 1/2/3/4 fail: perturbation amplitude 0.3 is too large; graph irregularity
  breaks the continuum approximation at the chosen simulation scale.
- Check 6 fail: second-moment deviation larger than predicted — reassess DER-QNG-024 §3.
- Check 7 fail: systematic anisotropy bias; graph construction may not be isotropic on average.

## Artifact paths

- `07_validation/audits/qng-perturbed-lattice-isotropy-reference-v1/report.json`
- `07_validation/audits/qng-perturbed-lattice-isotropy-reference-v1/summary.md`
