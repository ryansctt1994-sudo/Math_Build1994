import Mathlib

namespace MathBuild

/--
Day-1 operational theorem: √2 is irrational.

This first brick intentionally uses Mathlib's maintained theorem rather than
pretending an unverified hand-written coprime proof is complete.

Build target:

  lake build MathBuild
-/
theorem sqrt2_irrational_real : Irrational (Real.sqrt 2) := by
  simpa using irrational_sqrt_two

end MathBuild
