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

export const VisualSpecViewSchema = DiagramSchema.extend({
  id,
  format: z.literal("visualspec"),
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
  views: z.array(z.discriminatedUnion("format", [VisualSpecViewSchema, MermaidViewSchema])).min(1),
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
    if (view.format !== "visualspec") return;
    const nodeIds = new Set(view.nodes.map((node) => node.id));
    const laneIds = new Set(view.lanes.map((lane) => lane.id));
    view.nodes.forEach((node, nodeIndex) => {
      if (view.lanes.length && !node.lane) {
        context.addIssue({ code: "custom", path: ["views", viewIndex, "nodes", nodeIndex, "lane"], message: "Every node must be assigned when swimlanes exist" });
      }
      if (node.lane && !laneIds.has(node.lane)) {
        context.addIssue({ code: "custom", path: ["views", viewIndex, "nodes", nodeIndex, "lane"], message: `Unknown lane: ${node.lane}` });
      }
      if (node.child_view && !ids.has(node.child_view)) {
        context.addIssue({ code: "custom", path: ["views", viewIndex, "nodes", nodeIndex, "child_view"], message: `Unknown child view: ${node.child_view}` });
      }
    });
    view.edges.forEach((edge, edgeIndex) => {
      if (!nodeIds.has(edge.source) || !nodeIds.has(edge.target)) {
        context.addIssue({ code: "custom", path: ["views", viewIndex, "edges", edgeIndex], message: `Unknown edge endpoint: ${edge.source} → ${edge.target}` });
      }
    });
  });
});

export type Brand = z.infer<typeof BrandSchema>;
export type DiagramNode = z.infer<typeof DiagramNodeSchema>;
export type DiagramEdge = z.infer<typeof DiagramEdgeSchema>;
export type VisualSpecView = z.infer<typeof VisualSpecViewSchema>;
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
