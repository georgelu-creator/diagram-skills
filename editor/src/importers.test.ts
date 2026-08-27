import { describe, expect, it } from "vitest";
import { importCsv } from "./importers";
import { layoutView } from "./layout";
import { appendWorkspaceView } from "./model";
import { sampleWorkspace } from "./sample";
import { prepareWorkspaceImport } from "./workspace-import";

describe("CSV import", () => {
  it("creates nodes, semantic edges, lanes, and manual ranks", () => {
    const view = importCsv(`node_id,label,type,lane,lane_label,rank,source,target,edge_kind
request,提交请求,input,user,用户,0,,,
review,人工审核,decision,ops,运营,1,request,review,control
done,完成,process,ops,运营,2,review,done,success`);
    expect(view.nodes).toHaveLength(3);
    expect(view.edges.map((edge) => edge.kind)).toEqual(["control", "success"]);
    expect(view.lanes.map((lane) => lane.id)).toEqual(["user", "ops"]);
    expect(view.nodes.find((node) => node.id === "review")?.rank).toBe(1);
  });

  it("accepts a simple source/target edge table", () => {
    const view = importCsv("source,source_label,target,target_label\na,开始,b,结束");
    expect(view.nodes.map((node) => node.id)).toEqual(["a", "b"]);
    expect(view.edges[0]).toMatchObject({ source: "a", target: "b" });
  });

  it("rejects node identifiers that collide after normalization", () => {
    expect(() => importCsv("node_id,label\na b,One\na@b,Two")).toThrow(/Node id collision.*a-b/);
  });

  it("rejects lane identifiers that collide after normalization", () => {
    expect(() => importCsv("node_id,label,lane\na,One,ops team\nb,Two,ops@team")).toThrow(/Lane id collision.*ops-team/);
  });

  it("rejects duplicate authoritative node rows", () => {
    expect(() => importCsv("node_id,label\na,One\na,Two")).toThrow(/Duplicate node row.*a/);
  });

  it("rejects unknown node types instead of changing them to process", () => {
    expect(() => importCsv("node_id,label,type\na,One,service")).toThrow(/Unknown node type.*service/);
  });

  it("rejects unknown edge kinds instead of changing them to primary", () => {
    expect(() => importCsv("source,target,edge_kind\na,b,streaming")).toThrow(/Unknown edge kind.*streaming/);
  });

  it("rejects invalid manual ranks instead of discarding them", () => {
    expect(() => importCsv("node_id,label,rank\na,One,first")).toThrow(/Invalid rank.*first/);
  });

  it("reuses the generated id when the same punctuation-only source appears again", () => {
    const view = importCsv("node_id,label,source,target\n@,At,@,done");
    expect(view.nodes).toHaveLength(2);
    expect(view.edges[0].source).toBe(view.nodes[0].id);
  });

  it("surfaces a workspace validation failure for an imported view", () => {
    const view = importCsv("node_id,label,child_view\na,One,missing-view");
    const result = appendWorkspaceView(sampleWorkspace, view);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toContain("Unknown child view");
  });

  it("keeps the import transaction rejected when validation fails", async () => {
    await expect(prepareWorkspaceImport(sampleWorkspace, "csv", "Invalid", "node_id,label,child_view\na,One,missing-view"))
      .rejects.toThrow("Unknown child view");
    await expect(prepareWorkspaceImport(sampleWorkspace, "json", "Ignored", "{not json"))
      .rejects.toThrow();
    await expect(prepareWorkspaceImport(sampleWorkspace, "mermaid", "Invalid", "flowchart LR\n  A -->"))
      .rejects.toThrow();
  });
});

describe("layout adapter", () => {
  it("turns lanes into React Flow parent nodes", async () => {
    const view = importCsv(`node_id,label,lane,lane_label,rank
a,开始,user,用户,0
b,处理,ops,运营,1`);
    const layout = await layoutView(view);
    expect(layout.nodes.filter((node) => node.id.startsWith("lane:"))).toHaveLength(2);
    expect(layout.nodes.find((node) => node.id === "a")?.parentId).toBe("lane:user");
  });

  it("blocks duplicate ids before invoking ELK", async () => {
    const view = importCsv("node_id,label\na,One\nb,Two");
    view.nodes[1].id = "a";
    await expect(layoutView(view)).rejects.toThrow("Cannot layout duplicate node id: a");
  });
});
