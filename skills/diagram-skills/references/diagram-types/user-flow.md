# User flow

## Use when

Show a person's journey through entry points, screens/actions, choices, errors, and completion. Use process flow when the primary subject is an internal operating procedure rather than user experience.

## Input fields

- persona and job to be done
- entry point and trigger
- user actions and system responses
- screens or touchpoints
- decisions, errors, and recovery
- success moment and next habit

## Fixed layout

Use `TB` for decision-heavy onboarding or `LR` for short linear journeys. Keep the happy path centered. Put hesitation, error, and recovery branches beside the gate that creates them; return via `feedback` only when the user genuinely re-enters an earlier step.

## Visual rules

Use `external` for the human/entry, `input` for forms or permission grants, `decision` for user choices, `agent` for AI-assisted steps, and `success`/`error` branches with explicit labels. Default to `spectrum`.

## Example prompt

```text
Create a user-flow for first-time activation of an AI meeting assistant. Include discovery, value proof, consent, calendar connection, first recording, summary review, share, and repeat use; include a privacy-concern recovery branch. Use a top-to-bottom happy path, Chinese-first labels, spectrum theme, DiagramSpec JSON, strict validation.
```
