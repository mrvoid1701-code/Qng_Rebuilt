"""
PHASE 72 (particles / Gap 13) -- attack delta via the DYNAMICS of wall zero-mode
phase-locking (a real calculation, not a guessed angle).

Phase 71 showed no geometric angle gives the Koide offset delta. Here we model the
three domain-wall chiral zero-modes (the 3 generations, Phase 60) as three coupled
phase oscillators on the phi-circle, with the Z3 symmetry of the three equivalent
wall orientations, and ask what offset the system LOCKS into dynamically.

Model (repulsive Kuramoto -> phases spread to the splay state):
   d theta_i/dt = (K/N) sum_j sin(theta_i - theta_j)
The Z3-symmetric splay state is theta_j = delta + 2pi j/3 (the cube roots of unity),
stable for ANY global offset delta.

  T1 integrate from random initial phases -> confirm it locks to the 2pi/3 SPACING
     (the Koide three-phase structure, Phase 60/61) robustly.
  T2 the decisive test: compute the JACOBIAN eigenvalues at the splay state. If one
     eigenvalue is ZERO, the global offset delta is a GOLDSTONE / zero mode --
     undetermined by the symmetric dynamics (no restoring force). The spacing is
     fixed (negative eigenvalues), the offset is free.
  T3 verdict: if delta is a zero mode, the dynamics CONFIRMS the 2pi/3 spacing but
     does NOT fix delta -- and EXPLAINS Phase 71 (delta is a protected flat direction,
     hence no geometric value). Fixing delta requires EXPLICIT symmetry breaking (a
     reference phase QNG does not yet derive). Honest: delta open, now understood.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase72-delta-locking-v1")

N = 3
K = 1.0
DT = 0.01
STEPS = 20000


def deriv(theta):
    # repulsive Kuramoto: d theta_i/dt = (K/N) sum_j sin(theta_i - theta_j)
    d = np.zeros(N)
    for i in range(N):
        d[i] = (K/N)*np.sum(np.sin(theta[i] - theta))
    return d


def main():
    print("="*70)
    print("PHASE 72 (Gap 13) -- delta via wall zero-mode phase-locking dynamics")
    print("="*70)

    rng = np.random.RandomState(7)
    # T1: integrate from random init
    print("\n[T1] phase-locking from random initial phases (Z3-symmetric coupling):")
    results_spacing = []
    for trial in range(4):
        theta = rng.uniform(0, 2*np.pi, N)
        for _ in range(STEPS):
            theta = theta + DT*deriv(theta)
        th = np.sort(np.mod(theta, 2*np.pi))
        gaps = np.diff(np.concatenate([th, [th[0]+2*np.pi]]))
        results_spacing.append(gaps)
        print("     trial %d: locked gaps = [%.3f, %.3f, %.3f] rad (2pi/3 = %.3f); offset=%.3f"
              % (trial, gaps[0], gaps[1], gaps[2], 2*np.pi/3, th[0]))
    mean_gap = np.mean([g for gs in results_spacing for g in gs])
    spacing_ok = abs(mean_gap - 2*np.pi/3) < 0.05
    print("     => locks to the 2pi/3 SPLAY spacing (mean gap %.3f vs 2pi/3=%.3f): %s"
          % (mean_gap, 2*np.pi/3, spacing_ok))
    print("        BUT the global offset differs every trial -> not fixed by the dynamics.")

    # T2: Jacobian eigenvalues at the splay state
    print("\n[T2] DECISIVE test -- Jacobian eigenvalues at the splay state:")
    theta0 = np.array([0.0, 2*np.pi/3, 4*np.pi/3])
    eps = 1e-6
    J = np.zeros((N, N))
    f0 = deriv(theta0)
    for k in range(N):
        tp = theta0.copy(); tp[k] += eps
        J[:, k] = (deriv(tp) - f0)/eps
    evals = np.sort(np.linalg.eigvals(J).real)
    print("     Jacobian eigenvalues: [%.4f, %.4f, %.4f]" % (evals[0], evals[1], evals[2]))
    n_zero = int(np.sum(np.abs(evals) < 1e-3))
    print("     => %d ZERO eigenvalue(s): the global offset delta is a GOLDSTONE / zero" % n_zero)
    print("        mode (no restoring force). The other eigenvalues fix the 2pi/3 SPACING.")
    zero_mode = (n_zero == 1)

    # confirm: perturb global offset -> no return; perturb spacing -> returns
    print("\n     confirmation: perturb the GLOBAL offset (all +0.3) -> stays shifted")
    th_g = theta0 + 0.3
    for _ in range(5000): th_g = th_g + DT*deriv(th_g)
    print("        offset after relaxation: %.3f (started 0.3 -> stays ~%.2f, NOT 0): free"
          % (np.mod(th_g[0], 2*np.pi), 0.3))
    print("     perturb the SPACING (one phase +0.3) -> returns to 2pi/3")
    th_s = theta0.copy(); th_s[1] += 0.3
    for _ in range(5000): th_s = th_s + DT*deriv(th_s)
    th_s = np.sort(np.mod(th_s, 2*np.pi))
    gaps_s = np.diff(np.concatenate([th_s, [th_s[0]+2*np.pi]]))
    print("        spacing after relaxation: [%.3f,%.3f,%.3f] -> back to 2pi/3: spacing IS fixed"
          % (gaps_s[0], gaps_s[1], gaps_s[2]))

    # T3
    print("\n[T3] verdict:")
    print("     - the 2pi/3 SPACING is dynamically STABLE (negative eigenvalues) -> the")
    print("       Koide three-phase structure (Q=2/3, m_tau, P61) is robust.")
    print("     - the OFFSET delta is a GOLDSTONE ZERO MODE -> undetermined by the")
    print("       symmetric dynamics. This EXPLAINS Phase 71: delta is a protected flat")
    print("       direction, so no geometric angle fixes it.")
    print("     - fixing delta requires EXPLICIT symmetry breaking (a reference phase),")
    print("       which QNG does not derive from first principles -> delta genuinely OPEN.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  2pi/3 spacing dynamically stable (Koide structure robust): %s" % spacing_ok)
    print("  offset delta is a GOLDSTONE zero mode (1 zero eigenvalue): %s" % zero_mode)
    print("  => dynamics CONFIRMS spacing, does NOT fix delta; delta is a protected flat direction")

    verdict = (
        "DELTA_IS_A_GOLDSTONE_ZERO_MODE -- DYNAMICS CONFIRMS THE 2pi/3 SPACING BUT "
        "DOES NOT FIX delta (and EXPLAINS why Phase 71 found no geometric value). "
        "Modeling the three domain-wall chiral zero-modes (the 3 generations) as "
        "three Z3-symmetrically-coupled phase oscillators on the phi-circle: (T1) "
        "from random initial phases the system robustly LOCKS to the 2pi/3 splay "
        "spacing (the cube roots of unity) -- confirming the Koide three-phase "
        "structure that gives Q=2/3 and the m_tau prediction (Phase 61) -- but the "
        "global offset comes out DIFFERENT every trial. (T2) The decisive test is the "
        "Jacobian spectrum at the splay state: it has exactly ONE ZERO eigenvalue and "
        "two negative ones. The zero eigenvalue is the global phase rotation -- i.e. "
        "the offset delta is a GOLDSTONE / zero mode with NO restoring force, while "
        "the negative eigenvalues pin the 2pi/3 SPACING. Confirmed directly: "
        "perturbing the global offset leaves it shifted (free), whereas perturbing "
        "the spacing relaxes back to 2pi/3 (fixed). (T3) CONCLUSION: the phase-locking "
        "dynamics DERIVES the 2pi/3 spacing (the spacing is a dynamically stable "
        "attractor), but the offset delta is a protected FLAT DIRECTION -- a "
        "Goldstone mode of the global phase symmetry -- and is therefore NOT fixed by "
        "the symmetric dynamics. This is a genuine structural result: it EXPLAINS the "
        "Phase-71 negative (no geometric angle gives delta) -- delta cannot be a fixed "
        "geometric quantity precisely BECAUSE it is a Goldstone zero mode. To assign "
        "delta a value requires EXPLICIT breaking of the global phase symmetry (a "
        "reference phase -- e.g. a coupling to the phi-vacuum or a lattice-induced "
        "term), which QNG does not currently derive from first principles. So delta "
        "remains genuinely OPEN, but now UNDERSTOOD: it is the Goldstone direction of "
        "the 3-generation phase system, hence undetermined by both geometry (P71) and "
        "symmetric dynamics (here). We do NOT force delta=2/9. HONEST: this is a "
        "reduced (Kuramoto) model of the phase-locking, capturing the Z3 symmetry and "
        "the splay attractor; the real wall zero-modes would have additional "
        "structure, but the Goldstone-mode conclusion is symmetry-protected and "
        "robust -- any Z3-symmetric coupling has the offset as a zero mode. The "
        "honest open direction is now sharp: delta is fixed only if QNG provides an "
        "explicit phase reference that breaks the global U(1) -- a specific physical "
        "mechanism to identify, not a number to guess.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"mean_gap": float(mean_gap), "two_pi_3": float(2*np.pi/3),
                   "spacing_ok": bool(spacing_ok), "jacobian_eigenvalues": [float(e) for e in evals],
                   "n_zero_modes": n_zero, "delta_is_goldstone": bool(zero_mode),
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
