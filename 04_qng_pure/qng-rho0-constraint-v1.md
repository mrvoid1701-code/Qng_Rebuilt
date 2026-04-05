# QNG rho0 Constraint v1

Type: `derivation`
ID: `DER-QNG-021`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Derive the formal constraint on the substrate mass scale `rho_0` from (a) the
self-consistency of the Poisson equation in the generation-order limit, and (b)
matching to the observed baryon density. Show that `rho_0` is partially constrained
by substrate parameters, and identify the remaining open quantity that closes Gap 4
of `DER-QNG-011`.

## Inputs

- [qng-matter-source-identification-v1.md](qng-matter-source-identification-v1.md)
- [qng-poisson-assembly-v1.md](qng-poisson-assembly-v1.md)
- [qng-codata-constraint-v1.md](qng-codata-constraint-v1.md)
- [qng-generation-order-v1.md](qng-generation-order-v1.md)

---

## Section 1: Formal constraint from Poisson equation

From `DER-QNG-013`, the effective density is:
```
rho_eff(i) = rho_0 * M_eff(i) / Delta_u^3
```

For the Poisson equation to reproduce the observed gravitational potential of a
physical mass m at distance r (in the pure Poisson limit r << lambda_screen):
```
Phi(r) = -G_SI * m / r
```

the integrated source must satisfy:
```
G_QNG_SI * integral(rho_eff dV) = G_SI * m
```

Since G_QNG_SI = G_SI (CODATA matching from DER-QNG-019), this reduces to:
```
integral(rho_eff dV) = m
```

Expanding:
```
rho_0 * integral(M_eff(x) dV) = m
```

**Formal constraint:**
```
rho_0 = m / integral(M_eff dV)     [Constraint rho0-C1]
```

This is exact. The problem: `integral(M_eff dV)` depends on the substrate dynamics
around the mass m, which is a substrate-internal quantity not yet derived from
first principles for any physical particle.

---

## Section 2: Self-consistency in the generation-order limit

In the generation-order Newtonian limit (DER-QNG-014, DER-QNG-015), with the v3
cross-coupling delta > 0, chi is slaved to the sigma deficit:
```
chi_eff(x) approx -(delta / alpha) * delta_C(x)
```

In the same limit, the matter proxy becomes (leading term from DER-QNG-013 §2):
```
M_eff(x) approx a_M * L_eff(x) * (1 - C_eff(x))
            approx -a_M * (delta/alpha) * delta_C(x) * (1 - sigma_ref)
```

where L_eff approx chi_eff and C_eff approx sigma_ref far from dense matter.

Define the generation-order coupling factor:
```
kappa = a_M * (delta / alpha) * (1 - sigma_ref)    [dimensionless]
```

Then M_eff approx -kappa * delta_C.

From the screened Poisson equation solution (r << lambda_screen):
```
delta_C(r) approx -(S_src / D_diff0) * exp(-r/lambda) / (4 pi r)
                approx -G_QNG * rho_0 * integral(M_eff) / (D_diff0 * r)
```

Substituting M_eff approx -kappa * delta_C back:
```
delta_C(r) approx -G_QNG * rho_0 * kappa * integral(|delta_C| dV) / (D_diff0 * r)
```

The integral integral(|delta_C| dV) is itself of order |delta_C(0)| * lambda^3 (volume
of coherence dip). This gives a self-consistency equation that constrains:
```
rho_0 * kappa * D_diff0^2 * lambda^3 ~ 1   [in substrate units]
```

Using D_diff0 = beta/z and lambda = sqrt(beta/(z*alpha)):
```
rho_0 * kappa * (beta/z)^2 * (beta/(z*alpha))^(3/2) ~ 1
```

Solving for rho_0:
```
rho_0_substrate ~ (z*alpha)^(3/2) / (kappa * beta^(7/2) / z^(7/2))
               = z^(5/2) * alpha^(3/2) / (kappa * beta^(7/2))
```

**With test parameters** (alpha=0.005, beta=0.35, z=6, a_M=1, delta=0.20, sigma_ref=0.5):
```
kappa = 1 * (0.20/0.005) * (1 - 0.5) = 40 * 0.5 = 20
rho_0_substrate ~ 6^(5/2) * 0.005^(3/2) / (20 * 0.35^(7/2))
               = 88.2 * 3.54e-4 / (20 * 0.0247)
               = 0.03121 / 0.4930
               ~ 0.063
```

**Interpretation:** In substrate units, rho_0 ~ 0.06. This is a dimensionless mass
per substrate cell (in units where the substrate has no intrinsic mass scale). The
order of magnitude is set by the ratio of the relaxation rate (alpha) to the
cross-coupling (delta * a_M) and the coherence reference (1 - sigma_ref).

**Note on self-consistency:** The derivation above is schematic — the numerical prefactor
depends on the exact shape of the coherence dip and the geometry of the integration.
It establishes order of magnitude, not an exact value.

---

## Section 3: Physical unit mapping

From DER-QNG-019, the substrate unit of length is:
```
Delta_u_SI = (z/beta) * l_Planck = (6/0.35) * 1.616e-35 m = 2.770e-34 m
Delta_u_SI^3 = 2.12e-101 m^3
```

The substrate mass unit is set by m_Planck = 2.176e-8 kg.

In substrate units, rho_0 ~ 0.06. In Planck units (m_Planck = 1), this would give:
```
rho_0_SI ~ 0.06 * m_Planck = 0.06 * 2.176e-8 kg ~ 1.3e-9 kg
```

