<p align="center">
  <img src="skills/diagram-skills/assets/icon.svg" width="88" alt="DiagramSkills mark">
</p>

<p align="center"><a href="README.zh-CN.md">简体中文</a> · <strong>English</strong></p>

<h1 align="center">DiagramSkills</h1>

<p align="center"><strong>Beautiful visual thinking skills for AI agents.</strong></p>

<p align="center">
  Turn ideas, systems and complex information into visuals people can understand, edit and trust.<br>
  把复杂系统、流程与策略，变成真正能看懂、能修改、能交付的图。
</p>

<p align="center">
  Architecture · Workflows · Data Flows · Capability Maps · Topology · Decisions · Strategy
</p>

<p align="center">
  <a href="https://github.com/georgelu-creator/diagram-skills/actions/workflows/ci.yml"><img src="https://github.com/georgelu-creator/diagram-skills/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-171717" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Agent%20Skill-diagram--skills-4F46E5" alt="Agent Skill diagram-skills">
  <img src="https://img.shields.io/badge/engine-DiagramSpec-0A72EF" alt="Powered by DiagramSpec">
</p>

```bash
npx skills add georgelu-creator/diagram-skills --skill diagram-skills
```

<p align="center">
  <a href="examples/generated/enterprise-agent-office.svg">
    <img src="examples/generated/enterprise-agent-office.png" alt="跨设备云端 Agent 办公系统架构全景图">
  </a>
</p>

> **Copy this prompt**
>
> Use `$diagram-skills` to visualize our AI workspace for product and engineering leadership. Show users and Agents, the access gateway, memory and context capabilities, external tools, sources of truth, the end-to-end task flow, and the governing principles. Use Chinese-first labels, preserve established English technical terms, and deliver the finished visual with its editable source.

<p align="center"><sub>Powered by <strong>DiagramSpec</strong> — typed source · constrained layout · structural checks · SVG / HTML · optional PNG</sub></p>

## See what it makes

Seven different communication goals, seven different visual structures. Every example links to editable SVG, standalone HTML, source JSON and its hash-bound quality report.

<table>
  <tr>
    <td width="50%" valign="top">
      <a href="examples/generated/enterprise-agent-office.svg"><img src="examples/generated/enterprise-agent-office.png" alt="AI Agent workspace architecture"></a><br>
      <strong>AI Agent Workspace Architecture</strong><br>
      <sub>Help product and engineering leaders understand layers, boundaries, memory, tools and sources of truth.</sub><br>
      <a href="examples/enterprise-agent-office.json">Source</a> · <a href="examples/generated/enterprise-agent-office.html">Interactive HTML</a> · <a href="examples/generated/enterprise-agent-office.quality.json">Quality report</a>
    </td>
    <td width="50%" valign="top">
      <a href="examples/generated/agent-workflow.svg"><img src="examples/generated/agent-workflow.png" alt="Agent task execution workflow"></a><br>
      <strong>Multi-Agent Execution Loop</strong><br>
      <sub>Explain planning, context, missing-information recovery, tool use, verification and learning feedback.</sub><br>
      <a href="skills/diagram-skills/templates/agent-workflow.json">Source</a> · <a href="examples/generated/agent-workflow.html">Interactive HTML</a> · <a href="examples/generated/agent-workflow.quality.json">Quality report</a>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="examples/generated/data-flow.svg"><img src="examples/generated/data-flow.png" alt="Real-time intelligent data flow"></a><br>
      <strong>RAG &amp; Real-time Data Flow</strong><br>
      <sub>Trace data from sources through ingestion, governance, compute, storage, model serving and feedback.</sub><br>
      <a href="skills/diagram-skills/templates/data-flow.json">Source</a> · <a href="examples/generated/data-flow.html">Interactive HTML</a> · <a href="examples/generated/data-flow.quality.json">Quality report</a>
    </td>
    <td width="50%" valign="top">
      <a href="examples/generated/capability-map.svg"><img src="examples/generated/capability-map.png" alt="AI product capability map"></a><br>
      <strong>AI Product Capability Map</strong><br>
      <sub>Connect a north star to platform capabilities, governance and measurable product outcomes.</sub><br>
      <a href="skills/diagram-skills/templates/capability-map.json">Source</a> · <a href="examples/generated/capability-map.html">Interactive HTML</a> · <a href="examples/generated/capability-map.quality.json">Quality report</a>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="examples/generated/swimlane-release.svg"><img src="examples/generated/swimlane-release.png" alt="Software release swimlane"></a><br>
      <strong>Software Release Swimlane</strong><br>
      <sub>Make ownership, approvals, handoffs, evidence and rework visible across product, security and engineering.</sub><br>
      <a href="examples/swimlane-release.json">Source</a> · <a href="examples/generated/swimlane-release.html">Interactive HTML</a> · <a href="examples/generated/swimlane-release.quality.json">Quality report</a>
    </td>
    <td width="50%" valign="top">
      <a href="examples/generated/system-topology.svg"><img src="examples/generated/system-topology.png" alt="Highly available AI service topology"></a><br>
      <strong>Highly Available AI Service Topology</strong><br>
      <sub>Show edge, service, data and observability planes with synchronous and asynchronous paths.</sub><br>
      <a href="skills/diagram-skills/templates/system-topology.json">Source</a> · <a href="examples/generated/system-topology.html">Interactive HTML</a> · <a href="examples/generated/system-topology.quality.json">Quality report</a>
    </td>
  </tr>
  <tr>
    <td colspan="2" valign="top" align="center">
      <a href="examples/generated/user-flow.svg"><img src="examples/generated/user-flow.png" width="52%" alt="AI assistant first-activation user flow"></a><br>
      <strong>AI Assistant First-Activation User Flow</strong><br>
      <sub>Follow discovery, value understanding, readiness, scoped connection, first success, repeat use and an uncertainty recovery path.</sub><br>
      <a href="skills/diagram-skills/templates/user-flow.json">Source</a> · <a href="examples/generated/user-flow.html">Interactive HTML</a> · <a href="examples/generated/user-flow.quality.json">Quality report</a>
    </td>
  </tr>
