from __future__ import annotations

"""QNG-CPU-071: Hopfion Q=1 vs ring Q=0 — gravitational field sigma_g profile.

Runs dissipative dynamics WITH K_GM (gravity on). Measures:
1. Z-axis profile: delta_sigma_g through ring center (bipolar check)
2. Equatorial radial profile: delta_sigma_g in ring plane
3. Spherical shell average: delta_sigma_g(r) for Yukawa fit

Key question: does sigma_g around the structure look like a gravitational potential?
Is the Hopfion's gravitational signature qualitatively different from the ring?
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
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-hopfion-gravity-v1"

L=20; N=L*L*L; PHASE1=300; PHASE2_DISS=1500
SIGMA_REF=0.5; ALPHA=0.005; BETA=0.35; BETA_PHI=0.02
DELTA=0.20; CHI_DECAY=0.020; CHI_REL=0.35; GAMMA_PHI=0.10
K_BACK=0.10; K_GM=0.001; RING_R=5.0
RX=L/2.; RY=L/2.; RZ=L/2.
PI = math.pi

def make_coord_grids():
    xs = xp.arange(L, dtype=xp.float32)
    x3 = xp.broadcast_to(xs[:,None,None],(L,L,L))
    y3 = xp.broadcast_to(xs[None,:,None],(L,L,L))
    z3 = xp.broadcast_to(xs[None,None,:],(L,L,L))
    return x3,y3,z3

def _mi_arr(d): return d - xp.round(d/L)*L
def wrap_arr(a):
    a=a%(2*PI); return xp.where(a>PI,a-2*PI,a)
def adiff_arr(a,b): return wrap_arr(a-b)
def nb6(arr):
    return (xp.roll(arr,1,0)+xp.roll(arr,-1,0)+
            xp.roll(arr,1,1)+xp.roll(arr,-1,1)+
            xp.roll(arr,1,2)+xp.roll(arr,-1,2))/6.
def nb6_sum(arr):
    return (xp.roll(arr,1,0)+xp.roll(arr,-1,0)+
            xp.roll(arr,1,1)+xp.roll(arr,-1,1)+
            xp.roll(arr,1,2)+xp.roll(arr,-1,2))

def init_phi_gpu(q_twist):
    x3,y3,z3=make_coord_grids()
    dx=_mi_arr(x3-RX); dy=_mi_arr(y3-RY); dz=_mi_arr(z3-RZ)
    rho=xp.sqrt(dx*dx+dy*dy)
    return wrap_arr(xp.arctan2(dz,rho-RING_R)+q_twist*xp.arctan2(dy,dx))

def dis_arr(phi):
    sx=nb6(xp.cos(phi)); sy=nb6(xp.sin(phi))
    return xp.maximum(xp.zeros_like(phi),1.-xp.sqrt(sx*sx+sy*sy))

def _phi_align(sm,phi):
    tw=nb6_sum(sm); safe=xp.where(tw>1e-10,tw,xp.ones_like(tw))
    sx2=nb6_sum(sm*xp.cos(phi))/safe; sy2=nb6_sum(sm*xp.sin(phi))/safe
    pm=xp.where(tw>1e-10,xp.arctan2(sy2,sx2),phi)
    return wrap_arr(phi+BETA_PHI*adiff_arr(pm,phi))

def step_dissipative(sg,sm,chi,phi):
    sgb=nb6(sg); smb=nb6(sm)
    # sigma_g: Channel A + Channel D + Channel G + K_GM coupling (MINUS = attractive)
    dsg=ALPHA*(SIGMA_REF-sg)+BETA*(sgb-sg)+K_BACK*chi-K_GM*(SIGMA_REF-sm)
    sg=xp.clip(sg+dsg,0.,1.)
    # sigma_m: Channel A + Channel F (no Channel G)
    dsm=ALPHA*(SIGMA_REF-sm)+BETA*(smb-sm)-GAMMA_PHI*dis_arr(phi)*sm
    sm=xp.clip(sm+dsm,0.,1.)
    chi=chi*(1-CHI_DECAY)+CHI_REL*(sgb-sg)+DELTA*(SIGMA_REF-sg)
    return sg,sm,chi,_phi_align(sm,phi)

def get_np(arr):
    if xp.__name__=='cupy': return arr.get()
    return np.array(arr)

def ring_mass(sm):
    val=xp.sum(xp.maximum(xp.zeros_like(sm),SIGMA_REF-sm))
    return float(val.get() if xp.__name__=='cupy' else val)

def measure_gravity(sg, sm, label):
    """Measure sigma_g gravitational field profile around the structure."""
    sg_np = get_np(sg); sm_np = get_np(sm)
    dsg = sg_np - SIGMA_REF  # gravitational potential: negative = attractive well

    ix = int(round(RX)); iy = int(round(RY)); iz = int(round(RZ))

    # --- 1. Z-axis profile (through ring center, perpendicular to ring plane) ---
    z_profile = []
    for z in range(L):
        dz_mi = z - RZ
        if dz_mi > L/2: dz_mi -= L
        if dz_mi < -L/2: dz_mi += L
        z_profile.append({
            "z": z, "dz": round(float(dz_mi), 1),
            "dsg": round(float(dsg[ix, iy, z]), 6),
            "sm":  round(float(sm_np[ix, iy, z]), 4)
        })

    # --- 2. Equatorial radial profile (x-axis through ring equator) ---
    x_profile = []
    for x in range(L):
        dx_mi = x - RX
        if dx_mi > L/2: dx_mi -= L
        if dx_mi < -L/2: dx_mi += L
        x_profile.append({
            "x": x, "dx": round(float(dx_mi), 1),
            "dsg": round(float(dsg[x, iy, iz]), 6),
            "sm":  round(float(sm_np[x, iy, iz]), 4)
        })

    # --- 3. Spherical shell average delta_sigma_g(r) ---
    r_max = L//2 - 1; n_bins = r_max
    xs = np.arange(L); xx,yy,zz = np.meshgrid(xs,xs,xs,indexing='ij')
    dx_a = xx - RX; dy_a = yy - RY; dz_a = zz - RZ
    dx_a -= np.round(dx_a/L)*L
    dy_a -= np.round(dy_a/L)*L
    dz_a -= np.round(dz_a/L)*L
    r_arr = np.sqrt(dx_a**2+dy_a**2+dz_a**2)

    shell_r=[]; shell_dsg=[]; shell_count=[]
    for b in range(n_bins):
        r_lo=b; r_hi=b+1
        mask=(r_arr>=r_lo)&(r_arr<r_hi)
        cnt=int(mask.sum())
        if cnt>0:
            shell_r.append(round(float(np.mean(r_arr[mask])),3))
            shell_dsg.append(round(float(np.mean(dsg[mask])),6))
            shell_count.append(cnt)

    # --- 4. Fit to Yukawa: dsg(r) = A * exp(-r/lambda) / r ---
    # Use shell data at r > 2 (avoid ring interior)
    fit_r=[]; fit_y=[]
    for r,d,c in zip(shell_r, shell_dsg, shell_count):
        if r>2.5 and r<r_max-1 and c>3:
            fit_r.append(r); fit_y.append(d)

    lambda_fit=None; A_fit=None
    if len(fit_r)>=4:
        # log-linear: log(|dsg|*r) = log(|A|) - r/lambda
        fr=np.array(fit_r); fy=np.array(fit_y)
        # Only use negative (attractive) points
        neg_mask=fy<0
        if neg_mask.sum()>=3:
            fr2=fr[neg_mask]; fy2=fy[neg_mask]
            log_y=np.log(np.abs(fy2)*fr2+1e-12)
            # Linear fit: log_y = a + b*r
            A_mat=np.vstack([np.ones_like(fr2),fr2]).T
            try:
                coeffs=np.linalg.lstsq(A_mat,log_y,rcond=None)[0]
                b=coeffs[1]
                if b<0:
                    lambda_fit=round(float(-1./b),3)
                    A_fit=round(float(-np.exp(coeffs[0])),6)
            except Exception:
                pass

    # --- 5. Bipolar: north vs south ---
    north_mask=(dz_a>3); south_mask=(dz_a<-3); bulk_mask=(np.abs(dz_a)<=3)
    dsg_north=float(np.mean(dsg[north_mask])) if north_mask.any() else 0.
    dsg_south=float(np.mean(dsg[south_mask])) if south_mask.any() else 0.
    dsg_bulk=float(np.mean(np.abs(dsg[bulk_mask]))) if bulk_mask.any() else 0.
    bipolar_ratio=abs(dsg_north-dsg_south)/(dsg_bulk+1e-12)

    min_dsg=float(np.min(dsg))
    min_loc=np.unravel_index(np.argmin(dsg),dsg.shape)

    print(f"  min(delta_sg)={min_dsg:.6f} at {min_loc}")
    print(f"  Yukawa fit: lambda={lambda_fit}  A={A_fit}")
    print(f"  Bipolar: north={dsg_north:.6f}  south={dsg_south:.6f}  "
          f"bulk={dsg_bulk:.6f}  ratio={bipolar_ratio:.3f}")
    print(f"  M_ring={ring_mass(sm):.1f}")

    return {
        "min_dsg": round(min_dsg,6),
        "min_dsg_location": list(min_loc),
        "lambda_fit": lambda_fit,
        "A_fit": A_fit,
        "dsg_north": round(dsg_north,6),
        "dsg_south": round(dsg_south,6),
        "dsg_bulk": round(dsg_bulk,6),
        "bipolar_ratio": round(bipolar_ratio,4),
        "M_ring": round(ring_mass(sm),1),
        "z_axis_profile": z_profile,
        "equatorial_profile": x_profile,
        "shell_r": shell_r,
        "shell_dsg": shell_dsg
    }

def build_and_measure(q_twist, label):
    phi=init_phi_gpu(q_twist)
    sg=xp.full((L,L,L),SIGMA_REF,dtype=xp.float32)
    sm=xp.full((L,L,L),SIGMA_REF,dtype=xp.float32)
    chi=xp.zeros((L,L,L),dtype=xp.float32)

    print(f"  Phase 1 ({PHASE1})...", flush=True)
    for _ in range(PHASE1):
        sgb=nb6(sg); smb=nb6(sm)
        sg=xp.clip(sg+ALPHA*(SIGMA_REF-sg)+BETA*(sgb-sg),0.,1.)
        sm=xp.clip(sm+ALPHA*(SIGMA_REF-sm)+BETA*(smb-sm),0.,1.)
        chi=chi*(1-CHI_DECAY)+CHI_REL*(sgb-sg)+DELTA*(SIGMA_REF-sg)
        phi=_phi_align(sm,phi)

    print(f"  Phase 2 dissipative ({PHASE2_DISS}, K_GM={K_GM})...", flush=True)
    t0=time.time()
    for t in range(1,PHASE2_DISS+1):
        sg,sm,chi,phi=step_dissipative(sg,sm,chi,phi)
        if t%500==0:
            M=ring_mass(sm)
            sg_min=float(xp.min(sg).get() if xp.__name__=='cupy' else xp.min(sg))
            print(f"    t={t:5d}: M={M:.1f}  sg_min={sg_min:.5f}  "
                  f"({time.time()-t0:.0f}s)", flush=True)

    print(f"  Measuring gravitational field...", flush=True)
    return measure_gravity(sg, sm, label), sg, sm

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    args=p.parse_args(); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)

    print("QNG-CPU-071: Hopfion vs ring — gravitational field sigma_g profile")
    print(f"Device: {DEVICE}  K_GM={K_GM}  Phase2={PHASE2_DISS} diss steps")
    print()

    results={}
    for label,q_twist in [("ring_Q0",0),("hopfion_Q1",1)]:
        print(f"Building {label} (q_twist={q_twist})...", flush=True)
        grav,sg,sm=build_and_measure(q_twist,label)
        results[label]={"q_twist":q_twist,"gravity":grav}
        print()

    print("="*70)
    g0=results["ring_Q0"]["gravity"]
    g1=results["hopfion_Q1"]["gravity"]

    # Check 1: gravitational well exists (min delta_sg < -1e-4)
    c1_ring = g0["min_dsg"] < -1e-4
    c1_hopf = g1["min_dsg"] < -1e-4
    c1 = c1_ring and c1_hopf

    # Check 2: Hopfion deeper well
    c2 = abs(g1["min_dsg"]) > abs(g0["min_dsg"])

    # Check 3: Yukawa fit finite lambda
    c3_ring  = g0["lambda_fit"] is not None and 1 < g0["lambda_fit"] < L/2
    c3_hopf  = g1["lambda_fit"] is not None and 1 < g1["lambda_fit"] < L/2
    c3 = c3_ring or c3_hopf

    # Check 4 (info): bipolar
    c4_ring  = g0["bipolar_ratio"] > 0.5
    c4_hopf  = g1["bipolar_ratio"] > 0.5

    print(f"Ring Q=0:    min_dsg={g0['min_dsg']:.6f}  lambda={g0['lambda_fit']}  "
          f"bipolar_ratio={g0['bipolar_ratio']:.3f}")
    print(f"Hopfion Q=1: min_dsg={g1['min_dsg']:.6f}  lambda={g1['lambda_fit']}  "
          f"bipolar_ratio={g1['bipolar_ratio']:.3f}")
    print()
    print(f"Check 1 (grav well < -1e-4): ring={c1_ring} hopfion={c1_hopf} -> "
          f"{'PASS' if c1 else 'FAIL'}")
    print(f"Check 2 (Hopfion deeper): |{g1['min_dsg']:.6f}| > |{g0['min_dsg']:.6f}| -> "
          f"{'PASS' if c2 else 'FAIL'}")
    print(f"Check 3 (Yukawa lambda finite): ring={g0['lambda_fit']} hopfion={g1['lambda_fit']} -> "
          f"{'PASS' if c3 else 'FAIL'}")
    print(f"Check 4 (bipolar, info): ring={c4_ring}({g0['bipolar_ratio']:.3f}) "
          f"hopfion={c4_hopf}({g1['bipolar_ratio']:.3f})")

    overall="pass" if (c1 and c2) else "fail"
    print(f"\nqng_hopfion_gravity_reference: {overall.upper()}")

    report={"test_id":"QNG-CPU-071","decision":overall,"device":DEVICE,
            "K_GM":K_GM,"phase2_diss":PHASE2_DISS,
            "checks":{"grav_well_exists":c1,"hopfion_deeper":c2,
                      "yukawa_lambda_finite":c3,
                      "bipolar_ring":c4_ring,"bipolar_hopfion":c4_hopf},
            "ring_Q0":results["ring_Q0"],"hopfion_Q1":results["hopfion_Q1"]}
    rp=out/"report.json"
    with open(rp,"w") as f: json.dump(report,f,indent=2)
    print(f"\nReport: {rp}")
    return 0 if overall=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
