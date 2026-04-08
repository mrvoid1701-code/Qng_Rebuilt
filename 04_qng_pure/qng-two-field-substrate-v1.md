# QNG Two-Field Substrate (v7)

Type: `derivation`
ID: `DER-QNG-033`
Status: `candidate`
Author: `C.D Gabriel`
Date: `2026-04-07`

## Motivation

The single-sigma substrate cannot simultaneously satisfy:
  (a) KG wave equation — requires Channel G: sigma += k_back × chi
  (b) Stable vortex rings — requires Channel F: sigma -= gamma_phi × D_i × sigma
      AND absence of Channel G (stability threshold k_back < 0.0015)

CPU-059 confirmed: the v5 ring is NOT a soliton of H. Gap 7 is structural.

The natural resolution (Path D, NOTE-QNG-017): introduce two sigma-like fields,
one for each sector, coupled by a gravitational source term.

---

## Field content (v7 substrate)

Each node carries five fields instead of three:

  (sigma_g_i, sigma_m_i, chi_i, phi_i)  [chi is conjugate to sigma_g]

**sigma_g** — gravitational field
  - Reference value: sigma_g_ref = 0.5
  - Supports: KG wave propagation, Newtonian potential, Channel G
  - Analogy: metric perturbation, graviton field, ether substrate

**sigma_m** — matter field
  - Reference value: sigma_m_ref = 0.5
  - Supports: phi vortex ring stability, Channel F, matter condensate
  - Analogy: Higgs condensate, matter density

**chi** — canonical momentum of sigma_g
  - Conjugate to sigma_g (not to sigma_m)
  - Drives KG wave equation in sigma_g sector

**phi** — phase field
  - Winding defects (W=±1) in phi define vortex rings
  - Update weighted by sigma_m (matter field, not gravitational field)

---

## Update laws

### sigma_g (gravitational sector, v6 channels: A + B + G + coupling)

  sigma_g_i += alpha_g × (sigma_g_ref - sigma_g_i)        [Channel A: restoration]
             + beta_g × (sigma_g_bar - sigma_g_i)          [Channel B: diffusion]
             + k_back × chi_i                              [Channel G: KG wave]
             - k_gm × (sigma_m_ref - sigma_m_i)           [coupling: matter sources gravity — MINUS sign gives attractive potential]

  NO Channel F in sigma_g.

### sigma_m (matter sector, v5 channels: A + B + F)

  sigma_m_i += alpha_m × (sigma_m_ref - sigma_m_i)        [Channel A: restoration]
             + beta_m × (sigma_m_bar - sigma_m_i)          [Channel B: diffusion]
             - gamma_phi × D_i × sigma_m_i                 [Channel F: ring depletion]

  NO Channel G in sigma_m.

### chi (conjugate to sigma_g)

  chi_i += -chi_decay × chi_i                             [damping]
         + chi_rel × (sigma_g_bar - sigma_g_i)            [Laplacian coupling]
         + delta × (sigma_g_ref - sigma_g_i)              [cross-coupling]

  Note: chi couples to sigma_g only, not to sigma_m.

### phi (weighted by sigma_m)

  phi_i += BETA_PHI × angle_diff(phi_mean_m_i, phi_i)

  where phi_mean_m_i is the sigma_m-weighted circular mean of neighbor phases.
  (Matter field weights the phi alignment, not the gravitational field.)

---

## Coupling term: matter sources gravity

The term k_gm × (sigma_m_ref - sigma_m_i) in the sigma_g update is the
gravitational source:
- At the ring core: sigma_m_i < sigma_m_ref (matter depleted) → (sigma_m_ref - sigma_m) > 0 → subtract → sigma_g pulled DOWN ✓
- In vacuum: sigma_m_i = sigma_m_ref → source = 0 → no gravitational effect

Sign convention: the MINUS sign ensures that matter depletion (positive rho) sources a negative
gravitational potential (attractive), consistent with GRAV-C1 (Φ ∝ delta_sigma_g < 0 for matter).

This is the QNG analog of the stress-energy tensor sourcing the metric:
  -∇²delta_sigma_g ~ k_gm × (sigma_m_ref - sigma_m)
                   ~ k_gm × rho_matter   (rho > 0 → delta_sigma_g < 0 → Φ < 0, attractive)

For k_gm << alpha_g: the gravitational backreaction is weak (consistent with
the hierarchy G_Newton << other forces).

---

## Newtonian limit (revised for two-field)

In the two-field substrate, the screened Poisson equation becomes:

  (alpha_g + beta_g × z) × delta_sigma_g = k_gm × delta_sigma_m + ...

where delta_sigma = sigma - sigma_ref.

The gravitational potential Phi ∝ delta_sigma_g (from GRAV-C1, unchanged).
The source is now delta_sigma_m (matter field depletion) rather than delta_sigma.

This preserves the Newtonian limit structure:
  G_QNG = beta_g / z   [same formula, now with beta_g]
  lambda_screen = sqrt(beta_g / (z × alpha_g))   [same formula]

The physical mass of the ring is m_ring = k_gm × integral(delta_sigma_m) × (unit conversion).
This provides a NEW formula for m_u: it enters through k_gm, not directly.

---

## Comparison to v5/v6

| Channel | v5/v6 (single sigma) | v7 (two-field) |
|---------|---------------------|----------------|
| A (restoration) | sigma → sigma_ref | sigma_g → sigma_g_ref AND sigma_m → sigma_m_ref |
| B (diffusion) | sigma Laplacian | sigma_g Laplacian AND sigma_m Laplacian |
| D (chi cross) | sigma → chi coupling | sigma_g → chi coupling only |
| F (phi depletion) | sigma -= gamma_phi×D×sigma | sigma_m -= gamma_phi×D×sigma_m ONLY |
| G (back-reaction) | sigma += k_back×chi | sigma_g += k_back×chi ONLY |
| coupling (new) | — | sigma_g -= k_gm × (sigma_m_ref - sigma_m) |

---

## New free parameters

| Parameter | Role | Constraint |
|-----------|------|-----------|
| alpha_g | sigma_g restoration | same as alpha (initially) |
| alpha_m | sigma_m restoration | same as alpha (initially) |
| beta_g  | sigma_g diffusion | sets G_QNG and lambda_screen |
| beta_m  | sigma_m diffusion | controls ring structure |
| k_gm    | matter-gravity coupling | << alpha_g (weak gravity) |

For the first tests: alpha_g = alpha_m = alpha, beta_g = beta_m = beta.
Only k_gm is a new parameter to explore.

---

## Key prediction

If Path D is correct:
1. sigma_m ring survives Phase 2 with k_back > 0 (Channel G only in sigma_g)
2. sigma_g shows perturbation at ring location (k_gm coupling)
3. KG wave propagates in sigma_g sector (same as CPU-054)
4. The three sectors are decoupled at leading order

This is the first QNG architecture that can simultaneously support:
  (a) propagating matter waves (sigma_g + chi, KG)
  (b) stable topological particles (sigma_m + phi, rings)
  (c) Newtonian gravity (sigma_g, screened Poisson)

---

## Cross-references

- NOTE-QNG-017: Gap 7 identification and resolution paths
- DER-QNG-026: Channel F (v5) — applies unchanged to sigma_m
- DER-QNG-028/030: KG wave equation — applies unchanged to sigma_g
- DER-QNG-032: H = T + E — T = k_back/2 × Σchi² (chi conjugate to sigma_g)
- QNG-CPU-059: v5 ring NOT a H-soliton — motivates this derivation
- QNG-CPU-060: first test of two-field substrate (PENDING)
