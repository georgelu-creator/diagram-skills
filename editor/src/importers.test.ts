import { describe, expect, it } from "vitest";
import { importCsv } from "./importers";
import { layoutView } from "./layout";

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
});
