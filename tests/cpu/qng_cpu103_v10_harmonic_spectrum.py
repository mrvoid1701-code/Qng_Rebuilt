"""QNG-CPU-103 -- v10 harmonic oscillator spectrum test.

Pre-registration: 07_validation/prereg/QNG-CPU-103.md
Derivation:       04_qng_pure/qng-v10-foundational-v1.md (DER-QNG-062)

Tests whether v10 axioms (A3: [Psi, Psi_dag] = hbar_lattice) produce the
expected harmonic oscillator spectrum E_n = hbar_lattice * omega * (n + 1/2).

Single-site Hamiltonian (simplest non-trivial test):
    H = (1/(2 mu)) p^2 + (mu omega^2 / 2) x^2

where x = (Psi + Psi_dag)/sqrt(2), p = (Psi - Psi_dag)/(i sqrt(2))
satisfy [x, p] = i hbar_lattice.

Predicted spectrum: E_n = hbar_lattice * omega * (n + 1/2)

CPU only. No GPU. Analytical verification of DER-QNG-062 consistency.
"""
import numpy as np
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-cpu103-v10-harmonic-spectrum-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_operators(N_trunc, hbar_lattice):
    """Build annihilation/creation operators in truncated Fock basis.

    Psi |n> = sqrt(n * hbar) |n-1>
    Psi_dag |n> = sqrt((n+1) * hbar) |n+1>
    [Psi, Psi_dag] = hbar * I (exact in infinite basis, approx truncated)
    """
    Psi = np.zeros((N_trunc, N_trunc), dtype=np.complex128)
    for n in range(N_trunc - 1):
        Psi[n, n + 1] = np.sqrt((n + 1) * hbar_lattice)
    Psi_dag = Psi.conj().T
    return Psi, Psi_dag


def check_commutator(Psi, Psi_dag, hbar_lattice, label=""):
    """Verify [Psi, Psi_dag] = hbar * I numerically."""
    comm = Psi @ Psi_dag - Psi_dag @ Psi
    expected = hbar_lattice * np.eye(Psi.shape[0])
    N = Psi.shape[0]
    check_region = comm[:N-10, :N-10]
    expected_region = expected[:N-10, :N-10]
    diff = np.abs(check_region - expected_region).max()
    print(f"  [{label}] Commutator check: max|[Psi,Psi_dag] - hbar*I| "
          f"(first {N-10} rows) = {diff:.2e}")
    return diff


def harmonic_hamiltonian(Psi, Psi_dag, mu, omega, hbar_lattice):
    """H = (1/(2 mu)) p^2 + (mu omega^2 / 2) x^2
    with x = (Psi+Psi_dag)/sqrt(2), p = (Psi-Psi_dag)/(i sqrt(2))
    """
    x = (Psi + Psi_dag) / np.sqrt(2)
    p = (Psi - Psi_dag) / (1j * np.sqrt(2))
    H = (1.0 / (2.0 * mu)) * (p @ p) + (mu * omega * omega / 2.0) * (x @ x)
    herm_error = np.abs(H - H.conj().T).max()
    print(f"  Hermiticity check: max|H - H_dag| = {herm_error:.2e}")
    return H


def analyze_spectrum(eigs, hbar_lattice, omega):
    """Compare numerical spectrum with E_n = hbar*omega*(n+1/2)."""
    predicted = hbar_lattice * omega * (np.arange(len(eigs)) + 0.5)
    diff = eigs - predicted
    rel_diff = np.abs(diff) / np.maximum(np.abs(predicted), 1e-20)
    spacing = np.diff(eigs)
    spacing_expected = hbar_lattice * omega
    return {
        'eigs': eigs.tolist(),
        'predicted': predicted.tolist(),
        'abs_diff': diff.tolist(),
        'rel_diff': rel_diff.tolist(),
        'spacing': spacing.tolist(),
        'spacing_expected': spacing_expected,
        'spacing_std': float(np.std(spacing)),
        'spacing_mean': float(np.mean(spacing)),
    }


