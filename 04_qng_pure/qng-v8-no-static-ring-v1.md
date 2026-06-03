# QNG v8: 3D cubic substrate admits no static ring equilibrium

Type: `derivation`
ID: `DER-QNG-047`
Status: `locked for v8 in 3D` (GPU-024d v2 + GPU-028 verdict: NO_RESCUE across all natural V_couple families)
Author: `C.D Gabriel`
Date: `2026-04-21`

---

## Inputs

- [qng-v8-canonical-extension-v1.md](qng-v8-canonical-extension-v1.md) — DER-QNG-042 (v8 canonical)
- [qng-particle-mass-identification-v1.md](qng-particle-mass-identification-v1.md) — DER-QNG-038 (mass identification)
- [qng-hamiltonian-v7-two-field-v1.md](qng-hamiltonian-v7-two-field-v1.md) — DER-QNG-036 (v7 Hamiltonian)
- [qng-two-field-substrate-v1.md](qng-two-field-substrate-v1.md) — DER-QNG-033 (v7 two-field substrate)

---

## Objective

Document a structural finding that emerged from the GPU-024 cascade
(ring stability → channel-F isolation → gradient-flow relaxation): the
cached vortex ring `ring_L28_R4_P1_300_P2_1000` is NOT a stationary
point of the v8 Hamiltonian on the 3D z=6 cubic lattice in any regime
we have been able to probe, and under gradient flow it monotonically
decays toward the sine-Gordon vacuum `(sigma_m = sigma_m_ref, phi = 0)`.

This is NOT a statement that v8 is inconsistent. It is a statement that
the soliton ontology assumed in v5 / v7 (Channel F vortex ring as a
static minimum of the potential) is not inherited by v8. Under v8, any
object built as a "static" v7 ring is a dynamic pattern, not a rest-
frame soliton.

The finding promotes a previously-implicit question — is 3+1D
structurally required by QNG? — to an operational gap (Gap 10,
dimension selection).

---

## Evidence trail

| probe | script | verdict | summary |
|---|---|---|---|
| GPU-022 | qng_v8_bending_sigma_m_scan_probe | saturation | α_meas non-monotonic in pre-scale s |
| GPU-023 | qng_v8_bending_wide_detector_probe | candidate #1 ruled out | widening detector reduced α 20% uniformly |
| GPU-024 | qng_v8_ring_stability_probe | metastability | M_ring drifts 500-1000% under Phase-2 for ALL s |
| GPU-024b | qng_v8_ring_stability_diagnostic | V_couple + chi_decay ruled out | A=B byte-identical (k_gm=0), C unstable |
| GPU-024c | qng_v8_ring_stability_channelf | Channel F ruled out | D (chF off) and E (all off) still chaotic, 470% drift |
| GPU-024d v1 | qng_v8_static_ring_search | H_INCONCLUSIVE | M_ring 176.85 → 19.09 in 5000 iter, still dropping |
| GPU-024d v2 | qng_v8_static_ring_search_v2 | **H_NO_RING_IN_ANY_REGIME** | A (V_couple on): 177→0.05 at 18k iter. B (V_couple off): 177→0.10 at 30k iter. BOTH dissolve. |
| GPU-028 | qng_v8_alt_v_couple_search | **NO_RESCUE** | Four V_couple variants — (a) φ-mass quadratic: 177→0.046; (b) doubled-pitch 2φ: 177→0.016 (fastest); (c) quartic (1-cosφ)²: 177→0.070; (d) V=0 control: 177→0.098. ALL DISSOLVED. |

Key quantitative anchors:

- Force residual on cached ring (v8 channel_f=False):
  `||F_sm||_RMS = 8.38e-03`, `||F_phi||_RMS = 5.29e-03`
- Vacuum `(sigma_m_ref, phi=0)` has `||F|| = 0` exactly.
- Gradient flow dt_relax=0.05: M_ring trajectory monotonically decreasing
  after t=200; no plateau, no equilibrium reached before dissolution.

---

## Mechanism

The v8 potential contains three interacting pieces on a given node:

    E_v8 = E_v7 + V_couple
    V_couple = (g/2) * (sigma_m_ref - sigma_m)^2 * (1 - cos phi)

`V_couple` is a sine-Gordon-type coupling. It has two crucial properties:

1. **Minimum at phi=0 for any deficit**: (1 - cos phi) ≥ 0 with equality
   iff phi = 0 (mod 2π). Wherever a mass deficit exists
   (sigma_m < sigma_m_ref), V_couple pushes phi back toward 0.
2. **Explicit U(1) → Z breaking**: V_couple only sees cos phi, so the
   continuous phase symmetry of E_v7 is reduced to integer shifts
   phi → phi + 2π. This is the sine-Gordon Z vacuum structure
   documented in `project_cpu080_winding_destroyed`.

