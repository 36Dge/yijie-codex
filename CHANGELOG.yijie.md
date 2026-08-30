# Yijie Changelog

## Unreleased

- Add the Owner-authorized FEAT-136 candidate patch `0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch` after FEAT-126 `0001`. It emits one canonical Command `item/started` followed by one failed `item/completed` when final early sandbox denial previously returned before emitter creation, while preserving the original error, nonzero exit details, retry/approval decisions, sandbox, and permissions.
- Classify the FEAT-136 Runtime change as `semantic`: isolated macOS Apple Silicon release build and schema regeneration confirm the stable app-server Schema remains 267 files with no tracked diff. Focused core, four safe fake exec-server scenarios, focused app-server-protocol, fmt, scoped clippy, fork-management, normal-EOF stdio smoke, and Runtime→Contracts checks pass; downstream Host/Desktop conformance is not yet claimed.
- Require the exact ordered `0001` → `0002` overlay in patch replay and Runtime manifests, and make the credential-free app-server smoke harness close by stdin EOF without terminate/kill fallback.
- Keep Contracts `3c3000a6fbe2f08ab2131a463a1691e867d661b1` as historical provenance only until a new immutable candidate repins the repaired Runtime and confirmed Schema digest. Tool D4 remains blocked and was not run.
- Add a replayable FEAT-126 Runtime patch that excludes path-bearing HTTP, stream, shell, rollout, core utility, and feedback diagnostic targets from persistent SQLite logs while retaining reviewed state and app-server sub-target logs.
- Bind the reviewed patch path and SHA-256 into the Runtime artifact manifest and apply it only inside disposable build workspaces.
- Add a bidirectional `yijie-contracts` compatibility gate that pins the Runtime source, stable Schema tree, and exact Agent Host method/notification projection while remaining optional for standalone checkouts.
- Ignore local `.DS_Store` metadata consistently in upstream sync and zero-patch source verification while retaining all substantive source-drift checks.
- Establish Runtime Baseline 0 on upstream `rust-v0.144.6` commit `5d1fbf26c43abc65a203928b2e31561cb039e06d`.
- Materialize the exact upstream `codex-rs/` subtree with Apache-2.0 license and notice files.
- Keep canonical `codex-rs/` byte-for-byte equal to upstream and verify any Yijie overlay independently.
- Add reproducible release build orchestration for macOS Apple Silicon and host-target CI.
- Audit the upstream release lock normalization without modifying the pinned source lockfile.
- Generate and canonicalize 267 stable app-server JSON Schema files.
- Add credential-free JSONL-over-stdio app-server handshake compatibility testing.
- Generate artifact manifests with source, binary, Schema, and build-lock SHA-256 records.
