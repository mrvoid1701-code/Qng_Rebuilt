# QNG v8: Channel A (phi sector) as a canonical XY-model Hamiltonian term

Type: `derivation`
ID: `DER-QNG-050`
Status: `draft` (pencil work; pending numerical verification under GPU-031)
Author: `C.D Gabriel`
Date: `2026-04-21`

---

## Inputs

- `DER-QNG-033` — v7 two-field substrate (`qng-two-field-substrate-v1.md`), line 78:
  phi drive `BETA_PHI * wrap(pm_wmean - phi)` in uniform-σ_m limit.
- `DER-QNG-036` — v7 Hamiltonian (`qng-hamiltonian-v7-two-field-v1.md`), §2.4:
  E_phi = -(β_phi / z) · Σ_{i, j∈N(i)} σ_m_i · σ_m_j · cos(φ_i − φ_j).
- `DER-QNG-042` — v8 canonical extension (`qng-v8-canonical-extension-v1.md`):
  (σ_m, π_m) and (φ, π_φ) promoted to canonical pairs with μ_m=10, μ_φ=0.857.
- `DER-QNG-049` — Channel F as canonical Hamiltonian term.
- `GPU-030d` diagnostic (`07_validation/audits/qng-v8-h-sector-decomp-v2/report.json`):
  adding E_phi to the monitor absorbs 92 % of the apparent GPU-030 G1 FAIL;
  residual 6 % attributed to F_A being a uniform-σ_m approximation.

## Objective

Close the last non-canonical gap in the v8 matter sector: promote Channel A's
phi force (currently a small-angle / uniform-σ_m approximation) to the exact
derivative of E_phi from DER-QNG-036 §2.4, and include the corresponding
−∂E_phi/∂σ_m term in F_sm. This removes the 6 % residual H drift observed in
GPU-030d and makes the (σ_m, φ) pair strictly canonical.

## Status of the approximation

The code form (`force_phi_v8`, `tests/gpu/qng_v8_canonical_gpu.py` line 268):

    F_A_code_k = BETA_PHI · wrap(phi_wmean_k − φ_k)

where `phi_wmean_k = arg(Σ_{j∈N(k)} σ_m_j · e^{iφ_j})`. This is an effective
force that drives φ_k toward the σ_m-weighted circular mean of its neighbours'
phases. In the **uniform-σ_m, small-|φ_k−φ_j|** limit it equals the exact
canonical force derived from E_phi (shown below); outside that limit the
two forces differ at leading order in (σ_m − σ_m_ref) and at cubic order in
phase differences, and this deficit is what GPU-030d picked up as a 6 % H
drift under Yoshida4.

## Derivation

### 1. Start from E_phi (DER-QNG-036 §2.4)

Write the interaction as a double sum over edges e = {i, j} (with z the
coordination number and the convention that each unordered edge contributes
once):

    E_phi = −(β_DER / z) · Σ_{i, j∈N(i)} σ_m_i · σ_m_j · cos(φ_i − φ_j)

The double sum counts each edge twice (once as i→j, once as j→i), so the
symmetrised form is

    E_phi = −(2 β_DER / z) · Σ_{edges e={i,j}} σ_m_i · σ_m_j · cos(φ_i − φ_j)   (E)

This is the weighted XY model; β_DER is set below.

### 2. Canonical phi force F_A^exact

The Hamilton equation for φ is dπ_φ/dt = −∂H/∂φ. Differentiating (E):

    −∂E_phi/∂φ_k  =  −(2 β_DER / z) · σ_m_k · Σ_{j∈N(k)} σ_m_j · sin(φ_k − φ_j) · (−1)
                   =  −(2 β_DER / z) · σ_m_k · Σ_{j∈N(k)} σ_m_j · sin(φ_k − φ_j)

Define the σ_m-weighted complex neighbour vector

    Z_k ≡ Σ_{j∈N(k)} σ_m_j · e^{i φ_j} = R_k · e^{i Θ_k}

Then Σ_{j∈N(k)} σ_m_j · sin(φ_k − φ_j) = Im(e^{−iφ_k} · conj(Z_k))·(−1)
= R_k · sin(φ_k − Θ_k), and the exact canonical force is

    **F_A^exact_k  =  −(2 β_DER / z) · σ_m_k · R_k · sin(φ_k − Θ_k)**   (1)

### 3. Calibration of β_DER

In the uniform-σ_m limit σ_m_i ≡ σ_m_ref and for small |φ_k − Θ_k|,
equation (1) reduces to

    F_A^exact_k  ≈  −(2 β_DER / z) · σ_m_ref · R_k · (φ_k − Θ_k)

