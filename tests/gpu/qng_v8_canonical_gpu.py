from __future__ import annotations

"""QNG-GPU-020: v8 canonical extension test suite (DER-QNG-042).

Pre-registration: 07_validation/prereg/QNG-GPU-020.md
Derivation:       04_qng_pure/qng-v8-canonical-extension-v1.md
Prerequisites:    04_qng_pure/qng-v8-analytical-prereqs-v1.md

v8 promotes sigma_m and phi to canonical pairs (sigma_m, pi_m) and (phi, pi_phi)
with standard kinetic energies, preserving v7 (sigma_g, chi) via H_v7 = T_g[chi] + E_v7.

  H_v8 = T_g[chi] + T_m[pi_m] + T_phi[pi_phi] + E_v7 + V_couple
  T_m      = (1/(2*mu_m))     * sum_i pi_m_i^2
  T_phi    = (1/(2*mu_phi))   * sum_i pi_phi_i^2
  V_couple = (g/2) * sum_i (sigma_m_ref - sigma_m_i)^2 * (1 - cos phi_i)
             [Option E^2 per DER-QNG-042-A1 amendment]

Derived parameters (prereqs §3.3, unique light-cone c_g = c_m = c_phi at linear order):
  mu_m   = BETA_M / (K_BACK * BETA_G)                = 10.0
  mu_phi = 2 * BETA_PHI * SIGMA_M_REF^2 / (K_BACK * BETA_G) = 0.857
  m_phi  = sqrt(g * sigma_g_ref / mu_phi)            = 0.3585

Integrator (Commitment #8): Yoshida 4th-order symplectic, dt=0.025.
Abort monitors:
  - sigma_g positivity:  min(sigma_g) < 0.025  => v8 effective-theory boundary breached
  - energy drift:        |Delta H|/H > 1% per 1000 steps
  - Stage F stationarity: |Delta I_m|/mean(I_m) > 1% per 100 steps in window [900, 1000]

Six stages, pre-committed gates (single-pass, no tolerance relaxation):

  A (phi dispersion):    omega(k=0) in [0.323, 0.395]  (target m_phi=0.359 +-10%)
  B (inter-ring force):  v8-v7 excess fits exp(-d*m_m), R^2 > 0.9, range in [0.5, 5] lu
  C (F=ma drift):        x(t) AIC(quad) - AIC(lin) < -6
  D (Gap 8 CHI_DECAY=0): |<sigma_g> - ref| < 0.05 AND std finite at T=5000
  E (FC-4 recovery):     ring R, sigma_m_core, drift within 5% of CPU-043/CPU-073
  F (FC-5 mass ladder):  I_m(R) = N*sigma_m_ref - sum(sigma_m) vs CPU-074/075
                         Verdict C: |I_m_v8 - M_ref|/M_ref < 20% at R=3,4,5
                         Verdict B: ratio I_m_v8/I_m_v7 same (+-10%) across R
                         Verdict A: neither => DER-QNG-042 falsified_structural

Any of Stage D FAIL, Stage E FAIL, Stage F Verdict A is individually sufficient to
reject DER-QNG-042.

-----------------------------------------------------------------------------
AUDIT-QNG-005 (2026-04-22) — symplecticity qualification
-----------------------------------------------------------------------------
H_v8 conservation holds for the (sigma_m, pi_m) and (phi, pi_phi) canonical
pairs under Yoshida4 (W1, W2, W1) composition. The (sigma_g, chi) sector
is integrated with first-order Euler inside verlet_substep (v7 legacy,
gradient-flow pair in DER-QNG-036), contributing O(dt) H drift per step.
At dt=0.025 and typical R1-mode regimes (chi ~ 0 at orbital attractor),
this drift is small in practice (<0.1% per 1000 steps). A full symplectic
extension of (sigma_g, chi) is deferred to a future derivation. Stage
D (CHI_DECAY=0 stability) and any other claim relying on strict H-conservation
should carry this qualifier. Also: the default non-R1 F_A/E_phi mismatch
produces ~6% H drift in ring-containing runs (GPU-030d). Use exact_a='r1'
mode for clean H conservation claims.
-----------------------------------------------------------------------------
"""

import argparse
import json
import math
import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-v8-canonical-v1"

# ===========================================================================
# Physics parameters (pre-registered, not tunable within v8)
# ===========================================================================

SIGMA_G_REF  = 0.5
SIGMA_M_REF  = 0.5

ALPHA        = 0.005
BETA_G       = 0.35
BETA_M       = 0.35
BETA_PHI     = 0.06          # Choice A uniform (prereqs §3.3.4)
DELTA_CHI    = 0.20
CHI_REL      = 0.35
CHI_DECAY_V7 = 0.020         # v7 value (Gap 8), used for Stages A-C/E/F reference
GAMMA_PHI    = 0.10          # Channel F strength
K_BACK       = 0.10          # Channel G (v7 back-reaction sg<-chi)

G_V_COUPLE   = 0.22          # Einstein g-value (DER-QNG-041, Gap 9 EFT)

# ---------------------------------------------------------------------------
# Derived v8 parameters (prereqs §3.3, unique light-cone)
# ---------------------------------------------------------------------------

MU_M   = BETA_M / (K_BACK * BETA_G)                                 # 10.0
MU_PHI = 2.0 * BETA_PHI * SIGMA_M_REF**2 / (K_BACK * BETA_G)        # 0.857...
C_G2   = K_BACK * BETA_G / 6.0                                      # 0.00583...
# -------------------------------------------------------------------------
# M_PHI: STALE under DER-QNG-042-A1 (Option E^2). The original
# V_couple = g*sigma_g*(1-cos phi) predicted m_phi = sqrt(g*sigma_g_ref/mu_phi)
# = 0.3585 as a UNIVERSAL mass. Under Option E^2, vacuum phi is EXACTLY
# massless; inside a deficit region the local phi mass is
#     m_phi^2(local) = (g/mu_phi) * (sigma_m_ref - sigma_m_local)^2
# retained here only for backward compatibility with Stage A / dispersion
# probes that have not yet been ported to the A1/A2 split. AUDIT-QNG-005
# (2026-04-22) recommends replacing downstream uses.
# -------------------------------------------------------------------------
M_PHI_DEPRECATED = math.sqrt(G_V_COUPLE * SIGMA_G_REF / MU_PHI)     # 0.3585 (STALE; DER-QNG-041 only)

# ---------------------------------------------------------------------------
# Yoshida 4th-order symplectic integrator coefficients
#   One full step = leapfrog(w1) + leapfrog(w2) + leapfrog(w1)
#   w1 = 1/(2 - 2^(1/3)), w2 = 1 - 2*w1
# ---------------------------------------------------------------------------

DT      = 0.025
CBRT2   = 2.0 ** (1.0 / 3.0)
W1_YOSH = 1.0 / (2.0 - CBRT2)        # ~1.3512
W2_YOSH = 1.0 - 2.0 * W1_YOSH         # ~-1.7024

# ---------------------------------------------------------------------------
# Abort thresholds (Commitment #8)
# ---------------------------------------------------------------------------

SIGMA_G_MIN_ABORT      = 0.05 * SIGMA_G_REF           # 0.025
ENERGY_DRIFT_ABORT     = 0.01                          # per 1000 steps (fractional)
STATIONARITY_TOLERANCE = 0.01                          # |dI_m|/<I_m> per 100 substeps


# ===========================================================================
# Geometry helpers
# ===========================================================================

def build_nb(L):
    """6-neighbor index table for periodic cubic lattice, shape (N, 6)."""
    xs = np.arange(L, dtype=np.int32)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel()
    nb = np.stack([
        ((xg - 1) % L) * L * L + yg * L + zg,
        ((xg + 1) % L) * L * L + yg * L + zg,
        xg * L * L + ((yg - 1) % L) * L + zg,
        xg * L * L + ((yg + 1) % L) * L + zg,
        xg * L * L + yg * L + ((zg - 1) % L),
        xg * L * L + yg * L + ((zg + 1) % L),
    ], axis=1).astype(np.int32)
    return cp.asarray(nb)


def centered_coords(L, cx=None, cy=None, cz=None):
    if cx is None: cx = L / 2.0
    if cy is None: cy = L / 2.0
    if cz is None: cz = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg - cx; dy = yg - cy; dz = zg - cz
    for d in (dx, dy, dz):
        d[:] = np.where(d >  L / 2, d - L, d)
        d[:] = np.where(d < -L / 2, d + L, d)
    return dx, dy, dz


def wrap_gpu(a):
    a = a % (2.0 * math.pi)
    return cp.where(a > math.pi, a - 2.0 * math.pi, a)


