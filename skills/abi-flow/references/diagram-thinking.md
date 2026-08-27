# Diagram thinking contract

Use this reference before authoring DiagramSpec nodes, cards, or edges from prose. The output is a concise, reviewable **Diagram Brief**, not private chain-of-thought. Its purpose is to prevent a geometrically correct diagram from telling the wrong story.

## Content pass

1. **Frame the question.** Write one decision or understanding the diagram should support. Prefer a testable goal over “show the system.”
2. **Name the audience and scope.** State who reads it, what is inside, and what is intentionally outside. Audience controls vocabulary and density.
3. **Write one narrative sentence.** Capture what should remain after a five-second scan. Split unrelated stories or use a linked detail view.
4. **Prioritize supplied facts.** Separate `must_show`, `emphasize`, and `deemphasize`. Record missing facts as `uncertainties`; record only low-risk layout interpretations as `assumptions`.
5. **Model meaningful relationships.** Sequence, control, data, ownership, hierarchy, dependency, success/error, async, feedback, or source-of-truth links must be supported by the source.
6. **Select type and composition.** Use one diagram type. Use `graph` for smaller relationship structures and `board` for layered overviews with 20–45 concise concepts.
7. **Identify content risks.** State how this diagram could mislead—for example, implying realtime guarantees, inventing a trust boundary, or confusing memory with durable storage.
8. **Define review questions.** Tailor at least three questions from the selected profile in `diagram-thinking-profiles.json`.

## Sidecar format

```json
{
  "goal": "What understanding or decision should this support?",
  "audience": "Who is reading it?",
  "narrative": "One-sentence story of the diagram",
  "scope": "What is inside and outside?",
  "diagram_type": "system-architecture",
  "composition": "board",
  "must_show": ["facts that cannot disappear"],
  "emphasize": ["elements that deserve visual priority"],
  "deemphasize": ["details to group or move to drill-down"],
  "relationships": ["meaningful relationship semantics"],
  "uncertainties": ["facts not supplied"],
  "assumptions": ["explicit low-risk interpretations"],
  "density": "high",
  "content_risks": ["ways the diagram could mislead"],
  "quality_questions": ["questions answered after rendering"]
}
```

Validate before authoring source:

```bash
python3 scripts/diagram_brief.py work/example.brief.json --strict
```

## Closed-loop review

After rendering and inspecting the SVG or PNG, append one concrete, distinct answer for every profile-grounded `quality_questions` entry:

```json
"review_answers": [
  {
    "question": "Can the viewer identify the main story in five seconds?",
    "status": "pass",
    "evidence": "The core capability band is the largest green section and the primary route crosses it."
  }
]
```

Then run:

```bash
python3 scripts/diagram_brief.py work/example.brief.json --spec work/example.json --strict --reviewed
```

`--reviewed` fails when any question is missing, failed, not reviewed, or lacks evidence. `--spec` also blocks a mismatch between the brief's diagram type/composition and the rendered source. Fix the brief, source, or renderer and repeat; do not edit generated SVG by hand.

Finally, bind the reviewed brief to the exact source and inspected artifact with `abi_flow.py review`; see [quality-contract.md](quality-contract.md).

## Type-specific distinctions

- **System architecture:** responsibility layers, boundaries, integrations, sources of truth, and one end-to-end path. Distinguish memory/context from durable artifacts and logical architecture from topology.
- **Agent workflow:** trigger, objective, context, planning/routing, tool side effects, policy/human gates, verification, retry, and memory write-back.
- **Data flow:** provenance, transformations, stores/indexes/caches, timing semantics, consumers, and trust crossings. Do not substitute service topology for lineage.
- **Capability map:** durable domains, foundations, differentiated value, and outcomes. Do not turn it into a backlog or imply sequence with decorative arrows.
- **User flow:** user goal, entry, action, system response, decisions, recovery, and success/exit.
- **System topology:** deployed units, zones, runtime dependencies, traffic, replication/failover, and observability—only when supplied.
- **Decision tree:** ordered questions, available evidence, mutually understandable branches, unknown states, and terminal/escalation outcomes.
- **Roadmap:** outcomes, phases, dependencies, readiness gates, parallel work, and uncertainty. Never invent dates or certainty.
- **Strategy map:** north star, pillars, initiatives, enablers, outcomes, and supplied metrics. Treat causal links as hypotheses unless proven.
- **Process flow:** trigger, ownership, actions, handoffs, artifacts, decisions, exceptions/rework, and end state.

The machine-readable profiles are the source of truth for complete questions, distinctions, failure modes, and review seeds.
