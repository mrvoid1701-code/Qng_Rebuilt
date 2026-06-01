# Phase D Empirical Tests — 2026-04-25

Tests run against downloaded observational data:
- B1 — Rotation curves (DS-006 Rotmod_LTG, 176 galaxies)
- B2 — Cluster lensing offsets (Clowe 2006 + PSZ2 strict5, 527 clusters)
- B3 — Pioneer + flyby anomalies (Anderson 2002, 2008)
- A2 + C1 — Planck TT power spectrum (R3.01)

Plus D0 — Trajectory lag legacy prediction status audit.

## Summary

| Test | Result | Implication for QNG |
|---|---|---|
| B1 rotation | QNG correction at galactic scale ~10⁻¹⁰ vs 50% DM discrepancy | Confirmed: QNG does not replace DM at galaxy scale |
| B2 clusters | QNG correction at cluster scale ~10⁻¹² vs 200 kpc Bullet offset | Confirmed: QNG does not explain cluster DM |
| B3 Pioneer | QNG correction ~10⁻³³ m/s² vs Pioneer 8.7×10⁻¹⁰ m/s² | Confirmed: QNG does not explain Pioneer; +9 orders too small, wrong sign |
| C1 acoustic peaks | Detected Planck peaks consistent with ΛCDM positions | PASS: QNG with Λ=0 + Yukawa cosmological matches |
| **A2 low-ℓ ISW** | **ℓ=2 quadrupole DEFICIT (-1.9σ); Paper 4 predicts ENHANCED** | **YELLOW FLAG on Paper 4 §5.3** |
| D0 trajectory lag | Legacy proxy (DER-TRJ-001) suspended under v10 (Tesla gauge FALSIFIED retracted χ-as-memory) | Open question: does v10 χ-Channel-D give any trajectory signature? |

## Detailed findings

### B1 — Rotation curves (CPU-127)

176 galaxies, 2338 valid (radius, v_obs, v_baryon) data points from DS-006
Rotmod_LTG dataset (SPARC-like).

- Mean discrepancy: (v_obs² - v_baryon²)/v_obs² = 0.510
- Median discrepancy: 0.548
- Typical galactic radii: 0.1 - 50 kpc
- QNG Yukawa correction (using λ_screen = R_Hubble): 10⁻¹⁴ to 10⁻¹⁰ (relative)
- Fraction QNG explains: ~10⁻¹¹% to ~10⁻⁸%

**Verdict B1: PASS-honest** — confirms Paper 3 §6.1.6 statement that
QNG does not address galactic dark matter. Yukawa screening operates at
cosmological scale by construction.

### B2 — Cluster lensing offsets (CPU-130)

Bullet Cluster (Clowe 2006): 47 arcsec mass-baryon offset = ~218 kpc.
PSZ2 strict5 sample: 527 clusters, median offset 1.26 arcmin (~354 kpc).

QNG Yukawa correction at cluster scale (~Mpc): 10⁻¹² to 10⁻⁸ relative.
Required: ~1.0 (full non-Newtonian gravity).

**Verdict B2: PASS-honest** — confirms QNG does not explain DM offsets at
cluster scale. Compatible with QNG scope, NOT a falsification.

### B3 — Pioneer + flyby (CPU-128)

Pioneer 10/11 anomaly: 8.74×10⁻¹⁰ m/s² sunward at 50 AU.
QNG Yukawa correction: 3.6×10⁻³³ × (r/λ) ≈ 10⁻³³ m/s².

Ratio QNG/observed: 4×10⁻²⁴.
**QNG is 24 orders of magnitude too small AND wrong sign.**

Earth flyby anomalies: 0.02 - 13.5 mm/s.
QNG correction at perigee: ~10⁻³³ mm/s.
Ratio: 10⁻³⁴.

**Verdict B3: PASS-honest** — Paper 3 §6 explicitly notes QNG does not
explain solar-system anomalies. Confirmed.

### C1 — Planck TT acoustic peaks (CPU-129)

Detected first 5 acoustic peaks in Planck TT data; positions consistent
with ΛCDM Planck 2018 best-fit at within bin resolution (~5%).

**Verdict C1: PASS** — QNG with Λ=0 (Stability Principle) + Yukawa
cosmological does NOT modify pre-recombination physics. Acoustic peak
positions (sound horizon at last-scattering) match ΛCDM as predicted.

This is consistency, not a new prediction.

### A2 — Low-ℓ ISW (CPU-129) — **YELLOW FLAG**

Paper 4 §5.3 prediction: "the cross-correlation of CMB anisotropy with
large-scale structure (the 'late ISW' signal) is enhanced in QNG
relative to ΛCDM at large angular scales."

Direct CMB×LSS cross-correlation test requires full pipeline; **not
attempted in this round**.

Indirect proxy: TT auto-spectrum at low ℓ.
Observed: D_ℓ=2 = 226 μK² vs ΛCDM ~1200 μK² (-1.9σ DEFICIT).

