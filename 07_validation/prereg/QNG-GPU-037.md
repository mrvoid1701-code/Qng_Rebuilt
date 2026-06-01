---
type: test
id: QNG-GPU-037
title: Einstein B1 + C1 — phi response to sigma_m wells (trap/repel/radiate)
status: pre-registered
category: gpu
hardware: GPU (CuPy)
upstream:
  - 04_qng_pure/qng-v8-canonical-extension-v1.md
  - 04_qng_pure/qng-v8-analytical-prereqs-v1.md
  - 07_validation/prereg/QNG-GPU-035.md
scripts:
  - tests/gpu/qng_v8_b1_sm_well.py
  - tests/gpu/qng_v8_c1_ring_spectrum.py
audit_dirs:
  - 07_validation/audits/qng-v8-b1-sm-well-v1/
  - 07_validation/audits/qng-v8-c1-ring-spectrum-v1/
---

# Purpose

After QNG-GPU-035 confirmed the Jackiw-Rebbi dispersion m²_φ(x) = (g/(2μ_φ))·(σ_ref − σ_m(x))² at 0.02% precision with uniform σ_m, we now test whether a **localized** σ_m deficit behaves as:

1. a **bound-state cavity** that traps phi (→ baryon ladder = phi spectrum in cached ring)
2. a **Meissner-type cavity** that expels phi
3. a **mass barrier** that lets phi radiate through with attenuation

This is the decisive ontology test distinguishing:
- "matter = phi modes bound inside σ_m wells" (Einstein/Jackiw-Rebbi interpretation)
- "matter = σ_m well that pushes phi OUT" (Meissner/Tesla interpretation)

# Protocol — B1 (Gaussian σ_m well)

Static Gaussian well `σ_m(r) = σ_ref − 0.20·exp(−r²/9)` at center of L=28 box. freeze_sm=True throughout. Two configs:
- Config A: phi uniform 0.05 everywhere (reference).
- Config B: phi Gaussian (amp=0.05, w=3) centered on well.

Evolve T=400 lu with Yoshida4 symplectic. Track phi² inside ball r<4 vs outside.

# Verdict — B1

- `B1_TRAPPED` if Config-B retention > 80% (→ bound state)
- `B1_EXPELLED` if retention < 30% (→ Meissner)
- `B1_DISPERSED` if 30–80% (→ radiating mass barrier)

# Protocol — C1 (cached ring spectrum)

Load cached R=4, L=28 ring. Perturb phi += 0.02·randn(N). freeze_sm to cached σ_m profile. Evolve T=1000 lu. Sample phi at 4 azimuthal ring-core points and 1 ring-center point. FFT each series, extract top 3 peaks.

# Verdict — C1

- `C1_CORE_MODE_FOUND` if ring-azimuthal top peak ω matches √m²_core within ±20%.
- `C1_CORE_MODE_MISSED` otherwise.

# Downstream implication

If **B1 = TRAPPED** and **C1 = CORE_MODE_FOUND**: Jackiw-Rebbi ontology is intact, and the ring spectrum will seed a phi-bound-state baryon ladder.

If **B1 = DISPERSED** or **EXPELLED**: DER-QNG-038 baryon ladder needs new underlying mechanism — rings do not bind phi.
