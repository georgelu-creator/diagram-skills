---
name: abi-flow
description: Create or revise enterprise-grade architecture diagrams, Agent workflows, data flows, capability maps, user flows, system topologies, decision trees, roadmaps, strategy maps, and process flows as reproducible JSON, validated SVG, interactive HTML, and optional PNG. Use when meaning, layout, and visual quality must stay stable across revisions; do not use for quantitative charts or free-form raster illustration.
---

# VisualSpec

Turn a diagram request into a maintainable source specification, then render and validate it with the bundled dependency-free tool. The public Skill id remains `$abi-flow` for repository compatibility; the product is VisualSpec.

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
4. Read [references/spec.md](references/spec.md) while authoring JSON. Use `scripts/abi_flow.py new` when a starter is useful.
5. Read [references/visual-language.md](references/visual-language.md) only when choosing themes, node/edge semantics, or Chinese/English label treatment.
6. Render with the bundled script. Correct the JSON or renderer rather than hand-editing generated SVG/HTML.
7. Apply [references/quality-contract.md](references/quality-contract.md). A generated file is only a candidate until strict validation and visual review pass.

## Input contract

Accept natural language or structured fields. Preserve user-provided values; infer only low-risk omissions.

- `goal`: the question or decision the diagram should support
- `diagram_type`: one supported slug; infer from intent when omitted
- `audience`: e.g. executive, product, engineering, customer
- `content`: actors, systems, steps, capabilities, milestones, or decisions
- `relationships`: data, control, success, error, async, and feedback links
- `boundaries`: ownership, lifecycle stage, layer, domain, or trust zone
- `language`: Chinese-first by default; retain established English technical terms
- `theme`: `paper`, `notion`, `spectrum`, `blueprint`, or `terminal`
- `outputs`: source JSON plus any of SVG, HTML, and PNG

Ask only when an unresolved choice materially changes meaning, publishing safety, or required output. Otherwise choose the conventional layout from the type guide and state the assumption.

## Commands

From the Skill folder:

```bash
python3 scripts/abi_flow.py types
python3 scripts/abi_flow.py new system-architecture --output work/architecture.json
python3 scripts/abi_flow.py validate work/architecture.json --strict
python3 scripts/abi_flow.py render work/architecture.json --output-dir output --png --strict
```

`render` writes `.svg`, `.html`, `.quality.json`, and—when `rsvg-convert` is available and `--png` is supplied—`.png`.

## Non-negotiable behavior

- Prefer one primary message and one reading direction. Split diagrams above 14 nodes unless the user explicitly needs a single overview.
- Mark intentional return paths as `feedback`; unmarked cycles fail validation.
- Use semantic edge kinds, not decorative colors. Show a legend when two or more edge meanings need interpretation.
- Allow node links only for `https`, `http`, `mailto`, or page fragments. Executable URL schemes are rejected.
- Keep Chinese labels concise and put stable English technical terms in subtitles. Split overloaded nodes instead of shrinking text.
- Prefer `LR` for pipelines, roadmaps, topologies, and feedback loops; prefer `TB` for layers, decisions, strategies, and user journeys.
- Run strict validation. When PNG export is available, inspect the raster at full size and fix the source, not the generated geometry.
- Keep the source JSON beside deliverables so every diagram remains reproducible and reviewable.

## Output choice

- SVG: editable documentation and source control.
- HTML: responsive viewing, pan/zoom, theme switching, downloads, and clickable nodes.
- PNG: slides, chat, social previews, and fixed-size galleries.
- Quality JSON: machine-readable validation evidence.

## Extension

Add a new diagram type only when it has a distinct information model or layout contract. Add its slug to `DIAGRAM_TYPES`, schema enum, `templates/<slug>.json`, and `references/diagram-types/<slug>.md`; then add a strict validation test. New themes must preserve node and edge semantics across light/dark rendering.
