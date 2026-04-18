from __future__ import annotations

"""Phi mass term: V(phi) = 1 - cos(phi) (QNG-GPU-014, GPU).

Adds sine-Gordon potential to phi dynamics:
  phi_new = phi + BETA_PHI*(phi_wm - phi) - MU_PHI*sin(phi)

V(phi) = 1 - cos(phi):
  - Minima at phi = 0, +-2pi, ... (compatible with 2pi-periodic phi)
  - V''(0) = 1 => m_phi_eff = sqrt(MU_PHI)
  - Screening: xi = sqrt(BETA_PHI / MU_PHI)
  - Topology: ring winding Q=+/-1 is preserved (topologically protected)

Target: xi ~ lambda_screen = 8.37 lu
  => MU_PHI ~ BETA_PHI / lambda^2 = 0.02 / 70 ~ 0.0003

Scan MU_PHI in {0.0001, 0.0003, 0.001, 0.003} x L in {20, 30, 40, 60}
for R=4 and R=5.

Key questions:
  1. Does M(R=5)/M(R=4) converge with L for some MU_PHI?
  2. If yes, does it converge to SM=1.313?
  3. What MU_PHI gives xi ~ lambda_screen?
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-phi-mass-term-v1"

SIGMA_REF = 0.5
ALPHA     = 0.005
BETA      = 0.35
BETA_PHI  = 0.02
DELTA_CHI = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
GAMMA_PHI = 0.10

PHASE1 = 300
PHASE2 = 1500

LAMBDA_SCREEN = math.sqrt(BETA / ALPHA)   # 8.37 lu
RATIO_SM      = 1232.0 / 938.3            # 1.3131

# MU_PHI: potential coupling. xi ~ sqrt(BETA_PHI / MU_PHI)
MU_VALUES = [0.0001, 0.0003, 0.001, 0.003]
L_VALUES  = [20, 30, 40, 60]
RADII     = [4, 5]


def build_nb(L):
    xs = np.arange(L, dtype=np.int32)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel()
    nb = np.stack([
        ((xg-1)%L)*L*L + yg*L + zg, ((xg+1)%L)*L*L + yg*L + zg,
        xg*L*L + ((yg-1)%L)*L + zg,  xg*L*L + ((yg+1)%L)*L + zg,
        xg*L*L + yg*L + (zg-1)%L,    xg*L*L + yg*L + (zg+1)%L,
    ], axis=1).astype(np.int32)
    return cp.asarray(nb)


def build_phi_ring(L, R):
    cx = cy = cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg-cx; dy = yg-cy; dz = zg-cz
    for d in [dx, dy, dz]:
        d[:] = np.where(d >  L/2, d-L, d)
        d[:] = np.where(d < -L/2, d+L, d)
    rho = np.sqrt(dx*dx + dy*dy)
    return cp.asarray(np.arctan2(dz, rho-R).ravel())


def build_shells(L):
    cx = cy = cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg-cx; dy = yg-cy; dz = zg-cz
    for d in [dx, dy, dz]:
        d[:] = np.where(d >  L/2, d-L, d)
        d[:] = np.where(d < -L/2, d+L, d)
    r = np.sqrt(dx*dx + dy*dy + dz*dz).ravel()
    n = L // 2
    shells = [cp.asarray((r >= s) & (r < s+1)) for s in range(n)]
    return shells, np.arange(n) + 0.5


def wrap_gpu(a):
    a = a % (2*math.pi)
    return cp.where(a > math.pi, a - 2*math.pi, a)

def nb_mean(f, nb): return f[nb].mean(axis=1)

def disorder(phi, nb):
    pnb = phi[nb]
    return cp.maximum(0.0, 1.0 - cp.sqrt(cp.cos(pnb).mean(axis=1)**2 +
                                          cp.sin(pnb).mean(axis=1)**2))

def phi_wm(phi, sm, nb):
    pnb = phi[nb]; snb = sm[nb]; tw = snb.sum(axis=1)
    sx = (snb*cp.cos(pnb)).sum(axis=1); sy = (snb*cp.sin(pnb)).sum(axis=1)
    return cp.where(tw>1e-10, cp.arctan2(sy/cp.maximum(tw,1e-10),
                                          sx/cp.maximum(tw,1e-10)), phi)

def step1(sm, chi, phi, nb, mu_phi):
    smb = nb_mean(sm, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm), 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    pm  = phi_wm(phi, sm, nb)
    # V(phi) = 1 - cos(phi) => force = -dV/dphi = -sin(phi)
    np_ = wrap_gpu(phi + BETA_PHI*wrap_gpu(pm-phi) - mu_phi*cp.sin(phi))
    return nsm, nc, np_

def step2(sm, chi, phi, nb, mu_phi):
    smb = nb_mean(sm, nb)
    dis = disorder(phi, nb)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF-sm) + BETA*(smb-sm)
                     - GAMMA_PHI*dis*sm, 0.0, 1.0)
    nc  = chi*(1-CHI_DECAY) + CHI_REL*(smb-sm) + DELTA_CHI*(SIGMA_REF-sm)
    pm  = phi_wm(phi, sm, nb)
    np_ = wrap_gpu(phi + BETA_PHI*wrap_gpu(pm-phi) - mu_phi*cp.sin(phi))
    return nsm, nc, np_


def fit_xi(r_centers, profile, R, L):
    """Fit exponential to bulk disorder. Return xi, R2."""
    r_min = R + 5; r_max = L//2 - 3
    mask = (r_centers > r_min) & (r_centers < r_max)
    r_fit = r_centers[mask]
    d_fit = np.array([profile[i] for i in range(len(r_centers))])[mask]
    d_fit = np.maximum(d_fit, 1e-12)
    if len(r_fit) < 3:
        return None, None
    try:
        from scipy.optimize import curve_fit
        def exp_model(r, A, xi): return A * np.exp(-r / xi)
        popt, _ = curve_fit(exp_model, r_fit, d_fit,
                            p0=[d_fit[0], LAMBDA_SCREEN],
                            bounds=([0, 0.1], [1, 200]), maxfev=3000)
        xi = popt[1]
        pred = exp_model(r_fit, *popt)
        ss_res = np.sum((d_fit - pred)**2)
        ss_tot = np.sum((d_fit - d_fit.mean())**2) + 1e-20
        r2 = 1 - ss_res / ss_tot
        return round(float(xi), 3), round(float(r2), 4)
    except Exception:
        return None, None


def run_one(L, R, mu_phi, nb, shells, r_centers):
    N = L*L*L
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi_ring(L, R)

    for _ in range(PHASE1): sm, chi, phi = step1(sm, chi, phi, nb, mu_phi)
    for _ in range(PHASE2): sm, chi, phi = step2(sm, chi, phi, nb, mu_phi)

    M_ring = float(N*SIGMA_REF - cp.sum(sm))

    # Disorder profile
    dis_field = disorder(phi, nb)
    profile = []
    for mask in shells:
        n = float(cp.sum(mask))
        profile.append(float(cp.sum(dis_field*mask))/n if n > 0 else 0.0)

    xi, r2 = fit_xi(r_centers, profile, R, L)
    dis_bulk = float(cp.mean(dis_field))

    return {"M_ring": round(M_ring, 2), "xi": xi, "r2_exp": r2,
            "dis_bulk": round(dis_bulk, 6)}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print("Phi mass term V(phi)=1-cos(phi) (QNG-GPU-014)")
    print(f"BETA_PHI={BETA_PHI}  lambda_screen={LAMBDA_SCREEN:.2f} lu")
    print(f"Predicted xi = sqrt(BETA_PHI/MU_PHI):")
    for mu in MU_VALUES:
        xi_pred = math.sqrt(BETA_PHI / mu)
        print(f"  MU_PHI={mu:.4f} => xi_pred={xi_pred:.2f} lu")
    print(f"L values: {L_VALUES}  Radii: {RADII}")
    print(f"SM ratio = {RATIO_SM:.4f}")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    all_rows = []

    for mu in MU_VALUES:
        xi_pred = math.sqrt(BETA_PHI / mu)
        print(f"=== MU_PHI={mu:.4f}  xi_pred={xi_pred:.2f} lu ===", flush=True)

        scan = []
        for L in L_VALUES:
            nb = build_nb(L)
            shells, r_centers = build_shells(L)
            r4 = run_one(L, 4, mu, nb, shells, r_centers)
            r5 = run_one(L, 5, mu, nb, shells, r_centers)
            ratio = r5["M_ring"] / max(r4["M_ring"], 1e-6)
            vs_sm = (ratio - RATIO_SM) / RATIO_SM * 100
            print(f"  L={L:>2}: M(R4)={r4['M_ring']:>8.1f}  M(R5)={r5['M_ring']:>8.1f}  "
                  f"ratio={ratio:.4f}  vs_SM={vs_sm:+.2f}%  "
                  f"xi(R5)={r5['xi'] or '?'}  dis_bulk={r4['dis_bulk']:.5f}", flush=True)
            scan.append({"L": L, "M_R4": r4["M_ring"], "M_R5": r5["M_ring"],
                         "ratio": round(ratio, 5),
                         "xi_R5": r5["xi"], "dis_bulk_R4": r4["dis_bulk"]})

        ratios   = [s["ratio"] for s in scan]
        last3    = ratios[-3:]
        spread   = max(last3) - min(last3)
        converged = spread < 0.02
        ratio_last = scan[-1]["ratio"]
        sm_ok = abs(ratio_last - RATIO_SM) / RATIO_SM < 0.05

        if converged and sm_ok:
            verdict = "PASS"
        elif converged:
            verdict = "PASS_WEAK"
        else:
            verdict = "FAIL"

        print(f"  => spread(last3)={spread:.4f}  ratio@L{L_VALUES[-1]}={ratio_last:.4f}  "
              f"verdict={verdict}")
        print()

        all_rows.append({"mu_phi": mu, "xi_pred": round(xi_pred, 2),
                         "scan": scan, "spread": round(spread, 5),
                         "ratio_last": round(ratio_last, 5),
                         "converged": converged, "sm_ok": sm_ok, "verdict": verdict})

    print("="*75)
    print("SUMMARY: MU_PHI vs convergence")
    print("="*75)
    print(f"{'MU_PHI':>8}  {'xi_pred':>8}  {'spread':>8}  "
          f"{'ratio@L60':>10}  {'vs_SM%':>8}  {'verdict'}")
    print("-"*75)
    for row in all_rows:
        vs = (row["ratio_last"] - RATIO_SM) / RATIO_SM * 100
        print(f"  {row['mu_phi']:>6.4f}  {row['xi_pred']:>8.2f}  {row['spread']:>8.4f}  "
              f"{row['ratio_last']:>10.4f}  {vs:>+7.2f}%  {row['verdict']}")

    # Best candidate
    passing = [r for r in all_rows if r["verdict"] == "PASS"]
    weak    = [r for r in all_rows if r["verdict"] == "PASS_WEAK"]
    best    = (passing or weak or all_rows)[0]

    print()
    if passing:
        print(f"BEST: MU_PHI={best['mu_phi']}  xi_pred={best['xi_pred']} lu  "
              f"ratio={best['ratio_last']:.4f}  -> CONVERGES TO SM")
    elif weak:
        print(f"BEST: MU_PHI={best['mu_phi']}  xi_pred={best['xi_pred']} lu  "
              f"ratio={best['ratio_last']:.4f}  -> CONVERGES (not SM)")
    else:
        print("No MU_PHI value achieves convergence. Larger scan needed.")

    report = {
        "params": {"L_values": L_VALUES, "RADII": RADII,
                   "PHASE1": PHASE1, "PHASE2": PHASE2,
                   "GAMMA_PHI": GAMMA_PHI, "BETA_PHI": BETA_PHI,
                   "LAMBDA_SCREEN": LAMBDA_SCREEN},
        "SM_ratio": RATIO_SM,
        "rows": all_rows,
    }
    with open(out/"report.json", "w") as f: json.dump(report, f, indent=2)

    lines = ["# Phi Mass Term V(phi)=1-cos(phi) (QNG-GPU-014)", "",
             f"BETA_PHI={BETA_PHI}  lambda_screen={LAMBDA_SCREEN:.2f}  SM={RATIO_SM:.4f}", "",
             "## Results", "",
             "| MU_PHI | xi_pred | spread(last3) | ratio@L60 | vs SM% | verdict |",
             "|--------|---------|--------------|-----------|--------|---------|"]
    for row in all_rows:
        vs = (row["ratio_last"] - RATIO_SM) / RATIO_SM * 100
        lines.append(f"| {row['mu_phi']} | {row['xi_pred']} | {row['spread']:.4f} | "
                     f"{row['ratio_last']:.4f} | {vs:+.2f}% | {row['verdict']} |")
    (out/"summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0 if passing else 1


if __name__ == "__main__":
    raise SystemExit(main())
