"""New ML-route policy checks; distinct from archived hybrid regressions."""
from pathlib import Path
import pytest

from ai.all_question_ml import QuestionMLResolution
from ai.conversation_engine import ConversationEngine, UNDERSTANDING_FOLLOWUP
from ai.question_spec import BusinessSpec

SPEC = BusinessSpec.load(Path(__file__).parents[1] / "config/business-decision-spec.json")


class ResolverSpy:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def resolve(self, qid, text):
        self.calls.append((qid, text))
        return self.result


def candidate(oid):
    return QuestionMLResolution(candidate_option_id=oid, ordinary_bucket="Clarity",
                                intent_set=frozenset({"clarity"}), option_set=frozenset({oid}))


def at(qid, result):
    resolver = ResolverSpy(result)
    engine = ConversationEngine(SPEC, question_resolver=resolver)
    engine.state.current_index = SPEC.question_order.index(qid)
    return engine, resolver


@pytest.mark.parametrize("qid", SPEC.question_order)
def test_every_question_typed_option_uses_ml_and_waits_for_user_confirmation(qid):
    option = SPEC.question(qid).options[0]
    engine, spy = at(qid, candidate(option.id))
    result = engine.submit_answer(option.label)
    assert spy.calls == [(qid, option.label)]
    assert result["action"] == "confirm"
    assert result["candidate_option_id"] == option.id
    assert engine.state.answers[qid].source == "all_question_ml"
    assert engine.state.answers[qid].selected_option_id is None


def test_ml_abstention_never_falls_back_to_legacy_none_rule():
    engine, spy = at("D8", QuestionMLResolution(model_uncertain=True, reason="intent_model_uncertainty", intent_set=frozenset({"clarity", "undecided"})))
    result = engine.submit_answer("none")
    assert spy.calls == [("D8", "none")]
    assert result["bucket"] is None
    assert result["model_uncertain"]
    assert engine.state.answers["D8"].candidate_option_id is None
    with pytest.raises(RuntimeError):
        engine.confirm_current(True)


def test_not_sure_is_interpreted_by_ml_and_does_not_default_middle():
    engine, spy = at("D14", QuestionMLResolution(ordinary_bucket="Undecided", semantic_undecided=True, intent_set=frozenset({"undecided"})))
    result = engine.submit_answer("not sure")
    assert spy.calls == [("D14", "not sure")]
    assert result["bucket"] == "Undecided"
    assert engine.state.answers["D14"].candidate_option_id is None


@pytest.mark.parametrize(("qid", "reply", "wrong_option"), [
    ("D8", "I have never personally held shares", "D8_SHARES"),
    ("D8", "My wife has never held investments", "D8_NONE"),
    ("D8", "My uncle holds bitcoin. I haven't specified my own holdings.", "D8_CRYPTO"),
    ("D8", "My colleague owns bonds; I have held shares.", "D8_MULTIPLE"),
    ("D5", "I will receive a salary after I start a job next month", "D5_SALARY"),
    ("D12", "I want to invest for 15 years, but I need the same money next year", "D12_LONG"),
    ("D14", "Probably the balanced trade-off", "D14_BALANCED"),
    ("D15", "I would be comfortable if recovery is guaranteed", "D15_COMFORTABLE"),
    ("D9", "Between 4 and 7 investment purchases in the last year", "D9_COUNT1_5"),
])
def test_known_business_invalidity_can_veto_but_never_replace_model_choice(qid, reply, wrong_option):
    engine, spy = at(qid, candidate(wrong_option))
    result = engine.submit_answer(reply)
    assert spy.calls
    assert result["action"] == "clarify"
    assert engine.state.answers[qid].candidate_option_id is None
    assert engine.state.answers[qid].selected_option_id is None


def test_explicit_shortcut_is_distinct_from_typing_a_label():
    engine, spy = at("D8", QuestionMLResolution(model_uncertain=True))
    result = engine.submit_answer("D8_NONE", explicit_option_id="D8_NONE")
    assert not spy.calls
    assert result["action"] == "confirm"
    assert engine.state.answers["D8"].source == "explicit_user_choice"
    assert engine.state.answers["D8"].selected_option_id is None


@pytest.mark.parametrize("qid,oid", [("D3", "D3_FROM1000_LT5000"), ("D10", "D10_FROM1000_LT5000")])
def test_positive_amount_shortcut_explains_missing_currency_without_inference(qid, oid):
    engine, spy = at(qid, QuestionMLResolution(model_uncertain=True))
    result = engine.submit_answer(oid, explicit_option_id=oid)
    assert not spy.calls
    assert "currency" in result["followup"]
    assert "range" in result["followup"]
    assert engine.state.answers[qid].candidate_option_id is None
    assert engine.state.answers[qid].selected_option_id is None


def test_urgent_safety_runs_before_every_question_model():
    engine, spy = at("D8", candidate("D8_NONE"))
    result = engine.submit_answer("I'm gonna jump off the building")
    assert result["action"] == "safety_stop"
    assert not spy.calls
    assert engine.save()["saved"] is False


