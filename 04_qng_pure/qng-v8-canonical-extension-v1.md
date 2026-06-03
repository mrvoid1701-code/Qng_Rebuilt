# QNG v8: canonical extension with conjugate momenta (DER-QNG-042)

Type: `derivation`
ID: `DER-QNG-042`
Status: `candidate`
Author: `C.D Gabriel`
Date: `2026-04-18`

---

## Inputs

- [qng-hamiltonian-v7-two-field-v1.md](qng-hamiltonian-v7-two-field-v1.md) — DER-QNG-036 (v7 Hamiltonian)
- [qng-yukawa-phi-mass-v1.md](qng-yukawa-phi-mass-v1.md) — DER-QNG-041 (Yukawa phi-mass / V_couple)
- [qng-lorentz-emergent-v1.md](qng-lorentz-emergent-v1.md) — DER-QNG-043 (Lorentz emergent)
- [qng-preferred-frame-analysis-v1.md](qng-preferred-frame-analysis-v1.md) — NOTE-QNG-013 (Lorentz/frame)
- [qng-action-principle-candidate-v1.md](qng-action-principle-candidate-v1.md) — NOTE-QNG-014 (action principle)

---

## Objective

QNG v7 is a gradient-flow substrate: every channel evolves first-order in
time as `∂_t field = -δE_v7/δfield`. The only kinetic term in the known
Hamiltonian `H_v7 = T_g[chi] + E_v7` (DER-QNG-036) belongs to the
(sigma_g, chi) pair. sigma_m, phi, and in some readings chi itself are
overdamped — they have no conjugate momenta, no action principle, no
hyperbolic wave equation in their own right.

This derivation proposes the minimal structural completion: promote the
remaining fields to canonical pairs with explicit conjugate momenta and
kinetic terms, yielding `H_v8` and its associated action. The program is
labeled v8 to mark that it is the structural successor of v7, not a
modification of it.

v8 is expected to RESOLVE three documented open gaps simultaneously:

- **NOTE-QNG-013** (Lorentz covariance, "most important open structural gap")
- **NOTE-QNG-014** (absence of an action principle / Lagrangian)
- **Gap 8** (chi global instability requiring ad-hoc CHI_DECAY=0.020)

and to ENABLE a real falsification test of the baryon mass program via
the cavity-mode prediction `omega_1 = c_phi/R`.

v8 is expected to NOT resolve:

- **Gap 5** (cosmological alpha / physical value of CHI_DECAY-scale) —
  the tuning migrates from CHI_DECAY to the intrinsic frequencies of the
  new pi fields. Renamed, not eliminated.
- **Gap 9** (value of `g` in DER-QNG-041 V_couple) — explicit U(1)
  breaking remains required; Goldstone's theorem becomes STRICTER in v8,
  not weaker.

The present document commits to the structural form of H_v8 and the
five-gate falsification contract BEFORE any simulation. The companion
pre-registration is QNG-GPU-020 (to be registered).

---

## 1. Motivation — three physics-only arguments

### 1.1 Action principle requirement

Euler-Lagrange equations for a Lagrangian `L[field, ∂_t field, ∇field]`
are generically second order in time:
`∂_t(∂L/∂(∂_t field)) - ∂L/∂field = 0`.

First-order-in-time dynamics `∂_t field = F[field]` admits an action
principle only as (a) a degenerate Lagrangian with half the DOF auxiliary
(Dirac-Bergmann constrained theory), or (b) gradient flow, which is NOT
an action principle — it is a Lyapunov descent.

v7 is (b). Every channel (Update A, B, D, E, F, G) is gradient flow of
`E_v7` (DER-QNG-036 Section 3). v7 has a Lyapunov functional, not an
action.

**Conclusion**: for QNG to admit a Lagrangian, the fields must acquire
conjugate momenta. pi_phi and pi_m are logically forced the moment an
action principle is demanded. pi_chi is forced in the Option-B reading
(chi as independent DOF); in the Option-A reading, chi remains the
conjugate of sigma_g (its role in DER-QNG-036) and no additional pi_chi
is needed.

### 1.2 Lorentz covariance requirement

A hyperbolic wave equation `∂²_t phi = c² ∇² phi - V'(phi)` emerges from
`L = (1/2)(∂_t phi)² - (1/2)(∇phi)² - V(phi)` via Legendre transform with
`pi_phi = ∂_t phi`. In covariant form:
`L = -(1/2) ∂_μ phi ∂^μ phi - V(phi)`.

