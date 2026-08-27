import { describe, expect, it } from "vitest";
import { parseWorkspace, serializeWorkspace } from "./model";
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
    if (overview.format === "visualspec") overview.nodes[0].child_view = "missing-view";
    expect(parseWorkspace(JSON.stringify(workspace)).error).toContain("Unknown child view");
  });
});
