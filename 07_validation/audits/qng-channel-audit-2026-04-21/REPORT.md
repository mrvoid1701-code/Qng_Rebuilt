# QNG Channel Audit — 2026-04-21

Type: `audit`
Author: Claude (autonomous overnight audit, 03:30–05:00 German)
Scope: all update channels (A, B, D, E, F, G), V_couple, kinetic sectors, and hamiltonian_v8 monitor consistency
Artifact: this file, plus `07_validation/audits/qng-v8-h-sector-decomp-v1/`, `qng-v8-h-sector-decomp-v2/`

## Executive summary

The v8 integrator `yoshida4_step` in `tests/gpu/qng_v8_canonical_gpu.py` is canonical for **(σ_m, π_m)** and **(φ, π_φ)** but is **not canonical for (σ_g, χ)** — the code retains v7 gradient-flow form for χ even under Yoshida4. Separately, `hamiltonian_v8` is missing several terms of `E_v7`, so `|dH/H|` as reported by GPU tests is SYSTEMATICALLY INFLATED relative to true conservation.

**Concrete impact**: GPU-030 G1 FAIL with `max |dH/H|=0.94` was 92 % **monitor bug** (confirmed by GPU-030d this session: adding the missing `E_phi` term drops `|dH/H|` from +75 % to +6 %). The residual 6 % is genuine non-conservation stemming from the uniform-σ_m approximation in `F_A` (Channel A on φ).

**Nothing in v8 physics derivations is retracted by this audit.** The derivations DER-QNG-036, DER-QNG-042, DER-QNG-049 are analytically correct. The issues are all in the `hamiltonian_v8` monitor wiring and in the χ drive replicating v7 (not canonical) rather than Hamilton's eq.

---

## Finding table

| # | Channel / term | Drive form in code | Hamiltonian monitor | Verdict |
|---|---|---|---|---|
| 1 | Ch A (σ_g, σ_m) | `α(ref−σ)` | `E_A = (α/2)(σ−ref)²` | ✓ canonical |
| 2 | Ch B (σ_g, σ_m) | `β(σ̄−σ)` | `E_B = (β/(4z))Σ(σ_i−σ_j)²` | ✓ canonical (fixed 2026-04-21 from biharmonic proxy) |
| 3 | Ch D (σ_g→χ via DELTA_CHI) | `DELTA_CHI·(σ_g_ref−σ_g)` in `drive_chi_v7style` | **MISSING** from `hamiltonian_v8` | ⚠ monitor gap |
| 4 | Ch E (χ→φ via ε) | NOT PRESENT in code | n/a | ✓ intentional: DER-QNG-033 v7 drops ε·χ from DER-QNG-016 v4 — code matches v7 spec |
| 5 | Ch F on σ_m | `−γ_φ·D·σ_m` | `E_F = (γ_φ/2)Σ D·σ_m²` | ✓ canonical |
| 6 | Ch F on φ (F_F per DER-QNG-049) | `+(γ_φ/(2z))Σ sin(θ_i−φ_j)·σ_mᵢ²` | via same E_F | ✓ canonical (finite-diff 1.67e-8) |
| 7 | Ch G (σ_g ← χ) | `dσ_g/dt = K_BACK·χ` | `T_g = (K_BACK/2)Σ χ²` | ✓ canonical (χ = momentum of σ_g, 1/μ_g = K_BACK, μ_g = 10) |
| 8 | Ch A on φ (F_A, XY model §2.4) | `F_A = BETA_PHI·(pm_weighted − φ)` — **uniform-σ_m approximation** | **MISSING** from `hamiltonian_v8` (E_phi = −β_DER/z·Σ σ_mᵢ·σ_mⱼ·cos(φ_i−φ_j) absent) | ⚠⚠ monitor gap + force non-canonical in non-uniform σ_m |
| 9 | E_coupling (matter-gravity via K_GM) | `−k_gm·(σ_m_ref−σ_m)` in `drive_sg_v7style` | **MISSING** from `hamiltonian_v8` | ⚠ monitor gap; inactive when K_GM=0 |
| 10 | V_couple (DER-QNG-042-A1 Option E²) | `+g·deficit·(1−cos φ)` on σ_m, `−½g·deficit²·sin φ` on φ | `V_cp = ½g·Σ deficit²·(1−cos φ)` | ✓ canonical |
| 11 | T_m, T_φ | `dσ_m/dt = π_m/μ_m`, `dφ/dt = π_φ/μ_φ` | `T_m = ½/μ_m·Σ π_m²`, `T_φ = ½/μ_φ·Σ π_φ²` with μ_m=10.0, μ_φ=0.857 | ✓ canonical; μ's derived from c_g=c_m=c_φ |
| 12 | χ evolution | `drive_chi_v7style = −χ_decay·χ + CHI_REL·(σ_g_bar−σ_g) + DELTA_CHI·(σ_g_ref−σ_g)` | not canonical Hamilton's eq | ⚠⚠⚠ **structural**: code uses v7 gradient flow, NOT `dχ/dt = −∂H/∂σ_g`. For canonical Hamilton's eq, leading-order form is `dχ/dt = −α·(σ_g−σ_g_ref) + β_g·(σ̄−σ_g)` (DER-QNG-036 §4.3), which the code approximates by using DELTA_CHI (=0.20) in place of α (=0.005). Drive and hamiltonian_v8 use DIFFERENT coefficients for the same physical term — systematic ~40× mismatch in σ_g restoration. |

