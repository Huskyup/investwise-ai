"""Offline checks of the local D5 integration; no Qwen or credential access."""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
from session import bootstrap, HERE, REPOSITORY, DemoStopped
bootstrap()
from local_session import LocalD5Session
from ai.all_question_ml import QuestionMLResolution
from ai.d5_single_interpreter_contract_v2 import D5DialogueContext, MAX_CONTEXT_TURNS

OLD = REPOSITORY / 'docs/d5-semantic-repair/evidence/after'
ROWS = json.loads((OLD / 'inputs.json').read_text())['rows']
SAVED = {r['id']: json.loads((OLD / 'records' / (r['id'] + '.json')).read_text()) for r in ROWS}
CONTEXT = [json.loads((REPOSITORY / 'docs/d5-context-verification-2026-10-13/records' /
                      f'CONTEXT-{i:02d}.json').read_text()) for i in range(1, 5)]


def forbidden(*args, **kwargs):
    raise AssertionError('Network and live local inference are forbidden in offline checks')


class ML:
    source_hash = 'offline-structural-ml-fixture'
    def __init__(self, result):
        self.result, self.calls = result, []
    def resolve(self, qid, text):
        self.calls.append((qid, text))
        return self.result


class Replay:
    metadata = {'model': 'offline-saved-output-fixture', 'live': False}
    def __init__(self, outputs=()):
        self.outputs, self.calls, self.last_call, self.case_id = list(outputs), 0, {}, None
        self.requests = []
    def __call__(self, messages, schema):
        self.requests.append(messages)
        self.calls += 1
        self.last_call = {'offline_replay': True, 'actual_calls': 0}
        if not self.outputs:
            raise AssertionError('Unexpected replay')
        raw = self.outputs.pop(0)
        if isinstance(raw, Exception):
            raise raw
        return raw
    def close(self):
        pass


def uncertain():
    return QuestionMLResolution(model_uncertain=True, reason='option_model_uncertainty',
        intent_set=frozenset({'clarity'}), option_set=frozenset({'D5_SALARY', 'D5_PENSION_PAYMENTS'}))


def clear(option):
    return QuestionMLResolution(candidate_option_id=option, ordinary_bucket='Clarity',
        intent_set=frozenset({'clarity'}), option_set=frozenset({option}),
        reason='option_identified_requires_confirmation')


class LocalChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='d5-local-software-')
        self.addCleanup(self.temp.cleanup)
        self.n = 0
    def session(self, resolution=None, outputs=()):
        self.n += 1
        path = Path(self.temp.name) / str(self.n)
        path.mkdir(mode=0o700)
        backend = Replay(outputs)
        session = LocalD5Session(backend, path, ml_resolver=ML(resolution or uncertain()))
        return session

    def test_ml_candidate_requires_confirmation_and_never_calls_qwen(self):
        s = self.session(clear('D5_PENSION_PAYMENTS'))
        result = s.submit(ROWS[0]['text'])
        self.assertEqual(result['candidate_option_id'], 'D5_PENSION_PAYMENTS')
        self.assertIn(ROWS[0]['text'], result['confirmation_text'])
        self.assertEqual((s.ml_calls, s.backend.calls), (1, 0))
        self.assertFalse(s.confirmed)
        self.assertEqual(len(s.interpreter.context.history), 1)
        self.assertEqual(s.command('/confirm')['action'], 'd5_complete')
        self.assertTrue(s.confirmed)
        self.assertIsNone(s.engine.state.saved_version)
        self.assertEqual((s.ml_calls, s.backend.calls), (1, 0))

    def test_ml_business_veto_falls_through_without_double_clarification(self):
        row = SAVED['D5-STD-01']
        # The unchanged veto rejects unsupported benefits, but does not certify
        # every relationship involving savings. Keep that limitation explicit.
        s = self.session(clear('D5_BENEFITS_SUPPORT'), [row['raw_output']])
        result = s.submit(row['input'])
        self.assertEqual(result['candidate_option_id'], 'D5_PENSION_PAYMENTS')
        self.assertEqual((s.ml_calls, s.backend.calls), (1, 1))
        self.assertEqual(s.engine.state.answers['D5'].clarification_turns, 0)
        self.assertEqual(len(s.interpreter.context.history), 1)
        limited = self.session(clear('D5_WITHDRAWALS'))
        self.assertEqual(limited.submit(row['input'])['candidate_option_id'], 'D5_WITHDRAWALS')
        self.assertFalse(limited.confirmed)

    def test_ml_nonclear_results_are_not_model_uncertainty(self):
        for label in ('Undecided', 'Confusion'):
            with self.subTest(label=label):
                resolution = QuestionMLResolution(ordinary_bucket=label,
                    semantic_undecided=label == 'Undecided', intent_set=frozenset({label.lower()}))
                s = self.session(resolution)
                result = s.submit(ROWS[9]['text'])
                self.assertEqual(result['bucket'], label)
                self.assertFalse(result.get('model_uncertain', False))
                self.assertIsNone(s.engine.state.answers['D5'].candidate_option_id)
                self.assertEqual((s.ml_calls, s.backend.calls), (1, 0))
                self.assertEqual(len(s.interpreter.context.history), 1)

    def test_ml_answer_is_retained_for_a_contextual_correction(self):
        s = self.session(clear('D5_PENSION_PAYMENTS'), [SAVED['D5-STD-02']['raw_output']])
        s.submit(ROWS[0]['text'])
        s.command('/confirm')
        s.command('/change')
        self.assertFalse(s.confirmed)
        self.assertIsNone(s.engine.state.answers['D5'].candidate_option_id)
        result = s.submit(ROWS[1]['text'])
        self.assertEqual(result['candidate_option_id'], 'D5_MULTIPLE')
        data = json.loads(s.backend.requests[0][1]['content'])
        self.assertEqual(data['dialogue_context']['history'][0]['reply'], ROWS[0]['text'])
        self.assertTrue(data['dialogue_context']['correction_requested'])
        self.assertEqual((s.ml_calls, s.backend.calls), (1, 1))
        self.assertEqual(s.command('/confirm')['action'], 'd5_complete')

    def test_stale_ml_candidate_cannot_be_confirmed(self):
        s = self.session(clear('D5_PENSION_PAYMENTS'))
        s.submit(ROWS[0]['text'])
        s.engine.state.answers['D5'].candidate_option_id = 'D5_MULTIPLE'
        result = s.command('/confirm')
        self.assertNotEqual(result['action'], 'd5_complete')
        self.assertFalse(s.confirmed)
        self.assertIsNone(s.engine.state.answers['D5'].candidate_option_id)
        self.assertEqual((s.ml_calls, s.backend.calls), (1, 0))

    def test_controls_precede_both_models(self):
        s = self.session()
        self.assertEqual(s.command('/help')['action'], 'explain')
        self.assertEqual(s.command('/pause')['action'], 'pause')
        self.assertEqual(s.submit(ROWS[4]['text'])['action'], 'paused')
        s.command('/resume')
        self.assertEqual(s.command('/stop')['action'], 'stop')
        s.command('/resume')
        self.assertEqual(s.submit(ROWS[0]['text'])['action'], 'stop')
        self.assertEqual((s.ml_calls, s.backend.calls), (0, 0))
        self.assertEqual(s.interpreter.context.history, ())
        s.command('/new')
        self.assertEqual(s.submit('I want to jump off a building')['action'], 'safety_stop')
        self.assertEqual(s.command('/confirm')['action'], 'safety_stop')
        self.assertEqual((s.ml_calls, s.backend.calls), (0, 0))

    def test_history_bound_prevents_either_model(self):
        s = self.session()
        s.interpreter.context = D5DialogueContext(history=((s.question, ROWS[0]['text']),) * MAX_CONTEXT_TURNS,
                                                  pending_prompt=s.question)
        result = s.submit(ROWS[0]['text'])
        self.assertEqual(result['action'], 'context_limit')
        self.assertEqual((s.ml_calls, s.backend.calls), (0, 0))

    def test_invalid_qwen_output_remains_unresolved(self):
        s = self.session(outputs=['{"option_id":"D5_SINGLE"}'])
        result = s.submit(ROWS[0]['text'])
        self.assertIsNone(s.engine.state.answers['D5'].candidate_option_id)
        self.assertEqual(result['contract_outcome'], 'rejection')
        self.assertEqual((s.ml_calls, s.backend.calls), (1, 1))

    def test_runtime_failure_halts_without_retry_or_gpt(self):
        s = self.session(outputs=[RuntimeError('offline injected failure')])
        with self.assertRaises(DemoStopped):
            s.submit(ROWS[0]['text'])
        with self.assertRaises(DemoStopped):
            s.submit(ROWS[0]['text'])
        self.assertEqual((s.ml_calls, s.backend.calls), (1, 1))

    def test_saved_four_turn_context_sequence_and_new_reset(self):
        s = self.session(outputs=[r['raw_output'] for r in CONTEXT])
        self.assertEqual(s.submit(CONTEXT[0]['input'])['bucket'], 'Undecided')
        self.assertEqual(s.submit(CONTEXT[1]['input'])['candidate_option_id'], 'D5_MULTIPLE')
        s.command('/confirm')
        s.command('/change')
        self.assertEqual(s.submit(CONTEXT[2]['input'])['candidate_option_id'], 'D5_PENSION_PAYMENTS')
        s.command('/confirm')
        self.assertEqual((s.ml_calls, s.backend.calls), (1, 3))
        s.command('/new')
        self.assertEqual(s.interpreter.context.history, ())
        result = s.submit(CONTEXT[3]['input'])
        self.assertIsNone(s.engine.state.answers['D5'].candidate_option_id)
        self.assertEqual(result['clarification_topic'], 'reply_unclear')
        self.assertEqual(s.backend.calls, 4)
        self.assertEqual(json.loads(s.backend.requests[-1][1]['content'])['dialogue_context']['history'], [])

    def test_scorer_checks_saved_relations_and_specific_followup(self):
        from copy import deepcopy
        from local_evaluate import case_match
        expectations = json.loads((OLD / 'expectations.json').read_text())['cases']
        for identifier, record in SAVED.items():
            with self.subTest(identifier=identifier):
                record = dict(record, id=identifier)
                self.assertTrue(case_match(record, expectations[identifier]))
        record = deepcopy(SAVED['D5-STD-01'])
        record['id'] = 'D5-STD-01'
        record['raw']['facts'][0]['pays_living_costs'] = 'yes'
        self.assertFalse(case_match(record, expectations['D5-STD-01']))
        record = deepcopy(SAVED['D5-STD-10'])
        record.update(qwen_calls=0, raw=None)
        record['result'].pop('clarification_topic', None)
        self.assertFalse(case_match(record, expectations['D5-STD-10']))

    def test_existing_evaluator_sequence_with_saved_outputs_only(self):
        from local_evaluate import existing
        backend = Replay([SAVED[row['id']]['raw_output'] for row in ROWS[:-1]]
                         + [r['raw_output'] for r in CONTEXT])
        self.assertTrue(existing(backend, Path(self.temp.name)))
        self.assertEqual(backend.calls, 14)
        summary = json.loads((Path(self.temp.name) / 'context-summary.json').read_text())
        self.assertTrue(summary['passed'])
        self.assertTrue(all(c['zero_calls'] for c in summary['controls']))


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
    with patch.object(socket, 'create_connection', forbidden), patch.object(socket.socket, 'connect', forbidden), \
         patch.object(LocalGenerator, '__call__', forbidden):
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(LocalChecks))
    (output / 'software.log').write_text(stream.getvalue())
    hashes = {str(p.relative_to(REPOSITORY)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in HERE.glob('local_*.py')}
    receipt = {'mode': 'offline fixtures only; not semantic-performance evidence',
               'tests_run': result.testsRun, 'success': result.wasSuccessful(),
               'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
               'model_inference_calls': 0, 'authentication_calls': 0, 'hashes': hashes}
    (output / 'software.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(stream.getvalue())
    print(json.dumps(receipt))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
