# 14. Graviton-Matter Coupling and Newtonian Potential Recovery

How v11 quantum graviton mediates gravitational interaction between
matter sources. Recovery of Newton's law at tree level + leading
quantum corrections.

## Tree-level matter coupling

The interaction Lagrangian (from Section 11):

```
L_int = -(8π·G/c⁴) · ĥ_ij(x) · T̂^TT_ij(x)
```

where T_ij is the spatial stress-energy tensor of matter (σ_m + φ
sectors), and T^TT is its transverse-traceless part.

For static, non-relativistic matter: T_ij ≈ ρ · δ_ij (plus pressure
terms at higher order).

## Tree-level diagram: graviton exchange

For two static masses M₁, M₂ at separation r:

```
M₁ ----[graviton]---- M₂
```

Standard QFT calculation yields Newtonian potential:

```
V(r) = -G·M₁·M₂ / r
```

This is the leading-order graviton-mediated gravitational interaction.

**Recovered from QNG**: ✓ — same formula, with G = β_g/z derived from
substrate.

## Leading quantum correction (Donoghue 1994)

In effective field theory of gravity (Donoghue 1994, Bjerrum-Bohr,
Donoghue, Holstein 2003), one-loop graviton corrections give:

```
V(r) = -(G·M₁·M₂/r) · [1 + (3·G·(M₁+M₂))/(r·c²) + (41·G·ℏ)/(10π·c³·r²) + ...]
```

The three terms:
1. **Newton**: classical
2. **Post-Newtonian**: classical GR correction (1/r²)
3. **Quantum correction**: `41/10π × Gℏ/(c³r²)` — parameter-free QG prediction

## QNG version of Donoghue prediction

In QNG, the one-loop calculation involves graviton loop integral with
lattice propagator (Section 13):

```
G_QNG(k) = ℏ · P^TT_{ij,kl} / (μ_h · k²_lattice)
```

vs continuum:

```
G_continuum(k) = i · P^TT_{ij,kl} / (k² + iε)
```

For loop integrals at relevant momenta (k << 1/a_L for macroscopic r):
- `k²_lattice ≈ k² × (1 - k²·a_L²/12 + ...)`
- Continuum result modified by `O((k·a_L)²)` corrections

Since the loop integrand peaks at `k ~ 1/r`, the correction is
`O((a_L/r)²)`.

For r >> a_L (any macroscopic distance):
```
QNG correction to Donoghue coefficient ≈ (41/10π) × [1 + O((a_L/r)²)]
```

For r = 1 fm = 10⁻¹⁵ m, a_L = 5×10⁻³⁶ m:
```
(a_L/r)² = (5×10⁻³⁶/10⁻¹⁵)² = 25×10⁻⁴² = 2.5×10⁻⁴¹
```

UTTERLY NEGLIGIBLE at any macroscopic scale.

So **at macroscopic distances, QNG reproduces standard Donoghue
quantum gravity prediction exactly**. This is consistent with QNG
being an EFT framework above lattice scale.

## Where QNG differs from continuum EFT

At distances comparable to a_L (Planck scale):
- Lattice corrections become O(1)
- Standard EFT-of-gravity is non-renormalizable at this scale
- QNG provides a UV completion via lattice cutoff

**Specific QNG prediction at sub-Planck distances**:
```
At r ~ a_L (= 0.305 ℓ_Planck):
  Donoghue coefficient gets correction ≈ 1/12 ≈ 8.3%
```

This is a UNIQUE QNG prediction — string theory, LQG, CDT all give
different specific corrections at this scale.

**Currently not testable** — Planck distance is far below any
experimental access.

## Newtonian potential from QNG perspective

Two complementary derivations of Newton's law:

### Method 1: Classical (Section 09)
Screened Poisson equation in static limit with α → 0:
```
∇² Φ = 4π G ρ_m
Φ(r) = -G·M/r
```
Treats gravity as classical field theory.

