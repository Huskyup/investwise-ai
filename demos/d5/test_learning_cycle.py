"""Pure review/integrity/scoring tests; never fit or call an ML/LLM model.

These fixtures describe records, not additional financial language examples.
They may verify software before review; fitting still requires human approval.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import learning_cycle as cycle


def prediction(label):
    return {"argmax": label, "prediction_set": [label], "probabilities": {label: 1.0},
            "threshold": 0.5, "alpha": 0.10}


def observed(kind="clear", option="D5_WITHDRAWALS", *, accepted=False, control=False):
    bucket = "clarity" if kind == "clear" else kind
    if kind == "incomplete":
        bucket = "clarity"  # Diagnostic only; this kind has no forced raw gold.
    return {"route": "control" if control else "ml" if accepted else "ml_then_gpt",
        "action": "explain" if control else "confirm" if accepted else "escalation_required_not_executed",
        "raw": None if control else {"intent": prediction(bucket), "option": prediction(option)},
        "ordinary_bucket": "Clarity" if accepted else None,
        "result_bucket": "Clarity" if accepted else None,
        "ml_uncertain": not accepted, "resolver_candidate": option if accepted else None,
        "accepted_candidate": option if accepted else None,
        "ml_receipt_issued": accepted,
        "routing_ml_calls": 0 if control else 1, "diagnostic_predictor_calls": 0 if control else 2,
        "actual_gpt_calls": 0, "escalation_required": not control and not accepted}


def score_records():
    """Exactly the frozen split composition, using record-only fixtures."""
    descriptors = [
        ("clear", "D5_WITHDRAWALS"), ("clear", "D5_WITHDRAWALS"),
        ("clear", "D5_SALARY"), ("clear", "D5_MULTIPLE"),
        ("incomplete", None), ("incomplete", None),
        ("undecided", None), ("confusion", None)]
    rows = []
    for index, (kind, option) in enumerate(descriptors, 1):
        rows.append({"id": f"D5-LV-{index:02d}", "split": "validation",
            "expected": {"kind": kind, "bucket": "clarity" if kind == "clear" else
                None if kind == "incomplete" else kind, "option_id": option},
            "baseline": observed(kind, option or "D5_SALARY", control=index == 8),
            "candidate": observed(kind, option or "D5_SALARY", accepted=index == 1, control=index == 8)})
    rows.append({"id": "D5-STD-11", "split": "existing_regression",
        "expected": {"kind": "confusion", "bucket": "confusion", "option_id": None,
                     "control_required": True},
        "baseline": observed("confusion", control=True),
        "candidate": observed("confusion", control=True)})
    return rows


class ReviewAndFreezeTests(unittest.TestCase):
    def test_pending_review_cannot_reach_hash_reads(self):
        with patch.object(cycle, "file_hash", side_effect=AssertionError("no file access needed")):
            with self.assertRaisesRegex(cycle.CycleError, "explicit_human_business_approval_required"):
                cycle.validate_review({"schema_version": "d5-learning-review-v1",
                    "review_type": "human_business_review", "status": "pending_human_business_review"},
                    Path("unused-training"), Path("unused-validation"), ["record"])

    def test_approved_review_requires_exact_dataset_hashes(self):
        review = {"schema_version": "d5-learning-review-v1", "review_type": "human_business_review",
            "status": "approved", "reviewer": "Fixture reviewer", "reviewed_at": "2026-10-13T12:00:00+01:00",
            "dataset_sha256": {"training": "stale", "validation": "current"},
            "approved_case_ids": ["record"], "provenance_acknowledgement": "agent_authored_human_reviewed"}
        with patch.object(cycle, "file_hash", return_value="current"):
            with self.assertRaisesRegex(cycle.CycleError, "reviewed_dataset_hash_mismatch"):
                cycle.validate_review(review, Path("training"), Path("validation"), ["record"])

    def test_review_requires_all_ids_and_timezone(self):
        review = {"schema_version": "d5-learning-review-v1", "review_type": "human_business_review",
            "status": "approved", "reviewer": "Fixture reviewer", "reviewed_at": "2026-10-13T12:00:00+01:00",
            "dataset_sha256": {"training": "current", "validation": "current"},
            "approved_case_ids": ["record"], "provenance_acknowledgement": "agent_authored_human_reviewed"}
        with patch.object(cycle, "file_hash", return_value="current"):
            cycle.validate_review(review, Path("training"), Path("validation"), ["record"])
            incomplete = dict(review, approved_case_ids=[])
            with self.assertRaisesRegex(cycle.CycleError, "all_sixteen_case_ids_need_explicit_review"):
                cycle.validate_review(incomplete, Path("training"), Path("validation"), ["record"])
            naive = dict(review, reviewed_at="2026-10-13T12:00:00")
            with self.assertRaisesRegex(cycle.CycleError, "timezone_aware_review_timestamp_required"):
                cycle.validate_review(naive, Path("training"), Path("validation"), ["record"])

    def test_changed_frozen_file_rejected(self):
        with tempfile.TemporaryDirectory(prefix="d5-learning-software-") as directory:
            root = Path(directory)
            (root / "source.txt").write_text("fixture source")
            files = {"source.txt": cycle.file_hash(root / "source.txt")}
            cycle.verify_frozen_files(files, root=root)
            (root / "source.txt").write_text("changed fixture source")
            with self.assertRaisesRegex(cycle.CycleError, "frozen_file_changed"):
                cycle.verify_frozen_files(files, root=root)

    def test_frozen_paths_cannot_escape_root(self):
        with tempfile.TemporaryDirectory(prefix="d5-learning-software-") as directory:
            with self.assertRaisesRegex(cycle.CycleError, "frozen_file_changed"):
                cycle.verify_frozen_files({"../outside": "irrelevant"}, root=Path(directory))

    def test_phase_start_is_write_once_without_fitting(self):
        with tempfile.TemporaryDirectory(prefix="d5-learning-software-") as directory:
            root = Path(directory)
            cycle.begin_phase(root, "build")
            initial = (root / "build.started.json").read_bytes()
            with self.assertRaisesRegex(cycle.CycleError, "phase_already_attempted_no_retry"):
                cycle.begin_phase(root, "build")
            self.assertEqual(initial, (root / "build.started.json").read_bytes())

    def test_failed_phase_is_not_restarted(self):
        with tempfile.TemporaryDirectory(prefix="d5-learning-software-") as directory:
            root = Path(directory)
            cycle.write_once(root / "compare.STOP.json", {"retry": False})
            with self.assertRaisesRegex(cycle.CycleError, "phase_already_attempted_no_retry"):
                cycle.begin_phase(root, "compare")

    def test_review_failure_precedes_phase_start_or_ml_import(self):
        with patch.object(cycle, "verify_cycle", side_effect=cycle.CycleError("explicit_human_business_approval_required")), \
             patch.object(cycle, "runtime_baseline", side_effect=AssertionError("must not import or fit")), \
             patch.object(cycle, "begin_phase", side_effect=AssertionError("must not start")):
            with self.assertRaises(cycle.CycleError):
                cycle.build(Path("unused"))
            with self.assertRaises(cycle.CycleError):
                cycle.compare(Path("unused"))

    def test_offline_boundary_blocks_network_and_subprocess(self):
        with cycle.offline_only():
            with self.assertRaisesRegex(cycle.CycleError, "network_or_subprocess_forbidden"):
                cycle.socket.create_connection(("unused.invalid", 443))
            with self.assertRaisesRegex(cycle.CycleError, "network_or_subprocess_forbidden"):
                cycle.subprocess.Popen(["unused-command"])


class PureScoringTests(unittest.TestCase):
    def assert_gate(self, rows, gate):
        result = cycle.score_comparison(rows)
        self.assertFalse(result["first_turn_gates_passed"])
        self.assertIn(gate, {failure["gate"] for failure in result["blocking_gates"]})
        self.assertFalse(result["candidate_ready_for_demo"])

    def test_first_turn_gain_does_not_claim_context_or_demo_readiness(self):
        result = cycle.score_comparison(score_records())
        self.assertTrue(result["first_turn_gates_passed"])
        self.assertEqual(result["new_correct_accepted_validation_savings_ids"], ["D5-LV-01"])
        self.assertFalse(result["candidate_ready_for_demo"])
        self.assertIn("contextual", result["remaining_gate"])

    def test_no_new_accepted_savings_fails(self):
        rows = score_records()
        rows[0]["candidate"] = deepcopy(rows[0]["baseline"])
        self.assert_gate(rows, "at_least_one_new_accepted_unseen_savings")

    def test_training_fit_cannot_supply_unseen_gain(self):
        rows = score_records()
        rows[0]["split"] = "training_fit"
        self.assert_gate(rows, "at_least_one_new_accepted_unseen_savings")

    def test_all_four_new_clear_raw_options_are_required(self):
        rows = score_records()
        rows[3]["candidate"]["raw"]["option"]["argmax"] = "D5_SALARY"
        self.assert_gate(rows, "all_four_new_clear_raw_options")
        self.assert_gate(rows, "no_new_raw_error_preserve_previous_success")

    def test_clear_validation_cannot_keep_wrong_confident_customer_bucket(self):
        rows = score_records()
        for variant in ("baseline", "candidate"):
            rows[2][variant].update(route="ml", action="clarify", ordinary_bucket="Undecided",
                result_bucket="Undecided", ml_uncertain=False, escalation_required=False)
            rows[2][variant]["raw"]["intent"]["argmax"] = "undecided"
        self.assertEqual(rows[2]["baseline"], rows[2]["candidate"])
        self.assertEqual(rows[2]["candidate"]["raw"]["option"]["argmax"], "D5_SALARY")
        self.assertEqual(rows[0]["candidate"]["accepted_candidate"], "D5_WITHDRAWALS")
        self.assert_gate(rows, "clear_validation_no_wrong_confident_dialogue")

    def test_previous_correct_accepted_answer_cannot_be_lost(self):
        rows = score_records()
        rows[2]["baseline"] = observed(option="D5_SALARY", accepted=True)
        self.assert_gate(rows, "preserve_accepted_financial_success")

    def test_wrong_accepted_answer_and_receipt_absence_fail(self):
        rows = score_records()
        rows[2]["candidate"] = observed(option="D5_MULTIPLE", accepted=True)
        self.assert_gate(rows, "no_wrong_accepted_financial_answer")
        rows[0]["candidate"]["ml_receipt_issued"] = False
        self.assert_gate(rows, "real_ml_receipt_required")

    def test_new_wrong_commitment_is_not_hidden_by_veto_or_old_wrong_argmax(self):
        rows = score_records()
        # An opened regression already had a wrong option argmax. Its previous
        # set abstained; the new singleton is now an unsafe commitment even if
        # the unchanged business veto rejects it downstream.
        record = deepcopy(rows[3])
        record.update(id="D5-STD-02", split="existing_regression")
        record["baseline"]["raw"]["option"]["argmax"] = "D5_SALARY"
        record["candidate"]["raw"]["option"]["argmax"] = "D5_SALARY"
        record["candidate"].update(resolver_candidate="D5_SALARY", ordinary_bucket="Clarity", ml_uncertain=False)
        rows.append(record)
        self.assertIsNone(record["candidate"]["accepted_candidate"])
        self.assert_gate(rows, "no_new_wrong_raw_financial_commitment")

    def test_correct_confident_dialogue_must_be_preserved(self):
        rows = score_records()
        rows[6]["baseline"].update(route="ml", ordinary_bucket="Undecided", ml_uncertain=False,
            escalation_required=False)
        self.assert_gate(rows, "preserve_correct_confident_dialogue")

    def test_proposal_does_not_confirm_or_save(self):
        for key, value in (("selected", "D5_WITHDRAWALS"), ("confirmed_version", 1), ("saved_version", 1)):
            with self.subTest(key=key):
                rows = score_records()
                rows[0]["candidate"][key] = value
                self.assert_gate(rows, "proposal_must_not_confirm_or_save")

    def test_raw_option_is_not_scored_for_nonclear_or_incomplete(self):
        rows = score_records()
        for row in rows[4:8]:
            if row["candidate"]["raw"]:
                row["candidate"]["raw"]["option"]["argmax"] = "D5_NO_REGULAR"
        self.assertTrue(cycle.score_comparison(rows)["first_turn_gates_passed"])

    def test_incomplete_raw_intent_has_no_forced_gold(self):
        rows = score_records()
        for row in rows[4:6]:
            row["candidate"]["raw"]["intent"]["argmax"] = "undecided"
        self.assertTrue(cycle.score_comparison(rows)["first_turn_gates_passed"])

    def test_incomplete_confident_customer_bucket_is_unsafe(self):
        rows = score_records()
        rows[4]["candidate"].update(ordinary_bucket="Undecided", ml_uncertain=False)
        self.assert_gate(rows, "incomplete_no_invented_customer_bucket")

    def test_veto_cannot_hide_unsafe_incomplete_resolver_commitment(self):
        rows = score_records()
        rows[5]["candidate"].update(resolver_candidate="D5_MULTIPLE", ordinary_bucket="Clarity", ml_uncertain=False)
        self.assertIsNone(rows[5]["candidate"]["accepted_candidate"])
        self.assert_gate(rows, "incomplete_no_confident_financial_commitment")

    def test_wrong_nonclear_confident_bucket_is_unsafe(self):
        rows = score_records()
        rows[6]["candidate"].update(ordinary_bucket="Confusion", ml_uncertain=False)
        self.assert_gate(rows, "nonclear_confident_bucket_must_match")

    def test_new_raw_false_clarity_fails_separately_from_acceptance(self):
        rows = score_records()
        rows[6]["candidate"]["raw"]["intent"]["argmax"] = "clarity"
        self.assertIsNone(rows[6]["candidate"]["accepted_candidate"])
        self.assert_gate(rows, "no_new_raw_false_clarity")

    def test_help_requires_zero_diagnostic_and_route_calls(self):
        rows = score_records()
        rows[-1]["candidate"]["diagnostic_predictor_calls"] = 1
        self.assert_gate(rows, "existing_help_zero_models")

    def test_gpt_execution_would_fail_offline_gate(self):
        rows = score_records()
        rows[0]["candidate"]["actual_gpt_calls"] = 1
        self.assert_gate(rows, "offline_no_gpt_calls")


if __name__ == "__main__":
    unittest.main()
