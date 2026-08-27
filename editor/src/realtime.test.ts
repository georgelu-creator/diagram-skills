import { describe, expect, it } from "vitest";
import * as Y from "yjs";
import { realtimeChannel, workspaceSource } from "./realtime";

describe("realtime workspace state", () => {
  it("isolates persistence and websocket channels by document id", () => {
    expect(realtimeChannel("workspace-a")).not.toBe(realtimeChannel("workspace-b"));
    expect(() => realtimeChannel("unsafe/room")).toThrow("document id");
  });

  it("converges concurrent whole-workspace updates without concatenating JSON", () => {
    const left = new Y.Doc();
    const right = new Y.Doc();
    workspaceSource(left).set("source", JSON.stringify({ title: "left" }));
    workspaceSource(right).set("source", JSON.stringify({ title: "right" }));

    const leftUpdate = Y.encodeStateAsUpdate(left);
    const rightUpdate = Y.encodeStateAsUpdate(right);
    Y.applyUpdate(left, rightUpdate);
    Y.applyUpdate(right, leftUpdate);

    const leftSource = workspaceSource(left).get("source");
    const rightSource = workspaceSource(right).get("source");
    expect(leftSource).toBe(rightSource);
    expect(() => JSON.parse(leftSource ?? "")).not.toThrow();
    expect(["left", "right"]).toContain(JSON.parse(leftSource ?? "{}").title);
    left.destroy();
    right.destroy();
  });
});
