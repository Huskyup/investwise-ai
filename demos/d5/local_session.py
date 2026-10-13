"""Separate combined D5 session; the working direct-GPT entry point is unchanged."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import uuid

from session import (D5Session, DemoStopped, HERE, NoOtherQuestions, NoProfileSave,
                     REPOSITORY, RUNTIME, bootstrap, write_json)

bootstrap()

from ai.d5_single_interpreter_contract_v2 import D5DialogueContext, D5SingleInterpreter
from ai.llm_shadow import strict_json
from ai.question_spec import BusinessSpec
from local_engine import LocalD5Engine, digest


def load_baseline(spec):
    """Load byte-recorded baseline code and unchanged data without path mixing.

    The existing baseline fits deterministically from train/calibration on
    startup. This uses its original procedure, without tuning or writing model
    weights; test.csv and supplemental D5 data are never read.
    """
    manifest = json.loads((HERE / "baseline-ml-manifest.json").read_text())
    for relative, expected in manifest["files"].items():
        path = REPOSITORY / relative
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise DemoStopped("The recorded ML baseline has changed; no substitution")
    if (REPOSITORY / manifest["snapshot_origin"]).read_bytes() != (HERE / "baseline_ml.py").read_bytes():
        raise DemoStopped("The ML snapshot is not the unchanged main predictor")
    baseline_spec = BusinessSpec.load(REPOSITORY / manifest["baseline_spec"])
    option_ids = lambda value: tuple((qid, tuple(option.id for option in value.question(qid).options))
                                    for qid in value.question_order)
    if option_ids(baseline_spec) != option_ids(spec):
        raise DemoStopped("The unchanged fifteen-question option sets are required")
    # This unique module name retains the byte-exact main implementation while
    # imports of conformal/text classifiers resolve to byte-identical packaged
    # dependencies. It never replaces the older runtime ai.all_question_ml.
    from baseline_ml import build_all_question_ml_resolver
    resolver = build_all_question_ml_resolver(
        baseline_spec, REPOSITORY / manifest["data_directory"])
    return resolver, digest(manifest)


class LocalD5Session(D5Session):
    """Same terminal actions, with separate ML and named-backend audit counts."""
    def __init__(self, backend, output_dir, ml_resolver=None, *, backend_name="qwen"):
        if backend_name not in {"qwen", "gpt"}:
            raise ValueError("Unsupported D5 interpretation backend")
        self.backend_name = backend_name
        self.backend_calls_key = f"{backend_name}_calls"
        self.output_dir = Path(output_dir)
        self.spec = BusinessSpec.load(RUNTIME / "config/business-decision-spec.json")
        if len(self.spec.question_order) != 15:
            raise DemoStopped("The unchanged fifteen-question specification is required")
        if ml_resolver is None:
            self.ml_resolver, self.ml_identity = load_baseline(self.spec)
        else:
            self.ml_resolver = ml_resolver
            self.ml_identity = "injected_offline_ml_fixture"
        self.backend = backend
        self.failed = False
        self.sequence = 0
        self.last_record = None
        self._ml_calls_finished = 0
        self.new_example()

    @property
    def ml_calls(self):
        return self._ml_calls_finished + self.engine.ml_calls

    def new_example(self):
        if self.failed:
            raise DemoStopped("The session stopped after a failure; no automatic retry")
        if hasattr(self, "engine"):
            self._ml_calls_finished += self.engine.ml_calls
        self.captured = {}
        self.last_record = None

        def generate(messages, schema):
            raw = self.backend(messages, schema)
            self.captured["raw_output"] = raw
            return raw

        self.interpreter = D5SingleInterpreter(self.spec, generate,
                                              model_metadata=dict(self.backend.metadata))
        self.engine = LocalD5Engine(self.spec, ml_resolver=self.ml_resolver,
            ml_identity=self.ml_identity, d5_interpreter=self.interpreter,
            question_resolver=NoOtherQuestions(), store=NoProfileSave(),
            backend_name=self.backend_name)
        self.engine.state.current_index = self.spec.question_order.index("D5")
        self.interpreter.context = D5DialogueContext(pending_prompt=self.question)

    def submit(self, text, *, case_id=None):
        if self.failed:
            raise DemoStopped("The session has stopped")
        if self.confirmed or self.engine.state.current_question_id != "D5":
            return {"action": "d5_complete", "message":
                "D5 has ended. Use /change, /new or /exit; no other question will be interpreted."}
        self.sequence += 1
        identifier = case_id or f"reply-{self.sequence:04d}-{uuid.uuid4().hex[:8]}"
        self.backend.case_id = identifier
        self.backend.last_call = {}
        self.captured.clear()
        before_llm, before_ml = self.backend.calls, self.ml_calls
        context = self.interpreter.context
        try:
            result = self.engine.submit_answer(text)
        except Exception:
            self.failed = True
            write_json(self.output_dir / f"{identifier}-failure.json", {
                "case_id": identifier, self.backend_calls_key: self.backend.calls - before_llm,
                "actual_model_calls": self.backend.calls - before_llm,
                "ml_calls": self.ml_calls - before_ml,
                "safe_backend_receipt": dict(self.backend.last_call), "retry": False})
            location = "local" if self.backend_name == "qwen" else "GPT"
            raise DemoStopped(f"D5 stopped after a {location} runtime failure; no retry or fallback") from None
        llm_calls, ml_calls = self.backend.calls - before_llm, self.ml_calls - before_ml
        if llm_calls not in {0, 1} or ml_calls not in {0, 1}:
            self.failed = True
            raise DemoStopped("The one-call-per-route boundary was exceeded")
        raw = self.captured.get("raw_output")
        interpreted = self.engine.interpreted_reply
        if interpreted:
            self._remember_reply(text, result, context)
        if result.get("action") in {"stop", "safety_stop"}:
            self.interpreter.context = D5DialogueContext()
        elif not interpreted:
            self._remember_prompt(result)
        try:
            parsed = strict_json(raw) if raw is not None else None
        except ValueError:
            parsed = None
        decision = self.interpreter.last_decision
        answer = self.engine.state.answers["D5"]
        self.last_record = {
            "id": identifier, "input": text, "route": self.engine.last_route,
            "ml_calls": ml_calls, self.backend_calls_key: llm_calls,
            "actual_model_calls": llm_calls, "ml_evidence": self.engine.last_ml_evidence,
            "raw": parsed, "raw_output": raw,
            "dialogue_context": context.as_dict() if interpreted else None,
            "result": result,
            "decision": decision.as_dict() if decision and raw is not None else None,
            "backend_call": dict(self.backend.last_call),
            "candidate": answer.candidate_option_id, "selected": answer.selected_option_id,
            "confirmed_version": answer.confirmed_version,
            "saved_version": self.engine.state.saved_version, "answer_source": answer.source,
        }
        write_json(self.output_dir / f"{identifier}.json", self.last_record)
        return result


# Short public name for callers which already distinguish the D5 module.
LocalSession = LocalD5Session
