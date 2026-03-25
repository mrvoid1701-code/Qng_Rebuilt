# QNG-CPU-037

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`

## Title

Chi identification — falsification of `chi = m/c`, confirmation of `chi ∝ L_eff`

## Purpose

Test the legacy claim `chi = m/c` in the rebuilt framework. A claim is
treated as proxy-supported if its correlation exceeds 0.5 and is universal
across seeds. A claim is falsified at proxy level if its correlation is weak
and topology-dependent (changes sign across seeds).

Additionally identify the dominant actual correlate of `chi`.

## Inputs

- [qng-chi-identification-v1.md](../../08_governance/qng-chi-identification-v1.md)
- [qng_chi_identification_reference.py](../../tests/cpu/qng_chi_identification_reference.py)

## Seeds tested

20260325 (default), 42, 137, 1729, 2718

## Checks

1. `corr(chi, m/c) < 0.5` on default seed — claim not strongly supported
2. `std(corr_mc across 5 seeds) > 0.15` — claim not universal (topology-dependent)
3. `corr(chi, L_eff) > 0.5` on default seed — L_eff is dominant correlate
4. `corr(chi, L_eff) - corr(chi, m/c) > 0.3` on default seed — L_eff dominates m/c
5. `corr(chi, L_eff) > 0.5` on all 5 seeds — L_eff dominance is universal

## Decision rule

Pass if all preregistered checks pass.
The test passing means: `chi = m/c` is falsified at proxy level,
and `chi ∝ L_eff` is the supported identification.
