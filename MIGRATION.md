# VisualSkills naming and compatibility

The project is adopting a clearer two-layer identity:

- **VisualSkills** is the user-facing brand: visual thinking skills for AI agents.
- **DiagramSpec** is the technical engine: the typed source, layout, rendering and diagnostic layer.

`abi-flow` remains the repository name, public Skill id and CLI path for compatibility. `VisualSpec` was the previous presentation name and may remain in historical audit records, schema format identifiers and compatibility-sensitive browser internals.

## What changed in this presentation update

- The README and public Skill metadata now lead with VisualSkills.
- DiagramSpec names the existing rendering engine and source contract.
- The homepage shows six distinct visual outcomes instead of three similar enterprise boards.
- Current, preview, next and exploring capabilities are separated.
- Claims were narrowed where the current implementation still has known validation, packaging or collaboration limitations.

## What did not change

- Repository URL: `georgelu-creator/abi-flow`
- Install command: `npx skills add georgelu-creator/abi-flow --skill abi-flow`
- Skill id: `$abi-flow`
- Existing JSON and workspace schema versions
- CLI paths and command names
- Existing templates, examples and generated artifacts
- Studio local storage keys and the internal `visualspec` workspace format identifier

## Possible future migration

The proposed long-term repository slug is `visualskills-ai` and the proposed primary Skill id is `visual-thinking`. Neither is active yet. A future migration must preserve the old Skill entry, CLI behavior, JSON compatibility and Studio local data for a documented compatibility window.

Before any repository rename or stable release, the project should:

1. verify naming across GitHub, domains, package registries and relevant trademarks;
2. close the release-blocking findings in [`AUDIT.md`](AUDIT.md);
3. test new and legacy Skill installation from a clean environment;
4. test Studio migration with a real legacy workspace fixture;
5. publish release notes, compatibility guarantees and a rollback path.

This document describes product naming, not a completed package or repository migration.
