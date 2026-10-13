"""Pure fixtures for v2 review, recipe, identity and scoring; no ML imports.

Record-level fixtures do not introduce new financial-language test cases.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import learning_cycle_v2 as cycle
from test_learning_cycle import observed


def fixture_rows():
    descriptors = [("clear", "D5_WITHDRAWALS"), ("clear", "D5_WITHDRAWALS"),
        ("clear", "D5_SALARY"), ("clear", "D5_MULTIPLE"), ("incomplete", None),
        ("incomplete", None), ("undecided", None), ("confusion", None)]
    known = [("clear", "D5_PENSION_PAYMENTS"), ("clear", "D5_MULTIPLE"),
        ("clear", "D5_SALARY"), ("clear", "D5_BENEFITS_SUPPORT"),
        ("clear", "D5_BENEFITS_SUPPORT"), ("clear", "D5_WITHDRAWALS"),
        ("incomplete", None), ("clear", "D5_NO_REGULAR"), ("incomplete", None),
        ("undecided", None), ("confusion", None)]
    rows = []
    for split, prefix, meanings in (("opened_validation", "D5-LV", descriptors),
            ("existing_regression", "D5-STD", known), ("validation", "D5-V2-LV", descriptors)):
        for index, (kind, option) in enumerate(meanings, 1):
            control = kind == "confusion"
            baseline = observed(kind, option or "D5_SALARY", control=control)
            rows.append({"id": f"{prefix}-{index:02d}", "split": split,
                "expected": {"kind": kind, "bucket": "clarity" if kind == "clear" else
                    None if kind == "incomplete" else kind, "option_id": option,
                    "control_required": split == "existing_regression" and index == 11},
                "baseline": baseline,
                "candidate": observed(kind, option or "D5_SALARY",
                    control=control, accepted=split == "validation" and index == 1),
                "previous_v1_candidate": deepcopy(baseline) if split != "validation" else None})
    return rows


def by_id(rows, identifier):
    return next(row for row in rows if row["id"] == identifier)


def approved_review():
    return {"schema_version": "d5-learning-review-v2", "review_type": "human_business_review",
        "status": "approved", "reviewer": "Fixture business reviewer", "reviewed_at": "2026-10-13T19:00:00+01:00",
        "dataset_sha256": {"training": "current", "validation": "current"},
        "approved_case_ids": [f"D5-V2-LT-{n:02d}" for n in range(1, 17)] +
            [f"D5-V2-LV-{n:02d}" for n in range(1, 9)],
        "provenance_acknowledgement": "agent_authored_human_reviewed"}


class ReviewAndRecipeTests(unittest.TestCase):
    def test_pending_review_blocks_before_hash_reads(self):
        with patch.object(cycle.v1, "file_hash", side_effect=AssertionError("not needed")):
            with self.assertRaisesRegex(cycle.v1.CycleError, "explicit_v2_human_business_approval_required"):
                cycle.validate_review(dict(approved_review(), status="pending_human_business_review"),
                    Path("unused"), Path("unused"), [])

    def test_all_twenty_four_ids_and_hashes_are_required(self):
        review = approved_review()
        ids = review["approved_case_ids"]
        with patch.object(cycle.v1, "file_hash", return_value="current"):
            cycle.validate_review(review, Path("train"), Path("validation"), ids)
            with self.assertRaisesRegex(cycle.v1.CycleError, "all_twenty_four_case_ids_need_explicit_review"):
                cycle.validate_review(dict(review, approved_case_ids=ids[:-1]), Path("train"), Path("validation"), ids)
            changed = deepcopy(review)
            changed["dataset_sha256"]["training"] = "old"
            with self.assertRaisesRegex(cycle.v1.CycleError, "reviewed_dataset_hash_mismatch"):
                cycle.validate_review(changed, Path("train"), Path("validation"), ids)

    def test_v1_approval_does_not_approve_new_labels(self):
        with self.assertRaisesRegex(cycle.v1.CycleError, "explicit_v2_human_business_approval_required"):
            cycle.validate_review(dict(approved_review(), schema_version="d5-learning-review-v1"),
                Path("unused"), Path("unused"), [])

    def test_review_failure_precedes_models_and_phase_start(self):
        with patch.object(cycle, "verify_cycle", side_effect=cycle.v1.CycleError("explicit_v2_human_business_approval_required")), \
             patch.object(cycle.v1, "runtime_baseline", side_effect=AssertionError("must not import models")), \
             patch.object(cycle.v1, "begin_phase", side_effect=AssertionError("must not start")):
            with self.assertRaises(cycle.v1.CycleError):
                cycle.build(Path("unused"))
            with self.assertRaises(cycle.v1.CycleError):
                cycle.compare(Path("unused"))

    def test_exact_training_and_calibration_recipe(self):
        original = ([{"bucket": "clarity"}] * 48 + [{"bucket": "undecided"}] * 4 + [{"bucket": "confusion"}] * 4)
        calibration = ([{"bucket": "clarity"}] * 40 + [{"bucket": "undecided"}] * 10 + [{"bucket": "confusion"}] * 10)
        old = [{"bucket": "clarity"}] * 8
        new = [{"bucket": "clarity"}] * 8 + [{"bucket": "undecided"}] * 4 + [{"bucket": "confusion"}] * 4
        assembled = cycle.recipe(original, calibration, old, new)
        self.assertEqual((len(assembled["intent"][0]), len(assembled["option"][0])), (80, 64))
        self.assertIs(assembled["intent"][1], calibration)
        self.assertEqual(len(assembled["option"][1]), 40)
        self.assertEqual((assembled["intent"][2], assembled["option"][2]), ("bucket", "option_id"))
        with self.assertRaises(cycle.v1.CycleError):
            cycle.recipe(original, calibration + [{"bucket": "clarity"}], old, new)
        with self.assertRaises(cycle.v1.CycleError):
            cycle.recipe(original, calibration, old, new[:-1])

    def test_sixteen_training_labels_have_fixed_composition(self):
        rows = []
        for index, option in enumerate(["D5_WITHDRAWALS"] * 4 + ["D5_SALARY"] * 2 + ["D5_MULTIPLE"] * 2 + [None] * 8, 1):
            kind = "clear" if index <= 8 else "undecided" if index <= 12 else "confusion"
            rows.append({"id": f"D5-V2-LT-{index:02d}", "question_id": "D5", "split": "train", "kind": kind,
                "text": f"record-{index}", "bucket": "clarity" if kind == "clear" else kind, "option_id": option,
                "business_meaning": "fixture", "expected_action": "fixture", "source": "fixture", "group_id": str(index)})
        with patch.object(cycle.v1, "read_json", return_value={"rows": rows}):
            self.assertEqual(len(cycle.training_rows(Path("unused"))), 16)
            rows[-1]["kind"] = rows[-1]["bucket"] = "undecided"
            with self.assertRaisesRegex(cycle.v1.CycleError, "fixed_v2_training_composition_required"):
                cycle.training_rows(Path("unused"))

    def test_both_artifact_hashes_are_checked_before_loading(self):
        with tempfile.TemporaryDirectory(prefix="d5-v2-software-") as directory:
            root = Path(directory)
            (root / "protocol.json").write_text("fixture protocol")
            for axis, name in cycle.ARTIFACTS.items():
                (root / name).write_bytes(f"fixture-{axis}".encode())
            identity = {"protocol_sha256": cycle.v1.file_hash(root / "protocol.json"),
                "artifacts": {axis: cycle.v1.file_hash(root / name) for axis, name in cycle.ARTIFACTS.items()},
                "baseline_identity": "baseline", "baseline_source_hash": "source"}
            built = {"identity": identity, "candidate_identity_sha256": cycle.v1.digest(identity),
                "candidate_fit_counts": {"intent": 1, "option": 1}}
            cycle.verify_artifacts(root, built, "baseline", "source")
            for axis, name in cycle.ARTIFACTS.items():
                with self.subTest(axis=axis):
                    original = (root / name).read_bytes()
                    (root / name).write_bytes(b"changed")
                    with self.assertRaisesRegex(cycle.v1.CycleError, "candidate_two_artifact_identity_mismatch"):
                        cycle.verify_artifacts(root, built, "baseline", "source")
                    (root / name).write_bytes(original)
            built["candidate_fit_counts"]["intent"] = 2
            with self.assertRaises(cycle.v1.CycleError):
                cycle.verify_artifacts(root, built, "baseline", "source")

    def test_frozen_change_and_retry_remain_rejected(self):
        with tempfile.TemporaryDirectory(prefix="d5-v2-software-") as directory:
            root = Path(directory)
            source = root / "fixture.txt"
            source.write_text("original")
            frozen = {"fixture.txt": cycle.v1.file_hash(source)}
            source.write_text("changed")
            with self.assertRaisesRegex(cycle.v1.CycleError, "frozen_file_changed"):
                cycle.v1.verify_frozen_files(frozen, root)
            cycle.v1.begin_phase(root, "build")
            with self.assertRaisesRegex(cycle.v1.CycleError, "phase_already_attempted_no_retry"):
                cycle.v1.begin_phase(root, "build")


class UnionScoringTests(unittest.TestCase):
    def assert_gate(self, rows, gate, compared_with=None):
        result = cycle.score_comparison(rows)
        self.assertFalse(result["first_turn_gates_passed"])
        self.assertTrue(any(item["gate"] == gate and (compared_with is None or item.get("compared_with") == compared_with)
                            for item in result["blocking_gates"]), result["blocking_gates"])
        self.assertFalse(result["candidate_ready_for_demo"])

    def test_passing_first_turn_fixture_still_has_no_demo_profile(self):
        result = cycle.score_comparison(fixture_rows())
        self.assertTrue(result["first_turn_gates_passed"], result["blocking_gates"])
        self.assertEqual(result["new_correct_accepted_validation_savings_ids"], ["D5-V2-LV-01"])
        self.assertFalse(result["candidate_ready_for_demo"])

    def test_union_keeps_v1_only_std06_raw_success(self):
        rows = fixture_rows()
        row = by_id(rows, "D5-STD-06")
        row["baseline"]["raw"]["option"]["argmax"] = "D5_PENSION_PAYMENTS"
        row["candidate"]["raw"]["option"]["argmax"] = "D5_PENSION_PAYMENTS"
        self.assert_gate(rows, "no_new_raw_error_preserve_previous_success", "frozen_previous_v1_candidate")

    def test_union_keeps_baseline_only_success(self):
        rows = fixture_rows()
        row = by_id(rows, "D5-STD-03")
        row["previous_v1_candidate"]["raw"]["option"]["argmax"] = "D5_MULTIPLE"
        row["candidate"]["raw"]["option"]["argmax"] = "D5_MULTIPLE"
        self.assert_gate(rows, "no_new_raw_error_preserve_previous_success", "unchanged_baseline")

    def test_union_keeps_previous_accepted_answer(self):
        rows = fixture_rows()
        by_id(rows, "D5-STD-06")["previous_v1_candidate"] = observed(option="D5_WITHDRAWALS", accepted=True)
        self.assert_gate(rows, "preserve_accepted_financial_success", "frozen_previous_v1_candidate")

    def test_union_keeps_previous_correct_confident_dialogue(self):
        rows = fixture_rows()
        by_id(rows, "D5-STD-10")["previous_v1_candidate"].update(route="ml", ordinary_bucket="Undecided",
            result_bucket="Undecided", ml_uncertain=False, escalation_required=False)
        self.assert_gate(rows, "preserve_correct_confident_dialogue", "frozen_previous_v1_candidate")

    def test_all_opened_and_fresh_clear_options_are_required(self):
        for identifier in ("D5-LV-04", "D5-V2-LV-04"):
            with self.subTest(identifier=identifier):
                rows = fixture_rows()
                by_id(rows, identifier)["candidate"]["raw"]["option"]["argmax"] = "D5_SALARY"
                self.assert_gate(rows, "all_eight_opened_and_fresh_clear_raw_options")

    def test_known_gain_cannot_replace_fresh_savings_gain(self):
        rows = fixture_rows()
        row = by_id(rows, "D5-V2-LV-01")
        row["candidate"] = deepcopy(row["baseline"])
        by_id(rows, "D5-LV-01")["candidate"] = observed(accepted=True)
        self.assert_gate(rows, "at_least_one_fresh_savings_escalation_becomes_ml_acceptance")

    def test_fresh_gain_requires_baseline_escalation_and_real_receipt(self):
        for mutation in ({"escalation_required": False}, {"route": "ml"}):
            rows = fixture_rows()
            by_id(rows, "D5-V2-LV-01")["baseline"].update(mutation)
            self.assert_gate(rows, "at_least_one_fresh_savings_escalation_becomes_ml_acceptance")
        rows = fixture_rows()
        by_id(rows, "D5-V2-LV-01")["candidate"]["ml_receipt_issued"] = False
        self.assert_gate(rows, "real_ml_receipt_required")

    def test_clear_confident_wrong_bucket_is_not_safe_escalation(self):
        for identifier in ("D5-LV-03", "D5-V2-LV-03"):
            rows = fixture_rows()
            by_id(rows, identifier)["candidate"].update(route="ml", ordinary_bucket="Undecided", ml_uncertain=False)
            self.assert_gate(rows, "clear_validation_no_wrong_confident_dialogue")

    def test_incomplete_and_nonclear_cannot_commit_financially(self):
        rows = fixture_rows()
        by_id(rows, "D5-V2-LV-05")["candidate"].update(resolver_candidate="D5_WITHDRAWALS", ml_uncertain=False)
        self.assert_gate(rows, "incomplete_no_confident_financial_commitment")
        rows = fixture_rows()
        by_id(rows, "D5-V2-LV-07")["candidate"].update(resolver_candidate="D5_WITHDRAWALS", ml_uncertain=False)
        self.assert_gate(rows, "nonclear_no_confident_financial_commitment")

    def test_incomplete_cannot_be_labelled_customer_indecision(self):
        rows = fixture_rows()
        by_id(rows, "D5-V2-LV-06")["candidate"].update(ordinary_bucket="Undecided", ml_uncertain=False)
        self.assert_gate(rows, "incomplete_no_invented_customer_bucket")

    def test_false_clarity_wrong_acceptance_and_state_side_effects_fail(self):
        rows = fixture_rows()
        by_id(rows, "D5-V2-LV-07")["candidate"]["raw"]["intent"]["argmax"] = "clarity"
        self.assert_gate(rows, "no_new_raw_false_clarity")
        rows = fixture_rows()
        by_id(rows, "D5-V2-LV-03")["candidate"] = observed(option="D5_MULTIPLE", accepted=True)
        self.assert_gate(rows, "no_wrong_accepted_financial_answer")
        rows = fixture_rows()
        by_id(rows, "D5-V2-LV-01")["candidate"]["saved_version"] = 1
        self.assert_gate(rows, "proposal_must_not_confirm_or_save")

    def test_help_and_gpt_calls_have_separate_zero_call_gates(self):
        rows = fixture_rows()
        by_id(rows, "D5-STD-11")["candidate"]["routing_ml_calls"] = 1
        self.assert_gate(rows, "existing_help_zero_models")
        rows = fixture_rows()
        by_id(rows, "D5-V2-LV-01")["candidate"]["actual_gpt_calls"] = 1
        self.assert_gate(rows, "offline_no_gpt_calls")

    def test_missing_case_or_previous_reference_cannot_pass(self):
        rows = fixture_rows()
        self.assert_gate(rows[:-1], "exact_27_cases_and_reference_denominators")
        rows[0]["previous_v1_candidate"] = None
        self.assert_gate(rows, "exact_27_cases_and_reference_denominators")

    def test_baseline_parity_uses_stable_decisions_not_timings(self):
        first = observed()
        second = deepcopy(first)
        second["elapsed_seconds"] = 123
        second["raw"]["option"]["probabilities"] = {"D5_WITHDRAWALS": 0.9}
        self.assertEqual(cycle.semantic_fields(first), cycle.semantic_fields(second))
        second["raw"]["option"]["prediction_set"] = ["D5_SALARY", "D5_WITHDRAWALS"]
        self.assertNotEqual(cycle.semantic_fields(first), cycle.semantic_fields(second))


if __name__ == "__main__":
    unittest.main()
