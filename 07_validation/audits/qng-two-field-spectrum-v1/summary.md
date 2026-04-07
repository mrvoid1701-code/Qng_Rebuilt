# QNG-CPU-063 Audit Summary

**Result: FAIL (Check 2 — v7 spectrum differs from v5 by design)**
Date: 2026-04-07
Script: `tests/cpu/qng_two_field_spectrum_reference.py`

## Check results

| Check | Gate | Result |
|-------|------|--------|
| 1 - All rings survive (M>10) | M>10 for R=2..5 | PASS |
| 2 - v7 ratios match v5 within 5% | diff < 0.05 | FAIL (expected — different physics) |
| 3 - Pion ratio R=2 preserved | ratio ~ 0.149 | FAIL (ratio=0.383, pion match lost) |

## Mass spectrum at T=1000

| R | M_ring | E_ring | H(k=0.10) | H/H(R=5) | v5 ratio |
|---|--------|--------|-----------|----------|----------|
| 2 | 343.6  | 7.09   | 7.09      | 0.3833   | 0.1477   |
| 3 | 474.1  | 9.63   | 9.63      | 0.5203   | 0.2946   |
| 4 | 728.9  | 14.45  | 14.45     | 0.7810   | 0.6591   |
| 5 | 954.9  | 18.50  | 18.50     | 1.0000   | 1.0000   |

Note: H ≈ E_ring because chi_rms ~ 0.001 (chi couples to sigma_g, not sigma_m
in v7 -- no chi buildup at ring, so T = k_back/2 * sum_chi2 ≈ 0).

## Hadron ratio comparison

| R | ratio | Best match | PDG ratio | Deviation |
|---|-------|------------|-----------|-----------|
| 2 | 0.383 | K(494)?    | 0.527     | 27% (no match) |
| 3 | 0.520 | K(494 MeV) | 0.527     | **1.4% MATCH** |
| 4 | 0.781 | rho(770)   | 0.821     | 5% (borderline) |
| 5 | 1.000 | proton     | 1.000     | 0% (reference) |

NEW FINDING: R=3 matches K meson (strange meson, 494 MeV) to 1.4% in v7.
v5 had R=2 matching pion (140 MeV) to 1%.

## Why the spectrum changes

In v5: H = k_back/2 * sum_chi2 + E_ring
  chi_rms ~ 5 (large, from DELTA coupling to sigma)
  sum_chi2 ~ R^2 (chi_rms ~ R)
  H ~ k_back * R^2 / 2  (kinetic term dominates)
  H ~ R^2 scaling

In v7: E_ring only (chi ~ 0, coupled to sigma_g which is flat)
  E_ring = pure potential energy of sigma_m / phi vortex configuration
  E_ring ~ circumference of ring ~ 2*pi*R ~ R
  E_ring ~ R^1 scaling (string tension)

The v7 spectrum reflects the GEOMETRIC energy of the phi string defect.
The v5 spectrum reflected the KINETIC energy of the chi field around the ring.
These are physically distinct mass generation mechanisms.

## Scaling analysis: E ~ R^n

E_ring(R) at T=1000: 7.09, 9.63, 14.45, 18.50 for R=2,3,4,5.

Best-fit power law between pairs:
  E(R=3)/E(R=2) = 1.36  -> R^n with n = log(1.36)/log(1.5) = 0.80
  E(R=4)/E(R=2) = 2.04  -> R^n with n = log(2.04)/log(2.0) = 1.03
  E(R=5)/E(R=2) = 2.61  -> R^n with n = log(2.61)/log(2.5) = 1.06

Average n ≈ 0.96 ≈ 1 (approximately LINEAR in R).

Physical interpretation: E_ring ~ 2*pi*R * epsilon, where epsilon is the
vortex line tension (energy per unit length). This is the "string tension"
spectrum — the phi field is a topological string with finite tension.

## Comparison: v5 vs v7 spectra

| Property | v5 | v7 |
|----------|----|----|
| Mass mechanism | chi kinetic energy | phi string tension |
| E scaling | H ~ R^2 | E ~ R^1 |
| Absolute scale | H ~ 1600-10884 | E ~ 7-19 |
| Best hadron match | pi(140) at R=2 (1%) | K(494) at R=3 (1.4%) |
| Chi content | large (chi_rms ~ 5) | negligible (chi_rms ~ 0.001) |

## Physical interpretation

The v7 spectrum is the "pure geometry" spectrum of phi vortex rings.
Mass ∝ ring circumference (string tension). This predicts:
  m(R=2) / m(R=5) = 2/5 = 0.4   (pure linear)
  Measured: 7.09/18.50 = 0.383  (close to 0.4)

The K meson match at R=3 (1.4%) may be coincidental, like the pion match
in v5 was probably coincidental (both near R/R_max scaling).

## Key architectural finding

The v7 two-field substrate has TWO possible mass generation mechanisms:
1. Geometric (string tension): E_ring ~ R (this test, v7 without chi content)
2. Kinetic (chi field): T = k_back/2 * sum_chi2 ~ R^2 (v5 mechanism)

To recover the kinetic mass in v7, need chi to couple to sigma_m (not just
sigma_g). This requires a DELTA_m coupling:
  chi_i += DELTA_m * (sigma_m_ref - sigma_m_i)

With this addition: chi builds up at ring → T > 0 → H spectrum similar to v5.
The two mechanisms can coexist: E_string + T_kinetic.

## Next architectural question

Should chi couple to:
  (a) sigma_g only (current v7) -- clean separation, but no kinetic mass
  (b) sigma_m only -- kinetic mass at ring, but chi doesn't propagate as KG wave
  (c) both sigma_g and sigma_m -- chi is shared momentum field

Option (c) is the most physical: chi = canonical momentum of ALL substrate
degrees of freedom. This recovers the v5 kinetic mass while preserving v7
ring stability (Channel G only in sigma_g).
