# VOID — first GPU-020 run under original V_couple (2026-04-19)

This audit is officially **VOID**.

## Reason

Run used the original DER-QNG-042 V_couple form:

```
V_couple = g * sigma_g * (1 - cos phi)
```

Stage A passed (flat-vacuum dispersion) but Stage B produced NaN at the
first ring separation (d=6). Post-mortem probes identified a structural
incompatibility:

- `dV/dsigma_g = g*(1-cos phi) >= 0` drains sigma_g monotonically on any
  phi-winding configuration. No v7 channel can oppose the drain.
- Probe `qng_v8_stability_probe.py`: sigma_g -> 0 at t ~= 1.5 in 6/6 configs
  (dt-independent, damping-independent).
- Probe `qng_v8_g_scan_probe.py`: 3/3 g values in Stage A window
  [0.190, 0.276] breach `SIGMA_G_MIN_ABORT = 0.025` at t ∈ [1.0, 2.0].

## Resolution

DER-QNG-042-A1 amendment (`04_qng_pure/qng-v8-option-e2-amendment-v1.md`)
replaces V_couple with Option E^2:

```
V_couple_E2 = (g/2) * (SIGMA_M_REF - sigma_m)^2 * (1 - cos phi)
```

Verified numerically sound in `qng-v8-stability-probe-v1/option_e2.log`
and `option_e2_drift.log`. The next GPU-020 attempt will be written to
`qng-v8-canonical-v2/` under Option E^2.

## Artifacts retained

- `run.log` — console output of the aborted run (Stage A PASS, Stage B NaN).

Do NOT cite this audit as valid evidence for any DER-QNG-042 prediction.
