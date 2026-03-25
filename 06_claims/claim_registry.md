# Claim Registry

Type: `note`
ID: `NOTE-CLAIM-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Provide a clean registry standard for claims in the rebuilt workspace.

## Rule

Every claim should eventually have:

- one claim file
- explicit upstream dependencies
- explicit downstream tests
- one current status

## Status vocabulary

- `draft`
- `candidate`
- `supported`
- `failed`
- `archived`

## Anti-confusion rule

No claim should be marked `supported` only because:

- a related script exists
- a fit looks good
- or a legacy note says it passed

Support must point to explicit rebuilt validation records.
