# QNG To QM Coherence Proxy v1

Type: `derivation`
ID: `DER-BRIDGE-003`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first clean QM-facing proxy map from rebuilt QNG variables to correlator-like and propagation-like observables.

## Inputs

- [bridge-backbone-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/bridge-backbone-v1.md)
- [qm-observables-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/02_qm_pure/qm-observables-v1.md)
- [qng-emergent-field-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-emergent-field-v1.md)

## Scope

This file does not claim full quantization.

It only claims that the rebuilt QNG dynamics can generate proxy objects that are structurally comparable to:

- two-point functions
- coherence measures
- phase-sensitive transport indicators

## Starting point

The rebuilt QNG effective layer already gives:

- `C_eff(i)` as a coherence-sensitive amplitude source
- native phase information through the node phase variable

That suggests the first complex amplitude proxy:

`psi_QNG(i) = sqrt(C_eff(i)) exp(i phi_i)`

## Correlator proxy

Define the nearest-neighbor correlator proxy:

`G_1(i) = psi_QNG(i) psi_QNG(i+1)^*`

This yields:

- amplitude-like coherence: `|G_1(i)| = sqrt(C_eff(i) C_eff(i+1))`
- phase-sensitive part: `arg G_1(i) = phi_i - phi_{i+1}`

## Propagation proxy

Define the local transport-like quantity:

`J_QNG(i) = Im G_1(i)`

This is the first local propagation proxy in the rebuild.

It is not yet a conserved quantum current.

It is only the first phase-sensitive flow indicator.

## Why this is the right QM-facing level

This construction speaks directly to the QM rebuild at the correlator level.

It does not pretend that:

- operators are already reconstructed
- commutators are already derived
- Hilbert-space structure is already proven

But it does provide a valid first bridge object:

- a bounded complex correlator-like quantity

## Weak claim

The first QM-facing QNG claim is therefore:

- native QNG dynamics may support correlator-like coherence objects before any final quantization story is fixed

## Immediate downstream question

The first bridge test should ask whether `G_1` and `J_QNG` are:

- bounded
- nontrivial
- phase-sensitive
- history-sensitive

before making any stronger QM claim.
