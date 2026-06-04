#!/usr/bin/env python3
"""Generate a constitutional receipt for a Lean build.

This script is intentionally deterministic apart from timestamp and generated UUID.
It does not prove the build succeeded. It records a build result supplied by the caller.
In CI, call it only after `lake build MathBuild` succeeds.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = "ryansctt1994-sudo/Math_Build1994"
DEFAULT_TOOLCHAIN = "lean-toolchain"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_text(cmd: list[str], default: str = "UNKNOWN") -> str:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return default


def file_sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path, default: str = "UNKNOWN") -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return default


def environment_snapshot(toolchain: str, lake_manifest_hash: str | None) -> dict[str, str]:
    lean_version = run_text(["bash", "-lc", "lake env lean --version"])
    lake_version = run_text(["bash", "-lc", "lake --version"])
    uname = run_text(["bash", "-lc", "uname -a"])
    return {
        "os": platform.platform(),
        "uname": uname,
        "python_version": platform.python_version(),
        "lean_version": lean_version,
        "lake_version": lake_version,
        "toolchain": toolchain,
        "lake_manifest_hash": lake_manifest_hash or "UNKNOWN",
        "container_hash": os.environ.get("CONTAINER_HASH", "UNPINNED_SAME_ENVIRONMENT_REPLAY"),
    }


def environment_hash(snapshot: dict[str, str]) -> str:
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_receipt(result: str, command: str, output_path: Path) -> dict[str, Any]:
    commit = os.environ.get("GITHUB_SHA") or run_text(["git", "rev-parse", "HEAD"])
    toolchain = read_text(Path(DEFAULT_TOOLCHAIN))
    lake_manifest_hash = file_sha256(Path("lake-manifest.json"))
    lakefile_hash = file_sha256(Path("lakefile.lean"))
    env_snapshot = environment_snapshot(toolchain, lake_manifest_hash)
    env_hash = environment_hash(env_snapshot)

    receipt = {
        "receipt_type": "constitutional_receipt",
        "profile": "LEAN_BUILD",
        "receipt_id": str(uuid.uuid4()),
        "created_at": utc_now(),
        "claim": f"{command} returns {result}",
        "evidence": {
            "kind": "build",
            "command": command,
            "result": result,
            "timestamp": utc_now(),
            "artifact_paths": ["MathBuild/IrrationalSqrt2.lean"],
        },
        "provenance": {
            "repository": REPO,
            "commit": commit,
            "toolchain": toolchain,
            "mathlib_manifest_hash": lake_manifest_hash or "UNKNOWN",
            "lakefile_hash": lakefile_hash or "UNKNOWN",
            "environment": env_snapshot,
            "environment_hash": env_hash,
            "issuer": os.environ.get("GITHUB_ACTOR", "local"),
            "signature": "UNSIGNED_REFERENCE_RECEIPT",
        },
        "verification": {
            "method": "github_actions" if os.environ.get("GITHUB_ACTIONS") == "true" else "manual",
            "status": result,
            "workflow_run_url": os.environ.get("GITHUB_SERVER_URL", "") + "/" + os.environ.get("GITHUB_REPOSITORY", REPO) + "/actions/runs/" + os.environ.get("GITHUB_RUN_ID", "") if os.environ.get("GITHUB_RUN_ID") else "",
            "notes": "Reference receipt. Cryptographic signing not yet implemented.",
        },
        "expiration": None,
        "authority_effect": "NO_DIRECT_AUTHORITY",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", choices=["PASS", "FAIL", "PENDING"], default="PASS")
    parser.add_argument("--command", default="lake build MathBuild")
    parser.add_argument("--output", default="receipts/build/build_receipt_latest.json")
    args = parser.parse_args()

    receipt = build_receipt(args.result, args.command, Path(args.output))
    print(json.dumps({
        "receipt_id": receipt["receipt_id"],
        "output": args.output,
        "environment_hash": receipt["provenance"]["environment_hash"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
