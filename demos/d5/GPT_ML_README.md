# Separate D5 demonstration: ML + GPT

This manually launched terminal combines the unchanged main ML predictors with **GPT-6.1 Sol, low reasoning**, through the existing ChatGPT sign-in connection. The original direct-GPT command, local Qwen entry, all 15 questions and normal application default remain available and unchanged. No weights, datasets, business prompt or validation thresholds are changed.

## Start on the owner's computer

Close the older D5 terminal, then run:

```bash
cd "/Users/husky/Desktop/hackathon Bristol 2026/investwise-demo"
git switch feature/all-question-ml-prototype
git pull --ff-only https://github.com/Huskyup/investwise-ai.git feature/all-question-ml-prototype
"$HOME/.venvs/investwise-d5/bin/python" demos/d5/gpt_ml_demo.py chat
```

No additional dependency or sign-in is needed for an already configured installation with working access. New teammates should follow the original [Python 3.12 setup and their own ChatGPT sign-in](README.md#install-once), then launch `gpt_ml_demo.py chat`. This uses only the Huskyup repository. There is no shared API key, paid-API fallback, local Qwen fallback or automatic new sign-in.

## Conversation workflow

**Controls → first-reply ML → GPT if needed → strict validation → explicit confirmation.**

- ML checks the first interpreted reply in a fresh example. A Clarity candidate needs the existing singleton intent and option gates plus a matching result from the packaged D5 business validator. Confident ML Undecided or Confusion uses the existing authored response. This is unchanged ML predictors **plus the packaged D5 validator**, not an improved ML model.
- If ML cannot resolve that reply, one GPT request receives the original reply, question, options and unchanged business instructions. ML guesses and probabilities are never supplied to GPT.
- Subsequent replies and corrections go directly to contextual GPT. History contains the raw replies, including ML-handled replies, and the authored prompts they answered. There is no model voting or second interpretation stage after GPT.
- Each route retains its own immutable receipt. Confirmation reuses the accepted result; it makes no model call. A confident wrong ML result can still escape escalation, and internally consistent GPT output can still be wrong. Read the proposed meaning before confirming.

The screen reports the route and separate **ML calls / GPT calls**. One ML call means one resolver pass over its existing classifiers. At startup the unchanged baseline performs its existing deterministic fitting over the same training/calibration files; there is no extra data, tuning or saved-weight update.

## Use the existing conversation

Enter one line at a time:

```text
My pension pays some bills; I cannot tell whether my wages also do.
Yes.
/confirm
/change
My wages stay in savings.
/confirm
/new
Yes.
/exit
```

The intended meaning is a focused question about wages, then wages plus pension after `Yes.`, then pension only after the wages correction. `Yes.` after `/new` must not inherit the old answer. The [separate run report](../../docs/d5-ml-gpt-2026-10-13/REPORT.md) records which checks actually completed; this sequence is not a cached playback.

Use `/new` for a different fictional customer. Without it, earlier replies remain part of the same example. `/change` invalidates confirmation and retains history. `/help`, `/pause`, `/resume`, `/stop` and safety controls precede both models; paused input is not queued. Stop clears active history and cannot be undone with resume. The existing limits retain at most 12 interpreted replies including the current one and 32,768 characters; they do not silently summarise or discard facts.

## Scope, access and records

This standalone D5 example cannot advance to D6 or save a financial profile. The main application's separate save consent is unchanged. Use fictional text; diagnostic records are different from a confirmed/saved customer profile.

Every request uses exact `gpt-6.1-sol`, low reasoning, empty tools, `tool_choice: none`, `store: false` and the existing strict JSON schema. The unchanged transport requires a completed response and stream end, with a 30-second whole-request deadline and 1 MiB response limit. These are local limits, not a server token cap. See the [official plan inference documentation](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference).

Access or runtime failure stops the session. There is no automatic retry, output repair, model replacement or cached-answer recovery. A rejected contract creates no financial candidate. Each teammate needs their own eligible account and available usage; the combined route does not remove that dependency.

Credentials remain outside Git under `~/.config/investwise/d5-chatgpt-plan/`. New session records are owner-only under `~/.local/state/investwise/d5-ml-gpt-demo/`; they include input, supplied context, raw output, route, counts and safe transport receipts. `/new` clears active context, not existing diagnostic files. An optional `--output-dir` must be a new directory outside the repository. Do not publish private session records or credentials.

The unchanged direct-GPT entry remains `"$HOME/.venvs/investwise-d5/bin/python" demos/d5/demo.py chat`. Neither entry is automatically selected by the main application. Read the [bounded comparison](../../docs/d5-ml-gpt-2026-10-13/REPORT.md) before claiming semantic accuracy, ML efficiency or company-demo readiness.
