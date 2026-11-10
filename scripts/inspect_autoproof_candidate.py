#!/usr/bin/env python3
"""AP-MATH-001 receiving-side structural inspection (NO proof or acceptance).

The only success outcome here is STRUCTURALLY_BOUND_ONLY. A locally recomputed
digest is not authentication. Never execute a submitted candidate as Lean
source or mutate the canonical MathBuild repository through this tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

GOAL_NAME = "autoproof_goal"
SCHEMA_VERSION = "autoproof-candidate/1"
STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


class CandidateRefused(ValueError):
    pass


def _require(valid: bool, reason: str) -> None:
    if not valid:
        raise CandidateRefused(reason)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _digest(candidate: dict[str, Any]) -> str:
    encoded = json.dumps(candidate, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + _sha(encoded)


def inspect_candidate(envelope: dict[str, Any]) -> dict[str, Any]:
    _require(isinstance(envelope, dict), "Handoff is not a JSON object.")
    _require(envelope.get("authority") == "NONE", "Untrusted claim of authority.")
    _require(envelope.get("mathbuild_acceptance") == "NOT_EVALUATED", "Untrusted acceptance claim.")
    _require(envelope.get("independent_reproduction") is False, "Untrusted reproduction claim.")
    candidate = envelope.get("candidate")
    _require(isinstance(candidate, dict), "Candidate object missing.")
    _require(candidate.get("schema_version") == SCHEMA_VERSION, "Unsupported schema.")
    _require(candidate.get("source_system") == "AutoProof", "Unexpected source system.")
    _require(candidate.get("goal_name") == GOAL_NAME, "Unexpected theorem name.")
    for key in ("session_id", "attempt_id", "statement", "binders", "proof_text",
                "checker_version", "lean_version_reported"):
        _require(isinstance(candidate.get(key), str), f"Missing {key}.")
    for key in ("session_id", "attempt_id", "statement", "proof_text",
                "checker_version", "lean_version_reported"):
        _require(bool(candidate[key].strip()), f"Empty {key}.")
    _require(candidate.get("verdict_reported") == "verified", "Reported proof was not verified.")
    axioms = candidate.get("axioms_reported")
    _require(isinstance(axioms, list) and all(isinstance(a, str) for a in axioms),
             "Invalid axiom audit.")
    _require(len(axioms) == len(set(axioms)) and set(axioms) <= STANDARD_AXIOMS,
             "Extra or duplicate axiom claim.")

    statement = candidate["statement"]
    binders = candidate["binders"]
    proof = candidate["proof_text"]
    head = "theorem autoproof_goal" + ((" " + binders.strip()) if binders.strip() else "")
    signature = f"{head} : {statement.strip()}"
    generated = signature + " := by\n"
    generated += "\n".join("  " + line.rstrip() if line.strip() else "" for line in proof.splitlines()) + "\n"

    _require(candidate.get("statement_sha256") == _sha(signature), "Statement digest drift.")
    _require(candidate.get("proof_sha256") == _sha(proof), "Proof digest drift.")
    _require(candidate.get("generated_lean_source") == generated, "Generated source bytes differ.")
    _require(candidate.get("source_sha256") == _sha(generated), "Source digest drift.")
    _require(envelope.get("candidate_sha256") == _digest(candidate), "Candidate digest drift.")

    return {
        "inspection": "STRUCTURALLY_BOUND_ONLY",
        "accepted": False,
        "authority": "NONE",
        "candidate_sha256": envelope["candidate_sha256"],
        "session_id": candidate["session_id"],
        "attempt_id": candidate["attempt_id"],
        "remaining_obligations": [
            "independent checker attestation",
            "proof check in MathBuild's pinned Lake/Mathlib environment",
            "canonical inclusion at an exact MathBuild commit",
            "post-merge acceptance predicates B/R/S/T/E/P",
            "independent reproduction for E4"
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate_json", type=Path)
    args = parser.parse_args()
    try:
        envelope = json.loads(args.candidate_json.read_text(encoding="utf-8"))
        result = inspect_candidate(envelope)
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({"inspection": "REFUSED", "accepted": False,
                          "authority": "NONE", "reason": str(error)}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
