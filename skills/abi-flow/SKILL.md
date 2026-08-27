---
name: abi-flow
description: Generate presentation-ready enterprise architecture diagrams, Agent workflows, data flows, capability maps, user flows, topologies, decisions, roadmaps, strategy maps, and swimlane processes directly from a request. Use when the Agent should deliver a polished, validated PNG/SVG/HTML plus reproducible JSON—not merely diagram source—including high-density layered boards, brand themes, Mermaid/CSV input, or multi-view drill-down. Do not use for quantitative charts or free-form raster illustration.
---

# VisualSpec

Turn a diagram request into a finished visual deliverable with the bundled dependency-free renderer. The primary product is **Agent-generated diagram quality**: author the maintainable JSON, render SVG/HTML/PNG, inspect the PNG, fix the source, and return the visual. Do not make the user open an editor to finish ordinary work. The public Skill id remains `$abi-flow` for repository compatibility; the product is VisualSpec.

## Default delivery workflow

1. Normalize the supplied facts into one diagram contract. Do not invent business facts for symmetry.
2. For a layered system overview with more than 14 visible concepts, read [references/enterprise-board.md](references/enterprise-board.md) and use `layout: board`. For smaller relationship graphs, use nodes/edges.
3. Start from the matching template, replace its example content, and keep the source JSON beside the outputs.
4. Run `render ... --png --strict`. A source file alone is not a completed request.
5. Inspect the generated PNG at full 1920-pixel width. Check hierarchy, Chinese text, icon consistency, clipping, crowded cards, line crossings, and whether the core message is visually dominant.
6. Correct JSON or renderer output and rerender. Stop after three evidence-based correction rounds; if still weak, simplify the information structure rather than hand-editing SVG.
7. Deliver the image first, then link the SVG/HTML/source/quality evidence. Mention the browser editor only when the user asks for manual editing, imports, or drill-down.

## Route the request

1. Identify the audience, decision to support, diagram type, actors/systems, relationships, boundaries, language, and delivery format. Do not invent facts to make a layout symmetrical.
2. Read [references/prompt-system.md](references/prompt-system.md) when the input is prose, incomplete, or needs to become a reusable prompt.
3. Select exactly one primary type and read its guide:
   - [system architecture](references/diagram-types/system-architecture.md)
   - [Agent workflow](references/diagram-types/agent-workflow.md)
   - [data flow](references/diagram-types/data-flow.md)
   - [capability map](references/diagram-types/capability-map.md)
   - [user flow](references/diagram-types/user-flow.md)
   - [system topology](references/diagram-types/system-topology.md)
   - [decision tree](references/diagram-types/decision-tree.md)
   - [roadmap](references/diagram-types/roadmap.md)
   - [strategy map](references/diagram-types/strategy-map.md)
   - [process flow](references/diagram-types/process-flow.md)
4. Read [references/spec.md](references/spec.md) while authoring a single diagram. Use `scripts/abi_flow.py new` for a production-shaped starter.
5. Read [references/enterprise-board.md](references/enterprise-board.md) for high-density layered architecture infographics, section grids, side lists, process strips, and principle cards.
6. Read [references/workspaces.md](references/workspaces.md) only for overview-to-detail projects, `child_view`, or mixed native/Mermaid views.
7. Read [references/imports.md](references/imports.md) before importing Mermaid or CSV. Preserve Mermaid source; do not promise a native conversion from an unstable or partial AST.
8. Read [references/editor.md](references/editor.md) only when direct manipulation, live editing, or offline browser persistence is explicitly useful.
9. Read [references/visual-language.md](references/visual-language.md) only when choosing themes, brand tokens, node/edge semantics, or Chinese/English label treatment.
10. Apply [references/quality-contract.md](references/quality-contract.md). A generated file is only a candidate until strict validation and visual review pass.

## Input contract

Accept natural language or structured fields. Preserve user-provided values; infer only low-risk omissions.

