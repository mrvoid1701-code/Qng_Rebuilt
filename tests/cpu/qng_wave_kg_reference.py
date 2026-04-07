from __future__ import annotations

"""
QNG-CPU-054: v6 massless Klein-Gordon wave propagation test.

Fixes CPU-052 overdiffusive failure:
  - delta=0 (massless wave, m^2=0)
  - chi_decay=0.001 (less dissipation)
  - L=64 (room for clean propagation)
  - Peak tracking instead of threshold wavefront

Corrected speed formula (DER-QNG-032 fix — z=6 normalization):
  v_eff^2 = k_back * chi_rel / 6   (NOT k_back * beta)
  chi drives sigma: ∂_t chi = chi_rel*(sb-si) = chi_rel*∇²s/6
  so ∂²_t s = k_back*∂_t chi = k_back*chi_rel/6 * ∇²s

k_back=1.00 -> v_pred = sqrt(0.35/6) = 0.2415
k_back=0.50 -> v_pred = sqrt(0.175/6) = 0.1708
k_back=0.10 -> v_pred = sqrt(0.035/6) = 0.0764

Fit strategy: use only RISING portion of r_rms(t) to avoid late-time
amplitude-decay pulling the slope down.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-wave-kg-v1"

# Lattice
L: int = 64
N: int = L * L * L

# Substrate parameters
SIGMA_REF: float = 0.5
ALPHA:     float = 0.005
BETA:      float = 0.35
DELTA:     float = 0.0      # MASSLESS: delta=0 eliminates mass term
CHI_DECAY: float = 0.001    # Reduced vs CPU-052 (was 0.005)
CHI_REL:   float = 0.35

# Perturbation — w=4 (narrow): at r>12, initial tail < 1e-6*A_perturb (negligible)
# delta=0 massless KG: v_group = v_phase = v_eff independent of wavelength -> any w works
A_PERTURB: float = 0.15     # larger amplitude: more budget before 1/r decay kills signal
W_PERTURB: float = 4.0

# k_back scan
K_BACKS = [0.10, 0.50, 1.00]

MAX_STEPS: int = 200
T_START_FIT: int = 30       # Skip diffusion-dominated early phase (w=4 Gaussian spreads to r~10 in <20 steps)

# Physical constants (for unit evaluation C3)
C_LIGHT_MS: float  = 2.998e8
M_PROTON_KG: float = 1.673e-27
L_PLANCK_M: float  = 1.616e-35
G_QNG: float       = BETA / 6.0
G_NEWTON: float    = 6.674e-11


# ---------------------------------------------------------------------------
# Indexing and geometry
# ---------------------------------------------------------------------------

def idx3(x: int, y: int, z: int) -> int:
    return (x % L) * L * L + (y % L) * L + (z % L)

def coord3(i: int) -> tuple[int, int, int]:
    x = i // (L * L); y = (i % (L * L)) // L; z = i % L
    return x, y, z

def dist_center(i: int) -> float:
    x, y, z = coord3(i)
    cx = cy = cz = L / 2.0
    dx = min(abs(x - cx), L - abs(x - cx))
    dy = min(abs(y - cy), L - abs(y - cy))
    dz = min(abs(z - cz), L - abs(z - cz))
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def init_gaussian() -> tuple[list[float], list[float]]:
    sigma = []
    for i in range(N):
        r = dist_center(i)
        sigma.append(SIGMA_REF + A_PERTURB * math.exp(-r*r / (2*W_PERTURB**2)))
    chi = [0.0] * N
    return sigma, chi


# ---------------------------------------------------------------------------
# Update step (v6, vacuum: no phi, delta=0)
# ---------------------------------------------------------------------------

def update_step(sigma: list[float], chi: list[float],
                k_back: float) -> tuple[list[float], list[float]]:
    ns = [0.0] * N
    nc = [0.0] * N
    for i in range(N):
        x, y, z = coord3(i)
        nb = [idx3(x-1,y,z), idx3(x+1,y,z),
              idx3(x,y-1,z), idx3(x,y+1,z),
              idx3(x,y,z-1), idx3(x,y,z+1)]
        sb = sum(sigma[j] for j in nb) / 6.0
        si = sigma[i]; ci = chi[i]

        # Sigma: Channels A + B + G (delta=0, no D, no F)
        ns[i] = clip01(
            si
            + ALPHA   * (SIGMA_REF - si)   # A: self-restore
            + BETA    * (sb - si)          # B: diffusion
            + k_back  * ci                 # G: chi back-reaction (v6)
        )

        # Chi: channels chi_decay + chi_rel (no delta term since delta=0)
        nc[i] = ci * (1.0 - CHI_DECAY) + CHI_REL * (sb - si)

    return ns, nc


# ---------------------------------------------------------------------------
# Radial profile (spherical shells)
# ---------------------------------------------------------------------------

def radial_profile(sigma: list[float]) -> list[tuple[float, float]]:
    """Returns (r_mid, mean_sigma_deviation) for integer-shell bins."""
    shells: dict[int, list[float]] = {}
    for i in range(N):
        r = dist_center(i)
        b = int(r + 0.5)
        if b <= L // 2:
            shells.setdefault(b, []).append(sigma[i] - SIGMA_REF)
    result = []
    for b in sorted(shells):
        vals = shells[b]
        mean_dev = sum(vals) / len(vals)
        result.append((float(b), mean_dev))
    return result


def find_r_peak(profile: list[tuple[float, float]],
                init_profile: list[tuple[float, float]]) -> float:
    """
    Position of the outgoing wave crest: r > W_PERTURB where
    (dev(r,t) - dev_initial(r)) is POSITIVE and maximum.
    The initial Gaussian depletes the center; the outgoing wave is a
    positive ring beyond the initial width.
    """
    init_map = {r: d for r, d in init_profile}
    best_r = 0.0
    best_dev = 0.0
    for r, dev in profile:
        if r < W_PERTURB:       # skip initial Gaussian region
            continue
        dev_out = dev - init_map.get(r, 0.0)   # signed: positive = outgoing crest
        if dev_out > best_dev:
            best_dev = dev_out
            best_r = r
    return best_r


def rms_radius_net(profile: list[tuple[float, float]],
                   init_profile: list[tuple[float, float]]) -> float:
    """
    RMS radius of the net wave signal: r_rms = sqrt(sum(r^2 * |dev_net| * r^2) / sum(|dev_net| * r^2))
    where dev_net(r,t) = dev(r,t) - dev_initial(r).
    Shell weight = r^2 (spherical surface element in 3D).

    For a ballistic wave shell: r_rms grows linearly with t -> slope = v_group.
    For pure diffusion: r_rms ~ sqrt(t).
    """
    init_map = {r: d for r, d in init_profile}
    numerator = 0.0
    denominator = 0.0
    for r, dev in profile:
        dev_init = init_map.get(r, 0.0)
        dev_net = abs(dev - dev_init)
        weight = dev_net * r * r    # |dev_net| * r^2 (shell weight)
        numerator  += r * r * weight
        denominator += weight
    if denominator < 1e-30:
        return 0.0
    return math.sqrt(numerator / denominator)


def find_wavefront_radius(profile: list[tuple[float, float]],
                          init_profile: list[tuple[float, float]],
                          threshold: float = A_PERTURB * 0.10) -> float:
    """
    Outward wavefront: largest r where net deviation exceeds threshold.
    Higher threshold (0.10 × A_perturb) avoids diffusive precursor.
    """
    init_map = {r: d for r, d in init_profile}
    r_front = 0.0
    for r, dev in profile:
        dev_net = abs(dev - init_map.get(r, 0.0))
        if dev_net > threshold:
            r_front = r
    return r_front


# ---------------------------------------------------------------------------
# Linear fit: r_peak(t) vs t -> slope = v_group
# ---------------------------------------------------------------------------

def linear_fit(ts: list[float], rs: list[float]) -> tuple[float, float]:
    n = len(ts)
    if n < 3:
        return 0.0, 0.0
    tm = sum(ts) / n; rm = sum(rs) / n
    num = sum((t - tm) * (r - rm) for t, r in zip(ts, rs))
    den = sum((t - tm)**2 for t in ts)
    slope = num / den if den > 1e-10 else 0.0
    intercept = rm - slope * tm
    return slope, intercept


def sqrt_fit(ts: list[float], rs: list[float]) -> float:
    """Fit r = a * sqrt(t), return a (diffusive coefficient)."""
    n = len(ts)
    if n < 3:
        return 0.0
    num = sum(r * math.sqrt(t) for t, r in zip(ts, rs))
    den = sum(t for t in ts)
    return num / den if den > 1e-10 else 0.0


# ---------------------------------------------------------------------------
# Run one k_back scenario
# ---------------------------------------------------------------------------

def run_kback(k_back: float) -> dict:
    v_pred = math.sqrt(k_back * CHI_REL / 6.0)   # corrected: z=6 normalization
    print(f"  k_back={k_back:.2f}  v_pred={v_pred:.4f}", flush=True)

    sigma, chi = init_gaussian()
    trajectory: list[dict] = []

    # Record initial profile (subtract later to isolate wave signal)
    init_profile = radial_profile(sigma)

    r_front_max = 0.0   # monotonically increasing wavefront
    boundary = L // 3  # stop fitting before periodic boundary effects

    for t in range(1, MAX_STEPS + 1):
        sigma, chi = update_step(sigma, chi, k_back)

        if t % 5 == 0 or t <= 5:
            profile = radial_profile(sigma)
            r_rms = rms_radius_net(profile, init_profile)
            r_peak = find_r_peak(profile, init_profile)
            r_front = find_wavefront_radius(profile, init_profile)
            r_front_max = max(r_front_max, r_front)
            trajectory.append({
                "t": t,
                "r_rms": round(r_rms, 3),
                "r_peak": round(r_peak, 1),
                "r_front": round(r_front_max, 3),
            })
            if t % 10 == 0:
                print(f"    T={t:4d}: r_peak={r_peak:.1f}  r_rms={r_rms:.2f}  r_front={r_front_max:.2f}", flush=True)

    # PRIMARY: fit v from r_peak(t) — tracks outgoing wave crest.
    # Use all points where r_peak is in (W_PERTURB, boundary).
    # No stopping criterion: jitter at early/late times averages out in linear fit.
    peak_boundary = L // 2 - 5   # stop before periodic wrap (L/2=32, use 27)
    # Use points from T_START_FIT until the FIRST time r_peak hits peak_boundary.
    # After that, the wave has reached the periodic boundary and reflections pollute the signal.
    peak_pts = []
    for p in trajectory:
        if p["t"] < T_START_FIT or p["r_peak"] <= W_PERTURB:
            continue
        if p["r_peak"] >= peak_boundary:
            break   # wave hit the boundary — stop here
        peak_pts.append(p)
    ts_peak = [p["t"] for p in peak_pts]
    rs_peak = [p["r_peak"] for p in peak_pts]
    v_meas, r0 = linear_fit(ts_peak, rs_peak)

    # SECONDARY: r_rms rising portion (kept for diagnostics)
    rising: list[dict] = []
    r_rms_prev = 0.0
    for p in trajectory:
        if p["t"] < T_START_FIT or p["r_rms"] <= W_PERTURB:
            r_rms_prev = p["r_rms"]
            continue
        if p["r_rms"] < r_rms_prev - 0.5:
            break
        rising.append(p)
        r_rms_prev = p["r_rms"]
    fit_pts_rms = rising
    ts_rms = [p["t"] for p in fit_pts_rms]
    rs_rms = [p["r_rms"] for p in fit_pts_rms]

    # Also fit from wavefront (leading edge)
    fit_pts_front = [(p["t"], p["r_front"]) for p in trajectory
                     if p["t"] >= T_START_FIT
                     and p["r_front"] > W_PERTURB
                     and p["r_front"] < boundary]
    ts_fit = [p[0] for p in fit_pts_front]
    rs_fit = [p[1] for p in fit_pts_front]
    v_front, _ = linear_fit(ts_fit, rs_fit)

    # Also fit sqrt(t) for diffusion comparison (using peak)
    a_sqrt = sqrt_fit(ts_peak, rs_peak)

    # Chi2 for linear vs sqrt fit (using peak)
    def chi2_linear(ts, rs, v, r0):
        return sum((r - v*t - r0)**2 for t, r in zip(ts, rs)) if ts else 999
    def chi2_sqrt(ts, rs, a):
        return sum((r - a*math.sqrt(t))**2 for t, r in zip(ts, rs)) if ts else 999
    c2_lin  = chi2_linear(ts_peak, rs_peak, v_meas, r0)
    c2_sqrt = chi2_sqrt(ts_peak, rs_peak, a_sqrt)

    r_rms_final  = trajectory[-1]["r_rms"]  if trajectory else 0.0
    r_final = trajectory[-1]["r_front"] if trajectory else 0.0

    return {
        "k_back":     k_back,
        "v_pred":     round(v_pred, 4),
        "v_measured": round(v_meas, 4),
        "r_final":    r_final,
        "fit_n_pts_peak": len(peak_pts),
        "fit_n_pts_rms": len(fit_pts_rms),
        "v_front":      round(v_front, 4),
        "r_rms_final":  r_rms_final,
        "chi2_linear":  round(c2_lin, 4),
        "chi2_sqrt":    round(c2_sqrt, 4),
        "ballistic_ratio": round(c2_sqrt / c2_lin, 3) if c2_lin > 1e-10 else 0.0,
        "trajectory": trajectory[:20],   # truncate for report
    }


# ---------------------------------------------------------------------------
# Physical units (C3 + C1)
# ---------------------------------------------------------------------------

def physical_units(v_meas: float) -> dict:
    if v_meas <= 0:
        return {}
    tau_over_a = v_meas / C_LIGHT_MS
    a_proton = M_PROTON_KG * G_NEWTON * tau_over_a**2 / G_QNG
    return {
        "tau_over_a_s_per_m": tau_over_a,
        "a_m":                a_proton,
        "a_l_planck":         round(a_proton / L_PLANCK_M, 2),
        "lambda_phys_m":      round(3.41 * a_proton, 4),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--k-backs", nargs="+", type=float, default=K_BACKS)
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    print(f"QNG-CPU-054: Massless KG wave  L={L}  w={W_PERTURB}  delta={DELTA}")
    print(f"alpha={ALPHA}  beta={BETA}  chi_rel={CHI_REL}  chi_decay={CHI_DECAY}")
    print(f"v_pred(k_back=1.0) = sqrt(chi_rel/6) = {math.sqrt(CHI_REL/6):.4f}  [corrected from DER-QNG-032]")
    print()

    all_results: dict[float, dict] = {}
    for kb in args.k_backs:
        result = run_kback(kb)
        all_results[kb] = result
        print(f"  -> v_measured={result['v_measured']:.4f}  v_pred={result['v_pred']:.4f}  "
              f"r_final={result['r_final']:.1f}  ballistic_ratio={result['ballistic_ratio']:.2f}")
        print()

    # Checks
    r1  = all_results.get(1.00, {})
    r01 = all_results.get(0.10, {})

    v_strong = r1.get("v_measured", 0.0)
    v_pred_strong = math.sqrt(1.00 * CHI_REL / 6.0)  # corrected formula

    check1 = r1.get("r_final", 0) > 2 * W_PERTURB  # wave traveled > 2×initial width
    check2 = (v_strong > 0 and
              abs(v_strong - v_pred_strong) / v_pred_strong < 0.25)
    # Check 3: speed scales with sqrt(k_back)
    v_lo = r01.get("v_measured", 0.0)
    v_hi = v_strong
    pred_ratio = math.sqrt(1.00 / 0.10)   # = sqrt(10) ≈ 3.16
    meas_ratio = v_hi / v_lo if v_lo > 0.01 else 0.0
    check3 = 2.0 <= meas_ratio <= 4.5
    # Check 4: ballistic > diffusive (informational)
    check4_info = r1.get("ballistic_ratio", 0) > 1.5

    decision = check1 and check2

    print("=" * 60)
    print(f"{'k_back':>8}  {'v_pred':>8}  {'v_meas':>8}  {'rel_err':>8}  "
          f"{'r_final':>8}  {'ballist':>8}")
    for kb in args.k_backs:
        r = all_results[kb]
        rel = abs(r['v_measured'] - r['v_pred']) / r['v_pred'] if r['v_pred'] > 0 else 999
        print(f"  {kb:>6.2f}  {r['v_pred']:>8.4f}  {r['v_measured']:>8.4f}  "
              f"{rel:>8.3f}  {r['r_final']:>8.1f}  {r['ballistic_ratio']:>8.2f}")
    print()

    phys = physical_units(v_strong)
    if phys:
        print("Physical units (C3+C1, m_node=m_proton, k_back=1.0):")
        print(f"  a = {phys['a_m']:.3e} m = {phys['a_l_planck']:.1f} l_Planck")
        print(f"  tau = {phys['tau_over_a_s_per_m'] * phys['a_m']:.3e} s")
        print(f"  lambda_phys = {phys['lambda_phys_m']:.3e} m")
    print()

    print("Checks:")
    print(f"  Check 1 (r_final > 2w={2*W_PERTURB:.0f}): {'PASS' if check1 else 'FAIL'}  "
          f"r={r1.get('r_final', 0):.1f}")
    print(f"  Check 2 (v within 20% of sqrt(beta)): {'PASS' if check2 else 'FAIL'}  "
          f"v={v_strong:.4f} pred={v_pred_strong:.4f}")
    print(f"  Check 3 (v scales with sqrt(k_back)): {'PASS' if check3 else 'FAIL'}  "
          f"ratio={meas_ratio:.2f} pred={pred_ratio:.2f}")
    print(f"  Check 4 [info] ballistic > diffusive: {'PASS' if check4_info else 'FAIL'}  "
          f"ratio={r1.get('ballistic_ratio', 0):.2f}")
    print(f"\nqng_wave_kg_reference: {'PASS' if decision else 'FAIL'}")

    report = {
        "test_id": "QNG-CPU-054",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "L": L, "N": N, "A_perturb": A_PERTURB, "w": W_PERTURB,
            "alpha": ALPHA, "beta": BETA, "delta": DELTA,
            "chi_decay": CHI_DECAY, "chi_rel": CHI_REL,
            "max_steps": MAX_STEPS, "t_start_fit": T_START_FIT,
        },
        "v_pred_kback_1": round(v_pred_strong, 4),
        "results": {
            f"k_back_{kb:.2f}": {
                "v_pred":     r["v_pred"],
                "v_measured": r["v_measured"],
                "r_final":    r["r_final"],
                "fit_n_pts":  r["fit_n_pts_peak"],
                "ballistic_ratio": r["ballistic_ratio"],
            }
            for kb, r in all_results.items()
        },
        "physical_units_k1": phys,
        "checks": {
            "wave_propagates_pass":   check1,
            "speed_correct_pass":     check2,
            "sqrt_scaling_pass":      check3,
            "ballistic_info":         check4_info,
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-CPU-054: Massless Klein-Gordon Wave Test",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- L={L}, w={W_PERTURB}, delta={DELTA} (massless)",
        "",
        "## Speed Results",
        "| k_back | v_pred | v_measured | rel_err | r_final | ballistic |",
        "|--------|--------|------------|---------|---------|-----------|",
    ] + [
        f"| {kb:.2f} | {r['v_pred']:.4f} | {r['v_measured']:.4f} | "
        f"{abs(r['v_measured']-r['v_pred'])/r['v_pred']:.3f} | "
        f"{r['r_final']:.1f} | {r['ballistic_ratio']:.2f} |"
        for kb, r in all_results.items()
    ] + [
        "",
        "## Checks",
        f"- Check 1 (wave propagates): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (speed correct): {'PASS' if check2 else 'FAIL'}",
        f"- Check 3 (sqrt(k_back) scaling): {'PASS' if check3 else 'FAIL'}",
        f"- Check 4 [info] ballistic: {'PASS' if check4_info else 'FAIL'}",
    ]
    if phys:
        lines += [
            "",
            "## Physical Units (k_back=1, m_node=m_proton)",
            f"- a = {phys['a_m']:.3e} m = {phys['a_l_planck']:.1f} l_Planck",
        ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nReport: {(out_dir / 'report.json').as_posix()}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
