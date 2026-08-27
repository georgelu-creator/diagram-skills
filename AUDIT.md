# VisualSpec delivery audit

Audit date: 2026-08-27

## Verdict

**Passed.** No release-blocking correctness, security, provenance, layout, packaging, or visual-review findings remain in the reviewed upgrade.

## Evidence

- The Agent Skill structure passes the `skill-creator` quick validator.
- The Python suite has 17 passing tests covering rendering, strict geometry, all 10 diagram-type templates, scaffolding, cycles, link safety, text escaping, schema parsing, themes, directions, swimlanes, manual ranks, brand tokens, workspaces, and primary CLI artifacts.
- The browser package has 5 passing tests for workspace references, CSV mappings, and lane-parent layout; TypeScript checking and the Vite production build pass.
- `npm audit` reports zero known vulnerabilities after pinning the patched DOMPurify transitive version.
- All 10 checked-in templates pass strict validation with zero structural errors, node overlaps, edge/node collisions, group overlaps, or group intrusions.
- The three-view enterprise workspace passes strict CLI validation.
- Seven gallery diagrams render reproducibly to SVG, standalone HTML, PNG, and quality JSON, including the new brand-themed swimlane example.
- The gallery PNGs were inspected at 1920 px. Chinese labels, English subtitles, hierarchy, groups/lanes, arrow routes, legends, whitespace, and light/dark contrast are readable with no clipping.
- VisualSpec Studio was exercised in a real desktop browser: the native swimlane overview rendered, double-click drill-down opened its ELK detail, the local Monaco editor and Mermaid live preview loaded without a CDN, and CSV import produced a native two-lane view.
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
7. Added true swimlanes, explicit node rank hints, and allowlisted brand theme tokens to the deterministic renderer and schema.
8. Added a versioned multi-view workspace contract with native and Mermaid views, `child_view` drill-down, schema validation, and an enterprise example.
9. Added VisualSpec Studio using React Flow, ELK, Monaco, Papa Parse, Mermaid, Zod, and Yjs instead of project-local canvas, optimizer, editor, CSV parser, renderer, or CRDT implementations.
10. Added offline IndexedDB persistence, optional Yjs WebSocket sync, Web CI, dependency auditing, and primary-source architecture research.

## Residual limitations

- The Python export path remains a deterministic single-view renderer. Multi-view navigation and Mermaid rendering live in the browser workspace; the CLI validates workspace structure but only checks that Mermaid source is non-empty.
- Authenticated shared-room infrastructure is not bundled. Network collaboration requires a trusted Yjs-compatible endpoint plus application-specific auth, authorization, room isolation, and retention controls.
- Mermaid imports remain source views instead of lossy conversion to native VisualSpec nodes.
- ELK and Mermaid are lazy browser chunks; first use may be noticeably heavier than the base editor bundle.
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
python3 skills/abi-flow/scripts/abi_flow.py workspace-validate examples/enterprise-ai-workspace.json --strict
cd editor
npm ci
npm run typecheck
npm test
npm run build
npm audit
```
