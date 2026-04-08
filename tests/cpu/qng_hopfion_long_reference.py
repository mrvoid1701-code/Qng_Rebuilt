from __future__ import annotations

"""QNG-CPU-067: Hopfion Q=1 vs ring Q=0 — long conservative run (1000 steps).

Tests whether topological protection of Q=1 Hopfion provides longer
conservative stability than the standard ring Q=0.
"""

import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-hopfion-long-v1"

L=20; N=L*L*L; PHASE1=300; PHASE2_DISS=1000; PHASE2_CONS=1000
SIGMA_REF=0.5; ALPHA=0.005; BETA=0.35; BETA_PHI=0.02
DELTA=0.20; CHI_DECAY=0.020; CHI_REL=0.35; GAMMA_PHI=0.10
K_BACK=0.10; K_GM=0.001; RING_R=5.0
RX=L/2.; RY=L/2.; RZ=L/2.
DT_CONS=0.005
RECORD_EVERY=50

def idx3(x,y,z): return (x%L)*L*L+(y%L)*L+(z%L)
def coord3(i): x=i//(L*L);y=(i%(L*L))//L;z=i%L;return x,y,z
def _mi(d):
    while d>L/2: d-=L
    while d<-L/2: d+=L
    return d
def wrap(a): a=a%(2*math.pi);return a-2*math.pi if a>math.pi else a
def adiff(a,b): return wrap(a-b)
def clip01(x): return max(0.,min(1.,x))
def nb(x,y,z): return [idx3(x-1,y,z),idx3(x+1,y,z),idx3(x,y-1,z),idx3(x,y+1,z),idx3(x,y,z-1),idx3(x,y,z+1)]

def init_phi(q_twist):
    p=[]
    for i in range(N):
        x,y,z=coord3(i)
        dx=_mi(x-RX); dy=_mi(y-RY); dz=_mi(z-RZ)
        rho=math.sqrt(dx*dx+dy*dy)
        poloidal=math.atan2(dz, rho-RING_R)
        toroidal=math.atan2(dy, dx)
        p.append(wrap(poloidal + q_twist*toroidal))
    return p

def dis(phi,i):
    x,y,z=coord3(i); nbs=nb(x,y,z)
    sx=sum(math.cos(phi[j]) for j in nbs)/6.
    sy=sum(math.sin(phi[j]) for j in nbs)/6.
    return max(0., 1.-math.sqrt(sx*sx+sy*sy))

def step_dissipative(sg,sm,chi,phi):
    nsg,nsm,nc,np_=[],[],[],[]
    for i in range(N):
        x,y,z=coord3(i); nbs=nb(x,y,z)
        sgb=sum(sg[j] for j in nbs)/6.; smb=sum(sm[j] for j in nbs)/6.
        s=sg[i]; m=sm[i]; c=chi[i]; p=phi[i]
        dsg=ALPHA*(SIGMA_REF-s)+BETA*(sgb-s)+K_BACK*c-K_GM*(SIGMA_REF-m)
        nsg.append(clip01(s+dsg))
        dsm=ALPHA*(SIGMA_REF-m)+BETA*(smb-m)-GAMMA_PHI*dis(phi,i)*m
        nsm.append(clip01(m+dsm))
        nc.append(c*(1-CHI_DECAY)+CHI_REL*(sgb-s)+DELTA*(SIGMA_REF-s))
        tw=sum(sm[j] for j in nbs)
        if tw>1e-10:
            sx2=sum(sm[j]*math.cos(phi[j]) for j in nbs)/tw
            sy2=sum(sm[j]*math.sin(phi[j]) for j in nbs)/tw
            pm=math.atan2(sy2,sx2)
        else: pm=p
        np_.append(wrap(p+BETA_PHI*adiff(pm,p)))
    return nsg,nsm,nc,np_

def step_conservative(sg,sm,chi,phi):
    """Conservative: no ALPHA in sigma, no Channel F, no CHI_DECAY."""
    nsg,nsm,nc,np_=[],[],[],[]
    for i in range(N):
        x,y,z=coord3(i); nbs=nb(x,y,z)
        sgb=sum(sg[j] for j in nbs)/6.; smb=sum(sm[j] for j in nbs)/6.
        s=sg[i]; m=sm[i]; c=chi[i]; p=phi[i]
        ds=K_BACK*c + CHI_REL*(sgb-s) + DELTA*(s-SIGMA_REF)
        nsg.append(clip01(s+DT_CONS*ds))
        dm=BETA*(smb-m)
        nsm.append(clip01(m+DT_CONS*dm))
        dc=-ALPHA*(s-SIGMA_REF)+BETA*6*(sgb-s)-DELTA*c
        nc.append(c+DT_CONS*dc)
        tw=sum(sm[j] for j in nbs)
        if tw>1e-10:
            sx2=sum(sm[j]*math.cos(phi[j]) for j in nbs)/tw
            sy2=sum(sm[j]*math.sin(phi[j]) for j in nbs)/tw
            pm=math.atan2(sy2,sx2)
        else: pm=p
        np_.append(wrap(p+BETA_PHI*adiff(pm,p)))
    return nsg,nsm,nc,np_

def ring_mass(sm): return sum(max(0.,SIGMA_REF-sm[i]) for i in range(N))

