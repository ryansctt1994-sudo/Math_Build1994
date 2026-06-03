# Coprime Proof Repair Notes

## Status

The original hand-written natural-number proof of irrationality of the square root of 2 is not locked yet.

It had useful mathematical intent, but the pasted Lean source contained hard failures:

1. An editor suggestion line was pasted into the source: `simp? at h says ...`.
2. The name `hb` was reused for two different facts.
3. The proof tried to move through the substitution `a = 2 * a'` without a clean arithmetic normalization step.

## Current v3.1 policy

The Day-1 theorem is intentionally short and stable:

```lean
import Mathlib

namespace MathBuild

theorem sqrt2_irrational_real : Irrational (Real.sqrt 2) := by
  simpa using irrational_sqrt_two

end MathBuild
```

This is a legitimate first brick because it builds against Mathlib's maintained theorem.

## Repair target

The repair branch should eventually add a second theorem with no direct call to `irrational_sqrt_two`:

```lean
theorem sqrt2_no_coprime_solution
    (a b : Nat)
    (hb_pos : b > 0)
    (hcop : Nat.gcd a b = 1)
    (h : a ^ 2 = 2 * b ^ 2) : False := by
  -- repair proof here
```

Then a wrapper theorem can reduce an arbitrary rational representation to a coprime one.

## Lock condition

The repair branch is not accepted until:

```bash
lake build MathBuild
```

passes locally or in CI.
