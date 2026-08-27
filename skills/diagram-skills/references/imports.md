# Mermaid and CSV imports

This is an optional DiagramSkills Studio workflow from the full repository checkout; it is not bundled as an executable importer in a standalone Skill installation. Read it when the repository's `editor/` package is present and the user wants to convert existing text or table sources into a DiagramSpec workspace.

## Mermaid

Mermaid import is intentionally source-preserving:

1. Store the text in a workspace view with `format: "mermaid"`.
2. Validate with the official Mermaid API.
3. Render with strict security mode.
4. Let the user edit the original source and see the preview update.

Do not claim that arbitrary Mermaid diagrams were converted to native DiagramSpec nodes. Mermaid's public `parse()` API guarantees syntax validation and diagram type detection, not a stable cross-diagram AST. Convert manually only when the user explicitly needs native DiagramSpec editing and the chosen Mermaid type has a reviewed mapping.

## CSV

CSV import creates a native `diagramspec` view with Papa Parse. Supported columns:

| Column | Meaning |
|---|---|
| `node_id` or `id` | Node identifier |
| `label` | Node primary label |
| `subtitle` | Optional secondary label |
| `type` | DiagramSpec node type |
| `lane` | Swimlane id |
| `lane_label` | Human-readable swimlane label |
| `rank` | Non-negative manual hierarchy level |
| `child_view` | Drill-down target view id |
| `source`, `target` | Edge endpoints; missing endpoint nodes are created |
| `source_label`, `target_label` | Labels for endpoint nodes created from an edge table |
| `edge_label` | Optional edge label |
| `edge_kind` | DiagramSpec semantic edge kind |

Example:

```csv
node_id,label,type,lane,lane_label,rank,source,target,edge_kind
request,提交请求,input,user,用户,0,,,
review,人工审核,decision,ops,运营,1,request,review,control
approve,审核通过,process,ops,运营,2,review,approve,success
```

Rules:

- IDs are normalized to `[A-Za-z0-9_.-]+`; two distinct source IDs that normalize to the same value block import.
- Duplicate node rows block import; keep one authoritative node row.
- Unknown node or edge types block import instead of silently changing meaning.
- Invalid manual ranks block import instead of being discarded.
- Invalid CSV, an empty graph, or malformed workspace JSON blocks import and surfaces an error.
- Import untrusted files locally; do not upload private diagrams to a third party.
