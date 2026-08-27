import { describe, expect, it } from "vitest";
import { parseWorkspace, removeDiagramNodes, serializeWorkspace, validateWorkspaceUpdate, type DiagramSpecView } from "./model";
import { sampleWorkspace } from "./sample";

describe("workspace schema", () => {
  it("round-trips the multi-view sample", () => {
    const result = parseWorkspace(serializeWorkspace(sampleWorkspace));
    expect(result.error).toBeUndefined();
    expect(result.workspace?.entry_view).toBe("overview");
    expect(result.workspace?.views).toHaveLength(3);
  });

  it("rejects a child view that does not exist", () => {
    const workspace = structuredClone(sampleWorkspace);
    const overview = workspace.views[0];
    if (overview.format === "diagramspec") overview.nodes[0].child_view = "missing-view";
    expect(parseWorkspace(JSON.stringify(workspace)).error).toContain("Unknown child view");
  });

  it("rejects duplicate node, group, and lane identifiers", () => {
    const duplicateNode = structuredClone(sampleWorkspace);
    const nodeView = duplicateNode.views[0] as DiagramSpecView;
    nodeView.nodes.push({ ...nodeView.nodes[0] });
    expect(parseWorkspace(JSON.stringify(duplicateNode)).error).toContain("Duplicate node id");

    const duplicateGroup = structuredClone(sampleWorkspace);
    const groupView = duplicateGroup.views[0] as DiagramSpecView;
    groupView.groups = [{ id: "domain", label: "One" }, { id: "domain", label: "Two" }];
    groupView.nodes[0].group = "domain";
    expect(parseWorkspace(JSON.stringify(duplicateGroup)).error).toContain("Duplicate group id");

    const duplicateLane = structuredClone(sampleWorkspace);
    const laneView = duplicateLane.views[0] as DiagramSpecView;
    laneView.lanes.push({ ...laneView.lanes[0] });
    expect(parseWorkspace(JSON.stringify(duplicateLane)).error).toContain("Duplicate lane id");
  });

  it("rejects unknown or empty boundaries", () => {
    const unknownGroup = structuredClone(sampleWorkspace);
    (unknownGroup.views[0] as DiagramSpecView).nodes[0].group = "missing";
    expect(parseWorkspace(JSON.stringify(unknownGroup)).error).toContain("Unknown group");

    const emptyLane = structuredClone(sampleWorkspace);
    (emptyLane.views[0] as DiagramSpecView).lanes.push({ id: "empty", label: "Empty", order: 9 });
    expect(parseWorkspace(JSON.stringify(emptyLane)).error).toContain("Lane has no nodes");
  });

  it("rejects unsafe links and unmarked cycles but permits feedback", () => {
    const unsafe = structuredClone(sampleWorkspace);
    (unsafe.views[0] as DiagramSpecView).nodes[0].link = "javascript:alert(1)";
    expect(parseWorkspace(JSON.stringify(unsafe)).error).toContain("Link must be an http(s), mailto, or non-empty fragment URL");

    const cyclic = structuredClone(sampleWorkspace);
    (cyclic.views[0] as DiagramSpecView).edges.push({ source: "brief", target: "intent", kind: "primary" });
    expect(parseWorkspace(JSON.stringify(cyclic)).error).toContain("Non-feedback edges contain a cycle");
    expect(parseWorkspace(serializeWorkspace(sampleWorkspace)).error).toBeUndefined();
  });

  it("enforces the same diagram-type grammar used by the CLI", () => {
    const architecture = structuredClone(sampleWorkspace);
    const architectureView = architecture.views[0] as DiagramSpecView;
    architectureView.nodes = [{ id: "only", label: "Only", type: "process" }];
    architectureView.edges = [];
    architectureView.groups = [];
    architectureView.lanes = [];
    expect(parseWorkspace(JSON.stringify(architecture)).error).toMatch(/requires (node type|at least)/);

    const decision = structuredClone(sampleWorkspace);
    const decisionView = decision.views[0] as DiagramSpecView;
    decisionView.diagram_type = "decision-tree";
    decisionView.direction = "TB";
    decisionView.groups = [];
    decisionView.lanes = [];
    decisionView.nodes = [
      { id: "gate", label: "Gate", type: "decision" },
      { id: "yes", label: "Yes", type: "process" },
      { id: "no", label: "No", type: "process" },
    ];
    decisionView.edges = [
      { source: "gate", target: "yes", kind: "primary" },
      { source: "gate", target: "no", kind: "primary" },
    ];
    expect(parseWorkspace(JSON.stringify(decision)).error).toContain("explicit success and error branches");
  });

  it("returns an explicit failed update instead of accepting invalid workspace state", () => {
    const invalid = structuredClone(sampleWorkspace);
    (invalid.views[0] as DiagramSpecView).nodes[0].lane = "missing";
    const result = validateWorkspaceUpdate(invalid);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toContain("Unknown lane");
  });

  it("blocks deletion of the final node or the final member of a boundary", () => {
    const oneNode: DiagramSpecView = {
      id: "single",
      format: "diagramspec",
      title: "Single",
      diagram_type: "process-flow",
      direction: "LR",
      theme: "paper",
      layout_mode: "auto",
      groups: [],
      lanes: [],
      nodes: [{ id: "only", label: "Only", type: "process" }],
      edges: [],
    };
    expect(removeDiagramNodes(oneNode, ["only"])).toMatchObject({ ok: false });
    const overview = sampleWorkspace.views[0] as DiagramSpecView;
    expect(removeDiagramNodes(overview, ["intent", "brief"])).toMatchObject({ ok: false, error: expect.stringContaining("lane empty") });
  });
});
