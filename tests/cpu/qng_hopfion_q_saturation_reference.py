from __future__ import annotations

"""QNG-CPU-153: Hopfion Q-saturation test (Q=1..7) under v12 plaquette curl.

CPU-151 found that Hopfion Q=1 and Q=2 have NEARLY IDENTICAL E_gauge
(7817 vs 7738, agreement to 1%) despite distinct phi-XY energies
(Q=1: ΔE=9.76, Q=2: ΔE=12.11). This suggested a Q-SATURATION of the
v12 photon emission channel.

CPU-153 tests this prediction across Q=1..7:
- If E_gauge plateaus at some Q* (and stays constant for Q > Q*),
  Q-saturation is genuine. The v12 photon channel has a topology-
  insensitive rate once toroidal winding is established.
- If E_gauge continues growing with Q, saturation is just an L=20
  finite-volume coincidence.

Also probed: spectral structure of E_gauge — does it decompose into
"plateau" + "step contributions" that hint at internal selection rules?

Theoretical context: in SM, radiative transition rates between
excited atomic/nuclear states are NOT universal — they depend on
matrix elements |<f|H_int|i>|^2 which vary by orders of magnitude.
QNG-Q-saturation would be a NOVEL prediction not present in SM.

Reference: DER-QNG-076 (v12 EM), DER-QNG-092 §F (CPU-151), Paper 7 P3.
"""

import json
import math
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-hopfion-q-saturation-v1"


L = 24                # default; override with --L
RING_R = 5.0          # ring radius (kept fixed; in absolute lattice units)


