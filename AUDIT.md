# DiagramSkills verification record

Verification date: 2026-08-27

This file records reproducible checks and known limits. It does not self-certify that the project is defect-free. The repair candidate must pass the commands below and a separate read-only review before release.

## Prior review findings and closure evidence

| Finding | Repair | Evidence |
|---|---|---|
| Installed Skill referenced repository-only editor/import paths | Generation is self-contained; Studio, Mermaid/CSV import, and workspace editing are explicitly repository companions | `tests/test_skill_package.py` copies only `skills/diagram-skills` and scaffolds, validates, and renders a board |
| Published schema and ten type names were not runtime contracts | Dependency-free schema evaluation now enforces types, required fields, enums, array limits, formats, and `additionalProperties`; type-specific direction and semantic rules are active | malformed-type/additional-field tests plus strict validation of all ten templates |
| Omitting `diagram_type` bypassed the default contract | A missing type now selects the documented `process-flow` default before contract validation instead of returning early | single-node/zero-edge default-contract regression plus independent CLI probe |
| Board text could escape unmeasured regions | Board grids lower effective columns; title, section, banner, list, card, footer, flow, principle, and connection regions report `text_overflow_count` | dense-grid and extreme subtitle/footer regressions plus regenerated boards |
| Edge meaning depended on color | Every graph and board kind changes line pattern and/or width in paths and legends, in addition to color and marker | all-kind graph style test, board semantic-legend test, and inspected gallery PNGs |
| PNG failure could be reviewed into `passed` through the SVG sibling | `png-backend` probes rsvg-convert or ImageMagick; failed requested PNG exits nonzero, produces a failed receipt, and `review` refuses it | missing-backend plus post-failure review regression and CI real rasterizer |
| SVG/HTML changed across `PYTHONHASHSEED` | Ordered brand-token precedence and serialized vocabularies remove set-order drift | full-brand swimlane render compared across four hash seeds |
| Review evidence was not bound to the complete output set | Quality receipt v3 stores sibling filenames and source/SVG/HTML/PNG/brief SHA-256 values; `review` verifies every declared current byte before atomically finalizing `passed` | stale source, selected artifact, sibling HTML, sibling PNG, and brief tests plus seven launch receipts |
| A blocked visual-review state could be finalized | `review` accepts only a pending or already-passed visual-review state and rejects blocked or malformed receipts without mutating them | blocked-state regression plus independent receipt-state probe |
| Arbitrary or duplicated review questions/evidence could pass | `--reviewed` requires `--spec`, profile-grounded unique questions, and concrete distinct evidence | Diagram Brief negative tests and seven reviewed launch Briefs |
| Concurrent Yjs text replacement could produce invalid JSON | Realtime state uses a convergent `Y.Map` value and document-scoped channels | `editor/src/realtime.test.ts` |
| All collaborators shared one room and IndexedDB key | URL `document` id scopes WebSocket room and offline database | realtime channel isolation tests |
| Failed CSV import could still report success | Import is transactional: parse, validate the complete workspace, then commit | importer and workspace-import tests |
| CSV normalization silently merged distinct ids | Normalized node and lane collisions now block import | collision tests |
| CSV import silently defaulted duplicates and unknown semantics | Duplicate authoritative rows, unknown node/edge enums, and invalid ranks now block before the workspace transaction | importer negative tests |
| Browser validation was weaker than the CLI | Studio rejects duplicate ids, unknown/empty groups and lanes, unsafe links, invalid endpoints, bad child views, and non-feedback cycles | model tests |
| Studio could save a graph the CLI type contract rejected | Workspace refinement mirrors all ten CLI diagram-type rules, including minimum structure, required roles/groups, direction, branching, and semantic edges | shared positive workspace plus architecture/decision negative fixtures |
| Deleting the final node could split canvas and source | Deletion is rejected before the React Flow mutation when it would empty the view, lane, or group | model deletion tests |
| Brand/theme controls did not reach the canvas | Five distinct theme token sets and all nine brand tokens drive canvas, nodes, text, borders, groups, edges, and controls | theme tests and production build |
| Enterprise boards silently ignored most theme/brand tokens | Board surfaces, text, boundaries, groups, icons, and edges consume the same five themes and nine-token allowlist with deterministic precedence | board theme/full-token renderer regression |
| Board `accent` disappeared when `group_stroke` was explicit | Accent now has its own visible header emphasis while `group_stroke` overrides only the group boundary | simultaneous nine-token SVG regression plus independent output inspection |
| Homepage looked like one board style and omitted user flow | English and Chinese homepages display seven structures: architecture, Agent workflow, data flow, capability map, swimlane, topology, and user flow | README gallery and `gallery/manifest.json` |

