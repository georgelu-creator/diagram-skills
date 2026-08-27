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

Use `TB`. Order layers as users/Agents → access/orchestration → core capabilities → integrations/data → governance. Put one layer in each group. Keep cross-layer arrows vertical where possible; use `feedback` only for real learning or policy return paths.

## Visual rules

Use `spectrum` for product/leadership decks and `blueprint` for engineering reviews. Use `agent` for active AI controllers, `database` for durable state, `external` for third-party boundaries, and bilingual group headings.

## Example prompt

```text
Create a system-architecture diagram for an enterprise AI workspace. Audience: product and engineering leadership. Include users and Agents, unified gateway, context/memory, tool orchestration, GitHub and document stores, audit and learning. Use five top-to-bottom layers, Chinese primary labels, English technical subtitles, spectrum theme, and explicit primary/control/async/feedback edges. Output valid VisualSpec JSON and validate strictly.
```