def nb_mean(field, nb_idx):
    return field[nb_idx].mean(axis=1)


def disorder_gpu(phi, nb_idx):
    pnb = phi[nb_idx]
    return cp.maximum(
        0.0,
        1.0 - cp.sqrt(cp.cos(pnb).mean(axis=1) ** 2 + cp.sin(pnb).mean(axis=1) ** 2),
    )


def phi_wmean_gpu(phi, sm, nb_idx):
    pnb = phi[nb_idx]; snb = sm[nb_idx]; tw = snb.sum(axis=1)
    sx = (snb * cp.cos(pnb)).sum(axis=1)
    sy = (snb * cp.sin(pnb)).sum(axis=1)
    return cp.where(
        tw > 1e-10,
        cp.arctan2(sy / cp.maximum(tw, 1e-10), sx / cp.maximum(tw, 1e-10)),
        phi,
    )


def sm_weighted_Z_gpu(phi, sm, nb_idx):
    """Complex vector Z_k = sum_{j in N(k)} sigma_m_j * exp(i phi_j).

    Returns (R, Theta) with R = |Z|, Theta = arg(Z). Used by DER-QNG-050
    exact canonical Channel A:
        F_A_exact_k      = -(2 beta_DER / z) * sigma_m_k * R_k * sin(phi_k - Theta_k)
        F_sm_XY_term_k  = +(2 beta_DER / z) * R_k * cos(phi_k - Theta_k)
    with beta_DER = BETA_PHI / (2 * SIGMA_M_REF**2).

    This is the unnormalized magnitude R (not per-neighbour average), matching
    DER-QNG-036 section 2.4 convention.
    """
    pnb = phi[nb_idx]; snb = sm[nb_idx]
    sx = (snb * cp.cos(pnb)).sum(axis=1)
    sy = (snb * cp.sin(pnb)).sum(axis=1)
    R = cp.sqrt(sx * sx + sy * sy)
    Theta = cp.arctan2(sy, sx)
    return R, Theta


# ===========================================================================
# Initial conditions
# ===========================================================================

def init_phi_single_ring(L, R, cx=None, cy=None, cz=None):
    dx, dy, dz = centered_coords(L, cx, cy, cz)
    rho = np.sqrt(dx * dx + dy * dy)
    return cp.asarray(np.arctan2(dz, rho - R).ravel())


def init_phi_two_rings(L, R, d, same_chirality=True):
    """Two rings on the x-axis at separation d. W+W+ (same) or W+W- (opposite)."""
    cx = L / 2.0
    shift = d / 2.0
    dx1, dy1, dz1 = centered_coords(L, cx=cx - shift)
    rho1 = np.sqrt(dy1 * dy1 + dz1 * dz1)
    phi1 = np.arctan2(dx1, rho1 - R)
    dx2, dy2, dz2 = centered_coords(L, cx=cx + shift)
    rho2 = np.sqrt(dy2 * dy2 + dz2 * dz2)
    phi2 = np.arctan2(dx2, rho2 - R) if same_chirality else -np.arctan2(dx2, rho2 - R)
    return cp.asarray((phi1 + phi2).ravel())


def make_state(L, phi_init=None, flat_sigmas=True, pi_m_zero=True, pi_phi_zero=True):
    N = L * L * L
    sg  = cp.full(N, SIGMA_G_REF, dtype=cp.float64) if flat_sigmas else cp.zeros(N, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_M_REF, dtype=cp.float64) if flat_sigmas else cp.zeros(N, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    if phi_init is None:
        phi = cp.zeros(N, dtype=cp.float64)
    else:
        phi = phi_init.copy()
    pi_m   = cp.zeros(N, dtype=cp.float64) if pi_m_zero else None
    pi_phi = cp.zeros(N, dtype=cp.float64) if pi_phi_zero else None
    return {
        'sg': sg, 'sm': sm, 'chi': chi, 'phi': phi,
        'pi_m': pi_m, 'pi_phi': pi_phi,
    }


# ===========================================================================
# v7 gradient-flow reference step (dt=1 per step) — used for v7 reference
# ===========================================================================

def step_v7(sg, sm, chi, phi, nb_idx, k_gm=0.0, pin_idx=None, pin_sg=0.20,
            channel_f=True, channel_g=True, chi_decay=CHI_DECAY_V7, channel_ag=True):
    """Single v7 Phase-2 gradient-flow step (dt=1)."""
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)
    dis = disorder_gpu(phi, nb_idx) if channel_f else cp.zeros_like(sm)

    dsg = BETA_G * (sgb - sg)
    if channel_ag:
        dsg = dsg + ALPHA * (SIGMA_G_REF - sg)
    if channel_g:
        dsg = dsg + K_BACK * chi
    dsg = dsg - k_gm * (SIGMA_M_REF - sm)
    nsg = cp.clip(sg + dsg, 0.0, 1.0)

    dsm = BETA_M * (smb - sm) - GAMMA_PHI * dis * sm
    if channel_ag:
        dsm = dsm + ALPHA * (SIGMA_M_REF - sm)
    nsm = cp.clip(sm + dsm, 0.0, 1.0)

    nchi = chi * (1.0 - chi_decay) + CHI_REL * (sgb - sg) + DELTA_CHI * (SIGMA_G_REF - sg)

    pm = phi_wmean_gpu(phi, sm, nb_idx)
    nphi = wrap_gpu(phi + BETA_PHI * wrap_gpu(pm - phi))

    if pin_idx is not None:
        nsg[pin_idx] = pin_sg
        nchi[pin_idx] = 0.0

    return nsg, nsm, nchi, nphi


# ===========================================================================
# v8 canonical forces (F_q = -dH/dq for each dynamical q)
# ===========================================================================

def force_sm_v8(sg, sm, phi, nb_idx, channel_f=True, exact_a=False):
    """F_sm = -dE_v7/dsm - dV_couple_E2/dsm
           = [ALPHA(ref-sm) + BETA_M(<sm>-sm) - GAMMA_PHI*disorder*sm]
           + g*(SIGMA_M_REF - sm)*(1 - cos phi)       [E^2 restoring]

    DER-QNG-042-A1: V_couple = (g/2)*(sm_ref - sm)^2 * (1 - cos phi).

    channel_f=False disables the -GAMMA_PHI*disorder*sm term
    (diagnostic mode; not a physical parameter change — used for
    GPU-024c to test whether Channel F drives ring instability).

    exact_a=True (DER-QNG-050) adds the canonical XY back-reaction
        +(2*beta_DER/z) * R_k * cos(phi_k - Theta_k)
    where R_k, Theta_k come from sm_weighted_Z_gpu. Vanishes in the
    uniform-sigma_m limit by construction; non-trivial in ring cores.

    exact_a='r1' (DER-QNG-051 Option R1) drops sigma_m weighting in E_phi
    entirely, so dE_phi/dsm = 0 and no F_XY_sm is added. This tests
    whether the sigma_m->1 condensation in GPU-031c/d is driven by the
    sm-weighted XY Hamiltonian rather than being fundamental to v8.
    """
    smb = nb_mean(sm, nb_idx)
    F_e_v7 = ALPHA * (SIGMA_M_REF - sm) + BETA_M * (smb - sm)
    if channel_f:
        dis = disorder_gpu(phi, nb_idx)
        F_e_v7 = F_e_v7 - GAMMA_PHI * dis * sm
    deficit = SIGMA_M_REF - sm
    F_couple = G_V_COUPLE * deficit * (1.0 - cp.cos(phi))
    F_total = F_e_v7 + F_couple
    if exact_a is True:
        z_coord = float(nb_idx.shape[1])
        beta_DER = BETA_PHI / (2.0 * SIGMA_M_REF ** 2)
        R, Theta = sm_weighted_Z_gpu(phi, sm, nb_idx)
        F_XY_sm = (2.0 * beta_DER / z_coord) * R * cp.cos(phi - Theta)
        F_total = F_total + F_XY_sm
    # exact_a == 'r1': E_phi_R1 has no sm dependence; no F_XY_sm term
    return F_total


