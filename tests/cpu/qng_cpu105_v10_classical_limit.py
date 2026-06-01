"""QNG-CPU-105 -- v10 classical limit verification.

Derivation: 04_qng_pure/qng-v10-foundational-v1.md (DER-QNG-062 corrected)
            04_qng_pure/qng-v10-classical-limit-v1.md (DER-QNG-063)

Tests whether v10 coherent state evolution reproduces v8 classical
trajectory in the limit hbar_lattice / |alpha|^2 -> 0.

Single-site harmonic oscillator (simplest non-trivial case):
  H = (1/(2 mu)) Pi_dag Pi + (mu omega^2 / 2) Psi_dag Psi

Classical trajectory (Ehrenfest): <Psi(t)> = alpha_0 * exp(-i omega t)

v10 prediction: for coherent state |alpha_0>:
  <Psi(t)> = alpha_0 * exp(-i omega t) * (exact, due to linearity)

Test: verify agreement at multiple (hbar, alpha_0) values.

CPU only. Analytical verification.
"""
import numpy as np
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-cpu105-v10-classical-limit-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_canonical_operators(N_trunc, hbar):
    """Build canonical pair (Psi, Pi) with [Psi, Pi_dag] = i*hbar.

    Implement via quadratures: Psi = x + iy, Pi = p_x - ip_y (formally).
    For single-mode, take Psi = (1/sqrt(2))(x + ip), Pi = (1/sqrt(2))(p - ix)
    so that [Psi, Pi_dag] = i*hbar exactly.

    Simpler: use standard x,p quadratures where [x,p] = i*hbar.
    Then Psi = (x + ip)/sqrt(2), Pi_canonical_momentum = mu*dx/dt + i*mu*dy/dt etc.

    For this simplest test, use bosonic operators a, a_dag with [a, a_dag] = 1:
      Psi = sqrt(hbar) * a     so [Psi, Psi_dag] = hbar
      Pi  = -i sqrt(hbar) * a  so [Psi, Pi_dag] = i hbar  (canonical!)
    This mirrors DER-QNG-063 §5 corrected formulation.
    """
    a = np.zeros((N_trunc, N_trunc), dtype=np.complex128)
    for n in range(N_trunc - 1):
        a[n, n + 1] = np.sqrt(n + 1)
    a_dag = a.conj().T
    Psi = np.sqrt(hbar) * a
    Psi_dag = Psi.conj().T
    # Canonical momentum Pi such that [Psi, Pi_dag] = i*hbar
    # Use Pi = -i*sqrt(hbar)*a (trial)
    Pi = -1j * np.sqrt(hbar) * a
    Pi_dag = Pi.conj().T
    # Verify [Psi, Pi_dag] = -i*sqrt(hbar)*sqrt(hbar)* [a, a_dag_conj.T] wait let me think again
    # Pi_dag = (-i*sqrt(hbar)*a).conj().T = i*sqrt(hbar)*a_dag
    # [Psi, Pi_dag] = [sqrt(hbar)*a, i*sqrt(hbar)*a_dag] = i*hbar*[a, a_dag] = i*hbar*I
    # OK so this works.
    return Psi, Psi_dag, Pi, Pi_dag, a, a_dag


def harmonic_H(a, a_dag, hbar, omega):
    """H = hbar*omega*(a_dag a + 1/2) -- standard harmonic oscillator."""
    N_op = a_dag @ a
    I = np.eye(a.shape[0])
    return hbar * omega * (N_op + 0.5 * I)


def coherent_state_normalized(alpha, N_trunc):
    """|alpha> with <a> = alpha (standard bosonic convention).

    |alpha> = exp(-|alpha|^2/2) sum_n (alpha^n / sqrt(n!)) |n>
    """
    psi = np.zeros(N_trunc, dtype=np.complex128)
    log_prefactor = -0.5 * abs(alpha)**2
    log_factorial = 0.0
    for n in range(N_trunc):
        if n > 0:
            log_factorial += 0.5 * np.log(n)
        log_c = n * np.log(abs(alpha)) - log_factorial + log_prefactor
        if log_c > -700:
            phase = np.exp(1j * n * np.angle(alpha))
            psi[n] = np.exp(log_c) * phase
    norm = np.linalg.norm(psi)
    if norm > 0:
        psi = psi / norm
    return psi


def evolve_under_H(psi0, H, t, hbar):
    """U(t) |psi> = exp(-i H t / hbar) |psi>

    Use eigendecomposition for exact evolution.
    """
    evals, evecs = np.linalg.eigh(H)
    # Expand psi0 in eigenbasis
    psi_eig = evecs.conj().T @ psi0
    # Time-evolve coefficients
    phases = np.exp(-1j * evals * t / hbar)
    psi_t_eig = phases * psi_eig
    # Transform back
    return evecs @ psi_t_eig


