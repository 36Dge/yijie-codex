#!/usr/bin/env python3
"""Check the neighboring Agent Host contract against this Runtime checkout."""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from runtime_manifest import sha256_tree


COMPATIBILITY_RELATIVE_PATH = Path("compatibility/agent-host-runtime-v1.json")
CANONICAL_RUNTIME_REPOSITORY = "https://github.com/36Dge/yijie-codex.git"
EXPECTED_RUNTIME_METHODS = [
    "thread/resume",
    "thread/start",
    "turn/interrupt",
    "turn/start",
]
EXPECTED_RUNTIME_NOTIFICATIONS = [
    "error",
    "item/agentMessage/delta",
    "item/completed",
    "item/started",
    "thread/started",
    "turn/completed",
    "turn/started",
    "warning",
]
EXPECTED_HOST_PROJECTION = {
    "transport": "local-http-sse",
    "authentication": "owner-only-bearer",
    "sandbox": "read-only",
    "approval_policy": "never",
    "runtime_methods": EXPECTED_RUNTIME_METHODS,
    "runtime_notifications": EXPECTED_RUNTIME_NOTIFICATIONS,
}

ROOT_KEYS = {"schema_version", "contracts_version", "runtime", "host_projection"}
RUNTIME_KEYS = {
    "repository",
    "repository_commit",
    "upstream_tag",
    "upstream_commit",
    "version",
    "transport",
    "experimental_api",
    "schema_file_count",
    "schema_tree_sha256",
}
PROJECTION_KEYS = {
    "transport",
    "authentication",
    "sandbox",
    "approval_policy",
    "runtime_methods",
    "runtime_notifications",
}
HEX_SHA_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_SHA_64 = re.compile(r"^[0-9a-f]{64}$")
CONTRACTS_VERSION = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)


class CompatibilityError(ValueError):
    """Raised when the contracts projection and Runtime are inconsistent."""


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise CompatibilityError(f"{label} is missing: {path}") from error
    except json.JSONDecodeError as error:
        raise CompatibilityError(f"{label} is not valid JSON: {path}: {error}") from error
    if not isinstance(value, dict):
        raise CompatibilityError(f"{label} must contain a JSON object: {path}")
    return value


