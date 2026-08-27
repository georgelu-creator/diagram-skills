# Mermaid and CSV imports

Read this reference when converting existing text or table sources into a VisualSpec workspace.

## Mermaid

Mermaid import is intentionally source-preserving:

1. Store the text in a workspace view with `format: "mermaid"`.
2. Validate with the official Mermaid API.
3. Render with strict security mode.
4. Let the user edit the original source and see the preview update.

Do not claim that arbitrary Mermaid diagrams were converted to native VisualSpec nodes. Mermaid's public `parse()` API guarantees syntax validation and diagram type detection, not a stable cross-diagram AST. Convert manually only when the user explicitly needs native VisualSpec editing and the chosen Mermaid type has a reviewed mapping.

## CSV

CSV import creates a native `visualspec` view with Papa Parse. Supported columns:

| Column | Meaning |
|---|---|
| `node_id` or `id` | Node identifier |
| `label` | Node primary label |
| `subtitle` | Optional secondary label |
| `type` | VisualSpec node type |
| `lane` | Swimlane id |
| `lane_label` | Human-readable swimlane label |
| `rank` | Non-negative manual hierarchy level |
| `child_view` | Drill-down target view id |
| `source`, `target` | Edge endpoints; missing endpoint nodes are created |
| `source_label`, `target_label` | Labels for endpoint nodes created from an edge table |
| `edge_label` | Optional edge label |
| `edge_kind` | VisualSpec semantic edge kind |

Example:

```csv
node_id,label,type,lane,lane_label,rank,source,target,edge_kind
request,提交请求,input,user,用户,0,,,
review,人工审核,decision,ops,运营,1,request,review,control
approve,审核通过,process,ops,运营,2,review,approve,success
```

Rules:

- IDs are normalized to `[A-Za-z0-9_.-]+`.
- Duplicate node rows update nothing; keep one authoritative node row.
- Unknown node or edge types fall back to `process` and `primary`.
- Invalid CSV, an empty graph, or malformed workspace JSON blocks import and surfaces an error.
- Import untrusted files locally; do not upload private diagrams to a third party.
