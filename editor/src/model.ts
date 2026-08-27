import { z } from "zod";

export const diagramTypes = [
  "system-architecture",
  "agent-workflow",
  "data-flow",
  "capability-map",
  "user-flow",
  "system-topology",
  "decision-tree",
  "roadmap",
  "strategy-map",
  "process-flow",
] as const;

export const themeNames = ["paper", "notion", "spectrum", "blueprint", "terminal"] as const;
export const nodeTypes = ["process", "decision", "input", "document", "database", "agent", "external"] as const;
export const edgeKinds = ["primary", "control", "feedback", "async", "success", "error"] as const;

const id = z.string().regex(/^[A-Za-z0-9_.-]+$/);
const color = z.string().regex(/^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$/);

export const BrandSchema = z.object({
  name: z.string().min(1).optional(),
  primary: color.optional(),
  accent: color.optional(),
  page: color.optional(),
  surface: color.optional(),
  ink: color.optional(),
  muted: color.optional(),
  hair: color.optional(),
  group: color.optional(),
  group_stroke: color.optional(),
}).strict();

export const DiagramNodeSchema = z.object({
  id,
  label: z.string().min(1),
  subtitle: z.string().optional(),
  type: z.enum(nodeTypes).default("process"),
  group: id.optional(),
  lane: id.optional(),
  rank: z.number().int().nonnegative().optional(),
  child_view: id.optional(),
  link: z.string().optional(),
  position: z.object({ x: z.number(), y: z.number() }).optional(),
}).strict();

export const DiagramEdgeSchema = z.object({
  id: id.optional(),
  source: id,
  target: id,
  label: z.string().optional(),
  kind: z.enum(edgeKinds).default("primary"),
}).strict();

export const DiagramSchema = z.object({
  title: z.string().min(1),
  subtitle: z.string().optional(),
  diagram_type: z.enum(diagramTypes).default("process-flow"),
  direction: z.enum(["LR", "TB"]).default("LR"),
  theme: z.enum(themeNames).default("paper"),
  brand: BrandSchema.optional(),
  layout_mode: z.enum(["auto", "ranked", "manual"]).default("auto"),
  legend: z.boolean().optional(),
  groups: z.array(z.object({ id, label: z.string().min(1) }).strict()).default([]),
  lanes: z.array(z.object({ id, label: z.string().min(1), order: z.number().int().nonnegative().optional() }).strict()).default([]),
  nodes: z.array(DiagramNodeSchema).min(1),
  edges: z.array(DiagramEdgeSchema).default([]),
}).strict();

export const DiagramSpecViewSchema = DiagramSchema.extend({
  id,
  format: z.literal("diagramspec"),
});

export const MermaidViewSchema = z.object({
  id,
  format: z.literal("mermaid"),
  title: z.string().min(1),
  source: z.string().min(1),
}).strict();

