# History and Pointer to Original Folder

## Why this folder exists

`theory-v2/` is a CLEAN reconstruction of QNG theory using only content
that survived all audits and falsifications during development.

The development happened in `QNG-Theory Release-01/` (parent folder).
That folder contains the FULL HISTORY:
- 100+ test scripts (CPU + GPU)
- Multiple version iterations (v3 → v10 → v11 → v12)
- Audit logs
- Retracted derivations
- Failed hypotheses
- Multiple gap discussions

## What's preserved here vs original

| Content | theory-v2/ | original folder |
|---|---|---|
| Locked derivations | YES (clean) | YES + retracted ones |
| Stability Principle | YES | YES (multiple versions) |
| 8 predictions | YES (consolidated) | YES (in DER-QNG-083) |
| GR static-source 6/6 | YES (consolidated) | YES (in DER-QNG-068) |
| v11, v12 extensions | YES (concise) | YES (full discussion) |
| Open problems | YES (12 file) | YES (GAP_INVENTORY.md) |
| Failed hypotheses | NO | YES (full audit trail) |
| Retraction discussions | NO | YES |
| Test scripts | minimal verification | 100+ full tests |

## Major retractions (in original folder)

These are documented in `QNG-Theory Release-01/` but excluded from
`theory-v2/`:

### DER-QNG-038 baryon ladder
- Original claim: R=4→N(938), R=5→Δ(1232), R=6→N*(1520), R=7→Δ(1700)
  with single calibration `a_M = 1.373×10⁻³`
- Retracted via Gap 13 (22-order calibration tension) + Gap 14
  (lattice-size dependence)
- Documented in: `04_qng_pure/qng-gap13-scale-tension-v1.md` (DER-QNG-074)
  and `qng-gap14-mring-lattice-dependence-v1.md` (DER-QNG-075)

### DER-QNG-079 breakthrough on Gap 13
- Original claim: α(L) ~ α_substrate × (a_L/L)² with p=2 dimensional
- Initial appearance: factor-15 match across 125 orders of magnitude
- Retracted via CPU-141 (classical α is L-independent, CV<1%)
- Documented in: `04_qng_pure/qng-gap13-A1-step1-result-v1.md` (DER-QNG-080)

### chi-as-DM hypothesis (DM Phase 1)
- Original claim: chi field generates rotation curve excess
- Retracted via CPU-132 (λ_chi ~ 10⁻³⁶ m, sub-Planck)
- Plus CPU-049 reinterpretation under v12 (chirality = Coulomb force)

### Tesla U(1) gauge interpretation
- Original claim: chi field = U(1) gauge connection (Tesla-style)
- Retracted in DER-QNG-044: v8 has only Z winding (sine-Gordon vacuum)

### Trajectory lag (DER-TRJ-001)
- Original phenomenological proxy for solar-system anomalies
- Retracted via CPU-128 (Pioneer requires 10⁻¹⁰ m/s², QNG gives 10⁻³³)
- Plus underlying chi-as-memory interpretation FALSIFIED

## How to use original folder

For HISTORY of how findings evolved:
- Read `QNG-Theory Release-01/THEORY_STATE.md` for chronological status
- Read `QNG-Theory Release-01/GAP_INVENTORY.md` for gap status
- Read `QNG-Theory Release-01/04_qng_pure/qng-*-v1.md` for derivations

For ACTUAL TESTS:
- Run `QNG-Theory Release-01/tests/cpu/qng_cpu107_hbar_unique_check.py`
- Run `QNG-Theory Release-01/tests/cpu/qng_cpu108_hbar_L_scan.py`
- (Many more tests for all derivations)

For CURRENT (clean) THEORY:
- Read `theory-v2/` files in order 00 → 12
- Single-script verification: `theory-v2/tests/verify_constants.py`

## Major test logs preserved

| Test ID | Topic | Status |
|---|---|---|
| CPU-107 | ℏ unique-check (triple-method) | PASS |
| CPU-108 | ℏ L-scan thermodynamic limit | PASS |
| CPU-113 | β/μ robustness | PASS |
| CPU-114 | SI unit-bridge | PASS (machine prec) |
| CPU-117/c | WEP + Pound-Rebka v10 | PASS |
| CPU-119 | Schwarzschild analog | PASS |
| CPU-120 | Hawking T_H | PASS (consistency) |
| CPU-127 | Galaxy rotation honest scope | PASS-honest |
| CPU-129 | Planck TT acoustic peaks | PASS |
| CPU-131 | eBOSS BAO | FAIL Paper 4 |
| CPU-132 | chi-DM | FALSIFIED |
| CPU-138 | v12 charge + Coulomb | retroactive validation |
| CPU-141 | α L-scan | DER-QNG-079 falsified |
| CPU-142 | σ_g defects | RULED OUT structurally |
| CPU-143 | hopfion charge v12 | DM no-go |
| CPU-144 | predictions extraction | 8 predictions documented |

## Why theory-v2 matters

The original folder preserves the FULL JOURNEY including dead ends. This
is scientifically valuable (auditable) but cognitively heavy.

`theory-v2/` provides the FINAL STATE in clean form for:
- Reading the theory without confusion
- Building on it cleanly
- Submitting papers
- Future research

Both folders have value:
- `theory-v2/`: forward-looking, clean foundation
- `QNG-Theory Release-01/`: archival, full audit trail

## Date

`theory-v2/` initialized: 2026-04-26
After autonomous block that:
- Falsified DER-QNG-079 (Gap 13 breakthrough)
- Established DM no-go (DER-QNG-082)
- Extracted 8 predictions (DER-QNG-083)
- Updated all relevant memory + inventory documents

## Future updates

When new findings emerge:
- LOCKED results → add to theory-v2/
- Failed hypotheses → keep in original folder, NOT in theory-v2
- Retractions → update theory-v2 file + add to HISTORY here

This keeps theory-v2 always representing current best-knowledge clean
state.
