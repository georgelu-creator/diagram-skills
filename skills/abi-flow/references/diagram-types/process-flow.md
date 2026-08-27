# Process flow

## Use when

Explain an operational procedure, handoff, approval, release, incident, or lifecycle. Use Agent workflow when autonomous planning/tool use is central and user flow when screens and human experience are central.

## Input fields

- trigger and expected outcome
- ordered actions and owners
- inputs and produced artifacts
- decisions and branch conditions
- handoffs, waits, and async events
- failure, escalation, and feedback paths

## Fixed layout

Use `LR` for a compact lifecycle or `TB` for approval-heavy procedures. Keep the happy path dominant and put exception outcomes beside the relevant gate. A return to an earlier step must be `feedback`; terminate abandoned/rejected branches explicitly.

## Visual rules

Use `paper` for business operations and `terminal` for runbooks. Use verbs for action labels, nouns for artifacts, decision diamonds for real branches, and semantic edge kinds. Add a legend when branch meanings are not self-evident.

## Example prompt

```text
Create a process-flow for production release: candidate change, automated checks, risk gate, canary, monitoring, full release, retrospective, and a fix/retry path. Use a left-to-right happy path with explicit success/error/feedback semantics, paper theme, Chinese-first labels, VisualSpec JSON, strict validation.
```
