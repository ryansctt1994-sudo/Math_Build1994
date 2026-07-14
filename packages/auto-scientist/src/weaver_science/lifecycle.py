"""Explicit scientific lifecycle state machine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Stage(str, Enum):
    QUESTION = "QUESTION"
    HYPOTHESIS = "HYPOTHESIS"
    PLAN = "PLAN"
    EXPERIMENT = "EXPERIMENT"
    AUDIT = "AUDIT"
    REPLAY = "REPLAY"
    WITNESS = "WITNESS"
    PROMOTED = "PROMOTED"
    REJECTED = "REJECTED"


ALLOWED: dict[Stage, frozenset[Stage]] = {
    Stage.QUESTION: frozenset({Stage.HYPOTHESIS, Stage.REJECTED}),
    Stage.HYPOTHESIS: frozenset({Stage.PLAN, Stage.REJECTED}),
    Stage.PLAN: frozenset({Stage.EXPERIMENT, Stage.REJECTED}),
    Stage.EXPERIMENT: frozenset({Stage.AUDIT, Stage.REJECTED}),
    Stage.AUDIT: frozenset({Stage.REPLAY, Stage.REJECTED}),
    Stage.REPLAY: frozenset({Stage.WITNESS, Stage.REJECTED}),
    Stage.WITNESS: frozenset({Stage.PROMOTED, Stage.REJECTED}),
    Stage.PROMOTED: frozenset(),
    Stage.REJECTED: frozenset(),
}


@dataclass
class Lifecycle:
    research_id: str
    stage: Stage = Stage.QUESTION
    history: list[tuple[str, str]] = field(default_factory=list)

    def transition(self, target: Stage, evidence_id: str) -> None:
        if not evidence_id:
            raise ValueError("every transition requires an evidence identifier")
        if target not in ALLOWED[self.stage]:
            raise ValueError(f"invalid lifecycle transition: {self.stage.value} -> {target.value}")
        self.history.append((target.value, evidence_id))
        self.stage = target

