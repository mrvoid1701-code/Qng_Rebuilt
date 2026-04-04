# QNG Lensing Gradient Assignment v1

Type: `note`
ID: `NOTE-LENS-003`
Status: `draft`
Author: `C.D Gabriel`

## Purpose

This document resolves the blocking issue identified in Section 5.3 of `TEST-LENS-002` (`qng-lensing-data-interface-v1.md`). The columns `sigma_grad_x` and `sigma_grad_y` in `data/lensing/cluster_offsets_real.csv` are currently set equal to `lens_x` and `lens_y` respectively. This makes the cosine test statistic T trivially equal to +1.0 for every cluster and constitutes a circular dependency that invalidates any run on the real data.

This document specifies how to replace those columns with an **independent proxy gradient direction** `theta_proxy(i)` for each cluster, and declares the algorithm that must be executed before any comparison against observed offsets is run.

---

## Section 1: The Assignment Problem

### 1.1 What is needed

The test statistic from TEST-LENS-002 §5.3:

```
T = (1/N) * sum_{i=1}^{N} cos(theta_obs(i) - theta_proxy(i))
```

`theta_proxy(i)` must be a 2D sky angle (radians) for each cluster satisfying:

> **Independence requirement:** `theta_proxy(i)` must not be computed from, or be a deterministic function of, `lens_x(i)` or `lens_y(i)` for the same cluster i.

### 1.2 What the current proxy produces

The QNG lensing proxy (DER-LENS-001) produces `alpha_lens(i)` — a signed dimensionless scalar on each node of a 16-node periodic graph (Config: `n_nodes=16, seed=20260325, steps=24`):

```
Phi_lens(i)   = 0.5 * (h_00(i) + h_11(i))
alpha_lens(i) = -0.5 * (Phi_lens[(i+1) % N] - Phi_lens[(i-1) % N])
```

The proxy has **16 nodes**. The cluster catalog has **527 clusters**. This is a 16-to-527 mapping problem.

`alpha_lens(i)` is a signed scalar — it has no intrinsic 2D orientation and cannot specify north/south/east/west without a declared projection convention.

---

## Section 2: Candidate Strategies

| Strategy | Independent? | Implementable now? | Verdict |
|---|---|---|---|
| **A — Hash-based random** | YES | YES | Use as **negative control only** |
| **B — Cosmic web filament direction** | YES | NO (requires external catalog) | Deferred |
| **C — QNG geometry estimator output** | YES | YES | **Primary assignment** |
| **D — Perpendicular to merger axis** | Conditionally | NO (requires X-ray morphology) | Deferred |

### Strategy A detail

`theta_proxy(i) = sha256(system_id_i) mod 2π` — deterministic, independent of offset data, uses only cluster name. Must be run as control (1) in TEST-LENS-002 §5.4. Using it as the primary assignment is a category error.

### Strategy C detail — recommended

Run the canonical proxy simulation (Config defaults), extract `alpha_lens` for all 16 nodes, sort clusters by RA, assign `node_index = cluster_rank mod 16`, project signed scalar to binary north/south sky angle.

---

## Section 3: Recommended Strategy and Complete Algorithm

**Primary: Strategy C. Negative control: Strategy A.**

### 3.1 Declared bridge assumptions

| # | Assumption | Classification |
|---|---|---|
| C.1 | Sorting clusters by RA is a valid proxy for cluster-to-node mapping | **Declared bridge** |
| C.2 | Modular tiling `node_index = cluster_rank mod 16` extends 16 proxy values to 527 clusters | **Declared bridge (weak)** |
| C.3 | Binary sky angle projection (north/south only) is the first valid 1D→2D projection | **Declared bridge — convention must be fixed before running** |
| C.4 | Default Config (`n_nodes=16, seed=20260325, steps=24`) is the canonical proxy run | **Declared bridge — any Config change requires new document version** |

### 3.2 Step-by-step algorithm

**Step 1 — Run proxy simulation**

```python
import sys
sys.path.insert(0, "tests/cpu")

from qng_native_update_reference import Config, run_rollout
from qng_effective_field_reference import field_extract
from qng_lensing_proxy_reference import lensing_proxy

cfg = Config()  # n_nodes=16, seed=20260325, steps=24 — do not modify
_, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
c_eff, _ = field_extract(hist_state, hist_history)
proxy = lensing_proxy(c_eff)
alpha = proxy["alpha"]  # 16 signed floats — write to audit log
```

**Step 2 — Load cluster catalog and sort by RA**

```python
import csv

with open("data/lensing/cluster_offsets_real.csv", newline="", encoding="utf-8") as f:
    clusters = list(csv.DictReader(f))

clusters_sorted = sorted(clusters, key=lambda row: float(row["baryon_ra_deg"]))
for rank, row in enumerate(clusters_sorted):
    row["_ra_sort_rank"] = rank
```

**Step 3 — Assign proxy node index**

```python
n_proxy = len(alpha)  # = 16

for row in clusters_sorted:
    rank = row["_ra_sort_rank"]
    node_index = rank % n_proxy
    row["_proxy_node_index"] = node_index
    row["_alpha_lens"] = alpha[node_index]
```

**Step 4 — Project to 2D sky angle (Convention PROJ-C1)**

