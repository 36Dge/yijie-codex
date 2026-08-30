#!/usr/bin/env python3
"""Safety regression tests for the credential-free app-server smoke harness."""

import ast
import importlib.util
import io
import subprocess
import unittest
from pathlib import Path
from types import ModuleType


SCRIPT_PATH = Path(__file__).with_name("app-server-smoke.py")


def load_smoke_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("app_server_smoke", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load smoke module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeStdin:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class FakeStderr(io.StringIO):
    def __init__(self, process: "FakeProcess") -> None:
        super().__init__("benign stderr\n")
        self.process = process

    def read(self, *args: object, **kwargs: object) -> str:
        if self.process.returncode is None:
            raise AssertionError("stderr must not be read while the child is still running")
        return super().read(*args, **kwargs)


class FakeProcess:
    def __init__(self, *, time_out: bool = False) -> None:
        self.pid = 4242
        self.stdin_stream = FakeStdin()
        self.stdin = self.stdin_stream
        self.returncode: int | None = None
        self.wait_calls: list[float] = []
        self.time_out = time_out
        self.stderr = FakeStderr(self)

    def poll(self) -> int | None:
        return self.returncode

    def wait(self, timeout: float) -> int:
        self.wait_calls.append(timeout)
        if not self.stdin_stream.closed:
            raise AssertionError("normal shutdown must close stdin before waiting")
        if self.time_out:
            raise subprocess.TimeoutExpired("fake-app-server", timeout)
        self.returncode = 0
        return self.returncode


class AppServerSmokeSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.smoke = load_smoke_module()

    def test_failure_requests_normal_shutdown_with_stdin_eof(self) -> None:
        process = FakeProcess()
        with self.assertRaises(SystemExit) as raised:
            self.smoke.fail("expected failure", process, shutdown_timeout=0.25)
        self.assertIsNone(process.stdin)
        self.assertTrue(process.stdin_stream.closed)
        self.assertEqual(process.wait_calls, [0.25])
        self.assertIn("expected failure", str(raised.exception))
        self.assertIn("benign stderr", str(raised.exception))

    def test_shutdown_timeout_reports_without_reading_live_stderr(self) -> None:
        process = FakeProcess(time_out=True)
        with self.assertRaises(SystemExit) as raised:
            self.smoke.fail("expected timeout", process, shutdown_timeout=0.25)
        self.assertIsNone(process.stdin)
        self.assertTrue(process.stdin_stream.closed)
        self.assertEqual(process.wait_calls, [0.25])
        self.assertIn("did not exit after stdin EOF", str(raised.exception))
        self.assertIn("process 4242 was left running", str(raised.exception))
        self.assertIn("no forced stop was attempted", str(raised.exception))

    def test_smoke_harness_contains_no_process_signal_calls(self) -> None:
        tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"), filename=str(SCRIPT_PATH))
        forbidden = {"kill", "terminate", "send_signal"}
        calls = [
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in forbidden
        ]
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
