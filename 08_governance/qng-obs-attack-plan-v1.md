# QNG Observational Attack Plan v1

Type: `note`
Status: `active`
Author: `C.D Gabriel`
Date: `2026-04-05`

## Context

QNG-OBS-001 returned FAIL on Check 3: the per-galaxy free parameter a_M is
uncorrelated with baryonic mass (Pearson r = -0.03). The flat-ether model
improves chi²/dof 2.26x mechanically (adding one free param per galaxy always
helps), but the QNG-specific physical prediction — that a_M ∝ M_baryon — is
not confirmed.

Three open issues from QNG-OBS-001:
1. The flat-ether profile may be wrong or too simple — a per-galaxy free
   constant is just absorbing residual noise.
2. The physical scaling a_M ∝ M_baryon (from Tully-Fisher + chi-field sourcing)
   does not hold in this dataset.
3. The test had 171 free parameters (one a_M per galaxy) — not a prediction.

---

## QNG-OBS-002: Global a_M — the real bet

**The bet:**

Use a_M fixed globally at A_vortex_ring = 0.225 (extracted from the 3D vortex
ring simulation, QNG-CPU-043 + DER-QNG-027). No per-galaxy fitting. Zero free
parameters.

```
V²_QNG(r) = V²_baryon(r) + 0.225
```

Applied identically to all 175 galaxies.

**Win condition:** if the median chi²/dof improvement is still >= 1.5x over
baryon-only with this single number, then one value extracted from a small 3D
lattice vortex explains galaxy rotation better than Einstein's baryon-only model.
That is a genuine QNG confirmation.

**Lose condition:** improvement < 1.5x, or QNG gets WORSE than baryon-only —
meaning the fixed value is too large for most galaxies (over-corrects).

**Why this matters:** QNG-OBS-001 showed that letting the computer choose a_M
per galaxy always helps (trivially). QNG-OBS-002 removes all freedom — the
substrate itself fixes the amplitude. If it works, the chi-field from a vortex
ring lattice simulation directly predicts real galaxy dynamics.

**Implementation note:** same weighted chi²/dof machinery as QNG-OBS-001,
but skip the WLS fit — just subtract baryon_term and compute residuals against
the fixed a_M = 0.225.

---

## QNG-OBS-003: QNG vs MOND

**Purpose:** Compare the QNG flat-ether model against MOND on the same 175
galaxies. MOND predicts:

```
a_MOND = sqrt(a_N × a_0)   for a_N << a_0
```

where a_N is the Newtonian acceleration and a_0 ≈ 1.2e-10 m/s².

In terms of rotation curves:
```
V⁴_MOND = V²_baryon × a_0 × r
```

**Question:** Does QNG do something MOND doesn't, or are they equivalent at
this level of comparison?

Three outcomes:
1. QNG flat model fits comparably to MOND → QNG has a different physical
   mechanism but similar predictive power at this scale.
2. MOND fits significantly better → the QNG flat profile is the wrong shape;
   the chi-field must have a MOND-like radial dependence, not a flat one.
3. QNG fits significantly better → the flat constant is a better description
   of the data than the MOND interpolating function.

**Implementation note:** requires computing a_N(r) = V²_baryon(r) / r for each
data point, applying the MOND interpolating function (simple form: mu(x) = x/sqrt(1+x²)),
and computing chi²/dof for the MOND prediction without free parameters (using
a_0 from literature).

---

## Attack order for tomorrow

1. QNG-OBS-002 first — write prereg + script + run on 175 galaxies.
   Expected runtime: < 1 second (no simulation, just arithmetic on CSV).
   
2. If QNG-OBS-002 PASS (>= 1.5x improvement): declare the vortex bet won.
   Write the result note, commit, then move to QNG-OBS-003 for comparison.
   
3. If QNG-OBS-002 FAIL: diagnose — is it because a_M=0.225 is too large
   (over-corrects massive galaxies) or too small (under-corrects dwarfs)?
   Inform whether a_M needs mass-dependent scaling or a different profile.

4. QNG-OBS-003 in parallel or after: MOND comparison gives context for
   interpreting whatever QNG-OBS-002 returns.

---

## Key numbers to carry forward

- A_vortex_ring = 0.225 (QNG-CPU-043)
- G_QNG = beta/z = 0.35/6 = 0.0583
- lambda_substrate = 3.41 lattice units
- Delta_V² = a_M × alpha × M_baryon (DER-QNG-027 prediction; Check 3 of OBS-001 FAIL)
- Pearson r(a_M, M_proxy) = -0.03 (OBS-001 result — a_M uncorrelated with mass)
- chi²/dof improvement with free a_M: 2.26x (38.87 → 17.17)
- Mean M_proxy for negative-a_M galaxies: 50792 (3x higher than positive-a_M group)
