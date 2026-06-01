# Decision: χ evolution equation in v8 — keep legacy v7 drive or promote to strict Hamilton's equation?

Type: `decision`
ID: `DEC-QNG-005`
Status: `proposed` (open for C.D Gabriel review; default = DEFER per §6)
Author: `C.D Gabriel` (drafted by Claude, Opus 4.7)
Date: `2026-04-21`

---

## Context

Audit Finding #12 (`07_validation/audits/qng-channel-audit-2026-04-21/REPORT.md`)
flagged that `drive_chi_v7style` in `tests/gpu/qng_v8_canonical_gpu.py` is NOT
the canonical Hamilton equation that the v8 derivation DER-QNG-036 §4.3
would demand.

Code form (legacy v7):
    dχ/dt = −chi_decay · χ + CHI_REL · (σ̄_g − σ_g) + DELTA_CHI · (σ_g_ref − σ_g)

Canonical Hamilton form implied by E_v7 §2.3:
    dχ/dt = −∂H_v8 / ∂σ_g   (uses ALPHA, BETA_G, CHI_REL, DELTA_CHI all consistently)

The two forms differ most visibly in the relative weighting: the code's
DELTA_CHI=0.20 plays the role of an "effective α" but the Hamiltonian's
E_A_g uses ALPHA=0.005 — a 40× mismatch.

## Evidence

| Measurement                                                | Value       |
|------------------------------------------------------------|-------------|
| H drift, k_gm=0, chi=0 (Channel A residual, GPU-030d)      | 6.1 %       |
| H drift, k_gm=0.1, chi perturbed 5 %, T=20 lu (GPU-030e)   | 8.2 %       |
| Excess attributable to Finding #12                         | 2.1 %       |
| Typical χ amplitude in Einstein correspondence runs        | O(10^{−2})  |
| Typical k_gm in those runs                                 | 0.05 − 0.10 |

Measured excess is small enough that **DER-QNG-044 Einstein correspondence
verdicts are not materially biased** by Finding #12 in the scan regime.

## Options

### Option A — Keep v7 drive, accept as "effective sub-theory"

Leave `drive_chi_v7style` unchanged. Document explicitly in DER-QNG-036
that the χ evolution in v8 code is a v7 gradient-flow drive, not a strict
Hamilton equation; introduce the symbol `H̃_v8` (quasi-H) and note that
|d H̃_v8 / dt| is bounded but non-zero at O(few %).

**Pros**:
- Zero code change → preserves all existing Einstein correspondence results,
  all GPU-029/030 traces, all CPU-076 calibration values.
- Matches the v7 substrate philosophy: (σ_g, χ) is the "gravitational
  sector" whose dynamics were never meant to be fully symplectic —
  χ is a memory field, not a canonical momentum in v7.
- v7-symmetric back-reaction (CPU-073) is already defined relative to
  this drive.

**Cons**:
- Any paper claim of "v8 is a strictly Hamiltonian theory" needs a
  footnote that the (σ_g, χ) sector is treated as an external bath.
- Long-run conservation gates (T > 100 lu) will fail G1 for non-Channel-A
  reasons; we'd need to widen the gate in (σ_g, χ)-active runs.

### Option B — Promote (σ_g, χ) to strict Hamilton pair

Replace `drive_chi_v7style` with `dχ/dt = −∂H_v8/∂σ_g`, where the derivative
is taken from the full patched `hamiltonian_v8` (which now includes E_chi
cross-terms). Rename `drive_chi_v7style` → `drive_chi_legacy` and retain
behind a flag for regression.

**Pros**:
- Strict Hamiltonian structure across all four (+1) sectors.
- Long-run G1 gates become meaningful again.
- DER-QNG-036 §4.3 becomes a theorem of the code, not an aspiration.