- `goal`: the question or decision the diagram should support
- `diagram_type`: one supported slug; infer from intent when omitted
- `audience`: e.g. executive, product, engineering, customer
- `content`: actors, systems, steps, capabilities, milestones, or decisions
- `relationships`: data, control, success, error, async, and feedback links
- `boundaries`: ownership, lifecycle stage, layer, domain, or trust zone
- `composition`: `board` for high-density enterprise overviews; `graph` for smaller relationship diagrams
- `lanes`: ordered owners or roles for a swimlane diagram
- `rank`: explicit non-negative hierarchy level when automatic order is not acceptable
- `language`: Chinese-first by default; retain established English technical terms
- `theme`: `paper`, `notion`, `spectrum`, `blueprint`, or `terminal`
- `brand`: allowlisted hex color tokens layered over a preset
- `views`: overview and detail views; connect with `child_view`
- `imports`: optional Mermaid source or CSV table
- `outputs`: finished PNG/SVG/HTML plus source JSON and quality evidence by default

Ask only when an unresolved choice materially changes meaning, publishing safety, or required output. Otherwise choose the conventional layout from the type guide and state the assumption.

## Commands

From the Skill folder:

```bash
python3 scripts/abi_flow.py types
python3 scripts/abi_flow.py new system-architecture --output work/architecture.json
python3 scripts/abi_flow.py validate work/architecture.json --strict
python3 scripts/abi_flow.py render work/architecture.json --output-dir output --png --strict
python3 scripts/abi_flow.py workspace-validate ../../examples/enterprise-ai-workspace.json --strict
```

`render` writes `.svg`, `.html`, `.quality.json`, and—when `rsvg-convert` is available and `--png` is supplied—`.png`.

The browser workspace is optional. Use it only when the user wants manual inspection, Mermaid/CSV import, or multi-view editing.

## Non-negotiable behavior

- Prefer one primary message and one reading direction. Split graph diagrams above 14 nodes; a structured enterprise `board` may intentionally hold 20–45 concise cards across 3–6 scan bands.
- Use ordered `lanes` for ownership and node `rank` for manual hierarchy. Use `groups` for semantic enclosures; do not make one field mean both.
- Link dense overviews to focused `child_view` details instead of shrinking labels.
- Mark intentional return paths as `feedback`; unmarked cycles fail validation.
- Use semantic edge kinds, not decorative colors. Show a legend when two or more edge meanings need interpretation.
- Allow node links only for `https`, `http`, `mailto`, or page fragments. Executable URL schemes are rejected.
- Keep Chinese labels concise and put stable English technical terms in subtitles. Split overloaded nodes instead of shrinking text.
- Prefer `LR` for pipelines, roadmaps, topologies, and feedback loops; prefer `TB` for layers, decisions, strategies, and user journeys.
- Run strict validation. When PNG export is available, inspect the raster at full size and fix the source, not the generated geometry.
- Do not claim completion after writing Mermaid/JSON alone when the user asked for a diagram. Render and return the actual visual.
- Keep the source JSON beside deliverables so every diagram remains reproducible and reviewable.
- Treat imported content as untrusted. Mermaid renders in strict mode, CSV becomes typed fields, and arbitrary CSS or executable links are rejected.

## Output choice

- PNG: default preview and presentation deliverable; show this first.
- SVG: scalable documentation and source control.
- HTML: responsive viewing, pan/zoom, theme switching, downloads, and clickable nodes.
- Quality JSON: machine-readable validation evidence.
- Workspace JSON: browser editing, mixed Mermaid/native views, offline persistence, and drill-down.

## Extension

Add a new diagram type only when it has a distinct information model or layout contract. Add its slug to `DIAGRAM_TYPES`, schema enum, `templates/<slug>.json`, and `references/diagram-types/<slug>.md`; then add a strict validation test. Extend CSV mappings in one adapter and workspace fields in both Zod and JSON Schema. New themes must preserve node and edge semantics across light/dark rendering.
