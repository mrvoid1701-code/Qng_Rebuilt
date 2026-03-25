# Paper Figure Pack v1

Type: `note`
ID: `NOTE-EXP-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Provide one renderable pack containing all primary manuscript figures for rebuilt QNG.

## Figure 1: rebuilt QNG architecture

```mermaid
flowchart LR
    A["Native update law"] --> B["Split effective layer (C_eff, L_eff)"]
    B --> C["GR-facing lane"]
    B --> D["QM-facing lane"]
    C --> E["Bridge layer"]
    D --> E
    E --> F["Phenomenology"]
```

## Figure 2: legacy compression vs rebuild correction

```mermaid
flowchart LR
    A["Legacy compression"] --> B["Sigma overloaded"]
    A --> C["tau drift"]
    A --> D["chi = m/c hardened too early"]
    A --> E["Phenomenology carrying theory load"]
    B --> F["Rebuild correction"]
    C --> F
    D --> F
    E --> F
    F --> G["Native memory in update law"]
    F --> H["Split effective layer"]
    F --> I["Bridge ladders"]
    F --> J["Phenomenology downstream only"]
```

## Figure 3: GR recovery ladder

```mermaid
flowchart LR
    A["C_eff"] --> B["Geometry proxy"]
    B --> C["Lorentzian signature proxy"]
    C --> D["Weak-field assembly"]
    D --> E["Linearized curvature proxy"]
```

## Figure 4: QM recovery ladder

```mermaid
flowchart LR
    A["(C_eff, phi)"] --> B["Correlator proxy"]
    B --> C["Local generator proxy"]
    C --> D["Mode/spectrum proxy"]
    D -.-> E["Continuity closure (open)"]
```

## Figure 5: bridge and source-response

```mermaid
flowchart LR
    A["GR-facing lane"] --> C["Back-reaction proxy closure"]
    B["QM-facing lane"] --> C
    C --> D["Source-response consistency"]
```

## Figure 6: phenomenology descent map

```mermaid
flowchart LR
    A["Rebuilt core"] --> B["Trajectory"]
    A --> C["Lensing"]
    A --> D["Rotation"]
    A --> E["Timing"]
    A --> F["Cosmology"]
```

## Figure 7: support status map

```mermaid
flowchart TB
    A["Proxy-supported"] --> A1["Native update"]
    A --> A2["CPU/GPU agreement"]
    A --> A3["Split effective layer"]
    A --> A4["GR weak-field lane"]
    A --> A5["QM generator/spectrum lane"]
    A --> A6["Bridge/source-response"]
    A --> A7["Phenomenology proxies"]
    B["Candidate"] --> B1["GR recovery program"]
    B --> B2["QM recovery program"]
    B --> B3["Unified split-bridge architecture"]
    B --> B4["Provisional core backbone"]
    C["Open"] --> C1["Exact GR recovery"]
    C --> C2["Exact QM recovery"]
    C --> C3["Exact closure"]
    C --> C4["Final matter ontology"]
    C --> C5["Universal tau"]
    C --> C6["Final Sigma status"]
```

## Figure 8: freeze core vs experimental lanes

```mermaid
flowchart LR
    A["Provisional core"] --> B["Native update"]
    A --> C["(C_eff, L_eff)"]
    A --> D["GR/QM lanes"]
    A --> E["Bridge"]
    F["Experimental lanes"] --> G["Exact recovery theorems"]
    F --> H["chi mass semantics"]
    F --> I["tau unification"]
    F --> J["Proxy-to-data mapping"]
```
