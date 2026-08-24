# Visual language

## Direction

- `LR`: pipelines, lifecycle loops, data movement, model/agent architecture.
- `TB`: decisions, approvals, incident response, procedures read as a checklist.

## Node semantics

| Type | Meaning | Shape treatment |
|---|---|---|
| `process` | Transformation or action | Rounded rectangle |
| `decision` | Branching condition | Diamond |
| `input` | Input or output artifact | Parallelogram |
| `document` | File, report, specification | Folded-corner document |
| `database` | Durable store | Cylinder |
| `agent` | Active controller or AI agent | Double-border rounded rectangle |
| `external` | System outside the owned boundary | Dashed rounded rectangle |

## Edge semantics

| Kind | Meaning | Default treatment |
|---|---|---|
| `primary` | Main data or execution path | Blue solid |
| `control` | Trigger or orchestration | Orange solid |
| `feedback` | Return path or iteration | Purple solid, outer lane |
| `async` | Eventual/asynchronous delivery | Gray dashed |
| `success` | Accepted/healthy branch | Green solid |
| `error` | Failed/rejected branch | Red dashed |

Do not use color as the only signal: dash patterns, labels, and the legend preserve meaning for color-vision deficiencies.

## Themes

- `paper`: warm, low-noise business documentation; default for explanatory pages.
- `notion`: neutral white documentation and knowledge bases.
- `spectrum`: white canvas with accessible pastel node types and stage colors; best for showcase diagrams and presentations.
- `blueprint`: dark technical architecture presentations.
- `terminal`: dark, high-contrast engineering/runbook diagrams.

Themes change surface and typography colors, not graph meaning.

## Content limits

- Target 4–10 nodes; split diagrams above 14 unless a single overview is essential.
- Primary labels: preferably ≤24 Latin characters or ≤12 CJK characters.
- Edge labels: preferably ≤3 words or ≤8 CJK characters.
- Put one main idea in each node. Do not turn nodes into paragraphs.
- Use groups only when they communicate ownership, lifecycle stage, or system boundary.
