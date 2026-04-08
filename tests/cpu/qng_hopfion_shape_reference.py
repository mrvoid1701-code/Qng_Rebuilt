from __future__ import annotations

"""QNG-CPU-070: Hopfion Q=1 vs ring Q=0 — sigma_m radial profile shape measurement.

CPU-069: total M nearly constant (ring 99.91%, Hopfion 99.98%) over 100k steps.
This test measures SHAPE: does the depletion tube broaden while total mass is conserved?

Profile measurement: sigma_m(x, RY, z) slice through ring equator (y=RY plane).
Radial profile: sigma_m vs distance from ring center (x=RX, z=RZ).
"""

import json, math, time
from pathlib import Path

try:
    import cupy as cp
    xp = cp
    DEVICE = "GPU (CuPy)"
except ImportError:
    import numpy as cp  # type: ignore
    xp = cp
    DEVICE = "CPU (numpy fallback)"

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-hopfion-shape-v1"

L=20; N=L*L*L; PHASE1=300; PHASE2_DISS=1000; PHASE2_CONS=50000
SIGMA_REF=0.5; ALPHA=0.005; BETA=0.35; BETA_PHI=0.02
DELTA=0.20; CHI_DECAY=0.020; CHI_REL=0.35; GAMMA_PHI=0.10
K_BACK=0.10; K_GM=0.001; RING_R=5.0
RX=L/2.; RY=L/2.; RZ=L/2.
DT_CONS=0.005
RECORD_EVERY=10000
PI = math.pi

def make_coord_grids():
    xs = xp.arange(L, dtype=xp.float32)
    x3 = xp.broadcast_to(xs[:, None, None], (L, L, L))
    y3 = xp.broadcast_to(xs[None, :, None], (L, L, L))
    z3 = xp.broadcast_to(xs[None, None, :], (L, L, L))
    return x3, y3, z3

def _mi_arr(d):
    return d - xp.round(d / L) * L

def wrap_arr(a):
    a = a % (2 * PI)
    return xp.where(a > PI, a - 2 * PI, a)

def adiff_arr(a, b):
    return wrap_arr(a - b)

def nb6(arr):
    return (xp.roll(arr,1,0)+xp.roll(arr,-1,0)+
            xp.roll(arr,1,1)+xp.roll(arr,-1,1)+
            xp.roll(arr,1,2)+xp.roll(arr,-1,2)) / 6.0

def nb6_sum(arr):
    return (xp.roll(arr,1,0)+xp.roll(arr,-1,0)+
            xp.roll(arr,1,1)+xp.roll(arr,-1,1)+
            xp.roll(arr,1,2)+xp.roll(arr,-1,2))

def init_phi_gpu(q_twist):
    x3,y3,z3 = make_coord_grids()
    dx=_mi_arr(x3-RX); dy=_mi_arr(y3-RY); dz=_mi_arr(z3-RZ)
    rho=xp.sqrt(dx*dx+dy*dy)
    return wrap_arr(xp.arctan2(dz,rho-RING_R) + q_twist*xp.arctan2(dy,dx))

def dis_arr(phi):
    sx=nb6(xp.cos(phi)); sy=nb6(xp.sin(phi))
    return xp.maximum(xp.zeros_like(phi), 1.0-xp.sqrt(sx*sx+sy*sy))

def _phi_align(sm, phi):
    tw=nb6_sum(sm)
    safe=xp.where(tw>1e-10,tw,xp.ones_like(tw))
    sx2=nb6_sum(sm*xp.cos(phi))/safe
    sy2=nb6_sum(sm*xp.sin(phi))/safe
    pm=xp.where(tw>1e-10, xp.arctan2(sy2,sx2), phi)
    return wrap_arr(phi + BETA_PHI*adiff_arr(pm,phi))

def step_dissipative(sg,sm,chi,phi):
    sgb=nb6(sg); smb=nb6(sm)
    sg=xp.clip(sg+ALPHA*(SIGMA_REF-sg)+BETA*(sgb-sg)+K_BACK*chi-K_GM*(SIGMA_REF-sm),0.,1.)
    sm=xp.clip(sm+ALPHA*(SIGMA_REF-sm)+BETA*(smb-sm)-GAMMA_PHI*dis_arr(phi)*sm,0.,1.)
    chi=chi*(1-CHI_DECAY)+CHI_REL*(sgb-sg)+DELTA*(SIGMA_REF-sg)
    return sg,sm,chi,_phi_align(sm,phi)

def step_conservative(sg,sm,chi,phi):
    sgb=nb6(sg); smb=nb6(sm)
    sg=xp.clip(sg+DT_CONS*(K_BACK*chi+CHI_REL*(sgb-sg)+DELTA*(sg-SIGMA_REF)),0.,1.)
    sm=xp.clip(sm+DT_CONS*BETA*(smb-sm),0.,1.)
    chi=chi+DT_CONS*(-ALPHA*(sg-SIGMA_REF)+BETA*6*(sgb-sg)-DELTA*chi)
    return sg,sm,chi,_phi_align(sm,phi)

