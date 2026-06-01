# Phase 13 (Drumul 3) — why the Stability Principle fixes ℏ but is blind to α

Type: `note` / `evidence`
Status: `RUN COMPLETE 2026-06-01 — honest no-go + redirection`
Probe: `demo-theory/tests/t_phase13_alpha_stability_probe.py`
Artifact: `07_validation/audits/demo-phase13-alpha-stability-v1/`

---

## The conscious attack (and why it is honest)

Drumul 3 = derive the gauge coupling α (Gap 17). The natural attack: the
Stability Principle *derived ℏ* — does it also fix α? Attacking "consciously"
means **testing whether the template can work**, not forcing the number 1/137.

The ℏ derivation worked because **ℏ enters the vacuum-energy balance linearly**:
`E_classical + (ℏ/2)Σω = 0` → ℏ unique. For α to be fixable the same way, the
**vacuum energy must depend on the coupling e**. Decisive test: does it?

## Result: **STABILITY_PRINCIPLE_BLIND_TO_ALPHA_EM** (proven, not assumed)

| Test | Result |
|---|---|
| Photon (massless) zero-point vs e (e = 0.01…10) | **245.669 — EXACTLY constant** |
| Massive (Higgsed) boson zero-point vs e (m=ev) | 264 → 382 → 985 — **depends on e** |

> The photon is **massless** (`ω_k = c·k`), so its zero-point energy
> `(ℏ/2)·2·Σω` is **independent of the coupling e** — verified across three
> decades of e, the free vacuum energy does not move. The coupling enters only
> the interaction `cos(φ−eA)` at **O(e²) loop level**, invisible to the
> free/quadratic vacuum that the Stability Principle balances.
>
> **Therefore the ℏ-template CANNOT derive α_em.** This is a genuine **no-go**,
> proven by direct computation — not a failure to find the number, but a proof
> that this particular principle is structurally blind to it.

## Why this is real progress on Drumul 3

It explains, precisely, **why α is harder than ℏ in QNG**:
- ℏ multiplies the zero-point energy **linearly** → vacuum balance fixes it.
- α (for the massless photon) is **invisible** to the vacuum balance → the same
  principle says nothing about it.

And it **redirects** Drumul 3 to where α actually lives — the **interacting
level**:
1. **RG fixed point** — does the QNG edge coupling flow to a fixed value? (This
   is the asymptotic-safety route; note Phase 11 already used the *running* of
   the coupling.)
2. **Anomaly / consistency** constraints (fix charge ratios; the overall scale
   needs more).
3. **Schwinger-Dyson self-consistency** of the interacting vacuum.
These are the genuine (hard) routes to α — the same ones open in QFT generally.
The point: **stop trying the ℏ-template for α_em; it is provably blind.**

## The asymmetry that IS exploitable (the tractable sub-target)

The contrast test shows: for **MASSIVE** gauge bosons (W/Z, Higgsed), the vacuum
energy **does** depend on the coupling (via `m ~ e·v`). So a **vacuum-stability
argument CAN have traction on the WEAK coupling** — once the Higgs VEV is in the
theory. This is a **separate, more tractable sub-target** than α_em:

> The Stability Principle is blind to α_em (massless) but **not** to the
> massive-sector couplings (W/Z masses depend on g and v). A gauge-sector
> stability/vacuum-balance argument is the right tool **there**, not for the
> photon.

## Honest status of Drumul 3 after Phase 13

- **α_em (1/137):** the ℏ-template is **ruled out** (this phase). It needs an
  RG-fixed-point / interacting principle — the genuine α problem, unsolved here
  and everywhere. **Not faked.**
- **Weak couplings (g, g′):** a vacuum-stability argument is viable in principle
  (massive → coupling-dependent vacuum), pending the Higgs VEV (v13 ontology).
- **Drumul 1 link:** the proton mass (Phase 12) is exact for α_s(M_P)≈0.0153; α_s
  runs (asymptotic free), so its UV value is the relevant input — an **RG-flow /
  fixed-point** question, consistent with the redirection above.

## Bottom line

Drumul 3 attacked consciously: the result is a **clean no-go** (the
ℏ-deriving Stability Principle is provably blind to α_em, because the massless
photon's vacuum energy is coupling-independent) plus a **precise redirection**
(α needs a fixed-point / interacting principle; the massive-sector couplings are
where vacuum-stability has traction). This is honest progress — it eliminates the
wrong approach and names the right one — without manufacturing the number 1/137.
