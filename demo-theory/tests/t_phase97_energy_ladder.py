"""
PHASE 97 (energy) -- the energy-PRODUCTION ladder and the ultimate extractable energy
from matter, in QNG.

Gabriel: what types of energy can be PRODUCED? Every process converts some fraction of
a mass m into usable energy, with the ceiling E = m c^2 (relativistic mass-energy, from
QNG's emergent SR, P02). Different processes extract different fractions.

  T1 the ladder: chemical, nuclear fission, nuclear fusion, matter-antimatter
     annihilation, black-hole processes -- ranked by fraction of m c^2 extracted.
  T2 QNG view: all are conversions of the binding/potential term (V_couple) or the full
     mass into kinetic/field energy; the ceiling is E=mc^2; the maximum is annihilation
     (100%, matter+antimatter = opposite phi-windings -> photons) and BH accretion (~42%).
  T3 QNG limits + the honest caveat: max density (P37), max T (P51), max field (P78)
     bound any reactor; and E=mc^2 holds as relativistic kinematics (emergent SR), though
     the ring 'rest mass = M_ring' identification was subtle (DER-QNG-044, rings dynamic).

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase97-energy-ladder-v1")

C = 2.998e8


def main():
    print("="*70)
    print("PHASE 97 (energy) -- the energy-production ladder (fraction of m c^2)")
    print("="*70)

    # T1: the ladder
    print("\n[T1] energy-production ladder (fraction of m c^2 extracted, per kg):")
    print("     process                     fraction of mc^2   energy per kg (J)")
    ladder = [
        ("chemical (burning/batteries)", 3e-10, "molecular bonds (EM potential)"),
        ("nuclear fission (U-235)", 9e-4, "nuclear binding (strong)"),
        ("nuclear fusion (H->He)", 7e-3, "nuclear binding (the Sun)"),
        ("BH accretion disk (max spin)", 0.42, "gravitational binding (Penrose/ISCO)"),
        ("matter-antimatter annihilation", 1.0, "full rest mass -> photons"),
    ]
    mc2_per_kg = C**2
    for name, frac, what in ladder:
        E = frac*mc2_per_kg
        print("     %-30s %.1e          %.2e   [%s]" % (name, frac, E, what))
    print("     => ceiling = E = m c^2 (annihilation, 100%%); BH accretion ~42%%;")
    print("        fusion 0.7%% (stars); fission 0.09%%; chemical ~1e-9. Each is a")
    print("        different fraction of the SAME m c^2 ceiling.")

    # T2: QNG view
    print("\n[T2] QNG view of each:")
    print("     - chemical: rearranging EM-bound potential V (electrons/edges) -> tiny fraction.")
    print("     - fission/fusion: nuclear binding (the V_couple/strong term) -> ~0.1-0.7%%.")
    print("     - annihilation: matter + antimatter = OPPOSITE phi-windings; they unwind")
    print("       completely (net winding 0) -> ALL rest mass -> photons (100%%, the ceiling).")
    print("     - BH accretion: gravitational binding energy released as matter falls;")
    print("       up to ~42%% for a maximally-spinning hole (most efficient steady source).")
    print("     => the convertible energy is the BINDING/mass term of H_QNG; the ceiling")
    print("        E=mc^2 is the full mass term (emergent SR, P02).")

    # T3: limits + caveat
    print("\n[T3] QNG limits on any energy production + honest caveat:")
    print("     - bounded by max density rho_max~54 Planck (P37), max T~1.6e32 K (P51),")
    print("       max E-field ~Schwinger (P78) -> a ceiling on reactor conditions.")
    print("     - NO free lunch (P96): the vacuum is the minimum; only the binding/mass")
    print("       term is convertible, never the ground state.")
    print("     - E=mc^2 holds as RELATIVISTIC kinematics (emergent SR); the QNG ring")
    print("       'rest mass = M_ring' identification was subtle (DER-QNG-044: rings are")
    print("       dynamic patterns), but mass-energy equivalence itself is sound.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  ceiling: E=mc^2 (annihilation 100%%); BH accretion ~42%%; fusion 0.7%%; fission 0.09%%")
    print("  QNG: convertible energy = binding/mass term of H_QNG; vacuum NOT extractable")
    print("  bounded by max density/T/field; mass-energy equivalence sound (ring rest-mass subtle)")

    verdict = (
        "THE_ENERGY-PRODUCTION_LADDER: E=mc^2_IS_THE_CEILING, ANNIHILATION_REACHES_IT, "
        "QNG_BOUNDS_THE_EXTREMES_AND_FORBIDS_THE_FREE-LUNCH. (T1) Every energy-production "
        "process converts some fraction of a mass m into usable energy, capped at E = m "
        "c^2 (relativistic mass-energy, from QNG's emergent special relativity, P02). "
        "The ladder, by fraction of m c^2: chemical ~3e-10 (molecular/EM bonds), nuclear "
        "fission ~9e-4 (0.09%), nuclear fusion ~7e-3 (0.7%, the Sun), black-hole "
        "accretion up to ~0.42 (42%, the most efficient steady astrophysical source, a "
        "maximally-spinning hole's ISCO), and matter-antimatter annihilation 1.0 (100%, "
        "the absolute ceiling). (T2) QNG's view: all of these are conversions of the "
        "BINDING/potential term (or the full mass term) of the single Hamiltonian H_QNG "
        "into kinetic and field energy -- chemical rearranges EM-bound potential, "
        "fission/fusion release nuclear binding (the strong/V_couple term), black-hole "
        "accretion releases gravitational binding, and annihilation is the cleanest: "
        "matter and antimatter are OPPOSITE phi-windings (P78), so they unwind "
        "completely to net winding zero, converting ALL the rest mass into photons -- "
        "100%, the E=mc^2 ceiling reached. (T3) QNG bounds any conceivable reactor by "
        "its hard limits -- maximum density (rho_max ~ 54 Planck densities, P37), "
        "maximum temperature (~1.6e32 K, P51), and maximum electric field (Schwinger, "
        "P78) -- and, crucially, forbids the free lunch (P96): only the binding/mass "
        "term is convertible, NEVER the vacuum (the ground state, E_vac=0). So the "
        "complete QNG energy-production picture: the convertible energy is the "
        "binding/mass content of matter, the ceiling is E=mc^2 (annihilation), the most "
        "efficient practical-astrophysical source is black-hole accretion (~42%), and "
        "no process can dip below the vacuum or exceed the substrate's density/"
        "temperature/field ceilings. HONEST CAVEAT: E=mc^2 holds in QNG as relativistic "
        "kinematics (emergent SR, P02), but the specific identification 'QNG ring rest "
        "mass = M_ring' was found subtle (DER-QNG-044: the rings are dynamic patterns, "
        "and M_ring is a topological charge, not cleanly a static rest mass) -- so the "
        "mass-energy equivalence as a PRINCIPLE is sound, while the detailed rest-mass "
        "of a specific QNG soliton needs the full v8 dynamics. The ladder fractions are "
        "standard nuclear/astrophysics, framed in QNG's energy taxonomy; the bounds and "
        "the no-free-lunch are the QNG-specific content. No hype: the maximum is E=mc^2 "
        "(annihilation), nothing exceeds it, and the vacuum is off-limits.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"ladder": {n: f for n, f, _ in ladder}, "ceiling": "E=mc^2 (annihilation 100%)",
                   "most_efficient_steady": "BH accretion ~42%",
                   "qng_limits": "max density P37, max T P51, max field P78; no vacuum extraction P96",
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
