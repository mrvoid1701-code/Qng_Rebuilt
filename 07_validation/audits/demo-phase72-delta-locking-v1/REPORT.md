# REPORT — demo Phase-72: δ via wall zero-mode phase-locking dynamics

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase72_delta_phase_locking.py`
Verdict: **δ IS A GOLDSTONE ZERO MODE** — dynamics confirms the 2π/3 spacing but does not fix δ (and explains the Phase-71 negative)

Models the 3 domain-wall chiral zero-modes (the 3 generations, P60) as 3
Z₃-symmetrically-coupled phase oscillators; asks what offset they lock into.

- **T1.** From random initial phases the system robustly locks to the **2π/3 splay
  spacing** (gaps all 2.094 rad = 2π/3) — confirming the Koide three-phase structure
  (Q=2/3, m_τ, P61) — but the global offset is DIFFERENT every trial (0.62, 0.50,
  1.76, 2.06...).
- **T2 (decisive).** Jacobian eigenvalues at the splay state: **[−0.5, −0.5, 0]**.
  Exactly ONE zero eigenvalue = the global phase rotation → **δ is a GOLDSTONE / zero
  mode** (no restoring force); the two −0.5 eigenvalues pin the 2π/3 spacing.
  Confirmed: perturbing the global offset leaves it shifted (free); perturbing the
  spacing relaxes back to 2π/3 (fixed).
- **T3.** The spacing is a dynamically stable attractor (derived); δ is a protected
  FLAT DIRECTION — undetermined by the symmetric dynamics.

**Net.** This is a genuine structural result: δ is the Goldstone mode of the
3-generation phase system. It EXPLAINS the Phase-71 negative — δ cannot be a fixed
geometric angle precisely BECAUSE it is a Goldstone zero mode. Fixing δ requires
EXPLICIT breaking of the global phase symmetry (a reference phase — coupling to the
φ-vacuum or a lattice term), which QNG does not currently derive. **δ remains open,
but now understood; 2/9 still refused.**

**Honest.** Reduced Kuramoto model (captures Z₃ + splay attractor); the Goldstone
conclusion is symmetry-protected (robust for any Z₃-symmetric coupling). The sharp
open direction: δ is fixed only by an explicit QNG phase reference breaking the global
U(1) — a physical mechanism to identify, not a number to guess.
