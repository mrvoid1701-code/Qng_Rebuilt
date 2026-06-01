"""QNG-CPU-135 -- Audit: does QNG v10/v11 contain electromagnetism?

This audit asks: can EM emerge from existing QNG fields, or do we need
a new ontology (v12 extension)?

Standard EM requirements:
  1. Vector gauge field A_mu (4 components in 4D, 3 spatial in lattice)
  2. Field strength F_mu_nu = d_mu A_nu - d_nu A_mu (antisymmetric)
  3. Local U(1) gauge invariance: A_mu -> A_mu + d_mu chi
  4. Massless propagating photon (spin-1)
  5. Coupling to charged matter via covariant derivative D_mu = d_mu - i e A_mu

Tests against current QNG fields:
  A. phi-phase: scalar (spin-0). Has GLOBAL U(1) symmetry, but not LOCAL.
  B. chi: scalar (spin-0). Already used for matter-gravity responsiveness.
  C. sigma_g: scalar (spin-0). Already used for gravitational potential.
  D. Composite fields: gradient of phi, etc.

Each test:
  - Identify spin via field transformation
  - Check if EM-like F_mu_nu can be constructed
  - Check if it produces non-trivial propagating modes
"""
import numpy as np

print("=" * 80)
print("QNG-CPU-135: Does QNG v10/v11 contain electromagnetism?")
print("=" * 80)
print()

# ==============================================================
# Section A: phi-phase as photon candidate
# ==============================================================
print("=" * 80)
print("A. phi-phase field as photon candidate")
print("=" * 80)
print()
print("phi_n is a scalar field per node, phi_n in [-pi, pi].")
print()
print("Symmetries:")
print("  GLOBAL U(1): phi -> phi + alpha (constant) leaves Hamiltonian invariant.")
print("  LOCAL U(1):  phi -> phi + alpha(x) does NOT leave H_XY invariant:")
print("    cos(phi_i - phi_j) -> cos(phi_i - phi_j + (alpha_i - alpha_j))")
print()
print("  -> phi has GLOBAL U(1) symmetry only.")
print()
print("Spin of phi excitations:")
print("  phi is scalar field at each node.")
print("  Excitations (phasons) transform trivially under rotation -> SPIN 0.")
print()
print("Conclusion A: phi-phase produces SPIN-0 phonons (Goldstone modes of")
print("              broken global U(1)), NOT spin-1 photons. NOT a photon candidate.")
print()

# ==============================================================
# Section B: gradient of phi as gauge field?
# ==============================================================
print("=" * 80)
print("B. Gradient of phi as vector potential A_i candidate")
print("=" * 80)
print()
print("Naively: (grad phi)_i has 3 spatial components, transforms as vector.")
print("  Could (grad phi)_i play role of vector potential A_i?")
print()
print("Test: compute field strength F_ij = d_i A_j - d_j A_i")
print()
print("  If A_i = (grad phi)_i = d_i phi:")
print("  F_ij = d_i (d_j phi) - d_j (d_i phi) = 0  identically (commuting partials)")
print()
print("=> Field strength VANISHES. No magnetic field, no electric field.")
print("   Gradient-of-scalar is PURE GAUGE in EM sense — gauge-trivial.")
print()
print("Conclusion B: A_i = grad phi gives F_ij = 0 -> NO EM dynamics.")
print()

# ==============================================================
# Section C: chi field as scalar potential candidate
# ==============================================================
print("=" * 80)
print("C. chi field as scalar potential A_0 candidate")
print("=" * 80)
print()
print("chi_n is per-node scalar. Could it be the time component A_0 of EM gauge field?")
print()
print("In Coulomb gauge: A_0(x) = phi_Coulomb(x), set by Poisson eq.")
print("chi obeys screened Poisson: (CHI_DECAY - CHI_REL/z * Lap) chi = source")
print()
print("Differences from EM A_0:")
print("  - chi has DECAY TERM (CHI_DECAY): dissipative dynamics")
print("    EM A_0 satisfies Laplace eq (no decay) in vacuum")
print("  - chi sourced by sigma_g deviation, NOT charge density")
print("  - chi has NO companion vector field A_i in QNG")
print()
print("Conclusion C: chi is NOT EM A_0. Different sourcing, different dynamics.")
print()

