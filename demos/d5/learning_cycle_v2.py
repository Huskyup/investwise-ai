"""Separate, reviewed D5 intent-and-option learning cycle; never a demo default.

Reuses v1's immutable offline routing and integrity utilities, not its fitted
candidate. The previous 19-case evidence supplies preservation requirements.
Only explicitly approved new labels permit a write-once freeze/build/compare.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
import os
from pathlib import Path
import sys

import learning_cycle as v1

HERE, ROOT = v1.HERE, v1.ROOT
DEFAULT_DATA = ROOT / "docs/d5-learning-cycle-v2"
OLD_DATA = ROOT / "docs/d5-learning-cycle-v1"
OLD_EVIDENCE = OLD_DATA / "evidence"
VERSION = "d5-intent-option-learning-v2"
ARTIFACTS = {"intent": "d5-intent-candidate.joblib", "option": "d5-option-candidate.joblib"}


def validate_review(review, training, validation, case_ids):
    if (review.get("schema_version") != "d5-learning-review-v2"
            or review.get("review_type") != "human_business_review" or review.get("status") != "approved"):
        raise v1.CycleError("explicit_v2_human_business_approval_required")
    if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
        raise v1.CycleError("named_human_reviewer_required")
    try:
        reviewed = datetime.fromisoformat(review.get("reviewed_at", "").replace("Z", "+00:00"))
        if reviewed.utcoffset() is None:
            raise ValueError
    except (AttributeError, TypeError, ValueError):
        raise v1.CycleError("timezone_aware_review_timestamp_required") from None
    if review.get("dataset_sha256") != {"training": v1.file_hash(training), "validation": v1.file_hash(validation)}:
        raise v1.CycleError("reviewed_dataset_hash_mismatch")
    approved = review.get("approved_case_ids")
    if (not isinstance(approved, list) or any(not isinstance(x, str) for x in approved)
            or len(approved) != 24 or len(set(approved)) != 24 or set(approved) != set(case_ids)):
        raise v1.CycleError("all_twenty_four_case_ids_need_explicit_review")
    if review.get("provenance_acknowledgement") != "agent_authored_human_reviewed":
        raise v1.CycleError("truthful_review_provenance_required")


def training_rows(path):
    rows = v1.read_json(path).get("rows")
    if not isinstance(rows, list) or len(rows) != 16:
        raise v1.CycleError("exactly_sixteen_new_training_rows_required")
    for row in rows:
        if not isinstance(row, dict) or row.get("question_id") != "D5" or row.get("split") != "train":
            raise v1.CycleError("d5_first_turn_training_required")
        if any(not isinstance(row.get(key), str) or not row[key].strip()
               for key in ("id", "text", "business_meaning", "expected_action", "source", "group_id")):
            raise v1.CycleError("missing_dataset_annotation")
        kind, bucket, option = row.get("kind"), row.get("bucket"), row.get("option_id")
        if not ((kind == "clear" and bucket == "clarity" and option in v1.OPTIONS)
                or (kind in {"undecided", "confusion"} and bucket == kind and option is None)):
            raise v1.CycleError("invalid_business_label_contract")
    if (Counter(row["kind"] for row in rows) != {"clear": 8, "undecided": 4, "confusion": 4}
            or Counter(row["option_id"] for row in rows if row["kind"] == "clear") != {
                "D5_WITHDRAWALS": 4, "D5_SALARY": 2, "D5_MULTIPLE": 2}
            or {row["id"] for row in rows} != {f"D5-V2-LT-{n:02d}" for n in range(1, 17)}):
        raise v1.CycleError("fixed_v2_training_composition_required")
    return rows


def expected(case):
    return {key: case.get(key) for key in ("kind", "bucket", "option_id", "control_required")}


def load_previous_reference(cases):
    """Read and bind frozen evidence; never deserialize or run the v1 model."""
    protocol = v1.read_json(OLD_EVIDENCE / "protocol.json")
    frozen = v1.read_json(OLD_EVIDENCE / "freeze.json")
    built = v1.read_json(OLD_EVIDENCE / "build.json")
    result = v1.read_json(OLD_EVIDENCE / "compare.json")
    protocol_hash = v1.file_hash(OLD_EVIDENCE / "protocol.json")
    identity = built["identity"]
    if (protocol.get("version") != v1.VERSION or frozen["protocol_sha256"] != protocol_hash
            or identity["protocol_sha256"] != protocol_hash or result["protocol_sha256"] != protocol_hash
            or built["candidate_identity_sha256"] != v1.digest(identity)
            or result["candidate_identity_sha256"] != built["candidate_identity_sha256"]
            or identity["artifact_sha256"] != v1.file_hash(OLD_EVIDENCE / "d5-option-candidate.joblib")
            or result.get("status") != "comparison_complete" or result.get("actual_gpt_calls") != 0):
        raise v1.CycleError("previous_v1_evidence_identity_mismatch")
    v1.verify_frozen_files(protocol["files"])
    previous = result["cases"]
    if len(previous) != 19 or {row["id"] for row in previous} != {row["id"] for row in cases}:
        raise v1.CycleError("previous_nineteen_case_identity_mismatch")
    by_id = {row["id"]: row for row in previous}
    for case in cases:
        recorded = by_id[case["id"]]
        if recorded["text"] != case["text"] or recorded["expected"] != expected(case):
            raise v1.CycleError("previous_case_text_or_gold_changed")
    return by_id


def recipe(original_train, original_calibration, old_training, additions):
    """Pure assembly. Original calibration is never augmented or relabelled."""
    if (len(original_train) != 56 or Counter(row["bucket"] for row in original_train) != {
            "clarity": 48, "undecided": 4, "confusion": 4}
            or len(original_calibration) != 60
            or Counter(row["bucket"] for row in original_calibration) != {
                "clarity": 40, "undecided": 10, "confusion": 10}
            or len(old_training) != 8 or len(additions) != 16):
        raise v1.CycleError("unchanged_original_d5_recipe_required")
    intent_train = original_train + old_training + additions
    option_train = [row for row in intent_train if row["bucket"] == "clarity"]
    option_calibration = [row for row in original_calibration if row["bucket"] == "clarity"]
    if len(intent_train) != 80 or len(option_train) != 64 or len(option_calibration) != 40:
        raise v1.CycleError("exact_80_intent_64_option_recipe_required")
    return {"intent": (intent_train, original_calibration, "bucket"),
            "option": (option_train, option_calibration, "option_id")}


def load_inputs(training, validation, review):
    additions = training_rows(training)
    fresh = v1.dataset_rows(validation, "validation")
    if {row["id"] for row in fresh} != {f"D5-V2-LV-{n:02d}" for n in range(1, 9)}:
        raise v1.CycleError("fixed_v2_validation_ids_required")
    validate_review(v1.read_json(review), training, validation, [row["id"] for row in additions + fresh])
    old_training, opened, _clear, _cal = v1.load_reviewed_inputs(
        OLD_DATA / "training-draft.json", OLD_DATA / "validation-draft.json", OLD_DATA / "human-review.json")
    manifest = v1.read_json(v1.BASELINE_MANIFEST)
    data = ROOT / manifest["data_directory"]
    original_train, original_calibration = v1.csv_d5(data / "train.csv"), v1.csv_d5(data / "calibration.csv")
    regression = v1.original_cases()
    known = original_train + original_calibration + old_training + opened + regression
    new = additions + fresh
    if (len({row["id"] for row in new}) != 24 or len({row["group_id"] for row in new}) != 24
            or len({v1.normalise(row["text"]) for row in new}) != 24):
        raise v1.CycleError("duplicate_v2_case_group_or_normalised_reply")
    for key in ("id", "group_id"):
        if {row[key] for row in new} & {row[key] for row in known if row.get(key)}:
            raise v1.CycleError("v2_cases_overlap_known_bank")
    if {v1.normalise(row["text"]) for row in new} & {v1.normalise(row["text"]) for row in known}:
        raise v1.CycleError("v2_cases_overlap_known_bank")
    assembled = recipe(original_train, original_calibration, old_training, additions)
    previous = load_previous_reference(opened + regression)
    opened = [dict(row, split="opened_validation") for row in opened]
    return {"recipe": assembled, "cases": opened + regression + fresh, "previous": previous}


def freeze(training, validation, review, output):
    load_inputs(training, validation, review)
    files = v1.freeze_files(training, validation, review)
    extra = [Path(__file__), HERE / "test_learning_cycle_v2.py", OLD_DATA / "training-draft.json",
        OLD_DATA / "validation-draft.json", OLD_DATA / "human-review.json"]
    extra += [OLD_EVIDENCE / name for name in ("protocol.json", "freeze.json", "build.json",
        "compare.json", "d5-option-candidate.joblib")]
    files.update({v1.relative_file(path): v1.file_hash(path) for path in extra})
    cycle = v1.external_cycle(output)
    if cycle.exists():
        raise v1.CycleError("cycle_directory_already_exists")
    protocol = {"version": VERSION, "created_at": v1.utc_now(), "files": files,
        "training": v1.relative_file(training), "validation": v1.relative_file(validation),
        "review": v1.relative_file(review), "environment": v1.environment_identity(),
        "recipe": {"intent_train": 80, "intent_calibration": 60, "option_train": 64,
            "option_calibration": 40, "alpha": 0.10, "candidate_fits": {"intent": 1, "option": 1}},
        "previous_compare": v1.relative_file(OLD_EVIDENCE / "compare.json"),
        "evaluation": {"opened_validation": 8, "existing_regression": 11, "validation": 8},
        "preservation": "union of unchanged baseline and frozen previous-v1-candidate correct results by case ID",
        "automatic_retry": False, "runtime_integration": False,
        "remaining_gate": "candidate-specific original four-context and control verification before any demo integration"}
    cycle.mkdir(parents=True, exist_ok=False, mode=0o700)
    v1.write_once(cycle / "protocol.json", protocol)
    v1.write_once(cycle / "freeze.json", {"protocol_sha256": v1.file_hash(cycle / "protocol.json"),
        "created_at": v1.utc_now(), "status": "frozen_after_human_review"})
    return {"status": "frozen", "cycle": str(cycle), "candidate_fits": 0, "actual_gpt_calls": 0}


def verify_cycle(cycle):
    cycle = v1.external_cycle(cycle)
    protocol = v1.read_json(cycle / "protocol.json")
    if (protocol.get("version") != VERSION or v1.file_hash(cycle / "protocol.json") !=
            v1.read_json(cycle / "freeze.json")["protocol_sha256"]):
        raise v1.CycleError("protocol_identity_mismatch")
    v1.verify_frozen_files(protocol["files"])
    if protocol["environment"] != v1.environment_identity():
        raise v1.CycleError("frozen_runtime_environment_changed")
    inputs = load_inputs(*(ROOT / protocol[key] for key in ("training", "validation", "review")))
    return cycle, protocol, inputs


def check_predictor(predictor, baseline_predictor):
    if (type(predictor) is not type(baseline_predictor)
            or type(predictor.classifier) is not type(baseline_predictor.classifier)
            or predictor.alpha != 0.10 or predictor.alpha != baseline_predictor.alpha
            or predictor.classifier.classes != baseline_predictor.classifier.classes):
        raise v1.CycleError("candidate_architecture_or_label_identity_changed")


def build(cycle):
    cycle, protocol, inputs = verify_cycle(cycle)
    v1.begin_phase(cycle, "build")
    try:
        with v1.offline_only():
            import joblib
            spec, baseline, baseline_identity = v1.runtime_baseline()
            from baseline_ml import _fit_predictor
            predictors = {}
            for axis in ("intent", "option"):
                train, calibration, target = inputs["recipe"][axis]
                predictors[axis], _support = _fit_predictor(train, calibration, target)
                old = baseline.predictors["D5"].intent if axis == "intent" else baseline.predictors["D5"].options
                check_predictor(predictors[axis], old)
                descriptor = os.open(cycle / ARTIFACTS[axis], os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(descriptor, "wb") as handle:
                    joblib.dump(predictors[axis], handle, compress=3)
            identity = {"protocol_sha256": v1.file_hash(cycle / "protocol.json"),
                "artifacts": {axis: v1.file_hash(cycle / name) for axis, name in ARTIFACTS.items()},
                "baseline_identity": baseline_identity, "baseline_source_hash": baseline.source_hash,
                "old_training_sha256": protocol["files"][v1.relative_file(OLD_DATA / "training-draft.json")],
                "new_training_sha256": protocol["files"][protocol["training"]],
                "calibration_sha256": protocol["files"]["data/nlp/all_questions/calibration.csv"]}
            result = {"status": "built_not_promoted", "completed_at": v1.utc_now(), "identity": identity,
                "candidate_identity_sha256": v1.digest(identity), "candidate_fit_counts": {"intent": 1, "option": 1},
                "training_rows": {"intent": 80, "option": 64}, "calibration_rows": {"intent": 60, "option": 40},
                "thresholds": {axis: predictor.threshold for axis, predictor in predictors.items()}, "alpha": 0.10,
                "baseline_startup": "unchanged original routine reconstructs 15 intent and 15 option predictors",
                "other_fourteen_retained": True, "all_questions": list(spec.question_order),
                "actual_gpt_calls": 0, "default_changed": False, "candidate_ready_for_demo": False}
            v1.verify_frozen_files(protocol["files"])
            v1.write_once(cycle / "build.json", result)
            return result
    except BaseException as exc:
        v1.failure_receipt(cycle, "build", exc)
        raise


def verify_artifacts(cycle, built, baseline_identity, baseline_source_hash):
    """Verify both files before allowing either joblib object to be loaded."""
    identity = built["identity"]
    if (identity["protocol_sha256"] != v1.file_hash(cycle / "protocol.json")
            or identity.get("artifacts") != {axis: v1.file_hash(cycle / name) for axis, name in ARTIFACTS.items()}
            or identity["baseline_identity"] != baseline_identity
            or identity["baseline_source_hash"] != baseline_source_hash
            or built["candidate_identity_sha256"] != v1.digest(identity)
            or built.get("candidate_fit_counts") != {"intent": 1, "option": 1}):
        raise v1.CycleError("candidate_two_artifact_identity_mismatch")


def candidate_resolver(cycle, baseline, baseline_identity):
    import joblib
    from baseline_ml import AllQuestionMLResolver, QuestionPredictors, lexical_support
    built = v1.read_json(cycle / "build.json")
    verify_artifacts(cycle, built, baseline_identity, baseline.source_hash)
    # Pickles are executable: accept only these hash-bound, trusted local outputs.
    intent, option = (joblib.load(cycle / ARTIFACTS[axis]) for axis in ("intent", "option"))
    check_predictor(intent, baseline.predictors["D5"].intent)
    check_predictor(option, baseline.predictors["D5"].options)
    pairs = dict(baseline.predictors)
    pairs["D5"] = QuestionPredictors(intent, option,
        lambda text: lexical_support(intent.classifier, text),
        lambda text: lexical_support(option.classifier, text))
    resolver = AllQuestionMLResolver(pairs, baseline.allowed_options, source_hash=built["candidate_identity_sha256"])
    if any(resolver.predictors[qid] is not baseline.predictors[qid] for qid in pairs if qid != "D5"):
        raise v1.CycleError("other_fourteen_predictor_identity_not_preserved")
    return resolver, built["candidate_identity_sha256"]


def semantic_fields(observed):
    """Stable decisions for unchanged-baseline parity; never timing or identity."""
    keys = ("route", "action", "ordinary_bucket", "result_bucket", "intent_set", "option_set",
        "ml_uncertain", "ml_reason", "resolver_candidate", "business_validation", "accepted_candidate",
        "contract_outcome", "escalation_required", "routing_ml_calls", "diagnostic_predictor_calls",
        "actual_gpt_calls", "ml_receipt_issued", "selected", "confirmed_version", "saved_version")
    value = {key: observed.get(key) for key in keys}
    raw = observed.get("raw")
    value["raw"] = None if raw is None else {axis: {key: raw[axis].get(key)
        for key in ("argmax", "prediction_set", "alpha")} for axis in ("intent", "option")}
    return value


def score_comparison(rows):
    """Preserve the union of baseline and saved-v1 successes without refitting v1."""
    result = v1.score_comparison(rows)
    failures = [dict(item, compared_with="unchanged_baseline") for item in result["blocking_gates"]
                if item["gate"] != "at_least_one_new_accepted_unseen_savings"]
    expected_ids = {"opened_validation": {f"D5-LV-{n:02d}" for n in range(1, 9)},
        "existing_regression": {f"D5-STD-{n:02d}" for n in range(1, 12)},
        "validation": {f"D5-V2-LV-{n:02d}" for n in range(1, 9)}}
    if (len(rows) != 27 or len({row["id"] for row in rows}) != 27 or any(
            {row["id"] for row in rows if row["split"] == split} != ids for split, ids in expected_ids.items())
            or any(sum(row["expected"]["kind"] == "clear" for row in rows if row["split"] == split) != 4
                   for split in ("opened_validation", "validation"))
            or any((row.get("previous_v1_candidate") is not None) != (row["split"] != "validation") for row in rows)):
        failures.append({"gate": "exact_27_cases_and_reference_denominators", "case_id": None})
    preservation = [dict(item, compared_with="unchanged_baseline") for item in result["preservation_by_case_and_axis"]]
    previous_rows = [dict(row, baseline=row["previous_v1_candidate"]) for row in rows if row.get("previous_v1_candidate") is not None]
    previous_result = v1.score_comparison(previous_rows)
    failures += [dict(item, compared_with="frozen_previous_v1_candidate") for item in previous_result["blocking_gates"]
                 if item["gate"] != "at_least_one_new_accepted_unseen_savings"]
    preservation += [dict(item, compared_with="frozen_previous_v1_candidate") for item in previous_result["preservation_by_case_and_axis"]]
    for row in rows:
        if row["expected"]["kind"] == "clear" and row["split"] in {"opened_validation", "validation"}:
            candidate, option = row["candidate"], row["expected"]["option_id"]
            if not candidate.get("raw") or candidate["raw"]["option"]["argmax"] != option:
                failures.append({"gate": "all_eight_opened_and_fresh_clear_raw_options", "case_id": row["id"]})
            if not candidate.get("ml_uncertain") and candidate.get("ordinary_bucket") in {"Undecided", "Confusion"}:
                failures.append({"gate": "clear_validation_no_wrong_confident_dialogue", "case_id": row["id"]})
    gained = [row["id"] for row in rows if row["split"] == "validation"
        and row["expected"]["kind"] == "clear" and row["expected"]["option_id"] == "D5_WITHDRAWALS"
        and row["baseline"].get("escalation_required")
        and row["baseline"].get("route") == "ml_then_gpt"
        and row["candidate"].get("accepted_candidate") == "D5_WITHDRAWALS"
        and row["candidate"].get("ml_receipt_issued") and row["candidate"].get("route") == "ml"]
    if not gained:
        failures.append({"gate": "at_least_one_fresh_savings_escalation_becomes_ml_acceptance", "case_id": None})
    return {"first_turn_gates_passed": not failures, "blocking_gates": failures,
        "new_correct_accepted_validation_savings_ids": gained,
        "preservation_by_case_and_axis": preservation, "candidate_ready_for_demo": False,
        "remaining_gate": "candidate-specific original four contextual turns and controls; no v2 demo profile yet"}


def metrics(rows, variant):
    return {split: v1.metrics([dict(row, split="validation") for row in rows if row["split"] == split], variant)["validation"]
        for split in ("opened_validation", "existing_regression", "validation")}


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
                current_baseline = v1.inspect_case(spec, baseline, baseline_identity, case)
                previous = inputs["previous"].get(case["id"])
                if previous and semantic_fields(current_baseline) != semantic_fields(previous["baseline"]):
                    v1.write_once(cycle / "baseline-mismatch.json", {"case_id": case["id"],
                        "current": current_baseline, "previous": previous["baseline"], "retry": False})
                    raise v1.CycleError("unchanged_baseline_semantic_parity_failed")
                rows.append({"id": case["id"], "split": case["split"], "text": case["text"],
                    "expected": expected(case), "baseline": current_baseline,
                    "candidate": v1.inspect_case(spec, candidate, identity, case),
                    "previous_v1_candidate": previous["candidate"] if previous else None})
            result = {"status": "comparison_complete", "completed_at": v1.utc_now(),
                "candidate_identity_sha256": identity, "protocol_sha256": v1.file_hash(cycle / "protocol.json"),
                **score_comparison(rows), "baseline": metrics(rows, "baseline"),
                "candidate": metrics(rows, "candidate"), "cases": rows,
                "previous_baseline_semantic_parity": {"matched": 19, "required": 19},
                "actual_gpt_calls": 0, "candidate_fits_during_compare": 0, "previous_candidate_rerun": False,
                "default_changed": False, "validation_used_for_tuning": False,
                "limitations": ["Fresh eight replies are agent-authored and human-reviewed, not independent human-original evaluation.",
                    "Previous eight validation and original eleven replies are opened preservation evidence.",
                    "Escalation is recorded before any LLM execution; controls are not ML interpretation successes.",
                    "Raw option accuracy is only defined for clear replies; incomplete raw labels have no forced gold."]}
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
    command.add_argument("--training", type=Path, default=DEFAULT_DATA / "training-additions.json")
    command.add_argument("--validation", type=Path, default=DEFAULT_DATA / "validation-draft.json")
    command.add_argument("--review", type=Path, default=DEFAULT_DATA / "human-review.json")
    command.add_argument("--output", type=Path, required=True)
    for name in ("build", "compare"):
        commands.add_parser(name).add_argument("--cycle", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = (freeze(args.training, args.validation, args.review, args.output) if args.command == "freeze"
                  else build(args.cycle) if args.command == "build" else compare(args.cycle))
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0 if result.get("first_turn_gates_passed", True) else 2
    except (Exception, KeyboardInterrupt) as exc:
        print(json.dumps({"status": "stopped", "failure_code": str(exc) if isinstance(exc, v1.CycleError)
            else "local_runtime_failure", "error_type": type(exc).__name__, "retry": False}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
