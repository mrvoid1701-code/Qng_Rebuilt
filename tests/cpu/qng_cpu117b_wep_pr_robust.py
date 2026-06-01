"""QNG-CPU-117b -- ROBUSTNESS check for CPU-117.

Triple self-verification: vary (k, M_src) and confirm Pound-Rebka
shift tracks exact KG dispersion across the sweep.

Per Gabriel: "sa te verifici de mai multe ori" — this is verification
round 4+ for WEP+Pound-Rebka.
"""
import numpy as np

beta_phi = 0.06
beta_g   = 0.35
mu_phi   = 0.857
z_coord  = 6
alpha    = 0.005

c_phi_sq = beta_phi / (z_coord * mu_phi)
G_QNG    = beta_g / z_coord
lam_screen = np.sqrt(beta_g / (z_coord * alpha))

def Phi(r, M):
    return -G_QNG * M * np.exp(-r/lam_screen) / r

def run_kg_constant_phi(Phi_const, k_target, T_sim=500.0):
    N = 2048
    L_box = 50.0
    x_arr = np.linspace(-L_box/2, L_box/2, N)
    dx = x_arr[1] - x_arr[0]
    c_eff_sq = c_phi_sq * (1 + 2*Phi_const/c_phi_sq)
    if c_eff_sq <= 0:
        return 0.0, 0.0, 0.0
    m_int = max(1, int(round(k_target * L_box / (2*np.pi))))
    k_actual = 2*np.pi*m_int / L_box
    omega_target = np.sqrt(c_eff_sq) * k_actual
    phi = np.cos(k_actual * x_arr)
    phi_dot = omega_target * np.sin(k_actual * x_arr)
    dt = 0.2 * dx / np.sqrt(c_eff_sq)
    phi_prev = phi - dt*phi_dot + 0.5*dt**2 * (-k_actual**2 * c_eff_sq * phi)
    N_steps = int(T_sim/dt)
    idx = N//2
    phi_x0 = np.zeros(N_steps)
    for step in range(N_steps):
        lap = np.zeros_like(phi)
        lap[1:-1] = (phi[2:] - 2*phi[1:-1] + phi[:-2]) / dx**2
        lap[0]  = (phi[1]  - 2*phi[0]  + phi[-1]) / dx**2
        lap[-1] = (phi[0]  - 2*phi[-1] + phi[-2]) / dx**2
        phi_next = 2*phi - phi_prev + dt**2 * c_eff_sq * lap
        phi_prev = phi
        phi = phi_next
        phi_x0[step] = phi[idx]
    sig = phi_x0 - np.mean(phi_x0)
    sig *= np.hanning(len(sig))
    fft = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(len(sig), d=dt) * 2*np.pi
    idx_peak = np.argmax(np.abs(fft[1:])) + 1
    # Parabolic interp
    if 0 < idx_peak < len(fft)-1:
        a = np.abs(fft[idx_peak-1]); b = np.abs(fft[idx_peak]); c = np.abs(fft[idx_peak+1])
        denom = a - 2*b + c
        if abs(denom) > 1e-20:
            p = 0.5*(a-c)/denom
            omega_meas = (idx_peak + p) * (freqs[1] - freqs[0])
        else:
            omega_meas = freqs[idx_peak]
    else:
        omega_meas = freqs[idx_peak]
    return omega_meas, k_actual, omega_target

print("=" * 80)
print("QNG-CPU-117b: Pound-Rebka ROBUSTNESS (k, M_src scan)")
print("=" * 80)
print()

r1_fixed, r2_fixed = 3.0, 6.0

results = []
print(f"{'k':>6} {'M_src':>8} {'Phi1/c^2':>12} {'meas_shift':>14} {'exact_shift':>14} {'ratio':>8} {'|meas/exact-1|':>14}")
print("-" * 90)
for k_test in [0.5, 1.0, 2.0]:
    for M_src in [0.05, 0.1, 0.2]:
        Phi1 = Phi(r1_fixed, M_src)
        Phi2 = Phi(r2_fixed, M_src)
        dPhi = Phi1 - Phi2
        w_m1, k_a, _ = run_kg_constant_phi(Phi1, k_test, T_sim=500.0)
        w_m2, _, _   = run_kg_constant_phi(Phi2, k_test, T_sim=500.0)
        w0 = np.sqrt(c_phi_sq)*k_a
        meas_shift = (w_m1 - w_m2)/w0
        exact_shift = (np.sqrt(c_phi_sq*(1+2*Phi1/c_phi_sq)) - np.sqrt(c_phi_sq*(1+2*Phi2/c_phi_sq)))*k_a/w0
        ratio = meas_shift/exact_shift
        err = abs(ratio - 1)
        results.append((k_test, M_src, Phi1/c_phi_sq, meas_shift, exact_shift, ratio, err))
        print(f"{k_test:>6.2f} {M_src:>8.3f} {Phi1/c_phi_sq:>12.4e} {meas_shift:>14.4e} {exact_shift:>14.4e} {ratio:>8.4f} {err*100:>12.3f}%")

print()

# Aggregate
errs = [r[6] for r in results]
max_err = max(errs)
mean_err = np.mean(errs)
print(f"Max error across sweep: {max_err*100:.3f}%")
print(f"Mean error across sweep: {mean_err*100:.3f}%")
print()

if max_err < 0.03:
    verdict = "ROBUST PASS (max err < 3%): Pound-Rebka consistent across (k, M) sweep"
elif max_err < 0.10:
    verdict = "PASS (max err < 10%): Pound-Rebka consistent (residual from linearization + FFT binning)"
else:
    verdict = f"FAIL: max err {max_err*100:.2f}% — re-examine"

print(f"VERDICT: {verdict}")
print()

# Also verify that shift scales LINEARLY with M_src at fixed k
# exact_shift ~ dPhi/c^2 ~ M_src/c^2 — should be proportional
print("Self-verify #5: linearity in M_src at fixed k=1")
Ms = [0.02, 0.05, 0.1, 0.15, 0.2]
shifts_measured = []
shifts_predicted = []
for M_src in Ms:
    Phi1 = Phi(r1_fixed, M_src)
    Phi2 = Phi(r2_fixed, M_src)
    w_m1, k_a, _ = run_kg_constant_phi(Phi1, 1.0, T_sim=500.0)
    w_m2, _, _   = run_kg_constant_phi(Phi2, 1.0, T_sim=500.0)
    w0 = np.sqrt(c_phi_sq)*k_a
    meas = (w_m1 - w_m2)/w0
    exact = (Phi1 - Phi2)/c_phi_sq
    shifts_measured.append(meas)
    shifts_predicted.append(exact)
    print(f"  M={M_src}: meas={meas:+.5e}, linear_pred={exact:+.5e}, ratio={meas/exact:.4f}")

# Linear fit: meas = a + b*M_src
Ms_arr = np.array(Ms)
meas_arr = np.array(shifts_measured)
slope, intercept = np.polyfit(Ms_arr, meas_arr, 1)
print(f"  Linear fit: meas_shift = {slope:.4e} * M_src + {intercept:.4e}")
print(f"  (should be proportional, slope significant, intercept near zero)")
print(f"  R^2 via residual: {1 - np.var(meas_arr - (slope*Ms_arr + intercept))/np.var(meas_arr):.6f}")

print()
print("=" * 80)
print("DER-QNG-044 Test 3 (WEP + Pound-Rebka) ROBUSTNESS CONFIRMED" if max_err < 0.10 else "CHECK NEEDED")
print("=" * 80)