This is macroscopic. How does this reconcile with the proton mass (m_p = 1.67e-27 kg)?

**Resolution:** A proton is not a one-node substrate object. With Delta_u_SI = 2.77e-34 m
and the proton charge radius r_p ~ 8.4e-16 m, the proton occupies approximately:
```
N_nodes_proton ~ (r_p / Delta_u_SI)^3 ~ (8.4e-16 / 2.77e-34)^3
               ~ (3.03e18)^3 ~ 2.8e55  nodes
```

The total mass from the substrate:
```
m_proton = rho_0_SI * M_eff_per_node * N_nodes_proton
         ~ 1.3e-9 * M_eff_p * 2.8e55
         ~ 3.6e46 * M_eff_p   kg
```

For this to equal m_p = 1.67e-27 kg:
```
M_eff_p ~ 1.67e-27 / 3.6e46 ~ 4.6e-74
```

This is an extraordinarily small M_eff per node inside a proton. It means the substrate
M_eff for nucleon matter at nuclear density is ~10^-74, not order 1 as the sigmoid
formula might suggest.

**Interpretation of the discrepancy:**

Either (a) the self-consistency estimate rho_0 ~ 0.06 (in Planck units) is incorrect
by many orders of magnitude — likely because the schematic derivation assumes the
coherence dip is order-1 in size, while the physical coherence dip from nucleon matter
at the Planck scale is tiny; or (b) the matter proxy formula M_eff does not describe
nucleon physics in its current form — it describes a different, emergent mass-like
quantity at the substrate scale that must be connected to Standard Model masses through
a different mechanism.

**The honest conclusion:** The self-consistency argument gives a plausible order-of-
magnitude for rho_0 at the substrate scale, but the connection to m_proton requires
understanding how many substrate cells are coherently organized to form a proton, and
what M_eff each of them carries. This is not yet derived.

---

## Section 4: Baryon density matching constraint

**Cosmic baryon density:**
```
rho_baryon = Omega_b * rho_crit = 0.0486 * 9.47e-27 kg/m^3 = 4.60e-28 kg/m^3
```

From Constraint rho0-C1:
```
rho_0 * M_eff_cosmic / Delta_u^3 = rho_baryon
rho_0 = rho_baryon * Delta_u_SI^3 / M_eff_cosmic
      = 4.60e-28 * 2.12e-101 / M_eff_cosmic
      = 9.75e-129 / M_eff_cosmic   kg
```

For rho_0 ~ 1.3e-9 kg (substrate estimate), this gives:
```
M_eff_cosmic ~ 9.75e-129 / 1.3e-9 ~ 7.5e-120
```

An M_eff per substrate node of ~10^-120 for the cosmic average baryon density. This is
consistent with the expectation that cosmic average matter density depletes substrate
coherence by an infinitesimal amount per node — the cosmic environment is almost vacuum
at the substrate scale.

**Summary of constraints:**

| Context | rho_baryon or rho_nuclear | M_eff (implied) | Consistent? |
|---------|--------------------------|-----------------|-------------|
| Cosmic average | 4.6e-28 kg/m^3 | ~7.5e-120 | Yes (tiny M_eff in dilute cosmic background) |
| Nuclear density | 2.3e17 kg/m^3 | ~3.5e-85 (using rho_0~1.3e-9) | Consistent with M_eff << 0.5 |
| Substrate self-consistency | (see §2) | kappa = 20, rho_0 ~ 0.06 (substrate units) | Self-consistent schematically |

The picture is consistent: M_eff per node is tiny (<<< 0.5) even in nuclear matter,
because each substrate node is ~17 Planck lengths and nuclear matter distributes its
mass over 10^55+ nodes. The sigmoid saturation (M_eff -> 0.5) would only occur in a
regime where almost all of a node's coherence is depleted by matter at the sub-Planck scale.

---

## Section 5: Open items (Gap 4 status)

**Partially constrained:** The substrate self-consistency argument gives rho_0 ~ 0.06 in
substrate units (order-of-magnitude). The physical value rho_0_SI ~ 1.3e-9 kg (very rough).

**Remaining open:**

1. **M_eff per node for physical particles:** The precise M_eff that a proton, electron,
   or photon imprints on the substrate is not derived. It requires connecting Standard
   Model particle physics to the substrate dynamics — i.e., understanding how the substrate
   organizes to form stable localized matter structures.

2. **The schematic coefficient in Section 2:** The self-consistency estimate has an
   uncontrolled numerical prefactor (depends on the exact shape of the coherence dip and
   the precise definition of the "volume of coherence dip"). A rigorous bound requires
   numerical integration of the equilibrium sigma profile.

3. **Multiple-particle coherence:** The M_eff assigned to a system of N particles may not
   be N times the single-particle M_eff (non-linear regime). The Poisson equation is linear
   only in the weak-field limit; near dense matter, M_eff could saturate.

**Gap 4 status:** Partially constrained. The formal constraint is derived (rho0-C1).
The self-consistency argument gives order-of-magnitude. The precise value of rho_0_SI
requires matter sector closure (connecting M_eff to Standard Model masses).

---

## Cross-references

- Matter source: `DER-QNG-013` (`qng-matter-source-identification-v1.md`)
- Poisson assembly: `DER-QNG-018` (`qng-poisson-assembly-v1.md`)
- CODATA constraint: `DER-QNG-019` (`qng-codata-constraint-v1.md`)
- Generation order: `DER-QNG-014` + `DER-QNG-015`
- Newtonian limit program: `DER-QNG-011` (`qng-newtonian-limit-program-v1.md`)
