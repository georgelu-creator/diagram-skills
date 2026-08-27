import { importCsv, importMermaid } from "./importers";
import { appendWorkspaceView, parseWorkspace, type Workspace } from "./model";

export type ImportMode = "json" | "csv" | "mermaid";

export async function prepareWorkspaceImport(
  workspace: Workspace,
  mode: ImportMode,
  title: string,
  source: string,
): Promise<{ workspace: Workspace; activeViewId: string }> {
  if (mode === "json") {
    const parsed = parseWorkspace(source);
    if (!parsed.workspace) throw new Error(parsed.error);
    return { workspace: parsed.workspace, activeViewId: parsed.workspace.entry_view };
  }
  const view = mode === "csv" ? importCsv(source, title) : await importMermaid(source, title);
  const merged = appendWorkspaceView(workspace, view);
  if (!merged.ok) throw new Error(merged.error);
  return { workspace: merged.workspace, activeViewId: view.id };
}
