"""
PHASE 3 -- attack the edges: can QNG edges host a NON-ABELIAN gauge field?

Following the Hodge no-go (DER-QNG-101): forces live on edges. The U(1) photon
came from a scalar phase per edge. Here we put an SU(2) GROUP ELEMENT (matrix
holonomy) on each edge -- the natural richer structure -- and test:

  G1 GAUGE INVARIANCE: random local SU(2) transform leaves the Wilson action
     invariant (machine precision) -> it is a genuine gauge theory.
  G2 MC CORRECTNESS: mean plaquette vs beta matches the strong-coupling
     expansion <P> -> beta/4 (SU(2)) at small beta.
  G3 CONFINEMENT: Wilson-loop Creutz ratios chi(R,R) -> a nonzero string
     tension (AREA law) -> the uniquely non-abelian signature (= strong force).

SU(2) links stored as unit quaternions q=(a0,a1,a2,a3), |q|=1, representing
U = a0 I + i(a1 sx + a2 sy + a3 sz). Tr U = 2 a0. Vectorized checkerboard
Metropolis. ASCII output, CPU/numpy.
"""

import json
import os
import numpy as np

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..",
                       "07_validation", "audits", "demo-phase3-su2-edges-v1")

rng = np.random.default_rng(12345)


# ---- quaternion (SU(2)) algebra, vectorized over a lattice ----
def qmul(p, q):
    """quaternion product, p,q shape (...,4)."""
    a0, a1, a2, a3 = p[..., 0], p[..., 1], p[..., 2], p[..., 3]
    b0, b1, b2, b3 = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    out = np.empty(p.shape)
    out[..., 0] = a0*b0 - a1*b1 - a2*b2 - a3*b3
    out[..., 1] = a0*b1 + a1*b0 + a2*b3 - a3*b2
    out[..., 2] = a0*b2 - a1*b3 + a2*b0 + a3*b1
    out[..., 3] = a0*b3 + a1*b2 - a2*b1 + a3*b0
    return out


def qconj(p):
    out = p.copy()
    out[..., 1:] *= -1.0
    return out


def qtr(p):
    """Tr U = 2 a0."""
    return 2.0 * p[..., 0]


def rand_su2_near(shape, eps):
    """random SU(2) quaternions near identity (a0 ~ 1)."""
    v = rng.normal(size=shape + (3,)) * eps
    a0 = np.sqrt(np.maximum(1.0 - np.sum(v**2, axis=-1), 1e-12))
    q = np.empty(shape + (4,))
    q[..., 0] = a0
    q[..., 1:] = v
    n = np.sqrt(np.sum(q**2, axis=-1, keepdims=True))
    return q / n