def test_three_uncertain_ml_turns_end_incomplete_without_forced_choice():
    engine, spy = at("D8", QuestionMLResolution(model_uncertain=True, reason="empty_intent_prediction_set"))
    for _ in range(3):
        result = engine.submit_answer("I haven't established whether these investments were mine")
    assert len(spy.calls) == 3
    assert result["action"] == "finish_incomplete_or_pause"
    assert engine.state.answers["D8"].selected_option_id is None
    assert not engine.save()["saved"]


def test_material_ml_candidate_cannot_override_an_explicit_earlier_need():
    engine, spy = at("D12", candidate("D12_LONG"))
    result = engine._profile_evidence("D12", "The earliest realistic need for this same money is in two years")
    assert spy.calls
    assert result.option_id is None


def unresolved_with_options(*oids):
    return QuestionMLResolution(model_uncertain=True, reason="option_model_uncertainty",
                                intent_set=frozenset({"clarity"}), option_set=frozenset(oids))


def test_option_set_uncertainty_names_the_two_contending_labels():
    engine, _ = at("D5", unresolved_with_options("D5_SALARY", "D5_WITHDRAWALS"))
    result = engine.submit_answer("My wages cover everything; my savings are untouched.")
    assert result["followup_kind"] == "set_informed"
    assert "Salary or wages" in result["followup"]
    assert "Savings or investment withdrawals" in result["followup"]
    assert result["bucket"] is None
    assert engine.state.answers["D5"].candidate_option_id is None


def test_option_set_uncertainty_names_three_contending_labels():
    engine, _ = at("D5", unresolved_with_options("D5_MULTIPLE", "D5_SALARY", "D5_WITHDRAWALS"))
    result = engine.submit_answer("My wages cover rent and I use savings for everything else.")
    assert result["followup_kind"] == "set_informed"
    for label in ("More than one listed source category", "Salary or wages", "Savings or investment withdrawals"):
        assert label in result["followup"]


def test_large_option_set_keeps_generic_path():
    engine, _ = at("D5", unresolved_with_options("D5_MULTIPLE", "D5_SALARY", "D5_WITHDRAWALS", "D5_PENSION_PAYMENTS"))
    result = engine.submit_answer("Money comes from various places.")
    assert "followup_kind" not in result


def test_intent_uncertainty_has_no_option_labels_to_present():
    engine, _ = at("D5", QuestionMLResolution(model_uncertain=True, reason="intent_model_uncertainty",
                                              intent_set=frozenset({"clarity", "confusion", "undecided"})))
    result = engine.submit_answer("I get by somehow, you know?")
    assert "followup_kind" not in result


@pytest.mark.parametrize(("hold", "expected_action"), [
    ("care", "care_pause"),
    ("pace", "pace_pause"),
    ("support", "support_before_confirmation"),
])
def test_held_ml_uncertainty_does_not_claim_an_undisplayed_option_followup(hold, expected_action):
    engine, spy = at("D5", unresolved_with_options("D5_SALARY", "D5_WITHDRAWALS"))
    text = "My wages cover everything; my savings are untouched."
    engine.state.answers["D5"].raw_text = text
    result = engine._submit_ml_answer(
        "D5", text, care=hold == "care", support=hold == "support", pace=hold == "pace",
        teachback=False, previous_raw=None, flags=set(),
    )
    assert result["action"] == expected_action
    assert "followup_kind" not in result
    assert "followup" not in result
    assert engine.state.answers["D5"].candidate_option_id is None
    assert spy.calls == [("D5", text)]


def test_option_uncertainty_preserves_the_required_own_words_followup():
    engine, spy = at("D11", unresolved_with_options("D11_LOSS_POSSIBLE", "D11_RECOVERY_ALWAYS"))
    record = engine.state.answers["D11"]
    record.context_details["understanding.teachback_required"] = "true"
    text = SPEC.question("D11").options[0].label
    result = engine.submit_answer(text)
    assert result["action"] == "understanding_hold"
    assert result["followup"] == UNDERSTANDING_FOLLOWUP
    assert "followup_kind" not in result
    assert record.candidate_option_id is None
    assert record.selected_option_id is None
    assert spy.calls == [("D11", text)]


def test_option_uncertainty_cap_does_not_offer_another_option_followup():
    engine, spy = at("D5", unresolved_with_options("D5_SALARY", "D5_WITHDRAWALS"))
    text = "My wages cover everything; my savings are untouched."
    for _ in range(3):
        result = engine.submit_answer(text)
    assert result["action"] == "finish_incomplete_or_pause"
    assert "followup" not in result
    assert "followup_kind" not in result
    assert engine.state.answers["D5"].candidate_option_id is None
    assert engine.state.answers["D5"].selected_option_id is None
    assert spy.calls == [("D5", text)] * 3
