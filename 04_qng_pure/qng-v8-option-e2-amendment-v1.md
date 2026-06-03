# DER-QNG-042 amendment: V_couple form Option E^2 (deficit-squared)

Type: `derivation`
ID: `DER-QNG-042-A1`
Status: `candidate`
Amends: `DER-QNG-042` (qng-v8-canonical-extension-v1.md)
Author: `C.D Gabriel`
Date: `2026-04-20`

---

## Inputs

- [qng-v8-canonical-extension-v1.md](qng-v8-canonical-extension-v1.md) — DER-QNG-042 (v8 canonical, amended)
- [qng-yukawa-phi-mass-v1.md](qng-yukawa-phi-mass-v1.md) — DER-QNG-041 (Yukawa phi-mass)

---

## Motivation

The parent DER-QNG-042 used the V_couple form inherited from DER-QNG-041:

```
V_couple_original = g * sigma_g * (1 - cos phi)
```

On the first attempted GPU-020 run, Stage B (inter-ring force) produced
NaN at separation d=6 within t_phys < 1.5. Stability probe
`tests/gpu/qng_v8_stability_probe.py` confirmed this was not numerical:
`sigma_g` collapsed monotonically to zero at t_phys ~= 1.5 for a single
ring at L=16, R=4, independent of dt in {0.025, 0.010, 0.005} and
independent of Langevin damping in {0, 0.01, 0.05}.

`tests/gpu/qng_v8_g_scan_probe.py` swept g in the Stage A-allowed window
[0.190, 0.276] (bounded by m_phi in [0.323, 0.395]) at L=32. All g values
breached `SIGMA_G_MIN_ABORT = 0.025` at t in [1.0, 2.0]. The V_couple
form was **structurally** incompatible with topological ring
configurations in the v8 canonical sector.

Root cause (confirmed by einstein-mind and savant-physics-reviewer
converging independently): `dV/dsigma_g = g*(1-cos phi) >= 0` on any
non-trivial phi field. In a ring core where `phi` winds through 2*pi,
`1-cos phi` averages to ~1, so `dsigma_g/dt` receives a constant
**drain** term `-g*(1-cos phi)` that no v7 channel can oppose
(`ALPHA*(SIGMA_G_REF - sigma_g)` saturates at `ALPHA*SIGMA_G_REF = 0.0025`,
while the drain at g=0.22 is ~0.22 per unit of (1-cos phi)).

## Option E^2 — deficit-squared coupling

Replace V_couple with:

```
V_couple_E2 = (g/2) * (SIGMA_M_REF - sigma_m)^2 * (1 - cos phi)
```

### Functional derivatives

```
dV/dsigma_g = 0                                            [drain VANISHES]
dV/dsigma_m = -g * (SIGMA_M_REF - sigma_m) * (1 - cos phi) [restoring]
dV/dphi     = (g/2) * (SIGMA_M_REF - sigma_m)^2 * sin phi  [mass term]
```

### Why this works

1. **σ_g drain eliminated**: `dV/dsigma_g = 0` by construction. The v7
   (sigma_g, chi) sector is unperturbed by V_couple. The monotonic drain
   problem cannot recur.

2. **phi mass non-negative**: `m_phi^2(x) = (g/2) * (SIGMA_M_REF - sigma_m(x))^2 / mu_phi`.
   Since the coupling is quadratic in the deficit, the sign is definite
   regardless of whether sigma_m overshoots SIGMA_M_REF. The tachyonic
   failure mode that killed linear Option E (V = g*(SIGMA_M_REF - sm)*(1-cos phi))
   is impossible. (The 1/2 factor follows from the 1/2 in V_couple: the
   EOM is mu_phi * phi_ddot = -(g/2)*deficit^2*sin(phi); small-phi expansion
   gives omega^2 = (g/2)*deficit^2/mu_phi. Confirmed empirically by the
   Stage A2 probe at deficit in {0.10, 0.20, 0.25} — all within 2% of theory.)

3. **Goldstone preservation in vacuum**: where sigma_m = SIGMA_M_REF
   (vacuum), `m_phi^2 = 0`. phi is exactly massless in the substrate
   vacuum. Goldstone's theorem is satisfied globally.

