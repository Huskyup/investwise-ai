# Separate local D5 demonstration: ML + Qwen

**Status: implemented; the live comparison stopped on its third example.** Preflight passed, then two combined-route replies passed. Qwen mislabelled two employers as multiple source categories on the third; validation rejected it. The remaining examples and live context checks were not run. This route is available for development, but is not a verified company-demo replacement or an efficiency improvement. See the [results and stop evidence](../../docs/d5-local-ml-qwen-2026-10-13/REPORT.md). The existing [GPT terminal](README.md) remains available with its original launch command.

This entry point combines the unchanged main application's ML predictors with the cached **Qwen3-4B-Instruct-2507-4bit**, revision `50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b`. It runs on **Apple Silicon macOS**, in a separate local worker. It uses no ChatGPT sign-in, API key or GPT fallback. The normal application, all 15 questions, datasets and existing model weights are unchanged.

## Launch on the current owner's computer

Close an older terminal demonstration before starting this separate route:

```bash
cd "/Users/husky/Desktop/hackathon Bristol 2026/investwise-demo"
"$HOME/.venvs/investwise-d5/bin/python" demos/d5/local_demo.py chat \
  --worker-python "$HOME/.workbuddy/binaries/python/envs/default/bin/python"
```

This uses the already installed D5 controller environment, existing MLX worker environment and pinned model in the Hugging Face cache. It does not install or download anything. If a required dependency or cached file differs, it stops instead of substituting a model.

## First-time teammate setup

Use only the maintained Huskyup repository. The following installation and optional model preparation require network access; the actual demonstration runs offline.

```bash
git clone --branch feature/all-question-ml-prototype https://github.com/Huskyup/investwise-ai.git
cd investwise-ai
python3.12 -m venv "$HOME/.venvs/investwise-d5"
"$HOME/.venvs/investwise-d5/bin/python" -m pip install -r demos/d5/requirements.txt
python3.12 -m venv "$HOME/.venvs/investwise-d5-local-worker"
"$HOME/.venvs/investwise-d5-local-worker/bin/python" -m pip install -r demos/d5/requirements-local-worker.txt
```

The controller keeps its existing numerical dependencies; the second environment isolates MLX and the local tokeniser dependencies. Use an installed Python 3.12 interpreter to create these environments. Do not change the normal application's environment.

Model weights are **not in Git**. If the exact snapshot is already cached, skip preparation. Otherwise explicitly obtain only the pinned model files once, from the repository root:

```bash
"$HOME/.venvs/investwise-d5-local-worker/bin/python" - <<'PY'
import sys
sys.path.insert(0, "demos/d5")
from huggingface_hub import snapshot_download
from local_transport import MODEL_ID, MODEL_REVISION, PINNED_MODEL_FILES
print(snapshot_download(repo_id=MODEL_ID, revision=MODEL_REVISION,
                        allow_patterns=list(PINNED_MODEL_FILES), token=False))
PY
```

Then start the terminal manually:

```bash
"$HOME/.venvs/investwise-d5/bin/python" demos/d5/local_demo.py chat \
  --worker-python "$HOME/.venvs/investwise-d5-local-worker/bin/python"
```

The expected default model directory is `~/.cache/huggingface/hub/models--mlx-community--Qwen3-4B-Instruct-2507-4bit/snapshots/50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b`. If an explicit download used another cache location, pass its returned snapshot directory with `--model-path`. The worker checks the exact file list and hashes before loading. It never downloads missing files itself. Do not remove or edit another application's cache to bypass a failed check.

For an existing checkout, update only from the owner's repository before launching:

```bash
git switch feature/all-question-ml-prototype
git pull --ff-only https://github.com/Huskyup/investwise-ai.git feature/all-question-ml-prototype
```

## What the combined route does

**Controls → first-answer ML → Qwen if needed → validation → customer confirmation.**

