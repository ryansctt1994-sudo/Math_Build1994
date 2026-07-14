"""Seed-matched integer benchmark comparison."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkRun:
    system: str
    seed: int
    score_micros: int


@dataclass(frozen=True)
class BenchmarkComparison:
    candidate: str
    baseline: str
    seeds: tuple[int, ...]
    mean_gain_micros: int
    wins: int
    losses: int
    ties: int


def compare_benchmarks(candidate: list[BenchmarkRun], baseline: list[BenchmarkRun]) -> BenchmarkComparison:
    if not candidate or not baseline:
        raise ValueError("candidate and baseline runs are required")
    candidate_by_seed = {run.seed: run for run in candidate}
    baseline_by_seed = {run.seed: run for run in baseline}
    if len(candidate_by_seed) != len(candidate) or len(baseline_by_seed) != len(baseline):
        raise ValueError("duplicate benchmark seeds are forbidden")
    if candidate_by_seed.keys() != baseline_by_seed.keys():
        raise ValueError("candidate and baseline must use identical seeds")
    seeds = tuple(sorted(candidate_by_seed))
    gains = [candidate_by_seed[seed].score_micros - baseline_by_seed[seed].score_micros for seed in seeds]
    mean_gain = sum(gains) // len(gains)
    return BenchmarkComparison(
        candidate=candidate[0].system,
        baseline=baseline[0].system,
        seeds=seeds,
        mean_gain_micros=mean_gain,
        wins=sum(gain > 0 for gain in gains),
        losses=sum(gain < 0 for gain in gains),
        ties=sum(gain == 0 for gain in gains),
    )

