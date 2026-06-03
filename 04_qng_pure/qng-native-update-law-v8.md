# QNG Native Update Law v8

Type: `derivation`
ID: `DER-QNG-039`
Status: `confirmed`
Author: `C.D Gabriel`
Date: `2026-04-14`

## Inputs

- [qng-two-field-substrate-v1.md](qng-two-field-substrate-v1.md) — DER-QNG-033 (v7 two-field substrate)
- [qng-hamiltonian-v7-two-field-v1.md](qng-hamiltonian-v7-two-field-v1.md) — DER-QNG-036 (v7 Hamiltonian)
- [qng-particle-mass-identification-v1.md](qng-particle-mass-identification-v1.md) — DER-QNG-038 (mass identification)
- [qng-native-update-law-v5.md](qng-native-update-law-v5.md) — DER-QNG-026 (v5 baseline)

---

## Objective

Resolve the ring stability problem: vortex rings in v7 substrate dissolve at a
constant rate (proportional to gamma) in the infinite-volume limit. Channel H
introduces depletion-weighted phi diffusion, confining the phi winding to the
ring and enabling genuinely stable vortex rings confirmed by GPU simulation.

## Root Cause of Dissolution (pre-v8)

v5 Channel F: `sigma_m -= gamma * disorder(phi) * sigma_m`

Channel F depletes sigma_m where phi winds (ring core). But phi (BETA_PHI term)
diffuses outward from the ring into the bulk. As winding spreads, disorder
becomes nonzero over a growing region. Channel F then depletes sigma_m over this
larger region at a constant rate proportional to gamma.

Confirmed numerically (ratio scan GPU, 2026-04-14):
- Late-time dissolution rate = 0.0044 * ratio (linear scaling, flat trend)
- Rate never converges to zero regardless of gamma/alpha ratio
- Rate minimum ~0.001 even with gamma/alpha = 0.5

## Channel H Definition

Replace constant BETA_PHI with depletion-weighted phi diffusion rate:

```
depletion_i = max(0, sigma_ref - sigma_m_i) / sigma_ref   [in [0, 1]]

bp_eff_i = BETA_PHI_MIN + BETA_PHI_RING * depletion_i

phi_i(t+1) = wrap(phi_i + bp_eff_i * adiff(phi_mean_i, phi_i))
```

where `phi_mean_i` is the sigma_m-weighted circular mean of phi over neighbors
(unchanged from v5).

**Physical interpretation (Ginzburg-Landau analogy):**
The phi field is the internal phase of the vortex (order parameter). In
condensed matter, order parameter dynamics exist only where condensate is
present. In the bulk (sigma_m = sigma_ref, depletion = 0), phi has no dynamics
(bp_eff = BETA_PHI_MIN ~ 0). At the ring core (sigma_m depleted, depletion > 0),
phi aligns rapidly (bp_eff ~ BETA_PHI_RING). This keeps the phi winding
localized at the ring and prevents boundary erosion.

## Parameters (canonical values from GPU confirmation)

```
BETA_PHI_MIN  = 0.001   # residual diffusion in bulk (prevents freezing)
BETA_PHI_RING = 0.005   # diffusion at ring core (same as v5 BETA_PHI)
```

## Upstream

- [qng-native-update-law-v5.md](qng-native-update-law-v5.md) — DER-QNG-026 (Channel F)
- [qng-two-field-substrate-v1.md](qng-two-field-substrate-v1.md) — DER-QNG-033 (v7)
- [qng-hamiltonian-v7-two-field-v1.md](qng-hamiltonian-v7-two-field-v1.md) — DER-QNG-036

## Full v8 Update Law (sigma_m channel, Phase 2)

