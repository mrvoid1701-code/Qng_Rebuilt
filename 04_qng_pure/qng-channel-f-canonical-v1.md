# QNG v8: Channel F as a canonical Hamiltonian term

Type: `derivation`
ID: `DER-QNG-049`
Status: `draft` (pencil work; to be verified numerically)
Author: `C.D Gabriel`
Date: `2026-04-21`

---

## Objective

Resolve the Channel F coherence crisis exposed by GPU-029 pilot v1/v2:

- **Pilot v1** (cached ring + v8 symplectic, channel_f=False): violent
  quench, M_ring swings ±500, H grows 300%.
- **Pilot v2** (v8-native small-amplitude IC, channel_f=False): small
  perturbations disperse (variant A), or chaotic collapse (B/C).
- **Combined reading we wrote**: "Scenario A (bounded orbit) is dead;
  v8 + Channel F off has no particle-like excitation."

But the correct reading — exposed by reading `tests/gpu/qng_v8_canonical_gpu.py`:

1. `force_sm_v8` with `channel_f=True` adds `-GAMMA_PHI * disorder * sm`
   to F_sm.
2. `hamiltonian_v8` does NOT include a corresponding `E_F` term.
3. `force_phi_v8` does NOT include any Channel F back-reaction on phi.

⇒ Channel F as implemented is **neither a canonical Hamiltonian force
nor a pure gradient flow**. It is a one-sided dissipator that violates
detailed balance in the (σ_m, φ) pair.

When `channel_f=True` is used with Yoshida4, H drifts (Channel F adds
force without subtracting energy).
When `channel_f=False` is used with Yoshida4, the ring's stabilizer
is removed without replacement, and rings dissolve or explode.

**Neither mode tests whether v8 admits a canonical ring equilibrium.**
The correct test requires adding Channel F as a two-sided canonical
coupling, with E_F in the Hamiltonian and the corresponding φ-force
in force_phi_v8.

---

## Current (broken) implementation

```python
# force_sm_v8 (channel_f=True)
F_sm = ALPHA*(SIGMA_M_REF - sm) + BETA_M*(<sm>nb - sm)
     - GAMMA_PHI * disorder(phi, nb) * sm     # <-- Channel F
     + G_V_COUPLE * (SIGMA_M_REF - sm) * (1 - cos phi)

# force_phi_v8 (no Channel F contribution)
F_phi = BETA_PHI * wrap(phi_wmean - phi)
      - 0.5 * G_V_COUPLE * (SIGMA_M_REF - sm)^2 * sin phi

# hamiltonian_v8 (no E_F term)
H = T_g + T_m + T_phi + E_A_g + E_A_m + E_B_g + E_B_m + V_couple
```

disorder_i is defined as `max(0, 1 - |Z_i|)` with
`Z_i = (1/z) * sum_{k ∈ N(i)} exp(i * phi_k)`, a neighbourhood phase
coherence magnitude. In vacuum (uniform phi), |Z|=1 → disorder=0;
near a vortex singularity, |Z|<1 → disorder>0.

---

## Canonical form

Define

    E_F = (GAMMA_PHI / 2) * sum_i  disorder_i * sigma_m_i^2

Compute partial derivatives:

**∂E_F/∂σ_m_i**:
    ∂E_F/∂σ_m_i = GAMMA_PHI * disorder_i * sigma_m_i

So `F_sm_F_i = -∂E_F/∂σ_m_i = -GAMMA_PHI * disorder_i * σ_m_i` —
**matches the current implementation exactly**. ✓

**∂E_F/∂φ_j**:

disorder_i = 1 - |Z_i|  (when positive)
|Z_i| = sqrt(X_i^2 + Y_i^2)  with X_i = (1/z) sum_{k ∈ N(i)} cos φ_k,
                                    Y_i = (1/z) sum_{k ∈ N(i)} sin φ_k

∂|Z_i|/∂φ_j is nonzero only for j ∈ N(i). For such j:

