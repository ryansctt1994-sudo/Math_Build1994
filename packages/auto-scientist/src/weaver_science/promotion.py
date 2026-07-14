"""Science-specific evidence promotion."""

from __future__ import annotations

from dataclasses import dataclass

from weaver_assurance import EvidenceLevel


@dataclass(frozen=True)
class ScienceEvidence:
    pre_registered: bool = False
    local_run_receipt: bool = False
    failure_path_exercised: bool = False
    artifact_hashes: bool = False
    locked_environment: bool = False
    replay_receipt: bool = False
    producer_id: str | None = None
    witness_id: str | None = None
    witness_transcript: bool = False
    domain_review: bool = False
    limitations: bool = False


@dataclass(frozen=True)
class SciencePromotion:
    granted: bool
    target: EvidenceLevel
    missing: tuple[str, ...]
    reason: str


def evaluate_science_promotion(target: EvidenceLevel, evidence: ScienceEvidence) -> SciencePromotion:
    missing: list[str] = []
    if target >= EvidenceLevel.E1 and not evidence.limitations:
        missing.append("limitations")
    if target >= EvidenceLevel.E2:
        if not evidence.pre_registered:
            missing.append("pre_registered")
        if not evidence.local_run_receipt:
            missing.append("local_run_receipt")
        if not evidence.failure_path_exercised:
            missing.append("failure_path_exercised")
        if not evidence.artifact_hashes:
            missing.append("artifact_hashes")
    if target >= EvidenceLevel.E3:
        if not evidence.locked_environment:
            missing.append("locked_environment")
        if not evidence.replay_receipt:
            missing.append("replay_receipt")
    if target >= EvidenceLevel.E4:
        if not evidence.witness_id:
            missing.append("witness_id")
        if evidence.witness_id and evidence.witness_id == evidence.producer_id:
            missing.append("distinct_witness")
        if not evidence.witness_transcript:
            missing.append("witness_transcript")
    if target >= EvidenceLevel.E5 and not evidence.domain_review:
        missing.append("domain_review")

    if missing:
        return SciencePromotion(False, target, tuple(sorted(set(missing))), "PROMOTION_BLOCKED")
    return SciencePromotion(True, target, (), "PROMOTION_GRANTED")

