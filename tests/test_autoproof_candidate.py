"""Unit tests for structurally bound AutoProof candidate, never acceptance."""
import copy
import hashlib
import json
import unittest

from scripts.inspect_autoproof_candidate import CandidateRefused, inspect_candidate


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def digest(data):
    return "sha256:" + sha(json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def good():
    signature = "theorem autoproof_goal (n : Nat) : n + 0 = n"
    source = signature + " := by\n  simp\n"
    candidate = {
        "schema_version": "autoproof-candidate/1",
        "source_system": "AutoProof",
        "session_id": "session-123",
        "attempt_id": "attempt-123",
        "goal_name": "autoproof_goal",
        "statement": "n + 0 = n",
        "binders": "(n : Nat)",
        "statement_sha256": sha(signature),
        "proof_text": "simp",
        "proof_sha256": sha("simp"),
        "generated_lean_source": source,
        "source_sha256": sha(source),
        "checker_version": "3",
        "lean_version_reported": "Lean (fixture only)",
        "axioms_reported": [],
        "verdict_reported": "verified",
    }
    return {
        "candidate": candidate,
        "candidate_sha256": digest(candidate),
        "authority": "NONE",
        "mathbuild_acceptance": "NOT_EVALUATED",
        "independent_reproduction": False,
    }


class APHandoffTests(unittest.TestCase):
    def test_good_structural_binding_never_grants_authority(self):
        result = inspect_candidate(good())
        self.assertEqual(result["inspection"], "STRUCTURALLY_BOUND_ONLY")
        self.assertFalse(result["accepted"])
        self.assertEqual(result["authority"], "NONE")
        self.assertIn("canonical inclusion at an exact MathBuild commit",
                      result["remaining_obligations"])

    def test_field_tampering_fails_closed(self):
        cases = [
            ("statement", "0 = 1"),
            ("proof_text", "sorry"),
            ("source_sha256", "f" * 64),
            ("statement_sha256", "a" * 64),
            ("proof_sha256", "b" * 64),
            ("generated_lean_source", "theorem fake : True := by trivial"),
            ("goal_name", "another"),
            ("session_id", ""),
            ("verdict_reported", "incomplete"),
            ("axioms_reported", ["user_axiom"]),
        ]
        for key, value in cases:
            with self.subTest(key=key):
                envelope = good()
                envelope["candidate"][key] = value
                with self.assertRaises(CandidateRefused):
                    inspect_candidate(envelope)

    def test_envelope_tampering_fails_closed(self):
        for key, value in [
            ("authority", "ACCEPT"),
            ("mathbuild_acceptance", "PASS"),
            ("independent_reproduction", True),
            ("candidate_sha256", "sha256:" + "0" * 64),
        ]:
            with self.subTest(key=key):
                envelope = good()
                envelope[key] = value
                with self.assertRaises(CandidateRefused):
                    inspect_candidate(envelope)

    def test_rehashed_forgery_is_not_a_proof_or_accepted(self):
        envelope = good()
        candidate = envelope["candidate"]
        candidate["session_id"] = "forged-session"
        envelope["candidate_sha256"] = digest(candidate)
        result = inspect_candidate(envelope)
        # Hash consistency is NOT cryptographic authenticity or MathBuild proof.
        self.assertEqual(result["inspection"], "STRUCTURALLY_BOUND_ONLY")
        self.assertFalse(result["accepted"])


if __name__ == "__main__":
    unittest.main()
