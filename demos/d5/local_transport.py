"""Bounded, offline Qwen worker transport for the opt-in D5 example.

The schema is included in the prompt, not enforced by a constrained decoder.
The caller still applies the unchanged passive-output business contract.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import subprocess
import time


HERE = Path(__file__).resolve().parent
MODEL_ID = "mlx-community/Qwen3-4B-Instruct-2507-4bit"
MODEL_REVISION = "50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b"
DEFAULT_MODEL_PATH = (Path.home() / ".cache/huggingface/hub"
    / "models--mlx-community--Qwen3-4B-Instruct-2507-4bit/snapshots" / MODEL_REVISION)
DEFAULT_WORKER_PYTHON = (Path.home()
    / ".workbuddy/binaries/python/envs/default/bin/python")
MAX_TOKENS = 2048
MAX_RESPONSE_BYTES = 1024 * 1024
LOAD_TIMEOUT = 60.0
GENERATION_TIMEOUT = 30.0
PROTOCOL_VERSION = 1
PINNED_WORKER_VERSIONS = {
    "mlx": "0.32.3", "mlx-lm": "0.32.0",
    "transformers": "5.19.0", "tokenizers": "0.23.3",
}
BUSINESS_PROMPT_SHA256 = "474f95b7bdbf2dd5b0b2f3ea499b7eab1a06a588ab592c51f9045a1706b7c003"
LOCAL_CATEGORY_INSTRUCTION = (
    "LOCAL CATEGORY CONSISTENCY. For a complete Clarity answer with all relevant "
    "funding relations established, select option_id from the distinct source_category "
    "values in your facts where owner is self, time is current and pays_living_costs "
    "is yes. One such category requires that same category as option_id; two or more "
    "require D5_MULTIPLE. Count categories, not jobs, employers, payers or accounts. "
    "Excluded sources do not count. No active category does not by itself establish "
    "D5_NO_REGULAR: retain the existing explicit-absence, incomplete-answer and "
    "uncertainty instructions. The category count does not establish completeness "
    "or change Undecided, Confusion or abstention handling. "
    "Do not invent, alter or omit supported facts to make "
    "them fit an option. Return only the same required JSON object."
)
PINNED_MODEL_FILES = {
    "added_tokens.json": "c0284b582e14987fbd3d5a2cb2bd139084371ed9acbae488829a1c900833c680",
    "chat_template.jinja": "40c21f34cf67d8c760ef72f8ad3ae5afad514299d4b06e91dd9a8d705af7b541",
    "config.json": "574349e5a343236546fda55e4744a76e181f534182d7dc60ff1bad7e7a502849",
    "generation_config.json": "835fffe355c9438e7a25be099b3fccaa98350b83451f9fd2d99512e74f1ade48",
    "merges.txt": "8831e4f1a044471340f7c0a83d7bd71306a5b867e95fd870f74d0c5308a904d5",
    "model.safetensors": "2a73c6c248601ab904e035548abd8e6abb65ea27dcb5f342fb0a8910eb44173f",
    "model.safetensors.index.json": "388d811b8b7c2608dd04cce1bcb04a8bf715d19b42790894e6d3427ff429a777",
    "special_tokens_map.json": "76862e765266b85aa9459767e33cbaf13970f327a0e88d1c65846c2ddd3a1ecd",
    "tokenizer.json": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4",
    "tokenizer_config.json": "4397cc477eb6d79715ccd2000accd6b3531928f30029665832fa1b255f24d2b9",
    "vocab.json": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910",
}


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False)


def _sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _strict_json(value):
    def pairs(items):
        result = {}
        for key, item in items:
            if key in result:
                raise ValueError("duplicate_key")
            result[key] = item
        return result
    def invalid(_):
        raise ValueError("nonfinite_json")
    return json.loads(value, object_pairs_hook=pairs, parse_constant=invalid)


def prepare_messages(messages, schema):
    """Preserve shared instructions/data; append local format and consistency guidance."""
    from ai.d5_single_interpreter_contract_v2 import (
        D5DialogueContext, MISSING_TOPICS, output_schema)
    from ai.d5_puzzle_interpreter import D5_OPTION_IDS
    if _json(schema) != _json(output_schema()):
        raise ValueError("unchanged_d5_schema_required")
    if (not isinstance(messages, list) or len(messages) != 2
            or any(not isinstance(message, dict)
                   or set(message) != {"role", "content"} for message in messages)
            or [message["role"] for message in messages] != ["system", "user"]
            or any(not isinstance(message["content"], str) for message in messages)
            or _sha(messages[0]["content"]) != BUSINESS_PROMPT_SHA256):
        raise ValueError("unchanged_business_instructions_required")
    data = _strict_json(messages[1]["content"])
    if (not isinstance(data, dict) or set(data) != {
            "current_question", "allowed_options", "original_reply", "dialogue_context"}
            or not isinstance(data["current_question"], dict)
            or set(data["current_question"]) != {"id", "text"}
            or data["current_question"]["id"] != "D5"
            or not isinstance(data["current_question"]["text"], str)
            or not isinstance(data["allowed_options"], list)
            or any(not isinstance(option, dict)
                   or set(option) != {"id", "label", "definition"}
                   or any(not isinstance(value, str) for value in option.values())
                   for option in data["allowed_options"])
            or {option["id"] for option in data["allowed_options"]} != D5_OPTION_IDS
            or len(data["allowed_options"]) != len(D5_OPTION_IDS)):
        raise ValueError("d5_input_envelope_required")
    D5DialogueContext.from_dict(data["dialogue_context"]).validate(data["original_reply"])
    prepared = deepcopy(messages)
    prepared[0]["content"] += (
        "\n\nLOCAL OUTPUT FORMAT. Return one JSON object only, without Markdown fences. "
        "Use the exact property names, JSON types and enum values in this schema. "
        "In particular pays_living_costs is a string, not a boolean. "
        "The schema is a prompt instruction; the application validates the output independently.\n"
        + _json(schema)
        + "\nThe only permitted missing_information items are: "
        + _json(sorted(MISSING_TOPICS))
        + "\n\n" + LOCAL_CATEGORY_INSTRUCTION)
    return prepared


def worker_environment(output_dir):
    """Allowlist a child environment; never copy provider tokens or proxy settings."""
    cache = Path(output_dir).resolve() / ".worker-cache"
    return {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "LANG": "en_US.UTF-8", "LC_ALL": "en_US.UTF-8",
        "HF_HOME": str(cache), "HF_TOKEN_PATH": str(cache / "absent-token"),
        "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
        "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1", "HF_HUB_DISABLE_TELEMETRY": "1",
        "TOKENIZERS_PARALLELISM": "false", "DO_NOT_TRACK": "1",
    }


class LocalTransportError(RuntimeError):
    """Only fixed error codes are exposed; never arbitrary worker/provider text."""

    def __init__(self, code, *, stage=None):
        self.code = code
        self.stage = stage
        super().__init__("Local D5 worker stopped; no retry")


def _write_json(path, value):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(_json(value) + "\n")


class LocalGenerator:
    def __init__(self, output_dir, worker_python=None, model_path=None):
        self.trace_root = Path(output_dir).expanduser().absolute()
        if self.trace_root.resolve().is_relative_to(HERE.parents[1]):
            raise ValueError("session_output_must_be_outside_repository")
        self.worker_python = Path(worker_python or DEFAULT_WORKER_PYTHON).expanduser().absolute()
        self.model_path = Path(model_path or DEFAULT_MODEL_PATH).expanduser().absolute()
        self.calls = 0
        self.case_id = None
        self.last_call = {}
        self._process = None
        self._selector = None
        self._buffer = bytearray()
        self._stderr_bytes = 0
        self._halted = False
        self._worker_metadata = None

    @property
    def metadata(self):
        return {
            "backend": "local_qwen_mlx_offline", "model": MODEL_ID,
            "revision": MODEL_REVISION, "temperature": 0.0,
            "max_tokens": MAX_TOKENS, "tools": [], "tool_choice": "none",
            "store": False, "network": False, "trust_remote_code": False,
            "constrained_decoder": False, "fresh_generation_cache": True,
            "local_format_policy": "unchanged_business_prompt_plus_schema_topics_category_consistency_v2",
            "local_category_instruction_sha256": _sha(LOCAL_CATEGORY_INSTRUCTION),
            "model_files_sha256": dict(PINNED_MODEL_FILES),
            "required_worker_versions": dict(PINNED_WORKER_VERSIONS),
            "business_prompt_sha256": BUSINESS_PROMPT_SHA256,
            "transport_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "worker_sha256": hashlib.sha256((HERE / "local_worker.py").read_bytes()).hexdigest(),
        }

    def _stop(self):
        if self._process is not None:
            if self._process.poll() is None:
                self._process.kill()
            try:
                self._process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                pass
            for pipe in (self._process.stdin, self._process.stdout, self._process.stderr):
                if pipe is not None:
                    pipe.close()
        if self._selector is not None:
            self._selector.close()
        self._process = None
        self._selector = None
        self._buffer.clear()

    def close(self):
        self._halted = True
        self._stop()

    def _read(self, deadline):
        total = len(self._buffer)
        while True:
            if b"\n" in self._buffer:
                line, remaining = bytes(self._buffer).split(b"\n", 1)
                self._buffer[:] = remaining
                if remaining:
                    raise LocalTransportError("unexpected_extra_worker_output")
                try:
                    result = _strict_json(line.decode("utf-8"))
                except (ValueError, UnicodeError):
                    raise LocalTransportError("malformed_worker_response") from None
                if not isinstance(result, dict):
                    raise LocalTransportError("malformed_worker_response")
                return result
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise LocalTransportError("worker_deadline_exceeded")
            events = self._selector.select(remaining)
            if not events:
                raise LocalTransportError("worker_deadline_exceeded")
            for key, _ in events:
                chunk = os.read(key.fd, 65536)
                if key.data == "stderr":
                    self._stderr_bytes += len(chunk)
                    if self._stderr_bytes > MAX_RESPONSE_BYTES:
                        raise LocalTransportError("worker_diagnostic_limit")
                    if not chunk:
                        self._selector.unregister(key.fileobj)
                    continue
                if not chunk:
                    raise LocalTransportError("interrupted_worker_response")
                total += len(chunk)
                if total > MAX_RESPONSE_BYTES:
                    raise LocalTransportError("worker_response_limit")
                self._buffer.extend(chunk)

    def _send(self, payload, deadline):
        encoded = (_json(payload) + "\n").encode("utf-8")
        if len(encoded) > MAX_RESPONSE_BYTES:
            raise LocalTransportError("worker_request_limit")
        # Requests can exceed pipe capacity. A nonblocking write shares the same
        # whole-request deadline as generation; it cannot hang before the timer.
        pipe = self._process.stdin
        descriptor = pipe.fileno()
        os.set_blocking(descriptor, False)
        with selectors.DefaultSelector() as writable:
            writable.register(descriptor, selectors.EVENT_WRITE)
            position = 0
            while position < len(encoded):
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not writable.select(remaining):
                    raise LocalTransportError("worker_deadline_exceeded")
                try:
                    position += os.write(descriptor, encoded[position:])
                except BlockingIOError:
                    continue

    def _ensure_worker(self):
        if self._process is not None:
            return
        if not self.worker_python.is_file() or not self.model_path.is_dir():
            raise LocalTransportError("local_dependencies_or_snapshot_missing")
        deadline = time.monotonic() + LOAD_TIMEOUT
        self._process = subprocess.Popen(
            [str(self.worker_python), "-I", "-u", str(HERE / "local_worker.py"),
             "--model-path", str(self.model_path)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=worker_environment(self.trace_root), cwd=str(HERE), bufsize=0,
            start_new_session=True)
        self._selector = selectors.DefaultSelector()
        self._selector.register(self._process.stdout, selectors.EVENT_READ, "stdout")
        self._selector.register(self._process.stderr, selectors.EVENT_READ, "stderr")
        ready = self._read(deadline)
        if (ready.get("status") == "failed"
                and ready.get("code") == "worker_dependency_versions_mismatch"):
            raise LocalTransportError("worker_dependency_versions_mismatch")
        if (ready.get("status") != "ready" or ready.get("protocol") != PROTOCOL_VERSION
                or ready.get("model") != MODEL_ID or ready.get("revision") != MODEL_REVISION
                or ready.get("model_files_sha256") != PINNED_MODEL_FILES
                or ready.get("offline") is not True or ready.get("trust_remote_code") is not False):
            raise LocalTransportError("worker_identity_or_load_rejected")
        if ready.get("versions") != PINNED_WORKER_VERSIONS:
            raise LocalTransportError("worker_dependency_versions_mismatch")
        self._worker_metadata = ready

    def __call__(self, messages, schema):
        if self._halted:
            raise LocalTransportError("local_session_stopped_no_retry")
        if not isinstance(self.case_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", self.case_id):
            raise ValueError("unique_safe_case_id_required")
        prepared = prepare_messages(messages, schema)
        self.trace_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        target = self.trace_root / self.case_id
        target.mkdir(mode=0o700, exist_ok=False)
        data = _strict_json(messages[1]["content"])
        self.last_call = {
            **self.metadata, "actual_calls": 0, "retry": False,
            "output_repair": False, "blocked": False, "status": "starting",
            "terminal_completed": False, "max_response_bytes": MAX_RESPONSE_BYTES,
            "load_timeout_seconds": LOAD_TIMEOUT,
            "generation_timeout_seconds": GENERATION_TIMEOUT,
            "previous_reply_count": len(data["dialogue_context"]["history"]),
            "request_sha256": _sha(_json(prepared)),
            "schema_sha256": _sha(_json(schema)),
        }
        started = time.monotonic()
        stage = "startup"
        try:
            _write_json(target / "request.json", {"messages": prepared, "schema": schema})
            self._ensure_worker()
            self.last_call["worker_metadata"] = self._worker_metadata
            stage = "generation"
            deadline = time.monotonic() + GENERATION_TIMEOUT
            self.calls += 1
            self.last_call.update(actual_calls=1, status="generating")
            self._send({"protocol": PROTOCOL_VERSION, "id": self.case_id,
                        "messages": prepared, "max_tokens": MAX_TOKENS,
                        "temperature": 0.0}, deadline)
            response = self._read(deadline)
            stage = "protocol"
            if time.monotonic() >= deadline:
                raise LocalTransportError("worker_deadline_exceeded")
            if (response.get("protocol") != PROTOCOL_VERSION
                    or response.get("id") != self.case_id
                    or response.get("model") != MODEL_ID
                    or response.get("revision") != MODEL_REVISION):
                raise LocalTransportError("worker_response_identity_rejected")
            if response.get("status") != "completed":
                raise LocalTransportError("worker_generation_failed")
            if (set(response) != {"protocol", "id", "model", "revision", "status",
                                  "finish_reason", "text", "prompt_tokens", "generation_tokens"}
                    or response["finish_reason"] != "stop"
                    or not isinstance(response["text"], str) or not response["text"].strip()
                    or type(response["prompt_tokens"]) is not int or response["prompt_tokens"] < 1
                    or type(response["generation_tokens"]) is not int
                    or not 0 < response["generation_tokens"] <= MAX_TOKENS):
                raise LocalTransportError("incomplete_or_nonpassive_local_output")
            _write_json(target / "response.json", response)
            self.last_call.update(status="completed", terminal_completed=True,
                finish_reason="stop", provider_model=MODEL_ID,
                usage={"input_tokens": response["prompt_tokens"],
                       "output_tokens": response["generation_tokens"]})
            return response["text"]
        except Exception as exc:
            self._halted = True
            code = exc.code if isinstance(exc, LocalTransportError) else "local_runtime_failure"
            self.last_call.update(blocked=True, status="stopped", failure_code=code, stage=stage)
            self._stop()
            raise LocalTransportError(code, stage=stage) from None
        finally:
            self.last_call["elapsed_seconds"] = time.monotonic() - started
            self.last_call["stderr_bytes_discarded"] = self._stderr_bytes
            _write_json(target / "receipt.json", self.last_call)
