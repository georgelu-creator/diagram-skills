# Quality contract

A render is deliverable only when every required check passes.

## Content gate

- A nontrivial prose request has a validated `.brief.json` sidecar.
- The brief states one goal, audience, narrative, scope, type, composition, and real content priorities.
- Uncertainties remain absent from the diagram unless later resolved; assumptions are explicit and low risk.
- `must_show` facts remain visible; `deemphasize` facts are intentionally grouped, omitted, or moved to a detail view.
- Content risks are tailored to the selected diagram type rather than copied mechanically.
- After SVG or PNG inspection, every type-profile question has a passing `review_answers` entry with concrete, distinct evidence.

Run `diagram_brief.py <brief> --strict` before authoring and `diagram_brief.py <brief> --spec <source> --strict --reviewed` after inspection. The latter requires the source, profile-grounded unique questions, and non-template evidence, and proves that type and composition agree.

Then finalize the render receipt:

```bash
python3 scripts/abi_flow.py review source.json \
  --quality output/diagram.quality.json \
  --brief source.brief.json \
  --artifact output/diagram.svg
```

`render` records source and output SHA-256 values plus sibling artifact filenames and leaves overall status `pending-review`. `review` recomputes the source hash and every declared SVG/HTML/PNG hash, validates the brief against the source, verifies that the inspected SVG or PNG is the declared sibling output, and atomically changes the receipt to `passed`. Any changed source, brief, sibling artifact, missing PNG, failed PNG request, or failed structural check blocks finalization; rerender instead of editing the receipt by hand. A failed PNG receipt cannot be finalized by switching the review target to SVG: rerender without `--png` first.

## Structural gate

- JSON parses and matches the supported field vocabulary.
- Node ids are unique; all edge and group references resolve.
- Board section, block, and card ids are unique; all board connections resolve.
- Non-feedback edges form a DAG. Intentional cycles are explicitly `feedback`.
- Links use an allowed scheme.
- SVG parses as XML; every marker reference resolves.

## Geometry gate

- Nodes do not overlap.
- Edges terminate at node boundaries.
- Edge segments do not cross unrelated node interiors.
- Text-width estimates fit the selected node geometry.
- Canvas margins, title area, group padding, and legend area remain clear.
- Crossings are counted and reported. Zero crossings is the target; any residual crossing must be explained.

## Accessibility gate

- SVG has a title and description.
- Meaning is not encoded by color alone.
- Linked nodes have an accessible label, visible focus state, and safe new-tab behavior.
- The interactive HTML supports keyboard zoom/reset controls and reduced-motion preferences.
- Minimum body text remains readable when the SVG is shown at 960 CSS pixels.

For high-density boards, review at the delivered 1920-pixel width. The board is intended for full-width documentation, decks, and zoomable HTML rather than a narrow inline chat column.

## Visual review gate

When `png-backend` reports a PNG renderer:

1. Render at 1920 px width.
2. Inspect the image rather than trusting source validation.
3. Check hierarchy, clipping, label wrapping, whitespace, route clarity, and theme contrast.
4. Correct the JSON or renderer, rerun validation, and reinspect. Limit correction to three evidence-based rounds; then simplify or split the diagram.

The deliverable is the rendered visual, not merely source code. Present the PNG or SVG first, keep JSON beside it for reproducibility, and treat the browser editor as an optional inspection surface rather than a required generation step.

When no raster renderer is available, inspect the SVG at full size and bind that SVG as the reviewed artifact. If no image inspection capability is available, leave the receipt `pending-review` and do not claim visual verification.

## Security and portability gate

- Generated artifacts contain no remote scripts, fonts, trackers, or runtime dependencies.
- Text and attributes are escaped before entering SVG/HTML.
- Links never use `javascript:`, `data:`, or other executable schemes.
- The source JSON and HTML do not contain credentials or private data unless the user explicitly intends that content to be published.
