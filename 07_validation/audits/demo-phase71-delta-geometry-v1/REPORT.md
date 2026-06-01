# REPORT — demo Phase-71: can δ (Koide offset) be derived from wall geometry?

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase71_delta_from_geometry.py`
Verdict: **δ NOT DERIVED FROM WALL GEOMETRY — honest negative, 2/9 refused**

Genuine attempt to derive the Koide offset δ from the 3-domain-wall geometry (P60).

- **T1.** Precise offset from measured masses: **δ = 0.22227 rad (12.74°)**.
- **T2.** Candidate geometric values of the 3-orthogonal-wall config:
  | candidate | rad | err |
  |---|---|---|
  | 2/9 (rational radian) | 0.2222 | 0.02% |
  | π/14 | 0.2244 | 1.0% |
  | π/12 (Berry/gen) | 0.2618 | 18% |
  | π/4 (Berry octant) | 0.785 | 253% |
  | arccos(1/√3) | 0.955 | 330% |
- **T3.** No genuine geometric angle (multiple of π, arccos of a simple ratio)
  matches at <1% (best π-based is π/14 at 1.0%, with arbitrary "14"). The only
  <0.1% match is 2/9 — a RATIONAL NUMBER OF RADIANS (no π), which is the signature of
  a numerical coincidence, NOT a geometric angle. **2/9 refused** (same discipline as
  Phases 61/33/63).

**Net.** The wall geometry DERIVES the 2π/3 three-phase SPACING (→ Koide Q=2/3 →
m_τ to 0.006%, P61), but does NOT derive the OFFSET δ. δ remains a free phase (one of
the two undetermined Koide parameters with M₀); absolute lepton masses still open.

**Honest.** The attempt was made in earnest; the geometry does not supply δ; no
derivation manufactured. The real open direction: δ might be fixed by the DYNAMICS of
how the three wall zero-modes phase-lock (a real calculation, not a geometric angle) —
not a number to guess.
