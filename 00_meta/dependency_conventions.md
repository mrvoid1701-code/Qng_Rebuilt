# Dependency Conventions

All theory files in this workspace should declare dependencies explicitly.

## Dependency types

- `primitive dependency`
- `derived dependency`
- `validation dependency`
- `historical source only`

## Rule

If a file uses an old-repo idea only as inspiration, it should not be treated as canonical dependency.  
Only files inside `Relearning qng` can become canonical dependencies in this workspace.

## Preferred style

Each substantive file should include:

- objective
- inputs
- strict exclusions
- downstream uses

This keeps the dependency graph readable by both humans and agents.
