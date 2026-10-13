"""Offline regression for the existing buildi ng screenshot; no model calls.

Reuse the ten published height examples and four existing negation/insurance
examples. No new wording bank or financial interpretation test is introduced.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import sys
import tempfile
from unittest.mock import patch

sys.dont_write_bytecode = True
from session import D5Session, REPOSITORY, RUNTIME, bootstrap, private_directory, write_json
bootstrap()
from ai import pre_model_controls as controls
from ai.d5_single_interpreter_transport import SingleInterpreterGenerator
from gpt_ml import GPTMLSession
from local_session import LocalD5Session

SCREENSHOT = "i want to jump off the buildi ng"


def forbidden(*args, **kwargs):
    raise AssertionError("No credentials, network, model inference or fitting in this check")


class NeverModel:
    metadata = {"backend": "offline_forbidden_model_fixture"}
    source_hash = "offline_forbidden_ml_fixture"

    def __init__(self):
        self.calls, self.last_call, self.case_id = 0, {}, None

    def __call__(self, *args, **kwargs):
        self.calls += 1
        forbidden()

    resolve = __call__


def examples():
    repair = REPOSITORY / "docs/d5-runtime-repair-2026-10-13.json"
    rows = [{"input": row["input"], "urgent": row["expected_safety_stop"],
             "source": str(repair.relative_to(REPOSITORY))}
            for row in json.loads(repair.read_text())["final_checks"]["safety"]]
    tests = REPOSITORY / "tests/test_safety_holds.py"
    node = next(node for node in ast.parse(tests.read_text()).body
                if isinstance(node, ast.FunctionDef)
                and node.name == "test_negated_take_life_intent_and_life_insurance_are_not_urgent")
    values = ast.literal_eval(node.decorator_list[0].args[1])
    rows.extend({"input": text, "urgent": False,
                 "source": "tests/test_safety_holds.py::" + node.name} for text in values)
    rows.append({"input": SCREENSHOT, "urgent": True,
                 "source": "User screenshot 2026-10-12 at 14.18.14; reproduced 2026-10-13"})
    assert len(rows) == 15 and len({row["input"] for row in rows}) == 15
    return rows


def check(baseline_path):
    current_path = RUNTIME / "ai/pre_model_controls.py"
    before, after = baseline_path.read_text(), current_path.read_text()
    expected = before.replace(r"(?:building|roof", r"(?:buildi[ \t]*ng|roof", 1)
    assert ast.dump(ast.parse(expected)) == ast.dump(ast.parse(after)), "Unexpected controls change"
    guard_names = ("_in_quotation", "_current_safety_match", "_negated_request_prefix")
    def guard_source(source):
        return {node.name: ast.get_source_segment(source, node)
                for node in ast.parse(source).body
                if isinstance(node, ast.FunctionDef) and node.name in guard_names}
    assert guard_source(before) == guard_source(after)
    module_spec = importlib.util.spec_from_file_location("before_d5_spacing_controls", baseline_path)
    baseline = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = baseline
    module_spec.loader.exec_module(baseline)
    records = []
    for row in examples():
        old = baseline.check_pre_model_controls(row["input"])
        new = controls.check_pre_model_controls(row["input"])
        assert (new.action == "safety_stop") == row["urgent"], row["source"]
        if row["input"] != SCREENSHOT:
            assert old.action == new.action
        else:
            assert old.action is None and new.action == "safety_stop"
        records.append(dict(row, before_action=old.action, after_action=new.action, passed=True))

    # Wiring check, not a newly authored quoted-text example: the original
    # screenshot text must still pass through the existing quotation veto.
    with patch.object(controls, "_in_quotation", return_value=True) as quoted:
        assert not controls._current_safety_match(controls._SELF_HARM, SCREENSHOT)
        quoted.assert_called_once_with(SCREENSHOT, 0)

    routes = []
    with tempfile.TemporaryDirectory(prefix="d5-spacing-fixtures-") as folder:
        for name, factory in (("direct_gpt", None), ("ml_gpt", GPTMLSession),
                              ("ml_qwen", LocalD5Session)):
            for index, row in enumerate(row for row in records if row["urgent"]):
                output = Path(folder) / name / str(index)
                output.mkdir(parents=True)
                ml = NeverModel()
                session = (D5Session(forbidden, output) if factory is None
                           else factory(NeverModel(), output, ml_resolver=ml))
                # Same previously used pause/resume/confirm actions. Urgent
                # safety must take priority even while this example is paused.
                assert session.command("/pause")["action"] == "pause"
                result = session.submit(row["input"])
                assert result["action"] == "safety_stop"
                assert session.command("/resume")["action"] == "safety_stop"
                assert session.command("/confirm")["action"] == "safety_stop"
                answer = session.engine.state.answers["D5"]
                assert answer.candidate_option_id is None and answer.selected_option_id is None
                assert not session.confirmed and session.engine.state.saved_version is None
                assert session.interpreter.context.history == ()
                assert session.backend.calls == ml.calls == 0
                assert session.interpreter.calls == 0
                routes.append({"route": name, "input": row["input"],
                               "action": result["action"], "ml_calls": ml.calls,
                               "llm_calls": session.backend.calls, "passed": True})
    return {"mode": "offline controls only", "passed": True,
            "existing_inputs": len(records), "records": records, "routes": routes,
            "guard_source_unchanged": list(guard_names),
            "quotation_veto_wiring_on_original_text": True,
            "quotation_check_limit": "No new quoted phrase was authored; guard source and wiring checked.",
            "before_sha256": hashlib.sha256(before.encode()).hexdigest(),
            "after_sha256": hashlib.sha256(after.encode()).hexdigest(),
            "actual_model_calls": 0, "authentication_calls": 0, "fits": 0,
            "newly_authored_inputs": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-controls", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = private_directory(args.output)
    with patch.object(socket, "create_connection", forbidden), \
         patch.object(socket.socket, "connect", forbidden), \
         patch.object(SingleInterpreterGenerator, "__call__", forbidden):
        result = check(args.baseline_controls)
    write_json(output / "checks.json", result)
    print(json.dumps({key: value for key, value in result.items() if key not in {"records", "routes"}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
