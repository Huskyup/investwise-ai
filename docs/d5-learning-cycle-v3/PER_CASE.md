# D5 v3 saved per-case results

All 27 inputs were already opened and remain outside training. This table is a presentation of `evidence/compare.json`, not another inference or scoring run. Raw option predictions are scored only on clear replies; an option prediction on an incomplete or nonclear reply is diagnostic, not a financial answer. No reply was selected, confirmed or saved.

## Raw source comparison

| Case | Expected kind / source | Baseline raw | Saved v1 raw | Saved v2 raw | V3 raw | V3 first stopping gate | V3 accepted |
|---|---|---|---|---|---|---|---|
| D5-LV-01 | clear / savings/withdrawals | self-employment | self-employment | savings/withdrawals | self-employment | intent_model_uncertainty | — |
| D5-LV-02 | clear / savings/withdrawals | savings/withdrawals | savings/withdrawals | savings/withdrawals | savings/withdrawals | intent_model_uncertainty | — |
| D5-LV-03 | clear / wages | wages | wages | wages | wages | option_model_uncertainty | — |
| D5-LV-04 | clear / multiple categories | savings/withdrawals | savings/withdrawals | multiple categories | multiple categories | option_model_uncertainty | — |
| D5-LV-05 | incomplete / — | not source-scored | not source-scored | not source-scored | not source-scored | intent_model_uncertainty | — |
| D5-LV-06 | incomplete / — | not source-scored | not source-scored | not source-scored | not source-scored | option_model_uncertainty | — |
| D5-LV-07 | undecided / — | not source-scored | not source-scored | not source-scored | not source-scored | intent_model_uncertainty | — |
| D5-LV-08 | confusion / — | not source-scored | not source-scored | not source-scored | not source-scored | control: explain | — |
| D5-STD-01 | clear / pension | wages | wages | wages | wages | option_model_uncertainty | — |
| D5-STD-02 | clear / multiple categories | multiple categories | multiple categories | multiple categories | multiple categories | option_model_uncertainty | — |
| D5-STD-03 | clear / wages | wages | wages | wages | wages | option_model_uncertainty | — |
| D5-STD-04 | clear / benefits/support | benefits/support | benefits/support | benefits/support | benefits/support | option_model_uncertainty | — |
| D5-STD-05 | clear / benefits/support | savings/withdrawals | savings/withdrawals | savings/withdrawals | savings/withdrawals | option_model_uncertainty | — |
| D5-STD-06 | clear / savings/withdrawals | pension | savings/withdrawals | pension | savings/withdrawals | option_model_uncertainty | — |
| D5-STD-07 | incomplete / — | not source-scored | not source-scored | not source-scored | not source-scored | intent_model_uncertainty | — |
| D5-STD-08 | clear / no regular source | no regular source | no regular source | no regular source | no regular source | intent_model_uncertainty | — |
| D5-STD-09 | incomplete / — | not source-scored | not source-scored | not source-scored | not source-scored | option_model_uncertainty | — |
| D5-STD-10 | undecided / — | not source-scored | not source-scored | not source-scored | not source-scored | intent_model_uncertainty | — |
| D5-STD-11 | confusion / — | not source-scored | not source-scored | not source-scored | not source-scored | control: explain | — |
| D5-V2-LV-01 | clear / savings/withdrawals | savings/withdrawals | not source-scored | savings/withdrawals | savings/withdrawals | option_model_uncertainty | — |
| D5-V2-LV-02 | clear / savings/withdrawals | savings/withdrawals | not source-scored | savings/withdrawals | savings/withdrawals | option_model_uncertainty | — |
| D5-V2-LV-03 | clear / wages | self-employment | not source-scored | self-employment | savings/withdrawals | intent_model_uncertainty | — |
| D5-V2-LV-04 | clear / multiple categories | savings/withdrawals | not source-scored | wages | wages | option_model_uncertainty | — |
| D5-V2-LV-05 | incomplete / — | not source-scored | not source-scored | not source-scored | not source-scored | intent_model_uncertainty | — |
| D5-V2-LV-06 | incomplete / — | not source-scored | not source-scored | not source-scored | not source-scored | intent_model_uncertainty | — |
| D5-V2-LV-07 | undecided / — | not source-scored | not source-scored | not source-scored | not source-scored | intent_model_uncertainty | — |
| D5-V2-LV-08 | confusion / — | not source-scored | not source-scored | not source-scored | not source-scored | intent_model_uncertainty | — |

## Both gates and business validation

Sets below include the diagnostic raw option set even when the intent gate prevented routing from reaching it. `Not reached` is not a validator rejection.

