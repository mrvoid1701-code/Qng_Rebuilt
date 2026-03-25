# GR Primitives

Type: `definition`
ID: `DEF-GR-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

State the minimal GR vocabulary that must exist before any QNG-native object is introduced.

## Primitive objects

The GR layer starts from the following objects:

- spacetime domain `M`
- Lorentzian metric `g_{mu nu}` on `M`
- matter content represented by `T_{mu nu}`
- action principle for gravity and matter

These are primitive at the GR layer. They are not yet explained by any deeper substrate.

## Derived objects

The following are derived from the metric and its derivatives:

- inverse metric `g^{mu nu}`
- Levi-Civita connection `Gamma^rho_{mu nu}`
- Riemann tensor `R^rho_{ sigma mu nu}`
- Ricci tensor `R_{mu nu}`
- scalar curvature `R`
- Einstein tensor `G_{mu nu}`
- geodesic equation

## Operational subsets

The rebuild will distinguish three GR levels from the beginning:

1. `exact GR`
   Uses the full metric and full Einstein equations.
2. `weak-field GR`
   Uses `g_{mu nu} = eta_{mu nu} + h_{mu nu}` with small perturbation.
3. `observational GR proxies`
   Uses Newtonian potential, PPN parameters, Shapiro-like observables, and geodesic approximations.

These must not be conflated.

## Strict exclusions

The following do not belong in `GR pure`:

- graph substrate
- node states
- memory-coupled substrate variables
- native lag parameters
- memory kernels
- emergent metric claims

Those are QNG-layer or bridge-layer objects.

## Immediate dependency rule

Any future file in `GR pure` must say whether it depends on:

- `DEF-GR-001` only
- a later GR derivation
- or an external mathematical convention

No GR file may depend on QNG ontology.
