# FEAT-164 Kimi K3.1 Pro isolated candidate

Owner approved FEAT-164 implementation. This candidate remains inactive until Contracts/Host/Desktop compatibility and governance gates pass. Overall migration impact is breaking; the new Runtime request guard and search-source predicate are a minimal semantic change with no intended app-server schema change.

Keep upstream `rust-v0.144.6` / `5d1fbf26c43abc65a203928b2e31561cb039e06d`, Rust 1.95.0, and patches 0001–0006 unchanged. Apply `chat-models/0007-feat-164-kimi-k31-pro.patch` last in the temporary build source. It rejects `kimi-k3` before constructing a new Responses request and asks for real search sources for `kimi-k3.1-pro`. Historical text and model records are not rewritten. This guard does not replace Host/Native retirement and migration checks.

Canonical command: `bash scripts/build-kimi-k31-pro.sh`. Output: `.yijie/build/kimi-k31-pro-r1/aarch64-apple-darwin`. Existing binary/manifest is never overwritten. It uses standard builds and the established cache, checks the reviewed patch digests, runs only reviewed ordinary focused tests, generates a manifest/schema, compares the schema to the retained web-sources candidate, and checks stdio startup with normal EOF shutdown. It makes no authenticated model request.

Validation status belongs in the FEAT-164 implementation record; do not infer success from this document or the presence of an output directory. Existing production/consumer pins and default launchers are not switched by this build.
