# Phase 8 — the Eightfold Way from the SU(3) Skyrme baryon

Type: `note` / `evidence`
Status: `RUN COMPLETE 2026-06-01`
Probe: `demo-theory/tests/t_phase8_su3_eightfold.py`
Artifact: `07_validation/audits/demo-phase8-su3-eightfold-v1/`

---

## Result

Extending the v13 baryon (B=1 Skyrmion) to **SU(3) flavor** and applying the
Wess-Zumino constraint `Y_R = N_c·B/3 = 1` (with `N_c=3` from the edge-SU(3)
color of Phase 3, `B=1` from the Skyrmion of Phase 5) **selects exactly the two
lowest baryon multiplets**:

| Multiplet | SU(3) rep | dim | J | content | match |
|---|---|---|---|---|---|
| **Octet** | (1,1) | 8 | **½** | N, Λ, Σ, Ξ | ✓ observed J=½ baryons |
| **Decuplet** | (3,0) | 10 | **3/2** | Δ, Σ\*, Ξ\*, Ω | ✓ observed J=3/2 baryons |

The spin follows from the isospin of the `Y=1` state (octet I=½ → J=½; decuplet
I=3/2 → J=3/2). **This is the Eightfold Way**, reproduced from QNG's
edge-color + node-Skyrmion ingredients. Verdict: **EIGHTFOLD_WAY_FROM_SKYRME**.

## Scale-free mass STRUCTURE that comes for free (verified on PDG)

The multiplet structure also predicts scale-free mass *relations* (independent
of the absolute scale), which hold in nature:

- **Gell-Mann–Okubo (octet):** `2(m_N + m_Ξ) = 3m_Λ + m_Σ`.
  PDG: `2(939+1318)=4514` vs `3·1116+1193=4541` → **0.6% agreement**.
- **Decuplet equal spacing:** `Δ→Σ\*→Ξ\*→Ω` spacings = 153, 148, 139 MeV
  (≈ 147 ± 7) → **equal-spacing rule holds**; the bottom of the decuplet is the
  `Ω⁻` (I=0, Y=−2, J=3/2) — the famous Eightfold-Way prediction, present here as
  the decuplet's apex.

These are genuine, observed, scale-free consequences of the structure QNG-Skyrme
selects — they do **not** need ℏ or Gap 13.

## What this adds to the inventory

The baryon sector now reproduces **the full light-baryon multiplet structure**
(octet + decuplet, correct spins, correct membership, GMO + equal-spacing
relations) — not just the nucleon/Δ. QNG-Skyrme gives the Eightfold Way.

## Honest scope

- This is **representation theory + the Skyrme WZW selection rule** applied with
  QNG's `N_c` (edge-color) and `B` (Skyrmion). The multiplet *structure* is a
  genuine consequence; QNG supplies the two integers that drive it.
- **Intra-multiplet SPLITTINGS' magnitude** (how big the GMO spacing is) needs
  flavor-SU(3) breaking (the strange-quark mass) — not derived in QNG. The
  *relations* hold regardless; the *scale* of the splitting does not follow.
- **Absolute masses** still blocked (ℏ + Gap 13), as everywhere.
- Requires promoting v13 from SU(2) to **SU(3) flavor** ontology (3 light
  flavors) — a further node-multiplet extension, consistent with the v13 pattern.

## Bottom line

From `forces=edges` + `baryon=Skyrmion`, QNG-Skyrme reproduces: the photon, the
confining gauge sector, the nucleon/Δ with a J(J+1) band, the correct hadron
charges, and now **the full Eightfold Way (octet + decuplet) with GMO and
equal-spacing relations** — all the *structure* of the light-hadron spectrum.
The only things still missing are the *absolute scale* (ℏ + Gap 13) and the
*elementary fermions* (v14 chirality).
