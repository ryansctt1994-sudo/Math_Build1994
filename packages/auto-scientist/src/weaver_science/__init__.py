"""Public API for Weaver Auto Scientist."""

from .benchmark import BenchmarkComparison, BenchmarkRun, compare_benchmarks
from .experiment import ExperimentResult, ExperimentRunner, ExperimentSpec
from .lifecycle import Lifecycle, Stage
from .proof import LeanChecker, ProofResult, ProofStatus
from .promotion import ScienceEvidence, SciencePromotion, evaluate_science_promotion

__all__ = [
    "BenchmarkComparison",
    "BenchmarkRun",
    "ExperimentResult",
    "ExperimentRunner",
    "ExperimentSpec",
    "LeanChecker",
    "Lifecycle",
    "ProofResult",
    "ProofStatus",
    "ScienceEvidence",
    "SciencePromotion",
    "Stage",
    "compare_benchmarks",
    "evaluate_science_promotion",
]

