---
id: NOTE-QNG-018
type: note
title: Edge-stochastic program — hbar candidate in link channel (Gabriel intuition)
version: v1
date: 2026-04-22
status: open
upstream:
  - DER-QNG-042 (v8 canonical Hamiltonian)
  - DER-QNG-051 (vacuum instability, R1 pure-XY cure)
  - project_lagrangian_invariant_derived.md (L = N*beta_phi/2 XY ground)
  - project_hbar_h2_onsager_dead.md (8 node-only programs failed)
---

# NOTE-QNG-018: Edge-stochastic hbar program

## 1. Origin and motivation

All eight hbar-hunt programs (alpha, beta, gamma, delta, theta, Tesla-cavity,
Bohr-Sommerfeld, Hessian-RMT) probed NODE-level observables of the v8
canonical Hamiltonian and FAILED. The R-universal invariant L = 660 turned
out to be the classical XY ferromagnetic ground state (Gate A PASS
2026-04-22: alpha = 2.986, E_char/N = beta_phi/2 within 0.5% for
L in {24, 28}). Deterministic v8 at node level exhibits no action
quantization scale.

Gabriel (2026-04-22) proposed a structurally different source: the
EDGES of the graph, currently inert geometric relations, may carry the
missing stochasticity. When coarse-grained over many edges per unit
volume, microscopic edge noise produces a single universal action scale
by central-limit accumulation — the inverse of the sand analogy
(microscopic chaos hidden on links; macroscopic smoothness with one
emergent constant).

## 2. Ontological status of edges in v8

Current v8 primitives (from `04_qng_pure/qng-ontology-v1.md` + DER-QNG-042):

- **Node state** (active): sigma_g, sigma_m, chi, phi and conjugate
  momenta pi_m, pi_phi.
- **Edge/adjacency** (passive): z=6 cubic lattice, static, no state.
  Edges only define the neighbour set N(i) used in gradient terms and
  XY cosine pair sums.

This asymmetry is the unexplored territory: every dynamical channel
lives on nodes, so every ergodicity test probed nodes. The edge channel
has never been made dynamical.

## 3. Proposed promotion

Promote each undirected edge (i,j) from a passive geometric relation
to a stochastic transmission channel carrying a phase offset:

    cos(phi_i - phi_j)  ->  cos(phi_i - phi_j + xi_ij(t))

Where xi_ij(t) is a zero-mean stochastic variable with variance eps:

    <xi_ij(t)> = 0
    <xi_ij(t) xi_kl(t')> = eps * delta_{(ij),(kl)} * C(|t - t'|)

`eps` is the single new parameter. Two sub-models:

- **Quenched** (static disorder): xi_ij frozen at t=0. Breaks no
  symmetry, adds spatial noise, preserves H. Used as null hypothesis.
- **Dynamic** (time-fluctuating, correlation time tau_c): xi_ij
  resampled or Ornstein-Uhlenbeck. This is the genuine promotion;
  dynamic link noise is the coarse-graining candidate for hbar.

## 4. Predictions and gates

### Gate X1 — quenched null
Quenched xi_ij must leave <L> = N beta_phi/2 up to disorder-averaged
corrections scaling as eps^2. No emergent action scale.

### Gate X2 — dynamic response
Dynamic xi_ij with correlation tau_c shifts <L>; the shift should obey
an FDT-like relation

    Delta L = A * eps * tau_c / dt_int

where A is geometry-dependent. If linear in eps, no hbar (just extra
noise). If <L> develops STEPS or saturates at a universal scale
independent of (eps, tau_c) in some domain, that scale is the hbar
candidate.

### Gate X3 — coarse-graining universality
Scan L in {10, 16, 24}. Measure the emergent scale (if any) as
function of N, z, eps. hbar candidate requires the emergent scale to
be intensive (independent of N) OR to scale with volume in a way that
defines a universal density.

### Gate X4 — dispersion signature
Measure phi dispersion omega(k) with edge noise on. Quenched noise
broadens peaks. Dynamic noise at the ergodic limit should produce a
noise floor; Planck-scale action would appear as a minimum-action
floor in the spectrum, not in <L> directly.

## 5. Relation to prior programs

- Distinct from v9 Langevin (Xi_chi): v9 adds noise on NODE state chi.
  Current program adds noise on EDGE coupling, which is a new primitive
  channel rather than an extra force term on an existing variable.
  Gabriel refused v9 on aesthetic grounds 2026-04-22; edge stochastic
  is a promotion, not a bolt-on.