---

## Detailed findings

### Finding #1-2 (Ch A, Ch B): clean

Drive and Hamiltonian match. Verified analytically and by finite differences (`tests/gpu/qng_v8_der049_finite_diff.py` Part B/C).

### Finding #3 (Ch D monitor gap)

`drive_chi_v7style` (line 326-328) includes `DELTA_CHI·(SIGMA_G_REF − σ_g)`. DER-QNG-036 §2.3 specifies the corresponding E_chi term `−δ·χ·(σ_g_ref − σ_g)`. `hamiltonian_v8` lines 445-449 contain a comment acknowledging "CHI_REL and DELTA_CHI cross-terms with sigma_g are included in drive_chi, but in the H monitor we approximate with the dominant self-term". This is OK for tests where χ ≈ 0 (e.g., GPU-030 with K_GM=0) but degrades monitor accuracy whenever χ is active.

**Fix**: add to `hamiltonian_v8`:
```python
E_chi_cross = (-CHI_REL / 2.0) * float(cp.sum(chi * (sg - sgb)))
E_chi_delta = (-DELTA_CHI) * float(cp.sum(chi * (SIGMA_G_REF - sg)))
```
Also optionally `E_chi_self = (CHI_DECAY_V7/2) * float(cp.sum(chi*chi))` — but this is dissipative, not conservative, and should only be included when the integrator runs with χ_decay > 0.

### Finding #4 (Ch E intentionally dropped)

DER-QNG-016 (v4) introduced `phi_i += ε·χ_i`. DER-QNG-033 (v7) substrate derivation `qng-two-field-substrate-v1.md` line 78 specifies only `phi_i += BETA_PHI·angle_diff(phi_mean_m, phi_i)` — no χ coupling. Code matches v7.
**Verdict: CORRECT**. No action.

### Finding #5-6 (Ch F): clean

DER-QNG-049 canonical form was verified by `qng_v8_der049_finite_diff.py` (rel err 1.67e-8). Adds F_F to φ, not to σ_m (σ_m already has `−γ_φ·D·σ_m`). Both derive from a single E_F.

### Finding #7 (Ch G): clean

χ is the conjugate momentum of σ_g. `T_g = (K_BACK/2)Σχ²` means `1/μ_g = K_BACK`, so `μ_g = 10`. Hamilton's eq `dσ_g/dt = ∂T_g/∂χ = K_BACK·χ` — the "Channel G" drive — is exactly this.