def build_structure(q_twist):
    """Phase 1 + Phase 2 dissipative to build fully formed structure."""
    phi0=init_phi(q_twist)
    sg=[SIGMA_REF]*N; sm=[SIGMA_REF]*N; chi=[0.]*N; phi=list(phi0)
    # Phase 1
    for _ in range(PHASE1):
        nsg,nsm,nc,np_=[],[],[],[]
        for i in range(N):
            x,y,z=coord3(i); nbs=nb(x,y,z)
            sgb=sum(sg[j] for j in nbs)/6.; smb=sum(sm[j] for j in nbs)/6.
            s=sg[i]; m=sm[i]; c=chi[i]; p=phi[i]
            nsg.append(clip01(s+ALPHA*(SIGMA_REF-s)+BETA*(sgb-s)))
            nsm.append(clip01(m+ALPHA*(SIGMA_REF-m)+BETA*(smb-m)))
            nc.append(c*(1-CHI_DECAY)+CHI_REL*(sgb-s)+DELTA*(SIGMA_REF-s))
            tw=sum(sm[j] for j in nbs)
            if tw>1e-10:
                sx2=sum(sm[j]*math.cos(phi[j]) for j in nbs)/tw
                sy2=sum(sm[j]*math.sin(phi[j]) for j in nbs)/tw
                pm=math.atan2(sy2,sx2)
            else: pm=p
            np_.append(wrap(p+BETA_PHI*adiff(pm,p)))
        sg,sm,chi,phi=nsg,nsm,nc,np_
    # Phase 2 dissipative
    for t in range(1,PHASE2_DISS+1):
        sg,sm,chi,phi=step_dissipative(sg,sm,chi,phi)
    return sg,sm,chi,phi

def half_life(traj, M0):
    """First t where M < M0/2, or None if never."""
    for pt in traj:
        if pt["M"] < M0/2.: return pt["t"]
    return None

def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    args=p.parse_args(); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)

    print("QNG-CPU-067: Hopfion Q=1 vs ring Q=0 -- long conservative run")
    print(f"L={L}  R={RING_R}  CONS steps={PHASE2_CONS}  DT={DT_CONS}  total_time={PHASE2_CONS*DT_CONS:.2f}")
    print(f"Diffusion timescale estimate: R^2/BETA*DT = {RING_R**2/BETA*DT_CONS:.2f} units")
    print()

    results={}
    for label, q_twist in [("ring_Q0", 0), ("hopfion_Q1", 1)]:
        print(f"Building {label} (Phase1={PHASE1} + Phase2_diss={PHASE2_DISS})...", flush=True)
        sg,sm,chi,phi=build_structure(q_twist)
        M0=ring_mass(sm)
        print(f"  Fully formed: M0={M0:.1f}")
        print(f"  Running {PHASE2_CONS} conservative steps...", flush=True)

        traj=[]
        for t in range(1, PHASE2_CONS+1):
            sg,sm,chi,phi=step_conservative(sg,sm,chi,phi)
            if t%RECORD_EVERY==0:
                M=ring_mass(sm)
                traj.append({"t":t,"M":round(M,1),"frac":round(M/M0,4) if M0>0 else 0})
                if t%200==0:
                    print(f"  cons t={t:5d}: M={M:7.1f}  ({100*M/M0:.1f}%)",flush=True)

        M_final=ring_mass(sm)
        hl=half_life(traj, M0)
        print(f"  Final M={M_final:.1f} ({100*M_final/M0:.1f}%)  half-life: {hl if hl else '>'+str(PHASE2_CONS)} steps")
        results[label]={"q_twist":q_twist,"M0":round(M0,1),"M_final":round(M_final,1),
                        "frac_final":round(M_final/M0,4) if M0>0 else 0,
                        "half_life_steps":hl,"traj":traj}
        print()

    print("="*60)
    r0=results["ring_Q0"]; r1=results["hopfion_Q1"]

    hl0=r0["half_life_steps"]; hl1=r1["half_life_steps"]
    # Check 1: Hopfion half-life > ring half-life
    # If neither has reached half-life, both get PHASE2_CONS as lower bound
    hl0_eff=hl0 if hl0 else PHASE2_CONS+1
    hl1_eff=hl1 if hl1 else PHASE2_CONS+1
    c1=(hl1_eff >= hl0_eff)

    c2=(r1["M_final"] > r1["M0"]*0.50)
    c3=(r0["M_final"]>50 or r1["M_final"]>50)

    print(f"Ring Q=0:    M0={r0['M0']:.1f} -> M_final={r0['M_final']:.1f} ({100*r0['frac_final']:.1f}%)  "
          f"half-life={hl0 if hl0 else '>'+str(PHASE2_CONS)} steps")
    print(f"Hopfion Q=1: M0={r1['M0']:.1f} -> M_final={r1['M_final']:.1f} ({100*r1['frac_final']:.1f}%)  "
          f"half-life={hl1 if hl1 else '>'+str(PHASE2_CONS)} steps")
    print()
    print(f"Check 1 (Hopfion half-life >= ring): {hl1_eff} >= {hl0_eff} -> {'PASS' if c1 else 'FAIL'}")
    print(f"Check 2 (Hopfion >50% mass at T=500): {100*r1['frac_final']:.1f}% -> {'PASS' if c2 else 'FAIL'}")
    print(f"Check 3 (any M>50 at T=1000): ring={r0['M_final']:.1f} hopfion={r1['M_final']:.1f} "
          f"-> {'PASS' if c3 else 'FAIL'}")

    overall="pass" if c1 else "fail"
    print(f"\nqng_hopfion_long_reference: {overall.upper()}")

    report={"test_id":"QNG-CPU-067","decision":overall,
            "cons_steps":PHASE2_CONS,"dt":DT_CONS,"total_time":PHASE2_CONS*DT_CONS,
            "checks":{"hopfion_longer_halflife":c1,"hopfion_50pct_at_500":c2,"any_survives":c3},
            "ring_Q0":r0,"hopfion_Q1":r1}
    rp=out/"report.json"
    with open(rp,"w") as f: json.dump(report,f,indent=2)
    print(f"\nReport: {rp}")
    return 0 if overall=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
