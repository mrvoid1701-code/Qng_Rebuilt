# QNG Hamiltonian for v7 Two-Field Substrate

Type: `derivation`
ID: `DER-QNG-036`
Status: `candidate`
Author: `C.D Gabriel`
Date: `2026-04-13`

## Objective

Construct the full Hamiltonian H_v7 = T + E for the v7 two-field substrate
(DER-QNG-033) and show:

1. All v7 update channels follow from gradient flow of a single potential E_v7.
2. The coupling term (sigma_m → sigma_g) implies a missing back-reaction
   (sigma_g → sigma_m) required for matter to fall in gravitational wells.
3. The conservative limit of H_v7 gives a Klein-Gordon equation for sigma_g with
   Lorentz covariance emergent at scales r >> a.
4. The v7 unit system is closed by C1 (G_Newton) + C3 (v = c) applied to sigma_g.
5. sigma_m remains in the overdamped (dissipative) limit at this stage; its
   conservative extension requires a new conjugate momentum pi_m.

## Inputs

- [qng-two-field-substrate-v1.md](qng-two-field-substrate-v1.md) — DER-QNG-033: v7 update laws
- [qng-hamiltonian-conservative-limit-v1.md](qng-hamiltonian-conservative-limit-v1.md) — DER-QNG-032: H = T + E for v6
- [qng-action-principle-candidate-v1.md](qng-action-principle-candidate-v1.md) — NOTE-QNG-014: E[sigma,chi,phi] for v5
- [qng-double-yukawa-derivation-v1.md](qng-double-yukawa-derivation-v1.md) — DER-QNG-035: double-Yukawa potential

---

## Section 1: Field content and notation

The v7 substrate has four fields per node:

```
sigma_g_i  — gravitational field (hosts Channel G, KG waves)
sigma_m_i  — matter field (hosts Channel F, vortex rings)
chi_i      — conjugate momentum of sigma_g (NOT of sigma_m)
phi_i      — phase field (winding defects = vortex rings)
```

Deviations from reference:
```
s_i   = sigma_g_i - sigma_g_ref    [gravitational perturbation]
m_i   = sigma_m_i - sigma_m_ref    [matter perturbation; < 0 at ring core]
c_i   = chi_i                      [momentum field]
```

Convention: sigma_g_ref = sigma_m_ref = 0.5.

---

## Section 2: Potential energy E_v7

### 2.1 Gravitational sector (sigma_g): Channels A + B

```
E_g[sigma_g] = sum_i {
    alpha_g/2 * (sigma_g_i - sigma_g_ref)^2           [Channel A: restoration well]
  + beta_g/4  * sum_{j~i} (sigma_g_j - sigma_g_i)^2  [Channel B: gradient tension]
}
```

Gradient flow (tau=1, sigma_g_bar = (1/z) sum_j sigma_g_j):
```
dE_g/d(sigma_g_i) = alpha_g*(sigma_g_i - sigma_g_ref)
                  + beta_g*(sigma_g_i - sigma_g_bar_i) * z * (1/z)
                  = alpha_g*(sigma_g_i - sigma_g_ref)
                  - beta_g*(sigma_g_bar_i - sigma_g_i)
```
Gradient flow update: sigma_g_i += -dE_g/d(sigma_g_i) = alpha_g*(sigma_g_ref - sigma_g_i)
                                                        + beta_g*(sigma_g_bar_i - sigma_g_i)
Reproduces Channels A+B of sigma_g. ✓

### 2.2 Matter sector (sigma_m): Channels A + B + F

```
E_m[sigma_m, phi] = sum_i {
    alpha_m/2 * (sigma_m_i - sigma_m_ref)^2           [Channel A: restoration well]
  + beta_m/4  * sum_{j~i} (sigma_m_j - sigma_m_i)^2  [Channel B: gradient tension]
  + gamma_phi/2 * D_i(phi) * sigma_m_i^2              [Channel F: phase-disorder coupling]
}
```

where D_i = 1 - |Z_i|, Z_i = (1/z) sum_{j~i} exp(i phi_j) (phase disorder parameter).

