---
type: derivation
id: DER-QNG-074
title: Gap 13 — Scale tension between unit-bridge and phenomenological calibrations
status: STRUCTURAL GAP IDENTIFIED (22 orders of magnitude tension)
author: C.D Gabriel
date: 2026-04-25
upstream:
  - DER-QNG-038 (baryon ladder, phenomenological calibration)
  - DER-QNG-067 (hbar derivation paper)
  - CPU-114 (unit-bridge SI consistency)
  - CPU-124 (scale tension audit)
---

# DER-QNG-074 — Gap 13: scale tension

## Statement

The QNG codebase contains two distinct calibrations of the natural mass
unit `a_M`, and they differ by **~22 orders of magnitude**:

| Calibration | Source | Value | Nature |
|---|---|---|---|
| `a_M_phenom` | DER-QNG-038 | 1.287 MeV/unit (= 2.30×10⁻³⁰ kg) | phenomenological fit (R=4 ↦ nucleon) |
| `a_M_bridge` | CPU-114 unit-bridge | 1.86×10²² MeV/unit (= 3.32×10⁻⁸ kg = 1.524 m_Planck) | substrate-derived from c, G, ℏ → SI |

Ratio: `a_M_bridge / a_M_phenom = 1.45 × 10²²`.

**Both cannot be the correct natural mass unit simultaneously.**

## Discovery context

Identified during Phase C1 prerequisite audit (CPU-124, 2026-04-25),
when starting baryon-ladder re-derivation under v10. The tension was
masked previously because:

1. DER-QNG-038 used `a_M_phenom` as ad-hoc calibration (no claim about
   underlying mass scale).
2. CPU-114 unit-bridge derived `a_M_bridge` purely structurally
   (no comparison to ring data was done).
3. CPU-115 `E = mc²` test used `a_M_phenom` for the calibration check
   (treating it as if it were the physical mass), which obscured the
   tension by mixing the two calibrations within a single derivation.

The correction requires Phase C1 to be re-scoped before continuing.

## Which calibration is structurally derived?

`a_M_bridge` is the unique solution of the 3-equation system:
```
c_SI = c_QNG · (a_L/a_T)
G_SI = G_QNG · (a_L³ / (a_M · a_T²))
ℏ_SI = ℏ_QNG · (a_M · a_L² / a_T)
```
with `(c_QNG, G_QNG, ℏ_QNG)` substrate-derived. CPU-114 verified
machine-precision recovery of `(c_SI, G_SI, ℏ_SI)` from the solution
(< 10⁻¹⁰). The calibration is therefore **forced by the
substrate-derived constants**.

`a_M_phenom` is a one-parameter fit setting `M_ring(R=4)` = nucleon.
Once chosen, the predictions for R=5, 6, 7 follow at <2% (DER-QNG-038),
which is non-trivial — but the absolute scale is **not derived**.

**Conclusion**: `a_M_bridge` is the physically correct natural mass
unit. `a_M_phenom` is a ratio-preserving phenomenological calibration
that does not reflect substrate physics.

## Implications

### Ring masses under correct (substrate-derived) calibration

| R | M_ring | mass (substrate kg) | mass (substrate GeV) |
|---|---|---|---|
| 3 | 474.15 | 1.57×10⁻⁵ kg | 8.82×10²¹ GeV |
| 4 | 728.92 | 2.42×10⁻⁵ kg | 1.36×10²² GeV |
| 5 | 954.88 | 3.17×10⁻⁵ kg | 1.78×10²² GeV |
| 6 | 1172.13 | 3.89×10⁻⁵ kg | 2.18×10²² GeV |
| 7 | 1328.10 | 4.41×10⁻⁵ kg | 2.47×10²² GeV |

Compare with nucleon: 0.938 GeV.

**Under substrate-derived calibration, QNG rings are NOT hadrons.**
They are objects with mass ~10²² GeV — roughly 10⁻³ Planck masses each
(actually ~10⁻⁴ to 10⁻³ m_Planck × c² depending on R).

Wait — let me recompute. m_Planck = 2.176×10⁻⁸ kg. M_ring(R=4) = 728.92
units. Each unit = 1.524 m_Planck. So ring mass = 728.92 × 1.524 m_Planck
≈ 1110 m_Planck. That's a thousand Planck masses, not sub-Planck.
Energy = 1110 × E_Planck ≈ 1.36×10²² GeV.

So actually rings are **super-Planck-scale objects** in absolute mass.
This is consistent with rings being collective excitations of many
sub-Planck-spaced lattice sites.

### Hadron-ratio pattern preserved

The DER-QNG-038 finding that `M_ring(R)/M_ring(R=4)` matches hadron
mass ratios to <2% is **calibration-independent** (ratios cancel `a_M`).
This pattern is real and structurally interesting.

But its INTERPRETATION as "QNG explains hadron masses" requires either:
- A scale-bridging mechanism (Gap 13 closure path) translating Planck-scale
  substrate to hadronic-scale phenomenology
- Acceptance that the ratio match is coincidental (4-point pattern, not
  enough data to be conclusive)

### CPU-115 result must be recontextualized

