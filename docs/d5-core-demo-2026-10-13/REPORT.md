# D5 core demo: visible conversation and reproducible evidence

13 October 2026. The independent D5 browser demo is implemented and its recorded walkthrough works. It reuses the existing ML + GPT session and strict interpretation contract. One real browser request reached GPT but the provider reported `server_is_overloaded`; no live interpretation completed in this round. These two outcomes are recorded separately.

## Business meaning → problem → change → counterexample → result

**Business meaning.** D5 asks which source categories currently pay living costs. Receipt/ownership alone does not establish use; two employers are one salary category. Confirmation must preserve what the customer actually said.

**Observed problem.** The working conversation and accumulated evidence were spread between terminal commands, reports and private traces. A company audience could not readily see the interpreted relationships, retained history, corrections and confirmation state. Service availability also made a live-only presentation fragile.

**Change.** A manually launched local browser wraps `GPTMLSession` without changing the models, routing, prompt, validators or existing authored follow-ups. It displays validated candidate facts and their quotations, routes/counters and the current confirmation state. A separate replay mode consumes only four previously published outputs in their exact eighteen-action context sequence. There is no text-only cache, output repair, live fallback or financial option-selection shortcut. Current ML still runs in replay; the saved GPT outputs pass through the current validator and engine.

**Counterexample.** `Yes.` after the wages-use follow-up produces the existing wages/pension candidate; `Yes.` after New example remains model uncertainty with no financial answer. The latter must not inherit pension or become customer indecision. Excluding saved wages changes the earlier mixed answer to pension only and invalidates old confirmation first.

**Measured result.** All existing recorded outcomes are preserved in the new presentation. No new semantic improvement or unseen-text accuracy is claimed. The real service attempt returned an overload error before a usable output; it is not a semantic misclassification or a successful live conversation.

## What is now usable

- `sh demos/d5/run_core_demo.sh replay`: reproducible offline browser walkthrough, explicitly labelled as saved-output replay, with no API key or login required after dependencies are installed.
- `sh demos/d5/run_core_demo.sh live`: the same browser connected to the existing tool-free GPT route, accepting new fictional text. It needs the user's existing authorised account and working service access. Launch deliberately; failures stop the session.
- [D5 business standard](../../demos/d5/core/BUSINESS_STANDARD.md) and [annotated original eleven replies](../../demos/d5/core/business-examples.json): traceable source/use relationships, grouping, unknowns and appropriate next actions. Exact original IDs/text/gold are preserved; annotations await human business sign-off.

The [setup and presenter guide](../../demos/d5/core/README.md) includes commands, the full sequence, mode boundaries and limitations. There are no new Python runtime dependencies and no frontend build step. This entry is local, single-session and manually launched. It does not save a profile, cover the full fifteen-question journey or replace whole-product release checks.

## Verification and limits

| Evidence | Result | Meaning |
|---|---|---|
| Focused final offline verification | 8 groups passed; 0 failed/errors/skipped | Presentation, state, request boundaries and fixture replay work; no live semantic claim |
| Original 11 saved outcomes | All preserved; original ML predictions/probabilities match exactly | Known regression evidence only |
| Existing contextual sequence | 18 actions, four saved outputs, two explicit confirmations | Retained context, correction, reset and current validation reproduced |
| Existing controls | 14 actions, zero ML/GPT/replay calls | Help, pause/ignored input/resume, confirmation, correction, reset, stop and safety stay before interpretation |
| Actual browser, replay | 18 actions passed; 0 GPT requests; no script errors; narrow layout has no horizontal overflow | The actual HTML/JS interface and local server work together |
| Actual browser, live | Help passed with zero calls; one ML check and one GPT request; then provider overload | Connection reached provider, but 0/4 intended context interpretations completed |
| Retry / fallback / extra semantic cases | 0 / 0 / 0 | No dataset expansion or repeated service attempt |

The offline verifier additionally mutates existing protocol envelopes to check rejected output, stale confirmation, exact context/prompt/question/options/schema matching, and the fixed provider-failure display. These are software fixtures, not new financial replies. A simulated overload is labelled as a fixture and is never counted as a live request. The final offline run follows an initial seven-group pass; the additional group covers the actual overload envelope observed during the one live attempt.

The first browser automation interface was unavailable; a fresh isolated installed Chrome instance, controlled through Playwright, performed the recorded and live UI actions. It did not reuse personal browser cookies. Browser automation is verification tooling only; it is not a demo dependency.

### Real service failure

The [safe receipt](live-stop.json) records one request for `gpt-6.1-sol`, low reasoning, empty tools, `tool_choice: none`, `store: false`, no dispatcher, no retry and no output repair. The provider returned `server_is_overloaded` / `service_unavailable_error`; the transport refused it. An HTTP 200 envelope does not make a streamed provider failure a completed interpretation. No candidate or financial facts were accepted. No second request, sign-in change or replacement model followed.

Raw credentials and HTTP bodies are excluded. All session diagnostics remain outside Git under the user's private state directory. The published browser summaries contain only fictional inputs' display results and counters; no session access token or credential path is included.

## Scope preservation and team handoff

The before/after audit records the original tracked files and unrelated untracked work. Only root README navigation and the team handoff are edited among previously tracked files; runtime/model/prompt/schema/training/calibration/validators, the fifteen-question specification, existing terminal entries and earlier evidence remain byte-identical. New files are the separate presentation, its offline verifier, business matrix and delivery evidence. No teammate repository is a publication target.

The runtime still uses the original baseline's deterministic startup fitting procedure from unchanged data, without tuning or saved weight changes. ML handled 0/10 eligible first replies in the previous live bank; current parity preserves that behaviour. This delivery does not claim a completed learning flywheel or cheaper inference.

FCA is used only as a way to organise an offline business relationship matrix. There is no new lattice algorithm, runtime classifier, retrieval stage or generated financial rule. The remaining small steps are human review of the eleven annotations, a separately authorised repeat of the same live guide once service access works, and company usability feedback. Broader banks, self-hosted Qwen improvements and ML retraining remain separate decisions.

- [Final offline summary](offline-checks.json)
- [Actual browser replay summary](browser-replay.json)
- [Actual browser live attempt](browser-live.json)
- [Preservation audit](preservation.json)
- [Independent review](review.json)
- [Team handoff](../d5-semantic-method-handoff.md)
