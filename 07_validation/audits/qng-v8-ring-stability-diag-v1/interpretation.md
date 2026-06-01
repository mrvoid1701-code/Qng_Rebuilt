# QNG-GPU-024b ring stability diagnostic — Interpretation

Type: `note`
Status: `final`
Author: `C.D Gabriel`
Date: `2026-04-20`
Audit: `qng-v8-ring-stability-diag-v1`
Upstream: `QNG-GPU-024` (ring is metastable under Phase-2)
Companion: `qng_v8_ring_stability_diagnostic.py`, `report.json`, `run.log`

---

## 1. Pre-registered question

Which Hamiltonian term drives the Phase-2 chaos discovered in GPU-024?
Three candidates: V_couple, chi_decay, Channel F.

## 2. Results

| Config | v_couple_on | chi_decay | Channel F | drift % | max RMS % |
|--------|-------------|-----------|-----------|---------|-----------|
| A (control) | True | 0.020 | on | 702.35 | 28.53 |
| B (chi off) | True | 0.000 | on | **702.35 (identical to A)** | 28.53 |
| C (V_couple off) | False | 0.000 | on | 712.66 | 27.97 |

Pre-committed verdict: **H_INTRINSIC** (all three chaotic, trajectory B vs C differs > 10%).

## 3. Three findings

### 3.1 chi_decay has ZERO effect on sigma_m (A = B byte-identical)

Every sampled M_ring value in Config B matches Config A to machine
precision (176.85, 1418.95, 559.83, 627.29, 1133.90, 666.87).
Setting chi_decay from 0.020 to 0.000 does not perturb the ring
dynamics at all.

**Why**: `yoshida4_step` defaults to `k_gm=0.0`, so Channel G (back-reaction
sigma_g ← chi) is **off** during this probe. chi evolves in isolation
(no coupling to sigma_g) and its decay does not feed back to sigma_m.

**Implication for GPU-025**: the minimum-effort Phase-3 patch — simply
setting chi_decay=0 during T_track — would give **identical α_meas**
to the GPU-022 results. It is not a fix for the saturation question.

**Caveat**: if the bending probe uses `k_gm > 0` (needs verification),
chi_decay could matter via sigma_g coupling. But under k_gm=0 Phase-2,
chi_decay is cosmetic.

### 3.2 V_couple alters trajectory but does NOT stabilize

Config C (V_couple off) gives **different** M_ring evolution than A/B:
M_ring dips to 25.0 at t=200 lu (vs A/B staying positive), and the
oscillation structure differs. But overall drift is still 712% — same
order as A. V_couple is **not the sole chaos driver**; it shapes the
attractor but doesn't create it.

### 3.3 Channel F is the leading remaining suspect

The only Hamiltonian term NOT tested here is Channel F
(`- GAMMA_PHI * disorder * sm`, GAMMA_PHI=0.10). It is always active
in `compute_sm_force_v8` and cannot be turned off via the current
`yoshida4_step` signature without code modification.

Since:
- V_couple off does not stabilize,
- chi_decay has no effect,
- Channel F is the only untested term,

Channel F is the **leading candidate driver** of the instability.
Confirmation requires adding a `channel_f` flag to `yoshida4_step` and
re-testing (proposed: GPU-024c).

If Channel F off stabilizes the ring → Phase-3 measurement mode is
"v_couple_on=True, chi_decay=0 (or 0.020, irrelevant), channel_f=False".

If Channel F off also fails to stabilize → **the ring has no equilibrium
in any accessible v8 regime**. This would be a structural finding
about the theory, not just about the measurement protocol.

## 4. Implications

### 4.1 GPU-025 pathway narrowed

The "minimal patch" (just chi_decay=0) is **dead**. Any Phase-3-mode
measurement must:
- Expose `channel_f` flag in `yoshida4_step` (code mod)
- Run with `channel_f=False` during T_track
- Assume V_couple and chi_decay are either preserved or inconsequential

### 4.2 Ring equilibrium question sharpened

If GPU-024c (Channel F off) also chaotic → v8 does not admit a static
3D ring equilibrium under any parameter setting. This:
- Strengthens the "rings are dynamic patterns, not static solitons"
  note from DER-QNG-044
- Re-opens NOTE-QNG-014 (action principle) in a sharpened form:
  "H_v8 has kinetic ring modes but no static-ring fixed point"
- Raises the question of whether the choice of spatial dimension
  (3D cubic lattice, z=6) is structurally implicated

### 4.3 Dimension hypothesis (user question 2026-04-20)

The user raised the question: does QNG v8 have a dynamical preference
for 3+1D? The substrate ontology is dimension-agnostic (node state +
graph adjacency works in any d). If the 3D ring has no equilibrium,
this could indicate:
- (a) the ring structure needs different topology (e.g., 4D membrane)
- (b) the v8 coupling constants are tuned for a different dimension
- (c) static rings don't exist in v8; only dynamic patterns do

Queued as potential QNG-GPU-026: KG dispersion in 4D lattice (L=12,
z=8, T=100 lu) — ~15 min. Diagnostic for whether the substrate is
dimension-robust at all.

## 5. Status updates

- **Candidate 3 driver = V_couple**: **RULED OUT** (Config C still chaotic)
- **Candidate 3 driver = chi_decay**: **RULED OUT** (Config B identical to A)
- **Candidate 3 driver = Channel F**: **LEADING** (remaining term; confirmation pending GPU-024c code mod)
- **Candidate 3 driver = intrinsic (no single-term fix)**: **POSSIBLE** — if GPU-024c is also chaotic
- **NOTE-QNG-014**: reopens with sharpened question
- **Dimension dependence**: new open structural question; QNG-GPU-026 queued as diagnostic

## 6. Artifacts

- `report.json` — full M_ring(t) trajectories for 3 configs
- `run.log` — console output
- `interpretation.md` — this file

Total runtime: 9.8 min (3 × 196 s).

---

## Appendix: why A = B to machine precision

With `k_gm=0` in `yoshida4_step`, the equations of motion for sigma_m
are:

    d(sigma_m)/dt = pi_m / mu_m
    d(pi_m)/dt   = F_e_v7(sigma_m, phi) + F_couple(sigma_m, phi)

Neither depends on chi. chi evolves via:

    d(chi)/dt = ... - chi_decay * chi

but chi never enters the sigma_m / pi_m right-hand side. So any change
in chi_decay leaves the (sigma_m, phi) subsystem untouched. This
confirms in the code what DER-QNG-033 says structurally: in the
two-field substrate, chi couples to sigma_g via Channel G, and to
sigma_m only through the sigma_g intermediary. With Channel G off,
chi is a decoupled spectator.
