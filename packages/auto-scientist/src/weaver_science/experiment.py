"""Bounded local experiment execution and receipt generation."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from weaver_assurance import EvidenceReceipt
from weaver_assurance.canonical import sha256_bytes, sha256_json


@dataclass(frozen=True)
class ExperimentSpec:
    experiment_id: str
    command: tuple[str, ...]
    input_files: tuple[Path, ...] = ()
    timeout_seconds: int = 60
    expected_exit_code: int = 0


@dataclass(frozen=True)
class ExperimentResult:
    passed: bool
    exit_code: int | None
    reason: str
    stdout: str
    stderr: str
    duration_ns: int
    receipt: EvidenceReceipt


class ExperimentRunner:
    """Run a command in a disposable directory with an environment allow-list.

    This is a reproducible process boundary, not a complete hostile-code
    sandbox. High-risk code requires a container or microVM adapter.
    """

    def __init__(self, allowed_executables: set[str], environment_hash: str, max_output_bytes: int = 131072) -> None:
        self.allowed_executables = allowed_executables
        self.environment_hash = environment_hash
        self.max_output_bytes = max_output_bytes

    @staticmethod
    def _file_hash(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def run(self, spec: ExperimentSpec, *, created_at: str) -> ExperimentResult:
        if not spec.command:
            raise ValueError("experiment command must be non-empty")
        executable = spec.command[0]
        resolved = shutil.which(executable) or executable
        if executable not in self.allowed_executables and resolved not in self.allowed_executables:
            raise ValueError(f"executable is not allow-listed: {executable}")
        if spec.timeout_seconds <= 0:
            raise ValueError("timeout must be positive")

        inputs: dict[str, str] = {}
        started = time.monotonic_ns()
        exit_code: int | None = None
        reason = "UNKNOWN"
        stdout_bytes = b""
        stderr_bytes = b""

        with tempfile.TemporaryDirectory(prefix="weaver-experiment-") as directory:
            workspace = Path(directory)
            for source in spec.input_files:
                source = source.resolve()
                if not source.is_file():
                    raise ValueError(f"input is not a file: {source}")
                destination = workspace / source.name
                if destination.exists():
                    raise ValueError(f"duplicate input filename: {source.name}")
                shutil.copy2(source, destination)
                inputs[source.name] = self._file_hash(source)

            environment = {key: value for key, value in os.environ.items() if key in {"PATH", "LANG", "LC_ALL"}}
            try:
                completed = subprocess.run(
                    list(spec.command),
                    cwd=workspace,
                    env=environment,
                    capture_output=True,
                    timeout=spec.timeout_seconds,
                    shell=False,
                    check=False,
                )
                exit_code = completed.returncode
                stdout_bytes = completed.stdout[: self.max_output_bytes]
                stderr_bytes = completed.stderr[: self.max_output_bytes]
                reason = "EXPECTED_EXIT" if exit_code == spec.expected_exit_code else "UNEXPECTED_EXIT"
            except subprocess.TimeoutExpired as exc:
                stdout_bytes = (exc.stdout or b"")[: self.max_output_bytes]
                stderr_bytes = (exc.stderr or b"")[: self.max_output_bytes]
                reason = "TIMEOUT"

        duration = time.monotonic_ns() - started
        output_hashes = {
            "stdout": sha256_bytes(stdout_bytes),
            "stderr": sha256_bytes(stderr_bytes),
            # Duration is telemetry, not semantic output: including it would
            # make two equivalent runs produce different evidence hashes.
            "result": sha256_json(
                {"exit_code": exit_code if exit_code is not None else -1, "reason": reason}
            ),
        }
        receipt = EvidenceReceipt.create(
            receipt_id=str(uuid.uuid4()),
            subject=spec.experiment_id,
            producer="weaver-auto-scientist",
            policy_version="weaver.science.experiment.v1",
            evidence_level="E2",
            input_hashes=inputs,
            output_hashes=output_hashes,
            command=spec.command,
            exit_code=exit_code if exit_code is not None else 124,
            environment_hash=self.environment_hash,
            replay_status="LOCAL_RUN",
            created_at=created_at,
        )
        return ExperimentResult(
            passed=reason == "EXPECTED_EXIT",
            exit_code=exit_code,
            reason=reason,
            stdout=stdout_bytes.decode("utf-8", errors="replace"),
            stderr=stderr_bytes.decode("utf-8", errors="replace"),
            duration_ns=duration,
            receipt=receipt,
        )
