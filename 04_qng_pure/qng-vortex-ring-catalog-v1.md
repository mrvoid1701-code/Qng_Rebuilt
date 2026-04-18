# QNG Vortex Ring Catalog

type: note
id: NOTE-QNG-015
author: C.D Gabriel
date: 2026-04-15
status: living-document

---

Catalog complet al proprietatilor inelului de vortex QNG.
Actualizat dupa fiecare test nou. Fiecare sectiune marcheaza:
  [CONFIRMED] = verificat numeric
  [EMPIRIC]   = observat dar nededus din principii
  [OPEN]      = necunoscut / in lucru
  [BLOCKED]   = blocat de alta problema deschisa

---

## 1. Ce este inelul

**Definitie**:
Un inel de vortex QNG este o configuratie topologica stabila in substratul v7
(sigma_m, sigma_g, chi, phi) caracterizata prin:

- Depletion toroidal in sigma_m: sigma_m < SIGMA_REF intr-o regiune toroidala
- Winding de faza phi = Q = +1 sau -1 in jurul miezului torusului
- Miez al torusului la raza R (masurata in unitati de lattice, intreg)
- Raza tubului ~ 2-3 lu (independenta de R in conditiile actuale)

**Parametri de formare** [CONFIRMED, CPU-042/043/074]:
  ALPHA = 0.005, BETA = 0.35, GAMMA_PHI = 0.10, BETA_PHI = 0.02
  CHI_DECAY = 0.020, K_BACK = 0.10, K_GM = 0.010

**Protocol standard** [CONFIRMED, CPU-073/074/075]:
  Phase 1: 300 pasi (fara Channel F/G) -- phi vortex se formeaza
  Phase 2: 1500 pasi (Channel F activ) -- inelul se formeaza
  Phase 3: 1000 pasi (conservative, fara A/F) -- masurare masa

---

## 2. Identitate si Topologie

**Winding number Q** [CONFIRMED]:
  Q = +1 (particula) sau Q = -1 (antiparticula)
  phi = +arctan2(dz, rho-R)  =>  Q = +1
  phi = -arctan2(dz, rho-R)  =>  Q = -1
  Toate inelele stabile observate au |Q| = 1.

**Chiralitate** [CONFIRMED, CPU-049]:
  W+ si W- = doua chiralitati distincte ale aceluiasi inel
  W+W+ => repulsie (forte la distanta mica)
  W+W- => atractie (forte la distanta mica)
  Legatura cu Q: [OPEN] -- nu stim exact daca chiralitate = semn Q sau altceva

**Raza discreta R** [CONFIRMED]:
  R = 3, 4, 5, 6, 7 testate
  R < 3: inelul nu se formeaza (instabil la dimensiuni mici)
  R > 7: [OPEN] -- netestate sistematic

**Q = 0 (fara winding)** [CONFIRMED, GPU-004]:
  Structuri cu depletion sigma_m dar phi=0 NU supravietuiesc.
  Channel F nu actioneaza fara disorder (disorder=0 cand phi=0).
  => Nu exista inel stabil fara topologie phi.

  GPU-004 (3 configuratii, L=60, PHASE2=3000):
  | Config      | M0    | retained@T=1500 | verdict  |
  |-------------|-------|-----------------|----------|
  | blob_Q0     | 180.9 | 0.0%            | UNSTABLE |
  | ring_Q0     | 156.3 | 0.0%            | UNSTABLE |
  | ring_Q1 (ctrl) | 156.3 | 143.5%      | GROWING  |

  Q=0 se dizolva complet in <500 pasi. Q=1 creste (Channel F activ).
  Discriminatorul este topologia phi, nu geometria depletionului.
  => DARK MATTER in QNG necesita un mecanism complet diferit.

---

## 3. Masa

### 3.1 Identificarea barionica [EMPIRIC, DER-QNG-038]

Cu a_M = 1.373e-3 (calibrat pe proton la L=20):

| R | M_ring (L=20) | Particula SM | Masa SM (MeV) | Eroare |
|---|--------------|-------------|--------------|--------|
| 3 | ~611 | NEIDENTIFICAT | -- | -- |
| 4 | 728.92 | N(938) proton | 938.3 | 0% (fix) |
| 5 | 954.88 | Delta(1232) | 1232 | ~0.3% |
| 6 | ~1182 | N*(1520) | 1520 | <0.1% |
| 7 | ~1320 | Delta(1700) | 1700 | ~0.4% |

