from __future__ import annotations

"""
QNG-CPU-055: Vortex ring energy vs sigma integral — E_ring vs M_ring decay.

Runs the v5 vortex ring (identical to CPU-044 parameters) and measures both:
  M_ring(t) = Σ max(0, sigma_ref - sigma_i)   [sigma depletion — charge-like]
  E_ring(t) = E[sigma,chi,phi] - E_vacuum      [free energy — energy-like]

Key question for matter source identification: do E and M decay at the same
rate (mass ∝ charge) or independently (need separate identification)?
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-energy-v1"

# ---------------------------------------------------------------------------
# Parameters (identical to CPU-044)
# ---------------------------------------------------------------------------

L: int = 20
N: int = L * L * L
PHASE1_STEPS: int = 300
PHASE2_STEPS: int = 2500
CHECK_INTERVAL: int = 200

SIGMA_REF: float = 0.5
ALPHA:     float = 0.005
BETA:      float = 0.35
BETA_PHI:  float = 0.02
DELTA:     float = 0.20
EPSILON:   float = 0.0
CHI_DECAY: float = 0.005
CHI_REL:   float = 0.35
GAMMA_PHI: float = 0.10

RING_X: float = L / 2.0
RING_Y: float = L / 2.0
RING_Z: float = L / 2.0
RING_R: float = 5.0
RING_TUBE_R: float = 3.0    # nodes within this distance of ring tube = "ring nodes"


# ---------------------------------------------------------------------------
# Indexing and geometry
# ---------------------------------------------------------------------------

def idx3(x: int, y: int, z: int) -> int:
    return (x % L) * L * L + (y % L) * L + (z % L)

def coord3(i: int) -> tuple[int, int, int]:
    x = i // (L * L); y = (i % (L * L)) // L; z = i % L
    return x, y, z

def _mi(d: float) -> float:
    while d >  L / 2: d -= L
    while d < -L / 2: d += L
    return d

def wrap(a: float) -> float:
    a = a % (2 * math.pi)
    return a - 2 * math.pi if a > math.pi else a

def angle_diff(a: float, b: float) -> float:
    return wrap(a - b)

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))

def neighbors(x: int, y: int, z: int) -> list[int]:
    return [idx3(x-1,y,z), idx3(x+1,y,z),
            idx3(x,y-1,z), idx3(x,y+1,z),
            idx3(x,y,z-1), idx3(x,y,z+1)]

def is_ring_node(i: int) -> bool:
    """Node within RING_TUBE_R lattice units of the ring tube."""
    x, y, z = coord3(i)
    dx = _mi(x - RING_X); dy = _mi(y - RING_Y); dz = _mi(z - RING_Z)
    rho = math.sqrt(dx*dx + dy*dy)
    d_tube = math.sqrt((rho - RING_R)**2 + dz*dz)
    return d_tube <= RING_TUBE_R

RING_NODES: list[int] = [i for i in range(N) if is_ring_node(i)]


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def init_phi_ring() -> list[float]:
    phi = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - RING_X); dy = _mi(y - RING_Y); dz = _mi(z - RING_Z)
        rho = math.sqrt(dx*dx + dy*dy)
        phi.append(math.atan2(dz, rho - RING_R))
    return phi


# ---------------------------------------------------------------------------
# Phase disorder
# ---------------------------------------------------------------------------

def phase_disorder(phi: list[float], i: int) -> float:
    x, y, z = coord3(i)
    nb = neighbors(x, y, z)
    sx = sum(math.cos(phi[j]) for j in nb) / 6.0
    sy = sum(math.sin(phi[j]) for j in nb) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx*sx + sy*sy))


# ---------------------------------------------------------------------------
# Update step (v5, identical to CPU-044)
# ---------------------------------------------------------------------------

def update_step(sigma: list[float], chi: list[float], phi: list[float],
                channel_f: bool) -> tuple[list[float], list[float], list[float]]:
    ns, nc, np_ = [], [], []
    for i in range(N):
        x, y, z = coord3(i)
        nb = neighbors(x, y, z)
        sigma_bar = sum(sigma[j] for j in nb) / 6.0

        if channel_f:
            D_i = phase_disorder(phi, i)
            s = clip01(sigma[i] + ALPHA*(SIGMA_REF - sigma[i])
                       + BETA*(sigma_bar - sigma[i])
                       - GAMMA_PHI*D_i*sigma[i])
        else:
            s = clip01(sigma[i] + ALPHA*(SIGMA_REF - sigma[i])
                       + BETA*(sigma_bar - sigma[i]))

        c = (chi[i]*(1 - CHI_DECAY)
             + CHI_REL*(sigma_bar - sigma[i])
             + DELTA*(SIGMA_REF - sigma[i]))

        nb_phi = [phi[j] for j in nb]
        nb_sig = [sigma[j] for j in nb]
        tw = sum(nb_sig)
        if tw > 1e-10:
            sx2 = sum(nb_sig[k]*math.cos(nb_phi[k]) for k in range(6)) / tw
            sy2 = sum(nb_sig[k]*math.sin(nb_phi[k]) for k in range(6)) / tw
            pm = math.atan2(sy2, sx2)
        else:
            pm = phi[i]
        p = wrap(phi[i] + BETA_PHI*angle_diff(pm, phi[i]) + EPSILON*chi[i])

        ns.append(s); nc.append(c); np_.append(p)
    return ns, nc, np_


# ---------------------------------------------------------------------------
# Energy functional E[sigma, chi, phi] from DER-QNG-032
# ---------------------------------------------------------------------------

def compute_energy(sigma: list[float], chi: list[float],
                   phi: list[float], node_set: list[int] | None = None) -> float:
    """
    E = Σ_i {
      alpha/2 * (sigma_i - sigma_ref)²          [self-restore well]
      + beta/4 * Σ_{j~i} (sigma_j - sigma_i)²   [gradient tension, double-counts edges]
      + chi_decay/2 * chi_i²                     [chi self-energy]
      + chi_rel/2 * chi_i*(sigma_bar_i-sigma_i)  [chi-sigma coupling]
      + delta * chi_i*(sigma_i - sigma_ref)       [Channel D cross-coupling]
      - beta_phi/6 * Σ_{j~i} s_i*s_j*cos(Δphi)  [XY phase energy]
      + gamma_phi/2 * D_i * sigma_i²             [Channel F disorder]
    }
    node_set: if given, only sum over these nodes (ring-localized energy).
    """
    if node_set is None:
        node_set = range(N)

    E = 0.0
    for i in node_set:
        x, y, z = coord3(i)
        nb = neighbors(x, y, z)
        sigma_bar = sum(sigma[j] for j in nb) / 6.0
        si = sigma[i]; ci = chi[i]; pi = phi[i]
        ds = si - SIGMA_REF

        # Channel A: self-restore well
        E += ALPHA / 2.0 * ds * ds

        # Channel B: gradient tension (double-counts edges — consistent with DER-QNG-032)
        E += BETA / 4.0 * sum((sigma[j] - si)**2 for j in nb)

        # Chi self-energy
        E += CHI_DECAY / 2.0 * ci * ci

        # Chi-sigma gradient coupling
        E += CHI_REL / 2.0 * ci * (sigma_bar - si)

        # Channel D: chi-sigma offset coupling
        E += DELTA * ci * (si - SIGMA_REF)

        # XY phase energy (favorable alignment → negative contribution)
        E -= BETA_PHI / 6.0 * sum(si * sigma[j] * math.cos(angle_diff(pi, phi[j]))
                                   for j in nb)

        # Channel F: phase disorder energy
        D_i = phase_disorder(phi, i)
        E += GAMMA_PHI / 2.0 * D_i * si * si

    return E


def compute_m_ring(sigma: list[float], node_set: list[int] | None = None) -> float:
    """M_ring = Σ max(0, sigma_ref - sigma_i) = total sigma depletion."""
    if node_set is None:
        node_set = range(N)
    return sum(max(0.0, SIGMA_REF - sigma[i]) for i in node_set)


# ---------------------------------------------------------------------------
# Vacuum energy (reference: sigma=sigma_ref, chi=0, phi=0 everywhere)
# ---------------------------------------------------------------------------

def vacuum_energy() -> float:
    """E at perfect vacuum state. Should be ~0 for most terms."""
    sigma_vac = [SIGMA_REF] * N
    chi_vac   = [0.0] * N
    phi_vac   = [0.0] * N
    return compute_energy(sigma_vac, chi_vac, phi_vac)


# ---------------------------------------------------------------------------
# Exponential decay fit: f(t) = f0 * exp(-t / tau)
# ---------------------------------------------------------------------------

def fit_exp_decay(ts: list[float], ys: list[float]) -> tuple[float, float]:
    """Fit y = y0 * exp(-t/tau). Returns (y0, tau). Uses log-linear regression."""
    log_pts = [(t, math.log(y)) for t, y in zip(ts, ys) if y > 1e-10]
    if len(log_pts) < 3:
        return ys[0] if ys else 0.0, float('inf')
    n = len(log_pts)
    tm = sum(p[0] for p in log_pts) / n
    lm = sum(p[1] for p in log_pts) / n
    num = sum((p[0]-tm)*(p[1]-lm) for p in log_pts)
    den = sum((p[0]-tm)**2 for p in log_pts)
    slope = num/den if abs(den) > 1e-12 else 0.0
    tau = -1.0/slope if abs(slope) > 1e-12 else float('inf')
    y0 = math.exp(lm - slope*tm)
    return y0, tau


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    print("QNG-CPU-055: Ring energy vs sigma integral")
    print(f"L={L}  R={RING_R}  Phase2={PHASE2_STEPS}  ring_nodes={len(RING_NODES)}")
    print(f"ALPHA={ALPHA} BETA={BETA} DELTA={DELTA} GAMMA_PHI={GAMMA_PHI}")
    print()

    # Vacuum reference energy
    E_vac = vacuum_energy()
    print(f"E_vacuum = {E_vac:.4f}")
    print()

    # Initialize
    sigma = [SIGMA_REF] * N
    chi   = [0.0] * N
    phi   = init_phi_ring()

    # Phase 1: form ring (no Channel F)
    print("Phase 1: forming ring...")
    for t in range(PHASE1_STEPS):
        sigma, chi, phi = update_step(sigma, chi, phi, channel_f=False)
    print(f"  Phase 1 done. M_ring_global={compute_m_ring(sigma):.1f}")
    print()

    # Phase 2: ring dynamics with Channel F + measurements
    print("Phase 2: ring evolution + energy measurements")
    print(f"{'t':>6}  {'M_global':>10}  {'M_local':>10}  {'E_global':>12}  {'E_local':>10}  {'ratio_g':>9}  {'ratio_l':>9}")

    trajectory = []
    ts_fit:  list[float] = []
    M_fits:  list[float] = []
    E_fits:  list[float] = []

    for t in range(1, PHASE2_STEPS + 1):
        sigma, chi, phi = update_step(sigma, chi, phi, channel_f=True)

        if t % CHECK_INTERVAL == 0 or t == 1:
            M_g = compute_m_ring(sigma)
            M_l = compute_m_ring(sigma, RING_NODES)
            E_g = compute_energy(sigma, chi, phi) - E_vac
            E_l = compute_energy(sigma, chi, phi, RING_NODES) - compute_energy(
                [SIGMA_REF]*N, [0.0]*N, [0.0]*N, RING_NODES)
            ratio_g = E_g / M_g if M_g > 1e-6 else 0.0
            ratio_l = E_l / M_l if M_l > 1e-6 else 0.0

            print(f"  T={t:4d}  {M_g:10.2f}  {M_l:10.2f}  {E_g:12.4f}  {E_l:10.4f}  {ratio_g:9.4f}  {ratio_l:9.4f}", flush=True)
            trajectory.append({
                "t": t, "M_global": round(M_g,3), "M_local": round(M_l,3),
                "E_global": round(E_g,6), "E_local": round(E_l,6),
                "ratio_global": round(ratio_g,6), "ratio_local": round(ratio_l,6),
            })
            if t >= CHECK_INTERVAL:
                ts_fits = ts_fit + [float(t)]
                M_fits2 = M_fits + [M_g]
                E_fits2 = E_fits + [E_g]
            ts_fit.append(float(t)); M_fits.append(M_g); E_fits.append(E_g)

    print()

    # Fit decay rates — use only the DECAYING portion (after M peaks).
    # M grows during early Phase 2 as Channel F depletes ring core, then decays.
    # Find peak M index and fit from there.
    peak_idx = M_fits.index(max(M_fits))
    ts_dec  = ts_fit[peak_idx:]
    M_dec   = M_fits[peak_idx:]
    E_dec   = [abs(e) for e in E_fits[peak_idx:]]   # |E| since E is negative (bound state)
    _, tau_M = fit_exp_decay(ts_dec, M_dec)
    _, tau_E = fit_exp_decay(ts_dec, E_dec)
    tau_ratio = tau_E / tau_M if tau_M > 0 and tau_M < 1e9 else float('nan')

    # Ratio stability (only over decaying portion, use absolute ratio)
    ratios_g = [abs(p["ratio_global"]) for p in trajectory
                if p["t"] >= ts_fit[peak_idx] and p["M_global"] > 1.0]
    mean_ratio = sum(ratios_g)/len(ratios_g) if ratios_g else 0.0
    std_ratio  = math.sqrt(sum((r-mean_ratio)**2 for r in ratios_g)/len(ratios_g)) if len(ratios_g)>1 else 0.0
    ratio_cv   = std_ratio / mean_ratio if mean_ratio > 1e-10 else float('nan')

    # Checks
    check1 = trajectory[-1]["M_global"] > 50 if len(trajectory) >= 5 else False
    check2 = (trajectory[0]["E_global"] > 0 and trajectory[0]["M_global"] > 0)
    decision = check1 and check2

    print("=" * 70)
    print(f"Decay time constants:")
    print(f"  tau_M (sigma depletion) = {tau_M:.1f} steps")
    print(f"  tau_E (free energy)     = {tau_E:.1f} steps")
    print(f"  tau_E / tau_M           = {tau_ratio:.3f}  (1.0 = same decay)")
    print()
    print(f"E/M ratio (global): mean={mean_ratio:.4f}  std={std_ratio:.4f}  CV={ratio_cv:.3f}")
    print(f"  CV < 0.20 -> ratio stable (E proportional to M throughout decay)")
    print(f"  CV > 0.20 -> ratio evolves (E and M decouple)")
    print()
    print("Checks:")
    print(f"  Check 1 (ring survives, M_global > 50 at T=final): {'PASS' if check1 else 'FAIL'}  M={trajectory[-1]['M_global']:.1f}")
    print(f"  Check 2 (E and M measurable at T=1):               {'PASS' if check2 else 'FAIL'}")
    print(f"  Check 3 [finding] tau_E/tau_M = {tau_ratio:.3f}")
    print(f"  Check 4 [finding] ratio CV    = {ratio_cv:.3f}")
    print(f"\nqng_ring_energy_reference: {'PASS' if decision else 'FAIL'}")

    report = {
        "test_id": "QNG-CPU-055",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "L": L, "N": N, "R": RING_R, "phase1": PHASE1_STEPS,
            "phase2": PHASE2_STEPS, "alpha": ALPHA, "beta": BETA,
            "delta": DELTA, "gamma_phi": GAMMA_PHI, "beta_phi": BETA_PHI,
        },
        "E_vacuum": round(E_vac, 6),
        "tau_M": round(tau_M, 1) if tau_M < 1e8 else None,
        "tau_E": round(tau_E, 1) if tau_E < 1e8 else None,
        "tau_ratio": round(tau_ratio, 4) if not math.isnan(tau_ratio) else None,
        "ratio_global_mean": round(mean_ratio, 6),
        "ratio_global_cv":   round(ratio_cv, 4) if not math.isnan(ratio_cv) else None,
        "checks": {
            "ring_survives": check1,
            "quantities_measurable": check2,
        },
        "trajectory": trajectory,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-CPU-055: Ring Energy vs Sigma Integral",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Key Findings",
        f"- tau_M (sigma depletion decay) = {tau_M:.1f} steps",
        f"- tau_E (free energy decay)     = {tau_E:.1f} steps",
        f"- tau_E / tau_M = {tau_ratio:.3f}",
        f"- E/M ratio CV  = {ratio_cv:.3f}  ({'stable' if ratio_cv<0.20 else 'evolving'})",
        "",
        "## Trajectory",
        "| t | M_global | M_local | E_global | E_local | ratio_g | ratio_l |",
        "|---|----------|---------|----------|---------|---------|---------|",
    ] + [
        f"| {p['t']} | {p['M_global']:.1f} | {p['M_local']:.1f} | {p['E_global']:.4f} | {p['E_local']:.4f} | {p['ratio_global']:.4f} | {p['ratio_local']:.4f} |"
        for p in trajectory
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nReport: {(out_dir / 'report.json').as_posix()}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