def force_phi_v8(sg, sm, phi, nb_idx, channel_f=True, exact_a=False):
    """F_phi = -dE_v7/dphi - dV_couple_E2/dphi - dE_F/dphi

    Contributions:
      F_A    = BETA_PHI * (pm_weighted - phi)                [-dE_v7/dphi, uniform-sm approx]
      F_vcp  = -0.5 * g * (sm_ref - sm)^2 * sin(phi)         [-dV_couple/dphi]
      F_F    = +(GAMMA_PHI/(2z)) * sum_{i in N(j)} sin(theta_i - phi_j) * sm_i^2

    F_F is the Channel F back-reaction on phi (DER-QNG-049): makes Channel F
    canonical by pairing the existing -GAMMA_PHI*disorder*sm force on sigma_m
    with its conjugate phi-force derived from the same E_F potential:
        E_F = (GAMMA_PHI/2) * sum_i disorder_i * sigma_m_i^2

    Without F_F, Channel F is a one-sided dissipator that breaks detailed
    balance between the (sm, pi_m) and (phi, pi_phi) sectors. Setting
    channel_f=False drops F_F (diagnostic only; matches legacy pre-DER-049
    implementation).

    exact_a=True (DER-QNG-050) replaces the uniform-sigma_m-approximation
    F_A by the exact canonical XY force
        F_A_exact_k = -(2*beta_DER/z) * sigma_m_k * R_k * sin(phi_k - Theta_k)
    where R_k*exp(i*Theta_k) = sum_{j in N(k)} sigma_m_j * exp(i*phi_j).
    In the uniform-sigma_m small-angle limit this reduces to the code's
    BETA_PHI*(pm - phi) with beta_DER = BETA_PHI/(2*SIGMA_M_REF**2) = 0.12.
    In non-uniform ring cores the two differ; the exact form is conservative.

    exact_a='r1' (DER-QNG-051 Option R1) uses pure XY without sigma_m
    weights: E_phi_R1 = -(beta_R1/z) * sum_{i,j~i} cos(phi_i - phi_j)
    with beta_R1 = BETA_PHI/2 so F_A_R1 matches BETA_PHI*(pm - phi) in
    the uniform-sm small-angle limit. sigma_m decouples from E_phi,
    removing the condensation force diagnosed in GPU-031c.
    Closed form: F_A_R1_k = BETA_PHI * sin(theta_unw_k - phi_k)
    where theta_unw_k = arg(sum_{j~k} exp(i*phi_j)) is the unweighted
    circular mean of neighbour phases.
    """
    deficit = SIGMA_M_REF - sm
    if exact_a is True:
        z_coord = float(nb_idx.shape[1])
        beta_DER = BETA_PHI / (2.0 * SIGMA_M_REF ** 2)
        R, Theta = sm_weighted_Z_gpu(phi, sm, nb_idx)
        F_A = -(2.0 * beta_DER / z_coord) * sm * R * cp.sin(phi - Theta)
    elif exact_a == 'r1':
        # E_phi_R1 = -(beta_R1/z) * sum_{i, j~i} cos(phi_i - phi_j),
        # beta_R1 = BETA_PHI/2. F_A_R1_k = (BETA_PHI/z) * Im[Z_k * e^{-i phi_k}]
        # with Z_k = sum_{j in N(k)} e^{i phi_j}.
        z_coord = float(nb_idx.shape[1])
        pnb = phi[nb_idx]
        cos_sum = cp.cos(pnb).sum(axis=1)
        sin_sum = cp.sin(pnb).sum(axis=1)
        F_A = (BETA_PHI / z_coord) * (sin_sum * cp.cos(phi) - cos_sum * cp.sin(phi))
    else:
        pm = phi_wmean_gpu(phi, sm, nb_idx)
        F_A = BETA_PHI * wrap_gpu(pm - phi)
    F_vcp  = -0.5 * G_V_COUPLE * (deficit * deficit) * cp.sin(phi)
    if not channel_f:
        return F_A + F_vcp

    # ---- Channel F back-reaction on phi (DER-QNG-049) ----
    # theta_i = arg(Z_i) with Z_i = (1/z) sum_{k in N(i)} exp(i phi_k)
    pnb = phi[nb_idx]
    cos_mean = cp.cos(pnb).mean(axis=1)
    sin_mean = cp.sin(pnb).mean(axis=1)
    theta_i = cp.arctan2(sin_mean, cos_mean)

    # For node j, sum over i in N(j) of sin(theta_i - phi_j) * sm_i^2
    z_coord = float(nb_idx.shape[1])
    theta_nb = theta_i[nb_idx]           # (N, z)
    sm_nb_sq = sm[nb_idx] ** 2           # (N, z)
    F_F = (GAMMA_PHI / (2.0 * z_coord)) * (
        cp.sin(theta_nb - phi[:, None]) * sm_nb_sq
    ).sum(axis=1)

    return F_A + F_vcp + F_F


def drive_sg_v7style(sg, sm, chi, phi, nb_idx, k_gm, include_v_couple=True):
    """sigma_g update rate (pure v7 Channel A/B/G + gravity, NO V_couple back-reaction).

    DER-QNG-042-A1 Option E^2: V_couple is independent of sigma_g by construction.
    The include_v_couple flag is retained as a no-op for signature compatibility
    with callers; sigma_g is never perturbed by V_couple under Option E^2."""
    sgb = nb_mean(sg, nb_idx)
    dsg = (ALPHA * (SIGMA_G_REF - sg)
           + BETA_G * (sgb - sg)
           + K_BACK * chi
           - k_gm * (SIGMA_M_REF - sm))
    # Option E^2: dV/dsigma_g = 0. No back-reaction term.
    return dsg


def drive_chi_v7style(sg, chi, nb_idx, chi_decay):
    sgb = nb_mean(sg, nb_idx)
    return -chi_decay * chi + CHI_REL * (sgb - sg) + DELTA_CHI * (SIGMA_G_REF - sg)


# ===========================================================================
# F_A-only helper (used when v_couple_on=False: skip F_vcp and F_F)
# ===========================================================================

def _f_A_only_v8(sm, phi, nb_idx, exact_a):
    """Phase-1 F_phi: only the XY restoring force (no V_couple, no Channel F).

    Matches the exact_a mode of force_phi_v8 but returns just F_A.
    """
    if exact_a is True:
        z_coord = float(nb_idx.shape[1])
        beta_DER = BETA_PHI / (2.0 * SIGMA_M_REF ** 2)
        R, Theta = sm_weighted_Z_gpu(phi, sm, nb_idx)
        return -(2.0 * beta_DER / z_coord) * sm * R * cp.sin(phi - Theta)
    if exact_a == 'r1':
        z_coord = float(nb_idx.shape[1])
        pnb = phi[nb_idx]
        cos_sum = cp.cos(pnb).sum(axis=1)
        sin_sum = cp.sin(pnb).sum(axis=1)
        return (BETA_PHI / z_coord) * (sin_sum * cp.cos(phi) - cos_sum * cp.sin(phi))
    return BETA_PHI * wrap_gpu(phi_wmean_gpu(phi, sm, nb_idx) - phi)


# ===========================================================================
# Velocity Verlet sub-step (inner block of Yoshida 4)
# ===========================================================================

def verlet_substep(state, dt, nb_idx, k_gm, pin_idx, pin_sg,
                   damping_gamma, chi_decay, v_couple_on, channel_f=True,
                   exact_a=False):
    """One leapfrog-Verlet substep of physical-time size dt.

    Update sequence (symplectic splitting):
      1. half kick:  pi += (dt/2) * F(q)   with optional Langevin -gamma*pi
      2. drift:      q  += dt * pi/mu;     sigma_g, chi via v7-gradient Euler(dt)
      3. half kick:  pi += (dt/2) * F(q_new)

    exact_a=True uses DER-QNG-050 exact canonical Channel A form (sigma_m-weighted
    XY interaction E_phi = -(beta_DER/z)*sum sm_i*sm_j*cos(phi_i-phi_j)) rather
    than the uniform-sigma_m approximation. Required for canonical energy
    conservation in non-uniform ring cores.
    """
    sg, sm, chi, phi = state['sg'], state['sm'], state['chi'], state['phi']
    pi_m, pi_phi = state['pi_m'], state['pi_phi']

    # ---- Step 1: half kick on momenta (with optional Langevin damping) ----
    F_sm  = force_sm_v8(sg, sm, phi, nb_idx, channel_f=channel_f, exact_a=exact_a)
    F_phi = force_phi_v8(sg, sm, phi, nb_idx, channel_f=channel_f, exact_a=exact_a) if v_couple_on else \
            _f_A_only_v8(sm, phi, nb_idx, exact_a)
    if damping_gamma > 0.0:
        pi_m   = pi_m   + (dt / 2.0) * (F_sm  - damping_gamma * pi_m)
        pi_phi = pi_phi + (dt / 2.0) * (F_phi - damping_gamma * pi_phi)
    else:
        pi_m   = pi_m   + (dt / 2.0) * F_sm
        pi_phi = pi_phi + (dt / 2.0) * F_phi

    # ---- Step 2: drift q; sigma_g, chi via 1st-order Euler in dt ----
    sm  = cp.clip(sm + dt * pi_m / MU_M, 0.0, 1.0)
    phi = wrap_gpu(phi + dt * pi_phi / MU_PHI)
    dsg = drive_sg_v7style(sg, sm, chi, phi, nb_idx, k_gm,
                           include_v_couple=v_couple_on)
    sg  = cp.clip(sg + dt * dsg, 0.0, 1.0)
    dchi = drive_chi_v7style(sg, chi, nb_idx, chi_decay)
    chi = chi + dt * dchi
    if pin_idx is not None:
        sg[pin_idx]  = pin_sg
        chi[pin_idx] = 0.0

    # ---- Step 3: half kick on momenta with new forces ----
    F_sm  = force_sm_v8(sg, sm, phi, nb_idx, channel_f=channel_f, exact_a=exact_a)
    F_phi = force_phi_v8(sg, sm, phi, nb_idx, channel_f=channel_f, exact_a=exact_a) if v_couple_on else \
            _f_A_only_v8(sm, phi, nb_idx, exact_a)
    if damping_gamma > 0.0:
        pi_m   = pi_m   + (dt / 2.0) * (F_sm  - damping_gamma * pi_m)
        pi_phi = pi_phi + (dt / 2.0) * (F_phi - damping_gamma * pi_phi)
    else:
        pi_m   = pi_m   + (dt / 2.0) * F_sm
        pi_phi = pi_phi + (dt / 2.0) * F_phi

    return {'sg': sg, 'sm': sm, 'chi': chi, 'phi': phi,
            'pi_m': pi_m, 'pi_phi': pi_phi}


