"""
PHASE 4a -- Custodial symmetry audit (closes the tesla-mind (sigma_g, sigma_m)
isospin-doublet conjecture definitively).

The professor's group-theory verdict says two REAL scalars cannot form an SU(2)
doublet. But a weaker question remains: does the FREE (k_gm=0) dynamics at least
have an SO(2) rotation symmetry mixing sigma_g and sigma_m? If yes, there is a
hidden internal symmetry worth building on; if no, the doublet idea is dead at
every level.

Operational symmetry test: evolve a small-fluctuation state two ways --
(A) rotate (sigma_g,sigma_m) by angle theta, THEN evolve;
(B) evolve, THEN rotate.
If A == B for all theta, the rotation commutes with the dynamics (symmetry).
We use the actual v7/v8 channel structure: sigma_g carries Channel-G/KG dynamics
(inertia ~ 1/k_back), sigma_m carries Channel-F gradient flow (inertia mu_m).

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase4a-custodial-v1")

# v8 parameters. The c_g=c_m matching (DER-QNG-042) makes the FREE wave operators
# equal, so a naive free test would show a spurious symmetry. The PHYSICAL
# asymmetry is the CHANNEL structure: sigma_m carries Channel F (a depletion/mass
# term), sigma_g does not. That is what we test.
COEF = 0.006      # matched free wave coefficient (c_g^2 = c_m^2)
GAMMA_F = 0.02    # Channel-F-like term, sigma_m ONLY (the physical asymmetry)
DT = 0.1


def lap(f):
    out = -6.0 * f
    for ax in range(3):
        out += np.roll(f, 1, axis=ax) + np.roll(f, -1, axis=ax)
    return out


def evolve(sg, sm, vg, vm, steps, gamma_f=GAMMA_F):
    """Matched free wave operators (c_g=c_m) PLUS the physical channel asymmetry:
    sigma_m has a Channel-F-like term (-gamma_f*sm), sigma_g does not."""
    for _ in range(steps):
        ag = COEF * lap(sg)                       # sigma_g: wave only
        am = COEF * lap(sm) - gamma_f * sm        # sigma_m: wave + Channel-F term
        vg += DT * ag; vm += DT * am
        sg += DT * vg; sm += DT * vm
    return sg, sm, vg, vm


def rotate(sg, sm, theta):
    c, s = np.cos(theta), np.sin(theta)
    return c*sg + s*sm, -s*sg + c*sm


def main():
    print("="*70)
    print("PHASE 4a -- custodial (sigma_g, sigma_m) rotation symmetry audit")
    print("="*70)
    L = 16
    rng = np.random.default_rng(7)
    sg0 = 0.01*rng.standard_normal((L, L, L))
    sm0 = 0.01*rng.standard_normal((L, L, L))

    def commutator(theta, gamma_f):
        a_sg, a_sm = rotate(sg0.copy(), sm0.copy(), theta)
        a_sg, a_sm, _, _ = evolve(a_sg, a_sm, np.zeros_like(a_sg),
                                  np.zeros_like(a_sg), 100, gamma_f)
        b_sg, b_sm, _, _ = evolve(sg0.copy(), sm0.copy(), np.zeros_like(sg0),
                                  np.zeros_like(sg0), 100, gamma_f)
        b_sg, b_sm = rotate(b_sg, b_sm, theta)
        d = float(np.max(np.abs(a_sg-b_sg)) + np.max(np.abs(a_sm-b_sm)))
        sc = float(np.max(np.abs(b_sg)) + np.max(np.abs(b_sm)))
        return d/sc if sc else d

    print("  REAL dynamics (Channel-F term on sigma_m only, gamma_f=%.3f):" % GAMMA_F)
    diffs = []
    for theta in (0.3, 0.7, 1.5):
        rel = commutator(theta, GAMMA_F)
        diffs.append(rel)
        print("    theta=%.2f : |rotate-evolve commutator| (relative) = %.4e"
              % (theta, rel))

    ctrl_rel = commutator(0.7, 0.0)   # control: remove the Channel-F asymmetry
    print("\n  CONTROL (gamma_f=0, perfectly matched fields): commutator = %.4e"
          % ctrl_rel)

    breaks = max(diffs) > 1e-6
    control_symmetric = ctrl_rel < 1e-6
    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  Channel-F asymmetry BREAKS the (sigma_g,sigma_m) rotation : %s" % breaks)
    print("  control (gamma_f=0) is symmetric (only SO(2)=U(1), real)  : %s" % control_symmetric)

    if breaks and control_symmetric:
        verdict = ("NO_CUSTODIAL_SU2: the physical channel asymmetry (Channel F "
                   "acts on sigma_m but not sigma_g) BREAKS the (sigma_g, sigma_m) "
                   "rotation -- it does not commute with the real dynamics. The "
                   "control (gamma_f=0, perfectly matched) recovers the symmetry, "
                   "proving the breaking is physical, not numerical. CRUCIALLY: "
                   "even in the symmetric limit the symmetry is only SO(2)=U(1) (a "
                   "rotation of two REAL fields), NEVER SU(2) (which acts on C^2). "
                   "So tesla-mind's (sigma_g,sigma_m)=isospin-doublet conjecture "
                   "fails at BOTH levels: (i) the channel structure breaks even the "
                   "U(1), and (ii) real fields cannot carry SU(2) regardless. "
                   "Confirms the professor. Non-abelian matter = new ontology v13.")
    else:
        verdict = "UNEXPECTED -- see numbers above."
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"commutators_real": diffs, "control_gamma0": ctrl_rel,
                   "breaks": breaks, "control_symmetric": control_symmetric,
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
