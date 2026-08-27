# Visual language

VisualSpec uses a restrained enterprise language: clear hierarchy, low-saturation surfaces, semantic accents, dense but scannable content, and no decorative 3D or clip art.

## Reading direction

- `LR`: pipelines, lifecycle loops, Agent workflows, data movement, topologies, and roadmaps.
- `TB`: architecture layers, decisions, strategies, capability maps, and user journeys.
- Keep one dominant direction. Use feedback edges only for intentional return paths.

## Chinese-first typography

- Use concise Chinese for primary labels; retain established English technical terms in `subtitle`.
- Preferred pattern: `中文概念` + `English · Technical · Detail`.
- Avoid full-sentence nodes. Target ≤12 CJK characters for labels and one or two short subtitle lines.
- Group labels may use `中文 / ENGLISH` to support fast executive and engineering scanning.

## Node semantics

| Type | Meaning | Shape treatment |
|---|---|---|
| `process` | Transformation or action | Rounded rectangle |
| `decision` | Branching condition or gate | Diamond |
| `input` | Input/output artifact or entry | Parallelogram |
| `document` | File, report, milestone, result | Folded-corner document |
| `database` | Durable store, memory, platform base | Cylinder |
| `agent` | Active controller or AI Agent | Double-border rounded rectangle |
| `external` | User or system outside the boundary | Dashed rounded rectangle |

## Edge semantics

| Kind | Meaning | Default treatment |
|---|---|---|
| `primary` | Main data or execution path | Blue solid |
| `control` | Trigger, policy, orchestration | Orange solid |
| `feedback` | Return path or iteration | Purple solid, outer lane |
| `async` | Eventual/asynchronous delivery | Gray dashed |
| `success` | Accepted or healthy branch | Green solid |
| `error` | Failed, rejected, or fallback branch | Red dashed |

Color is never the only signal: line patterns, labels, and the legend preserve meaning for color-vision deficiencies.

## Themes

- `spectrum`: modern SaaS / AI infrastructure; pastel semantic nodes and layer tones; default for showcases.
- `paper`: warm low-noise business documentation; good for decisions and operating processes.
- `notion`: neutral white knowledge-base style; good for strategy and product maps.
- `blueprint`: dark technical presentation style; good for topology and platform architecture.
- `terminal`: dark high-contrast engineering/runbook style.

Themes change surface and typography colors, never graph meaning.

## Density limits

- Target 4–10 nodes; split above 14 unless a single overview is essential.
- Put one idea in each node. Move stable details to subtitles.
- Edge labels should be verbs, artifacts, branch conditions, or compact metrics.
- Use groups only when they communicate ownership, stage, domain, layer, or boundary.
- Prefer whitespace and grouping over smaller fonts.