</table>

The launch-gallery metadata lives in [`gallery/manifest.json`](gallery/manifest.json). The complete artifact index is in [`examples/README.md`](examples/README.md).

## Visual thinking, not diagram picking

You should not need to know the name of a diagram before asking for one. Tell the Agent:

1. **What must be explained?** A system, process, decision, strategy or change.
2. **Who needs to understand it?** Executives, customers, product, engineering or operations.
3. **What should they understand or decide?** The five-second narrative and the important boundaries.
4. **Which facts cannot be lost?** Actors, dependencies, exceptions, evidence and uncertainty.

The Skill turns that brief into an appropriate visual grammar and a maintainable DiagramSpec source instead of treating every request as the same generic flowchart.

## How it works

```text
Intent
  → Diagram Brief
  → visual grammar
  → typed DiagramSpec JSON
  → constrained layout and rendering
  → structural checks and visual inspection
  → SVG / HTML / optional PNG + source
```

1. **Fix the story.** Record the audience, scope, must-show facts, uncertainty and failure risks before layout.
2. **Choose the grammar.** Select one primary structure: architecture, workflow, data flow, capability map, user flow, topology, decision tree, roadmap, strategy map or process flow.
3. **Author the source.** Keep content and relationships in JSON so revisions do not begin from pixels.
4. **Render the result.** Produce reviewable SVG and standalone HTML; generate PNG only after `png-backend` finds a supported local rasterizer.
5. **Inspect and bind the evidence.** Check the full-size visual, answer type-specific review questions, then bind source, brief, inspected artifact and SHA-256 values into the quality receipt.

## Why DiagramSpec

**Built to survive AI revisions.** DiagramSpec is the technical engine beneath DiagramSkills.

- **Meaning is separate from pixels.** Nodes, sections, relationships, lanes and ranks remain editable source data.
- **Source and artifacts travel together.** JSON, SVG, HTML and quality diagnostics can be reviewed in version control.
- **Layout is constrained.** Layered graphs, swimlanes and enterprise boards follow reusable composition rules.
- **Checks are machine-readable.** The CLI catches structural references, unsafe links and several geometry problems before delivery.
- **The core is portable.** SVG and HTML rendering use the Python standard library; PNG is an optional system integration.
- **Mature tools are reused.** The optional Studio builds on React Flow, ELK, Monaco, Mermaid, Papa Parse, Zod and Yjs.

Mermaid remains excellent for diagrams-as-text. DiagramSkills is aimed at communication-ready explanatory visuals that also need a semantic source, a visual system, an editing surface and inspectable diagnostics.

## Same idea, stronger handoff

| A one-off generated picture | A DiagramSkills handoff |
|---|---|
| The layout is the only source of truth | The semantic JSON remains the source |
| Revisions often restart the picture | Agents revise content and rerender |
| Relationships may depend on visual guesswork | Relationships, lanes and groups are explicit |
| Usually one image format | SVG, standalone HTML, optional PNG and diagnostics |
| Hard to review in source control | Source and generated artifacts can be compared |

## Capability map

| Status | What belongs here |
|---|---|
| **Available** | 10 enforced visual grammars; graph and enterprise-board compositions; Chinese-first labels; five renderer themes; deterministic SVG/HTML; optional PNG; text-bound diagnostics; hash-bound review receipts |
| **Preview** | Local DiagramSkills Studio; native workspace editing; complete theme tokens; manual rank; swimlanes; strict Mermaid/CSV import; document-isolated offline and Yjs workspaces; overview-to-detail files |
| **Next** | Generated Gallery site; visual diff; portable multi-view export; browser bundle optimization |
| **Exploring** | diagrams.net interoperability; extension API; authenticated collaboration deployment |

