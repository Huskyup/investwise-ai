# D5 core company demo

This separate browser entry makes the existing ML + GPT D5 conversation visible. It does not replace the terminal, main application, model, prompt, validators or any of the fifteen questions. It uses the same `GPTMLSession`; the browser cannot select an answer option or confirm it indirectly.

## Start on the owner's Mac

Close an older core-demo server with **Ctrl+C** before restarting. From the repository root:

```bash
cd "/Users/husky/Desktop/hackathon Bristol 2026/investwise-demo"
git switch feature/all-question-ml-prototype
git pull --ff-only https://github.com/Huskyup/investwise-ai.git feature/all-question-ml-prototype
sh demos/d5/run_core_demo.sh replay
```

The browser opens at a loopback address. If it does not open, copy the complete local URL printed by the command. It includes a temporary local session token; do not share it. Use **Run next recorded step** to advance. Step 10 shows the corrected, confirmed pension-only answer. The later steps demonstrate reset, stop and safety handling.

For real free text, stop that server with Ctrl+C and deliberately launch live mode:

```bash
sh demos/d5/run_core_demo.sh live
```

Live mode requires your existing authorised ChatGPT profile and available service access. It makes no inference until you submit a reply. The guide only fills the answer box; **Interpret answer** sends it. You can also enter your own fictional wording. Use **New example** between different fictional people; **Change answer** retains earlier replies while invalidating confirmation. Confirmation itself never makes another model call.

**Latest live evidence:** after the first attempt stopped on provider overload, a separately authorised run completed the existing eighteen-action browser guide using four live GPT requests and no replay. The user then entered their own `savings` → `yes but 50% also come form my wages` → `/confirm` example: savings was retained, wages added, and the updated answer confirmed. That separate user example used one ML check and two live GPT requests. See the [company case, exact transcript and presenter script](../../../docs/d5-company-case-2026-10-13/CASE.md). The original failure is retained in the earlier report. These successes do not guarantee service availability or arbitrary new-wording accuracy.

To present the user's example, use live mode, start a fresh example and type those two replies yourself before confirming. Do not use the optional guide or replay button: they refer to a different existing sequence. This publication did not add the user's example to the replay or test banks, or run any further inference or tests.

## New teammate setup

Use only the Huskyup repository:

```bash
git clone --branch feature/all-question-ml-prototype https://github.com/Huskyup/investwise-ai.git
cd investwise-ai
python3.12 -m venv "$HOME/.venvs/investwise-d5"
"$HOME/.venvs/investwise-d5/bin/python" -m pip install -r demos/d5/requirements.txt
sh demos/d5/run_core_demo.sh replay
```

Python 3.12 on macOS or Linux is required. The browser server uses the Python standard library and local HTML/CSS/JavaScript: no Node build, browser plug-in, external font, database or new Python dependency is needed. Installation may need network access for dependencies. After installation, replay needs no network service, API key or login. The unchanged ML baseline uses its existing deterministic startup fit from the existing training/calibration files; nothing is tuned or saved as new weights.

