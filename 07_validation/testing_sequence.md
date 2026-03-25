# Testing Sequence

Type: `note`
ID: `NOTE-VAL-002`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define when the rebuild should move from pure structuring into active testing.

## Short answer

Testing should start as soon as the minimum native stack exists:

1. primitive ontology
2. native update law
3. effective field candidate
4. one emergent-geometry candidate

Not later than that.

## Why not earlier

If we test before those four items exist, then tests will end up defining the theory.

That is exactly what this rebuild is trying to avoid.

## Why not later

If we delay testing until full phenomenology, then category mistakes survive too long and become harder to see.

## Testing phases

### Phase T1: static theory audits

Hardware:

- `CPU`

Purpose:

- forbidden-symbol checks
- category purity checks
- dependency checks

### Phase T2: reference core numerics

Hardware:

- `CPU`

Purpose:

- small deterministic reference implementation
- sanity of native update law
- sanity of effective field construction

### Phase T3: accelerated replication

Hardware:

- `GPU`

Purpose:

- large sweeps
- spectral batches
- robustness scans

### Phase T4: CPU/GPU agreement

Hardware:

- `CPU+GPU`

Purpose:

- verify that accelerated numerics still track the reference implementation

## Practical trigger for us

The trigger to begin active testing is:

- the moment we write `qng-native-update-law-v1`

That should immediately be followed by:

- one CPU reference test
- one GPU-scale test scaffold
- one CPU/GPU agreement spec
