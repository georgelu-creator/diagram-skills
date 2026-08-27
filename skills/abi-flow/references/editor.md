# Browser editor

Use VisualSpec Studio when the task needs direct manipulation, live source validation, swimlanes, manual hierarchy, imports, brand preview, or multi-view drill-down. The Python CLI remains the stable automation and export path; the editor is an additional workspace surface.

## Start locally

From the repository root:

```bash
cd editor
npm install
npm run dev
```

Open the local URL printed by Vite. Production assets are created with `npm run build` under `editor/dist`.

## What the editor owns

- React Flow renders and edits native VisualSpec nodes, edges, lane parents, handles, selection, pan, zoom, and minimap.
- ELK Layered computes automatic positions for non-lane diagrams.
- Explicit `rank` values and swimlanes use a stable grid so manual hierarchy is not discarded by an optimizer.
- Monaco edits the workspace JSON and Mermaid source with immediate validation.
- Papa Parse turns CSV rows into native VisualSpec nodes, lanes, ranks, and semantic edges.
- Mermaid validates and renders imported Mermaid source in `securityLevel: strict`; source is preserved instead of converted with a partial parser.
- Yjs stores the workspace document, while y-indexeddb restores it offline. Set `VITE_YJS_WEBSOCKET_URL` only for a trusted Yjs-compatible WebSocket endpoint.

The editor loads Monaco from the installed package, not a public CDN.

## Interaction model

- Select a view in the left rail.
- Double-click a node with `child_view` to drill down; use Back to return.
- Select a node to edit label, type, rank, lane, and child view.
- Drag a node to store a manual `position` and switch that view to manual layout.
- Use Workspace JSON for full-source editing. Invalid JSON or references do not replace the last valid canvas.
- Import JSON to replace the workspace; import CSV or Mermaid to add a new view.

## Verification

```bash
cd editor
npm run typecheck
npm test
npm run build
npm audit
```

For release review, also open the production or development build at a desktop viewport and verify overview, drill-down, Mermaid live preview, and CSV import.
