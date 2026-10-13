# D5 v2 business sample review

**Approved by the business owner in this chat on 13 October 2026.** These are 24 new fictional examples: 16 training additions and eight validation replies. This review preceded the single v2 fit and comparison; see the [subsequent result](RESULTS.md). The earlier eight training rows remain approved and are reused without changing their words.

D5 asks: **What currently pays for your everyday living costs?** Review the meaning and intended action, not a predicted model outcome. Both banks are AI-authored; the validation author did not see the new training wording or model results.

## Sixteen new training examples

Eight clear rows enter both classifiers. Four Undecided and four Confusion rows enter only the intent classifier; no financial option is supplied for them.

| ID | Exact reply | Label | Business meaning |
|---|---|---|---|
| D5-V2-LT-01 | The balance I built up in my savings account is paying for food and electricity at the moment. | Clarity — savings / withdrawals | Existing savings are actively paying current living costs. |
| D5-V2-LT-02 | I am taking cash out of savings to meet my household expenses; my wages are left untouched. | Clarity — savings / withdrawals | Savings pay current expenses; wages are explicitly excluded from expenditure. |
| D5-V2-LT-03 | My pension has not started yet, so I cover this month's living expenses from savings. | Clarity — savings / withdrawals | Savings are active now; a pension not yet started is excluded. |
| D5-V2-LT-04 | I have stopped earning for now and am using my saved-up money to keep the bills paid. | Clarity — savings / withdrawals | Previously saved money pays current bills; no current wage source is asserted. |
| D5-V2-LT-05 | I leave my savings alone and spend the pay from my job on day-to-day expenses. | Clarity — wages | Employment pay funds current costs; savings are held but not spent. |
| D5-V2-LT-06 | Pay from both my jobs goes towards the rent and groceries; I don't use my savings. | Clarity — wages | Two employment payers remain one salary category; savings are excluded. |
| D5-V2-LT-07 | Some household costs are covered by the pay from my job, and the rest by money I take out of savings. | Clarity — multiple categories | Wages and savings both pay current living costs; no allocation is inferred. |
| D5-V2-LT-08 | For everyday spending, I combine my pay packet with cash from my savings. | Clarity — multiple categories | Current spending draws on two categories: employment pay and savings. |
| D5-V2-LT-09 | I understand you mean what pays my bills, but I can't work out whether I use saved money or my wages. | Undecided — no financial option | The customer explicitly cannot establish whether savings or wages pay costs; this is genuine indecision, not model uncertainty. |
| D5-V2-LT-10 | My pension definitely covers rent. I'm unsure whether I also spend savings on food. | Undecided — no financial option | Pension use is stated but savings use is explicitly unresolved, so no complete financial option is labelled. |
| D5-V2-LT-11 | I don't know which of my accounts the money for everyday spending is actually coming from. | Undecided — no financial option | The customer understands expenditure but explicitly cannot identify its funding source. |
| D5-V2-LT-12 | I can name the money I receive, but I cannot work out which of it is going on living costs. | Undecided — no financial option | Explicit inability to determine expenditure, rather than mere omission of use, warrants an Undecided follow-up. |
| D5-V2-LT-13 | I don't understand the question. What do you mean by a source of money for living costs? | Confusion — no financial option | The customer asks for the meaning of the question, not a financial interpretation. |
| D5-V2-LT-14 | Does 'withdrawals' mean the money in my account or the amount I take out? I'm confused by that word. | Confusion — no financial option | The customer requests a terminology explanation; no source-use answer is supplied. |
| D5-V2-LT-15 | I thought you wanted my total savings. Can you explain what funding my living costs means? | Confusion — no financial option | The customer is confusing an asset balance with the source of expenditure and asks for explanation. |
| D5-V2-LT-16 | Are you asking where the money comes from or how much I spend each month? I do not understand which you need. | Confusion — no financial option | The customer asks whether the question concerns funding source or spending amount. |

## Eight new validation examples

These replies never enter fitting or calibration. The first four have financial labels; the remaining four must not create a definite financial answer. Model uncertainty may safely escalate; it must not be relabelled as customer indecision.

| ID | Exact reply | Expected meaning / category | Expected action |
|---|---|---|---|
| D5-V2-LV-01 | I've been moving a little out of my savings each week to cover the food shop and the electricity meter. | Clarity — savings / withdrawals | Propose savings or investment withdrawals, preserving that the stated source is savings, and ask for explicit confirmation. |
| D5-V2-LV-02 | Each month I transfer some of my savings into my current account, then use that to pay the rent and household bills. | Clarity — savings / withdrawals | Propose savings or investment withdrawals on the basis of the stated savings use, and ask the customer to confirm. |
| D5-V2-LV-03 | I'm paid fortnightly by my employer, and that's the money I live on between paydays. | Clarity — wages | Propose salary or wages as the supported current funding category and request explicit confirmation. |
| D5-V2-LV-04 | The pay from my shop job covers the weekly food shop, and I take money from my savings for the rent. | Clarity — multiple categories | Propose more than one listed source category, name both wages and savings withdrawals, and request confirmation of that stated mixture. |
| D5-V2-LV-05 | I've got money sitting in a building society account. | Incomplete — use not established | Ask whether that money is currently used for living costs or whether something else pays them. Leave the financial option unresolved; do not infer no regular source, indecision or confusion. |
| D5-V2-LV-06 | A payment from my employer comes into my account each month. | Incomplete — use not established | Ask whether the payment is used for current living costs or whether those costs are paid another way. Keep the financial option unresolved without assuming that received money is spent. |
| D5-V2-LV-07 | I'm honestly not sure whether I'm living off my pay or dipping into the money I'd put aside. I can't work out which is covering things at the moment. | Undecided — no financial option | Ask neutrally whether they can identify what currently pays those costs, allowing either mentioned possibility, both, another source or continued uncertainty. Keep the option null and nonclear financial facts empty. |
| D5-V2-LV-08 | When you say 'pays for living costs', do you mean whose name is on the bills, or where the money to pay them comes from? | Confusion — no financial option | Explain that the question asks where the money actually used for everyday costs comes from, rather than whose name appears on a bill, then invite an answer. Assign no financial option; a pre-model Help response may handle the explanation. |

## Review boundaries

- Receiving or owning money is not evidence that it pays current living costs.
- Savings and investment withdrawals share the questionnaire category; the confirmation must preserve the actual stated source.
- Multiple employers remain wages; mixed means different funding categories.
- Future pensions and explicitly unused sources do not count as current funding.
- Genuine inability to identify use is Undecided; asking what a question means is Confusion. Missing detail alone is neither.

The [overlap review](overlap-review.json) reports equality and nearest wording. Two validation constructions were revised by their separate author before this review, and one training sentence clarified uncertainty rather than nondisclosure. No prediction or outcome informed those edits. Existing nineteen replies remain opened regression evidence.

The business owner approved the meanings and uses of IDs **D5-V2-LT-01–16 and D5-V2-LV-01–08**. This approves 24 new rows, not the entire historical corpus. The [review record](human-review.json) binds this approval to the exact draft bytes shown here; draft JSON status metadata is retained unchanged. These inputs were frozen before either candidate classifier was fitted.

Training SHA-256: `58f4b353e4e3699e01244dfd9809c70edf105c6a50eed66bd258969b36e1c5ec`
Validation SHA-256: `c5b7c787d8e524190cbaf0f180665d46f038ffcb6367615f26e72459e5b225ba`