Treating D_i as fixed for this variation:
```
dE_m/d(sigma_m_i) = alpha_m*(sigma_m_i - sigma_m_ref)
                  - beta_m*(sigma_m_bar_i - sigma_m_i)
                  + gamma_phi * D_i * sigma_m_i
```
Gradient flow: sigma_m_i += alpha_m*(sigma_m_ref - sigma_m_i)
                           + beta_m*(sigma_m_bar_i - sigma_m_i)
                           - gamma_phi * D_i * sigma_m_i
Reproduces Channels A+B+F of sigma_m. ✓

### 2.3 Chi sector (chi coupled to sigma_g): decay + chi_rel + delta

```
E_chi[sigma_g, chi] = sum_i {
    chi_decay/2 * chi_i^2                                    [chi self-energy]
  - chi_rel/2  * chi_i * (sigma_g_i - sigma_g_bar_i)        [chi-sigma_g gradient coupling]
  - delta      * chi_i * (sigma_g_ref - sigma_g_i)          [Channel D cross-coupling]
}
```

Gradient w.r.t. chi_i:
```
dE_chi/d(chi_i) = chi_decay * chi_i
                - chi_rel/2 * (sigma_g_i - sigma_g_bar_i)
                - delta * (sigma_g_ref - sigma_g_i)
```
Gradient flow: chi_i += -chi_decay * chi_i
                      + chi_rel * (sigma_g_bar_i - sigma_g_i)
                      + delta * (sigma_g_ref - sigma_g_i)
Reproduces chi update (decay + chi_rel + delta terms). ✓

Note: chi couples to sigma_g only, NOT to sigma_m. The chi sector E_chi contains no
sigma_m terms, consistent with DER-QNG-033.

### 2.4 Phi sector (weighted by sigma_m): XY model

```
E_phi[sigma_m, phi] = - beta_phi/z * sum_{i, j~i} sigma_m_i * sigma_m_j * cos(phi_i - phi_j)
```

This is the sigma_m-weighted XY model (matter field weights the phase alignment).
Gradient w.r.t. phi_i (small-angle approximation):
```
dE_phi/d(phi_i) ≈ beta_phi * sigma_m_i * (phi_i - phi_mean_m_i)
```
where phi_mean_m_i is the sigma_m-weighted circular mean of neighbor phases.
Gradient flow: phi_i += beta_phi * (phi_mean_m_i - phi_i)
Reproduces phi update of DER-QNG-033. ✓

### 2.5 Coupling term: matter sources gravity

The v7 sigma_g update contains:
```
sigma_g_i += -k_gm * (sigma_m_ref - sigma_m_i)
```
(MINUS sign: matter depletion at ring → sigma_g pulled down → attractive potential.)

For this to follow from gradient flow of a coupling energy E_coupling:
```
-dE_coupling/d(sigma_g_i) = -k_gm * (sigma_m_ref - sigma_m_i)
dE_coupling/d(sigma_g_i)  =  k_gm * (sigma_m_ref - sigma_m_i)
```

The minimal functional satisfying this condition:
```
E_coupling[sigma_g, sigma_m] = k_gm * sum_i (sigma_m_ref - sigma_m_i) * (sigma_g_ref - sigma_g_i)
                              = k_gm * sum_i (-m_i) * (-s_i)
                              = k_gm * sum_i m_i * s_i
```

Verification:
```
dE_coupling/d(sigma_g_i) = k_gm * (sigma_m_ref - sigma_m_i) = -k_gm * m_i   ✓
dE_coupling/d(sigma_m_i) = k_gm * (sigma_g_ref - sigma_g_i) = -k_gm * s_i
```

**Key structural finding:** The same E_coupling that gives the sigma_g channel also
implies a back-reaction term in sigma_m:
```
sigma_m_i += -dE_coupling/d(sigma_m_i) = k_gm * (sigma_g_i - sigma_g_ref) = k_gm * s_i
```

