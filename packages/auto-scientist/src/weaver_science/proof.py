"""Strict Lean checker adapter."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from weaver_assurance.canonical import sha256_bytes


class ProofStatus(str, Enum):
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    UNAVAILABLE = "UNAVAILABLE"
    TIMEOUT = "TIMEOUT"


@dataclass(frozen=True)
class ProofResult:
    status: ProofStatus
    checker: str
    exit_code: int | None
    stdout_hash: str
    stderr_hash: str
    diagnostics: str

    @property
    def verified(self) -> bool:
        return self.status is ProofStatus.VERIFIED


class LeanChecker:
    def __init__(self, command: tuple[str, ...] = ("lean",), timeout_seconds: int = 30) -> None:
        if not command:
            raise ValueError("checker command must be non-empty")
        self.command = command
        self.timeout_seconds = timeout_seconds

    def check(self, source: str) -> ProofResult:
        checker = shutil.which(self.command[0])
        if checker is None:
            return ProofResult(
                ProofStatus.UNAVAILABLE,
                self.command[0],
                None,
                sha256_bytes(b""),
                sha256_bytes(b"checker unavailable"),
                "Lean checker is not installed; no proof claim was made.",
            )

        with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False, encoding="utf-8") as handle:
            handle.write(source)
            source_path = Path(handle.name)
        try:
            completed = subprocess.run(
                [checker, *self.command[1:], str(source_path)],
                capture_output=True,
                timeout=self.timeout_seconds,
                shell=False,
                check=False,
            )
            status = ProofStatus.VERIFIED if completed.returncode == 0 else ProofStatus.REJECTED
            diagnostics = completed.stderr.decode("utf-8", errors="replace")[-8000:]
            return ProofResult(
                status,
                " ".join(self.command),
                completed.returncode,
                sha256_bytes(completed.stdout),
                sha256_bytes(completed.stderr),
                diagnostics,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or b""
            stderr = exc.stderr or b""
            return ProofResult(
                ProofStatus.TIMEOUT,
                " ".join(self.command),
                None,
                sha256_bytes(stdout),
                sha256_bytes(stderr),
                "Lean checker timed out; no proof claim was made.",
            )
        finally:
            os.unlink(source_path)