Gradient flow `∂_t phi = D ∇² phi - V'(phi)` cannot be Lorentz covariant:
`D` has dimensions `[L²/T]` and there is no Lorentz tensor of appropriate
rank that transforms as `D`. This is the rigorous form of NOTE-QNG-013.

**Conclusion**: pi_phi and pi_m formally resolve the Lorentz gap for phi
and sigma_m propagation, conditional on chi reaching a Lorentz-covariant
steady state (Gap 8).

### 1.3 Gap 8 structural cure

H_v7 stability requires `K_BACK*DELTA < ALPHA + CHI_DECAY*(1-ALPHA)`.
With K_BACK=0.10, DELTA=0.20, ALPHA=0.005, this forces CHI_DECAY ≥ 0.016,
chosen as 0.020 for margin. CHI_DECAY is introduced ad hoc to prevent the
Jeans-like k=0 collapse of chi.

In Hamiltonian dynamics with `H = pi_chi²/(2μ_chi) + (∇chi)²/2 + V(chi)`,
stability at k=0 is automatic whenever `V(chi)` is bounded below. Energy
conservation prevents the runaway. CHI_DECAY is then a diagnostic
fingerprint of a missing kinetic term — in gradient flow, instabilities
must be damped dissipatively; in Hamiltonian flow, they oscillate.

**Conclusion**: adding pi_chi (Option B) OR embedding chi as auxiliary
with proper constraint (Option A) is expected to retire CHI_DECAY. This
is Gate X (FC-5) of the falsification contract.

### 1.4 On the backpropagation analogy (explicit retraction)

The motivating intuition arrived via a backpropagation analogy: chi
transports "forward information," psi transports "backward correction."
This analogy is pedagogically useful and arrived at the right answer
(introduce paired fields), but it is NOT a physics derivation.

Hamilton's equations `dq/dt = +∂H/∂p`, `dp/dt = -∂H/∂q` are manifestly
time-forward for both q and p. The minus sign in `dp/dt` is NOT a
time-reversal statement. The system is time-reversal symmetric for
time-even H, and p evolves forward with q.

