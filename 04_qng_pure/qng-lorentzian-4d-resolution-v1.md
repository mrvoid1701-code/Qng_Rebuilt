# QNG Lorentzian 4D Resolution v1

Type: `note`
ID: `NOTE-QNG-012`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Assess and resolve the three structural gaps documented in `qng-lorentzian-signature-proxy-v1.md` (DER-QNG-009):

- Gap 1: Dimensional mismatch — `g_sig(i) = diag(-T_sig(i), g_11(i))` is 2×2, not 4×4
- Gap 2: Spatial isotropy in 3+1D is not addressed
- Gap 3: The GR recovery ladder above the signature proxy inherits its unresolved status

This note does not close those gaps. It characterises the two available resolution paths, compares them to analogous choices in CDT, LQG, and causal sets, specifies the minimal 4×4 extension, records the experimental isotropy constraint, and states the resolution decision QNG currently takes.

## Inputs

- [qng-lorentzian-signature-proxy-v1.md](qng-lorentzian-signature-proxy-v1.md)
- [qng-emergent-geometry-v1.md](qng-emergent-geometry-v1.md)
- [qng-ontology-backbone-v1.md](qng-ontology-backbone-v1.md)

## Background

The QNG ontological backbone identifies the primitive layer as:

```
relational substrate + local history-sensitive update + derived effective field layer + derived emergent geometry
```

The geometry estimator (DER-QNG-002) produces a Euclideanised proxy. DER-QNG-009 then applies a temporal sign flip driven by the back-reaction sector to obtain:

```
g_sig(i) = diag( -T_sig(i), g_11(i) )
```

This is the first Lorentzian-signature proxy. It is explicitly 2×2. A physical 3+1D Lorentzian metric requires a 4×4 matrix with one negative-signature slot and three positive-signature slots.

The question this note addresses: how does the theory obtain — or assume — the full 4×4 structure?

---

## Section 1 — The Two Resolution Options

### Option A: Dynamic Selection (Dimensionality is Derived)

**Claim:** The graph dynamics of `N_i(t)` under `U` spontaneously produce exactly 3+1 dimensions.

**What the mechanism would need:**

1. A graph-growth or graph-pruning rule that drives the coordination structure of `G(t)` toward effective dimensionality 3+1 under coarse-graining.
2. A stability argument showing 3+1 is the unique stable attractor under generic initial conditions.
3. An asymmetry source that distinguishes exactly one direction as timelike.

**Whether QNG's current update law supports it:**

The current update law is specified only at the level of locality, discreteness, and history dependence. No explicit graph-growth rule or dimensional attractor analysis exists in the current rebuild.

**Option A is not currently supported. It is a research program, not an established result.**

---

### Option B: External Assumption (Dimensionality is Declared)

**Formal statement:**

> **QNG Structural Assumption D1:** The relational substrate `G(t)` is taken to carry three independent spatial graph directions and one temporal direction. This is not derived from the native update law. It is an external structural input characterising the class of graphs to which the theory applies.

**Consequences:**

1. The claim that "geometry emerges from the substrate" is partially qualified — the topology and dimensionality of that emergence are pre-declared.
2. What emerges is the metric coefficients, not the dimension count or signature.
3. Any statement that QNG "derives" the Lorentzian signature must be restricted to: the sign of the temporal slot is derived; the count of spatial directions is assumed.

**Option B is the intellectually honest and currently correct description of QNG's situation.**

---

## Section 2 — Comparison to CDT, LQG, and Causal Sets

| Programme     | Dimensionality handling                                           | Mechanism                                          |
|---------------|-------------------------------------------------------------------|----------------------------------------------------|
| CDT           | Simplex dimension input; macroscopic 4D geometry is output        | Regge path integral + causal foliation restriction |
| LQG           | 3+1 assumed via ADM decomposition before quantisation             | No mechanism; structural input                     |
| Causal sets   | Dimension estimated from partial order statistics                 | Myrheim-Meyer estimator                            |
| QNG (current) | 3+1 assumed as structural input (Option B)                        | No mechanism; adopted as assumption                |

**CDT** (Ambjørn, Jurkiewicz, Loll, PRL 93:131301, 2004): inputs simplex dimension, outputs macroscopic 4D de Sitter geometry via Monte Carlo. The causal foliation restriction is essential — without it the sum collapses.

**LQG**: assumes 3+1 via the ADM canonical decomposition before quantisation. QNG under Option B is structurally identical to LQG at this point.

**Causal sets**: dimension estimated from partial order statistics via the Myrheim-Meyer estimator — the only existing approach where dimension is genuinely emergent from the relational structure alone. This is what Option A would require QNG to develop.

**QNG is currently closest to LQG** in its handling of dimensionality. To move toward the causal-set position, QNG would need a dimension estimator applied to the partial order induced by `T_sig(i)` on `G(t)`.

---

## Section 3 — The Minimal 4×4 Extension

### Temporal slot (unchanged)

```
g_00(i) = -T_sig(i)   where T_sig(i) = 1 + lambda |Q_ctr(i)| + nu h_00(i) > 0
```

### Three spatial slots — Sub-option B1 (isotropy assumed)

