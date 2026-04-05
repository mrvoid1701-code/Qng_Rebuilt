# QNG Chi Status v1

Type: `note`
ID: `NOTE-QNG-007`
Status: `draft`
Author: `C.D Gabriel`

## Labeling requirement

**Any file that uses `chi` or `χ` must specify which label applies:**

- `chi_native` — native memory/load variable (substrate-level primitive candidate)
- `chi_effective` — coarse-grained effective field
- `chi_phenomenological` — observationally inferred proxy

Use without a label = unresolved. Files using unlabeled `chi` must be flagged as containing unresolved symbol status.

---

## Objective

Fix the status of `chi` in the rebuilt theory.

## Legacy observation

`chi` was used as:

- local memory coupling
- component of node state
- source for `tau`
- sometimes implicitly tied to mass via `chi = m/c`

The first role is strong.  
The last role is weak.

## Rebuild decision

`chi` remains a plausible native or near-native memory/load variable.

But the mapping

`chi = m/c`

is not locked as ontology.

## What is retained

The rebuild keeps the idea that `chi` may control or summarize local memory structure.

This is one of the more coherent ideas from the old project.

## What is explicitly downgraded

The rebuild downgrades the following from ontology to candidate phenomenological or effective hypothesis:

- `chi = m/c`
- direct universal mass-scaling from `chi`
- automatic identifiability of `chi` from trajectory amplitudes

## Immediate consequence

Future uses of `chi` must declare whether they mean:

- native memory/load variable
- effective field-like variable
- phenomenological inferred proxy

This prevents `chi` from silently inheriting mass semantics it has not earned yet.
