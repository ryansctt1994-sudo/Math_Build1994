import Mathlib.NumberTheory.Real.Irrational
import Mathlib.Tactic

namespace MathBuild

/--
Coprime-denominator obstruction behind the classical √2 proof.

If `m` and `n` are coprime natural numbers, then `m^2 = 2*n^2` is impossible:
2 divides `m`, hence 2 divides `n`, contradicting coprimality.
-/
theorem coprime_square_ne_two_mul_square (m n : ℕ) (hcop : m.Coprime n) :
    m ^ 2 ≠ 2 * n ^ 2 := by
  intro h
  have h2_dvd_m_sq : 2 ∣ m ^ 2 := by
    rw [h]
    exact dvd_mul_right 2 (n ^ 2)
  have h2_dvd_m : 2 ∣ m := Nat.prime_two.dvd_of_dvd_pow h2_dvd_m_sq
  have h2_dvd_n_sq : 2 ∣ n ^ 2 := by
    rcases h2_dvd_m with ⟨k, hk⟩
    use k ^ 2
    rw [hk] at h
    nlinarith
  have h2_dvd_n : 2 ∣ n := Nat.prime_two.dvd_of_dvd_pow h2_dvd_n_sq
  have htwo_eq_one : 2 = 1 := Nat.eq_one_of_dvd_coprimes hcop h2_dvd_m h2_dvd_n
  norm_num at htwo_eq_one

/-- `2` is not a square in `ℕ`, proved through the coprime obstruction above. -/
theorem two_not_isSquare_nat : ¬ IsSquare (2 : ℕ) := by
  rintro ⟨n, hn⟩
  have hcop : n.Coprime 1 := by simp
  have hsq : n ^ 2 = 2 * 1 ^ 2 := by
    simpa [pow_two] using hn.symm
  exact coprime_square_ne_two_mul_square n 1 hcop hsq

/-- Day-1 operational theorem: √2 is irrational, without the forbidden direct shim. -/
theorem sqrt2_irrational_real : Irrational (Real.sqrt 2) := by
  simpa using irrational_sqrt_natCast_iff.mpr two_not_isSquare_nat

end MathBuild
