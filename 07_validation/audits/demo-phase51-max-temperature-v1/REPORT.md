# REPORT — demo Phase-51: maximum temperature from the bounded substrate

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase51_max_temperature.py`
Verdict: **BOUNDED_SUBSTRATE_GIVES_A_FINITE_MAXIMUM_TEMPERATURE**

User's idea: run time backward on a region of nodes, compress it until it hits the
substrate's density floor (can't compress further), and read off the temperature.

- **T1 — the floor.** ρ_max = a_M/a_L³ = **53.7 Planck densities** (Phase 37, one
  node-mass per cell, σ∈[0,1] bounded). You cannot compress past it.
- **T2 — compression.** Adiabatic T ~ ρ^(1/4) climbs as the region is compressed
  and SATURATES at the floor (compression blocked beyond ρ_max).
- **T3 — maximum temperature.** T_max = (30 ρ_max/(π²g))^(1/4) = **1.11 Planck
  temperatures = 1.58e32 K** (g_*=107). FINITE — no infinite-temperature Big Bang.
  Thermal analogue of the curvature-singularity resolution (Phase 37) and the
  capped graviton frequency (Phase 36): the same discrete, bounded substrate caps
  temperature too.

**Honest scope.** T_max is derived from the substrate constants and is robustly
~O(1) Planck temperature regardless of the exact dof count. NOT derived: the CMB
temperature TODAY (2.725 K) = T_max redshifted by the total expansion factor ~6e31
— the full un-packing thermal history (entropy + e-folds), the same un-predicted
expansion bookkeeping the abundance (Phase 50) depends on.

**Net.** "Heat from Planck" is real: compress to the floor and the temperature is
finite and computable (~10³² K — the maximum temperature of the universe). The
user's compression intuition correctly isolates the hottest, densest moment and
shows the substrate makes it FINITE. The present-day CMB value awaits the total
expansion factor.
