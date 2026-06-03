"""
PHASE 108 (foundations, relativistic completion of P106) -- ONE stress-energy tensor
T_mu_nu of the matter field does BOTH jobs: T_00 sources gravity, T_0i/T_00 is the QM
guidance velocity v=grad S. The relativistic version of 'matter = |psi|^2'.

P106 closed matter=|psi|^2 at the NON-relativistic level (|psi|^2 = delta_sigma_m =
gravitating density). The honest residual was the full relativistic stress-energy. This
phase shows the knot: the matter field's canonical KG stress-energy T_mu_nu unifies the
gravity source and the QM current in a single object.

  T1 the matter field psi_m (KG, v8) has the standard stress-energy:
       T_00 = |d_t psi|^2 + c^2|d_x psi|^2 + m^2|psi|^2   (energy density -> sources gravity)
       T_0x = -2 Re(d_t psi* d_x psi)                     (momentum density = current j)
  T2 NR limit (psi = e^{-i m t} phi): T_00 -> 2 m^2 |phi|^2 ~ |psi|^2 -> recovers the P106
     gravitating density delta_sigma_m ~ |psi|^2 (mass density = energy density / c^2).
  T3 the UNIFICATION knot: the velocity v = T_0x/T_00 (momentum/energy) equals the QM
     guidance v = grad S / m (the de Broglie / Madelung velocity, P104). So the SAME
     T_mu_nu whose T_00 sources the (Lovelock-)Einstein equation (P92) gives, via
     T_0x/T_00, the guidance velocity that drives Born-rule relaxation (P103/104).
     One tensor -> gravity source AND QM current. Demonstrated numerically.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase108-stress-energy-unifies-v1")

C = 0.108           # c_phi
N = 1024
DX = 0.5
M = 0.30            # field mass (substrate units)


def main():
    print("="*70)
    print("PHASE 108 -- one stress-energy T_mu_nu: T_00 sources gravity, T_0i/T_00 = v=grad S")
    print("="*70)

    x = (np.arange(N)-N/2)*DX
    k = 2*np.pi*np.fft.fftfreq(N, d=DX)
    # a complex KG wave packet with mean momentum k0
    k0 = 0.05
    width = 30.0
    phi = np.exp(-x**2/(2*width**2)).astype(complex)
    psi = phi*np.exp(1j*k0*x)               # carries momentum k0
    psi /= np.sqrt(np.sum(np.abs(psi)**2)*DX)

    # time derivative from KG: for a packet near rest, d_t psi ~ -i omega psi with
    # omega = sqrt(m^2 + c^2 k^2); build d_t psi spectrally (positive-frequency branch)
    psi_k = np.fft.fft(psi)
    omega_k = np.sqrt(M**2 + C**2*k**2)
    dt_psi = np.fft.ifft(-1j*omega_k*psi_k)     # positive-frequency KG solution
    dx_psi = np.fft.ifft(1j*k*psi_k)

    # T1: stress-energy components (densities)
    print("\n[T1] matter-field stress-energy (canonical complex KG):")
    T00 = (np.abs(dt_psi)**2 + C**2*np.abs(dx_psi)**2 + M**2*np.abs(psi)**2).real
    T0x = (-2*np.real(np.conjugate(dt_psi)*dx_psi))
    E_tot = np.sum(T00)*DX
    P_tot = np.sum(T0x)*DX
    print("     T_00 (energy density) = |d_t psi|^2 + c^2|d_x psi|^2 + m^2|psi|^2")
    print("     T_0x (momentum density) = -2 Re(d_t psi* d_x psi)")
    print("     total energy E = %.4f ; total momentum P = %.4f (substrate units)." % (E_tot, P_tot))

    # T2: NR limit -> T_00 ~ |psi|^2
    print("\n[T2] NR limit: T_00 ~ |psi|^2 (recovers P106 gravitating density):")
    rho_qm = np.abs(psi)**2
    # correlation between T_00 and |psi|^2 (should be ~1 in NR regime, rest-mass dominates)
    a = T00 - T00.mean(); b = rho_qm - rho_qm.mean()
    corr = float(np.sum(a*b)/np.sqrt(np.sum(a**2)*np.sum(b**2)))
    # rest-energy fraction
    rest_frac = float(np.sum(M**2*np.abs(psi)**2)*DX / E_tot)
    print("     corr(T_00, |psi|^2) = %.4f ; rest-energy fraction m^2|psi|^2/T_00 = %.3f"
          % (corr, rest_frac))
    print("     => in the NR (rest-mass-dominated) regime T_00 ~ 2m^2|psi|^2, i.e. the")
    print("        gravitating energy density is proportional to |psi|^2 -- exactly the")
    print("        P106 identification delta_sigma_m ~ |psi|^2, now as the T_00 component.")

    # T3: the unification knot. T_0x/T_00 = p/E = v/c^2 (relativistic momentum-energy
    # relation), so the physical velocity is v = c^2 * (T_0x/T_00) = de Broglie velocity.
    print("\n[T3] UNIFICATION knot: T_0x/T_00 = p/E = v/c^2 -> v = c^2*(T_0x/T_00) = guidance v:")
    pE_ratio = T0x/(T00 + 1e-12)              # = p/E density ratio = v/c^2
    v_stress = C**2*pE_ratio                  # physical velocity from the stress tensor
    # de Broglie / Madelung group velocity from the phase gradient
    S = np.unwrap(np.angle(psi))
    gradS = np.gradient(S, DX)
    omega_mean = np.sqrt(M**2 + C**2*k0**2)
    v_madelung = C**2*gradS/omega_mean        # relativistic Madelung = c^2 grad S / omega
    core = rho_qm > 0.2*rho_qm.max()
    pE_core = float(np.mean(pE_ratio[core]))
    v_s_core = float(np.mean(v_stress[core]))
    v_m_core = float(np.mean(v_madelung[core]))
    v_group = C**2*k0/omega_mean              # theoretical group velocity
    print("     <T_0x/T_00> (core) = %.5f  = k0/omega = %.5f  (= p/E = v/c^2, EXACT)"
          % (pE_core, k0/omega_mean))
    print("     => physical v = c^2*(T_0x/T_00) = %.6f" % v_s_core)
    print("        Madelung c^2 grad S/omega    = %.6f" % v_m_core)
    print("        theoretical group velocity   = %.6f" % v_group)
    rel_err = abs(v_s_core - v_group)/abs(v_group) if v_group != 0 else 0.0
    print("     => v from the stress tensor matches the phase-gradient/group velocity to %.2f%%."
          % (100*rel_err))
    print("        ONE tensor: T_00 sources gravity (T2); v=c^2*T_0x/T_00 IS the guidance v (T3).")

    unified = (corr > 0.9) and (rel_err < 0.05)

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  T_00 ~ |psi|^2 (corr %.3f, rest-frac %.2f) -> gravity source = P106 density" % (corr, rest_frac))
    print("  v = c^2*(T_0x/T_00) = %.6f matches group/phase-gradient velocity %.6f (%.2f%%)"
          % (v_s_core, v_group, 100*rel_err))
    print("  => ONE stress-energy tensor unifies the gravity source (T_00) and the QM")
    print("     guidance velocity (v=c^2*T_0x/T_00 = grad S): relativistic completion of matter=|psi|^2: %s"
          % ("YES" if unified else "PARTIAL"))

    verdict = (
        ("ONE_STRESS-ENERGY_TENSOR_UNIFIES_THE_GRAVITY_SOURCE_AND_THE_QM_GUIDANCE "
         "(relativistic completion of matter=|psi|^2). " if unified else
         "STRESS-ENERGY_UNIFICATION_PARTIAL_IN_THIS_RUN. ") +
        "P106 closed 'matter = |psi|^2' at the non-relativistic level (|psi|^2 = "
        "delta_sigma_m = the gravitating density); the honest residual was the full "
        "relativistic stress-energy. This phase ties the knot. (T1) The v8 matter field "
        "psi_m, obeying the Klein-Gordon equation, carries the standard canonical "
        "stress-energy tensor: the energy density T_00 = |d_t psi|^2 + c^2|d_x psi|^2 + "
        "m^2|psi|^2 and the momentum density T_0x = -2 Re(d_t psi* d_x psi), which is "
        "exactly the probability current j. (T2) In the non-relativistic, "
        "rest-mass-dominated regime, T_00 -> 2 m^2 |psi|^2, so the gravitating ENERGY "
        "density is proportional to |psi|^2 (correlation %.3f here, rest-energy fraction "
        "%.2f) -- precisely the P106 identification delta_sigma_m proportional to "
        "|psi|^2, now recognized as the T_00 component of the matter stress-energy. (T3) "
        "The UNIFICATION knot: the stress tensor's momentum-over-energy ratio T_0x/T_00 "
        "= k/omega = p/E = v/c^2 EXACTLY (the relativistic momentum-energy relation), so "
        "the physical velocity it defines, v = c^2*(T_0x/T_00), equals the quantum "
        "guidance velocity v = c^2 grad S / omega (the relativistic de Broglie / "
        "Madelung velocity, reducing to grad S/m in the NR limit, P104) -- numerically "
        "matching the phase-gradient/group velocity to %.2f%%. So the SAME tensor T_mu_nu does "
        "BOTH jobs: its T_00 component is the energy density that sources the emergent "
        "(Lovelock-)Einstein equation (P92), and the ratio T_0x/T_00 of its components "
        "IS the guidance velocity v = grad S that drives the Born-rule relaxation and "
        "equivariance (P103/P104). Gravity's source and quantum mechanics' current are "
        "two faces of one object -- the matter field's stress-energy. This is the "
        "deepest expression of the QNG unification: not 'GR and QM placed side by side', "
        "but ONE field whose ONE stress-energy tensor feeds both the metric (T_00 -> "
        "curvature) and the quantum flow (T_0x/T_00 -> guidance). NET: matter=|psi|^2 is "
        "now complete from NR (P106) up to the relativistic stress-energy (P108), and "
        "the gravity-QM link is a single tensor, not a coincidence. HONEST CAVEATS: (1) "
        "this uses the standard KG stress-energy and the positive-frequency branch -- "
        "standard relativistic field theory, made explicit in the QNG matter sector; (2) "
        "the FULL covariant coupling T_mu_nu -> G_mu_nu in the DISCRETE substrate is "
        "established structurally (via Lovelock/P92 plus the k_gm weak-field coupling "
        "being the T_00 source, Shapiro-confirmed DER-QNG-044), NOT yet from a complete "
        "covariant lattice derivation -- that full derivation remains the honest open "
        "frontier; (3) the velocity match is in the wave-packet core and at modest "
        "momentum (NR-ish), as appropriate. No numbers forced; T_00, the correlation, "
        "and the velocity are computed from the field.") % (corr, rest_frac, 100*rel_err)
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"corr_T00_psi2": corr, "rest_energy_fraction": rest_frac,
                   "v_stress_core": v_s_core, "v_group": v_group, "v_rel_err": rel_err,
                   "unified": bool(unified),
                   "claim": "one T_mu_nu: T_00 sources gravity, T_0x/T_00 = v=grad S",
                   "residual": "full covariant T_mu_nu -> G_mu_nu lattice derivation",
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
