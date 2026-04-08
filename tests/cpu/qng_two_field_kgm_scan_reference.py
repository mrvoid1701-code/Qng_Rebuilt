from __future__ import annotations

"""QNG-CPU-062: Two-field v7 k_gm scan — ring stability vs gravity coupling."""

import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-two-field-kgm-scan-v1"

L=20; N=L*L*L; PHASE1=300; PHASE2=1500
SIGMA_REF=0.5; ALPHA=0.005; BETA=0.35; BETA_PHI=0.02
DELTA=0.20; CHI_DECAY=0.005; CHI_REL=0.35; GAMMA_PHI=0.10
K_BACK=0.10; RING_R=5.0; RX=L/2.; RY=L/2.; RZ=L/2.
K_GMS=[0.0, 0.001, 0.005, 0.01, 0.05, 0.10]

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
def init_phi():
    p=[]
    for i in range(N):
        x,y,z=coord3(i);dx=_mi(x-RX);dy=_mi(y-RY);dz=_mi(z-RZ)
        rho=math.sqrt(dx*dx+dy*dy);p.append(math.atan2(dz,rho-RING_R))
    return p
def dis(phi,i):
    x,y,z=coord3(i);nbs=nb(x,y,z)
    sx=sum(math.cos(phi[j]) for j in nbs)/6.;sy=sum(math.sin(phi[j]) for j in nbs)/6.
    return max(0.,1.-math.sqrt(sx*sx+sy*sy))
def step_v7(sg,sm,chi,phi,k_gm):
    nsg,nsm,nc,np_=[],[],[],[]
    for i in range(N):
        x,y,z=coord3(i);nbs=nb(x,y,z)
        sgb=sum(sg[j] for j in nbs)/6.;smb=sum(sm[j] for j in nbs)/6.
        s=sg[i];m=sm[i];c=chi[i];p=phi[i]
        dsg=ALPHA*(SIGMA_REF-s)+BETA*(sgb-s)+K_BACK*c-k_gm*(SIGMA_REF-m)
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

def ring_nodes_idx():
    idx=[]
    for i in range(N):
        x,y,z=coord3(i);dx=_mi(x-RX);dy=_mi(y-RY);dz=_mi(z-RZ)
        rho=math.sqrt(dx*dx+dy*dy);d=math.sqrt((rho-RING_R)**2+dz*dz)
        if d<=2.5: idx.append(i)
    return idx

def run_kgm(k_gm, ring_idx, base_phi):
    sg=[SIGMA_REF]*N; sm=[SIGMA_REF]*N; chi=[0.]*N; phi=list(base_phi)
    for _ in range(PHASE1): sg,sm,chi,phi=step_v7(sg,sm,chi,phi,0.0)
    for t in range(1,PHASE2+1):
        sg,sm,chi,phi=step_v7(sg,sm,chi,phi,k_gm)
        if t==1000:
            M=sum(max(0.,SIGMA_REF-sm[i]) for i in range(N))
            dsg=sum(SIGMA_REF-sg[i] for i in ring_idx)/len(ring_idx) if ring_idx else 0.
            cr=math.sqrt(sum(c*c for c in chi)/N)
        if t==PHASE2:
            M_fin=sum(max(0.,SIGMA_REF-sm[i]) for i in range(N))
            dsg_fin=sum(SIGMA_REF-sg[i] for i in ring_idx)/len(ring_idx) if ring_idx else 0.
            cr_fin=math.sqrt(sum(c*c for c in chi)/N)
    return {"k_gm":k_gm,"M_1000":round(M,2),"dsg_1000":round(dsg,6),"chi_rms_1000":round(cr,4),
            "M_final":round(M_fin,2),"dsg_final":round(dsg_fin,6),"chi_rms_final":round(cr_fin,4),
            "ring_alive":M_fin>50}

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    args=p.parse_args();out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)

    print("QNG-CPU-062: Two-field v7 k_gm scan")
    print(f"L={L}  R={RING_R}  k_back={K_BACK}  k_gm scan={K_GMS}")
    print()

    base_phi=init_phi()
    ring_idx=ring_nodes_idx()
    print(f"Ring tube nodes: {len(ring_idx)}")
    print()
    print(f"  {'k_gm':>8}  {'M(T=1000)':>10}  {'dsg_core':>10}  {'chi_rms':>9}  {'ring':>6}")

    results=[]
    for kgm in K_GMS:
        r=run_kgm(kgm,ring_idx,base_phi)
        results.append(r)
        alive="OK" if r["ring_alive"] else "DEAD"
        print(f"  k_gm={kgm:.3f}  M={r['M_1000']:10.1f}  dsg={r['dsg_1000']:+10.6f}  "
              f"chi={r['chi_rms_1000']:9.4f}  {alive}",flush=True)

    print()
    alive_kgms=[r["k_gm"] for r in results if r["ring_alive"]]
    dead_kgms=[r["k_gm"] for r in results if not r["ring_alive"]]
    check1=all(r["ring_alive"] for r in results if r["k_gm"]<=0.01)
    print("Checks:")
    print(f"  Check 1 (ring alive for k_gm<=0.01): {'PASS' if check1 else 'FAIL'}")
    print(f"  Alive: {alive_kgms}  Dead: {dead_kgms}")
    print()
    print("Signal scaling (dsg_core vs k_gm at T=final):")
    for r in results:
        print(f"  k_gm={r['k_gm']:.3f}: dsg_final={r['dsg_final']:+.6f}")

    overall="pass" if check1 else "fail"
    print(f"\nqng_two_field_kgm_scan_reference: {overall.upper()}")

    report={"test_id":"QNG-CPU-062","decision":overall,"k_back":K_BACK,
            "checks":{"ring_alive_kgm_le_001":check1},
            "results":results}
    rp=out/"report.json"
    with open(rp,"w") as f: json.dump(report,f,indent=2)
    print(f"\nReport: {rp}")
    return 0 if overall=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
