# Relearning QNG

Clean-room reconstruction of Quantum Node Gravity from first principles.

Author/Owner: `C.D Gabriel`
Date opened: `2026-03-25`
Status: `active rebuild`

## Purpose

This workspace rebuilds the theory in the correct order:

1. `GR pure`
2. `QM pure`
3. `GR-QM bridge`
4. `QNG pure`
5. `Phenomenology`
6. `Validation and governance`

The older repo is treated as historical source material, not as canonical structure.

## Core rule

No file may mix:

- ontology and evidence
- derivation and governance
- claim and test result
- theory definition and phenomenology fit

## Directory map

- `00_meta/`: project rules, reconstruction order, testing policy
- `01_gr_pure/`: GR-only foundations and derivations
- `02_qm_pure/`: QM-only foundations and derivations
- `03_gr_qm_bridge/`: bridge objects, shared limits, consistency layers
- `04_qng_pure/`: QNG ontology, axioms, operators, internal dynamics
- `05_phenomenology/`: observational consequences built on top of QNG core
- `06_claims/`: explicit claims with dependencies
- `07_validation/`: prereg, tests, manifests, evidence
- `08_governance/`: freezes, switches, decision logs
- `09_templates/`: document templates
- `10_exports/`: renderable paper and figure assets
- `data/`: datasets only
- `scripts/`: runners and utilities only
- `tests/cpu/`: CPU test entrypoints
- `tests/gpu/`: GPU test entrypoints

## Immediate build standard

- every new concept starts as `axiom`, `definition`, or `derivation`
- every claim must cite exact upstream dependencies
- every test must declare `CPU`, `GPU`, or `CPU+GPU`
- phenomenology cannot introduce new primitive objects
- governance cannot change theory silently

## First milestone

Build a strict minimal backbone:

- GR primitives
- QM primitives
- bridge dictionary
- QNG primitive ontology
- one dependency-traceable claim chain
- one CPU test lane and one GPU test lane scaffold

## Current map

Canonical rebuild navigation:

- [master-index-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/master-index-v1.md)
- [rebuild-status-map-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/rebuild-status-map-v1.md)
- [hard-open-problems-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/hard-open-problems-v1.md)
- [recovery-comparison-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/recovery-comparison-v1.md)
- [next-attack-order-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/next-attack-order-v1.md)
- [core-freeze-candidate-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/core-freeze-candidate-v1.md)
- [core-manual-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/core-manual-v1.md)
- [qng-gr-effective-source-matching-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-gr-effective-source-matching-v1.md)
- [qng-qm-propagator-composition-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-propagator-composition-proxy-v1.md)
- [paper-spine-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/paper-spine-v1.md)
- [paper-abstract-candidate-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/paper-abstract-candidate-v1.md)
- [paper-introduction-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/paper-introduction-v1.md)
- [paper-contribution-list-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/paper-contribution-list-v1.md)
- [figure-plan-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/figure-plan-v1.md)
- [paper-methods-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/paper-methods-v1.md)
- [paper-results-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/paper-results-v1.md)
- [paper-discussion-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/paper-discussion-v1.md)
- [paper-conclusion-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/paper-conclusion-v1.md)
- [paper-figures-draft-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/paper-figures-draft-v1.md)
- [paper-full-draft-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/paper-full-draft-v1.md)
- [paper-full-draft-v2.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/paper-full-draft-v2.md)
- [paper-figure-pack-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/10_exports/paper_figures/paper-figure-pack-v1.md)
- [experimental-lanes-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/08_governance/experimental-lanes-v1.md)
