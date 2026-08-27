import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Background,
  ConnectionMode,
  Controls,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
  type Edge,
  type OnNodeDrag,
  type Connection,
  type NodeProps,
} from "@xyflow/react";
import { importCsv, importMermaid } from "./importers";
import { layoutView, type CanvasNode, type CanvasNodeData } from "./layout";
import {
  WorkspaceSchema,
  diagramTypes,
  nodeTypes,
  parseWorkspace,
  serializeWorkspace,
  themeNames,
  type DiagramNode,
  type VisualSpecView,
  type Workspace,
  type WorkspaceView,
} from "./model";
import { RealtimeWorkspace, type RealtimeStatus } from "./realtime";
import { sampleWorkspace } from "./sample";

const nodeTypeMap = { visual: VisualNode, lane: LaneNode };
const Editor = lazy(() => import("./MonacoEditor"));

function VisualNode({ data, selected }: NodeProps<CanvasNode>) {
  const horizontal = data.direction !== "TB";
  return (
    <div className={`visual-node visual-node--${data.kind} ${selected ? "is-selected" : ""}`}>
      <Handle type="target" position={horizontal ? Position.Left : Position.Top} />
      <div className="visual-node__label">{data.label}</div>
      {data.subtitle && <div className="visual-node__subtitle">{data.subtitle}</div>}
      {data.childView && <div className="visual-node__drill">双击下钻 ↗</div>}
      <Handle type="source" position={horizontal ? Position.Right : Position.Bottom} />
    </div>
  );
}

function LaneNode({ data }: NodeProps<CanvasNode>) {
  return <div className="lane-node"><span>{data.laneLabel ?? data.label}</span></div>;
}

function DiagramCanvas({
  view,
  onChange,
  onSelectNode,
  onOpenView,
}: {
  view: VisualSpecView;
  onChange: (view: VisualSpecView) => void;
  onSelectNode: (nodeId?: string) => void;
  onOpenView: (viewId: string) => void;
}) {
  return (
    <ReactFlowProvider>
      <DiagramCanvasInner view={view} onChange={onChange} onSelectNode={onSelectNode} onOpenView={onOpenView} />
    </ReactFlowProvider>
  );
}

function DiagramCanvasInner({
  view,
  onChange,
  onSelectNode,
  onOpenView,
}: {
  view: VisualSpecView;
  onChange: (view: VisualSpecView) => void;
  onSelectNode: (nodeId?: string) => void;
  onOpenView: (viewId: string) => void;
}) {
  const [nodes, setNodes, onNodesChange] = useNodesState<CanvasNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const { fitView } = useReactFlow();
  const dragStarted = useRef<string | undefined>(undefined);

  useEffect(() => {
    let active = true;
    layoutView(view).then((layout) => {
      if (!active) return;
      setNodes(layout.nodes.map((node) => ({ ...node, data: { ...node.data, direction: view.direction } as CanvasNodeData })));
      setEdges(layout.edges);
      window.setTimeout(() => fitView({ padding: 0.18, duration: 220 }), 0);
    });
    return () => { active = false; };
  }, [view, setNodes, setEdges, fitView]);

  const commitPosition: OnNodeDrag<CanvasNode> = useCallback((_event, canvasNode) => {
    if (canvasNode.id.startsWith("lane:") || dragStarted.current !== canvasNode.id) return;
    dragStarted.current = undefined;
    onChange({
      ...view,
      layout_mode: "manual",
      nodes: view.nodes.map((node) => node.id === canvasNode.id ? { ...node, position: canvasNode.position } : node),
    });
  }, [onChange, view]);

  const connect = useCallback((connection: Connection) => {
    if (!connection.source || !connection.target) return;
    onChange({
      ...view,
      edges: [...view.edges, { id: `edge-${Date.now()}`, source: connection.source, target: connection.target, kind: "primary" }],
    });
  }, [onChange, view]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypeMap}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeDragStart={(_event, node) => { dragStarted.current = node.id; }}
      onNodeDragStop={commitPosition}
      onConnect={connect}
      onPaneClick={() => onSelectNode(undefined)}
      onNodeClick={(_event, node) => !node.id.startsWith("lane:") && onSelectNode(node.id)}
      onNodeDoubleClick={(_event, node) => node.data.childView && onOpenView(node.data.childView)}
      onNodesDelete={(deleted) => onChange({
        ...view,
        nodes: view.nodes.filter((node) => !deleted.some((item) => item.id === node.id)),
        edges: view.edges.filter((edge) => !deleted.some((item) => item.id === edge.source || item.id === edge.target)),
      })}
      onEdgesDelete={(deleted) => onChange({
        ...view,
        edges: view.edges.filter((edge, index) => !deleted.some((item) => item.id === (edge.id ?? `${edge.source}-${edge.target}-${index}`))),
      })}
      connectionMode={ConnectionMode.Loose}
      minZoom={0.2}
      maxZoom={2.2}
      deleteKeyCode={["Backspace", "Delete"]}
      colorMode={view.theme === "blueprint" || view.theme === "terminal" ? "dark" : "light"}
      className={`canvas canvas--${view.theme}`}
    >
      <Background gap={24} size={1} />
      <MiniMap pannable zoomable nodeStrokeWidth={2} />
      <Controls showInteractive={false} />
    </ReactFlow>
  );
}

