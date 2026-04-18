# QNG v8: V(sigma_m) potential — Ginzburg-Landau term for matter sector

Type: `derivation`
ID: `DER-QNG-040`
Status: `falsified_structural`
Author: `C.D Gabriel`
Date: `2026-04-18`
Falsified: `2026-04-18` (QNG-GPU-018 FAIL_H3_STRUCTURAL)

---

## Objective

Add a Ginzburg-Landau potential `V(sigma_m) = (lambda/4) * (sigma_m^2 - sigma_ref^2)^2`
to the v7 Hamiltonian E_v7 so that the sigma_m sector acquires an intrinsic
healing length `xi` independent of ring radius R. Derive `lambda` from existing
QNG primitives (no fit parameter). Define the forced predictions and the
non-riggable falsifiability gates for GPU-018.

This is the v8 candidate. It is proposed, not accepted — acceptance requires
GPU-018 to pass.

## Motivation (from exhaustion)

Four consecutive falsifications under v5+Channel H:

| Test | Observable | Verdict |
|---|---|---|
| GPU-009..014 | M_ring | FAIL — geometric 5/4 |
| GPU-015 | H_v7 total Hamiltonian | FAIL — same IR pathology |
| GPU-016 | e_B (Bogomolny proxy) | FAIL_GEOMETRIC, windowed ratio 4.5 |
| GPU-017 | Hopfion Q=1 topology | FAIL — α=1.89 slower than ring 2.39 |

Common root cause (NOTE-QNG-016, einstein-mind diagnosis 2026-04-18,
savant-physics-reviewer diagnosis 2026-04-18):

**sigma_m has no intrinsic mass scale in v7. phi is a massless Goldstone
of the global U(1) shift symmetry. No dressing of phi (including Hopfion
topology) can supply a length scale to sigma_m. The fix must come from
the sigma_m sector itself — via an explicit potential V(sigma_m).**

## 1. Form of the potential

Mexican-hat in sigma_m, with vacuum at sigma_m = sigma_ref (= 0.5 by v7
convention):

```
V(sigma_m) = (lambda/4) * (sigma_m^2 - sigma_ref^2)^2
```

Derivative (used in gradient flow):
```
dV/dsigma_m = lambda * sigma_m * (sigma_m^2 - sigma_ref^2)
```

Linearization around the vacuum (sigma_m = sigma_ref + s, |s| << sigma_ref):
```
V ~ lambda * sigma_ref^2 * s^2 + O(s^3)
   => m_V^2 = d^2V/dsigma_m^2 |_{sigma_ref} = 2 * lambda * sigma_ref^2
```

**Savant observation** (critique-v-sigma-m-routes.md §Q3): because sigma_m
is clipped to [0,1], the negative-branch minimum sigma_m = -sigma_ref lies
outside the physical domain. The Z2 is explicitly broken by the boundary.
In the physical sector, V is indistinguishable from a simple mass term
`m_V^2 * (sigma_m - sigma_ref)^2` near the vacuum. The "Mexican hat" shape
matters only at order O(s^3), and only if large deviations occur (which
they do NOT during ring dynamics because the depletion is bounded).

Therefore at leading order V is a **localized mass term** for sigma_m
fluctuations. That is exactly what the sigma_m sector needs.

## 2. Derivation of lambda: marginal stability extension of DER-QNG-034

### 2.1 Route comparison

Three candidate derivation routes were analyzed (einstein-mind derivation
file; savant critique file). Summary:

| Route | Constraint type | Derivability of lambda |
|---|---|---|
| (a) DER-QNG-034 marginal stability, extended to sigma_m | LOWER BOUND | Gives `lambda >= lambda_min`; saturation is a convention |
| (b) DER-QNG-037 G-consistency | anti-constraint | Forces `lambda = 0` at k=0; invalid |
| (c) DER-QNG-023 FDT variance | circular | Free parameter = choice of equipartition target |

**Route (a) is selected**, with the explicit understanding that saturation
of the marginal-stability condition is a *convention* inherited from
DER-QNG-034 (where the same saturation convention was used).

### 2.2 Equation of motion with V(sigma_m)

The v7 sigma_m update, with Channel F and V added:

```
d_t sigma_m_i = alpha_m*(sigma_m_ref - sigma_m_i)
              + beta_m*Laplacian(sigma_m)_i
              - gamma_phi*(1-|Z_i|)*sigma_m_i
              - dV/dsigma_m(sigma_m_i)
```

### 2.3 Linearized mass-squared in the ring core

Inside the ring core |Z| → 0, Channel F contributes a negative mass-squared
m_F^2 = -gamma_phi (the destabilizing "bag sink"). V contributes a positive
restoring curvature m_V^2 = 2*lambda*sigma_ref^2. The damping alpha_m
provides additional dissipation.

