# D5 business standard for the core demonstration

**Question:** What currently pays for your everyday living costs?

This reference explains the existing eleven fictional examples in [business-examples.json](business-examples.json). Their IDs, wording and gold expectations are copied from the saved [inputs](../../../docs/d5-semantic-repair/evidence/after/inputs.json) and [expectations](../../../docs/d5-semantic-repair/evidence/after/expectations.json). The [technical handoff](../../../docs/d5-semantic-method-handoff.md#the-business-meaning-the-interpreter-must-preserve) supplies the business rationale. Source hashes are recorded in the JSON.

**Review status: agent authored, pending human business sign-off.** The annotations below are a reviewable explanation of existing evidence. They are not new unseen cases, independent human approval, a new performance result or a model-training update. No model, prompt, validator, question or default is changed by these files.

## What a D5 answer means

Identify the categories of money actually paying the customer's current living costs. Read whose money it is, when it is available, and its relationship to those costs. Do not infer an amount, financial sufficiency, investment recommendation or risk category.

- **Received or held is not necessarily spent.** Receiving wages and pension payments does not establish that either pays living costs. A pension fund that has not been drawn is not an active payment source.
- **Count categories, not payers.** Two employers remain salary/wages. Benefits and regular family help share the existing benefits/support category. They do not become multiple categories merely because there are two payers.
- **Preserve exclusions.** Saved wages and a pension starting next year stay outside current cost funding. The category label must not hide the distinction between savings and investment withdrawals actually mentioned by the customer.
- **Classify the customer's relationship.** Money regularly sent by a brother for rent is support received by the customer. Do not infer or classify the brother's earnings.
- **Unknown is not no.** Missing information does not justify `D5_NO_REGULAR`; that option needs an explicit current absence of a regular funding source.
- **Keep uncertainty separate from indecision.** A missing expenditure relationship is not proof that the customer is Undecided or Confused. Explicit inability to establish a source's use supports Undecided; a terminology question supports Confusion or the pre-model Help response.

The questionnaire supplies context for an ordinary direct answer. Customers do not have to repeat scripted wording about living costs in every turn. In a dialogue, use the explicitly available history; if a correction's addition or replacement scope is unresolved, ask rather than silently dropping or adding a source. These eleven single-turn examples do not themselves validate correction handling.

## The eleven existing meanings

| Case | Expected meaning and category | Appropriate next action |
|---|---|---|
| 01 | Wages stay saved; pension pays bills. `D5_PENSION_PAYMENTS` | Confirm pension funding while preserving the wage exclusion |
| 02 | Wages and pension both pay current costs. `D5_MULTIPLE` | Confirm both categories |
| 03 | Pay from two employers funds living costs. `D5_SALARY` | Confirm salary; do not count employers as separate categories |
| 04 | Benefits and regular family help pay bills. `D5_BENEFITS_SUPPORT` | Confirm the single support category without discarding either payer |
| 05 | Weekly money from a brother pays rent and food. `D5_BENEFITS_SUPPORT` | Confirm regular support; do not ask how the brother earns his money |
| 06 | Savings pay bills now; pension starts next year. `D5_WITHDRAWALS` | Confirm the stated savings use and exclude future pension payments |
| 07 | A pension fund is held but not drawn. No option | Ask what currently pays costs; do not infer no regular source or customer confusion |
| 08 | Explicitly no regular source currently pays costs. `D5_NO_REGULAR` | Confirm that statement without implying no assets |
| 09 | Wages and pension payments are received, but use is unstated. No option | Ask which sources actually pay costs, allowing another source, neither or continued uncertainty |
| 10 | Pension pays some bills; wage use is explicitly uncertain. Undecided, no option | Ask neutrally about wage use and permit the customer to remain unsure |
| 11 | The customer asks whether pension means a fund or payments. Confusion/Help, no option | Explain the distinction; a pre-model Help response counts as dialogue handling with zero interpretation calls |

The exact saved `gold.kind`, `gold.option`, `gold.meaning` and `gold.next` remain in the JSON. Cases 07 and 09 retain `missing_information`, rather than introducing a fourth customer bucket or forcing an exact raw bucket.

## When to ask and when to confirm

Confirm a complete, supported category proposal; confirmation is an explicit customer action, not the result of classification. Ask about the particular missing relationship when information is incomplete. Explain the question when the person asks what it means. A generic choice menu or safe abstention alone is not evidence of successful free-text interpretation.

`proposed_follow_up` contains business wording for review and demonstration explanation. It is **not a replacement for the runtime's authored responses**, a new model instruction, or an assertion that these precise words have been tested. No follow-up response from the customer is invented in this bank.

For example, case 09 needs a question about actual expenditure. Case 10 needs only a neutral wage-use question. Asking the case 06 customer for future pension details would not improve the already clear current answer.

Nonclear runtime outputs must retain empty financial facts and a null option under the existing contract. Case 10's supported pension relationship is useful for offline business review, but the annotation must not be copied into a nonclear model payload. Similarly, an excluded holding in case 07 is not an accepted financial answer. The reference does not weaken any current check.

## Data dictionary

| Field | Meaning and permitted interpretation |
|---|---|
| `schema_version` | Version of this offline reference format, not a new runtime contract |
| `question_id`, `question` | The unchanged D5 identity and business question |
| `review_status`, `review_limit` | Agent-authored annotations pending human business sign-off; no completed human review is implied |
| `case_status` | All eleven examples are fictional and previously opened |
| `sources[].path`, `sources[].sha256` | Repository-relative input/reference files and their hashes at authoring time |
| `interpretation_boundary`, `nonclear_boundary` | Limits separating review annotations from requests, raw model output and accepted financial facts |
| `cases[].id`, `text` | Exact existing case ID and original reply; neither is rewritten |
| `gold.kind` | Unchanged expectation: `clear`, `missing_information`, `undecided` or `confusion`; this is an offline case type, not a replacement for the three runtime buckets |
| `gold.option` | Unchanged expected financial option, or JSON null when no supported complete candidate exists |
| `gold.meaning`, `gold.next` | Exact original meaning and next-action expectation, preserved verbatim |
| `business_annotations.sources` | Review notes on mentioned category/use relationships; this list is not runtime financial output |
| `source_description` | Plain-English description of the mentioned source or related holding |
| `category_id` | Existing category being considered; on an excluded or unknown relation it does not assert an active funding source |
| `pays_living_costs` | `yes`, `no` or `unknown`, assessed for **current** living costs. Future income has no current cost use; absent evidence stays unknown |
| `time_scope` | `current` or `future`, as supported by the existing reply and D5's current-cost question |
| `evidence_quote` | An exact substring of that case's original reply supporting the annotation; no generated paraphrase is presented as a quotation |
| `note` | Why the relation matters, including limits on inference |
| `category_reason` | Why the original expected category or unresolved outcome follows from the business meaning |
| `excluded_sources` | Explicitly excluded sources, in business prose; an empty list means no explicit exclusion is recorded, not proof that all mentioned sources are active |
| `missing_facts` | Information needed to resolve the answer or explain terminology. An empty list on a clear case is not proof of real-world completeness beyond the agreed questionnaire meaning |
| `proposed_follow_up` | Reviewable business wording; never silently supplied as model input or substituted for the current authored runtime response |

The relationship annotations may later support an offline coverage table after human review. They do not add FCA, a rule-based interpreter, automatic learning or another classifier to the conversation. Before reusing any row for future training, preserve its provenance and prior evaluation exposure; it cannot also be claimed as an unseen test case.
