#!/usr/bin/env python3
"""Unit tests for the Agent Host contracts compatibility gate."""

import copy
import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from check_agent_host_contracts import (
    CANONICAL_RUNTIME_REPOSITORY,
    COMPATIBILITY_RELATIVE_PATH,
    EXPECTED_HOST_PROJECTION,
    EXPECTED_RUNTIME_METHODS,
    EXPECTED_RUNTIME_NOTIFICATIONS,
    CompatibilityError,
    check_sibling,
    validate_compatibility,
)
from runtime_manifest import sha256_tree


COMMIT = "a" * 40
UPSTREAM_COMMIT = "b" * 40


class Fixture:
    def __init__(self, root: Path) -> None:
        self.repo_root = root / "yijie-codex"
        self.contracts_repo = root / "yijie-contracts"
        self.schema_dir = self.repo_root / ".yijie/schemas/app-server/generated-json-schema"
        self.baseline_path = self.repo_root / ".yijie/schemas/app-server/baseline.json"
        self.contracts_path = self.contracts_repo / COMPATIBILITY_RELATIVE_PATH
        self.runtime_manifest_path = root / "runtime-manifest.json"

        self.schema_dir.mkdir(parents=True)
        self.contracts_path.parent.mkdir(parents=True)
        self.write_json(
            self.schema_dir / "ClientRequest.json",
            self.method_schema(EXPECTED_HOST_PROJECTION["runtime_methods"]),
        )
        self.write_json(
            self.schema_dir / "ServerNotification.json",
            self.method_schema(EXPECTED_HOST_PROJECTION["runtime_notifications"]),
        )
        self.write_json(
            self.baseline_path,
            {
                "schemaVersion": 1,
                "upstreamTag": "rust-v0.144.6",
                "upstreamCommit": UPSTREAM_COMMIT,
                "runtimeVersion": "0.144.6",
                "experimentalApi": False,
                "transport": "stdio",
            },
        )
        self.manifest = {
            "schema_version": 1,
            "contracts_version": "0.7.0",
            "runtime": {
                "repository": CANONICAL_RUNTIME_REPOSITORY,
                "repository_commit": COMMIT,
                "upstream_tag": "rust-v0.144.6",
                "upstream_commit": UPSTREAM_COMMIT,
                "version": "0.144.6",
                "transport": "stdio",
                "experimental_api": False,
                "schema_file_count": 2,
                "schema_tree_sha256": sha256_tree(self.schema_dir),
            },
            "host_projection": copy.deepcopy(EXPECTED_HOST_PROJECTION),
        }
        self.runtime_manifest = {
            "upstream": {
                "tag": "rust-v0.144.6",
                "commit": UPSTREAM_COMMIT,
            },
            "runtime": {"version": "0.144.6"},
            "appServer": {
                "transport": "stdio",
                "experimentalApi": False,
                "schemaFileCount": 2,
                "schemaTreeSha256": self.manifest["runtime"]["schema_tree_sha256"],
            },
        }
        self.flush()

    @staticmethod
    def method_schema(methods: list[str]) -> dict[str, object]:
        return {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {"method": {"type": "string", "enum": [method]}},
                }
                for method in methods
            ]
        }

    @staticmethod
    def write_json(path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")

    def flush(self) -> None:
        self.write_json(self.contracts_path, self.manifest)
        self.write_json(self.runtime_manifest_path, self.runtime_manifest)


class AgentHostContractsCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="yijie-contracts-check-")
        self.fixture = Fixture(Path(self.temporary.name))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def validate(self) -> None:
        self.fixture.flush()
        validate_compatibility(
            self.fixture.repo_root,
            self.fixture.contracts_path,
            self.fixture.runtime_manifest_path,
            repository_commit=COMMIT,
        )

    def test_valid_manifest_matches_source_schemas_and_runtime_artifact(self) -> None:
        self.validate()

    def test_expected_projection_is_exactly_contracts_v070(self) -> None:
        self.assertEqual(
            EXPECTED_RUNTIME_METHODS,
            [
                "skills/config/write",
                "skills/extraRoots/set",
                "skills/list",
                "thread/resume",
                "thread/start",
                "turn/interrupt",
                "turn/start",
            ],
        )
        self.assertEqual(
            EXPECTED_RUNTIME_NOTIFICATIONS,
            [
                "error",
                "item/agentMessage/delta",
                "item/commandExecution/outputDelta",
                "item/completed",
                "item/mcpToolCall/progress",
                "item/reasoning/textDelta",
                "item/started",
                "skills/changed",
                "thread/started",
                "turn/completed",
                "turn/plan/updated",
                "turn/started",
                "warning",
            ],
        )

    def test_missing_sibling_is_an_explicit_non_blocking_skip(self) -> None:
        missing = Path(self.temporary.name) / "not-checked-out"
        output = io.StringIO()
        with redirect_stdout(output):
            checked = check_sibling(self.fixture.repo_root, missing)
        self.assertFalse(checked)
        self.assertIn("SKIP", output.getvalue())
        self.assertIn("unavailable", output.getvalue())

    def test_existing_sibling_without_manifest_fails(self) -> None:
        empty_repo = Path(self.temporary.name) / "empty-contracts"
        empty_repo.mkdir()
        with self.assertRaisesRegex(CompatibilityError, "manifest is missing"):
            check_sibling(self.fixture.repo_root, empty_repo)

    def test_runtime_identity_mismatches_fail(self) -> None:
        mutations = {
            "repository": "https://example.invalid/runtime.git",
            "repository_commit": "c" * 40,
            "upstream_tag": "rust-v9.9.9",
            "upstream_commit": "d" * 40,
            "version": "9.9.9",
            "transport": "websocket",
            "experimental_api": True,
            "schema_file_count": 3,
            "schema_tree_sha256": "e" * 64,
        }
        for key, bad_value in mutations.items():
            with self.subTest(key=key):
                original = self.fixture.manifest["runtime"][key]
                self.fixture.manifest["runtime"][key] = bad_value
                with self.assertRaisesRegex(CompatibilityError, re.escape(f"runtime.{key}")):
                    self.validate()
                self.fixture.manifest["runtime"][key] = original

    def test_projected_method_and_notification_sets_are_exact(self) -> None:
        for key in ("runtime_methods", "runtime_notifications"):
            with self.subTest(key=key):
                original = self.fixture.manifest["host_projection"][key]
                self.fixture.manifest["host_projection"][key] = original[:-1]
                with self.assertRaisesRegex(CompatibilityError, "host_projection"):
                    self.validate()
                self.fixture.manifest["host_projection"][key] = original

    def test_projected_protocol_member_must_exist_in_generated_schema(self) -> None:
        client_schema = self.fixture.schema_dir / "ClientRequest.json"
        value = json.loads(client_schema.read_text(encoding="utf-8"))
        value["oneOf"] = value["oneOf"][:-1]
        Fixture.write_json(client_schema, value)
        self.fixture.manifest["runtime"]["schema_tree_sha256"] = sha256_tree(
            self.fixture.schema_dir
        )
        self.fixture.runtime_manifest["appServer"]["schemaTreeSha256"] = self.fixture.manifest[
            "runtime"
        ]["schema_tree_sha256"]
        with self.assertRaisesRegex(CompatibilityError, "methods are missing"):
            self.validate()

    def test_projected_notification_must_exist_in_generated_schema(self) -> None:
        notification_schema = self.fixture.schema_dir / "ServerNotification.json"
        value = json.loads(notification_schema.read_text(encoding="utf-8"))
        value["oneOf"] = value["oneOf"][:-1]
        Fixture.write_json(notification_schema, value)
        self.fixture.manifest["runtime"]["schema_tree_sha256"] = sha256_tree(
            self.fixture.schema_dir
        )
        self.fixture.runtime_manifest["appServer"]["schemaTreeSha256"] = self.fixture.manifest[
            "runtime"
        ]["schema_tree_sha256"]
        with self.assertRaisesRegex(CompatibilityError, "notifications are missing"):
            self.validate()

    def test_runtime_artifact_is_checked_against_the_same_schema_facts(self) -> None:
        self.fixture.runtime_manifest["appServer"]["schemaTreeSha256"] = "f" * 64
        with self.assertRaisesRegex(CompatibilityError, "Runtime artifact manifest"):
            self.validate()


if __name__ == "__main__":
    unittest.main(verbosity=2)
