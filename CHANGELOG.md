# Changelog

DiagramSkills is currently pre-release. Until the first tagged release, compatible improvements are recorded under **Unreleased** and breaking changes must also be documented in [`MIGRATION.md`](MIGRATION.md).

## Unreleased

### Added

- Self-contained `$diagram-skills` Agent Skill with ten visual grammars, enterprise boards, editable DiagramSpec JSON, SVG/HTML rendering, and optional local PNG export.
- Optional DiagramSkills Studio for native graph workspaces, swimlanes, ranks, Mermaid source views, CSV import, brand preview, drill-down, and offline persistence.
- Reproducible example gallery, Diagram Briefs, machine-readable quality evidence, and CI validation.

### Changed

- Renamed the public project, repository slug, installable Skill, CLI path, Studio package, workspace format, and browser storage namespace from the former ABI Flow / VisualSkills / VisualSpec names to `DiagramSkills`, `diagram-skills`, and `DiagramSpec`.
- Quality receipts use schema version 3 and remain `pending-review` until the exact source, brief, inspected SVG or PNG, and every declared sibling artifact are hash-bound by the `review` command.
- The installed Skill is self-contained for generation; Studio, Mermaid/CSV import, and multi-view workspaces are clearly repository-only companions.
- The homepage now has English and Chinese editions and seven reviewed visual structures.

### Fixed

- Enforced published JSON Schema and diagram-type contracts without adding a Python runtime dependency.
- Made SVG/HTML deterministic across Python hash seeds, including complete brand-token overrides, and prevented every single-line board region from overflowing text.
- Added non-color edge semantics and legends to both graphs and enterprise boards.
- Applied renderer themes and all brand tokens to enterprise boards with explicit accent/group-stroke precedence.
- Made PNG backend failures explicit and impossible to report as passed quality, including later SVG review attempts.
- Isolated Studio collaboration by document id, prevented concurrent JSON concatenation, and made imports transactional and strict for duplicate rows, unknown enums, normalized collisions, and invalid ranks.
- Rejected duplicate or colliding IDs, unsafe links, invalid references, empty groups/lanes, and non-feedback cycles in Studio.
- Applied all theme and brand tokens to the Studio canvas.

### Compatibility

- This is an intentional pre-release breaking rename. New installs use `georgelu-creator/diagram-skills`, `$diagram-skills`, `scripts/diagram_skills.py`, and Studio workspace format `diagramspec`.
- GitHub redirects the former repository URL, but the removed Skill id, CLI filename, workspace format, and browser storage namespace are not compatibility aliases. See [`MIGRATION.md`](MIGRATION.md).
