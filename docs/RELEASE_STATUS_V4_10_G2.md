# Adaptive Core V4.10-G2 Release Status

Author attribution: DarekDGB
License: MIT
Evidence date: 2026-09-08

## Status

G2 is a metadata/documentation/test candidate. Post-commit CI and fresh-ZIP
verification remain pending. This package declares no new release or tag,
changes no runtime behavior, and adds no Shield cryptographic verification.
The next independent release number is unassigned.

## Version reconciliation

| Surface | Value | Meaning |
|---|---|---|
| Distribution | `digibyte-quantum-adaptive-core` 3.1.0 | G2 corrects stale 3.0.0 package metadata to the existing public baseline |
| Existing tag | `v3.1.0` at `899ef8efd7426ded302a1599073b950ca7e36afe` | Historical tagged snapshot, not the later working tree |
| Report-document baseline | `v3.0.0` | Preserved v3 contract-document version, not package discovery |
| Advisory interface | `adaptive_core_oracle_v3` | Frozen receiver-facing contract marker |
| Exporter default `oracle_version` | `adaptive-core/3.0.0` | Frozen, caller-overridable advisory metadata |
| Exporter default `external_source_id` | `adaptive-core-v3-adamantine-export` | Advisory source label, not authenticated identity |

There is no runtime `__version__` or `server_version` surface. The exporter
does not read package metadata to construct `oracle_version`. Its default is
kept byte-identical to preserve the shared AdamantineOS vector; it must not be
represented as the installed distribution's version or verified provenance.
Callers may supply another non-empty metadata string, as before.

G2 reconciles the active package, README, security status, and version test.
It does not rewrite frozen report schemas, registries, proposal version
markers, historical v2 documents, or emitted evidence. Adaptive Core does not
inherit Shield `v4.0.0`. Changing a distribution label is not a contract bump
or an execution-authority change.

## Authenticated source

- Archive: `DigiByte-Adaptive-Core-main(20260812-060639).zip`.
- SHA-256: `d3cadd532d4e22eaeb7e421aed088fbb50fc23646bc7d5070bdb76cce4eecbd2`.
- Inventory: 124 files, 21 directories, 145 ZIP entries; safe paths and CRC.
- Embedded/current-main commit: `13bbd054732cd22cb550b203e591c26864b685bf`.
- Reconstructed/official tree: `77d2614f242a7dccbdda7b1f225c9e0bfd5bea81`.
- The two available post-FIX1 archives are byte-identical. GitHub comparison
  confirms the source is 51 commits ahead of the existing v3.1.0 tag.

