#!/usr/bin/env python3
"""Unit tests for the Runtime manifest's exact reviewed patch allowlist."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import ModuleType


SCRIPT_PATH = Path(__file__).with_name("write-runtime-manifest.py")


def load_manifest_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("write_runtime_manifest", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load manifest module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeManifestPatchSetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_manifest_module()
        self.temporary = tempfile.TemporaryDirectory(prefix="yijie-runtime-patches-")
        self.patch_dir = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_patch(self, name: str) -> None:
        (self.patch_dir / name).write_text("benign patch fixture\n", encoding="utf-8")

    def test_accepts_only_the_exact_ordered_feat126_feat136_patch_set(self) -> None:
        for name in reversed(self.manifest.EXPECTED_PATCH_NAMES):
            self.write_patch(name)
        patches = self.manifest.reviewed_patch_files(self.patch_dir)
        self.assertEqual(
            [patch.name for patch in patches],
            list(self.manifest.EXPECTED_PATCH_NAMES),
        )

    def test_rejects_missing_extra_or_renamed_patch(self) -> None:
        cases = (
            self.manifest.EXPECTED_PATCH_NAMES[:1],
            (*self.manifest.EXPECTED_PATCH_NAMES, "0003-unreviewed.patch"),
            (*self.manifest.EXPECTED_PATCH_NAMES, ".0003-hidden.patch"),
            (*self.manifest.EXPECTED_PATCH_NAMES, ".patch"),
            (
                self.manifest.EXPECTED_PATCH_NAMES[0],
                "0002-renamed.patch",
            ),
        )
        for index, names in enumerate(cases):
            with self.subTest(names=names):
                case_dir = self.patch_dir / str(index)
                case_dir.mkdir()
                for name in names:
                    (case_dir / name).write_text("benign patch fixture\n", encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "exact ordered"):
                    self.manifest.reviewed_patch_files(case_dir)


if __name__ == "__main__":
    unittest.main(verbosity=2)
