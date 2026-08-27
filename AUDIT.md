# VisualSpec delivery audit

Audit date: 2026-08-27

## Verdict

**Passed.** No release-blocking correctness, security, provenance, layout, packaging, or visual-review findings remain in the reviewed upgrade.

## Evidence

- The Agent Skill structure passes the `skill-creator` quick validator.
- The unit suite covers rendering, strict geometry, all 10 diagram-type templates, scaffolding, cycles, link safety, text escaping, schema parsing, themes, directions, and primary CLI artifacts.
- All 10 checked-in templates pass strict validation with zero structural errors, node overlaps, edge/node collisions, group overlaps, or group intrusions.
- Six new gallery diagrams render reproducibly to SVG, standalone HTML, PNG, and quality JSON.
- The six PNGs were inspected at 1920 px. Chinese labels, English subtitles, hierarchy, grouping, arrow routes, legends, whitespace, and light/dark contrast are readable with no clipping.
- SVG is valid XML and generated HTML remains dependency-free with its existing restrictive Content Security Policy.
- Executable URL schemes remain rejected and all text entering SVG/HTML is escaped.
- The renderer and scaffolder use only the Python standard library; optional PNG export uses `rsvg-convert` when available.

## Upgrade scope

1. Repositioned the project as **VisualSpec**, a prompt-native diagram framework and Agent Skill, while preserving the `abi-flow` repository and Skill id for compatibility.
2. Added semantic `diagram_type` metadata and bilingual badges to generated diagrams and quality reports.
3. Added 10 type contracts, 10 valid starter templates, and `types`/`new` CLI commands.
4. Added the normalized prompt contract, Chinese-first enterprise visual language, and progressive Skill routing.
5. Added system architecture, Agent workflow, data flow, capability map, user flow, and system topology gallery assets.
6. Rebuilt the README as an open-source project homepage and added contribution and example guides.

## Residual limitations

- Layout is deterministic and dependency-free, but uses a purpose-built layered heuristic rather than a general graph optimizer. Split dense graphs into linked views.
- Groups are enclosures around computed node bounds; true swimlanes and manual rank hints are not implemented yet.
- PNG export requires `rsvg-convert`; SVG, HTML, JSON scaffolding, validation, and quality reports require no third-party runtime dependency.
- Quantitative charts, BPMN semantics, arbitrary whiteboards, and free-form illustration are outside project scope.

## Reproduction

```bash
python3 -m unittest discover -s tests -v
for spec in skills/abi-flow/templates/*.json; do
  python3 skills/abi-flow/scripts/abi_flow.py validate "$spec" --strict
done
for name in system-architecture agent-workflow data-flow capability-map user-flow system-topology; do
  python3 skills/abi-flow/scripts/abi_flow.py render "skills/abi-flow/templates/$name.json" \
    --output-dir examples/generated --name "$name" --png --strict
done
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/abi-flow
```