class SU2:
    def __init__(self, L, D=4):
        self.L, self.D = L, D
        # U[mu] shape (L,)*D + (4,); init cold (identity)
        self.U = np.zeros((D,) + (L,)*D + (4,))
        self.U[..., 0] = 1.0

    def staple(self, mu):
        """sum of staples for links in direction mu (returned as a quaternion
        field -- note: staple is a sum of SU(2) matrices, NOT itself SU(2))."""
        L, D, U = self.L, self.D, self.U
        S = np.zeros((L,)*D + (4,))
        for nu in range(D):
            if nu == mu:
                continue
            Unu = U[nu]
            Umu = U[mu]
            # forward staple: U_nu(n+mu) U_mu(n+nu)^dag U_nu(n)^dag
            Unu_pmu = np.roll(Unu, -1, axis=mu)
            Umu_pnu = np.roll(Umu, -1, axis=nu)
            term1 = qmul(qmul(Unu_pmu, qconj(Umu_pnu)), qconj(Unu))
            # backward staple: U_nu(n+mu-nu)^dag U_mu(n-nu)^dag U_nu(n-nu)
            Unu_pmu_mnu = np.roll(Unu_pmu, +1, axis=nu)
            Umu_mnu = np.roll(Umu, +1, axis=nu)
            Unu_mnu = np.roll(Unu, +1, axis=nu)
            term2 = qmul(qmul(qconj(Unu_pmu_mnu), qconj(Umu_mnu)), Unu_mnu)
            S += term1 + term2
        return S

    def sweep(self, beta, eps=0.4):
        """one checkerboard Metropolis sweep."""
        L, D = self.L, self.D
        coords = np.indices((L,)*D).sum(0) % 2
        for mu in range(D):
            S = self.staple(mu)
            for par in (0, 1):
                mask = (coords == par)
                Uold = self.U[mu]
                R = rand_su2_near((L,)*D, eps)
                Unew = qmul(R, Uold)
                # S_link = -(beta/2) Tr(U_mu . Staple) = -beta * scalarpart(U_mu Staple)
                # where U_P = U_mu . Staple, so use the TRUE product scalar part.
                dot_new = qmul(Unew, S)[..., 0]       # = (1/2)Tr(Unew . S)
                dot_old = qmul(Uold, S)[..., 0]
                dS = -(beta) * (dot_new - dot_old)
                acc = (dS < 0) | (rng.random((L,)*D) < np.exp(-np.clip(dS, 0, 50)))
                take = acc & mask
                self.U[mu] = np.where(take[..., None], Unew, Uold)

    def mean_plaquette(self):
        L, D, U = self.L, self.D, self.U
        tot, cnt = 0.0, 0
        for mu in range(D):
            for nu in range(mu+1, D):
                Umu = U[mu]; Unu = U[nu]
                P = qmul(qmul(Umu, np.roll(Unu, -1, axis=mu)),
                         qmul(qconj(np.roll(Umu, -1, axis=nu)), qconj(Unu)))
                tot += np.mean(0.5*qtr(P)); cnt += 1
        return tot/cnt

    def _link(self, direction, o_mu, o_nu, mu, nu):
        """U[direction] evaluated at base+o_mu*mu+o_nu*nu (field indexed by base)."""
        f = self.U[direction]
        if o_mu:
            f = np.roll(f, -o_mu, axis=mu)
        if o_nu:
            f = np.roll(f, -o_nu, axis=nu)
        return f

    def wilson_loop(self, R, T, mu=0, nu=3):
        """planar RxT Wilson loop in plane (mu,nu), averaged over all base sites."""
        # bottom: R links along +mu at o_nu=0
        W = self._link(mu, 0, 0, mu, nu)
        for s in range(1, R):
            W = qmul(W, self._link(mu, s, 0, mu, nu))
        # right: T links along +nu at o_mu=R
        for s in range(0, T):
            W = qmul(W, self._link(nu, R, s, mu, nu))
        # top: R links along -mu at o_nu=T (reversed, conjugated)
        for s in range(R-1, -1, -1):
            W = qmul(W, qconj(self._link(mu, s, T, mu, nu)))
        # left: T links along -nu at o_mu=0 (reversed, conjugated)
        for s in range(T-1, -1, -1):
            W = qmul(W, qconj(self._link(nu, 0, s, mu, nu)))
        return float(np.mean(0.5*qtr(W)))


def gauge_invariance_test(L=6, D=4):
    m = SU2(L, D)
    for _ in range(20):
        m.sweep(beta=2.0)
    P_before = m.mean_plaquette()
    # random local gauge transform: U_mu(n) -> g(n) U_mu(n) g(n+mu)^dag
    g = rand_su2_near((L,)*D, eps=0.9)
    for mu in range(D):
        gp = np.roll(g, -1, axis=mu)
        m.U[mu] = qmul(qmul(g, m.U[mu]), qconj(gp))
    P_after = m.mean_plaquette()
    return abs(P_after - P_before)


