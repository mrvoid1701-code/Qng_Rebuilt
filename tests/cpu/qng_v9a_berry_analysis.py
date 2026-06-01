"""QNG-CPU-098: V9-A Berry-integral analysis on GPU-100 phase-space data.

Loads reduced_series.npz and snapshots.npz from
qng-v9a-phase-space-v1/R{3,4,5}/ and computes four candidate loop
integrals per orbital cycle:

  S1 = oint P_M dM_ring                  (zero-mode action)
  S2 = int_cycle sum_i pi_m_i dsigma_m_i (full-field kinetic action)
  S3 = int_cycle sum_i pi_phi_i dphi_i   (phi kinetic action)
  S4 = oint P_COM . dR_COM               (COM action)

Orbital cycles are detected via zero-crossings of (M_ring - <M_ring>).
Verdict logic per prereg QNG-CPU-098.md:
  V9A-PASS: per-R means cluster at integer multiples of single theta_0
            (|err| < 5%) AND within-R CV < 10%
  V9A-QUANTIZED_CONTINUOUS: within-R CV < 10% but R-dependent (adiabatic)
  V9A-FAIL: within-R CV > 20% (no invariant)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "07_validation" / "audits" / "qng-v9a-phase-space-v1"
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-v9a-berry-analysis-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def find_cycles(M, t, min_period_lu=30.0):
    """Detect cycles via zero-crossings of (M - mean(M)).

    Returns list of (i_start, i_end) index pairs covering complete cycles
    (negative-to-negative or positive-to-positive, whichever is cleaner).
    Enforces min period to avoid grazing noise.
    """
    M = np.asarray(M)
    t = np.asarray(t)
    c = M - np.mean(M)
    # Detect sign changes (ascending crossings: neg to pos)
    asc = np.where((c[:-1] < 0) & (c[1:] >= 0))[0]
    if len(asc) < 2:
        return []
    cycles = []
    for k in range(len(asc) - 1):
        i_s = int(asc[k]); i_e = int(asc[k + 1])
        if (t[i_e] - t[i_s]) >= min_period_lu:
            cycles.append((i_s, i_e))
    return cycles


def loop_integral_PdQ(Q, P, idx_start, idx_end):
    """Trapezoidal integral of P dQ from idx_start to idx_end.

    Uses Stokes-style line integral: sum P_k * (Q_{k+1} - Q_{k-1}) / 2
    """
    # Simple trapezoid: int P dQ ≈ sum((P[k]+P[k+1])/2 * (Q[k+1]-Q[k]))
    Pm = 0.5 * (P[idx_start:idx_end] + P[idx_start + 1:idx_end + 1])
    dQ = Q[idx_start + 1:idx_end + 1] - Q[idx_start:idx_end]
    return float(np.sum(Pm * dQ))


def kinetic_action_from_snaps(sm_stack, pim_stack, t_snap, t_start, t_end):
    """S2 = int sum_i pi_m_i dsigma_m_i across snapshot window [t_start, t_end].

    Uses trapezoid on snapshot grid. Sigma_m and pi_m stored as (T, N).
    """
    mask = (t_snap >= t_start) & (t_snap <= t_end)
    if np.sum(mask) < 3:
        return None
    sm_w = sm_stack[mask]     # (Tw, N)
    pim_w = pim_stack[mask]   # (Tw, N)
    # Midpoint pi_m at interval k→k+1:
    pim_mid = 0.5 * (pim_w[:-1] + pim_w[1:])   # (Tw-1, N)
    dsm = sm_w[1:] - sm_w[:-1]                  # (Tw-1, N)
    per_step = np.sum(pim_mid * dsm, axis=1)    # (Tw-1,)
    return float(np.sum(per_step))


def phi_kinetic_action(phi_stack, piphi_stack, t_snap, t_start, t_end):
    """S3 = int sum_i pi_phi_i dphi_i — unwrap phi differences modulo 2π."""
    mask = (t_snap >= t_start) & (t_snap <= t_end)
    if np.sum(mask) < 3:
        return None
    phi_w = phi_stack[mask]
    pip_w = piphi_stack[mask]
    pip_mid = 0.5 * (pip_w[:-1] + pip_w[1:])
    # Shortest-arc dphi
    dphi = phi_w[1:] - phi_w[:-1]
    dphi = (dphi + np.pi) % (2 * np.pi) - np.pi
    per_step = np.sum(pip_mid * dphi, axis=1)
    return float(np.sum(per_step))


def analyze_R(R):
    """Analyze one R value."""
    R_dir = DATA_ROOT / f"R{R}"
    if not (R_dir / "reduced_series.npz").exists():
        print(f"  [R={R}] missing reduced_series.npz — skipping")
        return None
    red = np.load(R_dir / "reduced_series.npz")
    t = red['t']; M = red['M_ring']; P_M = red['P_M']
    COMx = red['COM_x']; COMy = red['COM_y']; COMz = red['COM_z']

    cycles = find_cycles(M, t, min_period_lu=80.0)
    print(f"  [R={R}] found {len(cycles)} cycles in reduced series")
    if len(cycles) == 0:
        return {'R': R, 'n_cycles': 0, 'verdict': 'V9A-FAIL-NO-CYCLES'}

    # Per-cycle S1 (P_M dM_ring on 1-lu grid)
    S1_vals = []
    for i_s, i_e in cycles:
        S1_vals.append(loop_integral_PdQ(M, P_M, i_s, i_e))
    S1_arr = np.asarray(S1_vals)

    # Per-cycle COM loop (use sqrt(COMx²+COMy²+COMz²) and momentum via
    # finite difference; approximate P_COM = mu_m * d(COM)/dt)
    # Simpler: S4 = oint COMx dCOMy (xy-plane area)
    S4_vals = []
    for i_s, i_e in cycles:
        # Shoelace-ish line integral
        cx = COMx[i_s:i_e + 1]; cy = COMy[i_s:i_e + 1]
        S4_vals.append(0.5 * float(
            np.sum(cx[:-1] * cy[1:] - cx[1:] * cy[:-1])))
    S4_arr = np.asarray(S4_vals)

    # Per-cycle S2, S3 from snapshots (coarser — 10 lu) where available
    S2_vals = []; S3_vals = []
    snap_path = R_dir / "snapshots.npz"
    if snap_path.exists():
        snap = np.load(snap_path)
        t_snap = snap['t_snap']
        sm_st = snap['sm']; pim_st = snap['pi_m']
        phi_st = snap['phi']; piphi_st = snap['pi_phi']
        print(f"  [R={R}] loaded {len(t_snap)} snapshots, "
              f"{sm_st.shape[1]} sites")
        for i_s, i_e in cycles:
            t_s = t[i_s]; t_e = t[i_e]
            s2 = kinetic_action_from_snaps(sm_st, pim_st, t_snap, t_s, t_e)
            s3 = phi_kinetic_action(phi_st, piphi_st, t_snap, t_s, t_e)
            S2_vals.append(s2 if s2 is not None else np.nan)
            S3_vals.append(s3 if s3 is not None else np.nan)
    else:
        print(f"  [R={R}] no snapshots.npz — S2, S3 unavailable")
    S2_arr = np.asarray(S2_vals) if S2_vals else np.array([np.nan])
    S3_arr = np.asarray(S3_vals) if S3_vals else np.array([np.nan])

    def stats(arr, name):
        arr = np.asarray(arr, dtype=np.float64)
        arr_clean = arr[~np.isnan(arr)]
        if len(arr_clean) == 0:
            return {'name': name, 'n': 0, 'mean': None, 'std': None, 'cv': None}
        mean = float(np.mean(arr_clean))
        std = float(np.std(arr_clean))
        cv = abs(std / mean) if abs(mean) > 1e-10 else None
        return {'name': name, 'n': int(len(arr_clean)),
                'mean': mean, 'std': std, 'cv': cv,
                'values': arr_clean.tolist()}

    result = {
        'R': R,
        'n_cycles': len(cycles),
        'cycle_times': [(float(t[i_s]), float(t[i_e])) for i_s, i_e in cycles],
        'S1_P_M_dM_ring': stats(S1_arr, 'S1'),
        'S2_sum_pi_m_dsm': stats(S2_arr, 'S2'),
        'S3_sum_pi_phi_dphi': stats(S3_arr, 'S3'),
        'S4_COM_xy_area': stats(S4_arr, 'S4'),
    }

    # Save per-R cycles
    with open(OUT_DIR / f"cycles_R{R}.json", 'w') as f:
        json.dump(result, f, indent=2)
    return result


def verdict_per_candidate(per_R_stats, key):
    """Decide V9A status for one candidate (S1, S2, S3, or S4) across R."""
    per_R = {R: r[key] for R, r in per_R_stats.items() if r is not None}
    means = {R: s.get('mean') for R, s in per_R.items()
             if s and s.get('mean') is not None}
    cvs = {R: s.get('cv') for R, s in per_R.items()
           if s and s.get('cv') is not None}
    if len(means) < 2 or len(cvs) < 2:
        return {'status': 'V9A-FAIL-INSUFFICIENT-DATA', 'means': means, 'cvs': cvs}
    all_cv_ok = all(cv is not None and cv < 0.10 for cv in cvs.values())
    all_cv_fail = any(cv is not None and cv > 0.20 for cv in cvs.values())

    if all_cv_fail:
        return {'status': 'V9A-FAIL', 'means': means, 'cvs': cvs,
                'reason': 'within-R CV > 20% at some R (no classical adiabatic invariant)'}
    if not all_cv_ok:
        return {'status': 'V9A-MARGINAL', 'means': means, 'cvs': cvs,
                'reason': '10% < CV < 20% — within-R noise too high for clean verdict'}
    # Check R-invariance up to integer scaling
    mean_vals = np.array(list(means.values()))
    # Test hypothesis: mean_R = n_R * theta_0 for small integers n_R in {1,2,3,...}
    # Minimize |mean - round(mean/theta)*theta| over theta
    abs_mean = np.abs(mean_vals)
    if np.max(abs_mean) < 1e-8:
        return {'status': 'V9A-FAIL', 'means': means, 'cvs': cvs,
                'reason': 'all means near zero — trivial'}
    # Candidate theta_0: try fractions of max mean
    best = {'theta_0': None, 'max_err': np.inf, 'ratios': None}
    # Grid-search theta in (|max|/10, |max|*2) with fine step
    m_max = np.max(abs_mean)
    theta_grid = np.linspace(m_max / 10.0, m_max * 2.0, 400)
    for theta in theta_grid:
        if theta < 1e-12:
            continue
        ratios = mean_vals / theta
        rounded = np.round(ratios)
        mask = rounded != 0  # skip singular
        if not np.any(mask):
            continue
        errs = np.abs(ratios[mask] - rounded[mask]) / np.abs(rounded[mask])
        max_err = float(np.max(errs))
        if max_err < best['max_err']:
            best = {'theta_0': float(theta), 'max_err': max_err,
                    'ratios': ratios.tolist(),
                    'rounded': rounded.tolist()}
    if best['max_err'] < 0.05:
        return {'status': 'V9A-PASS', 'means': means, 'cvs': cvs,
                'theta_0': best['theta_0'], 'max_err': best['max_err'],
                'ratios_to_theta0': best['ratios'],
                'rounded_integers': best['rounded']}
    return {'status': 'V9A-QUANTIZED_CONTINUOUS', 'means': means, 'cvs': cvs,
            'reason': f'within-R CV OK but no integer-ratio structure '
                      f'(best theta_0 max_err={best["max_err"]:.3f})'}


def main():
    print("=" * 80)
    print("QNG-CPU-098: V9-A Berry-integral analysis")
    print("=" * 80)
    per_R = {}
    for R in (3, 4, 5):
        print(f"\n--- R = {R} ---")
        per_R[R] = analyze_R(R)

    # Verdicts
    print("\n" + "=" * 80)
    print("PER-CANDIDATE VERDICTS")
    print("=" * 80)
    verdicts = {}
    for key, name in [('S1_P_M_dM_ring', 'S1 (P_M dM_ring)'),
                       ('S2_sum_pi_m_dsm', 'S2 (sum pi_m dsm)'),
                       ('S3_sum_pi_phi_dphi', 'S3 (sum pi_phi dphi)'),
                       ('S4_COM_xy_area', 'S4 (COM xy area)')]:
        v = verdict_per_candidate(per_R, key)
        verdicts[key] = v
        print(f"\n  {name}:")
        for k, val in v.items():
            if k in ('means', 'cvs', 'ratios_to_theta0', 'rounded_integers'):
                print(f"    {k}: {val}")
            else:
                print(f"    {k} = {val}")

    # Overall V9-A verdict: PASS if ANY candidate reaches V9A-PASS
    any_pass = any(v.get('status') == 'V9A-PASS' for v in verdicts.values())
    any_quantized = any(v.get('status') == 'V9A-QUANTIZED_CONTINUOUS'
                        for v in verdicts.values())
    any_marginal = any(v.get('status') == 'V9A-MARGINAL' for v in verdicts.values())
    any_fail = any(v.get('status') == 'V9A-FAIL' for v in verdicts.values())

    if any_pass:
        overall = 'V9A-PASS'
    elif any_quantized:
        overall = 'V9A-QUANTIZED_CONTINUOUS'
    elif any_marginal:
        overall = 'V9A-MARGINAL'
    elif any_fail:
        overall = 'V9A-FAIL'
    else:
        overall = 'V9A-INSUFFICIENT'

    summary = {
        'test_id': 'QNG-CPU-098',
        'date': '2026-04-22',
        'data_source': str(DATA_ROOT),
        'per_R_n_cycles': {R: r.get('n_cycles') if r else 0
                            for R, r in per_R.items()},
        'verdicts': verdicts,
        'overall_verdict': overall,
    }
    with open(OUT_DIR / "report.json", 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n  OVERALL V9-A VERDICT: {overall}")
    print(f"  Report: {OUT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