- Connects to LQG spin networks (edges carry quanta) and CDT
  (edge/triangulation dynamics) without adopting their formalism.
- Does not supersede DER-QNG-051 XY cure; edge noise modifies the XY
  cosine form, not the Hamiltonian structure.

## 6. Immediate work

- **QNG-CPU-092**: `tests/cpu/qng_edge_stochastic_probe.py`
  - L = 8 and L = 10, z = 6, no ring, pure vacuum.
  - Scan eps in {0, 0.01, 0.05, 0.1, 0.3, 1.0}.
  - Quenched and dynamic (tau_c = 1, 10, 100 dt).
  - Measure <L>, Var(phi_i), autocorr(L, t), edge-averaged cos
    <cos(phi_i - phi_j + xi_ij)>.
  - Gates X1 (quenched null), X2 (dynamic response form).
- If any signature of quantized action appears, promote to GPU probe
  on L = 24 with ring for R-scan universality test.
- If X1 passes and X2 shows only linear shift, edge-stochastic
  program falsifies at node-level observables; next escalation is
  edge internal state (phase + amplitude) instead of scalar xi.

## 7. Success criterion

An hbar candidate survives only if:
1. Gate X2 reveals a scale INDEPENDENT of (eps, tau_c) inside a
   physical domain.
2. That scale is R-universal (like <L>).
3. That scale appears as a MINIMUM quantum of action in phi dispersion
   or action spectrum, not just a shift in mean quantities.

Failure of all three ends the hbar-hunt inside v8 canonical; only then
does v9 Langevin become justified as the residual structural option.

## 8. Status

Opened 2026-04-22 by Gabriel intuition. CPU-092, CPU-093, CPU-094
all executed same day. Scalar i.i.d. edge noise family CLOSED.

### CPU-092 result (2026-04-22)

Scalar Gaussian xi_ij probed on L in {8, 10}, eps in {0.01..1.0}, both
quenched and dynamic modes, 2 seeds each, Yoshida4.

- **X1 quenched**: |shift|/<L>_0 = 0.28 * eps^1.89 -> **PASS** (eps^2
  confirms disorder preserves H at O(eps^2)).
- **X2 dynamic**: |shift|/<L>_0 = 0.50 * eps^1.96 -> matches
  **Debye-Waller** prediction <cos(d phi + xi)> = <cos(d phi)> *
  exp(-eps^2/2) exactly (p=2, rel_A=0.5). Effective coupling
  beta_eff = beta_phi * exp(-eps^2/2).
- **X3 intensivity**: rel_A(L=10)/rel_A(L=8) = 0.98 (quenched), 0.86
  (dynamic) -> intensive but intensive of a thermal effect.

**Verdict: scalar edge noise is classical thermal bond disorder.**
Quadratic response = Debye-Waller signature. No universal action
scale; no hbar emergence. The simplest realization of the
edge-stochastic hypothesis is falsified.

**Gabriel intuition NOT dead** — only its scalar-Gaussian embodiment.
The coarse-graining-CLT reasoning in §1 is correct: many edges x
i.i.d. noise => universal scale. The falsification tells us the noise
is not scalar — edges need **internal dynamical state** to carry a
quantized action scale.

### CPU-093 result (2026-04-22) — non-Gaussian distributions

Extended to Laplace and (clipped) Cauchy xi_ij at L=8 dynamic:

- **Laplace dynamic**: A = 0.520, p = 2.020 -> IDENTICAL to Gaussian.
- **Cauchy (clipped to +-10 gamma)**: A = 3.034, p = 1.748. Pure Cauchy
  destabilizes Yoshida4 (H_drift 86% at gamma=0.3) -> infinite variance
  incompatible with symplectic classical dynamics. The "p=1 linear-in-scale"
  theoretical prediction cannot be tested in a conservative integrator,
  which itself argues against Cauchy as a physical noise source.

Distribution shape irrelevant: every finite-variance distribution gives
Debye-Waller universal law.

### CPU-094 result (2026-04-22) — discrete/sparse distributions

Five families at L=8 dynamic mode, matched rms:

| distribution | A | p |
|---|---|---|
| Gaussian | 0.538 | 2.028 |
| Uniform | 0.551 | 2.040 |
| Z_6 discrete | 0.550 | 2.038 |
| Bernoulli-Gauss p=0.1 | 0.390 | 1.918 |
| Bernoulli-Gauss p=0.01 | 0.057 | 1.265 (plateau) |

