from __future__ import annotations

"""QNG-CPU-063: Two-field v7 mass spectrum — H_ring(R) for R=2,3,4,5."""

import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-two-field-spectrum-v1"

L=20; N=L*L*L; PHASE1=300; PHASE2=1500; SNAP_T=1000
SIGMA_REF=0.5; ALPHA=0.005; BETA=0.35; BETA_PHI=0.02
DELTA=0.20; CHI_DECAY=0.005; CHI_REL=0.35; GAMMA_PHI=0.10
K_BACK=0.10; K_GM=0.001
RX=L/2.; RY=L/2.; RZ=L/2.
RADII=[2.0,3.0,4.0,5.0]
SNAP_K_BACKS=[0.005,0.01,0.02,0.05,0.10,1.00]

# CPU-058 v5 ratios (reference for Check 2)
V5_RATIOS={2.0:0.1477,3.0:0.2946,4.0:0.6591,5.0:1.0000}

HADRON_RATIOS={"pi(140)":140./938.3,"K(494)":494./938.3,"rho(770)":770./938.3,
               "proton(938)":1.000,"Delta(1232)":1232./938.3}

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
def step_v7(sg,sm,chi,phi,cf,cg):
    nsg,nsm,nc,np_=[],[],[],[]
    for i in range(N):
        x,y,z=coord3(i);nbs=nb(x,y,z)
        sgb=sum(sg[j] for j in nbs)/6.;smb=sum(sm[j] for j in nbs)/6.
        s=sg[i];m=sm[i];c=chi[i];p=phi[i]
        dsg=ALPHA*(SIGMA_REF-s)+BETA*(sgb-s)
        if cg: dsg+=K_BACK*c
        dsg-=K_GM*(SIGMA_REF-m)
        nsg.append(clip01(s+dsg))
        dsm=ALPHA*(SIGMA_REF-m)+BETA*(smb-m)
        if cf: dsm-=GAMMA_PHI*dis(phi,i)*m
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

def run_radius(R,ev):
    print(f"\n  R={R:.0f}",flush=True)
    sg=[SIGMA_REF]*N;sm=[SIGMA_REF]*N;chi=[0.]*N;phi=init_phi(R)
    for _ in range(PHASE1): sg,sm,chi,phi=step_v7(sg,sm,chi,phi,False,False)
    snap=None
    for t in range(1,PHASE2+1):
        sg,sm,chi,phi=step_v7(sg,sm,chi,phi,True,True)
        if t%200==0 or t==1:
            M=sum(max(0.,SIGMA_REF-sm[i]) for i in range(N))
            Er=compute_E(sg,sm,chi,phi)-ev
            cr=math.sqrt(sum(c*c for c in chi)/N)
            sc2=sum(c*c for c in chi)
            km=2*abs(Er)/sc2 if sc2>1e-10 else float("inf")
            print(f"    t={t:5d}: M={M:7.1f}  E_ring={Er:9.2f}  chi_rms={cr:.4f}  k_min={km:.5f}",flush=True)
        if t==SNAP_T:
            M=sum(max(0.,SIGMA_REF-sm[i]) for i in range(N))
            Er=compute_E(sg,sm,chi,phi)-ev
            sc2=sum(c*c for c in chi)
            km=2*abs(Er)/sc2 if sc2>1e-10 else float("inf")
            Hs={kb:kb/2.*sc2+Er for kb in SNAP_K_BACKS}
            snap={"t":t,"R":R,"M":round(M,2),"E_ring":round(Er,3),
                  "sum_chi2":round(sc2,2),"k_min":round(km,6),
                  "H":{round(kb,4):round(hv,3) for kb,hv in Hs.items()}}
    return snap or {}

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    args=p.parse_args();out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)

    print("QNG-CPU-063: Two-field v7 mass spectrum R=2..5")
    print(f"L={L}  Phase2={PHASE2}  snapshot T={SNAP_T}  k_back={K_BACK}  k_gm={K_GM}")
    print()

    ev=E_vac()
    print(f"E_vacuum (v7 two-field) = {ev:.4f}")

    results={}
    for R in RADII: results[R]=run_radius(R,ev)

    print()
    print("="*70)
    print("Mass spectrum at T=1000:")
    H_ref=results.get(5.0,{}).get("H",{}).get(0.10,1.0)
    rows=[]
    print(f"  {'R':>3}  {'M_ring':>8}  {'H(k=0.10)':>12}  {'H/H(R=5)':>10}  {'v5_ratio':>10}  {'diff':>8}")
    for R in RADII:
        s=results.get(R,{})
        M=s.get("M",0.)
        H=s.get("H",{}).get(0.10,0.)
        ratio=H/H_ref if H_ref else 0.
        v5r=V5_RATIOS.get(R,0.)
        diff=abs(ratio-v5r)
        rows.append((R,M,H,ratio,v5r,diff))
        print(f"  R={R:.0f}  M={M:8.1f}  H={H:12.2f}  ratio={ratio:.4f}  v5={v5r:.4f}  diff={diff:.4f}")

    print()
    print("Hadron ratio comparison:")
    print(f"  {'R':>3}  {'ratio':>8}  {'pi(140)':>10}  {'K(494)':>10}  {'rho(770)':>10}  {'proton':>10}  {'Delta':>10}")
    for R,M,H,ratio,v5r,diff in rows:
        print(f"  R={R:.0f}  {ratio:.4f}",end="")
        for name,hr in HADRON_RATIOS.items():
            d=abs(ratio-hr)/hr if hr else 999
            flag=" <--" if d<0.10 else "    "
            print(f"  {hr:.4f}({d:.2f}){flag}",end="")
        print()

    check1=all(results.get(R,{}).get("M",0)>10 for R in RADII)
    check2=all(abs(rows[i][3]-V5_RATIOS.get(rows[i][0],0))<0.05 for i in range(len(rows)))
    v7_pi_ratio=rows[0][3] if rows else 0.

    print()
    print("Checks:")
    print(f"  Check 1 (all rings M>10):           {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (v7 ratios match v5 <5%):   {'PASS' if check2 else 'FAIL'}")
    print(f"  Check 3 (pion ratio R=2): {v7_pi_ratio:.4f} vs PDG 0.1492 "
          f"(diff={abs(v7_pi_ratio-0.1492):.4f})")

    overall="pass" if (check1 and check2) else "fail"
    print(f"\nqng_two_field_spectrum_reference: {overall.upper()}")

    report={"test_id":"QNG-CPU-063","decision":overall,"k_back":K_BACK,"k_gm":K_GM,
            "E_vacuum":ev,"checks":{"all_rings":check1,"v7_matches_v5":check2},
            "results":{str(R):results.get(R,{}) for R in RADII},
            "mass_ratios":{str(R):rows[i][3] for i,R in enumerate(RADII)},
            "v5_ratios":V5_RATIOS,"hadron_ratios":HADRON_RATIOS}
    rp=out/"report.json"
    with open(rp,"w") as f: json.dump(report,f,indent=2)
    print(f"\nReport: {rp}")
    return 0 if overall=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
