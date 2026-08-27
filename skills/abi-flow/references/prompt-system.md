# Prompt and template system

Use this contract to turn prose into a stable diagram brief before authoring JSON. The goal is repeatability: information structure first, visual language second.

## 1. Normalized brief

Collect or infer these fields:

| Field | Question | Default |
|---|---|---|
| `goal` | What decision or understanding should the diagram enable? | Explain the supplied system accurately |
| `diagram_type` | Which information model fits the content? | Infer from the type router |
| `composition` | Small relationship graph or high-density enterprise board? | Board for layered architecture overviews; graph otherwise |
| `audience` | Who must understand it? | Product + engineering leadership |
| `scope` | What is inside/outside the canvas? | Only facts provided or clearly implied |
| `content` | Which actors, steps, systems, capabilities, or milestones exist? | Preserve source wording |
| `relationships` | What flows, controls, branches, stores, or feeds back? | Primary only unless evidence supports more |
| `boundaries` | Which layers, owners, stages, domains, or trust zones matter? | None |
| `lanes` | Do owners/roles need explicit swimlanes? | None |
| `rank_hints` | Which nodes must stay at a specified hierarchy/stage? | Compute from relationships |
| `language` | Which language and technical vocabulary? | Chinese-first, English technical terms retained |
| `theme` | Which presentation context? | `spectrum` |
| `brand` | Are approved brand colors required? | Theme defaults |
| `views` | Does the overview need focused drill-downs? | One view unless density requires splitting |
| `imports` | Is Mermaid or CSV an input source? | None |
| `outputs` | Which deliverables are needed? | JSON + SVG + HTML + PNG + quality report |

Do not infer business facts, performance numbers, ownership, or security boundaries. Ask only when their absence materially changes the diagram.

## 2. Type router

- Layers and system boundaries → `system-architecture`
- Agent plan/tool/verify loop → `agent-workflow`
- Data origin, transformation, storage, consumption → `data-flow`
- Product domains and outcome hierarchy → `capability-map`
- Human journey, screens, choices, completion → `user-flow`
- Runtime services, zones, dependencies, failover → `system-topology`
- Questions and branch outcomes → `decision-tree`
- Time phases, milestones, dependencies → `roadmap`
- Vision, pillars, initiatives, metrics → `strategy-map`
- Operational steps and handoffs → `process-flow`

If two types are both useful, choose one primary overview and recommend a linked drill-down rather than mixing layouts.

For a system/data/Agent overview with three or more layers and more than 14 visible concepts, prefer the reusable `layout: board` composition in [enterprise-board.md](enterprise-board.md). It is intentionally designed for a single dense executive/technical overview; do not split it merely because it exceeds the small-graph node guideline.

## 3. Copy/paste generation prompt

```text
You are designing an enterprise-grade diagram from structured business and technical information.

Goal: {goal}
Diagram type: {diagram_type}
Composition: {graph_or_board}
Audience: {audience}
Scope: {scope}
Content: {content}
Relationships: {relationships}
Boundaries: {boundaries}
Swimlanes: {lanes}
Manual rank hints: {rank_hints}
Language: Chinese-first; retain established English technical terms
Theme: {theme}
Brand tokens: {brand}
Views/imports: {views_and_imports}

Requirements:
1. Preserve facts and relationships. Do not invent components, metrics, ownership, or sequence.
2. Apply the fixed layout contract for {diagram_type}; use one dominant reading direction.
3. Use concise Chinese primary labels and English technical subtitles where useful.
4. Use semantic node types and edge kinds; mark intentional cycles as feedback.
5. For graph composition, target 4–10 nodes and split views above 14 nodes. For board composition, use 3–6 scan bands and 20–45 concise cards with one visual center.
6. Output valid VisualSpec JSON. Use graph nodes/edges or board sections/blocks/connections/flow/principles; never mix the two structures.
7. Render JSON, SVG, HTML, PNG, and quality evidence. Inspect the 1920-pixel PNG, fix source/layout issues, and rerender before delivery.
```

Append the selected type guide's input fields and fixed layout rules. Do not copy all type guides into one prompt.

## 4. Stable visual contract

- Modern SaaS / AI infrastructure aesthetic; flat vector surfaces; no 3D, cartoon, glassmorphism, or decorative illustrations.
- Low-saturation palette with semantic accents and strong text contrast.
- High information density through hierarchy, grouping, and concise subtitles—not smaller type.
- The title states the subject; subtitle states scope, time, or system promise; diagram-type badge records intent.
- Major groups use layer/domain labels; arrows encode meaning, not decoration.
- Source JSON, SVG, HTML, quality report, and optional PNG stay together.

## 5. Revision protocol

When revising a diagram, change meaning first in the JSON, rerender, then compare node/edge/group counts and quality evidence. Never patch a generated SVG to hide a layout issue. If the third evidence-based layout attempt still fails, simplify or split the diagram.
