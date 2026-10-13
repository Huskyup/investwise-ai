# Local ML + Qwen D5: implementation delivered, live check stopped

13 October 2026 · Huskyup `feature/all-question-ml-prototype`

The separate local terminal is implemented. **It is not a verified replacement for the working GPT company demonstration.** The single Qwen preflight passed, but the bounded comparison stopped on its third existing example. Qwen incorrectly selected “multiple categories” for pay from two employers. The unchanged validator blocked that candidate. No repair, retry, model substitution or later semantic phase followed.

## What changed

The new [manual entry and setup guide](../../demos/d5/LOCAL_README.md) runs controls first, then the unchanged ML predictors for the first eligible reply. A Clarity candidate needs both singleton gates and the packaged D5 business veto. Confident nonclear ML outputs use authored dialogue. Otherwise one local Qwen request receives the original reply, question, options and business instructions, without ML guesses. Subsequent replies and corrections go directly to Qwen with bounded same-example history.

The integration has separate immutable ML and LLM receipts. Confirmation reuses the accepted interpretation; `/change` invalidates confirmation and retains history, and `/new` clears history. Controls and paused input never enter either interpretation route. Route and separate call counts are visible. The worker retains cached weights but creates fresh generation state for each request, with no tools, credentials, network inference, automatic repair or fallback.

Existing ML fitting, data, features and thresholds are unchanged. The copied main predictor is byte-identical and hash-recorded; acceptance is **unchanged ML predictors plus the packaged D5 validator**, not identical whole-main-app acceptance. All 15 questions, the normal application default and the working GPT source remain unchanged.

## Measured results

| Check | Observed result |
|---|---|
| Offline integration and transport | 12 + 16 checks passed; fixtures only, zero model inference |
| Separate-process ML parity | 11/11 original replies identical, including probabilities; maximum difference 0 |
| Direct Qwen preflight | 1/1 passed: pension pays bills, saved wages excluded, valid completed contract |
| Combined first-turn run | 3/11 reached; two correct raw final categories and accepted candidates |
| Third reply | Source facts identified salary correctly; final `D5_MULTIPLE` category was wrong; rejected |
| Wrong accepted candidates | 0 among the three attempted replies |
| ML-handled share | 0/3 attempted combined replies; all three escalated to Qwen |
| Remaining checks | Eight original replies, four live context turns and live controls not run |
| Actual Qwen generations | 4 total: one preflight and three combined replies; no retries |
| Choice recovery | None; no choice response counted as free-text success |

The complete baseline-only parity output also abstains on every eligible first reply in this existing bank. No speed or efficiency improvement is demonstrated. Software fixtures exercise the ML acceptance route, context, confirmation/correction and zero-call controls; that is not live semantic evidence.

### Business meaning → failure → change → counterexample → result

D5 identifies **which categories currently pay living costs**, not how many payers exist. The baseline cannot confidently resolve these known replies. The proposed change gives unresolved replies to one local semantic interpreter while preserving validation and confirmation.

`My wages stay in savings. My pension pays the bills.` and `Both my wages and pension pay for everyday costs.` produced correct pension-only and mixed-source candidates. The counterexample, `Pay from my two employers covers my living costs.`, exposed the remaining problem: Qwen emitted one salary fact but selected `D5_MULTIPLE`. Two employers still belong to one salary category. The validator rejected it with `multiple_requires_distinct_active_categories`, leaving no financial answer. This is a raw classification error, not a service outage or a harmless JSON-format issue.

The earlier GPT successes for the first two replies were preserved in this local run; the third was lost. The required preservation gate therefore failed. Unrun replies cannot be counted as preserved, failed or successful. No full local D5 dialogue or unseen-text reliability is established.

## Limits and handoff

The existing business veto is not a semantic guarantee. During offline development, one fixture incorrectly assumed it would reject a withdrawals proposal on the pension/saved-wages reply. That assumption was corrected, the limitation retained explicitly, and the original failed log preserved. No new wording rule or validator relaxation was introduced. A genuinely wrong confident ML result can still escape escalation, as the approved plan acknowledged.

The final software checks and independent review preceded inference. The protocol and all runtime/scorer inputs were frozen; both live execution receipts record them unchanged. All 210 original tracked files were unchanged through live verification. Subsequent publication changes only the existing handoff document and adds the isolated implementation/evidence. See the [final preservation record](preservation.json).

Use the existing GPT terminal for the previously demonstrated conversation. The local command is available for explicit development use, with the failed acceptance status shown in its guide. This delivery does not alter defaults or claim whole-product readiness. There was no cloud authentication or API-key access in this cycle; no credentials or model weights are published.

Evidence: [frozen protocol](protocol.json), [independent review](review.json), [ML parity](evidence/baseline-parity/summary.json), [final integration checks](evidence/offline-final/software.json), [transport checks](evidence/transport-checks-final/software-checks.json), [preflight](evidence/preflight/preflight.json), [three-case result](evidence/existing/existing-summary.json), [write-once stop receipt](evidence/existing/STOP.json). Initial offline receipts remain alongside the final receipts.
