"""Private JSONL worker: cached Qwen weights, passive text only, no network.

This process has no tools or action dispatcher. Its network guard prevents
accidental library requests; it is not presented as an operating-system sandbox.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import hashlib
import importlib.metadata
import json
from pathlib import Path
import socket
import sys

# -I excludes script-directory imports, so add only this application's own code.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from local_transport import (MAX_RESPONSE_BYTES, MAX_TOKENS, MODEL_ID,
    MODEL_REVISION, PINNED_MODEL_FILES, PINNED_WORKER_VERSIONS, PROTOCOL_VERSION, _strict_json)


def deny_network():
    original_socket = socket.socket
    class OfflineSocket(original_socket):
        def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None):
            if family in {socket.AF_INET, socket.AF_INET6}:
                raise RuntimeError("network_disabled")
            super().__init__(family, type, proto, fileno=fileno)
    def denied(*args, **kwargs):
        raise RuntimeError("network_disabled")
    socket.socket = OfflineSocket
    socket.create_connection = denied
    socket.getaddrinfo = denied


def verify_snapshot(path):
    """Hash every supplied model/tokeniser file before using its local contents."""
    if not path.is_dir() or {p.name for p in path.iterdir()} != set(PINNED_MODEL_FILES):
        raise ValueError("pinned_snapshot_files_required")
    for name, expected in PINNED_MODEL_FILES.items():
        with (path / name).open("rb") as handle:
            if hashlib.file_digest(handle, "sha256").hexdigest() != expected:
                raise ValueError("pinned_snapshot_hash_mismatch")


class WorkerDependencyError(RuntimeError):
    """The exact reviewed runtime must be installed before loading weights."""


def verify_dependencies():
    try:
        versions = {name: importlib.metadata.version(name) for name in PINNED_WORKER_VERSIONS}
    except importlib.metadata.PackageNotFoundError:
        raise WorkerDependencyError("worker_dependency_versions_mismatch") from None
    if versions != PINNED_WORKER_VERSIONS:
        raise WorkerDependencyError("worker_dependency_versions_mismatch")
    return versions


def collect_generation(stream):
    """Consume to exhaustion: parseable JSON before a late error is not success."""
    segments = []
    size = 0
    terminal = None
    for event in stream:
        if terminal is not None:
            raise ValueError("output_after_terminal")
        if not isinstance(event.text, str):
            raise ValueError("nontext_generation")
        size += len(event.text.encode("utf-8"))
        if size > MAX_RESPONSE_BYTES:
            raise ValueError("generation_size_limit")
        segments.append(event.text)
        if event.finish_reason is not None:
            terminal = event
    if terminal is None or terminal.finish_reason != "stop":
        raise ValueError("generation_not_eos_completed")
    return "".join(segments), terminal.prompt_tokens, terminal.generation_tokens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=Path, required=True)
    args = parser.parse_args()
    output = sys.stdout
    def send(value):
        output.write(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n")
        output.flush()
    deny_network()
    try:
        versions = verify_dependencies()
        verify_snapshot(args.model_path)
        # Progress and incidental library output cannot become protocol content.
        with redirect_stdout(sys.stderr):
            from mlx_lm import load, stream_generate
            from mlx_lm.sample_utils import make_sampler
            model, tokenizer = load(str(args.model_path), lazy=False,
                tokenizer_config={"trust_remote_code": False, "local_files_only": True},
                trust_remote_code=False)
        send({"protocol": PROTOCOL_VERSION, "status": "ready", "model": MODEL_ID,
              "revision": MODEL_REVISION, "model_files_sha256": PINNED_MODEL_FILES,
              "offline": True, "trust_remote_code": False, "versions": versions})
    except WorkerDependencyError:
        send({"protocol": PROTOCOL_VERSION, "status": "failed",
              "code": "worker_dependency_versions_mismatch"})
        return 1
    except Exception:
        send({"protocol": PROTOCOL_VERSION, "status": "failed", "code": "local_load_failed"})
        return 1
    while True:
        line = sys.stdin.buffer.readline(MAX_RESPONSE_BYTES + 1)
        if not line:
            return 0
        identity = None
        try:
            if len(line) > MAX_RESPONSE_BYTES or not line.endswith(b"\n"):
                raise ValueError("bounded_request_required")
            request = _strict_json(line.decode("utf-8"))
            if (not isinstance(request, dict) or set(request) != {
                    "protocol", "id", "messages", "max_tokens", "temperature"}
                    or request["protocol"] != PROTOCOL_VERSION
                    or not isinstance(request["id"], str)
                    or request["max_tokens"] != MAX_TOKENS
                    or request["temperature"] != 0.0):
                raise ValueError("invalid_worker_request")
            identity = request["id"]
            with redirect_stdout(sys.stderr):
                prompt = tokenizer.apply_chat_template(request["messages"],
                    tokenize=False, add_generation_prompt=True)
                # No prompt cache is passed: generate_step allocates a new cache
                # for each request. Only the already-loaded weights are reused.
                stream = stream_generate(model, tokenizer, prompt=prompt,
                    max_tokens=MAX_TOKENS, sampler=make_sampler(temp=0.0),
                    prompt_cache=None)
                try:
                    text, prompt_tokens, generation_tokens = collect_generation(stream)
                finally:
                    stream.close()
            send({"protocol": PROTOCOL_VERSION, "id": identity, "model": MODEL_ID,
                  "revision": MODEL_REVISION, "status": "completed", "finish_reason": "stop",
                  "text": text, "prompt_tokens": prompt_tokens,
                  "generation_tokens": generation_tokens})
        except Exception:
            send({"protocol": PROTOCOL_VERSION, "id": identity, "model": MODEL_ID,
                  "revision": MODEL_REVISION, "status": "failed", "code": "local_generation_failed"})
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
