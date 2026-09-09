# Adaptive Core Changelog

Author attribution: DarekDGB
License: MIT

## Unreleased - V4.10-G2 release-truth alignment

### Changed

- Align distribution metadata from 3.0.0 to the already-existing v3.1.0 tag
  and public README baseline; use ASCII-safe package description typography.
- Distinguish the published tag from the later working tree. G2 is a
  metadata/documentation/test candidate, not a new release or tag action.
- Document the unchanged v3.0.0 report baseline, adaptive_core_oracle_v3
  interface, and caller-overridable adaptive-core/3.0.0 exporter default.
- Replace the obsolete current-facing 260-test count with dated source and
  candidate results. State that the enforced 100% gate covers statements.
- Clarify advisory-only authority, local counters/artifact output, and the
  non-cryptographic meaning of report signature-status labels.
- Add an indexed release-status record and six release-truth regression
  tests. Update only the package-version assertion in the V4.9-C test.

No runtime source, workflow, dependency requirement, schema, registry, fixture,
canonical byte profile, exporter default, or license is changed. The shared
AdamantineOS evidence vector remains byte-identical. No Shield cryptographic
verification, live-OQS proof, or final execution authority is added.

## Historical v3.1.0 tag

Verified 2026-09-08: tag v3.1.0 identifies
899ef8efd7426ded302a1599073b950ca7e36afe. The authenticated pre-G2 main at
13bbd054732cd22cb550b203e591c26864b685bf is 51 commits ahead of that tag.
This record does not retroactively assign every later change to the tag.
No changelog existed in the authenticated source; earlier detailed history
remains in Git history and the existing versioned documents.

See [current release status](docs/RELEASE_STATUS_V4_10_G2.md). The next
independent release number is unassigned; Adaptive Core does not inherit
Shield v4.0.0 automatically.
