"""Opt-in D5 routing: unchanged first-turn ML, contextual interpretation.

ML and LLM candidates have separate receipts. A validator can only retain or
reject an ML proposal; no ML proposal or probability is sent to the LLM.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from ai.bounded_answers import BoundedAnswer
from ai.conversation_engine import ConversationEngine
from ai.conversation_state import AnswerStatus
from ai.d5_candidate_validation import validate_d5_candidate
from ai.d5_single_interpreter_contract_v2 import D5SingleContractError
from ai.d5_single_interpreter_engine_v2 import D5BusinessStandardEngine

ML_SOURCE = "d5_local_baseline_ml"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class MLProposal:
    """An issued immutable proposal, not a fabricated LLM interpretation."""
    text: str
    option_id: str
    identity_sha256: str
    spec_sha256: str
    intent_set: frozenset[str]
    option_set: frozenset[str]
    details: tuple[tuple[str, str], ...]
    flags: frozenset[str]


@dataclass(frozen=True)
class MLReceipt:
    proposal: MLProposal
    profile_version: int
    record_sha256: str


class LocalD5Engine(D5BusinessStandardEngine):
    def __init__(self, business_spec, *, ml_resolver, ml_identity,
                 d5_interpreter, question_resolver, store=None, backend_name="qwen"):
        if backend_name not in {"qwen", "gpt"}:
            raise ValueError("Unsupported D5 interpretation backend")
        super().__init__(business_spec, d5_interpreter=d5_interpreter,
                         question_resolver=question_resolver, store=store)
        self.backend_name = backend_name
        self.ml_resolver = ml_resolver
        self.ml_identity = ml_identity
        self.ml_calls = 0
        self.last_route = "control"
        self.last_ml_evidence = None
        self.interpreted_reply = False
        self._ml_receipt = None
        self._issued_ml_proposal = None

    def _identity(self):
        return digest({"snapshot": self.ml_identity,
                       "predictor_source": self.ml_resolver.source_hash})

    def _bind_ml(self, proposal):
        self._ml_receipt = MLReceipt(proposal, self.state.profile_version,
                                     self._d5_record_digest())

    def _valid_ml_receipt(self, text, option_id=None):
        receipt = self._ml_receipt
        if receipt is None:
            return False
        proposal = receipt.proposal
        return bool(
            proposal is self._issued_ml_proposal and proposal.text == text
            and proposal.identity_sha256 == self._identity()
            and proposal.spec_sha256 == digest(self.spec.payload)
            and proposal.intent_set == frozenset({"clarity"})
            and proposal.option_set == frozenset({proposal.option_id})
            and (option_id is None or option_id == proposal.option_id)
            and receipt.profile_version == self.state.profile_version
            and receipt.record_sha256 == self._d5_record_digest())

    def _clear_d5_financial_state(self):
        super()._clear_d5_financial_state()
        self._ml_receipt = None
        self._issued_ml_proposal = None

    def _submit_ml_answer(self, qid, text, care, support, pace, teachback,
                          previous_raw, flags, *, explicit_selection=None):
        if qid != "D5":
            raise RuntimeError("Only D5 is available in the local demonstration")
        context = self.d5_interpreter.context
        self.d5_interpreter.last_decision = None
        self.d5_interpreter.context_limit_reached = False
        try:
            context.validate(text)
        except D5SingleContractError as exc:
            self._clear_d5_financial_state()
            self.last_route = "input_rejected"
            self.d5_interpreter.context_limit_reached = str(exc) == "dialogue_context_limit"
            return self._d5_unresolved(reason=str(exc), care=care, support=support,
                                       pace=pace, previous_raw=previous_raw)

        if not context.history and not context.correction_requested:
            self.ml_calls += 1
            resolved = self.ml_resolver.resolve(qid, text)
            self.interpreted_reply = True
            self.last_ml_evidence = {
                "source": resolved.source, "source_hash": self.ml_resolver.source_hash,
                "identity_sha256": self._identity(), "bucket": resolved.ordinary_bucket,
                "candidate": resolved.candidate_option_id,
                "intent_set": sorted(resolved.intent_set), "option_set": sorted(resolved.option_set),
                "intent_probabilities": dict(resolved.intent_probabilities),
                "option_probabilities": dict(resolved.option_probabilities),
                "model_uncertain": resolved.model_uncertain, "reason": resolved.reason,
            }
            clear = (not resolved.model_uncertain and resolved.ordinary_bucket == "Clarity"
                     and resolved.candidate_option_id is not None
                     and resolved.intent_set == frozenset({"clarity"})
                     and resolved.option_set == frozenset({resolved.candidate_option_id}))
            # This pure veto runs before financial state changes. It may not
            # introduce a replacement candidate, even if it infers another one.
            validation = (validate_d5_candidate(self.spec, text, resolved.candidate_option_id)
                          if clear else None)
            if validation is not None:
                self.last_ml_evidence["business_validation"] = {
                    "option_id": validation.option_id, "reason": validation.reason}
            if (validation is not None and validation.option_id == resolved.candidate_option_id
                    and validation.bucket == "Clarity"
                    and explicit_selection in {None, resolved.candidate_option_id}):
                self._clear_d5_financial_state()
                proposal = MLProposal(text, resolved.candidate_option_id, self._identity(),
                    digest(self.spec.payload), frozenset(resolved.intent_set),
                    frozenset(resolved.option_set), tuple(sorted(validation.context_details.items())),
                    frozenset(validation.flags))
                self._issued_ml_proposal = proposal
                self._bind_ml(proposal)
                self.last_route = "ml"
                result = self._set_candidate(qid, proposal.option_id, source=ML_SOURCE,
                    reason="unchanged_ml_singletons_and_packaged_d5_veto",
                    flags=set(flags or ()) | set(proposal.flags))
                result = self._pace_supported_answer(qid, result, care, support, pace)
                result.update(bucket="Clarity", contract_outcome="ml_financial_candidate")
                return result
            bucket = resolved.ordinary_bucket
            if (not resolved.model_uncertain and resolved.candidate_option_id is None
                    and bucket in {"Undecided", "Confusion"}
                    and resolved.intent_set == frozenset({bucket.lower()})):
                self._clear_d5_financial_state()
                self._record(qid).source = ML_SOURCE
                self.last_route = "ml"
                return self._d5_unresolved(reason=resolved.reason or "ml_dialogue_only",
                    bucket=bucket, outcome="ml_dialogue_only", care=care, support=support,
                    pace=pace, previous_raw=previous_raw)
            self.last_route = f"ml_then_{self.backend_name}"
        else:
            self.last_route = f"{self.backend_name}_context"
        before = self.d5_interpreter.calls
        result = super()._submit_ml_answer(qid, text, care, support, pace, teachback,
            previous_raw, flags, explicit_selection=explicit_selection)
        self.interpreted_reply |= self.d5_interpreter.calls > before
        return result

    def _set_candidate(self, qid, option_id, *, source, reason, flags=None):
        if qid != "D5" or source != ML_SOURCE:
            if qid == "D5":
                self._ml_receipt = None
                self._issued_ml_proposal = None
            return super()._set_candidate(qid, option_id, source=source, reason=reason, flags=flags)
        text = self._record(qid).raw_text or ""
        if not self._valid_ml_receipt(text, option_id):
            self._clear_d5_financial_state()
            return self._d5_unresolved(reason="stale_or_untrusted_ml_candidate")
        proposal = self._ml_receipt.proposal
        self._record(qid).context_details.update(dict(proposal.details))
        # Only this separately checked ML receipt authorises the base setter.
        result = ConversationEngine._set_candidate(self, qid, option_id,
            source=source, reason=reason, flags=flags)
        self._bind_ml(proposal)
        return result

    def _profile_evidence(self, qid, text):
        if qid == "D5" and self._record(qid).source == ML_SOURCE:
            if (not self.state.paused and not self.state.stopped_for_safety
                    and "user_stop" not in self.state.active_holds
                    and self._valid_ml_receipt(text)):
                return BoundedAnswer("Clarity", self._ml_receipt.proposal.option_id,
                                     "verified_ml_receipt")
            return BoundedAnswer(None, reason="stale_or_untrusted_ml_evidence")
        return super()._profile_evidence(qid, text)

    def confirm_current(self, confirmed):
        qid = self.state.current_question_id
        if qid != "D5" or self._record(qid).source != ML_SOURCE:
            return super().confirm_current(confirmed)
        if self.state.paused or self.state.stopped_for_safety:
            return ConversationEngine.confirm_current(self, confirmed)
        if (self._record(qid).status != AnswerStatus.CANDIDATE
                or not self._valid_ml_receipt(self._record(qid).raw_text or "",
                                              self._record(qid).candidate_option_id)):
            self._clear_d5_financial_state()
            return self._d5_unresolved(reason="stale_or_untrusted_ml_confirmation")
        proposal = self._ml_receipt.proposal
        result = ConversationEngine.confirm_current(self, confirmed)
        if result.get("action") in {"continue", "final_review"}:
            self._bind_ml(proposal)
        elif result.get("action") == "reask":
            self._ml_receipt = None
            self._issued_ml_proposal = None
        return result

    def correct_answer(self, question_id):
        result = super().correct_answer(question_id)
        if "D5" in result["invalidated_questions"]:
            self._ml_receipt = None
            self._issued_ml_proposal = None
        return result

    def submit_answer(self, text, *, explicit_option_id=None):
        self.last_route = "control"
        self.last_ml_evidence = None
        self.interpreted_reply = False
        result = super().submit_answer(text, explicit_option_id=explicit_option_id)
        if (result.get("action") == "confirm" and self._record("D5").source == ML_SOURCE
                and self._valid_ml_receipt(text, result.get("candidate_option_id"))):
            label = self.spec.option("D5", result["candidate_option_id"]).label
            result["confirmation_text"] = (
                "You said: " + json.dumps(text, ensure_ascii=False) + "\n"
                "Questionnaire category: " + label + ".\n"
                "This category groups related sources; your specific source is the wording above. "
                "Have I understood correctly?")
        return result