The CPU-115 "E=mc² PASS" claim used `a_M_phenom` to compute "m_ring
= 938 MeV" matching nucleon. With `a_M_bridge`, the ring rest energy
is 433 × 1.86×10²² MeV ≈ 8×10²¹ MeV, and m_inertial = 7×10²¹ MeV/c²,
**NOT 938 MeV**. The CPU-115 PASS verdict thus **inherits the
phenomenological-calibration assumption**, not the substrate-derived
one. Under substrate-derived calibration, `m_inertial / M_ring` ratio
~ 50 still holds (DER-QNG-068 distinction between inertial mass and
topological charge), but absolute identification with nucleon does not.

### DER-QNG-068 status update

DER-QNG-068 closed DER-QNG-044 to 6/6 PASS in v10. The tests that
relied on CPU-115's nucleon identification (E=mc² Test 1) must be
re-graded:

- **Test 1 E=mc²**: PASS structurally (m_inertial well-defined as
  E_rest/c²) — but the **identification with nucleon mass is
  phenomenological, not substrate-derived**. Under substrate calibration,
  m_inertial(R=4) ≈ 10²¹ GeV/c², not 938 MeV.

- Other tests (Shapiro, bending, Pound-Rebka, WEP, Hawking T_H, far-field,
  Λ=0) use only c, G, ℏ derivations and unit-bridge directly, so they are
  **unaffected by Gap 13**.

## Possibilities for Gap 13 closure

### Possibility A: Renormalization-group flow

QNG substrate operates at Planck scale with `a_M ~ 1.5 m_Planck`.
Hadronic-scale physics emerges via renormalization-group flow analogous
to QCD running. Hadrons are dressed Planck-scale rings whose effective
mass at low energies is ~ GeV. This requires **derivation of the
beta function** for QNG running couplings — substantial open program.

### Possibility B: M_ring ratio coincidence

The 4-point match of M_ring ratios with hadron mass ratios is
coincidental. Real ring masses are Planck-scale, real hadrons are
unrelated. DER-QNG-038 is then RETRACTED.

Test: extend M_ring measurements to more values of R (R=8, 9, 10, ...).
If the ratio match continues, structural pattern is reinforced. If it
breaks, coincidence is confirmed.

### Possibility C: Unit-bridge mis-identifies physical scale

The substrate-derived c, G, ℏ values may not correspond to the
physical c, G, ℏ in our universe. They could be effective values
at QNG's intrinsic scale, which is intermediate (sub-Planck,
super-hadronic).

But this contradicts CPU-114's machine-precision SI consistency check,
unless we reinterpret what CPU-114 actually verified.

### Possibility D: Two-scale theory by design

QNG is a multi-scale theory:
- Substrate at Planck scale (a_L, a_M, a_T = unit-bridge values)
- Composite particles at hadronic scale (M_ring × phenomenological a_M)
- The mapping between scales is an EMERGENCE relation (not unit
  conversion)

This requires explicit derivation of the scale-mapping mechanism.
Closest analog: QCD where quark scale (~ 1 GeV) emerges from QCD scale
(Lambda_QCD ~ 200 MeV) via running coupling, but the underlying QCD
fields live at all scales.

## Recommendation

1. **Add Gap 13 to THEORY_STATE Section 3 as open-HIGH** alongside
   Gap 12.
2. **Update DER-QNG-038 with explicit caveat**: "Mass ratios are
   structurally meaningful; absolute mass identification with hadron
   spectrum requires Gap 13 resolution."
3. **Update DER-QNG-068 (Test 1 E=mc²)**: PASS structurally for
   m_inertial/E_rest distinction; nucleon mass identification is
   phenomenological, pending Gap 13.
4. **Phase C1 re-scoped**: "v10 baryon-ladder re-derivation" becomes
   "v10 ring-spectrum analysis with explicit scale-bridging discussion".
5. **Don't proceed with C2 (leptons) until Gap 13 has at least
   provisional treatment** — otherwise we'd compound the calibration
   confusion.

## Honest impact on QNG status

**Before this audit**: QNG appeared to derive c, G, ℏ AND identify
nucleon, delta, N*, Δ' from ring topology — strong evidence for the
theory.

**After this audit**: QNG derives c, G, ℏ at Planck scale; the M_ring
ratio pattern matching hadron ratios is real but **the absolute
hadron-scale identification is a phenomenological choice, not a
substrate prediction**.

Net status: c, G, ℏ derivation is robust. Hadron-mass derivation is
**reduced from "predicted" to "ratio-pattern, scale unsolved"**.

## What remains valid

- DER-QNG-067 (ℏ derivation paper) — does not depend on hadron scale.
- Stability Principle, Λ = 0, Hawking T_H formula — all geometric,
  unaffected.
- DER-QNG-044 6/6 PASS — except Test 1 E=mc² needs re-grading per above.
- v11 spin-2 graviton (DER-QNG-072) — unaffected by mass-scale issue.
- Unit-bridge to SI for c, G, ℏ — unaffected (it IS the calibration).

## What requires Gap 13 closure

- DER-QNG-038 baryon ladder absolute mass identification.
- Particle physics program (Phase C) requires scale resolution before
  meaningful results possible.
- BH micro-state interpretation (would require knowing what QNG ring
  IS in terms of physical particles).

## Self-verification

- CPU-124 (this session): explicitly computed both calibrations,
  exposed 22-order discrepancy.
- Cross-check via Planck mass: m_Planck = 2.176e-8 kg; a_M_bridge
  = 3.317e-8 kg = 1.524 m_Planck. Direct numerical verification.
- Hadron ratio preservation under bridge calibration: trivial (ratios
  cancel calibration constant). Confirmed in CPU-124 output.
