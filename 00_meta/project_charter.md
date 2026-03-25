# Project Charter

Project: `Relearning QNG`
Owner: `C.D Gabriel`
Primary assistant role: `theory structuring, dependency control, validation discipline`
Opened: `2026-03-25`

## Mission

Reconstruct QNG in a stricter and cleaner form than the legacy workspace by forcing a one-way build order:

`GR pure -> QM pure -> bridge -> QNG pure -> phenomenology -> validation -> governance`

## Why this workspace exists

- to separate foundational theory from accumulated historical experimentation
- to expose hidden assumptions and category mistakes
- to detect where old derivations depended on post-hoc choices
- to produce a theory tree that is readable by both humans and agents

## Non-goals

- no immediate port of the old repo structure
- no mixing of exploratory artifacts into core theory
- no claim promotion without dependency trace
- no "official" switch logic inside theory folders

## Clean-room discipline

- legacy results may be consulted
- legacy file layout is not binding
- every imported idea must be rewritten in the new category system
- if a concept cannot be located cleanly in one category, it is not mature enough
