# D5 v3 measured result

**No new independent ML acceptance was obtained. The single candidate comparison failed and stopped.** One option model was fitted; the existing v2 intent artifact was reused without modification. All 27 replies are previously opened, training-excluded examples.

## Business meaning → failure → change → counterexample → result

D5 asks which sources currently pay living costs. Holding or receiving money alone is insufficient; a pension beginning next year is not a current payer. The financial meaning should remain the same when “everyday expenses” becomes “day-to-day expenses”. Prior diagnostics showed source predictions affected by ordinary spending vocabulary, and broad calibrated source sets prevented acceptance.

The approved repair changed 15 of the existing 64 option-training sentences: eight distributed “current living expenses” across all eight categories, and seven distributed “day-to-day” wording. Forty-nine sentences remained verbatim. Architecture, hyperparameters, labels, business validation, calibration data/algorithm/alpha and two singleton requirements stayed unchanged. This was one data hypothesis, not a promise that surface wording alone could teach compositional meaning.

The counterexample is `D5-LV-01`: “I'm living off the money I put aside over the years, using it for the rent, groceries and bills.” Saved v2 correctly ranked savings first; v3 ranks self-employment first. Its v3 probabilities are 0.153969 self-employment versus 0.153312 savings. The preservation check catches this small but real reversal. It is not accepted because the intent gate remains uncertain.

## Raw predictions and accepted candidates

| Bank / measure | Unchanged baseline | Saved v2 | V3 |
|---|---:|---:|---:|
| First opened bank: correct clear source | 2/4 | 4/4 | 3/4 |
| Original examples: correct clear source | 4/7 | 4/7 | 5/7 |
| Second opened bank: correct clear source | 2/4 | 2/4 | 2/4 |
| Total correct clear source | 8/15 | 10/15 | 10/15 |
| Correct independent financial candidates | 0 | 0 | 0 |
| Wrong pending financial candidates | 1 | 0 | 0 |

The baseline's wrong pending candidate is the previously recorded employer-pay → self-employment case, `D5-V2-LV-03`; it was never selected, confirmed or saved. V3 avoids committing but now ranks savings, which is also wrong. The other required unresolved clear case, `D5-V2-LV-04`, describes job pay plus savings and still ranks wages alone. Across both opened banks, five of eight clear raw sources are correct; the gate required eight.

V3 restores `D5-STD-06` (“I use my savings for bills. My pension starts next year.”) to savings, recovering v1's result. That gain offsets the lost `D5-LV-01` in aggregate accuracy, but does not meet per-case preservation. Preservation is **67/68 reference checks**, covering **27/28 distinct case-and-axis requirements**. These are not 68 separate cases. Repeated blocking-gate entries refer to overlapping requirements, not separate new failures.

All 25 eligible replies escalate before GPT: **12 at intent, 13 at option**. Two Help controls are separate and made zero model calls. The candidate reaches business validation on **zero** replies; there are therefore no v3 business-validator rejections or accepted candidates to report. Zero wrong acceptance here results from complete escalation, not useful independent handling. All saved v3 raw intent records match v2, with 17/19 scored intent predictions correct; two inherited raw False Clarity cases remain (`D5-LV-07`, `D5-STD-10`). No new raw intent error was introduced.

Incomplete holding/receipt replies remain without a financial candidate. No reply was selected, confirmed or saved, and no GPT call was made. This does not turn the inherited raw intent errors into successes.

## Why the two target savings replies still fail

| Case | Intent set | Source probabilities at or above cutoff | Accepted? |
|---|---|---|---|
| D5-V2-LV-01: weekly savings transfer for food/electricity | Clarity only | savings 0.198244; multiple 0.160202; wages 0.125221 | No: three source candidates |
| D5-V2-LV-02: monthly savings transfer for rent/bills | Clarity only | savings 0.159542; multiple 0.153794; pension 0.136198; wages 0.132932 | No: four source candidates |

The original calibration procedure recomputed the option nonconformity threshold as **0.8773703613464233**; thus each source with probability at least **0.1226296386535767** remains in the set. Saved v2's inclusion cutoff was 0.1167199552227606. The numerical threshold changes naturally with the fitted model; the rule and alpha were not changed or relaxed. These classifier probabilities are scores used by the existing procedure, not a guarantee of semantic correctness.

The reviewed wording change did not separate the right category from competing categories enough. It also left the previously problematic employer and mixed-source meanings unresolved. This run does not prove that the architecture can never improve, but it shows this particular change is insufficient to complete the requested flywheel. No threshold manipulation, second fit, added samples or further diagnostics using model predictions followed.

## Execution and preservation

- Software: one run, 19 passed, 0 failed/errors/skipped; pure fixtures, not language evaluation.
- Freeze: 85 files bound before the candidate build.
- Candidate: intent fit/calibration 0/0; option fit/calibration 1/1. Both artifacts saved and hash-verified. The unchanged baseline startup reconstructs its original predictors separately.
- Comparison: one run, 27/27 baseline semantic decision-field records matched prior evidence; this does not establish equality of every probability or output byte; earlier candidates were not rerun.
- Conditional context replay, live dialogue, runtime profile and model promotion: not performed.
- Existing model/data/source/default files and other work: preserved; only the handoff is intentionally updated among previously tracked files, as detailed in the preservation audit.

Identity: `8f96f9db7cdabf5f2ae52321b355557bef5ab02491738a64796a57b7dac00e0a`.

Option artifact SHA-256: `f0a24bb1632a224a9b3007796929025e90397a0e997b2a2b42a7982375187c2b`.

Reused intent SHA-256: `24086a0f0efe05eb3a69f6ef852c4714cd5e8f954584fa7c210f3cc643402831`.

Full probabilities, raw sets, routing reasons, validation status and accepted-candidate fields remain in [compare.json](evidence/compare.json). [PER_CASE.md](PER_CASE.md) presents every case, including unchanged failures. The [stop receipt](evidence/STOP.json) records the incomplete flywheel.
