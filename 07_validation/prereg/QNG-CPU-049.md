# Prereg QNG-CPU-049

Type: `prereg`
ID: `QNG-CPU-049`
Status: `locked`
Author: `C.D Gabriel`
Theory: `DER-BRIDGE-031`

## Locked before run

This file is written and committed BEFORE running the test.
Predictions cannot be changed after execution.

## What is being tested

Whether the QM multi-channel current channels (div_J_mis, div_J_mem) improve
the GR tensor fitting (E_xx, E_tt) beyond the existing 4-channel baseline.

6-channel extended fit:
```
E_μν ≈ a·κ + b·q_src + c·src + d·m_eff + e·div_J_mis + f·div_J_mem
```
vs 4-channel baseline:
```
E_μν ≈ a·κ + b·q_src + c·src + d·m_eff
```

where:
- div_J_mis[i] = C_eff[i] · Σ_j C_eff[j] · (mismatch[j] - mismatch[i])
- div_J_mem[i] = C_eff[i] · Σ_j C_eff[j] · (mem[j] - mem[i])

Seed: 20260325 (default cfg), use_history=True

## Baseline values (from QNG-CPU-030)

- ratio_e_xx(4-ch) = 0.2996
- ratio_e_tt(4-ch) = 0.3328
- ratio_split_mean(4-ch) = 0.3162
- a_xx = +4.524  (geometry coeff, positive)
- a_tt = -6.689  (geometry coeff, negative)

## Locked predictions

### P1: ratio_e_xx(6-ch) < 0.2996

Rationale: Adding div_J_mis and div_J_mem (the dominant QM density channels
per CPU-046) can only decrease the OLS residual. A decrease confirms they carry
information orthogonal to the existing 4 channels.

### P2: ratio_e_tt(6-ch) < 0.3328

Rationale: Same argument. E_tt couples to the time-time stress-energy component,
which should be most sensitive to the QM density flow.

### P3: ratio_split(6-ch) < 0.3162

Rationale: If both E_xx and E_tt improve, the split mean improves.

### P4: at least one of |e_mis| or |f_mem| > 0.1·|a_geom| in E_tt fit

Rationale: A coupling coefficient above 10% of the geometry channel indicates
a physically significant QM→GR coupling, not just numerical rounding.

## Falsification conditions

- FAIL if ratio_e_xx(6-ch) ≥ 0.2996 and ratio_e_tt(6-ch) ≥ 0.3328
  (QM channels carry no new information for the GR tensor)
- NOTE: OLS can never increase ratio when adding more channels with the same
  training data — so P1 and P2 are guaranteed PASS by OLS properties UNLESS
  the 6×6 normal system is numerically singular. The real test is P4 (significant
  coupling) and the magnitude of improvement (P3).

## Important note on P1/P2

By OLS properties, adding any columns to a full-rank system can only decrease
or maintain the residual. Therefore P1 and P2 will always pass unless the
system is numerically degenerate. The scientifically meaningful predictions are:

- **P3**: Is the improvement substantial (not just numerical noise)?
- **P4**: Is at least one QM channel coefficient physically significant?

Threshold for "substantial improvement": ratio drops by > 0.005 (0.5 percentage points).