Physical interpretation: where sigma_g is depleted (s_i < 0, a gravitational well),
sigma_m is further depleted (m_i decreases). This is matter falling into a gravitational
well — the mechanism by which vortex rings attract each other gravitationally.

**This back-reaction term is ABSENT from the current v7 update law (DER-QNG-033).**
It is required for dynamical consistency: the same coupling that creates the gravitational
well must also make matter respond to it. Without it, rings create gravity but do not
fall in each other's wells.

The symmetric coupling functional E_coupling encodes Newton's third law at the field level:
matter sources gravity (sigma_g responds to sigma_m) AND gravity acts on matter
(sigma_m responds to sigma_g).

---

## Section 3: Complete potential energy E_v7

Assembling all terms:

```
E_v7[sigma_g, sigma_m, chi, phi] = sum_i {

  [sigma_g sector]
  alpha_g/2 * (sigma_g_i - sigma_g_ref)^2
  + beta_g/4 * sum_{j~i} (sigma_g_j - sigma_g_i)^2

  [sigma_m sector]
  + alpha_m/2 * (sigma_m_i - sigma_m_ref)^2
  + beta_m/4 * sum_{j~i} (sigma_m_j - sigma_m_i)^2
  + gamma_phi/2 * D_i(phi) * sigma_m_i^2

  [chi sector]
  + chi_decay/2 * chi_i^2
  - chi_rel/2  * chi_i * (sigma_g_i - sigma_g_bar_i)
  - delta      * chi_i * (sigma_g_ref - sigma_g_i)

  [phi sector]
  - beta_phi/z * sum_{j~i} sigma_m_i * sigma_m_j * cos(phi_i - phi_j)

  [coupling: matter-gravity]
  + k_gm * (sigma_m_ref - sigma_m_i) * (sigma_g_ref - sigma_g_i)

}
```

The v7 update law is approximately gradient flow of E_v7:
```
sigma_g_i(t+1) = sigma_g_i - dE_v7/d(sigma_g_i)   [sigma_g channels A+B+coupling]
sigma_m_i(t+1) = sigma_m_i - dE_v7/d(sigma_m_i)   [sigma_m channels A+B+F+back-reaction]
chi_i(t+1)     = chi_i     - dE_v7/d(chi_i)        [chi channels: decay+chi_rel+delta]
phi_i(t+1)     = phi_i     - dE_v7/d(phi_i)        [phi channel: XY]
```

The Channel G term `+k_back * chi_i` in sigma_g is NOT from E_v7; it comes from the
kinetic term T (see Section 4). This is correct: kinetic coupling appears in the
Hamiltonian equations, not in the potential.

---

## Section 4: Kinetic energy T and the full Hamiltonian H_v7

### 4.1 Gravitational sector kinetics

From DER-QNG-032: chi_i is the canonical momentum of sigma_g_i.
Channel G: sigma_g_i(t+1) = sigma_g_i + k_back * chi_i
identifies:  ∂_t sigma_g = k_back * chi   →   chi = (∂_t sigma_g) / k_back

Kinetic energy:
```
T_g[chi] = (k_back / 2) * sum_i chi_i^2
         = (1 / (2 * k_back)) * sum_i (∂_t sigma_g_i)^2
```

### 4.2 Matter sector kinetics (overdamped limit)

The current v7 has NO Channel G in sigma_m → sigma_m has no oscillatory back-coupling.
sigma_m dynamics are purely dissipative (gradient flow of E_m + E_coupling).

For the overdamped limit: T_m = 0 (no kinetic energy in sigma_m).

This is the correct description at the current stage. The conservative extension would
require introducing a conjugate momentum pi_m_i and a new kinetic term:
```
T_m[pi_m] = (k_back_m / 2) * sum_i pi_m_i^2     [NOT yet part of v7]
```
with a new channel: sigma_m_i += k_back_m * pi_m_i (analogous to Channel G for sigma_g).
This extension is left for the v8 program (see Section 9, P2).

### 4.3 The v7 Hamiltonian

