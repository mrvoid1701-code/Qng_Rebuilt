"""Shared ring-formation cache for v8 probes.

Motivation:
  Several v8 GPU probes (Shapiro, redshift, Tesla, WEP, ...) all begin by
  forming an R=4 vortex ring via the same Phase-1 + Phase-2 protocol:
      P1 (T_P1 lu, v_couple_on=False) -> phi vortex
      P2 (T_P2 lu, v_couple_on=True ) -> sigma_m ring
  At L=20, P1=300/P2=500 the formation takes ~15 min on GPU.
  At L=28, P1=300/P2=1000 it takes ~30 min.

  Since the formed state is a deterministic function of the v8 constants
  + (L, R, T_P1, T_P2, DT), we cache the final state as an .npz under
  07_validation/audits/qng-v8-stability-probe-v1/ring_cache/ and keyed
  by a SHA1 of all relevant parameters. Any change to a v8 constant
  invalidates the cache automatically (different hash).

Usage:
  from qng_v8_ring_cache import form_ring_cached
  ring_state, nb_idx = form_ring_cached(L=20, R=4, T_P1=300.0, T_P2=500.0)

Cache filenames are human-readable: ring_L{L}_R{R}_P1_{int}_P2_{int}_{hash}.npz
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path

import cupy as cp
import numpy as np

from qng_v8_canonical_gpu import (
    SIGMA_G_REF, SIGMA_M_REF, BETA_PHI, MU_PHI, G_V_COUPLE, K_BACK,
    CHI_DECAY_V7, ALPHA, BETA_G, GAMMA_PHI,
    build_nb, make_state, init_phi_single_ring, yoshida4_step,
    ring_mass_deficit,
)

ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / "07_validation" / "audits" / "qng-v8-stability-probe-v1" / "ring_cache"

_STATE_FIELDS = ('sg', 'sm', 'chi', 'phi', 'pi_m', 'pi_phi')


def _cache_key(L, R, T_P1, T_P2, DT):
    params = (
        ('v8_ring', 1),
        ('L', int(L)), ('R', int(R)),
        ('T_P1', float(T_P1)), ('T_P2', float(T_P2)), ('DT', float(DT)),
        ('SIGMA_G_REF', float(SIGMA_G_REF)),
        ('SIGMA_M_REF', float(SIGMA_M_REF)),
        ('ALPHA', float(ALPHA)), ('BETA_G', float(BETA_G)),
        ('BETA_PHI', float(BETA_PHI)), ('MU_PHI', float(MU_PHI)),
        ('K_BACK', float(K_BACK)), ('G_V_COUPLE', float(G_V_COUPLE)),
        ('CHI_DECAY_V7', float(CHI_DECAY_V7)),
        ('GAMMA_PHI', float(GAMMA_PHI)),
    )
    h = hashlib.sha1(repr(params).encode('utf-8')).hexdigest()[:12]
    return f"ring_L{L}_R{R}_P1_{int(T_P1)}_P2_{int(T_P2)}_{h}"


def form_ring_raw(L, R, T_P1, T_P2, DT, verbose=True):
    """Unconditional ring formation. Returns (state, nb_idx)."""
    nb_idx = build_nb(L)
    phi_ic = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi_ic)
    n1 = int(T_P1 / DT)
    n2 = int(T_P2 / DT)
    t0 = time.time()
    for _ in range(n1):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=False,
                              chi_decay=CHI_DECAY_V7)
    for _ in range(n2):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7)
    wall = time.time() - t0
    if verbose:
        M = float(ring_mass_deficit(state['sm']))
        print(f"  Ring formation done ({n1+n2} steps, {wall:.1f}s) M_ring={M:.2f}")
    return state, nb_idx


def form_ring_cached(L, R, T_P1=300.0, T_P2=500.0, DT=0.025, verbose=True):
    """Load ring state from disk if cache key matches; else form + save."""
    key = _cache_key(L, R, T_P1, T_P2, DT)
    cache_path = CACHE_DIR / f"{key}.npz"
    nb_idx = build_nb(L)
    if cache_path.exists():
        if verbose:
            print(f"  [ring-cache HIT ] {cache_path.name}")
        data = np.load(cache_path)
        state = {fld: cp.asarray(data[fld], dtype=cp.float64)
                 for fld in _STATE_FIELDS}
        if verbose:
            M = float(ring_mass_deficit(state['sm']))
            print(f"  Ring loaded from cache, M_ring={M:.2f}")
        return state, nb_idx

    if verbose:
        print(f"  [ring-cache MISS] forming -> {cache_path.name}")
    state, nb_idx = form_ring_raw(L, R, T_P1=T_P1, T_P2=T_P2, DT=DT,
                                   verbose=verbose)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.savez(cache_path,
             **{fld: cp.asnumpy(state[fld]) for fld in _STATE_FIELDS})
    if verbose:
        size_mb = cache_path.stat().st_size / (1024 * 1024)
        print(f"  Ring cached to {cache_path.name} ({size_mb:.1f} MB)")
    return state, nb_idx
