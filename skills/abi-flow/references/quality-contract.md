# Quality contract

A render is deliverable only when every required check passes.

## Structural gate

- JSON parses and matches the supported field vocabulary.
- Node ids are unique; all edge and group references resolve.
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

## Visual review gate

When a PNG renderer is available:

1. Render at 1920 px width.
2. Inspect the image rather than trusting source validation.
3. Check hierarchy, clipping, label wrapping, whitespace, route clarity, and theme contrast.
4. Correct the JSON or renderer, rerun validation, and reinspect. Limit correction to three evidence-based rounds; then simplify or split the diagram.

When no raster renderer or image reader is available, report `visual review: skipped` and do not claim that the diagram was visually verified.

## Security and portability gate

- Generated artifacts contain no remote scripts, fonts, trackers, or runtime dependencies.
- Text and attributes are escaped before entering SVG/HTML.
- Links never use `javascript:`, `data:`, or other executable schemes.
- The source JSON and HTML do not contain credentials or private data unless the user explicitly intends that content to be published.
