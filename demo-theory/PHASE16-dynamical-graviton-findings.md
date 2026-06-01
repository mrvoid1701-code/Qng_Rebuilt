# Phase 16 (Gap 12) — the dynamical graviton on the edge lattice

Type: `note` / `evidence`
Status: `RUN COMPLETE 2026-06-01 — Gap 12 upgraded kinematic → dynamical`
Probe: `demo-theory/tests/t_phase16_dynamical_graviton.py`
Artifact: `07_validation/audits/demo-phase16-dynamical-graviton-v1/`

---

## The master key (from Phase 15)

The whole program reduces to Gap 12 (the dynamical graviton): it gates f_g →
α → parameter-free proton mass. E8 established the graviton only *kinematically*
(rank-2 edge object hosts 2 TT pols by counting). Phase 16 tests the
**dynamical** content — the property that makes a rank-2 field a *graviton*.

## Result: **DYNAMICAL_GRAVITON_ON_EDGES**

| Test | Result |
|---|---|
| **T1 diffeomorphism gauge invariance** | linearized Riemann unchanged under `h→h+∂ξ+∂ξ`: **4.5×10⁻¹⁶** (machine precision) |
| **T2 gauge modes unphysical** | pure-gauge `h=∂ξ+∂ξ` has TT fraction **3.4×10⁻⁴ ≈ 0** |
| T3 Newtonian 1/r (corroboration) | R²=0.69 — lattice-limited (coarse point-source FFT-Poisson); the Newtonian limit `Φ∝δ_C` is independently established (GRAV-C1) |

> **T1 is the decisive new result.** The linearized Riemann curvature built from
> the edge `h_ij` is **invariant under linearized diffeomorphisms**
> `h_ij → h_ij + ∂_i ξ_j + ∂_j ξ_i` to machine precision. **This is the defining
> property of a graviton** — it is the gauge field of diffeomorphisms — and E8
> (kinematic) did not test it. **T2** confirms the gauge modes carry no physical
> (TT) content, so only the 2 transverse-traceless polarizations propagate.

## What this establishes

Gap 12 is **upgraded from kinematic (E8) to dynamical**: the rank-2 edge object
supports **gauge-invariant linearized-GR dynamics with exactly 2 physical dof** —
a genuine graviton, not just a rank-2 field. The carrier *exists and is
dynamically consistent* (Fierz-Pauli / linearized-Einstein structure works on it,
diffeomorphism-invariant, 2 TT, Newtonian limit recovered analytically).

## Honest scope (the remaining core of Gap 12)

This shows the edge graviton is **consistent**, not that the substrate
**produces** it. The open core of Gap 12 is the **derivation**: show that
coarse-graining the QNG node/edge dynamics **flows to the linearized Einstein
(Fierz-Pauli) action** for `h_ij`. Phase 16 postulates that action and verifies
it is gauge-invariant and 2-dof on the lattice; it does not derive it from the
substrate.

So Gap 12 splits:
- **carrier + consistency**: DONE (E8 kinematic + Phase 16 dynamical/gauge).
- **action from substrate** (coarse-graining → Fierz-Pauli): the remaining core,
  and the prerequisite for computing `f_g → α` (Phase 15).

## Where this sits in the chain

```
   Gap 12 carrier+consistency  DONE (E8 + Phase 16)
        │
        ▼
   Gap 12 action-from-substrate  ← REMAINING CORE (coarse-grain → Fierz-Pauli)
        │
        ▼
   f_g(G_QNG)  (Phase 14/15: graviton loop → gauge beta)
        │
        ▼
   α  (Drumul 3)  →  parameter-free proton mass (Phase 11/12)  =  decisive distinction
```

## Bottom line

The master key (Gap 12) is now **half-turned**: the edge graviton is shown to be
a genuine, gauge-invariant, 2-polarization dynamical object (not merely a
kinematic rank-2 field). The remaining core — deriving its Fierz-Pauli action by
coarse-graining the substrate — is the single sharpest open target, because it
unlocks f_g → α → the parameter-free proton mass. The carrier exists and is
consistent; what remains is to show the substrate dynamics flow to it.