function MermaidCanvas({ view, onChange }: { view: Extract<WorkspaceView, { format: "mermaid" }>; onChange: (view: WorkspaceView) => void }) {
  const [svg, setSvg] = useState("");
  const [error, setError] = useState<string>();
  const renderId = useRef(0);

  useEffect(() => {
    let active = true;
    const timer = window.setTimeout(async () => {
      try {
        const { default: mermaid } = await import("mermaid");
        mermaid.initialize({ startOnLoad: false, securityLevel: "strict", theme: "base" });
        await mermaid.parse(view.source);
        const result = await mermaid.render(`visualspec-mermaid-${++renderId.current}`, view.source);
        if (active) {
          setSvg(result.svg);
          setError(undefined);
        }
      } catch (caught) {
        if (active) setError(caught instanceof Error ? caught.message : "Mermaid syntax error");
      }
    }, 180);
    return () => { active = false; window.clearTimeout(timer); };
  }, [view.source]);

  return (
    <div className="mermaid-workbench">
      <div className="mermaid-source">
        <div className="panel-caption">Mermaid source · 实时校验</div>
        <Suspense fallback={<div className="editor-loading">Loading editor…</div>}><Editor
            language="markdown"
            theme="vs-dark"
            value={view.source}
            onChange={(value) => onChange({ ...view, source: value ?? "" })}
            options={{ minimap: { enabled: false }, fontSize: 13, wordWrap: "on", automaticLayout: true }}
          /></Suspense>
      </div>
      <div className="mermaid-preview">
        {error ? <div className="error-card"><strong>Mermaid 校验失败</strong><span>{error}</span></div> : <div className="mermaid-svg" dangerouslySetInnerHTML={{ __html: svg }} />}
      </div>
    </div>
  );
}

