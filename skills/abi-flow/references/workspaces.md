# Multi-view workspaces

A workspace is the browser editor's source of truth for overview-to-detail navigation. Use it when one canvas would exceed the primary-message rule or when different audiences need different levels of detail.

## Shape

```json
{
  "schema_version": "3.0",
  "title": "Enterprise AI Platform",
  "entry_view": "overview",
  "views": [
    {
      "id": "overview",
      "format": "visualspec",
      "title": "平台总览",
      "diagram_type": "system-architecture",
      "direction": "LR",
      "theme": "spectrum",
      "layout_mode": "ranked",
      "groups": [],
      "lanes": [],
      "nodes": [
        {"id": "gateway", "label": "统一网关", "type": "process", "child_view": "gateway-detail"}
      ],
      "edges": []
    },
    {
      "id": "gateway-detail",
      "format": "mermaid",
      "title": "网关内部流程",
      "source": "flowchart LR\n  A[Auth] --> B[Route]"
    }
  ]
}
```

`workspace.schema.json` provides editor completion and structural checks. Runtime validation additionally enforces unique view ids, an existing `entry_view`, valid edge endpoints, lane references, and `child_view` references.

## View formats

- `visualspec`: native editable graph. It adds `id`, `format`, and `layout_mode` to the single-diagram contract. Nodes may also store editor `position` values.
- `mermaid`: original Mermaid source with live validation and preview.

## Drill-down rules

- Keep the entry view below roughly 14 nodes; link to focused detail views.
- A node may name one `child_view`. Use separate nodes when multiple detail perspectives are required.
- Keep overview labels stable so links remain understandable even when detail views evolve.
- Avoid circular drill-down. Navigation can recover, but a circular information hierarchy is confusing.
- Each view must still satisfy one reading direction and one primary message.

## Validation

```bash
python3 skills/abi-flow/scripts/abi_flow.py workspace-validate examples/enterprise-ai-workspace.json --strict
```

Mermaid syntax is validated in the browser editor by the official Mermaid engine; the dependency-free Python validator checks that Mermaid views contain non-empty source.