def ring_mass(sm):
    val=xp.sum(xp.maximum(xp.zeros_like(sm),SIGMA_REF-sm))
    return float(val.get() if xp.__name__=='cupy' else val)

def get_numpy(arr):
    if xp.__name__=='cupy': return arr.get()
    return np.array(arr)

def measure_profile(sm, label, t):
    """
    Measure sigma_m along the ring tube cross-section.

    Two profiles:
    1. Poloidal cross-section: sigma_m(x, RY, z) — xz plane through y=RY
       For each point, compute distance from ring centerline (torus axis at z=RZ,
       the ring lives at rho=RING_R from z-axis).
    2. Toroidal slice: sigma_m(x, RY, RZ) — along x-axis through ring center plane
    """
    sm_np = get_numpy(sm)

    # --- Profile 1: xz slice through y=int(RY) ---
    iy = int(round(RY))
    xz_slice = sm_np[:, iy, :]  # shape (L, L)

    # For each node (x,z) in this slice, compute:
    # rho = sqrt((x-RX)^2) — but in the xz plane at y=RY, rho = |x-RX| (distance from z-axis)
    # Actually rho = sqrt((x-RX)^2 + (RY-RY)^2) = |x-RX|, and z-RZ is the z-coordinate
    # The ring tube center is at (rho=RING_R, z=RZ), so distance from tube center:
    # d_tube = sqrt((rho - RING_R)^2 + (z-RZ)^2) where rho = |x-RX|

    xs = np.arange(L)
    zs = np.arange(L)
    xx, zz = np.meshgrid(xs, zs, indexing='ij')

    dx = xx - RX; dz = zz - RZ
    # min-image
    dx = dx - np.round(dx/L)*L; dz = dz - np.round(dz/L)*L

    rho = np.abs(dx)  # distance from z-axis in xz plane
    d_tube = np.sqrt((rho - RING_R)**2 + dz**2)  # distance from ring tube center

    # Bin by d_tube
    r_max = 8; n_bins = 16
    bin_edges = np.linspace(0, r_max, n_bins+1)
    bin_centers = 0.5*(bin_edges[:-1]+bin_edges[1:])
    profile = np.zeros(n_bins)
    counts = np.zeros(n_bins)
    for i in range(L):
        for k in range(L):
            d = d_tube[i, k]
            b = int(d / r_max * n_bins)
            if 0 <= b < n_bins:
                profile[b] += xz_slice[i, k]
                counts[b] += 1
    with np.errstate(invalid='ignore'):
        profile = np.where(counts>0, profile/counts, SIGMA_REF)

    # Tube center (d_tube ~ 0): min sigma_m
    min_sm = float(np.min(xz_slice))
    # FWHM of depletion: find width of region below (SIGMA_REF + min_sm)/2
    threshold = (SIGMA_REF + min_sm) / 2.
    depletion = profile < threshold
    if depletion.any():
        first = int(np.argmax(depletion))
        last = int(len(depletion) - 1 - np.argmax(depletion[::-1]))
        fwhm = (last - first + 1) * (r_max / n_bins)
    else:
        fwhm = 0.

    M = ring_mass(sm)
    print(f"    t={t:6d}: M={M:.1f}  min_sm={min_sm:.4f}  tube_FWHM={fwhm:.2f}  "
          f"core={profile[0]:.4f}", flush=True)

    return {
        "t": t,
        "M": round(M, 1),
        "min_sigma_m": round(float(min_sm), 4),
        "tube_fwhm": round(float(fwhm), 3),
        "core_sigma_m": round(float(profile[0]), 4),
        "profile_d": [round(float(x), 3) for x in bin_centers.tolist()],
        "profile_sm": [round(float(x), 4) for x in profile.tolist()]
    }

