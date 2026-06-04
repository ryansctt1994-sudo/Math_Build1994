#!/usr/bin/env python3
"""Verify a constitutional receipt against replay evidence.

Phase 4B scaffold:
- stdlib only
- no cryptographic theater
- rejects authority-bearing receipts
- checks replay matrix evidence for SUCCESS + environment_match == true
- reports unsigned receipts as replay-qualified but not cryptographically governed

This script does not make a receipt production-trusted. It only determines whether
an unsigned reference receipt has enough replay evidence to be eligible for later
cryptographic custody.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


DEFAULT_SCHEMA = Path("schemas/constitutional_receipt.schema.json")
DEFAULT_MATRIX = Path("receipts/replay/replay_matrix.json")
DEFAULT_KEYS = Path("TRUSTED_KEYS.json")

REQUIRED_TOP_LEVEL = [
    "receipt_type",
    "profile",
    "receipt_id",
    "created_at",
    "claim",
    "evidence",
    "provenance",
    "verification",
    "authority_effect",
]

ALLOWED_PROFILES = {
    "LEAN_THEOREM",
    "LEAN_BUILD",
    "REPLAY_BUILD",
    "HOPF_RELATIONAL",
    "ONTOLOGY_SNAPSHOT",
    "WITNESS_LOG",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def fail(code: str, detail: str) -> dict[str, Any]:
    return {"status": "FAIL", "code": code, "detail": detail}


def ok(code: str, detail: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"status": "PASS", "code": code, "detail": detail}
    if extra:
        payload.update(extra)
    return payload


def validate_receipt_shape(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_TOP_LEVEL:
        if field not in receipt:
            errors.append(f"missing top-level field: {field}")

    if receipt.get("receipt_type") != "constitutional_receipt":
        errors.append("receipt_type must be constitutional_receipt")

    if receipt.get("profile") not in ALLOWED_PROFILES:
        errors.append(f"unsupported profile: {receipt.get('profile')}")

    if receipt.get("authority_effect") != "NO_DIRECT_AUTHORITY":
        errors.append("authority_effect must be NO_DIRECT_AUTHORITY")

    evidence = receipt.get("evidence")
    if not isinstance(evidence, dict) or "kind" not in evidence:
        errors.append("evidence.kind is required")

    provenance = receipt.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        for field in ["repository", "commit", "toolchain"]:
            if field not in provenance:
                errors.append(f"provenance.{field} is required")

    verification = receipt.get("verification")
    if not isinstance(verification, dict):
        errors.append("verification must be an object")
    else:
        if verification.get("status") not in {"PASS", "FAIL", "PENDING"}:
            errors.append("verification.status must be PASS, FAIL, or PENDING")

    return errors


def load_replay_entries(matrix_path: Path) -> list[dict[str, Any]]:
    if not matrix_path.exists():
        return []
    matrix = read_json(matrix_path)
    if not isinstance(matrix, dict):
        return []
    entries = matrix.get("entries", [])
    return entries if isinstance(entries, list) else []


def matching_replays(entries: list[dict[str, Any]], receipt_hash: str) -> list[dict[str, Any]]:
    return [entry for entry in entries if entry.get("original_receipt_hash") == receipt_hash]


def best_replay_status(replays: list[dict[str, Any]]) -> dict[str, Any]:
    if not replays:
        return {
            "has_replay": False,
            "replay_success": False,
            "environment_match": False,
            "latest_replay": None,
        }

    latest = replays[-1]
    return {
        "has_replay": True,
        "replay_success": latest.get("replay_result") == "SUCCESS",
        "environment_match": latest.get("environment_match") is True,
        "latest_replay": latest,
    }


def verify_signature_placeholder(receipt: dict[str, Any], keys_path: Path) -> dict[str, Any]:
    provenance = receipt.get("provenance", {})
    signature = provenance.get("signature")

    if signature in (None, "", "UNSIGNED_REFERENCE_RECEIPT"):
        return {
            "signature_status": "UNSIGNED_REFERENCE_RECEIPT",
            "cryptographic_governance": False,
        }

    if not keys_path.exists():
        return {
            "signature_status": "NO_TRUSTED_KEYS_REGISTRY",
            "cryptographic_governance": False,
        }

    registry = read_json(keys_path)
    keys = registry.get("keys", []) if isinstance(registry, dict) else []
    if not keys:
        return {
            "signature_status": "NO_TRUST_ROOTS_ENROLLED",
            "cryptographic_governance": False,
        }

    return {
        "signature_status": "SIGNATURE_PRESENT_BUT_VERIFICATION_NOT_IMPLEMENTED",
        "cryptographic_governance": False,
    }


def verify(receipt_path: Path, matrix_path: Path, keys_path: Path) -> dict[str, Any]:
    if not receipt_path.exists():
        return fail("RECEIPT_NOT_FOUND", str(receipt_path))

    receipt = read_json(receipt_path)
    if not isinstance(receipt, dict):
        return fail("INVALID_RECEIPT_JSON", "receipt root must be an object")

    shape_errors = validate_receipt_shape(receipt)
    if shape_errors:
        return fail("SCHEMA_SHAPE_INVALID", "; ".join(shape_errors))

    if receipt.get("verification", {}).get("status") != "PASS":
        return fail("RECEIPT_VERIFICATION_NOT_PASS", "receipt verification.status is not PASS")

    receipt_hash = sha256_file(receipt_path)
    entries = load_replay_entries(matrix_path)
    replays = matching_replays(entries, receipt_hash)
    replay_status = best_replay_status(replays)

    if not replay_status["has_replay"]:
        return fail("NO_REPLAY_EVIDENCE", "receipt hash not found in replay matrix")

    if not replay_status["replay_success"]:
        return fail("REPLAY_NOT_SUCCESSFUL", "latest replay_result is not SUCCESS")

    if not replay_status["environment_match"]:
        return fail("ENVIRONMENT_NOT_MATCHED", "latest replay does not show environment_match == true")

    sig = verify_signature_placeholder(receipt, keys_path)

    return ok(
        "REPLAY_QUALIFIED_UNSIGNED_RECEIPT",
        "receipt is schema-valid, replay-successful, and environment-matched; cryptographic custody is not active",
        {
            "receipt_hash": receipt_hash,
            "replay_count": len(replays),
            "latest_replay": replay_status["latest_replay"],
            **sig,
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", help="Path to receipt JSON")
    parser.add_argument("--matrix", default=str(DEFAULT_MATRIX))
    parser.add_argument("--keys", default=str(DEFAULT_KEYS))
    args = parser.parse_args()

    result = verify(Path(args.receipt), Path(args.matrix), Path(args.keys))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