def wrap_pi(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def setup_lattice(L_param: int):
    """(Re)initialize globals for given L."""
    global L, N, XC, YC, ZC, XX, YY, ZZ, DX, DY, DZ
    L = L_param
    N = L * L * L
    XC, YC, ZC = L/2.0, L/2.0, L/2.0
    ax = np.arange(L, dtype=np.float64)
    XX, YY, ZZ = np.meshgrid(ax, ax, ax, indexing='ij')
    def mi(d):
        d = d.copy()
        d[d >  L/2] -= L
        d[d < -L/2] += L
        return d
    DX = mi(XX - XC)
    DY = mi(YY - YC)
    DZ = mi(ZZ - ZC)


setup_lattice(L)


def init_phi_hopfion(q_twist: int) -> np.ndarray:
    rho = np.sqrt(DX*DX + DY*DY)
    poloidal = np.arctan2(DZ, rho - RING_R)
    toroidal = np.arctan2(DY, DX)
    return wrap_pi(poloidal + q_twist * toroidal)


def plaquette_curls(phi: np.ndarray):
    phi_x_step = wrap_pi(np.roll(phi, -1, axis=0) - phi)
    phi_y_step = wrap_pi(np.roll(phi, -1, axis=1) - phi)
    phi_z_step = wrap_pi(np.roll(phi, -1, axis=2) - phi)
    F_xy = (phi_x_step + np.roll(phi_y_step, -1, axis=0)
            - np.roll(phi_x_step, -1, axis=1) - phi_y_step)
    F_yz = (phi_y_step + np.roll(phi_z_step, -1, axis=1)
            - np.roll(phi_y_step, -1, axis=2) - phi_z_step)
    F_xz = (phi_x_step + np.roll(phi_z_step, -1, axis=0)
            - np.roll(phi_x_step, -1, axis=2) - phi_z_step)
    return F_xy, F_yz, F_xz


def analyze(phi, label):
    F_xy, F_yz, F_xz = plaquette_curls(phi)
    all_F = np.concatenate([F_xy.flatten(), F_yz.flatten(), F_xz.flatten()])
    n_flux = int(np.sum(np.abs(all_F) > math.pi))
    E_gauge = float(np.sum(all_F * all_F))
    max_F = float(np.max(np.abs(all_F)))
    mean_F_abs = float(np.mean(np.abs(all_F)))
    # Decomposition by plane
    E_xy = float(np.sum(F_xy * F_xy))
    E_yz = float(np.sum(F_yz * F_yz))
    E_xz = float(np.sum(F_xz * F_xz))
    return {
        "label": label,
        "E_gauge_total": E_gauge,
        "E_gauge_xy_plane": E_xy,
        "E_gauge_yz_plane": E_yz,
        "E_gauge_xz_plane": E_xz,
        "n_flux_above_pi": n_flux,
        "max_abs_F": max_F,
        "mean_abs_F": mean_F_abs,
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--Q-max", type=int, default=7)
    ap.add_argument("--L", type=int, default=L)
    args = ap.parse_args()

    if args.L != L:
        setup_lattice(args.L)

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f"QNG-CPU-153: Hopfion Q-saturation test")
    print(f"L={L}  N={N}  ring R={RING_R}")
    print(f"Testing Q = 0..{args.Q_max}")
    print()

    results = []
    t_start = time.time()
    for Q in range(args.Q_max + 1):
        phi = init_phi_hopfion(Q)
        res = analyze(phi, f"hopfion_Q{Q}")
        res["Q"] = Q
        results.append(res)
        print(f"  Q={Q}: E_gauge={res['E_gauge_total']:.1f}  "
              f"N_flux={res['n_flux_above_pi']}  "
              f"max|F|={res['max_abs_F']:.3f}  "
              f"by plane (xy/yz/xz)={res['E_gauge_xy_plane']:.1f}/"
              f"{res['E_gauge_yz_plane']:.1f}/{res['E_gauge_xz_plane']:.1f}",
              flush=True)
    dt = time.time() - t_start
    print(f"\nTotal time: {dt:.2f} s")
    print()

    # Saturation analysis
    print("=" * 90)
    print(f"{'Q':>4}  {'E_gauge':>10}  {'E/E_Q1':>10}  {'delta vs prev':>14}  "
          f"{'N_flux':>8}")
    print("-" * 90)
    E_Q1 = results[1]["E_gauge_total"] if len(results) > 1 else 1.0
    prev = None
    for r in results:
        if prev is None:
            delta_pct = "—"
        else:
            delta_pct = f"{(r['E_gauge_total']/prev - 1)*100:+.2f}%"
        rel = r["E_gauge_total"] / E_Q1
        print(f"  {r['Q']:>2}  {r['E_gauge_total']:>10.1f}  {rel:>10.4f}  "
              f"{delta_pct:>14}  {r['n_flux_above_pi']:>8d}")
        prev = r["E_gauge_total"]
    print("=" * 90)

    # Q-saturation criterion: from Q=2 onward, successive deltas < 5%
    saturated_above = None
    for i in range(2, len(results)):
        delta = abs(results[i]["E_gauge_total"] / results[i-1]["E_gauge_total"] - 1)
        if delta < 0.05:
            if saturated_above is None:
                saturated_above = results[i]["Q"]
        else:
            saturated_above = None  # reset
    print()
    if saturated_above is not None and saturated_above <= 3:
        print(f"  -> Q-saturation CONFIRMED from Q >= {saturated_above}")
        print(f"     Successive E_gauge changes < 5% for Q >= {saturated_above}")
        decision = True
    elif saturated_above is not None:
        print(f"  -> Q-saturation PARTIAL: holds from Q >= {saturated_above}")
        print(f"     But not at Q=2 as predicted from CPU-151")
        decision = True
    else:
        print(f"  -> Q-saturation FALSIFIED: E_gauge grows with Q monotonically")
        decision = False

    # Best fit: E_gauge(Q) for Q>=1
    Q_arr = np.array([r["Q"] for r in results if r["Q"] >= 1])
    E_arr = np.array([r["E_gauge_total"] for r in results if r["Q"] >= 1])
    # Fit to power law E = A * Q^p
    if len(Q_arr) >= 2:
        lnQ = np.log(Q_arr)
        lnE = np.log(E_arr)
        # least-squares slope
        n = len(lnQ)
        slope = ((n*np.sum(lnQ*lnE) - np.sum(lnQ)*np.sum(lnE))
                 / (n*np.sum(lnQ*lnQ) - np.sum(lnQ)**2))
        intercept = (np.sum(lnE) - slope*np.sum(lnQ)) / n
        A = float(np.exp(intercept))
        p = float(slope)
        # Also fit asymptote model E = E_inf - C/Q (Q-saturation curve)
        # E_inf = lim_Q E, C = (E_inf - E_1)
        # 1/E - 1/E_inf = (1/C - 1/(C*Q)). Fit linearly?
        # Simpler: assume saturation, take average over Q>=2 as E_inf
        if len(Q_arr) >= 2:
            E_inf_estimate = float(np.mean(E_arr[1:]))  # average Q>=2
            saturation_rel_dev = float(np.std(E_arr[1:]) / E_inf_estimate)
        else:
            E_inf_estimate = E_arr[-1]
            saturation_rel_dev = 0.0
        print()
        print(f"Power-law fit E_gauge = A * Q^p:")
        print(f"  A = {A:.1f}, p = {p:.4f}")
        print(f"Saturation level E_inf estimate (avg Q>=2): {E_inf_estimate:.1f}")
        print(f"  Std/mean of E for Q>=2: {saturation_rel_dev*100:.2f}%")
    else:
        A = p = 0.0
        E_inf_estimate = 0.0
        saturation_rel_dev = 0.0

    report = {
        "test_id": "QNG-CPU-153",
        "decision": "pass" if decision else "fail",
        "params": {"L": L, "RING_R": RING_R, "Q_max": args.Q_max},
        "results": results,
        "analysis": {
            "saturated_from_Q": saturated_above,
            "power_law_A": A,
            "power_law_p": p,
            "E_inf_estimate_avg_Qge2": E_inf_estimate,
            "saturation_relative_dev_pct": saturation_rel_dev * 100,
        },
        "interpretation": (
            "If E_gauge saturates (relative deviation < 5% for Q >= some Q*), "
            "the v12 photon emission rate is Q-independent, a novel QNG "
            "prediction (P3 in Paper 7). Otherwise, saturation observed at "
            "Q=1,2 in CPU-151 was a finite-volume coincidence."
        ),
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
