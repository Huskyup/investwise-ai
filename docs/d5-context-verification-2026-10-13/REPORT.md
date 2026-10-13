# D5 context verification and delivery

13 October 2026 · Delivery: [Huskyup/investwise-ai, feature/all-question-ml-prototype](https://github.com/Huskyup/investwise-ai/tree/feature/all-question-ml-prototype).

**D5 handled a short follow-up and a targeted correction in one real terminal conversation.** Four model requests completed with the expected meanings. Two correct financial candidates were separately confirmed. A confirmation display issue found during that run was repaired afterwards and checked with the same saved outputs, without further inference.

## Business meaning and measured result

D5 identifies what currently pays living costs. Within one example, a follow-up answer should retain unaffected information; a correction should replace the conflicting detail. A new example must not inherit the previous customer's sources. The existing single interpreter now receives earlier raw user replies and the question just asked. No second interpretation stage, classifier, training or new financial rule was added.

The [pre-inference plan](plan.json) froze the runtime, four-call limit and expected outcomes before calling the service. The actual `demos/d5/demo.py chat` process used the existing eligible sign-in and GPT-6.1 Sol, low reasoning. Labels were not sent to the interpreter.

| Current input | Expected and observed raw meaning | Accepted financial candidate |
|---|---|---|
| `My pension pays some bills; I cannot tell whether my wages also do.` | Undecided; ask whether wages pay costs; no financial facts in the nonclear output | None |
| `Yes.` after that follow-up | Pension and wages both pay costs | `D5_MULTIPLE` |
| `/change`, then `My wages stay in savings.` | Wages are excluded; pension remains active | `D5_PENSION_PAYMENTS` |
| `/new`, then `Yes.` | Unclear reply with empty history; no inherited financial facts | None |

Results: **4/4 expected raw outcomes; 2/2 correct financial candidates; zero contract rejections or wrong accepted answers; zero choice recovery.** Fourteen control or blocked-input actions made zero interpretation calls, including Help, pause/resume, input while paused, confirmation, correction navigation, new example, stop/post-stop input and safety. Both confirmations reused the issued interpretation; no financial profile was saved. The paused family-support reply did not enter history. There was no service failure, inference retry, model substitution or output repair.

This is a bounded sequence using known source meanings and short contextual turns, not four independent customers or an unseen-text accuracy estimate. The retained [live transcript](live-transcript.txt), [summary](live-summary.json) and [four filtered records](records/) distinguish raw output, contract outcome, candidates and controls. The published transcript replaces the private output-directory path and removes trailing whitespace; the original local capture is retained.

## Confirmation repair after the live run

The live model understood `Yes.` correctly, but confirmation repeated the old quotation containing “I cannot tell”. The current result was therefore unclear on screen. The final runtime presents **current funding categories**, the latest reply, and historical supporting quotations separately. Approved categories are identified as questionnaire groups; exact source wording and exclusions remain visible. No inference or validation check changed.

The plan stated that unexpected behaviour should stop the run. This presentation issue was observed after the second call, but the remaining two planned calls were completed with the runtime unchanged. This is a procedural deviation; the run is not an unqualified plan-compliance pass. The final display repair was verified only by offline replay, not a second live run.

The final [offline checks](software-after-playback-repair.json) passed **20/20**, with credentials and network access forbidden. They cover provenance, immutable decision snapshots, context bounds, controls, confirmation and the exact four saved outputs. [Fixed playback](fixed-playback.json) records the repaired text. The earlier 19-check receipt remains separate. These software checks are not additional semantic successes.

## Four main-app files reviewed and completed

Two separate changes are delivered:

- `ai/pre_model_controls.py` and `tests/test_bounded_semantics.py`: recognise the missed first-person height-danger intent forms before financial interpretation; retain existing negation and quotation guards.
- `ai/conversation_engine.py` and `tests/test_ml_conversation.py`: when the existing ML option set contains two or three unresolved candidates, name their approved labels in the follow-up. Preserve safety/support/pause priority, D11's own-words explanation and the existing clarification cap. Do not label a follow-up as displayed when a hold intercepted it, or ask another option question after the cap.

The final affected selection passed **56/56** ([receipt](main-app-final-checks.json)). These are software checks using existing wording and resolver fixtures, with no service calls or semantic-bank expansion. Earlier 51- and 40-check runs overlap with this selection and must not be added as separate unique checks. This improves dialogue handling, not ML interpretation accuracy.

## Preserved scope and teammate use

GPT model/settings, the financial output contract and validators, all 15 questions, trained models, data and the default model factory are unchanged in this verification round. Main-app safety and follow-up behaviour changed as separately authorised. The D5 route remains a manually started, separate terminal. No cascade, deployment or meeting-material work is included. Historical evidence is retained; credentials and raw authentication records are excluded from publication. See the [preservation audit](preservation.json).

Close the old terminal, then run from your checkout:

```bash
git switch feature/all-question-ml-prototype
git pull --ff-only https://github.com/Huskyup/investwise-ai.git feature/all-question-ml-prototype
"$HOME/.venvs/investwise-d5/bin/python" demos/d5/demo.py chat
```

Existing installations need no dependency change. First-time teammates follow the [installation and personal sign-in instructions](../../demos/d5/README.md). Use `/change` for the same example and `/new` for a different example. Read and explicitly confirm the proposed meaning. New wording and account availability remain fallible; this evidence does not establish whole-product readiness.
