# System architecture

## Use when

Explain layered systems, platform boundaries, integration surfaces, source-of-truth ownership, or a target-state technical design. Do not use it for runtime deployment/failover details; use system topology instead.

## Input fields

- users and entry points
- access/orchestration layer
- core services and responsibilities
- integrations and external systems
- durable stores and sources of truth
- security, governance, and feedback paths
- current vs target state, if relevant

## Fixed layout

For a compact technical relationship graph, use `TB`: users/Agents → access/orchestration → core capabilities → integrations/data → governance.

For a product, strategy, or executive architecture overview, default to [`layout: board`](../enterprise-board.md): users/Agents → access/control → core capabilities → integrations → sources of truth, followed by a numbered data-flow strip and durable principles. Use the core capability band as the visual center, a right-side list for examples or guardrails, and semantic cross-layer arrows. A board may intentionally contain 20–45 concise cards.

## Visual rules

Use low-saturation category tones, white cards, consistent built-in line icons, Chinese primary labels, and compact English technical subtitles. Use a graph `spectrum` theme only when the request is explicitly a smaller relationship diagram.

## Example prompt

```text
Use $diagram-skills to create a presentation-ready enterprise architecture board for an AI workspace. Audience: product and engineering leadership. Include users and Agents, unified gateway, context/memory, tool orchestration, external tools, GitHub and document sources of truth, a six-step task data flow, and five architecture principles. Use Chinese primary labels, retained English technical terms, low-saturation layer tones, consistent line icons, and explicit primary/control/sync/feedback links. Deliver validated JSON, SVG, HTML, and hash-bound quality evidence; add PNG when `png-backend` succeeds, inspect the SVG or PNG, and finalize the review receipt before delivery.
```
