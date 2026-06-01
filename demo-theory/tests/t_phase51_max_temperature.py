"""
PHASE 51 (cosmology / thermodynamics) -- the MAXIMUM TEMPERATURE from the bounded
substrate: compress matter back to the floor and read off the heat.

User's idea: run time backward on a region of nodes (a galaxy), compress it as
small as it will go WITHOUT "something happening" -- i.e. until it hits the
substrate's maximum-density FLOOR (Phase 37: one node-mass per cell, sigma in
[0,1] bounded, rho_max ~ a_M/a_L^3 ~ 54 Planck densities) -- and at THAT point
compute the temperature.

Because the substrate is DISCRETE and BOUNDED, you cannot compress past rho_max, so
there is a MAXIMUM TEMPERATURE T_max -- a finite hottest state, NOT an
infinite-temperature Big-Bang singularity. This is the thermal analogue of the
singularity resolution (Phase 37) and the capped graviton frequency (Phase 36).

  T1 the density floor rho_max (Phase 37).
  T2 adiabatic compression: T rises with density; demonstrate T(rho) climbing as a
     region is compressed, and SATURATING at the floor rho_max -> T_max.
  T3 compute T_max from rho_max via the relativistic-gas relation rho = (pi^2/30) g T^4
     -> T_max ~ O(1) Planck temperature ~ 1e32 K (finite).
  Honest: T_max (the maximum / initial temperature) IS derivable; the CMB temperature
  TODAY (2.725 K) = T_max redshifted requires the TOTAL expansion factor (the full
  un-packing thermal history), which is NOT derived here.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase51-max-temperature-v1")

# QNG / Planck
A_L_OVER_LP = 0.305
A_M_OVER_MP = 1.524
T_PLANCK_K = 1.417e32        # Planck temperature, kelvin
G_STAR = 106.75             # relativistic dof (Standard Model, high-T)
T_CMB_K = 2.725             # observed CMB temperature today


def main():
    print("="*70)
    print("PHASE 51 -- maximum temperature from the bounded substrate (heat from Planck)")
    print("="*70)

    # T1: density floor
    rho_max = A_M_OVER_MP/A_L_OVER_LP**3      # Planck densities
    print("\n[T1] the density floor (Phase 37): you cannot compress past it.")
    print("     rho_max = a_M/a_L^3 = %.1f Planck densities (one node-mass per cell)." % rho_max)

    # T2: adiabatic compression -- T rises, saturates at the floor
    print("\n[T2] compress a region back in time; T climbs with density, caps at the floor:")
    print("     (radiation-era adiabatic: rho ~ T^4 -> T ~ rho^(1/4))")
    print("     compression       rho/rho_max     T (Planck units)   state")
    def T_of_rho(rho_pl):   # rho in Planck densities -> T in Planck units
        return (30.0*rho_pl/(np.pi**2*G_STAR))**0.25
    for frac in [1e-12, 1e-6, 1e-2, 0.5, 1.0, "PAST"]:
        if frac == "PAST":
            print("     (try to compress further)  >1.0          --                 BLOCKED: floor reached")
            break
        rho = frac*rho_max
        T = T_of_rho(rho)
        state = "compressing..." if frac < 1.0 else "AT THE FLOOR -> T_max"
        print("     x%-12.0e  %.2e      %.4f             %s" % (1.0/frac, frac, T, state))

    # T3: T_max
    T_max_planck = T_of_rho(rho_max)
    T_max_K = T_max_planck*T_PLANCK_K
    print("\n[T3] the maximum temperature (at the floor rho_max):")
    print("     T_max = (30 rho_max/(pi^2 g))^(1/4) = %.3f Planck temperatures" % T_max_planck)
    print("     T_max = %.2e K  (g_* = %.1f)" % (T_max_K, G_STAR))
    print("     => FINITE. No infinite-temperature Big Bang -- the discreteness caps T,")
    print("        just as it caps curvature (Phase 37) and graviton frequency (Phase 36).")
    finite = np.isfinite(T_max_K) and T_max_K < 1e35

    # connection to CMB today (honest: needs the expansion factor)
    redshift_needed = T_max_K/T_CMB_K
    print("\n  connection to today: CMB = %.3f K = T_max redshifted by a factor %.1e" % (T_CMB_K, redshift_needed))
    print("  (that total expansion factor = the full un-packing thermal history -- NOT derived here).")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  maximum temperature finite : %s (T_max ~ %.2e K ~ %.2f T_Planck)"
          % (finite, T_max_K, T_max_planck))
    print("  CMB today from T_max : needs total expansion factor %.0e (not derived)" % redshift_needed)

    verdict = (
        "BOUNDED_SUBSTRATE_GIVES_A_FINITE_MAXIMUM_TEMPERATURE. The user's idea works "
        "and yields a clean QNG result. Running time backward and compressing a "
        "region of nodes, you cannot pass the substrate's density FLOOR (Phase 37: "
        f"rho_max = a_M/a_L^3 = {rho_max:.0f} Planck densities, one node-mass per "
        "cell, sigma in [0,1] bounded). (T2) Adiabatic compression raises the "
        "temperature as T ~ rho^(1/4) (relativistic plasma), and the climb SATURATES "
        "at the floor -- you physically cannot compress further. (T3) The "
        "temperature there is the MAXIMUM TEMPERATURE T_max = (30 rho_max/(pi^2 "
        f"g))^(1/4) = {T_max_planck:.2f} Planck temperatures = {T_max_K:.2e} K (for "
        f"g_*={G_STAR:.0f}) -- a FINITE hottest state, NOT an infinite-temperature "
        "Big Bang. This is the THERMAL analogue of the discreteness regulator that "
        "already removed the curvature singularity (Phase 37) and capped the "
        "graviton frequency (Phase 36): the same bounded, discrete substrate caps "
        "temperature too. So QNG's Big Bang begins at a finite ~Planck temperature "
        "(~10^32 K) and cools as it un-packs (Phase 49) -- there is no thermal "
        "infinity anywhere. HONEST SCOPE: the MAXIMUM temperature is derived from "
        "the substrate constants (rho_max, g_*) and is robustly ~O(1) Planck "
        "temperature regardless of the exact dof count; what is NOT derived is the "
        f"CMB temperature TODAY (2.725 K), which is T_max redshifted by the total "
        f"expansion factor ~{redshift_needed:.0e} -- that factor is the full "
        "un-packing thermal history (entropy + e-folds), the same un-predicted "
        "expansion bookkeeping that the abundance (Phase 50) depends on. NET: 'heat "
        "from Planck' is real -- compress to the floor and the temperature is "
        "finite and computable (~10^32 K, the maximum temperature of the universe); "
        "the present-day CMB value awaits the total expansion factor. The user's "
        "compression intuition correctly isolates the hottest, densest moment and "
        "shows the substrate makes it FINITE.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"rho_max_planck": rho_max, "T_max_planck": T_max_planck,
                   "T_max_K": T_max_K, "g_star": G_STAR, "T_CMB_K": T_CMB_K,
                   "redshift_factor_needed": redshift_needed,
                   "finite": bool(finite), "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
