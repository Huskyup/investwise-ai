# D5 safety control: spaced building repair

13 October 2026 · Huskyup/investwise-ai · `feature/all-question-ml-prototype`

**The existing screenshot input `i want to jump off the buildi ng` now stops the standalone D5 conversation before either model.** Previously, the space inside `building` prevented the height-intent safety pattern from matching.

## Small, shared runtime repair

The packaged control pattern now accepts horizontal whitespace at the observed split: `buildi[ \t]*ng`. Intent prefixes, other height nouns and word boundaries are unchanged. The original text and match offsets still reach the existing negation and quotation guards; no global whitespace normalisation or fuzzy classifier was added.

This one shared runtime file serves the direct GPT, ML + GPT and local ML + Qwen terminal entries. The main application's controls and default route are unchanged. Model weights, ML predictors, training/calibration data, prompts, semantic validators and all 15 questions are unchanged. The runtime manifest records the new file hash; historical evidence is preserved.

## Existing examples only

The [recorded offline check](checks.json) reused ten published safety examples, four existing negation/insurance examples and the original screenshot text: **15 inputs, all passing**. The screenshot changed from no control action to `safety_stop`; all other 14 outcomes were preserved. Six negative examples remained outside the urgent safety action.

The nine urgent inputs were also passed through each of the three terminal session routes: **27 safety flows passed**. Safety took priority while paused. Resume and confirmation could not bypass the stop; no financial candidate, confirmed answer, saved profile or interpreted history was produced. Forbidden model backends and blocked network connections enforced **zero ML, GPT, Qwen and authentication calls**. No new example, fitting or live semantic evaluation was added.

Source comparison confirmed the negation and quotation guards were unchanged. A forced quotation-veto check confirmed that the original screenshot text still reaches that guard. There was no existing quoted-height input in the reused bank, so this is a source/wiring preservation check, not a quoted-input regression result. Independent read-only review found no blocking issue.

## Use and limits

Pull the Huskyup branch and restart the existing terminal using the [handoff commands](../d5-semantic-method-handoff.md). Existing installations need no dependency or sign-in change. This repair covers the observed split; it does not establish general typo detection or new model accuracy. See the [preservation audit](preservation.json) for the unchanged previous files and unrelated local work.