function Inspector({
  view,
  workspace,
  selectedNode,
  onChange,
  onAddNode,
  onAddLane,
}: {
  view: WorkspaceView;
  workspace: Workspace;
  selectedNode?: string;
  onChange: (view: WorkspaceView) => void;
  onAddNode: () => void;
  onAddLane: () => void;
}) {
  if (view.format === "mermaid") {
    return <div className="inspector"><h3>Mermaid 视图</h3><p>官方 Mermaid 引擎负责语法校验和渲染。源码保留，不做有损转换。</p></div>;
  }
  const node = view.nodes.find((item) => item.id === selectedNode);
  const updateNode = (patch: Partial<DiagramNode>) => onChange({ ...view, nodes: view.nodes.map((item) => item.id === node?.id ? { ...item, ...patch } : item) });
  return (
    <div className="inspector">
      <div className="inspector__heading"><h3>{node ? "节点属性" : "视图设置"}</h3>{node && <button className="text-button" onClick={() => updateNode({ position: undefined })}>清除坐标</button>}</div>
      {node ? (
        <>
          <Field label="标题"><input value={node.label} onChange={(event) => updateNode({ label: event.target.value })} /></Field>
          <Field label="副标题"><input value={node.subtitle ?? ""} onChange={(event) => updateNode({ subtitle: event.target.value || undefined })} /></Field>
          <Field label="类型"><select value={node.type} onChange={(event) => updateNode({ type: event.target.value as DiagramNode["type"] })}>{nodeTypes.map((type) => <option key={type}>{type}</option>)}</select></Field>
          <Field label="手动层级 / Rank"><input type="number" min="0" value={node.rank ?? ""} onChange={(event) => updateNode({ rank: event.target.value === "" ? undefined : Number(event.target.value) })} /></Field>
          <Field label="泳道"><select value={node.lane ?? ""} onChange={(event) => updateNode({ lane: event.target.value || undefined })}>{!view.lanes.length && <option value="">未分配</option>}{view.lanes.map((lane) => <option key={lane.id} value={lane.id}>{lane.label}</option>)}</select></Field>
          <Field label="下钻视图"><select value={node.child_view ?? ""} onChange={(event) => updateNode({ child_view: event.target.value || undefined })}><option value="">无</option>{workspace.views.filter((item) => item.id !== view.id).map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></Field>
        </>
      ) : (
        <>
          <Field label="视图标题"><input value={view.title} onChange={(event) => onChange({ ...view, title: event.target.value })} /></Field>
          <Field label="图类型"><select value={view.diagram_type} onChange={(event) => onChange({ ...view, diagram_type: event.target.value as VisualSpecView["diagram_type"] })}>{diagramTypes.map((type) => <option key={type}>{type}</option>)}</select></Field>
          <Field label="方向"><select value={view.direction} onChange={(event) => onChange({ ...view, direction: event.target.value as "LR" | "TB" })}><option value="LR">左 → 右</option><option value="TB">上 → 下</option></select></Field>
          <Field label="布局"><select value={view.layout_mode} onChange={(event) => onChange({ ...view, layout_mode: event.target.value as VisualSpecView["layout_mode"] })}><option value="auto">ELK 自动布局</option><option value="ranked">手动 Rank</option><option value="manual">手动坐标</option></select></Field>
          <Field label="主题"><select value={view.theme} onChange={(event) => onChange({ ...view, theme: event.target.value as VisualSpecView["theme"] })}>{themeNames.map((theme) => <option key={theme}>{theme}</option>)}</select></Field>
          <div className="color-grid">
            <ColorField label="品牌主色" value={view.brand?.primary ?? "#4F46E5"} onChange={(primary) => onChange({ ...view, brand: { ...view.brand, primary } })} />
            <ColorField label="强调色" value={view.brand?.accent ?? "#14B8A6"} onChange={(accent) => onChange({ ...view, brand: { ...view.brand, accent } })} />
          </div>
          <div className="button-row"><button onClick={onAddNode}>＋ 节点</button><button onClick={onAddLane}>＋ 泳道</button></div>
        </>
      )}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="field"><span>{label}</span>{children}</label>;
}

function ColorField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return <label className="color-field"><span>{label}</span><input type="color" value={value.slice(0, 7)} onChange={(event) => onChange(event.target.value)} /></label>;
}

function ImportDialog({ onClose, onImport }: { onClose: () => void; onImport: (mode: "json" | "csv" | "mermaid", title: string, source: string) => Promise<void> }) {
  const [mode, setMode] = useState<"json" | "csv" | "mermaid">("csv");
  const [title, setTitle] = useState("导入视图");
  const [source, setSource] = useState("node_id,label,type,lane,lane_label,rank,source,target,edge_kind\nrequest,提交请求,input,user,用户,0,,,\nreview,人工审核,decision,ops,运营,1,request,review,control\napprove,审核通过,process,ops,运营,2,review,approve,success");
  const [error, setError] = useState<string>();
  const submit = async () => {
    try { await onImport(mode, title, source); onClose(); } catch (caught) { setError(caught instanceof Error ? caught.message : "Import failed"); }
  };
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="modal" role="dialog" aria-modal="true" aria-label="Import" onMouseDown={(event) => event.stopPropagation()}>
        <div className="modal__header"><div><strong>导入到 VisualSkills</strong><span>JSON Workspace · CSV · Mermaid</span></div><button onClick={onClose}>×</button></div>
        <div className="segmented">{(["csv", "mermaid", "json"] as const).map((item) => <button key={item} className={mode === item ? "active" : ""} onClick={() => setMode(item)}>{item.toUpperCase()}</button>)}</div>
        {mode !== "json" && <Field label="视图标题"><input value={title} onChange={(event) => setTitle(event.target.value)} /></Field>}
        <textarea value={source} onChange={(event) => setSource(event.target.value)} spellCheck={false} />
        <label className="file-picker">从本地文件读取<input type="file" accept={mode === "csv" ? ".csv,text/csv" : mode === "json" ? ".json,application/json" : ".mmd,.mermaid,text/plain"} onChange={(event) => { const file = event.target.files?.[0]; if (file) file.text().then(setSource); }} /></label>
        {error && <div className="inline-error">{error}</div>}
        <div className="modal__actions"><button onClick={onClose}>取消</button><button className="primary" onClick={submit}>校验并导入</button></div>
      </section>
    </div>
  );
}

