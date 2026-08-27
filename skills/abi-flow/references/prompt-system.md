# Prompt and template system

Use this contract to turn prose into a validated **Diagram Brief** before authoring JSON. The goal is repeatability: content intent first, information structure second, visual language third.

## 1. Diagram Brief

Collect or infer these content fields. Do not infer business facts, performance numbers, ownership, dates, security boundaries, protocols, or causal relationships. Ask only when their absence materially changes the diagram.

| Field | Question | Default |
|---|---|---|
| `goal` | What decision or understanding should the diagram enable? | Explain the supplied system accurately |
| `audience` | Who must understand it? | Product + engineering leadership |
| `narrative` | What one sentence remains after a five-second scan? | Derive only from supplied facts |
| `scope` | What is explicitly inside and outside? | Supplied or clearly implied scope only |
| `diagram_type` | Which information model fits the content? | Infer from the type router |
| `composition` | Small relationship graph or high-density board? | Board for layered overviews; graph otherwise |
| `must_show` | Which facts cannot disappear without changing meaning? | Critical supplied entities and relationships |
| `emphasize` | What deserves visual priority? | Main narrative and differentiating boundaries |
| `deemphasize` | What should be grouped or moved to detail? | Low-level detail outside the goal |
| `relationships` | Which sequence, control, data, hierarchy, ownership, dependency, source-of-truth, or feedback semantics matter? | Supported relationships only |
| `uncertainties` | What does the source not establish? | Record it; never silently guess |
| `assumptions` | Which low-risk interpretation choices are made? | Conventional layout choices only |
| `density` | How much information belongs on one canvas? | `medium` |
| `content_risks` | How could the diagram mislead? | Tailor selected profile failure modes |
| `quality_questions` | What must be verified after rendering? | At least three tailored questions |

Keep language, theme, brand, views/imports, lanes/rank hints, and output format as authoring parameters after the content brief.

A brief is ready when it has one coherent narrative, real prioritization, explicit uncertainty, at least one content risk, and three answerable quality questions. Validate it before authoring source:

```bash
python3 scripts/diagram_brief.py work/example.brief.json --strict
```

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

Read only the selected entry in `diagram-thinking-profiles.json`, then read its guide under `diagram-types/`.

For a system/data/Agent overview with three or more layers and more than 14 visible concepts, prefer the reusable `layout: board` composition in [enterprise-board.md](enterprise-board.md). It is intentionally designed for a single dense executive/technical overview; do not split it merely because it exceeds the small-graph node guideline.

## 3. Copy/paste generation prompt

```text
You are designing an enterprise-grade diagram from structured business and technical information.

Source request:
{source_request}

Authoring context:
Audience hint: {audience}
Scope hint: {scope}
Language: Chinese-first; retain established English technical terms
Theme: {theme}
Brand tokens: {brand}
Views/imports: {views_and_imports}

Stage A — Diagram Brief
Output goal, audience, narrative, scope, diagram_type, composition, must_show,
emphasize, deemphasize, relationships, uncertainties, assumptions, density,
content_risks, and at least three quality_questions.

1. Preserve facts. Do not invent components, metrics, ownership, sequence, dates, protocols, boundaries, or causal claims.
2. Select one type and composition. Use a linked detail instead of mixing incompatible information models.
3. Make must_show and deemphasize force real prioritization.
4. Record missing facts under uncertainties rather than guessing.
5. Tailor risks and questions from the selected thinking profile.
6. Validate the sidecar with diagram_brief.py --strict.

Stage B — VisualSpec source
1. Apply the selected type and composition contract with one dominant reading direction.
2. Use concise Chinese labels and useful English technical subtitles.
3. Use semantic node/edge kinds and mark intentional cycles as feedback.
4. Graphs target 4–10 nodes and split above 14. Boards use 3–6 scan bands and 20–45 concise concepts.
5. A must_show fact may not silently disappear; deemphasized facts may be grouped or moved to a child view.
6. Output valid graph nodes/edges or board sections/blocks/connections/flow/principles; never mix them.

Stage C — Render and review
1. Render JSON, SVG, HTML, PNG, and quality evidence with strict validation.
2. Inspect the 1920-pixel PNG and answer every brief quality question with concrete evidence.
3. Append review_answers and run diagram_brief.py --spec <source.json> --strict --reviewed.
4. If any answer fails, fix the brief, source, or renderer and rerender. Do not patch generated SVG.
```

Load only the selected profile and type guide; do not copy every guide into one prompt.

## 4. Stable visual contract

- Modern SaaS / AI infrastructure aesthetic; flat vector surfaces; no 3D, cartoon, glassmorphism, or decorative illustrations.
- Low-saturation palette with semantic accents and strong text contrast.
- High information density through hierarchy, grouping, and concise subtitles—not smaller type.
- The title states the subject; subtitle states scope, time, or system promise; diagram-type badge records intent.
- Major groups use layer/domain labels; arrows encode meaning, not decoration.
- Diagram Brief, source JSON, SVG, HTML, quality report, and optional PNG stay together.

## 5. Revision protocol

When revising a diagram, reread the brief and original request. Update narrative, scope, prioritization, uncertainty, or risks when meaning changes; then change source, rerender, compare quality evidence, and answer the review questions again. Never patch generated SVG. If the third evidence-based attempt still fails, simplify or split the diagram.
