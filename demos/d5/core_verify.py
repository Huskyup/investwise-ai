#!/usr/bin/env python3
"""Offline verification of the separate D5 core presentation and local server.

Reuses the original eleven replies and the existing four-turn, eighteen-action
context sequence. Malformed envelopes mutate only existing fixtures. Saved
output replay is not live free-text interpretation or unseen accuracy.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import http.client
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
from core_demo import (ASSETS, COMMANDS, CoreDemo, EVIDENCE, MAX_BODY,
                       RecordedBackend, make_server, read_record, scenario)
from session import DemoStopped, REPOSITORY, external_path, private_directory, write_json
from gpt_ml import GPTMLSession
from ai.d5_single_interpreter_contract_v2 import build_messages, output_schema

OUTPUT = None
DETAILS = {}


def forbidden(*_args, **_kwargs):
    raise AssertionError('Live generation, authentication and subprocesses are forbidden')


def resolution_dict(value):
    return {'candidate': value.candidate_option_id, 'bucket': value.ordinary_bucket,
            'model_uncertain': value.model_uncertain,
            'semantic_undecided': value.semantic_undecided, 'reason': value.reason,
            'intent_set': sorted(value.intent_set), 'option_set': sorted(value.option_set),
            'intent_probabilities': dict(value.intent_probabilities),
            'option_probabilities': dict(value.option_probabilities)}


class CoreChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed = GPTMLSession(RecordedBackend([]), private_directory(OUTPUT / 'baseline'))
        cls.resolver, cls.identity = seed.ml_resolver, seed.ml_identity
        cls.spec = seed.spec
        cls.created = 0

    def demo(self, records=(), mode='live'):
        type(self).created += 1
        directory = private_directory(OUTPUT / f'session-{self.created:03}')
        session = GPTMLSession(RecordedBackend(deepcopy(records)), directory,
                               ml_resolver=self.resolver)
        # This is the actual unchanged resolver, not an ML prediction fixture.
        session.ml_identity = self.identity
        session.new_example()
        return CoreDemo(session, mode=mode)

    def assert_no_financial_display(self, view):
        self.assertIsNone(view['option'])
        self.assertIsNone(view['option_label'])
        self.assertEqual(view['facts'], [])
        self.assertFalse(view['can_confirm'])

    def test_business_assets_preserve_original_inputs_and_gold(self):
        bank = json.loads((ASSETS / 'business-examples.json').read_text())
        source = REPOSITORY / 'docs/d5-semantic-repair/evidence/after'
        rows = json.loads((source / 'inputs.json').read_text())['rows']
        gold = json.loads((source / 'expectations.json').read_text())['cases']
        self.assertEqual([(r['id'], r['text']) for r in bank['cases']],
                         [(r['id'], r['text']) for r in rows])
        for row in bank['cases']:
            self.assertEqual(row['gold'], gold[row['id']])
            for relation in row['business_annotations']['sources']:
                self.assertIn(relation['evidence_quote'], row['text'])
        self.assertEqual(bank['review_status'], 'agent_authored_pending_human_business_sign_off')
        self.assertEqual(len(bank['cases']), 11)
        for identifier in [r['id'] for r in rows] + [f'CONTEXT-{i:02}' for i in range(1, 5)]:
            self.assertEqual(read_record(identifier)['id'], identifier)
        DETAILS['business_asset_cases'] = 11

    def test_real_baseline_parity_and_eleven_saved_outputs(self):
        references = json.loads((EVIDENCE / 'reference-predictions.json').read_text())
        results = []
        for number in range(1, 12):
            identifier = f'D5-STD-{number:02}'
            old = read_record(identifier)
            with self.subTest(case=identifier):
                actual = resolution_dict(self.resolver.resolve('D5', old['input']))
                self.assertEqual(actual, references[identifier])
                demo = self.demo([old])
                view = demo.act(old['input'])
                self.assertIsNone(view['error'])
                self.assertEqual(view['option'], old['candidate'])
                self.assertEqual(view['events'][-1]['action'], old['result']['action'])
                self.assertEqual(view['bucket'], old['result'].get('bucket'))
                self.assertEqual(view['gpt_calls'], 0)
                self.assertEqual(view['ml_calls'], 0 if number == 11 else 1)
                self.assertEqual(view['replayed_outputs'], 0 if number == 11 else 1)
                if old['candidate'] is None:
                    self.assert_no_financial_display(view)
                else:
                    self.assertTrue(view['can_confirm'])
                    self.assertEqual(view['facts'], [{k: f[k] for k in
                        ('source_category', 'owner', 'time', 'pays_living_costs', 'evidence')}
                        for f in old['raw']['facts']])
                results.append({'id': identifier, 'candidate': view['option'],
                                'action': view['events'][-1]['action'], 'passed': True})
        DETAILS['baseline_parity_cases'] = 11
        DETAILS['existing_cases'] = results

    def test_complete_recorded_context_sequence_and_fourteen_zero_call_controls(self):
        demo = self.demo([read_record(f'CONTEXT-{i:02}') for i in range(1, 5)], mode='replay')
        expected = json.loads((EVIDENCE / 'context-summary.json').read_text())
        controls = iter(expected['controls'])
        context_indices = {1: 1, 5: 2, 8: 3, 11: 4}
        snapshots = []
        for index, step in enumerate(scenario()):
            view = demo.act()
            self.assertIsNone(view['error'])
            event = view['events'][-1]
            self.assertEqual(event['input'], step['text'])
            self.assertEqual(event['gpt_calls'], 0)
            if index in context_indices:
                old = read_record(f'CONTEXT-{context_indices[index]:02}')
                self.assertEqual(view['option'], old['candidate'])
                self.assertEqual(event['action'], old['result']['action'])
                self.assertEqual(event['replayed_outputs'], 1)
                self.assertIn('saved_output', event['route'])
            else:
                control = next(controls)
                self.assertEqual(event['action'], control['action'])
                self.assertEqual((event['ml_calls'], event['gpt_calls'], event['replayed_outputs']), (0, 0, 0))
            if index in {6, 9}:
                self.assertEqual(view['status'], 'Confirmed in this session')
                self.assertFalse(view['can_confirm'])
            if index in {7, 10, 11, 12, 13, 14, 15, 16, 17}:
                self.assert_no_financial_display(view)
            if index in {10, 15}:
                self.assertEqual(view['history_count'], 0)
            self.assertIsNone(demo.session.engine.state.saved_version)
            snapshots.append({'step': index + 1, 'action': event['action'],
                              'option': view['option'], 'history_count': view['history_count'],
                              'ml_calls': event['ml_calls'], 'replayed_outputs': event['replayed_outputs']})
        self.assertEqual(next(controls, None), None)
        self.assertEqual(view['step'], 18)
        self.assertEqual(view['replayed_outputs'], 4)
        self.assertEqual(view['ml_calls'], 2)
        with self.assertRaises(ValueError):
            demo.act()
        DETAILS['context_steps'] = snapshots
        DETAILS['context_turns'] = 4
        DETAILS['zero_call_controls'] = 14

    def test_replay_rejects_wrong_context_or_schema_without_consuming_output(self):
        old = read_record('CONTEXT-02')
        backend = RecordedBackend([old])
        messages = build_messages(self.spec, old['input'])
        payload = json.loads(messages[1]['content'])
        context = deepcopy(old['dialogue_context'])
        context['correction_requested'] = not context['correction_requested']
        payload['dialogue_context'] = context
        messages[1]['content'] = json.dumps(payload)
        with self.assertRaises(DemoStopped):
            backend(messages, output_schema())
        payload['dialogue_context'] = old['dialogue_context']
        messages[1]['content'] = json.dumps(payload)
        with self.assertRaises(DemoStopped):
            backend(messages, {})
        for key in ('current_question', 'allowed_options'):
            modified = deepcopy(messages)
            value = deepcopy(payload)
            value[key] = {} if key == 'current_question' else []
            modified[1]['content'] = json.dumps(value)
            with self.assertRaises(DemoStopped):
                backend(modified, output_schema())
        modified = deepcopy(messages)
        modified[0]['content'] += '\n'
        with self.assertRaises(DemoStopped):
            backend(modified, output_schema())
        self.assertEqual((backend.calls, backend.replayed_outputs, len(backend.records)), (0, 0, 1))
        self.assertEqual(backend(messages, output_schema()), old['raw_output'])
        self.assertEqual(backend.replayed_outputs, 1)

    def test_rejected_or_stale_receipts_never_show_financial_facts(self):
        old = read_record('D5-STD-01')
        rejected = deepcopy(old)
        raw = json.loads(rejected['raw_output'])
        raw['option_id'] = 'D5_SALARY'  # Existing facts contradict this envelope field.
        rejected['raw_output'] = json.dumps(raw)
        demo = self.demo([rejected])
        view = demo.act(old['input'])
        self.assertEqual(view['contract_outcome'], 'rejection')
        self.assert_no_financial_display(view)
        view = demo.act('/confirm')
        self.assert_no_financial_display(view)
        stale = self.demo([old])
        stale.act(old['input'])
        stale.session.engine.state.profile_version += 1
        view = stale.act('/confirm')
        self.assert_no_financial_display(view)
        self.assertFalse(stale.session.confirmed)
        self.assertEqual(view['gpt_calls'], 0)

    def test_input_bounds_and_runtime_stop_have_no_retry(self):
        old = read_record('D5-STD-01')
        demo = self.demo([old])
        for invalid in (None, '', ' ', old['input'] * 1000, 12, '/missing'):
            with self.subTest(structural_type=type(invalid).__name__):
                with self.assertRaises(ValueError):
                    demo.act(invalid)
        self.assertEqual((demo.version, demo.session.ml_calls, demo.session.backend.replayed_outputs), (0, 0, 0))
        wrong = deepcopy(old)
        wrong['dialogue_context']['correction_requested'] = True
        halted = self.demo([wrong])
        view = halted.act(old['input'])
        self.assertEqual(view['events'][-1]['action'], 'runtime_stopped')
        self.assert_no_financial_display(view)
        self.assertTrue(view['stopped'])
        with self.assertRaises(ValueError):
            halted.act(old['input'])
        self.assertEqual(halted.session.backend.replayed_outputs, 0)
        self.assertEqual(halted.session.backend.calls, 0)

    def test_saved_overload_envelope_stops_without_a_second_attempt(self):
        class OverloadFixture:
            metadata = {'model': 'offline-error-fixture', 'live': False}
            calls = 0  # Simulated provider attempts, not network requests.
            last_call = {}
            case_id = ''

            def __call__(self, _messages, _schema):
                self.calls += 1
                self.last_call = {'offline_fixture': True, 'actual_network_calls': 0,
                    'provider_error': {'code': 'server_is_overloaded'}}
                raise RuntimeError('Offline injected provider overload')

        demo = self.demo()
        demo.session.backend = OverloadFixture()
        text = read_record('CONTEXT-01')['input']
        view = demo.act(text)
        expected = ('GPT reported that the service is overloaded. No financial answer was accepted. '
                    'This session has stopped without retry or fallback.')
        self.assertEqual(view['error'], expected)
        self.assertTrue(view['stopped'])
        self.assert_no_financial_display(view)
        self.assertEqual(view['events'][-1]['action'], 'runtime_stopped')
        self.assertEqual(view['events'][-1]['route'], 'runtime_stopped')
        self.assertEqual(view['events'][-1]['gpt_calls'], 1)
        self.assertEqual(view['replayed_outputs'], 0)
        for subsequent in [text, *sorted(COMMANDS)]:
            with self.subTest(action='existing reply' if subsequent == text else subsequent):
                with self.assertRaises(ValueError):
                    demo.act(subsequent)
        self.assertEqual(demo.session.backend.calls, 1)
        self.assertEqual((demo.version, len(demo.events)), (1, 1))
        self.assertIsNone(demo.session.engine.state.saved_version)
        DETAILS['overload_failure_envelope'] = {
            'existing_input': 'CONTEXT-01', 'simulated_provider_attempts': 1,
            'actual_network_calls': 0, 'safe_message': True,
            'no_financial_display': True, 'no_retry_for_any_following_action': True}

    def test_loopback_http_authorisation_bounds_and_duplicate_actions(self):
        demo = self.demo([], mode='live')
        server = make_server(demo, 0)
        self.assertEqual(server.server_address[0], '127.0.0.1')
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        port = server.server_port
        host = f'127.0.0.1:{port}'
        def request(method, path, body=None, replacements=None, extra=()):
            payload = json.dumps(body).encode() if isinstance(body, dict) else (body or b'')
            headers = {'Host': host, 'X-D5-Token': demo.token, 'Origin': 'http://' + host,
                       'Content-Type': 'application/json', 'Content-Length': str(len(payload))}
            for key, value in (replacements or {}).items():
                if value is None:
                    headers.pop(key, None)
                else:
                    headers[key] = value
            conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
            try:
                conn.putrequest(method, path, skip_host=True, skip_accept_encoding=True)
                for key, value in list(headers.items()) + list(extra):
                    conn.putheader(key, value)
                conn.endheaders(payload)
                response = conn.getresponse()
                status, raw = response.status, response.read()
                self.assertNotIn(demo.token.encode(), raw)
                self.assertEqual(response.getheader('Cache-Control'), 'no-store')
                self.assertEqual(response.getheader('X-Content-Type-Options'), 'nosniff')
                return status, raw
            finally:
                conn.close()
        try:
            for asset in ('/', '/app.js', '/style.css'):
                self.assertEqual(request('GET', asset)[0], 200)
            for hidden in ('/../session.py', '/%2e%2e/session.py', '/recordings.json', '/business-examples.json'):
                self.assertEqual(request('GET', hidden)[0], 404)
            self.assertEqual(request('GET', '/api/state')[0], 200)
            for replacements in ({'Host': 'example.invalid'}, {'X-D5-Token': None},
                                  {'X-D5-Token': 'invalid'}, {'Origin': 'https://example.invalid'},
                                  {'Origin': None}):
                self.assertEqual(request('POST', '/api/action', {'version': 0, 'text': '/help'}, replacements)[0], 403)
            for header in ('Host', 'Origin', 'X-D5-Token'):
                value = {'Host': host, 'Origin': 'http://' + host, 'X-D5-Token': demo.token}[header]
                self.assertEqual(request('POST', '/api/action', {'version': 0, 'text': '/help'}, extra=[(header, value)])[0], 403)
            for replacements in ({'Content-Length': str(MAX_BODY + 1)}, {'Content-Length': None},
                                  {'Content-Type': 'text/plain'}, {'Transfer-Encoding': 'chunked'}):
                self.assertEqual(request('POST', '/api/action', {'version': 0, 'text': '/help'}, replacements)[0], 400)
            for body in (b'{', {'version': True, 'text': '/help'}, {'version': 0, 'text': '/help', 'extra': 1}):
                self.assertEqual(request('POST', '/api/action', body)[0], 400)
            self.assertEqual(demo.version, 0)
            demo.lock.acquire()
            try:
                self.assertEqual(request('POST', '/api/action', {'version': 0, 'text': '/help'})[0], 409)
                self.assertEqual(request('GET', '/api/state')[0], 409)
            finally:
                demo.lock.release()
            self.assertEqual(request('POST', '/api/action', {'version': 0, 'text': '/help'})[0], 200)
            self.assertEqual(demo.version, 1)
            for version in (0, 2):
                self.assertEqual(request('POST', '/api/action', {'version': version, 'text': '/help'})[0], 409)
            self.assertEqual((demo.version, len(demo.events)), (1, 1))
            self.assertEqual((demo.session.ml_calls, demo.session.backend.calls, demo.session.backend.replayed_outputs), (0, 0, 0))
            DETAILS['http_security'] = {'loopback_only': True, 'host_origin_token': True,
                'request_bounds': True, 'fixed_assets_only': True,
                'stale_duplicate_busy_no_repeated_action': True, 'response_token_absent': True}
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def main():
    global OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    OUTPUT = external_path(args.output)
    OUTPUT.mkdir(mode=0o700, parents=True, exist_ok=False)
    original_connect = socket.socket.connect
    def loopback_connect(sock, address):
        if not isinstance(address, tuple) or address[0] not in {'127.0.0.1', '::1'}:
            raise AssertionError('Only loopback verification traffic is allowed')
        return original_connect(sock, address)
    log = io.StringIO()
    with ExitStack() as stack:
        stack.enter_context(patch('socket.socket.connect', loopback_connect))
        stack.enter_context(patch('subprocess.Popen', forbidden))
        stack.enter_context(patch('gpt_ml.GPTMLGenerator.__call__', forbidden))
        stack.enter_context(patch('ai.d5_single_interpreter_transport.SingleInterpreterGenerator.__call__', forbidden))
        stack.enter_context(patch('ai.d5_chatgpt_auth.ChatGPTCredentials.__init__', forbidden))
        stack.enter_context(patch('ai.d5_chatgpt_auth.ChatGPTCredentials.get_access_token', forbidden))
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(CoreChecks))
    (OUTPUT / 'software.log').write_text(log.getvalue())
    summary = {'mode': 'offline saved-output and loopback software verification',
        'passed': result.wasSuccessful(), 'checks': result.testsRun,
        'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped),
        'live_gpt_calls': 0, 'authentication_calls': 0, 'new_semantic_cases': 0,
        'ml': 'Unchanged real baseline, including its existing startup fit from unchanged train/calibration; no tuning or saved weight changes',
        'limits': 'Saved output replay and software checks, not new live free-text accuracy or a human business review',
        'details': DETAILS,
        'source_sha256': {str(p.relative_to(REPOSITORY)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [Path(__file__).resolve(), ASSETS.parent / 'core_demo.py',
                                    ASSETS / 'business-examples.json', ASSETS / 'recordings.json']}}
    write_json(OUTPUT / 'summary.json', summary)
    print(json.dumps({k: summary[k] for k in ('passed', 'checks', 'failures', 'errors', 'live_gpt_calls', 'authentication_calls', 'new_semantic_cases')}))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
