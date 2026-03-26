# DER-BRIDGE-041 — Lorentzian Signature Buildup via Phi Dynamics

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-040 (CPU-058), QNG-CPU-033 (Lorentzian signature proxy)
**Addresses**: Problem 6 (Lorentzian signature recovery)

---

## Motivation

CPU-058 established that the Lorentzian signature is **phi-driven**, not ρ-driven.
The GR back-reaction on ρ does not change the metric signature — that signature
is encoded in the phase field phi.

CPU-033 established that:
- corr(h_tt, h_xx) ≈ −0.97 at the final rollout state (with history)
- History amplifies the discriminant 331× vs no-history
- frac_hxx_pos = 1.0 (all nodes spacelike), frac_htt_neg ≈ 0.69

But CPU-033 was a single static measurement at the final state. It did not answer:

**Does the Lorentzian signature emerge progressively as the rollout evolves?**

If signature emergence is a dynamical process driven by phi synchronization,
then corr(E_tt, E_xx) should monotonically increase in magnitude over rollout steps,
with the history-amplified version always stronger than the no-history version.

---

## Phi synchronization and signature

From CPU-040: the phase field phi achieves near-perfect synchronization with
history (sync_order > 0.94 universally) and anti-synchronization (structured
diversity) without history.

The mechanism proposed here:

1. As phi synchronizes through the rollout, it develops a spatially coherent pattern
2. This coherent phi pattern produces a correlated E_tt/E_xx pair via the metric assembly
3. The anticorrelation between E_tt and E_xx — the Lorentzian signature proxy — grows
   as phi becomes more ordered
4. History feedback (history.phase) stabilizes the phi pattern and thus stabilizes
   the Lorentzian signature (explaining the 331× amplification)

---

## Claims

### Claim A — Signature builds up dynamically

The Lorentzian anti-correlation |corr(E_tt, E_xx)| increases from step 1 to
step T=24 under the history-driven rollout:

    |corr_T| > |corr_1|   on majority of seeds

### Claim B — History amplifies signature throughout, not just at the end

At each step t, the history-driven metric anti-correlation exceeds the
no-history version:

    |corr_hist(t)| > |corr_nohist(t)|   on average across seeds and steps

### Claim C — Phi Kuramoto order correlates with signature buildup

At each step t, the Kuramoto order parameter r(t) = |Σ_i exp(i·phi_i)| / N
correlates with |corr(E_tt, E_xx)|(t) across seeds and time:

    Pearson(r(t), |corr(t)|) across seeds > 0   on majority of steps

(Higher phase synchrony → stronger Lorentzian signature)

### Claim D — Signature convergence

The signature converges to a plateau — |corr| stops increasing after some step t*:

    |corr_T| - |corr_{T/2}| < |corr_{T/2}| - |corr_1|   on majority of seeds

---

## Protocol

For each seed in {20260325, 42, 137, 1729, 2718}:

1. Run rollout step by step from t=0 to T=24 (with history)
2. At each step t: capture (c_t, phi_t), compute metric_diagnostics
3. Also run rollout without history from t=0 to T=24
4. At each step t: compute Kuramoto order r(t) = |Σ_k exp(i·phi_t[k])| / N
5. Track: corr(E_tt, E_xx)(t), frac_htt_neg(t), r(t)

Pass criteria:

- P1: |corr(E_tt,E_xx)| at step 24 > at step 1 on ≥ 4/5 seeds (signature builds)
- P2: mean(|corr_hist|) > mean(|corr_nohist|) across t=1..24 on ≥ 4/5 seeds
- P3: Pearson(r(t), |corr(t)|) > 0.2 on ≥ 3/5 seeds (phi sync → signature)
- P4: signature converges — |corr_24| − |corr_12| < |corr_12| − |corr_1| on ≥ 4/5 seeds

---

## Theoretical significance

**If P1+P2+P3 pass**: Lorentzian signature emerges dynamically from phi
synchronization. History feedback accelerates convergence. The mechanism for
Problem 6 is identified: **phi sync → metric anti-correlation → Lorentzian signature**.

**If P3 fails but P1+P2 pass**: Signature builds, but NOT through Kuramoto-type
phase synchrony — some other phi mechanism drives the signature.

**If P1 fails**: Signature does not build up over the rollout — the final-state
anti-correlation is not more pronounced than the initial one. The CPU-033 measurement
captures a fluctuation, not a built-up signal.

---

## Falsifiability

- P1 fails → signature is present from step 1 (initial condition effect, not dynamics)
- P3 fails → signature not driven by phi sync order; driven by local phi structure
- P4 fails → signature grows monotonically without saturation (no equilibrium)
