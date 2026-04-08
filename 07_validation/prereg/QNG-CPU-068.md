# QNG-CPU-068

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-08`
test_class: `hopfion_candidate`

## Title

Hopfion Q=1 vs ring Q=0 — ultra-long conservative run (15,000 steps, GPU-accelerated)

## Purpose

CPU-067 ran 1000 conservative steps at DT=0.005. Einstein review (2026-04-08) identified
that the TRUE diffusion timescale is R²/(BETA×DT) = 25/(0.35×0.005) = **14,286 steps**,
not 71 steps as the script's label implied (operator precedence error: script computed
(R²/BETA)×DT = 0.36 time units = 71 CPU steps, which is actually the timescale in
time units — but in conservative steps with DT=0.005, the correct number is 14,286).

CPU-067's 1000 steps = only 7% of the diffusion timescale. Einstein's verdict:
"The exact soliton result is almost certainly a finite-time artifact — it is slowness,
not topological protection."

This test runs 15,000 conservative steps (≈ 1.05× diffusion timescale) to determine
whether dissolution occurs when sigma_m has actually had time to diffuse.

GPU acceleration (CuPy) used to make 15,000 steps feasible in reasonable time.

## Upstream

- DER-QNG-036: Hopfion topology in v7
- QNG-CPU-067: PASS — both ring and Hopfion stable at 1000 conservative steps
- Einstein review 2026-04-08: 1000 steps insufficient; true tau_diff = 14,286 steps

## Experimental design

- Start from fully formed dissipative state (Phase1=300 + Phase2_diss=1000)
- Switch to conservative dynamics (no Channel A, no Channel F, no CHI_DECAY)
- Run 15,000 conservative steps at DT=0.005 (total time = 75.0 substrate units)
- Record M(t) every 500 steps
- GPU acceleration via CuPy (fallback to numpy if unavailable)

## Checks

**Check 1 — Any dissolution at T=15000 (informational):**
Define dissolution as M(T=15000) < 0.99 × M0 (any 1% loss is detectable).
Informational only — records whether dissolution is visible.

**Check 2 — Hopfion retains more mass than ring at T=15000:**
M_hopfion(T=15000) >= M_ring(T=15000).
Gate: Hopfion equal or heavier than ring.

**Check 3 — Half-life comparison (50% threshold):**
T_half(hopfion) >= T_half(ring), where T_half = first t with M < M0/2.
If neither dissolves: both get 15000+1 as lower bound → tie → PASS.

## Decision rule

PASS if Check 3 passes (Hopfion half-life >= ring half-life).
Check 1 (dissolution) and Check 2 (mass comparison) are informational.

## Artifact paths

- `07_validation/audits/qng-hopfion-ultralong-v1/report.json`
- `07_validation/audits/qng-hopfion-ultralong-v1/summary.md`
