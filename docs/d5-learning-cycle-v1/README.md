# D5 learning cycle

This cycle tests whether reviewed feedback can help the existing D5 ML option classifier accept a new savings expression without calling GPT or relaxing its checks. The original combined demo and main application remain unchanged.

**Current status: sample review pending. No candidate has been fitted or compared, and no live request has been made for this cycle.** See the [sixteen-row review](SAMPLE_REVIEW.md). Agreement with the implementation plan is not approval of sample labels that had not yet been written.

The offline tool is implemented. Its latest [pure software check](software-checks.json) passed 27 fixtures covering review, hash integrity, write-once phases and scoring. An initial 26-fixture run is retained; the second run followed a scoring repair found during static review. Neither run fitted or invoked an ML/LLM model.

## Business question

In the [recorded user-entered case](../d5-company-case-2026-10-13/CASE.md), `savings` produced an uncertain ML option set and required GPT. A later supplement added wages without losing savings. The user confirmed the combined answer, not the first savings candidate in isolation.

The learning target is deliberately narrower than the conversation: improve recognition of a complete first-turn funding answer. Contextual supplements remain with GPT. Receiving or holding money does not establish living-cost use, and model uncertainty does not establish customer indecision.

## Reviewed inputs and fixed recipe

- Eight AI-authored training additions: four savings, two wages, two savings-and-wages replies. They join the original 48 clear D5 training rows.
- Eight separately drafted AI-authored validation replies: four clear, two incomplete, one Undecided and one Confusion. They never enter fitting or calibration. Human review does not make them human-original independent evaluation.
- The original 40 D5 option-calibration rows, TF-IDF and logistic-regression settings, conformal algorithm and alpha remain fixed. The threshold is recalculated by that same algorithm; it is not manually chosen.
- Only the D5 option predictor is replaced in the isolated candidate. The intent predictor and the other fourteen questions retain their existing predictors.

The [overlap review](overlap-review.json) reports normalised equality and the nearest wording, without running a model. The [human review record](human-review.json) remains pending until the business owner explicitly reviews these exact dataset hashes. Historical evidence and [pre-change file hashes](preservation-before.json) are retained.

## Offline commands after review

The cycle tool provides three separate, write-once phases. It refuses pending review, altered frozen inputs, or an existing attempt at the same phase. An unsuccessful run is retained rather than overwritten.

From the repository root, after human review is recorded:

```bash
d5_python="$HOME/.venvs/investwise-d5/bin/python"
d5_cycle="$HOME/.local/state/investwise/d5-learning-v1/first-reviewed-cycle"
"$d5_python" -B demos/d5/learning_cycle.py freeze --review docs/d5-learning-cycle-v1/human-review.json --output "$d5_cycle"
"$d5_python" -B demos/d5/learning_cycle.py build --cycle "$d5_cycle"
"$d5_python" -B demos/d5/learning_cycle.py compare --cycle "$d5_cycle"
```

These commands are preparation instructions, not an execution receipt. The build retains the baseline's existing deterministic startup fitting and performs one additional D5 option fit. Comparison is ML-only; an escalation means **GPT required but not called**, not a correct GPT answer.

## What counts as improvement

The four new clear replies must have the correct raw option. At least one new savings reply must change from no correct baseline ML acceptance to a correct candidate ML acceptance through both singleton gates and the existing business veto. Other clear replies may still escalate. Existing correct raw interpretations and accepted outcomes must be preserved by case ID, with no new raw errors or wrong accepted financial answers.

Incomplete replies have no gold financial option. Their forced-choice option diagnostics are not option accuracy; an unsupported financial commitment is an error, even if the later veto blocks it. Confident Undecided or Confusion outcomes must match the business meaning; otherwise the model must retain uncertainty. The existing Help control is excluded from the interpreted-reply denominator.

The existing eleven examples are known preservation cases. The four existing context turns and controls are a separate replay/software check, not fresh semantic evidence. Frozen recordings must not be edited to fit changed candidate prompts. A first-turn improvement alone cannot enable the candidate demo.

## Conditional live demonstration and handoff

Only after the offline requirements pass will the manual `--ml-profile learning-v1` route be added. Baseline remains the default, and the existing replay stays on baseline. The candidate must use a real hash-bound identity, not a fixture identity.

The original and candidate will each receive the first successful new savings expression in case-ID order, the existing wages supplement, and explicit confirmation. Actual live counts and results will be recorded separately from the offline comparison. The anticipated total is three GPT requests across both sessions; it is not a measured saving yet. Service or semantic failure ends the attempt without retry.

Completion requires reviewed data, an actual model update, a new correctly accepted expression, a successful live conversation and reproducible handoff. Until those exist, this is preparation for a learning cycle, not a demonstrated learning success. No automatic training, whole-product readiness or general accuracy claim is made.
