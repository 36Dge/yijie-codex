#!/usr/bin/env python3
"""Replay the canonical patch chain into one stable incremental source directory."""
import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".local/web-retrieval-guard/workspace"


def main(manifest_script="write-answer-completion-runtime-manifest.py"):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("guard_manifest", ROOT / "scripts" / manifest_script)
    manifest = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(manifest)
    metadata = dict(line.split("=", 1) for line in (ROOT / ".yijie/upstream.env").read_text().splitlines() if "=" in line)
    with tempfile.TemporaryDirectory(prefix="yijie-guard-source-") as temporary:
        source = Path(temporary)
        archive = subprocess.Popen(["git", "-C", str(ROOT), "archive", metadata["YIJIE_CODEX_UPSTREAM_COMMIT"] + ":codex-rs"], stdout=subprocess.PIPE)
        extracted = subprocess.run(["tar", "-x", "-C", str(source)], stdin=archive.stdout)
        archive.stdout.close()
        if archive.wait() or extracted.returncode:
            raise SystemExit("Pinned source extraction failed")
        for patch in manifest.base.reviewed_patch_files(ROOT / ".yijie/patches", "input-only"):
            if False:
                baseline = ROOT / ".local/web-retrieval-guard/base"
                for saved in baseline.rglob("*"):
                    if saved.is_file():
                        saved.write_bytes((source / saved.relative_to(baseline)).read_bytes())
            subprocess.run(["git", "apply", "--check", str(patch)], cwd=source, check=True)
            subprocess.run(["git", "apply", str(patch)], cwd=source, check=True)
        env = {**os.environ, "CARGO_TARGET_DIR": str(ROOT / "codex-rs/target")}
        subprocess.run(["cargo", "metadata", "--offline", "--format-version", "1", "--filter-platform", "aarch64-apple-darwin"], cwd=source, env=env, stdout=subprocess.DEVNULL, check=True)
        WORK.mkdir(parents=True, exist_ok=True)
        for item in source.rglob("*"):
            relative = item.relative_to(source)
            target = WORK / relative
            if item.is_symlink():
                if not target.exists() and not target.is_symlink() and not args.check:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.symlink_to(os.readlink(item))
                elif not target.is_symlink() or os.readlink(target) != os.readlink(item):
                    raise SystemExit("Unexpected canonical source symlink difference")
            elif item.is_file():
                data = item.read_bytes()
                if target.is_symlink():
                    raise SystemExit("Canonical source target must be a regular file")
                if not target.exists() or target.read_bytes() != data:
                    if args.check:
                        raise SystemExit("Canonical source drift: " + str(relative))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
        for item in WORK.rglob("*"):
            if (item.is_file() or item.is_symlink()) and not (source / item.relative_to(WORK)).exists():
                raise SystemExit("Unexpected file in dedicated build source: " + str(item.relative_to(WORK)))
    print("Canonical execution guard source verified; stable incremental directory retained.")


if __name__ == "__main__":
    main()
