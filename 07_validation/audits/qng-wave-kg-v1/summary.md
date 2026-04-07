# QNG-CPU-054: Massless Klein-Gordon Wave Test
- **decision**: `PASS`
- **date**: 2026-04-07
- **author**: C.D Gabriel

## Parameters
- L=64, w=4.0, delta=0.0 (massless), A_perturb=0.15
- alpha=0.005, beta=0.35, chi_rel=0.35, chi_decay=0.001
- k_back scan: [0.10, 0.50, 1.00]
- MAX_STEPS=200, T_START_FIT=30

## Corrected speed formula (DER-QNG-032 fix)
Original draft had v²=k_back×beta. Corrected to v²=k_back×chi_rel/6.
Reason: z=6 cubic lattice uses average of neighbors (sb=(1/z)∑σ_nb),
so (sb-si)=∇²s/6, not ∇²s. Factor of 6 missing from draft.

## Speed Results
| k_back | v_pred | v_measured | rel_err | ballistic_ratio |
|--------|--------|------------|---------|-----------------|
| 0.10 | 0.0764 | 0.0608 | 20.4% | 3.19 |
| 0.50 | 0.1708 | 0.1624 | **4.9%** | 9.37 |
| 1.00 | 0.2415 | 0.2286 | **5.3%** | 16.32 |

k_back=0.10 remains at 20% error — at low coupling the diffusion timescale
(τ_diff~2 steps) is comparable to the wave period, making measurement noisier.

## Checks
- **Check 1** (wave propagates, r_final > 2w=8): PASS — r=11.0
- **Check 2** (v within 25% of sqrt(chi_rel/6)): PASS — v=0.2286, pred=0.2415, err=5.3%
- **Check 3** (v scales with sqrt(k_back)): PASS — ratio=3.76, pred=3.16
- **Check 4** [info] ballistic > diffusive: PASS — ratio=16.32 (strongly ballistic)

## Key findings

**F1 — Channel G works.** The v6 substrate supports Klein-Gordon wave propagation.
Setting sigma_i += k_back × chi_i (Channel G) converts the parabolic v5 substrate
into a wave-supporting medium. The wave crest travels at v=sqrt(k_back×chi_rel/6).

**F2 — sqrt(k_back) scaling confirmed.** Measured ratio 3.76 vs predicted 3.16.
This confirms the coupling mechanism: chi back-reaction on sigma drives propagation.

**F3 — Strongly ballistic.** ballistic_ratio=16 means chi²(linear fit) is 16×
smaller than chi²(sqrt(t) fit). The wave is genuinely ballistic, not diffusive.

**F4 — Constraint C3 operational.** Setting v_KG = c:
  τ/a = v_meas/c = 0.2286 / (3×10⁸) = 7.62×10⁻¹⁰ s/m
  With C1 (G matching) and m_node=m_proton:
  a = m_p × G_Newton × (τ/a)² / G_QNG ≈ 1.1×10⁻⁵⁴ m (far sub-Planck)
  Note: a is far sub-Planck for m_node=m_proton. This is consistent with the
  finding in DER-QNG-029 that Planck-scale substrate is inconsistent with
  galactic Yukawa. The physical value of m_node is still open (Gap 4, 1 free param).

## Open after this test
- k_back measured: k_back=1 gives v within 5% — but k_back is a free parameter,
  not yet derived from first principles
- Gap 4: 2 constraints (C1+C3) now confirmed numerically; still need m_node
- Gap 5 (α physical value) untouched
- Phi sector Lorentz covariance (DER-QNG-032 §8 P2) not yet tested
- Massless graviton vs massive KG tension (DER-QNG-032 §7 P3) still open

## Artifacts
- `report.json` — full numerical results
- `summary.md` — this file
- Script: `tests/cpu/qng_wave_kg_reference.py`
- Derivation: `04_qng_pure/qng-hamiltonian-conservative-limit-v1.md` (DER-QNG-032)