function downloadJson(workspace: Workspace) {
  const blob = new Blob([serializeWorkspace(workspace)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${workspace.title.replace(/[^A-Za-z0-9\u4e00-\u9fff-]+/g, "-") || "visualskills"}.json`;
  anchor.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export default function App() {
  const initialSource = useMemo(() => serializeWorkspace(sampleWorkspace), []);
  const [workspace, setWorkspace] = useState<Workspace>(sampleWorkspace);
  const [source, setSource] = useState(initialSource);
  const [sourceError, setSourceError] = useState<string>();
  const [activeViewId, setActiveViewId] = useState(sampleWorkspace.entry_view);
  const [history, setHistory] = useState<string[]>([]);
  const [selectedNode, setSelectedNode] = useState<string>();
  const [panel, setPanel] = useState<"inspector" | "source">("inspector");
  const [showImport, setShowImport] = useState(false);
  const [status, setStatus] = useState<RealtimeStatus>("loading");
  const realtime = useRef<RealtimeWorkspace | undefined>(undefined);

  const receiveSource = useCallback((nextSource: string) => {
    setSource(nextSource);
    const parsed = parseWorkspace(nextSource);
    if (parsed.workspace) {
      setWorkspace(parsed.workspace);
      setSourceError(undefined);
    } else setSourceError(parsed.error);
  }, []);

  useEffect(() => {
    const document = new RealtimeWorkspace(initialSource, receiveSource, setStatus);
    realtime.current = document;
    return () => document.destroy();
  }, [initialSource, receiveSource]);

  const updateWorkspace = useCallback((nextWorkspace: Workspace) => {
    const result = WorkspaceSchema.safeParse(nextWorkspace);
    if (!result.success) {
      const issue = result.error.issues[0];
      setSourceError(`${issue.path.join(".") || "workspace"}: ${issue.message}`);
      return;
    }
    const normalized = result.data;
    const nextSource = serializeWorkspace(normalized);
    setWorkspace(normalized);
    setSource(nextSource);
    setSourceError(undefined);
    realtime.current?.replace(nextSource);
  }, []);

  const activeView = workspace.views.find((view) => view.id === activeViewId) ?? workspace.views[0];
  useEffect(() => {
    if (!workspace.views.some((view) => view.id === activeViewId)) setActiveViewId(workspace.entry_view);
  }, [workspace, activeViewId]);

  const updateView = useCallback((nextView: WorkspaceView) => {
    updateWorkspace({ ...workspace, views: workspace.views.map((view) => view.id === nextView.id ? nextView : view) });
  }, [updateWorkspace, workspace]);

  const openView = useCallback((viewId: string) => {
    if (!workspace.views.some((view) => view.id === viewId) || viewId === activeViewId) return;
    setHistory((items) => [...items, activeViewId]);
    setActiveViewId(viewId);
    setSelectedNode(undefined);
  }, [activeViewId, workspace.views]);

  const goBack = () => setHistory((items) => {
    const next = [...items];
    const target = next.pop();
    if (target) setActiveViewId(target);
    return next;
  });

  const addNode = () => {
    if (activeView.format !== "visualspec") return;
    const id = `node-${Date.now()}`;
    const lane = activeView.lanes[0]?.id;
    updateView({ ...activeView, nodes: [...activeView.nodes, { id, label: "新节点", type: "process", lane }] });
    setSelectedNode(id);
  };

  const addLane = () => {
    if (activeView.format !== "visualspec") return;
    const id = `lane-${activeView.lanes.length + 1}`;
    updateView({
      ...activeView,
      lanes: [...activeView.lanes, { id, label: `泳道 ${activeView.lanes.length + 1}`, order: activeView.lanes.length }],
      nodes: activeView.lanes.length ? activeView.nodes : activeView.nodes.map((node) => ({ ...node, lane: id })),
    });
  };

  const addView = () => {
    const id = `view-${Date.now()}`;
    const next: VisualSpecView = { id, format: "visualspec", title: "新视图", diagram_type: "process-flow", direction: "LR", theme: "paper", layout_mode: "auto", groups: [], lanes: [], nodes: [{ id: "start", label: "开始", type: "input" }], edges: [] };
    updateWorkspace({ ...workspace, views: [...workspace.views, next] });
    setActiveViewId(id);
  };

  const handleSourceChange = (nextSource: string) => {
    setSource(nextSource);
    const parsed = parseWorkspace(nextSource);
    if (parsed.workspace) {
      setWorkspace(parsed.workspace);
      setSourceError(undefined);
      realtime.current?.replace(nextSource);
    } else setSourceError(parsed.error);
  };

  const handleImport = async (mode: "json" | "csv" | "mermaid", title: string, importSource: string) => {
    if (mode === "json") {
      const parsed = parseWorkspace(importSource);
      if (!parsed.workspace) throw new Error(parsed.error);
      updateWorkspace(parsed.workspace);
      setActiveViewId(parsed.workspace.entry_view);
      return;
    }
    const view = mode === "csv" ? importCsv(importSource, title) : await importMermaid(importSource, title);
    updateWorkspace({ ...workspace, views: [...workspace.views, view] });
    setActiveViewId(view.id);
  };

  const statusText = status === "connected" ? "实时协作已连接" : status === "offline-ready" ? "离线自动保存" : status === "disconnected" ? "协作已断开 · 本地可用" : "正在恢复文档";

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="product"><span className="product__mark">V</span><div><strong>VisualSkills Studio</strong><span>Visual thinking workbench</span></div></div>
        <div className="breadcrumbs">{history.length > 0 && <button onClick={goBack}>← 返回</button>}<span>{workspace.title}</span><b>/</b><strong>{activeView.title}</strong></div>
        <div className="topbar__actions"><span className={`sync-status sync-status--${status}`}>{statusText}</span><button onClick={() => setShowImport(true)}>导入</button><button onClick={() => downloadJson(workspace)}>导出 JSON</button></div>
      </header>
      <div className="workspace-grid">
        <aside className="view-rail">
          <div className="rail-heading"><span>视图 / Views</span><button onClick={addView}>＋</button></div>
          <nav>{workspace.views.map((view) => <button key={view.id} className={view.id === activeView.id ? "active" : ""} onClick={() => { setActiveViewId(view.id); setHistory([]); }}><span className={`format-dot format-dot--${view.format}`} /> <span>{view.title}</span><small>{view.format}</small></button>)}</nav>
          <div className="rail-note"><strong>多视图下钻</strong><span>在节点属性中选择 child_view，双击节点即可进入子视图。</span></div>
        </aside>
        <main className="canvas-area" style={activeView.format === "visualspec" ? ({
          "--brand-primary": activeView.brand?.primary ?? "#4F46E5",
          "--brand-accent": activeView.brand?.accent ?? "#14B8A6",
        } as React.CSSProperties) : undefined}>
          {activeView.format === "visualspec"
            ? <DiagramCanvas view={activeView} onChange={updateView as (view: VisualSpecView) => void} onSelectNode={setSelectedNode} onOpenView={openView} />
            : <MermaidCanvas view={activeView} onChange={updateView} />}
        </main>
        <aside className="right-panel">
          <div className="panel-tabs"><button className={panel === "inspector" ? "active" : ""} onClick={() => setPanel("inspector")}>属性</button><button className={panel === "source" ? "active" : ""} onClick={() => setPanel("source")}>Workspace JSON</button></div>
          {panel === "inspector"
            ? <Inspector view={activeView} workspace={workspace} selectedNode={selectedNode} onChange={updateView} onAddNode={addNode} onAddLane={addLane} />
            : <div className="source-panel"><Suspense fallback={<div className="editor-loading">Loading editor…</div>}><Editor language="json" value={source} onChange={(value) => handleSourceChange(value ?? "")} options={{ minimap: { enabled: false }, fontSize: 12, tabSize: 2, automaticLayout: true, wordWrap: "on" }} /></Suspense>{sourceError && <div className="source-error">{sourceError}</div>}</div>}
        </aside>
      </div>
      {showImport && <ImportDialog onClose={() => setShowImport(false)} onImport={handleImport} />}
    </div>
  );
}
