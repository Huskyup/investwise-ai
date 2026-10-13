"""Offline checks for the opt-in ML + GPT D5 terminal, using existing fixtures.

These checks establish software behaviour, not live semantic performance. The
same eleven saved examples and four saved context turns are reused; there is no
authentication, model inference or new semantic evaluation case.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
from local_verify import (CONTEXT, ML, ROWS, SAVED, LocalChecks, Replay,
                          clear, forbidden, uncertain)
from session import HERE, REPOSITORY
from gpt_ml import GPTMLGenerator, GPTMLSession
from local_engine import ML_SOURCE
from ai.d5_single_interpreter_contract_v2 import (PROMPT_PATH, SOURCE,
                                                output_schema)
from ai.d5_single_interpreter_transport import (SingleInterpreterGenerator,
                                               request_payload)
from ai.d5_tool_free_gpt_experiment import generation_schema, passive_text


class GPTMLChecks(LocalChecks):
    """Repeat established routing checks against the GPT-labelled session."""

    def session(self, resolution=None, outputs=()):
        self.n += 1
        path = Path(self.temp.name) / str(self.n)
        path.mkdir(mode=0o700)
        # Saved fixtures remain labelled as offline fixtures. They are not
        # model calls and must not manufacture real-provider provenance.
        return GPTMLSession(Replay(outputs), path,
                            ml_resolver=ML(resolution or uncertain()))

    def test_existing_evaluator_sequence_with_saved_outputs_only(self):
        from local_evaluate import existing
        backend = Replay([SAVED[row['id']]['raw_output'] for row in ROWS[:-1]]
                         + [row['raw_output'] for row in CONTEXT])
        self.assertTrue(existing(backend, Path(self.temp.name), complete_bank=True,
                                 session_factory=GPTMLSession, backend_name='gpt'))
        self.assertEqual(backend.calls, 14)
        summary = json.loads((Path(self.temp.name) / 'context-summary.json').read_text())
        self.assertTrue(summary['passed'])
        self.assertTrue(all(c['zero_calls'] for c in summary['controls']))
        scores = json.loads((Path(self.temp.name) / 'existing-summary.json').read_text())
        for score in scores['cases']:
            self.assertIn('gpt_calls', score)
            self.assertNotIn('qwen_calls', score)

    def test_existing_gpt_request_boundary_and_unsteered_input(self):
        # Deliberately rejected ML proposal uses an existing reply. Nothing
        # from that proposal or its probabilities may reach the GPT request.
        s = self.session(clear('D5_BENEFITS_SUPPORT'), [SAVED['D5-STD-01']['raw_output']])
        s.submit(ROWS[0]['text'])
        messages = s.backend.requests[0]
        unchanged_messages = deepcopy(messages)
        schema = output_schema()
        unchanged_schema = deepcopy(schema)
        payload = request_payload(messages, schema)
        self.assertEqual(messages, unchanged_messages)
        self.assertEqual(schema, unchanged_schema)
        self.assertEqual(set(payload), {'model', 'reasoning', 'input', 'instructions',
                                       'tools', 'tool_choice', 'store', 'stream', 'text'})
        self.assertEqual(payload['model'], 'gpt-6.1-sol')
        self.assertEqual(payload['reasoning'], {'effort': 'low'})
        self.assertEqual(payload['tools'], [])
        self.assertEqual(payload['tool_choice'], 'none')
        self.assertIs(payload['store'], False)
        self.assertIs(payload['stream'], True)
        self.assertEqual(payload['instructions'], PROMPT_PATH.read_text())
        self.assertEqual(payload['input'], [messages[1]])
        self.assertEqual(payload['text']['format'], {
            'type': 'json_schema', 'name': 'd5_single_interpreter_v1', 'strict': True,
            'schema': generation_schema(schema)})
        supplied = json.loads(payload['input'][0]['content'])
        self.assertEqual(set(supplied), {'current_question', 'allowed_options',
                                      'original_reply', 'dialogue_context'})
        self.assertEqual(supplied['original_reply'], ROWS[0]['text'])
        self.assertEqual(supplied['dialogue_context']['history'], [])
        self.assertNotIn('LOCAL CATEGORY CONSISTENCY', payload['instructions'])

    def test_provider_metadata_and_original_transport_are_reused(self):
        self.assertIs(GPTMLGenerator.__call__, SingleInterpreterGenerator.__call__)
        generator = GPTMLGenerator(Path(self.temp.name) / 'traces', forbidden)
        self.assertEqual(generator.metadata['model'], 'gpt-6.1-sol')
        self.assertEqual(generator.metadata['reasoning_effort'], 'low')
        self.assertEqual(generator.calls, 0)
        self.assertEqual(generator.last_call, {})

    def test_gpt_receipt_routes_and_counts_remain_distinct_from_ml(self):
        s = self.session(outputs=[SAVED['D5-STD-01']['raw_output'],
                                  SAVED['D5-STD-02']['raw_output']])
        s.submit(ROWS[0]['text'])
        record = s.last_record
        self.assertEqual(record['route'], 'ml_then_gpt')
        self.assertEqual((record['ml_calls'], record['gpt_calls'],
                          record['actual_model_calls']), (1, 1, 1))
        self.assertNotIn('qwen_calls', record)
        self.assertEqual(record['answer_source'], SOURCE)
        self.assertIsNone(s.engine._ml_receipt)
        self.assertIs(s.engine._d5_receipt.decision, s.interpreter.last_decision)
        self.assertTrue(s.interpreter.verify_decision(
            s.engine._d5_receipt.decision, ROWS[0]['text'],
            option_id='D5_PENSION_PAYMENTS'))
        s.command('/confirm')
        s.command('/change')
        s.submit(ROWS[1]['text'])
        self.assertEqual(s.last_record['route'], 'gpt_context')
        self.assertEqual((s.last_record['ml_calls'], s.last_record['gpt_calls']), (0, 1))
        self.assertIsNone(s.engine._ml_receipt)

        ml = self.session(clear('D5_PENSION_PAYMENTS'))
        ml.submit(ROWS[0]['text'])
        self.assertEqual(ml.last_record['route'], 'ml')
        self.assertEqual(ml.last_record['answer_source'], ML_SOURCE)
        self.assertEqual((ml.last_record['ml_calls'], ml.last_record['gpt_calls']), (1, 0))
        self.assertIsNotNone(ml.engine._ml_receipt)
        self.assertIsNone(ml.engine._d5_receipt)
        self.assertIsNone(ml.interpreter.last_decision)

    def test_stale_gpt_candidate_cannot_be_confirmed(self):
        s = self.session(outputs=[SAVED['D5-STD-01']['raw_output']])
        s.submit(ROWS[0]['text'])
        s.engine.state.answers['D5'].candidate_option_id = 'D5_MULTIPLE'
        self.assertNotEqual(s.command('/confirm')['action'], 'd5_complete')
        self.assertFalse(s.confirmed)
        self.assertIsNone(s.engine.state.answers['D5'].candidate_option_id)
        self.assertEqual((s.ml_calls, s.backend.calls), (1, 1))

    def test_passive_provider_boundary_rejects_incomplete_or_tool_output(self):
        valid = {'model': 'gpt-6.1-sol', 'status': 'completed', 'error': None,
                 'tools': [], 'tool_choice': 'none', 'store': False,
                 'reasoning': {'effort': 'low'}, 'output': [{
                     'type': 'message', 'role': 'assistant', 'status': 'completed',
                     'content': [{'type': 'output_text',
                                  'text': SAVED['D5-STD-01']['raw_output']}]}]}
        self.assertEqual(passive_text(valid), SAVED['D5-STD-01']['raw_output'])
        for field, value in [('model', 'offline-wrong-model'), ('status', 'incomplete'),
                             ('tools', [{'type': 'function'}]), ('tool_choice', 'auto'),
                             ('store', True), ('reasoning', {'effort': 'high'}),
                             ('output', [{'type': 'function_call'}]),
                             ('output', [])]:
            with self.subTest(field=field, value=value):
                changed = deepcopy(valid)
                changed[field] = value
                with self.assertRaises((ValueError, RuntimeError)):
                    passive_text(changed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output.is_relative_to(REPOSITORY):
        parser.error('Use a new external directory')
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    stream = io.StringIO()
    from local_transport import LocalGenerator
    from ai.d5_chatgpt_auth import ChatGPTCredentials
    with ExitStack() as stack:
        for owner, attribute in ((socket, 'create_connection'), (socket.socket, 'connect'),
                                 (subprocess, 'Popen'), (SingleInterpreterGenerator, '__call__'),
                                 (LocalGenerator, '__call__'),
                                 (ChatGPTCredentials, 'get_access_token')):
            stack.enter_context(patch.object(owner, attribute, forbidden))
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(GPTMLChecks))
    (output / 'software.log').write_text(stream.getvalue())
    files = sorted(set(HERE.glob('gpt_ml*.py')) | set(HERE.glob('local_*.py')))
    receipt = {'mode': 'offline fixtures only; not semantic-performance evidence',
               'tests_run': result.testsRun, 'success': result.wasSuccessful(),
               'failures': len(result.failures), 'errors': len(result.errors),
               'skipped': len(result.skipped), 'model_inference_calls': 0,
               'authentication_calls': 0,
               'hashes': {str(path.relative_to(REPOSITORY)):
                          hashlib.sha256(path.read_bytes()).hexdigest() for path in files}}
    (output / 'software.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(stream.getvalue())
    print(json.dumps(receipt))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
