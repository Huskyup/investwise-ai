"""Pure v3 integrity/scoring fixtures; no fitting, deserialisation or inference.

Every test blocks model imports, network and subprocesses. Existing case-record
fixtures are mutated only to exercise software gates, not to add language cases.
"""
import builtins
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

_original_import = builtins.__import__


def safe_import(name, *args, **kwargs):
    if name.split(".")[0] in {"ai", "baseline_ml", "sklearn", "numpy", "joblib", "jwt", "requests", "httpx"}:
        raise AssertionError("Model, deserialisation and service imports are forbidden in pure fixtures")
    return _original_import(name, *args, **kwargs)


with patch("builtins.__import__", side_effect=safe_import):
    import learning_cycle_v3 as cycle
    from test_learning_cycle import observed
    from test_learning_cycle_v2 import fixture_rows as v2_fixture_rows, by_id


def records():
    rows = v2_fixture_rows()
    for row in rows:
        row["split"] = cycle.BANKS[row["split"]]
        row["previous_v2_candidate"] = deepcopy(row["baseline"])
    return rows


def proposal_fixture():
    proposal = cycle.v1.read_json(cycle.DEFAULT_DATA / "training-review-draft.json")
    original = [dict(row, text=row["original_text"]) for row in proposal["rows"]]
    return proposal, original


def review_fixture():
    ids = [f"record-{n:02d}" for n in range(64)]
    review = {"schema_version": "d5-learning-review-v3", "review_type": "human_business_review",
        "status": "approved", "reviewer": "Fixture business reviewer", "reviewed_at": "2026-10-13T20:00:00+01:00",
        "dataset_sha256": {"training": "proposal-hash"}, "review_document_sha256": "display-hash",
        "approved_case_ids": ids, "provenance_acknowledgement": "agent_authored_human_reviewed"}
    request = {"training_sha256": "proposal-hash", "training_file": "proposal.json", "row_ids": ids,
        "review_sha256": "display-hash", "review_file": "SAMPLE_REVIEW.md"}
    return review, request, ids


class OfflineOnlyTests(unittest.TestCase):
    def setUp(self):
        self.import_guard = patch("builtins.__import__", side_effect=safe_import)
        self.import_guard.start()
        self.addCleanup(self.import_guard.stop)
        self.network_guard = cycle.v1.offline_only()
        self.network_guard.__enter__()
        self.addCleanup(self.network_guard.__exit__, None, None, None)


