"""External research skill packs are references, not trusted runtime code."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchSkillSource:
    name: str
    use: str
    boundary: str


SOURCES = (
    ResearchSkillSource("AI-Research-SKILLs", "research engineering guidance", "MIT; review each skill"),
    ResearchSkillSource("Hugging Face skills", "training/evaluation guidance", "Apache-2.0; review each skill"),
    ResearchSkillSource("agency-agents6", "role templates", "MIT; provenance mismatch requires quarantine"),
    ResearchSkillSource("Quillan-v4.2", "MoE/council experiments", "Apache-2.0; no authority claims"),
    ResearchSkillSource("Delta-RPM-Protocol", "scientific reference only", "all rights reserved; no code import"),
)