### 3.2 Dependenta de L -- REZOLVATA: phi este fara masa [CONFIRMED, GPU-009..013]

**Problema**: M_ring (global = N*sigma_ref - sum(sigma_m)) creste cu L ca L^1.6.

| L | M(R=4) | M(R=5) | ratio |
|---|--------|--------|-------|
| 20 | 509 | 810 | 1.589 |
| 30 | 967 | 1301 | 1.345 |
| 40 | 1503 | 1861 | 1.238 |
| 60 | 2851 | 3250 | 1.140 |
| 80 | 4593 | 5029 | 1.095 |

**Diagnosticul complet (GPU-012/013, Einstein-mind)**:

Phi este un camp Goldstone FARA MASA (massless). Inelul de vortex intr-un camp
fara masa are o "halo" de energie divergenta: M_ring = core (finit) + halo (divergent ~L^1.6).

Profilul de dezordine (GPU-012, L=80, R=5):
  dis(r) ~ r^(-2.37)  [power law, NU exponential]
  Fit: R2_pow=0.9993 > R2_exp=0.9861

Scanul GAMMA_PHI (GPU-013, GAMMA in {0.03, 0.05, 0.10, 0.20}):
  xi = 6.00 lu CONSTANT (slope log(xi)/log(gamma) = 0.000)
  => Channel F NU genereaza masa pentru phi
  => xi e setat de geometria inelului (R=5), nu de parametri de disipatie

**Testul V(phi) = 1-cos(phi) (GPU-014, MU_PHI in {0.0001..0.003})**:
  TOATE esueaza. Ratio-ul deriva chiar si cu dis_bulk=0 (phi confinat complet).
  Cauza: sigma_m difuzeaza cu BETA=0.35 => depletion din core se extinde in bulk.
  La L->inf: ratio -> 5/4 = 1.25 (perimetrul geometric R=5/R=4), NU SM=1.313.

**Concluzia finala [CONFIRMED, GPU-009..014]**:
  Acordul 0.24% la L=20 este o COINCIDENTA de marime finita.
  Ratio M(R5)/M(R4) e controlat de VOLUMUL GEOMETRIC al torului (proportional cu R),
  nu de dinamica particulelor.
  Nu exista parametru in substratul actual care sa fixeze ratio-ul la SM independent de L.
  a_M = 1.373e-3 este o conventie la L=20, nu o constanta fundamentala.

**Ce lipseste pentru predictie reala**:
  Un mecanism care face M(R) proportional cu masa barionului, nu cu R geometric.
  Candidat: masurare din energia hamiltoniana H_v7 (nu din depletion totala),
  sau substrat v9 cu dinamica complet diferita pentru sigma_m.

### 3.3 Simetrie particula-antiparticula [CONFIRMED, GPU-005]

  M(Q=+1, R=4) = M(Q=-1, R=4) = 1503.01 (L=40)
  Diferenta: 0.000% -- simetrie exacta la precizie de masina.
  Confirma CPT-like in QNG: masa antiparticulei = masa particulei.

### 3.4 Conservarea masei [CONFIRMED, CPU-074/075]

  In Phase 3 (conservative, fara Channel A sau F):
  M_ring = N*sigma_ref - sum(sigma_m) = constant exact.
  Laplacianul sumeaza la zero pe lattice periodic => conservare exacta.

---

## 4. Stabilitate

**Fara Channel H** [CONFIRMED, CPU-051, GPU-003]:
  Inelul se dizolva. Channel F erodeaza sigma_m la granita inelului
  la viteza constanta proportionala cu GAMMA_PHI.
  Mecanism: phi difuzeaza in afara miezului => disorder creste in bulk =>
  Channel F actioneaza pe regiune tot mai mare.

**Cu Channel H** [CONFIRMED, GPU-001/v8]:
  bp_eff(i) = BETA_PHI_MIN + BETA_PHI_RING * depletion(i)
  phi difuzeaza RAPID in miez (unde e depletion) si INCET in bulk.
  Winding-ul ramane localizat => granita ramane ascutita => eroziunea -> 0.
  Rezultat: inel metastabil (PLATEAU -> STABLE in teste lungi).

