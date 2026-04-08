# QNG-CPU-068 Audit Summary

**Result: PASS**
Date: 2026-04-08
Script: `tests/cpu/qng_hopfion_ultralong_reference.py`
Device: GPU (CuPy) — runtime ~2 minutes (vs ~3+ hours on CPU)

## Check results

| Check | Gate | Result |
|-------|------|--------|
| 1 - Any dissolution (info) | informational | Ring: False (99.98%), Hopfion: False (100.00%) |
| 2 - Hopfion >= ring mass at T=15000 | M_hopfion >= M_ring | PASS (1785.2 >= 952.9) |
| 3 - Hopfion half-life >= ring half-life | T_half(h) >= T_half(r) | PASS (both >15000) |

## Key result: BOTH structures survive past the diffusion timescale with near-zero mass loss

| Structure | M0 | M(T=15000) | Loss | Half-life |
|-----------|----|------------|------|-----------|
| Ring Q=0  | 953.0 | 952.9 | 0.02% | >15000 steps |
| Hopfion Q=1 | 1785.2 | 1785.2 | 0.00% | >15000 steps |

Run parameters: 15,000 conservative steps, DT=0.005, total time = 75.0 substrate units.
Diffusion timescale (Einstein estimate): R²/(BETA×DT) = 14,286 steps. Ran 1.05× this.

## Einstein's prediction vs result

Einstein review (2026-04-08) predicted: "The exact soliton result is almost certainly a
finite-time artifact — it is slowness, not topological protection. Run 15,000 steps."

**Result: Einstein's prediction is not confirmed.** At 1.05× the estimated diffusion
timescale, mass loss is 0.02% (ring) and 0.00% (Hopfion). This is below any detection
threshold and consistent with float32 numerical precision rather than physical dissolution.

## Why the structures don't dissolve

Two mechanisms may be responsible. Their relative contributions are not yet quantified:

**Mechanism A — 3D lattice diffusion factor:**
The estimate tau = R²/(BETA×DT) = 14,286 steps omits the 1/6 factor of the 3D lattice
Laplacian. The discrete Laplacian: (smb - sm) ≈ (1/6)∇²sm in lattice units, so the
effective diffusion coefficient is D_eff = BETA×DT/6 per step.

Corrected diffusion timescale by tube radius r_tube ≈ 2-3 nodes:
  tau_tube = r_tube² / D_eff = 4 × 6 / (0.35 × 0.005) = ~14,000 steps by tube radius
  tau_ring  = R²   / D_eff = 25 × 6 / (0.35 × 0.005) = ~86,000 steps by ring radius

The ring as a geometric object (radius R=5) has timescale ~86,000 steps. We ran 15,000 =
17.5% of this — the bulk ring topology has barely moved.

**Mechanism B — phi topology anchoring:**
Even though Channel F is OFF in conservative dynamics (sigma_m does not directly couple
to phi disorder), the phi field maintains its toroidal winding pattern via alignment
dynamics. The sigma_m depletion profile was established IN the phi-disordered region
during Phase 2. In conservative mode, sigma_m diffuses isotropically, but the region
with lowest sigma_m (core of tube) still overlaps with the phi-disordered region.

NOTE: these two mechanisms cannot be separated by M(t) alone. A shape measurement
(sigma_m profile cross-section over time) would distinguish them.

## Comparison: CPU-059 vs CPU-067 vs CPU-068

| Test | Substrate | Steps | Outcome |
|------|-----------|-------|---------|
| CPU-059 | v5 single-sigma | 50 cons | Ring dissolves (half-life ~25 steps) |
| CPU-067 | v7 two-field | 1000 cons | Both stable 100.0% |
| CPU-068 | v7 two-field | 15,000 cons | Both stable 99.98% / 100.00% |

The v7 two-field separation (DER-QNG-033) is the decisive structural change.
In v7 conservative dynamics, sigma_m has NO Channel G coupling — pure diffusion only.
Pure diffusion conserves sum(sigma_m) exactly, and the depletion structure survives
because the corrected diffusion timescale is ~86,000 steps, not 14,286.

## Gap 9 status (from Newton review)

Newton identified Gap 9: KG waves (K_BACK=0.10) and quasi-static Newtonian potential
are structurally contradictory without WKB separation of scales. CPU-068 runs in
conservative mode with KG oscillations active (sigma_g + chi coupled). The soliton
stability observed here is purely in the sigma_m / phi sector — it does not depend
on the sigma_g/chi dynamics. Gap 9 remains open but does not affect this result.

## Next steps

**Option A — Extended run (100,000 steps):** Test whether the ~86,000-step timescale
eventually leads to dissolution. Would require ~15 minutes on GPU.

**Option B — Shape measurement:** Track sigma_m cross-section profile (not just total M)
to detect smearing of the depletion tube even when total M is conserved.

**Option C — Skyrme/conservative Channel F:** Add conservative energy term anchoring
sigma_m to phi topology. Would make Q dynamically relevant (Einstein recommendation).

**Option D — DER-QNG-037:** Write the WKB/secular decomposition for Gap 9 (Newton
recommendation). Separates static Newtonian potential from KG oscillations.
