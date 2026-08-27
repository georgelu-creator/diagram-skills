<p align="center">
  <img src="skills/abi-flow/assets/icon.svg" width="88" alt="VisualSkills mark">
</p>

<h1 align="center">VisualSkills</h1>

<p align="center"><strong>Beautiful visual thinking skills for AI agents.</strong></p>

<p align="center">
  Turn ideas, systems and complex information into visuals people can understand, edit and trust.<br>
  把复杂系统、流程与策略，变成真正能看懂、能修改、能交付的图。
</p>

<p align="center">
  Architecture · Workflows · Data Flows · Capability Maps · Topology · Decisions · Strategy
</p>

<p align="center">
  <a href="https://github.com/georgelu-creator/abi-flow/actions/workflows/ci.yml"><img src="https://github.com/georgelu-creator/abi-flow/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-171717" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Agent%20Skill-abi--flow-4F46E5" alt="Agent Skill abi-flow">
  <img src="https://img.shields.io/badge/engine-DiagramSpec-0A72EF" alt="Powered by DiagramSpec">
</p>

```bash
npx skills add georgelu-creator/abi-flow --skill abi-flow
```

<p align="center">
  <a href="examples/generated/enterprise-agent-office.svg">
    <img src="examples/generated/enterprise-agent-office.png" alt="跨设备云端 Agent 办公系统架构全景图">
  </a>
</p>

> **Copy this prompt**
>
> Use `$abi-flow` to visualize our AI workspace for product and engineering leadership. Show users and Agents, the access gateway, memory and context capabilities, external tools, sources of truth, the end-to-end task flow, and the governing principles. Use Chinese-first labels, preserve established English technical terms, and deliver the finished visual with its editable source.

<p align="center"><sub>Powered by <strong>DiagramSpec</strong> — typed source · constrained layout · structural checks · SVG / HTML · optional PNG</sub></p>

## See what it makes

Six different communication goals, six different visual structures. Every example links to editable SVG, standalone HTML, source JSON and its checked-in quality report.

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
      <a href="skills/abi-flow/templates/agent-workflow.json">Source</a> · <a href="examples/generated/agent-workflow.html">Interactive HTML</a> · <a href="examples/generated/agent-workflow.quality.json">Quality report</a>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="examples/generated/data-flow.svg"><img src="examples/generated/data-flow.png" alt="Real-time intelligent data flow"></a><br>
      <strong>RAG &amp; Real-time Data Flow</strong><br>
      <sub>Trace data from sources through ingestion, governance, compute, storage, model serving and feedback.</sub><br>
      <a href="skills/abi-flow/templates/data-flow.json">Source</a> · <a href="examples/generated/data-flow.html">Interactive HTML</a> · <a href="examples/generated/data-flow.quality.json">Quality report</a>
    </td>
    <td width="50%" valign="top">
      <a href="examples/generated/capability-map.svg"><img src="examples/generated/capability-map.png" alt="AI product capability map"></a><br>
      <strong>AI Product Capability Map</strong><br>
      <sub>Connect a north star to platform capabilities, governance and measurable product outcomes.</sub><br>
      <a href="skills/abi-flow/templates/capability-map.json">Source</a> · <a href="examples/generated/capability-map.html">Interactive HTML</a> · <a href="examples/generated/capability-map.quality.json">Quality report</a>
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
      <a href="skills/abi-flow/templates/system-topology.json">Source</a> · <a href="examples/generated/system-topology.html">Interactive HTML</a> · <a href="examples/generated/system-topology.quality.json">Quality report</a>
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
4. **Render the result.** Produce reviewable SVG and standalone HTML; generate PNG when `rsvg-convert` is available.
5. **Inspect and revise.** Treat automated reports as diagnostics, then check the full-size visual before delivery.

## Why DiagramSpec

**Built to survive AI revisions.** DiagramSpec is the technical engine beneath VisualSkills.

- **Meaning is separate from pixels.** Nodes, sections, relationships, lanes and ranks remain editable source data.
- **Source and artifacts travel together.** JSON, SVG, HTML and quality diagnostics can be reviewed in version control.
- **Layout is constrained.** Layered graphs, swimlanes and enterprise boards follow reusable composition rules.
- **Checks are machine-readable.** The CLI catches structural references, unsafe links and several geometry problems before delivery.
- **The core is portable.** SVG and HTML rendering use the Python standard library; PNG is an optional system integration.
- **Mature tools are reused.** The optional Studio builds on React Flow, ELK, Monaco, Mermaid, Papa Parse, Zod and Yjs.

Mermaid remains excellent for diagrams-as-text. VisualSkills is aimed at communication-ready explanatory visuals that also need a semantic source, a visual system, an editing surface and inspectable diagnostics.

## Same idea, stronger handoff

