from __future__ import annotations

"""QNG-CPU-069: Hopfion Q=1 vs ring Q=0 — 100,000 step conservative run (GPU).

CPU-068 ran 15k = 17.5% of corrected tau_ring ≈ 86,000 steps.
This run covers 1.16× tau_ring to detect dissolution at the true timescale.
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
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-hopfion-100k-v1"

L=20; N=L*L*L; PHASE1=300; PHASE2_DISS=1000; PHASE2_CONS=100000
SIGMA_REF=0.5; ALPHA=0.005; BETA=0.35; BETA_PHI=0.02
DELTA=0.20; CHI_DECAY=0.020; CHI_REL=0.35; GAMMA_PHI=0.10
K_BACK=0.10; K_GM=0.001; RING_R=5.0
RX=L/2.; RY=L/2.; RZ=L/2.
DT_CONS=0.005
RECORD_EVERY=2000
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
    cphi=xp.cos(phi); sphi=xp.sin(phi)
    sx=nb6(cphi); sy=nb6(sphi)
    return xp.maximum(xp.zeros_like(phi), 1.0-xp.sqrt(sx*sx+sy*sy))

def _phi_align(sm, phi):
    sm_cos=sm*xp.cos(phi); sm_sin=sm*xp.sin(phi)
    tw=nb6_sum(sm)
    safe=xp.where(tw>1e-10,tw,xp.ones_like(tw))
    sx2=nb6_sum(sm_cos)/safe; sy2=nb6_sum(sm_sin)/safe
    pm=xp.where(tw>1e-10, xp.arctan2(sy2,sx2), phi)
    return wrap_arr(phi + BETA_PHI*adiff_arr(pm,phi))

def step_dissipative(sg,sm,chi,phi):
    sgb=nb6(sg); smb=nb6(sm)
    sg=xp.clip(sg+ALPHA*(SIGMA_REF-sg)+BETA*(sgb-sg)+K_BACK*chi-K_GM*(SIGMA_REF-sm),0.,1.)
    sm=xp.clip(sm+ALPHA*(SIGMA_REF-sm)+BETA*(smb-sm)-GAMMA_PHI*dis_arr(phi)*sm,0.,1.)
    chi=chi*(1-CHI_DECAY)+CHI_REL*(sgb-sg)+DELTA*(SIGMA_REF-sg)
    phi=_phi_align(sm,phi)
    return sg,sm,chi,phi

def step_conservative(sg,sm,chi,phi):
    sgb=nb6(sg); smb=nb6(sm)
    sg=xp.clip(sg+DT_CONS*(K_BACK*chi+CHI_REL*(sgb-sg)+DELTA*(sg-SIGMA_REF)),0.,1.)
    sm=xp.clip(sm+DT_CONS*BETA*(smb-sm),0.,1.)
    chi=chi+DT_CONS*(-ALPHA*(sg-SIGMA_REF)+BETA*6*(sgb-sg)-DELTA*chi)
    phi=_phi_align(sm,phi)
    return sg,sm,chi,phi

def ring_mass(sm):
    val=xp.sum(xp.maximum(xp.zeros_like(sm),SIGMA_REF-sm))
    return float(val.get() if xp.__name__=='cupy' else val)

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
    print(f"  Phase 2 dissipative...", flush=True)
    for t in range(1,PHASE2_DISS+1):
        sg,sm,chi,phi=step_dissipative(sg,sm,chi,phi)
        if t%500==0:
            print(f"    diss t={t}: M={ring_mass(sm):.1f}", flush=True)
    M0=ring_mass(sm)
    print(f"  M0={M0:.1f}", flush=True)
    return sg,sm,chi,phi,M0

def half_life(traj,M0):
    for pt in traj:
        if pt["M"]<M0/2.: return pt["t"]
    return None

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    args=p.parse_args(); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)

    tau_ring = RING_R**2 * 6 / (BETA*DT_CONS)
    print("QNG-CPU-069: Hopfion Q=1 vs ring Q=0 -- 100,000 step conservative run")
    print(f"Device: {DEVICE}")
    print(f"L={L}  CONS={PHASE2_CONS}  DT={DT_CONS}  total_time={PHASE2_CONS*DT_CONS:.0f}")
    print(f"tau_ring (corrected) = R^2*6/(BETA*DT) = {tau_ring:.0f} steps  "
          f"({PHASE2_CONS/tau_ring:.2f}x)")
    print()

    results={}
    for label,q_twist in [("ring_Q0",0),("hopfion_Q1",1)]:
        print(f"Building {label}...", flush=True)
        sg,sm,chi,phi,M0=build_structure(q_twist)
        print(f"  Running {PHASE2_CONS} conservative steps...", flush=True)
        t0=time.time(); traj=[]
        for t in range(1,PHASE2_CONS+1):
            sg,sm,chi,phi=step_conservative(sg,sm,chi,phi)
            if t%RECORD_EVERY==0:
                M=ring_mass(sm)
                frac=M/M0 if M0>0 else 0.
                traj.append({"t":t,"M":round(M,1),"frac":round(frac,4)})
                if t%10000==0:
                    el=time.time()-t0
                    rate=t/el
                    rem=(PHASE2_CONS-t)/rate
                    print(f"  cons t={t:7d}: M={M:7.1f}  ({100*frac:.2f}%)  "
                          f"[{el:.0f}s  ~{rem:.0f}s left]", flush=True)
        M_final=ring_mass(sm)
        hl=half_life(traj,M0)
        dissolved=M_final<0.99*M0
        print(f"  Final: M={M_final:.1f} ({100*M_final/M0:.3f}%)  "
              f"half-life: {hl if hl else '>'+str(PHASE2_CONS)}  dissolved: {dissolved}")
        results[label]={"q_twist":q_twist,"M0":round(M0,1),
                        "M_final":round(M_final,1),
                        "frac_final":round(M_final/M0,4) if M0>0 else 0,
                        "half_life_steps":hl,"dissolved_1pct":dissolved,"traj":traj}
        print()

    print("="*70)
    r0=results["ring_Q0"]; r1=results["hopfion_Q1"]
    c1_ring=r0["dissolved_1pct"]; c1_hopf=r1["dissolved_1pct"]
    c2=r1["M_final"]>=r0["M_final"]
    hl0=r0["half_life_steps"]; hl1=r1["half_life_steps"]
    hl0e=hl0 if hl0 else PHASE2_CONS+1
    hl1e=hl1 if hl1 else PHASE2_CONS+1
    c3=hl1e>=hl0e

    print(f"Ring Q=0:    M0={r0['M0']:.1f} -> {r0['M_final']:.1f} "
          f"({100*r0['frac_final']:.3f}%)  dissolved={c1_ring}  "
          f"half-life={hl0 if hl0 else '>'+str(PHASE2_CONS)}")
    print(f"Hopfion Q=1: M0={r1['M0']:.1f} -> {r1['M_final']:.1f} "
          f"({100*r1['frac_final']:.3f}%)  dissolved={c1_hopf}  "
          f"half-life={hl1 if hl1 else '>'+str(PHASE2_CONS)}")
    print()
    print(f"tau_ring = {tau_ring:.0f} steps  (ran {PHASE2_CONS/tau_ring:.2f}x)")
    print(f"Check 1 (dissolution info): ring={c1_ring}  hopfion={c1_hopf}")
    print(f"Check 2 (hopfion >= ring mass): {'PASS' if c2 else 'FAIL'}")
    print(f"Check 3 (half-life): {hl1e} >= {hl0e} -> {'PASS' if c3 else 'FAIL'}")

    overall="pass" if c3 else "fail"
    print(f"\nqng_hopfion_100k_reference: {overall.upper()}")

    report={"test_id":"QNG-CPU-069","decision":overall,"device":DEVICE,
            "cons_steps":PHASE2_CONS,"dt":DT_CONS,
            "tau_ring_corrected":round(tau_ring),
            "tau_ratio":round(PHASE2_CONS/tau_ring,3),
            "checks":{"ring_dissolved":c1_ring,"hopfion_dissolved":c1_hopf,
                      "hopfion_ge_ring":c2,"hopfion_halflife_ge_ring":c3},
            "ring_Q0":r0,"hopfion_Q1":r1}
    rp=out/"report.json"
    with open(rp,"w") as f: json.dump(report,f,indent=2)
    print(f"\nReport: {rp}")
    return 0 if overall=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
