# D5 option learning comparison

13 October 2026. One candidate fit and one frozen comparison completed after the business owner approved all sixteen sample meanings and uses. **The candidate did not add any correctly accepted ML answer, so it has not been connected to the live demo.** The working GPT demo, model architecture, validators, fifteen questions and defaults remain unchanged.

## Business meaning and measured result

D5 asks what currently pays living costs. The hypothesis was that a small set of reviewed savings and wage examples could help the existing option classifier recognise a new savings expression without GPT. The intent classifier was deliberately retained.

| Measure | Baseline | Candidate |
|---|---:|---:|
| New validation clear raw options | 2/4 | 2/4 |
| Existing clear raw options | 4/7 | 5/7 |
| Correct ML-accepted financial answers across 19 cases | 0 | 0 |
| ML-handled eligible replies | 0/17 | 0/17 |
| Wrong accepted financial answers | 0 | 0 |
| Zero-call explanation controls | 2 | 2 |
| Live GPT requests | 0 | 0 |

The seven eligible validation replies and ten eligible existing replies all require escalation. Escalation was intercepted before generation; it is not a successful GPT interpretation. Direct diagnostic intent and option predictions were also collected offline, separately from routing checks.

## Where the cycle stopped

The frozen requirements failed on the two raw source errors below and the absence of any newly accepted savings answer. No retraining, output repair, new phrases, context replay or live service call followed.

| Case | Business meaning | Observed limitation |
|---|---|---|
| D5-LV-01 | Money put aside over the years pays current rent, groceries and bills: savings | Both raw option predictions remain self-employment. The unchanged intent set is also `{clarity, undecided}`, so the route stops before option acceptance. |
| D5-LV-02 | Current household spending comes out of savings | Both raw option predictions are correctly savings, but the unchanged intent set is `{clarity, confusion}`. Option-only learning cannot remove this first gate. |
| D5-LV-04 | Wages pay rent and savings pay groceries/bills: mixed sources | Both raw option predictions remain savings only; the option set retains multiple categories, so no financial answer is accepted. |
| D5-STD-06 | Savings pay bills; pension begins next year | The raw source changes from pension to savings, but the candidate option set expands from two to four choices. This raw improvement does not become a usable ML answer. |

**None of the 19 cases reaches financial business validation.** Four of the 17 interpreted replies stop at the unchanged intent gate and thirteen at the option gate. This run therefore does not support blaming or weakening the validator.

The unchanged recalibration procedure uses the same 40 option-calibration rows and alpha 0.10. Its nonconformity threshold moves from `0.8721306352047945` to `0.8811152578401586`; these are derived values, not manual settings. The corresponding class-inclusion floor moves from approximately 0.12787 to 0.11888. Several option sets become larger, while financial acceptance still requires a singleton.

## Preservation and scope

All 17 recorded previously correct raw case/axis checks are preserved. Baseline had no accepted financial answers in this bank, so acceptance preservation is zero-to-zero. The raw Undecided-to-Clarity intent errors in D5-LV-07 and D5-STD-10 remain in both versions; there is no claim of zero raw False Clarity. Neither error becomes a resolver financial commitment or an accepted answer.

D5-STD-09, which only states that wages and pension payments are received, remains unresolved. No source-use answer is invented. Both explanation controls execute without model calls. No answer is selected, confirmed or saved by the comparator. The [byte-level preservation audit](preservation-after.json) confirms all 61 frozen files and seven unrelated user files are unchanged; among the original 407 tracked files, only the handoff was updated.

The eight validation expressions are AI-drafted and human-reviewed, with separate authoring and no use in training or calibration. They are now opened comparison material, not human-original independent testing. The original eleven are known preservation examples. No success on a training sentence is counted as generalisation.

## Exact first-turn comparison

Raw financial option labels are scored only for clear cases; incomplete and nonclear forced-choice option diagnostics have no gold option. All first-turn financial acceptances are empty.

| Case | Expected | Baseline raw option | Candidate raw option | First blocking stage / action |
|---|---|---|---|
| D5-LV-01 | Savings / withdrawals | Self-employment | Self-employment | Intent set is not singleton |
| D5-LV-02 | Savings / withdrawals | Savings / withdrawals | Savings / withdrawals | Intent set is not singleton |
| D5-LV-03 | Salary / wages | Salary / wages | Salary / wages | Option set is not singleton |
| D5-LV-04 | Multiple categories | Savings / withdrawals | Savings / withdrawals | Option set is not singleton |
| D5-LV-05 | incomplete | Not scored | Not scored | Option set is not singleton |
| D5-LV-06 | incomplete | Not scored | Not scored | Option set is not singleton |
| D5-LV-07 | undecided | Not scored | Not scored | Option set is not singleton |
| D5-LV-08 | confusion | Not scored | Not scored | Explanation control |
| D5-STD-01 | Pension payments | Salary / wages | Salary / wages | Option set is not singleton |
| D5-STD-02 | Multiple categories | Multiple categories | Multiple categories | Option set is not singleton |
| D5-STD-03 | Salary / wages | Salary / wages | Salary / wages | Option set is not singleton |
| D5-STD-04 | Benefits / support | Benefits / support | Benefits / support | Option set is not singleton |
| D5-STD-05 | Benefits / support | Savings / withdrawals | Savings / withdrawals | Option set is not singleton |
| D5-STD-06 | Savings / withdrawals | Pension payments | Savings / withdrawals | Option set is not singleton |
| D5-STD-07 | incomplete | Not scored | Not scored | Intent set is not singleton |
| D5-STD-08 | No regular source | No regular source | No regular source | Intent set is not singleton |
| D5-STD-09 | incomplete | Not scored | Not scored | Option set is not singleton |
| D5-STD-10 | undecided | Not scored | Not scored | Option set is not singleton |
| D5-STD-11 | confusion | Not scored | Not scored | Explanation control |

## Reproduction and decision

The [approved review](human-review.json), [frozen protocol](evidence/protocol.json), [one build receipt](evidence/build.json), [complete comparison](evidence/compare.json), [candidate artifact](evidence/d5-option-candidate.joblib) and [separate evidence review](final-evidence-review.json) retain the entire bounded result. The original private cycle is write-once. The artifact is retained for audit and explicitly authorised reproduction; it is not a supported demo model.

Use the existing baseline live demo for company conversations. No `learning-v1` launch route was added, and the four-context check and paired live dialogue were not entered. The [cycle instructions](README.md) explain how a separately requested reproduction can be made without overwriting these receipts.

This completes the authorised fit and comparison, but **does not complete a successful learning flywheel**. The demonstrated limitation is that option-only training cannot repair an upstream ambiguous intent decision, and these eight additions did not establish correct mixed-source generalisation. Any further learning change needs a separate decision; this run makes none.
