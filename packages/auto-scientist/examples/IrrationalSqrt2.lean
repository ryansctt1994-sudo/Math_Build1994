import Mathlib

namespace WeaverScience

/-- First operational proof brick: the square root of two is irrational. -/
theorem sqrt_two_is_irrational : Irrational (Real.sqrt 2) := by
  exact irrational_sqrt_two

end WeaverScience