**Stabilitate la perturbatii** [CONFIRMED, CPU-039]:
  Lattice cubic perturbat (perturbatie 0.3) => inel supravietuieste.
  Simetria D2 (second-moment condition) suficienta pentru izotropie.

**Constrangere v7** [CONFIRMED, DER-QNG-034]:
  K_BACK * DELTA < ALPHA + CHI_DECAY * (1-ALPHA)
  Cu K_BACK=0.10, DELTA=0.20, ALPHA=0.005: CHI_DECAY >= 0.016.
  Valoare folosita: CHI_DECAY = 0.020 (marja de siguranta).
  Nerespectare => instabilitate Jeans globala (colaps sigma_g la T>2000).

---

## 5. Autodinamica (Miscare proprie)

**Viteza Biot-Savart** [FAIL, CPU-045]:
  Predictia clasica: v ~ log(R/a) / R (vortex inel in superfluid).
  Rezultat QNG: phi difuzeaza si creeaza drift dominant. Regim overdamped.
  Inelul NU se misca cu viteza Biot-Savart in v7.
  Cauza: sigma_m este overdamped (gradient flow, fara termen cinetic T_m).

**Viteza terminala in potential gravitational** [CONFIRMED, CPU-073]:
  In prezenta putului sigma_g, inelul deriva cu viteza terminala constanta
  (nu accelereaza = nu este cadere libera).
  extra_drift = 1.01 lu (masurat direct).
  Cauza: sigma_m overdamped => F = -grad(E_v7) echilibrat instant de disipatie.
  => Necesita v8 cu pi_m (momentum conjugat sigma_m) pentru F=ma real.

**Precesia inelului** [OPEN]:
  Un inel perturbat precesioneaza? Nu testat.
  Ar putea codifica spin-ul (J) prin raspuns giroscopic.

---

## 6. Interactii intre inele

**Forta chiralitate-sensitiva** [CONFIRMED, CPU-049]:
  W+W+: respingere la distanta mica
  W+W-: atractie la distanta mica
  Mecanismul: interferenta constructiva/destructiva a campurilor phi.

**Potential Lennard-Jones** [CONFIRMED, CPU-050]:
  Potentialul W+W- nu este monoton -- are un echilibru la d ~ 3*lambda.
  Structura: repulsie la d < d_eq, atractie la d > d_eq.
  => Pot exista STARI LEGATE de doua inele (analog deuteron).
  Stare legata testata: [OPEN]

**Tranzitia inel-la-inel** [FAIL, GPU-001/002]:
  R=5 + R=4 in acelasi box: ambele se dizolva (NO_TRANSITION).
  Cauza: interferenta phi distruge ambele inele.
  Alternativa necesara: inele separate cu distanta mare, phi izolat.

