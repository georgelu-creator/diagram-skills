# Diagram specification

The renderer consumes UTF-8 JSON. Keep sources under version control. Editors may use [`spec.schema.json`](spec.schema.json) for completion and basic schema validation; the renderer additionally checks graph references, cycles, links, and computed geometry.

## Top-level fields

| Field | Required | Values |
|---|---:|---|
| `title` | yes | Non-empty string |
| `subtitle` | no | One short context line |
| `diagram_type` | no | Supported type slug; defaults to `process-flow` |
| `layout` | no | `graph` (default) or high-density `board` |
| `direction` | graph only | `LR` (default) or `TB` |
| `theme` | no | `paper`, `notion`, `spectrum`, `blueprint`, or `terminal` |
| `brand` | no | Injection-safe brand color overrides |
| `nodes` | graph only | Array of node objects |
| `edges` | graph only | Array of edge objects |
| `groups` | no | Array of group objects |
| `lanes` | no | Ordered horizontal or vertical swimlanes |
| `legend` | no | Boolean; defaults to true when multiple edge kinds exist |
| `sections` | board only | Ordered enterprise scan bands |
| `connections` | board only | Links between section, block, or card ids |
| `flow` | board only | Numbered lifecycle/data-flow strip |
| `principles` | board only | Final design-principle cards |

Supported `diagram_type` values:

`system-architecture`, `agent-workflow`, `data-flow`, `capability-map`, `user-flow`, `system-topology`, `decision-tree`, `roadmap`, `strategy-map`, `process-flow`.

The type is semantic metadata: it records intent, selects a template, appears as a diagram badge, and is included in the quality report. Direction and graph relationships still determine layout.

## Enterprise board

Set `layout: "board"` for a layered, presentation-ready enterprise infographic with 20–45 visible concepts. A board replaces `nodes`/`edges` with:

- ordered `sections` using semantic color tones;
- `grid`, `banner`, and `list` blocks with relative `span` widths;
- icon-bearing bilingual cards;
- cross-layer `connections` with the same semantic edge kinds;
- optional numbered `flow` and final `principles` strips.

The full contract, fixed composition, icon policy, and acceptance rules are in [enterprise-board.md](enterprise-board.md). [`spec.schema.json`](spec.schema.json) contains the exact fields and supported built-in icon names.

## Nodes

```json
{
  "id": "context",
  "label": "构建上下文",
  "subtitle": "Memory · Files · Recent activity",
  "type": "process",
  "group": "core",
  "lane": "engineering",
  "rank": 2,
  "child_view": "context-detail",
  "link": "https://example.com/context"
}
```

- `id`: unique token matching `[A-Za-z0-9_.-]+`.
- `label`: short primary label. Chinese-first is recommended for Chinese deliverables.
- `subtitle`: optional detail, English technical terms, or a compact metric.
- `type`: `process`, `decision`, `input`, `document`, `database`, `agent`, or `external`.
- `group`: optional group id.
- `lane`: optional swimlane id. When `lanes` are declared, every node must be assigned.
- `rank`: optional non-negative manual hierarchy level. It overrides the computed topological rank.
- `child_view`: optional target view id used by the browser workspace for drill-down.
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

## Swimlanes

```json
{
  "lanes": [
    {"id": "product", "label": "产品 / PRODUCT", "order": 0},
    {"id": "engineering", "label": "研发 / ENGINEERING", "order": 1}
  ]
}
```

Swimlanes are full diagram bands. In `LR` diagrams they are horizontal; in `TB` diagrams they are vertical. Use a lane for ownership or responsibility and a group for a semantic enclosure. Do not overload one construct to mean both.

## Brand tokens

```json
{
  "theme": "paper",
  "brand": {
    "name": "Acme",
    "primary": "#1D4ED8",
    "accent": "#0F766E",
    "page": "#F8FAFC",
    "surface": "#FFFFFF",
    "ink": "#172033",
    "muted": "#667085",
    "hair": "#D7E0EA",
    "group": "#EFF6FF",
    "group_stroke": "#93C5FD"
  }
}
```

All color values must be six- or eight-digit hex colors. The renderer maps `primary` to the primary edge and Agent accent, and `accent` to group emphasis. The allowlist prevents arbitrary CSS from entering generated SVG.

## Multi-view workspaces

This file describes one renderable diagram. For overview-to-detail projects, wrap diagram views in the versioned workspace contract documented in [workspaces.md](workspaces.md) and validated by [workspace.schema.json](workspace.schema.json).

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