For a live run, follow the [existing own-account login instructions](../README.md#install-once). Do not copy another person's credentials. Credentials and diagnostic records stay outside the repository. There is no new paid-API route, local Qwen fallback or automatic sign-in.

If port 8765 is already used, choose a different local port:

```bash
"$HOME/.venvs/investwise-d5/bin/python" -B demos/d5/core_demo.py --mode replay --port 8767 --open
```

The server always binds `127.0.0.1`. This is a single-user, single-session local demonstration, not a hosted multi-user service. Do not expose it through a tunnel or reverse proxy. Closing the browser does not stop the server; Ctrl+C does. Each fresh launch starts a new session. The original terminal command remains `"$HOME/.venvs/investwise-d5/bin/python" demos/d5/gpt_ml_demo.py chat`.

## What each mode proves

| Mode | What actually runs | What it does not establish |
|---|---|---|
| Recorded output replay | Current unchanged ML, four previously saved raw GPT outputs, current strict validator, authored follow-ups and confirmation state | New GPT generation, new wording accuracy or service availability |
| Live ML + GPT | Controls, first-reply ML, one GPT interpretation when needed or contextual, validation, explicit confirmation | Universal accuracy, an independently validated financial-advice system, or a complete fifteen-question product |

Replay has no free-text entry. It matches the exact input, whole conversation context, question/options, system-prompt hash and schema before supplying a recording. It never approximates a match or falls back to live GPT. Both occurrences of `Yes.` are context-bound: one adds wages to the known pension funding; the fresh one remains unclear.

The screen separates actual GPT requests, local ML checks and saved outputs consumed. The historical original bank had **0/10 eligible first replies handled by ML alone**. Do not claim reduced GPT usage. No case, customer wording, saved output or business annotation is automatically added to training.

Only validated candidate facts appear in the meaning panel; correction/reset/stop clear them. The programme owns controls, follow-ups and confirmation. A confirmed D5 answer stays in this session. This entry cannot save a financial profile or advance to D6. The main product's final playback and separate save consent remain outside this demo.

## Two-minute presentation

1. State the mode explicitly: “This is a reproduction using saved model outputs” or “This is a live service call.”
2. Explain the business meaning: D5 asks what **currently pays living costs**, not every source received or held.
3. Start the guided sequence. The customer knows pension pays bills but is uncertain whether wages do. D5 asks specifically about wages.
4. Show that paused text is ignored. Resume, answer `Yes.`, and review wages plus pension before confirming.
5. Choose change and submit `My wages stay in savings.`. Pension remains, wages are excluded, and the corrected answer requires fresh confirmation.
6. At step 10, stop the presentation or continue to show that New example clears memory and a fresh `Yes.` is not enough. The remaining existing controls demonstrate stop and a fictional safety probe.

Suggested honest explanation: “The improvement is a clearer business representation and controlled conversation. The interpreter separates source category, timing and living-cost use, and the software checks that interpretation before asking the customer to confirm. Our original ML is still the first check, but these known examples rely on GPT. Today's replay demonstrates the workflow, not new semantic accuracy.”

## Reproduce the bounded software check

The following command performs **no live GPT or authentication calls**. Use a new external output directory each time:

```bash
"$HOME/.venvs/investwise-d5/bin/python" -B demos/d5/core_verify.py \
  --output "$HOME/.local/state/investwise/d5-core-check-$(date +%Y%m%dT%H%M%S)"
```

It reuses the existing eleven replies and four context turns; it also checks malformed protocol envelopes and presentation state using those same fixtures. It verifies ML parity, exact recording/context matching, zero-call controls, rejected/stale candidate display, and local HTTP boundaries. It is not a fresh semantic benchmark.

## Business corpus and next work

- [One-page D5 business standard](BUSINESS_STANDARD.md) and [eleven-case source/relationship matrix](business-examples.json): existing IDs, replies and gold labels, with explicit unknowns and source hashes. Annotation review is agent-authored and independently agent-reviewed; human business sign-off is still needed.
- FCA (Formal Concept Analysis) is useful here as an **offline coverage/review method**. The matrix exposes actual use, exclusions, timing and category grouping; it is not another runtime interpreter or a source of automatically generated financial rules. No concept-lattice algorithm was added in this delivery.
- Next: have the business owner review these eleven annotations and wording, and use the documented live examples for company feedback. The separately authorised live guide has now passed. Broader usability research and any ML retraining remain separate later decisions.

Local reply/trace records are written under `~/.local/state/investwise/d5-core-demo/` with owner-only permissions. New example clears active memory, not the existing files. No browser endpoint serves credentials, traces or arbitrary files. Model/service failures stop the session; only fixed safe status text is sent to the browser.

See the [delivery evidence report](../../../docs/d5-core-demo-2026-10-13/REPORT.md) and [team handoff](../../../docs/d5-semantic-method-handoff.md).
