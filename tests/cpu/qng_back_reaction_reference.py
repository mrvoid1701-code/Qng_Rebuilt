from __future__ import annotations

"""QNG-CPU-073: Back-reaction test.

v7-original:   sigma_m does NOT respond to sigma_g (current DER-QNG-033).
v7-symmetric:  sigma_m_i += K_GM*(sigma_g_i - SIGMA_REF)  (term B from DER-QNG-036).

A static sigma_g well is pinned at GZ=3. A vortex ring is formed at center (10,10,10).
Test: does the ring centroid drift toward the well with term B active?

Gate: drift_symmetric > 0.5 lu AND extra_drift > 0.5 lu AND both rings alive.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-back-reaction-v1"

# --- Lattice ---
L = 20
N = L * L * L

# --- Physics ---
SIGMA_REF = 0.5
ALPHA = 0.005
BETA = 0.35
BETA_PHI = 0.02
DELTA = 0.20
CHI_DECAY = 0.020   # Gap 8 stability: K_BACK*DELTA=0.020 < ALPHA+CHI_DECAY*(1-ALPHA)=0.0249
CHI_REL = 0.35
GAMMA_PHI = 0.10
K_BACK = 0.10
K_GM = 0.050

# --- Ring ---
RING_R = 3.0
RX = RY = RZ = 10.0

# --- Gravity pin ---
GX = GY = 10
GZ = 3
PIN_RADIUS = 2.0
PIN_SG = 0.20   # sigma_g pinned below ref (delta = 0.30); strong signal

# --- Run ---
PHASE1 = 300
PHASE2 = 3000
TRACK_EVERY = 100


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def idx3(x, y, z):
    return (x % L) * L * L + (y % L) * L + (z % L)


def coord3(i):
    x = i // (L * L)
    y = (i % (L * L)) // L
    z = i % L
    return x, y, z


def _mi(d):
    while d > L / 2:
        d -= L
    while d < -L / 2:
        d += L
    return d


def wrap(a):
    a = a % (2 * math.pi)
    return a - 2 * math.pi if a > math.pi else a


def adiff(a, b):
    return wrap(a - b)


def clip01(x):
    return max(0.0, min(1.0, x))


def nb(x, y, z):
    return [
        idx3(x - 1, y, z), idx3(x + 1, y, z),
        idx3(x, y - 1, z), idx3(x, y + 1, z),
        idx3(x, y, z - 1), idx3(x, y, z + 1),
    ]


# Pre-compute neighbor lists and pin set
NBS = [nb(*coord3(i)) for i in range(N)]

PINS = frozenset(
    i for i in range(N)
    if math.sqrt(
        _mi(coord3(i)[0] - GX) ** 2 +
        _mi(coord3(i)[1] - GY) ** 2 +
        _mi(coord3(i)[2] - GZ) ** 2
    ) <= PIN_RADIUS
)


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init_phi():
    p = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - RX); dy = _mi(y - RY); dz = _mi(z - RZ)
        rho = math.sqrt(dx * dx + dy * dy)
        p.append(math.atan2(dz, rho - RING_R))
    return p


def disorder(phi, i):
    nbs = NBS[i]
    sx = sum(math.cos(phi[j]) for j in nbs) / 6.0
    sy = sum(math.sin(phi[j]) for j in nbs) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx * sx + sy * sy))


# ---------------------------------------------------------------------------
# Step functions
# ---------------------------------------------------------------------------

def _phi_mean(sm, phi, nbs):
    tw = sum(sm[j] for j in nbs)
    if tw > 1e-10:
        sx2 = sum(sm[j] * math.cos(phi[j]) for j in nbs) / tw
        sy2 = sum(sm[j] * math.sin(phi[j]) for j in nbs) / tw
        return math.atan2(sy2, sx2)
    return None


def step_v7_original(sg, sm, chi, phi, k_gm, use_pin):
    """Standard v7: sigma_m does NOT respond to sigma_g."""
    nsg = [0.0] * N
    nsm = [0.0] * N
    nc  = [0.0] * N
    np_ = [0.0] * N
    for i in range(N):
        nbs = NBS[i]
        s = sg[i]; m = sm[i]; c = chi[i]; p = phi[i]
        sgb = sum(sg[j] for j in nbs) / 6.0
        smb = sum(sm[j] for j in nbs) / 6.0

        # sigma_g: A + B + G + coupling
        if use_pin and i in PINS:
            nsg[i] = PIN_SG
            nc[i] = 0.0
        else:
            dsg = (ALPHA * (SIGMA_REF - s)
                   + BETA * (sgb - s)
                   + K_BACK * c
                   - k_gm * (SIGMA_REF - m))
            nsg[i] = clip01(s + dsg)
            nc[i] = (c * (1.0 - CHI_DECAY)
                     + CHI_REL * (sgb - s)
                     + DELTA * (SIGMA_REF - s))

        # sigma_m: A + B + F  (NO back-reaction)
        dsm = (ALPHA * (SIGMA_REF - m)
               + BETA * (smb - m)
               - GAMMA_PHI * disorder(phi, i) * m)
        nsm[i] = clip01(m + dsm)

        # phi
        pm = _phi_mean(sm, phi, nbs)
        np_[i] = wrap(p + BETA_PHI * adiff(pm if pm is not None else p, p))

    return nsg, nsm, nc, np_


def step_v7_symmetric(sg, sm, chi, phi, k_gm, use_pin):
    """v7-symmetric: sigma_m += K_GM*(sigma_g_i - SIGMA_REF)  [term B, DER-QNG-036]."""
    nsg = [0.0] * N
    nsm = [0.0] * N
    nc  = [0.0] * N
    np_ = [0.0] * N
    for i in range(N):
        nbs = NBS[i]
        s = sg[i]; m = sm[i]; c = chi[i]; p = phi[i]
        sgb = sum(sg[j] for j in nbs) / 6.0
        smb = sum(sm[j] for j in nbs) / 6.0

        # sigma_g: A + B + G + coupling  (same as original)
        if use_pin and i in PINS:
            nsg[i] = PIN_SG
            nc[i] = 0.0
        else:
            dsg = (ALPHA * (SIGMA_REF - s)
                   + BETA * (sgb - s)
                   + K_BACK * c
                   - k_gm * (SIGMA_REF - m))
            nsg[i] = clip01(s + dsg)
            nc[i] = (c * (1.0 - CHI_DECAY)
                     + CHI_REL * (sgb - s)
                     + DELTA * (SIGMA_REF - s))

        # sigma_m: A + B + F + BACK-REACTION (term B from DER-QNG-036)
        back_rxn = k_gm * (sg[i] - SIGMA_REF)   # < 0 near gravity well
        dsm = (ALPHA * (SIGMA_REF - m)
               + BETA * (smb - m)
               - GAMMA_PHI * disorder(phi, i) * m
               + back_rxn)
        nsm[i] = clip01(m + dsm)

        # phi
        pm = _phi_mean(sm, phi, nbs)
        np_[i] = wrap(p + BETA_PHI * adiff(pm if pm is not None else p, p))

    return nsg, nsm, nc, np_


# ---------------------------------------------------------------------------
# Observables
# ---------------------------------------------------------------------------

def z_centroid(sm):
    """Sigma_m-depletion-weighted z-coordinate of ring."""
    num = den = 0.0
    for i in range(N):
        _, _, z = coord3(i)
        dep = max(0.0, SIGMA_REF - sm[i])
        num += dep * z
        den += dep
    return num / den if den > 1e-10 else RZ


def ring_mass(sm):
    return sum(max(0.0, SIGMA_REF - sm[i]) for i in range(N))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("QNG-CPU-073: Back-reaction test (v7-symmetric vs v7-original)")
    print(f"L={L}  R={RING_R}  K_GM={K_GM}  K_BACK={K_BACK}  CHI_DECAY={CHI_DECAY}")
    print(f"Ring center: ({RX},{RY},{RZ})  Pin: ({GX},{GY},{GZ})  "
          f"PIN_R={PIN_RADIUS}  PIN_SG={PIN_SG}")
    dist_ring_pin = min(abs(RZ - GZ), L - abs(RZ - GZ))
    print(f"Pin nodes: {len(PINS)}  Distance ring-to-pin: {dist_ring_pin:.1f} lu")
    print(f"Gap 8 criterion: K_BACK*DELTA={K_BACK*DELTA:.4f} < "
          f"ALPHA+CHI_DECAY*(1-ALPHA)={ALPHA+CHI_DECAY*(1-ALPHA):.4f}  "
          f"{'OK' if K_BACK*DELTA < ALPHA+CHI_DECAY*(1-ALPHA) else 'VIOLATED'}")
    print()

    # --- Phase 1: form ring without gravity (no pin, k_gm=0) ---
    sg = [SIGMA_REF] * N
    sm = [SIGMA_REF] * N
    chi = [0.0] * N
    phi = init_phi()
    for _ in range(PHASE1):
        sg, sm, chi, phi = step_v7_original(sg, sm, chi, phi, 0.0, use_pin=False)

    M0 = ring_mass(sm)
    z0 = z_centroid(sm)
    print(f"After Phase 1: M={M0:.1f}  z_centroid={z0:.4f}")
    print()

    # --- Branch: copy state for two scenarios ---
    sg_a, sm_a, chi_a, phi_a = list(sg), list(sm), list(chi), list(phi)
    sg_b, sm_b, chi_b, phi_b = list(sg), list(sm), list(chi), list(phi)

    # Activate pin at start of Phase 2
    for i in PINS:
        sg_a[i] = PIN_SG; chi_a[i] = 0.0
        sg_b[i] = PIN_SG; chi_b[i] = 0.0

    track_a = []
    track_b = []

    print(f"  {'step':>5}  {'z_orig':>9}  {'z_sym':>9}  {'M_orig':>8}  {'M_sym':>8}")

    for t in range(1, PHASE2 + 1):
        sg_a, sm_a, chi_a, phi_a = step_v7_original(
            sg_a, sm_a, chi_a, phi_a, K_GM, use_pin=True)
        sg_b, sm_b, chi_b, phi_b = step_v7_symmetric(
            sg_b, sm_b, chi_b, phi_b, K_GM, use_pin=True)

        if t % TRACK_EVERY == 0:
            za = z_centroid(sm_a)
            zb = z_centroid(sm_b)
            ma = ring_mass(sm_a)
            mb = ring_mass(sm_b)
            track_a.append({"t": t, "z_cen": round(za, 4), "M": round(ma, 2)})
            track_b.append({"t": t, "z_cen": round(zb, 4), "M": round(mb, 2)})
            print(f"  {t:5d}  {za:9.4f}  {zb:9.4f}  {ma:8.1f}  {mb:8.1f}", flush=True)

    z_fin_a = track_a[-1]["z_cen"]
    z_fin_b = track_b[-1]["z_cen"]
    M_fin_a = track_a[-1]["M"]
    M_fin_b = track_b[-1]["M"]

    drift_a = z0 - z_fin_a          # positive = moved toward pin (lower z)
    drift_b = z0 - z_fin_b
    extra_drift = drift_b - drift_a  # extra drift due to back-reaction

    print()
    print(f"z_centroid initial          : {z0:.4f}")
    print(f"z_centroid final (original) : {z_fin_a:.4f}  drift={drift_a:+.4f} lu")
    print(f"z_centroid final (symmetric): {z_fin_b:.4f}  drift={drift_b:+.4f} lu")
    print(f"Extra drift from back-rxn   : {extra_drift:+.4f} lu")
    print(f"M_final original            : {M_fin_a:.1f}")
    print(f"M_final symmetric           : {M_fin_b:.1f}")
    print()

    check1 = drift_b > 0.5
    check2 = extra_drift > 0.5
    check3 = M_fin_a > 50.0 and M_fin_b > 50.0
    decision = check1 and check2 and check3

    print("Checks:")
    print(f"  Check 1 (drift_sym > 0.5 lu toward pin) : "
          f"{'PASS' if check1 else 'FAIL'}  [{drift_b:.4f}]")
    print(f"  Check 2 (extra_drift > 0.5 lu)          : "
          f"{'PASS' if check2 else 'FAIL'}  [{extra_drift:.4f}]")
    print(f"  Check 3 (both M_final > 50)             : "
          f"{'PASS' if check3 else 'FAIL'}  [orig={M_fin_a:.1f}, sym={M_fin_b:.1f}]")
    print()
    print(f"qng_back_reaction_reference: {'PASS' if decision else 'FAIL'}")

    report = {
        "test_id": "QNG-CPU-073",
        "decision": "pass" if decision else "fail",
        "params": {
            "L": L, "K_GM": K_GM, "K_BACK": K_BACK, "CHI_DECAY": CHI_DECAY,
            "PIN_SG": PIN_SG, "PIN_RADIUS": PIN_RADIUS,
            "PHASE1": PHASE1, "PHASE2": PHASE2,
        },
        "results": {
            "z_initial": round(z0, 4),
            "z_final_original": round(z_fin_a, 4),
            "z_final_symmetric": round(z_fin_b, 4),
            "drift_original": round(drift_a, 4),
            "drift_symmetric": round(drift_b, 4),
            "extra_drift": round(extra_drift, 4),
            "M_final_original": round(M_fin_a, 2),
            "M_final_symmetric": round(M_fin_b, 2),
        },
        "checks": {
            "drift_toward_pin": check1,
            "extra_drift_from_backreaction": check2,
            "rings_alive": check3,
        },
        "track_original": track_a,
        "track_symmetric": track_b,
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)

    summary = [
        "# QNG-CPU-073 Back-Reaction Test",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Physics tested",
        "DER-QNG-036 predicts back-reaction term (B):",
        "  sigma_m_i += K_GM * (sigma_g_i - SIGMA_REF)  (matter falls into gravity wells)",
        "This term is absent from current v7 (DER-QNG-033).",
        "Test: ring centroid drifts toward static sigma_g depletion pin when (B) is active.",
        "",
        "## Results",
        "| Metric | Value |",
        "|--------|-------|",
        f"| z_centroid initial       | {z0:.4f} |",
        f"| Drift original v7        | {drift_a:+.4f} lu |",
        f"| Drift symmetric v7       | {drift_b:+.4f} lu |",
        f"| Extra drift (back-rxn)   | {extra_drift:+.4f} lu |",
        f"| M_final original         | {M_fin_a:.1f} |",
        f"| M_final symmetric        | {M_fin_b:.1f} |",
        "",
        "## Checks",
        f"- Check 1 drift_sym > 0.5 lu : {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 extra_drift > 0.5 lu: {'PASS' if check2 else 'FAIL'}",
        f"- Check 3 rings alive         : {'PASS' if check3 else 'FAIL'}",
    ]
    (out / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(f"\nReport: {rp}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