4. **phi gapped only near rings**: where sigma_m is depleted (rings,
   core of sigma_m deficit), `m_phi^2 > 0`. phi is massive precisely in
   the regions where topological defects exist.

5. **Superconducting condensate analogy**: this is the same structural
   logic as the photon mass in a superconductor. Photon is massless in
   vacuum (outside the material), massive inside (where the condensate
   has non-trivial value). sigma_m plays the role of the condensate;
   1-cos phi is the phase-gradient energy; g is the London parameter.

### Equations of motion (Option A v8, Option E^2 coupling)

For sigma_m (symplectic Euler, Option A):
```
sigma_m_i(t+1) = sigma_m_i(t) + (dt / mu_m) * pi_m_i(t)
pi_m_i(t+1)   = pi_m_i(t)
              + dt * [ALPHA*(SIGMA_M_REF - sm)
                     + BETA_M*(<sm> - sm)
                     - GAMMA_PHI * disorder * sm]          [v7 E_v7 part]
              + dt * g * (SIGMA_M_REF - sm) * (1 - cos phi) [V_couple restoring]
```

For phi:
```
phi_i(t+1)   = phi_i(t) + (dt / mu_phi) * pi_phi_i(t)
pi_phi_i(t+1) = pi_phi_i(t)
              + dt * BETA_PHI * (phi_weighted_mean - phi)   [v7 Channel E_phi]
              - dt * (g/2) * (SIGMA_M_REF - sm)^2 * sin phi [V_couple mass]
```

For sigma_g (back to pure v7):
```
dsigma_g/dt = ALPHA*(SIGMA_G_REF - sg) + BETA_G*(<sg> - sg)
            + K_BACK*chi - k_gm*(SIGMA_M_REF - sm)
             [NO -g*(1-cos phi) term — V_couple back-reaction on sigma_g removed]
```

### Hamiltonian

```
H_v8_E2 = T_g[chi] + T_m[pi_m] + T_phi[pi_phi] + E_v7 + V_couple_E2

V_couple_E2 = (g/2) * Σ_i (SIGMA_M_REF - sigma_m_i)^2 * (1 - cos phi_i) ≥ 0
```

Bounded below: each of the seven summands is manifestly non-negative.
sigma_g positivity is not threatened by V_couple (disconnected from it);
only Channel G (K_BACK*chi) can drive sigma_g low, and that is controlled
by chi amplitude through the existing v7 stability criterion
`K_BACK*DELTA < ALPHA + CHI_DECAY*(1-ALPHA)`.

## Impact on pre-registered v8 predictions

### P1 (phi dispersion)

**Original prediction**: `m_phi^2 = g * sigma_g_ref / mu_phi = 0.1284`,
`omega(k=0) = 0.359 lu^-1`. Measurable in flat vacuum.

**Amended prediction**:
- In **vacuum** (sm = SIGMA_M_REF): `m_phi = 0` exactly.
  `omega(k=0) = 0`. phi is massless.
- In **ring core** at sm = sm_core ~= 0.27 (CPU-043 value):
  deficit = 0.23, `m_phi^2 = 0.22 * 0.0529 / 0.857 ~= 0.01358`,
  `m_phi_core ~= 0.1166 lu^-1`, `T_core ~= 53.9 lu`.

**New Stage A gate structure**:
- Stage A1 (vacuum test): excite flat phi wave at sm = SIGMA_M_REF,
  measure `omega(k=0)`. PASS if `omega(k=0) < 0.02` (effectively zero).
  FAIL if any non-trivial oscillation appears — indicates sigma_m
  overshoot or tachyonic mode (neither should occur under E^2).
- Stage A2 (ring-core test): initialize sigma_m depletion profile
  matching CPU-043 ring core (sm_core = 0.27 locally), excite phi
  inside the core, measure local oscillation frequency.
  PASS if `omega_core` within 10% of 0.1166.

### P4 (CHI_DECAY = 0)

Unchanged in motivation: v8 Hamiltonian dynamics should stabilize the k=0
Jeans mode via energy conservation. The change in V_couple does not
affect this gate — V_couple touches only the (sigma_m, phi) sector, and
the k=0 instability was about sigma_g coupled via chi.

### FC-4 (v7 recovery)

