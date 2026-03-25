# QNG-CPU-013

Type: `test`
ID: `QNG-CPU-013`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Check that the first rebuilt matter-sector proxy is bounded, transport-sensitive, distinct from pure geometry, and history-sensitive.

## Category

`qng core`

## Hardware

`CPU`

## Target

From rebuilt QNG quantities, construct:

- `M_eff`

and verify:

- boundedness
- positive relation to memory-load
- positive relation to transport activity
- separation from pure geometry content
- history imprint

## Reference implementation

- `tests/cpu/qng_matter_sector_proxy_reference.py`

## Artifacts

- `07_validation/audits/qng-matter-sector-proxy-reference-v1/report.json`
- `07_validation/audits/qng-matter-sector-proxy-reference-v1/summary.md`
