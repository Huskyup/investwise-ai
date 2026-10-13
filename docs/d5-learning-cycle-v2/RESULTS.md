# D5 v2 learning result

13 October 2026. The owner approved the exact 24 new sample meanings and uses. One candidate was built, fitting the existing D5 intent and option classifiers once each, and one fixed 27-case comparison completed. **Some raw predictions improved, but no new savings answer became independently acceptable to ML.** The candidate is not connected to the demo.

## Business question and measured result

D5 must recognise what currently pays living costs while separating money received or held from money spent. This cycle added clear funding contrasts and genuine Undecided/Confusion examples to the same two TF-IDF + logistic-regression classifiers. Architecture, hyperparameters and validation were retained; the isolated candidate's fitted coefficients changed.

| Measure | Original baseline | V2 candidate |
|---|---:|---:|
| Opened v1 validation: clear raw sources | 2/4 | 4/4 |
| Original eleven: clear raw sources | 4/7 | 4/7 |
| Fresh eight: clear raw sources | 2/4 | 2/4 |
| Fresh eight: raw intent, scored cases | 4/6 | 6/6 |
| Correct ML financial acceptances, all 27 | 0 | 0 |
| Wrong ML financial acceptances, all 27 | 1 | 0 |
| ML-handled eligible replies | 1/25, incorrect | 0/25 |
| Zero-model explanation controls | 2 | 2 |
| Actual GPT requests | 0 | 0 |

The fresh intent denominator excludes the two incomplete replies, which have no forced gold bucket. Financial source accuracy counts only clear replies. The baseline's one handled reply is an error, not an efficiency success. Candidate escalation was intercepted before GPT and does not count as GPT interpretation, useful model-authored follow-up or choice recovery.

## Why the target was not reached

Both new savings replies have the correct raw highest-scoring source and singleton Clarity intent. Their option sets nevertheless contain three and four categories:

- **D5-V2-LV-01:** food and electricity paid from savings; candidate set is `{MULTIPLE, SALARY, WITHDRAWALS}`.
- **D5-V2-LV-02:** savings transferred to a current account then spent on rent/bills; candidate set is `{MULTIPLE, PENSION_PAYMENTS, SALARY, WITHDRAWALS}`.

Neither can pass the unchanged single-option gate. The original intent ambiguity also remains on the two opened savings expressions: D5-LV-01 has two intent candidates, and D5-LV-02 has three. Better raw prediction does not establish that alternatives have been ruled out.

Two fresh source meanings are still wrong at raw level: **D5-V2-LV-03**, employer pay used to live on, predicts self-employment; **D5-V2-LV-04**, shop wages and savings both used, predicts wages only. The known mixed-source case D5-LV-04 improves to the correct mixed category, showing a development gain without establishing generalisation to the different fresh mixture.

The required preservation check also fails: **D5-STD-06**, savings pay bills and pension begins next year, returned to pension from the correct savings prediction of the previous v1 candidate. All 23 current-baseline correct raw case/axis checks are retained; 17/18 previous-v1 checks are retained. The combined 40/41 count contains duplicated reference checks, not 41 different examples; distinct case/axis preservation is 23/24. No prior correct accepted financial answer existed in these ML banks.

All 25 candidate-interpreted replies defer: 12 at the intent gate and 13 at the option gate. None reaches candidate business validation. Two explanation controls bypass both models. This result does not justify relaxing the validator or treating the top-scoring class as an answer.

## Newly observed baseline limitation

For D5-V2-LV-03, `I'm paid fortnightly by my employer, and that's the money I live on between paydays.`, the unchanged baseline forms a singleton self-employment prediction and the existing business veto accepts it. That is a wrong pending financial candidate; it is not a user-confirmed or saved answer. V2 keeps this reply unresolved, but its raw option is still wrong.

This new observation does not invalidate the fact that earlier specific GPT conversations completed; it does prevent claiming that the unchanged baseline or its validator guarantees correctness on new text. No repair to that validator or default was authorised or performed in this cycle.

