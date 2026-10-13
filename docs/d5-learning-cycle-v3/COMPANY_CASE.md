# D5: what this reviewed learning attempt demonstrated

**We have a working, previously observed ML + GPT conversation, but this learning attempt did not yet teach ML to handle a new savings expression independently.**

The business task is to understand what currently pays living costs. D5 must distinguish using savings from merely holding savings, using wages from merely receiving wages, and two different paying categories from two payers within the same category.

Our existing user-entered case is `savings` → `yes but 50% also come form my wages` → confirmation. In that recorded live conversation, ML was uncertain and GPT interpreted both replies; the application kept the context and requested confirmation. That is a live conversation success, not evidence that ML learned from the conversation automatically.

For this learning attempt, the business owner reviewed 15 wording changes across 64 existing fictional training sentences. We retained the earlier intent classifier and fitted the existing TF-IDF + logistic-regression source classifier once. We kept the original calibration method and all acceptance checks, and compared both versions on the same 27 existing replies outside training.

| Required evidence | Observed |
|---|---|
| Reviewed business meanings and data use | Approved and hash-recorded |
| Actual model update | One isolated source-classifier fit; no architecture change |
| More reliable source meaning | Some gains and a regression; 10/15 clear raw sources, same total as v2 |
| A new savings reply accepted by ML alone | None; target replies retain three/four source candidates |
| Candidate live conversation | Not run because the earlier check failed |

The guardrails kept the candidate from committing a wrong answer, but they did so by escalating every eligible reply. That does not demonstrate an efficiency gain. We preserved the existing demo and stopped this candidate; we did not lower checks to make the company demonstration look successful.

**Meeting wording:** “Our prototype can demonstrate the reviewed D5 conversation with GPT assistance. We have also implemented and audited the review–train–compare part of a learning workflow. This particular data repair has not yet reduced GPT reliance, so we are not presenting it as a completed learning flywheel.”

Use the [existing live company case](../d5-company-case-2026-10-13/CASE.md) and current demo command in the [handoff](../d5-semantic-method-handoff.md). All fifteen questions and the default remain unchanged. This cycle makes no whole-product reliability or current service-availability claim.