Channel F (the v5 mechanism that originally stabilized the vortex ring)
pulls sigma down in regions of phi disorder. But disorder vanishes as
phi collapses to the Z vacuum, so Channel F provides no restoring force
once V_couple begins to unwind the phi texture.

Empirically (GPU-024d v1): from the cached state, F_sm ≈ 8e-3 pushes
sigma_m UP toward sigma_m_ref (reducing the deficit), and F_phi ≈ 5e-3
pulls phi toward 0. The two effects reinforce each other: smaller
deficit → weaker V_couple gradient on phi → phi relaxes → less
disorder → Channel F contribution decays → sigma_m fully relaxes.

The cached ring therefore sits on the **flank** of the basin whose
bottom is the sine-Gordon vacuum. No barrier, no basin, no static
ring.

---

## What "cached ring" actually is

The cached ring was produced by v7 three-phase gradient flow:

    Phase 1 (300 lu): no Channel F, no K_GM → phi vortex forms
    Phase 2 (1000 lu): Channel F active, CHI_DECAY=0.020 → sigma_m ring forms

This is a v7 equilibrium (Channel F balances sigma_m diffusion in the
toroidal core). It is NOT a v8 equilibrium because:

- v7 has no V_couple — the sine-Gordon breaking is absent.
- v7 phi is a gradient-flow Goldstone mode; the 2π winding is
  metastable under diffusion alone.
- Adding V_couple in v8 creates an explicit potential for phi that was
  not present during Phase 2 of ring formation.

The cached ring is the GROUND STATE OF A DIFFERENT HAMILTONIAN. Using
it as "the" ring in v8 is a methodological artifact.

This is why CPU-080 (winding diagnostic) found |W|_init = 1 but
|W|_cached = 0 — the Phase-2 gradient flow already started dissolving
the winding, but the cache was captured before the dissolution
completed.

---

## Consequences

### Immediate (verified)

- **GPU-021/022/023 α_meas measurements are time-averaged over a
  chaotic M_ring trajectory.** The saturation at s=1.4 (GPU-022) may
  be a property of the chaos, not of the underlying EOM.
- **DER-QNG-046 §5 tensorial cancellation** remains retracted; the
  basis state on which the cancellation was defined does not exist.
- **DER-QNG-038 baryon ladder** retains R-scaling evidence from
  CPU-074/075, but the interpretation of M_ring as a conserved
  topological charge of an isolated soliton is not supported by v8 —
  it is a Noether charge of a dynamic pattern.

### Structural (open)

- v8 on 3D cubic may have no static particle-like soliton at all. The
  v5 / v7 vortex-ring ontology would then be a v7 artifact that v8
  inherits only as a dynamic excitation.
- Alternatively, the static ring may require a V_couple different from
  the canonical sine-Gordon form of DER-QNG-042. Candidates: double
  Yukawa, gauge-invariant (requires restoring U(1)), or vanishing
  V_couple plus different phi mass mechanism.
- Alternatively, 3+1D may be structurally hostile to ring solitons
  altogether; higher-dimensional v8 (codim ≥ 3) may be required. See
  Gap 10.

### Theory consolidation (done as part of this doc)

- The "ring" entity is split:
  - **v7 ring** — gradient-flow Channel F equilibrium; basis for v7
    mass identification (DER-QNG-038). Exists.
  - **v8 ring** — hypothesized static V_couple + Channel F equilibrium.
    **Does not exist in accessible regimes** based on GPU-024 cascade.
- All phenomenology derived from loading the v7 cache and integrating
  under v8 is DYNAMIC ring phenomenology, not static soliton
  phenomenology. This applies retroactively to GPU-020/021/022/023
  bending analyses.

---

## Falsification path — resolved

GPU-024d v2 decided between two hypotheses:

- **H_V_COUPLE_IS_CULPRIT**: with g=0 (V_couple off), cached ring
  relaxes to a nontrivial stationary state. *Ruled out.*
- **H_NO_RING_IN_ANY_REGIME**: with g=0 the ring still dissolves.
  **Confirmed.**

Run B (V_couple off) took 30000 iterations to reach M_ring = 0.10
(vs. 18000 for Run A with V_couple on). V_couple accelerates the
dissolution but is not required for it. The v7 ring has no v8
analogue in 3D on the cubic substrate regardless of coupling choice.

### Extension via GPU-028 — no natural V_couple form rescues the ring

GPU-028 closed the remaining escape hatch: "maybe a *different* V_couple
form admits a static ring." Four natural alternatives were tested on
the same cached ring under identical protocol (30000 iter gradient
flow, Channel F off, dt=0.05, g=0.22):

- (a) **φ-mass quadratic** `V = (g/2)·Δ²·φ²/2` — preserves continuous
  U(1) as a mass-type term (no topological obstruction from potential).
  M_final = 0.046.
