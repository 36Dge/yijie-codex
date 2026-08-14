# Yijie Changelog

## Unreleased

- Add a replayable FEAT-126 Runtime patch that excludes path-bearing diagnostic target families from persistent SQLite logs while retaining reviewed state and app-server sub-target logs.
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
