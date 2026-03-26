# QNG-CPU-059 Pre-Registration

**Status**: LOCKED
**Theory doc**: DER-BRIDGE-041 (qng-gr-lorentzian-buildup-v1.md)
**Date locked**: 2026-03-26
**Depends on**: QNG-CPU-058 (geometry/matter separation), QNG-CPU-033 (Lorentzian proxy)

---

## Question

Does the Lorentzian metric signature (corr(E_tt,E_xx) < 0, frac_htt_neg > 0.5)
emerge dynamically as the rollout evolves from step 1 to step 24? And does phi
synchronization drive this emergence?

---

## Setup

- Seeds: {20260325, 42, 137, 1729, 2718}
- N = 12, Steps = 1..24 (track full trajectory)
- Two tracks: with history (use_history=True), without history (use_history=False)
- At each step: capture c, phi, compute E_tt/E_xx/corr via assemble_linearized_metric
- Kuramoto order: r = |Σ_k exp(i·phi_k)| / N (complex amplitude magnitude)

---

## Pass criteria

| ID | Criterion | Threshold |
|----|-----------|-----------|
| P1 | \|corr(E_tt,E_xx)\| at step 24 > step 1 | ≥ 4/5 seeds |
| P2 | mean_t(\|corr_hist(t)\|) > mean_t(\|corr_nohist(t)\|) | ≥ 4/5 seeds |
| P3 | Pearson(r(t), \|corr(t)\|) across t > 0.2 | ≥ 3/5 seeds |
| P4 | Signature converges: \|corr_24\|−\|corr_12\| < \|corr_12\|−\|corr_1\| | ≥ 4/5 seeds |

---

## Expected outcomes

- P1: likely PASS — CPU-033 shows strong final-state signature; step 1 should be weaker
- P2: likely PASS — history amplifies signature (CPU-033: 331× amplification)
- P3: UNCERTAIN — phi sync drives E_tt pattern; Kuramoto order may or may not
  be the right measure of this
- P4: likely PASS — systems tend to converge; signature should plateau

---

## Audit output

- `07_validation/audits/qng-gr-lorentzian-buildup-reference-v1/report.json`
- `07_validation/audits/qng-gr-lorentzian-buildup-reference-v1/summary.md`