- (b) **Doubled-pitch** `V = (g/2)·Δ²·(1-cos 2φ)` — Z₂ residual symmetry.
  M_final = 0.016 (fastest).
- (c) **Quartic** `V = (g/4)·Δ²·(1-cos φ)²` — quadratic in deficit,
  weakest slope at φ=0. M_final = 0.070.
- (d) **V=0 control** — baseline. M_final = 0.098.

ALL dissolved. Dissolution-speed ranking b < a < c ≈ d tracks the
LOCAL slope of V at φ=0: steeper slope → faster dissolution. No form
provides a stabilizing contribution; every φ-deficit coupling adds
dissipation on the ring without basin structure.

Three inferences:

1. **V_couple is not the primary culprit** — (d) V=0 dissolves as fast
   as the canonical sine-Gordon equivalents.
2. **No local φ-deficit coupling stabilizes** — the three natural
   symmetry alternatives cover (continuous U(1) mass / Z₂ residual /
   weaker slope); none rescue.
3. **The obstruction is structural** to v8 gradient flow with Channel F
   off. The cached ring is a v7 Channel-F equilibrium; once Channel F
   is off for measurement purity, the kinetic+potential v8 sector alone
   does not support a static ring under any local V_couple.

Escape routes that remain untested (not accessible from this probe):

- Non-local V_couple (gauge fields, derivative couplings `∂φ·∂σ_m`).
- Higher-dimensional substrate where topology admits codim-2 defects
  (4D torus Class A in DER-QNG-048; predicted to dissolve for the same
  local reason, see GPU-027 note).
- Dynamic-orbit ontology (Scenario A) — rings as bounded invariant
  orbits of v8, NOT equilibria. This is the load-bearing path forward.

Consequence: the ring-as-static-soliton ontology is abandoned for v8
in 3D. v7 remains the substrate in which DER-QNG-038 (baryon mass
ladder) was derived; that derivation's R-scaling results stand as v7
conservation-law statements, but the "rest mass" interpretation does
not survive the transfer to v8.

### Additional falsification (scope Gap 10)

- QNG-GPU-026 (4D KG dispersion, pre-registered): tests whether the
  substrate is dimension-robust at the wave level. If c_g^2 = beta_g/z
  scales correctly from 3D (z=6) to 4D (z=8), dimension-agnosticism is
  confirmed at least at the linear level. Does not yet test ring
  stability in 4D.
- 4D ring stability test (not yet pre-registered): requires defining
  "ring" in 4D (codim 3 curve vs codim 2 membrane) and has significant
  theoretical prereqs.

---

## Upstream dependencies

- `DER-QNG-033` — v7 two-field substrate (defines sigma_g, sigma_m, chi, phi)
- `DER-QNG-036` — H_v7 Hamiltonian (gradient flow of E_v7)
- `DER-QNG-038` — v7 ring mass identification + baryon ladder
- `DER-QNG-042` — v8 canonical extension (defines V_couple as sine-Gordon)
- `DER-QNG-044` — Einstein correspondence suite (Tesla gauge falsified)
- `CPU-080` — winding diagnostic (|W| destroyed by Phase-2)
- `CPU-074/075` — M_ring conservation as topological (Noether) charge

## Downstream

- Retroactively contextualizes `GPU-020`, `GPU-021`, `GPU-022`, `GPU-023`
  as dynamic-pattern phenomenology, not static-soliton phenomenology.
- Promotes `Gap 10` (dimension selection) from speculation to an open
  structural gap with an empirical first probe (QNG-GPU-026).

---

## Status

**Locked for v8 in 3D (cubic z=6).** Based on GPU-024d v2 + GPU-028:

- GPU-024d v2 A: V_couple canonical on, Ch F off, N=30000 → DISSOLVED at iter 18000
  (M=0.05, ||F_sm||=2.2e-08)
- GPU-024d v2 B: V_couple off, Ch F off, N=30000 → DISSOLVED at iter 30000
  (M=0.10, ||F_sm||=2.2e-08)
- GPU-028 (a) φ-mass: M=0.046 at iter 18000
- GPU-028 (b) doubled-pitch: M=0.016 at iter 12000
- GPU-028 (c) quartic: M=0.070 at iter ≥30000
- GPU-028 (d) V=0 control: M=0.098 at iter ≥30000 (confirms GPU-024d v2 B)
- All converged to `(sigma_m=sigma_m_ref, phi=0)` vacuum.

The derivation does NOT claim:

- No v8 ring solution in higher dimensions (Gap 10 remains partly
  open; DER-QNG-048 predicts the same obstruction in 4D Class A).
- No non-local or derivative-coupled V_couple admits a ring (not
  tested; these are the only remaining local-form escape routes).
- Rings are absent from v8 dynamics as orbits (they likely exist as
  bounded chaotic/quasi-periodic trajectories; this is distinct from
  static equilibrium, and is the Scenario (A) path forward).
