# Paper Results v1

Type: `note`
ID: `NOTE-GOV-015`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Provide the manuscript-style results section for the rebuilt QNG paper using only support levels already earned in the rebuild.

## Results

### 1. Native update and effective-layer results

The first result of the rebuild is that the native QNG update law supports a stable and reproducible memory-sensitive reference implementation. The native update is not only structurally defined but numerically controlled. This matters because the rebuilt program now places memory inside the substrate dynamics rather than only in phenomenological interpretation.

The second result is that the native layer supports a split effective reduction. The rebuild no longer treats one scalar as carrying all effective content. Instead, the current support favors a two-channel reduction:

- `C_eff` for coherence / compatibility structure
- `L_eff` for memory-load structure

This split is one of the strongest architectural results of the rebuild because it replaces the legacy compression in which one field had to serve geometric, historical, and phenomenological roles at the same time.

### 2. Cross-hardware reproducibility result

The rebuilt native update has already passed a direct CPU/GPU agreement test. The reported maximum discrepancy between the CPU and GPU paths is

`max_diff = 1.3322676295501878e-15`

which is far below the declared tolerance used in the agreement audit.

This matters for the manuscript because it shows that the native update law is not only conceptually defined but also numerically reproducible across correctness and acceleration lanes. In the present rebuild, CPU remains the correctness lane and GPU the scale lane, but the agreement result shows that the native update layer already behaves as one coherent numerical object.

### 3. GR-facing recovery results

The GR-facing side is currently the strongest recovery lane of the rebuild. The present support chain is:

`C_eff -> geometry proxy -> Lorentzian signature proxy -> weak-field assembly -> linearized curvature proxy`

The most important qualitative result is that the rebuilt theory no longer stops at isolated geometric proxies. It already supports a coherent weak-field assembly in which the metric-side construction is internally aligned with the back-reacted acceleration proxy. This is the point at which the GR-facing lane becomes more than a collection of local surrogates.

The curvature-side result also matters. The linearized curvature step is already marked `proxy-supported`, and the rebuilt status map now treats the GR side as having crossed from object-level support to assembled weak-field structure. This does not amount to exact Einstein recovery, but it does establish a disciplined GR-facing ladder rather than a loose heuristic analogy.

### 4. QM-facing recovery results

The QM-facing side is also real, but it is not strongest in the same place as the GR side. The present QM ladder is:

`(C_eff, phi) -> correlator proxy -> local generator proxy -> mode/spectrum proxy`

The strongest QM-side result is not continuity closure. It is the generator-and-spectrum structure that emerges from the rebuilt local complex update picture. This is an important clarification produced by the rebuild: the QM lane is currently better described as generator-led than continuity-led.

This result matters because it prevents the paper from forcing the QM side into a stronger or more standard field-theoretic reading than the current support justifies. The rebuild therefore supports a real QM-facing lane, but one whose strongest present form is local generator and spectral organization rather than exact balance-law closure.

### 5. Bridge and source-response results

The bridge layer now has more than parallel GR-facing and QM-facing constructions. It has:

- a back-reaction proxy closure
- a source-response consistency step

The source-response result is particularly important. In the source-response audit, a geometry-only fit yields

`ratio = 0.7126219623332939`

while the source-augmented fit yields

`ratio = 0.44926739673107696`

for the history-enabled case, corresponding to an improvement of

`ratio_improvement_history = 0.26335456560221693`

This means the rebuilt bridge is not functioning only as a conceptual coexistence layer. The source-side sector already improves the response-side description in a controlled and numerically visible way. That is still not a final closure theorem, but it is stronger than a purely parallel proxy architecture.

### 6. Downstream phenomenology results

The rebuilt program now supports downstream phenomenology across five branches:

- trajectory
- lensing
- rotation
- timing
- cosmology

The key result here is architectural as much as phenomenological. These branches now descend from the same rebuilt core rather than being allowed to back-define the ontology. In manuscript terms, this means the phenomenology section can be presented as a derived consequence layer rather than as a substitute for foundational structure.

### 7. Comparative recovery result

The rebuild has produced an important asymmetry:

- GR recovery is ahead of QM recovery

More precisely:

- the GR side is strongest at weak-field metric assembly and linearized curvature organization
- the QM side is strongest at local generator and mode/spectrum organization

This asymmetry is a result, not a defect in presentation. It is one of the clearest things the rebuild has made visible. The present paper should therefore state that the rebuilt theory is already strong enough to support both a GR-facing lane and a QM-facing lane, while also being explicit that the GR lane is presently more mature in assembly terms.

### 8. Supported-result boundary

The present results do not justify the following claims:

- exact Einstein recovery
- exact canonical quantization recovery
- exact back-reaction closure
- final matter ontology
- universal `tau`

The rebuilt manuscript should therefore present its results as a strengthened recovery architecture with validated proxy ladders and controlled downstream phenomenology, not as a finished unification theorem.

## Results summary

The strongest present result of the rebuild is that a native memory-sensitive substrate can be reduced to a split effective layer, can support a stronger GR-facing lane, a strengthening QM-facing lane, a nontrivial bridge/source-response layer, and multiple derived phenomenology branches without allowing those downstream layers to define the theory. This is the main positive result that the paper has already earned.