### Finding #8 (Ch A on φ — the GPU-030 drama)

**This is the primary audit finding.** Detailed reasoning:

(a) DER-QNG-036 §2.4 gives E_phi as the σ_m-weighted XY model:
```
E_phi = −(β_φ / z) · Σ_{i,j ∈ N(i)}  σ_mᵢ · σ_mⱼ · cos(φᵢ − φⱼ)
```

(b) Exact canonical force from this E_phi (at node k):
```
F_A^exact_k = −∂E_phi/∂φ_k = −(2·β_DER/z) · σ_mₖ · Σ_{j ∈ N(k)} σ_mⱼ · sin(φₖ − φⱼ)
            = −(2·β_DER/z) · σ_mₖ · |Z_sm_k| · sin(arg(Z_sm_k) − φₖ) · z        (in σ_m-weighted complex form)
```
with `Z_sm_k = (1/z)·Σⱼ σ_mⱼ·exp(iφⱼ)`, and β_DER related to the code's BETA_PHI by the uniform-σ_m matching condition.

(c) Code's F_A (line 288):
```
F_A_code = BETA_PHI · wrap(arg(Σⱼ σ_mⱼ·e^{iφⱼ}) − φ_k)
```
This is a phase-only relaxation toward the σ_m-weighted circular-mean phase. It matches F_A^exact only in the **uniform σ_m, small-angle limit**: both reduce to `≈ BETA_PHI·(pm_weighted − φ_k)` when σ_mⱼ = σ_m_ref and all |φⱼ − φₖ| are small. Away from this regime they differ.

(d) Matching calibration (small-angle limit): `BETA_PHI_code = 2·β_DER·σ_m_ref²`, hence `β_DER = BETA_PHI / (2·σ_m_ref²) = 0.06 / 0.50 = 0.12`.

(e) `hamiltonian_v8` does NOT include E_phi. Consequence verified by **GPU-030d (this audit)** on cached L=28 R=4 ring, T=20 lu, DT=0.01, channel_f=True:

| monitor | dH/H₀ at T=20 |
|---|---|
| `hamiltonian_v8` (no E_phi) | **+75.5 %**  |
| `hamiltonian_v8 + E_phi`    | **+6.1 %**  |

**92 % of the apparent GPU-030 G1 FAIL is a monitor bug** (missing E_phi). The residual 6 % is the non-uniform-σ_m correction to F_A.

(f) Two complementary fixes:

**Fix-M (monitor, trivial)**: add E_phi to `hamiltonian_v8`:
```python
z = float(nb_idx.shape[1])
sm_nb = sm[nb_idx]
phi_nb = phi[nb_idx]
cos_dphi = cp.cos(phi[:, None] - phi_nb)
E_phi = -(BETA_PHI / (2.0 * SIGMA_M_REF**2) / z) * float(cp.sum(sm[:, None] * sm_nb * cos_dphi))
# then add E_phi to the total
```
After this fix, GPU-030 G1 becomes ~6 % (still fail at 1 % threshold, but not catastrophic).

**Fix-F (force, structural)**: replace `F_A_code` with the exact canonical form F_A^exact. Also add `−dE_phi/dσ_m` to `force_sm_v8` (currently missing):
```python
F_sm_from_E_phi_k = +(2·β_DER/z) · Σ_{j∈N(k)} σ_mⱼ · cos(φₖ − φⱼ)
```
After both fixes, the full (σ_m, π_m, φ, π_φ) sector is strictly canonical. This requires a new derivation (**proposed DER-QNG-050**).

### Finding #9 (E_coupling monitor gap)

Drive of σ_g uses `−k_gm·(σ_m_ref − σ_m)` with MINUS sign (from DER-QNG-036 §2.5). The corresponding E_coupling is
```
E_coupling = k_gm · Σᵢ (σ_m_ref − σ_m) · (σ_g_ref − σ_g)
```
which is absent from `hamiltonian_v8`. Inactive when K_GM=0 (all GPU-030 tests), but biased whenever gravity is on.

