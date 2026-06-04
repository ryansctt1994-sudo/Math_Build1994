#!/usr/bin/env python3
"""Replay a Lean build from a constitutional build receipt.

Phase 3 minimal replay:
- Reads a build receipt.
- Checks out the recorded commit in the current repository unless --no-checkout is used.
- Runs the recorded build command.
- Emits a replay result JSON.
- Appends a replay matrix entry.

This is same-environment replay. It does not yet provide Docker-pinned replay,
cryptographic receipt signing, or signed trust-anchor validation.
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


DEFAULT_MATRIX = Path("receipts/replay/replay_matrix.json")
DEFAULT_OUTPUT_DIR = Path("receipts/replay")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, text=True, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def run_shell(command: str) -> tuple[int, str, str]:
    p = subprocess.run(command, text=True, capture_output=True, shell=True)
    return p.returncode, p.stdout, p.stderr


def run_text(command: str, default: str = "UNKNOWN") -> str:
    code, out, err = run_shell(command)
    if code != 0:
        return default
    return (out or err).strip() or default


def current_commit() -> str:
    code, out, _ = run(["git", "rev-parse", "HEAD"])
    return out.strip() if code == 0 else "UNKNOWN"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_sha256_plain(path: Path) -> str | None:
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


def environment_snapshot() -> dict[str, str]:
    toolchain = read_text(Path("lean-toolchain"))
    lake_manifest_hash = file_sha256_plain(Path("lake-manifest.json"))
    return {
        "os": platform.platform(),
        "uname": run_text("uname -a"),
        "python_version": platform.python_version(),
        "lean_version": run_text("lake env lean --version"),
        "lake_version": run_text("lake --version"),
        "toolchain": toolchain,
        "lake_manifest_hash": lake_manifest_hash or "UNKNOWN",
        "container_hash": os.environ.get("CONTAINER_HASH", "UNPINNED_SAME_ENVIRONMENT_REPLAY"),
    }


def environment_hash(snapshot: dict[str, str]) -> str:
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def append_matrix(matrix_path: Path, replay_result: dict[str, Any]) -> None:
    if matrix_path.exists():
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    else:
        matrix = {"schema_version": "replay-matrix/0.1", "entries": []}

    matrix.setdefault("entries", []).append({
        "replay_id": replay_result["replay_id"],
        "replay_timestamp": replay_result["replay_timestamp"],
        "original_receipt_hash": replay_result["original_receipt_hash"],
        "original_commit": replay_result["original_commit"],
        "replay_result": replay_result["replay_result"],
        "receipt_environment_hash": replay_result["receipt_environment_hash"],
        "current_environment_hash": replay_result["current_environment_hash"],
        "environment_match": replay_result["environment_match"],
        "environment_drift_status": replay_result["environment_drift_status"],
        "output_path": replay_result["output_path"],
    })
    write_json(matrix_path, matrix)


def replay(receipt_path: Path, output_dir: Path, matrix_path: Path, no_checkout: bool) -> dict[str, Any]:
    receipt = read_json(receipt_path)
    original_hash = sha256_file(receipt_path)

    provenance = receipt.get("provenance", {})
    evidence = receipt.get("evidence", {})
    target_commit = provenance.get("commit")
    command = evidence.get("command", "lake build MathBuild")
    receipt_env_hash = provenance.get("environment_hash", "UNKNOWN")

    starting_commit = current_commit()
    checkout_status = "SKIPPED" if no_checkout else "PENDING"
    checkout_stderr = ""

    if not no_checkout:
        if not target_commit or target_commit == "UNKNOWN":
            checkout_status = "FAILED_NO_TARGET_COMMIT"
        else:
            code, _, err = run(["git", "checkout", target_commit])
            checkout_status = "PASS" if code == 0 else "FAIL"
            checkout_stderr = err[-4000:]

    current_env = environment_snapshot()
    current_env_hash = environment_hash(current_env)
    environment_match = receipt_env_hash != "UNKNOWN" and receipt_env_hash == current_env_hash
    if receipt_env_hash == "UNKNOWN":
        drift_status = "RECEIPT_ENVIRONMENT_HASH_MISSING"
    elif environment_match:
        drift_status = "ENVIRONMENT_MATCH"
    else:
        drift_status = "ENVIRONMENT_DRIFT_DETECTED"

    code, stdout, stderr = run_shell(command)
    result = "SUCCESS" if code == 0 else "FAILURE"

    replay_id = str(uuid.uuid4())
    output_path = output_dir / f"replay_result_{replay_id}.json"

    replay_result = {
        "schema_version": "build-replay-result/0.2",
        "replay_id": replay_id,
        "replay_result": result,
        "replay_timestamp": utc_now(),
        "original_receipt_path": str(receipt_path),
        "original_receipt_hash": original_hash,
        "original_commit": target_commit or "UNKNOWN",
        "starting_commit": starting_commit,
        "checkout_status": checkout_status,
        "checkout_stderr_tail": checkout_stderr,
        "command": command,
        "exit_code": code,
        "stdout_tail": stdout[-4000:],
        "stderr_tail": stderr[-4000:],
        "environment": current_env,
        "receipt_environment_hash": receipt_env_hash,
        "current_environment_hash": current_env_hash,
        "environment_match": environment_match,
        "environment_drift_status": drift_status,
        "diff": "" if result == "SUCCESS" else "Build command returned non-zero exit status.",
        "limitations": [
            "same-environment replay only",
            "no Docker-pinned environment yet",
            "no cryptographic signature verification yet",
        ],
        "output_path": str(output_path),
    }

    write_json(output_path, replay_result)
    append_matrix(matrix_path, replay_result)
    return replay_result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", help="Path to build receipt JSON")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--matrix", default=str(DEFAULT_MATRIX))
    parser.add_argument("--no-checkout", action="store_true", help="Replay current worktree without checking out recorded commit")
    args = parser.parse_args()

    result = replay(Path(args.receipt), Path(args.output_dir), Path(args.matrix), args.no_checkout)
    print(json.dumps({
        "replay_result": result["replay_result"],
        "output_path": result["output_path"],
        "original_receipt_hash": result["original_receipt_hash"],
        "environment_match": result["environment_match"],
        "environment_drift_status": result["environment_drift_status"],
    }, indent=2))
    return 0 if result["replay_result"] == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