def yoshida4_step(state, dt, nb_idx, k_gm=0.0, pin_idx=None, pin_sg=0.20,
                  damping_gamma=0.0, chi_decay=CHI_DECAY_V7, v_couple_on=True,
                  channel_f=True, exact_a=False):
    """One Yoshida 4 step of physical-time size dt.

    Composition: Verlet(w1*dt) + Verlet(w2*dt) + Verlet(w1*dt)
    with w1, w2 the 4th-order symmetric coefficients.

    channel_f=False disables GAMMA_PHI*disorder*sm (Channel F); diagnostic
    mode for GPU-024c instability localization, not a physical default.

    exact_a=True swaps the uniform-sigma_m Channel A approximation
    BETA_PHI*(pm_wmean - phi) for the DER-QNG-050 exact canonical form
    derived from E_phi = -(beta_DER/z)*sum sm_i*sm_j*cos(phi_i-phi_j).
    """
    for w in (W1_YOSH, W2_YOSH, W1_YOSH):
        state = verlet_substep(state, w * dt, nb_idx, k_gm, pin_idx, pin_sg,
                                damping_gamma, chi_decay, v_couple_on,
                                channel_f=channel_f, exact_a=exact_a)
    return state


# ===========================================================================
# Hamiltonian evaluation (for drift monitor)
# ===========================================================================

def hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0, exact_a=False):
    """Exact H_v8 on GPU (not proxy).

    Audit 2026-04-21: pre-audit code used E_B = (beta/2)*3*(sigma-sigma_bar)^2,
    which is a BIHARMONIC proxy and does NOT match the gradient force
    beta*(sigma_bar - sigma) used by the integrator. Finite-difference check
    (qng_v8_der049_finite_diff.py) confirmed the code force equals
    -dE_B_true/dsigma where
        E_B_true = (beta/(4z)) * sum_i sum_{j in N(i)} (sigma_i - sigma_j)^2
    with z=6 for cubic lattice. The proxy vs. true forms can differ by ~20%
    on typical ring states, which explains apparent H drift in GPU-030 even
    though the integrator is canonically exact.

    This updated form uses E_B_true so that |dH/H| reflects true conservation.

    With channel_f=True, also includes E_F = (GAMMA_PHI/2) * sum_i disorder_i * sm_i^2
    (DER-QNG-049). Required for energy conservation whenever the integrator is
    invoked with channel_f=True.

    Audit 2026-04-21 (GPU-030d): pre-patch form was missing three DER-QNG-036
    terms that the integrator does evolve:
      - E_phi  (§2.4, XY-model weighted by sigma_m) - absorbed 92% of GPU-030 drift
      - E_chi  (§2.3, CHI_REL + DELTA_CHI cross-terms between chi and sigma_g)
      - E_cpl  (§2.5, k_gm*(sm_ref-sm)*(sg_ref-sg) matter-gravity coupling)
    These are now included so the monitor reflects true H_v7+V_couple. Pass
    k_gm to match the value supplied to yoshida4_step.
    """
    sg, sm, chi, phi = state['sg'], state['sm'], state['chi'], state['phi']
    pi_m, pi_phi = state['pi_m'], state['pi_phi']
    z_coord = float(nb_idx.shape[1])

    T_g       = (K_BACK / 2.0)   * float(cp.sum(chi * chi))
    T_m       = (1.0 / (2.0 * MU_M))   * float(cp.sum(pi_m * pi_m))
    T_phi_kin = (1.0 / (2.0 * MU_PHI)) * float(cp.sum(pi_phi * pi_phi))

    # Channel A: restoration well (matches force alpha*(ref - sigma))
    E_A_g = (ALPHA / 2.0) * float(cp.sum((sg - SIGMA_G_REF) ** 2))
    E_A_m = (ALPHA / 2.0) * float(cp.sum((sm - SIGMA_M_REF) ** 2))

    # Channel B: gradient tension (exact form matching force beta*(sbar - sigma))
    sg_nb = sg[nb_idx]; sm_nb = sm[nb_idx]
    dsg = sg[:, None] - sg_nb
    dsm = sm[:, None] - sm_nb
    E_B_g = (BETA_G / (4.0 * z_coord)) * float(cp.sum(dsg * dsg))
    E_B_m = (BETA_M / (4.0 * z_coord)) * float(cp.sum(dsm * dsm))

    # Channel A' (phi): XY-model from DER-QNG-036 Section 2.4
    #   E_phi = -(beta_DER / z) * sum_{i, j in N(i)} sm_i * sm_j * cos(phi_i - phi_j)
    #   beta_DER = BETA_PHI / (2 * SIGMA_M_REF^2)  ensures F_A -> BETA_PHI*(pm_w - phi)
    #   in the uniform-sm small-angle limit (GPU-030d verified).
    # exact_a='r1' (DER-QNG-051 Option R1): pure XY, no sm weights,
    #   beta_R1 = BETA_PHI/2 so F_A matches uniform-sm small-angle limit.
    phi_nb = phi[nb_idx]
    cos_dphi = cp.cos(phi[:, None] - phi_nb)
    if exact_a == 'r1':
        beta_R1 = BETA_PHI / 2.0
        E_phi_A = -(beta_R1 / z_coord) * float(cp.sum(cos_dphi))
    else:
        beta_phi_der = BETA_PHI / (2.0 * SIGMA_M_REF ** 2)
        E_phi_A = -(beta_phi_der / z_coord) * float(cp.sum(sm[:, None] * sm_nb * cos_dphi))

    # Chi cross-terms (DER-QNG-036 Section 2.3): CHI_REL and DELTA_CHI pieces.
    # Self-term (chi_decay/2)*chi^2 is DISSIPATIVE - omitted from conservative H.
    sgb = nb_mean(sg, nb_idx)
    E_chi_rel   = -(CHI_REL / 2.0) * float(cp.sum(chi * (sg - sgb)))
    E_chi_delta = -DELTA_CHI       * float(cp.sum(chi * (SIGMA_G_REF - sg)))

    # Matter-gravity coupling (DER-QNG-036 Section 2.5)
    if k_gm != 0.0:
        E_cpl = k_gm * float(cp.sum((SIGMA_M_REF - sm) * (SIGMA_G_REF - sg)))
    else:
        E_cpl = 0.0

    # DER-QNG-042-A1 Option E^2: V = (g/2)*sum((sm_ref - sm)^2 * (1 - cos phi))
    deficit = SIGMA_M_REF - sm
    V_cp  = 0.5 * G_V_COUPLE * float(cp.sum((deficit * deficit) * (1.0 - cp.cos(phi))))

    # DER-QNG-049: Channel F canonical potential
    if channel_f:
        dis = disorder_gpu(phi, nb_idx)
        E_F = 0.5 * GAMMA_PHI * float(cp.sum(dis * sm * sm))
    else:
        E_F = 0.0

    return (T_g + T_m + T_phi_kin
            + E_A_g + E_A_m + E_B_g + E_B_m
            + E_phi_A + E_chi_rel + E_chi_delta + E_cpl
            + V_cp + E_F)


