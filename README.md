# ABI Flow

ABI Flow is a production-oriented Agent Skill that turns structured process descriptions into polished SVG flowcharts, responsive interactive HTML, quality reports, and optional PNG previews.

![Aurora Deep-Space Resilience Network](examples/generated/aurora-resilience-network.svg)

The hero example is a deliberately fictional deep-space autonomy network. It contains no corporate workflow, customer data, or private architecture.

## ABI Flow

ABI Flow combines the strongest ideas from several diagramming traditions without copying or bundling their code:

- Mermaid-style text-first, version-controllable sources
- D2/Graphviz-style deterministic layout
- ELK/React Flow-style routing and interactive navigation concepts
- Excalidraw-style editable vector output
- fireworks-tech-graph-style semantic arrows, geometry checks, and visual review gates
- Spectrum showcase theme with a white canvas, pastel semantic nodes, and six stage colors

The renderer itself uses only the Python standard library. PNG export is optional and uses `rsvg-convert` when available.

### Install as an Agent Skill

```bash
npx skills add georgelu-creator/abi-flow --skill abi-flow
```

Or copy `skills/abi-flow` into a compatible agent's skills directory.

### Render the included example

```bash
python3 skills/abi-flow/scripts/abi_flow.py render \
  examples/aurora-resilience-network.json \
  --output-dir examples/generated \
  --name aurora-resilience-network \
  --png \
  --strict
```

Outputs:

- `aurora-resilience-network.svg` — editable vector diagram
- `aurora-resilience-network.html` — standalone, dependency-free viewer with pan/zoom, themes and downloads
- `aurora-resilience-network.png` — 1920 px preview when `rsvg-convert` is available
- `aurora-resilience-network.quality.json` — machine-readable validation evidence

### Source format

```json
{
  "title": "Release gate",
  "direction": "LR",
  "theme": "paper",
  "nodes": [
    {"id": "change", "label": "Candidate", "type": "input"},
    {"id": "test", "label": "Regression", "type": "process"},
    {"id": "release", "label": "Release", "type": "process"}
  ],
  "edges": [
    {"source": "change", "target": "test", "kind": "primary"},
    {"source": "test", "target": "release", "kind": "success"},
    {"source": "release", "target": "change", "label": "next cycle", "kind": "feedback"}
  ]
}
```

See [`skills/abi-flow/references/spec.md`](skills/abi-flow/references/spec.md) for the complete format and [`quality-contract.md`](skills/abi-flow/references/quality-contract.md) for delivery requirements.

## Design boundaries

ABI Flow is optimized for process flows, feedback loops, architecture narratives and linked technical diagrams. It is not a quantitative charting library, general whiteboard, BPMN engine, or unrestricted illustration generator.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/abi-flow
python3 skills/abi-flow/scripts/abi_flow.py validate examples/aurora-resilience-network.json --strict
```

## License

MIT. See [LICENSE](LICENSE). Conceptual inspirations and project links are documented in [NOTICE.md](NOTICE.md).

The release evidence and known limitations are documented in [AUDIT.md](AUDIT.md).