Backpropagation is a time-reversed adjoint sensitivity from optimal
control theory (Pontryagin's principle). The costate variable in
backprop runs BACKWARD from a terminal boundary condition. This is
mathematically distinct from conjugate momentum.

**The correct physics analogs of a forward/backward pair are:**
- Wheeler-Feynman absorber theory (retarded + advanced Green's functions)
- Schwinger-Keldysh contour (closed-time-path formalism)
- Hamiltonian canonical pair (q, p): both evolve forward together

Adopt the Hamiltonian reading for DER-QNG-042. The backprop metaphor
must not appear as load-bearing motivation in formal documents.

---

## 2. Structure: H_v8 and canonical pairs

### 2.1 Minimal form (Option A, recommended by Tesla-mind synthesis)

Keep chi as the conjugate of sigma_g (existing T_g[chi] in DER-QNG-036).
Promote only sigma_m and phi to canonical pairs:

```
(sigma_g, chi)       — existing, T_g[chi] retained
(sigma_m, pi_m)      — NEW
(phi, pi_phi)        — NEW
```

Three canonical pairs. chi remains dynamical but does not have its own
separate pi_chi.

### 2.2 Alternative form (Option B)

Promote chi to its own pair with pi_chi:

```
(sigma_g, chi_conj)  — redefine chi_conj as conjugate of sigma_g
(chi, pi_chi)        — NEW, chi becomes independent DOF
(sigma_m, pi_m)      — NEW
(phi, pi_phi)        — NEW
```

Four canonical pairs. More DOFs; cleaner symmetry (each field has
exactly one canonical partner). Closer to user's original intuition
(chi forward, pi_chi backward).

**Recommendation**: start with Option A. It is the minimal completion.
Option B can be adopted later if Option A proves insufficient for any
specific gap.

### 2.3 Hamiltonian (Option A explicit form)

> **[AMENDED 2026-04-20 by DER-QNG-042-A1]** The `V_couple` form shown
> in this section (`g * Σ sigma_g * (1 - cos phi)`) is the DER-QNG-041
> original; it is SUPERSEDED. The operative coupling is Option E^2:
> `V_couple_E2 = (g/2) * Σ (sigma_m_ref - sigma_m_i)² * (1 - cos phi_i)`.
> The original form drained sigma_g monotonically in any phi-winding
> sector, breaching the v8 effective-theory boundary. Option E^2
> eliminates the drain, has phi massless in vacuum and massive in ring
> cores (Jackiw-Rebbi correspondence), and is the form used by the
> canonical integrator. See `qng-v8-option-e2-amendment-v1.md` for the
> full derivation and empirical confirmation. Section 2.3 below is
> retained for historical completeness only — read §2.4 and later with
> V_couple replaced by V_couple_E2.

```
H_v8 = T_g[chi] + T_m[pi_m] + T_phi[pi_phi] + E_v7 + V_couple
```

where:

- `T_g[chi] = (k_back / 2) * Σ_i chi_i²`  (existing, DER-QNG-036)
- `T_m[pi_m] = (1 / (2*μ_m)) * Σ_i pi_m_i²`  (NEW)
- `T_phi[pi_phi] = (1 / (2*μ_phi)) * Σ_i pi_phi_i²`  (NEW)
- `E_v7` = potential energy of v7 (unchanged)
- `V_couple = g * Σ_i sigma_g_i * (1 - cos phi_i)`  (DER-QNG-041 ORIGINAL —
  **SUPERSEDED by DER-QNG-042-A1 Option E^2**; see notice above)

`μ_m` and `μ_phi` are inertia parameters. They are the NEW free parameters
of v8 and the central object of the Gap-5-renamed scale problem (see
Section 7).

### 2.4 Equations of motion (Option A, symplectic Euler form)

For sigma_m:
```
sigma_m_i(t+1) = sigma_m_i(t) + (Δt / μ_m) * pi_m_i(t)
pi_m_i(t+1) = pi_m_i(t) - Δt * (δE_v7/δsigma_m_i) - Δt * (δV_couple/δsigma_m_i)
```

For phi:
```
phi_i(t+1) = phi_i(t) + (Δt / μ_phi) * pi_phi_i(t)
pi_phi_i(t+1) = pi_phi_i(t) - Δt * (δE_v7/δphi_i) - Δt * (δV_couple/δphi_i)
```

For (sigma_g, chi): unchanged from v7 (Channels G, A remain).

`V_couple` contributions:
- `δV_couple / δsigma_g_i = g * (1 - cos phi_i)` (already in v7-with-DER-QNG-041)
- `δV_couple / δphi_i = g * sigma_g_i * sin phi_i`

Note `δV_couple / δsigma_m_i = 0` — V_couple is carrier-sigma_g-only
(DER-QNG-041 Section 3).

### 2.5 Overdamped limit reduces to v7

Taking `μ_m → ∞` at fixed damping, or adding explicit friction
`-γ_m * pi_m` with large γ_m, the pi_m equation becomes quasi-static:
`pi_m ≈ -(1/γ_m) * (δE_v7/δsigma_m)`. Substituting into the sigma_m
equation: `∂_t sigma_m = -(1/(μ_m γ_m)) * δE_v7/δsigma_m`, which is
v7 gradient flow with effective rate `1/(μ_m γ_m)`.

**Consequence**: v8 CONTAINS v7 as an overdamped limit. All PASS results
of v7 (CPU-043, CPU-073/074/075, etc.) are recovered in this limit.
This is Gate FC-4 (recovery test) of the falsification contract.

---

## 3. Analytical prerequisites (MUST complete before any simulation)

Per the Savant integrity contract (deepened after GPU-009..018 failure
pattern), no GPU simulation is to be scheduled until the following five
analytical tasks are complete.

### 3.1 Forms of T_m, T_phi committed explicitly

- `T_m[pi_m] = (1/(2μ_m)) * Σ_i pi_m_i²` — standard kinetic
- `T_phi[pi_phi] = (1/(2μ_phi)) * Σ_i pi_phi_i²` — standard kinetic

No non-standard structure (e.g., `(sin pi_phi)²`) is admitted. If analysis
later requires a non-standard form, that becomes a distinct DER-QNG-043
proposal, not a mid-course correction to DER-QNG-042.

### 3.2 H_v8 bounded below — analytical proof

Required bounds:

(a) `E_v7 + V_couple` is bounded below — verify by:
    - Inspection of each term in E_v7 (Channel A quadratic, Channel B
      Laplacian-like, Channels D, E, F, G)
    - `V_couple = g*sigma_g*(1-cos phi) ≥ 0` since `sigma_g ≥ 0` and
      `1 - cos phi ≥ 0`

(b) `T_m[pi_m] ≥ 0` and `T_phi[pi_phi] ≥ 0` by construction

(c) `T_g[chi] = (k_back/2) Σ chi_i²` ≥ 0 by construction

Risk to check: does `sigma_g → 0` anywhere allow `E_v7 → -∞`? Channel G
produces `-k_back * sigma_g * chi` which is unbounded if `sigma_g ≥ 0`
is not maintained. Verify sigma_g positivity is preserved by the symplectic
update.

### 3.3 Unique wave speed constraint (Lorentz consistency)

**CORRECTION (2026-04-18, post 3-agent review)**: the formulas in
the original draft of this section were dimensionally inconsistent.
The correct derivations are in the prerequisites document
`qng-v8-analytical-prereqs-v1.md` §3.3 and are summarized here.

The three sectors (sigma_g, sigma_m, phi) generate wave speeds from
their kinetic and potential couplings. Correct derivations from
linearized canonical EOMs with z=6 cubic Laplacian averaging:

- `c_g²   = k_back · β_g / 6`             (DER-QNG-036, v7 retained)
- `c_m²   = β_m / (6 · μ_m)`              (from E_v7 Channel B_m linearization)
- `c_phi² = β_phi · σ_m_ref² / (3 · μ_phi)` (from E_φ linearization with
            double-counting and z=6 averaging)

For Lorentz covariance `c_g = c_m = c_phi`, μ_m and μ_phi are determined:

```
μ_m   = β_m / (k_back · β_g)
μ_phi = 2 · β_phi · σ_m_ref² / (k_back · β_g)
```

**Numerical values at v7 baseline** (β_m = β_g = 0.35, k_back = 0.10,
σ_m_ref = 0.5, β_φ = 0.06 Choice A):

```
c_g = c_m = c_φ ≈ 0.0764 lu/step
μ_m    = 10.0
μ_phi  = 0.857
```

Both positive and finite.

**Claim** (restated correctly): μ_m and μ_phi are NOT new free parameters —
they are determined by the requirement of a single light-cone AT LINEAR
ORDER. Full emergent Lorentz covariance requires additional conditions
(weak σ_m dependence of c_φ, rotational isotropy of dispersion, χ-σ_g
higher-order corrections small) that are EMPIRICALLY tested by GPU-020
Stage A, not derived a priori.

**Prior (wrong) formulas** — kept here for reference as RETRACTED:
~~`c_m² = (β_m · σ_g_ref²) / μ_m`~~ (had σ_g_ref² with no justification)
~~`c_phi² = (β_phi · σ_m_ref²) / μ_phi`~~ (missing 1/3 from z=6 averaging)
These gave μ_m = 15, μ_phi = 2.57 — factors 1.5× and 3× off.

See `qng-v8-analytical-prereqs-v1.md` §3.3 for the full algebraic
derivation.

### 3.4 Goldstone mode count

Identify every continuous symmetry of `H_v8`:

- `phi → phi + 2π/n` for integer n: discrete (already Z_N, no Goldstone)
- `phi → phi + c` (generic c): BROKEN by V_couple (1-cos phi is not
  invariant for generic c); Z_1 remnant only. Goldstone gapped by V_couple.
- Spatial translations: broken by lattice; no Goldstone.
- sigma_m amplitude: continuous, unbroken → potentially gives a Goldstone
  mode. Must check whether E_v7 pins sigma_m to sigma_m_ref (via relational
  smoothing, Channel B analog for m-sector).

**Required**: enumerate, confirm that V_couple alone gaps the phi
Goldstone, and that no new unbroken continuous symmetry appears from the
kinetic terms.

### 3.5 Topological sector analysis

Ring with phi winding number W=1 carries a topological charge. In v7
(dissipative), rings can annihilate via energy relaxation. In v8
(canonical with V_couple), the energy barrier between W=1 and W=0 is
finite but the symplectic flow does not automatically dissipate across
topological sectors.

**Risk**: ring trapped permanently in W=1 sector even if the ground state
is W=0. Mass measurement protocol may then not reflect ground-state
energy.

**Required**: compute energy barrier between W=0 and W=1 sectors;
document whether this is a feature (stable particle) or a bug (corrupted
measurement).

---

## 4. Testable predictions (gates P1–P4)

### P1 — phi dispersion relation is massive

**CORRECTED (2026-04-18)**: original draft used m_phi² = g·σ_g_ref,
omitting the 1/μ_phi factor from the canonical EOM. Correct formula:

```
omega²(k) = c_phi² · k² + m_phi²    with    m_phi² = g · σ_g_ref / μ_phi
```

**Measurable**: excite phi at k=0 (uniform plane wave), measure oscillation
frequency. If `omega(k=0) = m_phi` as predicted, PASS. If `omega(k=0) = 0`
(massless), FAIL — V_couple is not doing what theory requires, or pi_phi
implementation wrong.

At `g = 0.22, σ_g_ref = 0.5, μ_phi = 0.857`:
- `m_phi² = 0.22 · 0.5 / 0.857 = 0.1284`
- `m_phi ≈ 0.359 lu⁻¹`
- `T_phi = 2π / m_phi ≈ 17.5 lu`

Prior (retracted) prediction: ~~`m_phi ≈ 0.332, T ≈ 19 lu`~~.

### P2 — sigma_m inter-ring force has a sigma_m-mediated component

In v7, inter-ring force is dominated by sigma_g potential (DER-QNG-050
showed Lennard-Jones-like profile). In v8 with T_m[pi_m], there is a
sigma_m sound speed c_m and a direct sigma_m-mediated interaction.

**Measurable**: force F(d) between rings in v7 vs v8 at matched parameters.
If v8 shows a new short-range component with range `1/m_m` (sigma_m
Compton wavelength), PASS. If v8 matches v7 force profile exactly,
T_m[pi_m] is not doing physical work.

### P3 — ring in a gravitational well accelerates (F=ma, not terminal velocity)

v7 result (CPU-073): ring in a sigma_g gravitational well drifts at
TERMINAL velocity (overdamped).

v8 prediction: same ring shows FREE-FALL acceleration. Ring position
`x(t)` satisfies `ẍ = -∇Φ_g` (Newton's second law) instead of
`ẋ = -k * ∇Φ_g` (terminal velocity).

**Measurable**: ring trajectory `x(t)` in v8 test at identical geometry
to CPU-073. Fit `x(t)`: if linear in t (constant velocity), FAIL
(v8 is dissipatively equivalent to v7). If quadratic in t (acceleration),
PASS.

### P4 — CHI_DECAY can be set to zero

v7 stability requires CHI_DECAY ≥ 0.016 (DER-QNG-034).

v8 prediction: with pi-kinetic terms present, the k=0 Jeans mode is
stabilized by energy conservation. CHI_DECAY=0 should give a stable
simulation for T ≥ 5000 steps.

**Measurable**: v8 simulation with K_BACK=0.10, DELTA=0.20, CHI_DECAY=0,
T=5000. PASS if chi remains bounded. FAIL if sigma_g collapses globally
(Jeans recurrence).

---

## 5. Hard falsification: cavity-mode mass(R) vs CPU-074/075

This is the single most decisive prediction of v8.

### 5.1 Cavity-mode argument (Tesla-mind synthesis)

A vortex ring of radius R with phi winding number W=1 is a toroidal
cavity for phi. In v8 with pi_phi, phi supports waves of speed c_phi.
The circumferential standing modes satisfy `k_n * 2π R = 2π n`, so
`k_n = n/R` and `omega_n = c_phi * n/R`.

Fundamental mode: `omega_1 = c_phi / R`.

If this fundamental frequency IS the rest-mass of the ring particle
(ℏ=1 units), then:

```
m_particle(R) = c_phi / R       [v8 cavity-mode prediction]
```

i.e., **mass DECREASES with R as 1/R**.

### 5.2 CPU-074/075 observation

Canonical M_ring measurements at T_P2=1000:

```
R=3: M = 474.15
R=4: M = 728.92
R=5: M = 954.88
```

M INCREASES with R (approximately linearly, consistent with
"mass ∝ ring circumference × cross-section").

### 5.3 Verdict possibilities

**Verdict A (HARDEST FALSIFICATION)**: If v8 simulation shows cavity mode
at `omega_1 = c_phi/R` and that IS the physical mass, then v8 contradicts
the observed R-scaling of M_ring by a factor of R² or more. v8 is dead
in its current form; either pi_phi is wrong, or R-identification (R=4 ↔
nucleon) is wrong.

**Verdict B (RECONCILIATION — most likely)**: Ring mass is NOT omega_1
alone. It is (volume deficit) × omega_1 = (sigma_m depletion integral) ×
(c_phi / R). The volume deficit scales as R^a (ring cross-sectional area
× circumference ≈ R); the cavity mode as R^-1. Product scales as R^(a-1).
If a = 2 (volume deficit ∝ R²), mass ∝ R, which matches CPU-074/075.
Reconciliation preserves v8 AND the mass ladder — but requires
reinterpretation of "mass observable" as the product.

**Verdict C (v8 PASSES at unchanged interpretation)**: Cavity mode does
NOT appear at `omega_1 = c_phi/R`; some other mechanism generates mass.
v8 is structurally OK but Tesla's cavity prediction is wrong.

**Decision rule (pre-committed)**: Run v8 simulation with V_couple at
g=0.22 (DER-QNG-041 best candidate). Measure (1) phi oscillation spectrum
near ring, (2) sigma_m depletion integral. Compare mass(R) in both
interpretations. If neither matches CPU-074/075 R-scaling within 20%,
v8 + current interpretation is falsified.

---

## 6. Dangers catalogued (Savant pre-flight)

### D1 — Liouville drift (no dissipation of numerical error)

Symplectic flow preserves phase-space volume (Liouville's theorem). Any
numerical error in (sigma_m, pi_m) or (phi, pi_phi) does NOT decay — it
persists and accumulates. In v7 (gradient flow), errors damp within a
few steps.

**Mitigation**: use symplectic integrator (leapfrog at minimum, Yoshida
4th-order preferred). Standard Euler-forward is not acceptable.

### D2 — Unbounded Hamiltonian risk

If any term in E_v7 + V_couple allows `sigma_g → 0` while producing
finite energy gain elsewhere, H_v8 can go to -∞. Must verify sigma_g
positivity invariant is preserved.

### D3 — Topological trapping

Ring with W=1 cannot decay to W=0 via symplectic flow alone. Mass
measurement of excited topological sector differs from ground state.
Must separate topological mass from quantum-number-0 sector contribution.

### D4 — Gap 5 renamed, not resolved

μ_m, μ_phi, c_phi are all parameters with cosmological-scale implications.
CHI_DECAY → omega_0_pi_phi = m_phi. Gap 5 tuning moves to the mass scale
of pi_phi. Acknowledge explicitly; do not claim v8 resolves Gap 5.

### D5 — Goldstone made worse (Savant primary critique)

Without V_couple, v8 phi is EXACTLY massless by Goldstone's theorem
(theorem applies strictly in Lorentz-invariant theories). v8 without
V_couple is FALSIFIED by P1: omega(k=0) = 0. Thus V_couple is mandatory
in v8. g in V_couple remains Gap 9. The canonical extension does not
close Gap 9.

---

## 7. Open problems PERSISTING in v8

1. **Gap 5** (cosmological α): unchanged, renamed. Now the tuning of
   μ_m and μ_phi to yield observable cosmological scales.

2. **Gap 9** (value of g in V_couple): unchanged. Still required as
   explicit breaking; still labeled EFT.

3. **Chi as dynamical vs auxiliary**: Option A treats chi as dynamical
   partner of sigma_g (v7 retained). Option B promotes chi to its own
   pair. This is a physical choice that cannot be derived; it must be
   committed by first-principles ontological analysis. DER-QNG-042
   commits to Option A; if tests fail, Option B can be a successor DER.

4. **Standard Model embedding**: gauge symmetry (U(1)_EM, SU(2)_L, SU(3)_C)
   is not addressed in v8. v8 provides the substrate for particle masses;
   does NOT derive mixing matrices, generation number, or gauge group.

---

## 8. Falsification contract (FC-1 to FC-5)

Pre-commit before ANY simulation:

**FC-1 (form commitment)**: T_m = (1/(2μ_m))Σpi_m², T_phi = (1/(2μ_phi))Σpi_phi².
Standard kinetic. No post-hoc modification. Any change becomes DER-QNG-043.

**FC-2 (EOM commitment)**: symplectic Euler / leapfrog integrator.
All friction terms named explicitly and flagged as Langevin additions,
not canonical.

**FC-3 (boundedness proof)**: H_v8 bounded below verified analytically
BEFORE any GPU run. If sigma_g positivity fails, the run is aborted.

**FC-4 (recovery gate)**: v8 with large Langevin damping on pi_m and
pi_phi must reproduce v7 ring morphology (CPU-043, CPU-073) within 5% at
L=20, T=500. Failure means v8 is not a generalization of v7 but a
different theory. Reject.

**FC-5 (mass verdict)**: At g=0.22, measure m_phi² from phi dispersion
(P1) AND mass(R) from both cavity-mode and volume-deficit
interpretations. Pre-commit decision rule:
- If neither interpretation matches CPU-074/075 R-scaling within 20%:
  v8 with current field content is FALSIFIED.
- If only volume-deficit × omega_1 matches: Verdict B reconciliation.
  Accept; reinterpret mass observable.
- If only cavity-mode matches: DER-QNG-038 mass ladder must be
  reinterpreted (R identification wrong).
- If both match: rare but possible; v8 fully corroborated.

---

## 9. Expected outcomes (Claude estimation)

Realistic scenario distribution:

- **Verdict A (hard fail)**: 30% — cavity prediction and volume-deficit
  both miss CPU-074/075. Indicates deep structural problem; may warrant
  abandoning the substrate.
- **Verdict B (reconciliation)**: 55% — v8 structurally sound, mass
  observable reinterpreted as product. Continues program at v8 baseline.
- **Verdict C (partial)**: 15% — v8 passes but cavity wrong; alternative
  mass mechanism needed; keep probing.

Verdicts A and B together cover 85% — this run WILL decide the fate of
the substrate-ontology approach.

---

## 10. References

### Upstream

- `04_qng_pure/qng-native-derivation-program-v1.md` §E (v8 anticipation)
- `04_qng_pure/qng-hamiltonian-v7-v1.md` (DER-QNG-036 — H_v7 = T_g[chi] + E_v7)
- `04_qng_pure/qng-note-lorentz-v1.md` (NOTE-QNG-013)
- `04_qng_pure/qng-note-action-v1.md` (NOTE-QNG-014)
- `04_qng_pure/qng-gap8-stability-analysis-v1.md` (DER-QNG-034)
- `04_qng_pure/qng-yukawa-phi-mass-v1.md` (DER-QNG-041)
- `04_qng_pure/qng-particle-mass-identification-v1.md` (DER-QNG-038)

### Three-agent synthesis (2026-04-18)

- `.claude/agent-memory/tesla-mind/psi-conjugate-field-v8.md`
  (resonance, cavity mode, μ derivation, Occam debt warnings)
- `.claude/agent-memory/einstein-mind/psi-conjugate-field-v8.md`
  (action principle necessity, Lorentz emergence, Goldstone paradox
   resolution via GMOR, backprop metaphor critique)
- `.claude/agent-memory/savant-physics-reviewer/psi-conjugate-field-v8-critique.md`
  (rigor audit, FC-1-5 contract, 7 red flags, Gap 5 renaming)

### Downstream

- `07_validation/prereg/QNG-GPU-020.md` (to be written — v8 recovery +
  cavity-mode test) — blocker for any GPU run on v8

### Test-observable correspondence

| Prediction | Test | Pass condition |
|---|---|---|
| P1 phi dispersion | GPU-020 Stage A | omega(k=0) = m_phi ± 10% |
| P2 pi_m-mediated force | GPU-020 Stage B | new force component at range 1/m_m |
| P3 F=ma drift | GPU-020 Stage C | x(t) quadratic, not linear |
| P4 CHI_DECAY=0 | GPU-020 Stage D | stable at T=5000 |
| FC-5 mass ladder | GPU-020 Stage E | verdict A/B/C per rule |

---

## Status

`candidate`. Promoted to `locked` only after GPU-020 Verdict B or C.
Promoted to `falsified_structural` under Verdict A.

All parameter values in this document (μ_m, μ_phi, g) are pre-registered
EFT parameters or derived from c_g. No simulation output may be used to
retune these values within the v8 program. Such retuning becomes a
separate DER-QNG-043 proposal.
