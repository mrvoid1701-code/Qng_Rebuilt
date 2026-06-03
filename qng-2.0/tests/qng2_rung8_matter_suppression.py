"""
QNG 2.0 / RUNG 8 (open frontier, point 1) -- does MATTER suppress non-manifold-like causets?
The conjecture: in Z = Sum_C int Dpsi e^{iS_field}, the field action S_field = psi*(B+m^2)psi
is 'wild' (large operator norm, broad spectrum -> rapid phase oscillation -> destructive
interference) on non-manifold-like causets, suppressing them. Test the MECHANISM directly:
compute the spectrum of the BD kinetic operator B on manifold-like sprinklings vs random
posets and compare the spectral spread / operator norm (the proxy for how wildly S_field
oscillates). Larger on random => matter suppresses non-manifold-like. Honest either way.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "qng2-rung8-matter-suppression-v1")
SEED = 17


def smeared_kernel_2d(n, eps):
    om = 1.0-eps; n = n.astype(float)
    return (om**n)*(1.0 - 2*eps*n/om + (eps**2)*n*(n-1)/(2*om*om))


def bd_matrix(P, eps):
    # SYMMETRIC d'Alembertian-like operator for the field ACTION: each event couples to
    # BOTH past and future small-interval neighbors (the retarded-only B is triangular =>
    # nilpotent => trivial spectrum; the action's quadratic form needs the symmetric op).
    Cint = (P.astype(np.int32) @ P.astype(np.int32))
    W = smeared_kernel_2d(Cint, eps)*P       # W[y,x]: x couples to past y
    M = -2.0*np.eye(P.shape[0]) + eps*(W + W.T)   # past (W^T acting) + future (W) -> symmetric
    return 0.5*(M + M.T)                      # enforce exact symmetry


def sprinkle_diamond(N, rng):
    pts = []
    while len(pts) < N:
        m = (N-len(pts))*3+30
        t = rng.uniform(0, 1, m); x = rng.uniform(-0.5, 0.5, m)
        ok = (t > np.abs(x)) & ((1-t) > np.abs(x))
        for i in np.where(ok)[0]:
            pts.append((t[i], x[i]))
            if len(pts) >= N: break
    a = np.array(pts); a = a[np.argsort(a[:, 0])]
    t, x = a[:, 0], a[:, 1]
    dt = t[None, :]-t[:, None]; dx = np.abs(x[None, :]-x[:, None])
    return (dt > dx) & (dt > 0)


def random_poset(N, rng, p=0.06):
    lbl = np.argsort(rng.rand(N)); A = np.zeros((N, N), bool)
    for i in range(N):
        for j in range(N):
            if lbl[i] < lbl[j] and rng.rand() < p:
                A[i, j] = True
    R = A.copy()
    for _ in range(int(np.ceil(np.log2(N)))+1):
        R2 = R | ((R.astype(np.int32) @ R.astype(np.int32)) > 0)
        if np.array_equal(R2, R): break
        R = R2
    return R


def spectral_spread(P, eps=0.2):
    B = bd_matrix(P, eps)
    ev = np.linalg.eigvalsh(B)               # symmetric -> real eigenvalues
    return float(np.max(np.abs(ev))), float(np.std(ev))   # spectral radius, spread


def main():
    print("="*70)
    print("QNG 2.0 / RUNG 8 -- does the matter action suppress non-manifold-like causets?")
    print("="*70)
    rng = np.random.RandomState(SEED)
    N, n_samp = 120, 8

    print("\n[setup] compute BD kinetic-operator spectrum on N=%d causets, %d samples each." % (N, n_samp))
    print("        larger spectral radius / spread => S_field oscillates more wildly =>")
    print("        stronger destructive-interference suppression in Z = Sum_C int Dpsi e^{iS}.")

    radii_m, spread_m, radii_r, spread_r = [], [], [], []
    for s in range(n_samp):
        Pm = sprinkle_diamond(N, rng); r, sp = spectral_spread(Pm)
        radii_m.append(r); spread_m.append(sp)
        Pr = random_poset(N, rng); r2, sp2 = spectral_spread(Pr)
        radii_r.append(r2); spread_r.append(sp2)

    rm, rr = np.mean(radii_m), np.mean(radii_r)
    sm, sr = np.mean(spread_m), np.mean(spread_r)
    print("\n  metric                   manifold-like      random poset      ratio (rand/man)")
    print("  spectral radius |B|max   %.3f              %.3f             %.2fx" % (rm, rr, rr/rm))
    print("  eigenvalue spread        %.3f              %.3f             %.2fx" % (sm, sr, sr/sm))

    suppresses = (rr/rm > 1.3) or (sr/sm > 1.3)
    direction = "SUPPRESSES non-manifold-like" if suppresses else "does NOT clearly suppress"
    print("\n  => matter action %s (random-poset operator is %.1fx %s)."
          % (direction, max(rr/rm, sr/sm), "wilder" if suppresses else "comparable"))

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  spectral radius ratio %.2fx, spread ratio %.2fx (random/manifold)" % (rr/rm, sr/sm))
    print("  conjecture 'matter suppresses non-manifold-like causets': %s"
          % ("SUPPORTED (mechanism active)" if suppresses else "NOT supported by this proxy"))

    verdict = (
        ("MATTER_PLAUSIBLY_SUPPRESSES_NON-MANIFOLD-LIKE_CAUSETS: THE_FIELD_OPERATOR_IS_"
         "SPECTRALLY_WILDER_THERE (mechanism active, beyond the rung-5/6 premise). " if suppresses else
         "RUNG8_NULL: THE_SPECTRAL_PROXY_DOES_NOT_SHOW_MATTER_SUPPRESSION (honest null). ") +
        "Point 1 (the open frontier) attacked directly: does including the matter field in "
        "the sum-over-causets reweight it toward manifold-like geometries? The mechanism "
        "tested is that S_field = psi*(B+m^2)psi oscillates more wildly on non-manifold-"
        "like causets (a broader/larger spectrum of the BD kinetic operator B means more "
        "rapid phase variation across field configurations, hence stronger destructive "
        "interference and suppression in Z = Sum_C int Dpsi e^{iS}). Comparing the BD "
        "operator's spectrum on manifold-like sprinklings vs generic random posets "
        "(N=%d, %d samples each): the random-poset operator has spectral radius %.2fx and "
        "eigenvalue spread %.2fx that of the manifold-like one. " +
        ("Since the operator is markedly WILDER on non-manifold-like causets, the field "
         "action oscillates faster there, so matter does provide a suppression channel -- "
         "the conjecture's MECHANISM is active, upgrading it from 'premise sound' (rung 5) "
         "and 'gravity-action-supported' (rung 6, Loomis-Carlip) to 'matter-mechanism "
         "demonstrated at the operator level'. " if suppresses else
         "The proxy does NOT show a clear difference, so this run gives no evidence that "
         "matter suppresses non-manifold-like causets -- reported as an honest null; the "
         "gravity-action suppression (Loomis-Carlip, rung 6) stands alone. ") +
        "HONEST AND CRUCIAL: this is a PROXY (the operator's spectral spread as a stand-in "
        "for how wildly S_field oscillates), on SMALL causets (N=%d), comparing two "
        "classes -- it is NOT a computation of the full matter-coupled partition function "
        "Z = Sum_C int Dpsi e^{iS} and its manifold-dominance, which remains the genuine "
        "open problem (a research-scale Monte-Carlo over the sum-over-causets). So 'matter "
        "suppresses' here means 'the field operator is spectrally wilder on non-manifold-"
        "like causets, providing a plausible suppression channel', not 'we proved manifold "
        "dominance'. Combined with the gravity-action result (Loomis-Carlip), the "
        "manifold-selection debt is being paid down from two sides; the full interacting "
        "proof is the standing frontier. No numbers forced.") % (
            N, n_samp, rr/rm, sr/sm, N)
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"N": N, "n_samples": n_samp,
                   "spectral_radius_manifold": rm, "spectral_radius_random": rr,
                   "radius_ratio": rr/rm, "spread_manifold": sm, "spread_random": sr,
                   "spread_ratio": sr/sm, "suppresses": bool(suppresses),
                   "note": "operator-spectrum proxy, small N; not the full partition function",
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
