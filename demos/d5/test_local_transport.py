"""Offline transport checks using a fake pipe worker; no model or credentials."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from session import bootstrap
bootstrap()
from ai.d5_single_interpreter_contract_v2 import PROMPT_PATH, build_messages, output_schema
from ai.question_spec import BusinessSpec
import local_transport as transport
from local_worker import WorkerDependencyError, collect_generation, verify_dependencies


class LocalTransportChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="investwise-local-transport-")
        self.root = Path(self.directory.name)
        self.spec = BusinessSpec.load(Path(__file__).parent / "runtime/config/business-decision-spec.json")
        self.messages = build_messages(self.spec,
            "My wages stay in savings. My pension pays the bills.")
        self.schema = output_schema()
        self.backend = transport.LocalGenerator(self.root / "traces",
            worker_python=sys.executable, model_path=self.root)
        self.backend.case_id = "fixture_01"
        self.children = []

    def tearDown(self):
        self.backend.close()
        self.directory.cleanup()

    def fake_worker(self, *, ready_change=None, response_change=None, mode="normal"):
        ready = {"protocol": transport.PROTOCOL_VERSION, "status": "ready",
            "model": transport.MODEL_ID, "revision": transport.MODEL_REVISION,
            "model_files_sha256": transport.PINNED_MODEL_FILES,
            "offline": True, "trust_remote_code": False,
            "versions": transport.PINNED_WORKER_VERSIONS}
        ready.update(ready_change or {})
        source = "import json,sys,time\n"
        if mode == "startup_timeout":
            source += "time.sleep(5)\n"
        source += "print(" + repr(json.dumps(ready)) + ", flush=True)\n"
        source += "for line in sys.stdin:\n request=json.loads(line)\n"
        if mode == "generation_timeout":
            source += " time.sleep(5)\n"
        source += (" response={'protocol':1,'id':request['id'],'model':"
            + repr(transport.MODEL_ID) + ",'revision':" + repr(transport.MODEL_REVISION)
            + ",'status':'completed','finish_reason':'stop','text':'{}',"
            "'prompt_tokens':30,'generation_tokens':2}\n")
        source += " response.update(" + repr(response_change or {}) + ")\n"
        if mode == "malformed":
            source += " print('not json',flush=True)\n"
        elif mode == "truncated":
            source += " sys.stdout.write('{');sys.stdout.flush();sys.exit(0)\n"
        elif mode == "oversized":
            source += " print('x'*(1024*1024+1),flush=True)\n"
        elif mode == "stderr":
            source += " print('fixture-private-diagnostic',file=sys.stderr,flush=True)\n print(json.dumps(response),flush=True)\n"
        else:
            source += " print(json.dumps(response),flush=True)\n"
        real_popen = subprocess.Popen
        def launch(*args, **kwargs):
            child = real_popen([sys.executable, "-I", "-u", "-c", source], **kwargs)
            self.children.append(child)
            return child
        return patch.object(transport.subprocess, "Popen", side_effect=launch)

    def assert_stops(self, expected, **fake_options):
        with self.fake_worker(**fake_options):
            with self.assertRaises(transport.LocalTransportError) as caught:
                self.backend(self.messages, self.schema)
            self.assertEqual(caught.exception.code, expected)
            self.assertEqual(self.backend.last_call["failure_code"], expected)
            self.assertIsNotNone(self.children[-1].poll())
            attempted = self.backend.calls
            self.backend.case_id = "fixture_02"
            with self.assertRaises(transport.LocalTransportError) as repeated:
                self.backend(self.messages, self.schema)
            self.assertEqual(repeated.exception.code, "local_session_stopped_no_retry")
            self.assertEqual(self.backend.calls, attempted)
            self.assertEqual(len(self.children), 1)

    def test_preparation_preserves_prompt_and_user_data(self):
        original = deepcopy(self.messages)
        prepared = transport.prepare_messages(self.messages, self.schema)
        self.assertEqual(self.messages, original)
        self.assertEqual(prepared[1], original[1])
        self.assertTrue(prepared[0]["content"].startswith(PROMPT_PATH.read_text()))
        self.assertIn(transport._json(self.schema), prepared[0]["content"])
        self.assertIn('"source_use_unknown:D5_SALARY"', prepared[0]["content"])
        self.assertNotIn("tools", prepared[1])

    def test_preparation_rejects_changed_business_prompt_schema_or_context(self):
        changed = deepcopy(self.messages)
        changed[0]["content"] += "different"
        with self.assertRaises(ValueError):
            transport.prepare_messages(changed, self.schema)
        changed_schema = deepcopy(self.schema)
        changed_schema["additionalProperties"] = True
        with self.assertRaises(ValueError):
            transport.prepare_messages(self.messages, changed_schema)
        changed = deepcopy(self.messages)
        envelope = json.loads(changed[1]["content"])
        envelope["dialogue_context"]["history"] = [{"prompt": "", "reply": "x"}]
        changed[1]["content"] = json.dumps(envelope)
        with self.assertRaises(ValueError):
            transport.prepare_messages(changed, self.schema)

    def test_environment_omits_provider_credentials_and_proxies(self):
        with patch.dict(transport.os.environ, {"OPENAI_API_KEY": "fixture-secret",
                "HF_TOKEN": "fixture-hf", "HTTPS_PROXY": "fixture-proxy",
                "PYTHONPATH": "fixture-path"}):
            env = transport.worker_environment(self.root)
        self.assertNotIn("fixture", json.dumps(env))
        self.assertEqual(env["HF_HUB_OFFLINE"], "1")
        self.assertEqual(env["TRANSFORMERS_OFFLINE"], "1")
        self.assertEqual(env["HF_HUB_DISABLE_IMPLICIT_TOKEN"], "1")
        self.assertEqual(env["HF_TOKEN_PATH"], str(self.root.resolve() / ".worker-cache/absent-token"))

    def test_completed_output_reuses_worker_and_passes_raw_to_contract(self):
        with self.fake_worker(response_change={"text": "malformed model JSON"}):
            self.assertEqual(self.backend(self.messages, self.schema), "malformed model JSON")
            self.backend.case_id = "fixture_02"
            self.assertEqual(self.backend(self.messages, self.schema), "malformed model JSON")
        self.assertEqual(len(self.children), 1)
        self.assertEqual(self.backend.calls, 2)
        self.assertTrue(self.backend.last_call["terminal_completed"])
        self.assertFalse(self.backend.last_call["output_repair"])
        self.assertEqual(self.backend.last_call["actual_calls"], 1)

    def test_startup_timeout_kills_worker_without_model_call(self):
        with patch.object(transport, "LOAD_TIMEOUT", 0.05):
            self.assert_stops("worker_deadline_exceeded", mode="startup_timeout")
        self.assertEqual(self.backend.calls, 0)
        self.assertEqual(self.backend.last_call["stage"], "startup")

    def test_generation_timeout_kills_worker_and_cannot_retry(self):
        with patch.object(transport, "GENERATION_TIMEOUT", 0.05):
            self.assert_stops("worker_deadline_exceeded", mode="generation_timeout")
        self.assertEqual(self.backend.calls, 1)

    def test_wrong_ready_model_stops_before_call(self):
        for index, (change, expected) in enumerate((
                ({"model": "other"}, "worker_identity_or_load_rejected"),
                ({"versions": {}}, "worker_dependency_versions_mismatch"),
                ({"status": "failed", "code": "worker_dependency_versions_mismatch"},
                 "worker_dependency_versions_mismatch"))):
            with self.subTest(change=change):
                self.backend.close()
                self.backend = transport.LocalGenerator(self.root / str(index),
                    worker_python=sys.executable, model_path=self.root)
                self.backend.case_id = "fixture_01"
                self.children = []
                self.assert_stops(expected, ready_change=change)
                self.assertEqual(self.backend.calls, 0)
        with patch("local_worker.importlib.metadata.version", side_effect=lambda name:
                   transport.PINNED_WORKER_VERSIONS[name]):
            self.assertEqual(verify_dependencies(), transport.PINNED_WORKER_VERSIONS)
        with patch("local_worker.importlib.metadata.version", return_value="wrong"):
            with self.assertRaises(WorkerDependencyError):
                verify_dependencies()

    def test_wrong_response_model_is_rejected(self):
        self.assert_stops("worker_response_identity_rejected", response_change={"model": "other"})

    def test_length_completed_json_is_rejected(self):
        self.assert_stops("incomplete_or_nonpassive_local_output",
            response_change={"finish_reason": "length", "text": "{}"})

    def test_worker_failure_does_not_accept_prior_json(self):
        self.assert_stops("worker_generation_failed",
            response_change={"status": "failed", "text": "{}"})

    def test_tool_bearing_envelope_is_rejected(self):
        self.assert_stops("incomplete_or_nonpassive_local_output",
            response_change={"tool_calls": []})

    def test_truncated_worker_output_is_rejected(self):
        self.assert_stops("interrupted_worker_response", mode="truncated")

    def test_malformed_worker_json_is_rejected(self):
        self.assert_stops("malformed_worker_response", mode="malformed")

    def test_oversized_worker_output_is_rejected(self):
        self.assert_stops("worker_response_limit", mode="oversized")

    def test_worker_diagnostics_are_not_retained(self):
        with self.fake_worker(mode="stderr"):
            self.backend(self.messages, self.schema)
        self.assertGreater(self.backend.last_call["stderr_bytes_discarded"], 0)
        for path in (self.root / "traces").rglob("*.json"):
            self.assertNotIn("fixture-private-diagnostic", path.read_text())

    def test_stream_consumes_completion_and_rejects_late_errors(self):
        def event(text, reason):
            return SimpleNamespace(text=text, finish_reason=reason,
                prompt_tokens=30, generation_tokens=2)
        self.assertEqual(collect_generation(iter([event("{}", "stop")])), ("{}", 30, 2))
        def late_error():
            yield event("{}", "stop")
            raise RuntimeError("fixture error after parseable JSON")
        with self.assertRaises(RuntimeError):
            collect_generation(late_error())
        with self.assertRaises(ValueError):
            collect_generation(iter([event("{}", "length")]))
        with self.assertRaises(ValueError):
            collect_generation(iter([event("{}", None)]))
        with self.assertRaises(ValueError):
            collect_generation(iter([event("{}", "stop"), event("trailing", None)]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