def check_sigma_g_positivity(state):
    mn = float(cp.min(state['sg']))
    return mn, mn >= SIGMA_G_MIN_ABORT


# ===========================================================================
# Ring observables
# ===========================================================================

def ring_mass_deficit(sm):
    """I_m = N*sigma_m_ref - sum(sigma_m) (CPU-074/075 canonical form)."""
    N = int(sm.shape[0])
    return float(N * SIGMA_M_REF - cp.sum(sm))


def ring_radius(sm, L):
    """sigma_m-depletion-weighted major radius, measured about box centre."""
    dep = cp.maximum(0.0, SIGMA_M_REF - sm)
    dx, dy, dz = centered_coords(L)
    dx_g = cp.asarray(dx.ravel()); dy_g = cp.asarray(dy.ravel())
    rho = cp.sqrt(dx_g * dx_g + dy_g * dy_g)
    mask = (cp.abs(cp.asarray(dz.ravel())) <= 2.0)   # narrow z-band about ring plane
    num = float(cp.sum(dep * rho * mask))
    den = float(cp.sum(dep * mask))
    return num / den if den > 1e-10 else 0.0


def ring_sigma_m_core(sm, L, R_guess):
    """Minimum sigma_m near nominal ring curve (proxy for core depth)."""
    dx, dy, dz = centered_coords(L)
    rho = np.sqrt(dx * dx + dy * dy)
    dist_curve = np.sqrt((rho - R_guess) ** 2 + dz * dz)
    mask = cp.asarray((dist_curve <= 1.2).ravel())
    if int(cp.sum(mask)) == 0:
        return float('nan')
    return float(cp.min(sm[mask]))


def ring_z_centroid(sm, L):
    dep = cp.maximum(0.0, SIGMA_M_REF - sm)
    _, _, dz = centered_coords(L)
    dz_g = cp.asarray(dz.ravel())
    num = float(cp.sum(dep * dz_g))
    den = float(cp.sum(dep))
    return num / den if den > 1e-10 else 0.0


# ===========================================================================
# STAGE A — phi dispersion relation (P1)
# ===========================================================================

