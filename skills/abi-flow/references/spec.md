# Diagram specification

The renderer consumes UTF-8 JSON. Keep sources under version control. Editors may use [`spec.schema.json`](spec.schema.json) for completion and basic schema validation; the renderer additionally checks graph references, cycles, links, and computed geometry.

## Top-level fields

| Field | Required | Values |
|---|---:|---|
| `title` | yes | Non-empty string |
| `subtitle` | no | One short context line |
| `diagram_type` | no | Supported type slug; defaults to `process-flow` |
| `direction` | no | `LR` (default) or `TB` |
| `theme` | no | `paper`, `notion`, `spectrum`, `blueprint`, or `terminal` |
| `nodes` | yes | Array of node objects |
| `edges` | yes | Array of edge objects |
| `groups` | no | Array of group objects |
| `legend` | no | Boolean; defaults to true when multiple edge kinds exist |

Supported `diagram_type` values:

`system-architecture`, `agent-workflow`, `data-flow`, `capability-map`, `user-flow`, `system-topology`, `decision-tree`, `roadmap`, `strategy-map`, `process-flow`.

The type is semantic metadata: it records intent, selects a template, appears as a diagram badge, and is included in the quality report. Direction and graph relationships still determine layout.

## Nodes

```json
{
  "id": "context",
  "label": "构建上下文",
  "subtitle": "Memory · Files · Recent activity",
  "type": "process",
  "group": "core",
  "link": "https://example.com/context"
}
```

- `id`: unique token matching `[A-Za-z0-9_.-]+`.
- `label`: short primary label. Chinese-first is recommended for Chinese deliverables.
- `subtitle`: optional detail, English technical terms, or a compact metric.
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
- Parallel edges are allowed but should express distinct meanings and labels.

## Groups

```json
{
  "id": "core",
  "label": "核心能力 / CORE CAPABILITIES"
}
```

Groups are visual enclosures, not graph nodes. Use them only for layers, ownership, lifecycle stages, domains, or trust boundaries. Every referenced group must be declared; empty groups are rejected.

## Complete minimal example

```json
{
  "title": "变更发布流程",
  "subtitle": "从候选变更到稳定发布",
  "diagram_type": "process-flow",
  "direction": "LR",
  "theme": "paper",
  "nodes": [
    {"id": "change", "label": "候选变更", "type": "input"},
    {"id": "test", "label": "自动验证", "type": "process"},
    {"id": "pass", "label": "验证通过？", "type": "decision"},
    {"id": "release", "label": "发布", "type": "process"}
  ],
  "edges": [
    {"source": "change", "target": "test", "kind": "primary"},
    {"source": "test", "target": "pass", "kind": "control"},
    {"source": "pass", "target": "release", "label": "是", "kind": "success"},
    {"source": "release", "target": "change", "label": "next cycle", "kind": "feedback"}
  ]
}
```

Use `python3 scripts/abi_flow.py new <diagram_type> --output <file>` to start from a production-shaped source instead of a blank object.
