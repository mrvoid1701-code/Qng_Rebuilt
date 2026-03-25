# Figure 1

Title: `rebuilt QNG architecture`
Author: `C.D Gabriel`

Caption:

High-level architecture of the rebuilt QNG program. A native memory-sensitive update law feeds a split effective layer `(C_eff, L_eff)`, from which GR-facing, QM-facing, bridge, and downstream phenomenology layers are derived.

```mermaid
flowchart LR
    A["Native update law"] --> B["Split effective layer (C_eff, L_eff)"]
    B --> C["GR-facing lane"]
    B --> D["QM-facing lane"]
    C --> E["Bridge layer"]
    D --> E
    E --> F["Phenomenology"]
```
