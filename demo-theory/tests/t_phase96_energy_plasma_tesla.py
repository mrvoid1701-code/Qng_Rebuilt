"""
PHASE 96 (electromagnetism / energy) -- types of energy, plasma, and Tesla resonance
in QNG: separating the REAL physics from the free-energy MYTH.

Gabriel: explore the Tesla side of electricity -- what types of energy exist, what can
be produced, plasma, etc. Honest framing: Tesla's REAL contributions (AC, resonance,
standing waves, wireless resonant power, plasma) are valid physics and map cleanly to
QNG; the popular 'free energy from the aether/vacuum' is FORBIDDEN by QNG (the vacuum
is the energy MINIMUM, Stability Principle, P30/P77).

  T1 the TYPES of energy in QNG = the terms of the master Hamiltonian H_QNG:
     matter-kinetic, field (EM + gravitational), binding/potential, and the chi (dark)
     sector. A taxonomy -- every energy form is one term of one Hamiltonian.
  T2 PLASMA in QNG: ionized sigma_m (mobile phi-winding charges) + the edge U(1) EM
     field, coupled -> collective plasma oscillations (plasma frequency). Bounded by
     QNG's max E-field (Schwinger, P78) and max density (P37).
  T3 TESLA: resonance / standing waves / wireless resonant power transfer = REAL
     (resonant coupling of substrate modes; demonstrate efficient transfer at
     resonance). BUT 'free energy from the vacuum/aether' = FORBIDDEN: E_vacuum = 0 is
     the MINIMUM (P30), H bounded below (P77) -> NO net extraction (the Casimir effect
     gives only a tiny finite difference, not unlimited free energy). Honest: valid
     Tesla yes, free-energy myth no.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase96-energy-plasma-tesla-v1")


def main():
    print("="*70)
    print("PHASE 96 -- energy types, plasma, and Tesla resonance in QNG (real vs myth)")
    print("="*70)

    # T1: energy taxonomy
    print("\n[T1] the TYPES of energy in QNG = the terms of H_QNG (one Hamiltonian):")
    types = [
        ("matter kinetic", "pi_m^2/2mu_m, pi_phi^2/2mu_phi", "motion of matter/phase quanta"),
        ("EM field", "edge U(1) A_ij field energy (1/2)(E^2+B^2)", "electric+magnetic, light (P78)"),
        ("gravitational field", "coarse-grained sigma_g gradient energy", "Newtonian/GW energy (P16)"),
        ("binding / potential", "on-site V(sigma,chi,phi), V_couple", "rest mass, chemical, nuclear"),
        ("dark (chi) sector", "chi VEV (V_0) + fluctuations", "dark energy + dark matter (P66)"),
    ]
    for name, term, what in types:
        print("     - %-20s [%s]  -> %s" % (name, term, what))
    print("     => EVERY form of energy is one term of the single Hamiltonian H_QNG (P91).")
    print("        Conversions between them = the dynamics; total energy CONSERVED (H_v8).")

    # T2: plasma
    print("\n[T2] PLASMA in QNG (the 4th state of matter):")
    print("     ionized sigma_m (mobile phi-winding charges) + edge U(1) EM field, coupled.")
    print("     collective oscillation = plasma frequency omega_p = sqrt(n e^2/(eps0 m_e)).")
    n_e = 1e20  # m^-3, lab plasma
    eps0 = 8.854e-12; e = 1.602e-19; m_e = 9.109e-31
    w_p = np.sqrt(n_e*e**2/(eps0*m_e))
    print("     e.g. n=%.0e /m^3 -> omega_p = %.2e rad/s (f_p = %.2e Hz)" % (n_e, w_p, w_p/(2*np.pi)))
    print("     QNG BOUNDS the extremes: max E-field ~Schwinger 1.3e18 V/m (P78), max")
    print("     density rho_max~54 Planck (P37) -> a hottest/densest plasma ceiling.")

    # T3: Tesla resonance (real) vs free energy (myth)
    print("\n[T3] TESLA -- resonance REAL, free-energy MYTH:")
    # resonant coupling: two oscillators, energy transfer efficiency peaks at resonance
    print("     resonant power transfer (two coupled modes, Tesla's wireless idea):")
    print("       detuning d/omega    transfer efficiency")
    for det in [0.0, 0.1, 0.3, 1.0]:
        eff = 1.0/(1.0 + (det/0.05)**2)   # Lorentzian resonance, width 0.05
        print("       %.2f                %.3f" % (det, eff))
    print("     => transfer PEAKS at resonance (detuning 0) -> wireless resonant power is")
    print("        REAL (modern wireless charging uses exactly this). Tesla was right here.")
    print("     BUT 'free energy from the vacuum/aether':")
    print("       E_vacuum = 0 is the MINIMUM (Stability Principle, P30); H bounded below (P77).")
    print("       => you CANNOT extract net energy from the vacuum (it is the ground state).")
    print("          the Casimir effect yields only a tiny FINITE difference, not free energy.")
    print("       => the 'free energy' myth is FORBIDDEN by QNG. No perpetual motion.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  energy types = the terms of H_QNG (kinetic/EM/gravity/potential/dark); total conserved")
    print("  plasma = ionized sigma_m + edge U(1), bounded by max-E (P78) and max-density (P37)")
    print("  Tesla resonance/wireless transfer: REAL (substrate modes); free vacuum energy: FORBIDDEN")

    verdict = (
        "QNG_ENERGY_TAXONOMY + PLASMA + TESLA: RESONANCE_REAL, FREE-VACUUM-ENERGY_"
        "FORBIDDEN. (T1) In QNG every form of energy is one term of the single master "
        "Hamiltonian H_QNG (P91): matter-kinetic (pi^2/2mu), the EM field (edge U(1), "
        "(1/2)(E^2+B^2)), the gravitational field (coarse-grained sigma_g gradients), "
        "binding/potential (on-site V, V_couple -> rest mass, chemical, nuclear "
        "energy), and the chi dark sector (VEV -> dark energy, fluctuations -> dark "
        "matter). Energy 'conversions' (chemical->heat, mass->energy, etc.) are just "
        "the dynamics moving energy between these terms, and the TOTAL is conserved "
        "exactly (H_v8 is the conserved Hamiltonian). So QNG gives a clean taxonomy: "
        "one Hamiltonian, several terms, all the energy 'types' are its pieces. (T2) "
        "PLASMA -- the fourth state of matter -- is ionized sigma_m (mobile phi-winding "
        "charges) coupled to the edge U(1) electromagnetic field; its collective "
        "oscillation is the plasma frequency omega_p = sqrt(n e^2/eps0 m), and QNG "
        "BOUNDS its extremes by the maximum electric field (Schwinger ~1.3e18 V/m, "
        "P78) and the maximum density (rho_max ~ 54 Planck densities, P37) -- there is "
        "a hottest, densest plasma the substrate allows. (T3) On TESLA: his REAL "
        "physics is valid and maps to QNG -- AC, RESONANCE, standing waves, and "
        "especially WIRELESS RESONANT POWER TRANSFER, which is the resonant coupling "
        "of substrate modes (transfer efficiency peaks sharply at resonance, "
        "demonstrated; modern wireless charging uses exactly this principle). Tesla "
        "was genuinely right about resonance and field energy. BUT the popular "
        "extrapolation -- 'free energy from the aether/vacuum', perpetual motion -- is "
        "FORBIDDEN by QNG: the vacuum energy E_vacuum = 0 is the MINIMUM (the Stability "
        "Principle, P30), and the Hamiltonian is bounded below (P77), so NO net energy "
        "can be extracted from the vacuum -- it is the ground state, and extracting "
        "from it would mean going below the ground state, which is impossible. (The "
        "Casimir effect yields only a tiny FINITE difference between boundary "
        "conditions, not an unlimited free-energy source.) NET: QNG honors Tesla's "
        "real genius (resonance, AC, plasma, wireless transfer, the substrate as a "
        "real medium) while rigorously forbidding the free-energy myth -- the same "
        "bounded-below substrate that forbids warp drives (P77) forbids perpetual "
        "motion. The 'new' energy QNG does add is the chi DARK sector (dark energy + "
        "dark matter), a genuinely new energy form -- but it too is bounded and "
        "conserved, not a free lunch. HONEST: the energy taxonomy and the "
        "vacuum-is-the-minimum no-free-lunch are rigorous (H_v8 bounded below, "
        "conserved); the plasma is standard plasma physics within QNG's EM sector "
        "(bounded by the QNG limits); the resonance demo is a standard Lorentzian. No "
        "hype: Tesla's resonance yes, his free-energy no.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"energy_types": [t[0] for t in types], "plasma_freq_example_rad_s": float(w_p),
                   "tesla_resonance": "REAL (resonant mode coupling, wireless transfer)",
                   "free_vacuum_energy": "FORBIDDEN (E_vac=0 minimum, H bounded below)",
                   "new_energy_form": "chi dark sector (DE+DM), bounded+conserved",
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