```python
import math

for row in clusters_sorted:
    alpha_val = row["_alpha_lens"]
    theta_proxy = math.pi / 2.0 if alpha_val >= 0.0 else 3.0 * math.pi / 2.0
    row["sigma_grad_x"] = math.cos(theta_proxy)   # = 0.0 always under PROJ-C1
    row["sigma_grad_y"] = math.sin(theta_proxy)   # = +1.0 or -1.0
```

Test statistic under PROJ-C1 simplifies to:
```
T = (1/N) * sum_i sin(theta_obs(i)) * sign(alpha_lens(node_i))
```
i.e., the projection of the observed offset onto the north/south axis, signed by the proxy gradient.

**Step 5 — Write output CSV**

```python
from pathlib import Path

output_fields = [
    "system_id", "baryon_x", "baryon_y", "lens_x", "lens_y",
    "sigma_grad_x", "sigma_grad_y", "sigma",
    "baryon_ra_deg", "baryon_dec_deg", "lens_ra_deg", "lens_dec_deg",
    "sep_arcmin", "match_mode", "baryon_id", "lens_id",
    "baryon_source", "lens_source"
]

out_path = Path("data/lensing/cluster_offsets_proxy_assigned.csv")
with open(out_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=output_fields, extrasaction="ignore")
    writer.writeheader()
    # Restore original row order (not RA-sorted) for downstream compatibility
    id_to_row = {row["system_id"]: row for row in clusters_sorted}
    for orig_row in clusters:
        writer.writerow(id_to_row[orig_row["system_id"]])
```

**Step 6 — Write audit log**

File: `data/lensing/cluster_offsets_proxy_assigned_audit.json`

Must contain:
1. The 16 `alpha_lens` values (6 decimal places each)
2. Full RA-sorted cluster order: `(system_id, baryon_ra_deg, ra_sort_rank, proxy_node_index, alpha_lens_value, sigma_grad_y_assigned)` for all 527 clusters
3. Config used: `n_nodes, seed, steps, use_history=True`
4. Script file path and git commit hash at execution time
5. SHA-256 of input `cluster_offsets_real.csv`
6. SHA-256 of output `cluster_offsets_proxy_assigned.csv`

**Step 7 — Strategy A null assignment**

```python
import hashlib

for row in clusters:
    sid = row["system_id"].encode("utf-8")
    hash_int = int(hashlib.sha256(sid).hexdigest(), 16)
    theta_null = (hash_int % 1_000_000) / 1_000_000 * 2.0 * math.pi
    row["sigma_grad_x_null"] = math.cos(theta_null)
    row["sigma_grad_y_null"] = math.sin(theta_null)
```

Write to: `data/lensing/cluster_offsets_null_assigned.csv`

### 3.3 Sky projection convention declaration (PROJ-C1)

```
theta_proxy(i) = pi/2   if alpha_lens(node_index(i)) >= 0   [north, +Dec direction]
theta_proxy(i) = 3*pi/2 if alpha_lens(node_index(i)) < 0    [south, -Dec direction]

sigma_grad_x(i) = cos(theta_proxy(i))  [= 0.0 always]
sigma_grad_y(i) = sin(theta_proxy(i))  [= +1.0 or -1.0]
```

Local tangent plane: x-axis = +RA direction, y-axis = +Dec direction (standard gnomonic, north up, east left).

**Known consequence:** PROJ-C1 discards east/west information entirely. Only the north/south component of the observed offset is tested. East/west extension requires a second independent proxy quantity and is deferred.

This convention must not be changed after the audit log is written.

---

## Section 4: Known Weaknesses

| # | Weakness | Impact |
|---|---|---|
| W1 | Graph has 16 nodes; catalog has 527 clusters. Modular tiling means 33 clusters share each proxy value. | Very weak cluster-specific test — first pass only |
| W2 | RA ordering has no physical derivation. | Bridge assumption with no substrate grounding |
| W3 | Binary projection discards magnitude and east/west. | Low statistical power by construction |
| W4 | The graph is a toy periodic cycle, not the actual large-scale structure environment of any cluster. | No physical connection between graph node and specific cluster |

A FAIL under Strategy C at this stage does not falsify QNG — see TEST-LENS-002 §6.2 for correct failure interpretation.

---

## Section 5: Pre-Run Checklist

- [x] This document committed (NOTE-LENS-003)
- [ ] Proxy assignment script run (Steps 1–7 of §3.2)
- [ ] Audit log written and reviewed
- [ ] `cluster_offsets_proxy_assigned.csv` committed to `data/lensing/`
- [ ] `cluster_offsets_null_assigned.csv` committed to `data/lensing/`
- [ ] Cosine test run against proxy-assigned CSV using statistic from TEST-LENS-002 §5.3
- [ ] Strategy A null run performed simultaneously
- [ ] Results reported under TEST-LENS-002 §5.5 pass criteria

No result computed against `cluster_offsets_real.csv` with circular `sigma_grad` columns counts as a registered test result.

---

## Cross-references

- Blocking issue: `TEST-LENS-002` §5.3 (`qng-lensing-data-interface-v1.md`)
- Proxy definition: `DER-LENS-001` (`qng-lensing-proxy-v1.md`)
- Reference implementation: `tests/cpu/qng_lensing_proxy_reference.py`
- Canonical Config: `tests/cpu/qng_native_update_reference.py`
- Input data: `data/lensing/cluster_offsets_real.csv`
- Output (to produce): `data/lensing/cluster_offsets_proxy_assigned.csv`
- Audit log (to produce): `data/lensing/cluster_offsets_proxy_assigned_audit.json`
