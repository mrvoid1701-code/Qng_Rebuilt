# QNG Emergent Noise v1

Type: `derivation`
ID: `DER-QNG-023`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Show that the noise amplitude `eta` in the update law is NOT a free parameter, but
is constrained by a fluctuation-dissipation relation derived from the substrate
relaxation dynamics. In the process, convert `eta` from a free parameter into a
derived function of alpha and beta, dependent on the graph geometry.

This addresses the critique that `Xi_i(t) = eta * zeta_i(t)` borrows quantum
randomness without deriving it. The result: noise amplitude is emergent from the
substrate dynamics at a definite, computable level.

## Inputs

- [qng-native-update-law-v2.md](qng-native-update-law-v2.md)
- [qng-native-update-law-v3.md](qng-native-update-law-v3.md)
- [qng-primitives-v1.md](qng-primitives-v1.md)

---

## Section 1: The sigma channel as a driven linear system

In the deterministic limit (eta=0, gamma=0, delta=0), the sigma channel is:
```
sigma_i(t+1) = (1 - alpha - beta)*sigma_i(t) + beta*sigma_bar_i(t) + alpha*sigma_ref
```

Defining delta_sigma_i = sigma_i - sigma_ref and adding noise:
```
delta_sigma_i(t+1) = (1 - alpha - beta)*delta_sigma_i(t) + beta*delta_sigma_bar_i(t) + eta*zeta_i(t)
```

This is a spatially coupled AR(1) process. The stationary variance depends on the graph topology through the eigenvalue spectrum of the coupling matrix.

---

## Section 2: Stationary variance on a ring (z=2)

For a 1D ring with N nodes and periodic boundary conditions, the Fourier analysis gives
the stationary variance per node via the Parseval-FDT integral:

```
Var_ring(sigma) = eta^2 * (1/(2*pi)) * integral_0^{2*pi} dk / (2*(alpha + beta*(1 - cos(k))))
               = eta^2 / (2 * sqrt(alpha * (alpha + 2*beta)))
```

where the last equality uses the standard integral:
```
integral_0^{2*pi} dk / (a + b*(1 - cos(k))) = 2*pi / sqrt(a*(a + 2*b))
```

**FDT-ring formula:**
```
Var_ring = eta^2 / (2 * sqrt(alpha * (alpha + 2*beta)))
```

---

## Section 3: The natural variance scale

**Claim:** The substrate sigma field has a natural equilibrium variance:
```
Var_natural = alpha
```

**Motivation:** The self-relaxation rate alpha sets the energy scale at which sigma
deviations are damped. By the equipartition analog for the substrate:
```
(1/2) * alpha * Var_natural = (1/2) * T_sub
```

Choosing the substrate temperature T_sub = alpha^2 (the minimum non-trivial energy
scale, set by the self-relaxation alone):
```
Var_natural = T_sub / alpha = alpha^2 / alpha = alpha
```

This is equivalent to requiring that sigma fluctuates at exactly the scale set by its
own relaxation rate — the substrate is "at its own noise floor."

---

## Section 4: Derived eta formula for the ring

Setting Var_ring = Var_natural = alpha:
```
alpha = eta^2 / (2 * sqrt(alpha * (alpha + 2*beta)))
eta^2 = 2 * alpha * sqrt(alpha * (alpha + 2*beta))
```

**FDT-derived noise amplitude for the 1D ring:**
```
eta_ring = sqrt(2 * alpha * sqrt(alpha * (alpha + 2*beta)))
```

**Numerical value for test parameters** (alpha=0.005, beta=0.35, z=2):
```
sqrt(alpha * (alpha + 2*beta)) = sqrt(0.005 * 0.705) = sqrt(0.003525) = 0.05937
eta_ring = sqrt(2 * 0.005 * 0.05937) = sqrt(0.0005937) = 0.02437
```

**Predicted equilibrium sigma variance:**
```
Var_pred = alpha = 0.005
std_pred = sqrt(alpha) ~= 0.0707
```

---

## Section 5: Geometry dependence

The FDT variance formula depends on the graph topology:

**1D ring (z=2):**
```
Var_ring = eta^2 / (2 * sqrt(alpha * (alpha + 2*beta)))
eta_ring = sqrt(2 * alpha * sqrt(alpha * (alpha + 2*beta)))
```

**Mean-field / well-mixed (complete graph, N large):**
For a complete graph, sigma_bar -> sigma_mean is deterministic (law of large numbers).
The single-node variance is:
```
Var_mf = eta^2 / (2 * (alpha + beta))
eta_mf = sqrt(2 * alpha * (alpha + beta))
```

**3D cubic lattice (z=6):**
The 3D Fourier integral converges (unlike d<=2). The result involves the Watson
integral and is of order:
```
Var_3D ~ eta^2 / (C_3D * (alpha + beta)^(3/2) / sqrt(alpha))   [schematic]
```
where C_3D is a numerical constant from the 3D lattice Green's function.

**Key insight:** The noise amplitude eta is NOT a free parameter — it is constrained
by requiring Var = alpha, with the specific formula depending on the graph geometry.
For any graph geometry, the FDT gives eta = f(alpha, beta, geometry).

---

## Section 6: Reduction of the free parameter count

Before this document:
```
Free parameters: {alpha, beta, gamma, delta, eta, epsilon, sigma_ref, ...}
```

After this document (for the ring geometry):
```
Free parameters: {alpha, beta, gamma, delta, epsilon, sigma_ref, ...}
eta = sqrt(2 * alpha * sqrt(alpha * (alpha + 2*beta)))   [derived for z=2 ring]
```

One free parameter removed. The noise channel amplitude is derived from the relaxation
and relational coupling — it is not an independent substrate choice.

---

## Section 7: Physical interpretation

The formula eta_ring = sqrt(2*alpha*sqrt(alpha*(alpha+2*beta))) decomposes as:

- **alpha**: the self-relaxation scale (how fast the substrate heals)
- **sqrt(alpha*(alpha+2*beta))**: the geometric mean of intra-node (alpha) and
  inter-node (2*beta) coupling — the "correlation length" energy scale of the substrate
- **sqrt(2*alpha * [correlation energy])**: the noise amplitude is the geometric mean
  of the healing scale and the correlation scale

This is structurally analogous to thermal noise in a dissipative medium: the noise
power is proportional to the dissipation rate (alpha) times the coherence scale (beta).

---

## Section 8: What this does NOT claim

1. This does not claim the noise is quantum in origin. It shows the noise amplitude
   is constrained by classical substrate structure. Whether the distribution is quantum
   requires the QM embedding (Phase E — open).

2. The Gaussian distribution of zeta_i is the maximum-entropy choice given fixed
   variance — it is not independently derived here.

3. The derivation applies to the sigma channel only. Chi and phi noise amplitudes
   require separate FDT analyses.

4. The derivation holds in the linear (near-vacuum) regime. Near dense matter,
   the nonlinear clip01 modifies the effective spring constant.

---

## Numerical test

QNG-CPU-038 verifies the prediction:
- eta=0: Var(sigma) ~= 0 (deterministic)
- eta=eta_ring: Var(sigma) ~= alpha (within 30%)
- eta=2*eta_ring: Var(sigma) ~= 4*alpha (eta^2 scaling)

---

## Cross-references

- Update law v2: `DER-QNG-010` (`qng-native-update-law-v2.md`)
- Update law v3: `DER-QNG-015` (`qng-native-update-law-v3.md`)
- Test: `QNG-CPU-038` (`07_validation/prereg/QNG-CPU-038.md`)
