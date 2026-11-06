# Host image candidate

FEAT-168 extends native-public-messages-r3 with ordered patch 0019. The local thread override `yijie_host_images` is off by default. On the managed Kimi and MiniMax profiles, an opted-in ordinary thread uses the native image executor with a flat function spec. Input-only turns and subagents do not gain the tool.

`item/imageGeneration/generate` runs over the existing app-server request channel, directed to the sole subscriber of that thread. The input carries thread, turn and call identity, prompt and whether to use the current attachment. The response is a success boolean. The Host controls attachment access, secrets, cancellation and Artifact storage. Ordinary OpenAI image behavior continues to use the upstream backend.

Run `bash scripts/build-host-images.sh` for a new isolated local artifact. The script replays the fixed upstream and patch chain, builds offline with the normalized lock, checks replay and exports the canonical schema and manifest. Then run `node scripts/generate-runtime-host-images.mjs` in the Contracts repository to project the new candidate. Reverting a candidate means stop admitting its new calls and retain the existing artifact reader; do not restore an old image producer.
