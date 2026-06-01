"""QNG-CPU-095: Edge-stochastic TEMPORAL correlation probe (OU process).

CPU-092/093/094 closed the scalar i.i.d. edge noise family: every
finite-variance distribution gives Debye-Waller universal law
|shift|/<L>_0 = (Var_eff / 2) * f_perturbed. Scale proportional to
Var(xi) -> no hbar.

This test probes Option (b'): TEMPORALLY CORRELATED noise via
Ornstein-Uhlenbeck process per edge:

    xi_ij(t+dt) = exp(-dt/tau_c) * xi_ij(t) + sigma_ou * eta

with sigma_ou = rms * sqrt(1 - exp(-2 dt / tau_c)).

Stationary variance = rms^2. Correlation time = tau_c.

Physical regimes:
  - tau_c -> 0:   white noise (instantaneous resample)
  - tau_c ~ 1:    matches phi relaxation -> motional narrowing regime
  - tau_c -> inf: quenched (xi frozen)

KEY QUESTION: does the Debye-Waller law break down at any tau_c,
revealing a new scale? Or is shift merely a smooth function of
(rms, tau_c)?

Expected (classical): motional narrowing at small tau_c reduces shift
(averaged xi -> 0 faster than phi responds). This is known chemical
exchange / Doppler physics, NOT hbar.

If shift SATURATES at a universal value independent of rms at some
tau_c window, THAT is an hbar candidate.

L=8, z=6, vacuum (no ring). rms = 0.2 fixed (Debye-Waller regime).
Scan tau_c in {0.1, 0.5, 1, 2, 5, 10, 50, 1000} lu.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "07_validation" / "audits" / "qng-edge-stochastic-ou-v1"
AUDIT.mkdir(parents=True, exist_ok=True)

BETA_PHI = 0.06
MU_PHI = 0.857
DT = 0.05
T_SIM = 150.0
N_STEPS = int(T_SIM / DT)
L = 8
Z = 6
RMS = 0.2  # Debye-Waller regime


def build_edge_list(L):
    edges = []
    for x in range(L):
        for y in range(L):
            for z in range(L):
                i = x * L * L + y * L + z
                for dx, dy, dz in [(1,0,0), (0,1,0), (0,0,1)]:
                    nx, ny, nz = (x+dx) % L, (y+dy) % L, (z+dz) % L
                    j = nx * L * L + ny * L + nz
                    edges.append((min(i,j), max(i,j)))
    return np.array(edges, dtype=np.int64)


def energy_and_force(phi, pi_phi, edges, xi):
    a = edges[:, 0]; b = edges[:, 1]
    dphi = phi[a] - phi[b] + xi
    E_phi = -(BETA_PHI / Z) * np.cos(dphi).sum()
    T_phi = 0.5 * (pi_phi * pi_phi).sum() / MU_PHI
    H = T_phi + E_phi
    sin_dphi = np.sin(dphi)
    coeff = (BETA_PHI / Z) * sin_dphi
    N = phi.shape[0]
    force = np.zeros(N)
    np.add.at(force, a, -coeff)
    np.add.at(force, b, +coeff)
    return H, T_phi, E_phi, force


def yoshida4_step(phi, pi_phi, edges, xi, dt):
    w1 = 1.0 / (2.0 - 2.0**(1.0/3.0))
    w0 = 1.0 - 2.0 * w1
    for w in [w1, w0, w1]:
        dt_sub = w * dt
        _, _, _, f = energy_and_force(phi, pi_phi, edges, xi)
        pi_phi = pi_phi + 0.5 * dt_sub * f
        phi = phi + dt_sub * pi_phi / MU_PHI
        phi = (phi + np.pi) % (2 * np.pi) - np.pi
        _, _, _, f = energy_and_force(phi, pi_phi, edges, xi)
        pi_phi = pi_phi + 0.5 * dt_sub * f
    return phi, pi_phi


def run_trial(rms, tau_c, seed):
    """Run with Ornstein-Uhlenbeck edge noise, correlation time tau_c (lu)."""
    rng = np.random.default_rng(seed)
    N = L**3
    edges = build_edge_list(L)
    n_edges = edges.shape[0]
    phi = rng.normal(0, 0.1, size=N)
    pi_phi = rng.normal(0, 0.05, size=N) * np.sqrt(MU_PHI)

    # Initialize xi at stationary distribution
    if rms == 0:
        xi = np.zeros(n_edges)
        decay = 1.0
        sigma_innov = 0.0
    else:
        xi = rng.normal(0, rms, size=n_edges)
        decay = np.exp(-DT / tau_c) if tau_c > 0 else 0.0
        sigma_innov = rms * np.sqrt(max(1.0 - decay**2, 0.0))

    H_list, L_list, T_list = [], [], []
    xi_var_list = []
    xi_autocorr_list = []
    xi_initial = xi.copy()
    n_burn = int(0.25 * N_STEPS)
    for step in range(N_STEPS):
        # Evolve xi via OU
        if rms > 0 and tau_c < 1e9:
            innov = rng.normal(0, sigma_innov, size=n_edges)
            xi = decay * xi + innov
        phi, pi_phi = yoshida4_step(phi, pi_phi, edges, xi, DT)
        if step >= n_burn and step % 10 == 0:
            H, T, _, _ = energy_and_force(phi, pi_phi, edges, xi)
            H_list.append(H)
            T_list.append(T)
            if rms > 0:
                xi_var_list.append(xi.var())
                xi_autocorr_list.append(float(np.mean(xi * xi_initial) / max(xi_initial.var(), 1e-12)))

    H_arr = np.array(H_list); T_arr = np.array(T_list)
    H_mean = float(H_arr.mean()); T_mean = float(T_arr.mean())
    L_val = 2 * T_mean - H_mean
    H_drift = float((H_arr.max() - H_arr.min()) / max(abs(H_mean), 1.0) * 100)
    return {
        'rms': rms, 'tau_c': tau_c, 'seed': seed,
        'H_mean': H_mean, 'T_mean': T_mean, 'L_invariant': L_val,
        'H_drift_pct': H_drift,
        'xi_var_effective': float(np.mean(xi_var_list)) if xi_var_list else 0.0,
        'xi_autocorr_final': xi_autocorr_list[-1] if xi_autocorr_list else None,
    }


def main():
    print("=" * 78)
    print("QNG-CPU-095: Edge OU temporal correlation probe")
    print("=" * 78)
    print(f"  L={L}, beta_phi={BETA_PHI}, T_sim={T_SIM}, dt={DT}")
    print(f"  Fixed rms={RMS}; scan tau_c in {{0.1, 0.5, 1, 2, 5, 10, 50, 1000}} lu")
    print()

    # Baseline
    r0 = run_trial(0.0, 1.0, 42)
    L0 = r0['L_invariant']
    print(f"  Baseline <L>_0 = {L0:.4f} (XY ground prediction = {L**3 * BETA_PHI / 2:.2f})")
    print()

    tau_values = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 1000.0]

    print(f"  {'tau_c':>8} {'<L>':>9} {'shift':>10} {'shift/L0':>12} {'var_eff':>10} {'autocorr':>10} {'H_drift%':>9}")

    results = [r0]
    for tau_c in tau_values:
        Ls, vars_e, ac, hd = [], [], [], []
        for s in [100, 101]:
            r = run_trial(RMS, tau_c, s)
            results.append(r)
            Ls.append(r['L_invariant'])
            vars_e.append(r['xi_var_effective'])
            if r['xi_autocorr_final'] is not None:
                ac.append(r['xi_autocorr_final'])
            hd.append(r['H_drift_pct'])
        Lmean = np.mean(Ls)
        shift = Lmean - L0
        print(f"  {tau_c:>8.2f} {Lmean:>9.3f} {shift:>+10.4f} {shift/L0:>+12.6f} "
              f"{np.mean(vars_e):>10.4f} {np.mean(ac) if ac else 0:>+10.4f} {np.mean(hd):>9.3f}")

    # Analysis: is shift a non-trivial function of tau_c?
    print()
    print("=" * 78)
    print("ANALYSIS: shift vs tau_c at fixed rms")
    print("=" * 78)

    taus = sorted(set(r['tau_c'] for r in results if r['rms'] > 0))
    shift_by_tau = {}
    for tau in taus:
        Ls = [r['L_invariant'] for r in results if r['rms'] > 0 and r['tau_c'] == tau]
        shift_by_tau[tau] = (np.mean(Ls) - L0) / L0

    # Debye-Waller prediction (quenched limit, tau_c -> inf):
    # For each independent xi_ij, <cos(dphi + xi)> = <cos(dphi)> * exp(-Var(xi)/2)
    # Shift factor = exp(-Var/2) - 1 ~ -Var/2 at small Var
    dw_pred = -(RMS**2) / 2
    print(f"  Debye-Waller quenched prediction (rms={RMS}): shift/L0 ~ {dw_pred:.6f}")
    print()
    print(f"  {'tau_c':>8} {'shift/L0':>12} {'vs DW':>10} {'regime':>20}")
    for tau in sorted(shift_by_tau):
        ratio = shift_by_tau[tau] / dw_pred if dw_pred != 0 else 0
        if tau < 0.5:
            regime = "motional narrowing"
        elif tau > 100:
            regime = "quenched"
        else:
            regime = "dynamic"
        print(f"  {tau:>8.2f} {shift_by_tau[tau]:>+12.6f} {ratio:>+10.3f} {regime:>20}")

    # Look for saturation / plateau
    print()
    print("INTERPRETATION:")
    print("  - Smooth monotone in tau_c: classical motional narrowing, NO hbar")
    print("  - Plateau/saturation at universal value: hbar candidate -> investigate")
    print("  - All ratios near 1.0: Debye-Waller at all tau_c (no tau_c structure)")

    with open(AUDIT / "report.json", 'w') as f:
        json.dump({
            'L': L, 'beta_phi': BETA_PHI, 'T_sim': T_SIM, 'rms': RMS,
            'L_0': L0, 'tau_values': tau_values,
            'dw_pred': dw_pred,
            'shift_by_tau': {str(k): v for k, v in shift_by_tau.items()},
            'results': results,
        }, f, indent=2, default=float)
    print(f"\n  Report: {AUDIT / 'report.json'}")


if __name__ == "__main__":
    main()