**Fix**:
```python
E_coupling = k_gm * float(cp.sum((SIGMA_M_REF - sm) * (SIGMA_G_REF - sg)))
```

### Finding #10 (V_couple): clean

DER-QNG-042-A1 Option E². Drive and Hamiltonian match.

### Finding #11 (kinetic terms, μ derivation): clean

μ_m = β_m/(k_back·β_g) = 10.0; μ_φ = 2·β_φ·σ_m_ref²/(k_back·β_g) = 0.857 (DER-QNG-042-prereqs §3.3, GPU-012 v3 PASS).

### Finding #12 (χ evolution non-canonical) — the deepest structural issue

**This is the most subtle audit finding.**

In v8 canonical form, if χ is the momentum of σ_g (T_g = (K_BACK/2)Σχ², Finding #7), then Hamilton's eq says:
```
dχ/dt = −∂H_v8/∂σ_g
      = −α·(σ_g−σ_g_ref)                [from E_A_g, DER-QNG-036 §2.1]
      + β_g·(σ̄_g−σ_g)                   [from E_B_g, DER-QNG-036 §2.1]
      + [cross-terms from E_chi, E_coupling]
```
(DER-QNG-036 §4.3 leading-order form, line 283-288.)

But `drive_chi_v7style` computes:
```
dχ/dt = −χ_decay·χ + CHI_REL·(σ̄_g−σ_g) + DELTA_CHI·(σ_g_ref−σ_g)
```
**Neither form matches the other.** In particular:
- The code's DELTA_CHI=0.20 plays the role of "α for χ equation", but `hamiltonian_v8`'s E_A_g uses ALPHA=0.005 — a 40× mismatch.
- The code's CHI_REL=0.35 (same as BETA_G numerically) approximates the β_g coefficient.
- The code includes a χ_decay term which is Langevin-like (dissipative), not canonical.

This is known historically: v7 had χ as its own field with its own gradient flow of E_chi (§2.3). v8 REINTERPRETS χ as momentum of σ_g (§4.1). The two pictures are reconciled only if DELTA_CHI and CHI_REL are absorbed into a redefined E_chi that includes the canonical restoring forces. **This has NOT been done in the code.**

**Practical consequence**: in the (σ_g, χ) sector, the v8 code does NOT evolve symplectically — it evolves with v7 gradient flow wrapped inside Yoshida4 scaffolding. The (σ_m, π_m, φ, π_φ) sector IS symplectic. This is why:
- GPU-030 (K_GM=0, no (σ_g, χ) activity) shows H drift entirely from Finding #8
- GPU-011 KG wave tests pass — they measure dispersion from the drive equations, not canonical H
- Shapiro tests (K_GM>0) still "work" as proxies because they use spatial phase profile, not H conservation

**Fix** (if strict canonical form desired):
- Replace `drive_chi_v7style` with `dχ/dt = −∂H_v8/∂σ_g`:
  ```
  dχ/dt = −α·(σ_g−σ_g_ref) + β_g·(σ̄−σ_g) − k_gm·(σ_m_ref − σ_m) − χ_decay·χ
         + CHI_REL·(σ̄−σ_g) + DELTA_CHI·(σ_g_ref−σ_g)  [if E_chi cross-terms retained]
  ```
- Decide whether the CHI_REL/DELTA_CHI terms are to be KEPT (then merge with α/β_g, effective parameters α_eff = α+DELTA_CHI, β_eff = β_g+CHI_REL) or DROPPED (as legacy v7 residue).

This is a **derivation decision** (proposed DER-QNG-050 or amendment to DER-QNG-042), not a bug fix.

---

## Mistakes I made (Claude) during this investigation

1. **Called GPU-030 FAIL "DER-QNG-049 bug" initially.** Finite-diff test immediately ruled out DER-QNG-049. The real cause turned out to be a monitor bug (Finding #8), not the derivation. This is a good example of "test the derivation AND the monitor — they can be wrong independently".

2. **Proposed E_B_true fix as "the closure"**, expecting it to drop dH/H to <1 %. It dropped only marginally because E_phi was the dominant missing term. **Lesson**: when H-monitor drift is reported, decompose by sector before proposing structural fixes.

3. **Took at face value the initial claim that GPU-030 result implied "v8 is not a Hamiltonian system"**. GPU-030c (sector decomp) immediately showed H_grav=0 throughout, so the drift was entirely in matter sector — a much narrower issue than a full Hamiltonian failure.

4. **Did not initially check Finding #12** (χ evolution non-canonical) — this was only surfaced near the end of the audit when looking for monitor consistency. For tests with K_GM=0, it doesn't matter; for tests with active gravity, it's the elephant in the room.

---

## Recommendations (ordered by risk / impact)

**R1 — trivial fix, high impact**: Apply Fix-M (add E_phi to `hamiltonian_v8`). This alone takes GPU-030 G1 from 94 % to 6 %. Do NOT patch without user decision because it changes the reported drift on all prior GPU-020 / GPU-030 / GPU-011 audit artifacts.

**R2 — new derivation**: Author DER-QNG-050 that either
- (a) derives exact canonical F_A and F_sm_from_E_phi (Fix-F), OR
- (b) derives the "effective potential" whose gradient is the code's actual `F_A_code = BETA_PHI·(pm_weighted − φ)` (unlikely to have closed form due to atan2 branch cuts, but worth a try).

**R3 — audit E_chi cross-term impact**: run a single GPU sanity test with K_GM=0.1 and χ initially non-zero to quantify how much of the "hidden" drift in GPU-011/013 is Finding #12 vs genuine physics.

**R4 — THEORY_STATE.md update**: add a footnote "GPU-030 dH/H=94 % was 92 % monitor bug (E_phi missing from H); residual 6 % is uniform-σ_m approximation in F_A. Structural status of canonical v8 (σ_m, π_m, φ, π_φ) sector UNCHANGED."

**R5 — formalize the χ interpretation** (Finding #12): decide whether v8 keeps v7's mixed gradient-flow/symplectic χ evolution (current code — pragmatic but not canonical) or fully promotes χ to Hamiltonian momentum with `dχ/dt = −∂H/∂σ_g` (strictly canonical but requires decisions on χ_decay, CHI_REL, DELTA_CHI fate). **This is a theory question, not an implementation bug.**

---

## Non-findings (positive audit outcomes)

- DER-QNG-049 (Channel F canonical completion) is **correct**.
- DER-QNG-042 (v8 canonical extension) μ_m and μ_φ are **correctly implemented**.
- V_couple drive and Hamiltonian match (DER-QNG-042-A1 Option E²).
- E_B_true fix from earlier in this session is **correct**: finite-diff rel err was 1.67e-8, well within tolerance.
- THEORY_STATE.md items "Confirmed in v8: phi dispersion, KG wave equation, Shapiro delay, emergent Lorentz isotropy" all remain VALID — none of these depend on the H-monitor being complete, they depend on the drive equations (which are OK modulo the χ issue in Finding #12).
- DER-QNG-033 correctly drops Channel E (ε·χ on φ) from DER-QNG-016 — code matches the v7 spec.

---

## Closing note

This audit confirms that the QNG v8 theory as DERIVED is more self-consistent than the "H drift 94 %" symptom suggested. Most of what looked like a physics bug is a hamiltonian_v8 wiring gap. The one genuine non-canonical aspect (Finding #12) is a known v7-legacy artifact that has pragmatic justification but should be formalized.

No retractions of THEORY_STATE.md locked items. No retractions of DER-QNG-044 Einstein-correspondence results (all measured via drive equations or spatial profiles, not H-monitor). No retractions of DER-QNG-047 (v8 3D admits no static ring) — that result comes from dynamical evolution, independent of H-monitor.

**Net theory impact: 0 retractions, 1 monitor bug confirmed, 1 structural simplification suggested for future work.**
