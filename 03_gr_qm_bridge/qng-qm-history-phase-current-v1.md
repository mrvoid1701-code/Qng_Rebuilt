# QNG QM History-Phase Current v1

Type: `derivation`
ID: `DER-BRIDGE-026`
Status: `proxy-supported` (informative negative: current form ruled out as bottleneck)
Author: `C.D Gabriel`
Prereq: `DER-BRIDGE-025` (Madelung amplitude)

## Objective

Test whether replacing `phi` with `history.phase` as the phase field in the
U(1) current construction improves the calibrated continuity balance.

## Background

QNG-CPU-043 (Madelung) concluded:

- Amplitude form (C_eff vs sqrt(C_eff)) is NOT the bottleneck for R²_calib
- Mean R²≈0.20 across seeds regardless of amplitude choice
- R²_max=0.572–0.580 on seed 137 only
- **Bottleneck: the phase gradient structure** `sin(phi_j - phi_i)`

Why phi is a poor phase gradient probe:

1. `phi` achieves near-perfect synchronization (sync_order > 0.94 universally)
2. Near-sync means `phi_j ≈ phi_i` → `sin(phi_j - phi_i) ≈ 0` for most pairs
3. Small phase differences → weak current signal → poor R²

What `history.phase` encodes:

- `history.phase[i]` = exponential moving average of `angle_diff(phi_new, phi_neigh)` at node i
- Decay rate: `hist_p_rate = 0.35` → fast-tracking memory of local phase mismatch
- It is the **accumulated phase gradient history** at each node
- It feeds back into phi update: `phi_new += phi_hist_gain * history.phase[i]`
- It feeds into C_eff: `0.20 * (1 + cos(history.phase[i])) / 2`

The key distinction:

- `phi` → actual angle, near-synchronized globally
- `history.phase` → local phase GRADIENT memory, captures residual mismatches
- `history.phase` has larger cross-node variance (it measures how much each node
  deviates from its neighborhood, not the absolute angle)

Hypothesis: `history.phase` used as the phase field gives a better current proxy
because it directly measures phase mismatch rather than absolute phase.

## Construction

### History-phase amplitude

```
ψ_hp_i = C_eff_i · exp(i · history.phase_i)
```

### History-phase density

```
ρ_hp_i = |ψ_hp_i|² = C_eff_i²
```

(same as standard — density unchanged, only phase field swapped)

### History-phase edge current

```
J_hp_{i→j} = Im(ψ_hp_i* · ψ_hp_j)
            = C_eff_i · C_eff_j · sin(history.phase_j - history.phase_i)
```

### History-phase div current

```
div(J_hp)_i = C_eff_i · Σ_{j∈neighbors(i)} C_eff_j · sin(history.phase_j - history.phase_i)
```

### Calibrated coupling (same estimator as CPU-042)

```
α*_hp = -Σ(Δ(C_eff²) · div(J_hp)) / Σ(div(J_hp)²)
R²_hp = 1 - Var(Δ(C_eff²) + α*_hp · div(J_hp)) / Var(Δ(C_eff²))
```

### Comparison metric

```
improvement_i = R²_hp[seed_i] - R²_std[seed_i]
```

where `R²_std` is the reference from QNG-CPU-042.

## Claims

### Claim A: R²_hp > R²_std on majority of seeds (≥3/5)

Prediction: OPEN

Argument: `history.phase` has larger cross-node variance than `phi` (near-synced).
Larger phase differences → larger `sin(...)` values → stronger current signal.
Whether this translates to better correlation with Δρ is the key test.

### Claim B: α*_hp > 0 on majority of seeds (≥3/5)

Prediction: OPEN

Argument: Same sign structure as standard. If `history.phase` gradients correlate
with density flow, sign should be positive. But sign-stability is not guaranteed.

### Claim C: cv(|α*_hp|) < cv(|α*_std|) (more universal coupling)

Prediction: OPEN

Argument: `history.phase` is topology-dependent (Tier-2 per CPU-040), so
universality may not improve. But the variance structure is different enough
to warrant testing.

### Claim D: mean R²_hp > 0.20 (beats Madelung benchmark)

Prediction: OPEN

Argument: If phase gradient hypothesis is correct, mean R² should increase.
The 0.20 bar is the mean Madelung/standard result.

## Physical interpretation

If R²_hp > R²_std universally, then `history.phase` — the accumulated local
phase mismatch memory — is the natural phase variable for the QNG continuity
equation, not the raw oscillator angle `phi`. This would mean:

- The effective quantum phase is gradient-memory, not absolute position
- The U(1) structure of QNG is built on local mismatch tracking, not global phase

If R²_hp ≤ R²_std, then the phase gradient structure is the bottleneck regardless
of which phase proxy is used, and a fundamentally different continuity approach
is needed (e.g., tensor-valued current, multi-step gradient, or operator-algebraic).

## Validation

Test: `QNG-CPU-044` — `qng_history_phase_current_reference.py`
Decision: FAIL (1/4 predictions — informative negative result)

Results:
- P1: R²_hp > R²_std on ≥3/5 seeds — FAIL (1/5 only: seed 1729)
- P2: α*_hp > 0 on ≥3/5 seeds — PASS (4/5)
- P3: mean R²_hp > 0.20 — FAIL (mean=0.1175)
- P4: max R²_hp > 0.50 — FAIL (max=0.3329)

Key finding: phi and history.phase are highly correlated (corr 0.84–0.97);
history.phase has 3–8x SMALLER variance than phi → smaller phase differences
→ weaker current signal → R²_hp < R²_std on 4/5 seeds.

Critical conclusion: The bottleneck for R²_calib is NOT the phase variable
choice (phi vs history.phase). Three diagnoses now ruled out:
1. Amplitude form — RULED OUT (QNG-CPU-043)
2. Scale mismatch calibration — ABSORBED by α*≈10⁻³
3. Phase variable choice — RULED OUT (QNG-CPU-044)
Remaining bottleneck: the current functional form J = C_i·C_j·sin(Δφ)
may be the wrong structure for QNG density flow.
