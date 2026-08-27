import * as Y from "yjs";
import { IndexeddbPersistence } from "y-indexeddb";
import { WebsocketProvider } from "y-websocket";

export type RealtimeStatus = "loading" | "offline-ready" | "connected" | "disconnected";

export class RealtimeWorkspace {
  readonly doc = new Y.Doc();
  readonly text = this.doc.getText("workspace");
  readonly persistence: IndexeddbPersistence;
  readonly websocket?: WebsocketProvider;

  constructor(initialSource: string, onChange: (source: string) => void, onStatus: (status: RealtimeStatus) => void) {
    this.persistence = new IndexeddbPersistence("visualspec-studio-v3", this.doc);
    this.text.observe(() => onChange(this.text.toString()));
    this.persistence.once("synced", () => {
      if (!this.text.length) this.replace(initialSource);
      else onChange(this.text.toString());
      onStatus("offline-ready");
    });
    const websocketUrl = import.meta.env.VITE_YJS_WEBSOCKET_URL as string | undefined;
    if (websocketUrl) {
      this.websocket = new WebsocketProvider(websocketUrl, "visualspec-studio-v3", this.doc);
      this.websocket.on("status", ({ status }: { status: "connected" | "connecting" | "disconnected" }) => onStatus(status === "connecting" ? "loading" : status));
    }
  }

  replace(source: string): void {
    if (source === this.text.toString()) return;
    this.doc.transact(() => {
      this.text.delete(0, this.text.length);
      this.text.insert(0, source);
    });
  }

  destroy(): void {
    this.websocket?.destroy();
    this.persistence.destroy();
    this.doc.destroy();
  }
}
