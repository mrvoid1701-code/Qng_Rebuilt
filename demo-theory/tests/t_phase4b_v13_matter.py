"""
PHASE 4b -- v13 matter doublet: build the door the Hodge no-go + Phase-3 pointed
to. The edges host SU(2) (confirmed, Phase 3); the missing piece is a MATTER
multiplet at the nodes for the gauge field to act on.

Construct a complex 2-component node field psi(n) in C^2 (the minimal SU(2)
fundamental = isospin doublet), coupled to the SU(2) edge links U_ij via the
gauge-COVARIANT hopping:
    S_matter = sum_{n,d} | psi(n) - U_d(n) psi(n+e_d) |^2   +  m^2 sum_n |psi(n)|^2

Tests:
  G1 GAUGE INVARIANCE: under psi(n)->g(n)psi(n), U_d(n)->g(n)U_d(n)g(n+e_d)^dag,
     the action is invariant to machine precision (it is a genuine gauged
     matter theory).
  G2 PHYSICS -- W rotates isospin: a nonzero SU(2) gauge background transports a
     pure "up" doublet (1,0) into a mixture of up/down -> the gauge boson
     converts isospin components (the n<->p / weak-current content).

This DEMONSTRATES v13 is a consistent construction. It does NOT claim the
doublet has a natural source in existing QNG fields (Phase-3 verdict: it does
not -- this is honest new ontology). ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase4b-v13-matter-v1")
rng = np.random.default_rng(2026)


def su2_from_quat(q):
    """q shape (...,4) unit quaternion -> SU(2) matrix shape (...,2,2) complex."""
    a0, a1, a2, a3 = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    U = np.empty(q.shape[:-1] + (2, 2), dtype=complex)
    U[..., 0, 0] = a0 + 1j*a3
    U[..., 0, 1] = a2 + 1j*a1
    U[..., 1, 0] = -a2 + 1j*a1
    U[..., 1, 1] = a0 - 1j*a3
    return U


def rand_su2_field(shape, eps=1.0):
    v = rng.normal(size=shape + (3,)) * eps
    a0 = rng.normal(size=shape) * eps
    q = np.concatenate([a0[..., None], v], axis=-1)
    q /= np.linalg.norm(q, axis=-1, keepdims=True)
    return su2_from_quat(q)


def matvec(U, psi):
    """U (...,2,2) acting on psi (...,2)."""
    return np.einsum("...ij,...j->...i", U, psi)


def dagger(U):
    return np.conj(np.swapaxes(U, -1, -2))


def action(psi, Ulinks, m2=0.1):
    """S = sum_{n,d} |psi(n) - U_d(n) psi(n+e_d)|^2 + m2 sum |psi|^2."""
    S = 0.0
    for d in range(3):
        psi_shift = np.roll(psi, -1, axis=d)          # psi(n+e_d)
        cov = psi - matvec(Ulinks[d], psi_shift)      # covariant difference
        S += np.sum(np.abs(cov)**2)
    S += m2 * np.sum(np.abs(psi)**2)
    return float(S)


def gauge_transform(psi, Ulinks, g):
    """psi(n)->g(n)psi(n); U_d(n)->g(n)U_d(n)g(n+e_d)^dag."""
    psi2 = matvec(g, psi)
    U2 = []
    for d in range(3):
        g_shift = np.roll(g, -1, axis=d)
        U2.append(np.einsum("...ij,...jk,...kl->...il", g, Ulinks[d], dagger(g_shift)))
    return psi2, U2


def main():
    print("="*70)
    print("PHASE 4b -- v13 matter doublet + SU(2) edge gauge")
    print("="*70)
    L = 8
    psi = (rng.normal(size=(L, L, L, 2)) + 1j*rng.normal(size=(L, L, L, 2)))
    Ulinks = [rand_su2_field((L, L, L)) for _ in range(3)]

    # ---- G1 gauge invariance ----
    S0 = action(psi, Ulinks)
    g = rand_su2_field((L, L, L), eps=1.0)
    psi_g, U_g = gauge_transform(psi, Ulinks, g)
    S1 = action(psi_g, U_g)
    dS = abs(S1 - S0)
    print("\n[G1] gauge invariance of covariant matter action")
    print("    S(before)=%.6f  S(after local SU(2))=%.6f  |dS|=%.3e"
          % (S0, S1, dS))
    g1 = dS < 1e-8 * abs(S0)

    # ---- G2 W rotates isospin ----
    # uniform SU(2) link along x representing a W background: a rotation by angle
    # phi about the 1-axis (sigma_x). Transport a pure 'up' doublet across N steps.
    phi = np.pi / 6
    Wx = su2_from_quat(np.array([np.cos(phi/2), np.sin(phi/2), 0.0, 0.0]))
    up = np.array([1.0 + 0j, 0.0 + 0j])
    state = up.copy()
    pops_up, pops_dn = [], []
    for step in range(13):
        pops_up.append(float(np.abs(state[0])**2))
        pops_dn.append(float(np.abs(state[1])**2))
        state = Wx @ state                   # parallel-transport one edge
    print("\n[G2] W-background transports a pure 'up' doublet (isospin rotation)")
    print("    step  0: |up|^2=%.3f  |down|^2=%.3f" % (pops_up[0], pops_dn[0]))
    print("    step  6: |up|^2=%.3f  |down|^2=%.3f" % (pops_up[6], pops_dn[6]))
    print("    step 12: |up|^2=%.3f  |down|^2=%.3f" % (pops_up[12], pops_dn[12]))
    isospin_mixes = max(pops_dn) > 0.5    # 'up' converted substantially to 'down'

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  G1 gauged matter action invariant under local SU(2) : %s" % g1)
    print("  G2 W-background converts up<->down (weak current)    : %s" % isospin_mixes)

    if g1 and isospin_mixes:
        verdict = ("V13_MATTER_CONSISTENT: a complex node doublet psi in C^2 "
                   "coupled to the SU(2) edge links via the covariant hopping "
                   "|psi_i - U_ij psi_j|^2 is gauge-invariant to machine precision "
                   "(genuine gauged matter), and the SU(2) gauge background rotates "
                   "the isospin doublet (up<->down) -- exactly the weak-current "
                   "content (n<->p, the W boson converting isospin partners). The "
                   "door works: IF QNG adds a complex node doublet (v13), the full "
                   "non-abelian matter+gauge structure is consistent. HONEST SCOPE: "
                   "the doublet is genuinely NEW ontology -- it has no natural "
                   "source in the existing real scalars (sigma_g,sigma_m,chi,phi); "
                   "Phase-4a confirmed no custodial (sigma_g,sigma_m) symmetry. "
                   "And CHIRALITY (parity violation of the weak force) needs Dirac "
                   "fermions, not this scalar doublet -- the deeper v14 wall.")
    else:
        verdict = "INCONCLUSIVE -- see gates above."
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"G1_dS": dS, "S0": S0, "pops_up": pops_up, "pops_dn": pops_dn,
                   "gauge_invariant": g1, "isospin_mixes": isospin_mixes,
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
