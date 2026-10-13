# Qwen-only category instruction: target error persists

13 October 2026 · Huskyup `feature/all-question-ml-prototype`

**The requested prompt change was implemented, but did not fix the two-employer error.** The existing 11 examples were each checked once: four correct financial candidates, one wrong financial candidate, five contract rejections and one correct zero-call Help response. Thus five of 11 dialogue outcomes matched; four of ten interpreted replies met the expected outcome. The four context turns were not run. There were no retries, extra inputs, output repairs or changes between cases.

## What changed

`demos/d5/local_transport.py` appends one general instruction to Qwen's local prompt: for an established complete Clarity answer, choose the final option from the distinct current self-funding categories in its facts. One category maps to itself; two or more map to MULTIPLE. Count categories, not employers or payers. The instruction explicitly retains exclusions, the explicit-absence requirement for NO_REGULAR, incomplete answers, Undecided, Confusion and abstention. It forbids changing supported facts to fit an option.

This repeats the existing business standard at final option selection; it is not a new financial rule. The original GPT prompt, both models and their weights, schema, strict validator, ML routing, data, all 15 questions and main-app default are unchanged. The suffix has its own version and hash. No wrong output is automatically relabelled.

The verification runner adds a separate `prompt-check` round. As requested, it completes the existing 11 once, then permits the existing four context turns only if every case matches. A runtime failure still stops immediately. The older preflight/first-failure mode is preserved. No additional preflight generation was made in this round.

## Existing examples: raw meaning and accepted result

| Case | Raw interpretation | Contract / dialogue result |
|---|---|---|
| 01: wages saved, pension pays | Correct pension-only meaning | Correct pending candidate |
| 02: wages and pension pay | Correct two-category meaning | Correct pending candidate |
| 03: two employers | One correct salary fact, wrong MULTIPLE option | Rejected; target error remains |
| 04: benefits and family support | Correct single support category | Correct pending candidate |
| 05: brother sends money for costs | Support recognised, but incorrectly assigned to `owner=other` | Rejected; expected support candidate lost |
| 06: savings pay, pension future | Savings incorrectly labelled OTHER_REGULAR | Rejected; expected withdrawals candidate lost |
| 07: pension fund not drawn | Wrong Undecided output with financial facts and option | Rejected; required missing-use follow-up not delivered |
| 08: explicit no regular source | Correct absence of current regular funding | Correct pending candidate |
| 09: wages and pension received | Receipt incorrectly treated as expenditure | **Wrong MULTIPLE candidate accepted for confirmation** |
| 10: unsure whether wages also pay | Undecided bucket, but illegal financial option/facts | Rejected; required wage-use follow-up not delivered |
| 11: pension terminology question | Pre-model Help | Correct explanation; zero ML/Qwen calls |

No candidate was confirmed or saved. This does not excuse case 09: it is a wrong accepted interpretation, and demonstrates that internally consistent output can still misread the customer's meaning.

## What the comparison establishes

Business meaning is unchanged: two employers belong to one salary category. The earlier failure combined a correct salary fact with a wrong MULTIPLE option. The proposed local instruction explicitly linked those fields. The new request contains that instruction, with unchanged user data and schema, but Qwen returned the **same raw output** on case 03. The instruction was delivered and was insufficient.

The only earlier local results were cases 01–03. Their raw outputs are byte-identical: the two prior correct candidates were preserved and the target failure was not recovered. Cases 04–11 are newly measured for this local model, so their failures cannot be described as regressions caused by the suffix. Against the earlier saved GPT outcomes, cases 03/05/06 lose correct financial candidates and cases 07/09/10 lose the expected follow-up behaviour. There is no demonstrated semantic improvement from this change.

Ten eligible replies each used one ML pass and one Qwen generation; Help used neither. ML handled 0/10 eligible replies, so no efficiency benefit is established. The completed requests stayed within the existing local worker boundaries. All frozen files remained unchanged during inference, and old evidence remains intact.

## Team handoff

The local entry remains an explicit development route, **not a company-demo replacement**. Keep using the previously demonstrated GPT terminal for that conversation. [Both launch commands and setup instructions](../../demos/d5/LOCAL_README.md) remain available. The branch contains the attempted instruction and its failed acceptance evidence; it must not be described as a successful fix or general free-text reliability result.

Five affected offline checks passed before inference, using existing saved outputs and mocked preparation only. Independent read-only review verified the new prompt delivery, target response, full-bank results and conditional context stop. No new semantic examples, credentials, cloud calls, downloads, model training or wider test suite were added.

Evidence: [frozen protocol and instruction](protocol.json), [offline checks](evidence/software.json), [all 11 results](evidence/run/existing-summary.json), [execution receipt](evidence/run/execution.json), [stop receipt](evidence/run/STOP.json), [independent review and preservation comparison](review.json), [file preservation audit](preservation.json). The [previous local round](../d5-local-ml-qwen-2026-10-13/REPORT.md) is unchanged.
