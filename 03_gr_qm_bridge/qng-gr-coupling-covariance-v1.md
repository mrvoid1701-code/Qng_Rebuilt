# DER-BRIDGE-032 — QM→GR 6-Channel Coupling Covariance

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-028 (CPU-046), DER-BRIDGE-031 (CPU-049)

---

## Motivation

CPU-049 confirmed that adding div_J_mis and div_J_mem to the GR tensor fitting
improves E_xx and E_tt prediction on a single default seed. The cross-sector bridge:

    E_μν ≈ a·κ + b·q_src + c·src + d·m_eff + e·div_J_mis + f·div_J_mem

gave ratio improvements of −8.4% (E_xx) and −17.1% (E_tt), with div_J_mis as
the dominant QM coupler (|e_mis| > |f_mem|).

However, this result was obtained on a single topology (default seed). The
question is: are e_mis and f_mem Tier-1 universal (stable across all seeds) or
Tier-2 topology-dependent (vary with graph structure)?

---

## Theoretical claim

The QM→GR coupling is driven by mismatch-gradient divergence current (div_J_mis),
which measures local density flux induced by coherence mismatch between neighbors.
This flux couples to the time-time component of the GR tensor (E_tt) because:

1. E_tt ~ Laplacian(h_xx) tracks energy density accumulation
2. div_J_mis tracks QM energy-density outflow from each node
3. Physical consistency: ∇·J_matter ≈ −∂_t ρ in the linearized GR limit

This coupling is a local property of each node's neighborhood, independent of
global topology. Therefore:

**Hypothesis**: The 6-channel improvement and sign pattern of e_mis are universal
(Tier-1) across random graph topologies.

**Null hypothesis**: The improvement disappears or reverses on some seeds
(Tier-2 or noise).

---

## Mathematical structure

For each seed s, define:

    Δratio_s = ratio6_split_s − ratio4_split_s    (negative = improvement)
    sign_e_mis_s = sign(e_mis_ett_s)               (coupling sign in E_tt)
    dom_s = 1 if |e_mis_s| > |f_mem_s| else 0     (mismatch dominance)
    sig_s = 1 if max(|e_mis_s|,|f_mem_s|) > 0.1·|a_geom_s| else 0  (significance)

Tier-1 classification requires:
- Δratio_s < 0 on ≥ 4/5 seeds
- Consistent sign(e_mis_ett) on ≥ 4/5 seeds
- |e_mis| > |f_mem| on ≥ 4/5 seeds

---

## Predictions (pre-registered)

**P1 — Universal 6-channel improvement**:
    ratio6_split_s < ratio4_split_s on ≥ 4/5 seeds
    (= 6-channel beats 4-channel consistently)

**P2 — Mismatch dominance**:
    |e_mis_ett_s| > |f_mem_ett_s| on ≥ 4/5 seeds
    (div_J_mis is the primary QM coupler)

**P3 — Sign coherence of e_mis**:
    sign(e_mis_ett_s) is the same on ≥ 4/5 seeds
    (coupling direction is structural, not random)

**P4 — Significance threshold**:
    max(|e_mis_s|, |f_mem_s|) > 0.1·|a_geom_s| on ≥ 3/5 seeds
    (QM coupling is non-negligible relative to geometry)

Pass: ≥ 3/4 predictions confirmed
Partial: 2/4
Fail: ≤ 1/4

---

## Tier classification

If P1 + P3 both pass → Tier-1 (universal, topology-independent coupling)
If only P1 passes → Tier-1.5 (improvement universal but sign topology-dependent)
If P1 fails → Tier-2 (topology-dependent)

---

## Open questions not tested here

- Does the 6-channel improvement scale with N (tested separately in CPU-051)?
- Is there a phi-channel contribution to GR beyond div_J_mis?
- Can the coupling coefficient e_mis be predicted from graph topology?
