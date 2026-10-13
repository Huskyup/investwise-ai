"""Opt-in ML + GPT D5 wiring over the unchanged ChatGPT-plan transport."""
from types import MappingProxyType

from session import bootstrap
bootstrap()
from ai.d5_single_interpreter_transport import SingleInterpreterGenerator
from local_session import LocalD5Session


class GPTMLGenerator(SingleInterpreterGenerator):
    # Used to bind interpreter identity, not as a substitute for the transport's
    # validation of the actual completed provider response.
    metadata = MappingProxyType({
        "model": "gpt-6.1-sol", "reasoning_effort": "low",
        "backend": "existing_chatgpt_plan_single_interpreter",
    })


class GPTMLSession(LocalD5Session):
    """Reuse the existing routing and receipts, with truthful GPT provenance."""

    def __init__(self, backend, output_dir, ml_resolver=None, *, backend_name="gpt"):
        if backend_name != "gpt":
            raise ValueError("This entry requires the GPT route")
        super().__init__(backend, output_dir, ml_resolver=ml_resolver,
                         backend_name="gpt")
