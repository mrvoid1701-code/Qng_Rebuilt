# Phase 3 — What hides in the edges

Type: `note` / `evidence`
Status: `RUN COMPLETE 2026-06-01`
Author: `C.D Gabriel`
Inputs: tesla-mind + quantum-node-theory-professor consultations; tests
`t_phase2_v12_lattice_photon.py`, `t_phase3_su2_edges.py`
Depends on: `DER-QNG-101` (Hodge no-go), `DER-QNG-076` (v12 U(1))

---

## The mandate

Gabriel: *"attack the edges with everything we can, see what hides in them —
maybe we find the rest of the gauge forces."* The Hodge no-go (DER-QNG-101)
told us forces live on edges. The U(1) photon was the first inhabitant. What
else is in there?

## The edge zoo (classified by what an edge can carry)

| Edge object | Symmetry | Physical identity | QNG status |
|---|---|---|---|
| node scalar `φ` | — (exact 1-form) | mass / sound / Goldstone | nodes (longitudinal only) |
| vector `A_ij` (U(1) phase) | antisym 1-form | **photon** (spin-1) | **DONE** (v12, Phase-2 confirmed) |
| matrix `U_ij` (SU(2)/SU(3)) | non-abelian holonomy | **W/Z, gluons + confinement** | **edges CAN host** (Phase-3) |
| symmetric rank-2 | TT | **graviton** (spin-2) | edge rank-2 (E8 kinematic) |
| antisymmetric rank-2 `B_[ij]` | 2-form | Kalb-Ramond / **torsion** (couples to spin) | unexplored slot |

## The key physical idea (both agents converged)

**An edge is a transporter.** The gauge-invariant object in v12 is `exp(i e A_ij)`
— a U(1) group element on the edge, and the matter coupling
`cos(φ_i − φ_j − e A_ij)` literally means *"compare node phases after
parallel-transport along the edge."*

> A transporter can carry a single phase (U(1) → light) **or a multiplet, and
> then it must be a matrix** (SU(N) → nuclear forces). The non-commutativity of
> matrix links is automatically the gluon self-interaction → asymptotic freedom
> and **confinement**, present the moment an edge carries a matrix instead of a
> number.

## What we tested and found

### Phase-2 — the photon in the *real* v12 structure (`demo-phase2-v12-photon-v1`)

Not the idealized spectral operator of E7, but v12's actual lattice gauge
(`A_a` links, `F_p` plaquettes, `DER-QNG-076`): **2 transverse polarizations
degenerate, longitudinal frozen (Gauss).** `V12_PHOTON_CONFIRMED`. The edge
photon is real in the original theory's formulation.

### Phase-3 — SU(2) on the edges (`demo-phase3-su2-edges-v1`)

SU(2) group elements (unit quaternions) on every edge, Wilson action, vectorized
Metropolis:

| Gate | Result |
|---|---|
| **G1 gauge invariance** | `|ΔP|` under random local SU(2) = **0.000** (exact) → genuine gauge theory |
| **G2 MC correctness** | `⟨P⟩` = 0.2105 (β=1, pred β/4=0.25) ; 0.658 (β=2.6, pred 0.65) → MC correct |
| **G3 confinement** | area-law ratio `ln W(2,2)/ln W(1,1)` = **4.03** at strong coupling (= area ratio 4, textbook area law), dropping to 3.03 at weak coupling |

**`SU2_EDGES_CONFINE`**: QNG edges host a genuine, gauge-invariant SU(2) theory
that **confines** (area law, string tension `σ ≈ 1.56` lattice units at β=1).
The edge sector extends naturally from the U(1) photon to a non-abelian
**confining** force — the qualitative signature of the strong interaction.

## The honest verdict (where the two agents agreed, and disagreed)

**Agreement — the pure-gauge edge sector is solid and forced-type.** Both the
visionary (tesla-mind) and rigorous (professor) analyses agree: putting SU(2)/
SU(3) *gauge fields* on edges is a clean, well-defined extension — the same
pattern as v12, now confirmed to confine. The free spectrum is `N²−1` gauge
bosons × 2 transverse polarizations (3 for SU(2), 8 gluons for SU(3)).

**Disagreement, resolved — the matter sector is a hard wall.** tesla-mind's
flagship idea was that `(σ_g, σ_m)` is the SU(2) isospin doublet (with `k_gm`
the symmetry breaking). The professor **refuted this on rigorous group theory**:
SU(2) acts on `ℂ²`, so a doublet needs **two complex** fields (4 real dof); two
**real** scalars cannot form an SU(2) doublet — it is numerology. tesla-mind
flagged the same gap himself (the elegant `(ψ_g, ψ_m)` doublet needs a second
phase `φ_g` that does not exist). **Verdict: non-abelian *matter* requires
genuinely new node ontology (v13) — complex multiplets, and for chiral weak
interactions, Dirac fermions. This is the same Class-II obstruction as
DER-QNG-091.**

So the precise statement:

> **QNG edges are naturally extensible to the full non-abelian gauge sector
> (and they confine). QNG nodes are NOT naturally extensible to the matter
> multiplets those gauge fields must act on. These two facts are independent.**

## What this means for "finding the rest of the gauge"

- **Light (U(1))**: found, forced, confirmed (Phase-2). ✓
- **Strong/weak gauge bosons (SU(2)/SU(3))**: the edges *host* them and
  *confine* — the carriers and the confinement phenomenology are in reach
  (Phase-3). The **gauge group choice** is not forced (Gap 17 generalized).
- **Their matter (quarks/leptons)**: blocked by the node-ontology wall. Needs
  v13 (complex multiplets + Dirac/chiral structure). The professor flags
  chirality as the deepest obstruction — no scalar theory is parity-violating.
- **Higgs**: the χ-VEV (dark-energy field) **cannot** be the SM Higgs — χ is a
  real singlet (`Tr T^a = 0`), so it can't break SU(2). A genuine doublet Higgs
  is new ontology too.

## Honest caveats

- Phase-3 confinement is the **pure-gauge** sector; no matter coupling tested.
- `(σ_g, σ_m)` isospin doublet is **refuted** (real fields); do not propagate it.
- SU(3) has **no node triplet** in the current substrate — weakest part; not
  pursued until SU(2)-with-matter exists.
- Lattice L=6, modest statistics — the area-law ratio (4.03 vs ideal 4) is
  clean but should be reconfirmed larger before any publication claim.

## Next probes (queued, from the consultations)

- **P2** node-doublet gauge invariance (needs a v13 complex doublet first).
- **P3-full** string tension `σ` vs the CPU-050 inter-ring potential — does color
  confinement connect to the ring–ring (nuclear-residual) force? (tesla-mind P5)
- **P4** custodial-symmetry audit: is there *any* `(σ_g, σ_m)` rotation symmetry
  when `k_gm=0`? (even if not full SU(2), worth knowing — tesla-mind P4)
- **torsion slot**: antisymmetric edge rank-2 coupling to ring spin.

## Bottom line for the theory

The edge sector is **richer than the photon** and the demo confirms it hosts a
**confining non-abelian gauge theory**. The forces of nature plausibly all live
on QNG edges. The bottleneck for a full Standard Model is **not** the forces —
it is the **matter** (chiral fermion multiplets at nodes), which is genuinely
new ontology (v13). This sharpens exactly where the next real work is.
