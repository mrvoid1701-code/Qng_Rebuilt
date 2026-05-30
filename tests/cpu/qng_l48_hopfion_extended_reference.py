from __future__ import annotations

"""QNG-CPU-175: L=48 Hopfion Q=1..15 extended ladder + R variation.

Phase 1 of autonomous extension run: extend Hopfion ladder beyond CPU-145
Q=1..5 limit to find more nucleon excitations + test if different R
radius gives different particle families.

At L=24, Q=6..10 was contaminated by lattice equipartition (CPU-155
clusters). L=48 should resolve this and give clean Q=6..15 predictions.

Tests:
A. Q=1..15 at fixed R=5 (extended nucleon spectrum)
B. R=3, 4, 5, 6, 7, 8 at fixed Q=1 (R-variation for different families)

Reference: DER-QNG-098 §"Q>=6 needs L=48+", CPU-145 v2.
"""

import json
import math
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-l48-hopfion-extended-v1"


# L=48 lattice
L = 48
N = L * L * L
BETA_PHI = 0.06
Z_NB = 6

DEFAULT_RING_R = 5.0


def wrap_pi(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def mi_arr(d):
    d = d.copy()
    d[d >  L/2] -= L
    d[d < -L/2] += L
    return d


def make_coords():
    ax = np.arange(L, dtype=np.float64)
    XX, YY, ZZ = np.meshgrid(ax, ax, ax, indexing='ij')
    return XX, YY, ZZ


def init_phi_hopfion(q_twist, ring_R=DEFAULT_RING_R):
    XC, YC, ZC = L/2.0, L/2.0, L/2.0
    XX, YY, ZZ = make_coords()
    DX = mi_arr(XX - XC)
    DY = mi_arr(YY - YC)
    DZ = mi_arr(ZZ - ZC)
    rho = np.sqrt(DX*DX + DY*DY)
    poloidal = np.arctan2(DZ, rho - ring_R)
    toroidal = np.arctan2(DY, DX)
    return wrap_pi(poloidal + q_twist * toroidal)


def phi_energy(phi):
    """E_phi = -(beta_phi/(2z)) * sum_<ij> cos(phi_i - phi_j)."""
    total = 0.0
    for axis in range(3):
        for shift in (-1, +1):
            pj = np.roll(phi, shift, axis=axis)
            total += float(np.cos(pj - phi).sum())
    return -(BETA_PHI / (2 * Z_NB)) * total


def relax_step(phi, eta=0.20):
    ssin = np.zeros_like(phi)
    for axis in range(3):
        for shift in (-1, +1):
            phi_j = np.roll(phi, shift, axis=axis)
            ssin += np.sin(phi_j - phi)
    grad = -(BETA_PHI / Z_NB) * ssin
    return wrap_pi(phi - eta * grad)


def relax_and_measure(phi, label, n_steps=15000, log_every=1500):
    """Relax phi and measure final energy."""
    E_init = phi_energy(phi)
    print(f"  [{label}] E_init = {E_init:.3f}", flush=True)
    for t in range(1, n_steps + 1):
        phi = relax_step(phi)
        if t % log_every == 0:
            E = phi_energy(phi)
            print(f"  [{label}] step {t}  E={E:.3f}", flush=True)
    E_final = phi_energy(phi)
    E_vac = -BETA_PHI * N / 2.0  # Vacuum: all phi same, cos=1, total = 3N
    dE = E_final - E_vac
    return {
        "label": label,
        "E_init": E_init,
        "E_final": E_final,
        "dE": dE,
    }


# PDG nucleon spectrum + Delta
PDG_NUCLEON = [
    ("p", 938.27, "1/2+"),
    ("n", 939.57, "1/2+"),
    ("N(1440)", 1430, "1/2+"),
    ("N(1520)", 1515, "3/2-"),
    ("N(1535)", 1535, "1/2-"),
    ("N(1650)", 1650, "1/2-"),
    ("N(1675)", 1675, "5/2-"),
    ("N(1680)", 1680, "5/2+"),
    ("N(1700)", 1700, "3/2-"),
    ("N(1710)", 1710, "1/2+"),
    ("N(1720)", 1720, "3/2+"),
    ("N(1875)", 1875, "3/2-"),
    ("N(1900)", 1900, "3/2+"),
    ("N(2090)", 2090, "1/2-"),
    ("N(2100)", 2100, "1/2+"),
    ("N(2120)", 2120, "3/2-"),
    ("N(2190)", 2190, "7/2-"),
    ("N(2220)", 2220, "9/2+"),
    ("N(2250)", 2250, "9/2-"),
    ("Delta(1232)", 1232, "3/2+"),
    ("Delta(1600)", 1600, "3/2+"),
    ("Delta(1620)", 1620, "1/2-"),
    ("Delta(1700)", 1700, "3/2-"),
    ("Delta(1900)", 1900, "1/2-"),
    ("Delta(1905)", 1905, "5/2+"),
    ("Delta(1910)", 1910, "1/2+"),
    ("Delta(1920)", 1920, "3/2+"),
    ("Delta(1930)", 1930, "5/2-"),
    ("Delta(1950)", 1950, "7/2+"),
    ("Delta(2350)", 2350, "5/2-"),
    ("Delta(2390)", 2390, "7/2+"),
    ("Delta(2420)", 2420, "11/2+"),
]


def find_best_pdg_match(predicted_mass):
    best = min(PDG_NUCLEON, key=lambda x: abs(predicted_mass - x[1]))
    err = (predicted_mass - best[1]) / best[1] * 100
    return best[0], best[1], best[2], err


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--Q-max", type=int, default=15)
    ap.add_argument("--R-list", type=float, nargs='+',
                    default=[3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    ap.add_argument("--relax-steps", type=int, default=15000)
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f"QNG-CPU-175: L={L} extended Hopfion ladder + R variation")
    print(f"beta_phi={BETA_PHI}, relax_steps={args.relax_steps}")
    print()

    # ---------------------------------------------------------------
    # Part A: Q=1..15 at fixed R=5
    # ---------------------------------------------------------------
    print("=" * 100)
    print(f"PART A: Q-ladder at R={DEFAULT_RING_R}, L={L}")
    print("=" * 100)

    Q_results = []
    Q1_dE = None
    t_start = time.time()
    for Q in range(1, args.Q_max + 1):
        print(f"--- Q={Q} ---", flush=True)
        phi = init_phi_hopfion(Q, ring_R=DEFAULT_RING_R)
        res = relax_and_measure(phi, f"Q={Q}", n_steps=args.relax_steps)
        res["Q"] = Q
        res["R"] = DEFAULT_RING_R
        Q_results.append(res)
        if Q == 1:
            Q1_dE = res["dE"]
        # Predicted mass using Q=1 -> proton calibration
        if Q1_dE:
            pred = (res["dE"] / Q1_dE) * 938.27
            best_name, best_mass, best_jp, err = find_best_pdg_match(pred)
            res["predicted_MeV"] = pred
            res["best_match"] = best_name
            res["best_match_mass"] = best_mass
            res["best_match_JP"] = best_jp
            res["error_pct"] = err
            print(f"  Q={Q}: dE={res['dE']:.3f}, pred={pred:.1f} MeV "
                  f"-> {best_name} ({best_mass}, {best_jp}) err={err:+.2f}%",
                  flush=True)
        print()
    dt_A = time.time() - t_start
    print(f"Part A time: {dt_A:.1f}s")
    print()

    # ---------------------------------------------------------------
    # Part B: R variation at Q=1
    # ---------------------------------------------------------------
    print("=" * 100)
    print(f"PART B: R variation at Q=1, L={L}")
    print("=" * 100)
    R_results = []
    t_start = time.time()
    for R in args.R_list:
        print(f"--- R={R} ---", flush=True)
        phi = init_phi_hopfion(1, ring_R=R)
        res = relax_and_measure(phi, f"R={R}", n_steps=args.relax_steps)
        res["R"] = R
        res["Q"] = 1
        R_results.append(res)
        print()
    dt_B = time.time() - t_start
    print(f"Part B time: {dt_B:.1f}s")
    print()

    # Summary
    print("=" * 100)
    print("PART A SUMMARY: Hopfion Q ladder at R=5, L=48")
    print("=" * 100)
    print(f"{'Q':>3} {'dE':>10} {'pred MeV':>10} {'best match':<20} {'JP':>6} {'err %':>8}")
    print("-" * 100)
    for r in Q_results:
        if "predicted_MeV" in r:
            print(f"{r['Q']:>3} {r['dE']:>10.3f} {r['predicted_MeV']:>10.1f} "
                  f"{r['best_match']:<20} {r['best_match_JP']:>6} "
                  f"{r['error_pct']:>+8.2f}")
        else:
            print(f"{r['Q']:>3} {r['dE']:>10.3f} (Q=1 ref)")
    print()

    print("=" * 100)
    print("PART B SUMMARY: R variation at Q=1, L=48")
    print("=" * 100)
    print(f"{'R':>4} {'dE':>10} {'ratio R/R5':>12} {'as fraction of nucleon':>22}")
    print("-" * 100)
    R5_dE = next((r["dE"] for r in R_results if abs(r["R"] - 5.0) < 0.01), None)
    for r in R_results:
        if R5_dE:
            ratio = r["dE"] / R5_dE
            frac = ratio * 938.27
            print(f"{r['R']:>4.1f} {r['dE']:>10.3f} {ratio:>12.4f} "
                  f"{frac:>18.1f} MeV")
        else:
            print(f"{r['R']:>4.1f} {r['dE']:>10.3f}")
    print("=" * 100)

    # Save
    report = {
        "test_id": "QNG-CPU-175_L48_hopfion_extended",
        "params": {"L": L, "beta_phi": BETA_PHI,
                   "relax_steps": args.relax_steps,
                   "Q_max": args.Q_max,
                   "R_list": args.R_list},
        "Q_ladder_results": Q_results,
        "R_variation_results": R_results,
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
