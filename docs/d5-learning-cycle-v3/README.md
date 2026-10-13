# D5 learning cycle v3 — reviewed wording repair, stopped after one comparison

13 October 2026. **Approved, frozen, fitted once and compared once. Required first-turn gates failed. No contextual replay, GPT dialogue or candidate demo profile followed. The learning flywheel is not complete.**

The owner approved the [15 before/after edits and all 64 rows](SAMPLE_REVIEW.md). The [human approval record](human-review.json) binds the exact displayed table and proposal. Pending-status text in the frozen review packet, earlier request and source-preparation records is historical; this separate approval supersedes it without changing those bytes.

The hypothesis was narrow: distribute ordinary spending phrases across existing source categories to reduce accidental TF-IDF associations. No row, source, spending proportion or frequency was added. The human business owner reviewed the AI-authored fictional meanings and uses. These are not the owner's financial information or human-original independent evaluation.

## Actual execution

- One software gate: 19 pure integrity/scoring fixtures passed; model imports, deserialisation, network and subprocesses blocked. Software success is not semantic accuracy.
- One freeze: 85 source/data/reference files recorded before candidate work.
- Saved v2 intent copied byte-for-byte, with its vocabulary and threshold. No intent fit or recalibration.
- One option fit on 64 approved rows; unchanged TF-IDF, logistic regression, seed and hyperparameters. One recalibration with the original forty rows, algorithm and alpha 0.10.
- One comparison: original eleven plus both opened eight-case banks. Baseline parity matched the semantic decision fields of all 27 prior records, not every probability or output byte. Earlier candidates' saved predictions were not rerun.
- Zero GPT requests. The unchanged baseline startup reconstructs its original fifteen intent and fifteen option predictors; these routine baseline fits are separate from the single candidate option fit.

**Zero correct independent financial acceptances; both target savings replies retain multiple candidates; one previous raw savings success regressed.** See [results](RESULTS.md), [all cases](PER_CASE.md), [company account](COMPANY_CASE.md) and [stop receipt](evidence/STOP.json). Correct argmax is not acceptance through both singleton gates.

## Evidence and reproduction

Use only [Huskyup/investwise-ai](https://github.com/Huskyup/investwise-ai/tree/feature/all-question-ml-prototype). Existing installation instructions remain in the [D5 handoff](../d5-semantic-method-handoff.md). This attempt used Python 3.12.14, scikit-learn 1.9.1, NumPy 2.5.3, SciPy 1.18.1 and joblib 1.6.0. Exact runtime, source and data identities are in [protocol.json](evidence/protocol.json). No dependency was changed.

For a fresh checkout/environment (omit environment creation if already installed):

```bash
git clone --branch feature/all-question-ml-prototype https://github.com/Huskyup/investwise-ai.git
cd investwise-ai
python3.12 -m venv "$HOME/.venvs/investwise-d5"
"$HOME/.venvs/investwise-d5/bin/python" -m pip install -r demos/d5/requirements.txt
```

The frozen numerical environment is Python 3.12.14; a different Python patch version is a disclosed reproduction difference. Offline comparison needs no sign-in or API credentials. Live use retains the existing account setup in the demo guide.

From the repository root, these are the exact commands used, each run once and checked before continuing:

```bash
d5_python="$HOME/.venvs/investwise-d5/bin/python"
d5_cycle="$HOME/.local/state/investwise/d5-learning-v3/first-reviewed-cycle"
"$d5_python" -B demos/d5/learning_cycle_v3.py freeze --review docs/d5-learning-cycle-v3/human-review.json --output "$d5_cycle"
"$d5_python" -B demos/d5/learning_cycle_v3.py build --cycle "$d5_cycle"
"$d5_python" -B demos/d5/learning_cycle_v3.py compare --cycle "$d5_cycle"
```

The comparison exited **2**: it completed but failed required gates. It was not retried. These commands document reproduction, not permission to resume this stopped attempt. Existing directories and phase markers block repeat execution. A separately authorised reproduction must retain the original evidence and use a new external directory; it is not an automatic tuning loop. Its new protocol records its own timestamp/runtime identity, so the complete receipt identity need not equal this original.

Read saved results without model loading, fitting, prediction or a service call:

```bash
python3 -B -c 'import json; from pathlib import Path; r=json.loads(Path("docs/d5-learning-cycle-v3/evidence/compare.json").read_text()); print(json.dumps({k:r[k] for k in ("first_turn_gates_passed","baseline","candidate","blocking_gates","actual_gpt_calls")}, indent=2))'
```

The nine files in `evidence/` are byte-identical copies of the external completed cycle: both trusted artifacts, protocol, freeze, phase markers, build, comparison and stop. [Copy hashes](evidence-copy.json) bind every file. [Software evidence](software-checks.json), [preservation](preservation-after.json) and [independent result review](result-review.json) are separate. All 27 replies are opened and outside training; there is no fresh independent accuracy estimate. Never load model artifacts from an untrusted source.

## Existing demo remains unchanged

```bash
"$HOME/.venvs/investwise-d5/bin/python" -B demos/d5/gpt_ml_demo.py chat
```

This launches the existing baseline ML + GPT demo. **There is no `--ml-profile learning-v3` interface.** The failed candidate is for audit only. Browser, fixed replay and GPT-only entries, all fifteen questions, validators, controls, confirmation and save-consent logic remain unchanged. Previous live evidence is preserved; service availability was not checked here.

Conditional stages were not run: the original four context turns and controls; opt-in candidate selection; paired baseline/candidate live savings → wages → confirmation. No promotion or whole-product readiness claim follows from this attempt.