**Z_6 behaves IDENTICALLY to Gaussian** at matched variance — discrete
phase set provides no structural gain over continuous. Bernoulli
deviations are trivial percolation effects (fraction-perturbed < 1), not
quantization.

### Unified closure statement (CPU-092 + CPU-093 + CPU-094)

For ANY zero-mean i.i.d. scalar edge noise xi_ij with characteristic
function phi_xi, the leading response is

    |Delta <L>| / <L>_0 = (Var_eff / 2) * f_perturbed

where Var_eff is the realized per-edge variance and f_perturbed is the
fraction of edges with non-zero kicks per step. Derivation:

    <cos(dphi + xi)> = <cos(dphi)> * Re[phi_xi(1)]
    phi_xi(t) ~ 1 - Var(xi) * t^2 / 2  near t = 0

so every finite-variance distribution produces the SAME universal
leading O(Var) shift. This is the central-limit theorem acting on the
coupling: the universal scale CLT delivers is Var(xi) itself, which is
a tunable parameter, not a constant independent of the noise amplitude.

**Why Gabriel's CLT intuition is structurally false in this form:**
a true hbar is a universal scale independent of ALL tunable
microscopic amplitudes. Scalar i.i.d. edges give a universal FORM
(Debye-Waller) but not a universal VALUE. The family cannot source hbar.

### Escalation path (Program 9-gauge)

Next promotion: xi_ij -> U_ij in U(1), compact phase with conjugate
momentum pi_ij, evolving under its own Hamiltonian:

    H_edge = sum_edges [pi_ij^2 / (2 mu_U) + V(U_ij)]
    coupling: cos(phi_i - phi_j) -> Re[U_ij^* exp(i(phi_i - phi_j))]

This is lattice-gauge structure (Kogut-Susskind) embedded inside
QNG edges. It promotes the adjacency from passive geometry to a
full gauge field, restoring the mechanism by which lattice gauge
theories carry action quanta. The compact U(1) naturally introduces
discrete flux sectors (topological quanta on closed loops), which
ARE action scales — the natural home of hbar in a lattice theory.

Design ticket (next session): NOTE-QNG-019 + QNG-CPU-093 pre-reg.

### Relation to prior falsifications

Including CPU-092 through CPU-094, the scalar i.i.d. edge-noise
family (seven distributions tested: Gaussian, Laplace, clipped
Cauchy, Uniform, Z_6, Bernoulli-Gauss x 2) is CLOSED. This adds a
tenth program to the hbar-hunt tally (alpha, beta, gamma, delta,
theta, Tesla-cavity, Bohr-Sommerfeld, Hessian-RMT, edge-scalar-
Gaussian, edge-scalar-discrete/non-Gaussian). Option (b) as a simple
extension is now EXHAUSTED for scalar edge variables.

Residual structural moves:
- (a) **Dynamical edge gauge variables** (Program 9-gauge): edge
  carries conjugate pair (U_ij, pi_ij) with its own Hamiltonian.
  Preserves emergence-from-ontology aesthetic. Independent review
  (3/4 agents 2026-04-22) warns this IMPORTS hbar via the commutator
  [E_ij, U_ij] = U_ij rather than DERIVING it — needs audit.
