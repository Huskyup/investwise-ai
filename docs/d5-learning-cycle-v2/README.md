# D5 learning cycle v2

This isolated cycle tests whether reviewed contrast examples can improve both existing D5 classifiers, so that at least one new savings answer is accepted by ML through the original gates. It preserves the normal app, all fifteen questions, business validation and the current ML + GPT demonstration.

**Status: all 24 new rows approved; one two-head build and one 27-case comparison completed.** The candidate did not gain any independently accepted savings reply and lost a previous raw success, so no context replay, live request or candidate launch interface followed. Opened clear raw sources improved 2/4 to 4/4 and fresh raw intent improved 4/6 to 6/6; fresh clear sources stayed 2/4. See [full results](RESULTS.md) and the [company case](COMPANY_CASE.md).

## Business target and data

The [first cycle](../d5-learning-cycle-v1/RESULTS.md) corrected one raw source prediction but added no accepted answer. Its new savings replies stopped at the unchanged intent gate; one option set also grew from savings alone to savings plus multiple categories. V2 addresses both existing heads through additional data, with no extra model or decision stage.

The eight previously approved clear training rows are retained. Sixteen new training rows contain eight clear contrasts (four savings, two wages, two mixed), four genuine Undecided answers and four Confusion answers. An additional eight validation rows are separately AI-authored without seeing the new training wording or prediction results: two savings, one wage, one mixture, two incomplete, one Undecided and one Confusion. The owner explicitly approved these exact rows before the 71-file freeze. The [hash-bound human record](human-review.json) is authoritative; draft JSON status metadata remains unchanged to preserve reviewed bytes.

The saved `savings` phrase is training material, not an unseen success. The context-dependent `yes but 50% also come form my wages` remains a dialogue supplement, never a standalone wage training label. All material is fictional; it does not establish the owner's personal finances.

## Fixed build and comparison

V2 trains the D5 intent head once on 80 rows (56 original + 8 retained + 16 new) and the D5 option head once on 64 clear rows (48 original + 8 retained + 8 new). TF-IDF, logistic regression, seed, balanced class weighting and other hyperparameters remain fixed. The original 60 intent-calibration and 40 option-calibration rows retain alpha 0.10 and the same algorithm. Computed thresholds can change; there is no manual threshold selection or guarantee of narrower sets. Other fourteen predictors are retained.

A single offline comparison uses 19 opened regression cases plus the eight new validation cases, identically for baseline and candidate. Its acceptance policy requires preservation of correct raw results from both baseline and the previous failed candidate by case ID, including the savings-before-pension improvement; V2 failed that requirement on D5-STD-06. All four old validation clear source predictions and all four new clear source predictions must be correct. At least one fresh savings case must change from baseline escalation to a correct, validated ML acceptance with a real receipt. Incomplete answers must not become financial commitments; no new raw error, False Clarity or wrong acceptance is allowed. Controls remain separate from ML successes.

The candidate is stored as two hash-bound artifacts. The inherited baseline, prior receipts, data, recipe, validators and new review are frozen. Build and comparison phases are write-once, offline, and stop before GPT escalation. No previous candidate is rerun, and no unsuccessful attempt is overwritten or automatically retried.

## Reproduction and existing demo

Use the existing Python 3.12.14 environment and [pinned installation](../../demos/d5/README.md#install-once). No account login is needed for the offline cycle. The [published build](evidence/build.json) and [comparison](evidence/compare.json) retain the completed attempt; 23 [pure software checks](software-checks.json) passed before it. For a separately requested reproduction, use a new external directory and the frozen environment. Reproduction is not additional independent evaluation:

```bash
d5_python="$HOME/.venvs/investwise-d5/bin/python"
d5_cycle="$HOME/.local/state/investwise/d5-learning-v2/independent-reproduction-01"
"$d5_python" -B demos/d5/learning_cycle_v2.py freeze --review docs/d5-learning-cycle-v2/human-review.json --output "$d5_cycle"
"$d5_python" -B demos/d5/learning_cycle_v2.py build --cycle "$d5_cycle"
"$d5_python" -B demos/d5/learning_cycle_v2.py compare --cycle "$d5_cycle"
```

The commands describe reproduction; linked receipts document the actual single attempt. The original private cycle directory remains write-once and must not be overwritten. A pending or changed review cannot start a cycle. `compare` returned exit code 2 for failed semantic gates, not a runtime crash. No repetition was performed.

The first-turn requirements failed. The four-turn context check, paired live dialogue and `--ml-profile learning-v2` interface were therefore not entered. Both saved artifacts are retained for audit only. No new version is enabled in the terminal or browser.

Keep the existing ML + GPT terminal command unchanged:

```bash
"$HOME/.venvs/investwise-d5/bin/python" -B demos/d5/gpt_ml_demo.py chat
```

The existing browser uses `sh demos/d5/run_core_demo.sh live`; `replay` remains a labelled recording. See the [technical handoff](../d5-semantic-method-handoff.md). Live use requires the user's existing access; this cycle made no service calls and does not confirm present availability. The newly observed wrong baseline pending candidate is described prominently in [the result report](RESULTS.md); preserved defaults do not mean arbitrary new wording is reliable.

## Delivery boundary

Publication is limited to this cycle's code, reviewed data, resulting evidence and handoff in Huskyup/investwise-ai on feature/all-question-ml-prototype. Preserve unrelated local work and old evidence. The [pre-change hashes](preservation-before.json) record that boundary.

A completed learning flywheel requires explicit review, actual model updates, at least one new correct ML acceptance, successful live conversation and reproducible handoff. Preparatory code, tests or correct training answers alone do not satisfy it. Existing historical label limitations are not silently rewritten in this data-only cycle, and no whole-product reliability or automatic learning is claimed.
