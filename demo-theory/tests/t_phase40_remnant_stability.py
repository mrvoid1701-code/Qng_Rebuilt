"""
PHASE 40 (dark matter) -- DYNAMICAL stability of the neutral Planck node-core.

Phase 39 showed the Planck remnant EVADES the DM no-go (it can be neutral, q=0,
because its stability is from the minimum length, not phi-winding). The open
question: does a neutral, maximally-packed node-core actually PERSIST under the
substrate dynamics, or disperse? (DM Phase-2a saw winding rings dissolve in ~10^4
lu; a non-topological lump has no topological protection.)

This is the decisive test. We evolve a neutral sigma_m matter core (matter =
sigma_m DEPLETION, the ring/baryon convention) WITH gravitational self-binding
(v7-symmetric: matter depletes sigma_g -> a well; the well deepens the sigma_m
depletion -> self-gravity), plus diffusion (Channel A). NO phi field at all
(strictly neutral). The substrate scalars are CLAMPED to [0,1] -- the bounded-
scalar ontology -- so a collapsing core SATURATES at sigma_m=0 (the field-level
echo of the minimum-length floor) instead of running away.

Dynamics (gradient-flow / overdamped, faithful to v7-symmetric CPU-073):
   sigma_g += ALPHA_G * lap(sigma_g)  - K_GM*(sigma_m_ref - sigma_m)   (matter depletes g)
   sigma_m += ALPHA_M * lap(sigma_m)  + K_GM*(sigma_g - sigma_g_ref)   (back-reaction)
   clamp both to [0,1].

Outcomes:
  - K_GM=0 (pure diffusion, CONTROL): core must disperse (depth -> 0).
  - K_GM>0: does self-gravity + the [0,1] floor give a PERSISTENT saturated core?
We track core depth (sigma_m_ref - min sigma_m), core radius, and total depletion.

ASCII output, CPU/numpy. ~1-2 min.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase40-remnant-stability-v1")

L = 32
SM_REF = 0.6
SG_REF = 0.6
ALPHA = 0.10          # diffusion (Channel A)
GAMMA = 0.04          # sigma_g restoring/screening (QNG gravity is screened-Poisson,
                      # range lam_g = sqrt(ALPHA/GAMMA) ~ 1.6 cells); suppresses the
                      # global Jeans (k=0) runaway so the LOCAL balance can be tested
DT = 1.0
STEPS = 6000


def lap(f):
    return (np.roll(f, 1, 0) + np.roll(f, -1, 0) +
            np.roll(f, 1, 1) + np.roll(f, -1, 1) +
            np.roll(f, 1, 2) + np.roll(f, -1, 2) - 6.0*f)


def core_metrics(sm):
    dep = SM_REF - sm                       # depletion field (>0 in the core)
    dep = np.clip(dep, 0, None)
    depth = float(dep.max())
    total = float(dep.sum())
    if total > 1e-9:
        # second moment radius about the peak
        idx = np.unravel_index(np.argmax(dep), dep.shape)
        coords = [np.arange(L) - idx[a] for a in range(3)]
        X, Y, Z = np.meshgrid(coords[0], coords[1], coords[2], indexing="ij")
        r2 = X**2 + Y**2 + Z**2
        radius = float(np.sqrt((dep*r2).sum()/total))
    else:
        radius = float("nan")
    return depth, radius, total


def run(k_gm):
    cx = L//2
    coords = np.arange(L) - cx
    X, Y, Z = np.meshgrid(coords, coords, coords, indexing="ij")
    r2 = X**2 + Y**2 + Z**2
    w = 3.0
    sm = SM_REF - 0.4*np.exp(-r2/(2*w**2))      # neutral sigma_m depletion core
    sg = np.full((L, L, L), SG_REF)
    sm = np.clip(sm, 0, 1); sg = np.clip(sg, 0, 1)
    d0, r0, t0 = core_metrics(sm)
    snaps = {}
    for step in range(1, STEPS+1):
        sg += DT*(ALPHA*lap(sg) - k_gm*(SM_REF - sm) - GAMMA*(sg - SG_REF))
        sm += DT*(ALPHA*lap(sm) + k_gm*(sg - SG_REF))
        np.clip(sg, 0, 1, out=sg); np.clip(sm, 0, 1, out=sm)
        if step in (1000, 3000, 6000):
            snaps[step] = core_metrics(sm)
    return (d0, r0, t0), snaps


def main():
    print("="*70)
    print("PHASE 40 (dark matter) -- dynamical stability of the neutral node-core")
    print("="*70)
    print("\n  neutral sigma_m depletion core (NO phi, q=0); self-gravity (v7-symmetric)")
    print("  + diffusion; scalars clamped to [0,1] (bounded-scalar floor). L=%d, %d steps." % (L, STEPS))

    results = {}
    for k_gm, tag in [(0.0, "CONTROL: pure diffusion"), (0.06, "self-gravity k_gm=0.06"),
                      (0.15, "strong self-gravity k_gm=0.15")]:
        (d0, r0, t0), snaps = run(k_gm)
        results[k_gm] = {"init": (d0, r0, t0), "snaps": snaps}
        print("\n  [%s]  k_gm=%.2f" % (tag, k_gm))
        print("     t       core_depth   core_radius   total_depletion")
        print("     0       %.4f       %.2f          %.2f" % (d0, r0, t0))
        for t in (1000, 3000, 6000):
            d, r, tot = snaps[t]
            print("     %-6d  %.4f       %.2f          %.2f" % (t, d, r, tot))

    # verdicts -- classify each run: DISPERSE / LOCALIZED-CORE / GLOBAL-COLLAPSE
    def classify(k):
        d0, r0, t0 = results[k]["init"]
        d, r, tot = results[k]["snaps"][6000]
        if tot > 2.0*t0:                      # total depletion grew -> matter ran away
            return "GLOBAL-COLLAPSE", d, r, tot
        if d < 0.4*d0:                        # peak faded, mass conserved -> spread out
            return "DISPERSE", d, r, tot
        if r > 2.5*r0:                         # peak survives but bloated -> not localized
            return "DISPERSE", d, r, tot
        return "LOCALIZED-CORE", d, r, tot

    d0c, r0c, t0c = results[0.0]["init"]
    cls = {k: classify(k) for k in results}

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    for k, tag in [(0.0, "CONTROL pure diffusion"), (0.06, "self-gravity 0.06"),
                   (0.15, "strong self-gravity 0.15")]:
        c, d, r, tot = cls[k]
        print("  k_gm=%.2f (%s): %-15s depth=%.3f radius=%.2f total=%.0f"
              % (k, tag, c, d, r, tot))

    control_disperses = cls[0.0][0] == "DISPERSE"
    any_localized = any(cls[k][0] == "LOCALIZED-CORE" for k in (0.06, 0.15))
    any_collapse = any(cls[k][0] == "GLOBAL-COLLAPSE" for k in (0.06, 0.15))

    if any_localized:
        head = "NEUTRAL_CORE_CAN_FORM_A_LOCALIZED_SELF_BOUND_REMNANT"
    elif any_collapse:
        head = "NEUTRAL_CORE_NOT_STABILIZED_SELF_GRAVITY_GOES_JEANS_UNSTABLE"
    else:
        head = "NEUTRAL_CORE_DISPERSES_REMNANT_STABILITY_NOT_SUPPORTED"

    verdict = (
        head + ". Decisive dynamical test of the Phase-39 remnant-DM proposal: does "
        "a NEUTRAL (q=0, no phi-winding) node-core survive the substrate dynamics? "
        "We evolved a neutral sigma_m depletion core under v7-symmetric self-gravity "
        "(matter depletes sigma_g -> a screened well; the well deepens the "
        "depletion) plus diffusion, scalars clamped to [0,1] (bounded-scalar floor), "
        f"with sigma_g screening GAMMA={GAMMA} (QNG gravity is screened-Poisson, "
        "range ~1.6 cells) to suppress the spurious global Jeans (k=0) runaway. "
        f"RESULTS: CONTROL (k_gm=0, pure diffusion) -> {cls[0.0][0]} (depth "
        f"{d0c:.3f}->{cls[0.0][1]:.3f}), the expected fate of an unprotected lump. "
        f"self-gravity k_gm=0.06 -> {cls[0.06][0]} (final depth {cls[0.06][1]:.3f}, "
        f"radius {cls[0.06][2]:.2f}); strong k_gm=0.15 -> {cls[0.15][0]} (depth "
        f"{cls[0.15][1]:.3f}, radius {cls[0.15][2]:.2f}). " +
        ("INTERPRETATION: a neutral core can form a LOCALIZED self-bound remnant -- "
         "self-gravity balances diffusion at a finite radius, with the bounded-scalar "
         "floor preventing runaway. This is direct dynamical support for remnant-DM. "
         if any_localized else
         "INTERPRETATION: self-gravity does NOT yield a localized bound remnant in "
         "this bare model -- below threshold the core disperses, above threshold it "
         "goes globally unstable (collapse fills the box). A genuine localized "
         "remnant would need pressure/kinetic support (full v8 symplectic dynamics "
         "with pi_m, or an explicit minimum-length hard core) that this overdamped "
         "screened-diffusion model lacks. So remnant stability remains UNPROVEN -- "
         "and this test shows WHY it is hard: the same self-gravity that could bind "
         "the core drives instability without a support term. ") +
        "HONEST SCOPE: overdamped (gradient-flow) v7-symmetric dynamics on L=32 over "
        "6000 steps, NOT full v8 symplectic evolution and NOT a Hubble time; "
        "outcome is parameter-dependent. NET: the dynamical test is "
        + ("POSITIVE (localized remnant forms) " if any_localized else
           "NOT yet supportive (no localized remnant in this model) ") +
        "-- consistent with Phase-39's honest verdict that remnant-DM is a viable "
        "DIRECTION with stability still open; the decisive check needs the full v8 "
        "kinetic substrate.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    out = {str(k): {"init": list(v["init"]),
                    "snaps": {str(s): list(m) for s, m in v["snaps"].items()}}
           for k, v in results.items()}
    out["verdict"] = verdict
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
