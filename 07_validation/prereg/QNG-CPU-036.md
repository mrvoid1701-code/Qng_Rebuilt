# QNG-CPU-036

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`

## Title

Covariance stability — universality of physical signals across graph topologies

## Purpose

Verify that the key physical signals identified on the default seed
(QNG-CPU-029 through QNG-CPU-035) are stable properties of the QNG
substrate, not artifacts of a single graph topology. Tests K=5 different
seeds.

## Inputs

- [qng-covariance-stability-v1.md](../../08_governance/qng-covariance-stability-v1.md)
- [qng_covariance_stability_reference.py](../../tests/cpu/qng_covariance_stability_reference.py)

## Seeds tested

42, 137, 1729, 2718, 31415

## Checks

1. `corr(E_tt, E_xx) < -0.5` on all K seeds
2. `w_eff ∈ (-1.0, -0.3)` on all K seeds
3. `|e_xx_coeff − e_tt_coeff| > 0.5` on all K seeds (tensor separation)
4. `std_hist > std_nohist` for c_eff on all K seeds
5. `std(w_eff across seeds) / mean(|w_eff|) < 0.20`

## Decision rule

Pass if all preregistered checks pass.