def build_structure(q_twist):
    phi=init_phi_gpu(q_twist)
    sg=xp.full((L,L,L),SIGMA_REF,dtype=xp.float32)
    sm=xp.full((L,L,L),SIGMA_REF,dtype=xp.float32)
    chi=xp.zeros((L,L,L),dtype=xp.float32)
    for _ in range(PHASE1):
        sgb=nb6(sg); smb=nb6(sm)
        sg=xp.clip(sg+ALPHA*(SIGMA_REF-sg)+BETA*(sgb-sg),0.,1.)
        sm=xp.clip(sm+ALPHA*(SIGMA_REF-sm)+BETA*(smb-sm),0.,1.)
        chi=chi*(1-CHI_DECAY)+CHI_REL*(sgb-sg)+DELTA*(SIGMA_REF-sg)
        phi=_phi_align(sm,phi)
    for t in range(1,PHASE2_DISS+1):
        sg,sm,chi,phi=step_dissipative(sg,sm,chi,phi)
    return sg,sm,chi,phi

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    args=p.parse_args(); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)

    tau_ring = RING_R**2 * 6 / (BETA*DT_CONS)
    print("QNG-CPU-070: Hopfion shape measurement — sigma_m radial profile")
    print(f"Device: {DEVICE}")
    print(f"CONS={PHASE2_CONS}  tau_ring={tau_ring:.0f}  ({PHASE2_CONS/tau_ring:.2f}x)")
    print()

    results={}
    for label,q_twist in [("ring_Q0",0),("hopfion_Q1",1)]:
        print(f"Building {label}...", flush=True)
        sg,sm,chi,phi=build_structure(q_twist)
        M0=ring_mass(sm)
        print(f"  M0={M0:.1f}")

        snapshots=[]
        # Measure initial profile
        print(f"  Profile snapshots:")
        snap=measure_profile(sm,label,0)
        snap["M0"]=round(M0,1)
        snapshots.append(snap)
        fwhm0=snap["tube_fwhm"]; min_sm0=snap["min_sigma_m"]

        print(f"  Running {PHASE2_CONS} conservative steps...", flush=True)
        t0_=time.time()
        for t in range(1,PHASE2_CONS+1):
            sg,sm,chi,phi=step_conservative(sg,sm,chi,phi)
            if t%RECORD_EVERY==0:
                snap=measure_profile(sm,label,t)
                snapshots.append(snap)

        M_final=ring_mass(sm)
        snap_final=snapshots[-1]
        fwhm_final=snap_final["tube_fwhm"]
        min_sm_final=snap_final["min_sigma_m"]

        c1=fwhm_final < 1.5*fwhm0 if fwhm0>0 else True
        c2=min_sm_final > 0.5*min_sm0 if min_sm0>0 else True

        print(f"  Initial: FWHM={fwhm0:.2f}  min_sm={min_sm0:.4f}")
        print(f"  Final:   FWHM={fwhm_final:.2f}  min_sm={min_sm_final:.4f}  "
              f"M={M_final:.1f} ({100*M_final/M0:.2f}%)")
        print(f"  Check 1 (FWHM < 1.5x): {fwhm_final:.2f} < {1.5*fwhm0:.2f} -> "
              f"{'PASS' if c1 else 'FAIL'}")
        print(f"  Check 2 (min_sm > 0.5x): {min_sm_final:.4f} > {0.5*min_sm0:.4f} -> "
              f"{'PASS' if c2 else 'FAIL'}")

        results[label]={"q_twist":q_twist,"M0":round(M0,1),
                        "M_final":round(M_final,1),
                        "fwhm_initial":fwhm0,"fwhm_final":fwhm_final,
                        "min_sm_initial":min_sm0,"min_sm_final":min_sm_final,
                        "check_fwhm":c1,"check_depth":c2,
                        "snapshots":snapshots}
        print()

    print("="*70)
    r0=results["ring_Q0"]; r1=results["hopfion_Q1"]
    c1=r0["check_fwhm"] and r1["check_fwhm"]
    c2=r0["check_depth"] and r1["check_depth"]
    c3_info=r1["fwhm_initial"] > r0["fwhm_initial"]  # Hopfion wider?

    print(f"Ring Q=0:    FWHM {r0['fwhm_initial']:.2f} -> {r0['fwhm_final']:.2f}  "
          f"min_sm {r0['min_sm_initial']:.4f} -> {r0['min_sm_final']:.4f}")
    print(f"Hopfion Q=1: FWHM {r1['fwhm_initial']:.2f} -> {r1['fwhm_final']:.2f}  "
          f"min_sm {r1['min_sm_initial']:.4f} -> {r1['min_sm_final']:.4f}")
    print()
    print(f"Check 1 (tube width stable): {'PASS' if c1 else 'FAIL'}")
    print(f"Check 2 (depletion depth stable): {'PASS' if c2 else 'FAIL'}")
    print(f"Check 3 (Hopfion wider than ring, info): {r1['fwhm_initial']:.2f} > "
          f"{r0['fwhm_initial']:.2f} -> {'YES' if c3_info else 'NO'}")

    overall="pass" if (c1 and c2) else "fail"
    print(f"\nqng_hopfion_shape_reference: {overall.upper()}")

    report={"test_id":"QNG-CPU-070","decision":overall,"device":DEVICE,
            "cons_steps":PHASE2_CONS,"dt":DT_CONS,
            "tau_ring":round(tau_ring),
            "checks":{"fwhm_stable":c1,"depth_stable":c2,"hopfion_wider":c3_info},
            "ring_Q0":r0,"hopfion_Q1":r1}
    rp=out/"report.json"
    with open(rp,"w") as f: json.dump(report,f,indent=2)
    print(f"\nReport: {rp}")
    return 0 if overall=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