# ==============================================================
# Section D: sigma_g as A_0 candidate
# ==============================================================
print("=" * 80)
print("D. sigma_g deviation as A_0 candidate")
print("=" * 80)
print()
print("sigma_g deviation produces gravitational potential Phi (GRAV-C1).")
print("In GR weak-field: Phi appears in g_00. So sigma_g IS gravity, not EM.")
print()
print("Conclusion D: sigma_g is for gravity, not EM. Already used.")
print()

# ==============================================================
# Section E: composite vector candidates
# ==============================================================
print("=" * 80)
print("E. Composite vector field candidates")
print("=" * 80)
print()
print("Could ANY combination of QNG scalars give an INDEPENDENT vector field")
print("with non-trivial F_ij?")
print()
print("Standard composites (gradients of scalars):")
print("  - grad sigma_g  (curl-free)")
print("  - grad sigma_m  (curl-free)")
print("  - grad phi      (curl-free)")
print("  - grad chi      (curl-free)")
print()
print("Cross products: e.g., (grad sigma_m) x (grad sigma_g)")
print("  - This IS divergence-free (vector identity)")
print("  - But it is determined by sigma_m and sigma_g — not independent DOF")
print()
print("Linear combinations of scalar gradients ALL have curl = 0 in vacuum.")
print("To get non-trivial F_ij = curl A, need INDEPENDENT vector field.")
print()
print("Conclusion E: no scalar composite gives propagating EM field.")
print()

# ==============================================================
# Section F: counting DOF for EM
# ==============================================================
print("=" * 80)
print("F. Degrees-of-freedom counting for EM")
print("=" * 80)
print()
print("EM requires: 4 components A_mu (or 3 spatial A_i in 3D) per spacetime point.")
print("  Gauge fixing reduces to 2 physical (transverse photon polarizations).")
print()
print("QNG v10 fields: 4 scalars per node (sigma_g, sigma_m, phi, chi).")
print("  Total DOF per node: 4 (all spin-0).")
print("  None of these are independent vectors.")
print()
print("v11 added: h_ij rank-2 tensor (5 DOF after traceless), 2 physical TT.")
print("  These are SPIN-2, not spin-1.")
print()
print("=> QNG v10/v11 has NO independent rank-1 vector field. EM cannot exist.")
print()

# ==============================================================
# Section G: Verdict and v12 proposal
# ==============================================================
print("=" * 80)
print("G. VERDICT")
print("=" * 80)
print()
print("QNG v10/v11 DOES NOT contain electromagnetism.")
print()
print("Reasons:")
print("  1. All scalar fields are spin-0; cannot produce spin-1 photon.")
print("  2. No independent vector field in ontology.")
print("  3. Gradients of scalars are curl-free (gauge-trivial).")
print("  4. phi has only GLOBAL U(1) symmetry; LOCAL gauge requires edge field.")
print()
print("Gap 15 (NEW): Electromagnetism missing from QNG ontology.")
print()
print("=" * 80)
print("Proposed v12 extension")
print("=" * 80)
print()
print("To add EM, parallel to v11 (which added h_ij for spin-2 graviton),")
print("v12 would add a U(1) gauge field on lattice EDGES:")
print()
print("  A_{ij}: real scalar per directed edge, A_{ij} = -A_{ji}")
print("  Field strength on plaquettes: F_{ijkl} = A_{ij} + A_{jk} + A_{kl} + A_{li}")
print("  Lagrangian: L_A = -(1/4 mu_A) Sum_plaquettes F^2")
print("  Coupling to matter: replace cos(phi_i - phi_j) -> cos(phi_i - phi_j - e A_{ij})")
print()
print("This is standard COMPACT U(1) lattice gauge theory (Wilson 1974).")
print()
print("Predictions:")
print("  - Massless photon (spin-1, 2 polarizations) from A_{ij} fluctuations")
print("  - Local U(1) gauge symmetry: phi -> phi + alpha(x), A_{ij} -> A_{ij} + d_{ij}alpha")
print("  - Coupling constant e from substrate parameters (TBD)")
print("  - Matter (sigma_m vortex rings) coupling to A via cos(phi - eA) term")
print()
print("Same status as v11: this is AXIOMATIC EXTENSION, not derivation.")
print("It adds the minimal required ontology to have EM in QNG.")
print()
print("Would close Gap 15. Would enable:")
print("  - Particle identification (charged leptons via EM coupling)")
print("  - Distinction baryons vs DM (via EM coupling)")
print("  - Atomic physics, spectra")
print("  - Potentially: dark matter as EM-decoupled vortex rings")
print()
print("Same caveat as v11: parallels Higgs in Standard Model — added for")
print("observation, not derived. Standard physics move, not 'trick'.")