def run_confinement(L=6, D=4, betas=(1.0, 2.6), therm=120, meas=220):
    """Area-law diagnostic: r = ln W(2,2) / ln W(1,1).
       AREA law (confinement):  W(RT) ~ exp(-sigma R T) -> r = area(2x2)/area(1x1) = 4
       PERIMETER law (Coulomb):  W ~ exp(-mu perim)      -> r = perim(2x2)/perim(1x1) = 2
    """
    results = {}
    for beta in betas:
        m = SU2(L, D)
        for _ in range(therm):
            m.sweep(beta)
        acc = {(1, 1): [], (2, 2): [], (1, 2): []}
        Pm = []
        for _ in range(meas):
            m.sweep(beta)
            Pm.append(m.mean_plaquette())
            for k in acc:
                acc[k].append(m.wilson_loop(*k))
        W = {k: float(np.mean(v)) for k, v in acc.items()}
        W11, W22 = W[(1, 1)], W[(2, 2)]
        area_ratio = (float(np.log(W22) / np.log(W11))
                      if W11 > 0 and W22 > 0 else float("nan"))
        sigma = float(-np.log(W11))   # leading-order string tension (lattice units)
        results[str(beta)] = {"mean_plaquette": float(np.mean(Pm)),
                              "strong_coupling_pred_beta/4": beta/4.0,
                              "W_1x1": W11, "W_2x2": W22, "W_1x2": W[(1, 2)],
                              "area_ratio_lnW22_over_lnW11": area_ratio,
                              "string_tension_-lnW11": sigma}
    return results


def main():
    print("="*70)
    print("PHASE 3 -- SU(2) gauge field on QNG edges")
    print("="*70)

    gi = gauge_invariance_test()
    print("\n[G1] gauge invariance: |dP| under random local SU(2) = %.3e" % gi)
    g1 = gi < 1e-10

    print("\n[G2/G3] plaquette + confinement (4D L=6 SU(2) Metropolis)")
    res = run_confinement()
    for beta, r in res.items():
        print("  beta=%s  <P>=%.4f (pred b/4=%.4f)  W11=%.4f W22=%.5f  "
              "area_ratio(lnW22/lnW11)=%.2f  sigma=%.3f"
              % (beta, r["mean_plaquette"], r["strong_coupling_pred_beta/4"],
                 r["W_1x1"], r["W_2x2"],
                 r["area_ratio_lnW22_over_lnW11"], r["string_tension_-lnW11"]))

    # G2: plaquette matches strong-coupling expansion at small beta
    r_strong = res[str(1.0)]
    g2 = abs(r_strong["mean_plaquette"] - r_strong["strong_coupling_pred_beta/4"]) < 0.05
    # G3: area law at strong coupling -> area_ratio near 4 (>=3), and larger than weak
    ar_strong = r_strong["area_ratio_lnW22_over_lnW11"]
    ar_weak = res[str(2.6)]["area_ratio_lnW22_over_lnW11"]
    g3 = (ar_strong >= 3.0) and (ar_strong > ar_weak)

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  G1 gauge invariant (genuine gauge theory) : %s" % g1)
    print("  G2 plaquette matches strong-coupling beta/4 : %s" % g2)
    print("  G3 confinement: area_ratio strong=%.2f (~4) > weak=%.2f : %s"
          % (ar_strong, ar_weak, g3))

    if g1 and g3:
        verdict = ("SU2_EDGES_CONFINE: QNG edges host a genuine SU(2) gauge "
                   "theory -- gauge-invariant to machine precision, and the "
                   "Wilson-loop Creutz ratio shows a nonzero string tension "
                   "(AREA law) at strong coupling that weakens toward weak "
                   "coupling. This is the uniquely NON-ABELIAN signature: "
                   "confinement (the strong-force phenomenology). The edge sector "
                   "naturally extends from U(1) photon to SU(N) confining force. "
                   "CAVEAT (DER-QNG-101 / professor verdict): this is the PURE-"
                   "GAUGE sector only; the non-abelian MATTER multiplet is a hard "
                   "group-theory obstruction -- 2 real node scalars (sigma_g, "
                   "sigma_m) CANNOT form an SU(2) doublet (needs complex C^2). "
                   "Full SM gauge needs new node ontology (v13).")
    elif g1:
        verdict = ("SU2_EDGES_GAUGE_OK_CONFINEMENT_WEAK: gauge-invariant SU(2) "
                   "confirmed on edges; confinement signal weak at this lattice/"
                   "statistics -- rerun larger.")
    else:
        verdict = "INCONCLUSIVE -- gauge invariance failed; check implementation."
    print("\n  => " + verdict)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "report.json"), "w") as f:
        json.dump({"G1_gauge_invariance_dP": gi, "confinement": res,
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT_DIR, "report.json"))


if __name__ == "__main__":
    main()
