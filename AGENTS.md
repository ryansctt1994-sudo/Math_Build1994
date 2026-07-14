# Math Build Repository Contract

## Role

`Math_Build1994` is the formal methods and Auto Scientist laboratory in the Weaver Nexus three-repository master build.
It owns proof source, model-checking specifications, reproducible numerical experiments, benchmark harnesses, RTL simulations, cryptographic vectors, and machine-readable proof or failure receipts.

It does not grant runtime authority. `Weaver_Os` owns constitutional policy and promotion decisions. `Lumen` owns executable Chronicle, receipt, and replay infrastructure.

## Claim namespaces

Every result must use one exact modality:

- `FORMAL_SOURCE_PRESENT`
- `FORMAL_BUILD_PASSED`
- `MODEL_CHECK_PASSED`
- `FINITE_EXHAUSTIVE_CHECK_PASSED`
- `PROPERTY_TEST_PASSED`
- `NUMERICAL_EXPERIMENT_OBSERVED`
- `RTL_SIMULATION_PASSED`
- `HARDWARE_MEASURED`
- `FAILED`
- `UNVERIFIED`

Never collapse these into a generic `verified` label.

## Prohibited promotion paths

- Lean `sorry`, `admit`, or hidden shortcut theorems in promoted proofs.
- Agda postulates presented as completed proofs.
- TLA+ specifications without model-check output presented as verified systems.
- Property tests presented as deductive proofs unless finite exhaustiveness is established.
- RTL simulation presented as silicon validation.
- Numerical fit presented as theorem proof.
- Placeholder hashes or generated receipts without source and environment binding.

## Completion gate

Every promoted result must bind:

1. claim identifier and exact claim text;
2. source commit and file digest;
3. toolchain and dependency lock;
4. exact command;
5. raw stdout, stderr, and exit code;
6. assumptions and trusted computing base;
7. placeholder/admission audit;
8. negative or mutation test where applicable;
9. artifact hashes;
10. explicit non-claims;
11. independent reproduction status.

A failed proof, model check, simulation, or experiment must be retained as evidence.