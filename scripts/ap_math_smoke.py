#!/usr/bin/env python3
"""Controlled AP-MATH-001 smoke: fixed self-authored proof, trusted CI runner only.

Demonstrates compatibility of AutoProof's *reported* Lean-verification path with
the pinned MathBuild Lake environment, followed by a temporary worktree build.
This never grants canonical inclusion, replay acceptance, E4, or production
authority. Never substitute user-supplied proofs for the fixed test case.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from inspect_autoproof_candidate import inspect_candidate


ROOT = Path(__file__).resolve().parents[1]
AP_ROOT = Path(os.environ["AUTOPROOF_CHECKOUT"]).resolve()
AP_PIN = os.environ["AUTOPROOF_COMMIT_EXPECTED"]
RECEIPT_PATH = ROOT / "artifacts" / "ap_math_smoke.json"


def run(cmd: list[str], cwd: Path = ROOT, timeout: int = 180) -> str:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError(f"{cmd} failed (exit={p.returncode}): {p.stdout[-1800:]} {p.stderr[-1800:]}")
    return p.stdout.strip()


def digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def main() -> int:
    if os.environ.get("AP_MATH_TRUSTED_FIXTURE") != "1":
        raise RuntimeError("Only a trusted, fixed-fixture CI run may execute Lean.")
    ap_commit = run(["git", "rev-parse", "HEAD"], AP_ROOT)
    if ap_commit != AP_PIN:
        raise RuntimeError("AutoProof checkout identity differs from the expected pinned revision.")
    subject_commit = run(["git", "rev-parse", "HEAD"])
    toolchain = (ROOT / "lean-toolchain").read_text().strip()
    version = run(["lake", "env", "lean", "--version"])
    if toolchain.split(":")[-1].removeprefix("v") not in version:
        raise RuntimeError("Lean version differs from the pinned MathBuild toolchain.")
    lakefile = (ROOT / "lakefile.lean").read_text()
    pin = re.search(r'require mathlib from git\s+"[^"]+"\s+@\s+"([0-9a-f]{40})"', lakefile)
    if not pin:
        raise RuntimeError("No recognized pinned Mathlib revision.")
    manifest_file = ROOT / "lake-manifest.json"
    manifest = json.loads(manifest_file.read_text())
    mathlib = [p for p in manifest.get("packages", []) if p.get("name") == "mathlib"]
    if len(mathlib) != 1 or mathlib[0].get("rev") != pin.group(1):
        raise RuntimeError("Mathlib manifest is missing or differs from the Lake revision.")
    sys.path.insert(0, str(AP_ROOT / "backend"))
    os.environ["LEAN_PROJECT_DIR"] = str(ROOT)
    os.environ["LEAN_COMMAND"] = "lake env lean"
    os.environ["AUTOPROOF_TRUSTED_LEAN"] = "1"
    with tempfile.TemporaryDirectory(prefix="apmath-fixed-") as tmp:
        os.environ["DATABASE_PATH"] = str(Path(tmp) / "apmath.db")
        from fastapi.testclient import TestClient
        from app.main import app
        with TestClient(app) as client:
            session_response = client.post("/api/sessions", json={
                "statement": "n + 0 = n", "binders": "(n : Nat)",
            })
            if session_response.status_code != 201:
                raise RuntimeError(f"Session creation failed: {session_response.text}")
            session = session_response.json()
            check = client.post("/api/apply-tactic", json={
                "session_id": session["id"], "tactic": "simp", "proof": "simp",
            })
            if check.status_code != 200 or check.json().get("status") != "verified":
                raise RuntimeError(f"AutoProof did not verify the fixed proof: {check.text}")
            handoff_response = client.get(
                f"/api/sessions/{session['id']}/attempts/{check.json()['node_id']}/handoff"
            )
            if handoff_response.status_code != 200:
                raise RuntimeError(f"Candidate export failed: {handoff_response.text}")
            handoff = handoff_response.json()
        inspected = inspect_candidate(handoff)
        if inspected["inspection"] != "STRUCTURALLY_BOUND_ONLY" or inspected["accepted"]:
            raise RuntimeError("Candidate inspector promoted or rejected the result unexpectedly.")
        candidate = handoff["candidate"]
        if candidate["lean_version_reported"] != version.splitlines()[0]:
            raise RuntimeError("AutoProof checker version does not match MathBuild Lean.")
        source = candidate["generated_lean_source"]
        if candidate["source_sha256"] != hashlib.sha256(source.encode("utf-8")).hexdigest():
            raise RuntimeError("Candidate bytes mismatch after export.")

        root_file = ROOT / "MathBuild.lean"
        module_file = ROOT / "MathBuild" / "APMathSmoke.lean"
        original_root = root_file.read_bytes()
        if module_file.exists() or b"import MathBuild.APMathSmoke" in original_root:
            raise RuntimeError("Smoke file already exists; refusing to overwrite canonical source.")
        try:
            module_file.write_text("import Mathlib\n\n" + source, encoding="utf-8")
            root_file.write_bytes(b"import MathBuild.APMathSmoke\n" + original_root)
            build_output = run(["lake", "build", "MathBuild"], timeout=300)
        finally:
            root_file.write_bytes(original_root)
            module_file.unlink(missing_ok=True)

        evidence = {
            "experiment": "AP-MATH-001",
            "disposition": "TEMPORARY_WORKTREE_SMOKE_PASS_NO_PROMOTION",
            "auto_proof_commit": ap_commit,
            "mathbuild_base_commit": subject_commit,
            "mathbuild_worktree_modified_during_build": True,
            "canonical_commit_inclusion": False,
            "mathbuild_acceptance": False,
            "authority": "NONE",
            "independent_reproduction": False,
            "target": "MathBuild",
            "lean_version": version.splitlines()[0],
            "mathlib_revision": pin.group(1),
            "mathlib_manifest_sha256": digest(manifest_file.read_bytes()),
            "candidate_sha256": handoff["candidate_sha256"],
            "statement_sha256": candidate["statement_sha256"],
            "proof_sha256": candidate["proof_sha256"],
            "source_sha256": candidate["source_sha256"],
            "smoke_build_output_tail": build_output[-1200:],
        }
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n")
        print(json.dumps(evidence, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
