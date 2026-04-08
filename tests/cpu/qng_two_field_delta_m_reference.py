from __future__ import annotations

"""QNG-CPU-065: Two-field v7 with DELTA_m coupling — kinetic mass recovery scan."""

import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-two-field-delta-m-v1"

L=20; N=L*L*L; PHASE1=300; PHASE2=1500; SNAP_T=1000
SIGMA_REF=0.5; ALPHA=0.005; BETA=0.35; BETA_PHI=0.02
DELTA=0.20; CHI_DECAY=0.020; CHI_REL=0.35; GAMMA_PHI=0.10
K_BACK=0.10; K_GM=0.001
RX=L/2.; RY=L/2.; RZ=L/2.
RADII=[2.0,3.0,4.0,5.0]
DELTA_MS=[0.0, 0.02, 0.05, 0.10, 0.20]

HADRON_RATIOS={"pi(140)":140./938.3,"K(494)":494./938.3,"rho(770)":770./938.3,
               "proton(938)":1.000}

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

def init_phi(R):
    p=[]
    for i in range(N):
        x,y,z=coord3(i);dx=_mi(x-RX);dy=_mi(y-RY);dz=_mi(z-RZ)
        rho=math.sqrt(dx*dx+dy*dy);p.append(math.atan2(dz,rho-R))
    return p

def dis(phi,i):
    x,y,z=coord3(i);nbs=nb(x,y,z)
    sx=sum(math.cos(phi[j]) for j in nbs)/6.;sy=sum(math.sin(phi[j]) for j in nbs)/6.
    return max(0.,1.-math.sqrt(sx*sx+sy*sy))

def step_v7(sg,sm,chi,phi,delta_m):
    nsg,nsm,nc,np_=[],[],[],[]
    for i in range(N):
        x,y,z=coord3(i);nbs=nb(x,y,z)
        sgb=sum(sg[j] for j in nbs)/6.;smb=sum(sm[j] for j in nbs)/6.
        s=sg[i];m=sm[i];c=chi[i];p=phi[i]
        # sigma_g: A + B + G + K_GM coupling (correct sign)
        dsg=ALPHA*(SIGMA_REF-s)+BETA*(sgb-s)+K_BACK*c
        dsg-=K_GM*(SIGMA_REF-m)
        nsg.append(clip01(s+dsg))
        # sigma_m: A + B + F (no Channel G)
        dsm=ALPHA*(SIGMA_REF-m)+BETA*(smb-m)-GAMMA_PHI*dis(phi,i)*m
        nsm.append(clip01(m+dsm))
        # chi: couples to sigma_g (DELTA) AND sigma_m (DELTA_m — new)
        nc.append(c*(1-CHI_DECAY)+CHI_REL*(sgb-s)+DELTA*(SIGMA_REF-s)+delta_m*(SIGMA_REF-m))
        # phi: weighted by sigma_m
        tw=sum(sm[j] for j in nbs)
        if tw>1e-10:
            sx2=sum(sm[j]*math.cos(phi[j]) for j in nbs)/tw
            sy2=sum(sm[j]*math.sin(phi[j]) for j in nbs)/tw
            pm=math.atan2(sy2,sx2)
        else: pm=p
        np_.append(wrap(p+BETA_PHI*adiff(pm,p)))
    return nsg,nsm,nc,np_

def compute_E(sg,sm,chi,phi):
    E=0.
    for i in range(N):
        x,y,z=coord3(i);nbs=nb(x,y,z)
        sgb=sum(sg[j] for j in nbs)/6.;smb=sum(sm[j] for j in nbs)/6.
        s=sg[i];m=sm[i];c=chi[i];p=phi[i]
        E+=ALPHA/2.*(s-SIGMA_REF)**2+BETA/4.*sum((sg[j]-s)**2 for j in nbs)
        E+=ALPHA/2.*(m-SIGMA_REF)**2+BETA/4.*sum((sm[j]-m)**2 for j in nbs)
        E-=BETA_PHI/6.*sum(m*sm[j]*math.cos(adiff(p,phi[j])) for j in nbs)
        E+=GAMMA_PHI/2.*dis(phi,i)*m*m
        E+=CHI_DECAY/2.*c*c+CHI_REL/2.*c*(sgb-s)+DELTA*c*(s-SIGMA_REF)
        E-=K_GM/2.*(SIGMA_REF-m)*(SIGMA_REF-s)
    return E

def E_vac():
    sg=[SIGMA_REF]*N;sm=[SIGMA_REF]*N;c=[0.]*N;p=[0.]*N
    return compute_E(sg,sm,c,p)

def run_one(R, delta_m, ev):
    sg=[SIGMA_REF]*N;sm=[SIGMA_REF]*N;chi=[0.]*N;phi=init_phi(R)
    # Phase 1: no channels active (phi settles)
    for _ in range(PHASE1):
        nsg,nsm,nc,np_=[],[],[],[]
        for i in range(N):
            x,y,z=coord3(i);nbs=nb(x,y,z)
            sgb=sum(sg[j] for j in nbs)/6.;smb=sum(sm[j] for j in nbs)/6.
            s=sg[i];m=sm[i];c=chi[i];p=phi[i]
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
    # Phase 2: all channels active
    snap=None
    for t in range(1,PHASE2+1):
        sg,sm,chi,phi=step_v7(sg,sm,chi,phi,delta_m)
        if t==SNAP_T:
            M=sum(max(0.,SIGMA_REF-sm[i]) for i in range(N))
            Er=compute_E(sg,sm,chi,phi)-ev
            sc2=sum(c*c for c in chi)
            T_kin=K_BACK/2.*sc2
            H=Er+T_kin
            cr=math.sqrt(sc2/N)
            snap={"t":t,"R":R,"delta_m":delta_m,"M":round(M,2),
                  "E_ring":round(Er,4),"T_kin":round(T_kin,4),"H":round(H,4),
                  "chi_rms":round(cr,4),"sum_chi2":round(sc2,2)}
    return snap or {}

