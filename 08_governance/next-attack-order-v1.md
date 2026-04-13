# Next Attack Order v1

Type: `note`
ID: `NOTE-GOV-005`
Status: `active`
Author: `C.D Gabriel`
Last updated: `2026-04-13`

## Context

After session 2026-04-13: baryon resonance ladder identified (DER-QNG-038, CPU-074/075 PASS).
R=4->N, R=5->Delta(1232), R=6->N*(1520), R=7->Delta(1700) — one free parameter, three predictions.
CPU-076 registered as decisive stability test. This file ranks what to attack next.

---

## Rank 1 — CPU-076: M_ring ratio stability (IMMEDIATE)

**Why first:** The N/Delta identification rests on M(R=4)/M(R=5) = 0.7634 matching m_N/m_Delta = 0.7616
to 0.24%. CPU-076 tests whether this ratio is a topological invariant of the ring geometry
(stable across parameter variations) or a kinematic coincidence tuned to default parameters.
If the ratio varies >10% across 27 configurations, today's discovery is suspect.
If stable <5%, the identification is robust and all downstream work is justified.

**Script to write:** `tests/cpu/qng_mring_ratio_stability_reference.py`
**Prereg:** `07_validation/prereg/QNG-CPU-076.md` (registered)
**Grid:** alpha_m in {0.003,0.005,0.008}, beta_m in {0.25,0.35,0.45}, gamma_phi in {0.07,0.10,0.14}
**T_P2 scan:** {500, 750, 1000, 1250, 1500} at default params
**Gates:** std/mean < 5% (Part A), T_P2 range < 3% (Part B)

---

## Rank 2 — R=8, 9, 10: isospin rule extension

**Why second:** The even/odd R -> I=1/2 / I=3/2 pattern is observed at 4 points only (R=4,5,6,7).
This is not a derived result — it is a pattern. R=8 should give I=1/2 ~1900 MeV,
R=9 should give I=3/2 ~2100 MeV. Confirmed SM candidates exist near these masses
(N(1900) F15, Delta(2000)). If the rule fails at R=8, the pattern is coincidental.

**Prerequisite:** CPU-076 PASS (topological).
**Script:** extend qng_extended_mring_reference.py to R=8,9,10
**Prereg:** write QNG-CPU-077

---

## Rank 3 — R=3 lifetime measurement

**Why third:** R=3 predicts 611 MeV — no stable SM baryon at this mass. Einstein hypothesis:
R=3 is a sub-threshold / off-shell configuration with short lifetime.
Test: measure T_lifetime(R=3) vs T_lifetime(R=4). If T_lifetime(R=3) << T_lifetime(R=4),
R=3 is an unstable resonance (consistent with no PDG entry). If stable, it is a new prediction.

**Prerequisite:** CPU-076 PASS.
**Prereg:** write QNG-CPU-078 (ring lifetime by radius)

---

## Rank 4 — Decay widths from ring lifetimes

**Why:** Gamma_Delta = 117 MeV is a hard experimental target. If ring lifetime T_life maps to
decay width Gamma ~ hbar/T_life, and if Gamma(R=5) / Gamma(R=4) matches experimental ratio,
this is a zero-free-parameter prediction of decay rates.
Delta(1232) is the easiest target: very broad (Gamma = 117 MeV, lifetime ~1.7e-24 s).

**Prerequisite:** Rank 3 complete (lifetime protocol established).
**Prereg:** write QNG-CPU-079

---

## Rank 5 — Analytic M_ring(R) from H_v7

**Why:** The differences M(5)-M(4)=226, M(6)-M(5)=217, M(7)-M(6)=156 are sublinear and curving.
String-tension predicts E ~ R (linear). Fit the series and compare to E_v7 analytic estimate.
If analytic formula reproduces numerical M_ring(R) to <5%, the connection substrate->spectrum
is not just numerical but derivable.

**No new script needed initially** — analytical derivation from DER-QNG-036 Hamiltonian.
**Prereg:** write DER-QNG-039 (analytic M_ring(R) derivation)

---

## Rank 6 — Derivarea a_M din primitive (Gap 4 complet)

**Why:** a_M = 1.373e-3 = 1/728.92 e o ancora empirica. Daca exista o formula
`a_M = f(alpha_m, beta_m, gamma_phi, k_gm, a/l_Planck)` derivata din H_v7,
Gap 4 se inchide complet fara parametri empirici.

**Prerequisite:** Rank 5 (analytic M_ring formula needed).
**Note:** This is hard. May require v8 with conjugate momentum pi_m.

---

## Rank 7 — Mezonii (B=0 topological objects)

**Why:** Fara mezoni, QNG nu poate pretinde ca reproduce Modelul Standard complet.
Mezoni = B=0, pot fi inele cu W=+1 si W=-1 legate (meson = ring-antirim pair)?
Sau obiecte topologice distincte cu phi winding W=0 dar chi vortex?

**This is a new program**, not a continuation. Requires ontological work before numerics.
**Prerequisite:** baryon sector fully validated (Ranks 1-4 complete).

---

## Rank 8 — v7-symmetric formalizare in DER-QNG-033

**Why:** Back-reaction `sigma_m += k_gm*(sigma_g - sigma_g_ref)` e confirmata de CPU-073
dar nu e inca in derivarea oficiala DER-QNG-033. Trebuie formalizata inainte de paper.

**Quick task:** update DER-QNG-033 with v7-symmetric channel.
**No new numerics needed.**

---

## Structural gaps (long term, no immediate action)

- **Lorentz covariance**: synchronous update = preferred foliation. Conservative limit H=T+E is
  the candidate. This requires v8 (conjugate momentum pi_m for sigma_m) — major program.
- **Spin from ring radius**: QNG derivation of J^P and I from ring geometry R. Open.
- **Gap 5 (cosmological alpha)**: why alpha takes its physical value. Not tractable yet.
- **Action principle**: H_v7 constructed but gradient flow is dissipative. Full action needs v8.
