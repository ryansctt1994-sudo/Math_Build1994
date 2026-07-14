# Math Build Formal and Auto Scientist Master v1

**Portfolio role:** Repository 3 of 3  
**Runtime authority:** NONE  
**Production authority:** NONE  
**Independent reproduction:** NOT ESTABLISHED

This repository becomes the single active home for formal proof, model checking, reproducible mathematical experiments, benchmark harnesses, RTL simulation, cryptographic vectors, and the evidence-governed Auto Scientist pipeline.

## Core program

The canonical research lifecycle is:

```text
Question
→ Hypothesis
→ Search
→ Plan
→ Experiment or proof obligation
→ Audit
→ Replay
→ Witness
→ Chronicle receipt
→ Promotion decision outside this repository
```

The laboratory may generate and validate claims. It may not authorize deployment or promote itself.

## Selected intake

### Direct consolidation candidates

- `AutoProof`: human-in-the-loop proof review and validation interface;
- `LogOS`: recoverable PROVE/RUNTIME/EMIT/VERIFY assets after dependency and placeholder audit;
- `t81-benchmarks`: exact benchmark definitions, vectors, harnesses, and result receipts;
- `t81-hardware`: RTL and testbench assets, with simulation and physical claims kept separate;
- `t81lib`: validated reusable library components;
- `ternary` and `ternary-tools`: falsifiable ternary-computing source, tooling, and vectors;
- `trinity-pow`: bounded experimental proof-of-work research.

### Candidate-only intake

- `duotronic-computing`;
- `trinity`.

These candidates remain outside promoted paths until they contain falsifiable definitions, exact commands, tests, raw outputs, and receipts.

### Reference-only donors

- `t81-foundation`;
- `t81-docs`;
- `t81-roadmap`.

Documentation, roadmaps, and upstream architecture do not inherit evidence status.

## Required directory model

```text
formal/
  lean/
  agda/
  tla/
experiments/
  numerical/
  cryptographic/
  agent_science/
hardware/
  rtl/
  testbenches/
benchmarks/
receipts/
  formal/
  experiments/
  hardware/
registry/
  claims.jsonl
  failures.jsonl
  sources.json
```

Existing source should move into this model only after provenance and build-path review. Historical paths remain valid until a supersession record exists.

## Evidence separation

Formal and empirical claims must remain separate.

A theorem-prover build can establish that a theorem is accepted under a stated toolchain and trusted computing base. It does not establish that a runtime implements the theorem.

A model-check pass can establish bounded state-space properties under a model and configuration. It does not establish production behavior outside that model.

A numerical experiment can establish observed results under exact code, data, seeds, and environment. It does not establish a theorem.

An RTL simulation can establish simulated behavior under a testbench. It does not establish synthesis closure, board behavior, analog timing, or physical safety.

## Auto Scientist authority boundary

The Auto Scientist may:

- propose hypotheses;
- search declared corpora;
- generate proof obligations and experiment plans;
- run authorized local tools;
- preserve raw outputs and failures;
- emit candidate receipts;
- request independent reproduction.

It may not:

- self-certify a result;
- convert model confidence into evidence;
- hide failed trials;
- alter acceptance criteria after seeing results without a recorded amendment;
- promote a claim or authorize deployment;
- treat agreement among AI systems as independent evidence.

## First consolidation sequence

1. Keep the current Lean square-root-of-two build as the smallest locked brick.
2. Resolve the open coprime-proof receipt path without forbidden shortcuts.
3. Integrate AutoProof as a review interface, not as a proof oracle.
4. Inventory LogOS formal assets and mark missing crates, postulates, placeholders, and unbuilt surfaces.
5. Import T81 and ternary assets only after source pins, licenses, vectors, and test commands are captured.
6. Add claim, source, failure, and receipt registries.
7. Produce a clean witness package for one Lean proof, one numerical experiment, one model check, and one RTL simulation.

## Non-claims

This baseline does not establish completion of the Millennium Prize Problems, AGI/ASI transition proof, hardware safety, cryptographic security, clinical validity, or production readiness. It establishes the repository boundary and evidence contract for work that may later support narrower claims.