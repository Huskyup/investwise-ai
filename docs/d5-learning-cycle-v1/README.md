# D5 learning cycle

This cycle tests whether reviewed feedback can help the existing D5 ML option classifier accept a new savings expression without calling GPT or relaxing its checks. The original combined demo and main application remain unchanged.

**Current status: business review approved; one candidate fit and one 19-case comparison completed. The required first-turn improvement was not achieved.** New clear raw options remain 2/4; existing clear raw options improve from 4/7 to 5/7, but correct ML financial acceptances remain zero. No context replay or live request followed. See the [complete result and reasons](RESULTS.md).

Before sample approval, the offline tool was implemented. Its latest [pure software check](software-checks.json) passed 27 fixtures covering review, hash integrity, write-once phases and scoring. An initial 26-fixture run is retained; the second run followed a scoring repair found during static review. Neither software run fitted or invoked an ML/LLM model. These checks were not repeated during the subsequent fit and comparison.

## Business question

In the [recorded user-entered case](../d5-company-case-2026-10-13/CASE.md), `savings` produced an uncertain ML option set and required GPT. A later supplement added wages without losing savings. The user confirmed the combined answer, not the first savings candidate in isolation.

The learning target is deliberately narrower than the conversation: improve recognition of a complete first-turn funding answer. Contextual supplements remain with GPT. Receiving or holding money does not establish living-cost use, and model uncertainty does not establish customer indecision.

## Reviewed inputs and fixed recipe

- Eight AI-authored training additions: four savings, two wages, two savings-and-wages replies. They join the original 48 clear D5 training rows.
- Eight separately drafted AI-authored validation replies: four clear, two incomplete, one Undecided and one Confusion. They never enter fitting or calibration. Human review does not make them human-original independent evaluation.
- The original 40 D5 option-calibration rows, TF-IDF and logistic-regression settings, conformal algorithm and alpha remain fixed. The threshold is recalculated by that same algorithm; it is not manually chosen.
- Only the D5 option predictor is replaced in the isolated candidate. The intent predictor and the other fourteen questions retain their existing predictors.

The [overlap review](overlap-review.json) reports normalised equality and the nearest wording, without running a model. The [human review record](human-review.json) binds the owner's explicit approval of all sixteen rows to their exact dataset hashes. The draft JSON files retain their original pending-review metadata to preserve their bytes; this separate approval record governs the freeze. The eight validation replies are now opened comparison material. Historical evidence and [pre-change file hashes](preservation-before.json) are retained.

## Reproduction commands

The cycle tool provides three separate, write-once phases. It refuses pending review, altered frozen inputs, or an existing attempt at the same phase. An unsuccessful run is retained rather than overwritten.

The executed attempt and its [frozen recipe](evidence/protocol.json), [build receipt](evidence/build.json), [comparison](evidence/compare.json) and candidate artifact are published under `evidence/`. No repetition is needed to use the existing demo. For an explicitly requested independent reproduction, use Python 3.12.14 and the unchanged pinned dependencies below, then select a **new external directory**. Do not overwrite the original attempt or treat reproduction as another independent evaluation.

From the repository root:

```bash
d5_python="$HOME/.venvs/investwise-d5/bin/python"
# Install only if this separate environment is not already present.
python3.12 -m venv "$HOME/.venvs/investwise-d5"
"$d5_python" -m pip install -r demos/d5/requirements.txt
d5_cycle="$HOME/.local/state/investwise/d5-learning-v1/independent-reproduction-01"
"$d5_python" -B demos/d5/learning_cycle.py freeze --review docs/d5-learning-cycle-v1/human-review.json --output "$d5_cycle"
"$d5_python" -B demos/d5/learning_cycle.py build --cycle "$d5_cycle"
"$d5_python" -B demos/d5/learning_cycle.py compare --cycle "$d5_cycle"
```

These commands describe reproduction; the linked receipts document the single actual attempt. `compare` returns exit code 2 when the frozen semantic gates fail, as happened here; this does not mean the comparison crashed. No credential or GPT connection is used by these phases. The build retains the baseline's existing deterministic startup fitting and performs one additional D5 option fit. Comparison is ML-only; an escalation means **GPT required but not called**, not a correct GPT answer.

## What counts as improvement

The four new clear replies must have the correct raw option. At least one new savings reply must change from no correct baseline ML acceptance to a correct candidate ML acceptance through both singleton gates and the existing business veto. Other clear replies may still escalate. Existing correct raw interpretations and accepted outcomes must be preserved by case ID, with no new raw errors or wrong accepted financial answers.

Incomplete replies have no gold financial option. Their forced-choice option diagnostics are not option accuracy; an unsupported financial commitment is an error, even if the later veto blocks it. Confident Undecided or Confusion outcomes must match the business meaning; otherwise the model must retain uncertainty. The two explanation controls (new D5-LV-08 and existing D5-STD-11) are excluded from the interpreted-reply denominator.

The existing eleven examples are known preservation cases. The four existing context turns and controls are a separate replay/software check, not fresh semantic evidence. Frozen recordings must not be edited to fit changed candidate prompts. A first-turn improvement alone cannot enable the candidate demo.

## Demo status and handoff

The first-turn gate failed, so the four-context check and paired live demonstration were not entered. No `--ml-profile learning-v1` interface was added. The saved candidate is an audit artifact, not a supported demo model. Both new savings replies stopped at the unchanged intent gate; none of the nineteen cases reached financial business validation. This evidence does not justify weakening that validator.

The existing baseline terminal remains the same, with no model switch required:

```bash
"$HOME/.venvs/investwise-d5/bin/python" -B demos/d5/gpt_ml_demo.py chat
```

For the existing browser entry, use `sh demos/d5/run_core_demo.sh live`; `replay` remains a labelled fixed walkthrough. See the [installation and sign-in guide](../../demos/d5/README.md#install-once) and [technical handoff](../d5-semantic-method-handoff.md). Live use still depends on service access; this offline cycle did not recheck availability or earlier GPT successes.

Completion of a successful flywheel requires reviewed data, an actual model update, a new correctly accepted expression, a successful live conversation and reproducible handoff. This cycle has the review, update and measured comparison, but no new accepted expression or candidate live success. No automatic training, efficiency improvement, whole-product readiness or general accuracy claim is made.
