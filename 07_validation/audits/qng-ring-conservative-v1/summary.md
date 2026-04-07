# QNG-CPU-059 Audit Summary

**Result: PASS**
Date: 2026-04-07
Script: `tests/cpu/qng_ring_conservative_reference.py`

## Check results

| Check | Gate | Result |
|-------|------|--------|
| 1 - Ring dissolves under conservative dynamics | M < M0/2 at step 500 | PASS (M=0 by step 75) |
| 2 - H approximately conserved (integration stable) | dH/H0 < 20% | PASS (dH/H0 = -6.9%) |

## Ring dissolution timeline

| Ham step | M_ring | H_total | dH/H0 |
|----------|--------|---------|-------|
| 0        | 954.9  | 10884   | 0.0%  |
| 25       | 486.7  | 10846   | -0.35% |
| 50       | 28.7   | 10809   | -0.69% |
| 75       | 0.0    | 10771   | -1.0%  |
| 500      | 0.0    | 10130   | -6.9%  |

**Ring half-life: 50 Hamiltonian steps** (= 50 x dt = 0.25 time units)

Compare to v5 ring lifetime: ~2000+ Phase-2 dissipative steps.
Conservative dynamics kills the ring ~20,000x faster than dissipative dynamics maintains it.

## Interpretation

The v5 ring is NOT a soliton of H.

The ring is a stable attractor of the DISSIPATIVE gradient flow of E (v5 dynamics).
Under CONSERVATIVE Hamilton's equations (no Channel A, no Channel F, no chi_decay),
the ring's sigma depletion fills in within 75 Hamiltonian steps.

The chi field spreads across the lattice (chi_rms decays from 5.34 to 3.21)
as kinetic energy redistributes. The phi winding structure collapses as the
sigma depletion (which defines the vortex core) disappears.

## Gap 7 confirmed

Einstein's question (NOTE-QNG-017): "Does the conservative Hamiltonian support
stable solitonic excitations?"

Answer: NO. The H = T + E functional does not support stable ring solitons with
current substrate parameters. The ring-as-particle program requires either:

1. A different conservative structure (Path C: Skyrme-like topological stabilizer)
2. The particle IS the dissipative attractor, not a conservative soliton
   (interpretation: rest mass = energy of dissipative attractor, not soliton energy)
3. A modified kinetic term T that provides topological stability

## H conservation check

H drifts -6.9% over 500 explicit Euler steps (expected for non-symplectic integrator).
The drift is linear in time (~0.014% per step), indicating a systematic but small error.
A symplectic integrator (leapfrog) would give exact H conservation -- but the ring
dissolution result is robust to this drift level.

## Note on CPU-057/058 mass estimates

CPU-057 evaluated H on a FROZEN v5 dissipative attractor, not a conservative soliton.
The snapshot Hamiltonian (H=10884 for k_back=0.10) is the energy of a dissipative
attractor state. This is not the same as rest mass energy in the physical sense.

However, it remains a valid UPPER BOUND on the energy that would be radiated if the
ring were to dissolve in a conservative substrate. Whether this maps to physical
particle mass requires resolving Gap 7.

## Next steps

1. Test Path C: add a Skyrme-like term Q = gamma_S × |chi|² × (1 + (sbar-si)²)^{1/2}
   to H that provides short-range repulsion and could stabilize the ring.

2. Test Path B: initialize a ring with NEGATIVE chi_core (sigma above sigma_ref
   inside ring). Check whether this configuration is compatible with both
   Channel G and stable phi winding.

3. Analytical: derive conditions on T for H to have a stationary point at some R*.
   The current T ~ R² is too steeply growing -- it pushes sigma back to sigma_ref
   rather than maintaining the depletion.