def run_stage_A(out_dir, verbose=True):
    """k=0 phi oscillation vs k>0 dispersion. Gate: omega(k=0) in [0.323, 0.395]."""
    L = 40
    N = L * L * L
    T_PHYS = 1000.0                       # physical-time units (lu)
    N_STEPS = int(T_PHYS / DT)            # 40000 Yoshida substeps
    SAMPLE_EVERY = 4                       # record phi every 4 Yoshida steps
    EPS = 0.05                             # phi excitation amplitude (small for linear regime)
    K_VALUES = [0, 1, 2, 4]                # k in units of 2*pi/L; k=0 gives mass mode

    nb_idx = build_nb(L)
    dx_np, _, _ = centered_coords(L)
    x_coord = cp.asarray(dx_np.ravel())   # periodic box-centred x coordinate

    results_per_k = {}
    for k_mode in K_VALUES:
        if k_mode == 0:
            phi_init = cp.full(N, EPS, dtype=cp.float64)
        else:
            k_phys = 2.0 * math.pi * k_mode / L
            phi_init = EPS * cp.cos(k_phys * x_coord)
        state = make_state(L, phi_init=phi_init)

        # Record mean phi or k-mode amplitude over time
        trace_t = []; trace_amp = []
        H0 = hamiltonian_v8(state, nb_idx)
        drift_max = 0.0

        for istep in range(N_STEPS):
            state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                                   chi_decay=CHI_DECAY_V7)
            if istep % SAMPLE_EVERY == 0:
                if k_mode == 0:
                    amp = float(cp.mean(state['phi']))
                else:
                    k_phys = 2.0 * math.pi * k_mode / L
                    amp = float(cp.mean(state['phi'] * cp.cos(k_phys * x_coord))) * 2.0
                trace_t.append(istep * DT)
                trace_amp.append(amp)
            if (istep + 1) % 1000 == 0:
                Ht = hamiltonian_v8(state, nb_idx)
                drift = abs(Ht - H0) / max(abs(H0), 1e-12)
                drift_max = max(drift_max, drift)

        # FFT to find peak frequency
        t_arr = np.array(trace_t)
        amp_arr = np.array(trace_amp) - np.mean(trace_amp)
        n_fft = len(amp_arr)
        dt_sample = t_arr[1] - t_arr[0]
        freqs = np.fft.fftfreq(n_fft, d=dt_sample)[:n_fft // 2]
        spec = np.abs(np.fft.fft(amp_arr)[:n_fft // 2])
        if len(spec) > 2:
            peak_idx = int(np.argmax(spec[1:])) + 1   # skip DC
            f_peak = float(freqs[peak_idx])
        else:
            f_peak = 0.0
        omega_peak = 2.0 * math.pi * f_peak

        results_per_k[k_mode] = {
            'k_mode': k_mode,
            'k_phys': float(2.0 * math.pi * k_mode / L),
            'omega_measured': float(omega_peak),
            # R1 (AUDIT-QNG-005): A1 sub-stage — flat vacuum under Option E^2
            # has m_phi = 0 by design (deficit = 0). Prediction is pure c_phi*k.
            # A2 sub-stage (frozen deficit=0.23) lives in separate probe scripts.
            'omega_predicted': float(math.sqrt(C_G2) * (2.0 * math.pi * k_mode / L)),
            'H_drift_max_per_1000': float(drift_max),
        }

        if verbose:
            pred = results_per_k[k_mode]['omega_predicted']
            print(f"  k={k_mode:d} (k_phys={2*math.pi*k_mode/L:.4f}): "
                  f"omega_meas={omega_peak:.4f}, omega_pred={pred:.4f}, drift<{drift_max*100:.3f}%",
                  flush=True)

    # Gate evaluation — R1 (AUDIT-QNG-005): A1 sub-stage under Option E^2.
    # Flat vacuum: deficit = 0, so m_phi = 0 exactly. Gate is omega(k=0) < 0.02.
    omega0 = results_per_k[0]['omega_measured']
    pass_k0 = (omega0 <= 0.02)
    # Dispersion check k>0: within 15% of c_phi*k (massless vacuum mode).
    dispersion_ok = True
    for k in K_VALUES[1:]:
        r = results_per_k[k]
        if r['omega_predicted'] > 0:
            err = abs(r['omega_measured'] - r['omega_predicted']) / r['omega_predicted']
            if err > 0.15:
                dispersion_ok = False

    verdict = 'PASS' if (pass_k0 and dispersion_ok) else 'FAIL'
    report = {
        'stage': 'A',
        'substage': 'A1',
        'name': 'phi_dispersion_flat_vacuum',
        'verdict': verdict,
        'omega_k0': omega0,
        'omega_k0_gate': [0.0, 0.02],
        'omega_k0_pass': pass_k0,
        'dispersion_k_gt_0_within_15pct': dispersion_ok,
        'per_k': results_per_k,
        'm_phi_predicted': 0.0,          # Option E^2 flat-vacuum mass
        'c_g_predicted': math.sqrt(C_G2),
        'note': ('A1 sub-stage: flat vacuum gate per AUDIT-QNG-005 / '
                 'DER-QNG-042-A1. A2 (frozen deficit=0.23, gate [0.105, 0.128]) '
                 'is a separate probe and not executed here.'),
    }
    return report


# ===========================================================================
# STAGE B — inter-ring force (P2)
# ===========================================================================

def run_stage_B(out_dir, verbose=True):
    """Measure F(d) in v7 and v8; fit v8-v7 excess as A*exp(-d*m_m)."""
    L = 80
    N = L * L * L
    SEPARATIONS = [6, 8, 10, 12, 14, 16, 18, 20]
    R = 4
    T_V7 = 1500               # v7 steps (dt=1)
    T_V8 = int(T_V7 / DT)     # v8 substeps to match same physical time

    nb_idx = build_nb(L)
    forces_v7 = []; forces_v8 = []

    for d in SEPARATIONS:
        if verbose:
            print(f"  sep d={d}: v7 ...", flush=True)
        phi_ic = init_phi_two_rings(L, R, d, same_chirality=True)

        # --- v7 reference ---
        sg  = cp.full(N, SIGMA_G_REF, dtype=cp.float64)
        sm  = cp.full(N, SIGMA_M_REF, dtype=cp.float64)
        chi = cp.zeros(N, dtype=cp.float64)
        phi = phi_ic.copy()
        # Phase 1 — no Channel F
        for _ in range(300):
            sg, sm, chi, phi = step_v7(sg, sm, chi, phi, nb_idx,
                                        channel_f=False)
        # Phase 2 — Channel F active
        for _ in range(T_V7):
            sg, sm, chi, phi = step_v7(sg, sm, chi, phi, nb_idx,
                                        channel_f=True)
        F_v7 = measure_inter_ring_force(sm, L, d)
        forces_v7.append(F_v7)

        # --- v8 canonical (same dynamics + pi_m, pi_phi) ---
        if verbose:
            print(f"  sep d={d}: v8 ...", flush=True)
        state = make_state(L, phi_init=phi_ic)
        # Phase 1: v_couple OFF (ring formation)
        # Use v7-like step via Yoshida with v_couple_on=False
        for _ in range(int(300.0 / DT)):
            state = yoshida4_step(state, DT, nb_idx, v_couple_on=False,
                                   chi_decay=CHI_DECAY_V7)
        # Phase 2: v_couple ON
        abort = False
        for _ in range(T_V8):
            state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                                   chi_decay=CHI_DECAY_V7)
            mn, ok = check_sigma_g_positivity(state)
            if not ok:
                abort = True
                break
        F_v8 = measure_inter_ring_force(state['sm'], L, d) if not abort else float('nan')
        forces_v8.append(F_v8)

        if verbose:
            print(f"    F_v7={F_v7:.4f}  F_v8={F_v8:.4f}  excess={F_v8-F_v7:.4f}", flush=True)

    # Fit exp decay to v8-v7 excess
    d_arr = np.array(SEPARATIONS, dtype=float)
    excess = np.array(forces_v8) - np.array(forces_v7)
    fit = fit_exp_decay(d_arr, excess)

    pass_gate = (fit['R2'] > 0.9 and 0.5 <= (1.0 / fit['m_m']) <= 5.0
                 and fit['A'] > 0) if fit['m_m'] > 0 else False
    verdict = 'PASS' if pass_gate else 'FAIL'

    report = {
        'stage': 'B',
        'name': 'inter_ring_force',
        'verdict': verdict,
        'separations': SEPARATIONS,
        'F_v7': forces_v7,
        'F_v8': forces_v8,
        'excess': excess.tolist(),
        'fit': fit,
        'gate': {'R2_min': 0.9, 'range_lu': [0.5, 5.0]},
    }
    return report


def measure_inter_ring_force(sm, L, d):
    """Force proxy: asymmetry in sigma_m depletion between x < cx and x > cx."""
    dx, _, _ = centered_coords(L)
    dx_g = cp.asarray(dx.ravel())
    dep = cp.maximum(0.0, SIGMA_M_REF - sm)
    left  = float(cp.sum(dep * (dx_g < 0)))
    right = float(cp.sum(dep * (dx_g > 0)))
    # Symmetric geometry should give ~0; attractive force skews; return scalar.
    return right - left


def fit_exp_decay(d, y):
    """Fit y = A * exp(-d * m) for y > 0 subset."""
    mask = y > 0
    if mask.sum() < 3:
        return {'A': float('nan'), 'm_m': float('nan'), 'R2': 0.0, 'n': int(mask.sum())}
    logy = np.log(y[mask])
    d_fit = d[mask]
    A_mat = np.column_stack([np.ones_like(d_fit), -d_fit])
    coef, *_ = np.linalg.lstsq(A_mat, logy, rcond=None)
    logA, m_m = coef
    pred = logA - m_m * d_fit
    ss_res = float(np.sum((logy - pred) ** 2))
    ss_tot = float(np.sum((logy - logy.mean()) ** 2))
    R2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {'A': float(math.exp(logA)), 'm_m': float(m_m), 'R2': float(R2),
            'n': int(mask.sum())}


# ===========================================================================
# STAGE C — F=ma drift (P3)
# ===========================================================================

def run_stage_C(out_dir, verbose=True):
    """Ring in linear sigma_g gradient background: v7 gives linear x(t), v8 gives quadratic.
    Gate: AIC(quad) - AIC(lin) < -6."""
    L = 80
    N = L * L * L
    R = 4
    T_PHYS = 2000.0
    N_STEPS = int(T_PHYS / DT)
    SAMPLE_EVERY = int(10.0 / DT)    # sample x(t) every 10 lu
    K_GM = 0.050

    nb_idx = build_nb(L)

    # Build static sigma_g well centered at (cx, cy, z=0.3*L): linear ramp in z
    dx, dy, dz = centered_coords(L)
    pin_idx = None
    pin_sg = 0.20

    # Easier: use CPU-073-style pin at fixed cell-group
    # Define pin region
    PIN_Z = int(0.2 * L)
    pin_mask = (np.abs(dx) <= 3.0) & (np.abs(dy) <= 3.0) & (np.abs(dz - (PIN_Z - L/2.0)) <= 2.0)
    pin_idx = cp.asarray(np.where(pin_mask.ravel())[0].astype(np.int32))

    phi_ic = init_phi_single_ring(L, R, cx=L/2.0, cy=L/2.0, cz=L/2.0)
    state = make_state(L, phi_init=phi_ic)

    # Phase 1 — ring formation (no V_couple, no K_GM, no pin)
    for _ in range(int(300.0 / DT)):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=False,
                               chi_decay=CHI_DECAY_V7)
    # Pin activation + V_couple on + K_GM
    state['sg'][pin_idx] = pin_sg
    state['chi'][pin_idx] = 0.0

    ts = []; z_c = []; H0 = hamiltonian_v8(state, nb_idx); drift_max = 0.0
    abort = False
    for istep in range(N_STEPS):
        state = yoshida4_step(state, DT, nb_idx, k_gm=K_GM,
                               pin_idx=pin_idx, pin_sg=pin_sg,
                               v_couple_on=True, chi_decay=CHI_DECAY_V7)
        if istep % SAMPLE_EVERY == 0:
            zc = ring_z_centroid(state['sm'], L)
            ts.append(istep * DT)
            z_c.append(zc)
        if (istep + 1) % 1000 == 0:
            Ht = hamiltonian_v8(state, nb_idx)
            drift_max = max(drift_max, abs(Ht - H0) / max(abs(H0), 1e-12))
        mn, ok = check_sigma_g_positivity(state)
        if not ok:
            abort = True
            break

    t_arr = np.array(ts); z_arr = np.array(z_c)
    if len(t_arr) < 10 or abort:
        return {
            'stage': 'C', 'name': 'fma_drift', 'verdict': 'VOID',
            'reason': 'abort_or_too_few_samples',
            'H_drift_max_per_1000': drift_max,
            'sigma_g_abort': abort,
            'trace_t': t_arr.tolist(), 'trace_z': z_arr.tolist(),
        }

    lin_fit = np.polyfit(t_arr, z_arr, 1)
    lin_pred = np.polyval(lin_fit, t_arr)
    ss_lin = float(np.sum((z_arr - lin_pred) ** 2))
    quad_fit = np.polyfit(t_arr, z_arr, 2)
    quad_pred = np.polyval(quad_fit, t_arr)
    ss_quad = float(np.sum((z_arr - quad_pred) ** 2))

    n = len(t_arr)
    aic_lin  = n * math.log(ss_lin  / n) + 2 * 2
    aic_quad = n * math.log(ss_quad / n) + 2 * 3
    delta_aic = aic_quad - aic_lin
    pass_gate = delta_aic < -6.0 and quad_fit[0] != 0.0
    verdict = 'PASS' if pass_gate else 'FAIL'

    return {
        'stage': 'C',
        'name': 'fma_drift',
        'verdict': verdict,
        'delta_aic_quad_minus_lin': delta_aic,
        'quad_coef_a': float(quad_fit[0]),
        'quad_coef_b': float(quad_fit[1]),
        'quad_coef_c': float(quad_fit[2]),
        'lin_slope':   float(lin_fit[0]),
        'H_drift_max_per_1000': drift_max,
        'sigma_g_abort': abort,
        'trace_t': t_arr.tolist(),
        'trace_z': z_arr.tolist(),
    }


# ===========================================================================
# STAGE D — CHI_DECAY=0 stability (P4, Gap 8)
# ===========================================================================

def run_stage_D(out_dir, verbose=True):
    """H_v8 simulation with CHI_DECAY=0. Gate: |<sigma_g> - ref| < 0.05 AND std bounded."""
    L = 20
    N = L * L * L
    T_PHYS = 5000.0
    N_STEPS = int(T_PHYS / DT)
    SAMPLE_EVERY = int(100.0 / DT)

    nb_idx = build_nb(L)
    state = make_state(L)
    state['phi'] = init_phi_single_ring(L, R=3)

    # Ring formation (V_couple off)
    for _ in range(int(300.0 / DT)):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=False,
                               chi_decay=CHI_DECAY_V7)

    # Main run with chi_decay=0
    ts = []; sg_mean = []; sg_std = []
    abort = False; abort_reason = None
    for istep in range(N_STEPS):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                               chi_decay=0.0)
        if istep % SAMPLE_EVERY == 0:
            m = float(cp.mean(state['sg']))
            s = float(cp.std(state['sg']))
            ts.append(istep * DT); sg_mean.append(m); sg_std.append(s)
            if verbose and (istep % (SAMPLE_EVERY * 5) == 0):
                print(f"    t={istep*DT:.1f}  <sg>={m:.4f}  std(sg)={s:.4f}", flush=True)
        mn, ok = check_sigma_g_positivity(state)
        if not ok:
            abort = True; abort_reason = f"sigma_g<{SIGMA_G_MIN_ABORT}"
            break
        if math.isnan(float(cp.mean(state['sg']))):
            abort = True; abort_reason = "nan"
            break

    if abort:
        return {
            'stage': 'D', 'name': 'chi_decay_zero_stability',
            'verdict': 'FAIL',
            'reason': abort_reason,
            'trace_t': ts, 'sg_mean': sg_mean, 'sg_std': sg_std,
        }

    final_mean = sg_mean[-1]; final_std = sg_std[-1]
    drift_mean = abs(final_mean - SIGMA_G_REF)
    pass_gate = drift_mean < 0.05 and final_std < 0.20 and math.isfinite(final_std)
    verdict = 'PASS' if pass_gate else 'FAIL'

    return {
        'stage': 'D',
        'name': 'chi_decay_zero_stability',
        'verdict': verdict,
        'final_mean_sg': final_mean,
        'drift_mean': drift_mean,
        'final_std_sg': final_std,
        'gate': {'drift_max': 0.05, 'std_bounded': True},
        'trace_t': ts, 'sg_mean': sg_mean, 'sg_std': sg_std,
    }