export const WorkspaceSchema = z.object({
  "$schema": z.string().optional(),
  schema_version: z.literal("3.0"),
  title: z.string().min(1),
  entry_view: id,
  views: z.array(z.discriminatedUnion("format", [DiagramSpecViewSchema, MermaidViewSchema])).min(1),
}).strict().superRefine((workspace, context) => {
  const ids = new Set<string>();
  workspace.views.forEach((view, index) => {
    if (ids.has(view.id)) {
      context.addIssue({ code: "custom", path: ["views", index, "id"], message: `Duplicate view id: ${view.id}` });
    }
    ids.add(view.id);
  });
  if (!ids.has(workspace.entry_view)) {
    context.addIssue({ code: "custom", path: ["entry_view"], message: "entry_view must reference an existing view" });
  }
  workspace.views.forEach((view, viewIndex) => {
    if (view.format !== "diagramspec") return;
    const nodeIds = collectUniqueIds(view.nodes, "node", viewIndex, context);
    const groupIds = collectUniqueIds(view.groups, "group", viewIndex, context);
    const laneIds = collectUniqueIds(view.lanes, "lane", viewIndex, context);
    collectUniqueEdgeIds(view.edges, viewIndex, context);
    const usedGroups = new Set<string>();
    const usedLanes = new Set<string>();
    view.nodes.forEach((node, nodeIndex) => {
      if (view.lanes.length && !node.lane) {
        context.addIssue({ code: "custom", path: ["views", viewIndex, "nodes", nodeIndex, "lane"], message: "Every node must be assigned when swimlanes exist" });
      }
      if (node.lane && !laneIds.has(node.lane)) {
        context.addIssue({ code: "custom", path: ["views", viewIndex, "nodes", nodeIndex, "lane"], message: `Unknown lane: ${node.lane}` });
      }
      if (node.lane) usedLanes.add(node.lane);
      if (node.group && !groupIds.has(node.group)) {
        context.addIssue({ code: "custom", path: ["views", viewIndex, "nodes", nodeIndex, "group"], message: `Unknown group: ${node.group}` });
      }
      if (node.group) usedGroups.add(node.group);
      if (node.child_view && !ids.has(node.child_view)) {
        context.addIssue({ code: "custom", path: ["views", viewIndex, "nodes", nodeIndex, "child_view"], message: `Unknown child view: ${node.child_view}` });
      }
      if (node.link && !isSafeLink(node.link)) {
        context.addIssue({ code: "custom", path: ["views", viewIndex, "nodes", nodeIndex, "link"], message: "Link must be an http(s), mailto, or non-empty fragment URL" });
      }
    });
    view.groups.forEach((group, groupIndex) => {
      if (!usedGroups.has(group.id)) {
        context.addIssue({ code: "custom", path: ["views", viewIndex, "groups", groupIndex], message: `Group has no nodes: ${group.id}` });
      }
    });
    view.lanes.forEach((lane, laneIndex) => {
      if (!usedLanes.has(lane.id)) {
        context.addIssue({ code: "custom", path: ["views", viewIndex, "lanes", laneIndex], message: `Lane has no nodes: ${lane.id}` });
      }
    });
    view.edges.forEach((edge, edgeIndex) => {
      if (!nodeIds.has(edge.source) || !nodeIds.has(edge.target)) {
        context.addIssue({ code: "custom", path: ["views", viewIndex, "edges", edgeIndex], message: `Unknown edge endpoint: ${edge.source} → ${edge.target}` });
      }
    });
    const cycle = findNonFeedbackCycle(view);
    if (cycle.length) {
      context.addIssue({ code: "custom", path: ["views", viewIndex, "edges"], message: `Non-feedback edges contain a cycle involving: ${cycle.join(", ")}` });
    }
    validateDiagramContract(view, viewIndex, context);
  });
});

type RefinementContext = Parameters<NonNullable<Parameters<typeof WorkspaceSchema.superRefine>[0]>>[1];

