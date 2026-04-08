from __future__ import annotations

"""QNG-CPU-068: Hopfion Q=1 vs ring Q=0 — ultra-long conservative run (15,000 steps).

GPU-accelerated via CuPy (falls back to numpy). Vectorized: no Python loop over nodes.

Einstein review (2026-04-08): CPU-067's 1000 steps = 7% of true diffusion timescale
  tau_diff = R²/(BETA*DT) = 25/(0.35*0.005) = 14,286 steps.
Need 15,000 steps (1.05× tau_diff) to test whether dissolution actually occurs.
"""

import json, math, sys, time
from pathlib import Path

try:
    import cupy as cp
    xp = cp
    DEVICE = "GPU (CuPy)"
except ImportError:
    import numpy as cp  # type: ignore
    xp = cp
    DEVICE = "CPU (numpy fallback)"

import numpy as np  # always available for I/O

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-hopfion-ultralong-v1"

L=20; N=L*L*L; PHASE1=300; PHASE2_DISS=1000; PHASE2_CONS=15000
SIGMA_REF=0.5; ALPHA=0.005; BETA=0.35; BETA_PHI=0.02
DELTA=0.20; CHI_DECAY=0.020; CHI_REL=0.35; GAMMA_PHI=0.10
K_BACK=0.10; K_GM=0.001; RING_R=5.0
RX=L/2.; RY=L/2.; RZ=L/2.
DT_CONS=0.005
RECORD_EVERY=500
PI = math.pi

# ── geometry helpers ──────────────────────────────────────────────────────────

def make_coord_grids():
    """Return (x, y, z) grids of shape (L,L,L) on xp device."""
    xs = xp.arange(L, dtype=xp.float32)
    x3 = xp.broadcast_to(xs[:, None, None], (L, L, L))
    y3 = xp.broadcast_to(xs[None, :, None], (L, L, L))
    z3 = xp.broadcast_to(xs[None, None, :], (L, L, L))
    return x3, y3, z3

def _mi_arr(d):
    """Minimum-image for array d on periodic lattice of size L."""
    d = d - xp.round(d / L) * L
    return d

def wrap_arr(a):
    a = a % (2 * PI)
    a = xp.where(a > PI, a - 2 * PI, a)
    return a

def adiff_arr(a, b):
    return wrap_arr(a - b)

def nb6(arr):
    """6-neighbor average on (L,L,L) array with periodic BCs."""
    return (xp.roll(arr, 1, 0) + xp.roll(arr, -1, 0) +
            xp.roll(arr, 1, 1) + xp.roll(arr, -1, 1) +
            xp.roll(arr, 1, 2) + xp.roll(arr, -1, 2)) / 6.0

def nb6_sum(arr):
    """6-neighbor SUM (not average)."""
    return (xp.roll(arr, 1, 0) + xp.roll(arr, -1, 0) +
            xp.roll(arr, 1, 1) + xp.roll(arr, -1, 1) +
            xp.roll(arr, 1, 2) + xp.roll(arr, -1, 2))

# ── initialisation ────────────────────────────────────────────────────────────

def init_phi_gpu(q_twist):
    """Vectorized Hopfion initial condition on GPU."""
    x3, y3, z3 = make_coord_grids()
    dx = _mi_arr(x3 - RX)
    dy = _mi_arr(y3 - RY)
    dz = _mi_arr(z3 - RZ)
    rho = xp.sqrt(dx*dx + dy*dy)
    poloidal = xp.arctan2(dz, rho - RING_R)
    toroidal = xp.arctan2(dy, dx)
    return wrap_arr(poloidal + q_twist * toroidal)

def dis_arr(phi):
    """Disorder field D_i = max(0, 1 - |<e^{i phi}>|) for all nodes."""
    cphi = xp.cos(phi); sphi = xp.sin(phi)
    sx = nb6(cphi); sy = nb6(sphi)
    return xp.maximum(xp.zeros_like(phi), 1.0 - xp.sqrt(sx*sx + sy*sy))

# ── dynamics ──────────────────────────────────────────────────────────────────

def step_dissipative(sg, sm, chi, phi):
    sgb = nb6(sg); smb = nb6(sm)
    dsg = ALPHA*(SIGMA_REF - sg) + BETA*(sgb - sg) + K_BACK*chi - K_GM*(SIGMA_REF - sm)
    sg = xp.clip(sg + dsg, 0., 1.)
    dsm = ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm) - GAMMA_PHI*dis_arr(phi)*sm
    sm = xp.clip(sm + dsm, 0., 1.)
    chi = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA*(SIGMA_REF - sg)
    sm_cos = sm * xp.cos(phi); sm_sin = sm * xp.sin(phi)
    tw = nb6_sum(sm)
    sx2 = nb6_sum(sm_cos) / xp.where(tw > 1e-10, tw, xp.ones_like(tw))
    sy2 = nb6_sum(sm_sin) / xp.where(tw > 1e-10, tw, xp.ones_like(tw))
    pm = xp.arctan2(sy2, sx2)
    pm = xp.where(tw > 1e-10, pm, phi)
    phi = wrap_arr(phi + BETA_PHI * adiff_arr(pm, phi))
    return sg, sm, chi, phi