Marginal stability of the worst-case (k=0, core-averaged) mode:

```
-alpha_m + m_V^2 + m_F^2 = 0
-alpha_m + 2*lambda*sigma_ref^2 - gamma_phi = 0
```

Solving for lambda:

```
lambda = (gamma_phi - alpha_m) / (2 * sigma_ref^2)       (Eq. 1)
```

Same algebraic template as DER-QNG-034:

```
DER-QNG-034:  K_BACK*DELTA = ALPHA + CHI_DECAY*(1-ALPHA)        [marginal]
DER-QNG-040:  gamma_phi    = alpha_m + 2*lambda*sigma_ref^2     [marginal]
```

The destabilizing channel (LHS) is balanced by dissipation + restoring
curvature (RHS).

### 2.4 Numerical value (v7 convention)

Parameters (v7 production):
- alpha_m = 0.005 (by minimality: same as alpha_g; see §6 caveat)
- beta_m = 0.35 (sigma_m diffusion, Channel B on sigma_m)
- gamma_phi = 0.10 (Channel F)
- sigma_ref = 0.5

From Eq. 1:
```
lambda = (0.10 - 0.005) / (2 * 0.25) = 0.095 / 0.5 = 0.19
```

(Correction of einstein-mind value: einstein-mind derivation used
sigma_ref=1. With v7 convention sigma_ref=0.5, Eq. 1 gives lambda=0.19.)

Healing length:
```
xi = sqrt(beta_m / (2 * lambda * sigma_ref^2))
   = sqrt(0.35 / (2 * 0.19 * 0.25))
   = sqrt(0.35 / 0.095)
   = sqrt(3.684) = 1.92 lu
```

Comparisons:
```
xi / a              = 1.92       (well-resolved: xi > lattice spacing)
xi / R(=5)          = 0.38       (thin-tube limit: xi << R)
xi / lambda_screen  = 0.23       (V does not disturb Newtonian limit)
```

Regime: **thin, resolved, decoupled from gravity**.

## 3. Critical caveats (from Savant critique, fully incorporated)

### 3.1 Saturation is a convention, not a derivation

Eq. 1 gives a **lower bound** lambda >= lambda_min on strict stability
grounds. Saturation (equality) is chosen because:

1. It matches the DER-QNG-034 convention (analogy of form).
2. It minimizes lambda, so the healing length is as LARGE as allowed;
   a smaller xi would require a strictly larger lambda.
3. Any strictly larger lambda is also stable but gives xi < 1.92 lu,
   shifting the mass ratio M(R=5)/M(R=4) toward the geometric limit 5/4 —
   which is the failure mode we are trying to cure.

The last point upgrades saturation from convention to **falsifiable
prediction**: if the saturation lambda = 0.19 does NOT pass GPU-018
Gates B and C (below), then lambda is free and the saturation convention
is falsified. The QNG mass scale would then become Gap 9 (below).

### 3.2 If saturation fails → Gap 9 (Yukawa-analog)

If Gate B (R-independent FWHM) or Gate C (mass ratio convergence) fail
under lambda = 0.19, V(sigma_m) is still the correct structural fix, but
lambda itself is not derivable from v7 primitives. This would be labeled:

**Gap 9 (the origin of the sigma_m mass scale).** lambda plays the role
of the Yukawa couplings in the Standard Model: it is a phenomenological
parameter that sets the absolute mass scale, distinct from the structural
(topological) claims of the theory. QNG would then predict:

- The baryon family STRUCTURE (ring topology, even/odd R → I=1/2 / I=3/2)
- The PATTERN of the mass spectrum (ordering of states)

but NOT:

- The absolute mass scale (requires lambda as external input)
- Why lambda takes its specific value

This is the SM precedent (Weinberg 1979, phenomenological Lagrangians).
It is legitimate; it must be labeled honestly. Route (a) saturation is
the FIRST TEST before capitulating to Gap 9.

## 4. Modification to the v7 Hamiltonian

E_v7 is augmented with a new term (call this E_v8):

```
E_v8 = E_v7 + sum_i V(sigma_m_i)
V(sigma_m) = (lambda/4) * (sigma_m^2 - sigma_ref^2)^2
lambda     = (gamma_phi - alpha_m) / (2 * sigma_ref^2)
```

The modification to the sigma_m gradient-flow equation (DER-QNG-036 §2.2):

```
dE_v8/dsigma_m = dE_v7/dsigma_m + lambda*sigma_m*(sigma_m^2 - sigma_ref^2)
              = -beta_m*Laplacian(sigma_m)
                + alpha_m*(sigma_m - sigma_ref)
                + gamma_phi*(1-|Z|)*sigma_m
                + lambda*sigma_m*(sigma_m^2 - sigma_ref^2)
```

