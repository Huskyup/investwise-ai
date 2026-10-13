"""One frozen ML + GPT round: existing preflight, eleven cases, conditional context."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from session import bootstrap, external_path, private_directory, write_json
bootstrap()
from local_evaluate import existing, frozen_files, no_changes, preflight, digest
from gpt_ml import GPTMLGenerator, GPTMLSession


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile-dir", type=Path,
                        default=Path.home() / ".config/investwise/d5-chatgpt-plan")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12) or os.name != "posix":
        parser.error("Use the existing Python 3.12 D5 environment on macOS or Linux.")
    os.umask(0o077)
    frozen = frozen_files()
    policy = json.loads(args.protocol.read_text())
    required = {"phase": "ml-gpt-existing", "model": "gpt-6.1-sol",
                "reasoning_effort": "low", "existing_examples": 11,
                "conditional_context_turns": 4, "preflight_calls": 1,
                "maximum_gpt_calls": 15, "retry": False,
                "labels_supplied_to_model": False}
    if (any(policy.get(k) != v for k, v in required.items())
            or policy.get("source_hashes") != frozen):
        parser.error("The separate frozen protocol does not match these sources and limits")
    output = private_directory(args.output)
    write_json(output / "started.json", {
        **required, "at_utc": datetime.now(timezone.utc).isoformat(),
        "hashes": frozen, "protocol_sha256": digest(args.protocol),
        "default_changed": False,
    })
    backend = None
    passed = preflight_passed = False
    failure = None
    try:
        from ai.d5_chatgpt_auth import ChatGPTCredentials
        credentials = ChatGPTCredentials(external_path(args.profile_dir))
        backend = GPTMLGenerator(output / "traces", credentials)
        preflight_passed = preflight(backend, output, backend_name="gpt")
        if preflight_passed:
            passed = existing(backend, output, complete_bank=True,
                              session_factory=GPTMLSession, backend_name="gpt")
    except Exception as error:
        # Exception strings and tracebacks can contain provider secrets.
        failure = {"type": type(error).__name__,
                   "safe_backend_receipt": dict(backend.last_call) if backend else None}
    preserved = no_changes(frozen)
    calls = backend.calls if backend else 0
    summary = {"phase": required["phase"],
               "passed": bool(passed and preserved and calls <= 15),
               "preflight_passed": preflight_passed,
               "files_unchanged": preserved, "actual_gpt_calls": calls,
               "failure": failure, "retry": False, "choice_recovery": 0}
    write_json(output / "execution.json", summary)
    if not summary["passed"]:
        write_json(output / "STOP.json", summary)
    print(json.dumps(summary))
    print("Private evidence:", output)
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
