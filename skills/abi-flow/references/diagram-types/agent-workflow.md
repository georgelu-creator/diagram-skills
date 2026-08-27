# Agent workflow

## Use when

Explain how an Agent receives intent, plans, retrieves context, chooses tools, handles authority, validates results, and writes back knowledge. Use process flow for a human-only SOP.

## Input fields

- initiating actor and goal
- planning and routing steps
- context/memory sources
- tools and external actions
- approval or information gates
- validation and failure behavior
- deliverables and memory writeback

## Fixed layout

Use `LR` for the main loop: request → plan → context → gate → execute → verify → deliver. Put clarification/fallback below the relevant gate. Route revision and learning as outer-lane `feedback` edges from the end of a cycle.

## Visual rules

Use `agent` only for components that choose or act. Use `control` for orchestration, `async` for events/jobs, `success`/`error` for decisions, and `feedback` for real iteration. `spectrum` is the default.

## Example prompt

```text
Create an agent-workflow diagram for a research Agent. Show user intent, task planning, retrieval from files and memory, evidence sufficiency gate, web/tool execution, citation verification, final report, and reusable memory writeback. Use a left-to-right primary path with clearly labeled fallback and feedback loops. Chinese-first, spectrum theme, VisualSpec JSON, strict validation.
```
