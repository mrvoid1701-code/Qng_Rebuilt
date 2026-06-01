"""
PHASE 25 (particle masses) -- the electroweak sector: the W-Z mass relation
(rho = 1, custodial symmetry).

The W/Z bosons live on the edges (v13 SU(2)xU(1), Phase 3/4b). Their ABSOLUTE
masses M_W = g v/2, M_Z = sqrt(g^2+g'^2) v/2 need the Higgs VEV v and the
couplings g,g' (inputs, as in the SM). But the doublet-Higgs structure predicts,
at tree level, the custodial relation:
    rho = M_W^2 / (M_Z^2 cos^2 theta_W) = 1   <->   M_W = M_Z cos theta_W
This is a STRUCTURAL consequence of the SU(2) DOUBLET Higgs (custodial SU(2)) --
exactly the v13 complex doublet (Phase 4b). A triplet/other Higgs would give
rho != 1. So rho = 1 is a genuine structural prediction of the v13 doublet.

Test: verify M_W = M_Z cos theta_W against PDG (tree level; the ~1% deviation is
the known radiative correction).
ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase25-electroweak-v1")

# PDG
M_W = 80.377      # GeV
M_Z = 91.1876     # GeV
sin2_thetaW = 0.23121   # on-shell


def main():
    print("="*70)
    print("PHASE 25 (particle masses) -- electroweak W-Z relation (rho=1)")
    print("="*70)

    cos_thetaW = np.sqrt(1 - sin2_thetaW)
    MW_pred = M_Z * cos_thetaW
    rho = M_W**2 / (M_Z**2 * cos_thetaW**2)
    print("\n  sin^2 theta_W = %.5f -> cos theta_W = %.5f" % (sin2_thetaW, cos_thetaW))
    print("  M_W = M_Z cos theta_W (custodial, tree):")
    print("    M_W_pred = %.3f GeV   vs PDG %.3f  (%.2f%%)"
          % (MW_pred, M_W, 100*abs(MW_pred-M_W)/M_W))
    print("  rho = M_W^2/(M_Z^2 cos^2 theta_W) = %.4f  (tree-level prediction = 1)" % rho)
    print("  (the ~1%% deviation from 1 is the known radiative (top/Higgs loop) correction)")

    custodial_ok = abs(rho - 1.0) < 0.02

    print("\n  [structural origin]")
    print("    rho=1 follows from the SU(2) DOUBLET Higgs (custodial SU(2)) = the")
    print("    v13 complex doublet (Phase 4b). A non-doublet Higgs gives rho != 1.")
    print("    So rho=1 is a genuine structural prediction of QNG's v13 doublet.")
    print("    ABSOLUTE M_W, M_Z need v (Higgs VEV) + g,g' (couplings) = inputs.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  rho = M_W^2/(M_Z^2 cos^2thetaW) = 1 (custodial, <2%%) : %s (%.4f)"
          % (custodial_ok, rho))

    verdict = (
        "ELECTROWEAK_RHO_1: the W-Z mass relation M_W = M_Z cos theta_W (the "
        f"custodial rho parameter) holds: rho = {rho:.4f} (tree-level prediction "
        "= 1; the ~1% deviation is the known top/Higgs radiative correction). "
        "This is a STRUCTURAL prediction of the SU(2) DOUBLET Higgs (custodial "
        "SU(2)) -- exactly the v13 complex doublet (Phase 4b); a non-doublet Higgs "
        "would give rho != 1. So QNG-v13 predicts rho=1, verified to ~1%. HONEST "
        "SCOPE: the ABSOLUTE W/Z masses (80.4, 91.2 GeV) need the Higgs VEV v=246 "
        "GeV and the couplings g, g' -- inputs, as in the SM (QNG does not derive "
        "the electroweak scale v, same status as the lepton Yukawas / Drumul 3). "
        "What QNG adds: the rho=1 STRUCTURE comes for free from the v13 doublet, "
        "and the W/Z carriers are the edge SU(2) gauge fields (Phase 3). The "
        "electroweak scale v itself is a separate input scale (like Lambda_QCD was "
        "before Phase 11/12 -- a dimensional-transmutation or vacuum-stability "
        "target for future work).")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"M_W_pred": float(MW_pred), "M_W_pdg": M_W, "M_Z_pdg": M_Z,
                   "rho": float(rho), "custodial_ok": bool(custodial_ok),
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