def run_test(mu=1.0, omega=1.0, hbar_lattice=1.0, N_trunc=100, label=""):
    print(f"\n=== {label} ===")
    print(f"  mu={mu}, omega={omega}, hbar_lattice={hbar_lattice}, N_trunc={N_trunc}")

    Psi, Psi_dag = build_operators(N_trunc, hbar_lattice)
    check_commutator(Psi, Psi_dag, hbar_lattice, label)
    H = harmonic_hamiltonian(Psi, Psi_dag, mu, omega, hbar_lattice)

    eigs = np.linalg.eigvalsh(H)
    print(f"  First 8 eigenvalues (lowest):")
    for i in range(8):
        expected = hbar_lattice * omega * (i + 0.5)
        rel = abs(eigs[i] - expected) / max(abs(expected), 1e-20)
        print(f"    E_{i} = {eigs[i]:.8f}  (expected {expected:.8f}, "
              f"rel diff {rel*100:.3f}%)")

    return analyze_spectrum(eigs[:20], hbar_lattice, omega)


def verdict(results):
    """Apply gates from pre-registration."""
    first5_rel_max = max(results['rel_diff'][:5])
    spacing_cv = results['spacing_std'] / max(abs(results['spacing_mean']), 1e-20)
    if first5_rel_max < 0.01 and spacing_cv < 0.001:
        return "HO_PASS", (
            f"First 5 eigenvalues within 1% (max rel {first5_rel_max*100:.3f}%), "
            f"spacing CV {spacing_cv*100:.3f}% < 0.1%. "
            f"v10 axioms A3 consistent.")
    elif first5_rel_max < 0.05:
        return "HO_MARGINAL", (
            f"First 5 eigenvalues within 5% but not 1% "
            f"(max rel {first5_rel_max*100:.3f}%). "
            f"Likely truncation; increase N.")
    else:
        return "HO_FAIL", (
            f"Eigenvalues off by {first5_rel_max*100:.2f}%. "
            f"v10 A3 algebra broken.")


def main():
    print("=" * 72)
    print("QNG-CPU-103: v10 harmonic oscillator spectrum test")
    print("DER-QNG-062 axiomatic consistency check")
    print("=" * 72)

    print("\n### Test 1: Standard parameters (hbar=1) ###")
    r1 = run_test(mu=1.0, omega=1.0, hbar_lattice=1.0, N_trunc=100,
                  label="PRIMARY_hbar1")

    print("\n### Test 2: hbar_lattice = beta_phi/2 = 0.03 (QNG prediction) ###")
    r2 = run_test(mu=1.0, omega=1.0, hbar_lattice=0.03, N_trunc=100,
                  label="QNG_hbar0.03")

    print("\n### Test 3: mu=0.857, omega=0.2 (scale check) ###")
    r3 = run_test(mu=0.857, omega=0.2, hbar_lattice=0.03, N_trunc=100,
                  label="SCALE_CHECK")

    print("\n### Test 4: Truncation sensitivity ###")
    r_N50 = run_test(mu=1.0, omega=1.0, hbar_lattice=1.0, N_trunc=50,
                     label="N50")
    r_N200 = run_test(mu=1.0, omega=1.0, hbar_lattice=1.0, N_trunc=200,
                      label="N200")
    trunc_diff = [abs(r_N50['eigs'][i] - r_N200['eigs'][i])
                  for i in range(5)]
    print(f"  Max diff in first 5 eigvals between N=50 and N=200: "
          f"{max(trunc_diff):.2e}")

    v1, d1 = verdict(r1)
    v2, d2 = verdict(r2)
    v3, d3 = verdict(r3)

    print("\n" + "=" * 72)
    print("VERDICTS")
    print("=" * 72)
    print(f"  Test 1 (hbar=1):    {v1}")
    print(f"    {d1}")
    print(f"  Test 2 (hbar=0.03): {v2}")
    print(f"    {d2}")
    print(f"  Test 3 (scale):     {v3}")
    print(f"    {d3}")

    overall = "HO_PASS" if (v1 == "HO_PASS" and v2 == "HO_PASS"
                             and v3 == "HO_PASS") else "HO_MIXED"
    print(f"\n  OVERALL: {overall}")

    json.dump({
        'test_id': 'QNG-CPU-103',
        'date': '2026-04-24',
        'test1_hbar1': {'verdict': v1, 'diagnosis': d1, 'results': r1},
        'test2_hbar_qng': {'verdict': v2, 'diagnosis': d2, 'results': r2},
        'test3_scale': {'verdict': v3, 'diagnosis': d3, 'results': r3},
        'truncation_check': {'max_diff_N50_N200': float(max(trunc_diff))},
        'overall': overall,
    }, open(OUT_DIR / "report.json", 'w'), indent=2, default=str)
    print(f"\nSaved: {OUT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
