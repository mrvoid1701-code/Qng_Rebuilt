# Prereg QNG-CPU-039: Sigma Identification

Status: `locked`
Locked before: first run of `qng_sigma_identification_reference.py`
Theory doc: `DER-GOV-004` (`qng-sigma-identification-v1.md`)

## Test objective

Determine the physical role of native field `sigma` by testing:
1. Whether sigma = C_eff (expected FALSIFIED)
2. Whether sigma ∝ C_eff with corr > 0.5 (expected SUPPORTED)
3. Whether C_eff is a stronger proxy for sigma than L_eff (expected SUPPORTED)
4. Whether sigma is recoverable from (C_eff, L_eff) jointly (OPEN)

## Setup

- n_nodes = 16, steps = 500
- Seeds: [20260325, 42, 137, 1729, 2718]
- use_history = True and use_history = False (comparison)

## Locked predictions

### P1: sigma ≠ C_eff
corr(sigma, C_eff) < 1.0 on ALL 5 seeds — EXPECTED TRUE

### P2: sigma ∝ C_eff (positive)
corr(sigma, C_eff) > 0.5 on ALL 5 seeds — EXPECTED TRUE

### P3: sigma also couples positively to L_eff
corr(sigma, L_eff) > 0.3 on ALL 5 seeds — OPEN (sigma drives chi which drives L_eff)

### P4: sigma recoverable from (C_eff, L_eff) jointly
R²(sigma ~ C_eff + L_eff) > 0.7 on ALL 5 seeds — EXPECTED TRUE

## Decision rule

PASS if P1 + P2 + P3 + P4 are all true on all 5 seeds.
CONDITIONAL if P2 fails on one seed but passes on four.
FAIL if P2 fails on more than one seed.

## Note on C_eff vs L_eff primacy

Whether C_eff or L_eff is the stronger proxy for sigma may be
topology-dependent (tier-2 signal). If C_eff primacy fails but P2 and P4
pass, the correct verdict is: sigma couples to the FULL effective layer
(C_eff and L_eff), with topology-dependent weighting.
