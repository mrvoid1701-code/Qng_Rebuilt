"""
PHASE 2 TEST -- validate the edge photon in the ACTUAL v12 lattice structure
(DER-QNG-076), not the idealized spectral operator used in E7.

v12 Lagrangian (DER-QNG-076):
    L_A = (1/2 mu_A) sum_edges (d_t A_ij)^2  -  (1/4 mu_A) sum_plaquettes F_p^2
    F_p = A_ij + A_jk + A_kl + A_li   (lattice curl around a plaquette)

We implement the lattice Maxwell EOM on a cubic lattice with link variables
A_a(n) (a in {x,y,z}) and electric momenta E_a(n):
    Adot_a = E_a
    Edot_a(n) = - sum_{b != a} [ F_ab(n) - F_ab(n - e_b) ]      (lattice Ampere)
    F_ab(n)  = A_a(n) + A_b(n+e_a) - A_a(n+e_b) - A_b(n)

Tests:
  T1 transverse plane wave (A_z(x)=cos kx)  -> propagates, omega vs c
  T2 second transverse pol (A_y(x)=cos kx)  -> degenerate with T1
  T3 longitudinal/pure-gauge (A_x(x)=cos kx) -> frozen (Gauss)
Pass => the real v12 edge structure carries the photon (2 transverse + frozen
longitudinal), confirming demo-E7 in the original theory's actual formulation.

ASCII output, CPU/numpy.
"""

import json
import os
import numpy as np

MU_A = 1.0
C2 = 1.0          # lattice Maxwell has c=1 in these units (we measure it)
DT = 0.1

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..",
                       "07_validation", "audits", "demo-phase2-v12-photon-v1")


def F_plaquette(A, a, b):
    """F_ab(n) = A_a(n) + A_b(n+e_a) - A_a(n+e_b) - A_b(n)."""
    return (A[a] + np.roll(A[b], -1, axis=a)
            - np.roll(A[a], -1, axis=b) - A[b])


def ampere(A):
    """Edot_a(n) = - sum_{b!=a} [F_ab(n) - F_ab(n-e_b)]."""
    out = [np.zeros_like(A[0]) for _ in range(3)]
    for a in range(3):
        acc = np.zeros_like(A[0])
        for b in range(3):
            if b == a:
                continue
            Fab = F_plaquette(A, a, b)
            acc += Fab - np.roll(Fab, +1, axis=b)
        out[a] = -acc
    return out


def evolve(A, E, steps, probe_cell=(1, 1, 1), probe_dir=2, sample=4):
    series = []
    for t in range(steps):
        acc = ampere(A)
        for a in range(3):
            E[a] += DT * acc[a] / MU_A
        for a in range(3):
            A[a] += DT * E[a]
        if t % sample == 0:
            series.append(A[probe_dir][probe_cell])
    return series


def measure_omega(series, dt_s):
    v = np.array(series) - np.mean(series)
    if np.allclose(v, 0):
        return 0.0
    sp = np.abs(np.fft.rfft(v))
    fr = np.fft.rfftfreq(len(v), d=dt_s)
    return float(2 * np.pi * fr[np.argmax(sp[1:]) + 1])


def plane_wave_A(L, n_mode, pol_dir):
    x = np.arange(L)
    X, _, _ = np.meshgrid(x, x, x, indexing="ij")
    k = 2 * np.pi * n_mode / L
    A = [np.zeros((L, L, L)) for _ in range(3)]
    A[pol_dir] = np.cos(k * X)        # varies along x; polarization = pol_dir
    return A, k


def run_pol(L, n_mode, pol_dir, steps=800):
    A, k = plane_wave_A(L, n_mode, pol_dir)
    E = [np.zeros_like(A[0]) for _ in range(3)]
    probe_dir = pol_dir
    series = evolve(A, E, steps, probe_dir=probe_dir, sample=4)
    om = measure_omega(series, 4 * DT)
    return om, k


def main():
    print("=" * 70)
    print("PHASE 2 -- v12 lattice photon (DER-QNG-076 actual structure)")
    print("=" * 70)
    L, n = 24, 2

    om_z, k = run_pol(L, n, pol_dir=2)   # transverse (pol z, varies along x)
    om_y, _ = run_pol(L, n, pol_dir=1)   # transverse (pol y, varies along x)
    om_x, _ = run_pol(L, n, pol_dir=0)   # longitudinal (pol x, varies along x)

    k_eff = np.sqrt(2 * (1 - np.cos(k)))
    c_meas = om_z / k_eff if k_eff else float("nan")

    print("\n  k = %.4f   k_eff(lattice) = %.4f" % (k, k_eff))
    print("  transverse pol z : omega = %.5f   c_meas = %.4f" % (om_z, c_meas))
    print("  transverse pol y : omega = %.5f" % om_y)
    print("  longitudinal x   : omega = %.5f   frozen=%s" % (om_x, om_x < 1e-3))

    two_transverse = abs(om_z - om_y) < 1e-3 and om_z > 1e-3
    long_frozen = om_x < 1e-3
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    print("  2 transverse polarizations degenerate : %s" % two_transverse)
    print("  longitudinal frozen (Gauss)           : %s" % long_frozen)

    if two_transverse and long_frozen:
        verdict = ("V12_PHOTON_CONFIRMED: the actual v12 lattice gauge structure "
                   "(A_ij on edges, F_p on plaquettes, DER-QNG-076) carries 2 "
                   "degenerate transverse polarizations and freezes the "
                   "longitudinal mode (Gauss constraint) -- the photon. This "
                   "validates demo-E7 in the original theory's real formulation, "
                   "not just the idealized spectral curl-curl. Edge gauge field "
                   "= light, confirmed dynamically on the lattice.")
    else:
        verdict = "INCONCLUSIVE -- see modes above."
    print("\n  => " + verdict)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "report.json"), "w") as f:
        json.dump({"k": float(k), "k_eff": float(k_eff),
                   "omega_trans_z": om_z, "omega_trans_y": om_y,
                   "omega_long_x": om_x, "c_meas": float(c_meas),
                   "two_transverse": bool(two_transverse),
                   "longitudinal_frozen": bool(long_frozen),
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT_DIR, "report.json"))


if __name__ == "__main__":
    main()
