"""QNG-CPU-104 -- v10 uncertainty principle test.

Derivation: 04_qng_pure/qng-v10-foundational-v1.md (DER-QNG-062)

Verifies that v10 axioms produce the Heisenberg uncertainty relation:
    Delta_x * Delta_p >= hbar_lattice / 2

with equality for coherent states (minimum uncertainty states).

CPU only. Analytical verification.
"""
import numpy as np
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-cpu104-v10-uncertainty-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_operators(N_trunc, hbar_lattice):
    Psi = np.zeros((N_trunc, N_trunc), dtype=np.complex128)
    for n in range(N_trunc - 1):
        Psi[n, n + 1] = np.sqrt((n + 1) * hbar_lattice)
    Psi_dag = Psi.conj().T
    x = (Psi + Psi_dag) / np.sqrt(2)
    p = (Psi - Psi_dag) / (1j * np.sqrt(2))
    return Psi, Psi_dag, x, p


def measure_uncertainty(psi, x, p):
    """Compute Delta_x, Delta_p, and their product for state psi."""
    psi = psi / np.linalg.norm(psi)
    x_exp = np.vdot(psi, x @ psi).real
    p_exp = np.vdot(psi, p @ psi).real
    x2_exp = np.vdot(psi, x @ x @ psi).real
    p2_exp = np.vdot(psi, p @ p @ psi).real
    dx = np.sqrt(x2_exp - x_exp**2)
    dp = np.sqrt(p2_exp - p_exp**2)
    return dx, dp, dx * dp


def coherent_state(alpha, N_trunc, hbar_lattice):
    """|alpha> = exp(-|alpha|^2/2hbar) sum_n alpha^n/(sqrt(n!) hbar^(n/2)) |n>"""
    psi = np.zeros(N_trunc, dtype=np.complex128)
    ln_factorial = 0.0
    for n in range(N_trunc):
        if n > 0:
            ln_factorial += np.log(n)
        # coefficient c_n = alpha^n / sqrt(n! hbar^n) * exp(-|alpha|^2/(2hbar))
        # Use log to avoid overflow
        log_c = (n * np.log(abs(alpha)) - ln_factorial / 2
                 - (n/2) * np.log(hbar_lattice)
                 - (abs(alpha)**2) / (2 * hbar_lattice))
        if log_c > -700:
            phase = np.exp(1j * n * np.angle(alpha))
            psi[n] = np.exp(log_c) * phase
    return psi / np.linalg.norm(psi)


def main():
    print("=" * 72)
    print("QNG-CPU-104: v10 uncertainty principle test")
    print("=" * 72)

    hbar_lattice_values = [1.0, 0.5, 0.03]
    results = []

    for hbar in hbar_lattice_values:
        print(f"\n### hbar_lattice = {hbar} ###")
        N = 100
        Psi, Psi_dag, x, p = build_operators(N, hbar)

        # Test 1: Ground state |0>
        psi_0 = np.zeros(N, dtype=np.complex128)
        psi_0[0] = 1.0
        dx0, dp0, prod0 = measure_uncertainty(psi_0, x, p)
        saturation0 = prod0 / (hbar / 2)
        print(f"  |0>:      Dx={dx0:.6f}, Dp={dp0:.6f}, DxDp={prod0:.6f}")
        print(f"            Saturation: DxDp / (hbar/2) = {saturation0:.6f}")

        # Test 2: First excited state |1>
        psi_1 = np.zeros(N, dtype=np.complex128)
        psi_1[1] = 1.0
        dx1, dp1, prod1 = measure_uncertainty(psi_1, x, p)
        saturation1 = prod1 / (hbar / 2)
        print(f"  |1>:      Dx={dx1:.6f}, Dp={dp1:.6f}, DxDp={prod1:.6f}")
        print(f"            Saturation: DxDp / (hbar/2) = {saturation1:.6f}")

        # Test 3: Coherent state at alpha=2
        psi_alpha = coherent_state(2.0, N, hbar)
        dxa, dpa, proda = measure_uncertainty(psi_alpha, x, p)
        saturationa = proda / (hbar / 2)
        print(f"  |alpha=2>:    Dx={dxa:.6f}, Dp={dpa:.6f}, DxDp={proda:.6f}")
        print(f"            Saturation: DxDp / (hbar/2) = {saturationa:.6f}")

        # Test 4: Superposition (|0> + |2>)/sqrt(2) — non-minimum
        psi_sup = np.zeros(N, dtype=np.complex128)
        psi_sup[0] = 1.0 / np.sqrt(2)
        psi_sup[2] = 1.0 / np.sqrt(2)
        dxs, dps, prods = measure_uncertainty(psi_sup, x, p)
        saturations = prods / (hbar / 2)
        print(f"  (|0>+|2>):  Dx={dxs:.6f}, Dp={dps:.6f}, DxDp={prods:.6f}")
        print(f"            Saturation: DxDp / (hbar/2) = {saturations:.6f}")

        results.append({
            'hbar': hbar,
            'ground': {'Dx': dx0, 'Dp': dp0, 'DxDp': prod0, 'sat': saturation0},
            'first_excited': {'Dx': dx1, 'Dp': dp1, 'DxDp': prod1, 'sat': saturation1},
            'coherent_alpha2': {'Dx': dxa, 'Dp': dpa, 'DxDp': proda, 'sat': saturationa},
            'superposition_02': {'Dx': dxs, 'Dp': dps, 'DxDp': prods, 'sat': saturations},
        })

    # Verdict
    print("\n" + "=" * 72)
    print("VERDICTS")
    print("=" * 72)

    all_pass = True
    for r in results:
        sat_ground = r['ground']['sat']
        sat_coherent = r['coherent_alpha2']['sat']
        sat_super = r['superposition_02']['sat']
        sat_excited = r['first_excited']['sat']

        # Key physics: uncertainty relation holds means saturation >= 1
        # Ground state should saturate exactly
        ground_saturates = abs(sat_ground - 1.0) < 0.01
        # ALL states must satisfy UR (saturation >= 1)
        all_states_satisfy_ur = (sat_ground >= 0.99 and sat_coherent >= 0.99
                                 and sat_super >= 0.99 and sat_excited >= 0.99)

        status = "UR_PASS" if (ground_saturates and all_states_satisfy_ur) else "UR_FAIL"
        print(f"  hbar={r['hbar']}: ground_sat={sat_ground:.4f} (should=1.0), "
              f"excited_sat={sat_excited:.4f}, super_sat={sat_super:.4f}, "
              f"coherent_sat={sat_coherent:.4f} -> {status}")
        if status == "UR_FAIL":
            all_pass = False

    overall = "UR_PASS" if all_pass else "UR_FAIL"
    print(f"\n  OVERALL: {overall}")

    json.dump({
        'test_id': 'QNG-CPU-104',
        'date': '2026-04-24',
        'results': results,
        'overall': overall,
    }, open(OUT_DIR / 'report.json', 'w'), indent=2, default=str)
    print(f"\nSaved: {OUT_DIR / 'report.json'}")


if __name__ == '__main__':
    main()