∂X_i/∂φ_j = -sin(φ_j)/z
∂Y_i/∂φ_j = +cos(φ_j)/z

∂|Z_i|/∂φ_j = (X_i * (-sin φ_j) + Y_i * cos φ_j) / (z * |Z_i|)

Writing Z_i = |Z_i| e^{iθ_i} so X_i = |Z_i| cos θ_i, Y_i = |Z_i| sin θ_i:

∂|Z_i|/∂φ_j = (|Z_i| sin θ_i cos φ_j − |Z_i| cos θ_i sin φ_j) / (z * |Z_i|)
             = sin(θ_i − φ_j) / z

Therefore:

∂disorder_i/∂φ_j = -sin(θ_i - φ_j) / z    (for j ∈ N(i), disorder_i > 0)

And:

∂E_F/∂φ_j = (GAMMA_PHI / 2) * sum_{i: j ∈ N(i)} (∂disorder_i/∂φ_j) * σ_m_i^2
          = -(GAMMA_PHI / (2z)) * sum_{i ∈ N(j)} sin(θ_i - φ_j) * σ_m_i^2

So the **missing φ-force** is:

    F_phi_F_j = -∂E_F/∂φ_j
              = +(GAMMA_PHI / (2z)) * sum_{i ∈ N(j)} sin(θ_i - φ_j) * σ_m_i^2

where θ_i = arg(Z_i) is the local phase average around site i.

---

## Physical interpretation

The missing φ-force is an **order-alignment pressure**:

- Where σ_m is large (vacuum), the term pulls φ_j toward the local
  neighbourhood average θ_i — a restoring force for phase order.
- Where σ_m is small (ring core), the term is weak, so phi is free to
  wind.

Under v7 gradient flow this asymmetry was irrelevant (F_phi was
computed from different equations and the effect was handled by
Channel A/B on φ). Under v8 symplectic evolution, the force HAS to
be explicit in F_phi, because omitting it breaks detailed balance
between the (σ_m, π_m) and (φ, π_φ) sectors.

**Mechanism of ring stability, restated**:
- E_A_m favours σ_m = σ_m_ref (no deficit) — resists ring
- V_couple favours φ=0 (no winding) — resists ring
- E_F favours σ_m small in disorder regions AND phi aligned in
  ordered regions — FAVOURS ring (low σ_m in core, aligned phi outside)

The ring is a local minimum of total E iff E_F outweighs E_A_m +
V_couple in the relevant region of configuration space. This was
empirically true under v7 gradient flow (Channel F sustained the
ring); it remains to verify under v8 symplectic.

---

## Required code changes

### `hamiltonian_v8` (currently line ~376)

Add after `V_cp`:

```python
dis = disorder_gpu(phi, nb_idx)
E_F = 0.5 * GAMMA_PHI * float(cp.sum(dis * sm * sm))
return T_g + T_m + T_phi_kin + E_A_g + E_A_m + E_B_g + E_B_m + V_cp + E_F
```

### `force_phi_v8` (currently line ~268)

Add the F_phi_F_j term. Computation requires:
- θ_i = arg(Z_i) for each site i
- sum over j ∈ N(i) of sin(θ_i - φ_j) * σ_m_i^2

Implementation sketch:

```python
def force_phi_v8(sg, sm, phi, nb_idx):
    pm = phi_wmean_gpu(phi, sm, nb_idx)
    deficit = SIGMA_M_REF - sm
    F_A    = BETA_PHI * wrap_gpu(pm - phi)
    F_vcp  = -0.5 * G_V_COUPLE * (deficit * deficit) * cp.sin(phi)

    # ---- Channel F back-reaction on phi (NEW, DER-QNG-049) ----
    # theta_i = arg(Z_i)  computed from pnb unweighted mean
    pnb = phi[nb_idx]                                # shape (N, z)
    cos_mean = cp.cos(pnb).mean(axis=1)
    sin_mean = cp.sin(pnb).mean(axis=1)
    theta_i = cp.arctan2(sin_mean, cos_mean)         # shape (N,)

    # For each node j, sum over i ∈ N(j) of sin(theta_i - phi_j) * sm_i^2
    theta_nb = theta_i[nb_idx]                        # shape (N, z)
    sm_nb_sq = (sm[nb_idx]) ** 2                      # shape (N, z)
    F_F_j = (GAMMA_PHI / (2.0 * Z)) * (
        cp.sin(theta_nb - phi[:, None]) * sm_nb_sq
    ).sum(axis=1)

    return F_A + F_vcp + F_F_j
```

