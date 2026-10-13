# D5: unchanged ML + GPT-6.1 Sol low

13 October 2026. **The separate combined route passed the authorised existing-example check.** It is available through `demos/d5/gpt_ml_demo.py chat`; the original GPT terminal and main application default are unchanged. No further cases or inference were added after this run.

## Business reason and change

D5 identifies the categories currently paying living costs. Two employers still mean one salary category; receiving wages and pension does not establish that both are spent on bills. The previous local Qwen run misclassified both situations. This delivery replaces Qwen only in a new, explicitly selected entry with the existing GPT-6.1 Sol low interpreter, using its unchanged business prompt and strict transport.

Controls run before models. Unchanged ML checks the first reply; its existing singleton gates and packaged D5 business veto must agree before it can propose an answer. Otherwise GPT interprets the original reply once, without ML guesses. Same-example follow-ups and corrections use contextual GPT directly. Validation and explicit confirmation remain application responsibilities. No retraining, new financial rules or model voting were introduced.

## Measured result

| Check | Result |
|---|---|
| Offline GPT routing/receipt/payload checks | 17 passed; saved fixtures, no live inference |
| Existing Qwen path compatibility | 12 passed offline |
| Unchanged ML comparison | Exact predictions and probabilities on all 11 original replies |
| One direct GPT preflight | Correct pension-only interpretation; valid completed response |
| Original bank | 10/10 model-interpreted outcomes correct, plus one correct zero-call Help response |
| Financial candidates in the bank | Seven correct, zero wrong; none automatically confirmed |
| Contract rejection | Zero |
| Four conditional context turns | 4/4 correct; two candidates explicitly confirmed |
| Context controls / blocked inputs | 14/14 correct; zero ML or GPT calls |
| Live calls | 15 GPT: one preflight, ten bank, four context; 12 ML resolver calls |
| Choice recovery / retries / repairs | Zero |

The four context turns handled an uncertain wages-use answer, `Yes.` resolving it alongside pension, a wages-only correction retaining pension, and a fresh `Yes.` after `/new`. The last correctly requested clarification. Help was handled before inference; it is not evidence that the model itself understood Confusion.

| Existing case | Previous ML + Qwen result | New ML + GPT result |
|---|---|---|
| 01: wages saved, pension pays | Correct pension | Correct pension |
| 02: wages and pension pay | Correct multiple categories | Correct multiple categories |
| 03: two employers | Rejected inconsistent multiple-category output | Correct salary category |
| 04: benefits and family support | Correct support category | Correct support category |
| 05: brother pays rent/food | Rejected | Correct support category |
| 06: savings now, pension next year | Rejected | Correct withdrawals; pension stays future |
| 07: pension fund not drawn | Rejected | Appropriate missing-funding question |
| 08: no regular funding | Correct no-regular-source answer | Correct no-regular-source answer |
| 09: wages and pension received | Wrong multiple-category candidate | Appropriate actual-use question |
| 10: pension pays, wages use uncertain | Rejected | Targeted Undecided follow-up about wages |
| 11: pension meaning question | Correct pre-model Help | Correct pre-model Help |

Every previous correct Qwen outcome and all original reviewed GPT expectations were preserved by case ID. This compares recorded implementations on identical opened inputs; the Qwen suffix and provider differ, so it does not isolate model size or establish universal model superiority. The raw meanings, contract outcomes and accepted candidates were reviewed separately.

**ML handled 0/10 eligible first replies without GPT.** Its unchanged baseline was uncertain on these replies. This run demonstrates the combined wiring and GPT dialogue behaviour, not improved ML accuracy, lower latency or reduced GPT usage. Across the context sequence, only its fresh first replies used ML; follow-up and correction went straight to GPT.

## Boundaries and evidence

The [frozen protocol](protocol.json) recorded 74 source/input hashes before inference. All remained unchanged during the run. The [preservation audit](preservation.json) covers the main app, models/data, original GPT entry, shared prompt, validators, all 15 questions and prior evidence. Only provider selection and truthful audit labels were added to the existing combined session; no Qwen prompt instruction was copied into GPT.

All 15 safe transport receipts report exact `gpt-6.1-sol`, low reasoning, empty tools, `tool_choice: none`, `store: false`, completion and no retry/repair. The existing 30-second/1 MiB transport limits remain. Raw HTTP requests/responses and credentials were not published. Evidence includes only reviewed fictional cases, safe receipts and software/parity results; credential-pattern scanning found no matches.

This live run used the terminal's actual session/backend path through the bounded harness. It was not manually typed UI evidence, an unseen-text benchmark, a complete 15-question journey or main-app integration. The independent entry cannot save a profile. Account access and usage remain necessary; a future service failure stops it without fallback. No whole-product readiness claim follows.

- [Execution receipt](evidence/run/execution.json), [preflight](evidence/run/preflight.json), [bank outcomes](evidence/run/existing-summary.json), [context and controls](evidence/run/context-summary.json)
- [Independent source review](review-before.json) and [raw/transport review](review-after.json)
- [Offline GPT checks](evidence/gpt-software/software.json), [Qwen compatibility](evidence/qwen-compatibility/software.json), [ML parity](evidence/baseline-parity/summary.json)
- [Exact setup/launch instructions](../../demos/d5/GPT_ML_README.md) and [team handoff](../d5-semantic-method-handoff.md)