- The first interpreted reply in a new example uses the unchanged ML predictors once. A financial candidate requires singleton intent and option sets plus agreement from the existing packaged D5 business validator. A confident Undecided or Confusion result uses an authored response without Qwen.
- Unresolved first-answer ML calls Qwen once. The model receives the original reply and business instructions, never the ML guess or probabilities.
- Once an interpreted reply exists, follow-ups and corrections go directly to contextual Qwen. That preserves earlier facts when the customer answers a focused question with `Yes.`. `/change` also uses the contextual route.
- ML and Qwen retain distinct provenance and immutable acceptance receipts. Confirmation reuses the accepted result; it does not invoke a model. No answer becomes a saved financial profile in this standalone example.

The baseline snapshot uses the main application's existing deterministic fitting procedure over its unchanged training and calibration CSVs. No supplemental examples, features, threshold changes or model tuning are added. The separate-process parity check found exactly matching predictions and probabilities on the original 11 replies. That establishes baseline reuse, not financial understanding or local-Qwen accuracy.

The terminal prints the selected route and separate **ML calls / Qwen calls** for each action. One ML call means one resolver pass, which may consult both existing classifiers. A correct choice or control response is not a free-text interpretation success. If every eligible first reply reaches Qwen, there is no demonstrated saving from ML routing.

## Use one fictional example at a time

The opening question is: **What currently pays for your everyday living costs?** Start with an existing example such as `My wages stay in savings. My pension pays the bills.` Read the proposed meaning before confirming it.

| Command | Behaviour |
|---|---|
| `/help` | Explain the question without calling either model. |
| `/confirm` | Confirm the pending candidate in this session, without another model call. |
| `/change` | Invalidate confirmation, retain this example's raw replies and ask what changed. |
| `/pause` / `/resume` | Retain context; text entered while paused is not interpreted or queued. |
| `/stop` | End this example and clear its active interpretation history. Resume cannot undo stop. |
| `/new` | Start a different fictional example with no earlier answer history. |
| `/exit` | Close the terminal and local worker. |

After confirmation, use `/change` for the same customer or `/new` for a different example. The session does not proceed to D6. Help, pause, stop and safety controls run before both models. Any displayed human handover is simulated.

History contains only interpreted user replies and authored prompts from this example, including ML-handled replies. It is bounded to 12 interpreted replies including the current one and 32,768 characters of context. At the limit, start afresh with `/new`; earlier facts are not silently discarded. The loaded Qwen weights stay in the worker between requests, but each generation uses a **fresh inference cache** and only the explicitly supplied dialogue history.

## Limits and records

The worker uses greedy decoding, a **2,048-token output cap**, **60-second initial load limit** and **30-second generation deadline**. The transport limits a worker response to 1 MiB; the unchanged interpretation contract has its separate 64 KiB output limit. Truncated output or a late error is not accepted as a completed interpretation. The schema is included as an instruction, not enforced by constrained decoding; the unchanged validator may reject generated JSON.

Runtime failures stop the session. There are no automatic retries, output repairs, alternative models, cloud calls or cached-answer fallbacks. A contract rejection creates no financial candidate. A confident wrong ML interpretation can still pass a structural check: neither its conformal sets nor exact quotations establish semantic truth, so customer confirmation remains necessary.

Use fictional data. Each launch creates owner-only records under `~/.local/state/investwise/d5-local-demo/`, including submitted text, context, raw output, validation result, route and separate model counts. These are diagnostic records, not a saved financial profile. `/new` clears active history but does not delete the existing records; restarting never loads them as memory. An optional `--output-dir` must name a new directory outside the repository. Do not commit these records or credentials.

The existing GPT route still launches with `"$HOME/.venvs/investwise-d5/bin/python" demos/d5/demo.py chat`. Selecting it is an explicit separate action, never an automatic local-model fallback. The local run used four Qwen calls in total; all three combined replies escalated from uncertain ML, so its observed ML-handled share was 0/3. The earlier successful GPT conversation remains separate evidence.
