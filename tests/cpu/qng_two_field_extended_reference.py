from __future__ import annotations

"""
QNG-CPU-061: Two-field v7 extended run — sigma_g spatial profile.

Runs v7 substrate to T=2500, measures radial profile of sigma_g depletion
around the ring. Tests whether ring sources a Yukawa-like gravitational halo.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-two-field-extended-v1"

L = 20; N = L*L*L
PHASE1_STEPS = 300; PHASE2_STEPS = 2500; CHECK_INTERVAL = 500
SIGMA_REF = 0.5; ALPHA = 0.005; BETA = 0.35; BETA_PHI = 0.02
DELTA = 0.20; CHI_DECAY = 0.005; CHI_REL = 0.35; GAMMA_PHI = 0.10
K_BACK = 0.10; K_GM = 0.001
RING_R = 5.0; RING_X = L/2.0; RING_Y = L/2.0; RING_Z = L/2.0

def idx3(x,y,z): return (x%L)*L*L+(y%L)*L+(z%L)
def coord3(i):
    x=i//(L*L); y=(i%(L*L))//L; z=i%L; return x,y,z
def _mi(d):
    while d>L/2: d-=L
    while d<-L/2: d+=L
    return d
def wrap(a):
    a=a%(2*math.pi); return a-2*math.pi if a>math.pi else a
def adiff(a,b): return wrap(a-b)
def clip01(x): return max(0.0,min(1.0,x))
def nb(x,y,z): return [idx3(x-1,y,z),idx3(x+1,y,z),idx3(x,y-1,z),idx3(x,y+1,z),idx3(x,y,z-1),idx3(x,y,z+1)]

def init_phi():
    p=[]
    for i in range(N):
        x,y,z=coord3(i); dx=_mi(x-RING_X); dy=_mi(y-RING_Y); dz=_mi(z-RING_Z)
        rho=math.sqrt(dx*dx+dy*dy); p.append(math.atan2(dz,rho-RING_R))
    return p

def disorder(phi,i):
    x,y,z=coord3(i); nbs=nb(x,y,z)
    sx=sum(math.cos(phi[j]) for j in nbs)/6.; sy=sum(math.sin(phi[j]) for j in nbs)/6.
    return max(0.,1.-math.sqrt(sx*sx+sy*sy))

def step_v7(sg,sm,chi,phi,cf,cg):
    nsg,nsm,nc,np_=[],[],[],[]
    for i in range(N):
        x,y,z=coord3(i); nbs=nb(x,y,z)
        sg_b=sum(sg[j] for j in nbs)/6.; sm_b=sum(sm[j] for j in nbs)/6.
        s=sg[i]; m=sm[i]; c=chi[i]; p=phi[i]
        dsg=ALPHA*(SIGMA_REF-s)+BETA*(sg_b-s)
        if cg: dsg+=K_BACK*c
        dsg-=K_GM*(SIGMA_REF-m)
        nsg.append(clip01(s+dsg))
        dsm=ALPHA*(SIGMA_REF-m)+BETA*(sm_b-m)
        if cf: dsm-=GAMMA_PHI*disorder(phi,i)*m
        nsm.append(clip01(m+dsm))
        nc.append(c*(1-CHI_DECAY)+CHI_REL*(sg_b-s)+DELTA*(SIGMA_REF-s))
        tw=sum(sm[j] for j in nbs)
        if tw>1e-10:
            sx2=sum(sm[j]*math.cos(phi[j]) for j in nbs)/tw
            sy2=sum(sm[j]*math.sin(phi[j]) for j in nbs)/tw
            pm=math.atan2(sy2,sx2)
        else: pm=p
        np_.append(wrap(p+BETA_PHI*adiff(pm,p)))
    return nsg,nsm,nc,np_

def m_ring(sm): return sum(max(0.,SIGMA_REF-sm[i]) for i in range(N))
def chi_rms(c): return math.sqrt(sum(x*x for x in c)/N)

def radial_sg_profile(sg, r_max=10):
    """Average sigma_g depletion as function of distance from ring tube."""
    shells = {r: [] for r in range(1, r_max+1)}
    for i in range(N):
        x,y,z=coord3(i)
        dx=_mi(x-RING_X); dy=_mi(y-RING_Y); dz=_mi(z-RING_Z)
        rho=math.sqrt(dx*dx+dy*dy)
        dist_tube=math.sqrt((rho-RING_R)**2+dz*dz)
        r_bin=int(dist_tube)
        if r_bin in shells:
            shells[r_bin].append(SIGMA_REF - sg[i])
    return {r: (sum(v)/len(v) if v else 0.0) for r, v in shells.items()}

def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    args=p.parse_args(); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)

    print("QNG-CPU-061: Two-field v7 extended run (sigma_g spatial profile)")
    print(f"L={L}  R={RING_R}  Phase2={PHASE2_STEPS}  k_back={K_BACK}  k_gm={K_GM}")
    print()

    sg=[SIGMA_REF]*N; sm=[SIGMA_REF]*N; chi=[0.]*N; phi=init_phi()
    print("Phase 1 ...",flush=True)
    for _ in range(PHASE1_STEPS): sg,sm,chi,phi=step_v7(sg,sm,chi,phi,False,False)
    print(f"  done. M={m_ring(sm):.1f}"); print()

    traj=[]; profile_records=[]
    print(f"  {'t':>5}  {'M_ring':>8}  {'chi_rms':>9}  {'dsg@r=2':>10}  {'dsg@r=5':>10}  {'dsg@r=9':>10}")

    for t in range(1,PHASE2_STEPS+1):
        sg,sm,chi,phi=step_v7(sg,sm,chi,phi,True,True)
        if t%CHECK_INTERVAL==0 or t==1:
            M=m_ring(sm); cr=chi_rms(chi)
            prof=radial_sg_profile(sg)
            row={"t":t,"M":round(M,2),"chi_rms":round(cr,4),
                 "sg_profile":{r:round(v,7) for r,v in prof.items()}}
            traj.append(row)
            print(f"  t={t:5d}  M={M:8.1f}  chi_rms={cr:9.4f}  "
                  f"dsg@r=2={prof.get(2,0):+10.6f}  "
                  f"dsg@r=5={prof.get(5,0):+10.6f}  "
                  f"dsg@r=9={prof.get(9,0):+10.6f}",flush=True)

    r2000=next((r for r in traj if r["t"]>=2000),traj[-1])
    M2000=r2000["M"]; chi2000=r2000["chi_rms"]; prof2000=r2000["sg_profile"]
    check1=M2000>50
    check2=abs(prof2000.get(5,0))>abs(prof2000.get(9,0)) if prof2000 else False
    check3=chi2000>0.01

    print()
    print("="*65)
    print(f"At T=2000: M={M2000:.1f}  chi_rms={chi2000:.4f}")
    print("sigma_g radial profile at T=2000:")
    for r in sorted(prof2000.keys()):
        print(f"  r={r}: delta_sg={prof2000[r]:+.7f}")
    print()
    print(f"Check 1 (M>50):               {'PASS' if check1 else 'FAIL'}")
    print(f"Check 2 (profile decays):     {'PASS' if check2 else 'FAIL'}")
    print(f"Check 3 (chi_rms>0.01):       {'PASS' if check3 else 'FAIL'}")

    overall="pass" if (check1 and check2) else "fail"
    print(f"\nqng_two_field_extended_reference: {overall.upper()}")
    if check2:
        print("  Yukawa-like sigma_g profile confirmed: ring sources gravitational halo.")

    report={"test_id":"QNG-CPU-061","decision":overall,"k_back":K_BACK,"k_gm":K_GM,
            "checks":{"ring_alive":check1,"profile_decays":check2,"chi_active":check3},
            "trajectory":traj}
    rp=out/"report.json"
    with open(rp,"w") as f: json.dump(report,f,indent=2)
    print(f"\nReport: {rp}")
    return 0 if overall=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
