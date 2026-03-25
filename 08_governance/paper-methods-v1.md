# Paper Methods v1

Type: `note`
ID: `NOTE-GOV-014`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Provide the manuscript-style methods section for the rebuilt QNG paper.

## Methods

### 1. Reconstruction principle

The present work uses a clean-room reconstruction protocol rather than a cumulative edit of the earlier QNG project. The reason is methodological: the earlier project contained useful theoretical material, but its growth path allowed ontology, bridge assumptions, phenomenology, and validation to compress into each other too early. The rebuild therefore treats the older project as historical source material, not as canonical structure.

The reconstruction order is fixed:

`GR pure -> QM pure -> bridge -> QNG pure -> phenomenology`

This ordering is not cosmetic. It is the main control mechanism used to prevent downstream empirical structure from silently defining the native theory.

### 2. Workspace layer discipline

Each category in the rebuilt workspace has a strict role.

- `01_gr_pure` contains only GR-side objects that make sense without QNG-native primitives.
- `02_qm_pure` contains only QM-side objects that make sense without QNG-native primitives.
- `03_gr_qm_bridge` contains only translation and consistency layers between GR-facing and QM-facing descriptions.
- `04_qng_pure` contains the native QNG ontology, update laws, and native emergent objects.
- `05_phenomenology` contains only downstream application layers derived from the core.
- `06_claims` contains dependency-traceable claims.
- `07_validation` contains preregistration, tests, and validation artifacts.
- `08_governance` contains freezes, status maps, and manuscript-control notes.

The layer rule is enforced to stop the manuscript from doing three common failure modes:

- using phenomenology to invent primitives
- using governance notes to silently rewrite theory
- using tests to define ontology after the fact

### 3. Document typing and dependency control

Every file is required to carry one primary role. The rebuild uses the following main document classes:

- `axiom`
- `definition`
- `derivation`
- `note`
- `claim`
- `test`
- `evidence`
- `decision`

This constraint matters because the paper is written against a dependency graph, not against a loose notebook structure. A derivation may derive; it may not report validation results. A validation artifact may test a claim; it may not redefine a primitive object. A governance file may freeze or classify content; it may not create a new scientific object.

### 4. Native-theory reconstruction strategy

The rebuilt native theory was developed by starting from the minimum substrate-level commitments that remained defensible after separation from legacy compression. The resulting provisional backbone is:

- a relational substrate
- local node state containers
- a local history-sensitive update law

The rebuild then asks what coarse-grained objects are actually needed downstream. This led to a split effective layer rather than a one-field structure:

- `C_eff` as coherence / compatibility content
- `L_eff` as memory-load content

This split is treated as a reconstruction result, not as a cosmetic relabeling. It was introduced because the old project asked one scalar object to support too many incompatible roles.

### 5. Recovery-ladder method

The rebuilt paper does not present exact unification as already established. Instead, it uses recovery ladders.

On the GR-facing side, the ladder is:

`C_eff -> geometry proxy -> Lorentzian signature proxy -> weak-field assembly -> linearized curvature proxy`

On the QM-facing side, the ladder is:

`(C_eff, phi) -> correlator proxy -> local generator proxy -> mode/spectrum proxy`

The bridge is treated as a third ladder:

- back-reaction proxy closure
- source-response consistency

This ladder-based method is central to the paper. It allows partial recovery to be stated honestly without being mistaken for a final theorem.

### 6. Status classification method

The manuscript uses a three-level support classification.

- `proxy-supported`
  a construct has an explicit definition, a bounded role, and direct numerical or structural support in the rebuilt validation stack
- `candidate`
  a construct is coherent and central to the current architecture, but lacks the level of closure required for stronger status
- `open`
  the issue remains unresolved, theorem-level incomplete, or interpretively unstable

This classification is used throughout the rebuild to stop stronger language from entering the paper prematurely. In particular, exact Einstein recovery, exact canonical quantization recovery, final matter ontology, and universal `tau` remain open.

### 7. Validation standard

Validation is hardware-explicit from the beginning of the rebuild.

- CPU is the correctness lane
- GPU is the scale lane
- CPU/GPU agreement is required whenever the same object exists on both lanes

Every important numerical object is expected, over time, to develop a validation chain of the form:

- CPU reference test
- GPU reproduction or stress test
- CPU/GPU agreement test

This matters for the paper because it prevents speed-oriented numerics from silently replacing canonical numerics. In the rebuilt program, the CPU version defines correctness; the GPU version must reproduce that result within declared tolerance.

### 8. Phenomenology containment rule

Phenomenology is treated strictly as a downstream layer. Trajectory, lensing, rotation, timing, and cosmology are introduced only after the core, effective layer, and bridge sectors have already been stated.

The manuscript therefore treats phenomenology as a consequence layer rather than a theory-defining layer. This is a deliberate correction to the older growth path, where phenomenological success could implicitly reshape the interpretation of the core.

### 9. Manuscript restraint rule

The paper is written under a restraint principle:

- support architecture strongly
- support proxy ladders honestly
- mark exact recovery programs as unfinished

This rule is methodological, not rhetorical. Its purpose is to keep the rebuilt QNG program technically readable and scientifically defensible while it remains in a provisional stage.

## Methods summary

The methods of this paper are therefore not only numerical or formal. They are also architectural. The rebuilt QNG manuscript is produced by controlled separation of layers, dependency-traceable reconstruction of the native theory, ladder-based recovery claims, and hardware-explicit validation. This is the mechanism by which the paper converts QNG from a historically compressed framework into a disciplined reconstruction program.