def step_conservative(sg, sm, chi, phi):
    """Conservative: no ALPHA in sigma, no Channel F, no CHI_DECAY."""
    sgb = nb6(sg); smb = nb6(sm)
    # sigma_g
    ds = K_BACK*chi + CHI_REL*(sgb - sg) + DELTA*(sg - SIGMA_REF)
    sg = xp.clip(sg + DT_CONS*ds, 0., 1.)
    # sigma_m: pure diffusion only (conserves total mass)
    dm = BETA*(smb - sm)
    sm = xp.clip(sm + DT_CONS*dm, 0., 1.)
    # chi
    dc = -ALPHA*(sg - SIGMA_REF) + BETA*6*(sgb - sg) - DELTA*chi
    chi = chi + DT_CONS*dc
    # phi alignment
    sm_cos = sm * xp.cos(phi); sm_sin = sm * xp.sin(phi)
    tw = nb6_sum(sm)
    sx2 = nb6_sum(sm_cos) / xp.where(tw > 1e-10, tw, xp.ones_like(tw))
    sy2 = nb6_sum(sm_sin) / xp.where(tw > 1e-10, tw, xp.ones_like(tw))
    pm = xp.arctan2(sy2, sx2)
    pm = xp.where(tw > 1e-10, pm, phi)
    phi = wrap_arr(phi + BETA_PHI * adiff_arr(pm, phi))
    return sg, sm, chi, phi

def ring_mass(sm):
    """Total sigma_m depletion mass."""
    val = xp.sum(xp.maximum(xp.zeros_like(sm), SIGMA_REF - sm))
    if xp.__name__ == 'cupy':
        return float(val.get())
    return float(val)

# ── build structure ───────────────────────────────────────────────────────────

def build_structure(q_twist, label):
    """Phase 1 (300) + Phase 2 dissipative (1000) to form fully developed structure."""
    phi = init_phi_gpu(q_twist)
    sg = xp.full((L, L, L), SIGMA_REF, dtype=xp.float32)
    sm = xp.full((L, L, L), SIGMA_REF, dtype=xp.float32)
    chi = xp.zeros((L, L, L), dtype=xp.float32)

    print(f"  Phase 1 ({PHASE1} steps)...", flush=True)
    for _ in range(PHASE1):
        sgb = nb6(sg); smb = nb6(sm)
        sg = xp.clip(sg + ALPHA*(SIGMA_REF - sg) + BETA*(sgb - sg), 0., 1.)
        sm = xp.clip(sm + ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm), 0., 1.)
        chi = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA*(SIGMA_REF - sg)
        sm_cos = sm*xp.cos(phi); sm_sin = sm*xp.sin(phi)
        tw = nb6_sum(sm)
        sx2 = nb6_sum(sm_cos)/xp.where(tw>1e-10,tw,xp.ones_like(tw))
        sy2 = nb6_sum(sm_sin)/xp.where(tw>1e-10,tw,xp.ones_like(tw))
        pm = xp.where(tw>1e-10, xp.arctan2(sy2,sx2), phi)
        phi = wrap_arr(phi + BETA_PHI*adiff_arr(pm, phi))

    print(f"  Phase 2 dissipative ({PHASE2_DISS} steps)...", flush=True)
    t0 = time.time()
    for t in range(1, PHASE2_DISS + 1):
        sg, sm, chi, phi = step_dissipative(sg, sm, chi, phi)
        if t % 200 == 0:
            M = ring_mass(sm)
            print(f"    diss t={t:5d}: M={M:7.1f}  ({time.time()-t0:.0f}s elapsed)", flush=True)

    M0 = ring_mass(sm)
    print(f"  Fully formed: M0={M0:.1f}", flush=True)
    return sg, sm, chi, phi, M0

