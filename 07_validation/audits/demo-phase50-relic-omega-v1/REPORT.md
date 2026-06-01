# REPORT — demo Phase-50: Ω_DM from the un-packing — achievable but fine-tuned

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase50_relic_omega_calc.py`
Verdict: **OMEGA_DM_IS_ACHIEVABLE_BUT_FINE-TUNED** (standard PBH abundance sensitivity)

Runs the reduced perturbation + Press-Schechter PBH abundance calculation to get
Ω_DM as a function of the matter-era duration N_m (the reheating-timing knob).

- **T1 — Ω_DM vs spectrum amplitude.** Ω_DM ≈ 0.26 when the spectrum reaches
  **δ_final ≈ 0.138** at the PBH scale; below → underproduce, above → overclose.
- **T2 — Ω_DM vs matter-era duration.** δ_final = σ_seed·e^(N_m) → Ω_DM=0.26 needs
  **N_m = 12.60 e-folds** — comfortably within the ~37 available (Phase 49). So NO
  shortage; the un-packing generically TENDS TO OVERPRODUCE.
- **T3 — sensitivity.** dln(Ω)/dN_m = δ_c²/δ² = **11**: a change of only **0.094
  e-folds** shifts Ω by a factor e; ~0.13 more e-folds → overclose. The abundance
  is doubly-exponentially sensitive — the WELL-KNOWN fine-tuning of all PBH-DM
  scenarios.

**Honest verdict.** The QNG un-packing produces dark matter abundantly and Ω_DM =
0.26 is achievable, but it is NOT a parameter-free prediction — it requires the
reheating epoch tuned to ~0.1 e-fold, which QNG does not fix from deeper dynamics.
Same predictive boundary every PBH-DM model hits.

**Net over the program (Phases 38–50):** QNG gives a COMPLETE, self-consistent,
CMB-consistent dark-matter story — WHAT it is (neutral cold ~3µg Planck relic /
degenerate core), HOW it forms (un-packing → matter era → PBHs → evaporation →
relics), WHY it returns black-hole information — with a single remaining
un-predicted number (Ω_DM), exponentially sensitive to reheating timing, exactly as
in standard PBH cosmology. A fully-articulated candidate, not a derivation of the
cosmic abundance.
