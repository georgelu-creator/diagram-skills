import Papa from "papaparse";
import { edgeKinds, nodeTypes, type MermaidView, type VisualSpecView } from "./model";

type CsvRow = Record<string, string | undefined>;

function safeId(value: string, fallback: string): string {
  const cleaned = value.trim().replace(/[^A-Za-z0-9_.-]+/g, "-").replace(/^-+|-+$/g, "");
  return cleaned || fallback;
}

export function importCsv(source: string, title = "CSV 导入视图"): VisualSpecView {
  const result = Papa.parse<CsvRow>(source, { header: true, skipEmptyLines: "greedy", transformHeader: (header) => header.trim() });
  if (result.errors.length) throw new Error(result.errors[0].message);
  const nodes = new Map<string, VisualSpecView["nodes"][number]>();
  const lanes = new Map<string, VisualSpecView["lanes"][number]>();
  const edges: VisualSpecView["edges"] = [];

  const ensureNode = (rawId: string | undefined, label?: string, row?: CsvRow) => {
    if (!rawId?.trim()) return;
    const nodeId = safeId(rawId, `node-${nodes.size + 1}`);
    if (nodes.has(nodeId)) return;
    const rawType = row?.type?.trim();
    const type = nodeTypes.includes(rawType as (typeof nodeTypes)[number]) ? rawType as (typeof nodeTypes)[number] : "process";
    const lane = row?.lane?.trim() ? safeId(row.lane, `lane-${lanes.size + 1}`) : undefined;
    const rankValue = row?.rank?.trim() ? Number(row.rank) : undefined;
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

  result.data.forEach((row, index) => {
    const nodeId = row.node_id ?? row.id;
    ensureNode(nodeId, row.label, row);
    ensureNode(row.source, row.source_label);
    ensureNode(row.target, row.target_label);
    if (row.source?.trim() && row.target?.trim()) {
      const kindValue = row.edge_kind?.trim();
      const kind = edgeKinds.includes(kindValue as (typeof edgeKinds)[number]) ? kindValue as (typeof edgeKinds)[number] : "primary";
      edges.push({
        id: `csv-edge-${index + 1}`,
        source: safeId(row.source, `source-${index + 1}`),
        target: safeId(row.target, `target-${index + 1}`),
        label: row.edge_label?.trim() || undefined,
        kind,
      });
    }
  });
  if (!nodes.size) throw new Error("CSV must contain node_id/id or source/target columns");
  return {
    id: `csv-${Date.now()}`,
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
  return { id: `mermaid-${Date.now()}`, format: "mermaid", title, source };
}
