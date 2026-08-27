# Enterprise board composition

Use `layout: "board"` when the requested deliverable is a high-density enterprise architecture infographic rather than a small graph. This is the default composition for layered system overviews intended for product, engineering, customer, or executive review.

## What it is for

- 20–45 visible concepts on one scan-friendly canvas
- architecture layers with distinct low-saturation color bands
- grids of bilingual module cards with consistent line icons
- side explanations, guardrails, ownership notes, or example lists
- explicit cross-layer request, control, sync, success, and feedback links
- a numbered lifecycle/data-flow strip and a final principles strip

Do not use a board to hide uncertain relationships. If the source does not establish a layer, owner, or direction, omit it or ask one material question.

## Fixed composition

1. Centered outcome title and one-line scope subtitle.
2. Three to six horizontal `sections` ordered from entry to durable outcomes.
3. A left label rail in every section: Chinese primary label plus compact English role.
4. One to four horizontal `blocks` per section.
5. `grid` blocks for modules, `banner` blocks for shared gateways/control planes, and `list` blocks for examples or guardrails.
6. `connections` only between declared section, block, or card ids.
7. Optional `flow` strip with six or seven numbered steps.
8. Optional `principles` strip with four to six durable design rules.

The renderer uses a 1800-unit vector canvas and exports a 1920-pixel PNG when `png-backend` reports rsvg-convert or ImageMagick. It computes section heights, block spans, card grids, anchors, icon placement, and cross-band routes deterministically.

## Board fields

- `layout`: must be `board`.
- `sections[]`: `id`, `label`, optional `subtitle`, semantic `tone`, and `blocks`.
- `tone`: `blue`, `purple`, `green`, `orange`, `teal`, `slate`, or `amber`. Use color to identify a layer, not for decoration.
- `blocks[]`: `grid`, `banner`, or `list`; use integer `span` to control relative width.
- `grid`: `title`, `columns`, `cards`, and optional `footer`.
- `cards[]`: unique `id`, concise `label`, optional technical `subtitle`, and a built-in line `icon`.
- `banner`: centered gateway/control-plane title, subtitle, and icon.
- `list`: title plus short bullet strings.
- `connections[]`: `source`, `target`, semantic `kind`, optional `label`, and optional `bidirectional`.
- `flow.steps[]` and `principles[]`: label, subtitle, icon.

Use only documented icon names from [`spec.schema.json`](spec.schema.json). Do not embed arbitrary SVG, CSS, remote images, or brand logos in JSON.

## Visual acceptance

- The core capability band is the visual center and receives the largest block.
- All cards keep the same visual grammar: icon, Chinese title, compact technical subtitle.
- Section labels, card labels, and side lists remain legible in the 1920-pixel PNG.
- Cross-layer arrows terminate at borders and never pass through unrelated cards.
- One band uses one semantic tone; keep the full board to five category tones plus neutral/flow strips.
- The reader can answer who enters, how access works, what the core does, which tools connect, where assets live, how one task flows, and which principles govern it.

## Generation prompt

```text
Use $diagram-skills to create a high-density enterprise architecture board.
Audience: product and engineering leadership.
Organize the facts into users/Agents, access/control, core capabilities,
integrations, and sources of truth. Add a right-side guardrail or example list
only where it improves comprehension. Add a six-step data-flow strip and five
principle cards. Use Chinese primary labels, retained English technical terms,
low-saturation layer colors, consistent line icons, and semantic arrows.
Deliver the validated JSON, SVG, HTML, PNG, and quality report. Inspect the PNG
at full size and revise the source if any label, route, or hierarchy is weak.
```

Start from the installed `templates/system-architecture.json`. A full repository checkout also contains the larger `examples/enterprise-agent-office.json` showcase, but generation must not depend on that repository-only example.