def best_hadron(ratio):
    best=min(HADRON_RATIOS.items(), key=lambda kv: abs(kv[1]-ratio)/kv[1])
    return best[0], best[1], abs(best[1]-ratio)/best[1]

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    args=p.parse_args();out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)

    print("QNG-CPU-065: Two-field v7 DELTA_m scan — kinetic mass recovery")
    print(f"L={L}  Phase2={PHASE2}  snap T={SNAP_T}  K_BACK={K_BACK}  CHI_DECAY={CHI_DECAY}")
    print(f"DELTA_m scan: {DELTA_MS}")
    print()

    ev=E_vac()
    print(f"E_vacuum = {ev:.4f}")
    print()

    all_results={}
    for dm in DELTA_MS:
        print(f"DELTA_m={dm:.2f}:", flush=True)
        dm_results={}
        for R in RADII:
            snap=run_one(R,dm,ev)
            dm_results[R]=snap
            print(f"  R={R:.0f}: M={snap['M']:7.1f}  E={snap['E_ring']:9.3f}  "
                  f"T={snap['T_kin']:9.3f}  H={snap['H']:9.3f}  chi={snap['chi_rms']:.4f}",
                  flush=True)
        all_results[dm]=dm_results

    print()
    print("="*70)
    print("Spectrum summary (H ratios vs DELTA_m):")
    print()

    spectrum_table={}
    for dm in DELTA_MS:
        H_ref=all_results[dm].get(5.0,{}).get("H",1.0)
        if not H_ref: H_ref=1.0
        ratios={}
        for R in RADII:
            H=all_results[dm].get(R,{}).get("H",0.)
            ratios[R]=H/H_ref if H_ref else 0.
        spectrum_table[dm]=ratios
        n=math.log(ratios.get(5.,1.)/max(ratios.get(2.,1e-10),1e-10))/math.log(5./2.) if ratios.get(2.,0)>0 else 0.
        bname,bval,bdev=best_hadron(ratios.get(2.,0))
        print(f"  DELTA_m={dm:.2f}: ratios={[round(ratios[R],4) for R in RADII]}  "
              f"n={n:.2f}  R=2 best={bname}({bdev:.2f})")

    print()

    # Checks
    c1=all(all_results[dm].get(R,{}).get("M",0)>10 for dm in DELTA_MS for R in RADII)

    T_base=all_results[0.0].get(5.0,{}).get("T_kin",0.)
    T_top=all_results[0.20].get(5.0,{}).get("T_kin",1e-10)
    c2_ratio=T_top/max(T_base,1e-10) if T_base>0 else T_top/1e-10
    c2=(c2_ratio>100) if T_base>1e-10 else (T_top>1e-6)

    c3=all(all_results[dm].get(R,{}).get("chi_rms",999)<1.0
           for dm in DELTA_MS for R in RADII)

    n_top=math.log(spectrum_table[0.20].get(5.,1.)/max(spectrum_table[0.20].get(2.,1e-10),1e-10))/math.log(5./2.) if spectrum_table[0.20].get(2.,0)>0 else 0.
    n_base=math.log(spectrum_table[0.0].get(5.,1.)/max(spectrum_table[0.0].get(2.,1e-10),1e-10))/math.log(5./2.) if spectrum_table[0.0].get(2.,0)>0 else 0.

    print(f"Check 1 (all rings M>10):          {'PASS' if c1 else 'FAIL'}")
    print(f"Check 2 (T_kin grows DELTA_m 0->0.2): T_base={T_base:.4f} T_top={T_top:.4f} "
          f"ratio={c2_ratio:.1f} -> {'PASS' if c2 else 'FAIL'}")
    print(f"Check 3 (chi_rms < 1.0):           {'PASS' if c3 else 'FAIL'}")
    print(f"Check 4 (spectrum scaling, info):   n(DELTA_m=0)={n_base:.2f}  n(DELTA_m=0.2)={n_top:.2f}")
    print(f"  (n=1 = string tension, n=2 = kinetic)")

    overall="pass" if (c1 and c2 and c3) else "fail"
    print(f"\nqng_two_field_delta_m_reference: {overall.upper()}")

    report={"test_id":"QNG-CPU-065","decision":overall,
            "chi_decay":CHI_DECAY,"k_back":K_BACK,"k_gm":K_GM,
            "delta_ms":DELTA_MS,"radii":RADII,
            "checks":{"all_rings":c1,"T_kin_grows":c2,"chi_stable":c3},
            "T_kin_ratio":round(c2_ratio,2),
            "spectrum":{ str(dm):{str(R):round(spectrum_table[dm][R],4) for R in RADII}
                         for dm in DELTA_MS},
            "scaling_n":{"delta_m_0":round(n_base,3),"delta_m_020":round(n_top,3)},
            "results":{str(dm):{str(R):all_results[dm].get(R,{}) for R in RADII}
                       for dm in DELTA_MS}}
    rp=out/"report.json"
    with open(rp,"w") as f: json.dump(report,f,indent=2)
    print(f"\nReport: {rp}")
    return 0 if overall=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
