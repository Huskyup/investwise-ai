# D5 same-example context handoff

13 October 2026 · Maintained only in [Huskyup/investwise-ai](https://github.com/Huskyup/investwise-ai/tree/feature/all-question-ml-prototype).

The standalone terminal carries earlier user replies into its existing D5 interpretation request. One bounded live conversation now verifies a short `Yes.`, a targeted correction and a clean `/new`: four model calls produced the four expected outcomes, including two correct financial candidates. This removes the requirement to repeat the entire funding situation in that demonstrated sequence; it does not establish that every short reference will be understood. See the [recorded verification](d5-context-verification-2026-10-13/REPORT.md).

## What changes

`D5Session` keeps ordered pairs of authored prompt and original user reply in memory. It records only replies actually interpreted, not paused or control-only input. Each request supplies the current reply separately from this history and the pending authored question. No previous model facts, candidate IDs or summaries become authoritative financial memory. GPT-6.1 Sol, low reasoning, remains the sole interpreter, with at most one call per eligible reply.

The prompt asks the model to retain unaffected user-established facts, apply the latest explicit correction, and clarify ambiguous references or replacement scope. Receipt of money still does not establish expenditure, and unresolved earlier sources cannot be silently dropped to produce Clarity. The existing source-use follow-up now asks one yes/no question and permits uncertainty. The same three semantic buckets and independent abstention remain.

The existing financial output schema is unchanged. Context-aware validation accepts quotations only from one actual user reply at a time. Authored assistant text and joins across turns cannot supply evidence. Non-abstaining contextual outputs must also quote the current reply. Existing category, relation, duplicate, completeness and no-financial-payload checks remain. These structural checks cannot prove that a correction was semantically understood.

Each issued immutable decision binds the exact context snapshot used for that call, in addition to the existing current-input, specification, prompt and output hashes. Confirmation recomputes against that frozen snapshot, even after the session has appended another turn. The engine still checks the unmodified current input and versioned candidate receipt. Contextual confirmation displays the latest reply, current funding categories and exact supporting quotations separately; nothing confirms or saves automatically. This presentation was repaired after the live run because an older quotation still contained uncertainty resolved by `Yes.`. The repaired rendering is checked by replaying the saved outputs, without further model calls.

## Lifecycle and limits

| Action | Context behaviour |
|---|---|
| Continue a follow-up | Send earlier interpreted user replies and authored prompts with the current reply. |
| `/change` | Invalidate the previous confirmation; retain history and mark a correction request. |
| `/confirm` | Reuse the same verified interpretation; no new model call. D5 then ends. |
| Pause/resume | Retain the example; ignore input blocked while paused. |
| Stop/safety-stop | Clear active interpretation history and retain the existing stop boundary. |
| `/new` | Replace interpreter and engine; clear history, last record and candidate state. |
| Exit/restart | No context is restored from disk. |

Requests are bounded to 12 interpreted user replies including the current one and 32,768 characters across replies and authored prompts. At the limit, no model request is made; a fresh example and restatement are requested. Whole turns are preserved without silent eviction or model-generated summarisation. Existing clarification limits can stop follow-ups earlier.

The existing private diagnostic files now include the context snapshot. Clearing active memory does not erase those files. They stay outside Git. Credentials and authentication are unchanged. The transport still requires the exact model, low reasoning, `tools: []`, `tool_choice: "none"`, `store: false`, a completed passive response and the existing deadline/response limit, with no retry. It sends manual context in the request data, with no server conversation ID or persistent conversation API. This follows the general [manual conversation-state pattern](https://developers.openai.com/api/docs/guides/conversation-state).

## Scope and use

This context feature applies only to the manually started D5 terminal. All 15 questions, trained models, normal app factory/default model route and existing experiment evidence remain unchanged. Separately authorised main-app safety and uncertainty-follow-up repairs are documented in the [verification report](d5-context-verification-2026-10-13/REPORT.md); they change those conversation behaviours. No fusion, dependencies or training are added. The earlier context implementation changed the prompt, request data, validator provenance scope and follow-up wording; this must not be described as a weights improvement or a general accuracy gain.

From the checkout root, use the existing launch command:

```bash
"$HOME/.venvs/investwise-d5/bin/python" demos/d5/demo.py chat
```

Use `/new` for a different fictional example, and `/change` for a correction to the same example. Existing eligible sign-in and dependencies are required; see the [run instructions](../demos/d5/README.md). No test command is required to launch. The new four-call transcript and offline software checks validate the bounded behaviours stated above. The earlier eleven-case comparison and 22-input repair replay remain historical evidence for their own versions.
