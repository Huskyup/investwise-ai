#!/usr/bin/env python3
"""Manual local ML + Qwen D5 terminal. The existing GPT command is unchanged."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
import uuid

sys.dont_write_bytecode = True
from session import DemoStopped, private_directory, render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["chat"])
    parser.add_argument("--worker-python", type=Path,
                        help="Python with the pinned local MLX dependencies")
    parser.add_argument("--model-path", type=Path,
                        help="Existing pinned Qwen snapshot directory; no download")
    parser.add_argument("--output-dir", type=Path,
                        help="New private session directory outside the checkout")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12) or os.name != "posix":
        parser.error("Use the existing Python 3.12 D5 environment on macOS.")
    os.umask(0o077)
    backend = None
    try:
        from local_transport import LocalGenerator
        from local_session import LocalD5Session
        output = private_directory(args.output_dir or (
            Path.home() / ".local/state/investwise/d5-local-demo" /
            (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])))
        backend = LocalGenerator(output / "traces", worker_python=args.worker_python,
                                 model_path=args.model_path)
        session = LocalD5Session(backend, output)
        print("InvestWise — local D5 | existing ML + Qwen3-4B-Instruct-2507-4bit")
        print("Use fictional text only. Private records:", output)
        print("No ChatGPT connection. This separate example cannot save a financial profile.")
        print("ML handles eligible first replies; Qwen handles unresolved replies and conversation context.")
        print("Commands: /help /confirm /change /pause /resume /stop /new /exit")
        print("\n" + session.question)
        while True:
            try:
                text = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nLocal D5 example closed.")
                return 0
            if not text:
                continue
            if text == "/exit":
                return 0
            before_ml, before_qwen = session.ml_calls, backend.calls
            result = session.command(text) if text.startswith("/") else session.submit(text)
            render(result)
            ml_calls, qwen_calls = session.ml_calls - before_ml, backend.calls - before_qwen
            route = (session.last_record or {}).get('route', 'control') if ml_calls or qwen_calls else 'control'
            print(f"[Route: {route}; ML calls: {ml_calls}; Qwen calls: {qwen_calls}]")
            if text == "/new":
                print(session.question)
    except DemoStopped as exc:
        print(str(exc), file=sys.stderr)
        print("No retry, output repair or GPT fallback.", file=sys.stderr)
        return 2
    except Exception:
        print("Local D5 stopped. Check the pinned dependencies, cached model and private receipt.", file=sys.stderr)
        print("No automatic download, retry or alternative model was used.", file=sys.stderr)
        return 2
    finally:
        if backend is not None:
            backend.close()


if __name__ == "__main__":
    raise SystemExit(main())
