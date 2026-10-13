"""Reviewed D5 wording repair: reuse frozen v2 intent; fit one option model.

Import and --help use only standard-library/v1/v2 offline utilities. Approval
must bind the exact 64-row proposal and displayed review before a cycle exists.
No existing data, candidate, runtime or default is overwritten by this tool.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import sys

import learning_cycle as v1
import learning_cycle_v2 as v2

HERE, ROOT = v1.HERE, v1.ROOT
DEFAULT_DATA = ROOT / "docs/d5-learning-cycle-v3"
V2_DATA = ROOT / "docs/d5-learning-cycle-v2"
V2_EVIDENCE = V2_DATA / "evidence"
VERSION = "d5-option-wording-learning-v3"
INTENT_SHA256 = "24086a0f0efe05eb3a69f6ef852c4714cd5e8f954584fa7c210f3cc643402831"
ARTIFACTS = dict(v2.ARTIFACTS)
DESIGNATED = frozenset({"D5-V2-LV-01", "D5-V2-LV-02"})
BANKS = {"opened_validation": "opened_validation_v1", "existing_regression": "existing_regression",
         "validation": "opened_validation_v2"}


def validate_review(review, proposal_path, row_ids):
    if (review.get("schema_version") != "d5-learning-review-v3"
            or review.get("review_type") != "human_business_review" or review.get("status") != "approved"):
        raise v1.CycleError("explicit_v3_human_business_approval_required")
    if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
        raise v1.CycleError("named_human_reviewer_required")
    try:
        stamp = datetime.fromisoformat(review.get("reviewed_at", "").replace("Z", "+00:00"))
        if stamp.utcoffset() is None:
            raise ValueError
    except (AttributeError, TypeError, ValueError):
        raise v1.CycleError("timezone_aware_review_timestamp_required") from None
    approved = review.get("approved_case_ids")
    if (not isinstance(approved, list) or any(not isinstance(value, str) for value in approved)
            or len(approved) != 64 or len(set(approved)) != 64 or set(approved) != set(row_ids)):
        raise v1.CycleError("all_sixty_four_case_ids_need_explicit_review")
    request = v1.read_json(DEFAULT_DATA / "review-request.json")
    if (review.get("dataset_sha256") != {"training": v1.file_hash(proposal_path)}
            or request.get("training_sha256") != v1.file_hash(proposal_path)
            or request.get("training_file") != v1.relative_file(proposal_path)
            or request.get("row_ids") != row_ids):
        raise v1.CycleError("reviewed_proposal_hash_or_ids_mismatch")
    document_hash = v1.file_hash(DEFAULT_DATA / "SAMPLE_REVIEW.md")
    if (review.get("review_document_sha256") != document_hash
            or request.get("review_sha256") != document_hash
            or request.get("review_file") != v1.relative_file(DEFAULT_DATA / "SAMPLE_REVIEW.md")):
        raise v1.CycleError("displayed_business_review_hash_mismatch")
    if review.get("provenance_acknowledgement") != "agent_authored_human_reviewed":
        raise v1.CycleError("truthful_review_provenance_required")


def validate_proposal(proposal, original_rows):
    rows = proposal.get("rows")
    if (not isinstance(rows, list) or len(rows) != 64 or any(not isinstance(row, dict) for row in rows)
            or [row.get("id") for row in rows] != [row["id"] for row in original_rows]
            or len({row.get("id") for row in rows}) != 64):
        raise v1.CycleError("exact_original_64_training_id_order_required")
    for row, original in zip(rows, original_rows):
        if any(row.get(key) != original.get(key) for key in
               ("question_id", "split", "bucket", "option_id", "source", "group_id")):
            raise v1.CycleError("original_training_labels_or_provenance_changed")
        if (row.get("bucket") != "clarity" or row.get("original_text") != original["text"]
                or row.get("original_source_path") != original["original_source_path"]
                or not isinstance(row.get("text"), str) or not row["text"].strip()
                or not isinstance(row.get("business_meaning"), str) or not row["business_meaning"].strip()
                or type(row.get("changed")) is not bool or row["changed"] != (row["text"] != original["text"])):
            raise v1.CycleError("invalid_before_after_training_contract")
    if Counter(row["option_id"] for row in rows) != Counter(row["option_id"] for row in original_rows):
        raise v1.CycleError("unchanged_option_class_counts_required")
    if len({v1.normalise(row["text"]) for row in rows}) != 64:
        raise v1.CycleError("duplicate_normalised_training_reply")
    return rows


def previous_v2_reference(cases):
    protocol = v1.read_json(V2_EVIDENCE / "protocol.json")
    built = v1.read_json(V2_EVIDENCE / "build.json")
    comparison = v1.read_json(V2_EVIDENCE / "compare.json")
    protocol_hash = v1.file_hash(V2_EVIDENCE / "protocol.json")
    if (protocol.get("version") != v2.VERSION
            or v1.read_json(V2_EVIDENCE / "freeze.json")["protocol_sha256"] != protocol_hash
            or comparison.get("protocol_sha256") != protocol_hash
            or comparison.get("candidate_identity_sha256") != built["candidate_identity_sha256"]
            or comparison.get("status") != "comparison_complete" or comparison.get("actual_gpt_calls") != 0
            or v1.file_hash(V2_EVIDENCE / ARTIFACTS["intent"]) != INTENT_SHA256
            or built["identity"]["artifacts"]["intent"] != INTENT_SHA256):
        raise v1.CycleError("frozen_v2_reference_or_intent_identity_mismatch")
    v2.verify_artifacts(V2_EVIDENCE, built, built["identity"]["baseline_identity"], built["identity"]["baseline_source_hash"])
    v1.verify_frozen_files(protocol["files"])
    old = comparison["cases"]
    if len(old) != 27 or {row["id"] for row in old} != {row["id"] for row in cases}:
        raise v1.CycleError("exact_previous_27_cases_required")
    previous = {row["id"]: row for row in old}
    for case in cases:
        recorded = previous[case["id"]]
        if (recorded["text"] != case["text"] or recorded["expected"] != v2.expected(case)
                or recorded["split"] != case["split"]):
            raise v1.CycleError("previous_case_text_gold_or_bank_changed")
    return protocol, built, previous


def load_inputs(proposal_path, review_path):
    if not Path(review_path).is_file():
        raise v1.CycleError("explicit_v3_human_business_approval_required")
    proposal = v1.read_json(proposal_path)
    rows = proposal.get("rows")
    if not isinstance(rows, list) or len(rows) != 64 or any(not isinstance(row, dict) for row in rows):
        raise v1.CycleError("exactly_sixty_four_review_rows_required")
    # Approval is checked before inherited-reference work, directory creation,
    # ML imports, startup fitting, model deserialisation or predictions.
    validate_review(v1.read_json(review_path), proposal_path, [row.get("id") for row in rows])
    old = v2.load_inputs(V2_DATA / "training-additions.json", V2_DATA / "validation-draft.json", V2_DATA / "human-review.json")
    originals = []
    for row in old["recipe"]["option"][0]:
        source = ("data/nlp/all_questions/train.csv" if row["id"].startswith("SYNTH-")
                  else "docs/d5-learning-cycle-v2/training-additions.json" if row["id"].startswith("D5-V2-")
                  else "docs/d5-learning-cycle-v1/training-draft.json")
        originals.append(dict(row, original_source_path=source))
    training = validate_proposal(proposal, originals)
    request = v1.read_json(DEFAULT_DATA / "review-request.json")
    changed = [row["id"] for row in training if row["changed"]]
    if request.get("changed_ids") != changed or request.get("unchanged_rows") != 64 - len(changed):
        raise v1.CycleError("reviewed_change_list_mismatch")
    calibration = old["recipe"]["option"][1]
    if len(calibration) != 40 or any(row["bucket"] != "clarity" for row in calibration):
        raise v1.CycleError("unchanged_forty_option_calibration_rows_required")
    excluded_texts = {v1.normalise(row["text"]) for row in old["recipe"]["intent"][1] + old["cases"]}
    if {v1.normalise(row["text"]) for row in training} & excluded_texts:
        raise v1.CycleError("training_overlaps_calibration_or_opened_evaluation")
    inherited_protocol, inherited_build, previous = previous_v2_reference(old["cases"])
    return {"training": training, "calibration": calibration,
        "cases": [dict(case, split=BANKS[case["split"]]) for case in old["cases"]],
        "previous_v1": old["previous"], "previous_v2": previous,
        "inherited_protocol": inherited_protocol, "inherited_build": inherited_build}


def freeze(proposal, review, output):
    inputs = load_inputs(proposal, review)
    files = dict(inputs["inherited_protocol"]["files"])
    extra = [Path(__file__), HERE / "test_learning_cycle_v3.py", Path(proposal), Path(review),
        DEFAULT_DATA / "review-request.json", DEFAULT_DATA / "SAMPLE_REVIEW.md",
        DEFAULT_DATA / "draft-quality-review.json", DEFAULT_DATA / "static-review.json"]
    extra += [V2_EVIDENCE / name for name in ("protocol.json", "freeze.json", "build.json", "compare.json", *ARTIFACTS.values())]
    files.update({v1.relative_file(path): v1.file_hash(path) for path in extra})
    v1.verify_frozen_files(files)
    cycle = v1.external_cycle(output)
    if cycle.exists():
        raise v1.CycleError("cycle_directory_already_exists")
    protocol = {"version": VERSION, "created_at": v1.utc_now(), "files": files,
        "proposal": v1.relative_file(proposal), "review": v1.relative_file(review),
        "environment": v1.environment_identity(), "intent_reused_sha256": INTENT_SHA256,
        "recipe": {"option_train": 64, "option_calibration": 40, "alpha": 0.10,
            "candidate_fits": {"intent": 0, "option": 1}, "candidate_calibrations": {"intent": 0, "option": 1}},
        "evaluation": {"opened_validation_v1": 8, "existing_regression": 11, "opened_validation_v2": 8},
        "designated_savings_ids": sorted(DESIGNATED), "automatic_retry": False,
        "runtime_integration": False, "default_changed": False, "actual_gpt_calls_allowed": 0,
        "scored_clear_rows_in_opened_banks": 8, "minimum_new_designated_acceptances": 1,
        "maximum_new_raw_errors": 0, "maximum_wrong_accepted_answers": 0,
        "preservation": "union of baseline and frozen v1/v2 correct results by case ID"}
    cycle.mkdir(parents=True, exist_ok=False, mode=0o700)
    v1.write_once(cycle / "protocol.json", protocol)
    v1.write_once(cycle / "freeze.json", {"protocol_sha256": v1.file_hash(cycle / "protocol.json"),
        "created_at": v1.utc_now(), "status": "frozen_after_human_review"})
    return {"status": "frozen", "cycle": str(cycle), "candidate_fits": 0, "actual_gpt_calls": 0}


def verify_cycle(cycle):
    cycle = v1.external_cycle(cycle)
    protocol = v1.read_json(cycle / "protocol.json")
    if (protocol.get("version") != VERSION or protocol.get("intent_reused_sha256") != INTENT_SHA256
            or v1.file_hash(cycle / "protocol.json") != v1.read_json(cycle / "freeze.json")["protocol_sha256"]):
        raise v1.CycleError("protocol_identity_mismatch")
    v1.verify_frozen_files(protocol["files"])
    if protocol["environment"] != v1.environment_identity():
        raise v1.CycleError("frozen_runtime_environment_changed")
    return cycle, protocol, load_inputs(ROOT / protocol["proposal"], ROOT / protocol["review"])


def build(cycle):
    cycle, protocol, inputs = verify_cycle(cycle)
    v1.begin_phase(cycle, "build")
    try:
        with v1.offline_only():
            import joblib
            spec, baseline, baseline_identity = v1.runtime_baseline()
            from baseline_ml import _fit_predictor
            # Entire v2 object is copied, including vocabulary/calibration. It
            # is neither deserialised nor fitted/recalibrated during this build.
            intent_bytes = (V2_EVIDENCE / ARTIFACTS["intent"]).read_bytes()
            if hashlib.sha256(intent_bytes).hexdigest() != INTENT_SHA256:
                raise v1.CycleError("frozen_intent_bytes_changed")
            descriptor = os.open(cycle / ARTIFACTS["intent"], os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(intent_bytes)
            option, _support = _fit_predictor(inputs["training"], inputs["calibration"], "option_id")
            v2.check_predictor(option, baseline.predictors["D5"].options)
            descriptor = os.open(cycle / ARTIFACTS["option"], os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as handle:
                joblib.dump(option, handle, compress=3)
            identity = {"protocol_sha256": v1.file_hash(cycle / "protocol.json"),
                "artifacts": {axis: v1.file_hash(cycle / name) for axis, name in ARTIFACTS.items()},
                "baseline_identity": baseline_identity, "baseline_source_hash": baseline.source_hash,
                "proposal_sha256": protocol["files"][protocol["proposal"]],
                "calibration_sha256": protocol["files"]["data/nlp/all_questions/calibration.csv"],
                "inherited_v2_candidate_identity": inputs["inherited_build"]["candidate_identity_sha256"]}
            result = {"status": "built_not_promoted", "completed_at": v1.utc_now(), "identity": identity,
                "candidate_identity_sha256": v1.digest(identity), "candidate_fit_counts": {"intent": 0, "option": 1},
                "candidate_calibration_counts": {"intent": 0, "option": 1},
                "option_training_rows": 64, "option_calibration_rows": 40,
                "intent_reused_sha256": INTENT_SHA256, "alpha": 0.10,
                "thresholds": {"intent": inputs["inherited_build"]["thresholds"]["intent"], "option": option.threshold},
                "baseline_startup": "unchanged original routine reconstructs 15 intent and 15 option predictors",
                "other_fourteen_retained": True, "all_questions": list(spec.question_order),
                "actual_gpt_calls": 0, "default_changed": False, "candidate_ready_for_demo": False}
            verify_artifacts(cycle, result, baseline_identity, baseline.source_hash)
            v1.verify_frozen_files(protocol["files"])
            v1.write_once(cycle / "build.json", result)
            return result
    except BaseException as exc:
        v1.failure_receipt(cycle, "build", exc)
        raise


def verify_artifacts(cycle, built, baseline_identity, baseline_source_hash):
    identity = built["identity"]
    if (identity["protocol_sha256"] != v1.file_hash(cycle / "protocol.json")
            or identity.get("artifacts") != {axis: v1.file_hash(cycle / name) for axis, name in ARTIFACTS.items()}
            or identity["artifacts"]["intent"] != INTENT_SHA256
            or built.get("intent_reused_sha256") != INTENT_SHA256
            or identity["baseline_identity"] != baseline_identity or identity["baseline_source_hash"] != baseline_source_hash
            or built.get("candidate_identity_sha256") != v1.digest(identity)
            or built.get("candidate_fit_counts") != {"intent": 0, "option": 1}
            or built.get("candidate_calibration_counts") != {"intent": 0, "option": 1}):
        raise v1.CycleError("candidate_two_artifact_or_intent_reuse_identity_mismatch")


def candidate_resolver(cycle, baseline, baseline_identity):
    import joblib
    from baseline_ml import AllQuestionMLResolver, QuestionPredictors, lexical_support
    built = v1.read_json(cycle / "build.json")
    verify_artifacts(cycle, built, baseline_identity, baseline.source_hash)
    # Load only trusted, hash-verified outputs after approval and frozen checks.
    intent, option = (joblib.load(cycle / ARTIFACTS[axis]) for axis in ("intent", "option"))
    v2.check_predictor(intent, baseline.predictors["D5"].intent)
    v2.check_predictor(option, baseline.predictors["D5"].options)
    if intent.threshold != built["thresholds"]["intent"]:
        raise v1.CycleError("reused_intent_threshold_mismatch")
    pairs = dict(baseline.predictors)
    pairs["D5"] = QuestionPredictors(intent, option, lambda text: lexical_support(intent.classifier, text),
        lambda text: lexical_support(option.classifier, text))
    resolver = AllQuestionMLResolver(pairs, baseline.allowed_options, source_hash=built["candidate_identity_sha256"])
    if any(resolver.predictors[qid] is not baseline.predictors[qid] for qid in pairs if qid != "D5"):
        raise v1.CycleError("other_fourteen_predictor_identity_not_preserved")
    return resolver, built["candidate_identity_sha256"]


def score_comparison(rows):
    # The reused scorer's internal names refer to its historical split. Output
    # below explicitly labels both eight-case banks as opened, never fresh.
    inverse_banks = {value: key for key, value in BANKS.items()}
    scored = [dict(row, split=inverse_banks[row["split"]]) for row in rows]
    result = v2.score_comparison(scored)
    failures = [item for item in result["blocking_gates"]
        if item["gate"] != "at_least_one_fresh_savings_escalation_becomes_ml_acceptance"]
    preservation = result["preservation_by_case_and_axis"]
    previous = [dict(row, baseline=row["previous_v2_candidate"]) for row in scored if row.get("previous_v2_candidate") is not None]
    union = v1.score_comparison(previous)
    failures += [dict(item, compared_with="frozen_previous_v2_candidate") for item in union["blocking_gates"]
        if item["gate"] != "at_least_one_new_accepted_unseen_savings"]
    preservation += [dict(item, compared_with="frozen_previous_v2_candidate") for item in union["preservation_by_case_and_axis"]]
    if len(previous) != 27:
        failures.append({"gate": "complete_frozen_v2_reference_required", "case_id": None})
    gained = [row["id"] for row in rows if row["id"] in DESIGNATED
        and row["expected"]["kind"] == "clear" and row["expected"]["option_id"] == "D5_WITHDRAWALS"
        and row["baseline"].get("escalation_required") and row["baseline"].get("route") == "ml_then_gpt"
        and row["candidate"].get("accepted_candidate") == "D5_WITHDRAWALS"
        and row["candidate"].get("ml_receipt_issued") and row["candidate"].get("route") == "ml"]
    if not gained:
        failures.append({"gate": "designated_opened_savings_escalation_becomes_ml_acceptance", "case_id": None})
    rename = {"all_eight_opened_and_fresh_clear_raw_options": "all_eight_opened_clear_raw_options",
        "all_four_new_clear_raw_options": "all_four_second_opened_clear_raw_options"}
    failures = [dict(item, gate=rename.get(item["gate"], item["gate"])) for item in failures]
    return {"first_turn_gates_passed": not failures, "blocking_gates": failures,
        "new_correct_accepted_designated_savings_ids": sorted(gained),
        "preservation_by_case_and_axis": preservation, "candidate_ready_for_demo": False,
        "remaining_gate": "candidate-specific original four contextual turns and controls; no v3 demo profile yet"}


def metrics(rows, variant):
    return {split: v1.metrics([dict(row, split="validation") for row in rows if row["split"] == split], variant)["validation"]
        for split in BANKS.values()}


def compare(cycle):
    cycle, protocol, inputs = verify_cycle(cycle)
    if not (cycle / "build.json").is_file() or (cycle / "build.STOP.json").exists():
        raise v1.CycleError("completed_single_build_required")
    v1.begin_phase(cycle, "compare")
    try:
        with v1.offline_only():
            spec, baseline, baseline_identity = v1.runtime_baseline()
            candidate, identity = candidate_resolver(cycle, baseline, baseline_identity)
            rows = []
            for case in inputs["cases"]:
                previous = inputs["previous_v2"][case["id"]]
                current_baseline = v1.inspect_case(spec, baseline, baseline_identity, case)
                if v2.semantic_fields(current_baseline) != v2.semantic_fields(previous["baseline"]):
                    v1.write_once(cycle / "baseline-mismatch.json", {"case_id": case["id"], "current": current_baseline,
                        "previous": previous["baseline"], "retry": False})
                    raise v1.CycleError("unchanged_baseline_semantic_parity_failed")
                old_v1 = inputs["previous_v1"].get(case["id"])
                rows.append({"id": case["id"], "split": case["split"], "text": case["text"],
                    "expected": v2.expected(case), "baseline": current_baseline,
                    "candidate": v1.inspect_case(spec, candidate, identity, case),
                    "previous_v1_candidate": old_v1["candidate"] if old_v1 else None,
                    "previous_v2_candidate": previous["candidate"]})
            result = {"status": "comparison_complete", "completed_at": v1.utc_now(),
                "candidate_identity_sha256": identity, "protocol_sha256": v1.file_hash(cycle / "protocol.json"),
                **score_comparison(rows), "baseline": metrics(rows, "baseline"), "candidate": metrics(rows, "candidate"),
                "cases": rows, "previous_baseline_semantic_parity": {"matched": 27, "required": 27},
                "actual_gpt_calls": 0, "candidate_fits_during_compare": 0, "previous_candidates_rerun": False,
                "intent_reused_sha256": INTENT_SHA256, "default_changed": False,
                "limitations": ["All 27 replies are opened, outside-training comparison material, not fresh independent evaluation.",
                    "The retained intent predictor has known raw errors; no new errors does not mean zero existing errors.",
                    "Escalation stops before GPT execution and is not interpretation success.",
                    "Raw interpretation, business veto and accepted candidates are separate; controls are not ML success."]}
            v1.verify_frozen_files(protocol["files"])
            v1.write_once(cycle / "compare.json", result)
            return {key: result[key] for key in ("status", "first_turn_gates_passed", "blocking_gates",
                "candidate_ready_for_demo", "remaining_gate", "actual_gpt_calls")}
    except BaseException as exc:
        v1.failure_receipt(cycle, "compare", exc)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("freeze")
    command.add_argument("--proposal", type=Path, default=DEFAULT_DATA / "training-review-draft.json")
    command.add_argument("--review", type=Path, default=DEFAULT_DATA / "human-review.json")
    command.add_argument("--output", type=Path, required=True)
    for name in ("build", "compare"):
        commands.add_parser(name).add_argument("--cycle", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = (freeze(args.proposal, args.review, args.output) if args.command == "freeze"
                  else build(args.cycle) if args.command == "build" else compare(args.cycle))
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0 if result.get("first_turn_gates_passed", True) else 2
    except (Exception, KeyboardInterrupt) as exc:
        print(json.dumps({"status": "stopped", "failure_code": str(exc) if isinstance(exc, v1.CycleError)
            else "local_runtime_failure", "error_type": type(exc).__name__, "retry": False}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
