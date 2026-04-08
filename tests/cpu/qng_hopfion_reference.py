from __future__ import annotations

"""QNG-CPU-066: Hopfion Q=1 vs ring Q=0 — topological stability in v7.

Hopfion initial condition: phi = atan2(z, rho-R) + q_twist * atan2(y, x)
q_twist=0: standard ring (Hopf charge Q=0)
q_twist=1: Q=1 Hopfion (toroidal twist adds Hopf linking)
"""

import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-hopfion-v1"

L=20; N=L*L*L; PHASE1=300
SIGMA_REF=0.5; ALPHA=0.005; BETA=0.35; BETA_PHI=0.02
DELTA=0.20; CHI_DECAY=0.020; CHI_REL=0.35; GAMMA_PHI=0.10
K_BACK=0.10; K_GM=0.001; RING_R=5.0
RX=L/2.; RY=L/2.; RZ=L/2.
PHASE2_DISS=1000    # dissipative run
PHASE2_CONS=150     # conservative run (no damping)
DT_CONS=0.005       # timestep for conservative dynamics

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
    """Initialize phi with toroidal twist q_twist.
    q_twist=0: standard ring  (Hopf charge Q=0)
    q_twist=1: Hopfion Q=1    (extra toroidal winding)
    """
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

def step_v7_dissipative(sg,sm,chi,phi):
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
    """Pure Hamilton's equations — no damping, no Channel F.
    sigma_g: ds/dt = K_BACK*c + CHI_REL/2*(sbar-s) + ... (no ALPHA, no K_GM)
    chi: dc/dt = -ALPHA*(s-SIGMA_REF) + BETA*z*(sbar-s) - DELTA*chi  (no CHI_DECAY)
    sigma_m: dm/dt = BETA*(mbar-m) only (no ALPHA, no Channel F)
    phi: same alignment
    """
    nsg,nsm,nc,np_=[],[],[],[]
    for i in range(N):
        x,y,z=coord3(i); nbs=nb(x,y,z)
        sgb=sum(sg[j] for j in nbs)/6.; smb=sum(sm[j] for j in nbs)/6.
        s=sg[i]; m=sm[i]; c=chi[i]; p=phi[i]
        # conservative sigma_g: gradient of H w.r.t chi
        ds=K_BACK*c + CHI_REL*(sgb-s) + DELTA*(s-SIGMA_REF)
        nsg.append(clip01(s+DT_CONS*ds))
        # conservative sigma_m: pure diffusion only
        dm=BETA*(smb-m)
        nsm.append(clip01(m+DT_CONS*dm))
        # conservative chi: -gradient of H w.r.t. sigma_g
        dc=-ALPHA*(s-SIGMA_REF)+BETA*6*(sgb-s)-DELTA*c
        nc.append(c+DT_CONS*dc)
        # phi alignment
        tw=sum(sm[j] for j in nbs)
        if tw>1e-10:
            sx2=sum(sm[j]*math.cos(phi[j]) for j in nbs)/tw
            sy2=sum(sm[j]*math.sin(phi[j]) for j in nbs)/tw
            pm=math.atan2(sy2,sx2)
        else: pm=p
        np_.append(wrap(p+BETA_PHI*adiff(pm,p)))
    return nsg,nsm,nc,np_

def ring_mass(sm): return sum(max(0.,SIGMA_REF-sm[i]) for i in range(N))

def chi_bipolar(chi):
    """Measure chi in north (z>RZ+3) and south (z<RZ-3) hemispheres."""
    north=[]; south=[]; bulk=[]
    for i in range(N):
        x,y,z=coord3(i); dz=_mi(z-RZ)
        if dz>3: north.append(chi[i])
        elif dz<-3: south.append(chi[i])
        else: bulk.append(chi[i])
    cn=sum(north)/len(north) if north else 0.
    cs=sum(south)/len(south) if south else 0.
    cb=math.sqrt(sum(c*c for c in bulk)/len(bulk)) if bulk else 0.
    return cn,cs,cb

def phase1_settle(phi_init):
    """Phase 1: let sigma fields settle with phi fixed topology."""
    sg=[SIGMA_REF]*N; sm=[SIGMA_REF]*N; chi=[0.]*N; phi=list(phi_init)
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
    return sg,sm,chi,phi