```
# sigma_g (gravitational field — Channel A_g + diffusion + Channel G)
sigma_g_i += ALPHA_G * (sigma_ref - sigma_g_i)
           + BETA_G  * (mean_sigma_g_neighbors - sigma_g_i)
           - k_gm    * max(0, sigma_ref - sigma_m_i)        [Channel G: matter -> gravity]

# sigma_m (matter field — Channel A + diffusion + Channel F + back-reaction)
sigma_m_i += ALPHA   * (sigma_ref - sigma_m_i)
           + BETA    * (mean_sigma_m_neighbors - sigma_m_i)
           - gamma   * disorder(phi_i) * sigma_m_i          [Channel F: phi -> ring]
           + k_gm    * max(0, sigma_ref - sigma_g_i)        [Channel B: gravity traps matter]

# chi (memory — couples to sigma_g)
chi_i = chi_i * (1 - CHI_DECAY)
      + CHI_REL * (mean_sigma_g - sigma_g_i)
      + DELTA   * (sigma_ref - sigma_g_i)

# phi (internal phase — Channel H: depletion-weighted)
depletion_i = max(0, sigma_ref - sigma_m_i) / sigma_ref
bp_eff_i    = BETA_PHI_MIN + BETA_PHI_RING * depletion_i
phi_i      += bp_eff_i * adiff(phi_mean_i, phi_i)           [Channel H: localized winding]
```

## Stability Mechanism

Three channels work together:

1. **Channel F** (v5): creates ring by depleting sigma_m where phi winds
2. **Channel G + back-reaction** (v7): ring depletion creates sigma_g well;
   well pulls sigma_m back into depletion zone (gravitational self-trapping)
3. **Channel H** (v8): phi winding stays localized at ring; no boundary erosion

Without Channel H: Channel G reduces but does not eliminate dissolution.
Without Channel G: Channel H reduces rate ~4x but floor at ~0.001.
With both: genuine stability confirmed (rate < 0.0005, decreasing).

## Numerical Confirmation

GPU scan (2026-04-14), L=40, R=8, alpha=0.005, gamma=0.005, k_gm=0.01:

| Config | k_gm | Channel H | M_stable | late_rate | Status |
|--------|------|-----------|----------|-----------|--------|
| v8_ref | 0    | YES       | 168.5    | 0.000999  | NEAR-STAB |
| v7h_a  | 0.01 | YES       | 36.0     | 0.000203  | STABLE |
| v7h_b  | 0.05 | YES       | 2.4      | 0.000014  | STABLE |
| v7h_c  | 0.10 | YES       | 0.7      | 0.000004  | STABLE |
| v7_only| 0.10 | NO        | ~0.0     | 0.000003  | STABLE* |

*v7_only: ring compresses to zero — trivial solution.

**First genuinely stable vortex ring in infinite-volume limit: v7h_a (k_gm=0.01).**

## Mass Calibration Note

Back-reaction (k_gm) compresses rings and perturbs the mass ratio M(R=4)/M(R=5):
- Without back-reaction: ratio = 0.7634 (matches m_proton/m_Delta = 0.7616)
- With back-reaction k_gm=0.01: ratio = 0.6471

**Conclusion:** intrinsic ring mass (mass identification protocol) is the free
ring mass at T_P2=1000 (CPU-074/075), NOT the gravitationally compressed
equilibrium mass. Back-reaction sets gravitational self-energy, not rest mass.
Mass identification protocol (DER-QNG-038) remains valid.

## Open Questions

1. **Residual rate ~0.0002** at v7h_a: physical (ring not true ground state) or
   numerical (lattice radiation)? Test: does it scale with lattice spacing?

2. **Decay widths**: dissolution rate != decay width Gamma. Physical decay
   (Delta -> N + pi) requires ring-to-ring transitions (R=5 -> R=4 + phi-wave).
   Requires multi-ring simulation with phi-wave emission channel.
   See: Einstein-mind review 2026-04-14.

3. **v8 action principle**: Channel H breaks the gradient-flow structure of
   DER-QNG-036 (H_v7 = T_g + E_v7). A v8 Hamiltonian H_v8 with depletion-
   weighted kinetic term for phi is needed.

## Audit Trail

- `tests/gpu/qng_v8_v7_combined_gpu.py` — stability confirmation
- `07_validation/audits/qng-v8-v7-combined-v1/` — full results
- `tests/gpu/qng_proton_mass_calibration_gpu.py` — mass ratio calibration
- `07_validation/audits/qng-proton-mass-calibration-v1/` — calibration results
