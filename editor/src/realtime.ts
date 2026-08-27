import * as Y from "yjs";
import { IndexeddbPersistence } from "y-indexeddb";
import { WebsocketProvider } from "y-websocket";

export type RealtimeStatus = "loading" | "offline-ready" | "connected" | "disconnected";

const DOCUMENT_ID = /^[A-Za-z0-9_.-]{1,128}$/;
const SOURCE_KEY = "source";

export function realtimeChannel(documentId: string): string {
  if (!DOCUMENT_ID.test(documentId)) throw new Error("document id must contain only letters, numbers, dot, underscore, or hyphen");
  return `visualskills-studio-v4-${documentId}`;
}

export function ensureDocumentId(): string {
  const url = new URL(window.location.href);
  const requested = url.searchParams.get("document");
  if (requested && DOCUMENT_ID.test(requested)) return requested;
  const generated = globalThis.crypto.randomUUID();
  url.searchParams.set("document", generated);
  window.history.replaceState(window.history.state, "", url);
  return generated;
}

export function workspaceSource(doc: Y.Doc): Y.Map<string> {
  return doc.getMap<string>("workspace");
}

export class RealtimeWorkspace {
  readonly doc = new Y.Doc();
  readonly state = workspaceSource(this.doc);
  readonly persistence: IndexeddbPersistence;
  readonly websocket?: WebsocketProvider;

  constructor(
    documentId: string,
    initialSource: string,
    onChange: (source: string) => void,
    onStatus: (status: RealtimeStatus) => void,
  ) {
    const channel = realtimeChannel(documentId);
    this.persistence = new IndexeddbPersistence(`${channel}-indexeddb`, this.doc);
    this.state.observe((event) => {
      if (!event.keysChanged.has(SOURCE_KEY)) return;
      const source = this.state.get(SOURCE_KEY);
      if (source !== undefined) onChange(source);
    });
    this.persistence.once("synced", () => {
      const persisted = this.state.get(SOURCE_KEY);
      if (persisted === undefined) this.replace(initialSource);
      else onChange(persisted);
      onStatus("offline-ready");
    });
    const websocketUrl = import.meta.env.VITE_YJS_WEBSOCKET_URL as string | undefined;
    if (websocketUrl) {
      this.websocket = new WebsocketProvider(websocketUrl, channel, this.doc);
      this.websocket.on("status", ({ status }: { status: "connected" | "connecting" | "disconnected" }) => onStatus(status === "connecting" ? "loading" : status));
    }
  }

  replace(source: string): void {
    if (source === this.state.get(SOURCE_KEY)) return;
    this.state.set(SOURCE_KEY, source);
  }

  destroy(): void {
    this.websocket?.destroy();
    this.persistence.destroy();
    this.doc.destroy();
  }
}
