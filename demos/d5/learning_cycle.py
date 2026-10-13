"""One reviewed, offline D5 option-learning cycle; never a demo default.

freeze -> build -> compare. Importing this module does not import ML, a GPT
transport or credentials. Every operational phase is write-once. A failed phase
needs a separately authorised cycle, not a retry or edits to the frozen inputs.
The only learned replacement is the existing D5 option predictor. The original
intent predictor, architecture, calibration rule and business veto are retained.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_DATA = ROOT / "docs/d5-learning-cycle-v1"
BASELINE_MANIFEST = HERE / "baseline-ml-manifest.json"
ORIGINAL = ROOT / "docs/d5-semantic-repair/evidence/after"
VERSION = "d5-option-learning-v1"
OPTIONS = frozenset({"D5_SALARY", "D5_SELF_EMPLOYMENT", "D5_PENSION_PAYMENTS",
    "D5_BENEFITS_SUPPORT", "D5_WITHDRAWALS", "D5_OTHER_REGULAR", "D5_NO_REGULAR",
    "D5_MULTIPLE"})


class CycleError(RuntimeError):
    """Only fixed, non-sensitive error codes cross the CLI boundary."""


class EscalationRequired(BaseException):
    """Stop exactly before LLM execution; not an LLM failure or mock answer."""


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_once(path, value):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def external_cycle(path):
    path = Path(path).expanduser().absolute()
    if path.is_symlink() or path.resolve().is_relative_to(ROOT):
        raise CycleError("cycle_output_must_be_outside_repository")
    return path


def relative_file(path):
    path = Path(path).expanduser().resolve()
    if not path.is_file() or not path.is_relative_to(ROOT):
        raise CycleError("frozen_source_must_be_a_repository_file")
    return path.relative_to(ROOT).as_posix()


def normalise(text):
    return " ".join(re.sub(r"[^\w]+", " ", text.casefold()).split())


def validate_review(review, training_path, validation_path, case_ids):
    """An agent-authored draft or pending review cannot authorise fitting."""
    if (review.get("schema_version") != "d5-learning-review-v1"
            or review.get("review_type") != "human_business_review"
            or review.get("status") != "approved"):
        raise CycleError("explicit_human_business_approval_required")
    if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
        raise CycleError("named_human_reviewer_required")
    try:
        reviewed = datetime.fromisoformat(review.get("reviewed_at", "").replace("Z", "+00:00"))
        if reviewed.utcoffset() is None:
            raise ValueError
    except (TypeError, ValueError, AttributeError):
        raise CycleError("timezone_aware_review_timestamp_required") from None
    expected = {"training": file_hash(training_path), "validation": file_hash(validation_path)}
    if review.get("dataset_sha256") != expected:
        raise CycleError("reviewed_dataset_hash_mismatch")
    approved = review.get("approved_case_ids")
    if (not isinstance(approved, list) or any(not isinstance(x, str) for x in approved)
            or len(approved) != len(set(approved)) or set(approved) != set(case_ids)):
        raise CycleError("all_sixteen_case_ids_need_explicit_review")
    if review.get("provenance_acknowledgement") != "agent_authored_human_reviewed":
        raise CycleError("truthful_review_provenance_required")


def dataset_rows(path, split):
    rows = read_json(path).get("rows")
    if not isinstance(rows, list) or len(rows) != 8:
        raise CycleError("exactly_eight_rows_per_split_required")
    for row in rows:
        if not isinstance(row, dict):
            raise CycleError("invalid_dataset_row")
        for key in ("id", "text", "business_meaning", "expected_action", "source", "group_id"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise CycleError("missing_dataset_annotation")
        if row.get("question_id") != "D5" or row.get("split") != split:
            raise CycleError("d5_first_turn_split_required")
        kind, bucket, option = row.get("kind"), row.get("bucket"), row.get("option_id")
        if kind == "clear":
            valid = bucket == "clarity" and option in OPTIONS
        elif kind in {"undecided", "confusion"}:
            valid = bucket == kind and option is None
        elif kind == "incomplete":
            valid = bucket is None and option is None
        else:
            valid = False
        if not valid:
            raise CycleError("invalid_business_label_contract")
    if split == "train":
        if (Counter(row["kind"] for row in rows) != {"clear": 8}
                or Counter(row["option_id"] for row in rows) != {
                    "D5_WITHDRAWALS": 4, "D5_SALARY": 2, "D5_MULTIPLE": 2}
                or sum(normalise(row["text"]) == "savings" for row in rows) != 1):
            raise CycleError("fixed_training_composition_required")
    elif (Counter(row["kind"] for row in rows) != {
                "clear": 4, "incomplete": 2, "undecided": 1, "confusion": 1}
            or Counter(row["option_id"] for row in rows if row["kind"] == "clear") != {
                "D5_WITHDRAWALS": 2, "D5_SALARY": 1, "D5_MULTIPLE": 1}):
        raise CycleError("fixed_validation_composition_required")
    return rows


def csv_d5(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return [row for row in csv.DictReader(handle) if row["question_id"] == "D5"]


def original_cases():
    labels = read_json(ORIGINAL / "expectations.json")["cases"]
    rows = []
    for item in read_json(ORIGINAL / "inputs.json")["rows"]:
        gold = labels[item["id"]]
        kind = "incomplete" if gold["kind"] == "missing_information" else gold["kind"]
        rows.append(dict(item, split="existing_regression", kind=kind,
            bucket="clarity" if kind == "clear" else None if kind == "incomplete" else kind,
            option_id=gold["option"], control_required=item["id"] == "D5-STD-11"))
    if len(rows) != 11:
        raise CycleError("unchanged_eleven_case_bank_required")
    return rows


def load_reviewed_inputs(training, validation, review):
    training_rows, validation_rows = dataset_rows(training, "train"), dataset_rows(validation, "validation")
    all_rows = training_rows + validation_rows
    validate_review(read_json(review), training, validation, [row["id"] for row in all_rows])
    for key in ("id", "group_id"):
        if len({row[key] for row in all_rows}) != 16:
            raise CycleError("duplicate_case_or_group_id")
    if len({normalise(row["text"]) for row in all_rows}) != 16:
        raise CycleError("duplicate_normalised_reply")
    manifest = read_json(BASELINE_MANIFEST)
    data = ROOT / manifest["data_directory"]
    original_train, original_calibration = csv_d5(data / "train.csv"), csv_d5(data / "calibration.csv")
    known = original_train + original_calibration + original_cases()
    known_texts = {normalise(row["text"]) for row in known}
    known_ids = {row["id"] for row in known}
    known_groups = {row["group_id"] for row in known if row.get("group_id")}
    if any(normalise(row["text"]) in known_texts or row["id"] in known_ids
           or row["group_id"] in known_groups for row in all_rows):
        raise CycleError("new_split_overlaps_existing_bank")
    train_clear = [row for row in original_train if row["bucket"] == "clarity"]
    cal_clear = [row for row in original_calibration if row["bucket"] == "clarity"]
    if len(train_clear) != 48 or len(cal_clear) != 40:
        raise CycleError("unchanged_48_train_40_calibration_required")
    if Counter(row["option_id"] for row in train_clear) != {option: 6 for option in OPTIONS}:
        raise CycleError("unchanged_original_training_balance_required")
    if Counter(row["option_id"] for row in cal_clear) != {option: 5 for option in OPTIONS}:
        raise CycleError("unchanged_original_calibration_balance_required")
    return training_rows, validation_rows, train_clear, cal_clear


def freeze_files(training, validation, review):
    manifest = read_json(BASELINE_MANIFEST)
    for name, expected in manifest["files"].items():
        if file_hash(ROOT / name) != expected:
            raise CycleError("baseline_manifest_mismatch")
    paths = {Path(ROOT / name) for name in manifest["files"]}
    paths.update({Path(__file__), HERE / "test_learning_cycle.py", BASELINE_MANIFEST,
        HERE / "session.py", HERE / "local_session.py", HERE / "local_engine.py", HERE / "requirements.txt",
        Path(training), Path(validation), Path(review), ORIGINAL / "inputs.json",
        ORIGINAL / "expectations.json"})
    # The packaged runtime includes control handling, question wording, prompt,
    # strict contract and business veto. None may drift after the freeze.
    paths.update(path for path in (HERE / "runtime").rglob("*")
        if path.is_file() and path.suffix in {".py", ".json", ".txt"})
    return {relative_file(path): file_hash(path) for path in sorted(paths)}


def environment_identity():
    return {"python": sys.version.split()[0], "packages": {
        name: importlib.metadata.version(name) for name in ("scikit-learn", "numpy", "scipy", "joblib")}}


def freeze(training, validation, review, output):
    load_reviewed_inputs(training, validation, review)
    files = freeze_files(training, validation, review)
    cycle = external_cycle(output)
    if cycle.exists():
        raise CycleError("cycle_directory_already_exists")
    protocol = {"version": VERSION, "created_at": utc_now(), "files": files,
        "training": relative_file(training), "validation": relative_file(validation),
        "review": relative_file(review), "environment": environment_identity(),
        "candidate": "D5 option predictor only; unchanged TF-IDF and logistic regression",
        "option_training_rows": 56, "option_calibration_rows": 40, "alpha": 0.10,
        "candidate_fit_limit": 1, "automatic_retry": False,
        "evaluation": "8 reviewed new first turns plus 11 opened regression replies",
        "not_claimed": ["independent human-authored evaluation", "whole-product readiness",
            "unseen success from training fit", "contextual live GPT success", "automatic learning"],
        "final_gate": "separate candidate four-context and control verification also required"}
    cycle.mkdir(parents=True, exist_ok=False, mode=0o700)
    write_once(cycle / "protocol.json", protocol)
    write_once(cycle / "freeze.json", {"protocol_sha256": file_hash(cycle / "protocol.json"),
        "created_at": utc_now(), "status": "frozen_after_human_review"})
    return {"status": "frozen", "cycle": str(cycle), "model_calls": 0, "candidate_fits": 0}


def verify_frozen_files(files, root=ROOT):
    for name, expected in files.items():
        path = (Path(root) / name).resolve()
        if not path.is_relative_to(Path(root).resolve()) or not path.is_file() or file_hash(path) != expected:
            raise CycleError("frozen_file_changed")


def verify_cycle(cycle):
    cycle = external_cycle(cycle)
    protocol = read_json(cycle / "protocol.json")
    if (protocol.get("version") != VERSION or
            file_hash(cycle / "protocol.json") != read_json(cycle / "freeze.json")["protocol_sha256"]):
        raise CycleError("protocol_identity_mismatch")
    verify_frozen_files(protocol["files"])
    if protocol["environment"] != environment_identity():
        raise CycleError("frozen_runtime_environment_changed")
    inputs = load_reviewed_inputs(*(ROOT / protocol[key] for key in ("training", "validation", "review")))
    return cycle, protocol, inputs


def begin_phase(cycle, phase):
    if any((cycle / name).exists() for name in
           (f"{phase}.started.json", f"{phase}.json", f"{phase}.STOP.json")):
        raise CycleError("phase_already_attempted_no_retry")
    try:
        write_once(cycle / f"{phase}.started.json", {"started_at": utc_now(), "retry": False})
    except FileExistsError:
        raise CycleError("phase_already_attempted_no_retry") from None


@contextmanager
def offline_only():
    def forbidden(*args, **kwargs):
        raise CycleError("network_or_subprocess_forbidden")
    # No subprocess launch is needed by the unchanged single-process baseline.
    # An LLM transport or credential acquisition is never imported by this CLI.
    with patch.object(socket.socket, "connect", forbidden), \
         patch.object(socket.socket, "connect_ex", forbidden), \
         patch.object(socket, "create_connection", forbidden), \
         patch.object(subprocess, "Popen", forbidden):
        yield


def runtime_baseline():
    # Lazy import: none of these paths can be reached before review and freeze.
    from session import RUNTIME, bootstrap
    bootstrap()
    from ai.question_spec import BusinessSpec
    from local_session import load_baseline
    spec = BusinessSpec.load(RUNTIME / "config/business-decision-spec.json")
    if len(spec.question_order) != 15:
        raise CycleError("unchanged_fifteen_questions_required")
    resolver, identity = load_baseline(spec)
    return spec, resolver, identity


def failure_receipt(cycle, phase, exc):
    write_once(cycle / f"{phase}.STOP.json", {"stopped_at": utc_now(),
        "failure_code": str(exc) if isinstance(exc, CycleError) else "local_runtime_failure",
        "error_type": type(exc).__name__, "actual_gpt_calls": 0, "retry": False})


def build(cycle):
    cycle, protocol, inputs = verify_cycle(cycle)
    begin_phase(cycle, "build")
    try:
        with offline_only():
            import joblib
            spec, baseline, baseline_identity = runtime_baseline()
            from baseline_ml import _fit_predictor
            additions, _, original_train, calibration = inputs
            candidate, _support = _fit_predictor(original_train + additions, calibration, "option_id")
            if candidate.alpha != 0.10 or candidate.classifier.classes != baseline.predictors["D5"].options.classifier.classes:
                raise CycleError("candidate_architecture_or_label_identity_changed")
            artifact = cycle / "d5-option-candidate.joblib"
            descriptor = os.open(artifact, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as handle:
                joblib.dump(candidate, handle, compress=3)
            identity_parts = {"protocol_sha256": file_hash(cycle / "protocol.json"),
                "artifact_sha256": file_hash(artifact), "baseline_identity": baseline_identity,
                "baseline_source_hash": baseline.source_hash,
                "training_sha256": protocol["files"][protocol["training"]],
                "calibration_sha256": protocol["files"]["data/nlp/all_questions/calibration.csv"]}
            result = {"status": "built_not_promoted", "completed_at": utc_now(),
                "identity": identity_parts, "candidate_identity_sha256": digest(identity_parts),
                "candidate_fit_count": 1, "candidate_training_rows": 56,
                "candidate_calibration_rows": 40, "alpha": candidate.alpha,
                "baseline_option_threshold": baseline.predictors["D5"].options.threshold,
                "candidate_option_threshold": candidate.threshold,
                "baseline_startup": "unchanged original procedure reconstructs 15 intent and 15 option predictors",
                "d5_intent_retained": True, "other_fourteen_retained": True,
                "all_questions": list(spec.question_order), "actual_gpt_calls": 0,
                "default_changed": False, "candidate_ready_for_demo": False}
            verify_frozen_files(protocol["files"])
            write_once(cycle / "build.json", result)
            return result
    except BaseException as exc:
        failure_receipt(cycle, "build", exc)
        raise


def candidate_resolver(cycle, baseline, baseline_identity):
    import joblib
    from baseline_ml import (AllQuestionMLResolver, BoundedTextClassifier,
        FiniteSampleConformalClassifier, QuestionPredictors, lexical_support)
    built = read_json(cycle / "build.json")
    identity = built["identity"]
    if (identity["protocol_sha256"] != file_hash(cycle / "protocol.json")
            or identity["artifact_sha256"] != file_hash(cycle / "d5-option-candidate.joblib")
            or identity["baseline_identity"] != baseline_identity
            or identity["baseline_source_hash"] != baseline.source_hash
            or built["candidate_identity_sha256"] != digest(identity)
            or built.get("candidate_fit_count") != 1):
        raise CycleError("candidate_artifact_identity_mismatch")
    # Joblib can execute code: only load this cycle's hash-verified local output.
    option = joblib.load(cycle / "d5-option-candidate.joblib")
    old = baseline.predictors["D5"]
    if (type(option) is not FiniteSampleConformalClassifier
            or type(option.classifier) is not BoundedTextClassifier
            or option.alpha != old.options.alpha
            or option.classifier.classes != old.options.classifier.classes):
        raise CycleError("candidate_architecture_or_label_identity_changed")
    pairs = dict(baseline.predictors)
    pairs["D5"] = QuestionPredictors(old.intent, option, old.intent_support,
        lambda text: lexical_support(option.classifier, text))
    candidate = AllQuestionMLResolver(pairs, baseline.allowed_options,
        source_hash=built["candidate_identity_sha256"])
    if (candidate.predictors["D5"].intent is not old.intent or any(
            candidate.predictors[qid] is not baseline.predictors[qid] for qid in pairs if qid != "D5")):
        raise CycleError("untouched_predictor_identity_not_preserved")
    return candidate, built["candidate_identity_sha256"]


def raw_prediction(predictor, text):
    result = predictor.predict(text)
    probabilities = dict(result.probabilities)
    return {"argmax": max(probabilities, key=probabilities.get), "probabilities": probabilities,
        "prediction_set": sorted(result.prediction_set), "threshold": result.threshold,
        "alpha": result.alpha}


def inspect_case(spec, resolver, identity, case):
    from ai.d5_single_interpreter_contract_v2 import D5DialogueContext, D5SingleInterpreter
    from local_engine import LocalD5Engine
    from session import NoOtherQuestions, NoProfileSave
    escalation = False

    def no_inference(messages, schema):
        nonlocal escalation
        escalation = True
        raise EscalationRequired()

    interpreter = D5SingleInterpreter(spec, no_inference,
        model_metadata={"mode": "offline_escalation_boundary_no_model"})
    engine = LocalD5Engine(spec, ml_resolver=resolver, ml_identity=identity,
        d5_interpreter=interpreter, question_resolver=NoOtherQuestions(),
        store=NoProfileSave(), backend_name="gpt")
    engine.state.current_index = spec.question_order.index("D5")
    interpreter.context = D5DialogueContext(pending_prompt=spec.question("D5").question)
    try:
        result = engine.submit_answer(case["text"])
    except EscalationRequired:
        result = {"action": "escalation_required_not_executed"}
    # Diagnose raw classifiers only when controls actually allowed ML to run.
    # This keeps Help at zero model calls. These are separate diagnostic calls,
    # not extra routing stages and are never supplied to GPT.
    raw = None
    if engine.ml_calls:
        pair = resolver.predictors["D5"]
        raw = {"intent": raw_prediction(pair.intent, case["text"]),
               "option": raw_prediction(pair.options, case["text"])}
    evidence = engine.last_ml_evidence or {}
    financial = engine.state.answers["D5"].candidate_option_id
    return {"route": engine.last_route, "action": result.get("action"),
        "ordinary_bucket": evidence.get("bucket"), "result_bucket": result.get("bucket"),
        "raw": raw, "raw_option_scored": case["kind"] == "clear" and raw is not None,
        "raw_intent_scored": case["kind"] != "incomplete" and raw is not None,
        "intent_set": evidence.get("intent_set", []), "option_set": evidence.get("option_set", []),
        "ml_uncertain": evidence.get("model_uncertain"), "ml_reason": evidence.get("reason"),
        "resolver_candidate": evidence.get("candidate"),
        "business_validation": evidence.get("business_validation"),
        "accepted_candidate": financial, "contract_outcome": result.get("contract_outcome"),
        "escalation_required": escalation, "routing_ml_calls": engine.ml_calls,
        "diagnostic_predictor_calls": 2 if raw else 0, "actual_gpt_calls": 0,
        "ml_receipt_issued": engine._ml_receipt is not None,
        "selected": engine.state.answers["D5"].selected_option_id,
        "confirmed_version": engine.state.answers["D5"].confirmed_version,
        "saved_version": engine.state.saved_version}


def score_comparison(rows):
    """Pure scoring; raw, gated and control denominators stay distinct."""
    failures, new_savings, preservation = [], [], []
    def fail(code, identifier):
        failures.append({"gate": code, "case_id": identifier})
    for row in rows:
        gold, base, new = row["expected"], row["baseline"], row["candidate"]
        identifier, kind = row["id"], gold["kind"]
        option, bucket = gold.get("option_id"), gold.get("bucket")
        braw, nraw = base.get("raw"), new.get("raw")
        for observed in (base, new):
            if any(observed.get(key) is not None for key in ("selected", "confirmed_version", "saved_version")):
                fail("proposal_must_not_confirm_or_save", identifier)
        if new.get("actual_gpt_calls") != 0:
            fail("offline_no_gpt_calls", identifier)
        if new.get("accepted_candidate") is not None and (kind != "clear" or new["accepted_candidate"] != option):
            fail("no_wrong_accepted_financial_answer", identifier)
        if new.get("accepted_candidate") is not None and not new.get("ml_receipt_issued"):
            fail("real_ml_receipt_required", identifier)
        if kind == "clear":
            if (row["split"] == "validation" and not new.get("ml_uncertain")
                    and new.get("ordinary_bucket") in {"Undecided", "Confusion"}):
                fail("clear_validation_no_wrong_confident_dialogue", identifier)
            if (new.get("resolver_candidate") not in {None, option}
                    and new.get("resolver_candidate") != base.get("resolver_candidate")):
                fail("no_new_wrong_raw_financial_commitment", identifier)
            if row["split"] == "validation" and (not nraw or nraw["option"]["argmax"] != option):
                fail("all_four_new_clear_raw_options", identifier)
            if base.get("accepted_candidate") == option:
                preservation.append({"case_id": identifier, "axis": "accepted_financial",
                    "preserved": new.get("accepted_candidate") == option})
                if new.get("accepted_candidate") != option:
                    fail("preserve_accepted_financial_success", identifier)
            if (row["split"] == "validation" and option == "D5_WITHDRAWALS"
                    and new.get("accepted_candidate") == option and base.get("accepted_candidate") != option):
                new_savings.append(identifier)
        if kind == "incomplete":
            # No forced argmax gold exists for an incomplete answer. However a
            # confident resolver commitment is unsafe even if the veto saves it.
            if new.get("resolver_candidate") is not None:
                fail("incomplete_no_confident_financial_commitment", identifier)
            if new.get("ordinary_bucket") in {"Undecided", "Confusion", "Clarity"} and not new.get("ml_uncertain"):
                fail("incomplete_no_invented_customer_bucket", identifier)
        if kind in {"undecided", "confusion"}:
            if new.get("resolver_candidate") is not None:
                fail("nonclear_no_confident_financial_commitment", identifier)
            confident = new.get("ordinary_bucket") if not new.get("ml_uncertain") else None
            if confident and confident.casefold() != kind:
                fail("nonclear_confident_bucket_must_match", identifier)
            if (base.get("route") == "ml" and not base.get("ml_uncertain")
                    and (base.get("ordinary_bucket") or "").casefold() == kind):
                retained = new.get("route") == "ml" and confident is not None and confident.casefold() == kind
                preservation.append({"case_id": identifier, "axis": "accepted_dialogue_bucket", "preserved": retained})
                if not retained:
                    fail("preserve_correct_confident_dialogue", identifier)
        if braw and nraw:
            axes = [("intent", bucket)] if kind != "incomplete" else []
            if kind == "clear":
                axes.append(("option", option))
            for axis, expected in axes:
                if braw[axis]["argmax"] == expected:
                    retained = nraw[axis]["argmax"] == expected
                    preservation.append({"case_id": identifier, "axis": "raw_" + axis, "preserved": retained})
                    if not retained:
                        fail("no_new_raw_error_preserve_previous_success", identifier)
            if kind in {"undecided", "confusion"} and braw["intent"]["argmax"] != "clarity" and nraw["intent"]["argmax"] == "clarity":
                fail("no_new_raw_false_clarity", identifier)
        elif braw and not nraw:
            fail("raw_diagnostic_disappeared", identifier)
        if gold.get("control_required"):
            for observed in (base, new):
                if (observed.get("routing_ml_calls") != 0 or observed.get("diagnostic_predictor_calls") != 0
                        or observed.get("actual_gpt_calls") != 0 or observed.get("escalation_required")
                        or observed.get("accepted_candidate") is not None or observed.get("action") != "explain"):
                    fail("existing_help_zero_models", identifier)
        # A validation Confusion reply may likewise be handled before either
        # predictor. Count that as control dialogue, never ML semantic success.
        if new.get("routing_ml_calls") == 0 and not gold.get("control_required"):
            if kind != "confusion" or new.get("action") != "explain":
                fail("unexpected_pre_model_control", identifier)
    if not new_savings:
        fail("at_least_one_new_accepted_unseen_savings", None)
    return {"first_turn_gates_passed": not failures, "blocking_gates": failures,
        "new_correct_accepted_validation_savings_ids": new_savings,
        "preservation_by_case_and_axis": preservation,
        "candidate_ready_for_demo": False,
        "remaining_gate": "original four contextual turns and controls with this candidate; separate evidence required"}


def metrics(rows, variant):
    result = {}
    for split in ("validation", "existing_regression"):
        subset = [row for row in rows if row["split"] == split]
        clear = [row for row in subset if row["expected"]["kind"] == "clear"]
        intent = [row for row in subset if row["expected"]["kind"] != "incomplete" and row[variant].get("raw")]
        result[split] = {
            "cases": len(subset), "raw_option_denominator": len([row for row in clear if row[variant].get("raw")]),
            "raw_option_correct": sum(bool(row[variant].get("raw")) and row[variant]["raw"]["option"]["argmax"] == row["expected"]["option_id"] for row in clear),
            "raw_intent_denominator": len(intent),
            "raw_intent_correct": sum(row[variant]["raw"]["intent"]["argmax"] == row["expected"]["bucket"] for row in intent),
            "accepted_correct_financial": sum(row[variant].get("accepted_candidate") == row["expected"]["option_id"] for row in clear),
            "wrong_accepted_financial": sum(row[variant].get("accepted_candidate") is not None and
                (row["expected"]["kind"] != "clear" or row[variant]["accepted_candidate"] != row["expected"]["option_id"]) for row in subset),
            "ml_handled": sum(row[variant]["route"] == "ml" for row in subset),
            "ml_eligible": sum(row[variant]["routing_ml_calls"] > 0 for row in subset),
            "escalation_required_not_executed": sum(row[variant]["escalation_required"] for row in subset),
            "control_handled": sum(row[variant]["routing_ml_calls"] == 0 for row in subset),
            "actual_gpt_calls": 0}
    return result


def compare(cycle):
    cycle, protocol, inputs = verify_cycle(cycle)
    if not (cycle / "build.json").is_file() or (cycle / "build.STOP.json").exists():
        raise CycleError("completed_single_build_required")
    begin_phase(cycle, "compare")
    try:
        with offline_only():
            spec, baseline, baseline_identity = runtime_baseline()
            candidate, candidate_identity = candidate_resolver(cycle, baseline, baseline_identity)
            rows = []
            for case in inputs[1] + original_cases():
                rows.append({"id": case["id"], "split": case["split"], "text": case["text"],
                    "expected": {key: case.get(key) for key in ("kind", "bucket", "option_id", "control_required")},
                    "baseline": inspect_case(spec, baseline, baseline_identity, case),
                    "candidate": inspect_case(spec, candidate, candidate_identity, case)})
            result = {"status": "comparison_complete", "completed_at": utc_now(),
                "candidate_identity_sha256": candidate_identity,
                "protocol_sha256": file_hash(cycle / "protocol.json"),
                **score_comparison(rows), "baseline": metrics(rows, "baseline"),
                "candidate": metrics(rows, "candidate"), "cases": rows,
                "actual_gpt_calls": 0, "candidate_fits_during_compare": 0,
                "default_changed": False, "validation_used_for_tuning": False,
                "limitations": ["Small agent-authored and human-reviewed pilot, not independent human-original evaluation.",
                    "Existing 11 replies are opened regression evidence.",
                    "Escalation is captured before inference; there are no GPT answers or contextual live results.",
                    "Raw argmax is diagnostic, not an accepted answer; incomplete answers have no forced raw label."]}
            verify_frozen_files(protocol["files"])
            write_once(cycle / "compare.json", result)
            return {key: result[key] for key in ("status", "first_turn_gates_passed", "blocking_gates",
                "candidate_ready_for_demo", "remaining_gate", "actual_gpt_calls")}
    except BaseException as exc:
        failure_receipt(cycle, "compare", exc)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("freeze", help="Freeze only explicitly approved, hash-bound business labels")
    command.add_argument("--training", type=Path, default=DEFAULT_DATA / "training-draft.json")
    command.add_argument("--validation", type=Path, default=DEFAULT_DATA / "validation-draft.json")
    command.add_argument("--review", type=Path, default=DEFAULT_DATA / "human-review.json")
    command.add_argument("--output", type=Path, required=True)
    for name in ("build", "compare"):
        commands.add_parser(name).add_argument("--cycle", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = (freeze(args.training, args.validation, args.review, args.output)
                  if args.command == "freeze" else build(args.cycle)
                  if args.command == "build" else compare(args.cycle))
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0 if result.get("first_turn_gates_passed", True) else 2
    except (Exception, KeyboardInterrupt) as exc:
        print(json.dumps({"status": "stopped", "failure_code": str(exc) if isinstance(exc, CycleError)
            else "local_runtime_failure", "error_type": type(exc).__name__, "retry": False}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