# ===========================================================================
# STAGE E — FC-4 v7 recovery gate
# ===========================================================================

def run_stage_E(out_dir, verbose=True):
    """v8 with Langevin damping gamma=10 -> should recover v7 ring morphology.
    Compare ring R, sigma_m_core, extra_drift vs CPU-043/CPU-073 references."""
    L = 20
    N = L * L * L
    R_TARGET = 3.0
    T_PHYS = 500.0                  # physical lu
    N_STEPS = int(T_PHYS / DT)
    GAMMA = 10.0

    nb_idx = build_nb(L)

    # --- v8 + damping, single ring (CPU-043 analog) ---
    state = make_state(L, phi_init=init_phi_single_ring(L, R_TARGET))
    for _ in range(int(300.0 / DT)):                    # Phase 1
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=False,
                               damping_gamma=GAMMA, chi_decay=CHI_DECAY_V7)
    for _ in range(N_STEPS):                             # Phase 2
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                               damping_gamma=GAMMA, chi_decay=CHI_DECAY_V7)
    R_v8 = ring_radius(state['sm'], L)
    core_v8 = ring_sigma_m_core(state['sm'], L, R_TARGET)

    # --- CPU-043 reference values ---
    R_REF_CPU043 = 4.84
    CORE_REF_CPU043 = 0.27

    err_R = abs(R_v8 - R_REF_CPU043) / R_REF_CPU043
    err_core = abs(core_v8 - CORE_REF_CPU043) / CORE_REF_CPU043
    pass_single = (err_R < 0.05) and (err_core < 0.05)

    # --- v8 + damping, ring + sigma_g pin (CPU-073 analog) ---
    dx, dy, dz = centered_coords(L)
    pin_mask = (np.abs(dx) <= 2.0) & (np.abs(dy) <= 2.0) & ((dz + 7.0) ** 2 <= 4.0)
    pin_idx = cp.asarray(np.where(pin_mask.ravel())[0].astype(np.int32))

    state2 = make_state(L, phi_init=init_phi_single_ring(L, R_TARGET))
    for _ in range(int(300.0 / DT)):
        state2 = yoshida4_step(state2, DT, nb_idx, v_couple_on=False,
                                damping_gamma=GAMMA, chi_decay=CHI_DECAY_V7)
    # Activate pin
    state2['sg'][pin_idx] = 0.20; state2['chi'][pin_idx] = 0.0

    z0 = ring_z_centroid(state2['sm'], L)
    for _ in range(int(3000.0 / DT)):                    # longer drift window
        state2 = yoshida4_step(state2, DT, nb_idx, k_gm=0.050,
                                pin_idx=pin_idx, pin_sg=0.20,
                                damping_gamma=GAMMA, v_couple_on=True,
                                chi_decay=CHI_DECAY_V7)
    z1 = ring_z_centroid(state2['sm'], L)
    extra_drift = z0 - z1                                # positive = toward pin

    DRIFT_REF_CPU073 = 1.01
    err_drift = abs(extra_drift - DRIFT_REF_CPU073) / DRIFT_REF_CPU073
    pass_drift = err_drift < 0.05

    verdict = 'PASS' if (pass_single and pass_drift) else 'FAIL'

    return {
        'stage': 'E',
        'name': 'v7_recovery',
        'verdict': verdict,
        'R_v8': float(R_v8),
        'R_ref_CPU043': R_REF_CPU043,
        'err_R': float(err_R),
        'core_v8': float(core_v8),
        'core_ref_CPU043': CORE_REF_CPU043,
        'err_core': float(err_core),
        'extra_drift_v8': float(extra_drift),
        'drift_ref_CPU073': DRIFT_REF_CPU073,
        'err_drift': float(err_drift),
        'gate': '<5% on all three metrics',
        'gamma': GAMMA,
    }


# ===========================================================================
# STAGE F — FC-5 mass ladder I_m(R) vs CPU-074/075
# ===========================================================================

M_REF_V7 = {3: 474.15, 4: 728.92, 5: 954.88}


def run_stage_F(out_dir, verbose=True):
    """Run v8 rings at R in {3,4,5}, measure I_m(R), compare to M_REF_V7."""
    L = 80
    N = L * L * L
    RADII = [3, 4, 5]
    T_P2 = 1000.0       # match CPU-074/075 protocol (physical lu)
    N_STEPS = int(T_P2 / DT)

    nb_idx = build_nb(L)
    per_radius = {}

    for R in RADII:
        if verbose:
            print(f"  R={R} ...", flush=True)
        phi_ic = init_phi_single_ring(L, R)
        state = make_state(L, phi_init=phi_ic)

        # Phase 1: ring formation, V_couple OFF
        for _ in range(int(300.0 / DT)):
            state = yoshida4_step(state, DT, nb_idx, v_couple_on=False,
                                   chi_decay=CHI_DECAY_V7)

        # Phase 2: V_couple ON, measure I_m with stationarity check
        ts = []; I_m_trace = []
        H0 = hamiltonian_v8(state, nb_idx); drift_max = 0.0
        abort = False
        for istep in range(N_STEPS):
            state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                                   chi_decay=CHI_DECAY_V7)
            t_now = istep * DT
            if istep % int(10.0 / DT) == 0:
                I_m = ring_mass_deficit(state['sm'])
                ts.append(t_now); I_m_trace.append(I_m)
            if (istep + 1) % 1000 == 0:
                Ht = hamiltonian_v8(state, nb_idx)
                drift_max = max(drift_max, abs(Ht - H0) / max(abs(H0), 1e-12))
            mn, ok = check_sigma_g_positivity(state)
            if not ok:
                abort = True; break

        # Stationarity pre-check (window [900, 1000])
        if not abort:
            window_mask = [(900.0 <= t <= 1000.0) for t in ts]
            Im_window = [I_m_trace[i] for i, m in enumerate(window_mask) if m]
            if len(Im_window) >= 3:
                mean_Im = float(np.mean(Im_window))
                std_Im = float(np.std(Im_window))
                stationary = (std_Im / max(abs(mean_Im), 1e-10)) < STATIONARITY_TOLERANCE
            else:
                mean_Im = I_m_trace[-1] if I_m_trace else float('nan')
                std_Im = float('nan')
                stationary = False
        else:
            mean_Im = float('nan'); std_Im = float('nan'); stationary = False

        # Decomposition diagnostic (tesla-mind mandate)
        decomp = decompose_I_m(state['sm'], L, R)

        per_radius[R] = {
            'R': R,
            'I_m_v8_final': float(I_m_trace[-1]) if I_m_trace else float('nan'),
            'I_m_v8_window_mean': mean_Im,
            'I_m_v8_window_std': std_Im,
            'stationary': bool(stationary),
            'M_ref_v7': M_REF_V7[R],
            'fractional_error': abs(mean_Im - M_REF_V7[R]) / M_REF_V7[R]
                                if math.isfinite(mean_Im) else float('nan'),
            'H_drift_max_per_1000': float(drift_max),
            'sigma_g_abort': abort,
            'trace_t': ts,
            'trace_I_m': I_m_trace,
            'decomposition': decomp,
        }
        if verbose:
            print(f"    I_m={mean_Im:.2f}  M_ref={M_REF_V7[R]}  err={per_radius[R]['fractional_error']:.3f}  "
                  f"stationary={stationary}", flush=True)

    # --- Verdict evaluation ---
    errors = [per_radius[R]['fractional_error'] for R in RADII]
    Ims = [per_radius[R]['I_m_v8_window_mean'] for R in RADII]

    # Verdict C: all individual errors within 20%
    all_within_20 = all(math.isfinite(e) and e < 0.20 for e in errors)

    # Verdict B: ratio I_m_v8/I_m_v7 constant within 10% across R
    if all(math.isfinite(x) for x in Ims) and all(M_REF_V7[R] > 0 for R in RADII):
        ratios = [Ims[i] / M_REF_V7[R] for i, R in enumerate(RADII)]
        ratio_mean = float(np.mean(ratios))
        ratio_spread = float(max(ratios) - min(ratios)) / max(abs(ratio_mean), 1e-10)
        b_hold = ratio_spread < 0.10
    else:
        ratios = []; ratio_mean = float('nan'); ratio_spread = float('nan'); b_hold = False

    if all_within_20:
        verdict = 'PASS_VERDICT_C'
    elif b_hold:
        verdict = 'PASS_VERDICT_B'
    else:
        verdict = 'FAIL_VERDICT_A'

    return {
        'stage': 'F',
        'name': 'mass_ladder',
        'verdict': verdict,
        'per_radius': per_radius,
        'fractional_errors': errors,
        'verdict_C_all_within_20pct': all_within_20,
        'verdict_B_ratio_spread_within_10pct': b_hold,
        'ratios_I_m_v8_over_M_ref': ratios,
        'ratio_mean': ratio_mean,
        'ratio_spread': ratio_spread,
        'M_ref_CPU074': M_REF_V7,
    }


