# Roadmap

## Use when

Show a time-ordered product, platform, or organizational plan with phases, outcomes, and dependencies. This is not a Gantt chart and should not imply dates or commitments that were not supplied.

## Input fields

- time horizon and phase labels
- objective and outcome for each phase
- key deliverables
- dependencies and gates
- owners/status only when supplied
- risks or assumptions that change sequence

## Fixed layout

Use `LR` with one rank per phase. Each phase group contains a milestone card; use linked drill-downs for multiple workstreams. Edges express dependency or readiness, not elapsed time. Keep 3–6 phases.

## Visual rules

Use `spectrum` for roadmap storytelling and `notion` for operating reviews. Use document nodes for milestones, database/agent/process types only when the nature of the deliverable matters. Avoid traffic-light status colors unless status data is provided.

## Example prompt

```text
Create a roadmap for an AI platform across Q1–Q4. Q1 context foundation, Q2 team Agents, Q3 Skill/MCP ecosystem, Q4 governed autonomy. State the outcome of each phase and dependency to the next. Use left-to-right groups, spectrum theme, Chinese primary labels, English technical subtitles, VisualSpec JSON.
```
