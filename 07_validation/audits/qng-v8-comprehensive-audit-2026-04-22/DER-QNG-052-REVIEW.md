---
id: REVIEW-QNG-052
type: note
title: Internal review of DER-QNG-052 (V9-C Weyl lift)
date: 2026-04-22
reviewer: main-assistant (not savant-physics-reviewer)
scope: self-audit of own draft for factual/algebraic issues before v9 decision
---

# Review of DER-QNG-052 — Issues found

## 1. §2 — Minor, correct in substance

Claim: "Neighbor-cos terms involve only commuting operators at distinct
sites."

Check: `[phi_i, phi_j] = 0` for `i ≠ j`, `[sigma_m_i, sigma_m_j] = 0` for
`i ≠ j` — correct. No Weyl-ordering ambiguity in `E_phi_R1` or the
quadratic `E_v7` neighbor terms. `V_couple` is a function of commuting
operators (`sigma_m_i, phi_i` at the same site — but no momentum
operators enter). OK.

## 2. §4 — Central argument needs sharper statement

Current text: "Therefore V9-C is NOT Madelung + noise; Wallstrom 1994
does not apply."

This conflates two points:

- **Scope**: V9-C is canonical path-integral quantization of a classical
  Hamiltonian. Wallstrom's 1994 theorem specifically targets Madelung
  hydrodynamics (ρ, S) + classical noise on (ρ, S) as the reconstruction
  substrate. V9-C does not start from (ρ, S); it starts from (q, p) with
  Weyl ordering. So Wallstrom's no-go is inapplicable by scope — this is
  a statement about what V9-C isn't.

- **Mechanism**: the positive statement is: integer winding enters the
  spectrum via the topological sector decomposition `Z = Σ_n Z_n`, where
  `n ∈ H^1(T^3, Z) = Z^3` for periodic BC. Within each sector, `phi`
  is single-valued (after a branch cut), and canonical quantization is
  standard. The quantization condition `∮ dφ = 2π n` is structural (from
  the cohomology), not enforced by dynamics or noise.

**Recommendation**: split §4 into §4a (scope) and §4b (mechanism).
Currently reads as if topological decomposition is the reason Wallstrom
doesn't apply, when actually Wallstrom is inapplicable independently,
and the sector decomposition explains how winding quantum numbers enter.

## 3. §6 — Tree-level dispersion factor check

Current formula:
`omega^2(k) = (beta_R1 / (2 mu_phi z)) * 4 sum_mu sin^2(k_mu/2)`

Direct derivation from `H = pi^2/(2 mu_phi) + V` with
`V = -(beta_R1/z) sum_<ij> cos(phi_i - phi_j)`:

- Expand `cos` to quadratic: `V ~ (beta_R1/(2z)) sum_<ij> (phi_i - phi_j)^2`
- Hamilton eqs give `phi_ddot_i = (beta_R1/(z mu_phi)) sum_{j~i} (phi_j - phi_i)`
- Plane wave: `omega^2 = (beta_R1/(z mu_phi)) * 4 sum_mu sin^2(k_mu/2)`

My derivation gives `4 beta_R1/(z mu_phi)`; the document has
`4 * beta_R1/(2 z mu_phi) = 2 beta_R1/(z mu_phi)` — factor of 2 off.

**Suspect**: convention on whether `<ij>` double-counts. The document's
`E_phi_R1 = -(beta_R1/z) sum_<ij> cos(...)` with `<ij>` unordered
matches a prefactor `beta_R1/z` in the Lagrangian-density sense. If the
code in `qng_v8_canonical_gpu.py` uses `-(BETA_PHI/(2z)) sum_i sum_{j~i}`
(double-counted), then `beta_R1 = BETA_PHI` (not BETA_PHI/2). The
derived `c_phi^2 = K_BACK * BETA_G / 6 = 0.00583` from
DER-QNG-042-prereqs is set by `mu_phi = 0.857` — and the correct check
is whether **that** `c_phi` matches the GPU-020 Stage A measurement
(it does, within 2%).

**Action**: add a footnote in §6 pinning the convention. The GPU data
is the ground truth; this is a convention-tracking issue, not a physics
error.

## 4. §7 — One-loop corrections: sketch only

The claim that sigma_m self-energy from phi loops is
`Sigma_{sm}(k) ~ g^2 * hbar * integral d^3k' / (beta_R1/z k'^2 + m_phi^2)`
is dimensionally correct but is a leading-order Feynman rule
application. The one-loop is schematically fine but no finite result
is presented.

**Action**: this is acceptable for a v1 draft, but a v2 should compute
at least the UV log coefficient explicitly to check renormalizability.
Critical for falsifier (B) in §10.

## 5. §10 falsifiers — well-stated

(A) V9-A promotion to theta-quantized: unambiguous.
(B) UV renormalizability at one loop: falsifier is clear.
(C) Tree-level matching to GPU-020 Stage A: deferred until R1 dispersion
runs under the new A1 sub-stage (R1 applied 2026-04-22 in canonical
module). Expected to PASS trivially.

## 6. Overall

Draft is sound in architecture. Three items to tighten before promoting
V9-C to "active residual path":

- [ ] §4: split into scope + mechanism
- [ ] §6: convention footnote on `beta_R1` definition + numerical check
  against GPU-020 Stage A (now A1 sub-stage per R1)
- [ ] §7: compute explicit UV log for phi self-energy

None of these change the conclusion. DER-QNG-052 stands as v1 draft.
Tightenings belong in v2 after V9-A verdict arrives.

## Connection to pre-check (PRECHECK.md)

The V9-A Berry-integral pre-check shows within-R CV > 10% for all four
candidates at R=3 and R=4. If R=5 confirms, overall V9-A verdict is
MARGINAL/FAIL, DER-QNG-052 becomes the load-bearing residual. The v2
tightening above should be prioritized under that scenario.