function validateDiagramContract(
  view: z.infer<typeof DiagramSpecViewSchema>,
  viewIndex: number,
  context: RefinementContext,
): void {
  const expectedDirection: Partial<Record<(typeof diagramTypes)[number], "LR" | "TB">> = {
    "agent-workflow": "LR",
    "data-flow": "LR",
    "capability-map": "TB",
    "user-flow": "TB",
    "system-topology": "LR",
    "decision-tree": "TB",
    roadmap: "LR",
    "strategy-map": "TB",
  };
  const requiredTypes: Record<(typeof diagramTypes)[number], Array<(typeof nodeTypes)[number]>> = {
    "system-architecture": ["process", "database"],
    "agent-workflow": ["input", "agent"],
    "data-flow": ["external", "database"],
    "capability-map": ["process"],
    "user-flow": ["external", "decision"],
    "system-topology": ["external", "database"],
    "decision-tree": ["decision"],
    roadmap: [],
    "strategy-map": ["process", "document"],
    "process-flow": ["process"],
  };
  const minimumNodes: Record<(typeof diagramTypes)[number], number> = {
    "system-architecture": 4, "agent-workflow": 4, "data-flow": 4, "capability-map": 4,
    "user-flow": 4, "system-topology": 4, "decision-tree": 3, roadmap: 2,
    "strategy-map": 4, "process-flow": 2,
  };
  const minimumEdges: Record<(typeof diagramTypes)[number], number> = {
    "system-architecture": 3, "agent-workflow": 3, "data-flow": 3, "capability-map": 3,
    "user-flow": 3, "system-topology": 3, "decision-tree": 2, roadmap: 1,
    "strategy-map": 3, "process-flow": 1,
  };
  const minimumGroups: Partial<Record<(typeof diagramTypes)[number], number>> = {
    "capability-map": 2, "system-topology": 2, roadmap: 2, "strategy-map": 3,
  };
  const issue = (field: string, message: string) => context.addIssue({
    code: "custom",
    path: ["views", viewIndex, field],
    message,
  });
  const expected = expectedDirection[view.diagram_type];
  if (expected && view.direction !== expected) issue("direction", `${view.diagram_type} requires direction ${expected}`);
  const presentTypes = new Set(view.nodes.map((node) => node.type));
  const missingTypes = requiredTypes[view.diagram_type].filter((type) => !presentTypes.has(type));
  if (missingTypes.length) issue("nodes", `${view.diagram_type} requires node type(s): ${missingTypes.join(", ")}`);
  if (view.nodes.length < minimumNodes[view.diagram_type]) issue("nodes", `${view.diagram_type} requires at least ${minimumNodes[view.diagram_type]} nodes`);
  if (view.edges.length < minimumEdges[view.diagram_type]) issue("edges", `${view.diagram_type} requires at least ${minimumEdges[view.diagram_type]} edges`);
  const groupMinimum = minimumGroups[view.diagram_type] ?? 0;
  if (view.groups.length < groupMinimum) issue("groups", `${view.diagram_type} requires at least ${groupMinimum} meaningful groups/phases`);
  const edgeKindsPresent = new Set(view.edges.map((edge) => edge.kind));
  if (view.diagram_type === "decision-tree") {
    const branching = view.nodes.some((node) => node.type === "decision" &&
      view.edges.some((edge) => edge.source === node.id && edge.kind === "success") &&
      view.edges.some((edge) => edge.source === node.id && edge.kind === "error"));
    if (!branching) issue("edges", "decision-tree requires a decision with explicit success and error branches");
  }
  if (view.diagram_type === "roadmap") {
    if (view.nodes.some((node) => !node.group)) issue("nodes", "every roadmap outcome must belong to a phase group");
    if (edgeKindsPresent.has("feedback") || edgeKindsPresent.has("error")) issue("edges", "roadmap cannot use feedback or error edges as chronology");
  }
  if (view.diagram_type === "capability-map" && edgeKindsPresent.has("feedback")) issue("edges", "capability-map cannot use feedback edges that imply execution sequence");
  if (view.diagram_type === "agent-workflow" && !["control", "success", "feedback"].some((kind) => edgeKindsPresent.has(kind as (typeof edgeKinds)[number]))) {
    issue("edges", "agent-workflow requires control, outcome, or feedback edge semantics");
  }
  if (view.diagram_type === "data-flow" && !view.nodes.some((node) => node.type === "process" || node.type === "agent")) {
    issue("nodes", "data-flow requires a process or agent transformation");
  }
}

function collectUniqueIds(
  items: Array<{ id: string }>,
  kind: "node" | "group" | "lane",
  viewIndex: number,
  context: RefinementContext,
): Set<string> {
  const ids = new Set<string>();
  items.forEach((item, index) => {
    if (ids.has(item.id)) {
      context.addIssue({
        code: "custom",
        path: ["views", viewIndex, `${kind}s`, index, "id"],
        message: `Duplicate ${kind} id: ${item.id}`,
      });
    }
    ids.add(item.id);
  });
  return ids;
}

function collectUniqueEdgeIds(
  edges: Array<{ id?: string }>,
  viewIndex: number,
  context: RefinementContext,
): void {
  const ids = new Set<string>();
  edges.forEach((edge, index) => {
    if (!edge.id) return;
    if (ids.has(edge.id)) {
      context.addIssue({ code: "custom", path: ["views", viewIndex, "edges", index, "id"], message: `Duplicate edge id: ${edge.id}` });
    }
    ids.add(edge.id);
  });
}

