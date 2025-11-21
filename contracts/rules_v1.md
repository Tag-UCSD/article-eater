# Rules Contract v1.0
## Purpose
Canonical micro‑contract for the Rules module: data model, required fields, and invariants used by services and UI.

## Schema (minimal)
- id: integer, unique
- text: string (required)
- parent_id: integer|null (self‑reference)
- evidence_count: integer >= 0
- weight: float ([-1.0, 1.0])
- paper_id: integer|null (FK to papers)

## Invariants
- `text` non‑empty; trimmed <= 1000 chars.
- `weight` in [-1, 1].
- `evidence_count` non‑negative integer.

## Versioning
- Version: v1.0
- Changes require a ledger update and a minor/major bump.