### Method 2: Quantum (this section)
Graviton exchange at tree level:
```
V(r) = -G·M₁·M₂/r
```
Treats gravity as graviton exchange.

**Both methods give the same answer**: Newton's law.

This is the standard QFT result that classical fields and graviton
exchange agree at tree level. Confirms internal consistency of QNG.

## Higher-order corrections

Post-Newtonian (1PN) corrections in QNG:
```
V(r) = -G·M₁·M₂/r · [1 + (3G(M₁+M₂))/(rc²) + ...]
```

This is GR-standard, recovered by v11 reproducing linearized GR with
non-linear self-coupling at higher orders (assuming Einstein-Hilbert
non-linear structure, which v11 doesn't yet derive — see 12-open-problems).

For practical Solar System tests:
- Mercury perihelion: GR prediction recovered
- Light bending at Sun: GR prediction recovered
- All within 1PN QNG = GR weak-field

## Specific QNG quantum predictions

Beyond Donoghue, QNG offers:

### Prediction 9: Lattice cutoff in Newton's law

For r near a_L (sub-Planck, hypothetical):
```
V_QNG(r) = -G·M₁·M₂/r · [1 + standard Donoghue + O((a_L/r)²)]
```

At r = 10·a_L ≈ 3 ℓ_Planck: correction ~1%.
At r = a_L ≈ 0.3 ℓ_Planck: correction ~10%.
At r << a_L: QNG framework breaks down (below substrate scale).

### Prediction 10: Modification of black hole potential at horizon

For Schwarzschild BH:
```
V_BH(r) = -GM/r  for r > a_L
V_BH(r) = ?       for r < a_L (substrate level)
```

QNG predicts a NATURAL CUTOFF inside Planck-mass BH at substrate scale.
Singularity inside r → 0 may be regularized by lattice cutoff.

This differs from standard GR (singularity at r=0) and from string/LQG
predictions.

### Prediction 11: Hawking radiation modifications

Hawking temperature: T_H = ℏc³/(8πGM·k_B). Reproduced exactly.

But the spectrum of emitted gravitons could deviate at high frequencies
(near Brillouin edge). Specific modification:
```
Spectrum shape: standard thermal × form factor F(k·a_L)
```

Currently not testable. Would distinguish QNG from string-theory BH
spectroscopy.

## Implications for paper

For Paper 1 (ℏ derivation):
- Add brief section on quantum graviton predictions
- Mentions Donoghue connection
- Highlights lattice cutoff as QNG-unique prediction

For Paper 5 (potential future):
- "Quantum gravity at sub-Planck scales: lattice vs continuum"
- Compares QNG predictions with string/LQG/CDT
- Specific differentiating signatures

## Consistency status

| Claim | QNG | Standard physics | Match? |
|---|---|---|---|
| Newton's law | -GM₁M₂/r | -GM₁M₂/r | ✓ |
| 1PN correction | 3G(M₁+M₂)/(rc²) | same | ✓ |
| Quantum 41/10π | 41/10π × [1 + O(a_L²/r²)] | 41/10π | ✓ at macro |
| UV cutoff | π/a_L = 10.3/ℓ_P | none (EFT) | QNG-specific |
| BH horizon physics | regularized at a_L | singular at r=0 | DIFFERENT |

## Status

Tree-level: VERIFIED structurally.
One-loop: SKETCHED, lattice corrections noted as O((a_L/r)²) suppressed
at macroscopic distances.
Strong-field: speculative, requires non-linear v11 work.

## Open questions

- Full one-loop calculation of QNG-modified Donoghue coefficient
- Exact spectrum of high-k corrections beyond k²a²/12
- Black hole interior physics (substrate-scale modifications)
- Connection to Sakharov "induced gravity" approach (similar
  microscopic spirit)

## References

- Donoghue 1994: original EFT of gravity calculation
- Bjerrum-Bohr, Donoghue, Holstein 2003: refined QG corrections
- DER-QNG-072 (v11 design)
- Section 13 (this folder): v11 quantization