class ReviewAndIdentityTests(OfflineOnlyTests):
    def test_fixture_boundary_prohibits_model_imports_and_network(self):
        with self.assertRaises(AssertionError):
            __import__("joblib")
        with self.assertRaises(cycle.v1.CycleError):
            cycle.v1.socket.create_connection(("unused.invalid", 443))

    def test_pending_review_cannot_reach_file_hash_or_model_work(self):
        review, _request, ids = review_fixture()
        review["status"] = "pending_human_business_review"
        with patch.object(cycle.v1, "file_hash", side_effect=AssertionError("must not reach hashing")):
            with self.assertRaisesRegex(cycle.v1.CycleError, "explicit_v3_human_business_approval_required"):
                cycle.validate_review(review, Path("proposal.json"), ids)

    def test_missing_review_is_explicit_approval_block_before_proposal_reads(self):
        with tempfile.TemporaryDirectory(prefix="d5-v3-software-") as directory, \
             patch.object(cycle.v1, "read_json", side_effect=AssertionError("must not read proposal or references")):
            with self.assertRaisesRegex(cycle.v1.CycleError, "explicit_v3_human_business_approval_required"):
                cycle.load_inputs(Path(directory) / "unused-proposal.json", Path(directory) / "missing-review.json")

    def test_approval_requires_all_ids_exact_proposal_and_display(self):
        review, request, ids = review_fixture()
        def hashed(path):
            return "proposal-hash" if Path(path).name == "proposal.json" else "display-hash"
        with patch.object(cycle.v1, "read_json", return_value=request), \
             patch.object(cycle.v1, "file_hash", side_effect=hashed), \
             patch.object(cycle.v1, "relative_file", side_effect=lambda path: Path(path).name):
            cycle.validate_review(review, Path("proposal.json"), ids)
            with self.assertRaisesRegex(cycle.v1.CycleError, "all_sixty_four_case_ids_need_explicit_review"):
                cycle.validate_review(dict(review, approved_case_ids=ids[:-1]), Path("proposal.json"), ids)
            with self.assertRaisesRegex(cycle.v1.CycleError, "reviewed_proposal_hash_or_ids_mismatch"):
                cycle.validate_review(dict(review, dataset_sha256={"training": "different"}), Path("proposal.json"), ids)
            with self.assertRaisesRegex(cycle.v1.CycleError, "displayed_business_review_hash_mismatch"):
                cycle.validate_review(dict(review, review_document_sha256="different"), Path("proposal.json"), ids)

    def test_prior_approval_does_not_approve_revised_wording(self):
        review, _request, ids = review_fixture()
        with self.assertRaisesRegex(cycle.v1.CycleError, "explicit_v3_human_business_approval_required"):
            cycle.validate_review(dict(review, schema_version="d5-learning-review-v2"), Path("unused"), ids)

    def test_review_failure_precedes_directory_and_phase_creation(self):
        with tempfile.TemporaryDirectory(prefix="d5-v3-software-") as directory:
            target = Path(directory) / "never-created"
            with patch.object(cycle, "load_inputs", side_effect=cycle.v1.CycleError("explicit_v3_human_business_approval_required")):
                with self.assertRaises(cycle.v1.CycleError):
                    cycle.freeze(Path("unused"), Path("unused"), target)
            self.assertFalse(target.exists())
        with patch.object(cycle, "verify_cycle", side_effect=cycle.v1.CycleError("explicit_v3_human_business_approval_required")), \
             patch.object(cycle.v1, "begin_phase", side_effect=AssertionError("must not start")):
            with self.assertRaises(cycle.v1.CycleError):
                cycle.build(Path("unused"))
            with self.assertRaises(cycle.v1.CycleError):
                cycle.compare(Path("unused"))

    def test_proposal_retains_exact_64_ids_labels_sources_and_before_text(self):
        proposal, original = proposal_fixture()
        self.assertEqual(len(cycle.validate_proposal(proposal, original)), 64)
        for key, replacement in (("option_id", "D5_MULTIPLE"), ("source", "changed-source"),
                ("original_text", "changed-before-text"), ("id", "unknown-record")):
            with self.subTest(key=key):
                changed = deepcopy(proposal)
                changed["rows"][0][key] = replacement
                with self.assertRaises(cycle.v1.CycleError):
                    cycle.validate_proposal(changed, original)
        with self.assertRaises(cycle.v1.CycleError):
            cycle.validate_proposal(dict(proposal, rows=proposal["rows"][:-1]), original)

    def test_incorrect_changed_flag_and_duplicate_wording_rejected(self):
        proposal, original = proposal_fixture()
        changed = deepcopy(proposal)
        changed["rows"][0]["changed"] = not changed["rows"][0]["changed"]
        with self.assertRaisesRegex(cycle.v1.CycleError, "invalid_before_after_training_contract"):
            cycle.validate_proposal(changed, original)
        changed = deepcopy(proposal)
        changed["rows"][1]["text"] = changed["rows"][0]["text"]
        changed["rows"][1]["changed"] = changed["rows"][1]["text"] != changed["rows"][1]["original_text"]
        with self.assertRaisesRegex(cycle.v1.CycleError, "duplicate_normalised_training_reply"):
            cycle.validate_proposal(changed, original)

    def test_both_artifacts_and_zero_intent_fit_calibration_are_bound(self):
        hashes = {"protocol.json": "protocol", cycle.ARTIFACTS["intent"]: cycle.INTENT_SHA256,
                  cycle.ARTIFACTS["option"]: "option"}
        identity = {"protocol_sha256": "protocol", "artifacts": {"intent": cycle.INTENT_SHA256, "option": "option"},
            "baseline_identity": "baseline", "baseline_source_hash": "source"}
        built = {"identity": identity, "candidate_identity_sha256": cycle.v1.digest(identity),
            "intent_reused_sha256": cycle.INTENT_SHA256, "candidate_fit_counts": {"intent": 0, "option": 1},
            "candidate_calibration_counts": {"intent": 0, "option": 1}}
        with patch.object(cycle.v1, "file_hash", side_effect=lambda path: hashes[Path(path).name]):
            cycle.verify_artifacts(Path("unused"), built, "baseline", "source")
            for axis, name in cycle.ARTIFACTS.items():
                with self.subTest(axis=axis):
                    previous = hashes[name]
                    hashes[name] = "changed"
                    with self.assertRaises(cycle.v1.CycleError):
                        cycle.verify_artifacts(Path("unused"), built, "baseline", "source")
                    hashes[name] = previous
            for key in ("candidate_fit_counts", "candidate_calibration_counts"):
                changed = deepcopy(built)
                changed[key]["intent"] = 1
                with self.assertRaises(cycle.v1.CycleError):
                    cycle.verify_artifacts(Path("unused"), changed, "baseline", "source")

    def test_frozen_change_and_repeat_phase_are_blocked(self):
        with tempfile.TemporaryDirectory(prefix="d5-v3-software-") as directory:
            root = Path(directory)
            source = root / "fixture.txt"
            source.write_text("original")
            files = {"fixture.txt": cycle.v1.file_hash(source)}
            source.write_text("changed")
            with self.assertRaises(cycle.v1.CycleError):
                cycle.v1.verify_frozen_files(files, root)
            cycle.v1.begin_phase(root, "build")
            with self.assertRaisesRegex(cycle.v1.CycleError, "phase_already_attempted_no_retry"):
                cycle.v1.begin_phase(root, "build")