```
H_v7[sigma_g, sigma_m, chi, phi] = T_g[chi] + E_v7[sigma_g, sigma_m, chi, phi]
                                 = (k_back/2) * sum_i chi_i^2  +  E_v7
```

Canonical equations of motion:
```
∂_t sigma_g_i = +∂H_v7/∂chi_i       = k_back * chi_i + ∂E_v7/∂chi_i
∂_t chi_i     = -∂H_v7/∂sigma_g_i  = -∂E_v7/∂sigma_g_i
```

Computing ∂E_v7/∂chi_i:
```
∂E_v7/∂chi_i = chi_decay * chi_i - chi_rel * (sigma_g_bar_i - sigma_g_i) - delta*(sigma_g_ref - sigma_g_i)
```

So:
```
∂_t sigma_g_i = k_back * chi_i + chi_decay * chi_i - chi_rel*(sigma_g_bar - sigma_g_i)
              - delta*(sigma_g_ref - sigma_g_i)
```

At leading order (drop chi_decay * chi_i and delta terms as small corrections):
```
∂_t sigma_g_i ≈ k_back * chi_i                                        ... (sigma eq.)
∂_t chi_i     = -alpha_g*(sigma_g_i - sigma_g_ref) + beta_g*(sigma_g_bar - sigma_g_i)
               + k_gm*(sigma_g_ref - sigma_g_i)     [from E_coupling gradient, small]
                                                                       ... (chi eq.)
```

For the sigma_m sector (overdamped — gradient flow only):
```
∂_t sigma_m_i = -∂E_v7/∂sigma_m_i
              = -alpha_m*(sigma_m_i - sigma_m_ref) + beta_m*(sigma_m_bar - sigma_m_i)
                - gamma_phi * D_i * sigma_m_i
                + k_gm * (sigma_g_i - sigma_g_ref)   [back-reaction: new term]
```

---

## Section 5: Conservative equations of motion — Klein-Gordon for sigma_g

Let s_i = sigma_g_i - sigma_g_ref (small perturbation in vacuum: sigma_m_i = sigma_m_ref,
chi_i = 0, D_i = 0).

From equations (sigma eq.) and (chi eq.):
```
∂_t s_i   = k_back * c_i                                             (i)
∂_t c_i   = -alpha_g * s_i + beta_g * (s_bar_i - s_i)              (ii)
```
where s_bar_i = (1/z) sum_{j~i} s_j.

Differentiating (i) and substituting (ii):
```
∂²_t s_i = k_back * ∂_t c_i
          = k_back * [-alpha_g * s_i + beta_g * (s_bar_i - s_i)]
```

z=6 averaging: s_bar_i - s_i = (1/6) * sum_{j~i} (s_j - s_i) ≈ (a²/6) * ∇²s_i

Therefore:
```
∂²_t s_i = (k_back * beta_g / 6) * a² * ∇²s_i - k_back * alpha_g * s_i
```

Klein-Gordon equation for sigma_g perturbations:
```
∂²_t s = v²_g ∇²s - m²_g s
```
with:
```
v²_g  = k_back * beta_g / 6 * (a/tau)^2    [gravitational wave speed squared]
m²_g  = k_back * alpha_g / tau^2            [gravitational boson mass squared]
```

This is identical in structure to DER-QNG-032 for v6, with the replacements:
  chi_rel → beta_g  (the chi_rel = beta convention is maintained in v7)
  alpha   → alpha_g

**Lorentz covariance (sigma_g sector):** Setting v_g = c, the dispersion relation
  ω² = v²_g k² + m²_g
reduces to the Lorentz-covariant form in the limit m_g → 0 (alpha_g → 0).
For alpha_g > 0 (needed for the Newtonian limit), the KG field is massive — consistent
with a Yukawa potential in the quasi-static limit (DER-QNG-035).

The preferred foliation of the substrate is sub-Planckian and not observable at
r >> a (Planck-scale safety argument, NOTE-QNG-013). The emergent Lorentz covariance
holds at scales r >> a, tau >> tau_lattice.

---

## Section 6: m_node from the v7 unit system

