# Weaver Auto Scientist / MathOS

An evidence-governed laboratory for computational experiments, theorem
checking, falsification, replay, and claim promotion.

The central lifecycle is:

```text
Question -> Hypothesis -> Plan -> Experiment -> Audit -> Replay
         -> Independent Witness -> Promotion
```

The system never treats a tactic suggestion, a demo heuristic, a successful
local subprocess, or an AI-written explanation as a proof. Lean results are
`VERIFIED` only when the real checker exits successfully. Missing Lean is
`UNAVAILABLE`, not success.

```bash
PYTHONPATH=../Weaver_Os/src:src python tests/run_tests.py
```

## Consolidated sources

- `Math_Build1994`: Lean pinning, proof receipts, and replay posture;
- `AutoProof`: human-in-the-loop proof UI and feedback concepts;
- `A.G.I-Seed-`: sufficiency checks, retained as advisory until calibrated;
- `AI-Research-SKILLs` and Hugging Face `skills`: external research skill packs;
- `t81-benchmarks`: benchmark schemas and publication discipline;
- Quillan/OWL/Ruflo: optional research-agent and routing adapters;
- Weaver/Lumen: receipts, replay, promotion, and non-claim boundaries.

`Delta-RPM-Protocol` is all-rights-reserved and is reference-only. No source
code or scientific claims from it are included.