where `Z = z = 6` is the cubic lattice coordination number.

**Note**: when disorder_i = 0 (identically, before the max-clip), the
analytic formula above holds. At sites where disorder_i was clipped to
zero (|Z_i| > 1, which can't happen analytically but may happen
numerically), the φ-force should also be zero. Since |Z_i| ≤ 1 by
Cauchy-Schwarz, the clip is a numerical safety net, not a physics
cutoff — the analytic F_phi_F formula is correct everywhere.

---

## Test plan

1. **GPU-030**: cached L=28 R=4 ring + v8 symplectic + channel_f=True
   + corrected F_phi + updated H. Short run T=100 lu, DT=0.01. Check:
   - (a) `|ΔH/H_0| < 1%` over T=100 lu ⇒ canonical form is correct.
   - (b) `M_ring` stays in [100, 250] ⇒ ring is a Hamiltonian
     equilibrium (at least marginally stable).

2. If (a) passes but (b) fails: ring is NOT a local min of E under v8
   canonical; pivot to dynamic-orbit (Scenario A, revived) or higher
   dimensions.

3. If (a) fails: derivation error somewhere; debug gradient computation
   against finite differences.

4. If BOTH pass: the previous "ring dissolves" findings were artifacts
   of the broken Channel F implementation. DER-QNG-047 needs
   qualification ("no static ring under INCONSISTENT v8 + Channel F",
   not "no static ring under v8"), and the DER-QNG-044 Einstein
   correspondence picks up a new positive result (static particle
   confirmed, E=mc² reading reinstated).

---

## Scope

This derivation only covers Channel F on σ_m / φ. It does NOT cover:

- Channel F on σ_g or χ — those channels are currently inactive in v8
  (Channel G handles σ_g back-reaction separately).
- Chi_decay as a conservative term — separately dissipative, likely
  requires its own Langevin-like canonicalization (treat as thermal
  bath with temperature T, not a pure Hamiltonian term). Out of scope.

Lorentz invariance of E_F: disorder_i is a gauge-invariant coherence
norm, and θ_i is a gauge-covariant phase. E_F is manifestly scalar
under the φ → φ + const global shift and under spatial rotations
of the graph. Same Lorentz properties as E_B_g / E_B_m (the discrete
Laplacian terms). No new symmetry issues.

---

## Upstream / downstream

**Upstream**:
- `DER-QNG-026` — Channel F introduction (v5)
- `DER-QNG-033` — v7 two-field substrate
- `DER-QNG-042` — v8 canonical extension (does not yet include E_F)
- `DER-QNG-047` — no static ring in 3D (provisionally locked)
- `GPU-024d v2` — cached ring dissolves without Channel F
- `GPU-028` — no V_couple form rescues ring
- `GPU-029 pilot v1/v2` — v8 + channel_f=False fails in all tested IC

**Downstream (conditional on GPU-030)**:
- If GPU-030 PASS: reopen DER-QNG-047 with channel_f=False scope only.
  Ring-as-static-soliton returns to the table for v8 with canonical E_F.
- If GPU-030 PASS (partial — H conserved, ring still unstable): DER-QNG-047
  strengthened — not an implementation artifact; v8 structurally
  lacks ring equilibrium even with canonical Channel F.

---

## Status

**Draft**. Derivation is analytic; implementation + numerical
verification are the next steps.