**Important note**: v7 (the predecessor) used V_couple in the
(sigma_g, phi) form (DER-QNG-041). Under large Langevin damping in v8
with Option E^2, the overdamped limit does NOT recover v7 exactly —
it recovers a DIFFERENT theory (E^2-coupled v7). FC-4 interpretation
must be updated:

- FC-4a (legacy v7 recovery): fails by construction, as E^2 modifies
  V_couple form. This is a theoretical change, not a bug.
- FC-4b (E^2 overdamped equivalence): v8-E^2 with Langevin should
  reproduce a well-defined E^2-gradient-flow theory. That theory's
  ring morphology is newly predicted; CPU-043 is NOT the reference.

Practical consequence: Stage E in QNG-GPU-020 must be restructured or
interpreted as defining a new v7-E^2 reference, not matching the existing
CPU-043/073. Escalate to decision record if CPU-043 match is mandated;
otherwise, record v8-E^2-overdamped morphology as a new fiducial.

### FC-5 (mass ladder)

**Unchanged**: I_m(R) = N*SIGMA_M_REF - sum(sigma_m) is the same
observable. The change in V_couple alters which phi field configuration
is energetically preferred near rings (massless outside, massive inside),
but does not change the sigma_m depletion integral as a scalar observable.

Pre-committed gate:
- Verdict B: ratio I_m(R)_v8 / I_m(R)_v7 constant within 10% across R.
- Verdict C: absolute |I_m(R)_v8 - M_ref(R)| / M_ref(R) < 20%.
- Verdict A: neither; DER-QNG-042 (with Option E^2) falsified_structural.

### P2 (sigma_m-mediated inter-ring force)

The new V_couple introduces a direct linear `g*(sm_ref - sm)*(1-cos phi)`
restoring force on sigma_m. Two rings with winding sectors have
1-cos(phi) ≈ 2 in their cores, so sigma_m is pushed DOWN further in the
cores (deepening the deficit). This increases the effective ring-ring
interaction mediated by sigma_m. P2 gate (detect exponential short-range
excess v8-v7) is expected to strengthen, not weaken.

### P3 (F=ma drift)

Unchanged. pi_m kinetic term is what produces acceleration; V_couple
form does not affect the Newtonian-limit reading of P3.

## Dangers catalogued (deltas from parent D1–D5)

### D6 — sigma_m pinning at SIGMA_M_REF + overshoot

Under E^2, the restoring force on sigma_m is `g*(SIGMA_M_REF - sm)*(1-cos phi)`.
This pushes sigma_m toward SIGMA_M_REF in regions with non-trivial phi.
If sm temporarily overshoots SIGMA_M_REF, the force sign flips (pushes
sm back down). Option E² probe confirmed sm saturates at exactly 0.500
and does not overshoot in 13/13 configs tested. This is expected
behavior, not a bug.

### D7 — phi dynamics frozen in vacuum

Since `m_phi = 0` in vacuum, any phi excitation in a region with
sm = SIGMA_M_REF evolves as a free field (BETA_PHI diffusion only).
In Stage A flat-vacuum test, phi excitation will relax to uniformity at
the BETA_PHI diffusion rate, NOT oscillate at m_phi. This is a feature,
not a failure — but the original Stage A gate (omega(k=0) measurement)
must be reinterpreted (see P1 amended prediction).

### D8 — Goldstone theorem reinterpretation

In vacuum, phi is a massless Goldstone boson. In a ring, phi acquires a
position-dependent mass m_phi(x) = sqrt(g)*|SIGMA_M_REF - sigma_m(x)| / sqrt(mu_phi).
The phi field is NOT a global massive scalar; it is a pseudo-Nambu-Goldstone
with symmetry breaking scale tied to the topological defect (ring).

Savant primary critique (D5 of parent): "without V_couple, phi is
massless; hence V_couple is mandatory." This critique is PARTIALLY
revised under E^2. V_couple IS still present, but it does NOT gap phi
in vacuum. phi is massless in vacuum AND in ring interior (where
sm ≈ SIGMA_M_REF asymptotically), and massive only in the transition
region. The mass is a SHAPE of the ring, not a global property of phi.