def main():
    print("=" * 72)
    print("QNG-CPU-105: v10 classical limit verification")
    print("=" * 72)

    N_trunc = 100
    omega = 1.0
    mu = 1.0  # not used directly in H=hbar*omega*(N+1/2) but here for consistency

    results = []

    test_cases = [
        (1.0, 2.0),     # hbar=1, alpha=2 -> |alpha|^2/hbar = 4
        (1.0, 5.0),     # hbar=1, alpha=5 -> 25 (semiclassical)
        (0.5, 5.0),     # hbar=0.5, alpha=5 -> 50
        (0.1, 5.0),     # hbar=0.1, alpha=5 -> 250 (deeply classical)
        (0.01, 5.0),    # hbar=0.01, alpha=5 -> 2500 (very classical)
    ]

    for hbar, alpha0 in test_cases:
        label = f"hbar={hbar}_alpha={alpha0}"
        print(f"\n### {label} ###")
        print(f"  Semiclassical parameter |alpha|^2/hbar = {abs(alpha0)**2/hbar:.1f}")

        Psi, Psi_dag, Pi, Pi_dag, a, a_dag = build_canonical_operators(N_trunc, hbar)
        H = harmonic_H(a, a_dag, hbar, omega)

        # Initial coherent state
        psi0 = coherent_state_normalized(alpha0, N_trunc)
        # Verify <a> = alpha at t=0
        a_exp_0 = np.vdot(psi0, a @ psi0)
        print(f"  <a>(t=0) = {a_exp_0:.6f}  (expected {alpha0})")
        # And <Psi> = sqrt(hbar)*alpha
        Psi_exp_0 = np.vdot(psi0, Psi @ psi0)
        print(f"  <Psi>(t=0) = {Psi_exp_0:.6f}  (expected {np.sqrt(hbar)*alpha0:.6f})")

        # Evolve to times t=pi/4, pi/2, pi, 2pi (one period = 2pi/omega)
        times = [np.pi/4, np.pi/2, np.pi, 2*np.pi]
        errors = []
        for t in times:
            psi_t = evolve_under_H(psi0, H, t, hbar)
            a_exp = np.vdot(psi_t, a @ psi_t)
            Psi_exp = np.vdot(psi_t, Psi @ psi_t)
            alpha_classical = alpha0 * np.exp(-1j * omega * t)
            Psi_classical = np.sqrt(hbar) * alpha_classical
            error_Psi = abs(Psi_exp - Psi_classical) / max(abs(Psi_classical), 1e-20)
            errors.append(error_Psi)
            print(f"  t={t:.4f}: <Psi> = {Psi_exp:.6f}  classical = {Psi_classical:.6f}  "
                  f"rel_err = {error_Psi*100:.4f}%")

        max_error = max(errors)
        results.append({
            'hbar': hbar,
            'alpha0': alpha0,
            'semiclassical_param': abs(alpha0)**2 / hbar,
            'max_rel_error': max_error,
            'errors_at_times': errors,
        })

    # Verdict
    print("\n" + "=" * 72)
    print("VERDICTS")
    print("=" * 72)
    all_pass = True
    for r in results:
        ok = r['max_rel_error'] < 0.001  # 0.1% target
        marginal = r['max_rel_error'] < 0.05  # 5% acceptable
        status = "CL_PASS" if ok else ("CL_MARGINAL" if marginal else "CL_FAIL")
        if not ok:
            all_pass = False
        print(f"  hbar={r['hbar']}, alpha={r['alpha0']}, "
              f"|alpha|^2/hbar={r['semiclassical_param']:.1f}: "
              f"max_rel_err={r['max_rel_error']*100:.4f}% -> {status}")

    overall = "CL_PASS" if all_pass else "CL_MIXED"
    print(f"\n  OVERALL: {overall}")

    # Key insight: check scaling of error with hbar
    print("\n  Error scaling check (Ehrenfest theorem):")
    print("    For harmonic oscillator, error should be ~0 (linearity)")
    print("    Any nonzero error indicates numerical truncation, not physics")

    json.dump({
        'test_id': 'QNG-CPU-105',
        'date': '2026-04-24',
        'results': results,
        'overall': overall,
    }, open(OUT_DIR / 'report.json', 'w'), indent=2, default=str)
    print(f"\nSaved: {OUT_DIR / 'report.json'}")


if __name__ == '__main__':
    main()