## Fixed method and execution limits

The candidate used 80 intent-training rows and 64 clear option-training rows. Intent calibration retained the original 60 rows; option calibration retained the original 40. Alpha stayed 0.10. The derived intent threshold moved from `0.7564028548675875` to `0.7331168060984319`; the option threshold moved from `0.8721306352047945` to `0.8832800447772394`. These are unchanged-algorithm calibration results, not manually chosen settings. Several prediction sets grew.

The 19 opened baseline decisions matched their saved reference. Both classifiers fitted once; the previous candidate was not rerun. Before inference, 23 pure software fixtures passed with model imports and network activity blocked. Human approval preceded the 71-file freeze. No labels, samples, calibration settings or code were changed after results were seen.

The first-turn requirements failed, so there was no context replay, live service call, demo profile, second candidate or additional evaluation. All fifteen questions, original training/calibration files, GPT configuration, business checks and defaults remain unchanged. No answer was selected, confirmed or saved by this comparison.

## Per-case first-turn comparison

All V2 financial acceptances are empty. Raw financial options for incomplete/nonclear replies are diagnostic only and are not scored.

| Case | Expected | Baseline raw source | V2 raw source | V2 first blocker |
|---|---|---|---|---|
| D5-LV-01 | Savings | Self-employment | Savings | Intent set |
| D5-LV-02 | Savings | Savings | Savings | Intent set |
| D5-LV-03 | Wages | Wages | Wages | Option set |
| D5-LV-04 | Mixed | Savings | Mixed | Option set |
| D5-LV-05 | Incomplete | Not scored | Not scored | Intent set |
| D5-LV-06 | Incomplete | Not scored | Not scored | Option set |
| D5-LV-07 | Undecided | Not scored | Not scored | Intent set |
| D5-LV-08 | Confusion | Not scored | Not scored | Explanation control |
| D5-STD-01 | Pension | Wages | Wages | Option set |
| D5-STD-02 | Mixed | Mixed | Mixed | Option set |
| D5-STD-03 | Wages | Wages | Wages | Option set |
| D5-STD-04 | Support | Support | Support | Option set |
| D5-STD-05 | Support | Savings | Savings | Option set |
| D5-STD-06 | Savings | Pension | Pension | Option set |
| D5-STD-07 | Incomplete | Not scored | Not scored | Intent set |
| D5-STD-08 | No regular source | No regular source | No regular source | Intent set |
| D5-STD-09 | Incomplete | Not scored | Not scored | Option set |
| D5-STD-10 | Undecided | Not scored | Not scored | Intent set |
| D5-STD-11 | Confusion | Not scored | Not scored | Explanation control |
| D5-V2-LV-01 | Savings | Savings | Savings | Option set |
| D5-V2-LV-02 | Savings | Savings | Savings | Option set |
| D5-V2-LV-03 | Wages | Self-employment | Self-employment | Intent set |
| D5-V2-LV-04 | Mixed | Savings | Wages | Option set |
| D5-V2-LV-05 | Incomplete | Not scored | Not scored | Intent set |
| D5-V2-LV-06 | Incomplete | Not scored | Not scored | Intent set |
| D5-V2-LV-07 | Undecided | Not scored | Not scored | Intent set |
| D5-V2-LV-08 | Confusion | Not scored | Not scored | Intent set |

## Evidence and handoff

The [human approval](human-review.json), [frozen protocol](evidence/protocol.json), [build receipt](evidence/build.json), [full comparison](evidence/compare.json), [software checks](software-checks.json) and [separate evidence review](final-evidence-review.json) retain the bounded attempt. Both [intent](evidence/d5-intent-candidate.joblib) and [option](evidence/d5-option-candidate.joblib) artifacts are available for audit, not promoted demo use.

See [reproduction and existing launch commands](README.md), the [company case](COMPANY_CASE.md) and the [preservation audit](preservation-after.json). A successful learning flywheel remains incomplete: there is no new ML acceptance or candidate live success. There was no automatic tuning, training loop or expansion into other questions.
