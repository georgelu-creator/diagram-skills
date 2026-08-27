---
name: diagram-skills
description: Generate presentation-ready enterprise architecture diagrams, Agent workflows, data flows, capability maps, user flows, topologies, decisions, roadmaps, strategy maps, and swimlane processes from a request. Use when the Agent should directly deliver polished SVG/HTML with editable JSON, plus PNG when a supported local rasterizer is available—not merely diagram source. Includes a self-contained renderer, high-density layered boards, graph starters, visual themes, and strict quality evidence. Do not use for quantitative charts or free-form raster illustration.
---

# DiagramSkills

Turn a diagram request into a finished visual deliverable with the bundled DiagramSpec renderer. The primary product is **Agent-generated diagram quality**: author maintainable JSON, render SVG/HTML and optional PNG, inspect the visual, fix the source, and return the result. Do not make the user open an editor to finish ordinary work. The public Skill id is `$diagram-skills`; the user-facing brand is DiagramSkills.

## Default delivery workflow

1. For prose-to-diagram work or a substantive revision, create a concise `.brief.json` from [templates/briefs/diagram-brief.json](templates/briefs/diagram-brief.json). It records goal, narrative, scope, prioritization, uncertainty, content risks, and review questions—not private chain-of-thought.
2. Read the selected profile in [references/diagram-thinking-profiles.json](references/diagram-thinking-profiles.json), tailor at least three quality questions, and run `diagram_brief.py ... --strict` before drawing.
3. For a layered overview with more than 14 visible concepts, read [references/enterprise-board.md](references/enterprise-board.md) and use `layout: board`. For smaller relationship graphs, use nodes/edges.
4. Start from the matching template, replace its example content, and keep the brief and source JSON beside the outputs.
5. Run `png-backend` before requesting PNG, then run `render ... --strict` with `--png` only when a supported local rasterizer is available. A source file alone is not a completed visual request.
6. Inspect the generated SVG or 1920-pixel PNG at full size. Check hierarchy, Chinese text, icon consistency, clipping, crowded cards, line crossings, and whether the brief's narrative is visually dominant.
7. Answer every brief quality question with concrete, distinct evidence and run `diagram_brief.py ... --spec ... --strict --reviewed`. Then bind the reviewed brief, source, and inspected SVG or PNG into the quality receipt with `diagram_skills.py review ...`. If any check fails, correct the brief, source, or renderer and rerender. Stop after three evidence-based correction rounds; then simplify or split.
8. Deliver the image first, then link the brief, SVG/HTML/source/quality evidence. Mention the browser editor only when the user asks for manual editing, imports, or drill-down.

## Route the request

1. Read [references/diagram-thinking.md](references/diagram-thinking.md) for prose-to-diagram tasks and substantive revisions. Do not invent facts to make a layout symmetrical.
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
4. Read only the selected type's profile in [references/diagram-thinking-profiles.json](references/diagram-thinking-profiles.json).
5. Read [references/spec.md](references/spec.md) while authoring a single diagram. Use `scripts/diagram_skills.py new` for a production-shaped starter.
6. Read [references/enterprise-board.md](references/enterprise-board.md) for high-density layered architecture infographics, section grids, side lists, process strips, and principle cards.
7. The installed Skill is the complete generation path. If a full DiagramSkills repository checkout is also present, [references/workspaces.md](references/workspaces.md), [references/imports.md](references/imports.md), and [references/editor.md](references/editor.md) describe optional Studio-only workflows. Check that the repository's `editor/` directory exists before offering them; never make them a prerequisite for generation.
8. Read [references/visual-language.md](references/visual-language.md) only when choosing themes, brand tokens, node/edge semantics, or Chinese/English label treatment.
9. Apply [references/quality-contract.md](references/quality-contract.md). A generated file is only a candidate until content review, strict validation, and visual review pass.

## Input contract

Accept natural language or structured fields. Preserve user-provided values; infer only low-risk omissions.

- `goal`: the question or decision the diagram should support
- `diagram_type`: one supported slug; infer from intent when omitted
- `audience`: e.g. executive, product, engineering, customer
- `narrative` / `scope`: the five-second story and explicit in/out boundary
- `must_show` / `emphasize` / `deemphasize`: content priority before layout
- `uncertainties` / `assumptions`: facts not supplied and low-risk interpretations
- `content_risks` / `quality_questions`: ways the diagram could mislead and post-render checks
- `content`: actors, systems, steps, capabilities, milestones, or decisions
- `relationships`: data, control, success, error, async, and feedback links
- `boundaries`: ownership, lifecycle stage, layer, domain, or trust zone
- `composition`: `board` for high-density enterprise overviews; `graph` for smaller relationship diagrams
- `lanes`: ordered owners or roles for a swimlane diagram
- `rank`: explicit non-negative hierarchy level when automatic order is not acceptable
- `language`: Chinese-first by default; retain established English technical terms
- `theme`: `paper`, `notion`, `spectrum`, `blueprint`, or `terminal`
- `brand`: allowlisted hex color tokens layered over a preset
- `views`: optional repository-Studio overview and detail views; connect with `child_view`
- `imports`: optional repository-Studio Mermaid source or CSV table
- `outputs`: finished SVG/HTML plus source JSON and diagnostics by default; PNG when the local rasterizer is available

