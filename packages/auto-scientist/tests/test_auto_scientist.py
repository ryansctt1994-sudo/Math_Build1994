from __future__ import annotations

import sys

from weaver_assurance import EvidenceLevel
from weaver_science import (
    BenchmarkRun,
    ExperimentRunner,
    ExperimentSpec,
    LeanChecker,
    Lifecycle,
    ProofStatus,
    ScienceEvidence,
    Stage,
    compare_benchmarks,
    evaluate_science_promotion,
)
from weaver_science.claims import Claim


def test_lifecycle_rejects_skipped_stages():
    lifecycle = Lifecycle("r1")
    try:
        lifecycle.transition(Stage.EXPERIMENT, "e1")
    except ValueError as exc:
        assert "invalid lifecycle transition" in str(exc)
    else:
        raise AssertionError("lifecycle allowed a skipped stage")


def test_lifecycle_requires_evidence_for_every_transition():
    lifecycle = Lifecycle("r2")
    try:
        lifecycle.transition(Stage.HYPOTHESIS, "")
    except ValueError:
        pass
    else:
        raise AssertionError("transition accepted without evidence")


def test_missing_lean_is_unavailable_not_verified():
    result = LeanChecker(("definitely-not-a-real-lean-binary",)).check("theorem x : True := by trivial")
    assert result.status is ProofStatus.UNAVAILABLE
    assert not result.verified


def test_real_checker_exit_code_controls_proof_status(tmp_path):
    checker = tmp_path / "fake_checker.py"
    checker.write_text("import sys\nsys.exit(0 if 'good' in open(sys.argv[1]).read() else 1)\n", encoding="utf-8")
    lean = LeanChecker((sys.executable, str(checker)))
    assert lean.check("good").verified
    assert lean.check("bad").status is ProofStatus.REJECTED


def test_experiment_success_and_failure_emit_verifiable_receipts():
    runner = ExperimentRunner({sys.executable}, "e" * 64)
    passed = runner.run(
        ExperimentSpec("exp-pass", (sys.executable, "-c", "print('ok')")),
        created_at="2026-07-14T00:00:00Z",
    )
    assert passed.passed
    assert passed.receipt.verify()
    failed = runner.run(
        ExperimentSpec("exp-fail", (sys.executable, "-c", "raise SystemExit(7)")),
        created_at="2026-07-14T00:00:01Z",
    )
    assert not failed.passed
    assert failed.exit_code == 7
    assert failed.receipt.verify()


def test_equivalent_experiment_runs_have_same_semantic_output_hashes():
    runner = ExperimentRunner({sys.executable}, "e" * 64)
    spec = ExperimentSpec("repeatable", (sys.executable, "-c", "print('same')"))
    first = runner.run(spec, created_at="2026-07-14T00:00:00Z")
    second = runner.run(spec, created_at="2026-07-14T00:00:01Z")
    assert first.receipt.output_hashes == second.receipt.output_hashes


def test_benchmark_requires_seed_matched_baseline():
    candidate = [BenchmarkRun("new", 1, 800_000), BenchmarkRun("new", 2, 900_000)]
    baseline = [BenchmarkRun("old", 1, 700_000), BenchmarkRun("old", 2, 850_000)]
    comparison = compare_benchmarks(candidate, baseline)
    assert comparison.mean_gain_micros == 75_000
    assert comparison.wins == 2
    try:
        compare_benchmarks(candidate, baseline[:1])
    except ValueError:
        pass
    else:
        raise AssertionError("unmatched seeds were accepted")


def test_local_run_cannot_be_promoted_as_independent_reproduction():
    evidence = ScienceEvidence(
        pre_registered=True,
        local_run_receipt=True,
        failure_path_exercised=True,
        artifact_hashes=True,
        locked_environment=True,
        replay_receipt=True,
        producer_id="same-ai-context",
        witness_id="same-ai-context",
        witness_transcript=True,
        limitations=True,
    )
    decision = evaluate_science_promotion(EvidenceLevel.E4, evidence)
    assert not decision.granted
    assert "distinct_witness" in decision.missing


def test_distinct_witness_can_satisfy_e4_gate():
    evidence = ScienceEvidence(
        pre_registered=True,
        local_run_receipt=True,
        failure_path_exercised=True,
        artifact_hashes=True,
        locked_environment=True,
        replay_receipt=True,
        producer_id="producer-a",
        witness_id="witness-b",
        witness_transcript=True,
        limitations=True,
    )
    assert evaluate_science_promotion(EvidenceLevel.E4, evidence).granted


def test_claim_requires_falsifier_evidence_and_limits():
    invalid = Claim("c1", "A causes B", "synthetic", (), ("r1",), ("not externally validated",))
    try:
        invalid.validate()
    except ValueError as exc:
        assert "falsifier" in str(exc)
    else:
        raise AssertionError("non-falsifiable claim was accepted")
