"""
Foundational frequency/light checks for demo-theory.

  E1  wave-packet group velocity -> c_phi (wave-picture sanity)
  E2  dispersion isotropy [100]/[110]/[111] -> lightcone roundness / eta_LV
  E3  standing-wave spectroscopy, L-scan -> box modes (~1/L) vs intrinsic (fixed)
  E6  two-slit phase interference -> fringes in coherence (superposition demo)

NOTE on E1: the classical substrate has no hbar; "E = hbar*omega" needs the
quantum, which is the separate (hard, still-open) hbar program. E1 here only
verifies the CLASSICAL wave kinematics (group velocity = c_phi), not hbar.

ASCII output, CPU/numpy.
"""

import json
import os
import numpy as np

BETA = 0.06
MU = 0.857
DT = 0.2
C2 = BETA / MU

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..",
                       "07_validation", "audits", "demo-foundational-e1e2e3e6-v1")


def laplacian(f):
    lap = np.zeros_like(f)
    for ax in range(f.ndim):
        lap += np.roll(f, 1, axis=ax) + np.roll(f, -1, axis=ax)
    lap -= 2.0 * f.ndim * f
    return lap


def step(phi, v, m2=0.0):
    v += DT * (C2 * laplacian(phi) - m2 * phi)
    phi += DT * v
    return phi, v


# ----------------------------------------------------------------------------
# E1 -- wave-packet group velocity
# ----------------------------------------------------------------------------
def E1_group_velocity(L=128, k0=2*np.pi*8/128, width=10.0, steps=200):
    x = np.arange(L)
    env = np.exp(-((x - L/4.0)**2) / (2*width**2))
    phi = (env * np.cos(k0 * x)).astype(float)
    # right-moving initial condition: v = -c * d phi/dx (approx)
    c = np.sqrt(C2)
    v = -c * (np.roll(phi, -1) - np.roll(phi, 1)) / 2.0
    def centroid(f):
        w = f**2
        return float((x * w).sum() / (w.sum() + 1e-12))
    c0 = centroid(phi)
    for _ in range(steps):
        phi, v = step(phi, v)
    c1 = centroid(phi)
    vg = (c1 - c0) / (steps * DT)
    return {"c_phi": float(c), "group_velocity": float(vg),
            "ratio_vg_to_c": float(vg / c)}


# ----------------------------------------------------------------------------
# E2 -- dispersion isotropy
# ----------------------------------------------------------------------------
def omega_of_plane_wave(L, kvec, steps=600):
    x = np.arange(L)
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    phase = kvec[0]*X + kvec[1]*Y + kvec[2]*Z
    phi = 0.01 * np.cos(phase)
    v = np.zeros_like(phi)
    probe = []
    for t in range(steps):
        v += DT * C2 * laplacian(phi)
        phi += DT * v
        if t % 4 == 0:
            probe.append(phi[0, 0, 0])
    vals = np.array(probe) - np.mean(probe)
    sp = np.abs(np.fft.rfft(vals))
    fr = np.fft.rfftfreq(len(vals), d=4*DT)
    return float(2*np.pi*fr[np.argmax(sp[1:]) + 1])


def E2_isotropy(L=24, n=2):
    k0 = 2*np.pi*n/L
    dirs = {"100": (k0, 0, 0),
            "110": (k0, k0, 0),
            "111": (k0, k0, k0)}
    res = {}
    for name, kv in dirs.items():
        om = omega_of_plane_wave(L, kv)
        kmag = np.sqrt(sum(c**2 for c in kv))
        res[name] = {"omega": om, "kmag": float(kmag),
                     "c": float(om/kmag) if kmag else float("nan")}
    cs = [res[d]["c"] for d in res]
    eta = (max(cs) - min(cs)) / (np.mean(cs) + 1e-12)
    return {"per_direction": res, "eta_LV_anisotropy": float(eta)}


