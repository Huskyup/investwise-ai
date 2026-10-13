# Company demo case: adding wages without losing savings

13 October 2026 · Live, manually entered D5 example · Runtime commit `ae2c0d2`

**The user entered a short answer, then supplemented it before confirming. D5 retained the earlier source, added the new source and asked for explicit confirmation of the updated answer.** This happened through the live browser, using two completed GPT requests and no recorded-output replay.

## What the audience should see

D5 asks: **What currently pays for your everyday living costs?**

| User input — exact wording | Observed response | Business interpretation |
|---|---|---|
| `savings` | Clarity; savings/withdrawals category; asks for confirmation and quotes `savings` | A short answer can use the current question as context. The user named savings as current funding. |
| `yes but 50% also come form my wages` | Clarity; multiple funding categories; retains savings and adds salary/wages; asks for confirmation again | The added source supplements the first answer. The typo `form` did not prevent correct interpretation in this example. |
| `/confirm` | D5 is confirmed in this session; no additional interpretation call | The user confirms the updated answer. No financial profile is saved. |

The final interpretation is **savings and wages fund current living costs**. The phrase `50%` is retained in the quoted reply; the system does not store a structured proportion, calculate a remaining savings percentage or assess financial sufficiency.

This is supplementation **before** the first explicit confirmation. There was no `/change` action, so this case does not demonstrate replacement of an already confirmed answer. The first candidate was pending; the updated mixed-source candidate was the one explicitly confirmed.

## Short presenter script

> “I answered ‘savings’, then added that 50% also came from wages. D5 kept the earlier savings information, added wages and asked me to confirm the combined answer. It handled my own wording in a live session, including the typo. The application controls confirmation; the model only proposes an interpretation. The percentage is quoted, not used for a financial calculation.”

If asked what ML contributed:

> “Our existing ML checked the first reply but remained uncertain, so GPT interpreted it. The next reply went directly to contextual GPT. This demonstrates the combined workflow and this contextual success; it does not show ML learning automatically or reducing GPT use here.”

## Exact observed confirmation

After the first reply:

```text
I understand your current living-cost funding as:
"savings"
Have I understood correctly?
```

After the added wages reply:

```text
Your latest reply: "yes but 50% also come form my wages"
Current funding categories: Salary or wages; Savings or investment withdrawals.
Your specific source wording is quoted below; these are the questionnaire groups.
Supporting wording from this example:
"savings"; "yes but 50% also come form my wages"
Have I understood correctly?
```

“Savings or investment withdrawals” is the questionnaire's grouped category label. The user's specific source is **savings**; the label is not evidence of investment withdrawals.

## Run it deliberately in the live demo

After following the [existing setup and own-account sign-in instructions](../../demos/d5/core/README.md), launch from your Huskyup checkout:

```bash
git switch feature/all-question-ml-prototype
git pull --ff-only https://github.com/Huskyup/investwise-ai.git feature/all-question-ml-prototype
sh demos/d5/run_core_demo.sh live
```

If another demo server uses port 8765, stop that server with Ctrl+C or deliberately choose a free port:

```bash
"$HOME/.venvs/investwise-d5/bin/python" -B demos/d5/core_demo.py --mode live --port 8766 --open
```

The page must say **LIVE · ML + GPT-6.1 Sol · low**. Start a fresh example, enter `savings` and submit. Before clicking Confirm answer, enter `yes but 50% also come form my wages` and submit. Review the combined interpretation, then click **Confirm answer** or submit `/confirm`. Do not click the optional guide: it belongs to a different, previously documented scenario.

These are presenter instructions, not additional execution performed for this publication. A new live run requires working account/service access and can differ. If the service fails, stop; do not present a saved transcript as a live answer. This case was not added to the replay sequence or evaluation banks.

## Evidence and limits

| Measure | Observed in this user-entered session |
|---|---|
| ML resolver checks | 1; uncertain first reply escalated |
| Completed live GPT requests | 2; exact `gpt-6.1-sol`, low reasoning |
| Raw meanings / contract / candidates | Savings then savings + wages; both passed the existing contract and became pending candidates |
| Explicit confirmations | 1; updated mixed-source answer confirmed |
| Confirmation model calls | 0 |
| Recorded outputs / retries / output repairs | 0 / 0 / 0 |
| Provider request elapsed times | Approximately 6.5 s and 10.2 s; not a latency benchmark or complete UI timing |
| Saved financial profiles / model training | 0 / 0 |

The [curated evidence](evidence.json) includes exact authorised wording, displayed responses, raw semantic outputs, contract outcomes, safe provider receipt fields and hashes of the five original local records. It excludes credentials, browser access tokens, private filesystem paths, HTTP bodies and unrelated session contents. The user explicitly authorised publishing this demo conversation. It is not treated as a verified statement of their finances.

This is a successful live example of user-entered phrasing, not an independent held-out benchmark or a general accuracy/typo-robustness estimate. It did not exercise Undecided, Confusion, safety, stop, separate save consent or the complete fifteen-question journey. A [separate, earlier live check](earlier-live-check.json) covered the existing eighteen-action guide; its four GPT calls must not be combined with this user's two-call result.

**Publication only:** no new inference, tests, model changes, validation changes, training, runtime changes, questions or default changes were introduced to prepare this case. Models did not learn from these replies automatically. [Preservation record](publication.json) · [Independent documentation review](review.json) · [Technical handoff](../d5-semantic-method-handoff.md).
