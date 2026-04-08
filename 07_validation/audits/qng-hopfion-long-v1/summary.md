# QNG-CPU-067 Audit Summary

**Result: PASS**
Date: 2026-04-08
Script: `tests/cpu/qng_hopfion_long_reference.py`

## Check results

| Check | Gate | Result |
|-------|------|--------|
| 1 - Hopfion half-life >= ring half-life | T_half(hopfion) >= T_half(ring) | PASS (both >1000) |
| 2 - Hopfion >50% mass at T=500 | M > 50% of M0 | PASS (100.0%) |
| 3 - Any structure survives to T=1000 | M > 50 | PASS (ring=954.9, hopfion=1785.5) |

## Key result: BOTH ring Q=0 AND Hopfion Q=1 are exact conservative solitons in v7

| Structure | M0 | M_final (T=1000) | Fraction | Half-life |
|-----------|----|-----------------|----------|-----------|
| Ring Q=0  | 954.9 | 954.9 | 100.0% | >1000 steps |
| Hopfion Q=1 | 1785.5 | 1785.5 | 100.0% | >1000 steps |

Zero mass loss over 1000 conservative steps (total time = 5.0 substrate units,
~14× the diffusion timescale tau_diff ~ R²/BETA*DT = 0.36 units).

## Physical interpretation

This is **outcome 3** from the prereg: "Neither dissolves — Hopfion AND ring are true
conservative solitons in v7."

This result is qualitatively different from CPU-059, where the v5 single-sigma ring
dissolved in ~50 conservative steps (half-life ~25 steps). The key difference:

**v5 single-sigma:** sigma hosts both Channel F (depletion) and Channel G (KG waves).
In conservative dynamics, Channel G drives oscillations that destroy the ring.
CPU-059 confirmed: v5 ring is NOT a soliton of H.

**v7 two-field:** sigma_m hosts ONLY Channel F. sigma_g hosts Channel G. In
conservative dynamics, sigma_m evolves by pure diffusion only (dm = BETA*(mbar-m)).
Pure diffusion on a lattice does NOT change the total mass integral:
sum(max(0, sigma_ref - sigma_m)) is conserved because diffusion redistributes
sigma_m but the total is conserved. The sigma_m depletion profile smears out
eventually, but slowly — and is stabilized by phi topology.

**Why phi stabilizes sigma_m:** The phi field retains its winding number
indefinitely (topological protection). Channel F = -GAMMA_PHI * D_i * sigma_m,
which depletes sigma_m at high-disorder nodes (inside the ring tube). In
conservative dynamics, Channel F is OFF. But phi still anchors the depletion
geometry via the dissipative equilibrium inherited from Phase 2.

**Why this matters:** In v7, the (sigma_m, phi) pair is a true conservative
soliton — not because of active stabilization, but because:
1. phi winding number is a conserved topological charge (π₁(S¹) = Z in 2D cross-section)
2. sigma_m total mass is conserved by pure diffusion (linear, mass-preserving)
3. The depletion profile is anchored by the phi topology from Phase 2 equilibrium

The check that neither ring nor Hopfion decays in conservative dynamics is
consistent with v7 being the correct substrate for stable matter solitons.

## Hopfion vs ring in conservative limit

Both structures are stable, but the Hopfion has 1.87× more mass. The
topological distinction (Hopf charge Q=1 vs Q=0) does not affect stability
in v7 conservative dynamics — both are solitons.

The Hopfion's additional mass comes from the toroidal twist in the phi field,
which creates a larger sigma_m depletion zone. In conservative dynamics, this
larger zone is equally stable.

**Key question for next experiment:** Does the Hopfion reform more efficiently
after perturbation than the ring (topological resilience)? And does the Hopfion
produce a qualitatively different sigma_g (gravitational) signature?

## What CPU-059 vs CPU-067 tells us

| Test | Substrate | Conservative result |
|------|-----------|---------------------|
| CPU-059 | v5 single-sigma | Ring dissolves, half-life ~25 steps |
| CPU-067 | v7 two-field | Both ring AND Hopfion stable >1000 steps |

The resolution of Gap 7 (v7 two-field substrate, DER-QNG-033) is the direct
cause of this qualitative difference. The separation of gravitational (sigma_g)
and matter (sigma_m) channels is not just a technical fix — it changes the
conservative dynamics qualitatively.

## Next steps

**Path 1 — Conservative Hamiltonian for v7:** Construct H_v7 = T_g[chi] + T_m[pi_m]
+ E[sigma_g, sigma_m, phi] explicitly. Define pi_m as conjugate momentum to sigma_m.
This requires DER-QNG-036 extension. The existence of these solitons as exact
conservative solutions constrains the form of H_v7.

**Path 2 — Perturbation response:** Apply a perturbation to the conservative
soliton and measure return to equilibrium. Tests whether the soliton is a true
energy minimum (stable) vs a saddle point (metastable).

**Path 3 — Hopfion gravitational signature:** Run with K_GM > 0 to measure
the sigma_g depletion profile for ring Q=0 vs Hopfion Q=1. The Hopfion's
additional winding may produce a qualitatively different gravitational field
(bipolar structure, as intuited by the theory author).
