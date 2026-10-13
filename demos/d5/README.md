# Run the independent D5 demonstration

This is a manually started **terminal conversation** using the repaired D5 interpreter: GPT-6.1 Sol with low reasoning. You can type new fictional replies, read the interpretation or focused follow-up, confirm a candidate and replace an earlier answer. The normal Streamlit app, its default model route and its 15 questions are unchanged.

The earlier current-reply-only version completed one live D5 conversation: a focused follow-up, pension-only confirmation, correction and fresh confirmation of mixed funding. It used three existing examples and three model calls. The [saved conversation and transcript](../../docs/d5-live-conversation-2026-10-12/REPORT.md) show that earlier run. The latest [same-example context update](../../docs/d5-same-example-context.md) has been reviewed statically only; it has not been tested live or through a new evaluation.

## Install once

Use **Python 3.12 on macOS or Linux**, a terminal and a local browser for sign-in. The existing credential implementation uses POSIX file locking; native Windows is not supported. Installation requires network access. The package pins match the source experiment; no model weights or additional LLM are downloaded.

For a first checkout, clone the maintained D5 branch from **Huskyup's repository**:

```bash
git clone --branch feature/all-question-ml-prototype https://github.com/Huskyup/investwise-ai.git
cd investwise-ai
```

Then, from the repository root:

```bash
python3.12 -m venv "$HOME/.venvs/investwise-d5"
"$HOME/.venvs/investwise-d5/bin/python" -m pip install -r demos/d5/requirements.txt
```

If `python3.12` is not found, install or select a Python 3.12 interpreter first. Use that interpreter only to create this separate environment; the commands afterwards use its explicit path. Do not change the normal app's environment.

## Sign in with your own account

```bash
"$HOME/.venvs/investwise-d5/bin/python" demos/d5/demo.py login
```

Complete **Continue with ChatGPT** in the system browser. The existing flow registers this app, checks identity and granted permission, and keeps credentials in an owner-only directory at `~/.config/investwise/d5-chatgpt-plan/`. The login command also checks that the account lists the exact `gpt-6.1-sol` model. Your account must be eligible and have access; somebody else's successful run does not grant access to your account. This uses the existing [official open-source sign-in flow](https://developers.openai.com/siwc/token-sharing-open-source/sign-in).

There is no shared credential in the repository, API-key setup or billing fallback. If this app already has a valid registration on your computer, you can start the conversation without signing in again. An expired token can be renewed by the existing credential provider; failed inference is never replayed automatically.

## Start a conversation

```bash
"$HOME/.venvs/investwise-d5/bin/python" demos/d5/demo.py chat
```

For an existing installation, close the D5 terminal, update from the repository root, then launch `chat` again:

```bash
git switch feature/all-question-ml-prototype
git pull --ff-only https://github.com/Huskyup/investwise-ai.git feature/all-question-ml-prototype
"$HOME/.venvs/investwise-d5/bin/python" demos/d5/demo.py chat
```

The 13 October safety, confirmation and same-example context updates require no dependency change. They apply to this standalone terminal; the normal Streamlit default is unchanged. First-time users must complete installation and their own sign-in above. No test command is needed before launch.

Enter a D5 answer on one line. The opening question is:

> What currently pays for your everyday living costs?

For example, use an existing demonstration reply: `My wages stay in savings. My pension pays the bills.` Read the proposed interpretation, then choose an explicit action:

| Command | Effect |
|---|---|
| `/help` | Explain D5 through the existing Help route. |
| `/confirm` | Confirm the pending D5 candidate in this session. No new interpretation call. |
| `/change` | Invalidate the previous confirmation, retain this example's earlier replies and ask what has changed. |
| `/pause` / `/resume` | Pause and resume the current example through the existing controls. |
| `/stop` | Stop this example and clear its interpretation history. Resume does not undo a stop. |
| `/new` | Start a separate fictional example with empty answer state and no earlier dialogue. |
| `/exit` | Close the terminal demonstration. |

Ordinary replies go through the existing control checks before interpretation. Within one example, the same single model request now includes earlier interpreted user replies and the authored prompts they answered. You can answer a focused follow-up briefly or correct one part of an earlier answer. The newest explicit correction should replace the conflicting detail; ambiguous references still require clarification. A short answer does not bypass explicit `/confirm`.

History is local to this running example. `/new` clears it; `/change` keeps it while invalidating confirmation. Pause/resume retains it, but input blocked while paused is never queued for interpretation. Stop or safety-stop clears it. The model receives at most 12 interpreted replies including the current reply, within 32,768 characters of dialogue and prompts. At the limit, the demo asks you to use `/new` and restate the current situation; it does not silently discard earlier facts or summarise them with another model.

Confirmation ends this D5 example rather than opening D6. You can then change D5, start a separate example or exit. This isolated example cannot save a completed financial profile or bypass the main application's separate save-consent workflow. A pause, stop or safety response creates no financial answer. Any human handover shown is simulated; nobody is contacted.

The screen shows the number of interpretation calls for each action. Financial interpretation uses one direct model call; Help and deterministic controls do not constitute model successes. No choice menu is used as free-text recovery.

