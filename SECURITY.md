# Security

## Supported versions

Security fixes are applied to the current default branch.

## Reporting

Do not publish suspected vulnerabilities or sensitive diagram data in a public issue. Use GitHub's enabled [private vulnerability reporting form](https://github.com/georgelu-creator/abi-flow/security/advisories/new). If that form is unavailable, open a public issue containing only a request for a private contact channel—do not include vulnerability details or sensitive data.

## Threat model

The DiagramSpec renderer treats diagram JSON as untrusted input:

- all SVG and HTML text is escaped;
- node links are restricted to HTTP(S), `mailto`, and page fragments;
- generated HTML contains no remote scripts, fonts, trackers, or network calls;
- the renderer does not execute content from the diagram specification;
- output paths are supplied explicitly by the caller.

VisualSkills Studio adds browser-side controls:

- Workspace JSON is parsed through a strict Zod model with reference checks.
- Mermaid uses the official renderer with `securityLevel: strict`.
- Monaco and all editor code load from installed packages; no public CDN is required.
- CSV is parsed locally and mapped into allowlisted workspace fields.
- Brand values accept only known keys and six- or eight-digit hex colors.
- Enterprise boards accept only known section tones, block kinds, semantic edge kinds, and built-in icon names; JSON cannot inject arbitrary SVG, CSS, scripts, or remote images.
- Yjs data persists in local IndexedDB. Network sync is disabled unless `VITE_YJS_WEBSOCKET_URL` names a trusted compatible endpoint.
- The dependency lock file is audited in CI.

Do not place credentials, private URLs, personal data, or confidential architecture details in a specification intended for a public repository.

Treat a configured collaboration endpoint as a data processor: add authentication, authorization, transport security, room isolation, retention, and abuse controls before using it with confidential workspaces.
