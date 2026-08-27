# Decision tree

## Use when

Turn policy or judgment into a finite set of questions and outcomes. Use strategy map for goals and causal initiatives; use process flow when branches are secondary to execution.

## Input fields

- decision subject and owner
- ordered questions
- branch labels and conditions
- terminal outcomes
- evidence needed at each gate
- fallback, escalation, or stop outcomes

## Fixed layout

Use `TB`. Start with the candidate/input, then order decision diamonds from broad eligibility to risk and evidence. Put terminal outcomes on the lowest available rank. Every outgoing edge from a decision needs a clear condition label.

## Visual rules

Use `paper` or `notion`. Reserve green/red semantics for accepted/rejected branches, not preference. Use short questions, parallel grammar, and terminal outcome cards. Avoid cycles; a decision tree should terminate.

## Example prompt

```text
Create a decision-tree for whether an AI feature should launch. Questions: user value proven, privacy/safety risk controlled, evaluation evidence sufficient. Outcomes: research further, guarded pilot, or general launch. Use top-to-bottom diamonds, explicit branch labels, paper theme, Chinese-first labels, valid DiagramSpec JSON.
```
