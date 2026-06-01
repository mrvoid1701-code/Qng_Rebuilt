# 06 — Experiments: turning the story into measurement

Type: `test` (pre-registration sketches)
Status: `proposed — none run yet`
Author: `C.D Gabriel`
Depends on: all of `00`–`05`
Substrate: v8 canonical, symplectic `yoshida4_step` (`tests/gpu/qng_v8_canonical_gpu.py`)

---

## 0. Why pre-register

Every claim in `00`–`05` is gated on a measurement. This page lists six
concrete, simulatable probes on the **existing** lattice substrate — no new
physics required to *run* them, only to interpret them. Each declares its
prediction *before* the run, so the result can falsify cleanly. (When promoted,
each gets a real ID in `07_validation/prereg/` per the repo testing policy.)

Priority order: **E5 and E4 are the make-or-break tests** (light, mass). E1–E3
are foundational sanity checks that should be cheap and pass. E6 is optional.

---

## E1 — Wave-packet propagation: is `E/ω` constant? (page 00, 02)

- **Setup:** launch a Gaussian phase wave-packet in `φ` on a 1-D/3-D lattice;
  evolve symplectically; measure carrier frequency `ω`, group velocity, and
  total energy `E`.
- **Predict:** `E/ω = const` across packets of different `ω` ⟹ `ℏ` is an
  invariant of the substrate (the action quantum carried by a wave). Group
  velocity `dω/dk → c_φ` for the massless branch.
- **Falsifies:** if `E/ω` drifts with `ω`, the `E=ℏω` reading of the wave
  sector is wrong (a known sore point — the ℏ program).
- **Cost:** cheap (minutes).

## E2 — Dispersion isotropy: is the lightcone real? (page 02)

- **Setup:** measure `ω(k)` for the massless `φ` branch along `[100]`, `[110]`,
  `[111]` directions on a cubic lattice.
- **Predict:** identical `c_φ` in all directions ⟹ a genuine round lightcone ⟹
  emergent rotational/Lorentz invariance at the linear level. (Main theory
  already saw isotropy at `L=32³`, GPU-012 v3 — E2 reconfirms in the
  frequency-first framing and quantifies any residual.)
- **Reports:** the LIV parameter `η_LV` = fractional anisotropy of `c_φ`. A
  nonzero, repeatable value is a **prediction**, testable against astrophysics.
- **Cost:** cheap–moderate.

## E3 — Standing-wave spectroscopy: box modes vs intrinsic modes (page 01, 05)

- **Setup:** put the substrate in a finite box; excite broadband; FFT in time
  to get the eigenmode spectrum. Repeat for `L ∈ {16, 20, 24, 32}`.
- **Predict:** modes whose frequency scales as `n/L` are **box modes** (cavity
  artifacts). Modes whose frequency is **fixed** as `L` grows are **intrinsic**
  (real substrate resonances). Separating these is essential before any
  "mass = mode" claim.
- **Watch for:** the suspicious fixed `R=2,3` `T≈167` mode seen in the lab —
  E3 says whether it is intrinsic or a finite-box ghost.
- **Cost:** moderate (multi-`L`).

## E4 ★ — Mass: density vs frequency (page 05, DECISIVE)

- **Setup:** form rings `R = 3, 4, 5, 6` (3-phase protocol); for each measure
  **separately** (a) the volume charge `Σσ_m` and (b) the internal toroidal
  fundamental `ω₁` (FFT of the circulating phase). Run at **≥2 lattice sizes**
  (e.g. `L=20` and `L=28`) to defeat the Gap-14 finite-size coincidence.
- **Predict / decide among:**
  - `m ∝ Σσ_m` → mass is volume charge (`R^a`),
  - `m ∝ ω₁` → mass is pure resonance (`1/R`),
  - **`m ∝ Σσ_m · ω₁`** → mass = density × frequency (`R^{a-1}`).
  Test each against the PDG baryon ratios `938 / 1232 / 1520`.
- **Gates:** the page-05 claim *"mass is a resonance."* Resolves the
  `1/R`-vs-`R^a` contradiction. **Do not claim mass-as-resonance until E4.**
- **Cost:** moderate–high (ring formation × radii × 2 sizes). Highest value.

## E5 ★★ — The honest photon: does the transverse edge mode propagate? (page 03, MAKE-OR-BREAK)

- **Setup:**
  1. Build the edge field `θ_ij = φ_i − φ_j` on a 3-D lattice.
  2. **Helmholtz-decompose** `θ⃗` into longitudinal (`∇α`) and transverse
     (`∇×Λ⃗`, `∇·θ⃗=0`) parts.
  3. Initialize a **purely transverse** configuration (zero longitudinal
     content) as initial condition.
  4. Evolve under `yoshida4_step`; track transverse energy, its dispersion, and
     polarization content.
- **Predict (if QNG has an honest photon):** the transverse branch
  **propagates** at `c_φ`, carries **2 independent polarizations**, and does
  **not** immediately decay into the longitudinal (sound) sector.
- **Falsifies:** if the transverse sector is **frozen / non-dynamical / pure
  gauge** (no restoring force, energy leaks instantly to longitudinal), then
  `φ` alone gives only sound — light needs Route B (φ–χ circulation) or a new
  field.
- **Gates:** *every* use of the words "light is derived" / "QNG has a photon."
  **Nothing in this folder may claim a derived photon until E5 passes.**
- **Cost:** moderate; the decomposition is the only new tooling needed.

## E6 — Two-slit phase interference (optional, page 04)

- **Setup:** drive `φ` coherently through two apertures in a barrier; measure
  the downstream `C_eff` (coherence) pattern.
- **Predict:** an interference fringe pattern in `C_eff` ⟹ the substrate
  supports genuine wave superposition (the QM face of the bridge made visual).
- **Cost:** cheap–moderate. Mostly a demonstration / sanity check.

---

## Summary table

| Probe | Tests | Gates the claim | Priority | Cost |
|---|---|---|---|---|
| E1 | `E/ω = ℏ` invariant | `E = ℏω` for waves | high | cheap |
| E2 | dispersion isotropy | real lightcone / `η_LV` | high | cheap |
| E3 | box vs intrinsic modes | "mass = mode" prerequisite | high | moderate |
| **E4 ★** | `Σσ_m` vs `ω₁` vs product | **mass as resonance** | **top** | moderate-high |
| **E5 ★★** | transverse `θ_ij` propagation | **light / photon exists** | **top** | moderate |
| E6 | two-slit `C_eff` fringes | wave superposition (demo) | low | cheap |

## Honesty contract for the whole thread

1. **E5 gates light.** No "derived photon" language until it passes.
2. **E4 gates mass-as-resonance.** No `m = ℏω₀/c²` as established until it
   selects (or refutes) the product law — at ≥2 lattice sizes.
3. **The impedance/Lorentz framing (page 02)** stays a *reframe*; `why` the
   impedances match is Gap 5, untouched.
4. **"Frequency is the sole primitive" (page 00)** stays a conjecture pending an
   adiabatic theorem; the defensible claim is *"phase organizes the
   amplitudes."*

When any probe is run, record it under `07_validation/audits/` and update this
file's Status line from `proposed` to the verdict.
