# QNG Sigma Identification v1

Type: `derivation`
ID: `DER-GOV-004`
Status: `proxy-supported`
Author: `C.D Gabriel`
Prereq: `DER-GOV-002` (chi identification), `DER-GOV-003` (tau identification)

## Objective

Determine the physical role of the native field `sigma` and test whether it is
reducible to the effective field `C_eff`, to `L_eff`, or to any linear combination
of the two.

## Background

The rebuild replaced the old overloaded scalar with the split effective layer
`(C_eff, L_eff)`. The native field `sigma` was retained as a primitive in the
native state `(sigma, chi, phi)`. But its relationship to the effective layer
has not been tested.

From the simulation kernel:

```
C_eff_i = 0.45 * sigma_i
        + 0.35 * (1 - mismatch_i)
        + 0.20 * (1 + cos(phase_i)) / 2

L_eff_i = 0.60 * mem_i + 0.40 * |chi_i|
```

This means:
- `sigma` is one of three inputs to `C_eff` with weight 0.45
- `sigma` does not appear in `L_eff`
- `C_eff != sigma` by construction

## Claims

### Claim A: sigma = C_eff

Prediction: FALSIFIED

Argument: By construction, `C_eff` includes `mismatch` and `phase` channels
that are independent of `sigma`. After a rollout, the mismatch and phase
channels carry independent history-driven variation. So `corr(sigma, C_eff)`
must be strictly less than 1.0, and the equality is falsified at proxy level.

### Claim B: sigma ∝ C_eff (corr > 0.5)

Prediction: SUPPORTED

Argument: Since `sigma` contributes 0.45 weight to `C_eff`, and the other two
channels (mismatch, phase) are themselves partially history-coupled to sigma
through the native update, a positive correlation above 0.5 is expected on
all seeds.

### Claim C: sigma also couples positively to L_eff

Prediction: SUPPORTED (QNG-CPU-039)

Argument: Although sigma does not appear directly in L_eff, the native update
law couples sigma to chi through the neighbor and history channels. Chi then
drives L_eff directly. This indirect path makes corr(sigma, L_eff) > 0.3
on all topologies.

### Claim D: sigma is substantially recoverable from (C_eff, L_eff)

Prediction: SUPPORTED (QNG-CPU-039)

R²(sigma ~ C_eff + L_eff) > 0.71 on all 5 seeds.

### Claim E: C_eff vs L_eff primacy is topology-dependent

Prediction: SUPPORTED (QNG-CPU-039)

On seeds 137 and 1729, corr(sigma, L_eff) > corr(sigma, C_eff). On the other
three seeds, C_eff is primary. This is a Tier-2 signal: the relative weight
of C_eff and L_eff in the sigma proxy depends on graph topology.

## Physical reidentification (proxy-level)

From QNG-CPU-039 results:

- `sigma = C_eff`: FALSIFIED — corr < 1.0 on all seeds; C_eff includes independent
  channels (mismatch, phase)
- `sigma ∝ C_eff`: SUPPORTED — corr(sigma, C_eff) ∈ [0.707, 0.954] universally
- `sigma ∝ L_eff`: PARTIALLY SUPPORTED — corr(sigma, L_eff) ∈ [0.438, 0.821];
  coupling is positive on all seeds but weaker than C_eff on most seeds
- `sigma` couples to the FULL effective layer (C_eff, L_eff), not C_eff alone
- C_eff-vs-L_eff primacy is topology-dependent (Tier-2 signal)

Physical picture:
- sigma is a self-regularizing coherence primitive
- it is the primary input to C_eff (direct, 45% weight)
- it also couples indirectly to L_eff via chi and memory dynamics
- sigma is NOT eliminable in favor of C_eff alone — L_eff adds R² gain of 0.07–0.21

## Open questions

- Is there a closed dynamical law relating sigma_i to C_eff_i in the large-N
  or long-time limit?
- Does sigma carry additional information beyond what C_eff captures
  (i.e., is R² < 1.0 nontrivially bounded away from 1.0)?
- Is sigma primitive, or can it be derived from a deeper internal node variable?

## Validation

Test: `QNG-CPU-039` — `qng_sigma_identification_reference.py`
Decision: PASS

Pass criteria:
- P1: `corr(sigma, C_eff)` < 1.0 on all K=5 seeds — PASS
- P2: `corr(sigma, C_eff)` > 0.5 on all K=5 seeds — PASS (min = 0.707)
- P3: `corr(sigma, L_eff)` > 0.3 on all K=5 seeds — PASS (min = 0.438)
- P4: R²(sigma ~ C_eff + L_eff) > 0.7 on all K=5 seeds — PASS (min = 0.713)
