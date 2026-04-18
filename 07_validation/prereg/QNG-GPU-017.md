# QNG-GPU-017

Type: `prereg`
Status: `registered`
Author: `C.D Gabriel`
Date: `2026-04-18`
test_class: `topology_mass_carrier`
hardware: `GPU`

## Title

Hopfion Q=1 vs ring Q=0 disorder-profile L-scan — testing whether
topology changes the IR behaviour of the phi Goldstone halo.

## Purpose

After the triple-FAIL of ring mass observables (GPU-009..014 M_ring,
GPU-015 H_v7, GPU-016 e_B), Option A (find a better ring-mass observable)
is exhausted. The structural root cause identified by both einstein-mind
and savant-physics-reviewer (2026-04-18) is a **massless phi Goldstone
halo** — GPU-012 measured `dis(r) ~ r^{-2.37}` for the vortex ring at L=80,
giving a slow power-law decay. Any volume-integrated observable inherits
this IR-divergent halo and exhibits either (i) L-drift (M_ring, H_v7,
e_B_global) or (ii) convergence to a non-SM, non-geometric ratio
(e_B_windowed/core ≈ 4.5-4.8 in GPU-016).

Savant-physics-reviewer's recommendation (preferred over Option B "add
V(sigma_m)") is to test whether a topologically different object — a
**Hopfion Q=1** with linked S^1 fibers (π_3(S²)=Z) — changes the IR
decay rate. The Faddeev-Niemi model predicts Hopfion far-field decay
~ r^{-4} (vs r^{-2} for vortex rings). If QNG Hopfion disorder decays
faster than the ring, the IR halo problem is topology-dependent and
Hopfion is a candidate mass carrier. If Hopfion decays at the same rate,
the halo is universal and Option B (new substrate term) is forced.

### Theoretical justification (not ad-hoc)

- Faddeev & Niemi, Nature 387:58 (1997): Hopfion solitons in a non-linear
  sigma model with Skyrme term have mass scaling `E ~ Q^{3/4}`, unlike
  vortex rings where core energy is perimeter-dominated.
- Hietarinta & Salo, PRD 62:081701 (2000): numerical Hopfion stability
  and energy bounds.
- Battye & Sutcliffe, PRL 81:4798 (1998): hopfions in Faddeev-Skyrme have
  compact energy density with exponential rather than power-law tails.
- In QNG, the Hopfion initial condition `phi = atan2(dz, rho-R) +
  q_twist*atan2(dy, dx)` with q_twist=1 adds a toroidal winding to the
  poloidal (ring) winding, giving linking number 1 (Hopf charge Q=1).

**Not a rescue of DER-QNG-038:** Hopfion topology is GENUINELY distinct
from a vortex ring. This is not a post-hoc relabeling; it is testing a
different topological sector.

## Hypothesis

### H1 (PASS — Hopfion cures IR halo):
Hopfion disorder profile decays with exponent `alpha >= 3.0` at L=80,
consistent across L ∈ {60, 80, 100}. The steeper decay indicates a
genuine topological gap (or at least IR localization) absent from the
ring. Option C (Hopfion as mass carrier) is then open for further mass
observables testing.

