# Contributing to VisualSpec

VisualSpec accepts focused contributions that improve diagram meaning, deterministic rendering, validation, accessibility, templates, or documentation.

## Before opening a change

- Check whether the request belongs to an existing diagram type.
- Add a new type only when it has a distinct information model or fixed layout contract.
- Preserve existing JSON compatibility unless the change is intentionally versioned.
- Do not add runtime dependencies when the standard library is sufficient.

## Local workflow

```bash
python3 -m unittest discover -s tests -v
for spec in skills/abi-flow/templates/*.json; do
  python3 skills/abi-flow/scripts/abi_flow.py validate "$spec" --strict
done
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/abi-flow
```

For visual changes, render representative `LR` and `TB` diagrams in light and dark themes. Inspect the PNG at full size for clipping, text wrapping, hierarchy, edge routes, group boundaries, and contrast.

## Add a diagram type

1. Add the slug and bilingual label to `DIAGRAM_TYPES` in `scripts/abi_flow.py`.
2. Add it to the `diagram_type` enum in `references/spec.schema.json`.
3. Add `templates/<slug>.json`; it must pass strict validation.
4. Add `references/diagram-types/<slug>.md` with use cases, input fields, fixed layout, visual rules, and an example prompt.
5. Add or update tests that prove the type is discoverable and its template is valid.

## Pull requests

- Keep one concern per pull request.
- Explain the diagram behavior or quality problem being solved.
- Include the exact validation commands and results.
- For output changes, include before/after screenshots or generated SVGs.
- Do not commit credentials, private architecture, customer data, or confidential URLs.

By contributing, you agree that your contribution is licensed under the repository's MIT License.
