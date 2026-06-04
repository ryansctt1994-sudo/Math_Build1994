#!/usr/bin/env python3
"""Repository self-check for Math_Build1994.

This is a lightweight deterministic guard for CI and local debugging. It checks
that required files exist and that JSON policy/receipt-governance artifacts parse.
It intentionally does not replace `lake build MathBuild`.
"""

from __future__ import annotations

import json
from pathlib import Path


REQUIRED_FILES = [
    "lakefile.lean",
    "lean-toolchain",
    "MathBuild/IrrationalSqrt2.lean",
    "schemas/constitutional_receipt.schema.json",
    "scripts/generate_build_receipt.py",
    "scripts/replay_build.py",
    "scripts/verify_receipt.py",
    "receipts/replay/replay_matrix.json",
    "TRUSTED_KEYS.json",
    "SIGNING_POLICY.md",
    ".github/workflows/lean-build.yml",
    ".github/workflows/replay.yml",
]

JSON_FILES = [
    "schemas/constitutional_receipt.schema.json",
    "receipts/replay/replay_matrix.json",
    "TRUSTED_KEYS.json",
]


def main() -> int:
    errors: list[str] = []

    for item in REQUIRED_FILES:
        if not Path(item).exists():
            errors.append(f"missing required file: {item}")

    for item in JSON_FILES:
        path = Path(item)
        if not path.exists():
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid JSON in {item}: {exc}")

    toolchain = Path("lean-toolchain")
    if toolchain.exists():
        value = toolchain.read_text(encoding="utf-8").strip()
        if not value.startswith("leanprover/lean4:"):
            errors.append("lean-toolchain must pin a concrete leanprover/lean4 version")

    if errors:
        print("Repository self-check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository self-check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