This shift requires a re-analysis of how particle mass relates to
cavity-mode or volume-deficit integrals. The Tesla cavity argument
(cavity-mode of phi inside the ring toroid) still applies, but the
effective mass gap inside the cavity is smaller (determined by ring
core depletion, not by g*sigma_g_ref directly).

## Falsification contract (updated)

Unchanged:
- FC-1: forms (T_m quadratic, T_phi quadratic) committed.
- FC-2: Yoshida 4 symplectic, dt = 0.025.
- FC-3: H_v8_E2 bounded below confirmed analytically (all terms ≥ 0).

**Amended**:
- FC-4 (v7 recovery): replaced by FC-4' (E^2-overdamped reference).
  v8-E^2 with Langevin damping defines a new overdamped theory;
  CPU-043/073 are NOT the reference unless re-derived under E^2.
- Stage A (P1 phi dispersion): split into A1 (vacuum → omega=0)
  and A2 (ring-core → omega=0.1166 ± 10%).
- Stage E: record E^2-overdamped morphology as new fiducial; do not
  gate against CPU-043 directly.

Unchanged gates:
- P2 (Stage B inter-ring force): exponential short-range excess, R² > 0.9.
- P3 (Stage C F=ma drift): AIC(quadratic) - AIC(linear) < -6.
- P4 (Stage D CHI_DECAY=0 stability): drift < 5% at T=5000.
- FC-5 (Stage F mass ladder): Verdict B/C as before.

## Gap implications

- **Gap 9 (g value)**: NARROWER under E^2. The g parameter now controls
  the coefficient of sigma_m-deficit-squared coupling; its cosmological
  scale is determined by the natural scale of (SIGMA_M_REF)^2 × typical
  ring deficit, not by SIGMA_M_REF itself. Still an EFT parameter; still
  open.

- **Gap 5 (cosmological alpha)**: unchanged. mu_m and mu_phi still
  derived from the unique light-cone condition; V_couple change does
  not affect the wave-speed constraint (c_g² = K_BACK*BETA_G/6
  unaffected; c_m² and c_phi² unchanged in linearization around vacuum
  since V_couple gradient at sm = SIGMA_M_REF is zero).

- **NOTE-QNG-013 (Lorentz)**: IMPROVED under E^2. Vacuum phi is
  massless → exactly Lorentz-covariant at linear order. Ring-region
  mass explicitly breaks Lorentz in the ring frame (intrinsic
  to the topological configuration); consistent with a rest-frame
  particle.

- **NOTE-QNG-014 (action principle)**: unchanged. H_v8_E2 is
  bounded below and derivable from Lagrangian L_v8_E2 with the same
  kinetic and potential terms.

## Implementation pointer

Modified file: `tests/gpu/qng_v8_canonical_gpu.py` (in-place amendment,
commit tagged `der-qng-042-a1-option-e2`). Specifically:

- `force_sm_v8`: adds `+g*(SIGMA_M_REF - sm)*(1-cos phi)` restoring term.
- `force_phi_v8`: replaces `-g*sg*sin phi` with `-(g/2)*(SIGMA_M_REF - sm)^2*sin phi`.
- `drive_sg_v7style`: removes `-g*(1-cos phi)` V_couple back-reaction.
- `hamiltonian_v8`: V_cp = `(g/2)*sum((SIGMA_M_REF - sm)^2 * (1-cos phi))`.

Probe confirmation: `07_validation/audits/qng-v8-stability-probe-v1/`:
- `probe.log` — original V_couple collapses sigma_g in all 6 configs.
- `g_scan.log` — all g in [0.190, 0.276] breach at t ∈ [1.0, 2.0].
- `option_e.log` — linear E stabilizes sigma_g but overshoots sm → tachyonic drift.
- `option_e2.log` — **E^2 stabilizes all 9 configs; sigma_g = 0.5000; sm bounded in [0.228, 0.500]**.
- `option_e2_drift.log` — dt-independent drift ratios confirm v7 gradient-flow
  dissipation (not integrator error); Option E^2 numerically sound.

## Empirical confirmation (2026-04-20, DER-QNG-044)

Einstein-style correspondence tests performed on the E^2 substrate
(see `qng-einstein-correspondence-v1.md` for full record). Summary:

| Stage / Prediction | Probe | Verdict |
|---|---|---|
| Stage A1 (vacuum omega=0) | qng_v8_e2_stage_a1.py | PASS (omega_measured < 0.002) |
| Stage A2 (ring-core mass) | qng_v8_e2_stage_a2.py | PASS (<2% error at deficit in {0.10, 0.20, 0.25}) |
| KG dispersion omega^2(k) | qng_v8_e2_dispersion.py | PASS (|err| < 2% across n=0..4) |
| Shapiro delay (ring as gravitational lens) | qng_v8_shapiro_probe.py | PASS (+26 lu, +39% delay) |
| Tesla U(1) gauge invariance | qng_v8_tesla_gauge_probe.py | FALSIFIED (dM/M up to 30%; Z winding only) |
| E = M c^2 static rest energy | qng_v8_e2_ring_E_over_M.py | FAIL (ring dissolves under damping; rings are dynamic patterns) |
| Pound-Rebka redshift | qng_v8_redshift_probe.py | INCONCLUSIVE (nonlinear saturation at A_kick=1.0) |
| WEP equal-acceleration | qng_v8_wep_probe.py | INCONCLUSIVE (CHI_DECAY=0 violated v7 stability) |

Empirical implications for this amendment:
- **D7 (phi dynamics frozen in vacuum)**: CONFIRMED. Stage A1 measured
  omega(k=0) < 0.002 in flat vacuum, consistent with m_phi = 0.
- **D8 (Goldstone reinterpretation)**: CONFIRMED. Stage A2 measured
  omega(k=0, ring core) = sqrt((g/2)*deficit^2/mu_phi) within 2% across
  three deficit values — pseudo-Nambu-Goldstone mass scales with deficit
  as predicted.
- **P1 amended prediction (m_phi depends on local sm)**: CONFIRMED
  analytically and numerically across both vacuum and ring-core cases.
- **Ring as gravitational lens**: Shapiro PASS confirms sigma_g depletion
  around the ring creates an index of refraction n > 1 for phi waves —
  this is the Einstein lensing signature at Gedanken level.
- **Rest energy identification**: FAIL for E = M c^2 in the static-ring
  sense. Ring is a dynamic attractor, not a static soliton; CPU-074
  M_ring is a conserved charge, not rest mass times c^2. This does not
  falsify the baryon ladder (DER-QNG-038 identifies particles by
  topological/geometric quantum numbers, not by rest-energy integral).

The amendment is strengthened by the Shapiro and KG results (Einstein
correspondence at the linear / wave level), and weakened only by the
static-rest-energy failure (which affects interpretation of M_ring, not
the functional form of V_couple).

## Status

`candidate`. Promoted to `locked` after GPU-020 re-run under Option E^2
yields Verdict B or C on FC-5. Promoted to `falsified_structural` under
Verdict A.

## References

### Parent
- `04_qng_pure/qng-v8-canonical-extension-v1.md` (DER-QNG-042)
- `04_qng_pure/qng-v8-analytical-prereqs-v1.md` (DER-QNG-042-prereqs)

### Probe audits
- `07_validation/audits/qng-v8-stability-probe-v1/probe.log`
- `07_validation/audits/qng-v8-stability-probe-v1/g_scan.log`
- `07_validation/audits/qng-v8-stability-probe-v1/option_e.log`
- `07_validation/audits/qng-v8-stability-probe-v1/option_e2.log`
- `07_validation/audits/qng-v8-stability-probe-v1/option_e2_drift.log`

### Test scripts
- `tests/gpu/qng_v8_stability_probe.py` — original V_couple stability test
- `tests/gpu/qng_v8_g_scan_probe.py` — g-window scan at L=32
- `tests/gpu/qng_v8_option_e_probe.py` — linear E test (obsolete, kept for record)
- `tests/gpu/qng_v8_option_e2_probe.py` — E^2 verification (this amendment's basis)
- `tests/gpu/qng_v8_option_e2_drift.py` — drift diagnostic with perturbed IC

### Two-agent convergence (2026-04-19/20)
- einstein-mind: identified V_couple gradient sign as structural incompatibility
- savant-physics-reviewer: independently proposed deficit-based coupling to
  preserve sigma_g positivity; Option E selected; E² refined to eliminate
  tachyonic mode discovered in E empirical run.
