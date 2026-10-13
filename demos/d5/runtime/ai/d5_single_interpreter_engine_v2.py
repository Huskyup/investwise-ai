"""Opt-in D5 wording from verified v2 decisions; normal factory is unchanged.

No source-word matching, extra interpreter, free-form model text rendering or
changes to control/state transitions. Follow-up topics come from the same call.
Confirmation quotes validated spans of the user's reply as data.
"""
import json

from ai.d5_single_interpreter_engine import D5SingleInterpreterEngine
from ai.d5_single_interpreter_contract_v2 import SOURCE, SOURCE_USE_TOPICS


D5_EXPLANATION = (
    "This asks what pays your housing, food and bills now. Pension payments "
    "count when you receive and use them for these costs; simply holding money "
    "inside a pension fund does not count. Receiving money does not by itself "
    "mean you spend it on living costs. You can name one source or several. "
    "Benefits and regular support share one answer category."
)


class D5BusinessStandardEngine(D5SingleInterpreterEngine):
    def _set_candidate(self, qid, option_id, *, source, reason, flags=None):
        # The inherited guard verifies the old receipt first, then binds a new
        # receipt after setting the candidate with this route's provenance.
        if qid == "D5" and source == "d5_single_interpreter_v1":
            source = SOURCE
        return super()._set_candidate(qid, option_id, source=source,
                                     reason=reason, flags=flags)

    def _d5_unresolved(self, **kwargs):
        result = super()._d5_unresolved(**kwargs)
        # Keep care, accessibility, support, pause and exhausted-budget routes.
        if (self.d5_interpreter.context_limit_reached
                and result.get("action") in {"clarify", "finish_incomplete_or_pause"}):
            result.pop("followup", None)
            result["action"] = "context_limit"
            result["message"] = (
                "This example has reached its short conversation limit. No interpretation was made. "
                "Use /new and give the current funding situation to start afresh."
            )
            return result
        if result.get("action") != "clarify":
            return result
        decision = self.d5_interpreter.last_decision
        text = self._record("D5").raw_text or ""
        if (decision is None or decision.outcome not in {"dialogue_only", "abstention"}
                or not self.d5_interpreter.verify_decision(decision, text, spec=self.spec)
                or decision.interpretation is None):
            return result
        meaning = decision.interpretation
        topic = meaning.missing_information[0]
        if topic in SOURCE_USE_TOPICS:
            category = topic.split(":", 1)[1]
            labels = {option.id: option.label.lower() for option in self.spec.question("D5").options}
            question = (
                f"Does money from {labels[category]} currently pay any of your living "
                "costs? You can say yes, no or that you are still unsure."
            )
        else:
            question = {
                "current_funding_unknown": (
                    "Which sources, if any, actually pay your housing, food and "
                    "bills now? They may differ from money you receive or hold. "
                    "You can name another source or leave this unresolved."
                ),
                "complete_answer_needed": (
                    "Which earlier source are you adding to or changing, and how is it "
                    "used now? Please name it so I do not guess what you mean."
                ),
                "question_meaning": D5_EXPLANATION + " What currently pays these costs for you?",
                "reply_unclear": (
                    "I haven't understood your wording. Could you describe what pays "
                    "your living costs in another way? You can leave this unresolved."
                ),
            }.get(topic)
        if question is not None:
            if meaning.semantic_bucket == "undecided":
                question = "It is fine to be unsure. " + question
            result["followup"] = question
            result["clarification_topic"] = topic
        return result

    def submit_answer(self, text, *, explicit_option_id=None):
        result = super().submit_answer(text, explicit_option_id=explicit_option_id)
        if (result.get("question_id") == "D5" and result.get("action") == "explain"
                and result.get("definition_only") is True
                and result.get("help_explanation_provided") is True):
            # A single authored D5 definition: no phrase detection or model call.
            result["help_prompt"] = D5_EXPLANATION
        if result.get("question_id") != "D5" or result.get("action") != "confirm":
            return result
        receipt = self._d5_receipt
        if receipt is None or not self._valid_receipt(text, result.get("candidate_option_id")):
            return result
        meaning = receipt.decision.interpretation
        # Category labels are broader than the user's actual sources. Keep the
        # exact validated evidence, including exclusions within an active category.
        active = list(dict.fromkeys(fact.evidence for fact in meaning.facts
                                    if fact.currently_funds_customer))
        if meaning.option_id == "D5_NO_REGULAR":
            playback = "You have no regular source paying your living costs at the moment."
        else:
            quotes = "; ".join(json.dumps(quote, ensure_ascii=False) for quote in active)
            playback = f"I understand your current living-cost funding as:\n{quotes}"
        if receipt.decision.context.history:
            categories = {fact.source_category for fact in meaning.facts if fact.currently_funds_customer}
            labels = [option.label for option in self.spec.question("D5").options if option.id in categories]
            if labels:
                # Historical quotes may still contain uncertainty which the
                # current reply has resolved. State the verified relation first;
                # retain quotes as provenance, not as the current conclusion.
                playback = ("Current funding categories: " + "; ".join(labels) + ".\n"
                            "Your specific source wording is quoted below; these are the questionnaire groups.\n"
                            "Supporting wording from this example:\n" + quotes)
            playback = "Your latest reply: " + json.dumps(text, ensure_ascii=False) + "\n" + playback
        excluded = list(dict.fromkeys(fact.evidence for fact in meaning.facts
                        if not fact.currently_funds_customer
                        and fact.source_category != "D5_NO_REGULAR"
                        and (fact.owner == "other" or fact.time in {"past", "future"}
                             or fact.pays_living_costs == "no")))
        if excluded:
            quotes = "; ".join(json.dumps(quote, ensure_ascii=False) for quote in excluded)
            playback += f"\nNot counted as current funding, from your words:\n{quotes}"
        result["confirmation_text"] = playback + "\nHave I understood correctly?"
        return result
