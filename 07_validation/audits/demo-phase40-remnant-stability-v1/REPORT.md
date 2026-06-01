# REPORT — demo Phase-40: dynamical stability of the neutral Planck node-core (remnant-DM)

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase40_remnant_stability.py`
Verdict: **NEUTRAL_CORE_NOT_STABILIZED_SELF_GRAVITY_GOES_JEANS_UNSTABLE** (negative)

Decisive dynamical test of the Phase-39 remnant-DM proposal: does a neutral
(q=0, no phi-winding) node-core actually persist under the substrate dynamics?

Setup: neutral sigma_m depletion core, v7-symmetric self-gravity (matter depletes
sigma_g → screened well; well deepens depletion) + diffusion, scalars clamped to
[0,1] (bounded-scalar floor), sigma_g screening GAMMA=0.04. L=32, 6000 steps.

Results:
| k_gm | outcome | final depth | radius | total depletion |
|---|---|---|---|---|
| 0.00 (control) | DISPERSE | 0.005 | 16.0 | 170 (conserved) |
| 0.06 | GLOBAL-COLLAPSE | 0.600 | 31.2 | 19661 (×116) |
| 0.15 | GLOBAL-COLLAPSE | 0.600 | 31.2 | 19661 (×116) |

**Honest negative.** No localized self-bound remnant forms. Below threshold the
core disperses (pure diffusion); above threshold self-gravity drives a global
Jeans collapse (the entire lattice sigma_m runs to the 0 floor — "core" fills the
box). A genuine localized remnant would need pressure/kinetic support (full v8
symplectic dynamics with pi_m, or an explicit minimum-length hard core) that this
overdamped screened-diffusion model lacks.

**Net:** remnant stability remains **UNPROVEN**, consistent with Phase-39's honest
verdict (viable direction, stability open). The test pinpoints the obstacle: the
same self-gravity that could bind a neutral core drives instability without a
support term. The decisive check requires the full v8 kinetic substrate — not
done here. This does NOT falsify remnant-DM (the overdamped model is the wrong
tool for a kinetic bound state), but it does NOT support it either.

Honest scope: overdamped gradient-flow on L=32 over 6000 steps; parameter-
dependent; not a Hubble time. The screening GAMMA=0.04 (range ~1.6 cells) did not
prevent the strong-coupling global collapse.
