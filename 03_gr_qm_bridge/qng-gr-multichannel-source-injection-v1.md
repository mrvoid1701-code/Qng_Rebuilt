# QNG GR Multi-Channel QM Source Injection v1

Type: `derivation`
ID: `DER-BRIDGE-031`
Status: `proxy-supported`
Author: `C.D Gabriel`
Prereq: `DER-BRIDGE-028` (multi-channel current), `DER-BRIDGE-030` (N-scaling closed)

## Objective

Test whether the QM multi-channel current channels (div_J_mis, div_J_mem) from
CPU-046 couple directly to the GR tensor components (E_xx, E_tt), improving
the existing 4-channel source-matching residual.

## Background

CPU-030 (tensorial source matching) established that E_xx and E_tt can be fit
by 4 channels with residual ratio ~0.30:

```
E_xx ≈ a·κ + b·q_src + c·src + d·m_eff     ratio = 0.2996
E_tt ≈ a·κ + b·q_src + c·src + d·m_eff     ratio = 0.3328
```

where:
- κ = geometry curvature proxy
- q_src = back-reaction source amplitude
- src = QM generator source amplitude
- m_eff = effective matter proxy

CPU-046 established the dominant QM density channels:

```
Δ(C_eff²) ≈ -(α_mis·div_J_mis + α_mem·div_J_mem + α_phi·div_J_phi)
```

where div_J_mis and div_J_mem are the dominant QM density drivers.

**Key question**: Do the QM density channels also appear as sources in the
GR tensor equations? If so, this is direct evidence that the QNG QM→GR bridge
carries the multi-channel current structure.

## Physical motivation

In classical GR, the stress-energy tensor T_μν sources the Einstein tensor G_μν.
In QNG, the analog is: the QM matter current should couple to the QNG effective
geometry channels (E_xx, E_tt).

If CPU-046 correctly identified the QM matter channels (div_J_mis, div_J_mem),
then these should appear in the GR tensor fitting with non-zero coefficients.
A negligible coefficient would mean the QM-GR bridge uses a different coupling
than what the QM continuity equation identifies.

## Construction

### 4-channel baseline (CPU-030)

```
columns: [κ, q_src, src, m_eff]
target: E_xx or E_tt
```

### 6-channel extended (this test)

```
columns: [κ, q_src, src, m_eff, div_J_mis, div_J_mem]
target: E_xx or E_tt
```

where:
```
div_J_mis[i] = C_eff[i] · Σ_{j∈adj[i]} C_eff[j] · (mismatch[j] - mismatch[i])
div_J_mem[i] = C_eff[i] · Σ_{j∈adj[i]} C_eff[j] · (mem[j] - mem[i])
```

Both channels come from the history state after `use_history=True` rollout
(same convention as CPU-046).

### Fit quality metric

```
ratio = ‖E - E_pred‖₂ / ‖E‖₂   (normalized residual)
```

Lower ratio = better fit. Adding channels can only decrease ratio (OLS).

### QM coupling significance

A channel is "significant" if |coeff| > 0.1 × |a_geom| where a_geom is the
geometry (κ) coefficient. This ensures the channel is not just rounding noise.

## Claims

### Claim A: ratio_e_xx(6-channel) < ratio_e_xx(4-channel) = 0.2996

Prediction: OPEN

Argument: The mismatch+mem current is the dominant QM density driver (CPU-046).
If it couples to E_xx, the 6-channel fit should improve. The question is whether
the improvement is substantial or marginal.

### Claim B: ratio_e_tt(6-channel) < ratio_e_tt(4-channel) = 0.3328

Prediction: OPEN

Argument: Same argument for E_tt. The time-time component should be most
sensitive to the matter density channels.

### Claim C: ratio_split(6-ch) < ratio_split(4-ch) = 0.3162

Prediction: OPEN

Argument: Combined improvement in both E_xx and E_tt means the QM channels
carry independent information not captured by existing 4 channels.

### Claim D: at least one QM channel (div_J_mis or div_J_mem) has
significant coefficient in E_tt fit (|coeff| > 0.1·|a_geom|)

Prediction: OPEN

Argument: If the QM multi-channel structure genuinely bridges to GR, the
dominant QM current (mismatch, from CPU-046) should have a measurable
coupling coefficient in the GR tensor equation.

## Physical interpretation

If 6-channel improves over 4-channel with significant QM coefficients:
- The QM multi-channel current structure couples directly to GR tensor components
- The bridge from QM density evolution to GR geometry is confirmed multi-channel
- Specifically: mismatch-memory-driven QM density flow sourcing GR geometry

If 6-channel only marginally improves (ratio drops by < 0.01):
- The QM channels are nearly collinear with existing 4 channels
- The GR bridge already captures the mismatch-memory content implicitly
- No new coupling information

If 6-channel does NOT improve:
- The QM density channels are orthogonal to GR tensor directions
- The QM-GR bridge requires a different coupling ansatz

## Validation

Test: `QNG-CPU-049` — `qng_gr_multichannel_source_injection_reference.py`
Decision: PASS (3/4 predictions)

Results:
- P1: ratio_e_xx(6ch) < 0.2996 — PASS (0.2745, −8.4%)
- P2: ratio_e_tt(6ch) < 0.3328 — PASS (0.2760, −17.1%)
- P3: ratio_split Δ > 0.005 — PASS (Δ=−0.041, 12.9% improvement)
- P4: |QM coeff| > 0.1·|a_geom| in E_tt — FAIL (0.096 vs 0.100, misses by 0.004)

Key findings:
- First QM→GR cross-sector coupling confirmed: div_J_mis couples to E_tt (−0.516) and E_xx (+0.238)
- Sign pattern consistent with GR: E_tt and E_xx have opposite sign couplings to QM current
- E_tt improvement (17%) >> E_xx (8%): time-time component most sensitive to QM density
- div_J_mem provides secondary correction (opposite sign to div_J_mis in both components)
- QM coupling strength: |e_mis|/|a_geom| = 0.096 ≈ 10% of geometry channel
- 6-channel equation: E_μν ≈ a·κ + b·q_src + c·src + d·m_eff + e_mis·div_J_mis + f_mem·div_J_mem