def half_life(traj, M0):
    for pt in traj:
        if pt["M"] < M0 / 2.: return pt["t"]
    return None

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = p.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    tau_diff = RING_R**2 / (BETA * DT_CONS)
    print("QNG-CPU-068: Hopfion Q=1 vs ring Q=0 -- ultra-long conservative run")
    print(f"Device: {DEVICE}")
    print(f"L={L}  R={RING_R}  CONS steps={PHASE2_CONS}  DT={DT_CONS}  total_time={PHASE2_CONS*DT_CONS:.1f}")
    print(f"True diffusion timescale: R^2/(BETA*DT) = {tau_diff:.0f} steps  ({PHASE2_CONS/tau_diff:.2f}x)")
    print()

    results = {}
    for label, q_twist in [("ring_Q0", 0), ("hopfion_Q1", 1)]:
        print(f"Building {label} (q_twist={q_twist})...", flush=True)
        sg, sm, chi, phi, M0 = build_structure(q_twist, label)

        print(f"  Running {PHASE2_CONS} conservative steps...", flush=True)
        t0 = time.time()
        traj = []
        for t in range(1, PHASE2_CONS + 1):
            sg, sm, chi, phi = step_conservative(sg, sm, chi, phi)
            if t % RECORD_EVERY == 0:
                M = ring_mass(sm)
                frac = M / M0 if M0 > 0 else 0.
                traj.append({"t": t, "M": round(M, 1), "frac": round(frac, 4)})
                if t % 2000 == 0:
                    elapsed = time.time() - t0
                    rate = t / elapsed
                    remaining = (PHASE2_CONS - t) / rate
                    print(f"  cons t={t:6d}: M={M:7.1f}  ({100*frac:.1f}%)  "
                          f"[{elapsed:.0f}s  ~{remaining:.0f}s left]", flush=True)

        M_final = ring_mass(sm)
        hl = half_life(traj, M0)
        dissolution = M_final < 0.99 * M0
        print(f"  Final: M={M_final:.1f} ({100*M_final/M0:.2f}%)  "
              f"half-life: {hl if hl else '>'+str(PHASE2_CONS)}  "
              f"dissolved: {dissolution}")
        results[label] = {
            "q_twist": q_twist, "M0": round(M0, 1),
            "M_final": round(M_final, 1),
            "frac_final": round(M_final / M0, 4) if M0 > 0 else 0,
            "half_life_steps": hl,
            "dissolved_1pct": dissolution,
            "traj": traj
        }
        print()

    print("=" * 70)
    r0 = results["ring_Q0"]; r1 = results["hopfion_Q1"]

    # Check 1: any dissolution detected (informational)
    c1_ring = r0["dissolved_1pct"]; c1_hopf = r1["dissolved_1pct"]

    # Check 2: Hopfion >= ring mass at T=PHASE2_CONS
    c2 = r1["M_final"] >= r0["M_final"]

    # Check 3: half-life comparison
    hl0 = r0["half_life_steps"]; hl1 = r1["half_life_steps"]
    hl0_eff = hl0 if hl0 else PHASE2_CONS + 1
    hl1_eff = hl1 if hl1 else PHASE2_CONS + 1
    c3 = hl1_eff >= hl0_eff

    tau_diff = RING_R**2 / (BETA * DT_CONS)
    print(f"Ring Q=0:    M0={r0['M0']:.1f} -> M_final={r0['M_final']:.1f} "
          f"({100*r0['frac_final']:.2f}%)  dissolved: {c1_ring}  "
          f"half-life: {hl0 if hl0 else '>'+str(PHASE2_CONS)}")
    print(f"Hopfion Q=1: M0={r1['M0']:.1f} -> M_final={r1['M_final']:.1f} "
          f"({100*r1['frac_final']:.2f}%)  dissolved: {c1_hopf}  "
          f"half-life: {hl1 if hl1 else '>'+str(PHASE2_CONS)}")
    print()
    print(f"Diffusion timescale: {tau_diff:.0f} steps  "
          f"(ran {PHASE2_CONS/tau_diff:.2f}x tau_diff)")
    print(f"Check 1 (dissolution, info): ring={c1_ring}  hopfion={c1_hopf}")
    print(f"Check 2 (hopfion >= ring mass): {r1['M_final']:.1f} >= {r0['M_final']:.1f} "
          f"-> {'PASS' if c2 else 'FAIL'}")
    print(f"Check 3 (hopfion half-life >= ring): {hl1_eff} >= {hl0_eff} "
          f"-> {'PASS' if c3 else 'FAIL'}")

    overall = "pass" if c3 else "fail"
    print(f"\nqng_hopfion_ultralong_reference: {overall.upper()}")

    report = {
        "test_id": "QNG-CPU-068", "decision": overall,
        "device": DEVICE,
        "cons_steps": PHASE2_CONS, "dt": DT_CONS,
        "total_time": PHASE2_CONS * DT_CONS,
        "tau_diff_steps": round(tau_diff),
        "tau_diff_ratio": round(PHASE2_CONS / tau_diff, 3),
        "checks": {
            "ring_dissolved_1pct": c1_ring,
            "hopfion_dissolved_1pct": c1_hopf,
            "hopfion_ge_ring_mass": c2,
            "hopfion_halflife_ge_ring": c3
        },
        "ring_Q0": r0, "hopfion_Q1": r1
    }
    rp = out / "report.json"
    with open(rp, "w") as f: json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0 if overall == "pass" else 1

if __name__ == "__main__": raise SystemExit(main())
