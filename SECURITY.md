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

Do not place credentials, private URLs, personal data, or confidential architecture details in a specification intended for a public repository.
