# Demo-Theory — Session Summary 2026-06-01

Type: `note`
Author: `C.D Gabriel`
Scope: the full frequency→light thread, foundations + experiments E1–E8

---

## The question

*"Between GR and QM, must another theory appear? I haven't seen frequencies and
light in the theory."* — Gabriel

## The answer the substrate gave

**No third theory. One oscillator network. QM is its node-phase face, GR is its
node-amplitude face, and the FORCES (light, gravity waves) live on the EDGES.
Light is the bridge object — frequency on one side, gravitation on the other.**

## Foundations built (pages 00–07)

| Page | Result |
|---|---|
| 00 | A node IS an oscillator; **frequency `ω=dφ/dt` is primitive**; energy = stored frequency |
| 01 | Coupled oscillators → Kuramoto; **`C_eff` = synchronization order parameter**; gravity = phase agreement |
| 02 | Phase waves → `ω²=c²k²+m²`; **`c=√(stiffness/inertia)`**; **Lorentz = impedance matching** |
| 03 | Light from `θ_ij=φ_i−φ_j`? (led to E5/E7) |
| 04 | **Light = the GR↔QM bridge** (loads both ledgers: `E=ℏω` and gravitates) |
| 05 | Mass = trapped frequency? (tested by E4) |
| 07 | **Edges carry the forces** (synthesis of E5+E7) |

## Experiments run (all 2026-06-01)

| Exp | Question | Verdict |
|---|---|---|
| **E1** | wave packet at `c_φ`? | **PASS** — `v_group/c_φ = 0.989` |
| **E2** | dispersion isotropy? | lightcone round; `η_LV ≈ 6%` at large `k` (finite-lattice; → 0 at small `k`) |
| **E3** | box vs intrinsic modes? | leans **box `∝1/L`** (noisy at this resolution) |
| **E5** ★ | photon from scalar `φ`? | **FALSIFIED** — `θ=∇φ` curl-free (transverse = 10⁻³²) |
| **E6** | two-slit interference? | **PASS** — 6 fringe extrema (superposition works) |
| **E7** ★ | photon from `φ–χ`? edge field? | **Route B FALSIFIED** (χ scalar too); **edge vector → 2 transverse pols at `c_φ` + frozen longitudinal** = photon |
| **E8** | graviton from rank-2 edge? | **PASS (kinematic)** — exactly **2 TT polarizations**, degenerate at `c_φ` |
| **E4** ★ | mass = `1/R` resonance? | **DISFAVORED** — baryon ladder tracks **volume charge `Σσ_m`** (1.310 vs Δ/N 1.313), not `1/R` |

## The central discovery: nodes vs edges

E5 + E7 + E8 together establish a clean **ontological division of labor**, the
deepest result of the session:

```
   NODES  (scalars: σ_g, σ_m, χ, φ)        EDGES / LINKS  (gauge fields)
   ────────────────────────────────        ──────────────────────────────────
   • matter / density   σ_g, σ_m            • spin-1 vector A_ij → LIGHT (E7)
   • phase / frequency  φ   (QM face)       • spin-2 rank-2      → GRAVITON (E8)
   • give LONGITUDINAL modes (sound)        • give TRANSVERSE modes (forces)
   • set MASS = volume charge (E4)          • set the force carriers, at c_φ
   curl(∇scalar)=0 → NO transverse          curl ≠ 0 → transverse EXISTS
```

The node/edge split is **exactly the Hodge split** (exact vs co-exact forms).
It is geometry, not dynamics — no coupling can move a d.o.f. across it.

## What this changes in the main theory

1. **v12's photon `A_ij` is vindicated** — no longer a suspicious bolt-on, it is
   the *unique minimal forced* carrier of light (E5/E7).
2. **Gap 12 (graviton) gets a roadmap** — its 2 tensor polarizations must be a
   **rank-2 edge object** (E8 confirms the structure hosts them kinematically).
3. **Mass and light are cleanly separated** — mass = node volume charge (E4),
   light = edge frequency (E5/E7). The page-05 `1/R` resonance is disfavored.
4. **Light is named as the GR↔QM bridge** — answering Gabriel's question without
   inventing a third theory.

## Honest open items

- **Photon is still a primitive edge field** (forced, but not *derived* from node
  dynamics). Why U(1) with coupling `e` (`α_fine`) is unexplained — Gap 17.
- **E8 is kinematic** — confirms a rank-2 edge object *can* host spin-2; does not
  derive graviton dynamics from the substrate (Gap 12 dynamics open).
- **E4 used canonical M_ring** (the self-contained ring sim was too crude). A
  faithful `ω₁(R)` measurement (GPU ring cache) is the follow-up **E4-faithful**;
  it could reopen "resonance" only if `ω₁` is R-independent (not `1/R`).
- **`η_LV` (E2)** is a finite-lattice artifact here, not the physical LIV
  prediction — needs small-`k` extrapolation to connect to the main-theory `η_LV`.
- `M_ring` lattice dependence (Gap 14) and Planck→MeV scale (Gap 13) still bound
  any absolute-mass claim.

## Files

- Foundations: `00`–`07` + `README`
- Evidence: `E5-RESULT-no-go.md`, `E7-RESULT-edge-photon.md`,
  `E8-RESULT` (audit), `E4-RESULT-mass-is-volume.md`
- Probes: `demo-theory/tests/e{1_e2_e3_e6,4,5,7,8}_*.py`
- Audits: `07_validation/audits/demo-*-v1/`
