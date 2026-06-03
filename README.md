# Master Custom Math Build v3.1

A stripped-down, working mathematical operating system.

First goal: prove that the square root of 2 is irrational in Lean.

## Status

This repository is Day-1 lockable.

The current Lean proof uses Mathlib's maintained theorem `irrational_sqrt_two` as the first verified brick. The earlier hand-written coprime proof is not treated as locked until it builds independently.

## Repository structure

```text
.
├── lakefile.lean
├── lean-toolchain
├── MathBuild/
│   └── IrrationalSqrt2.lean
├── logs/
│   └── meta_log_week1.md
├── docs/
│   └── COPRIME_PROOF_REPAIR_NOTES.md
└── README.md
```

## Build

```bash
lake update
lake build MathBuild
```

Expected result: Lean builds the `MathBuild` library without errors.

## Week 1 paths

Choose one path only.

Path A: repair the hand-written coprime natural-number proof.

Path B: add a small computation file under `python/` and explore prime gaps.

Path C: write `MathBuild/Divisibility.lean` with three or four basic divisibility lemmas.

## Weekly meta-log

Use `logs/meta_log_week1.md` and answer only four sections:

- Wins: what worked?
- Failures: what did not?
- Conjectures: what did you guess?
- Next 3 tasks: concrete steps.

## Lock rule

v3.1 is locked only by this command succeeding:

```bash
lake build MathBuild
```

No claim, title, or handoff text overrides the build result.
