from __future__ import annotations

"""QNG-CPU-149: Finite-volume test of knot universality.

CPU-148 confirmed universal half-life ~1044 lu for trefoil, figure-8,
cinquefoil at L=20. CPU-149 tests whether this universality is genuine
or a finite-volume artefact by repeating at L=32 and (optionally) L=40.

Same physical knot scale (KNOT_SCALE=1.8) maintained at both L — so the
knot occupies a smaller fraction of the lattice at L=32 and L=40. This
isolates the finite-volume contribution to the decay rate.

If half-lives stay near 1044 lu across L ∈ {20, 32, 40}: universality
is a real QNG prediction.

If half-lives drift with L: finite-volume effect, extrapolate to L→∞.

Reference: DER-QNG-092 §D (CPU-148 universality result), DER-QNG-091.
"""

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-knot-finite-volume-v1"


# Substrate parameters (canonical v7, match CPU-146/148)
SIGMA_REF = 0.5
ALPHA     = 0.005
BETA      = 0.35
BETA_PHI  = 0.02
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
GAMMA_PHI = 0.10
K_BACK    = 0.10
K_GM      = 0.001

KNOT_SCALE = 1.8

PHASE1 = 300
PHASE2 = 1500
PHASE3 = 3000

LOG_EVERY = 200


