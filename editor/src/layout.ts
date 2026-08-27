import type { ElkExtendedEdge, ElkNode } from "elkjs/lib/elk.bundled.js";
import { MarkerType, type Edge, type Node } from "@xyflow/react";
import type { DiagramNode, VisualSpecView } from "./model";

export type CanvasNodeData = {
  label: string;
  subtitle?: string;
  kind: DiagramNode["type"] | "lane";
  childView?: string;
  laneLabel?: string;
  direction?: "LR" | "TB";
};

export type CanvasNode = Node<CanvasNodeData>;
export type CanvasEdge = Edge;

const NODE_WIDTH = 224;
const NODE_HEIGHT = 88;

async function getElk() {
  const { default: ELK } = await import("elkjs/lib/elk.bundled.js");
  return new ELK();
}

function nodeData(node: DiagramNode): CanvasNodeData {
  return {
    label: node.label,
    subtitle: node.subtitle,
    kind: node.type,
    childView: node.child_view,
  };
}

function canvasEdge(view: VisualSpecView, index: number): CanvasEdge {
  const edge = view.edges[index];
  return {
    id: edge.id ?? `${edge.source}-${edge.target}-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.label,
    type: "smoothstep",
    animated: edge.kind === "feedback" || edge.kind === "async",
    className: `edge-${edge.kind}`,
    markerEnd: { type: MarkerType.ArrowClosed },
    data: { kind: edge.kind, index },
  };
}

function computeRanks(view: VisualSpecView): Map<string, number> {
  const ranks = new Map(view.nodes.map((node) => [node.id, node.rank ?? 0]));
  const outgoing = new Map(view.nodes.map((node) => [node.id, [] as string[]]));
  const indegree = new Map(view.nodes.map((node) => [node.id, 0]));
  view.edges.filter((edge) => edge.kind !== "feedback").forEach((edge) => {
    outgoing.get(edge.source)?.push(edge.target);
    indegree.set(edge.target, (indegree.get(edge.target) ?? 0) + 1);
  });
  const queue = view.nodes.filter((node) => indegree.get(node.id) === 0).map((node) => node.id);
  while (queue.length) {
    const current = queue.shift()!;
    for (const target of outgoing.get(current) ?? []) {
      if (view.nodes.find((node) => node.id === target)?.rank === undefined) {
        ranks.set(target, Math.max(ranks.get(target) ?? 0, (ranks.get(current) ?? 0) + 1));
      }
      indegree.set(target, (indegree.get(target) ?? 1) - 1);
      if (indegree.get(target) === 0) queue.push(target);
    }
  }
  return ranks;
}

function rankedNodes(view: VisualSpecView): CanvasNode[] {
  const ranks = computeRanks(view);
  const counters = new Map<number, number>();
  return view.nodes.map((node) => {
    const rank = ranks.get(node.id) ?? 0;
    const index = counters.get(rank) ?? 0;
    counters.set(rank, index + 1);
    const position = node.position ?? (view.direction === "LR"
      ? { x: 70 + rank * 320, y: 70 + index * 138 }
      : { x: 70 + index * 286, y: 70 + rank * 176 });
    return { id: node.id, type: "visual", position, data: nodeData(node) };
  });
}

function swimlaneNodes(view: VisualSpecView): CanvasNode[] {
  const ranks = computeRanks(view);
  const lanes = [...view.lanes].sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
  const maxRank = Math.max(0, ...view.nodes.map((node) => ranks.get(node.id) ?? 0));
  const result: CanvasNode[] = [];
  let laneOffset = 24;

  lanes.forEach((lane) => {
    const members = view.nodes.filter((node) => node.lane === lane.id);
    const rankCounts = new Map<number, number>();
    members.forEach((node) => rankCounts.set(ranks.get(node.id) ?? 0, (rankCounts.get(ranks.get(node.id) ?? 0) ?? 0) + 1));
    const maxInRank = Math.max(1, ...rankCounts.values());
    const horizontal = view.direction === "LR";
    const laneWidth = horizontal ? Math.max(780, 140 + (maxRank + 1) * 310) : Math.max(320, 92 + maxInRank * 250);
    const laneHeight = horizontal ? Math.max(190, 94 + maxInRank * 112) : Math.max(620, 110 + (maxRank + 1) * 160);
    const lanePosition = horizontal ? { x: 24, y: laneOffset } : { x: laneOffset, y: 24 };
    result.push({
      id: `lane:${lane.id}`,
      type: "lane",
      position: lanePosition,
      data: { label: lane.label, kind: "lane", laneLabel: lane.label },
      selectable: false,
      draggable: false,
      connectable: false,
      style: { width: laneWidth, height: laneHeight, zIndex: -1 },
    });

    const withinRank = new Map<number, number>();
    members.forEach((node) => {
      const rank = ranks.get(node.id) ?? 0;
      const index = withinRank.get(rank) ?? 0;
      withinRank.set(rank, index + 1);
      const fallback = horizontal
        ? { x: 112 + rank * 310, y: 64 + index * 112 }
        : { x: 44 + index * 250, y: 92 + rank * 160 };
      result.push({
        id: node.id,
        type: "visual",
        position: node.position ?? fallback,
        parentId: `lane:${lane.id}`,
        extent: "parent",
        expandParent: true,
        data: nodeData(node),
      });
    });
    laneOffset += (horizontal ? laneHeight : laneWidth) + 18;
  });
  return result;
}

async function elkNodes(view: VisualSpecView): Promise<CanvasNode[]> {
  const elk = await getElk();
  const direction = view.direction === "LR" ? "RIGHT" : "DOWN";
  const graph: ElkNode = {
    id: "root",
    layoutOptions: {
      "elk.algorithm": "layered",
      "elk.direction": direction,
      "elk.edgeRouting": "ORTHOGONAL",
      "elk.hierarchyHandling": "INCLUDE_CHILDREN",
      "elk.layered.spacing.nodeNodeBetweenLayers": "96",
      "elk.spacing.nodeNode": "54",
      "elk.layered.considerModelOrder.strategy": "NODES_AND_EDGES",
    },
    children: view.nodes.map((node) => ({
      id: node.id,
      width: NODE_WIDTH,
      height: NODE_HEIGHT,
      layoutOptions: node.rank === undefined ? undefined : {
        "elk.layered.layering.layerId": String(node.rank),
      },
    })),
    edges: view.edges.filter((edge) => edge.kind !== "feedback").map((edge, index): ElkExtendedEdge => ({
      id: edge.id ?? `edge-${index}`,
      sources: [edge.source],
      targets: [edge.target],
    })),
  };
  const laidOut = await elk.layout(graph);
  const positions = new Map((laidOut.children ?? []).map((node) => [node.id, { x: node.x ?? 0, y: node.y ?? 0 }]));
  return view.nodes.map((node) => ({
    id: node.id,
    type: "visual",
    position: view.layout_mode === "manual" && node.position ? node.position : positions.get(node.id) ?? { x: 0, y: 0 },
    data: nodeData(node),
  }));
}

export async function layoutView(view: VisualSpecView): Promise<{ nodes: CanvasNode[]; edges: CanvasEdge[] }> {
  const nodes = view.lanes.length
    ? swimlaneNodes(view)
    : view.layout_mode === "ranked"
      ? rankedNodes(view)
      : await elkNodes(view);
  return { nodes, edges: view.edges.map((_, index) => canvasEdge(view, index)) };
}
