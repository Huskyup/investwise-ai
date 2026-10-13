#!/usr/bin/env python3
"""Manually launch unchanged ML + GPT-6.1 Sol low for the D5 example."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
import uuid

sys.dont_write_bytecode = True
from session import DemoStopped, bootstrap, external_path, private_directory, render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["chat"])
    parser.add_argument("--profile-dir", type=Path,
                        default=Path.home() / ".config/investwise/d5-chatgpt-plan")
    parser.add_argument("--output-dir", type=Path,
                        help="New private session directory outside the repository")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12) or os.name != "posix":
        parser.error("Use the existing Python 3.12 D5 environment on macOS or Linux.")
    os.umask(0o077)
    bootstrap()
    from ai.d5_chatgpt_auth import AuthBlocked, ChatGPTCredentials
    from gpt_ml import GPTMLGenerator, GPTMLSession
    try:
        credentials = ChatGPTCredentials(external_path(args.profile_dir))
        output = private_directory(args.output_dir or (
            Path.home() / ".local/state/investwise/d5-ml-gpt-demo" /
            (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])))
        backend = GPTMLGenerator(output / "traces", credentials)
        session = GPTMLSession(backend, output)
        print("InvestWise — D5 | unchanged ML + GPT-6.1 Sol, low reasoning")
        print("Use fictional text only. Private records:", output)
        print("This separate example cannot save a financial profile. The normal app is unchanged.")
        print("ML checks the first reply; GPT handles uncertainty and same-example dialogue.")
        print("Commands: /help /confirm /change /pause /resume /stop /new /exit")
        print("\n" + session.question)
        while True:
            try:
                text = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nD5 example closed.")
                return 0
            if not text:
                continue
            if text == "/exit":
                return 0
            before_ml, before_gpt = session.ml_calls, backend.calls
            result = session.command(text) if text.startswith("/") else session.submit(text)
            render(result)
            ml_calls, gpt_calls = session.ml_calls - before_ml, backend.calls - before_gpt
            route = ((session.last_record or {}).get("route", "control")
                     if ml_calls or gpt_calls else "control")
            print(f"[Route: {route}; ML calls: {ml_calls}; GPT calls: {gpt_calls}]")
            if text == "/new":
                print(session.question)
    except AuthBlocked as error:
        print("Sign-in/access stopped:", error.code, file=sys.stderr)
        print("Use the existing documented login command deliberately; no automatic sign-in or retry.", file=sys.stderr)
        return 2
    except DemoStopped as error:
        print(str(error), file=sys.stderr)
        print("No retry or fallback. Inspect the private safe receipt.", file=sys.stderr)
        return 2
    except Exception:
        print("D5 stopped. Check installed dependencies and the private safe receipt.", file=sys.stderr)
        print("No automatic sign-in, retry, model substitution or paid-API fallback.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
