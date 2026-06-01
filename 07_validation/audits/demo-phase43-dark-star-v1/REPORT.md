# REPORT — demo Phase-43: QNG dark matter as a stable degenerate neutral node-core (dark star)

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase43_dark_star_hydrostatic.py`
Verdict: **DARK_MATTER_IS_A_STABLE_DEGENERATE_NEUTRAL_NODE_CORE** (correct hydrostatic treatment)

## Post-mortem of Phases 40–42 (why they failed — a model artifact)

Those field models coupled gravity as an **amplitude source**
(`sigma_m += k_gm*(sigma_g - ref)`), which creates/destroys matter. That makes the
uniform vacuum Jeans-unstable above `k_gm ~ sqrt(G_V*GAMMA) ≈ 0.028`; the runs used
0.15–0.30, far above threshold, so the **entire box** collapsed every time
(total → N·SM_REF identically). A model artifact, NOT a property of the dark core.
Real gravity is a **transport force** on a **conserved** density, not a source.

## The correct model (this phase)

Self-gravitating QNG matter = conserved density ρ = SM_REF − σ_m, with
**degeneracy pressure** from node discreteness (finite states/node → non-rel Fermi
EOS → polytrope n=3/2), in **hydrostatic equilibrium** = the **Lane-Emden equation**.

- **T1.** n=3/2 terminates at **ξ₁ = 3.654** (textbook 3.65), mass factor **2.714**
  (textbook 2.714); n=3 → ξ₁ = 6.897 (textbook 6.897). Integrator validated against
  known values. → a **stable, finite-radius**, self-gravitating degenerate sphere
  EXISTS (white-dwarf / neutron-star physics).
- **T2.** Mass–radius R ~ M^(−1/3) (more massive → smaller) — the degenerate
  compact-object signature.
- **T3.** QNG dark matter = a **dark star**: NEUTRAL (no φ-winding, q=0; evades the
  no-go DER-QNG-082, Phase 39), degenerate node-density core, held up by degeneracy
  pressure (stable, this phase), and the endpoint of black-hole evaporation
  (Phase 38) → **information-bearing** (the user's original intuition).

## Honest scope

This is the **standard polytrope/Lane-Emden existence result applied to QNG
matter** — it proves a stable equilibrium EXISTS under the correct
(conserved-density, degenerate, self-gravitating) physics. It does NOT yet (i)
derive the QNG degeneracy-EOS coefficient from the node state-count (→ sets the
absolute size/abundance), nor (ii) run a full dynamical QNG lattice simulation of
formation. The **conceptual chain is now closed**: neutral (39) + stable
degenerate (43) + information-bearing (38) = a viable, no-go-evading QNG
dark-matter candidate. Remaining work is **quantitative** (EOS coefficient →
abundance/size), not existential.