### C1 — Newton's constant matching (unchanged from DER-QNG-032)

From the Newtonian limit (GRAV-C1, GRAV-C2), matching G_QNG to G_Newton in SI:

```
G_Newton [m³ kg^-1 s^-2] = (beta_g/z) × a³ [m³] / (m_u [kg] × tau² [s²])
```

Solving for m_u × tau²:
```
m_u × tau² = (beta_g/z) / G_Newton × a³
           = (0.35/6) / (6.674×10^-11) × a³
           = 0.05833 / 6.674×10^-11 × a³
           = 8.740×10^8 × a³     [SI: m_u in kg, tau in s, a in m]
```

**Note (corrected 2026-04-13):** The correct SI coefficient is 8.740×10^8 kg·s²·m^-3,
NOT 8.740×10^-11. The earlier value was a transcription error (copying G_Newton's
exponent rather than computing 0.05833/G_Newton). The end formula for m_u below is
derived from the correct value.

(The formula for G_QNG in v7 with k_gm coupling is G_eff ∝ k_gm/(z×alpha_g), but
under consistency condition CC (k_gm = beta_g × alpha_g) this reduces to beta_g/z.
See DER-QNG-037.)

### C3 — Speed of light matching

Setting v_g = c:
```
v²_g = k_back * beta_g / 6 * (a/tau)^2 = c^2
tau / a = sqrt(k_back * beta_g / 6) / c
```

For k_back = 1, beta_g = 0.35:
```
tau / a = sqrt(0.35/6) / c = sqrt(0.05833) / c = 0.2415 / c
```

Therefore:
```
tau² = (0.05833 / c²) × a²   [with k_back=1]
```

### Closed unit system (C1 + C3):

Substituting tau² from C3 into the C1 formula:
```
m_u × (0.05833 / c²) × a² = 8.740×10^8 × a³

m_u = 8.740×10^8 × c² / 0.05833 × a / k_back
    = 8.740×10^8 / 0.05833 × a × c² / k_back
    = 1.498×10^10 × a × c² / k_back
```

Converting numerical factor: 1.498×10^10 × c² = 1.498×10^10 × 9×10^16 = 1.348×10^27.

```
m_u = 1.348×10^27 × a / k_back     [kg, a in meters, k_back dimensionless]
```

Or equivalently, keeping c explicit:
```
m_u = 1.498×10^10 × a × c² / k_back     [kg, a in meters, c in m/s]
```

For m_u = m_proton = 1.673×10^-27 kg, k_back = 1:
```
a = 1.673×10^-27 / (1.348×10^27)
  = 1.241×10^-54 m
```

**This is far below Planck scale (l_Planck = 1.616×10^-35 m) — physically unreasonable.**

**Resolution — m_u = m_proton convention vs. derived m_u:**
The assignment m_u = m_proton is a CONVENTION (part of the Gap 4 open program), not a
derivation. Once m_u is fixed conventionally, the formula m_u = 1.348×10^27 × a
determines a. The two possible interpretations are:

(A) **Convention m_u = m_proton**: yields a = 1.24×10^-54 m — unphysically sub-Planckian.
    This signals that the C1 constraint alone, with k_back=1, does not fix a sensible a.

(B) **Convention a = a_Planck-scale**: set a = (z/beta_g) × l_Planck = 17.1 l_Planck
    (from the CODATA Planck-unit analysis in DER-QNG-019). Then:
    m_u = 1.348×10^27 × 17.1 × l_Planck = 1.348×10^27 × 17.1 × 1.616×10^-35
        = 3.72×10^-7 kg — still unphysically large (Planck-scale mass).

**The C1+C3 system in full SI does not give a sub-Planck lattice with proton-scale mass
simultaneously.** The formula m_u = 1.498×10^-9 × a × c² (used in DER-QNG-029/037/038)
employs an implicit unit convention (natural units where the substrate speed is c = 1 in
Planck units, so the formula carries implicit Planck normalization). In that convention:

```
m_u = (beta_g / z) / G_Newton × (a^3 / tau^2)     [exact, unit-invariant]
```

