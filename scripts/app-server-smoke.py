#!/usr/bin/env python3
"""Credential-free JSONL/stdio handshake smoke test for Codex app-server."""

import argparse
import json
import os
import selectors
import subprocess
import sys
import tempfile
import time
from pathlib import Path


NORMAL_SHUTDOWN_TIMEOUT_SECONDS = 3.0


def close_process_stdin(process: subprocess.Popen[str]) -> None:
    """Request normal app-server shutdown by delivering stdio EOF exactly once."""
    stdin = process.stdin
    if stdin is None:
        return
    try:
        stdin.close()
    except (BrokenPipeError, OSError):
        # A concurrently exiting child may close its side of the pipe first.
        pass
    finally:
        process.stdin = None


def fail(
    message: str,
    process: subprocess.Popen[str] | None = None,
    shutdown_timeout: float = NORMAL_SHUTDOWN_TIMEOUT_SECONDS,
) -> None:
    shutdown_timed_out = False
    if process is not None and process.poll() is None:
        close_process_stdin(process)
        try:
            process.wait(timeout=shutdown_timeout)
        except subprocess.TimeoutExpired:
            shutdown_timed_out = True
    if shutdown_timed_out:
        process_id = getattr(process, "pid", "unknown")
        message = (
            f"{message}\napp-server did not exit after stdin EOF within "
            f"{shutdown_timeout:g}s; process {process_id} was left running and no forced "
            "stop was attempted"
        )
    stderr = ""
    if (
        process is not None
        and not shutdown_timed_out
        and process.poll() is not None
        and process.stderr is not None
    ):
        stderr = process.stderr.read().strip()
    if stderr:
        message = f"{message}\napp-server stderr:\n{stderr}"
    raise SystemExit(message)


def read_runtime_version(binary: Path, timeout: float) -> str:
    process = subprocess.Popen(
        [str(binary), "--version"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        fail(
            "Runtime --version did not exit after stdin EOF",
            process,
            shutdown_timeout=0,
        )
    if process.returncode != 0:
        detail = stderr.strip()
        message = f"Runtime --version exited with status {process.returncode}"
        if detail:
            message = f"{message}\nRuntime stderr:\n{detail}"
        raise SystemExit(message)
    return stdout.strip()


def read_json_line(process: subprocess.Popen[str], timeout: float) -> dict:
    if process.stdout is None:
        fail("app-server stdout is unavailable", process)

    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                fail("Timed out waiting for the initialize response", process)
            events = selector.select(remaining)
            if not events:
                continue
            line = process.stdout.readline()
            if not line:
                fail(
                    f"app-server exited before initialize completed (exit={process.poll()})",
                    process,
                )
            try:
                message = json.loads(line)
            except json.JSONDecodeError as error:
                fail(f"app-server emitted invalid JSONL: {error}: {line!r}", process)
            if not isinstance(message, dict):
                fail(f"app-server emitted a non-object JSON value: {message!r}", process)
            return message
    finally:
        selector.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    args = parser.parse_args()

    binary = args.binary.resolve()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        fail(f"Runtime binary is not executable: {binary}")

    version = read_runtime_version(binary, args.timeout_seconds)
    if args.expected_version not in version:
        fail(f"Expected runtime {args.expected_version}, got {version!r}")

    with tempfile.TemporaryDirectory(prefix="yijie-codex-home-") as codex_home:
        environment = os.environ.copy()
        environment["CODEX_HOME"] = codex_home
        for name in (
            "OPENAI_API_KEY",
            "CODEX_API_KEY",
            "CODEX_ACCESS_TOKEN",
            "CHATGPT_ACCESS_TOKEN",
        ):
            environment.pop(name, None)

        process = subprocess.Popen(
            [
                str(binary),
                "app-server",
                "--listen",
                "stdio://",
                "--strict-config",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
            env=environment,
        )

        if process.stdin is None:
            fail("app-server stdin is unavailable", process)

        initialize = {
            "method": "initialize",
            "id": 0,
            "params": {
                "clientInfo": {
                    "name": "yijie_runtime_baseline",
                    "title": "Yijie Runtime Baseline",
                    "version": "0.1.0",
                },
                "capabilities": {"experimentalApi": False},
            },
        }
        process.stdin.write(json.dumps(initialize, separators=(",", ":")) + "\n")
        process.stdin.flush()

        response = read_json_line(process, args.timeout_seconds)
        if response.get("id") != 0:
            fail(f"Unexpected initialize response id: {response!r}", process)
        if "error" in response:
            fail(f"Initialize failed: {response['error']!r}", process)
        if not isinstance(response.get("result"), dict):
            fail(f"Initialize response has no result object: {response!r}", process)

        initialized = {"method": "initialized", "params": {}}
        process.stdin.write(json.dumps(initialized, separators=(",", ":")) + "\n")
        process.stdin.flush()
        close_process_stdin(process)

        try:
            return_code = process.wait(timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            fail("app-server did not exit after stdio closed", process, shutdown_timeout=0)
        if return_code != 0:
            fail(f"app-server exited with status {return_code}", process)

    print(f"Verified app-server stdio initialize/initialized handshake with {version}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