Gradient flow: sigma_m_i += -dE_v8/dsigma_m_i × dt.

Channels G, A (chi), chi-decay, phi evolution are unchanged. V(sigma_m)
is purely in the sigma_m sector; it does NOT modify the chi sector.
Therefore G_QNG = beta/z (DER-QNG-037) is preserved at leading order.
This satisfies Route (b) as a consistency check (the k=0 Green's function
match is broken, but only within the sigma_m sector — the sigma_g sector
where gravity lives is unchanged).

## 5. Predicted mass ratio M(R=5)/M(R=4)

In the thin-tube limit (xi/R << 1) the ring mass has three terms:

```
M(R) = c_bag * V_bag(R)  +  c_sigma * S_bag(R)  +  c_phi * E_phi(R)
```

with
- V_bag(R) = 2*pi^2 * R * xi^2     [torus interior volume; bag contribution]
- S_bag(R) = 4*pi^2 * R * xi       [torus surface; tension contribution]
- E_phi(R) ~ R * ln(R/xi)          [Biot-Savart log-solenoid core energy]

For xi = 1.92:
```
            V_bag     S_bag     E_phi = R*ln(R/xi)
R = 4:    ~ 4         ~ 4       4*ln(4/1.92)  = 2.93
R = 5:    ~ 5         ~ 5       5*ln(5/1.92)  = 4.78
```

Define kappa = (c_bag*V_bag + c_sigma*S_bag) / (c_phi*E_phi). Then:

```
M(R=5)/M(R=4) = (4.78 + 5*kappa) / (2.93 + 4*kappa)

kappa      ratio
-----      -----
  0        1.63      (log-only; no V term effective — same as v5 Channel H failure)
  1        1.41
  2        1.35
  3       *1.325*   ← within 1% of SM 1.313
  5        1.298
  inf      1.25      (bag-only; pure geometric)
```

**SM target: N(1232)/N(938) = 1.313.** A kappa in the range 3–5 reproduces
it. Both c_bag and c_sigma are fixed by (lambda, beta_m); they are NOT free.
GPU-018 measures kappa directly by fitting the three contributions
separately.

Contrast: v5+Channel H had no bag (lambda=0), forcing kappa=0 → 1.63
under the pure-log fit. GPU-016 confirmed the L-drift pulls this toward
1.25 as L grows because the log coefficient itself vanishes under IR
smearing. V(sigma_m) pins BOTH: the log coefficient stays finite
(core is confined) AND a bag contribution exists.

## 6. Caveats

### 6.1 alpha_m not independently fixed

Taking alpha_m = alpha_g = 0.005 by minimality is an explicit choice.
If alpha_m is later derived separately (e.g., from an FDT analog of
DER-QNG-023 applied to sigma_m), the numerical value of lambda shifts.
The STRUCTURAL form Eq. 1 does not change. This is one explicit
assumption, called out.

### 6.2 Saturation vs. strict inequality

See §3.1. Saturation is the first falsifiable test; strict inequality
(any larger lambda) is the fallback if saturation is falsified.

### 6.3 Linearization validity

The derivation is linearized. Nonlinear corrections (sigma_m^6) appear at
next EFT order. Their size is controlled by (ring depletion)^2 × lambda;
for gamma_phi = 0.10 and typical core depletion ~0.3, these are ~3% and
can be measured from residuals in GPU-018 after the leading fit.

### 6.4 sigma_ref value

sigma_ref = 0.5 is the lattice normalization. Any other choice would
rescale lambda by (0.5/sigma_ref)^2 but leave xi invariant when beta_m
is rescaled consistently. sigma_ref = 0.5 is the v7 convention.

## 7. Upstream dependencies

- DER-QNG-023 — emergent noise (FDT template)
- DER-QNG-033 — v7 two-field substrate
- DER-QNG-034 — Gap 8 stability analysis (marginal-saturation template)
- DER-QNG-036 — H_v7 Hamiltonian structure
- DER-QNG-037 — G-reconciliation (Route b consistency check)
- NOTE-QNG-016 — mass-observable exhaustion
- GPU-012 through GPU-017 — four empirical falsifications forcing V
- einstein-mind/diagnosis-no-mass-scale-sigma-m.md
- einstein-mind/derivation-v-sigma-m-lambda.md
- savant-physics-reviewer/critique-v-sigma-m-routes.md

## 8. What would close this derivation

**Acceptance pathway**: GPU-018 Gates B (R-independent FWHM = 1.92 lu)
AND C (L-converged mass ratio in [1.25, 1.40]) both PASS at lambda = 0.19.
Then Eq. 1 saturation is confirmed and DER-QNG-040 is promoted to `locked`.