| A one-off generated picture | A VisualSkills handoff |
|---|---|
| The layout is the only source of truth | The semantic JSON remains the source |
| Revisions often restart the picture | Agents revise content and rerender |
| Relationships may depend on visual guesswork | Relationships, lanes and groups are explicit |
| Usually one image format | SVG, standalone HTML, optional PNG and diagnostics |
| Hard to review in source control | Source and generated artifacts can be compared |

## Capability map

| Status | What belongs here |
|---|---|
| **Available** | 10 starter visual grammars; graph and enterprise-board compositions; Chinese-first labels; five renderer themes; SVG/HTML and optional PNG; checked-in examples and templates |
| **Preview** | Local VisualSkills Studio; native workspace editing; manual rank; swimlanes; Mermaid source views; CSV import; overview-to-detail files |
| **Next** | Stronger type-specific contracts; text-bound checks; consistent browser/CLI validation; theme parity; installable editor/import workflow; gallery automation |
| **Exploring** | Diagram diff; portable multi-view export; diagrams.net interoperability; extension API; authenticated and isolated collaboration deployment |

“Available” means a current checked-in path exists. It does not mean every visual or review decision can be proven automatically.

## Quick start

### 1. Install the Agent Skill

```bash
npx skills add georgelu-creator/abi-flow --skill abi-flow
```

Or copy [`skills/abi-flow`](skills/abi-flow) into a compatible Agent's skills directory.

### 2. Ask for the outcome

```text
Use $abi-flow to explain this repository to a new engineer.

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
python3 skills/abi-flow/scripts/abi_flow.py types
python3 skills/abi-flow/scripts/abi_flow.py new system-architecture --output work/architecture.json
python3 skills/abi-flow/scripts/abi_flow.py validate work/architecture.json --strict
python3 skills/abi-flow/scripts/abi_flow.py render work/architecture.json \
  --output-dir output --name architecture --png --strict
```

`render` always targets SVG, standalone HTML and a quality report. PNG requires `rsvg-convert`; if it is not installed, use the SVG directly or install a compatible SVG rasterizer.

See [`spec.md`](skills/abi-flow/references/spec.md), [`prompt-system.md`](skills/abi-flow/references/prompt-system.md) and [`quality-contract.md`](skills/abi-flow/references/quality-contract.md).

</details>

## VisualSkills Studio

Studio is an optional local inspection and editing surface. It is not required for the normal Agent-generated-diagram workflow.

```bash
cd editor
npm install
npm run dev
```

Use it locally for graph/workspace inspection, manual positioning, ranks, swimlanes, Mermaid preview, CSV import and overview-to-detail navigation. The current supported posture is **local/offline-first**. Networked Yjs synchronization is experimental and should not be enabled for sensitive or multi-tenant workspaces until authenticated room isolation and conflict-safe document updates are implemented.

See [`editor.md`](skills/abi-flow/references/editor.md), [`imports.md`](skills/abi-flow/references/imports.md) and [`workspaces.md`](skills/abi-flow/references/workspaces.md).

## Project map

```text
VisualSkills                     User-facing visual thinking brand
├── $abi-flow                    Current compatible Agent Skill id
├── examples + gallery manifest  Reusable visual outcomes and artifacts
├── VisualSkills Studio          Optional local browser workbench
└── DiagramSpec                  JSON model, layout, renderer and diagnostics
```

The repository and public Skill id remain `abi-flow` today. `VisualSpec` was an earlier product name. No repository rename, schema change or CLI break is implied by this presentation update; see [`MIGRATION.md`](MIGRATION.md).

## Scope

VisualSkills currently focuses on explanatory diagrams: architecture, workflows, data movement, capability structures, topology, decisions, roadmaps, strategy and processes. It is not a quantitative charting library, BPMN execution engine, infinite whiteboard or unrestricted illustration generator.

## Roadmap

- [x] Agent Skill entry with reusable prompts, templates and enterprise-board composition
- [x] Ten starter diagram grammars and checked-in source/artifact examples
- [x] SVG and standalone HTML outputs; optional PNG export
- [x] Swimlanes, manual ranks, brand tokens and multi-view workspace files
- [x] Local Studio preview for JSON, Mermaid and CSV workflows
- [ ] Close the published validation and packaging gaps documented in [`AUDIT.md`](AUDIT.md)
- [ ] Add a generated Gallery site from [`gallery/manifest.json`](gallery/manifest.json)
- [ ] Add visual diff and portable multi-view export
- [ ] Publish an authenticated, isolated collaboration recipe
- [ ] Prepare a versioned migration preview before any repository rename

## Contributing

Contributions are welcome for visual grammars, layout quality, accessibility, tests, examples and documentation. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) and keep each change focused on one concern.

## License

MIT. See [`LICENSE`](LICENSE). Third-party inspiration and provenance are documented in [`NOTICE.md`](NOTICE.md).