class ThreeReferenceScoringTests(OfflineOnlyTests):
    def assert_gate(self, rows, gate, reference=None):
        result = cycle.score_comparison(rows)
        self.assertFalse(result["first_turn_gates_passed"])
        self.assertTrue(any(item["gate"] == gate and (reference is None or item.get("compared_with") == reference)
                            for item in result["blocking_gates"]), result["blocking_gates"])
        self.assertFalse(result["candidate_ready_for_demo"])

    def test_first_turn_success_is_only_opened_evidence_and_not_demo_ready(self):
        result = cycle.score_comparison(records())
        self.assertTrue(result["first_turn_gates_passed"], result["blocking_gates"])
        self.assertEqual(result["new_correct_accepted_designated_savings_ids"], ["D5-V2-LV-01"])
        self.assertNotIn("fresh", str(result))
        self.assertNotIn("unseen", str(result))
        self.assertFalse(result["candidate_ready_for_demo"])

    def test_baseline_v1_and_v2_correct_raw_union_is_preserved(self):
        for reference in ("baseline", "previous_v1_candidate", "previous_v2_candidate"):
            with self.subTest(reference=reference):
                rows = records()
                row = by_id(rows, "D5-STD-06")
                for axis in ("baseline", "previous_v1_candidate", "previous_v2_candidate", "candidate"):
                    row[axis]["raw"]["option"]["argmax"] = "D5_PENSION_PAYMENTS"
                row[reference]["raw"]["option"]["argmax"] = "D5_WITHDRAWALS"
                label = {"baseline": "unchanged_baseline", "previous_v1_candidate": "frozen_previous_v1_candidate",
                    "previous_v2_candidate": "frozen_previous_v2_candidate"}[reference]
                self.assert_gate(rows, "no_new_raw_error_preserve_previous_success", label)

    def test_v2_accepted_and_correct_confident_dialogue_cannot_disappear(self):
        rows = records()
        by_id(rows, "D5-STD-06")["previous_v2_candidate"] = observed(accepted=True)
        self.assert_gate(rows, "preserve_accepted_financial_success", "frozen_previous_v2_candidate")
        rows = records()
        by_id(rows, "D5-STD-10")["previous_v2_candidate"].update(route="ml", ordinary_bucket="Undecided",
            ml_uncertain=False, escalation_required=False)
        self.assert_gate(rows, "preserve_correct_confident_dialogue", "frozen_previous_v2_candidate")

    def test_all_eight_opened_clear_sources_still_required(self):
        for identifier in ("D5-LV-04", "D5-V2-LV-04"):
            rows = records()
            by_id(rows, identifier)["candidate"]["raw"]["option"]["argmax"] = "D5_SALARY"
            self.assert_gate(rows, "all_eight_opened_clear_raw_options")

    def test_only_designated_savings_can_supply_gain(self):
        rows = records()
        designated = by_id(rows, "D5-V2-LV-01")
        designated["candidate"] = deepcopy(designated["baseline"])
        by_id(rows, "D5-LV-01")["candidate"] = observed(accepted=True)
        self.assert_gate(rows, "designated_opened_savings_escalation_becomes_ml_acceptance")

    def test_gain_requires_baseline_escalation_and_authentic_receipt(self):
        rows = records()
        by_id(rows, "D5-V2-LV-01")["baseline"]["escalation_required"] = False
        self.assert_gate(rows, "designated_opened_savings_escalation_becomes_ml_acceptance")
        rows = records()
        by_id(rows, "D5-V2-LV-01")["candidate"]["ml_receipt_issued"] = False
        self.assert_gate(rows, "real_ml_receipt_required")

    def test_known_raw_error_is_not_misreported_as_zero_existing_errors(self):
        rows = records()
        row = by_id(rows, "D5-LV-07")
        for reference in ("baseline", "previous_v1_candidate", "previous_v2_candidate", "candidate"):
            row[reference]["raw"]["intent"]["argmax"] = "clarity"
        self.assertTrue(cycle.score_comparison(rows)["first_turn_gates_passed"])
        row["previous_v2_candidate"]["raw"]["intent"]["argmax"] = "undecided"
        self.assert_gate(rows, "no_new_raw_false_clarity", "frozen_previous_v2_candidate")

    def test_no_invented_bucket_wrong_financial_answer_or_save(self):
        rows = records()
        by_id(rows, "D5-V2-LV-05")["candidate"].update(ordinary_bucket="Undecided", ml_uncertain=False)
        self.assert_gate(rows, "incomplete_no_invented_customer_bucket")
        rows = records()
        by_id(rows, "D5-V2-LV-03")["candidate"] = observed(option="D5_MULTIPLE", accepted=True)
        self.assert_gate(rows, "no_wrong_accepted_financial_answer")
        rows = records()
        by_id(rows, "D5-V2-LV-01")["candidate"]["saved_version"] = 1
        self.assert_gate(rows, "proposal_must_not_confirm_or_save")

    def test_controls_stay_zero_call_and_all_reference_rows_are_required(self):
        rows = records()
        by_id(rows, "D5-STD-11")["candidate"]["routing_ml_calls"] = 1
        self.assert_gate(rows, "existing_help_zero_models")
        rows = records()
        rows[0]["previous_v2_candidate"] = None
        self.assert_gate(rows, "complete_frozen_v2_reference_required")
        self.assert_gate(records()[:-1], "exact_27_cases_and_reference_denominators")


if __name__ == "__main__":
    unittest.main()