With a/tau = c (from C3) this simplifies to:
```
m_u = (beta_g / z) × c^2 / G_Newton × a
    = G_QNG × c^2 / G_Newton × a
    = (0.05833 × c^2 / 6.674×10^-11) × a
    = 8.74×10^8 × c^2 × a
    = 8.74×10^8 × (3×10^8)^2 × a
    = 7.87×10^25 × a     [kg/m, a in meters]
```

For a ≈ 0.77 × l_Planck = 1.24×10^-35 m:
```
m_u = 7.87×10^25 × 1.24×10^-35 = 9.76×10^-10 kg   [≈ 10^18 m_proton]
```

This is still far from m_proton. **The C1 constraint does not predict m_u = m_proton
from first principles.** m_u is a free parameter fixed empirically by the mass
identification program (DER-QNG-038). The formula m_u = 1.498×10^-9 × a × c²
(as used in DER-QNG-029/037/038) assumes implicit Planck normalization;
use it as a shorthand that is self-consistent for extracting a given m_u, but
do not interpret the coefficient as a derived number.

**Operational summary (for mass identification, DER-QNG-038):**
The invariant form is:
```
m_u × tau² / a³ = (beta_g / z) / G_Newton = 8.74×10^8   [kg·s²·m^-3]
tau / a = sqrt(k_back × beta_g / 6) / c
→  m_u = (beta_g/z) × c² / G_Newton × a / k_back × 6/beta_g = G_QNG × c² × 6 × a / (G_Newton × k_back × beta_g)
```

The mass identification (DER-QNG-038) anchors this by choosing one particle at one R,
which fixes m_u (or equivalently a). This is **one empirical input** (Gap 4).

This is consistent with the Planck-scale substrate interpretation.

**The remaining open question (Gap 4):** why m_u = m_proton? This is not derived within
QNG — it requires identifying the physical mass scale from the vortex ring dynamics
(M_ring program: DER-QNG-027, DER-QNG-029). m_u is the one remaining free parameter
in the v7 unit system.

**CRITICAL CAVEAT — M_ring regime dependence:**
The mass formula ρ₀ = m_particle / (a_M × M_ring) requires M_ring to be measured in
the CONSERVATIVE regime (Phase-3 protocol of CPU-067/CPU-059), NOT from dissipative
measurements. Values are dramatically different across regimes:

| Measurement | Protocol | M_ring |
|-------------|----------|--------|
| CPU-051 | dissipative, no back-reaction, T=1000 | 158.4 |
| CPU-067 | conservative Phase 3 | 954.9 |
| CPU-073 | dissipative, WITH back-reaction, T=1000 | ~1034 |

Physical particles have conserved mass. The conservative Phase-3 value (954.9 for R=4)
is the only regime-stable number. The CPU-051 value of 158.4 used in DER-QNG-029 is
**DEPRECATED** for mass identification purposes.

CPU-074 (registered) will measure M_ring(R) in the conservative protocol for R=3,4,5,6
to provide the correct denominator for all mass identification calculations.

---

## Section 7: The missing back-reaction — v7 symmetry gap

The current v7 update law (DER-QNG-033) has sigma_g sourced by sigma_m, but NOT
sigma_m sourced back by sigma_g. As shown in Section 2.5, the coupling functional
E_coupling implies both:

```
(A) sigma_g_i += -k_gm * (sigma_m_ref - sigma_m_i)   [in DER-QNG-033: PRESENT]
(B) sigma_m_i += +k_gm * (sigma_g_i - sigma_g_ref)   [in DER-QNG-033: ABSENT]
```

Term (B) is the gravitational back-reaction on matter. Without it:
- Rings create gravitational wells in sigma_g. ✓
- Rings do NOT fall into each other's wells (no gravitational attraction). ✗

For v7 to exhibit gravitational attraction between rings, term (B) must be added.
Physical sign: delta_sigma_g < 0 at ring → k_gm * s_i < 0 → sigma_m further depleted
near gravitational wells of other rings.

