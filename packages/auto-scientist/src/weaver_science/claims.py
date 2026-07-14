"""Falsifiable claim records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Claim:
    claim_id: str
    statement: str
    scope: str
    falsifiers: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    limitations: tuple[str, ...]

    def validate(self) -> None:
        if not all((self.claim_id, self.statement, self.scope)):
            raise ValueError("claim id, statement, and scope are required")
        if not self.falsifiers:
            raise ValueError("scientific claims require at least one predeclared falsifier")
        if not self.evidence_ids:
            raise ValueError("claims require evidence identifiers")
        if not self.limitations:
            raise ValueError("claims require explicit limitations")

