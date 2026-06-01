"""QNG-CPU-112 -- EXTREME scenarios: what destroys the universe?"""
import numpy as np

def compute_QNG_state(beta_phi, mu_phi, z_coord, vacuum_total, L=20):
    """Compute QNG state for given parameters. Returns hbar and stability."""
    if beta_phi == 0:
        return {'hbar': float('nan'), 'stable': False, 'reason': 'NO INTERACTION (omega=0)',
                'a_L_planck': float('nan')}
    if mu_phi <= 0:
        return {'hbar': float('nan'), 'stable': False, 'reason': 'NEGATIVE INERTIA (causality broken)',
                'a_L_planck': float('nan')}
    if z_coord <= 0:
        return {'hbar': float('nan'), 'stable': False, 'reason': 'NO COORDINATION (no graph)',
                'a_L_planck': float('nan')}

    N_nodes = L**3
    k_vals = 2*np.pi*np.arange(L)/L
    kx, ky, kz = np.meshgrid(k_vals, k_vals, k_vals, indexing='ij')

    # If beta < 0: omega^2 < 0 -> imaginary frequencies (instability!)
    omega_sq = (beta_phi/(z_coord*mu_phi))*2.0*(3.0 - np.cos(kx) - np.cos(ky) - np.cos(kz))
    if beta_phi < 0:
        # All non-zero modes are imaginary (exponential growth)
        return {'hbar': float('nan'), 'stable': False,
                'reason': 'EXPONENTIAL INSTABILITY (omega^2 < 0 for all modes)',
                'a_L_planck': float('nan'), 'beta': beta_phi}

    mask = omega_sq > 1e-20
    if mask.sum() == 0:
        return {'hbar': float('nan'), 'stable': False, 'reason': 'NO MODES',
                'a_L_planck': float('nan')}

    omega_k = np.sqrt(omega_sq[mask])
    sum_omega = float(np.sum(omega_k))
    mean_omega = float(np.mean(omega_k))

    hbar = (2*vacuum_total + beta_phi*N_nodes) / sum_omega
    if hbar <= 0:
        return {'hbar': hbar, 'stable': False, 'reason': 'NEGATIVE HBAR (impossible)',
                'a_L_planck': float('nan')}

    # SI conversion
    c_QNG = np.sqrt(beta_phi/(z_coord*mu_phi))
    G_QNG = 0.0583  # Approximate, scales with beta_g not beta_phi
    c_SI = 2.998e8; G_SI = 6.674e-11; hbar_SI = 1.055e-34
    R = c_SI / c_QNG
    Q_h = hbar_SI / (hbar * R)
    Q_G = G_SI / (G_QNG * R**2)
    a_L = np.sqrt(Q_h * Q_G)
    a_M = np.sqrt(Q_h / Q_G)

    return {'hbar': hbar, 'stable': True, 'reason': 'OK',
            'a_L_planck': a_L/1.616e-35, 'a_M_planck': a_M/2.176e-8,
            'mean_omega': mean_omega, 'sum_omega': sum_omega}


def main():
    print("=" * 80)
    print("QNG-CPU-112: EXTREME scenarios — what destroys reality?")
    print("=" * 80)
    print()

    scenarios = [
        ("REFERINTA (universul nostru)", 0.06, 0.857, 6, 0),
        ("", None, None, None, None),
        ("=== ENERGIE EXTREMA ===", None, None, None, None),
        ("Energie 100% redusa (beta=0)", 0.0, 0.857, 6, 0),
        ("Energie 99.99% redusa", 6e-6, 0.857, 6, 0),
        ("Energie 50% redusa", 0.03, 0.857, 6, 0),
        ("Energie 10x mai mare", 0.6, 0.857, 6, 0),
        ("Energie 100x mai mare", 6.0, 0.857, 6, 0),
        ("ENERGIE NEGATIVA (anti-coupling)", -0.06, 0.857, 6, 0),
        ("", None, None, None, None),
        ("=== INERTIE EXTREMA ===", None, None, None, None),
        ("Inertie 0 (massless)", 0.06, 1e-10, 6, 0),
        ("Inertie infinita", 0.06, 1e10, 6, 0),
        ("Inertie negativa (impossible)", 0.06, -0.857, 6, 0),
        ("", None, None, None, None),
        ("=== GEOMETRIE EXTREMA ===", None, None, None, None),
        ("z=0 (no neighbors)", 0.06, 0.857, 0, 0),
        ("z=2 (1D-ish)", 0.06, 0.857, 2, 0),
        ("z=12 (FCC lattice)", 0.06, 0.857, 12, 0),
        ("z=26 (3D nearest+diagonals)", 0.06, 0.857, 26, 0),
        ("", None, None, None, None),
        ("=== VACUUM EXTREM ===", None, None, None, None),
        ("Vacuum = clasic (vacuum dominates)", 0.06, 0.857, 6, 658.56),
        ("Vacuum = -clasic (vacuum cancels)", 0.06, 0.857, 6, -658.56),
        ("Vacuum = 10x clasic", 0.06, 0.857, 6, 6585.6),
    ]

    print(f"{'Scenario':<45} {'hbar':>10} {'a_L/l_P':>10} {'Status':<30}")
    print("-" * 100)

    for label, beta, mu, z, vac in scenarios:
        if beta is None:
            print(label)
            continue
        r = compute_QNG_state(beta, mu, z, vac)
        if r['stable']:
            print(f"{label:<45} {r['hbar']:>10.4f} {r['a_L_planck']:>10.3f} {r['reason']:<30}")
        else:
            print(f"{label:<45} {'BROKEN':>10} {'-':>10} {r['reason']:<30}")

    print()
    print("=" * 80)
    print("INTERPRETARE FIZICA")
    print("=" * 80)
    print("""
1. ENERGIE = 0 -> Universul DISPARE
   - Nodurile nu interactioneaza
   - Nu exista unde, nu exista cuanta
   - hbar = 0/0 (nedefinit)
   - Realitatea se reduce la praf de noduri izolate

2. ENERGIE NEGATIVA -> Universul EXPLODEAZA exponential
   - Modurile au frecvente imaginare
   - Toate vibratiile cresc exponential in timp
   - Universul se "spulbera" in catastrofa instabila
   - Echivalent cu: AdS instability sau tachyon condensation

3. INERTIE 0 -> Frecvente infinite
   - Toate modurile vibreaza infinit de rapid
   - hbar -> 0, totul devine clasic
   - Universul nu poate sustine cuante

4. INERTIE INFINITA -> Universul INGHETAT
   - Frecvente -> 0
   - hbar -> infinit (totul cuantic)
   - Dar nimic nu se mai misca
   - Univers static permanent

5. z = 0 (no neighbors) -> Spatiul nu exista
   - Fiecare nod e izolat
   - Nu exista propagare a informatiei
   - Nu exista "spatiu" emergent

6. VACUUM ENERGY HUGE -> hbar drastic diferit
   - Universul ar avea o constanta cosmologica MASIVA
   - Expansiune accelerata uriasa
   - Stelele se distanteaza atat de repede ca nu pot exista
""")


if __name__ == '__main__':
    main()