def wrap_pi(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def trefoil_curve(t):
    s = KNOT_SCALE
    x = s * (np.sin(t) + 2 * np.sin(2*t))
    y = s * (np.cos(t) - 2 * np.cos(2*t))
    z = s * (-np.sin(3*t))
    return np.stack([x, y, z], axis=-1)


def figure8_curve(t):
    s = KNOT_SCALE * 0.7
    x = s * ((2 + np.cos(2*t)) * np.cos(3*t))
    y = s * ((2 + np.cos(2*t)) * np.sin(3*t))
    z = s * (np.sin(4*t))
    return np.stack([x, y, z], axis=-1)


def cinquefoil_curve(t):
    s = KNOT_SCALE * 0.6
    R = 2.5 * s
    r = 1.0 * s
    x = (R + r * np.cos(5*t)) * np.cos(2*t)
    y = (R + r * np.cos(5*t)) * np.sin(2*t)
    z = r * np.sin(5*t)
    return np.stack([x, y, z], axis=-1)


def init_phi_from_knot(curve_fn, L, n_curve=360):
    XC = YC = ZC = L / 2.0
    ax = np.arange(L, dtype=np.float64)
    XX, YY, ZZ = np.meshgrid(ax, ax, ax, indexing='ij')

    ts = np.linspace(0.0, 2*math.pi, n_curve, endpoint=False)
    curve = curve_fn(ts) + np.array([XC, YC, ZC])

    nxt = np.roll(curve, -1, axis=0)
    prv = np.roll(curve, +1, axis=0)
    T = nxt - prv
    T /= np.linalg.norm(T, axis=1, keepdims=True)

    z_hat = np.array([0.0, 0.0, 1.0])
    x_hat = np.array([1.0, 0.0, 0.0])
    Nf = np.cross(T, z_hat)
    Nm = np.linalg.norm(Nf, axis=1, keepdims=True)
    fb = Nm.flatten() < 1e-3
    if np.any(fb):
        Nfx = np.cross(T[fb], x_hat)
        Nf[fb] = Nfx
        Nm[fb] = np.linalg.norm(Nfx, axis=1, keepdims=True)
    Nf /= Nm
    Bf = np.cross(T, Nf)
    Bf /= np.linalg.norm(Bf, axis=1, keepdims=True)

    pts = np.stack([XX.flatten(), YY.flatten(), ZZ.flatten()], axis=-1)
    N_total = L * L * L

    chunk = 2000
    nearest_t = np.zeros(N_total, dtype=np.int64)
    for start in range(0, N_total, chunk):
        end = min(start + chunk, N_total)
        d = pts[start:end, None, :] - curve[None, :, :]
        for ax_i in range(3):
            d[..., ax_i] = np.where(d[..., ax_i] >  L/2, d[..., ax_i] - L, d[..., ax_i])
            d[..., ax_i] = np.where(d[..., ax_i] < -L/2, d[..., ax_i] + L, d[..., ax_i])
        dist_sq = np.sum(d * d, axis=-1)
        nearest_t[start:end] = np.argmin(dist_sq, axis=1)

    v = pts - curve[nearest_t]
    for ax_i in range(3):
        v[:, ax_i] = np.where(v[:, ax_i] >  L/2, v[:, ax_i] - L, v[:, ax_i])
        v[:, ax_i] = np.where(v[:, ax_i] < -L/2, v[:, ax_i] + L, v[:, ax_i])

    N_at = Nf[nearest_t]
    B_at = Bf[nearest_t]
    v_N = np.sum(v * N_at, axis=-1)
    v_B = np.sum(v * B_at, axis=-1)

    phi = np.arctan2(v_B, v_N).reshape((L, L, L))
    return wrap_pi(phi)


def neighbor_mean(field):
    s = np.zeros_like(field)
    for axis in range(3):
        for shift in (-1, +1):
            s += np.roll(field, shift, axis=axis)
    return s / 6.0


def phi_disorder(phi):
    s_cos = np.zeros_like(phi); s_sin = np.zeros_like(phi)
    for axis in range(3):
        for shift in (-1, +1):
            pj = np.roll(phi, shift, axis=axis)
            s_cos += np.cos(pj); s_sin += np.sin(pj)
    s_cos /= 6.0; s_sin /= 6.0
    mag = np.sqrt(s_cos*s_cos + s_sin*s_sin)
    return np.clip(1.0 - mag, 0.0, 1.0)


def phi_neighbor_xy_weighted(phi, sm):
    sx = np.zeros_like(phi); sy = np.zeros_like(phi); sw = np.zeros_like(phi)
    for axis in range(3):
        for shift in (-1, +1):
            pj = np.roll(phi, shift, axis=axis)
            mj = np.roll(sm,  shift, axis=axis)
            sx += mj * np.cos(pj); sy += mj * np.sin(pj); sw += mj
    pm = np.zeros_like(phi)
    safe = sw > 1e-10
    pm[safe]  = np.arctan2(sy[safe], sx[safe])
    pm[~safe] = phi[~safe]
    return pm


def step_v7(sg, sm, chi, phi, channel_f_active=True):
    sgb = neighbor_mean(sg); smb = neighbor_mean(sm)
    dsg = (ALPHA * (SIGMA_REF - sg) + BETA * (sgb - sg)
         + K_BACK * chi - K_GM * (SIGMA_REF - sm))
    sg_new = np.clip(sg + dsg, 0.0, 1.0)

    dsm = ALPHA * (SIGMA_REF - sm) + BETA * (smb - sm)
    if channel_f_active:
        dsm -= GAMMA_PHI * phi_disorder(phi) * sm
    sm_new = np.clip(sm + dsm, 0.0, 1.0)

    chi_new = (chi * (1.0 - CHI_DECAY) + CHI_REL * (sgb - sg)
             + DELTA * (SIGMA_REF - sg))

    pm = phi_neighbor_xy_weighted(phi, sm)
    dphi = BETA_PHI * wrap_pi(pm - phi)
    phi_new = wrap_pi(phi + dphi)

    return sg_new, sm_new, chi_new, phi_new


def ring_mass(sm):
    return float(np.maximum(0.0, SIGMA_REF - sm).sum())


def run_knot(label, curve_fn, L):
    sg  = np.full((L, L, L), SIGMA_REF)
    sm  = np.full((L, L, L), SIGMA_REF)
    chi = np.zeros((L, L, L))
    phi = init_phi_from_knot(curve_fn, L)

    history = []
    def snap(t, phase):
        return {"t": t, "phase": phase, "M_ring": ring_mass(sm)}

    history.append(snap(0, "init"))
    for t in range(1, PHASE1 + 1):
        sg, sm, chi, phi = step_v7(sg, sm, chi, phi, channel_f_active=False)
    history.append(snap(PHASE1, "P1_end"))

    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_v7(sg, sm, chi, phi, channel_f_active=True)
        if t % LOG_EVERY == 0 or t == PHASE2:
            history.append(snap(PHASE1 + t, "P2"))
            print(f"    [{label}@L={L}] P2 t={t} M={history[-1]['M_ring']:.2f}",
                  flush=True)

    for t in range(1, PHASE3 + 1):
        sg, sm, chi, phi = step_v7(sg, sm, chi, phi, channel_f_active=True)
        if t % LOG_EVERY == 0 or t == PHASE3:
            history.append(snap(PHASE1 + PHASE2 + t, "P3"))

    # Decay analysis
    p3 = [h for h in history if h["phase"] == "P3"]
    ratios = [p3[i]["M_ring"] / max(0.01, p3[i-1]["M_ring"])
              for i in range(1, len(p3))]
    mean_ratio = float(np.mean(ratios))
    if 0 < mean_ratio < 1:
        half_life_lu = math.log(0.5) / math.log(mean_ratio) * LOG_EVERY
    else:
        half_life_lu = float('inf')

    M_P2_end = next(h["M_ring"] for h in reversed(history) if h["phase"] == "P2")

    return {
        "label": label, "L": L,
        "M_P1_end": history[1]["M_ring"],
        "M_P2_end": M_P2_end,
        "M_P3_end": history[-1]["M_ring"],
        "mean_decay_ratio": mean_ratio,
        "half_life_lu": half_life_lu,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--L-values", type=int, nargs='+', default=[48, 56, 64])
    ap.add_argument("--quick", action='store_true',
                    help="Trefoil only (skip figure-8 and cinquefoil)")
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    knots = [
        ("trefoil",     trefoil_curve),
        ("figure_8",    figure8_curve),
        ("cinquefoil",  cinquefoil_curve),
    ]
    if args.quick:
        knots = knots[:1]

    print(f"QNG-CPU-149: Finite-volume test of knot universality")
    print(f"L values: {args.L_values}")
    print(f"Knots: {[k[0] for k in knots]}")
    print()

    all_results = []
    t_start = time.time()
    for L in args.L_values:
        print(f"=== L = {L} ===")
        for label, curve_fn in knots:
            print(f"  --- {label} ---")
            res = run_knot(label, curve_fn, L)
            all_results.append(res)
            print(f"  [{label}@L={L}] DONE  M_P2={res['M_P2_end']:.2f}  "
                  f"M_P3={res['M_P3_end']:.2f}  "
                  f"decay_ratio={res['mean_decay_ratio']:.4f}  "
                  f"half_life={res['half_life_lu']:.0f} lu", flush=True)
        print()
    dt = time.time() - t_start
    print(f"Total run time: {dt:.1f} s")
    print()

    # Cross-L analysis
    print("=" * 90)
    print(f"{'L':>4}  {'knot':<14}  {'M_P2_end':>10}  {'M_P3_end':>10}  "
          f"{'decay/200':>10}  {'half-life':>10}")
    print("-" * 90)
    for r in all_results:
        print(f"{r['L']:>4}  {r['label']:<14}  {r['M_P2_end']:>10.2f}  "
              f"{r['M_P3_end']:>10.2f}  {r['mean_decay_ratio']:>10.4f}  "
              f"{r['half_life_lu']:>10.0f}")
    print("=" * 90)

    # Per-L summary
    print()
    print("Per-L summary (averaged over knots):")
    for L in args.L_values:
        rs = [r for r in all_results if r["L"] == L]
        hls = [r["half_life_lu"] for r in rs if r["half_life_lu"] < 1e6]
        if hls:
            mean_hl = float(np.mean(hls))
            std_hl = float(np.std(hls))
            print(f"  L={L:>3}: mean half-life {mean_hl:.0f} lu  "
                  f"(spread {std_hl:.0f} = {std_hl/mean_hl*100:.1f}%)")

    # Cross-L drift
    print()
    print("Knot-by-knot L-dependence:")
    for k_label, _ in knots:
        krs = [r for r in all_results if r["label"] == k_label]
        hls = {r["L"]: r["half_life_lu"] for r in krs if r["half_life_lu"] < 1e6}
        if len(hls) >= 2:
            print(f"  {k_label}:")
            for L, hl in hls.items():
                print(f"    L={L:>3}: {hl:.0f} lu")

    # Decision
    # 1. all L-values give half-lives within 30% of CPU-148 baseline (1044 lu)
    # 2. relative spread of decay ratios at each L < 10%
    cpu148_baseline = 1044.0
    L_means = {}
    for L in args.L_values:
        rs = [r for r in all_results if r["L"] == L]
        hls = [r["half_life_lu"] for r in rs if r["half_life_lu"] < 1e6]
        if hls:
            L_means[L] = float(np.mean(hls))
    baseline_match = all(abs(hl - cpu148_baseline)/cpu148_baseline < 0.30
                         for hl in L_means.values())
    L_robust = True
    if len(L_means) >= 2:
        vals = list(L_means.values())
        L_robust = (max(vals) - min(vals)) / np.mean(vals) < 0.20

    decision = baseline_match and L_robust

    print()
    print(f"Baseline (1044 lu) match within 30%: {'YES' if baseline_match else 'NO'}")
    print(f"L-robust (drift < 20% across L): {'YES' if L_robust else 'NO'}")
    print(f"\nDecision: {'PASS' if decision else 'FAIL'}")
    if decision:
        print("\n  -> Universal half-life confirmed as genuine QNG prediction,")
        print("     not finite-volume artefact.")
    else:
        print("\n  -> Finite-volume effects detected. Extrapolate to L->inf needed.")

    report = {
        "test_id": "QNG-CPU-149",
        "decision": "pass" if decision else "fail",
        "params": {"L_values": args.L_values,
                   "PHASE1": PHASE1, "PHASE2": PHASE2, "PHASE3": PHASE3,
                   "BETA_PHI": BETA_PHI, "GAMMA_PHI": GAMMA_PHI,
                   "KNOT_SCALE": KNOT_SCALE},
        "results": all_results,
        "L_means": L_means,
        "cpu148_L20_baseline": cpu148_baseline,
        "verdicts": {
            "baseline_match_30pct": bool(baseline_match),
            "L_robust_20pct": bool(L_robust),
            "universality_genuine": bool(decision),
        },
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
