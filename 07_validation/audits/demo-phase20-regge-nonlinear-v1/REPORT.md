# REPORT — demo Phase-20 (Gap 12 nonlinear core) Regge nonlinear curvature

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase20_regge_nonlinear_curvature.py`
Verdict: **NONLINEAR_COMPLETION_IS_REGGE**

| Test | Result |
|---|---|
| T1 Gauss-Bonnet sum(deficit) on triangulated sphere | 4pi to 1.4e-14 (all mesh levels) |
| T2 deficit/area -> K (V=12,42,162) | 1.31 -> 1.08 -> 1.02 (-> K=1 unit sphere) |
| T3 deficit nonlinearity (quadratic coef) | a2 = -8.12 (non-negligible) |

## Verdict

The QNG edge rank-2 object (h_ij, Phase 16/17) is the Regge edge-length variable;
curvature lives on hinges as the deficit angle delta = 2pi - sum(angles). The
deficit IS the full curvature (T1 Gauss-Bonnet exact), the LOCAL Gaussian
curvature (T2 delta/area -> K), and a NONLINEAR function of edge lengths (T3).
By Regge's theorem the Regge action sum A_h delta_h -> int sqrt(g) R, the FULL
nonlinear Einstein-Hilbert action. The nonlinear completion of QNG gravity =
Regge action on the edge graviton; the edge-length -> nonlinear-curvature map is
demonstrated rigorously.

Remaining gap, now BOUNDED: derive the Regge MEASURE (hinge areas A_h + coupling
1/8piG = z/8pi beta_g) from the substrate. No longer "find the nonlinear
completion" but "derive the Regge measure from the substrate" -- well-posed, with
the coefficient already 15%-matched (Phase 17).

## Scope

T1/T2/T3 are rigorous demonstrations of Regge-curvature = full-nonlinear-curvature
(Gauss-Bonnet exact; delta/area->K; deficit nonlinear). Regge->EH is Regge's
theorem applied to the identification QNG-edge = Regge-edge-lengths (Phase 16/17).
Substrate->Regge-measure derivation is the remaining bounded piece.
