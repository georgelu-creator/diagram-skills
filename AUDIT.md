# ABI Flow delivery audit

Audit date: 2026-08-24

## Verdict

**Passed.** No release-blocking correctness, security, provenance, layout, or packaging findings remain in the reviewed standalone project.

## Evidence

- Agent Skill structure passes the official `skill-creator` quick validator.
- The full unit suite passes: 11 tests covering rendering, strict geometry, cycles, link safety, text escaping, schema parsing, CLI artifacts, themes, and directions.
- Strict validation passes on the included example with:
  - 12 nodes, 17 semantic edges, 6 system groups, and 51 routed segments
  - 0 node overlaps
  - 0 edge/node collisions
  - 0 edge crossings
  - 0 group overlaps
  - 0 group intrusions
- SVG is valid XML and the generated HTML loads without browser console warnings or errors.
- Browser review confirms pan, zoom, reset, theme switching, and clickable node links.
- SVG, HTML, and quality JSON render reproducibly from the same input.
- The generated PNG was inspected at 1920 px and contains no clipping, black-fill regression, unreadable labels, or overlapping groups.
- A filename-only secret scan found no credentials or private-key material in tracked files.
- `NOTICE.md` identifies conceptual inspirations; no third-party source code or bundled dependency is included.

## Findings resolved during review

1. CSS custom properties were not resolved by every SVG-to-PNG renderer, producing a black raster preview. Raster export now materializes theme colors before conversion.
2. Group containers could overlap or contain unrelated nodes without failing strict mode. Both conditions are now measured and rejected.
3. URL validation accepted malformed HTTP(S) links. HTTP(S) links now require a network location, and executable schemes are rejected.
4. Cycles without an explicit feedback edge were ambiguous. Strict mode now rejects unmarked cycles.

## Residual limitations

- Layout is deterministic and dependency-free, but it is a purpose-built layered heuristic rather than a general graph optimizer. Very dense graphs should be split into multiple views.
- PNG export requires `rsvg-convert`; SVG, HTML, and the quality report have no third-party runtime dependency.
- The quality report records automated geometry checks. Visual inspection remains a release step for each new diagram.

## Reproduction

```bash
python3 -m unittest discover -s tests -v
python3 skills/abi-flow/scripts/abi_flow.py validate examples/aurora-resilience-network.json --strict
python3 skills/abi-flow/scripts/abi_flow.py render examples/aurora-resilience-network.json --output-dir examples/generated --name aurora-resilience-network --png --strict
```
