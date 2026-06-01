# Demo-Theory — Frequency & Light as the GR↔QM Bridge

Type: `note`
Status: `exploratory thread (open)`
Author: `C.D Gabriel`
Started: `2026-06-01`

---

## The question that opened this thread

> *"Between GR and QM, must yet another theory appear? I have not yet seen
> frequencies and light in the theory. Let's start from the basics but move
> toward frequencies and light — who knows what answers we find."*
> — Gabriel, 2026-06-01

This folder is a **fresh, slow rebuild** that takes that question seriously.
We do not start from the full QNG v8 machinery. We start from the single most
primitive fact of the substrate and follow it forward.

## The one thesis

**The missing object between General Relativity and Quantum Mechanics is
LIGHT, and the missing *language* is FREQUENCY.**

In QNG every node carries a phase `φ ∈ [-π, π]`. A phase that turns in time
*is* a frequency: `dφ/dt = ω`. So frequency is not derived in QNG — it is
nearly the most primitive thing there is. Each node is, at heart, an
**oscillator**. The substrate is a network of coupled oscillators.

From this single seed, three things should grow:

1. **Synchronization** → the coherence field `C_eff` is a Kuramoto order
   parameter (where amplitude/geometry comes from).
2. **Phase waves** → a dispersion relation `ω² = c²k² + m²`, a lightcone,
   and `c = √(stiffness / inertia)`.
3. **Light** → the *transverse* part of the edge field `θ_ij = φ_i − φ_j`,
   which needs **no bolted-on gauge field** and carries exactly 2 polarizations.

And light is exactly the bridge: it has **frequency** (the QM/phase side,
`E = ℏω`) yet carries **energy-momentum that gravitates** (the GR/`σ_g` side).
Static mass gravitates but has no frequency; pure phase rotation has frequency
but (if energyless) does not gravitate. **Light is the diagonal that loads
both ledgers at once.**

## Reading order

| File | What it builds |
|---|---|
| `00-the-oscillator.md` | A single node IS an oscillator. Frequency as the primitive. `E = stored frequency`. |
| `01-coupled-oscillators.md` | Two → many nodes. Beats, synchronization, Kuramoto. `C_eff = order parameter`. |
| `02-phase-waves-and-lightcone.md` | The chain → dispersion `ω²=c²k²+m²`. `c=√(β/zμ)`. Lorentz = impedance matching. |
| `03-light-without-a-gauge-field.md` | The honest photon: transverse part of `θ_ij = φ_i−φ_j`. 2 polarizations, no U(1). |
| `04-light-as-the-bridge.md` | Why light is *the* GR↔QM object. The two-ledger argument. |
| `05-mass-as-resonance.md` | `m = ℏω₀/c²`? Cavity modes, the `1/R`-vs-`R^a` tension. |
| `06-experiments.md` | E1–E6: concrete simulatable probes on the existing lattice. |
| `07-edges-carry-the-forces.md` | **Synthesis (E5+E7):** matter/phase = nodes; forces = edges. |
| `SESSION-SUMMARY-2026-06-01.md` | **All of E1–E8 run.** One-page scoreboard + the central node/edge result. |

**Experiment scoreboard (all run 2026-06-01):** E1 PASS · E2 lightcone round
(η_LV≈6% finite-k) · E3 ~box modes · **E5 photon-from-φ FALSIFIED** · E6 fringes
PASS · **E7 photon = edge vector** (Route B falsified, edge field forced) · **E8
graviton = rank-2 edge** (2 TT pols, kinematic) · **E4 mass = volume charge**
(1/R resonance disfavored). See `SESSION-SUMMARY-2026-06-01.md`.

### Phases 1–4 — integrating the result into the original theory

After the demo proved *forces live on edges*, we propagated it into the main
theory and pushed further:

| Phase | What | Result |
|---|---|---|
| **1 Implement** | `DER-QNG-101` Hodge no-go in `04_qng_pure/`; THEORY_STATE Gap-12 update | node scalars can't carry transverse → carrier **forced** edge-valued |
| **2 Test** | v12's *actual* lattice gauge (`A_ij`/`F_p`) | **V12_PHOTON_CONFIRMED** (2 transverse + frozen longitudinal) |
| **3 Attack edges** | SU(2) quaternion links + Wilson MC (+ tesla-mind & professor consults) | **SU2_EDGES_CONFINE** — gauge-invariant, area-law confinement (4.03) |
| **4 Re-attack particles** | 4a custodial, 4b v13 doublet, 4c chirality | **edges=forces / nodes=mass**; rings = **Skyrme-type baryons**; quarks/leptons need **v13+v14** |

Findings: `PHASE3-edges-findings.md`, `PHASE4-particles-reattack.md`.
Layered map: v8(mass) → v11(graviton) → v12(photon) → **v13**(SU2/SU3 edge +
complex node multiplet; Skyrmion baryons) → **v14**(chiral fermions).

## Honesty contract (read before claiming anything)

This is an **exploration**, and physical intuition here sometimes outruns what
the substrate can justify. Two flags carried from the start:

- **"Frequency is the *sole* primitive" is too strong.** The honest version is
  *"phase organizes the amplitudes"* — `σ` follows `φ` — which needs an
  unproven adiabatic/slow-manifold theorem. Open program, not a result.
- **The impedance/Lorentz framing is a rigorous *analogy*, not a derivation**
  of *why* the impedance-matching condition `c_g = c_m = c_φ` holds. That is
  still tied to the open cosmological-α problem (Gap 5).

Two experiments are make-or-break and gate the two biggest claims:

- **E5 + E7 gated "QNG has a photon." [BOTH RAN 2026-06-01.]** Route A (scalar
  `φ`, E5) and Route B (`φ–χ` circulation, E7) are **both FALSIFIED**: no node
  scalars can source a transverse mode (`curl(∇·)=0`, machine precision). A
  **fundamental edge-vector field** gives the photon exactly (E7b: 2 transverse
  pols at `c_φ`, longitudinal frozen). **Verdict: light is necessarily a
  link/edge gauge field — v12's `A_ij` is forced, not a bolt-on.** See
  `E5-RESULT-no-go.md`, `E7-RESULT-edge-photon.md`, `07-edges-carry-the-forces.md`.
  The photon is still a *primitive* edge field (not derived from node dynamics),
  but it is now the unique minimal structure, not arbitrary.
- **E4 gates "mass is a resonance."** Do NOT write *"mass = ℏω₀/c²"* as
  established until the ring-radius scan distinguishes density from frequency.

## Relationship to the rest of the repo

- `theory-v2/` is the crystallized, audited core (c, G, ℏ derived; 6/6 Einstein).
- The main `QNG-Theory Release-01/` tree is the active lab.
- **`demo-theory/` is a parallel pedagogical/exploratory track** — it may reach
  conclusions that later feed back into the main theory, but nothing here is
  "locked" until it passes the audit gates above and is promoted.

Substrate facts reused (already established elsewhere, not re-derived here):
`ω² = c_φ²k² + m²` with `c_φ² = β_φ/(z·μ_φ)`; `E = ℏω`; the v12 axiomatic photon
and the **falsified** Tesla-U(1)-on-χ interpretation (`DER-QNG-044`).
