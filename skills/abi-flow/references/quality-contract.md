# Quality contract

A render is deliverable only when every required check passes.

## Content gate

- A nontrivial prose request has a validated `.brief.json` sidecar.
- The brief states one goal, audience, narrative, scope, type, composition, and real content priorities.
- Uncertainties remain absent from the diagram unless later resolved; assumptions are explicit and low risk.
- `must_show` facts remain visible; `deemphasize` facts are intentionally grouped, omitted, or moved to a detail view.
- Content risks are tailored to the selected diagram type rather than copied mechanically.
- After PNG inspection, every quality question has a passing `review_answers` entry with concrete evidence.

Run `diagram_brief.py <brief> --strict` before authoring and `diagram_brief.py <brief> --spec <source> --strict --reviewed` before delivery. The latter also proves that type and composition agree with the rendered source.

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

When a PNG renderer is available:

1. Render at 1920 px width.
2. Inspect the image rather than trusting source validation.
3. Check hierarchy, clipping, label wrapping, whitespace, route clarity, and theme contrast.
4. Correct the JSON or renderer, rerun validation, and reinspect. Limit correction to three evidence-based rounds; then simplify or split the diagram.

The deliverable is the rendered visual, not merely source code. Present the PNG or SVG first, keep JSON beside it for reproducibility, and treat the browser editor as an optional inspection surface rather than a required generation step.

When no raster renderer or image reader is available, report `visual review: skipped` and do not claim that the diagram was visually verified.

## Security and portability gate

- Generated artifacts contain no remote scripts, fonts, trackers, or runtime dependencies.
- Text and attributes are escaped before entering SVG/HTML.
- Links never use `javascript:`, `data:`, or other executable schemes.
- The source JSON and HTML do not contain credentials or private data unless the user explicitly intends that content to be published.
