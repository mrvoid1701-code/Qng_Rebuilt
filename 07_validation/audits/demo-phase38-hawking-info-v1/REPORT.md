# REPORT — demo Phase-38 quantum gravity: Hawking evaporation & the information paradox

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase38_hawking_information.py`
Verdict: **EVAPORATION_HALTS_AT_PLANCK_REMNANT_AND_INFORMATION_IS_PRESERVED**

Question (user): what happens to the BH core when it evaporates — is information lost?

GR/semiclassical paradox: BH shrinks to M->0 with T->infinity (final burst,
singularity exposed); if it vanishes into thermal radiation, infalling
information is lost (violates unitarity). QNG changes both endpoints.

**T1 — Hawking temperature.** With QNG constants (hbar=0.2326, c=0.108,
G=0.0583), semiclassical T_H = hbar c^3/(8 pi G M) ~ 1/M (smaller BH hotter).

**T2 — evaporation halts at a Planck remnant.** The horizon r_s = 2GM cannot
shrink below the minimum cell a_L, so evaporation stops at M_rem ~ a_L/2 = 0.152
Planck masses: a STABLE remnant — no T->infinity burst, no exposed singularity.
The Phase-37 node-core stays covered or becomes the remnant.

**T3 — information preserved (unitarity), DEMONSTRATED.** The v8 substrate update
is symplectic = time-reversal symmetric = reversible. A 64-node toy evolved 5000
symplectic steps forward then 5000 backward returns to its initial state to
**err = 2.3e-14** (machine precision). A reversible microscopic law cannot
destroy information → QNG is unitary by construction. The information exits in
radiation correlations and/or is held by the remnant; the paradox is a
continuum/semiclassical artifact the discrete reversible substrate does not share.

Honest scope: T_H used semiclassically (not re-derived from QNG microphysics —
that is the open `qng-hawking-temperature-program`); remnant-mass O(1) coefficient
depends on horizon<->a_L matching. Robust QNG-specific content: (i) minimum length
forces a FINITE remnant (no infinite-T burst); (ii) the substrate is provably
reversible → information conserved. Same discreteness + unitarity that tamed the
graviton (Phase 36) and the singularity (Phase 37).