- (b') **Correlated (non-i.i.d.) edge noise**: spatial or temporal
  correlations beyond the autocorrelation time already probed. May
  restore a structural ingredient missing from i.i.d.
- (c) Accept v8 is classical; impose external canonical quantization
  of H_v8 (path integral), not emergence. Wallstrom 1994 theorem
  (cited by savant-physics-reviewer 2026-04-22) forbids "hbar from
  classical noise alone" path in any formulation equivalent to the
  Madelung hydrodynamics + noise programme. Consistent with our null
  results.

Option (a) remains live but must pass an audit showing the [E,U]
commutator is not smuggled in. Option (b') is cheap to test
(temporal OU noise already probed partially; spatial correlations
new). Option (c) is the pragmatic endpoint; acknowledging it does
not collapse QNG but reassigns hbar from "emergent from substrate"
to "imposed by the measurement/quantization postulate."

### CPU-095 result (2026-04-22) — temporal OU correlation

L=8, fixed rms=0.2, OU process xi(t+dt) = exp(-dt/tau_c) xi(t) + sigma_innov eta
with tau_c in {0.1, 0.5, 1, 2, 5, 10, 50, 1000} lu.

| tau_c | shift/L0 | vs Debye-Waller | H_drift% |
|---|---|---|---|
| 0.1 | -0.0200 | +1.000 (motional narrow matches DW) | 1.7 |
| 2.0 | -0.0230 | +1.152 (peak at tau_c ~ tau_phi = 3.8 lu) | 16.8 |
| 5.0 | -0.0218 | +1.091 | 20.1 |
| 1000 | -0.0130 | +0.651 (quenched incomplete sampling) | 0.2 |

**Verdict: smooth function of tau_c with stochastic-resonance peak at
tau_c matching natural phi relaxation time. No plateau, no universal
scale. Classical Kubo chemical-exchange physics — no hbar.**

### CPU-096 result (2026-04-22) — spatial correlation

L=8, rms in {0.05, 0.1, 0.2, 0.3}, l_corr in {0, 1, 2, 4} lu, via FFT
Gaussian kernel smoothing of white noise.

| l_corr | mode | A | p |
|---|---|---|---|
| 0 (i.i.d.) | dynamic | 0.543 | 2.039 |
| 1 | dynamic | 0.566 | 2.025 |
| 2 | dynamic | 1.408 | 1.973 |
| 4 | dynamic | 0.483 | -0.012 (H_drift 236%) |

**Verdict: spatial correlation amplifies the Debye-Waller prefactor
A classically (27% at l=2) but the "flat" behavior at l=4 is
integrator breakdown (H_drift > 100%), not a physical plateau. At
l -> L/2, xi approaches uniform field = twisted boundary condition,
which is not a hbar signature. No universal scale.**

### CPU-097 result (2026-04-22) — compact U(1) lattice gauge

L=6, full gauge-coupled system: (phi, A_ij, E_ij) with plaquette
magnetic term mu_B (1 - cos W). Scan mu_E, mu_B in {0.1, 1, 10}.

| mu_E | mu_B | <L>/N | <cos W> | H_drift% |
|---|---|---|---|---|
| 0.1 | 0.1 | 0.1227 | 0.984 | 56 |
| 0.1 | 10 | 1.4482 | 0.979 | 32 |
| 1.0 | 0.1 | 0.0682 | 0.983 | 177 |
| 10.0 | 10 | 0.0292 | 0.989 | 0.3 |

- **CV(<L>/N) = 199.85%** across (mu_E, mu_B) — nowhere near universal.
- Range [0.029, 1.45]: 50x variation.
- At (mu_E = mu_B = 10), <L>/N -> beta_phi/2 = 0.030 exactly (recovers
  pure XY). Stiff gauge is frozen, system reduces to CPU-092 baseline.
- <cos W> ≈ 0.98-0.99 everywhere: small-angle Gaussian plaquette
  fluctuations, no integer-flux clustering.

**Verdict: agent audit CONFIRMED. Classical compact U(1) LGT coupled
to phi produces continuous <L>/N tracking coupling constants. No
quantization without [A, E] = i hbar imposed externally. Option (a)
does NOT derive hbar from classical dynamics — it requires hbar
imported via the canonical commutator.**

### Final closure (CPU-092 through CPU-097)

All three residual options of NOTE-QNG-018 §8 tested:

- **(a) Dynamical edge gauge field**: FALSIFIED — classical LGT is continuous, [A,E]=i hbar import needed (CPU-097)
- **(b') Correlated (non-i.i.d.) noise, temporal**: FALSIFIED — smooth stochastic resonance, no plateau (CPU-095)
- **(b') Correlated (non-i.i.d.) noise, spatial**: FALSIFIED — classical Debye-Waller amplification, integrator breakdown at large l (CPU-096)

Option (c) — accept H_v8 is classical, impose external canonical
quantization — is now the **residual structural option** for
reconciling QNG with quantum mechanics. Consistent with Wallstrom 1994
no-go theorem forbidding "hbar from classical noise alone."

**Inside the substrate, hbar does not emerge.** The edge-stochastic
program, opened 2026-04-22 on Gabriel's "edges carry the chaos"
intuition, closes the same day with a complete negative result across
three structural extensions. Gabriel's intuition **direction** (edges
are unexplored territory) was correct; the intuition's specific
MECHANISM (scalar i.i.d. noise → CLT → hbar) is structurally
impossible: CLT delivers a universal FORM, not a universal VALUE.

Next step outside this program: v9 Langevin structural extension with
FLUCTUATION-DISSIPATION as the organizing principle, with hbar
appearing as the ratio of thermal to quantum noise scales — to be
designed carefully, not as a bolt-on.
