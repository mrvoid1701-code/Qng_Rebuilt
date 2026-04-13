from __future__ import annotations

"""QNG-CPU-076: M_ring ratio stability under parameter variation.

Tests whether M_ring(R=4) / M_ring(R=5) = 0.7634 is a topological invariant
(stable across parameter space) or a kinematic coincidence tuned to default params.

Part A: 27-configuration parameter grid
  alpha_m in {0.003, 0.005, 0.008}
  beta_m  in {0.25,  0.35,  0.45 }
  gamma_phi in {0.07, 0.10, 0.14 }

Part B: T_P2 sensitivity at default params
  T_P2 in {500, 750, 1000, 1250, 1500}

Gates:
  Check 1: std(ratio_grid) / mean(ratio_grid) < 0.05  [topologically stable]
  Check 2: max(ratio_T_P2) - min(ratio_T_P2) < 0.030  [T_P2-invariant]
  Check 3: fraction of 27 configs with |ratio - 0.7616| < 0.020 >= 20/27

Prereg: 07_validation/prereg/QNG-CPU-076.md
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-mring-ratio-stability-v1"

# ---------------------------------------------------------------------------
# Fixed parameters (not varied)
# ---------------------------------------------------------------------------
L = 20
N = L * L * L

SIGMA_REF = 0.5
BETA_PHI  = 0.02
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
K_BACK    = 0.10   # not varied; part of sigma_g only (sigma_m sector independent)

# Default parameter values
DEFAULT_ALPHA = 0.005
DEFAULT_BETA  = 0.35
DEFAULT_GAMMA = 0.10

RX = RY = RZ = float(L // 2)
PHASE1 = 300
PHASE2 = 1500

# Part A grid
ALPHA_GRID = [0.003, 0.005, 0.008]
BETA_GRID  = [0.25,  0.35,  0.45]
GAMMA_GRID = [0.07,  0.10,  0.14]

# Part B T_P2 values
T_P2_GRID = [500, 750, 1000, 1250, 1500]

RADII = [4, 5]

# Reference ratio: M(R=4)/M(R=5) from CPU-074/075 at default params
RATIO_REF = 0.7634
RATIO_SM  = 0.7616   # m_N / m_Delta = 938.272 / 1232

# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def idx3(x, y, z):
    return (x % L) * L * L + (y % L) * L + (z % L)

def coord3(i):
    x = i // (L * L); y = (i % (L * L)) // L; z = i % L
    return x, y, z

def _mi(d):
    while d >  L / 2: d -= L
    while d < -L / 2: d += L
    return d

def wrap(a):
    a = a % (2 * math.pi)
    return a - 2 * math.pi if a > math.pi else a

def adiff(a, b):
    return wrap(a - b)

def clip01(x):
    return max(0.0, min(1.0, x))

def nb(x, y, z):
    return [idx3(x-1,y,z), idx3(x+1,y,z),
            idx3(x,y-1,z), idx3(x,y+1,z),
            idx3(x,y,z-1), idx3(x,y,z+1)]

NBS = [nb(*coord3(i)) for i in range(N)]

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init_phi(ring_r):
    p = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - RX); dy = _mi(y - RY); dz = _mi(z - RZ)
        rho = math.sqrt(dx * dx + dy * dy)
        p.append(math.atan2(dz, rho - ring_r))
    return p

def disorder(phi, i):
    nbs = NBS[i]
    sx = sum(math.cos(phi[j]) for j in nbs) / 6.0
    sy = sum(math.sin(phi[j]) for j in nbs) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx * sx + sy * sy))

# ---------------------------------------------------------------------------
# Step functions — parametrized by (alpha, beta, gamma_phi)
# ---------------------------------------------------------------------------

def step_phase1(sg, sm, chi, phi, alpha, beta):
    nsg = [0.0]*N; nsm = [0.0]*N; nc = [0.0]*N; np_ = [0.0]*N
    for i in range(N):
        nbs = NBS[i]
        s = sg[i]; m = sm[i]; c = chi[i]; p = phi[i]
        sgb = sum(sg[j] for j in nbs) / 6.0
        smb = sum(sm[j] for j in nbs) / 6.0
        nsg[i] = clip01(s + alpha*(SIGMA_REF-s) + beta*(sgb-s))
        nsm[i] = clip01(m + alpha*(SIGMA_REF-m) + beta*(smb-m))
        nc[i]  = c*(1-CHI_DECAY) + CHI_REL*(sgb-s) + DELTA*(SIGMA_REF-s)
        tw = sum(sm[j] for j in nbs)
        if tw > 1e-10:
            sx2 = sum(sm[j]*math.cos(phi[j]) for j in nbs) / tw
            sy2 = sum(sm[j]*math.sin(phi[j]) for j in nbs) / tw
            pm  = math.atan2(sy2, sx2)
        else:
            pm = p
        np_[i] = wrap(p + BETA_PHI * adiff(pm, p))
    return nsg, nsm, nc, np_


def step_phase2(sg, sm, chi, phi, alpha, beta, gamma_phi):
    nsg = [0.0]*N; nsm = [0.0]*N; nc = [0.0]*N; np_ = [0.0]*N
    for i in range(N):
        nbs = NBS[i]
        s = sg[i]; m = sm[i]; c = chi[i]; p = phi[i]
        sgb = sum(sg[j] for j in nbs) / 6.0
        smb = sum(sm[j] for j in nbs) / 6.0
        nsg[i] = clip01(s + alpha*(SIGMA_REF-s) + beta*(sgb-s))
        dsm = alpha*(SIGMA_REF-m) + beta*(smb-m) - gamma_phi*disorder(phi,i)*m
        nsm[i] = clip01(m + dsm)
        nc[i]  = c*(1-CHI_DECAY) + CHI_REL*(sgb-s) + DELTA*(SIGMA_REF-s)
        tw = sum(sm[j] for j in nbs)
        if tw > 1e-10:
            sx2 = sum(sm[j]*math.cos(phi[j]) for j in nbs) / tw
            sy2 = sum(sm[j]*math.sin(phi[j]) for j in nbs) / tw
            pm  = math.atan2(sy2, sx2)
        else:
            pm = p
        np_[i] = wrap(p + BETA_PHI * adiff(pm, p))
    return nsg, nsm, nc, np_

# ---------------------------------------------------------------------------
# Observable
# ---------------------------------------------------------------------------

def ring_mass(sm):
    return sum(max(0.0, SIGMA_REF - sm[i]) for i in range(N))

# ---------------------------------------------------------------------------
# Run one (radius, params, t_p2_snapshot) configuration
# ---------------------------------------------------------------------------

def run_one(ring_r, alpha, beta, gamma_phi, t_p2_snap=1000):
    """Returns M_ring at t_p2_snap."""
    sg  = [SIGMA_REF] * N
    sm  = [SIGMA_REF] * N
    chi = [0.0] * N
    phi = init_phi(ring_r)

    for _ in range(PHASE1):
        sg, sm, chi, phi = step_phase1(sg, sm, chi, phi, alpha, beta)

    M_snap = None
    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_phase2(sg, sm, chi, phi, alpha, beta, gamma_phi)
        if t == t_p2_snap:
            M_snap = ring_mass(sm)
            break

    if M_snap is None:
        # t_p2_snap > PHASE2 — run to end and use final
        M_snap = ring_mass(sm)

    return M_snap

# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def mean(vals):
    return sum(vals) / len(vals)

def std(vals):
    m = mean(vals)
    return math.sqrt(sum((v - m)**2 for v in vals) / len(vals))

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--skip-part-b", action="store_true",
                    help="Skip Part B (T_P2 sensitivity) to save time")
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("QNG-CPU-076: M_ring ratio stability test")
    print(f"L={L}, PHASE1={PHASE1}, PHASE2={PHASE2}")
    print(f"Reference ratio (CPU-074/075): {RATIO_REF:.4f}")
    print(f"SM target (m_N/m_d): {RATIO_SM:.4f}")
    print()

    # -----------------------------------------------------------------------
    # PART A: 27-configuration parameter grid
    # -----------------------------------------------------------------------
    print("=" * 60)
    print("PART A: Parameter grid (27 configurations)")
    print("=" * 60)

    configs = [
        (a, b, g)
        for a in ALPHA_GRID
        for b in BETA_GRID
        for g in GAMMA_GRID
    ]
    assert len(configs) == 27

    grid_results = []
    total = len(configs) * len(RADII)
    done = 0

    for cfg_idx, (alpha, beta, gamma) in enumerate(configs):
        M_r = {}
        for r in RADII:
            done += 1
            print(f"  [{done:3d}/{total}] cfg={cfg_idx+1:2d}  "
                  f"alpha={alpha:.3f}  beta={beta:.2f}  gamma={gamma:.2f}  R={r}  ...",
                  end="", flush=True)
            M_r[r] = run_one(r, alpha, beta, gamma, t_p2_snap=1000)
            print(f"  M={M_r[r]:.2f}")

        ratio = M_r[4] / M_r[5] if M_r[5] > 0 else float("nan")
        is_default = (alpha == DEFAULT_ALPHA and beta == DEFAULT_BETA and gamma == DEFAULT_GAMMA)
        grid_results.append({
            "cfg": cfg_idx + 1,
            "alpha": alpha,
            "beta": beta,
            "gamma_phi": gamma,
            "M_R4": round(M_r[4], 2),
            "M_R5": round(M_r[5], 2),
            "ratio": round(ratio, 4),
            "is_default": is_default,
        })
        tag = " <-- DEFAULT" if is_default else ""
        print(f"  >> ratio M(R=4)/M(R=5) = {ratio:.4f}{tag}")

    ratios_grid = [r["ratio"] for r in grid_results]
    ratio_mean  = mean(ratios_grid)
    ratio_std   = std(ratios_grid)
    ratio_cv    = ratio_std / ratio_mean   # coefficient of variation

    n_near_sm   = sum(1 for r in ratios_grid if abs(r - RATIO_SM) < 0.020)
    frac_near_sm = n_near_sm / 27

    check1 = ratio_cv < 0.05
    check3 = n_near_sm >= 20   # >= 20/27

    print()
    print("Part A summary:")
    print(f"  ratio mean = {ratio_mean:.4f}")
    print(f"  ratio std  = {ratio_std:.4f}")
    print(f"  CV (std/mean) = {ratio_cv:.4f}  [gate < 0.05]")
    print(f"  configs with |ratio - {RATIO_SM:.4f}| < 0.020: {n_near_sm}/27  [gate >= 20]")
    print(f"  Check 1 (topological stability CV<5%): {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 3 (N/d match broad): {'PASS' if check3 else 'FAIL'}")

    # -----------------------------------------------------------------------
    # PART B: T_P2 sensitivity (default params only)
    # -----------------------------------------------------------------------
    check2 = None
    tp2_results = []

    if not args.skip_part_b:
        print()
        print("=" * 60)
        print("PART B: T_P2 sensitivity (default params)")
        print("=" * 60)

        total_b = len(T_P2_GRID) * len(RADII)
        done_b = 0

        for tp2 in T_P2_GRID:
            M_r = {}
            for r in RADII:
                done_b += 1
                print(f"  [{done_b:2d}/{total_b}] T_P2={tp2}  R={r}  ...",
                      end="", flush=True)
                M_r[r] = run_one(r, DEFAULT_ALPHA, DEFAULT_BETA, DEFAULT_GAMMA,
                                 t_p2_snap=tp2)
                print(f"  M={M_r[r]:.2f}")
            ratio = M_r[4] / M_r[5] if M_r[5] > 0 else float("nan")
            tp2_results.append({"T_P2": tp2, "M_R4": round(M_r[4], 2),
                                 "M_R5": round(M_r[5], 2), "ratio": round(ratio, 4)})
            print(f"  >> T_P2={tp2}  ratio = {ratio:.4f}")

        ratios_tp2 = [r["ratio"] for r in tp2_results]
        tp2_range = max(ratios_tp2) - min(ratios_tp2)
        in_gate   = all(0.74 <= r <= 0.79 for r in ratios_tp2)

        check2 = (tp2_range < 0.030) and in_gate

        print()
        print("Part B summary:")
        print(f"  T_P2 ratio range: max-min = {tp2_range:.4f}  [gate < 0.030]")
        print(f"  All ratios in [0.74, 0.79]: {in_gate}")
        print(f"  Check 2 (T_P2-invariant): {'PASS' if check2 else 'FAIL'}")

    # -----------------------------------------------------------------------
    # Decision
    # -----------------------------------------------------------------------
    print()
    print("=" * 60)
    print("DECISION")
    print("=" * 60)

    if check2 is not None:
        if check1 and check2:
            decision = "pass_topological"
            label    = "PASS (topological): ratio is a topological invariant"
        elif check3 and check2:
            decision = "pass_conditional"
            label    = "PASS (conditional): ratio is parameter-sensitive but N/d match holds broadly"
        elif not check1 and not check3:
            decision = "fail"
            label    = "FAIL: ratio is tuned to default parameters"
        else:
            decision = "fail"
            label    = "FAIL: mixed result — requires manual review"
    else:
        # Part B skipped
        if check1:
            decision = "pass_partial"
            label    = "PASS (partial, Part B skipped): Part A topologically stable"
        elif check3:
            decision = "pass_conditional_partial"
            label    = "PASS (conditional, Part B skipped): N/d match holds broadly"
        else:
            decision = "fail"
            label    = "FAIL: ratio tuned to default params"

    overall_pass = decision.startswith("pass")

    print(f"  Check 1 (CV < 5%):          {'PASS' if check1 else 'FAIL'}  (CV={ratio_cv:.4f})")
    if check2 is not None:
        print(f"  Check 2 (T_P2 range <3%):   {'PASS' if check2 else 'FAIL'}")
    else:
        print(f"  Check 2 (T_P2 range <3%):   SKIPPED")
    print(f"  Check 3 (N/d match >=20/27): {'PASS' if check3 else 'FAIL'}  ({n_near_sm}/27)")
    print()
    print(f"  {label}")
    print(f"  qng_mring_ratio_stability_reference: {'PASS' if overall_pass else 'FAIL'}")

    # -----------------------------------------------------------------------
    # Save artifacts
    # -----------------------------------------------------------------------
    report = {
        "test_id": "QNG-CPU-076",
        "decision": decision,
        "reference_ratio": RATIO_REF,
        "sm_target": RATIO_SM,
        "part_a": {
            "n_configs": 27,
            "ratio_mean": round(ratio_mean, 4),
            "ratio_std":  round(ratio_std, 4),
            "ratio_cv":   round(ratio_cv, 4),
            "n_near_sm":  n_near_sm,
            "frac_near_sm": round(frac_near_sm, 3),
            "check1_cv_lt_5pct": check1,
            "check3_nd_match_broad": check3,
            "configs": grid_results,
        },
        "part_b": {
            "skipped": (check2 is None),
            "tp2_results": tp2_results,
            "check2_tp2_invariant": check2,
        },
    }

    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)

    # summary.md
    lines = [
        "# QNG-CPU-076 M_ring Ratio Stability",
        f"- decision: `{decision}`",
        f"- overall: `{'PASS' if overall_pass else 'FAIL'}`",
        "",
        "## Part A: Parameter grid (27 configs)",
        f"- ratio mean: {ratio_mean:.4f}",
        f"- ratio std:  {ratio_std:.4f}",
        f"- CV (std/mean): {ratio_cv:.4f}  (gate <0.05)",
        f"- configs with |ratio - {RATIO_SM:.4f}| < 0.020: {n_near_sm}/27  (gate >=20)",
        f"- Check 1 (topological stability): {'PASS' if check1 else 'FAIL'}",
        f"- Check 3 (N/d match broad):       {'PASS' if check3 else 'FAIL'}",
        "",
        "| cfg | alpha | beta | gamma | M(R=4) | M(R=5) | ratio |",
        "|-----|-------|------|-------|--------|--------|-------|",
    ]
    for r in grid_results:
        def_tag = " *" if r["is_default"] else ""
        lines.append(
            f"| {r['cfg']:2d} | {r['alpha']:.3f} | {r['beta']:.2f} | {r['gamma_phi']:.2f}"
            f" | {r['M_R4']:.1f} | {r['M_R5']:.1f} | {r['ratio']:.4f}{def_tag} |"
        )
    lines += [
        "",
        "## Part B: T_P2 sensitivity (default params)",
    ]
    if tp2_results:
        lines += [
            "| T_P2 | M(R=4) | M(R=5) | ratio |",
            "|------|--------|--------|-------|",
        ]
        for r in tp2_results:
            lines.append(f"| {r['T_P2']} | {r['M_R4']:.1f} | {r['M_R5']:.1f} | {r['ratio']:.4f} |")
        lines.append(f"- Check 2 (T_P2-invariant): {'PASS' if check2 else 'FAIL'}")
    else:
        lines.append("- (skipped)")
    lines += [
        "",
        "## Interpretation",
        f"- {label}",
    ]

    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