**Schimb sigma_g** [PARTIAL, CPU-073]:
  Doua inele in prezenta sigma_g se atrag (both fall into each other's well).
  Masurat: extra_drift = 1.01 lu spre putat gravitational al celuilalt inel.

---

## 7. Dezintegrare si Emisie

**Emisie in v7** [NO_EMISSION, GPU-003]:
  Inel R=5 singur, v7 fara Channel H.
  Dizolvare in ~1500 pasi. Nicio perturbare in coajele externe.
  sigma_g: semnal uniform (background chi), fara propagare.
  Concluzie: dezintegrarea in v7 este pur disipativa. Nicio emisie de unda.

**De ce nu exista emisie** [CONFIRMED, analitic]:
  sigma_m: overdamped (gradient flow) => difuzeaza, nu propaga.
  phi: difuzie pur disipativa (BETA_PHI fara termen cinetic) => nu propaga.
  sigma_g: are dinamica KG (v_s ~ 0.076 lu/step, confirmat CPU-054).
  Dar sigma_g nu este perturbat semnificativ de dizolvarea inelului in v7.

**Mezonul QNG** [OPEN]:
  Analogul pionului (emis in Delta -> N + pi) nu exista in v7.
  Necesar: v8 cu termen cinetic pentru phi (T_phi = pi_phi^2/2).
  Phi propagant => pachete de unda phi => mezoni.

**Anihilare Q+1 + Q-1** [OPEN]:
  Nu testat. Predictie: phi-urile se opun, disorder scade, ambele inele
  se destabilizeaza reciproc mai repede decat unul singur.

---

## 8. Cuplaj Gravitational

**Profilul sigma_g** [CONFIRMED, CPU-071/073]:
  In prezenta inelului, sigma_g scade sub SIGMA_REF in jurul inelului.
  Put gravitational: G_well = SIGMA_REF - mean(sigma_g | r < R_win).
  G_well este proportional cu M_ring (scade odata cu masa).

**Cuplajul k_gm** [CONFIRMED, v7]:
  sigma_g -= k_gm * max(0, SIGMA_REF - sigma_m)  [MINUS = atractie]
  sigma_m += k_gm * max(0, SIGMA_REF - sigma_g)
  Semn gresit (+=) => potential repulsiv (bug confirmat CPU-062/063).
  Corectat din CPU-064 inainte.

**Cascada G** [CONFIRMED, DER-QNG-037]:
  G_eff = k_gm / (z * alpha_g) -- formula v7
  G_QNG = beta_g / z -- formula v1 (single sigma)
  Reconciliere: k_gm = beta_g * alpha_g (conditie de consistenta CC).
  Implicatie: fine-tuning k_gm = fine-tuning alpha (Gap 5, nerezolvat).

**Limita newtoniana** [CONFIRMED, DER-QNG-012/018/019]:
  Phi(r) proportional cu delta_C (devierea C_eff de la referinta).
  G_QNG = beta/z in unitati de substrat.
  Confirmat numeric: QNG-CPU-035.

---

## 9. Numere Cuantice

**Numar barionic B = Q** [EMPIRIC]:
  Q = +1 => barion, Q = -1 => antibarion.
  Conservat topologic (winding nu poate fi distrus lin fara energie).

**Izospin I din R** [EMPIRIC, DER-QNG-038]:
  R par  => I = 1/2 (familia nucleonului: N, N*)
  R impar => I = 3/2 (familia Delta: Delta, Delta*)
  Mecanismul QNG: [OPEN] -- de ce R par/impar => I diferit?

**Spin J din R** [EMPIRIC, DER-QNG-038]:
  J^P(R=4) = 1/2+  [N(938)]
  J^P(R=5) = 3/2+  [Delta(1232)]
  J^P(R=6) = 1/2-? [N*(1520)]
  J^P(R=7) = 3/2-? [Delta(1700)]
  Mecanismul QNG: [OPEN] -- cel mai important gap ramas.

**Momentul unghiular phi** [CONFIRMED negativ, GPU-008]:
  L^2(phi, R) SCADE cu R. Nu scala ca J(J+1) si nici ca R^2.
  Concluzie: phi winding NU codifica spin-ul. Spin-ul vine din alta parte.
  Candidat: precesia orbitala a inelului sau chi field.

**Paritate P** [OPEN]:
  N(938): P=+1, Delta(1232): P=+1, N*(1520): P=-1.
  Cum apare paritatea din geometria inelului? Netestat.

**Sarcina electrica** [OPEN]:
  Protonul are Q_em=+1, neutronul Q_em=0 (ambii R=4).
  Inelele QNG nu au inca un analog pentru sarcina electrica.
  Candidat: semn chi sau chiralitate ca proxy Q_em.

---

## 10. Energetica

**Hamiltonianul v7** [CONFIRMED, DER-QNG-036]:
  H_v7 = T_g[chi] + E_v7
  E_v7 = E_A + E_B + E_F + E_G + E_C (potential)
  T_g[chi] = (1/2) * sum(chi_i^2) (cinetic pentru sigma_g)
  sigma_m: FARA termen cinetic T_m (overdamped).

**Energia inelului** [PARTIAL, CPU-056/057]:
  H_ring = H_total - H_vacuum masurat.
  Scala aproximativ cu M_ring (liniara in masa).
  Relatia exacta E(R): [OPEN]

**Energia de legatura** [OPEN]:
  Doua inele la echilibru (d ~ 3*lambda) au energie de legatura?
  Analog: energia de legatura a deuteronului (2.2 MeV).
  Netestat in QNG.

**Spectrul de mase** [EMPIRIC, CPU-058/063]:
  E ~ R^1 (string tension -- spectru liniar in R).
  Analog mezonic: K(494 MeV) la R=3? [OPEN]
  Regresie Roper N*(1440): ABSENT -- QNG selecteaza excitari orbitale (L=1),
  nu radiale (n=2).

---

## 11. Structura Interna

**Profilul sigma_m** [CONFIRMED, CPU-042/043]:
  sigma_core = 0.21 (in miez, R=5, gamma_phi=0.10)
  sigma_bulk = 0.47 (in bulk)
  Raport core/bulk = 2.2x

**Profilul phi** [CONFIRMED calitativ]:
  phi face un ciclu complet 0..2*pi in sectiunea transversala a tubului.
  Cu Channel H: winding localizat in miez.
  Fara Channel H: winding difuzeaza in bulk (cauza dizolvarii).

**Profilul chi** [PARTIAL]:
  chi este cuplat la sigma_g prin CHI_REL si DELTA_CHI.
  In prezenta inelului: chi < 0 in putat gravitational.
  Profilul exact: [OPEN]

**Raza tubului** [PARTIAL, CPU-043]:
  R_tube ~ 2.5 lu (din profilul sigma_m).
  Dependenta de parametri: [OPEN]

---

## 12. Analogii Fizice

**Cel mai apropiat in fizica cunoscuta**:

1. Modelul Skyrme (1961): barioni ca solitoni topologici in camp scalar.
   Diferenta: QNG are substrat discret + doua campuri separate (sigma_g/sigma_m).

2. Vortex cuantic in superfluid (3He-B, BEC):
   Inelul QNG se comporta ca un vortex inel in condensat.
   Diferenta: in BEC winding-ul da superfluiditate, in QNG da masa barionilor.

3. Wolfram Physics Project: reguli de update pe grafuri => fizica emergenta.
   Diferenta: QNG are predictii cantitative de mase (Wolfram nu).

4. Lord Kelvin (1867): atomi ca inele de vortex in eter clasic.
   Intuita corecta, mediul gresit. QNG: mediu discret cuantic + equations corecte.

---

## 13. Intrebari Deschise (prioritizate)

**CRITICA (blocheaza identificarea barionilor)**:
  Q1. Care este masa locala reala a inelului? (independent de L)
      Masurarea globala M_ring diverge cu L. Necesita windowed measurement.
      [UPDATE 2026-04-18, GPU-015 FAIL] Hamiltonian energy H_v7 = T_g + E_v7
      testat ca observabil alternativ la M_ring. Atat E_ring_global cat si
      E_ring_windowed sufera aceeasi patologie IR ca M_ring (Gate 1 = 0.218,
      Gate 2 = 0.216, threshold 0.03). Global ratio scade monoton 1.88 -> 1.13
      (sub SM=1.313, catre geometric ~1.0); windowed ratio stabilizat la ~2.25
      (window-artifact, nu SM). Structural hint (Gate 4 informational):
      sub-componentele e_B (sigma-gradient energy) si e_chi_rel (chi * grad_sm)
      se apropie monoton de SM=1.313 (la L=80: e_B=1.319, e_chi_rel=1.342),
      dar nu converg in intervalul testat. Optiuni deschise pentru Q1 enumerate
      in 07_validation/audits/qng-hamiltonian-l-convergence-v1/interpretation.md
      (A: e_B-only scan la L>=160; B: confinement mechanism pentru sigma_m;
      C: abandonarea identificarii fixed-R).
      [UPDATE 2026-04-18, GPU-017 FAIL — Optiunea C Hopfion falsificata]
      Hopfion Q=1 disorder L-scan (pre-reg QNG-GPU-017), Hopfion alpha=1.89
      la L=80 vs ring 2.39 (mai SLABA, nu mai rapida). Power-law R2=0.997 bate
      exponential R2=0.973. Topologia NU vindeca halo-ul IR, o agraveaza.
      Optiunea B (einstein-mind: adauga V(sigma_m) Ginzburg-Landau) ramane
      singura cale. Derivarea V(sigma_m) cu lambda dinamic generat (nu
      parametru liber) este necesara INAINTE de orice GPU-018.
      [UPDATE 2026-04-18, GPU-016 FAIL_GEOMETRIC — Optiunea A epuizata]
      e_B extended L-scan {L=20..120, R=4,5}, pre-reg 07_validation/prereg/QNG-GPU-016.md,
      artifacts 07_validation/audits/qng-e-b-l-scan-v1/. Global e_B ratio:
      4.33 -> 2.03 -> 1.53 -> 1.319 -> 1.215 -> 1.155 (drift continuat sub SM).
      Fit competition: Model A (a+b/L) preferat fata de Model B (a+b*log L) cu
      Delta-AIC=12.5; asimptota a=0.356 (threshold era a>1.28). Gate 5 FAIL:
      ratio(L=120)=1.155 < 1.28 (geometric rejection). Ipoteza Bogomolny /
      bag-model pentru e_B ca soliton rest-energy = FALSIFIED.
      STRUCTURAL FINDING (NU rescue): e_B windowed (sphere R+3) si e_B core
      (tube R around ring curve) sunt L-convergente <0.5% la L>=80, dar cu
      valori 4.46/4.84 (NU SM 1.313, NU geometric 1.25). M_ring(R=5)/M_ring(R=4)
      ~ 1.04 la L=120 (depletion egal), deci R=5 packeaza acelasi deficit in
      gradienti mai ascutiti (~R^7 scaling). Sectiunea inelului NU este
      scale-invarianta in R. Niciun observabil QNG dinamic in v5+Channel H nu
      match-uieste SM baryon ratio. Singurele optiuni ramase: B (confinement
      mecanism nou) sau C (abandonarea fixed-R baryon identification).

  Q2. De ce R par => I=1/2 si R impar => I=3/2?
      Mecanism geometric nededus.

  Q3. Cum apare spin-ul J din geometria inelului?
      Momentul unghiular phi NU codifica J (GPU-008: L^2 scade cu R).

**IMPORTANTE (sector de materie)**:
  Q4. Ce emite inelul cand se dizolva in v8 (cu T_phi)?
      In v7: NO_EMISSION confirmat. In v8: nepornit.

  Q5. Exista stari legate de doua inele (analogul deuteronului)?
      Potential Lennard-Jones sugereaza da (CPU-050). Netestat direct.

  Q6. Ce este R=3 la 611 MeV? (barion sau mezon?)
      Nu se potriveste cu niciun barion SM cunoscut.

**DESCHISE (dark matter, cosmologie)**:
  Q7. Exista structuri stabile cu Q=0 (dark matter candidat)?
      [CONFIRMED NO, GPU-004]: Q=0 se dizolva in <500 pasi (retained=0%).
      Dark matter necesita alt mecanism (ex: Q=2, hopfion, sigma_g soliton).

  Q8. Cum se anihileaza Q=+1 si Q=-1?
      Netestat.

  Q9. Poate inelul precesa sub perturbatie externa?
      Raspunsul giroscopic ar putea da J.

  Q10. Ce este sarcina electrica in QNG?
       Analog pentru Q_em neidentificat.

---

## 14. Constante si Parametri de Referinta

| Parametru | Valoare | Sursa | Status |
|-----------|---------|-------|--------|
| ALPHA | 0.005 | CPU-074 | CONFIRMED |
| BETA | 0.35 | CPU-074 | CONFIRMED |
| GAMMA_PHI | 0.10 | CPU-042/043 | CONFIRMED |
| BETA_PHI | 0.02 | CPU-043/074 | CONFIRMED |
| CHI_DECAY | 0.020 | DER-QNG-034 | CONFIRMED |
| K_BACK | 0.10 | CPU-054 | CONFIRMED |
| K_GM | 0.010 | CPU-073 | CONFIRMED |
| a_M | 1.373e-3 | DER-QNG-038 | EMPIRIC (L=20) |
| a (lattice) | ~0.77 l_Planck | DER-QNG-038 | EMPIRIC |
| lambda_screen | ~8.37 lu | sqrt(BETA/ALPHA) | CONFIRMED |
| v_sound (sigma_g) | 0.0764 lu/step | sqrt(K_BACK*CHI_REL/6) | CONFIRMED CPU-054 |

---

*Ultima actualizare: 2026-04-15*
*Teste de referinta: CPU-042/043/049/050/054/071/073/074/075, GPU-001..008 (GPU-004 complet)*