with R_k ≈ z · σ_m_ref. Therefore

    F_A^exact_k  ≈  −2 β_DER · σ_m_ref² · (φ_k − Θ_k)  =  −BETA_PHI · (φ_k − Θ_k)

matches the code form iff

    **β_DER = BETA_PHI / (2 · σ_m_ref²) = 0.06 / 0.50 = 0.12**   (2)

Relation (2) is the calibration used in the E_phi term just added to
`hamiltonian_v8` (DER-QNG-036 §2.4-compliant value). Numerical check
(GPU-030d): with (2), the patched monitor matches the external h_sectors
reference to 10^{−13} relative error.

### 4. Canonical σ_m back-reaction −∂E_phi/∂σ_m

Symmetric differentiation of (E) with respect to σ_m_k gives

    −∂E_phi/∂σ_m_k  =  (2 β_DER / z) · Σ_{j∈N(k)} σ_m_j · cos(φ_k − φ_j)
                    =  (2 β_DER / z) · Re(e^{−iφ_k} · Z_k)
                    =  (2 β_DER / z) · R_k · cos(φ_k − Θ_k)   (3)

Equation (3) is a **new term** for F_sm that the current `force_sm_v8` does
NOT contain. It is the σ_m analog of (1): phase coherence with neighbours
pulls σ_m up, phase disorder pushes σ_m down.

### 5. Uniform-σ_m consistency of the approximation

In the uniform-σ_m limit the XY mean-field result is R_k ≈ z · σ_m_ref and
Θ_k = φ_wmean,k. Expanding sin(φ_k − Θ_k):

- Code form has leading linear term BETA_PHI·(Θ_k − φ_k).
- Exact form (1) has leading term BETA_PHI·sin(Θ_k − φ_k), whose cubic
  correction is (BETA_PHI / 6) · (Θ_k − φ_k)^3.

For ring states |Θ_k − φ_k| ≤ π/z ≈ π/6, so the cubic error is of order
(π/6)² / 6 ≈ 0.046 of the linear piece — consistent with the 6 % residual
H drift observed in GPU-030d.

The σ_m-gradient in (3) vanishes by symmetry in the uniform-σ_m limit
(Σ_j σ_m_j cos… sums to a constant that drops out under σ_m → σ_m+δ
only if δ is uniform; **in a ring core σ_m is non-uniform, so (3) is a
non-trivial new force**). This is the second physical reason for the
GPU-030d residual.

## Consequences

1. Under the canonical forms (1) + (3) + existing E_F, the (σ_m, π_m, φ, π_φ)
   sub-system is strictly Hamiltonian. Combined with the symplectic Yoshida4
   integrator (DT = 0.025), |dH/H| should drop below 10^{−3} over T = 20 lu
   on cached rings. GPU-030 G1 gate becomes the exact test.

2. Ring equilibria computed under the code form (code-ring) will relax
   under the exact form (DER-QNG-050-ring) because F_sm picks up a new
   term. The magnitude of relaxation bounds how much of the CPU-074 and
   CPU-075 mass-ladder values (M_ring at T_P2=1000) depend on the exact
   vs. approximate F_A. Predict: <5 % shift, because Phase-2 ring
   formation is already in the uniform-σ_m limit away from the core.

3. Channel F (DER-QNG-049) and Channel A (this derivation) exhaust the
   canonical structure of the (σ_m, φ) pair in v7-substrate sense. The
   remaining known non-canonical piece is the (σ_g, χ) drive (Audit
   Finding #12) — orthogonal, addressed separately.

## Open work

- **R2-code-1**: patch `force_phi_v8` to return (1). Keep the code form
  available behind an `exact_a=False` kwarg for regression comparison.
- **R2-code-2**: add (3) to `force_sm_v8` under the same flag.
- **R2-test-1**: GPU-031 regression test — cached L=28 R=4 ring, T=20 lu,
  DT=0.01, channel_f=True, exact_a=True. Pass gate: |dH/H| < 10^{−3}.
- **R2-test-2**: re-run CPU-074/075 with exact_a=True, quantify M_ring
  shift. Expected: <5 %; if >10 %, DER-QNG-038 mass-ladder calibration
  must be re-examined.

## Pre-registration tracking

This derivation does NOT require a separate pre-registration — the test
is a re-run of the existing GPU-030 gate on the same cached ring, with
the exact_a flag toggled. Registered under QNG-GPU-030 amendment
(`07_validation/prereg/QNG-GPU-020.md`).

## Dependencies downstream

- DER-QNG-038 baryon ladder: re-validate under exact_a=True.
- DER-QNG-044 Einstein correspondence suite: Shapiro / bending probes
  use φ as a wave, so (1) vs code form affects the dispersion; expected
  shift is 2nd-order in wave amplitude, so probes are robust; worth a
  sanity run nevertheless.
