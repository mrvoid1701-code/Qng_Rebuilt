# QNG-CPU-054

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-06`
test_class: `structural_prediction`

## Title

v6 massless wave propagation — clean Klein-Gordon dispersion test (L=64, w=16, delta=0)

## Purpose

QNG-CPU-052 FAILED: v_meas=0.17 ≠ v_pred=0.59. Root cause (CLAUDE.md):
- Overdiffusive regime: sigma diffusion τ_diff≈2 steps << chi buildup 1/chi_decay=200 steps
- w=2 too narrow: mass-dominated regime (m²=k_back×delta >> v²k²), wave barely propagates
- Threshold wavefront method unreliable for diffusion-dominated dynamics

DER-QNG-032 (H=T+E, this session) identifies the fix:
- Set delta=0: massless wave (m²=0), pure dispersion ω²=v²k², group=phase velocity
- Widen to w=16: long-wavelength regime where KG dispersion is clean
- Reduce chi_decay to 0.001: less dissipation
- Track wave packet PEAK (r_peak vs t) instead of threshold wavefront
- L=64: room for wave to propagate 20+ lattice units before boundary effects

**Predicted speed (massless, DER-QNG-032 §4):**
```
v²_eff = k_back * beta   (chi_rel=0 case, or k_back << 2*beta/chi_rel)
v_pred(k_back) = sqrt(k_back * beta) = sqrt(k_back * 0.35)
```

k_back scan:
```
k_back=0.10: v_pred = sqrt(0.035) ≈ 0.187
k_back=0.50: v_pred = sqrt(0.175) ≈ 0.418
k_back=1.00: v_pred = sqrt(0.35)  ≈ 0.592  (maximum, DER-QNG-030 prediction)
```

The DER-QNG-030 v_pred = sqrt(beta) = 0.592 corresponds to k_back=1 (strong coupling).

## Inputs

- [qng-hamiltonian-conservative-limit-v1.md](../../04_qng_pure/qng-hamiltonian-conservative-limit-v1.md) — DER-QNG-032
- [qng-native-update-law-v6.md](../../04_qng_pure/qng-native-update-law-v6.md) — DER-QNG-030
- [qng_wave_kg_reference.py](../../tests/cpu/qng_wave_kg_reference.py)
- QNG-CPU-052 result (FAIL, overdiffusive diagnosis)

## Experimental design

**Lattice:** L=64, periodic boundary conditions

**Initialization:** Gaussian sigma perturbation:
```
sigma_i = sigma_ref + A_perturb * exp(-r²/(2*w²))
```
A_perturb=0.03, w=16, chi_i=0, phi_i=0 (vacuum).

**Parameters:** Same as CPU-052 except delta=0, chi_decay=0.001, L=64, w=16:
- alpha=0.005, beta=0.35, delta=0 (massless), chi_decay=0.001
- chi_rel=0.35, beta_phi=0, gamma_phi=0, epsilon=0 (vacuum, no phi)

**k_back values:** [0.10, 0.50, 1.00]

**Wave speed measurement — peak tracking:**
At each step t, compute spherical shell average sigma(r,t) for r in [0, L/2].
Find r_peak(t) = r where sigma_dev = sigma(r,t) - sigma_ref is maximum.
For a spherical wave packet, r_peak increases at v_group.
Fit r_peak(t) linearly for t in [t_start, MAX_STEPS] where r_peak > w.
Slope = v_measured.

**Run length:** MAX_STEPS=200 (vs 80 in CPU-052)

## Checks

**Check 1 — Wave packet propagates (r_peak > 2w at some time):**
```
r_peak(t_final) > 32  for k_back=1.00
```
The wave packet must travel past its initial size (2w=32) within 200 steps.

**Check 2 — Speed consistent with k_back-dependent prediction:**
```
For k_back=1.00: |v_meas - sqrt(0.35)| / sqrt(0.35) < 0.20
```
The strong-coupling limit should give v ≈ sqrt(beta) = 0.592 (DER-QNG-030 prediction).

**Check 3 — Speed scales with sqrt(k_back) as predicted:**
```
v_meas(k_back=1.00) / v_meas(k_back=0.10) in [2.0, 4.5]
```
Predicted ratio = sqrt(1.0/0.10) = sqrt(10) ≈ 3.16.

**Check 4 — Wave is not purely diffusive (informational):**
Fit the sigma(r,t) profile to distinguish ballistic peak (moves at v_pred) from
diffusive peak (r_peak ~ sqrt(t)). Report chi² for linear vs sqrt fit.

## Decision rule

**Overall PASS** if Checks 1 and 2 pass.

**Interpretation:**
- PASS: v6 substrate supports Klein-Gordon waves; v_pred = sqrt(k_back × beta) confirmed;
  setting k_back=1, v=c closes the unit system (C3): a ≈ 4.6 l_Planck
- FAIL Check 1: wave doesn't propagate — check Channel G implementation and k_back sign
- FAIL Check 2: speed wrong — dispersion relation incorrect; investigate sigma-chi coupling

## Artifact paths

- `07_validation/audits/qng-wave-kg-v1/report.json`
- `07_validation/audits/qng-wave-kg-v1/summary.md`
