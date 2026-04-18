from __future__ import annotations

"""Finite-size scaling of ring mass (QNG-GPU-006, GPU).

Determines the L->infinity canonical ring mass by scanning L=20..60.

Key question: at what L does M_ring(L) saturate?
  Screening length lambda = sqrt(BETA/ALPHA) = sqrt(70) ~ 8.4 lu
  Expected saturation at L >> 3*lambda ~ 25 lu
  CPU-074 used L=20 (below saturation threshold!)

Measurements:
  M_ring(R=4, L) and M_ring(R=5, L) for L in {20, 30, 40, 50, 60}
  Ratio M(R=5)/M(R=4, L) -- should converge if baryon ID is robust
  Extrapolated M_inf via fit: M(L) = M_inf * (1 - A*exp(-L/xi))

Physical implication:
  If ratio converges -> baryon mass identification (DER-QNG-038) robust
  If ratio drifts    -> a_M is L-dependent, identification needs L->inf value
  If mass saturates at L=40-50 -> L=20 underestimates by known factor
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-finite-size-scaling-v1"

# Matched to CPU-074
SIGMA_REF = 0.5
ALPHA     = 0.005
BETA      = 0.35
BETA_PHI  = 0.02
DELTA_CHI = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
GAMMA_PHI = 0.10
K_BACK    = 0.10

LAMBDA_SCREEN = math.sqrt(BETA / ALPHA)  # ~8.37 lu

PHASE1 = 300
PHASE2 = 1500
PHASE3 = 1000

L_VALUES = [20, 30, 40, 50, 60]
RADII    = [4, 5]

# CPU-074 reference (L=20)
CPU074 = {4: 728.92, 5: 954.88}


# ---------------------------------------------------------------------------
# Geometry (rebuilt per L)
# ---------------------------------------------------------------------------

def build_neighbor_arrays(L):
    xs = np.arange(L, dtype=np.int32)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel()
    nb = np.stack([
        ((xg - 1) % L) * L * L + yg * L + zg,
        ((xg + 1) % L) * L * L + yg * L + zg,
        xg * L * L + ((yg - 1) % L) * L + zg,
        xg * L * L + ((yg + 1) % L) * L + zg,
        xg * L * L + yg * L + (zg - 1) % L,
        xg * L * L + yg * L + (zg + 1) % L,
    ], axis=1).astype(np.int32)
    return cp.asarray(nb)


def build_phi(L, R):
    cx = cy = cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg - cx; dy = yg - cy; dz = zg - cz
    dx = np.where(dx >  L/2, dx - L, dx)
    dx = np.where(dx < -L/2, dx + L, dx)
    dy = np.where(dy >  L/2, dy - L, dy)
    dy = np.where(dy < -L/2, dy + L, dy)
    dz = np.where(dz >  L/2, dz - L, dz)
    dz = np.where(dz < -L/2, dz + L, dz)
    rho = np.sqrt(dx*dx + dy*dy)
    phi = np.arctan2(dz, rho - R)
    return cp.asarray(phi.ravel())


# ---------------------------------------------------------------------------
# GPU dynamics
# ---------------------------------------------------------------------------

def wrap_gpu(a):
    a = a % (2 * math.pi)
    return cp.where(a > math.pi, a - 2 * math.pi, a)


def nb_mean(field, nb_idx):
    return field[nb_idx].mean(axis=1)


def disorder_gpu(phi, nb_idx):
    phi_nb = phi[nb_idx]
    sx = cp.cos(phi_nb).mean(axis=1)
    sy = cp.sin(phi_nb).mean(axis=1)
    return cp.maximum(0.0, 1.0 - cp.sqrt(sx*sx + sy*sy))


def phi_weighted_mean(phi, sm, nb_idx):
    phi_nb = phi[nb_idx]
    sm_nb  = sm[nb_idx]
    tw = sm_nb.sum(axis=1)
    sx = (sm_nb * cp.cos(phi_nb)).sum(axis=1)
    sy = (sm_nb * cp.sin(phi_nb)).sum(axis=1)
    return cp.where(tw > 1e-10,
                    cp.arctan2(sy / cp.maximum(tw, 1e-10),
                               sx / cp.maximum(tw, 1e-10)),
                    phi)


def step_p1(sm, chi, phi, nb_idx):
    smb = nb_mean(sm, nb_idx)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm), 0.0, 1.0)
    nc  = chi*(1 - CHI_DECAY) + CHI_REL*(smb - sm) + DELTA_CHI*(SIGMA_REF - sm)
    pm  = phi_weighted_mean(phi, sm, nb_idx)
    np_ = wrap_gpu(phi + BETA_PHI * wrap_gpu(pm - phi))
    return nsm, nc, np_


def step_p2(sm, chi, phi, nb_idx):
    smb = nb_mean(sm, nb_idx)
    dis = disorder_gpu(phi, nb_idx)
    nsm = cp.clip(sm + ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
                     - GAMMA_PHI * dis * sm, 0.0, 1.0)
    nc  = chi*(1 - CHI_DECAY) + CHI_REL*(smb - sm) + DELTA_CHI*(SIGMA_REF - sm)
    pm  = phi_weighted_mean(phi, sm, nb_idx)
    np_ = wrap_gpu(phi + BETA_PHI * wrap_gpu(pm - phi))
    return nsm, nc, np_


def step_p3(sm, phi, nb_idx):
    """Conservative: diffusion only, no restoration, no Channel F."""
    smb = nb_mean(sm, nb_idx)
    nsm = cp.clip(sm + BETA*(smb - sm), 0.0, 1.0)
    pm  = phi_weighted_mean(phi, sm, nb_idx)
    np_ = wrap_gpu(phi + BETA_PHI * wrap_gpu(pm - phi))
    return nsm, np_


def measure_mring(sm, L):
    return float(L*L*L * SIGMA_REF - cp.sum(sm))


# ---------------------------------------------------------------------------
# Run one (L, R) combination
# ---------------------------------------------------------------------------

def run_one(L, R, nb_idx):
    N = L * L * L
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi(L, R)

    for _ in range(PHASE1):
        sm, chi, phi = step_p1(sm, chi, phi, nb_idx)

    for _ in range(PHASE2):
        sm, chi, phi = step_p2(sm, chi, phi, nb_idx)

    M_p2 = measure_mring(sm, L)

    # Phase 3 checkpoints
    ckpts = {}
    for t in range(1, PHASE3 + 1):
        sm, phi = step_p3(sm, phi, nb_idx)
        if t in (200, 500, 1000):
            ckpts[t] = round(measure_mring(sm, L), 3)

    return {"M_p2": round(M_p2, 3), "ckpts": ckpts, "M_final": ckpts[1000]}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("Finite-size scaling of ring mass (QNG-GPU-006)")
    print(f"L values: {L_VALUES}  Radii: {RADII}")
    print(f"Screening length lambda = sqrt(BETA/ALPHA) = {LAMBDA_SCREEN:.2f} lu")
    print(f"Expected saturation at L >> {3*LAMBDA_SCREEN:.0f} lu")
    print(f"CPU-074 reference (L=20): R=4 -> {CPU074[4]}, R=5 -> {CPU074[5]}")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    all_results = {}

    for L in L_VALUES:
        print(f"=== L={L} (N={L**3}) ===", flush=True)
        nb_idx = build_neighbor_arrays(L)
        row = {}
        for R in RADII:
            res = run_one(L, R, nb_idx)
            row[R] = res
            ref = CPU074.get(R, 0)
            pct = (res["M_final"] - ref) / ref * 100
            print(f"  R={R}: M_p2={res['M_p2']:.2f}  "
                  f"M_final={res['M_final']:.2f}  "
                  f"vs_CPU074={pct:+.1f}%  "
                  f"ckpts={res['ckpts']}", flush=True)

        ratio = row[5]["M_final"] / max(row[4]["M_final"], 1e-6)
        ratio_ref = CPU074[5] / CPU074[4]
        print(f"  Ratio M(R=5)/M(R=4) = {ratio:.4f}  "
              f"(CPU-074: {ratio_ref:.4f}  diff={abs(ratio-ratio_ref)/ratio_ref*100:.2f}%)")
        print()
        all_results[L] = row

    # Summary table
    print("="*70)
    print("FINITE-SIZE SCALING SUMMARY")
    print("="*70)
    print(f"{'L':>4}  {'M(R=4)':>9}  {'M(R=5)':>9}  {'ratio':>7}  "
          f"{'M4_vs_CPU074':>13}  {'ratio_vs_CPU074':>16}")
    print("-"*70)

    ratio_ref = CPU074[5] / CPU074[4]
    scan_data = []
    for L in L_VALUES:
        m4 = all_results[L][4]["M_final"]
        m5 = all_results[L][5]["M_final"]
        ratio = m5 / max(m4, 1e-6)
        pct4  = (m4 - CPU074[4]) / CPU074[4] * 100
        rpct  = (ratio - ratio_ref) / ratio_ref * 100
        print(f"{L:>4}  {m4:>9.2f}  {m5:>9.2f}  {ratio:>7.4f}  "
              f"{pct4:>+12.1f}%  {rpct:>+15.2f}%")
        scan_data.append({"L": L, "M4": m4, "M5": m5,
                          "ratio": round(ratio, 5),
                          "M4_pct_vs_ref": round(pct4, 2),
                          "ratio_pct_vs_ref": round(rpct, 2)})

    # Convergence check: is ratio stable in last 3 points?
    ratios = [d["ratio"] for d in scan_data]
    last3_spread = max(ratios[-3:]) - min(ratios[-3:])
    print()
    print(f"Ratio spread in last 3 L values: {last3_spread:.5f}")
    if last3_spread < 0.005:
        conv_verdict = "CONVERGED"
        conv_detail  = (f"Ratio stable at {ratios[-1]:.4f} +/- {last3_spread/2:.5f} "
                        f"for L={L_VALUES[-3:]}")
    else:
        conv_verdict = "NOT_CONVERGED"
        conv_detail  = (f"Ratio still drifting: {ratios[-3]:.4f} -> {ratios[-1]:.4f}. "
                        f"Need larger L.")

    print(f"CONVERGENCE: {conv_verdict}")
    print(f"  {conv_detail}")

    # Simple linear extrapolation for M_inf (assuming M ~ M_inf - A*exp(-L/xi))
    # Use last two points for rough estimate
    if len(L_VALUES) >= 2:
        L1, L2 = L_VALUES[-2], L_VALUES[-1]
        m4_1 = all_results[L1][4]["M_final"]
        m4_2 = all_results[L2][4]["M_final"]
        dL = L2 - L1
        if m4_2 > m4_1:
            rate = (m4_2 - m4_1) / dL
            m4_extrap = m4_2 + rate * (100 - L2)  # rough extrapolation to L=100
        else:
            m4_extrap = m4_2
        print(f"\nRough M(R=4) extrapolation to L=100: {m4_extrap:.1f}")
        print(f"(from linear trend at L={L1}->{L2}: "
              f"{m4_1:.1f} -> {m4_2:.1f}, delta={m4_2-m4_1:+.1f})")

    # Save
    report = {
        "params": {"L_values": L_VALUES, "RADII": RADII,
                   "ALPHA": ALPHA, "BETA": BETA,
                   "GAMMA_PHI": GAMMA_PHI, "BETA_PHI": BETA_PHI,
                   "PHASE1": PHASE1, "PHASE2": PHASE2, "PHASE3": PHASE3,
                   "lambda_screen": round(LAMBDA_SCREEN, 3)},
        "cpu074_ref": CPU074,
        "scan": scan_data,
        "convergence": conv_verdict,
        "convergence_detail": conv_detail,
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = [
        "# Finite-Size Scaling of Ring Mass (QNG-GPU-006)", "",
        f"Screening length lambda = {LAMBDA_SCREEN:.2f} lu  "
        f"(saturation expected at L >> {3*LAMBDA_SCREEN:.0f} lu)", "",
        "## Scan Results", "",
        "| L | M(R=4) | M(R=5) | ratio | M4 vs CPU-074 | ratio vs CPU-074 |",
        "|---|--------|--------|-------|---------------|-----------------|",
    ]
    for d in scan_data:
        lines.append(f"| {d['L']} | {d['M4']:.2f} | {d['M5']:.2f} | "
                     f"{d['ratio']:.4f} | {d['M4_pct_vs_ref']:+.1f}% | "
                     f"{d['ratio_pct_vs_ref']:+.2f}% |")
    lines += ["", f"## Convergence: {conv_verdict}", "", conv_detail,
              "", f"CPU-074 reference ratio: {ratio_ref:.4f} (L=20)"]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nArtifacts: {out}")
    return 0 if conv_verdict == "CONVERGED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
