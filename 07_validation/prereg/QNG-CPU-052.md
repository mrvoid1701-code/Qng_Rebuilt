# QNG-CPU-052

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

v6 wave propagation speed — Klein-Gordon dispersion test with Channel G

## Purpose

DER-QNG-030 predicts that v6 (Channel G: sigma_i += k_back*chi_i) produces a
Klein-Gordon wave with substrate speed:
```
v_substrate = sqrt(beta)  [lattice units/step, for k_back << 2*beta/chi_rel]
```

This test initializes a spherical sigma perturbation and measures how fast it
propagates. Verifying v_measured ≈ sqrt(beta) = sqrt(0.35) ≈ 0.592 confirms
the dispersion relation and grounds Constraint C3:
```
tau/a = sqrt(beta)/c = 0.592/c
```

With C3 + C1 (G_Newton matching): a ≈ 4.6 l_Planck for m_node = m_proton.

## Inputs

- [qng-native-update-law-v6.md](../../04_qng_pure/qng-native-update-law-v6.md) — DER-QNG-030
- [qng_wave_propagation_reference.py](../../tests/cpu/qng_wave_propagation_reference.py)

## Experimental design

**Lattice:** L=32, N=32768 (larger than ring tests for wave propagation room)

**Initialization:** Gaussian sigma perturbation at center (cx, cy, cz) = (L/2,L/2,L/2)
```
sigma_i = sigma_ref + A_perturb * exp(-r²/(2*w²))
```
where A_perturb=0.05 (small, linear regime), w=2.0 (width), r = distance from center.
chi_i = 0, phi_i = 0 everywhere (vacuum, no vortex rings).

**k_back values tested:** 0.01, 0.05, 0.1  (Channel G strength scan)

**Wave speed measurement:**
At each step t, compute sigma deviation profile sigma(r,t) = mean_{|r_i - r|<0.5} sigma_i.
The wavefront is where sigma(r,t) - sigma_ref first exceeds threshold = A_perturb/10.
Fit r_front(t) vs t; slope = v_measured.

**Predicted speed:** v_pred = sqrt(beta) = sqrt(0.35) ≈ 0.5916 (independent of k_back
for small k_back).

## Checks

**Check 1 — Wave propagates (perturbation reaches r=8 within 50 steps):**
```
r_front(T=50) > 8  for at least one k_back value
```

**Check 2 — Speed consistent with sqrt(beta):**
```
|v_measured - sqrt(beta)| / sqrt(beta) < 0.20  (within 20%)
```
for k_back = 0.05 or 0.10.

**Check 3 — Speed independent of k_back (k_back << 2*beta/chi_rel = 2.0):**
```
|v_measured(k_back=0.01) - v_measured(k_back=0.1)| < 0.15
```

**Check 4 — Physical unit constraint (informational):**
```
tau/a = v_measured / c
a = m_proton / (2.247e7 * kg/m) if m_node = m_proton
Report a in units of l_Planck
```

## Decision rule

**Overall PASS** if Checks 1, 2 pass.

**Interpretation:**
- PASS: v6 propagates at sqrt(beta); tau/a = 0.592/c is the correct substrate speed;
  with G matching, a ≈ 4.6 l_Planck for m_node = m_proton
- FAIL Check 1: wave doesn't propagate — Channel G too weak or wrong sign
- FAIL Check 2: wave speed wrong — dispersion relation differs from DER-QNG-030 prediction

## Artifact paths

- `07_validation/audits/qng-wave-propagation-v1/report.json`
- `07_validation/audits/qng-wave-propagation-v1/summary.md`