The source's successful
[Adaptive Core Tests #324](https://github.com/DarekDGB/DigiByte-Adaptive-Core/actions/runs/31537484644)
is source evidence only, not the future G2 commit's gate. The earlier 260-test
result in the integration document belonged to the V4.9-C checkpoint; the
authenticated pre-G2 source has 283 passing tests.

## Advisory and cryptographic boundaries

Adaptive Core produces advisory observations, findings, reports, and proposals.
It does not verify Shield signatures, possess Shield keys, select Shield trust
registries, or grant execution authority. Its outputs cannot approve, override,
downgrade, bypass, or rescue a Shield or AdamantineOS result. AdamantineOS
remains the authoritative, fail-closed final policy and execution boundary.

Read-only describes that external authority limit. Local counters and explicit
artifact emission exist and are permitted by the unchanged contract. They do
not authorize wallet/node mutation, transaction signing or broadcasting,
automatic PR merges, or self-upgrades.

Report `classical_signature` and `pqc_signature` fields are caller-supplied
status metadata with exactly `ABSENT`, `PRESENT`, and `UNSUPPORTED`. They are
not signature bytes; `PRESENT` does not prove a valid signature. A report hash
establishes deterministic byte integrity, not authorship, authentication,
honest execution, or permission to execute.

Required Shield policy remains `classical-ed25519 + ml-dsa`; optional `fn-dsa`
uses Falcon-1024 under `fips206-draft-falcon1024-v1`. It cannot replace, rescue,
override, or downgrade required verification and is not final FIPS 206 proof.
Q-ID identity keys and Shield decision-evidence keys remain separate. Adaptive
Core describes these boundaries but does not enforce Shield cryptography.

There is no OQS dependency or OQS workflow in this repository. G2 makes no
live-OQS, production deployment, or cryptographic certification claim.
Statement coverage alone cannot establish those properties.

The second workflow, `Demo - Emit Upgrade Proposal`, is manual-only and emits
a demonstration artifact. It is unchanged and does not verify Shield, apply
an upgrade, or constitute an additional G2 release gate. Only the standard
`Adaptive Core Tests` workflow is required for this step.

## Frozen evidence and integrity

Shared fixture:

```text
tests/fixtures/adamantine/adaptive_core_adamantine_advisory_evidence_v1.json
SHA-256: 5b7d99ec53bfccca70b28c7bc286f388c966eb3ef33f1c1dac20b7eafac4b43d
```

The fixture and all runtime source, schemas, registries, and existing vectors
are unchanged. The G2 test builds the default advisory evidence and compares
it to this exact shared fixture after the package-version correction. All
existing exporter, rejection, replay-determinism, and boundary tests still run.

The source has no release-content manifest requiring a refresh. Package
content hashes are recomputed in the copy-package handoff; existing fixture
and registry integrity locks remain active and unchanged.

## Test evidence

| Gate | Result or required action |
|---|---|
| Source, local CPython 3.11.15 | 283 passed, zero skips/failures/errors |
| G2 candidate, local CPython 3.11.15 | 289 passed, zero skips/failures/errors |
| Statement coverage | 1505/1505, 100% |
| G2 release-truth tests | 6 passed |
| Proposal inbox validation | PASS, using the unchanged CI command |
| Post-commit workflow | `Adaptive Core Tests` on the complete G2 commit |
| Final source gate | Fresh post-commit ZIP matching the exact copy set |

Branch coverage is not configured or claimed. Tests run after editable
installation, with normal bytecode and generated metadata enabled. The new
copy-file check scans exactly its 11 payloads; generated files are not source
payloads. The existing repository-text and attribution checks remain active.

No skipped native tests are needed to explain this suite: Adaptive Core is
advisory-only and has no native-OQS test tier.

## Exact copy scope

3 NEW / 8 REPLACE / 0 DELETE; 116 unrelated source files remain byte-identical.

NEW:

- `CHANGELOG.md`
- `docs/RELEASE_STATUS_V4_10_G2.md`
- `tests/test_v410g2_release_truth.py`

REPLACE:

- `pyproject.toml`
- `README.md`
- `SECURITY.md`
- `docs/reports/INDEX.md`
- `docs/reports/v3/INDEX.md`
- `docs/reports/v3/README.md`
- `docs/reports/v3/ADAMANTINEOS_INTEGRATION.md`
- `tests/test_v49c_documentation_alignment.py`

All 11 payloads use ASCII and LF for manual transfer. Package metadata changes
only the version and description typography. The existing V4.9-C test changes
only its package-version assertion; all other assertions remain byte-identical.
Document headings and historical contract distinctions are retained. First-party
attribution remains DarekDGB only; the MIT license and third-party references
are preserved. No external repository, workflow, dependency requirement,
runtime, fixture, schema, or registry is changed.

## Completion gate and references

Upload all 11 files and commit the complete set. The single `Adaptive Core
Tests` workflow runs automatically on pushes to main; it has no manual-dispatch
control. Verify its proposal-inbox validation and 100% coverage on that exact
commit, then provide a fresh Adaptive Core ZIP. A prepared package or earlier
green run does not complete G2. G3 AI Gateway follows only after this gate.
No release tag is created or moved.

- [README](../README.md)
- [Changelog](../CHANGELOG.md)
- [Security policy](../SECURITY.md)
- [Reports index](reports/INDEX.md)
- [v3 index](reports/v3/INDEX.md)
- [Normative contract](reports/v3/CONTRACT.md)
- [Authority boundaries](reports/v3/AUTHORITY_BOUNDARIES.md)
- [AdamantineOS exporter](reports/v3/ADAMANTINEOS_INTEGRATION.md)
