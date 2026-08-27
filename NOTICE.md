# Inspirations and provenance

DiagramSkills and its DiagramSpec engine (formerly presented as ABI Flow, VisualSkills, and VisualSpec) are an original implementation. The dependency-free Python renderer does not vendor source from the projects below. DiagramSkills Studio consumes released packages through npm; their public APIs provide the generic editor infrastructure:

- [React Flow](https://github.com/xyflow/xyflow): interactive graph canvas and parent-child nodes (MIT)
- [Eclipse ELK / elkjs](https://github.com/kieler/elkjs): layered automatic layout (EPL-2.0)
- [Mermaid](https://github.com/mermaid-js/mermaid): source validation and rendering (MIT)
- [Papa Parse](https://github.com/mholt/PapaParse): CSV parsing (MIT)
- [Monaco Editor](https://github.com/microsoft/monaco-editor): browser source editor (MIT)
- [Yjs](https://github.com/yjs/yjs), y-indexeddb, and y-websocket: CRDT document, offline persistence, and optional network provider (MIT)
- [Zod](https://github.com/colinhacks/zod): browser workspace validation (MIT)
- [Vite](https://github.com/vitejs/vite), React, and TypeScript: application build and runtime (MIT)

Earlier design research also considered Mermaid, D2, Graphviz, diagrams.net, Excalidraw, and fireworks-tech-graph. The resulting DiagramSpec schemas, rendering code, lane/rank adapter, import mappings, interface, prompts, and documentation were written for this repository.

The built-in enterprise-board line icons are original generic interface glyphs. They do not reproduce or claim to be AWS, Azure, Google Cloud, Google Workspace, Slack, Figma, Notion, GitHub, or other vendor product marks. Product names in fictional examples are plain text labels used to describe integrations.

Refer to `editor/package-lock.json` for the resolved dependency graph and to each upstream package for its license and notices.
