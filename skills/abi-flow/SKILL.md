---
name: abi-flow
description: Create or revise polished process flowcharts and technical workflow diagrams as deterministic SVG, interactive standalone HTML, and optional PNG. Use for process flows, architecture/data-flow explanations, feedback loops, linked diagram nodes, or when diagram quality needs geometry and accessibility validation; do not use for quantitative charts or free-form illustration.
---

# ABI Flow

Turn a process description into a maintainable diagram specification, then render and validate it with the bundled deterministic tool.

## Route the request

1. Extract the meaning before drawing: actors, steps, decisions, artifacts, groups, edge direction, feedback loops, and links.
2. Choose the smallest diagram that preserves the meaning. Split diagrams that exceed 14 nodes unless the user explicitly needs a single overview.
3. Read [references/spec.md](references/spec.md) while authoring or editing the JSON specification.
4. Read [references/visual-language.md](references/visual-language.md) when choosing node types, edge semantics, direction, or theme.
5. Render with `scripts/abi_flow.py`; do not hand-edit generated SVG or HTML unless the renderer cannot express a required feature.
6. Apply [references/quality-contract.md](references/quality-contract.md) before delivery. A generated file is a candidate until validation and visual review pass.

## Commands

```bash
python3 scripts/abi_flow.py render input.json --output-dir output --png --strict
python3 scripts/abi_flow.py validate input.json --strict
```

`render` writes `.svg`, `.html`, `.quality.json`, and—when `rsvg-convert` is available and `--png` is supplied—`.png`.

## Non-negotiable behavior

- Preserve the user's facts and relationships. Never invent a step to make the layout more symmetrical.
- Mark intentional return paths as `feedback`; unmarked cycles fail validation.
- Use semantic edge kinds, not decorative colors. Include a legend whenever two or more edge kinds are present.
- Allow node links only for `https`, `http`, `mailto`, or page-fragment targets. The renderer rejects executable URL schemes.
- Keep labels concise. Move explanations into `subtitle`; split overloaded nodes rather than shrinking text.
- Prefer `LR` for pipelines and feedback loops, `TB` for approval/decision flows.
- Run `--strict`, inspect the PNG when rendering is available, and correct the JSON rather than patching generated geometry.
- Report any skipped validation explicitly. Do not claim visual review when no raster was inspected.

## Output choice

- Deliver SVG for editable documentation and source control.
- Deliver standalone HTML when the user needs responsive viewing, light/dark themes, pan/zoom, downloads, or clickable nodes.
- Deliver PNG for slides, chat, and fixed previews.
- Keep the source JSON beside every deliverable so the diagram remains reproducible.
