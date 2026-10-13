# D5 semantic interpretation technical handoff

Updated 13 October 2026 · `feature/all-question-ml-prototype`

Maintained delivery repository: [Huskyup/investwise-ai](https://github.com/Huskyup/investwise-ai/tree/feature/all-question-ml-prototype). Use the explicit repository URL below when updating an older checkout whose `origin` may point elsewhere.

## D5 learning cycle: one completed fit and comparison

The business owner approved all sixteen sample meanings and uses, then the [D5 learning cycle](d5-learning-cycle-v1/README.md) froze its data and recipe. One isolated D5 option classifier was fitted using the original 48 training rows plus eight reviewed additions, with unchanged architecture, settings and forty-row recalibration procedure. One comparison covered the eight training-excluded expressions and original eleven examples. The AI-authored, human-reviewed expressions are now opened material, not human-original independent testing.

**Measured result: existing clear raw options improved from 4/7 to 5/7, new clear raw options stayed 2/4, and correct ML financial acceptances stayed 0.** All seventeen eligible replies still required GPT escalation, which was intercepted without any GPT request. Both new savings replies stopped at the unchanged intent gate; none of the nineteen cases reached business validation. All seventeen previously correct raw case/axis checks were preserved; two existing raw Undecided-to-Clarity errors remain. See the [full results and counterexamples](d5-learning-cycle-v1/RESULTS.md), [approved review](d5-learning-cycle-v1/human-review.json) and [saved artifact and receipts](d5-learning-cycle-v1/evidence/).

The required first-turn improvement did not pass, so no additional training, context replay, live dialogue or candidate launch interface followed. The original intent classifier, other fourteen questions, business checks, GPT configuration and defaults are unchanged. Keep using the existing launch commands below; the candidate is retained for audit only. This completed bounded learning attempt does not demonstrate a successful learning flywheel or an ML efficiency gain.

## Latest evidence: the user's own successful live conversation

The [company case and presenter script](d5-company-case-2026-10-13/CASE.md) document the user's manually entered `savings` → `yes but 50% also come form my wages` → `/confirm` conversation. D5 retained savings, added wages, changed the pending option from `D5_WITHDRAWALS` to `D5_MULTIPLE`, and requested confirmation of the combined answer. The final confirmation used no model call and saved no financial profile.

**Observed: one ML check, two completed live GPT requests, zero replayed outputs.** ML was uncertain on the first reply; GPT interpreted both replies. This is supplementation before confirmation, not a `/change` correction or automatic ML learning. The quoted 50% is not a structured allocation or financial calculation, and the grouped withdrawals category does not assert investment withdrawals. The case demonstrates this live wording, not universal free-text reliability. Exact transcript, raw meanings, accepted candidates and safe receipts are in the [curated evidence](d5-company-case-2026-10-13/evidence.json).

Before that user session, the separately authorised retry of the existing browser guide completed all eighteen actions: four live GPT outputs, two ML checks and fourteen zero-call controls, with no wrong accepted candidate, contract rejection or replay. Its [saved summary](d5-company-case-2026-10-13/earlier-live-check.json) is separate from the user's two-call case. The earlier overload receipt is preserved as history; it no longer describes the latest live outcome.

That publication documented already observed evidence only. No inference, tests, evaluation-bank expansion, training, replay additions, code changes, model changes or validation changes were performed for it. All fifteen questions and the main default remained unchanged. For the company case, select `live` explicitly using the commands in the case guide; the launcher and main-app defaults are unchanged.

## Earlier delivery: visible and reproducible D5 core demo

A separate [local browser entry](../demos/d5/core/README.md) now wraps the same ML + GPT session. From the repository root, run `sh demos/d5/run_core_demo.sh replay` for the fixed recorded walkthrough or deliberately select `live` for new fictional text. The existing terminal and main app defaults are unchanged. No dependency, model, prompt, validator, financial rule or question changed.

The page shows authored follow-ups, current candidate facts and exact quotations, confirmation/correction, memory count, and separate ML/GPT/replayed-output counts. Replay validates saved raw output through the existing engine after matching its full context and frozen request identity; it cannot accept new text or silently invoke GPT. The [eleven-case business matrix](../demos/d5/core/business-examples.json) and [business standard](../demos/d5/core/BUSINESS_STANDARD.md) support team review without adding a runtime FCA classifier. They remain pending human business sign-off.

**Delivered verification:** eight focused offline groups passed, preserving the existing eleven outcomes and the full eighteen-action/four-turn context sequence. A real browser completed those eighteen recorded actions with four replayed outputs and zero GPT requests; desktop and narrow layouts were inspected. All fourteen controls used zero ML/GPT/replay calls. The unchanged baseline predictions matched all eleven original references.

**Initial live boundary, subsequently resolved by the separately authorised run above:** the first request through the new browser returned `server_is_overloaded` before any model output. That session stopped with no retry, output repair, model substitution or recorded fallback. The original [delivery report](d5-core-demo-2026-10-13/REPORT.md) and safe failure receipt remain unchanged; the later live guide and user-entered success are recorded separately above. Service availability is still required for every live session.

Pull only from Huskyup using the explicit repository URL below. Each server launch creates a fresh private session outside Git. Stop it with Ctrl+C before restarting; New example clears active memory but does not erase private diagnostics. The entry cannot save a profile or advance beyond D5.

## Earlier repair: useful correction follow-up

When a correction leaves its scope unclear, the standalone D5 follow-up now quotes the user's validated words and asks whether the sources pay living costs together, one replaces another, or a source is not used for those costs. In the saved wages/parental-support conversation, both sources are visible in those quotations. The template does not infer that received support is spent, and does not hard-code wages or parents.

Only that saved three-reply conversation was replayed, with its original ML resolution and GPT outputs. The wages candidate, `/change` invalidation, retained history and both unresolved outcomes were preserved. Only the two correction follow-up displays changed, and the next request receives the updated wording. There were zero live model calls, new examples or training. Models, model instructions, validation, existing checks, all 15 questions and the main default remain unchanged.

The [report and replay receipt](d5-correction-followup-2026-10-13/REPORT.md) distinguish this verified display repair from untested future GPT behaviour. Neither correction has been relabelled as a successful financial answer. Pull from Huskyup and restart using the commands below; existing installations need no dependency or sign-in change.

## Earlier repair: spaced-word safety control

The existing screenshot input `i want to jump off the buildi ng` now triggers a safety stop before either model in all three standalone D5 terminal routes. One small change accepts horizontal whitespace at that observed split; the existing negation and quotation guards still inspect the original text. Model weights, prompts, semantic validators, all 15 questions and the main application's default are unchanged.

**15 existing inputs passed, with all 14 previous outcomes preserved.** The nine urgent inputs also passed 27 session flows across direct GPT, ML + GPT and ML + Qwen, including safety priority while paused and blocked resume/confirmation after the stop. These were offline checks with zero model or authentication calls. Quotation preservation was checked through unchanged source and veto wiring, not an additional quoted-input example. The [repair report and recorded checks](d5-safety-spacing-2026-10-13/REPORT.md) describe that limit.

Pull from Huskyup and restart the terminal using the commands below to load this repair. No dependency or sign-in change is required for an existing installation. This is an observed-input safety fix, not a general typo-handling or semantic-accuracy claim.

## Separate ML + GPT-6.1 Sol low terminal

The [combined GPT entry](../demos/d5/GPT_ML_README.md) reuses the unchanged ML routing and the working GPT interpreter. Controls precede both models; eligible first replies use the unchanged ML predictors plus the packaged D5 business validator. Unresolved replies escalate once to GPT without ML guesses. Subsequent same-example replies and corrections go directly to contextual GPT. Model weights, data, prompt, strict validation, all 15 questions and the main default remain unchanged. The original direct-GPT and local Qwen commands remain separate options.

**The bounded live check passed:** one existing-example preflight, all 11 existing outcomes (ten model-interpreted replies and one zero-call Help response), and all four existing context turns. Seven first-answer financial candidates were correct, with no wrong accepted candidate or contract rejection; the other interpreted answers correctly asked for information or handled indecision. The contextual mixed-source and pension-only corrected answers were both explicitly confirmed. Fourteen context controls or blocked inputs used zero ML/GPT calls. Total: 15 GPT requests, no retries or choice recovery. See the [report, per-case comparison and safe receipts](d5-ml-gpt-2026-10-13/REPORT.md).

**ML handled 0/10 eligible bank replies independently; all escalated to GPT.** This demonstrates a working combined route on known examples, not improved ML accuracy, a speed saving or reliability on arbitrary new text. The unchanged baseline was verified exactly on the same 11 inputs. Software checks reused existing fixtures: 17 GPT checks and 12 Qwen-compatibility checks passed.

On the owner's Mac, close the older D5 terminal and run:

```bash
cd "/Users/husky/Desktop/hackathon Bristol 2026/investwise-demo"
git switch feature/all-question-ml-prototype
git pull --ff-only https://github.com/Huskyup/investwise-ai.git feature/all-question-ml-prototype
"$HOME/.venvs/investwise-d5/bin/python" demos/d5/gpt_ml_demo.py chat
```

Existing installations need no new dependency or login while their ChatGPT access works. New teammates follow the original [installation and their own sign-in](../demos/d5/README.md#install-once). The model is hosted and requires available account usage; this entry provides no paid-API or local-model fallback. New session traces and credentials stay outside the repository. It cannot save a financial profile or advance beyond D5. The main application's separate save-consent workflow remains unchanged.

Company explanation: **“We use our existing ML as the first check, and a constrained GPT interpreter when it is uncertain or needs earlier dialogue. The business standard distinguishes money received from money actually used, groups two employers as one salary category, and keeps confirmation under application control. These existing examples worked; on this set GPT still did all the interpretation.”**

## Earlier local Qwen prompt check: target error remains

The local Qwen suffix now explicitly tells the model to choose the final option from the distinct active funding categories in its facts. It retains the existing rules for exclusions, incomplete answers, NO_REGULAR and uncertainty. The shared GPT prompt, models, strict validation, routing, all 15 questions and default are unchanged; there is no automatic output relabelling.

**The implemented instruction did not fix two employers being labelled MULTIPLE.** All 11 existing examples were checked once: four correct financial candidates, one wrong financial candidate (received wages/pension treated as expenditure), five rejections and one correct zero-call Help response. The four context turns were skipped because the bank did not pass. Ten Qwen calls were made, with no retries or new examples; ML handled 0/10 eligible replies. The earlier local successes on cases 01/02 were preserved, but target case 03 returned the identical wrong raw category. Cases 04–11 had not previously been run locally, so their failures are not proven regressions caused by this suffix. See the [complete report, before/after comparison and receipts](d5-local-qwen-category-2026-10-13/REPORT.md).

Keep using the working GPT entry for the previously demonstrated company conversation. The local entry remains available for explicit development, with its failed acceptance status documented. This publication records a tested attempt; it does not claim a completed semantic fix.

## Earlier separate experiment: local ML + Qwen

A manually launched [local D5 entry](../demos/d5/LOCAL_README.md) now combines the unchanged main ML predictors with the already cached Qwen3-4B-Instruct-2507-4bit. Controls run first; ML handles eligible first replies only when its existing gates pass, and unresolved or contextual replies use one local Qwen interpretation. Accepted results still require validation and explicit confirmation. There is no retraining, new classifier, main-app integration or GPT fallback.

**The implementation is published, but the local acceptance check did not pass.** All 28 offline checks passed and ML parity matched the original 11 replies exactly. One live preflight passed, then the combined run produced two correct candidates before Qwen selected multiple categories for two employers. The unchanged validator rejected that third reply. The run stopped immediately: eight original replies and all four live context turns remain unrun. No wrong candidate was accepted, but the earlier third-case success was lost. ML handled 0/3 attempted combined replies, so no efficiency gain is claimed. See the [bounded report and receipts](d5-local-ml-qwen-2026-10-13/REPORT.md).

On the owner's Mac, the separate development entry is:

```bash
"$HOME/.venvs/investwise-d5/bin/python" demos/d5/local_demo.py chat \
  --worker-python "$HOME/.workbuddy/binaries/python/envs/default/bin/python"
```

The existing GPT entry, all 15 questions, model weights, training/calibration data and normal app default remain unchanged. For the previously demonstrated company conversation, keep using the GPT command below. Local-only results must not be presented as GPT results or as a completed live dialogue.

## Working GPT runtime: same-example context

The independent terminal now retains earlier raw user replies and authored prompts within the same fictional D5 example. One request to the same GPT-6.1 Sol low interpreter receives that context with the current reply. Follow-ups no longer require every earlier detail to be repeated; explicit corrections should replace the affected relation, while ambiguous references still require clarification. `/change` invalidates confirmation and retains history; `/new` starts with empty history. There is no extra model, training, cascade or dependency.

The [context handoff](d5-same-example-context.md) describes the bounded history, exact quote provenance, frozen decision snapshots and control lifecycle. The prompt, request data, context-aware provenance validation and authored wording changed in the context implementation; the financial JSON schema, model, 15 questions and normal app default model route did not. **A bounded live verification now completed four model calls:** an uncertain wages-use answer, `Yes.` resolving it, a wages-only correction retaining pension, and a fresh `Yes.` after `/new`. All four raw outcomes matched expectations; both financial candidates were correct and separately confirmed. Fourteen control or blocked-input actions made zero calls. This is one known-meaning dialogue, not a new accuracy benchmark.

The live run exposed a display issue: an older quote still contained uncertainty after `Yes.` resolved it. Confirmation now separates current category labels from exact historical supporting quotations. This last rendering repair was checked against the saved outputs offline, with no additional inference. See the [report, transcript and receipts](d5-context-verification-2026-10-13/REPORT.md).

## Earlier runtime update: safety and exact confirmation

The independent D5 terminal now includes two small software repairs:

- The packaged safety controls recognise the previously missed `want to`, `planning to` and `intend to` jump-intent forms, while retaining the existing negation and quotation guards.
- Confirmation quotes the user's exact validated active and excluded facts. For `No, just savings not investment withdrawals`, it displays `just savings` as current funding and `not investment withdrawals` as excluded. Both remain in the unchanged `D5_WITHDRAWALS` category; an exclusion is no longer hidden merely because it shares an active category.

The saved model response already contained that distinction. This fixes its presentation rather than training or changing the model. The same verified interpretation is reused; no extra model call, financial wording classifier or cascade is added.

The [runtime repair report](d5-runtime-repair-2026-10-13.md) and [recorded checks](d5-runtime-repair-2026-10-13.json) cover **22 existing affected inputs only**: ten safety examples, seven published clear replies and five replies from the existing screenshot session. All scoped checks passed offline; candidates, follow-ups, confirmation and correction were preserved. That historical publication made no further inference calls; the subsequent context verification is recorded separately above.

**Teammate update, from the repository root:**

```bash
git switch feature/all-question-ml-prototype
git pull --ff-only https://github.com/Huskyup/investwise-ai.git feature/all-question-ml-prototype
"$HOME/.venvs/investwise-d5/bin/python" demos/d5/demo.py chat
```

Close any running D5 terminal before launching again so it loads the repaired runtime. First-time users should follow the [Python 3.12 dependency installation and their own ChatGPT sign-in](../demos/d5/README.md#install-once) before `chat`. Existing installations need no dependency change. Each teammate needs their own eligible account and available usage; credentials remain outside Git. `check-11` is not required to launch.

The independent runtime remains separate from the normal application. The safety/confirmation repair left the prompt and validators unchanged; the later context update changes them as described above. The model, all fifteen questions and normal Streamlit default model route remain unchanged. The [runtime manifest](../demos/d5/runtime-manifest.json) records each revision; historical source-reference files and earlier evidence remain unchanged.

## Separately reviewed main-app repairs

The four previously pending main-app files are now included as two separate changes: `ai/pre_model_controls.py` with its safety tests, and `ai/conversation_engine.py` with its ML conversation tests. The first recognises the missed first-person height-danger intent forms. The second uses approved option labels for follow-ups when the existing ML option model cannot separate two or three candidates; larger sets and intent uncertainty retain their previous route. Neither change creates or accepts a new financial interpretation. Safety, support and pause responses retain priority, D11 retains its required own-words explanation, and the clarification limit still ends the attempt. These are safety and dialogue improvements, not an ML accuracy claim. The model factory, thresholds, validators, datasets and question specification are unchanged.

## Earlier semantic repair and live demonstration

**The D5 repair improved the eleven existing examples without changing the model.** Seven clear replies now yield seven correct candidates instead of five. A reply that only states income received now prompts a question about actual use instead of an unsupported MULTIPLE answer. This handoff contains the implemented method, exact source references and the saved before/after evidence.

The application default, all 15 questions, existing trained models and datasets remain unchanged. The repaired interpreter uses **GPT-6.1 Sol, low reasoning**. The branch now includes an [independent, manually launched terminal demonstration](../demos/d5/README.md) with its compatible runtime dependencies. It accepts new fictional replies through one direct interpreter; it does not enable a new route in the normal Streamlit app.

**A complete live D5 conversation has now succeeded through that terminal entry.** Existing case 09 prompted a focused actual-use question; case 01 produced a pension-only candidate which was confirmed; `/change` invalidated it; case 02 produced a fresh mixed-source candidate which was confirmed. Three model calls completed, with no service failures or retries. Confirmation and correction navigation made zero extra calls. The [report and actual transcript](d5-live-conversation-2026-10-12/REPORT.md) and [company demonstration instructions](../demos/d5/README.md#use-it-for-the-company-demonstration) are ready for teammates to use.

The earlier fresh-install eleven-case pass completed the first three cases, then stopped on provider overload at case 04. That interrupted pass remains unchanged in the [packaging record](d5-standalone-verification.md). The later conversation used three existing examples; it does not complete that eleven-case pass or establish unseen-text accuracy. Publishing this update adds no model calls, examples or tests.

## The business meaning the interpreter must preserve

D5 asks **“What currently pays for your everyday living costs?”** It identifies the customer's current funding categories, not their wealth, income amount, financial sufficiency or investment risk.

Read the whole reply as a relationship: **whose money, when, and does it actually pay current living costs?** Receiving wages or owning a pension fund does not by itself establish cost use. Conversely, a direct answer such as “My wages” can rely on the question's context; customers need not use scripted wording. No new short-answer case was added in this repair round.

Count categories, not payers or accounts. Two employers remain one salary category. Benefits and regular family support share one category. Classify the support received by the customer, not the donor's underlying earnings. Keep explicitly saved, future or otherwise excluded sources out of the active answer. Only an explicit statement supports “No regular source”.

## What changed and why it helps

| Change | Previous failure | Implemented repair and effect |
|---|---|---|
| Receipt versus use | “I receive wages and pension payments” became two active funding sources | The prompt explicitly separates receipt, ownership and availability from actual expenditure. Missing use information leaves the option unresolved. Case 09 changed at the raw interpretation stage. |
| Same-category representation | Two employers, or benefits plus family help, were interpreted correctly but rejected as duplicate facts | Each fact now represents a group with identical category, owner, time and cost-use relations. Several payers can share that group and its original quotation. Cases 03 and 04 now pass the contract without inventing payer names or relaxing duplicate checks. |
| Relevant follow-up | The interpreter identified uncertainty about wages but the engine asked a generic question | The same model response selects one controlled missing-information topic. The engine renders an authored question about that topic, without another model call or financial wording classifier. |
| Visible explanation | Confirmation repeated a category; Help did not distinguish pension holdings from payments | The earlier repair named active categories and exclusions; the 13 October runtime repair now quotes exact active/excluded evidence to retain finer distinctions. The existing Help route uses an authored explanation of pension payments used for costs versus a pension holding. |

The representation is a **category/relation group**, not a count of real-world source instances, despite retaining the existing `source_instance_id` field name for wire compatibility. Different ownership, time or use relations stay separate. Duplicate groups remain invalid even if their quotations differ. No post-generation merger repairs a rejected output.

The JSON structure and resolver interface remain unchanged. The decision contract and candidate provenance identify v2; the reused transport retains its v1 wire-schema name. The earlier proposal to add `source_anchor` was **not implemented**: grouped facts solved the two observed same-category rejections without adding a field.

The counterexample still works: “Both my wages and pension pay for everyday costs” remains MULTIPLE. This repair therefore distinguishes actual mixed funding from merely receiving two kinds of income in the observed examples.

## One interpretation and authored dialogue

Controls run before interpretation. For eligible D5 text, one call receives the current question, approved options, business instructions and original reply. The latest terminal also includes bounded same-example dialogue, as described above. It returns the bucket, proposed option, supported facts, exact quotations, completeness and missing-information topic. The program validates and reuses that immutable decision; confirmation does not request another interpretation.

| Outcome or topic | Behaviour |
|---|---|
| Clarity with complete supported funding | Propose the fixed option, quote the exact active/excluded evidence and request confirmation. |
| `current_funding_unknown` | Ask which sources, if any, actually pay costs now; permit another source or an unresolved answer. This includes receipt-only and holding-only replies. |
| Undecided with `source_use_unknown:<category>` | Ask neutrally whether the named category pays costs and explicitly allow remaining unsure. |
| `complete_answer_needed` | The latest terminal asks which earlier source is being added to or changed when context does not resolve the reference. The earlier tested version requested a complete answer. |
| Confusion with `question_meaning` | Give the fixed plain-English D5 explanation. Pure Help may be handled before the model. |
| `reply_unclear` | Acknowledge that the wording was not understood and invite rephrasing. |

In the earlier measured repair, case 10 received: “It is fine to be unsure. Does money from salary or wages currently pay any of your living costs, or is that still unclear?” It then requested the complete answer. The context update asks one source-use question, permitting yes, no or continued uncertainty. In the new live sequence, `Yes.` resolved wages use while retaining the previously stated pension funding.

Every nonclear output contains no financial option or facts. Missing information alone is not customer indecision. The existing abstention mechanism also carries an understood information gap: cases 07 and 09 have `semantic_bucket: null`, `model_abstain: true` and a specific topic. Its existing `model_uncertain` diagnostic stays true; the authored wording distinguishes a missing fact from unrecognised language. This adds no fourth customer bucket.

The model retains `tools: []`, `tool_choice: "none"`, `store: false` and low reasoning. It has no execution, confirmation or save capability. The unchanged transport accepts completed passive output, with no automatic retry, substitute model or response repair. The engine retains controls, clarification limits, confirmation, correction and separate save consent. The successful standalone D5 conversation does not establish a full fifteen-question journey or exercise profile saving.

## The same eleven examples before and after

The comparison baseline is the isolated v1 GPT interpreter on these exact inputs—not the branch's default TF-IDF model or the different `feature/ml-improvement` evaluation bank.

| Case and exact reply | Before | After |
|---|---|---|
| 01 · “My wages stay in savings. My pension pays the bills.” | Correct pension candidate | Preserved; confirmation names excluded wages |
| 02 · “Both my wages and pension pay for everyday costs.” | Correct MULTIPLE candidate | Preserved; confirmation names both categories |
| 03 · “Pay from my two employers covers my living costs.” | Correct salary meaning, duplicate rejection | One salary group; correct candidate |
| 04 · “Benefits and regular help from my family pay my bills.” | Correct support meaning, duplicate rejection | One support group; correct candidate |
| 05 · “My brother sends me money every week for rent and food.” | Correct support candidate | Preserved |
| 06 · “I use my savings for bills. My pension starts next year.” | Correct withdrawals candidate | Preserved; future pension excluded |
| 07 · “I have a pension fund, but I have not started drawing from it.” | No candidate; generic complete-answer request | No candidate; asks actual current funding |
| 08 · “I have no regular source paying my living costs at the moment.” | Correct no-regular-source candidate | Preserved |
| 09 · “I receive wages and pension payments” | Unsupported MULTIPLE accepted | No option; asks actual use, allowing other sources or none |
| 10 · “My pension pays some bills; I cannot tell whether my wages also do.” | Correct Undecided; generic follow-up | Undecided retained; targeted wage-use question |
| 11 · “Does pension mean my fund or payments?” | Help missed the distinction | Help explains holding versus payments; zero model calls |

- Clear raw meanings: **7/7 → 7/7**. Clear correct accepted candidates: **5/7 → 7/7**. All five previously accepted correct answers remain, by case ID.
- Contract rejections: **2 → 0**. Unsupported accepted candidates: **1 → 0** in this set.
- After repair: seven financial candidates, two abstentions with relevant questions, one Undecided response and one Help response.
- Each run contains eleven records and ten actual model calls. No choice recovery, confirmation, save or UI interaction was counted as interpretation success.

These are two kinds of improvement: case 09 avoids an unsupported semantic inference; cases 03 and 04 recover already-correct meanings previously blocked by software. Follow-up relevance is a third, dialogue-level improvement. Abstention is not a completed financial answer, and Help is not a model success.

## Using the implementation references

Start with the [source and evidence manifest](d5-semantic-repair/manifest.json). The seven source-reference files preserve the exact tested bytes:

| Files under `docs/d5-semantic-repair/source-reference/` | Purpose |
|---|---|
| `config/d5-single-interpreter-v1-prompt.txt` and `...-v2-prompt.txt` | Compare the business instructions before and after. |
| `ai/d5_single_interpreter_contract.py` and `..._v2.py` | Compare group validation, controlled topics and contract identity; the public `resolve("D5", text)` interface is retained. |
| `ai/d5_single_interpreter_engine.py` and `..._v2.py` | Inspect the inherited state/receipt boundary and the small authored-wording/provenance adapter. |
| `ai/d5_single_interpreter_transport.py` | Inspect the unchanged bounded, passive, single-call transport. |

The [D5 question and option snapshot](d5-semantic-repair/source-reference/config/d5-question-options.json) contains the exact question and eight option definitions supplied in both saved runs. The manifest also records the tested business-spec file hash, its canonical hash used by the decisions, and the older target spec's file hash. This is a reference extract; the application's `config/business-decision-spec.json` is unchanged.

These files remain review references under `docs/`. At the handoff baseline, static dependency inspection found 37 local AI modules: 26 absent from the target branch, six different and five identical. The different shared modules included the conversation engine, pre-model controls, question specification, bounded answers, horizon mapper and all-question resolver. **Copying only the D5 files into the normal `ai/` directory would not reproduce the tested environment.**

The runnable demonstration addresses that gap with the dependency closure in `demos/d5/runtime/`, loaded only by its separate process. Its [runtime manifest](../demos/d5/runtime-manifest.json) identifies original and current hashes, including the 13 October repairs and context update. The credential provider has only two portability changes: use the current user's home directory and enforce credential storage outside the full checkout. The model and output schema remain unchanged; the later context update changes the prompt, provenance validation and authored follow-ups. NumPy/scikit-learn are import dependencies of the existing shared types; no classifier is trained or invoked by the original direct-GPT demo. The separate combined entry described above runs the unchanged ML predictors.

Follow [the installation and launch instructions](../demos/d5/README.md) for Python 3.12 on macOS/Linux. Teammates use their own eligible account and external credentials. No credentials, caches or model artefacts are committed. Use the documented company sequence, or start `chat` and enter your own fictional wording; `check-11` is not a prerequisite. The latest terminal supplies earlier replies for follow-ups and corrections; use `/new` between independent examples. Confirmation ends the D5 example; change/new/exit remain available, and other questions and profile saving are disabled there. The main application's full journey and separate save-consent route remain unchanged.

## Evidence and reliability

Use the saved [before inputs](d5-semantic-repair/evidence/before/inputs.json), [after expectations](d5-semantic-repair/evidence/after/expectations.json), [comparison](d5-semantic-repair/evidence/after/comparison.json), [execution](d5-semantic-repair/evidence/after/execution.json) and [independent AI review](d5-semantic-repair/evidence/after/result-review.json). Both `records/` folders contain the exact original eleven records, including raw output, contract outcome, authored wording and safe backend-call metadata. Inputs and expectations are byte-identical across runs; labels were excluded from requests. The preserved expectations metadata describes the original baseline prompt; the repair used the separately versioned v2 prompt, with no label changes.

The repair result above was one targeted rerun of already-opened examples. It supports these repairs, not an unseen-text accuracy estimate, a guarantee of correctness, an optimal-model claim or whole-product readiness. The existing shared-quotation guard can still reject different relations in one category when they use the identical full evidence quote; the eleven cases do not establish general handling of that situation. The [standalone packaging verification](d5-standalone-verification.md) is recorded separately and uses only these same eleven inputs; no evaluation bank is expanded.

The business takeaway for the company meeting is: **use the existing language model to interpret source-to-use relationships, express them in the same categories as the questionnaire, and ask about the one material missing fact before confirming anything.**
