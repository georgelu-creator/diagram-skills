# Browser editor

DiagramSkills Studio is a repository companion, not part of a standalone `$diagram-skills` Skill installation. Use it only when a full repository checkout is present and the task needs direct graph manipulation, live source validation, swimlanes, manual hierarchy, imports, brand preview, or multi-view drill-down. The bundled Python CLI remains the complete generation and export path. High-density `layout: board` sources use their generated zoomable HTML for inspection and are not edited in Studio.

## Start locally

First verify that the current checkout contains `editor/package.json`. Then, from the repository root:

```bash
cd editor
npm install
npm run dev
```

Open the local URL printed by Vite. Production assets are created with `npm run build` under `editor/dist`.

## What the editor owns

- React Flow renders and edits native DiagramSpec nodes, edges, lane parents, handles, selection, pan, zoom, and minimap.
- ELK Layered computes automatic positions for non-lane diagrams.
- Explicit `rank` values and swimlanes use a stable grid so manual hierarchy is not discarded by an optimizer.
- Monaco edits the workspace JSON and Mermaid source with immediate validation.
- Papa Parse turns CSV rows into native DiagramSpec nodes, lanes, ranks, and semantic edges.
- Workspace validation mirrors the CLI's ten diagram-type grammar contracts before a native view is committed.
- Mermaid validates and renders imported Mermaid source in `securityLevel: strict`; source is preserved instead of converted with a partial parser.
- Yjs stores the workspace as a convergent map value, while y-indexeddb restores it offline. A `document` query id scopes both the offline database and optional WebSocket room; opening the bare Studio URL creates a new id instead of joining a global room. Set `VITE_YJS_WEBSOCKET_URL` only for a trusted, authenticated Yjs-compatible endpoint.

Realtime collaboration intentionally uses deterministic whole-workspace winner semantics. It prevents concurrent JSON fragments from being concatenated into an invalid document, but it is not field-level collaborative merging. Authentication, authorization, retention, and the WebSocket service itself remain deployment responsibilities and are not bundled with Studio.

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
