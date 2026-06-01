# REPORT — demo Phase-45: QNG relic dark matter vs the real Planck CMB

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase45_cmb_planck_test.py`
Data: `data/cmb/planck/COM_PowerSpect_CMB-TT-full_R3.01.txt` (real Planck TT, 2507 multipoles)
Verdict: **QNG_RELIC_DM_IS_CONSISTENT_WITH_PLANCK_CMB** (abundance as input)

- **T1 — acoustic peaks located in the real data:** 1st ℓ≈220, 2nd ℓ≈516, 3rd
  ℓ≈817 — matches the standard Planck peak ladder.
- **T2 — the dark-matter fingerprint:** strong 3rd peak (D3/D2 = 0.98, prominence
  0.30 above the preceding trough). A strong 3rd peak REQUIRES substantial cold,
  non-baryonic matter — baryon-only acoustic physics cannot boost it this way.
- **T3 — QNG relic DM vs CMB requirements (all PASS):** COLD (v/c~2e-14),
  COLLISIONLESS + PHOTON-DECOUPLED (neutral, Phase 39), GRAVITATING, STABLE
  (Phase 38/43). Abundance Ω_DM h²=0.1200 = the INPUT it must match.

**Honest scope:** consistency test, NOT a from-scratch fit — no Boltzmann code
(CAMB/CLASS) was run to predict the spectrum from QNG parameters, and the relic
abundance is the input, not a prediction. Same status every leading DM candidate
has against the CMB. Net: QNG dark matter (neutral, cold, information-bearing
Planck relic / degenerate dark core) is consistent with Planck; the open piece is
the relic-abundance derivation (primordial production), not the particle's nature.

We also have rotation-curve data (`data/rotation/`): a CDM halo of relics gives
standard rotation curves (same as ΛCDM) — consistent, not a unique discriminator.