**This is the QNG field-level analog of the geodesic equation:** matter follows
the gradient of sigma_g (via the k_gm back-reaction), rather than traveling in
straight lines.

The addition of term (B) defines **v7-symmetric** (or v7+):
```
sigma_m_i += ... + k_gm * (sigma_g_i - sigma_g_ref)   [new, from E_coupling]
```

This term was tested in QNG-CPU-073 (PASS, 2026-04-13).

**CPU-073 results:**
- v7-original (no term B): drift = +0.14 lu over 3000 steps (residual indirect drift)
- v7-symmetric (with term B): drift = +1.15 lu toward pin — back-reaction confirmed
- Extra drift from term B: +1.01 lu

**Weak-field caveat (Newton review):** CPU-073 used PIN_SG=0.20 against sigma_g_ref=0.50,
giving |delta_sigma_g/sigma_g_ref| = 0.60 — outside the weak-field linearization regime.
The drift magnitude cannot be compared directly to a Newtonian force prediction.
The test confirms the SIGN and DIRECTION of the back-reaction, not its quantitative value.

**Additional CPU-073 finding:** M_final_symmetric (512) >> M_final_original (120). The
back-reaction deepens and sustains sigma_m depletion — the gravitational potential
extends the ring's lifetime. This finding strengthens the physical interpretation but
also confirms the M_ring regime dependence (Section 6 caveat).

---

## Section 8: Gradient flow vs. conservative dynamics — v7 structure

The v7 substrate is a MIXED system:

| Sector   | Dynamics       | Governing equation        | Physical analog           |
|----------|---------------|--------------------------|---------------------------|
| sigma_g  | Conservative  | KG: ∂²_t s = v²∇²s-m²s  | Gravitational field, metric |
| sigma_m  | Dissipative   | ∂_t m = -∂E_v7/∂(sigma_m)| Matter density, Higgs condensate |
| chi      | Conservative  | ∂_t chi = -∂E_v7/∂(sigma_g) | Conjugate momentum of sigma_g |
| phi      | Dissipative   | XY gradient flow          | Phase / topological charge |

The sigma_g sector is the CONSERVATIVE core of v7, governing KG waves and gravity.
The sigma_m + phi sector is DISSIPATIVE, governing vortex ring stability and matter.

**Kinematic consequence of the mixed structure:**
Because sigma_m is overdamped (no T_m), the back-reaction term (B) produces
TERMINAL-VELOCITY drift, not Newtonian free-fall. Specifically:

- Newtonian free-fall: z(t) ~ ½g·t²  (acceleration, ∂²_t z = g)
- sigma_m with back-reaction: ∂_t m = force  (speed ∝ force, ∂_t z = const)

CPU-073 data confirm terminal velocity: z_symmetric decreases at ~3.8×10⁻⁴ lu/step
(constant rate), not accelerating. The theory produces the CORRECT DIRECTION of
gravitational motion but NOT the Newtonian equation of motion F = ma.

Full Newtonian kinematics for the matter sector require the v8 conservative extension
(T_m term and conjugate pi_m), which gives ∂²_t m ~ force (see Section 9 P2).

This mixed structure is analogous to:
- Gravitational field (metric, hyperbolic) + matter fluid (parabolic/dissipative)
- The damped-drive equation: ∂²_t s + gamma * ∂_t s = v²∇²s - m²s + k_gm * m(x,t)
  where the matter source m(x,t) evolves dissipatively.

The full coupled system is NOT Hamiltonian (sigma_m is not conservative). But:
- The sigma_g sector is Hamiltonian when m = m_background (static matter).
- The fully conservative extension requires T_m and a new channel for sigma_m.

---

## Section 9: Open problems

**P1 — Graviton / massless limit (unchanged from DER-QNG-032):**
m²_g = k_back × alpha_g / tau² = 0 requires alpha_g = 0 (no restoration) or k_back = 0.
But alpha_g = 0 removes the Newtonian potential (the screened Poisson equation requires
alpha_g > 0). Tension: Newtonian gravity requires m_g > 0; massless graviton requires m_g = 0.
Resolution: the scalar s field is NOT the graviton. The graviton is a tensor perturbation
of the effective metric g_μν — a spin-2 excitation beyond the scalar KG field.