| Case / variant | Raw intent | Intent set | Raw option | Option set | Business validation | Accepted |
|---|---|---|---|---|---|---|
| D5-LV-01 / baseline | clarity | clarity, undecided | self-employment | wages, self-employment | not reached | — |
| D5-LV-01 / candidate | clarity | clarity, undecided | self-employment | wages, self-employment, savings/withdrawals | not reached | — |
| D5-LV-02 / baseline | clarity | clarity, confusion | savings/withdrawals | savings/withdrawals | not reached | — |
| D5-LV-02 / candidate | clarity | clarity, confusion, undecided | savings/withdrawals | multiple categories, wages, savings/withdrawals | not reached | — |
| D5-LV-03 / baseline | clarity | clarity | wages | benefits/support, wages | not reached | — |
| D5-LV-03 / candidate | clarity | clarity | wages | benefits/support, multiple categories, wages, savings/withdrawals | not reached | — |
| D5-LV-04 / baseline | clarity | clarity | savings/withdrawals | multiple categories, wages, savings/withdrawals | not reached | — |
| D5-LV-04 / candidate | clarity | clarity | multiple categories | multiple categories, wages, savings/withdrawals | not reached | — |
| D5-LV-05 / baseline | clarity | clarity | savings/withdrawals | multiple categories, savings/withdrawals | not reached | — |
| D5-LV-05 / candidate | clarity | clarity, confusion | savings/withdrawals | multiple categories, savings/withdrawals | not reached | — |
| D5-LV-06 / baseline | clarity | clarity | pension | multiple categories, pension | not reached | — |
| D5-LV-06 / candidate | clarity | clarity | pension | multiple categories, pension, savings/withdrawals | not reached | — |
| D5-LV-07 / baseline | clarity | clarity | savings/withdrawals | wages, self-employment, savings/withdrawals | not reached | — |
| D5-LV-07 / candidate | clarity | clarity, undecided | wages | multiple categories, wages, self-employment, savings/withdrawals | not reached | — |
| D5-LV-08 / baseline | control | — | — | — | not reached | — |
| D5-LV-08 / candidate | control | — | — | — | not reached | — |
| D5-STD-01 / baseline | clarity | clarity | wages | pension, wages | not reached | — |
| D5-STD-01 / candidate | clarity | clarity | wages | multiple categories, pension, wages, savings/withdrawals | not reached | — |
| D5-STD-02 / baseline | clarity | clarity | multiple categories | multiple categories, pension, wages | not reached | — |
| D5-STD-02 / candidate | clarity | clarity | multiple categories | multiple categories, pension, wages | not reached | — |
| D5-STD-03 / baseline | clarity | clarity | wages | benefits/support, wages, self-employment | not reached | — |
| D5-STD-03 / candidate | clarity | clarity | wages | benefits/support, multiple categories, wages, self-employment | not reached | — |
| D5-STD-04 / baseline | clarity | clarity | benefits/support | benefits/support, multiple categories | not reached | — |
| D5-STD-04 / candidate | clarity | clarity | benefits/support | benefits/support, multiple categories | not reached | — |
| D5-STD-05 / baseline | clarity | clarity | savings/withdrawals | benefits/support, self-employment, savings/withdrawals | not reached | — |
| D5-STD-05 / candidate | clarity | clarity | savings/withdrawals | benefits/support, wages, self-employment, savings/withdrawals | not reached | — |
| D5-STD-06 / baseline | clarity | clarity | pension | pension, savings/withdrawals | not reached | — |
| D5-STD-06 / candidate | clarity | clarity | savings/withdrawals | multiple categories, pension, wages, savings/withdrawals | not reached | — |
| D5-STD-07 / baseline | undecided | clarity, undecided | no regular source | multiple categories, no regular source, pension | not reached | — |
| D5-STD-07 / candidate | undecided | clarity, undecided | savings/withdrawals | multiple categories, no regular source, pension, savings/withdrawals | not reached | — |
| D5-STD-08 / baseline | clarity | clarity, undecided | no regular source | no regular source | not reached | — |
| D5-STD-08 / candidate | clarity | clarity, undecided | no regular source | no regular source | not reached | — |
| D5-STD-09 / baseline | clarity | clarity | pension | multiple categories, pension | not reached | — |
| D5-STD-09 / candidate | clarity | clarity | pension | multiple categories, pension, wages | not reached | — |
| D5-STD-10 / baseline | clarity | clarity | wages | pension, wages | not reached | — |
| D5-STD-10 / candidate | clarity | clarity, undecided | wages | multiple categories, pension, wages, savings/withdrawals | not reached | — |
| D5-STD-11 / baseline | control | — | — | — | not reached | — |
| D5-STD-11 / candidate | control | — | — | — | not reached | — |
| D5-V2-LV-01 / baseline | clarity | clarity | savings/withdrawals | wages, savings/withdrawals | not reached | — |
| D5-V2-LV-01 / candidate | clarity | clarity | savings/withdrawals | multiple categories, wages, savings/withdrawals | not reached | — |
| D5-V2-LV-02 / baseline | clarity | clarity | savings/withdrawals | pension, savings/withdrawals | not reached | — |
| D5-V2-LV-02 / candidate | clarity | clarity | savings/withdrawals | multiple categories, pension, wages, savings/withdrawals | not reached | — |
| D5-V2-LV-03 / baseline | clarity | clarity | self-employment | self-employment | {"option_id": "D5_SELF_EMPLOYMENT", "reason": "ml_candidate_passed_d5_vetoes"} | self-employment |
| D5-V2-LV-03 / candidate | clarity | clarity, confusion | savings/withdrawals | multiple categories, wages, self-employment, savings/withdrawals | not reached | — |
| D5-V2-LV-04 / baseline | clarity | clarity | savings/withdrawals | benefits/support, wages, self-employment, savings/withdrawals | not reached | — |
| D5-V2-LV-04 / candidate | clarity | clarity | wages | multiple categories, wages, self-employment, savings/withdrawals | not reached | — |
| D5-V2-LV-05 / baseline | clarity | clarity | savings/withdrawals | no regular source, self-employment, savings/withdrawals | not reached | — |
| D5-V2-LV-05 / candidate | clarity | clarity, confusion | savings/withdrawals | multiple categories, self-employment, savings/withdrawals | not reached | — |
| D5-V2-LV-06 / baseline | clarity | clarity | savings/withdrawals | pension, savings/withdrawals | not reached | — |
| D5-V2-LV-06 / candidate | clarity | clarity, confusion | savings/withdrawals | multiple categories, pension, wages, savings/withdrawals | not reached | — |
| D5-V2-LV-07 / baseline | clarity | clarity | no regular source | no regular source, wages, self-employment | not reached | — |
| D5-V2-LV-07 / candidate | undecided | clarity, undecided | self-employment | no regular source, wages, self-employment, savings/withdrawals | not reached | — |
| D5-V2-LV-08 / baseline | clarity | clarity | self-employment | wages, self-employment, savings/withdrawals | not reached | — |
| D5-V2-LV-08 / candidate | confusion | clarity, confusion | self-employment | wages, self-employment, savings/withdrawals | not reached | — |

