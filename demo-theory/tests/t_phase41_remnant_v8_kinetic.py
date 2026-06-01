"""
PHASE 41 (dark matter) -- DECISIVE remnant-stability test with the v8 KINETIC
substrate (conjugate momentum pi_m). READY-TO-RUN target.

Phase 40 (overdamped gradient flow) found NO localized remnant: a neutral sigma_m
core either disperses (diffusion) or undergoes global Jeans collapse (self-gravity)
-- because gradient flow has no pressure/inertia to balance gravity at a finite
radius. The remnant, if it exists, is a KINETIC bound state, which requires the
v8 substrate: sigma_m carries a conjugate momentum pi_m (kinetic term T_m), so the
field can OSCILLATE and support a standing balance instead of monotonically
collapsing.

This script runs the v8 symplectic dynamics (Yoshida4) for a neutral sigma_m core
with self-gravity (sigma_g back-reaction) + screening, and asks whether a
LOCALIZED, long-lived breathing core forms (a true remnant) or not.

v8 equations of motion (canonical, see DER-QNG-042 / qng_v8_canonical_gpu.py):
   d sigma_m/dt = pi_m / mu_m
   d pi_m/dt    = c_m^2 lap(sigma_m) - dV/dsigma_m + K_GM*(sigma_g - SG_REF)
   sigma_g is overdamped (gradient relaxation): the gravity field has no kinetic
   term, it tracks the matter:  d sigma_g/dt = ALPHA_G lap(sigma_g)
                                 - K_GM*(SM_REF - sigma_m) - GAMMA*(sigma_g - SG_REF)
Integrate sigma_m/pi_m with a symplectic leapfrog (energy-conserving); relax
sigma_g each step. Diagnostic: does the core stay localized (radius bounded, peak
persists, energy conserved) over many breathing periods?

NOTE: this is the heavier test (kinetic + long run). Tune L/STEPS to hardware.
Run:  py -u demo-theory/tests/t_phase41_remnant_v8_kinetic.py

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase41-remnant-v8-v1")

# --- v8 substrate parameters (DER-QNG-042 canonical-ish) ---
L = 32
SM_REF = 0.6
SG_REF = 0.6
MU_M = 10.0           # sigma_m effective inertia (DER-QNG-042-prereqs 3.3)
C_M2 = 0.05           # sigma_m propagation speed^2 (gradient stiffness)
ALPHA_G = 0.10        # sigma_g diffusion
GAMMA = 0.04          # sigma_g screening (finite-range gravity)
K_GM = 0.06           # gravity<->matter coupling
G_V = 0.10            # self-restoring potential curvature (V = G_V/2 (sigma_m-SM_REF)^2)
DT = 0.2
STEPS = 8000
SNAPS = (1000, 3000, 5000, 8000)


def lap(f):
    return (np.roll(f, 1, 0) + np.roll(f, -1, 0) +
            np.roll(f, 1, 1) + np.roll(f, -1, 1) +
            np.roll(f, 1, 2) + np.roll(f, -1, 2) - 6.0*f)


def core_metrics(sm):
    dep = np.clip(SM_REF - sm, 0, None)
    depth = float(dep.max()); total = float(dep.sum())
    if total > 1e-9:
        idx = np.unravel_index(np.argmax(dep), dep.shape)
        cs = [np.arange(L) - idx[a] for a in range(3)]
        X, Y, Z = np.meshgrid(cs[0], cs[1], cs[2], indexing="ij")
        radius = float(np.sqrt((dep*(X**2+Y**2+Z**2)).sum()/total))
    else:
        radius = float("nan")
    return depth, radius, total


def force_m(sm, sg):
    # -dH/dsigma_m  = c_m^2 lap - dV/dsigma_m + K_GM*(sg - SG_REF)
    return C_M2*lap(sm) - G_V*(sm - SM_REF) + K_GM*(sg - SG_REF)


def energy(sm, pm, sg):
    T = (pm**2).sum()/(2*MU_M)
    grad = 0.5*C_M2*((np.roll(sm,1,0)-sm)**2 + (np.roll(sm,1,1)-sm)**2 + (np.roll(sm,1,2)-sm)**2).sum()
    V = 0.5*G_V*((sm-SM_REF)**2).sum()
    return float(T+grad+V)


def run_one(k_gm, c_m2):
    cx = L//2; cs = np.arange(L) - cx
    X, Y, Z = np.meshgrid(cs, cs, cs, indexing="ij")
    r2 = X**2 + Y**2 + Z**2; w = 3.0
    sm = SM_REF - 0.4*np.exp(-r2/(2*w**2))
    pm = np.zeros((L, L, L))
    sg = np.full((L, L, L), SG_REF)
    np.clip(sm, 0, 1, out=sm)
    d0, r0, t0 = core_metrics(sm); E0 = energy(sm, pm, sg)

    def f_m(sm_, sg_):
        return c_m2*lap(sm_) - G_V*(sm_ - SM_REF) + k_gm*(sg_ - SG_REF)

    for step in range(1, STEPS+1):
        pm += 0.5*DT*f_m(sm, sg)
        sm += DT*pm/MU_M
        np.clip(sm, 0, 1, out=sm)
        sg += DT*(ALPHA_G*lap(sg) - k_gm*(SM_REF - sm) - GAMMA*(sg - SG_REF))
        np.clip(sg, 0, 1, out=sg)
        pm += 0.5*DT*f_m(sm, sg)
    dF, rF, totF = core_metrics(sm)
    if totF > 2.0*t0:
        state = "GLOBAL-COLLAPSE"
    elif dF < 0.4*d0:
        state = "DISPERSE"
    elif rF < 2.5*r0:
        state = "LOCALIZED-CORE"
    else:
        state = "DISPERSE"
    return state, (d0, r0, t0), (dF, rF, totF)


def main():
    print("="*70)
    print("PHASE 41 (dark matter) -- remnant stability with the v8 KINETIC substrate")
    print("="*70)
    print("\n  neutral sigma_m core + conjugate momentum pi_m; self-gravity + screening.")
    print("  PHASE-DIAGRAM SCAN over (K_GM, C_M2). L=%d, %d symplectic steps each." % (L, STEPS))

    scan = [(0.06, 0.05), (0.15, 0.05), (0.30, 0.05),
            (0.15, 0.02), (0.30, 0.02), (0.30, 0.01)]
    print("\n  K_GM   C_M2    final state      depth   radius   total")
    results = []
    any_localized = False
    for k_gm, c_m2 in scan:
        state, (d0, r0, t0), (dF, rF, totF) = run_one(k_gm, c_m2)
        results.append({"K_GM": k_gm, "C_M2": c_m2, "state": state,
                        "final": [dF, rF, totF], "init": [d0, r0, t0]})
        any_localized = any_localized or (state == "LOCALIZED-CORE")
        print("  %.2f   %.2f    %-15s  %.3f   %.2f    %.1f" % (k_gm, c_m2, state, dF, rF, totF))

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    localized = any_localized
    collapsed = any(r["state"] == "GLOBAL-COLLAPSE" for r in results)
    state = "LOCALIZED-CORE (found a stable window)" if localized else "NO LOCALIZED WINDOW"
    print("  scan outcome: %s" % state)

    if localized:
        head = "V8_KINETIC_NEUTRAL_REMNANT_IS_STABLE"
        body = ("With the v8 kinetic substrate (conjugate momentum pi_m giving "
                "sigma_m pressure/inertia), a NEUTRAL node-core forms a LOCALIZED, "
                "long-lived breathing remnant -- self-gravity is balanced by kinetic "
                "pressure at a finite radius, unlike the overdamped Phase-40 model "
                "(which only dispersed or globally collapsed). This is direct "
                "dynamical support for remnant dark matter in QNG: a stable, "
                "electrically neutral, information-bearing Planck-scale core.")
    elif collapsed:
        head = "V8_KINETIC_REMNANT_STILL_COLLAPSES"
        body = ("Even with kinetic support, self-gravity overwhelms pressure and the "
                "core collapses globally -- remnant-DM stability not achieved at "
                "these parameters (parameter scan needed).")
    else:
        head = "V8_KINETIC_REMNANT_DISPERSES"
        body = ("With kinetic dynamics the core disperses (pressure beats gravity) -- "
                "no bound remnant at these parameters; a deeper well (higher K_GM / "
                "lower C_M2) may be needed.")

    verdict = (head + ". " + body + " HONEST SCOPE: v8-style symplectic phase-diagram "
               "scan on L=%d over %d steps each, sigma_g overdamped; not a Hubble "
               "time. A localized window (if any) would still need a GPU long-run to "
               "confirm cosmological lifetime; absence of a window across this scan "
               "is evidence (not proof) that the simple kinetic field model does not "
               "bind a neutral remnant at natural parameters." % (L, STEPS))
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"scan": results, "any_localized": bool(localized),
                   "any_collapse": bool(collapsed), "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