**Falsification pathway A (lambda saturation wrong, structural form right)**:
Gate A (halo decay α > 3.5 at L=80) PASS but Gate B or C FAIL.
Interpretation: V(sigma_m) cures the IR halo but the specific lambda value
is not derivable. Re-open as Gap 9 (Yukawa analog). Run GPU-018B with
lambda as an EFT matching parameter; commit value pre-run.

**Falsification pathway B (structural form wrong)**:
Gate A FAIL. V(sigma_m) does not cure the halo. Ring-as-baryon program
requires a fundamentally different substrate modification (beyond both
topology and potential). Not yet identified.

---

## Summary

We extend the DER-QNG-034 marginal-stability template from sigma_g to sigma_m
and obtain:

```
lambda = (gamma_phi - alpha_m) / (2 * sigma_ref^2) = 0.19
xi = sqrt(beta_m / (2 * lambda * sigma_ref^2)) = 1.92 lu
```

All parameters are v7 primitives; the only explicit assumption is
alpha_m = alpha_g. The saturation convention matches DER-QNG-034 and is
itself a falsifiable prediction (GPU-018 Gates B and C test it). If
saturation fails, lambda becomes Gap 9 (Yukawa-analog), honestly labeled
and pre-registered as such before GPU-018B.

DER-QNG-040 is the proposed v8 modification to E_v7. Status: `candidate`
pending GPU-018.

---

## FALSIFICATION (2026-04-18, QNG-GPU-018)

**Verdict: FAIL_H3_STRUCTURAL.** DER-QNG-040 is falsified at
the structural level.

Gate results:

| Gate | Observed | Predicted | Verdict |
|---|---|---|---|
| A: halo α(L=80,R=5) | **2.49** | ≥ 3.5 | FAIL (clear) |
| B: FWHM R-indep | **1.00 lu** (R-indep) | 4.52 ± 30% | FAIL (wrong mag.) |
| C: ratio L-converge | **1.048** (1.070→1.031, L=60→120) | in [1.25,1.40] | FAIL (collapsing ↓) |
| D: r_eff linearized | **0.1055** | 0.100 | PASS (5.5% lattice corr.) |

### Root cause: phi is a Goldstone boson, not σ_m

The IR halo observable `dis(r)·σ_m = ⟨sin²(Δphi/2)⟩·σ_m` is dominated
by the phi field, not σ_m. The global U(1) shift symmetry
`phi → phi + c` is unbroken in v5+Channel H and in DER-QNG-040 because
V(σ_m) commutes with phi shifts. By Goldstone's theorem, phi remains
a massless mode, and its long-range correlations produce the observed
power-law halo regardless of σ_m dynamics.

**V(σ_m) cures σ_m but not phi** — and the halo is a phi observable.

### Secondary failure: over-suppression of σ_m depletion

At λ=0.19, the potential's restoring force near σ_m = 0 scales as
λ·σ_ref² ≈ 0.0475, dominating over the available gradient energy
β·(σ_mb - σ_m). The σ_m profile is pinned within a single lattice
cell of the ring core (FWHM = 1.00 everywhere). Even if the halo had
been cured, the mass observable would be degenerate in R.

### Savant's critique vindicated

Savant predicted that saturation of the marginal-stability inequality
was a *convention*, not a *derivation*, and that the committed λ value
would need to be refitted as an EFT parameter (Gap 9). The test
confirms this structurally: λ=0.19 is not the physical value because
V(σ_m) is not the right mechanism at all. Tuning λ to any value leaves
phi massless.

### DER-QNG-034 status unchanged

This falsification does NOT invalidate DER-QNG-034 (marginal-stability
for σ_g). σ_g has a physically motivated kinetic term T_g[chi] that
makes saturation energetically sensible. σ_m has no kinetic term
(overdamped in v7), so the analogical extension was on weaker ground.
Route (a) was the right structural template for σ_g but not for σ_m.

### Implications

- DER-QNG-040 is closed as falsified.
- NOTE-QNG-016 updated to record quintuple-FAIL chain (GPU-009..018).
- Next hypothesis: explicit breaking of phi's U(1) shift symmetry via
  Yukawa-type coupling `g·σ_m·(1 - cos phi)` (pion analog, GMOR-type).
  Formalized as DER-QNG-041 candidate pending 3-agent synthesis.
- If DER-QNG-041 also fails, Gap 4 is reopened as primary open
  structural problem with no viable path; program redirects to
  Lorentz-covariance / conservative-limit work (NOTE-QNG-013).

**Artifacts:**
- `07_validation/audits/qng-sigma-m-potential-v1/interpretation.md`
- `07_validation/audits/qng-sigma-m-potential-v1/report.json`
- `07_validation/audits/qng-sigma-m-potential-v1/run.log`
- `07_validation/prereg/QNG-GPU-018.md`