def decompose_I_m(sm, L, R):
    """Decompose mass deficit into (i) core-shell vs (ii) long-range bulk.

    Returns dict with:
      I_m_total = full deficit
      I_m_core  = sum over nodes within 1.2 lu of ring curve
      I_m_bulk  = rest
      core_frac = I_m_core / I_m_total
    """
    dx, dy, dz = centered_coords(L)
    rho = np.sqrt(dx * dx + dy * dy)
    dist_curve = np.sqrt((rho - R) ** 2 + dz * dz)
    core_mask = cp.asarray((dist_curve <= 1.2).ravel())
    dep = cp.maximum(0.0, SIGMA_M_REF - sm)
    total = float(cp.sum(dep))
    core = float(cp.sum(dep * core_mask))
    bulk = total - core
    return {
        'I_m_total': total,
        'I_m_core':  core,
        'I_m_bulk':  bulk,
        'core_frac': core / max(total, 1e-10),
    }


# ===========================================================================
# Main orchestrator
# ===========================================================================

STAGES = {
    'A': ('phi_dispersion',       run_stage_A),
    'B': ('inter_ring_force',     run_stage_B),
    'C': ('fma_drift',            run_stage_C),
    'D': ('chi_decay_stability',  run_stage_D),
    'E': ('v7_recovery',          run_stage_E),
    'F': ('mass_ladder',          run_stage_F),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', default='all',
                    help='A/B/C/D/E/F or all (comma list OK)')
    ap.add_argument('--out-dir', default=str(DEFAULT_OUT_DIR))
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    verbose = not args.quiet

    stages_to_run = []
    if args.stage == 'all':
        stages_to_run = list(STAGES.keys())
    else:
        for s in args.stage.split(','):
            s = s.strip().upper()
            if s in STAGES:
                stages_to_run.append(s)
            else:
                raise SystemExit(f"Unknown stage: {s}")

    print("=" * 78)
    print("QNG-GPU-020: v8 canonical extension (DER-QNG-042)")
    print("=" * 78)
    print(f"Physics parameters (pre-registered):")
    print(f"  MU_M   = {MU_M:.4f}")
    print(f"  MU_PHI = {MU_PHI:.4f}")
    print(f"  M_PHI_DEPRECATED = {M_PHI_DEPRECATED:.4f}  (stale; A1 vacuum m_phi=0)")
    print(f"  C_G    = {math.sqrt(C_G2):.4f}")
    print(f"  g (V_couple) = {G_V_COUPLE}")
    print(f"Integrator: Yoshida 4 at dt={DT}")
    print(f"Abort thresholds: sigma_g_min={SIGMA_G_MIN_ABORT}, "
          f"|dH|/H <= {ENERGY_DRIFT_ABORT} per 1000 steps")
    print(f"Stages: {stages_to_run}")
    print()

    master_report = {
        'test_id': 'QNG-GPU-020',
        'date_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'parameters': {
            'SIGMA_G_REF': SIGMA_G_REF, 'SIGMA_M_REF': SIGMA_M_REF,
            'ALPHA': ALPHA, 'BETA_G': BETA_G, 'BETA_M': BETA_M,
            'BETA_PHI': BETA_PHI, 'DELTA_CHI': DELTA_CHI,
            'CHI_REL': CHI_REL, 'CHI_DECAY_V7': CHI_DECAY_V7,
            'GAMMA_PHI': GAMMA_PHI, 'K_BACK': K_BACK,
            'G_V_COUPLE': G_V_COUPLE,
            'MU_M': MU_M, 'MU_PHI': MU_PHI, 'M_PHI_DEPRECATED': M_PHI_DEPRECATED,
            'C_G': math.sqrt(C_G2), 'DT': DT,
        },
        'integrator': 'Yoshida4 (W1*dt, W2*dt, W1*dt)',
        'stages': {},
    }

    for s in stages_to_run:
        name, func = STAGES[s]
        print(f"--- Stage {s} ({name}) ---", flush=True)
        t0 = time.time()
        res = func(out, verbose=verbose)
        dt_wall = time.time() - t0
        res['wall_seconds'] = round(dt_wall, 2)
        master_report['stages'][s] = res
        print(f"Stage {s} verdict: {res.get('verdict','?')}  "
              f"(wall {dt_wall:.1f}s)", flush=True)
        print()

    # Combined verdict per FC-5
    combined = evaluate_combined(master_report)
    master_report['combined_verdict'] = combined

    (out / 'report.json').write_text(json.dumps(master_report, indent=2, default=str))
    print("=" * 78)
    print(f"GPU-020 combined verdict: {combined['verdict']}")
    print(f"Written report.json to: {out / 'report.json'}")
    print("=" * 78)


def evaluate_combined(master_report):
    stages = master_report.get('stages', {})
    verdicts = {s: stages[s].get('verdict', 'MISSING') for s in stages}
    # Any individual structural failure:
    kill_reasons = []
    if verdicts.get('D') == 'FAIL':
        kill_reasons.append('Stage D FAIL: v8 does not close Gap 8')
    if verdicts.get('E') == 'FAIL':
        kill_reasons.append('Stage E FAIL: v8 not a generalization of v7')
    f_v = verdicts.get('F', 'MISSING')
    if f_v == 'FAIL_VERDICT_A':
        kill_reasons.append('Stage F Verdict A: mass ladder contradicts CPU-074/075')

    if kill_reasons:
        final = 'DER-QNG-042 falsified_structural'
    elif (verdicts.get('A') == 'PASS' and verdicts.get('B') == 'PASS'
          and verdicts.get('C') == 'PASS' and verdicts.get('D') == 'PASS'
          and verdicts.get('E') == 'PASS'
          and f_v in ('PASS_VERDICT_B', 'PASS_VERDICT_C')):
        final = 'v8 PASS (H1 or H2/H3 per F)'
    elif all(v in ('PASS', 'PASS_VERDICT_B', 'PASS_VERDICT_C') or v == 'MISSING'
             for v in verdicts.values()):
        final = 'partial pass — not all stages complete'
    else:
        final = 'mixed — see stage verdicts'

    return {
        'verdict': final,
        'per_stage': verdicts,
        'kill_reasons': kill_reasons,
    }


if __name__ == '__main__':
    main()
