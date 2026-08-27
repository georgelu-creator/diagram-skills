# DiagramSkills rename

The pre-release project has completed a one-time naming migration so the repository, install command, Skill invocation and implementation are understandable without prior context.

## Current names

| Surface | Current value |
|---|---|
| Product brand | **DiagramSkills** |
| GitHub repository | `georgelu-creator/diagram-skills` |
| Agent Skill id | `$diagram-skills` |
| Install command | `npx skills add georgelu-creator/diagram-skills --skill diagram-skills` |
| CLI entry point | `skills/diagram-skills/scripts/diagram_skills.py` |
| Source engine/model | **DiagramSpec** |
| Studio package | `@diagramskills/studio` |
| Native Studio view format | `diagramspec` |

## Retired names

`abi-flow`, `$abi-flow`, `abi_flow.py`, VisualSkills and the internal `visualspec` workspace format are retired. The old names were either opaque or collided with an existing AI visual-skill project.

GitHub redirects the former repository URL to the new repository, preserving commit history, issues, stars and settings. New documentation and installations must use the current URL because the removed Skill id, CLI filename, workspace format and browser storage namespace are not maintained as compatibility aliases.

## Why this is a clean break

The migration happened before a stable release and before known external adoption. Keeping duplicate repositories or two installable Skill directories would fragment search results, make the canonical project unclear and double the long-term test surface.

If a pre-release local checkout or Studio workspace exists, export its JSON before upgrading, change native view `format` values from `visualspec` to `diagramspec`, then validate it with the current CLI. Generated DiagramSpec files, SVG, HTML and PNG outputs should be regenerated so their quality receipts bind the current source and renderer.
