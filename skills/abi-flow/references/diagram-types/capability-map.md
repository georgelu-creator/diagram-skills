# Capability map

## Use when

Explain what a product or platform can do, how capabilities cluster into domains, and which customer/business outcomes they support. Do not imply execution sequence unless one truly exists.

## Input fields

- product promise or north star
- capability domains
- atomic capabilities per domain
- shared platform enablers
- user/business outcomes
- maturity or ownership only when supplied

## Fixed layout

Use `TB`: north star → 3–5 capability domains → matching outcomes. Use groups for each horizontal band. Avoid feedback edges and dense cross-links; split domain drill-downs when a domain has more than five capabilities.

## Visual rules

Use `notion` for portfolio documentation or `spectrum` for product storytelling. Prefer noun phrases. Use `database` for shared foundations, `process` for orchestration capability, `decision` for governance, and `document` for outcomes.

## Example prompt

```text
Create a capability-map for an AI customer-support platform. North star: trusted resolution at scale. Domains: understanding, orchestration, agent assistance, automation, governance. Outcomes: faster resolution, higher quality, lower risk. Use three top-to-bottom bands, no invented sequence, concise Chinese labels, English feature keywords, spectrum theme, valid VisualSpec JSON.
```