Ask only when an unresolved choice materially changes meaning, publishing safety, or required output. Otherwise choose the conventional layout from the type guide and state the assumption.

## Commands

From the Skill folder:

```bash
python3 scripts/diagram_brief.py work/architecture.brief.json --strict
python3 scripts/diagram_skills.py types
python3 scripts/diagram_skills.py png-backend
python3 scripts/diagram_skills.py new system-architecture --output work/architecture.json
python3 scripts/diagram_skills.py validate work/architecture.json --strict
python3 scripts/diagram_skills.py render work/architecture.json --output-dir output --strict
python3 scripts/diagram_brief.py work/architecture.brief.json --spec work/architecture.json --strict --reviewed
python3 scripts/diagram_skills.py review work/architecture.json --quality output/architecture.quality.json --brief work/architecture.brief.json --artifact output/architecture.svg
```

`render` always writes `.svg`, `.html`, and a hash-bound `.quality.json` receipt; it also writes `.png` when `--png` is supplied and `png-backend` reports a supported rasterizer. A structurally valid render remains `pending-review` until `review` verifies the source, inspected artifact, reviewed brief, and their hashes. A failed PNG request never leaves a passed receipt.

The installed Skill is self-contained for generation. The browser workspace, Mermaid/CSV import, and multi-view editing are repository companions and are available only from a full checkout containing `editor/`.

## Non-negotiable behavior

- Build and validate the concise Diagram Brief before authoring a nontrivial diagram. Share design decisions and evidence, never private chain-of-thought.
- Prefer one primary message and one reading direction. Split graph diagrams above 14 nodes; a structured enterprise `board` may intentionally hold 20–45 concise cards across 3–6 scan bands.
- Use ordered `lanes` for ownership and node `rank` for manual hierarchy. Use `groups` for semantic enclosures; do not make one field mean both.
- Link dense overviews to focused `child_view` details instead of shrinking labels.
- Mark intentional return paths as `feedback`; unmarked cycles fail validation.
- Use semantic edge kinds, not decorative colors. Show a legend when two or more edge meanings need interpretation.
- Allow node links only for `https`, `http`, `mailto`, or page fragments. Executable URL schemes are rejected.
- Keep Chinese labels concise and put stable English technical terms in subtitles. Split overloaded nodes instead of shrinking text.
- Prefer `LR` for pipelines, roadmaps, topologies, and feedback loops; prefer `TB` for layers, decisions, strategies, and user journeys.
- Run brief and diagram strict validation. Inspect the SVG or full-size PNG, answer every type-profile question with distinct evidence, and finalize the hash-bound quality receipt with `review`.
- Do not claim completion after writing Mermaid/JSON alone when the user asked for a diagram. Render and return the actual visual.
- Keep the `.brief.json` and source JSON beside deliverables so meaning and pixels remain reproducible and reviewable.
- When a full repository checkout provides Studio imports, treat imported content as untrusted. Mermaid renders in strict mode, CSV becomes typed fields, and arbitrary CSS or executable links are rejected.

## Output choice

- PNG: preferred preview when `png-backend` reports a supported local rasterizer; otherwise show the SVG first.
- Diagram Brief JSON: content intent, scope, uncertainty, prioritization, risks, and review evidence.
- SVG: scalable documentation and source control.
- HTML: responsive viewing, pan/zoom, theme switching, downloads, and clickable nodes.
- Quality JSON: machine-readable validation evidence.
- Workspace JSON: optional repository-Studio format for browser editing, mixed Mermaid/native views, offline persistence, and drill-down.

## Extension

Add a new diagram type only when it has a distinct information model or layout contract. Add its slug to `DIAGRAM_TYPES`, schema enum, `templates/<slug>.json`, `references/diagram-types/<slug>.md`, and `references/diagram-thinking-profiles.json`; then add strict rendering and thinking-profile tests. Extend CSV mappings in one adapter and workspace fields in both Zod and JSON Schema. New themes must preserve node and edge semantics across light/dark rendering.
