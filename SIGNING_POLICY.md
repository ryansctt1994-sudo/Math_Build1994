# Signing Policy

Status: DRAFT v0.1

Repository: Math_Build1994

Constitutional Status: Phase 4C — Cryptographic Custody Policy

## Purpose

This document defines the conditions under which constitutional receipts may be cryptographically signed.

A signature certifies provenance and custody.

A signature does not certify truth.

A signature does not certify mathematical significance.

A signature does not grant authority beyond the scope explicitly defined here.

## Core Principle

Provenance Non-Forgery Principle:

> No representation may silently inherit the authority of the thing it represents.

A signature certifies:

- A specific artifact existed.
- A specific signer attested to that artifact.
- The signer acted under this repository policy.

A signature does not certify:

- Mathematical correctness beyond available verification.
- Future reproducibility.
- Production readiness.
- Scientific truth.

## Constitutional Ordering

Receipts must pass through the following stages:

```text
Receipt
  -> Replay
  -> Replay Governance
  -> Environment Drift Detection
  -> Receipt Verification
  -> Signing Eligibility
  -> Signature
  -> Registry Governance
```

No stage may be skipped.

## Eligible Artifact Classes

The following artifact classes may become signable:

- `LEAN_BUILD`
- `LEAN_THEOREM`
- `REPLAY_BUILD`
- `RELEASE`

All other artifact classes are non-signable unless explicitly added by amendment.

## Signing Eligibility Requirements

A receipt becomes eligible for signing only if all conditions hold.

### Requirement 1 — Schema Valid

`verify_receipt.py` must return `PASS`.

### Requirement 2 — Replay Success

The replay matrix must contain at least one replay entry with:

```text
replay_result == SUCCESS
```

### Requirement 3 — Environment Match

The most recent replay must report:

```text
environment_match == true
```

### Requirement 4 — Replay Observation Window

The receipt must survive a minimum replay observation period.

Initial policy:

```text
30 calendar days
```

This window may be modified by future amendment.

### Requirement 5 — No Active Failure Reports

There must be no unresolved issue affecting the receipt with labels such as:

- `replay-failure`
- `custody-compromise`
- `environment-drift`

### Requirement 6 — Trusted Signer

The signer must appear in `TRUSTED_KEYS.json`, and the key must be active.

## Signing Procedure

1. Verify receipt eligibility.
2. Verify replay matrix status.
3. Verify environment match.
4. Verify signer enrollment.
5. Generate detached signature.
6. Commit signature artifact.
7. Record signing event in WITNESS.

## Signature Scope

A signature certifies:

- Receipt identity
- Receipt hash
- Signer identity
- Signing timestamp

A signature does not certify:

- Correctness of future builds
- Correctness of future proofs
- Correctness of future environments

## Revocation

A signature may be revoked if:

- The signing key is compromised.
- Provenance is found to be falsified.
- Replay evidence is discovered to be fraudulent.
- Registry governance determines custody was violated.

Revocation must be recorded in WITNESS.

Previous signed artifacts remain historically visible.

History may be annotated but not erased.

## Trust Root Enrollment

New keys require:

- Public key publication
- Repository review
- Chronicle or issue entry
- Registry update

No private key material may be stored in the repository.

## Current Repository Status

Current status:

- Receipt Governance: ACTIVE
- Replay Governance: ACTIVE
- Environment Drift Detection: ACTIVE
- Cryptographic Custody: NOT ACTIVE

Trust Roots:

```text
SIMULATED
```

Receipt Status:

```text
UNSIGNED_REFERENCE_RECEIPTS
```

No artifact in the repository currently satisfies this policy for cryptographic custody.

## Constitutional Seal

A receipt may be replayed without being signed.

A receipt may be signed without being true.

A receipt may be true without being signed.

A signature certifies custody, not reality.

History records all three.