“Available” means a current checked-in path exists. It does not mean every visual or review decision can be proven automatically.

## Quick start

### 1. Install the Agent Skill

```bash
npx skills add georgelu-creator/diagram-skills --skill diagram-skills
```

Or copy [`skills/diagram-skills`](skills/diagram-skills) into a compatible Agent's skills directory.

### 2. Ask for the outcome

```text
Use $diagram-skills to explain this repository to a new engineer.

Audience: engineering onboarding
Goal: understand entry points, services, data stores, external dependencies,
trust boundaries, failure paths and the ownership of each layer.

Choose the visual structure. Keep unknown facts explicit. Deliver the finished
SVG/HTML, the editable JSON source, and a PNG preview when the local renderer supports it.
```

### 3. Revise with the Agent

```text
Keep the same source and visual language. Add the audit boundary, split synchronous
and asynchronous paths, and create a second detail view for the retrieval pipeline.
```

<details>
<summary><strong>Use the DiagramSpec CLI directly</strong></summary>

```bash
python3 skills/diagram-skills/scripts/diagram_skills.py types
python3 skills/diagram-skills/scripts/diagram_skills.py png-backend
python3 skills/diagram-skills/scripts/diagram_skills.py new system-architecture --output work/architecture.json
python3 skills/diagram-skills/scripts/diagram_skills.py validate work/architecture.json --strict
python3 skills/diagram-skills/scripts/diagram_skills.py render work/architecture.json \
  --output-dir output --name architecture --strict
```

`render` always writes SVG, standalone HTML and a hash-bound quality receipt. A valid render remains `pending-review` until the Agent inspects the SVG or PNG and runs the documented `review` command with its reviewed Diagram Brief. PNG supports the backends reported by `png-backend`; if none is present, review and deliver the SVG directly.

See [`spec.md`](skills/diagram-skills/references/spec.md), [`prompt-system.md`](skills/diagram-skills/references/prompt-system.md) and [`quality-contract.md`](skills/diagram-skills/references/quality-contract.md).

</details>

## DiagramSkills Studio

Studio is an optional local inspection and editing surface. It is not required for the normal Agent-generated-diagram workflow.

```bash
cd editor
npm install
npm run dev
```

Use it locally for graph/workspace inspection, manual positioning, ranks, swimlanes, Mermaid preview, CSV import and overview-to-detail navigation. The current supported posture is **local/offline-first**. Networked Yjs synchronization uses conflict-safe workspace values and document-scoped room/storage ids, but remains experimental because the repository does not bundle an authenticated collaboration service; configure only a trusted endpoint with application-level authorization and retention controls.

See [`editor.md`](skills/diagram-skills/references/editor.md), [`imports.md`](skills/diagram-skills/references/imports.md) and [`workspaces.md`](skills/diagram-skills/references/workspaces.md).

## Project map

```text
DiagramSkills                     User-facing visual thinking brand
├── $diagram-skills               Installable Agent Skill id
├── examples + gallery manifest  Reusable visual outcomes and artifacts
├── DiagramSkills Studio          Optional local browser workbench
└── DiagramSpec                  JSON model, layout, renderer and diagnostics
```

The public repository, Agent Skill id and CLI entry point now share the same searchable name: `diagram-skills`. The former ABI Flow and VisualSkills names are retired; the completed rename is documented in [`MIGRATION.md`](MIGRATION.md).

## Scope

DiagramSkills currently focuses on explanatory diagrams: architecture, workflows, data movement, capability structures, topology, decisions, roadmaps, strategy and processes. It is not a quantitative charting library, BPMN execution engine, infinite whiteboard or unrestricted illustration generator.

## Roadmap

- [x] Agent Skill entry with reusable prompts, templates and enterprise-board composition
- [x] Ten starter diagram grammars and checked-in source/artifact examples
- [x] SVG and standalone HTML outputs; optional PNG export
- [x] Swimlanes, manual ranks, brand tokens and multi-view workspace files
- [x] Local Studio preview for JSON, Mermaid and CSV workflows
- [x] Enforce type contracts, schema parity, deterministic output, text bounds and hash-bound review receipts
- [x] Isolate the installed Skill from repository-only Studio/import workflows
- [ ] Add a generated Gallery site from [`gallery/manifest.json`](gallery/manifest.json)
- [ ] Add visual diff and portable multi-view export
- [ ] Publish an authenticated, isolated collaboration recipe
- [x] Unify the repository, Skill, CLI and Studio format under the DiagramSkills name

## Contributing

Contributions are welcome for visual grammars, layout quality, accessibility, tests, examples and documentation. Read [`CONTRIBUTING.md`](CONTRIBUTING.md), follow [`CHANGELOG.md`](CHANGELOG.md) for compatibility notes, and keep each change focused on one concern.

## License

MIT. See [`LICENSE`](LICENSE). Third-party inspiration and provenance are documented in [`NOTICE.md`](NOTICE.md).
