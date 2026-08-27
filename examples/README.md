# DiagramSkills example gallery

Every example keeps its checked-in JSON and generated artifacts together. The seven launch showcases are also indexed by [`../gallery/manifest.json`](../gallery/manifest.json); reusable starters live under [`../skills/diagram-skills/templates`](../skills/diagram-skills/templates).

| Example | Brief | Source | SVG | HTML | PNG | Quality |
|---|---|---|---|---|---|---|
| Cross-device Agent office | [Reviewed](briefs/enterprise-agent-office.brief.json) | [JSON](enterprise-agent-office.json) | [SVG](generated/enterprise-agent-office.svg) | [HTML](generated/enterprise-agent-office.html) | [PNG](generated/enterprise-agent-office.png) | [Report](generated/enterprise-agent-office.quality.json) |
| Agent workflow | [Reviewed](briefs/agent-workflow.brief.json) | [JSON](../skills/diagram-skills/templates/agent-workflow.json) | [SVG](generated/agent-workflow.svg) | [HTML](generated/agent-workflow.html) | [PNG](generated/agent-workflow.png) | [Report](generated/agent-workflow.quality.json) |
| Multi-Agent delivery control plane | — | [JSON](multi-agent-delivery-control-plane.json) | [SVG](generated/multi-agent-delivery-control-plane.svg) | [HTML](generated/multi-agent-delivery-control-plane.html) | [PNG](generated/multi-agent-delivery-control-plane.png) | [Report](generated/multi-agent-delivery-control-plane.quality.json) |
| Real-time AI data platform | — | [JSON](realtime-ai-data-platform.json) | [SVG](generated/realtime-ai-data-platform.svg) | [HTML](generated/realtime-ai-data-platform.html) | [PNG](generated/realtime-ai-data-platform.png) | [Report](generated/realtime-ai-data-platform.quality.json) |
| System architecture | — | [JSON](../skills/diagram-skills/templates/system-architecture.json) | [SVG](generated/system-architecture.svg) | [HTML](generated/system-architecture.html) | [PNG](generated/system-architecture.png) | [Report](generated/system-architecture.quality.json) |
| Data flow | [Reviewed](briefs/data-flow.brief.json) | [JSON](../skills/diagram-skills/templates/data-flow.json) | [SVG](generated/data-flow.svg) | [HTML](generated/data-flow.html) | [PNG](generated/data-flow.png) | [Report](generated/data-flow.quality.json) |
| Capability map | [Reviewed](briefs/capability-map.brief.json) | [JSON](../skills/diagram-skills/templates/capability-map.json) | [SVG](generated/capability-map.svg) | [HTML](generated/capability-map.html) | [PNG](generated/capability-map.png) | [Report](generated/capability-map.quality.json) |
| User flow | [Reviewed](briefs/user-flow.brief.json) | [JSON](../skills/diagram-skills/templates/user-flow.json) | [SVG](generated/user-flow.svg) | [HTML](generated/user-flow.html) | [PNG](generated/user-flow.png) | [Report](generated/user-flow.quality.json) |
| System topology | [Reviewed](briefs/system-topology.brief.json) | [JSON](../skills/diagram-skills/templates/system-topology.json) | [SVG](generated/system-topology.svg) | [HTML](generated/system-topology.html) | [PNG](generated/system-topology.png) | [Report](generated/system-topology.quality.json) |
| Swimlane release | [Reviewed](briefs/swimlane-release.brief.json) | [JSON](swimlane-release.json) | [SVG](generated/swimlane-release.svg) | [HTML](generated/swimlane-release.html) | [PNG](generated/swimlane-release.png) | [Report](generated/swimlane-release.quality.json) |

The Aurora example is a fictional dense graph retained as a layout and semantic-edge stress case.

[`enterprise-ai-workspace.json`](enterprise-ai-workspace.json) is the browser editor example. It contains three linked views: a native swimlane overview, an ELK-laid-out detail, and a source-preserving Mermaid quality gate. Validate it with:

```bash
python3 ../skills/diagram-skills/scripts/diagram_skills.py workspace-validate enterprise-ai-workspace.json --strict
```
