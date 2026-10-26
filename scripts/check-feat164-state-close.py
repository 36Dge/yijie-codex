#!/usr/bin/env python3
"""Normal zero-turn EOF qualification; preserve every home, DB and WAL on all outcomes."""
import argparse
import datetime
import hashlib
import json
import os
import re
from pathlib import Path
import selectors
import shutil
import sqlite3
import subprocess
import time

CONFIG = '''model = "kimi-k3.1-pro"
model_provider = "kimi"
model_reasoning_effort = "max"
model_context_window = 1048576
input_only = true
cli_auth_credentials_store = "file"
approval_policy = "never"
sandbox_mode = "read-only"
web_search = "disabled"
[analytics]
enabled = false
[feedback]
enabled = false
[features]
hooks = false
plugins = false
apps = false
tool_suggest = false
shell_snapshot = false
memories = false
[model_providers.kimi]
name = "FEAT164 zero-turn lifecycle qualification"
base_url = "http://127.0.0.1:9/v1"
wire_api = "responses"
requires_openai_auth = false
supports_websockets = false
request_max_retries = 0
stream_max_retries = 0
'''
DATABASES = ("state_5.sqlite", "logs_2.sqlite", "goals_1.sqlite", "memories_1.sqlite")


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    binary = args.binary.resolve()
    manifest = json.loads(args.manifest.read_text())
    if sha(binary) != manifest["runtime"]["sha256"]:
        raise SystemExit("binary does not match its manifest")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    home = output / "runtime-home"
    home.mkdir()
    (home / "config.toml").write_text(CONFIG)
    env = {key: os.environ[key] for key in ("PATH", "HOME", "TMPDIR") if key in os.environ}
    env.update(CODEX_HOME=str(home), CODEX_INTERNAL_APP_SERVER_REMOTE_CONTROL_DISABLED="1",
               RUST_LOG="codex_app_server=info,codex_app_server_transport=debug")
    result = {"started_at": datetime.datetime.now().astimezone().isoformat(),
              "binary_sha256": sha(binary), "manifest_sha256": sha(args.manifest),
              "real_model_http_added": 0, "turn_start_requests": 0, "signals_sent": [],
              "manual_checkpoint": False, "files_deleted": False, "methods": [],
              "scope": "credential-free input-only loaded thread, no turns; native listener lifecycle"}
    stderr = (output / "stderr.log").open("wb")
    process = subprocess.Popen([str(binary), "app-server", "--listen", "stdio://", "--strict-config"],
                               cwd=home, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
    result["pid"] = process.pid
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    pending = b""
    events = []

    def request(method, params, request_id=None):
        nonlocal pending
        payload = {"method": method, "params": params}
        if request_id is not None:
            payload["id"] = request_id
        result["methods"].append(method)
        process.stdin.write((json.dumps(payload) + "\n").encode())
        process.stdin.flush()
        if request_id is None:
            return None
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                if not line:
                    continue
                event = json.loads(line)
                events.append(event)
                if event.get("id") == request_id:
                    if "error" in event:
                        raise RuntimeError("native RPC returned error for " + method)
                    return event["result"]
            if selector.select(min(1, max(0, deadline - time.monotonic()))):
                chunk = os.read(process.stdout.fileno(), 65536)
                if not chunk:
                    raise RuntimeError("native stdout ended before RPC result")
                pending += chunk
        raise RuntimeError("native RPC observation deadline reached")

    failure = None
    try:
        request("initialize", {"clientInfo": {"name": "feat164_state_close", "version": "0.1.0"},
                               "capabilities": {"experimentalApi": False}}, 1)
        request("initialized", {})
        started = request("thread/start", {"model": "kimi-k3.1-pro", "modelProvider": "kimi",
                                           "cwd": str(home), "approvalPolicy": "never", "sandbox": "read-only"}, 2)
        thread_id = started["thread"]["id"]
        if started["model"] != "kimi-k3.1-pro" or started["modelProvider"] != "kimi":
            raise RuntimeError("unexpected native model identity")
        result["thread_id"] = thread_id
        read = request("thread/read", {"threadId": thread_id, "includeTurns": False}, 3)
        if read["thread"]["id"] != thread_id:
            raise RuntimeError("native loaded thread identity mismatch")
        result["loaded_thread_read"] = True
    except (OSError, RuntimeError, KeyError, ValueError) as error:
        failure = str(error)
    finally:
        process.stdin.close()
        try:
            result["exit_code"] = process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            failure = "normal EOF still pending; process and all files retained"
            result["process_retained"] = True
        selector.close()
        stderr.close()
        (output / "native-events.json").write_text(json.dumps(events, indent=2) + "\n")
    if result.get("exit_code") != 0:
        failure = failure or "native process did not exit successfully"
    if result.get("exit_code") == 0:
        lines = re.sub(r"\x1b\[[0-9;]*m", "", (output / "stderr.log").read_text()).splitlines()
        result["normal_exit_trace"] = [line for line in lines if any(marker in line for marker in
            ("stdin reader finished", "processor task exited", "outbound router task exited"))]
        if not any("last_connection_closed" in line and "shutdown_forced=false" in line
                   for line in result["normal_exit_trace"]):
            failure = failure or "normal stdio cleanup trace not confirmed"
    result["databases"] = []
    if result.get("exit_code") == 0:
        snapshot = output / "readonly-snapshot"
        snapshot.mkdir()
        for name in DATABASES:
            db = home / name
            files = [home / (name + suffix) for suffix in ("", "-wal", "-shm")]
            existing = [path for path in files if path.exists()]
            before = {path.name: sha(path) for path in existing}
            record = {"name": name, "before": before}
            if not db.exists():
                failure = failure or "expected state database missing"
                result["databases"].append(record)
                continue
            # This owned empty-home check has no external reader or persistent-WAL setting.
            # Check before any SQLite open; a leftover is retained and fails qualification.
            wal = home / (name + "-wal")
            record["wal_bytes_after_exit"] = wal.stat().st_size if wal.exists() else 0
            if record["wal_bytes_after_exit"]:
                failure = failure or "owned state WAL not checkpointed after normal EOF"
            for path in existing:
                shutil.copyfile(path, snapshot / path.name)
            connection = sqlite3.connect((snapshot / name).as_uri() + "?mode=ro", uri=True)
            try:
                connection.execute("PRAGMA query_only=ON")
                record["integrity"] = connection.execute("PRAGMA integrity_check").fetchall()
                if record["integrity"] != [("ok",)]:
                    failure = failure or "readonly snapshot integrity check failed"
            finally:
                connection.close()
            record["source_files_unchanged_by_inspection"] = before == {path.name: sha(path) for path in existing}
            if not record["source_files_unchanged_by_inspection"]:
                failure = failure or "source database changed during inspection"
            result["databases"].append(record)
    result["failure"] = failure
    result["status"] = "PASS_SCOPED" if failure is None else "FAIL"
    result["finished_at"] = datetime.datetime.now().astimezone().isoformat()
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "exit_code": result.get("exit_code"),
                      "real_model_http_added": 0, "output": str(output), "failure": failure}))
    return 0 if failure is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
