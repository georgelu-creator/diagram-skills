# Research and architecture decisions

Research date: 2026-08-27. The goal was to reuse proven diagram infrastructure and keep VisualSpec-specific code focused on its information model, quality contract, and Agent workflow.

## Adopted components

| Capability | Selected component | Why it is used |
|---|---|---|
| Browser canvas | [React Flow](https://reactflow.dev/learn/layouting/sub-flows) | Native React graph state, custom nodes/edges, handles, selection, pan/zoom, and documented parent-child subflows for grouping and lanes |
| Automatic layout | [Eclipse ELK / elkjs](https://eclipse.dev/elk/reference/algorithms/org-eclipse-elk-layered.html) | Layered layout, orthogonal routing, hierarchy, and cross-hierarchy graph support |
| Text diagram import | [Mermaid API](https://mermaid.js.org/config/usage.html) | Official syntax validation and SVG rendering; strict security mode preserves source without a lossy private parser |
| CSV parsing | [Papa Parse](https://www.papaparse.com/docs) | Browser-native CSV parsing with headers, errors, files, workers, and streaming when needed |
| Source editor | [Monaco Editor](https://microsoft.github.io/monaco-editor/) | The VS Code editor engine, with local package loading and browser validation |
| Realtime document | [Yjs](https://docs.yjs.dev/ecosystem/connection-provider/y-websocket) | CRDT document model, offline persistence through [y-indexeddb](https://docs.yjs.dev/getting-started/allowing-offline-editing), optional provider-based network sync |
| Runtime validation | [Zod](https://zod.dev/) | Typed workspace parsing with human-readable failures and cross-reference refinements |

## What VisualSpec implements

VisualSpec supplies the pieces that are product-specific rather than generic infrastructure:

- the diagram and workspace schemas;
- Chinese-first enterprise visual semantics;
- lane, rank, group, edge-kind, brand-token, and child-view mappings;
- CSV column mapping into the VisualSpec model;
- strict deterministic Python export and quality evidence;
- Agent Skill routing and prompt contracts.

## Enterprise diagram research

The high-density board composition was derived from recurring patterns in authoritative architecture libraries rather than copied from one picture:

- [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/) uses complete reference workloads with explicit security, networking, identity, monitoring, governance, and numbered logical flows—not isolated boxes.
- [AWS Architecture Diagrams](https://docs.aws.amazon.com/architecture-diagrams/latest/modern-data-analytics-on-aws/modern-data-analytics-on-aws.html) combines visual grouping, service-adjacent labels, annotated flow, and downloadable/editable source.
- [AWS guidance for better architecture diagrams](https://builder.aws.com/content/3DttzYU07FWj09CqNczGbfSnYF4/how-to-design-better-aws-architecture-diagrams) emphasizes input/processing/output structure, accurate arrow direction, official/current icons, and visual grouping.
- [C4 notation guidance](https://c4model.com/diagrams/notation) requires short element responsibilities and directional, meaningfully labelled relationships; hierarchy is expressed through separate abstraction levels.
- [Azure icon guidance](https://learn.microsoft.com/en-us/azure/architecture/icons/) places product names near icons and prohibits distorting product marks. VisualSpec therefore uses an original, consistent line-icon vocabulary rather than pretending generic glyphs are vendor logos.

These observations became reusable board primitives: horizontal scan bands, left label rails, grid/banner/list blocks, semantic tones, built-in line icons, id-based cross-band connections, a numbered flow strip, and a principle strip. The renderer computes these primitives from JSON; gallery images are not hand-positioned SVGs.

The lane layout is a bounded adapter for explicit `lane` and `rank` fields. It does not attempt to replace a graph optimizer. In VisualSpec Studio, diagrams without explicit lanes use ELK.

## Alternatives considered

- [diagrams.net](https://www.drawio.com/docs/manual/import/import-formats/) already imports Mermaid and specially formatted CSV, supports multi-page files, and exposes an embed protocol. It remains a strong future interoperability target. It was not embedded as the core editor because its XML/page model would make VisualSpec JSON a secondary source of truth.
- Mermaid alone is excellent for source-first diagrams but does not provide the direct node inspector, multi-view workspace, stable VisualSpec semantics, or cross-format JSON contract required here.
- A bespoke canvas, CSV parser, layout optimizer, code editor, or collaboration protocol was rejected because mature libraries already solve those problems.

## Deliberate boundaries

- Mermaid import preserves and renders source; arbitrary diagrams are not silently converted into a partial native graph.
- The default editor is offline-first and does not require a backend. Network collaboration activates only when a trusted Yjs-compatible WebSocket URL is configured.
- The Python CLI keeps zero required third-party runtime dependencies. Browser capabilities live in the separate `editor` package.
- VisualSpec is not a BPMN execution engine, quantitative charting system, or unlimited whiteboard.