## Current executable checks

```bash
python3 -m unittest discover -s tests -v

for spec in skills/diagram-skills/templates/*.json; do
  python3 skills/diagram-skills/scripts/diagram_skills.py validate "$spec" --strict
done

python3 skills/diagram-skills/scripts/diagram_skills.py png-backend
python3 skills/diagram-skills/scripts/diagram_skills.py render examples/enterprise-agent-office.json \
  --output-dir /tmp/diagramskills --name enterprise-agent-office --png --strict
python3 skills/diagram-skills/scripts/diagram_skills.py review examples/enterprise-agent-office.json \
  --quality /tmp/diagramskills/enterprise-agent-office.quality.json \
  --brief examples/briefs/enterprise-agent-office.brief.json \
  --artifact /tmp/diagramskills/enterprise-agent-office.png

python3 skills/diagram-skills/scripts/diagram_skills.py workspace-validate \
  examples/enterprise-ai-workspace.json --strict

cd editor
npm ci
npm run typecheck
npm test
npm run build
npm audit --audit-level=moderate
```

The test suite replays all eleven checked-in SVG/HTML pairs through the current renderer. CI also exercises a real Linux PNG backend and the integrity of the review command by finalizing a temporary hash-bound receipt; that command test is not represented as a new human visual judgment.

## Checked-in evidence

- Ten strict starter templates cover architecture, Agent workflow, data flow, capability map, user flow, topology, decision, roadmap, strategy, and process/swimlane communication.
- Eleven examples have current SVG, standalone HTML, PNG, and quality receipts.
- Seven homepage examples have individual reviewed Briefs and `status: passed` receipts whose hashes match their current source, brief, SVG, HTML, and PNG files.
- The other four generated examples intentionally remain `pending-review`; generated does not mean visually approved.
- The Hero and six other homepage PNGs were inspected at full size after regeneration for hierarchy, clipping, text fit, route clarity, edge semantics, contrast, and Chinese/English label treatment.
- DiagramSkills Studio was opened in a real desktop browser. The smoke test verified three view types, a document-specific URL and offline store, all nine Blueprint theme tokens reaching the canvas, and transactional CSV failure: a normalized-id collision remained visible in the open import dialog and did not replace the current workspace.

## Known limits

- SVG and HTML require only the Python standard library. PNG remains an optional system integration and requires a backend reported by `png-backend`.
- Text bounds use a conservative font estimate rather than browser `getBBox`; a real visual inspection is still required.
- A hash-bound review proves which bytes were reviewed, not that the written visual judgment is true. The reviewer or Agent remains responsible for the evidence.
- Yjs whole-workspace values converge without corrupting JSON, but simultaneous edits use deterministic winner semantics rather than field-level collaborative merging.
- Network collaboration infrastructure, authentication, authorization, and retention controls are not bundled. Studio remains local/offline-first unless a trusted service is configured.
- Monaco, Mermaid, and ELK produce large optional browser chunks. The build warns about size; loading performance remains a future optimization.
- Quantitative charts, BPMN execution semantics, arbitrary whiteboards, and free-form illustration are outside the project scope.

## Independent review

Status: passed with zero blocking findings on 2026-08-27.

The same read-only reviewer who reported the final three blockers re-ran targeted probes after repair. The default `process-flow` contract rejected a one-node/zero-edge source without `diagram_type`; a blocked visual receipt remained blocked and could not be finalized; all nine simultaneous board brand tokens were present in the SVG with separate accent and group-boundary use. The reviewer also recomputed the source, Brief, SVG, HTML, PNG, and review-anchor hashes for all seven launch receipts and found them current.