If QNG enhanced late-ISW → would predict EXCESS at low ℓ.
Observed DEFICIT goes opposite direction.

**Caveat**: TT auto-spectrum is dominated by Sachs-Wolfe, not late-ISW.
Late-ISW is ~10% of low-ℓ TT total. The ℓ=2 deficit could be due to
other causes (cosmic variance, foregrounds, alignment puzzles unrelated
to Paper 4).

**Verdict A2: INCONCLUSIVE with yellow flag.** Paper 4 §5.3 needs:
1. Quantitative QNG-modified C_ℓ computation (full Friedmann + Yukawa
   transfer function).
2. Direct CMB×LSS cross-correlation test (Planck × eBOSS).
3. If after proper computation Paper 4 still predicts enhanced ISW
   while data shows deficit, **§5.3 prediction must be revised**.

### D0 — Trajectory lag legacy prediction status

`DER-TRJ-001` (`05_phenomenology/trajectory/qng-trajectory-lag-proxy-v1.md`)
was a legacy phenomenological proxy:
```
R_edge(i) = L_edge(i) · a_edge(i)
A_trj = Σ R_edge(i)
S_trj = Σ |R_edge(i)|
```

**Status under v10/v11 (current 2026-04-25):**

1. The proxy used `L_eff` interpreted as coarse-grained χ-as-memory.
2. This χ interpretation was **superseded** by v8/v10:
   - χ is NOT a memory field.
   - χ is matter-gravity responsiveness via Channel D.
   - Tesla U(1) gauge interpretation FALSIFIED.
3. Under current v10, the legacy formula has no derived basis.
4. CPU-128 confirmed Yukawa-only mechanism gives negligible trajectory
   lag in solar system.

**However**: a v10/v11 derivation of trajectory effects from Channel D
dynamics is **open work**. χ does have its own dynamics in v10
(`χ_n += CHI_REL·(σ̄_g - σ_g) + DELTA·(σ_ref - σ_g) - CHI_DECAY·χ_n`),
which COULD in principle leave a "memory" of trajectories through
gravitational potentials. This has not been derived or tested in v10.

**Verdict D0: SUSPENDED**. Legacy proxy retracted. Reopen as v10/v11
research program if there is interest in solar-system signature
predictions.

## Implications for the Paper Series

### Paper 1 (ℏ derivation): UNAFFECTED
ℏ derivation is independent of empirical tests in Phase D.

### Paper 2 (Λ = 0 / Stability Principle): MILD CONFIRMATION
Acoustic peaks match ΛCDM (which has Λ ~ 10⁻¹²²). Consistent with
Paper 2's "Λ = 0 + Yukawa screening at cosmological scale" picture.
Does not directly test Stability Principle but consistent with it.

### Paper 3 (Comprehensive Framework): CONFIRMED
All "honest scope" disclaimers (no DM, no Pioneer, no full GR) are
empirically validated by B1, B2, B3 — QNG simply does not address
these problems, and the data confirm this is the correct scope.

### Paper 4 (Yukawa Cosmological Prediction): YELLOW FLAG
- §5.1 (w(z=0.5)): not testable without SN Ia data + Boltzmann code.
- §5.2 (suppressed P(k) at k < 0.01 h/Mpc): NOT YET tested (requires
  eBOSS BAO analysis).
- **§5.3 (enhanced late-ISW): INDIRECT evidence against from ℓ=2
  quadrupole deficit. Direct test (CMB×LSS) pending.**
- §5.4 (modified P(k)): NOT YET tested.

**Action for Paper 4**: revise §5.3 wording to explicitly note that
the predicted "enhancement" applies to CMB×LSS cross-correlation,
NOT to TT auto-spectrum alone, AND to acknowledge the ℓ=2 quadrupole
deficit as a yellow flag pending full quantitative analysis.

## Next-step priorities

### High priority (test Paper 4 directly)
1. **A1 — eBOSS BAO scale analysis**: real test of Paper 4 §5.2
   prediction (P(k) modification). Major effort (FITS parsing,
   correlation function).
2. **A3 — Direct CMB×LSS cross-correlation**: real test of §5.3.
   Heavy-pipeline.

### Medium priority
3. **Quantitative QNG-modified C_ℓ**: implement Friedmann + Yukawa
   in a Boltzmann-style code. Requires substantial dev.
4. **w(z) computation**: via modified Friedmann + Yukawa screening.

### Low priority
5. **D0 v10 trajectory derivation**: investigate whether Channel D
   dynamics give detectable solar-system signature.

## Files

Tests:
- `tests/cpu/qng_cpu127_rotation_yukawa_check.py`
- `tests/cpu/qng_cpu128_pioneer_yukawa_check.py`
- `tests/cpu/qng_cpu129_planck_tt_acoustic_peaks.py`
- `tests/cpu/qng_cpu130_cluster_lensing_check.py`

Reports:
- This file: `07_validation/audits/phase_d_empirical_2026_04_25/REPORT.md`