# ----------------------------------------------------------------------------
# E3 -- standing-wave spectroscopy, L-scan
# ----------------------------------------------------------------------------
def E3_standing_modes(Ls=(16, 20, 24), steps=1200):
    out = {}
    for L in Ls:
        rng = np.random.default_rng(0)
        x = np.arange(L)
        X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
        phi = np.zeros((L, L, L))
        for n in range(1, 5):
            phi += rng.normal()*np.cos(2*np.pi*n*X/L)
        v = np.zeros_like(phi)
        probe = []
        for t in range(steps):
            v += DT * C2 * laplacian(phi)
            phi += DT * v
            if t % 2 == 0:
                probe.append(phi[L//3, L//3, L//3])
        vals = np.array(probe) - np.mean(probe)
        sp = np.abs(np.fft.rfft(vals))
        fr = 2*np.pi*np.fft.rfftfreq(len(vals), d=2*DT)
        # top 3 peaks
        idx = np.argsort(sp[1:])[::-1][:3] + 1
        peaks = sorted(float(fr[i]) for i in idx)
        out[str(L)] = {"top_peaks_omega": peaks,
                       "lowest_peak_times_L": float(peaks[0]*L)}
    return out


# ----------------------------------------------------------------------------
# E6 -- two-slit interference (2D)
# ----------------------------------------------------------------------------
def E6_two_slit(L=100, steps=1400):
    phi = np.zeros((L, L))
    v = np.zeros((L, L))
    barrier_col = 28
    screen_col = 52                      # close enough that the wave arrives
    slit_rows = [L//2 - 7, L//2 + 7]
    wall = np.zeros((L, L), dtype=bool)  # True where the wall blocks
    wall[:, barrier_col] = True
    for r in slit_rows:                  # open two slits
        wall[r-2:r+3, barrier_col] = False
    accum = np.zeros(L)
    arrive = int(screen_col / np.sqrt(C2) / DT) + 100
    for t in range(steps):
        phi[:, 0] = np.sin(0.9 * t * DT)  # driven left edge
        v += DT * C2 * laplacian(phi)
        phi += DT * v
        phi[wall] = 0.0                   # hard wall only at wall cells
        v[wall] = 0.0
        if t > arrive:
            accum += phi[:, screen_col]**2
    screen = accum
    s = screen - screen.mean()
    sign = np.sign(s)
    crossings = int(np.sum(np.abs(np.diff(sign)) > 0))
    return {"screen_max": float(screen.max()),
            "approx_fringe_extrema": crossings,
            "fringes_present": bool(crossings >= 3)}


def main():
    print("="*70)
    print("Foundational checks E1/E2/E3/E6")
    print("="*70)

    e1 = E1_group_velocity()
    print("\n[E1] wave-packet group velocity")
    print("    c_phi=%.4f  v_group=%.4f  ratio=%.3f"
          % (e1["c_phi"], e1["group_velocity"], e1["ratio_vg_to_c"]))

    e2 = E2_isotropy()
    print("\n[E2] dispersion isotropy (lightcone roundness)")
    for d, r in e2["per_direction"].items():
        print("    [%s] omega=%.5f  |k|=%.4f  c=%.4f" % (d, r["omega"], r["kmag"], r["c"]))
    print("    eta_LV (anisotropy) = %.4f" % e2["eta_LV_anisotropy"])

    e3 = E3_standing_modes()
    print("\n[E3] standing-wave L-scan (box ~1/L vs intrinsic fixed)")
    for L, r in e3.items():
        print("    L=%s  lowest peak omega=%.4f  (omega*L=%.2f)"
              % (L, r["top_peaks_omega"][0], r["lowest_peak_times_L"]))
    Ls = sorted(int(k) for k in e3)
    prod = [e3[str(L)]["lowest_peak_times_L"] for L in Ls]
    box_like = float(np.std(prod)/ (np.mean(prod)+1e-12))
    print("    omega*L spread across L = %.3f  (small => box modes ~1/L)" % box_like)

    e6 = E6_two_slit()
    print("\n[E6] two-slit phase interference")
    print("    screen max=%.3f  extrema=%d  fringes=%s"
          % (e6["screen_max"], e6["approx_fringe_extrema"], e6["fringes_present"]))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "report.json"), "w") as f:
        json.dump({"E1": e1, "E2": e2, "E3": e3, "E3_box_spread": box_like,
                   "E6": e6}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT_DIR, "report.json"))


if __name__ == "__main__":
    main()