## Use it for the company demonstration

Start `chat` once. Enter each line below separately, read the response, then enter the next line. These are the exact existing examples used in the successful conversation; there is no need to run `check-11` first.

| Step | What to enter | What to look for |
|---|---|---|
| 1 | `I receive wages and pension payments` | A question about which sources actually pay living costs; no assumed financial answer. |
| 2 | `My wages stay in savings. My pension pays the bills.` | Pension-only candidate, with wages excluded; asks for confirmation. |
| 3 | `/confirm` | Confirms the pension answer in this session, with zero new model calls. |
| 4 | `/change` | Invalidates the previous answer. The latest runtime retains the example's earlier replies for the correction. |
| 5 | `Both my wages and pension pay for everyday costs.` | New mixed-source candidate with both categories, awaiting fresh confirmation. |
| 6 | `/confirm` | Confirms the corrected answer, with zero new model calls. |
| 7 | `/exit` | Ends the session without saving a financial profile. |

Explain the business point: **receiving money does not establish how it is used; one interpretation supports a focused follow-up, confirmation and correction.** The transcript records one successful live run of the earlier version, not a verification of the new context handling or guaranteed service availability. If a live request fails, the session stops. The saved transcript can be shown as a labelled recording of the earlier run; it must not be presented as live inference.

## Try your own wording

Use the same `chat` command and type your own fictional D5 answer instead of the demonstration sequence. Use `/new` between independent examples and `/change` to replace an answer within the same example. Read the proposed meaning before using `/confirm`.

For follow-ups, you can answer the question just asked without repeating all earlier details. For corrections, name what changes; `/change` retains earlier replies within this example. If a reference is unclear, the demo should ask rather than guess. Without `/new`, you remain in the same example: do not introduce a different fictional customer as though it were a continuation. Read the whole confirmation before using `/confirm`. This context behaviour is implemented but has not been measured live in this update.

## Local records and access failures

Use fictional data. Each launch creates a private directory under `~/.local/state/investwise/d5-demo/` containing replies, the exact context supplied, raw model output, authored responses and safe backend receipts. These are local diagnostic records, not a saved financial profile. `/new` clears active memory but does not delete these earlier trace files; restarting never reloads them as memory. The terminal prints the directory location. Do not commit these directories or authentication files.

Optional `--profile-dir` and `--output-dir` arguments select external directories; neither can point inside the repository. The output directory must be new. A runtime or access failure stops the session: there is no automatic sign-in, inference retry, model replacement, output repair or cached-answer fallback. Read the safe receipt's stage/code, then resolve access deliberately before a later run.

The transport still uses empty tools, `tool_choice: none`, `store: false` and completed streamed responses. Its 30-second deadline and 1 MiB response limit are local limits, not a server token cap. See the [official preview limitations](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).

## The original eleven examples

An explicit comparison command uses **only the same eleven published inputs**, through the same session submission method as the interactive entry:

```bash
"$HOME/.venvs/investwise-d5/bin/python" demos/d5/demo.py check-11
```

This command makes live model requests. Do not run it merely to view the existing results. It refuses changed input/expectation files, freezes the packaged code before execution, reads labels only after inference, and stops on a runtime/access failure without retry. The original Help example should make zero model calls. Automated option/routing matches still require a review of raw meanings and follow-up wording; they are not an independent semantic accuracy estimate.

The previous repair produced seven correct clear candidates, two missing-information responses, one Undecided response and one pre-model Help response. These are already-opened fictional examples, not an unseen evaluation bank. The [standalone verification record](../../docs/d5-standalone-verification.md) records the authorised packaging check separately.

## How the default stays unchanged

`runtime/` contains the existing tested dependency closure and full fifteen-question specification. A separate Python process loads that private `ai` package first and rejects imports mixed with the normal application's `ai` package. The normal factory and frontend never import this directory. Other-question resolution and profile saving are disabled in this example.

No model, prompt, schema, semantic validator, business definition or follow-up was changed during the original packaging. At that point, only the credential provider's personal default path and repository containment path were made portable. The subsequent [13 October runtime repair](../../docs/d5-runtime-repair-2026-10-13.md) adds the existing jump-intent safety fix and uses exact user quotations for confirmation, preserving exclusions such as "not investment withdrawals". It uses the same model interpretation and leaves the normal application unchanged.

The subsequent context update changes the packaged prompt, context-aware evidence validation, authored follow-up wording and request data. It keeps the financial JSON output schema, model and one-call resolver interface unchanged. It adds no retraining, second interpreter, classifier or dependency. Exact quotations may now come from a single earlier user reply, never from assistant text or a fabricated join across replies. The current reply must also be evidenced for a non-abstaining contextual interpretation.

Numerical packages are import dependencies of existing shared types; the demo does not train or call those classifiers. The [runtime manifest](runtime-manifest.json) records original and current hashes, portability differences, runtime updates and pinned versions. The earlier repair's offline results do not validate this later context update. No tests or live requests were run for the context change.

For the semantic method and all eleven before/after cases, read the [technical handoff](../../docs/d5-semantic-method-handoff.md).