Declare:

> **QNG Structural Assumption D2:** The three spatial metric components are isotropic in the weak-field, low-anisotropy limit: `g_11(i) = g_22(i) = g_33(i) ≡ g_sp(i)`

The minimal 4×4 proxy becomes:

```
g_sig^(4)(i) = diag( -T_sig(i), g_sp(i), g_sp(i), g_sp(i) )
```

No new graph structure is required. Consistent with the weak-field GR limit.

### Three spatial slots — Sub-option B2 (3-coloured graph, future)

Define a 3-coloured edge adjacency on `G(t)`, with per-direction coherence estimators `C_eff^(a)(i)` for `a in {1,2,3}`. Isotropy becomes a theorem only if the three colour-class statistics are statistically equivalent under `U`. This is the richer future target — not currently constructed.

### Determinant condition

```
det g_sig^(4)(i) = -T_sig(i) * g_sp(i)^3  <  0
```

holds whenever `T_sig(i) > 0` and `g_sp(i) > 0` — conditions already required by DER-QNG-009.

**Current recommendation:** Sub-option B1 (isotropy assumed) is the correct minimal extension for this rebuild stage.

---

## Section 4 — The Spatial Isotropy Constraint

CMB temperature anisotropy measurements (Planck 2018, A&A 641, A1) constrain spatial isotropy. Lorentz-violating parameterisations (Kostelecky and Mewes, 2002) place bounds at or below `10^{-23}` on certain anisotropy coefficients.

**Consequences for QNG:**

1. Any dimensional selection mechanism (Option A) must not predict a preferred spatial direction above this bound.
2. Any three-direction extension (Sub-option B2) must produce `g_11 = g_22 = g_33` to within observational tolerance.
3. Sub-option B1 (isotropy assumed by construction) is trivially consistent. Any future correction allowing the three components to differ must be bounded below the observational limit.

**The isotropy constraint is not a free parameter.** It is the tightest empirical constraint on the spatial sector and must be tracked in every extension.

---

## Section 5 — Resolution Decision

**QNG currently takes Option B + Sub-option B1.**

### What can be claimed

1. The temporal slot — its sign and structural dependence on the back-reaction sector — is derived within QNG, not merely inserted by hand.
2. The metric coefficients emerge from the coherence and back-reaction structure of the graph substrate.
3. The 4×4 proxy `g_sig^(4)(i)` satisfies `det < 0` and has the correct index structure by construction, given Assumptions D1 and D2.

### What cannot be claimed

1. QNG does not derive the number of spatial dimensions.
2. The GR recovery ladder is a proxy chain built on assumed 3+1 structure — no rung recovers 3+1D GR from first principles.
3. Isotropy is assumed, not derived.

### Revised scope statement

> QNG derives the sign structure of the Lorentzian metric and the scalar coefficients of an isotropic 3+1D metric proxy from the graph substrate dynamics. The dimensionality (3+1) and spatial isotropy are declared as external structural inputs (Assumptions D1 and D2). The full GR recovery program — including dimensional selection and isotropy emergence — remains an open research objective requiring an extension of the native update law and the development of a dimensional estimator analogous to the Myrheim-Meyer construction.

---

## Section 6 — Path Forward to Option A (Non-Binding)

**Step 1:** Construct a graph-theoretic analogue of the Myrheim-Meyer dimension estimator applied to the causal partial order induced by `T_sig(i)` on `G(t)`. Demonstrate `d_eff = 3` for the spatial sector under generic initial conditions.

**Step 2:** Introduce a 3-coloured edge structure. Derive per-direction coherence estimators and show convergence to a common value under `U` — producing isotropy as a theorem.

**Step 3:** Stability analysis — show 3+1 is a stable attractor, not merely a fixed point, under coarse-graining.

**Step 4:** If a path-integral formulation of QNG dynamics is constructed, study whether the sum over graph histories spontaneously produces 3+1 geometry (CDT-analogous Monte Carlo test).

Until these steps are completed, Option B with Assumptions D1 and D2 is the correct and honest description.

---

## Assumptions Registered

| Label         | Content                                                                                                              | Status              |
|---------------|----------------------------------------------------------------------------------------------------------------------|---------------------|
| Assumption D1 | `G(t)` carries three independent spatial directions and one temporal direction. Not derived; structural external input. | External assumption |
| Assumption D2 | Spatial isotropy: `g_11 = g_22 = g_33 = g_sp(i)` in the weak-field, low-anisotropy limit.                          | External assumption |

---

## Status of the Three Gaps

| Gap | Description | Status after this note |
|-----|-------------|------------------------|
| Gap 1 — Dimensional mismatch | 2×2 vs 4×4 | Addressed by minimal 4×4 extension under Assumptions D1 and D2. Not resolved from first principles. |
| Gap 2 — Spatial isotropy | Not addressed in DER-QNG-009 | Addressed by Assumption D2 (Sub-option B1). Empirical constraint documented. Not derived. |
| Gap 3 — Inherited proxy status | Ladder above DER-QNG-009 is a proxy chain | Unchanged. Revised scope statement in Section 5 is authoritative. |
