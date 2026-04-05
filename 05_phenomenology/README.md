# Phenomenology

This folder contains application layers built on top of `QNG pure`.

Domains should remain separate.

Suggested subdomains:

- trajectory
- lensing
- rotation
- timing
- cosmology

Hard rule:

No phenomenology file may redefine a primitive QNG object.

## Scope of the phenomenology layer

The proxy files in this directory demonstrate that the rebuilt effective layer can generate objects with the correct functional form for each observable class (trajectory lags, lensing deflection, rotation support, timing delay, expansion rate).

**These are structural demonstrations of descent from the core, not quantitative predictions for real astrophysical systems.**

Effective quantitative predictions require matter sector closure. Until `M_eff` has a grounded connection to physical mass-energy with dimensional analysis and a controlled limiting case recovering Newtonian gravity, all files in this directory are formally disconnected from observational astrophysics. Any language implying otherwise must be treated as unearned until that closure is achieved.
