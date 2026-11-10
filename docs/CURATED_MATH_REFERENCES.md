# Curated mathematics references and Lean proof-development map

**Status:** non-normative research guidance; no theorem, build, replay, or acceptance claim.
**Prepared:** 2026-11-10.
**Source catalog:** [Awesome_Math_Books](https://github.com/ryansctt1994-sudo/Awesome_Math_Books) (inspected `main`, revision `3ab4deb456d7b52a28cfefa5b52ebed9b850187e`).
**Catalog provenance:** the source README links to [valeman/Awesome_Math_Books](https://github.com/valeman/Awesome_Math_Books) and contains the original curator's first-person copy. Attribute the underlying catalog; do not infer ownership of every linked book.
**Implementation baseline:** `lake build MathBuild` remains the only Lean lock command; see [repair PR #6](https://github.com/ryansctt1994-sudo/Math_Build1994/pull/6). This reference plan is intentionally independent of PR #6, and must not be used to claim its post-merge acceptance gate passed.

## Scope and rules

The bibliography is **input for selecting original proof obligations**, not executable trusted evidence. A book citation, a PDF, or a catalog entry is never a Lean proof receipt. No textbook scans, covers, or full exercise sets are vendored. Publisher/author permissions and actual availability must be reviewed before any redistribution. Prefer author, publisher, university, or explicitly licensed sources over anonymous mirrors.

The reader should not assume that the source catalog's praise, historical circulation numbers, or marketing claims were verified by this document. The cited links identify resources or publishers; they do not verify the proof correctness of all their contents.

## Selected references → possible proof tasks

| Priority | Reference | Authoritative or attribution-conscious link | Relevance / *new* candidate Lean task | Status |
| --- | --- | --- | --- | --- |
| P1 | Richard Hammack, *Book of Proof* | [Author's book site](https://richardhammack.github.io/BookOfProof/index.html) | Propositional reasoning, contradiction, induction; demonstrate an original induction lemma over `Nat` | Bibliography only |
| P1 | Lehman, Leighton, Meyer, *Mathematics for Computer Science* | [MIT OpenCourseWare](https://ocw.mit.edu/courses/6-1200j-mathematics-for-computer-science-spring-2024/pages/readings/) | Divisibility, modular arithmetic and induction; define and verify small divisibility lemmas | Bibliography only |
| P1 | Sominskii, *The Method of Mathematical Induction* | [Source-catalog entry](https://github.com/ryansctt1994-sudo/Awesome_Math_Books#math) | Compare proof patterns with Lean's induction principles; do not copy scanned exercises | Bibliography only |
| P1 | I. M. Vinogradov, *Elements of Number Theory* | [Source-catalog entry](https://github.com/ryansctt1994-sudo/Awesome_Math_Books#math) | GCD, primes, modular reasoning; choose small lemmas and verify statements independently | Bibliography only |
| P2 | A. P. Kiselev, *Arithmetic / Algebra* | [Publisher and translator's catalog](https://russianmathbooks.com/) | Independent arithmetic proofs and proof pedagogy; commercial translations are not permission to redistribute text | Bibliography only |
| P2 | Deisenroth, Faisal, Ong, *Mathematics for Machine Learning* | [Cambridge University Press](https://www.cambridge.org/highereducation/books/mathematics-for-machine-learning/5EE57FD1CFB23E6EB11E130309C7EF98) | Later study map for linear algebra and probability; no near-term Lean expansion authorized | Bibliography only |
| P3 | Kolmogorov, *Foundations of the Theory of Probability* | [Source-catalog entry](https://github.com/ryansctt1994-sudo/Awesome_Math_Books#math) | Future probability formalization requiring explicit sample-space and measure assumptions | Deferred |
| P3 | Nemirovski, *Lectures on Modern Convex Optimization* | [Source-catalog entry](https://github.com/ryansctt1994-sudo/Awesome_Math_Books#optimization) | Future optimization formalization; outside the current first-brick lock | Deferred |

**Copyright note:** the Hammack book has a Creative Commons Attribution–NonCommercial–NoDerivatives license on its author-hosted site; bibliographic linking does not authorize adapting its text. MIT's 2024 course describes its textbook under CC BY-SA. Cambridge lists its machine-learning text as publisher-controlled. Check the precise edition and conditions before reuse.

## Proposed executable milestones (all unimplemented)

The next targets should be designed as independent Lean source contributions **after** baseline repair is accepted, not smuggled into an unrelated CI fix.

1. **MATH-LIT-001 — induction:** state an elementary natural-number identity in `MathBuild/Induction.lean`; compare a handwritten induction proof against the corresponding Mathlib theorem, if one exists.
2. **MATH-LIT-002 — divisibility:** prove a small implication such as `a ∣ b → a ∣ b*c` with explicit natural-number quantifiers; document any imported lemma. Avoid claiming novelty where Mathlib already proves it.
3. **MATH-LIT-003 — coprimality and sqrt(2):** independently reconstruct the parity/gcd steps of a coprime-based irrationality argument without weakening the existing Mathlib-backed lock. Do not label the handwritten version verified until its declaration is imported by the root and built.
4. **MATH-LIT-004 — prime-number foundations:** inspect Lean definitions of primes and formalize one bounded proposition. Do not silently infer an entire fundamental theorem of arithmetic from an example.
5. **MATH-LIT-005 — discrete probability:** only after a separate specification gate, formalize a finite sample space and a carefully bounded probability identity. No claims about general machine-learning reliability follow.

These are a **candidate backlog**. The statements, names, imports, and tactics are not asserted to compile as written.

## Per-theorem acceptance record (proposed)

Each new proof PR must record:

- `theorem_id`, mathematical statement, definitions, type universe and assumptions, and bibliographic inspiration.
- Lean file path; exact statement accepted by the kernel; import closure and root-module membership.
- Pinned source commit, Lean toolchain, Mathlib dependency lock/manifest, environment identity, and `lake build MathBuild` result.
- Dependency and axiom review (including `sorry`/`admit`, externally trusted axioms, and proof-term status).
- A retrievable artifact/receipt and exact workflow run; if reproduction is claimed, independent operator/environment evidence.
- Explicit result `PROPOSED / BUILT / REPLAYED / INDEPENDENTLY_REPRODUCED` for this theorem only. Missing evidence remains `HOLD`.

A successful documentation-only PR is not a successful Lean theorem build. Do not advance Math_Build1994's repository health or E4 status because of this reference plan.

## Integrating with the governed assurance architecture

`reference → original formal statement → Lean build → bound execution receipt → governed acceptance → independent reproduction`

The reference supplies human-readable motivation. The Lean kernel provides a conditional formal-checking result for imported declarations. The execution and evidence layers establish provenance. The acceptance verifier determines whether repository-level claims may be promoted. Each arrow is a new obligation, not automatic inheritance.

## Pending validation

- Review source-catalog link availability, editions, attribution, licensing, and duplicate titles independently; no exhaustive HTTP audit was performed.
- Do not merge this doc as a substitute for [PR #6](https://github.com/ryansctt1994-sudo/Math_Build1994/pull/6) or the post-merge Lean Build + Replay Governance gate.
- Later, test proposed theorem modules under the exact pinned Lean environment and retain exact-SHA CI receipts.