**Cons**:
- **DELTA_CHI=0.20 is load-bearing** — CPU-064 (Gap 8) was closed
  by choosing CHI_DECAY=0.020 against this 40× DELTA_CHI. Shrinking
  DELTA_CHI to ALPHA=0.005 in the canonical form removes the Gap 8
  fix. Need either (a) re-derive the stability bound with new form,
  or (b) keep DELTA_CHI but rebalance ALPHA upward (shifts every
  calibration since DER-QNG-019).
- Einstein correspondence probes (DER-QNG-044) must be re-run; values
  may shift by more than the 2.1 % Finding-#12 excess because the
  equilibrium itself changes.
- v7-symmetric back-reaction (CPU-073) must be re-derived from the
  new Hamilton equation; CPU-073 "extra drift 1.01 lu" result may shift.

### Option C — Parallel publish, defer unification

Treat v7 (gradient-flow (σ_g, χ)) and v8 (symplectic (σ_m, π_m, φ, π_φ))
as **two separate theories** with a shared (σ_g) field. Claim Hamiltonian
structure for the v8 matter sector only; document that the v7 gravitational
sector is a separate limit. Plan a v9 (DER-QNG-060+) that unifies both
in a strict Hamilton form.

**Pros**:
- Honest about the current scope: the paper's "v8 is canonical" claim
  is restricted to the matter sector where it is now exact (post-R1).
- No code churn, no calibration re-derivation.
- Lets DER-QNG-044 Einstein correspondence stand as "v7-gravity +
  v8-matter" joint prediction.

**Cons**:
- Slightly weakens the marketing: "joint v7-gravity/v8-matter" is less
  crisp than "v8 canonical".
- Creates an open future derivation (v9 unification).

## Recommendation

**Default: Option C (parallel publish, defer to v9).**

Reason: Finding #12 impact is bounded (2.1 % excess at the relevant scan
amplitudes), and the cost of Option B is disproportionately high (Gap 8
re-close, all DER-QNG-038 calibrations at risk). Option C pays the smallest
price today, keeps the theory honest, and leaves v9 as a clean research
program: "make (σ_g, χ) strictly canonical and re-close Gap 8 under the new
stability criterion." Current theoretical capital (baryon ladder, Einstein
correspondence, Lorentz) is not at risk.

Option A is equivalent to Option C at the paper level — the distinction is
whether the v8 derivation document is amended now (A) or a new v9 document
is begun (C). Prefer C because it makes the unification a named open program
rather than a caveat.

**Condition for revisiting**: if any Einstein correspondence probe at
larger k_gm (> 0.2) or larger χ amplitude (> 0.1) shows |dH/H| > 15 %,
escalate to Option B.

## Actions if accepted (Option C)

1. Annotate DER-QNG-042 (`qng-v8-canonical-extension-v1.md`) with scope
   note: "Canonical Hamiltonian structure is asserted for (σ_m, π_m) and
   (φ, π_φ); the (σ_g, χ) sector is inherited from v7 DER-QNG-036 as a
   gradient-flow sub-theory. See DEC-QNG-005."
2. Add Gap 11 to `08_governance/hard-open-problems-v1.md`:
   "Gap 11 (χ canonicalization): produce v9 substrate in which
   (σ_g, χ) is a strict Hamilton pair and Gap 8 is re-closed in the new
   stability criterion."
3. Reference this decision from `THEORY_STATE.md` structural-gaps list.
4. No code change to `drive_chi_v7style`.

## Pre-registration impact

None. Existing pre-registrations remain valid under Option C. New v9
derivation will require its own test registration.

## Audit trail

- Audit report: `07_validation/audits/qng-channel-audit-2026-04-21/REPORT.md`
- Diagnostic (k_gm=0, chi=0):  `07_validation/audits/qng-v8-h-sector-decomp-v2/report.json`
- Diagnostic (k_gm=0.1, chi perturbed): `07_validation/audits/qng-v8-chi-canonical-sanity-v1/report.json`
- Memory index: `project_channel_audit_2026_04_21.md`, `project_gpu030d_e_phi_92pct.md`
