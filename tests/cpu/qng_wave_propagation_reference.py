from __future__ import annotations

"""
QNG-CPU-052: v6 wave propagation speed test.

Channel G (k_back * chi_i) added to sigma update.
Measures wavefront propagation speed from a central Gaussian perturbation.
Checks v_measured ~ sqrt(beta) = 0.5916 (DER-QNG-030 prediction).
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-wave-propagation-v1"

L: int = 32
N: int = L * L * L

SIGMA_REF: float = 0.5
ALPHA:     float = 0.005
BETA:      float = 0.35
DELTA:     float = 0.20
CHI_DECAY: float = 0.005
CHI_REL:   float = 0.35

# No phi coupling (vacuum test — no vortex rings)
BETA_PHI:  float = 0.0
GAMMA_PHI: float = 0.0
EPSILON:   float = 0.0

# Gaussian perturbation
A_PERTURB: float = 0.05
W_PERTURB: float = 2.0

# Predicted wave speed from DER-QNG-030
V_PRED: float = math.sqrt(BETA)   # = 0.5916

# k_back values to scan
K_BACKS = [0.01, 0.05, 0.10]

MAX_STEPS: int = 80
THRESHOLD: float = A_PERTURB / 10.0   # 0.005

# Physical constants for C3 evaluation
C_LIGHT_MS: float = 2.998e8          # m/s
M_PROTON_KG: float = 1.673e-27       # kg
L_PLANCK_M: float = 1.616e-35        # m
G_QNG: float = BETA / 6.0            # = 0.05833 (substrate units)
G_NEWTON: float = 6.674e-11          # m^3 kg^-1 s^-2


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def idx3(x: int, y: int, z: int) -> int:
    return (x % L) * L * L + (y % L) * L + (z % L)

def coord3(i: int) -> tuple[int, int, int]:
    x = i // (L * L); y = (i % (L * L)) // L; z = i % L
    return x, y, z

def dist_center(i: int) -> float:
    x, y, z = coord3(i)
    cx = cy = cz = L / 2.0
    dx = x - cx; dy = y - cy; dz = z - cz
    # no periodic wrapping needed — perturbation stays near center within MAX_STEPS
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

def init_gaussian() -> list[float]:
    sigma = []
    for i in range(N):
        r = dist_center(i)
        sigma.append(SIGMA_REF + A_PERTURB * math.exp(-r*r / (2*W_PERTURB**2)))
    return sigma


# ---------------------------------------------------------------------------
# Update (v6 — vacuum only: no phi disorder, Channel G active)
# ---------------------------------------------------------------------------

def update_step_v6(sigma: list[float], chi: list[float],
                   k_back: float) -> tuple[list[float], list[float]]:
    ns, nc = [], []
    for i in range(N):
        x, y, z = coord3(i)
        nb = [idx3(x-1,y,z), idx3(x+1,y,z), idx3(x,y-1,z),
              idx3(x,y+1,z), idx3(x,y,z-1), idx3(x,y,z+1)]
        sb = sum(sigma[j] for j in nb) / 6.0

        # Sigma: Channels A + B + D + G (no F or E in vacuum)
        s = clip01(
            sigma[i]
            + ALPHA * (SIGMA_REF - sigma[i])        # A
            + BETA  * (sb - sigma[i])               # B
            - DELTA * (SIGMA_REF - sigma[i])        # D (v3 cross-coupling)
            + k_back * chi[i]                       # G (v6 new)
        )

        # Chi: unchanged from v5
        c = chi[i]*(1-CHI_DECAY) + CHI_REL*(sb - sigma[i]) + DELTA*(SIGMA_REF - sigma[i])

        ns.append(s); nc.append(c)
    return ns, nc


# ---------------------------------------------------------------------------
# Radial profile — measure sigma(r) averaged in spherical shells
# ---------------------------------------------------------------------------

def radial_profile(sigma: list[float],
                   r_max: int = L // 2,
                   dr: float = 1.0) -> list[tuple[float, float]]:
    """Returns list of (r_mid, mean_sigma_dev) for shells r in [0, r_max]."""
    shells: dict[int, list[float]] = {}
    for i in range(N):
        r = dist_center(i)
        bin_idx = int(r / dr)
        if bin_idx <= r_max:
            shells.setdefault(bin_idx, []).append(sigma[i] - SIGMA_REF)
    result = []
    for b in sorted(shells):
        r_mid = (b + 0.5) * dr
        vals = shells[b]
        mean_dev = sum(vals) / len(vals)
        result.append((r_mid, mean_dev))
    return result


def wavefront_radius(profile: list[tuple[float, float]],
                     threshold: float = THRESHOLD) -> float:
    """Largest r where |sigma_dev| > threshold."""
    r_front = 0.0
    for r, dev in profile:
        if abs(dev) > threshold:
            r_front = r
    return r_front


# ---------------------------------------------------------------------------
# Run one k_back scenario
# ---------------------------------------------------------------------------

def run_kback(k_back: float) -> dict:
    sigma = init_gaussian()
    chi   = [0.0] * N

    trajectory = []  # (t, r_front)

    for t in range(1, MAX_STEPS + 1):
        sigma, chi = update_step_v6(sigma, chi, k_back)
        if t % 5 == 0:
            profile = radial_profile(sigma)
            r_front = wavefront_radius(profile)
            trajectory.append({"t": t, "r_front": round(r_front, 3)})

    # Fit linear v = r/t on points where r_front > W_PERTURB (past init width)
    pts = [(p["t"], p["r_front"]) for p in trajectory if p["r_front"] > W_PERTURB + 1]
    if len(pts) >= 3:
        n = len(pts)
        ts = [p[0] for p in pts]; rs = [p[1] for p in pts]
        tm = sum(ts)/n; rm = sum(rs)/n
        num = sum((t-tm)*(r-rm) for t,r in zip(ts,rs))
        den = sum((t-tm)**2 for t in ts)
        v_meas = num/den if den > 1e-10 else 0.0
        r0 = rm - v_meas * tm
    else:
        v_meas = 0.0; r0 = 0.0

    r_at_50 = next((p["r_front"] for p in trajectory if p["t"] >= 50), 0.0)

    return {
        "k_back":    k_back,
        "v_measured": round(v_meas, 4),
        "v_pred":     round(V_PRED, 4),
        "r_at_T50":   r_at_50,
        "trajectory": trajectory,
        "fit_n_pts":  len(pts),
    }


# ---------------------------------------------------------------------------
# Physical unit evaluation (C3 + C1)
# ---------------------------------------------------------------------------

def physical_units(v_measured: float) -> dict:
    """Given substrate wave speed, compute tau/a and a (for m_node = m_proton)."""
    if v_measured <= 0:
        return {}
    # C3: tau/a = v_measured / c
    tau_over_a = v_measured / C_LIGHT_MS   # s/m
    # C1: m_u * tau^2 = G_QNG * a^3 / G_Newton
    #     m_u * (tau_over_a * a)^2 = G_QNG * a^3 / G_Newton
    #     m_u * tau_over_a^2 * a^2 = G_QNG * a^3 / G_Newton
    #     m_u = G_QNG * a / (G_Newton * tau_over_a^2)
    # For m_u = m_proton: a = m_proton * G_Newton * tau_over_a^2 / G_QNG
    a_proton = M_PROTON_KG * G_NEWTON * tau_over_a**2 / G_QNG   # meters
    a_planck_units = a_proton / L_PLANCK_M
    tau_proton = tau_over_a * a_proton   # seconds
    return {
        "tau_over_a_s_per_m": tau_over_a,
        "a_proton_m":         a_proton,
        "a_in_l_planck":      round(a_planck_units, 3),
        "tau_proton_s":       tau_proton,
        "lambda_phys_m":      round(3.41 * a_proton, 6),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    print(f"L={L}, N={N}  vacuum wave test (v6, Channel G)")
    print(f"A_perturb={A_PERTURB}  w={W_PERTURB}  threshold={THRESHOLD}")
    print(f"Predicted v = sqrt(beta) = {V_PRED:.4f} lattice/step")
    print(f"k_back values: {K_BACKS}")
    print()

    results = {}
    for kb in K_BACKS:
        print(f"=== k_back={kb} ===")
        r = run_kback(kb)
        results[kb] = r
        print(f"  v_measured={r['v_measured']:.4f}  v_pred={r['v_pred']:.4f}  "
              f"r@T50={r['r_at_T50']:.2f}")
        # print first few trajectory points
        for p in r["trajectory"][:4]:
            print(f"    T={p['t']:3d}: r_front={p['r_front']:.2f}")
        print()

    # --- Checks ---
    best_v = max(r["v_measured"] for r in results.values())
    r_at50_any = max(r["r_at_T50"] for r in results.values())

    check1 = r_at50_any > 8.0

    v_mid = results[K_BACKS[1]]["v_measured"]   # k_back=0.05
    check2 = (v_mid > 0 and abs(v_mid - V_PRED) / V_PRED < 0.20)

    v_lo = results[K_BACKS[0]]["v_measured"]
    v_hi = results[K_BACKS[-1]]["v_measured"]
    check3 = abs(v_lo - v_hi) < 0.15

    phys = physical_units(v_mid if v_mid > 0 else best_v)

    decision = check1 and check2

    print("=" * 60)
    print(f"{'k_back':>8}  {'v_meas':>8}  {'v_pred':>8}  {'rel_err':>8}  {'r@T50':>8}")
    for kb in K_BACKS:
        r = results[kb]
        rel_err = abs(r['v_measured'] - V_PRED) / V_PRED if r['v_measured'] > 0 else 999
        print(f"  {kb:>6}  {r['v_measured']:>8.4f}  {r['v_pred']:>8.4f}  "
              f"{rel_err:>8.3f}  {r['r_at_T50']:>8.2f}")
    print()
    if phys:
        print("Physical units (C3 + C1, m_node = m_proton):")
        print(f"  tau/a = {phys['tau_over_a_s_per_m']:.3e} s/m")
        print(f"  a     = {phys['a_proton_m']:.3e} m  = {phys['a_in_l_planck']:.1f} l_Planck")
        print(f"  tau   = {phys['tau_proton_s']:.3e} s")
        print(f"  lambda_phys = {phys['lambda_phys_m']:.3e} m")
    print()
    print("Checks:")
    print(f"  Check 1 (wave propagates r>8 at T=50): {'PASS' if check1 else 'FAIL'}  r={r_at50_any:.2f}")
    print(f"  Check 2 (v_meas within 20% of sqrt(beta)): {'PASS' if check2 else 'FAIL'}  v={v_mid:.4f}")
    print(f"  Check 3 (speed indep of k_back): {'PASS' if check3 else 'FAIL'}  dv={abs(v_lo-v_hi):.4f}")
    print(f"  Check 4 [info] a = {phys.get('a_in_l_planck','?')} l_Planck (m_node=m_proton)")
    print(f"\nqng_wave_propagation_reference: {'PASS' if decision else 'FAIL'}")

    report = {
        "test_id": "QNG-CPU-052",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "L": L, "N": N, "A_perturb": A_PERTURB, "w": W_PERTURB,
            "threshold": THRESHOLD, "beta": BETA, "alpha": ALPHA,
            "chi_rel": CHI_REL, "delta": DELTA, "chi_decay": CHI_DECAY,
            "k_backs": K_BACKS, "max_steps": MAX_STEPS,
        },
        "v_pred": V_PRED,
        "results": {
            str(kb): {
                "v_measured": results[kb]["v_measured"],
                "r_at_T50":   results[kb]["r_at_T50"],
                "fit_n_pts":  results[kb]["fit_n_pts"],
            } for kb in K_BACKS
        },
        "physical_units": phys,
        "checks": {
            "wave_propagates_pass":    check1,
            "speed_correct_pass":      check2,
            "speed_kback_indep_pass":  check3,
        },
        "trajectories": {str(kb): results[kb]["trajectory"] for kb in K_BACKS},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-CPU-052: v6 Wave Propagation Speed",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- v_pred = sqrt(beta) = {V_PRED:.4f}",
        "",
        "## Speed Results",
        "| k_back | v_measured | v_pred | rel_err | r@T50 |",
        "|--------|------------|--------|---------|-------|",
    ] + [
        f"| {kb} | {results[kb]['v_measured']} | {V_PRED:.4f} | "
        f"{abs(results[kb]['v_measured']-V_PRED)/V_PRED:.3f} | {results[kb]['r_at_T50']} |"
        for kb in K_BACKS
    ] + [
        "",
        "## Physical Units (m_node = m_proton)",
    ] + ([
        f"- tau/a = {phys['tau_over_a_s_per_m']:.3e} s/m",
        f"- a = {phys['a_proton_m']:.3e} m = {phys['a_in_l_planck']:.1f} l_Planck",
        f"- lambda_phys = {phys['lambda_phys_m']:.3e} m",
    ] if phys else ["- physical units not computed (v_measured=0)"]) + [
        "",
        "## Checks",
        f"- Check 1 (propagates): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (speed correct): {'PASS' if check2 else 'FAIL'}",
        f"- Check 3 (k_back independent): {'PASS' if check3 else 'FAIL'}",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
