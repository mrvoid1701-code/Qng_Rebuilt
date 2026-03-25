# Core Freeze Candidate v1

Type: `note`
ID: `NOTE-GOV-006`
Status: `draft`
Author: `C.D Gabriel`

## Objective

State which parts of the rebuilt workspace are strong enough to be treated as a provisional core freeze candidate.

## Freeze vocabulary

This file uses three labels:

- `freeze-candidate`
- `keep-open`
- `experimental`

## Freeze-candidate core

The following parts are strong enough to be treated as the provisional rebuilt backbone:

- native memory-sensitive update as the current reference dynamical spine
- split effective layer `(C_eff, L_eff)`
- geometry proxy estimator driven primarily by `C_eff`
- GR weak-field proxy sector
- QM coherence proxy sector
- Lorentzian signature proxy
- matter-sector proxy
- back-reaction proxy closure
- source-response consistency step

## Why these are allowed into the freeze candidate

These items satisfy the current rebuild standard:

- they are dependency-traceable
- they are validated by explicit rebuilt tests
- they do not depend on legacy fit language
- they are structurally coherent across folders

## Keep-open items

The following must remain open even if the provisional core is frozen:

- exact GR recovery
- exact QM recovery
- exact back-reaction closure
- exact Lorentzian recovery
- final matter interpretation
- final ontic status of `Sigma`
- final ontic status of `chi`
- any universal `tau`

## Experimental lanes

The following should remain explicitly experimental and must not silently harden into backbone:

- continuity-style QM balance
- any mass-scaling claim tied to `chi = m/c`
- any direct phenomenology-to-ontology leap
- any real-data fit that forces new primitives

## Working freeze statement

The rebuilt workspace may now provisionally freeze the following statement:

- QNG is currently best formulated as a native memory-sensitive relational update theory whose coarse-grained split effective layer feeds geometry, bridge sectors, and downstream phenomenology proxies

This is the strongest clean statement currently supported by the rebuild.

## What the freeze does not mean

This freeze candidate does not mean:

- the theory is final
- the symbols are final
- exact GR or QM recovery has been proven
- phenomenological success has been established on real data

It means only:

- the current backbone is stable enough to build on without re-litigating its existence every step
