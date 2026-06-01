# NOTE-QNG-015: Tesla U(1) gauge hypothesis falsified in v8

Type: `note`
ID: `NOTE-QNG-015`
Status: `resolved_falsified`
Author: `C.D Gabriel`
Date: `2026-04-20`
Upstream: `DER-QNG-042-A1` (Option E^2), `DER-QNG-044` (Einstein correspondence)

---

## Summary

The tesla-mind hypothesis (`qng-symmetry-hunt-v8.md`) that v8 carries a
continuous U(1)_g gauge symmetry acting on phi with sigma_g/sigma_m
gauge-invariant is **falsified**. The surviving phi symmetry is the
discrete winding group Z, not U(1).

## Structural origin

V_couple in Option E^2:

```
V_couple = (g/2) * (SIGMA_M_REF - sigma_m)^2 * (1 - cos phi)
```

is manifestly NOT invariant under continuous phi -> phi + alpha because
cos(phi + alpha) != cos phi for generic alpha. It IS invariant under
phi -> phi + 2*pi*n for integer n. The theory is in the same universality
class as the sine-Gordon / axion potential V ~ (1 - cos phi): an
explicit U(1) -> Z breaking at the Lagrangian level.

chi is the conjugate momentum of sigma_g via Channel G (K_BACK*chi), not
a gauge connection A_mu. There is no covariant derivative D_mu phi =
del_mu phi - A_mu whose gauge-invariance must be preserved.

## Empirical record

`tests/gpu/qng_v8_tesla_gauge_probe.py` applied four gauge transforms
to an R=4 ring and measured observable drift over 200 lu evolution:

- Case B (constant phase shift phi -> phi + alpha): M_ring drift up to 30%
- Case C (spatial-gradient shift phi -> phi + alpha*x/L): M_ring drift up to 30%
- Cases D, E (chi shift, sigma_m_ref shift): observable shifts confirming
  neither symmetry is gauge

See `07_validation/audits/qng-v8-stability-probe-v1/tesla_gauge_probe.log`
for raw data and DER-QNG-044 Test Tesla (lines 82-118) for the formal
write-up.

## Implications

1. **No Higgs-like mass generation in v8**: mass is not acquired through
   spontaneous breaking of a continuous U(1) by a sigma_m condensate.
   Mass is topological (ring winding Q = 1) and deficit-weighted
   (sigma_m depletion).

2. **Baryon ladder DER-QNG-038 unchanged**: the ladder was identified by
   ring radius R (topological + geometric quantum numbers), never by
   continuous-gauge quantum numbers. Falsification of U(1) does not
   affect the mass predictions.

3. **Goldstone theorem still applies**: phi is massless in vacuum
   (SIGMA_M_REF sm-background) because V_couple gradient vanishes there.
   Inside a ring's sigma_m-depleted region, phi acquires a position-
   dependent pseudo-Goldstone mass m_phi(x) = sqrt(g/(2*mu_phi)) *
   |SIGMA_M_REF - sigma_m(x)|. This is the pseudo-Nambu-Goldstone
   picture, not a Higgs picture.

4. **Lorentz is a separate question**: NOTE-QNG-013 (Lorentz emergent)
   is not affected. The falsification of gauge U(1) does not break the
   matched wave-speeds c_g = c_m = c_phi which is what makes Lorentz
   emergent at the linear level.

5. **No SU(2) or SU(3) tower to build**: the Tesla program proposed
   U(1)_g x SU(2)_m -> SU(3)_color. Since U(1) is already falsified,
   the higher non-abelian extensions on the same structural basis are
   also falsified. If QNG is to reproduce the Standard Model gauge
   content, it must come from a different mechanism (dual lattice,
   emergent gauge fields from topological defects, etc.) — this is
   left as an open problem.

## Status

`resolved_falsified`. No further investigation of continuous-phi gauge
symmetry is warranted in the v8 (Option E^2) theory.

## References

- `04_qng_pure/qng-einstein-correspondence-v1.md` (DER-QNG-044, Test Tesla)
- `04_qng_pure/qng-v8-option-e2-amendment-v1.md` (DER-QNG-042-A1)
- `tests/gpu/qng_v8_tesla_gauge_probe.py`
- `07_validation/audits/qng-v8-stability-probe-v1/tesla_gauge_probe.log`
