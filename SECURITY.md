# Security

## Supported versions

Security fixes are applied to the current default branch.

## Reporting

Do not publish suspected vulnerabilities or sensitive diagram data in a public issue. Contact the repository owner privately through the email address associated with the GitHub profile.

## Threat model

ABI Flow treats diagram JSON as untrusted input:

- all SVG and HTML text is escaped;
- node links are restricted to HTTP(S), `mailto`, and page fragments;
- generated HTML contains no remote scripts, fonts, trackers, or network calls;
- the renderer does not execute content from the diagram specification;
- output paths are supplied explicitly by the caller.

VisualSpec Studio adds browser-side controls:

- Workspace JSON is parsed through a strict Zod model with reference checks.
- Mermaid uses the official renderer with `securityLevel: strict`.
- Monaco and all editor code load from installed packages; no public CDN is required.
- CSV is parsed locally and mapped into allowlisted VisualSpec fields.
- Brand values accept only known keys and six- or eight-digit hex colors.
- Yjs data persists in local IndexedDB. Network sync is disabled unless `VITE_YJS_WEBSOCKET_URL` names a trusted compatible endpoint.
- The dependency lock file is audited in CI.

Do not place credentials, private URLs, personal data, or confidential architecture details in a specification intended for a public repository.

Treat a configured collaboration endpoint as a data processor: add authentication, authorization, transport security, room isolation, retention, and abuse controls before using it with confidential workspaces.
