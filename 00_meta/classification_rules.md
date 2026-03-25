# Classification Rules

This file defines the category system for the rebuild.

## Category meanings

### `01_gr_pure`

Contains only objects that make sense without QNG-specific primitives.

Allowed:

- spacetime structures
- metric objects
- curvature
- Einstein equations
- weak/strong field limits
- ADM, PPN, geodesics, action principles

Forbidden:

- `Sigma`, `chi`, `tau`, straton, node ontology
- dataset-specific fits
- gate thresholds

### `02_qm_pure`

Contains only objects that make sense without QNG-specific primitives.

Allowed:

- Hilbert space
- operators
- commutators
- propagators
- entanglement
- thermal and semiclassical QM foundations

Forbidden:

- graph-native QNG primitives unless introduced in bridge form
- observational fitting language

### `03_gr_qm_bridge`

Contains only translation layers between GR and QM vocabularies.

Allowed:

- semiclassical coupling maps
- continuum/discrete comparison dictionaries
- shared consistency conditions
- limiting procedures

Forbidden:

- full QNG ontology
- phenomenology fits

### `04_qng_pure`

Contains the native QNG core.

Allowed:

- ontology of nodes/edges/states
- primitive variables
- update laws
- native actions
- native constraints
- native emergent objects

Forbidden:

- direct observational claims unless they are abstract predictions
- policy switches

### `05_phenomenology`

Contains consequences of the theory once the core is fixed.

Allowed:

- flyby, lensing, rotation, CMB, cosmology mappings
- measurement-facing observables
- domain-specific effective reductions

Forbidden:

- changing primitive ontology
- retroactively redefining QNG objects to improve fit

### `06_claims`

Contains compact claim records only.

Required:

- claim statement
- status
- upstream dependencies
- downstream tests

### `07_validation`

Contains prereg, tests, manifests, evidence.

Required:

- reproducible procedures
- hardware declaration
- pass/fail criteria

### `08_governance`

Contains decision records only.

Allowed:

- freeze notes
- switch records
- version policy

Forbidden:

- new theoretical definitions

## Document types

Allowed document types:

- `axiom`
- `definition`
- `derivation`
- `note`
- `claim`
- `test`
- `evidence`
- `decision`

Every file should clearly identify exactly one primary type.

## Hard rules

1. A derivation cannot contain test results.
2. An evidence file cannot define theory primitives.
3. A claim file cannot contain free-form derivation.
4. A governance file cannot introduce scientific thresholds without explicit test references.
5. A phenomenology file must list every upstream QNG object it uses.
