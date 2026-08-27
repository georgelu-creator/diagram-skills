import Papa from "papaparse";
import { edgeKinds, nodeTypes, type MermaidView, type VisualSpecView } from "./model";

type CsvRow = Record<string, string | undefined>;

function safeId(value: string, fallback: string): string {
  const cleaned = value.trim().replace(/[^A-Za-z0-9_.-]+/g, "-").replace(/^-+|-+$/g, "");
  return cleaned || fallback;
}

function normalizedId(
  rawValue: string,
  fallback: string,
  namespace: string,
  origins: Map<string, string>,
): string {
  const raw = rawValue.trim();
  for (const [knownId, knownRaw] of origins) {
    if (knownRaw === raw) return knownId;
  }
  const normalized = safeId(raw, fallback);
  const previous = origins.get(normalized);
  if (previous !== undefined && previous !== raw) {
    throw new Error(`${namespace} id collision after normalization: "${previous}" and "${raw}" both become "${normalized}"`);
  }
  origins.set(normalized, raw);
  return normalized;
}

function uniqueViewId(prefix: string): string {
  const uuid = globalThis.crypto?.randomUUID?.();
  return uuid ? `${prefix}-${uuid}` : `${prefix}-${Date.now()}-${Math.floor(Math.random() * 1_000_000)}`;
}

export function importCsv(source: string, title = "CSV 导入视图"): VisualSpecView {
  const result = Papa.parse<CsvRow>(source, { header: true, skipEmptyLines: "greedy", transformHeader: (header) => header.trim() });
  if (result.errors.length) throw new Error(result.errors[0].message);
  const nodes = new Map<string, VisualSpecView["nodes"][number]>();
  const lanes = new Map<string, VisualSpecView["lanes"][number]>();
  const edges: VisualSpecView["edges"] = [];
  const nodeOrigins = new Map<string, string>();
  const laneOrigins = new Map<string, string>();
  const explicitNodeRows = new Set<string>();

  const ensureNode = (rawId: string | undefined, label?: string, row?: CsvRow) => {
    if (!rawId?.trim()) return;
    const nodeId = normalizedId(rawId, `node-${nodes.size + 1}`, "Node", nodeOrigins);
    const rawType = row?.type?.trim();
    if (rawType && !nodeTypes.includes(rawType as (typeof nodeTypes)[number])) {
      throw new Error(`Unknown node type: "${rawType}"`);
    }
    if (nodes.has(nodeId)) return;
    const type = rawType as (typeof nodeTypes)[number] || "process";
    const lane = row?.lane?.trim() ? normalizedId(row.lane, `lane-${lanes.size + 1}`, "Lane", laneOrigins) : undefined;
    const rankValue = row?.rank?.trim() ? Number(row.rank) : undefined;
    if (row?.rank?.trim() && (!Number.isInteger(rankValue) || (rankValue ?? -1) < 0)) {
      throw new Error(`Invalid rank for node "${nodeId}": "${row.rank}"`);
    }
    nodes.set(nodeId, {
      id: nodeId,
      label: label?.trim() || rawId.trim(),
      subtitle: row?.subtitle?.trim() || undefined,
      type,
      lane,
      rank: Number.isInteger(rankValue) && (rankValue ?? -1) >= 0 ? rankValue : undefined,
      child_view: row?.child_view?.trim() ? safeId(row.child_view, "detail") : undefined,
    });
    if (lane && !lanes.has(lane)) {
      lanes.set(lane, { id: lane, label: row?.lane_label?.trim() || row?.lane?.trim() || lane, order: lanes.size });
    }
  };

  result.data.forEach((row) => {
    const nodeId = row.node_id ?? row.id;
    if (!nodeId?.trim()) return;
    const normalized = normalizedId(nodeId, `node-${nodes.size + 1}`, "Node", nodeOrigins);
    if (explicitNodeRows.has(normalized)) throw new Error(`Duplicate node row: "${nodeId.trim()}"`);
    explicitNodeRows.add(normalized);
    ensureNode(nodeId, row.label, row);
  });

  result.data.forEach((row, index) => {
    ensureNode(row.source, row.source_label);
    ensureNode(row.target, row.target_label);
    if (row.source?.trim() && row.target?.trim()) {
      const kindValue = row.edge_kind?.trim();
      if (kindValue && !edgeKinds.includes(kindValue as (typeof edgeKinds)[number])) {
        throw new Error(`Unknown edge kind: "${kindValue}"`);
      }
      const kind = kindValue as (typeof edgeKinds)[number] || "primary";
      edges.push({
        id: `csv-edge-${index + 1}`,
        source: normalizedId(row.source, `source-${index + 1}`, "Node", nodeOrigins),
        target: normalizedId(row.target, `target-${index + 1}`, "Node", nodeOrigins),
        label: row.edge_label?.trim() || undefined,
        kind,
      });
    }
  });
  if (!nodes.size) throw new Error("CSV must contain node_id/id or source/target columns");
  return {
    id: uniqueViewId("csv"),
    format: "visualspec",
    title,
    diagram_type: "process-flow",
    direction: "LR",
    theme: "spectrum",
    layout_mode: lanes.size ? "ranked" : "auto",
    groups: [],
    lanes: [...lanes.values()],
    nodes: [...nodes.values()],
    edges,
  };
}

export async function importMermaid(source: string, title = "Mermaid 导入视图"): Promise<MermaidView> {
  const { default: mermaid } = await import("mermaid");
  const result = await mermaid.parse(source, { suppressErrors: false });
  if (!result) throw new Error("Mermaid source is invalid");
  return { id: uniqueViewId("mermaid"), format: "mermaid", title, source };
}
