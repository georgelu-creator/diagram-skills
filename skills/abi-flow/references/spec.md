# Diagram specification

The renderer consumes UTF-8 JSON. Keep source specifications under version control. Editors may use [`spec.schema.json`](spec.schema.json) for completion and basic schema validation; the renderer additionally checks graph references, cycles, links, and computed geometry.

## Top-level fields

| Field | Required | Values |
|---|---:|---|
| `title` | yes | Non-empty string |
| `subtitle` | no | Short context line |
| `direction` | no | `LR` (default) or `TB` |
| `theme` | no | `paper`, `notion`, `spectrum`, `blueprint`, or `terminal` |
| `nodes` | yes | Array of node objects |
| `edges` | yes | Array of edge objects |
| `groups` | no | Array of group objects |
| `legend` | no | Boolean; defaults to true when multiple edge kinds exist |

## Nodes

```json
{
  "id": "collect",
  "label": "Collect sessions",
  "subtitle": "Trace, outcome and feedback signals",
  "type": "process",
  "group": "data",
  "link": "https://example.com/traces"
}
```

- `id`: unique token matching `[A-Za-z0-9_.-]+`.
- `label`: short primary label.
- `subtitle`: optional detail; the renderer wraps it.
- `type`: `process`, `decision`, `input`, `document`, `database`, `agent`, or `external`.
- `group`: optional group id.
- `link`: optional `https`, `http`, `mailto`, or `#fragment` target.

## Edges

```json
{
  "source": "evaluate",
  "target": "collect",
  "label": "next cycle",
  "kind": "feedback"
}
```

- `source` and `target` must reference existing nodes.
- `kind`: `primary`, `control`, `feedback`, `async`, `success`, or `error`.
- `feedback` edges are excluded from acyclic rank calculation and routed on an outer lane.
- Parallel edges are allowed but should have distinct meanings and labels.

## Groups

```json
{
  "id": "data",
  "label": "Data loop"
}
```

Groups are visual enclosures, not additional graph nodes. Every referenced group must be declared; empty groups are rejected.

## Complete minimal example

```json
{
  "title": "Release gate",
  "direction": "LR",
  "theme": "paper",
  "nodes": [
    {"id": "change", "label": "Candidate change", "type": "input"},
    {"id": "test", "label": "Regression", "type": "process"},
    {"id": "pass", "label": "Pass?", "type": "decision"},
    {"id": "release", "label": "Release", "type": "process"}
  ],
  "edges": [
    {"source": "change", "target": "test", "kind": "primary"},
    {"source": "test", "target": "pass", "kind": "primary"},
    {"source": "pass", "target": "release", "label": "yes", "kind": "success"},
    {"source": "pass", "target": "change", "label": "fix", "kind": "feedback"}
  ]
}
```
