# Yijie Changelog

## Unreleased

- Establish Runtime Baseline 0 on upstream `rust-v0.144.6` commit `5d1fbf26c43abc65a203928b2e31561cb039e06d`.
- Materialize the exact upstream `codex-rs/` subtree with Apache-2.0 license and notice files.
- Keep the Yijie Runtime patch set empty and add byte-for-byte upstream verification.
- Add reproducible release build orchestration for macOS Apple Silicon and host-target CI.
- Audit the upstream release lock normalization without modifying the pinned source lockfile.
- Generate and canonicalize 267 stable app-server JSON Schema files.
- Add credential-free JSONL-over-stdio app-server handshake compatibility testing.
- Generate artifact manifests with source, binary, Schema, and build-lock SHA-256 records.
