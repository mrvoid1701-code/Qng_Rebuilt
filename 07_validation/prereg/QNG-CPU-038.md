# QNG-CPU-038

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Emergent noise: equilibrium sigma variance matches ring FDT prediction

## Purpose

Verify the fluctuation-dissipation (FDT) prediction from `DER-QNG-023` for the 1D
ring geometry (z=2):

```
Var_ring = eta^2 / (2 * sqrt(alpha * (alpha + 2*beta)))
```

Setting Var_ring = alpha (natural variance scale) gives:
```
eta_ring = sqrt(2 * alpha * sqrt(alpha * (alpha + 2*beta)))
```

The test runs the substrate at three noise levels (eta=0, eta_ring, 2*eta_ring) and
confirms that the equilibrium sigma variance scales as eta^2 and matches the predicted
value alpha at eta = eta_ring.

If confirmed: eta is NOT a free parameter — it is derived from alpha and beta via
the geometry-dependent FDT formula.

## Inputs

- [qng-emergent-noise-v1.md](../../04_qng_pure/qng-emergent-noise-v1.md)
- [qng-native-update-law-v3.md](../../04_qng_pure/qng-native-update-law-v3.md)
- [qng_emergent_noise_reference.py](../../tests/cpu/qng_emergent_noise_reference.py)

## Experimental design

**Lattice:** 200-node ring (1D, z=2, periodic). No source node — homogeneous equilibrium.

**Parameters:** alpha=0.005, beta=0.35, sigma_ref=0.5, gamma=0, delta=0.

**Predicted noise amplitude (ring FDT formula):**
```
sqrt(alpha*(alpha+2*beta)) = sqrt(0.005*0.705) = 0.05937
eta_ring = sqrt(2*0.005*0.05937) = sqrt(0.0005937) ~= 0.02437
```

**Predicted equilibrium sigma variance:**
```
Var_pred = alpha = 0.005
```

**Protocol:** For each eta in {0, eta_ring, 2*eta_ring}:
1. Initialize sigma = sigma_ref everywhere.
2. Run 4000 warmup steps (no sample collection).
3. Collect sigma values from all nodes over the next 1000 steps (200000 samples total).
4. Compute sample variance Var_meas.

## Checks

**Check 1 — Deterministic limit:**
```
Var_meas(eta=0) < 5e-6
```

**Check 2 — FDT prediction within 30%:**
```
|Var_meas(eta_ring) / alpha - 1| < 0.30
```

**Check 3 — eta^2 scaling within 30%:**
```
|Var_meas(2*eta_ring) / (4*alpha) - 1| < 0.30
```

**Check 4 — Ring FDT identity exact (algebraic):**
```
|eta_ring^2 / (2*sqrt(alpha*(alpha+2*beta))) / alpha - 1| < 1e-10
```

## Decision rule

**Overall PASS** if all four checks pass.

**Interpretation of PASS:**
The equilibrium sigma variance on a 1D ring is determined by the ring FDT formula.
eta is not a free parameter: eta_ring = sqrt(2*alpha*sqrt(alpha*(alpha+2*beta))) is
the unique noise amplitude consistent with Var = alpha on the z=2 ring geometry.

**Interpretation of FAIL:**
- Check 1 fails: coding error in deterministic (eta=0) branch.
- Check 2 fails: FDT prediction wrong. Check that the Fourier integral was computed
  correctly for the ring: Var = eta^2/(2*sqrt(alpha*(alpha+2*beta))).
- Check 3 fails: eta^2 scaling broken — check noise amplitude in code.
- Check 4 fails: algebraic formula error.

## Artifact paths

- `07_validation/audits/qng-emergent-noise-reference-v1/report.json`
- `07_validation/audits/qng-emergent-noise-reference-v1/summary.md`