## Exact inputs

All are fictional. Their unchanged expectations and provenance are preserved in the frozen reference banks.

| Case | Original reply |
|---|---|
| D5-LV-01 | I'm living off the money I put aside over the years, using it for the rent, groceries and bills. |
| D5-LV-02 | These days, everything I spend on keeping the household going comes out of my savings account. |
| D5-LV-03 | My pay from the supermarket covers my rent, food and bills. |
| D5-LV-04 | I pay the rent out of my wages and take money from savings for groceries and the household bills. |
| D5-LV-05 | I've got some savings in a separate bank account. |
| D5-LV-06 | A wage arrives each Friday and I get a pension payment once a month. |
| D5-LV-07 | I can't tell whether the money I've been spending on bills is from my wages or my savings. |
| D5-LV-08 | Are you asking how much my daily expenses are, or where the money to cover them comes from? |
| D5-STD-01 | My wages stay in savings. My pension pays the bills. |
| D5-STD-02 | Both my wages and pension pay for everyday costs. |
| D5-STD-03 | Pay from my two employers covers my living costs. |
| D5-STD-04 | Benefits and regular help from my family pay my bills. |
| D5-STD-05 | My brother sends me money every week for rent and food. |
| D5-STD-06 | I use my savings for bills. My pension starts next year. |
| D5-STD-07 | I have a pension fund, but I have not started drawing from it. |
| D5-STD-08 | I have no regular source paying my living costs at the moment. |
| D5-STD-09 | I receive wages and pension payments |
| D5-STD-10 | My pension pays some bills; I cannot tell whether my wages also do. |
| D5-STD-11 | Does pension mean my fund or payments? |
| D5-V2-LV-01 | I've been moving a little out of my savings each week to cover the food shop and the electricity meter. |
| D5-V2-LV-02 | Each month I transfer some of my savings into my current account, then use that to pay the rent and household bills. |
| D5-V2-LV-03 | I'm paid fortnightly by my employer, and that's the money I live on between paydays. |
| D5-V2-LV-04 | The pay from my shop job covers the weekly food shop, and I take money from my savings for the rent. |
| D5-V2-LV-05 | I've got money sitting in a building society account. |
| D5-V2-LV-06 | A payment from my employer comes into my account each month. |
| D5-V2-LV-07 | I'm honestly not sure whether I'm living off my pay or dipping into the money I'd put aside. I can't work out which is covering things at the moment. |
| D5-V2-LV-08 | When you say 'pays for living costs', do you mean whose name is on the bills, or where the money to pay them comes from? |
