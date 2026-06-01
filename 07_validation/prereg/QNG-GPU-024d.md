# QNG-GPU-024d

Type: `prereg`
Status: `executed — H_NO_RING_IN_ANY_REGIME` (v2)
Author: `C.D Gabriel`
Date: `2026-04-20` (v1) / `2026-04-21` (v2)
test_class: `structural_diagnostic`
hardware: `GPU`
upstream: `QNG-GPU-024c` (Channel F ruled out as sole driver; H_NO_EQUILIBRIUM)

## Title

v8 static-ring search via gradient-flow relaxation — does v8 admit a
nontrivial static ring equilibrium in any regime?

## Purpose

GPU-024c verdict `H_NO_EQUILIBRIUM` showed that even with Channel F
off, the cached ring does not reach a fixed point under v8 symplectic
evolution. That test ran Hamiltonian dynamics; this test runs pure
gradient flow to directly search for fixed points (wherever
`F_sm = F_phi = 0` in the relevant sector).

Two sub-experiments (v2):

- **A** — Full v8 minus Channel F (`v_couple_on=True`, `channel_f=False`).
  Tests whether sine-Gordon V_couple admits any ring fixed point.
- **B** — V_couple off (`g = 0` effective via `F_sm_nocouple`,
  `F_phi_nocouple`, `channel_f=False`). Tests whether the kinetic
  sector alone admits any ring fixed point. This is the "null" of the
  pair-wise diagnostic.

## Configuration

- L=28, R=4, cached ring `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz`,
  M_ring_base=176.85
- dt_relax=0.05 (overdamped gradient flow)
- v1: N_ITER=5000
- v2: N_ITER=30000 (for dissolution confirmation)
- Pre-flight: measure `||F_sm||_RMS`, `||F_phi||_RMS` on cached ring
  in both channel_f=True and False modes.
- Convergence: `||F|| < 1e-6` → CONVERGED; `|M_ring| < 0.1` → DISSOLVED.
- g = G_V_COUPLE = 0.22 (for Run A).

## Hypothesis map (v2)

Threshold: M_final classified as SURVIVES (≥50), SHRUNK, DISSOLVED (<1).

### H_V_COUPLE_IS_CULPRIT

A = DISSOLVED, B = SURVIVES. ⇒ V_couple (sine-Gordon) specifically
destroys the ring; kinetic sector alone admits a ring fixed point.
Alternative potentials (gauge-invariant, double-Yukawa) may restore
static ring.

### H_STATIC_V8_RING_FOUND

A = SURVIVES. ⇒ The cached ring was a basin flank; a nearby true
v8 fixed point exists. Save relaxed state; re-run all bending probes
from this new cache.

### H_NO_RING_IN_ANY_REGIME

A = DISSOLVED, B = DISSOLVED. ⇒ v8 3D admits no static ring in any
accessible regime. v7 ring ontology is a v7 artifact not inherited
by v8. Dimension hypothesis (Gap 10) strengthened.

### H_PARTIAL_SURVIVAL

A or B = SHRUNK (0.1 < M < 50). ⇒ Possible but unlikely intermediate
equilibrium; requires higher-resolution scan.

## v1 Result (2026-04-20)

**Verdict: H_INCONCLUSIVE.** Single run only (no B variant); N=5000
iter insufficient for final dissolution. Force residuals dropped from
||F_sm||=8.38e-03 to 1.33e-05 (630x); M_ring from 176.85 to 19.09
(9.3x). Clear monotonic descent toward vacuum but incomplete. Needed
extension.

## v2 Result (2026-04-21)

**Verdict: H_NO_RING_IN_ANY_REGIME.**

| Run | config | M_init | M_final | iter at dissolution | ||F_sm||_final |
|---|---|---|---|---|---|
| A | V_couple on, Ch F off | 176.85 | 0.05 | 18000 | 2.18e-08 |
| B | V_couple off, Ch F off | 176.85 | 0.10 | 30000 | 2.23e-08 |

Both relaxations fully dissolve the cached ring to the trivial vacuum
`(sigma_m = sigma_m_ref, phi = 0)`. V_couple accelerates dissolution
(~40% fewer iterations to dissolve) but is not required for it.

## Downstream actions (v2)

- `DER-QNG-047` (`04_qng_pure/qng-v8-no-static-ring-v1.md`) → locked
- `THEORY_STATE.md`: Gap 10 promoted to CONFIRMED via GPU-024d v2.
  Item 2e (Phase-2 ring instability) closed with resolution "no v8
  static ring in 3D". QNG-GPU-025 canceled (no static ring to measure
  against). QNG-GPU-026 (4D KG dispersion) promoted from conditional
  to load-bearing.
- `DER-QNG-038` baryon mass ladder: preserve R-scaling as v7
  conservation law; revise "rest mass" reading (explicit v7 scope).

## Artifacts

- v1 script: `tests/gpu/qng_v8_static_ring_search.py`
- v2 script: `tests/gpu/qng_v8_static_ring_search_v2.py`
- v1 audit: `07_validation/audits/qng-v8-static-ring-search-v1/`
- v2 audit: `07_validation/audits/qng-v8-static-ring-search-v2/`