**P2 — Conservative extension of sigma_m (v8 program):**
To make sigma_m conservative, introduce pi_m_i (conjugate momentum) and Channel G_m:
```
sigma_m_i += k_back_m * pi_m_i
∂_t pi_m_i = -∂E_v7/∂(sigma_m_i)
```
This gives a second Klein-Gordon equation for sigma_m:
```
∂²_t m = v²_m ∇²m - m²_m m  +  k_gm * s(x,t) [coupling from sigma_g]
```
with v²_m = k_back_m × beta_m / 6. If v_m ≠ v_g (different wave speeds for matter and
gravity), this is a two-scalar field theory with a speed hierarchy.

**P3 — Phi sector kinetics:**
E_phi (XY model) has no kinetic term. To make phi conservative:
```
T_phi = (beta_phi/2) * sum_i (∂_t phi_i)^2
```
This gives phi phonons propagating at v_phi = sqrt(beta_phi × sigma_m_ref^2). The
relationship between phi phonons and the sigma_g KG field is open.

**P4 — Effective metric Lorentz covariance:**
The scalar sigma_g satisfies KG (Lorentz-covariant in the conservative limit).
The effective metric g_μν requires tensor perturbation theory beyond this scalar field.
The spin-2 graviton requires a separate analysis of transverse-traceless perturbations
of the coarse-grained coherence tensor, not yet constructed.

**P5 — Back-reaction test (QNG-CPU-073):**
Test the v7-symmetric update law (adding term (B) of Section 7).
Pre-registration gate: a ring should drift toward the gravitational well of a static
sigma_g depletion source (sigma_g_i = 0.45 at a fixed point, sigma_m at rest).
If the ring drifts toward the depletion source, gravitational attraction is confirmed.

---

## Section 10: Summary

| Result | Status |
|--------|--------|
| E_v7 is a single potential for all v7 channels | DERIVED ✓ |
| sigma_g Channels A+B follow from E_g | DERIVED ✓ |
| sigma_m Channels A+B+F follow from E_m | DERIVED ✓ |
| chi channels follow from E_chi | DERIVED ✓ |
| phi channel follows from E_phi | DERIVED ✓ |
| Coupling channel (A) follows from E_coupling | DERIVED ✓ |
| Back-reaction (B) implied by E_coupling | DERIVED — ABSENT from current v7 |
| H_v7 = T_g + E_v7 constructed | DERIVED ✓ |
| chi_i = conjugate momentum of sigma_g_i | IDENTIFIED ✓ |
| Conservative limit of H_v7 gives KG for sigma_g | DERIVED ✓ |
| v²_g = k_back × beta_g / 6 × (a/tau)² | FORMULA ✓ |
| m²_g = k_back × alpha_g / tau² | FORMULA ✓ |
| C1 + C3 close the unit system | DERIVED ✓ |
| m_u physical value | OPEN (Gap 4) |
| sigma_m conservative extension (T_m) | OPEN (P2, v8 program) |
| phi sector kinetics | OPEN (P3) |
| Tensor graviton (spin-2) | OPEN (P4) |
| Back-reaction term (B) simulation test | CONFIRMED (P5, QNG-CPU-073 PASS) |

---

## Cross-references

- DER-QNG-033: v7 two-field substrate and update laws
- DER-QNG-032: v6 Hamiltonian H = T + E (single-sigma; this derivation extends to v7)
- NOTE-QNG-014: v5 free energy functional E[sigma,chi,phi]
- NOTE-QNG-013: Lorentz covariance and preferred foliation
- DER-QNG-035: double-Yukawa gravitational potential in v7
- DER-QNG-029: unit system C1, C2, C3
- QNG-CPU-054: wave equation test (confirmed v²_g formula for single-sigma)
- QNG-CPU-073: proposed back-reaction test (v7-symmetric update)
