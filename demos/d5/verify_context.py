"""Offline software checks for the bounded D5 dialogue context.

Uses published saved outputs and explicitly labelled structural fixtures. This
does not measure semantic accuracy and cannot call credentials or a network.
Run in its own process: python demos/d5/verify_context.py --output /tmp/...
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
import hashlib
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from session import D5Session, bootstrap

bootstrap()
from ai.d5_single_interpreter_contract_v2 import (
    D5DialogueContext, D5SingleContractError, D5SingleInterpreter,
    MAX_CONTEXT_CHARS, MAX_CONTEXT_TURNS, build_messages, output_schema,
    parse_interpretation,
)
from ai import d5_single_interpreter_transport as transport
from ai.llm_shadow import canonical_json, strict_json
from ai.question_spec import BusinessSpec

SPEC = BusinessSpec.load(HERE / "runtime/config/business-decision-spec.json")
FIXTURE_ROOT = ROOT / "docs/d5-semantic-repair/evidence/after/records"
FIXTURE_IDS = ("01", "02", "09", "10", "11")
FIXTURES = {identifier: json.loads(
    (FIXTURE_ROOT / f"D5-STD-{identifier}.json").read_text()) for identifier in FIXTURE_IDS}
LIVE_FIXTURE_ROOT = ROOT / "docs/d5-context-verification-2026-10-13/records"
LIVE_FIXTURES = [json.loads((LIVE_FIXTURE_ROOT / f"CONTEXT-{number:02d}.json").read_text())
                 for number in range(1, 5)]
FIXED_PLAYBACK = []


def forbidden(*args, **kwargs):
    raise AssertionError("Offline verification forbids credentials and network access")


class SavedOutputBackend:
    """A fixture replay double, never an actual interpretation service."""
    def __init__(self, *args, **kwargs):
        self.outputs = []
        self.calls = 0
        self.requests = []
        self.last_call = {}
        self.case_id = None

    def __call__(self, messages, schema):
        if not self.outputs:
            raise AssertionError("Unexpected extra fixture replay")
        # Exercise real passive request validation without constructing HTTP.
        payload = transport.request_payload(messages, schema)
        self.requests.append(payload)
        self.calls += 1
        self.last_call = {"offline_fixture_replay": True, "actual_calls": 0}
        return self.outputs.pop(0)


class ContextChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="d5-context-offline-")
        self.addCleanup(self.tmp.cleanup)

    def session(self, *identifiers):
        directory = Path(self.tmp.name) / f"session-{len(list(Path(self.tmp.name).iterdir()))}"
        directory.mkdir(mode=0o700)
        # The sentinel is not a credential provider and is never inspected.
        with patch.object(transport, "SingleInterpreterGenerator", SavedOutputBackend):
            session = D5Session(object(), directory)
        session.backend.outputs = [FIXTURES[i]["raw_output"] for i in identifiers]
        return session

    def original(self, session, identifier):
        return session.submit(FIXTURES[identifier]["input"])

    def context_fixture(self):
        """Structural 'yes' fixture; not a model output or accuracy case."""
        source = FIXTURES["01"]
        context = D5DialogueContext((("Original D5 question", source["input"]),),
            "Is that still the current funding situation?")
        data = deepcopy(source["raw"])
        data["evidence"].append("yes")
        return context, data

    def test_existing_source_followup_is_one_short_answerable_question(self):
        session = self.session("10")
        result = self.original(session, "10")
        question = result["followup"]
        self.assertEqual(result["clarification_topic"], "source_use_unknown:D5_SALARY")
        self.assertIn("salary or wages", question)
        self.assertIn("yes, no or", question)
        self.assertEqual(question.count("?"), 1)
        self.assertNotIn("complete current answer", question)
        self.assertEqual(len(session.interpreter.context.history), 1)
        self.assertIn(question, session.interpreter.context.pending_prompt)

    def test_existing_replies_are_forwarded_without_changing_original_text(self):
        session = self.session("09", "01")
        first = self.original(session, "09")
        result = self.original(session, "01")
        supplied = strict_json(session.backend.requests[-1]["input"][0]["content"])
        self.assertEqual(supplied["original_reply"], FIXTURES["01"]["input"])
        self.assertEqual(supplied["dialogue_context"]["history"][0]["reply"], FIXTURES["09"]["input"])
        self.assertIn(first["followup"], supplied["dialogue_context"]["pending_prompt"])
        self.assertEqual(result["candidate_option_id"], "D5_PENSION_PAYMENTS")
        self.assertEqual(session.backend.calls, 2)
        self.assertEqual(session.engine.state.answers["D5"].raw_text, FIXTURES["01"]["input"])

    def test_current_reply_and_separate_earlier_user_spans_are_valid(self):
        context, data = self.context_fixture()
        parsed = parse_interpretation(canonical_json(data), "yes", context=context)
        self.assertEqual(parsed.option_id, "D5_PENSION_PAYMENTS")

    def test_prior_reply_is_not_valid_evidence_without_context(self):
        _, data = self.context_fixture()
        with self.assertRaisesRegex(D5SingleContractError, "evidence_is_not_exact_reply_span"):
            parse_interpretation(canonical_json(data), "yes")

    def test_authored_prompt_is_never_financial_quote_evidence(self):
        context, data = self.context_fixture()
        data["evidence"].append(context.pending_prompt)
        with self.assertRaisesRegex(D5SingleContractError, "evidence_is_not_exact_reply_span"):
            parse_interpretation(canonical_json(data), "yes", context=context)

    def test_exact_quotes_cannot_be_joined_across_user_turns(self):
        context, data = self.context_fixture()
        split = replace(context, history=(("Question A", "My wages stay in"),
            ("Question B", " savings. My pension pays the bills.")))
        with self.assertRaisesRegex(D5SingleContractError, "evidence_is_not_exact_reply_span"):
            parse_interpretation(canonical_json(data), "yes", context=split)

    def test_context_does_not_authorise_ignoring_the_current_reply(self):
        context, data = self.context_fixture()
        data["evidence"].remove("yes")
        with self.assertRaisesRegex(D5SingleContractError, "current_reply_evidence_required"):
            parse_interpretation(canonical_json(data), "yes", context=context)

    def test_confirmation_uses_issued_snapshot_after_session_history_appends(self):
        session = self.session("09", "01")
        self.original(session, "09")
        self.original(session, "01")
        decision = session.interpreter.last_decision
        self.assertEqual(len(decision.context.history), 1)
        self.assertEqual(len(session.interpreter.context.history), 2)
        self.assertTrue(session.interpreter.verify_decision(decision, FIXTURES["01"]["input"]))
        with self.assertRaises(FrozenInstanceError):
            decision.context.pending_prompt = "changed"
        self.assertFalse(session.interpreter.verify_decision(
            replace(decision, context=D5DialogueContext()), FIXTURES["01"]["input"]))
        self.assertEqual(session.command("/confirm")["action"], "d5_complete")
        self.assertTrue(session.confirmed)
        self.assertEqual(session.backend.calls, 2)
        self.assertIsNone(session.engine.state.saved_version)

    def test_change_retains_history_invalidates_confirmation_and_replaces_candidate(self):
        session = self.session("01", "02")
        self.original(session, "01")
        session.command("/confirm")
        old_history = session.interpreter.context.history
        session.command("/change")
        self.assertEqual(session.interpreter.context.history, old_history)
        self.assertTrue(session.interpreter.context.correction_requested)
        answer = session.engine.state.answers["D5"]
        self.assertIsNone(answer.confirmed_version)
        self.assertIsNone(answer.selected_option_id)
        self.assertIsNone(answer.candidate_option_id)
        self.assertIsNone(session.engine._d5_receipt)
        self.assertEqual(session.backend.calls, 1)
        self.assertEqual(self.original(session, "02")["candidate_option_id"], "D5_MULTIPLE")
        supplied = strict_json(session.backend.requests[-1]["input"][0]["content"])
        self.assertTrue(supplied["dialogue_context"]["correction_requested"])
        self.assertFalse(session.interpreter.context.correction_requested)
        session.command("/confirm")
        self.assertEqual(session.engine.state.answers["D5"].selected_option_id, "D5_MULTIPLE")
        self.assertEqual(session.backend.calls, 2)

    def test_new_clears_history_and_old_answer(self):
        session = self.session("01", "02")
        self.original(session, "01")
        session.command("/confirm")
        old_interpreter = session.interpreter
        session.command("/new")
        self.assertIsNot(session.interpreter, old_interpreter)
        self.assertFalse(session.confirmed)
        self.assertEqual(session.interpreter.context.history, ())
        self.assertEqual(session.interpreter.context.pending_prompt, session.question)
        self.assertFalse(session.interpreter.context.correction_requested)
        self.assertIsNone(session.last_record)
        self.original(session, "02")
        supplied = strict_json(session.backend.requests[-1]["input"][0]["content"])
        self.assertEqual(supplied["dialogue_context"]["history"], [])

    def test_help_pause_paused_input_and_resume_make_no_calls_or_user_memory(self):
        session = self.session("09")
        self.original(session, "09")
        history = session.interpreter.context.history
        self.assertEqual(session.command("/help")["action"], "explain")
        self.assertEqual(session.command("/pause")["action"], "pause")
        self.assertEqual(self.original(session, "01")["action"], "paused")
        self.assertEqual(session.command("/resume")["action"], "resume")
        self.assertEqual(session.interpreter.context.history, history)
        self.assertEqual(session.backend.calls, 1)

    def test_existing_help_reply_is_not_sent_to_interpreter_or_remembered(self):
        session = self.session()
        result = self.original(session, "11")
        self.assertEqual(result["action"], "explain")
        self.assertEqual(session.backend.calls, 0)
        self.assertEqual(session.interpreter.context.history, ())

    def test_stop_clears_history_and_later_inputs_cannot_infer(self):
        session = self.session("09")
        self.original(session, "09")
        self.assertEqual(session.command("/stop")["action"], "stop")
        self.assertEqual(session.interpreter.context.history, ())
        self.assertEqual(self.original(session, "01")["action"], "stop")
        self.assertEqual(session.command("/resume")["action"], "stop")
        self.assertEqual(session.command("/change")["action"], "stop")
        self.assertEqual(session.backend.calls, 1)

    def test_existing_safety_input_clears_history_and_blocks_later_calls(self):
        session = self.session("09")
        self.original(session, "09")
        # Previously published safety example; no new safety wording bank.
        result = session.submit("I want to jump off the building.")
        self.assertEqual(result["action"], "safety_stop")
        self.assertEqual(session.interpreter.context.history, ())
        self.assertEqual(self.original(session, "01")["action"], "safety_stop")
        self.assertEqual(session.command("/resume")["action"], "safety_stop")
        self.assertEqual(session.command("/confirm")["action"], "safety_stop")
        self.assertEqual(session.backend.calls, 1)

    def test_turn_limit_preserves_whole_history_and_invalidates_stale_candidate(self):
        session = self.session("01")
        pair = (session.question, FIXTURES["09"]["input"])
        session.interpreter.context = D5DialogueContext((pair,) * (MAX_CONTEXT_TURNS - 1), session.question)
        self.original(session, "01")
        self.assertEqual(len(session.interpreter.context.history), MAX_CONTEXT_TURNS)
        before = session.interpreter.context.history
        result = self.original(session, "02")
        self.assertEqual(result["action"], "context_limit")
        self.assertEqual(session.interpreter.context.history, before)
        self.assertEqual(session.backend.calls, 1)
        self.assertIsNone(session.engine.state.answers["D5"].candidate_option_id)
        self.assertEqual(session.command("/confirm")["action"], "unresolved")

    def test_character_limit_rejects_without_call(self):
        session = self.session()
        session.interpreter.context = D5DialogueContext(pending_prompt="x" * MAX_CONTEXT_CHARS)
        result = self.original(session, "01")
        self.assertEqual(result["action"], "context_limit")
        self.assertEqual(session.backend.calls, 0)

    def test_context_requires_immutable_typed_turns(self):
        for context in (D5DialogueContext(history=[]),
                        D5DialogueContext(history=(["prompt", "reply"],)),
                        D5DialogueContext(history=(("prompt", ""),)),
                        D5DialogueContext(correction_requested="true")):
            with self.subTest(context=repr(context)):
                with self.assertRaises(D5SingleContractError):
                    context.validate(FIXTURES["01"]["input"])

    def test_transport_retains_interpretation_only_boundaries(self):
        context, _ = self.context_fixture()
        messages = build_messages(SPEC, "yes", context=context)
        payload = transport.request_payload(messages, output_schema())
        self.assertEqual(payload["model"], "gpt-6.1-sol")
        self.assertEqual(payload["reasoning"]["effort"], "low")
        self.assertEqual(payload["tools"], [])
        self.assertEqual(payload["tool_choice"], "none")
        self.assertIs(payload["store"], False)
        self.assertIs(payload["stream"], True)
        self.assertIs(payload["text"]["format"]["strict"], True)
        self.assertEqual(payload["instructions"], messages[0]["content"])
        self.assertEqual(len(payload["input"]), 1)
        self.assertEqual(strict_json(payload["input"][0]["content"])["dialogue_context"], context.as_dict())
        for key in ("conversation", "previous_response_id", "max_output_tokens"):
            self.assertNotIn(key, payload)
        self.assertEqual(transport.frozen.TIMEOUT_SECONDS, 30)
        self.assertEqual(transport.frozen.MAX_RESPONSE_BYTES, 1048576)
        self.assertEqual(len(SPEC.question_order), 15)

    def test_transport_rejects_unrecognised_context_fields(self):
        messages = build_messages(SPEC, FIXTURES["01"]["input"])
        data = strict_json(messages[1]["content"])
        data["dialogue_context"]["inferred_answer"] = "D5_MULTIPLE"
        messages[1]["content"] = canonical_json(data)
        with self.assertRaises(D5SingleContractError):
            transport.request_payload(messages, output_schema())

    def test_saved_live_conversation_with_repaired_current_meaning_playback(self):
        """Replay four already-recorded outputs; do not claim new live evidence."""
        session = self.session()
        session.backend.outputs = [row["raw_output"] for row in LIVE_FIXTURES]
        self.assertEqual(session.command("/help")["action"], "explain")

        def replay(number):
            source = LIVE_FIXTURES[number - 1]
            result = session.submit(source["input"])
            supplied = strict_json(session.backend.requests[-1]["input"][0]["content"])
            self.assertEqual(supplied["dialogue_context"], source["dialogue_context"])
            self.assertEqual(session.last_record["raw_output"], source["raw_output"])
            self.assertEqual(result["action"], source["result"]["action"])
            self.assertEqual(session.last_record["candidate"], source["candidate"])
            self.assertEqual(session.last_record["decision"]["outcome"], source["decision"]["outcome"])
            FIXED_PLAYBACK.append({"source_id": source["id"], "input": source["input"],
                "mode": "saved_output_replay_after_authored_playback_repair",
                "actual_model_calls": 0, "fixture_replays": 1,
                "raw_output_unchanged": True, "candidate": session.last_record["candidate"],
                "decision_outcome": session.last_record["decision"]["outcome"], "result": result})
            return result

        first = replay(1)
        self.assertEqual(first["bucket"], "Undecided")
        self.assertEqual(session.command("/pause")["action"], "pause")
        # Reuse a published reply while paused; its wording never reaches the model.
        self.assertEqual(self.original(session, "01")["action"], "paused")
        self.assertEqual(session.command("/resume")["action"], "resume")

        second = replay(2)
        self.assertEqual(second["candidate_option_id"], "D5_MULTIPLE")
        active = {fact["source_category"] for fact in session.last_record["raw"]["facts"]
                  if fact["pays_living_costs"] == "yes"}
        self.assertEqual(active, {"D5_SALARY", "D5_PENSION_PAYMENTS"})
        text = second["confirmation_text"]
        current, supporting = text.split("Supporting wording from this example:\n", 1)
        self.assertIn('Your latest reply: "Yes."', current)
        self.assertIn("Current funding categories: Salary or wages; Pension payments.", current)
        self.assertNotIn("I cannot tell", current)
        self.assertIn(json.dumps(LIVE_FIXTURES[0]["input"]), supporting)
        self.assertTrue(text.endswith("Have I understood correctly?"))
        self.assertEqual(session.command("/confirm")["action"], "d5_complete")
        session.command("/change")
        self.assertFalse(session.confirmed)
        self.assertIsNone(session.engine.state.answers["D5"].candidate_option_id)

        third = replay(3)
        self.assertEqual(third["candidate_option_id"], "D5_PENSION_PAYMENTS")
        text = third["confirmation_text"]
        current, supporting = text.split("Supporting wording from this example:\n", 1)
        self.assertIn("Current funding categories: Pension payments.", current)
        self.assertNotIn("Current funding categories: Salary", current)
        self.assertNotIn("I cannot tell", current)
        self.assertIn('Not counted as current funding, from your words:\n"My wages stay in savings."', supporting)
        self.assertEqual(session.command("/confirm")["action"], "d5_complete")
        self.assertEqual(session.engine.state.answers["D5"].selected_option_id, "D5_PENSION_PAYMENTS")
        session.command("/new")

        fourth = replay(4)
        self.assertEqual(fourth["action"], "clarify")
        self.assertEqual(fourth["clarification_topic"], "reply_unclear")
        self.assertEqual(session.last_record["raw"]["facts"], [])
        self.assertIsNone(session.last_record["candidate"])
        self.assertEqual(session.backend.calls, 4)
        self.assertEqual(session.backend.outputs, [])
        self.assertIsNone(session.engine.state.saved_version)


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed = []

    def addSuccess(self, test):
        self.passed.append(test.id())
        super().addSuccess(test)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="New evidence directory outside the repository")
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output.is_relative_to(ROOT):
        parser.error("Evidence must stay outside the repository")
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    log = io.StringIO()
    with patch.object(socket.socket, "connect", forbidden), \
            patch.object(socket, "create_connection", forbidden), \
            patch.object(transport.frozen, "_credentials", forbidden):
        result = unittest.TextTestRunner(stream=log, verbosity=2,
            resultclass=RecordedResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(ContextChecks))
    (output / "software-checks.log").write_text(log.getvalue())
    paths = [HERE / "session.py", HERE / "verify_context.py",
        *sorted((HERE / "runtime").rglob("*.py")),
        *sorted((HERE / "runtime/config").glob("*")),
        *(FIXTURE_ROOT / f"D5-STD-{identifier}.json" for identifier in FIXTURE_IDS),
        *(LIVE_FIXTURE_ROOT / f"CONTEXT-{number:02d}.json" for number in range(1, 5))]
    receipt = {"scope": "Offline context software checks; fixture replay is not model accuracy",
        "tests_run": result.testsRun, "passed": len(result.passed),
        "failures": [{"test": test.id(), "detail": detail} for test, detail in result.failures],
        "errors": [{"test": test.id(), "detail": detail} for test, detail in result.errors],
        "skipped": len(result.skipped), "success": result.wasSuccessful(),
        "actual_model_calls": 0, "authentication_calls": 0,
        "new_semantic_evaluation_cases": 0,
        "saved_output_ids": ["D5-STD-" + identifier for identifier in FIXTURE_IDS],
        "saved_context_output_ids": [row["id"] for row in LIVE_FIXTURES],
        "structural_fixtures_are_semantic_evidence": False,
        "passed_checks": result.passed,
        "sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in paths}}
    (output / "software-checks.json").write_text(json.dumps(receipt, indent=2) + "\n")
    (output / "fixed-playback.json").write_text(json.dumps({
        "scope": "Offline rendered results using exactly four previously completed live outputs",
        "actual_model_calls": 0, "authentication_calls": 0, "new_semantic_evaluation_cases": 0,
        "records": FIXED_PLAYBACK}, indent=2) + "\n")
    print(log.getvalue(), end="")
    print(f"Evidence: {output}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