def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    args=p.parse_args(); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)

    print("QNG-CPU-066: Hopfion Q=1 vs ring Q=0")
    print(f"L={L}  R={RING_R}  CHI_DECAY={CHI_DECAY}  K_BACK={K_BACK}")
    print(f"Phase2_dissipative={PHASE2_DISS}  Phase2_conservative={PHASE2_CONS} steps (dt={DT_CONS})")
    print()

    results={}

    for label, q_twist in [("ring_Q0", 0), ("hopfion_Q1", 1)]:
        print(f"--- {label} (q_twist={q_twist}) ---")
        phi0=init_phi(q_twist)

        # Phase 1
        sg,sm,chi,phi=phase1_settle(phi0)
        M0=ring_mass(sm)
        print(f"  After Phase 1: M={M0:.1f}")

        # Dissipative run
        sg_d,sm_d,chi_d,phi_d=[list(x) for x in [sg,sm,chi,phi]]
        traj_diss=[]
        for t in range(1,PHASE2_DISS+1):
            sg_d,sm_d,chi_d,phi_d=step_v7_dissipative(sg_d,sm_d,chi_d,phi_d)
            if t%200==0 or t==1:
                M=ring_mass(sm_d)
                cr=math.sqrt(sum(c*c for c in chi_d)/N)
                traj_diss.append({"t":t,"M":round(M,1),"chi_rms":round(cr,4)})
                print(f"  diss t={t:5d}: M={M:7.1f}  chi={cr:.4f}",flush=True)
        M_diss_final=ring_mass(sm_d)
        cn,cs,cb=chi_bipolar(chi_d)
        print(f"  chi bipolar: north={cn:.5f}  south={cs:.5f}  bulk_rms={cb:.5f}")

        # Conservative run (from fully formed dissipative state — correct starting point)
        sg_c,sm_c,chi_c,phi_c=[list(x) for x in [sg_d,sm_d,chi_d,phi_d]]
        traj_cons=[]
        for t in range(1,PHASE2_CONS+1):
            sg_c,sm_c,chi_c,phi_c=step_conservative(sg_c,sm_c,chi_c,phi_c)
            if t%25==0 or t==1:
                M=ring_mass(sm_c)
                traj_cons.append({"t":t,"M":round(M,1)})
                print(f"  cons t={t:4d}: M={M:7.1f}",flush=True)
        M_cons_final=ring_mass(sm_c)

        results[label]={"q_twist":q_twist,"M_after_phase1":round(M0,1),
                        "M_diss_T1000":round(M_diss_final,1),
                        "M_cons_T150":round(M_cons_final,1),
                        "chi_north":round(cn,6),"chi_south":round(cs,6),
                        "chi_bulk_rms":round(cb,6),
                        "traj_diss":traj_diss,"traj_cons":traj_cons}
        print()

    print("="*60)
    r0=results.get("ring_Q0",{}); r1=results.get("hopfion_Q1",{})

    c1=r1.get("M_diss_T1000",0)>50
    c2=r1.get("M_cons_T150",0)>r0.get("M_cons_T150",0)
    cn=r1.get("chi_north",0); cs=r1.get("chi_south",0); cb=r1.get("chi_bulk_rms",1)
    c3=(abs(cn)>2*cb or abs(cs)>2*cb)
    c4=r1.get("M_diss_T1000",0)>r0.get("M_diss_T1000",0)

    print(f"Check 1 (Hopfion M>50 dissipative T=1000): "
          f"M={r1.get('M_diss_T1000',0):.1f} -> {'PASS' if c1 else 'FAIL'}")
    print(f"Check 2 (Hopfion outlasts ring conservative T=150): "
          f"hopfion={r1.get('M_cons_T150',0):.1f} vs ring={r0.get('M_cons_T150',0):.1f} "
          f"-> {'PASS' if c2 else 'FAIL'}")
    print(f"Check 3 (bipolar chi structure): "
          f"north={cn:.5f} south={cs:.5f} bulk={cb:.5f} -> {'PASS' if c3 else 'FAIL'}")
    print(f"Check 4 (Hopfion energy > ring, info): "
          f"hopfion M={r1.get('M_diss_T1000',0):.1f} vs ring M={r0.get('M_diss_T1000',0):.1f} "
          f"-> {'PASS' if c4 else 'FAIL'}")

    overall="pass" if (c1 and c2) else "fail"
    print(f"\nqng_hopfion_reference: {overall.upper()}")

    report={"test_id":"QNG-CPU-066","decision":overall,
            "checks":{"hopfion_survives_diss":c1,"hopfion_outlasts_ring_cons":c2,
                      "bipolar_chi":c3,"hopfion_heavier":c4},
            "ring_Q0":r0,"hopfion_Q1":r1}
    rp=out/"report.json"
    with open(rp,"w") as f: json.dump(report,f,indent=2)
    print(f"\nReport: {rp}")
    return 0 if overall=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
