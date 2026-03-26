# QNG-CPU-038

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`

## Title

Tau identification — falsification of universal scalar tau,
confirmation of per-node history-driven timescale

## Purpose

Test the legacy claim that a universal scalar `tau` governs the QNG
substrate. Check whether the three config memory timescales are equal
and whether any universal per-node tau emerges from the dynamics.

## Inputs

- [qng-tau-identification-v1.md](../../08_governance/qng-tau-identification-v1.md)
- [qng_tau_identification_reference.py](../../tests/cpu/qng_tau_identification_reference.py)

## Seeds tested

20260325 (default), 42, 137, 1729, 2718

## Checks

1. `cv(tau_config) > 0.1` — three config timescales not equal (no universal tau)
2. `cv(tau_node) > 0.1` on default seed — per-node tau not constant
3. `corr(tau_node, mem) > 0.6` on all 5 seeds — tau tracks memory field
4. `mean_tau_hist > 2 * mean_tau_nohist` on all 5 seeds — history amplifies tau
5. `cv(mean_tau_hist across seeds) < 0.10` — mean tau relatively stable across topologies

## Decision rule

Pass if all preregistered checks pass.
The test passing means: universal scalar tau is falsified; per-node
history-driven tau is the supported identification.