### H2 (FAIL — halo is universal):
Hopfion disorder exponent `alpha < 2.5` at L=80 (same magnitude as the
ring's 2.37). The IR halo is a universal property of the massless phi
field, not of the topology. Option B (add V(sigma_m) or analogous
substrate term) becomes the only path forward; Option C pivot is
falsified.

### H3 (AMBIGUOUS):
`2.5 <= alpha < 3.0` at L=80. Intermediate improvement; decision
inconclusive. Would require secondary test (Hopfion mass L-scan) to
resolve.

## Upstream

- GPU-009..014 FAIL (M_ring geometric 5/4)
- GPU-015 FAIL (`07_validation/audits/qng-hamiltonian-l-convergence-v1/`)
- GPU-016 FAIL_GEOMETRIC (`07_validation/audits/qng-e-b-l-scan-v1/`)
- GPU-012 baseline (`07_validation/audits/qng-phi-mass-probe-v1/` —
  ring alpha = 2.37 at L=80)
- `04_qng_pure/qng-mass-observable-exhaustion-v1.md` — NOTE-QNG-016
  listing Options B/C
- Savant review (2026-04-18): Hopfion pivot recommendation (see
  `.claude/agent-memory/savant-physics-reviewer/project_mass_identification_status.md`)
- Einstein-mind review (2026-04-18): recommends V(sigma_m) first; this
  pre-reg tests savant's recommendation first because it requires no
  new theory
- CPU-066..072: existing Hopfion stability and shape tests

## Protocol

### Dynamics (identical to GPU-012 / GPU-016: v5 + Channel H)

```
ALPHA = 0.005, BETA = 0.35, DELTA_CHI = 0.20
CHI_DECAY = 0.020, CHI_REL = 0.35, GAMMA_PHI = 0.10
BETA_PHI_MIN = 0.0005, BETA_PHI_RING = 0.06
K_GM = 0.0
PHASE1 = 300, PHASE2 = 1500
```

### Initial condition

Hopfion: `phi = atan2(dz, rho-R) + q_twist * atan2(dy, dx)`, `R=5`.
Two variants per L:
- q_twist = 0 → vortex ring (CONTROL, must reproduce GPU-012 alpha≈2.37 at L=80)
- q_twist = 1 → Hopfion Q=1 (TEST)

### L-scan
```
L ∈ {40, 60, 80, 100}
```

GPU budget: L=100 = 1M sites, ~100 MB per field. Well within 12 GB.

### Measurement

For each (L, q_twist):
1. Run Phase 1 (300 steps, v5 dynamics, no Channel F).
2. Run Phase 2 (1500 steps, v5 + Channel F, + Channel H phi confinement).
3. Measure radial disorder profile `dis(r)` in spherical shells
   `r in {0.5, 1.5, 2.5, ..., L/2 - 2.5}` centered on box.
4. Fit power law `dis(r) = A * r^{-alpha}` in the bulk tail
   `r ∈ [R+5, L/2 - 3]` using log-log linear regression.
5. Compute R² goodness-of-fit.

### Observable

`alpha_{q=0}(L)` and `alpha_{q=1}(L)` for each L.

Cross-check: fit EXPONENTIAL `dis(r) = A * exp(-r/xi)` as alternative;
record which has higher R² (power-law vs exponential distinguishes
Goldstone from gapped).

## Gates

**Gate 1 — control reproducibility (GPU-012 vintage):**
```
|alpha_{q=0}(L=80) - 2.37| < 0.20
```
If this fails, dynamics have drifted from GPU-012 and the test is void.

**Gate 2 — Hopfion decay exponent:**
```
alpha_{q=1}(L=80) >= 3.0    [PASS clearly]
alpha_{q=1}(L=80) < 2.5     [FAIL clearly]
```
Intermediate → AMBIGUOUS.

**Gate 3 — L-independence of Hopfion exponent:**
```
max(alpha_{q=1}) - min(alpha_{q=1}) over L in {60, 80, 100} < 0.25
```
If alpha drifts with L, the fit is unreliable and result is AMBIGUOUS.

**Gate 4 — power-law vs exponential:**
Record R² for both fits on Hopfion at L=80. If exponential R² > power-law
R² by > 0.05, Hopfion has a mass gap (even stronger result — alpha
concept stops applying and xi is the relevant scale).

## Decision rule

- **PASS** (Hopfion pivot justified): Gate 1 + Gate 2 PASS + Gate 3.
  Interpretation: Hopfion is topologically distinct in IR behaviour;
  viable mass-carrier candidate. Follow-up: pre-register Hopfion mass
  L-scan analogous to GPU-016 for e_B.

- **PASS_STRONG** (Hopfion has a gap): Gate 1 + Gate 4 (exponential
  better fit). Hopfion has dynamically generated mass. Option C is
  strongly preferred over Option B.

- **FAIL** (halo is universal): Gate 1 PASS + Gate 2 FAIL clear.
  Interpretation: Goldstone halo is not cured by topology. Option C
  falsified at the structural level. Option B (add V(sigma_m) or
  equivalent substrate term) is forced as the only remaining path.
  Follow-up: theoretical derivation of a sigma_m confinement term
  (einstein-mind's recommendation) before further GPU testing.

- **AMBIGUOUS** (borderline): Gate 1 + Gate 3 pass but Gate 2
  intermediate. Record and require secondary test.

- **VOID** (control failed): Gate 1 fails. Dynamics have drifted from
  GPU-012 and comparison is invalid. Debug required.

## Artifact paths

- `tests/gpu/qng_hopfion_disorder_l_scan_gpu.py`
- `07_validation/audits/qng-hopfion-disorder-l-scan-v1/report.json`
- `07_validation/audits/qng-hopfion-disorder-l-scan-v1/summary.md`
- `07_validation/audits/qng-hopfion-disorder-l-scan-v1/interpretation.md`

## Pre-registration commitment

All four gates, numerical thresholds (alpha < 2.5 FAIL, alpha >= 3.0
PASS, Gate 3 spread < 0.25, Gate 4 ΔR² > 0.05), the fit domain
(r ∈ [R+5, L/2-3]), and the decision rule are fixed before execution.
No post-hoc gate adjustment. Exponential fit is cross-check only;
power-law is the primary gate.

### Risk disclosure

Ring baseline 2.37 from GPU-012 was measured with BETA_PHI=0.02 (fixed).
This pre-reg uses the Channel H bp_eff = BETA_PHI_MIN + BETA_PHI_RING*dep
(same as GPU-015/GPU-016). Gate 1 explicitly checks that control ring
still gives ~2.37 under Channel H — if Channel H shifts the exponent,
the comparison axis will be the CURRENT Gate-1 value, not the historical
2.37.

If Hopfion fails to form in the substrate (e.g. Q=1 winding is unstable
and decays to Q=0), dis(r) will look identical between q_twist=0 and
q_twist=1, which will manifest as identical alpha values AND identical
disorder amplitudes at small r. This is a detectable failure mode; the
interpretation will note it explicitly.