export function isSafeLink(link: string): boolean {
  if (link.startsWith("#")) return link.length > 1;
  if (/^mailto:[^\s@]+@?[^\s]*$/i.test(link)) return link.slice("mailto:".length).length > 0;
  if (!/^https?:\/\//i.test(link)) return false;
  try {
    const parsed = new URL(link);
    return (parsed.protocol === "http:" || parsed.protocol === "https:") && Boolean(parsed.host);
  } catch {
    return false;
  }
}

function findNonFeedbackCycle(view: DiagramSpecView): string[] {
  const ids = [...new Set(view.nodes.map((node) => node.id))];
  const nodeIds = new Set(ids);
  const indegree = new Map(ids.map((nodeId) => [nodeId, 0]));
  const outgoing = new Map(ids.map((nodeId) => [nodeId, [] as string[]]));
  view.edges.filter((edge) => edge.kind !== "feedback" && nodeIds.has(edge.source) && nodeIds.has(edge.target)).forEach((edge) => {
    outgoing.get(edge.source)?.push(edge.target);
    indegree.set(edge.target, (indegree.get(edge.target) ?? 0) + 1);
  });
  const queue = ids.filter((nodeId) => indegree.get(nodeId) === 0);
  const visited = new Set<string>();
  while (queue.length) {
    const current = queue.shift()!;
    visited.add(current);
    for (const target of outgoing.get(current) ?? []) {
      indegree.set(target, (indegree.get(target) ?? 1) - 1);
      if (indegree.get(target) === 0) queue.push(target);
    }
  }
  return ids.filter((nodeId) => !visited.has(nodeId));
}

export type Brand = z.infer<typeof BrandSchema>;
export type DiagramNode = z.infer<typeof DiagramNodeSchema>;
export type DiagramEdge = z.infer<typeof DiagramEdgeSchema>;
export type DiagramSpecView = z.infer<typeof DiagramSpecViewSchema>;
export type MermaidView = z.infer<typeof MermaidViewSchema>;
export type Workspace = z.infer<typeof WorkspaceSchema>;
export type WorkspaceView = Workspace["views"][number];

export function parseWorkspace(source: string): { workspace?: Workspace; error?: string } {
  try {
    const json: unknown = JSON.parse(source);
    const result = WorkspaceSchema.safeParse(json);
    if (!result.success) {
      const issue = result.error.issues[0];
      return { error: `${issue.path.join(".") || "workspace"}: ${issue.message}` };
    }
    return { workspace: result.data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : "Invalid JSON" };
  }
}

export function serializeWorkspace(workspace: Workspace): string {
  return JSON.stringify(workspace, null, 2);
}

export type WorkspaceUpdateResult =
  | { ok: true; workspace: Workspace }
  | { ok: false; error: string };

export function validateWorkspaceUpdate(workspace: unknown): WorkspaceUpdateResult {
  const result = WorkspaceSchema.safeParse(workspace);
  if (result.success) return { ok: true, workspace: result.data };
  const issue = result.error.issues[0];
  return { ok: false, error: `${issue.path.join(".") || "workspace"}: ${issue.message}` };
}

export function appendWorkspaceView(workspace: Workspace, view: WorkspaceView): WorkspaceUpdateResult {
  return validateWorkspaceUpdate({ ...workspace, views: [...workspace.views, view] });
}

export type ViewUpdateResult =
  | { ok: true; view: DiagramSpecView }
  | { ok: false; error: string };

export function removeDiagramNodes(view: DiagramSpecView, nodeIds: Iterable<string>): ViewUpdateResult {
  const deleted = new Set(nodeIds);
  const nodes = view.nodes.filter((node) => !deleted.has(node.id));
  if (!nodes.length) return { ok: false, error: "A visual view must keep at least one node" };
  const usedLanes = new Set(nodes.map((node) => node.lane).filter((lane): lane is string => Boolean(lane)));
  const emptyLane = view.lanes.find((lane) => !usedLanes.has(lane.id));
  if (emptyLane) return { ok: false, error: `Deleting these nodes would leave lane empty: ${emptyLane.id}` };
  const usedGroups = new Set(nodes.map((node) => node.group).filter((group): group is string => Boolean(group)));
  const emptyGroup = view.groups.find((group) => !usedGroups.has(group.id));
  if (emptyGroup) return { ok: false, error: `Deleting these nodes would leave group empty: ${emptyGroup.id}` };
  return {
    ok: true,
    view: {
      ...view,
      nodes,
      edges: view.edges.filter((edge) => !deleted.has(edge.source) && !deleted.has(edge.target)),
    },
  };
}