def require_exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise CompatibilityError(f"{label} keys differ: missing={missing}, extra={extra}")


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected or type(actual) is not type(expected):
        raise CompatibilityError(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def validate_contract_manifest_shape(manifest: dict[str, Any]) -> None:
    require_exact_keys(manifest, ROOT_KEYS, "contracts manifest")
    require_equal(manifest["schema_version"], 1, "contracts manifest schema_version")
    contracts_version = manifest["contracts_version"]
    if not isinstance(contracts_version, str) or not CONTRACTS_VERSION.fullmatch(contracts_version):
        raise CompatibilityError(
            "contracts manifest contracts_version must be a semantic version, "
            f"got {contracts_version!r}"
        )

    runtime = manifest["runtime"]
    if not isinstance(runtime, dict):
        raise CompatibilityError("contracts manifest runtime must be an object")
    require_exact_keys(runtime, RUNTIME_KEYS, "contracts manifest runtime")
    for key in ("repository", "upstream_tag", "version", "transport"):
        if not isinstance(runtime[key], str) or not runtime[key]:
            raise CompatibilityError(f"contracts manifest runtime.{key} must be a string")
    for key in ("repository_commit", "upstream_commit"):
        if not isinstance(runtime[key], str) or not HEX_SHA_40.fullmatch(runtime[key]):
            raise CompatibilityError(f"contracts manifest runtime.{key} must be a full commit SHA")
    if type(runtime["experimental_api"]) is not bool:
        raise CompatibilityError("contracts manifest runtime.experimental_api must be a boolean")
    if type(runtime["schema_file_count"]) is not int or runtime["schema_file_count"] < 1:
        raise CompatibilityError("contracts manifest runtime.schema_file_count must be positive")
    if not isinstance(runtime["schema_tree_sha256"], str) or not HEX_SHA_64.fullmatch(
        runtime["schema_tree_sha256"]
    ):
        raise CompatibilityError(
            "contracts manifest runtime.schema_tree_sha256 must be a SHA-256 digest"
        )

    projection = manifest["host_projection"]
    if not isinstance(projection, dict):
        raise CompatibilityError("contracts manifest host_projection must be an object")
    require_exact_keys(projection, PROJECTION_KEYS, "contracts manifest host_projection")
    for key in ("transport", "authentication", "sandbox", "approval_policy"):
        if not isinstance(projection[key], str) or not projection[key]:
            raise CompatibilityError(f"contracts manifest host_projection.{key} must be a string")
    for key in ("runtime_methods", "runtime_notifications"):
        values = projection[key]
        if not isinstance(values, list) or not values:
            raise CompatibilityError(f"contracts manifest host_projection.{key} must be an array")
        if any(not isinstance(value, str) or not value for value in values):
            raise CompatibilityError(
                f"contracts manifest host_projection.{key} must contain non-empty strings"
            )
        if len(values) != len(set(values)):
            raise CompatibilityError(
                f"contracts manifest host_projection.{key} must not contain duplicates"
            )


def git_head(repo_root: Path) -> str:
    try:
        commit = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise CompatibilityError(f"cannot resolve yijie-codex HEAD at {repo_root}") from error
    if not HEX_SHA_40.fullmatch(commit):
        raise CompatibilityError(f"yijie-codex HEAD is not a full commit SHA: {commit!r}")
    return commit


def schema_methods(path: Path, label: str) -> set[str]:
    schema = load_json(path, label)
    branches = schema.get("oneOf")
    if not isinstance(branches, list) or not branches:
        raise CompatibilityError(f"{label} must contain a non-empty oneOf")

    methods: set[str] = set()
    for index, branch in enumerate(branches):
        if not isinstance(branch, dict):
            raise CompatibilityError(f"{label} oneOf[{index}] must be an object")
        properties = branch.get("properties")
        method = properties.get("method") if isinstance(properties, dict) else None
        enum = method.get("enum") if isinstance(method, dict) else None
        if not isinstance(enum, list) or len(enum) != 1 or not isinstance(enum[0], str):
            raise CompatibilityError(
                f"{label} oneOf[{index}] must expose exactly one string method enum"
            )
        if enum[0] in methods:
            raise CompatibilityError(f"{label} contains duplicate method {enum[0]!r}")
        methods.add(enum[0])
    return methods


def validate_runtime_artifact(
    runtime_manifest_path: Path,
    expected_runtime: dict[str, Any],
) -> None:
    artifact = load_json(runtime_manifest_path, "Runtime artifact manifest")
    upstream = artifact.get("upstream")
    runtime = artifact.get("runtime")
    app_server = artifact.get("appServer")
    if not isinstance(upstream, dict) or not isinstance(runtime, dict) or not isinstance(
        app_server, dict
    ):
        raise CompatibilityError(
            "Runtime artifact manifest must contain upstream, runtime, and appServer objects"
        )

    comparisons = {
        "upstream.tag": (upstream.get("tag"), expected_runtime["upstream_tag"]),
        "upstream.commit": (upstream.get("commit"), expected_runtime["upstream_commit"]),
        "runtime.version": (runtime.get("version"), expected_runtime["version"]),
        "appServer.transport": (app_server.get("transport"), expected_runtime["transport"]),
        "appServer.experimentalApi": (
            app_server.get("experimentalApi"),
            expected_runtime["experimental_api"],
        ),
        "appServer.schemaFileCount": (
            app_server.get("schemaFileCount"),
            expected_runtime["schema_file_count"],
        ),
        "appServer.schemaTreeSha256": (
            app_server.get("schemaTreeSha256"),
            expected_runtime["schema_tree_sha256"],
        ),
    }
    for label, (actual, expected) in comparisons.items():
        require_equal(actual, expected, f"Runtime artifact manifest {label}")


def validate_compatibility(
    repo_root: Path,
    contracts_manifest_path: Path,
    runtime_manifest_path: Path | None = None,
    repository_commit: str | None = None,
) -> None:
    manifest = load_json(contracts_manifest_path, "Agent Host contracts compatibility manifest")
    validate_contract_manifest_shape(manifest)

    baseline_path = repo_root / ".yijie/schemas/app-server/baseline.json"
    schema_dir = repo_root / ".yijie/schemas/app-server/generated-json-schema"
    baseline = load_json(baseline_path, "app-server baseline")
    if not schema_dir.is_dir():
        raise CompatibilityError(f"app-server Schema directory is missing: {schema_dir}")
    schema_files = sorted(path for path in schema_dir.rglob("*.json") if path.is_file())
    if not schema_files:
        raise CompatibilityError(f"app-server Schema directory contains no JSON files: {schema_dir}")

    expected_runtime = {
        "repository": CANONICAL_RUNTIME_REPOSITORY,
        "repository_commit": repository_commit or git_head(repo_root),
        "upstream_tag": baseline.get("upstreamTag"),
        "upstream_commit": baseline.get("upstreamCommit"),
        "version": baseline.get("runtimeVersion"),
        "transport": baseline.get("transport"),
        "experimental_api": baseline.get("experimentalApi"),
        "schema_file_count": len(schema_files),
        "schema_tree_sha256": sha256_tree(schema_dir),
    }
    for key, expected in expected_runtime.items():
        require_equal(manifest["runtime"].get(key), expected, f"contracts manifest runtime.{key}")

    require_equal(
        manifest["host_projection"],
        EXPECTED_HOST_PROJECTION,
        "contracts manifest host_projection",
    )

    client_methods = schema_methods(schema_dir / "ClientRequest.json", "ClientRequest Schema")
    server_notifications = schema_methods(
        schema_dir / "ServerNotification.json", "ServerNotification Schema"
    )
    missing_methods = sorted(set(EXPECTED_RUNTIME_METHODS) - client_methods)
    missing_notifications = sorted(set(EXPECTED_RUNTIME_NOTIFICATIONS) - server_notifications)
    if missing_methods:
        raise CompatibilityError(
            f"Agent Host Runtime methods are missing from ClientRequest Schema: {missing_methods}"
        )
    if missing_notifications:
        raise CompatibilityError(
            "Agent Host Runtime notifications are missing from ServerNotification Schema: "
            f"{missing_notifications}"
        )

    if runtime_manifest_path is not None:
        validate_runtime_artifact(runtime_manifest_path, expected_runtime)


def check_sibling(
    repo_root: Path,
    contracts_repo: Path,
    runtime_manifest_path: Path | None = None,
) -> bool:
    if not contracts_repo.exists():
        print(
            "SKIP: Agent Host contracts compatibility check; sibling yijie-contracts "
            f"checkout is unavailable at {contracts_repo}"
        )
        return False
    contracts_manifest_path = contracts_repo / COMPATIBILITY_RELATIVE_PATH
    if not contracts_manifest_path.is_file():
        raise CompatibilityError(
            "sibling yijie-contracts checkout exists but its Runtime compatibility manifest "
            f"is missing: {contracts_manifest_path}"
        )
    validate_compatibility(repo_root, contracts_manifest_path, runtime_manifest_path)
    print(f"Agent Host contracts compatibility passed: {contracts_manifest_path}")
    return True


def main() -> int:
    default_repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument(
        "--contracts-repo",
        type=Path,
        default=None,
        help="yijie-contracts checkout (default: YIJIE_CONTRACTS_REPO or sibling checkout)",
    )
    parser.add_argument("--runtime-manifest", type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    contracts_repo = args.contracts_repo
    if contracts_repo is None:
        configured = os.environ.get("YIJIE_CONTRACTS_REPO")
        contracts_repo = Path(configured) if configured else repo_root.parent / "yijie-contracts"
    try:
        check_sibling(
            repo_root,
            contracts_repo.resolve(),
            args.runtime_manifest.resolve() if args.runtime_manifest else None,
        )
    except CompatibilityError as error:
        print(f"Agent Host contracts compatibility failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
