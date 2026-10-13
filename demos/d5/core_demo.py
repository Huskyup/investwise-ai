#!/usr/bin/env python3
"""Manually launched, loopback-only D5 browser demo; no main-app integration."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import sys
import threading
from urllib.parse import urlsplit
import uuid
import webbrowser

sys.dont_write_bytecode = True
from session import (DemoStopped, HERE, REPOSITORY, authored_text, bootstrap,
                     external_path, private_directory, write_json)
bootstrap()
from gpt_ml import GPTMLSession
from ai.d5_single_interpreter_contract_v2 import output_schema

ASSETS = HERE / 'core'
EVIDENCE = REPOSITORY / 'docs/d5-ml-gpt-2026-10-13/evidence/run'
COMMANDS = frozenset({'/help', '/confirm', '/change', '/pause', '/resume', '/stop', '/new'})
MAX_BODY = 140_000  # Allows UTF-8 encoding of the existing 32,768-character bound.


def read_record(identifier):
    manifest = json.loads((ASSETS / 'recordings.json').read_text())
    entry = manifest['records'][identifier]
    path = REPOSITORY / entry['path']
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
        raise DemoStopped('The recorded example changed; no replay substitution')
    return json.loads(path.read_text())


def scenario():
    """Exactly the previously exercised four context turns and fourteen controls."""
    rows = [read_record(f'CONTEXT-{i:02}') for i in range(1, 5)]
    inputs = [
        ('/help', 'Explain what D5 asks'),
        (rows[0]['input'], 'Ask only about the uncertain wages use'),
        ('/pause', 'Pause before interpreting anything else'),
        (read_record('D5-STD-05')['input'], 'Ignore this funding reply while paused'),
        ('/resume', 'Resume the same example'),
        (rows[1]['input'], 'Use earlier pension information with the short reply'),
        ('/confirm', 'Confirm the mixed-source candidate without another call'),
        ('/change', 'Invalidate confirmation and retain the conversation'),
        (rows[2]['input'], 'Exclude saved wages while retaining pension funding'),
        ('/confirm', 'Confirm the corrected pension-only answer'),
        ('/new', 'Clear the example and earlier answer history'),
        (rows[3]['input'], 'A fresh Yes has no funding context'),
        ('/stop', 'Stop this example'),
        ('/resume', 'A stopped example stays stopped'),
        (read_record('D5-STD-01')['input'], 'Do not interpret text after stop'),
        ('/new', 'Start a distinct fictional example'),
        ('I want to jump off a building', 'Exercise the existing safety control'),
        ('/confirm', 'Safety stop prevents confirmation'),
    ]
    return [{'text': text, 'purpose': purpose} for text, purpose in inputs]


class RecordedBackend:
    """Saved raw outputs, validated afresh; never a provider response or cache fallback."""
    metadata = {'model': 'offline-recorded-output', 'backend': 'saved_fixture', 'live': False}

    def __init__(self, records):
        self.records = list(records)
        self.request_identity = json.loads((ASSETS / 'recordings.json').read_text())['request_identity']
        self.calls = 0  # Actual GPT requests; always zero in this mode.
        self.replayed_outputs = 0
        self.last_call = {}
        self.case_id = ''

    def __call__(self, messages, schema):
        if not self.records:
            raise DemoStopped('No recorded output remains for this example')
        expected = self.records[0]
        supplied = json.loads(messages[1]['content'])
        # The two saved Yes replies differ by their entire conversation state.
        # Never use text-only, fuzzy or approximate matching.
        if (supplied['original_reply'] != expected['input']
                or supplied['dialogue_context'] != expected['dialogue_context']
                or supplied['current_question'] != self.request_identity['current_question']
                or supplied['allowed_options'] != self.request_identity['allowed_options']
                or hashlib.sha256(messages[0]['content'].encode()).hexdigest() != self.request_identity['system_sha256']
                or schema != self.request_identity['schema']):
            raise DemoStopped('No recording matches this reply and conversation state')
        self.records.pop(0)
        self.replayed_outputs += 1
        self.last_call = {'mode': 'offline_saved_output', 'source_case': expected['id'],
                          'raw_output_sha256': hashlib.sha256(expected['raw_output'].encode()).hexdigest(),
                          'actual_model_calls': 0, 'retry': False}
        return expected['raw_output']


class CoreDemo:
    """Presentation only: all answer mutations go through the existing session."""
    def __init__(self, session, *, mode):
        if mode not in {'live', 'replay'}:
            raise ValueError('Unknown demo mode')
        self.session, self.mode = session, mode
        self.version = 0
        self.step = 0
        self.steps = scenario()
        self.events = []
        self.current_facts = []
        self.error = None
        self.last_result = {}
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.Lock()

    def act(self, text=None):
        if self.error or self.session.failed:
            raise ValueError('The session has stopped; restart deliberately')
        if self.mode == 'replay':
            if text is not None or self.step >= len(self.steps):
                raise ValueError('Replay accepts only its next saved step')
            text = self.steps[self.step]['text']
        if not isinstance(text, str) or not text.strip() or len(text) > 32768:
            raise ValueError('Enter between 1 and 32,768 characters')
        text = text.strip()
        if text.startswith('/') and text not in COMMANDS:
            raise ValueError('Use one of the displayed controls')
        s, backend = self.session, self.session.backend
        before = (s.ml_calls, backend.calls, getattr(backend, 'replayed_outputs', 0))
        try:
            result = s.command(text) if text.startswith('/') else s.submit(text)
        except Exception:
            s.failed = True
            self.error = ('The service or runtime stopped. No retry or recorded-output fallback was used.'
                          if self.mode == 'live' else
                          'Recorded replay stopped. No live GPT request or fallback was used; inspect the replay counter.')
            if (self.mode == 'live' and isinstance(backend.last_call.get('provider_error'), dict)
                    and backend.last_call['provider_error'].get('code') == 'server_is_overloaded'):
                self.error = 'GPT reported that the service is overloaded. No financial answer was accepted. This session has stopped without retry or fallback.'
            result = {'action': 'runtime_stopped', 'message': self.error}
        delta = [s.ml_calls - before[0], backend.calls - before[1],
                 getattr(backend, 'replayed_outputs', 0) - before[2]]
        record = s.last_record or {}
        route = record.get('route', 'control') if any(delta) else 'control'
        if self.error:
            route = 'runtime_stopped'
        if self.mode == 'replay':
            route = route.replace('gpt', 'saved_output')
        if any(delta):
            decision = record.get('decision') or {}
            self.current_facts = ((record.get('raw') or {}).get('facts', [])
                if decision.get('outcome') == 'financial_candidate' else [])
        answer = s.engine.state.answers['D5']
        if (text in {'/new', '/change'} or result.get('action') in {'stop', 'safety_stop', 'runtime_stopped'}
                or (answer.candidate_option_id is None and not s.confirmed)):
            self.current_facts = []
        event = {'input': text, 'texts': authored_text(result), 'action': result.get('action'),
                 'bucket': result.get('bucket'), 'route': route,
                 'ml_calls': delta[0], 'gpt_calls': delta[1], 'replayed_outputs': delta[2]}
        self.events.append(event)
        self.last_result = result
        self.version += 1
        if self.step < len(self.steps) and text == self.steps[self.step]['text']:
            self.step += 1
        # Controls are recorded too; these logs remain outside the repository.
        write_json(s.output_dir / f'core-action-{self.version:04}.json',
                   {'mode': self.mode, 'event': event, 'version': self.version})
        return self.view()

    def view(self):
        s = self.session
        answer = s.engine.state.answers['D5']
        held = bool(s.engine.state.paused or s.engine.state.stopped_for_safety
                    or 'user_stop' in s.engine.state.active_holds or self.error)
        option = answer.selected_option_id if s.confirmed else answer.candidate_option_id
        label = next((o.label for o in s.spec.question('D5').options if o.id == option), None)
        status = ('Session stopped' if self.error else 'Stopped for safety' if s.engine.state.stopped_for_safety
                  else 'Stopped' if 'user_stop' in s.engine.state.active_holds
                  else 'Paused' if s.engine.state.paused else 'Confirmed in this session' if s.confirmed
                  else 'Awaiting your confirmation' if option else 'Needs your reply')
        facts = [{k: f[k] for k in ('source_category', 'owner', 'time', 'pays_living_costs', 'evidence')}
                 for f in self.current_facts] if option and not held else []
        return {'mode': self.mode, 'version': self.version, 'question': s.question,
                'events': self.events, 'status': status, 'option': option if not held else None,
                'option_label': label if not held else None, 'facts': facts,
                'bucket': ('Clarity' if option and not held else self.last_result.get('bucket') if not held else None),
                'contract_outcome': self.last_result.get('contract_outcome'),
                'model_uncertain': self.last_result.get('model_uncertain', False),
                'history_count': len(s.interpreter.context.history),
                'ml_calls': s.ml_calls, 'gpt_calls': s.backend.calls,
                'replayed_outputs': getattr(s.backend, 'replayed_outputs', 0),
                'can_confirm': bool(option and not held and not s.confirmed),
                'stopped': bool(self.error), 'error': self.error,
                'step': self.step, 'steps_total': len(self.steps),
                'next_step': self.steps[self.step] if self.step < len(self.steps) else None}


def make_server(demo, port=8765):
    class Handler(BaseHTTPRequestHandler):
        server_version = 'InvestWiseD5'
        def log_message(self, *_):
            pass  # No reply text, tokens or request paths in console logs.

        def send_data(self, status, body, mime='application/json'):
            if not isinstance(body, bytes):
                body = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', mime + '; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass  # The completed action is not retried after a browser disconnect.

        def authorised(self, *, mutation=False):
            host = f'127.0.0.1:{self.server.server_port}'
            if self.headers.get_all('Host') != [host]:
                return False
            if mutation and self.headers.get_all('Origin') != ['http://' + host]:
                return False
            values = self.headers.get_all('X-D5-Token') or []
            return len(values) == 1 and secrets.compare_digest(values[0], demo.token)

        def do_GET(self):
            route = urlsplit(self.path).path
            assets = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'),
                      '/style.css': ('style.css', 'text/css')}
            if self.headers.get_all('Host') != [f'127.0.0.1:{self.server.server_port}']:
                return self.send_data(403, {'error': 'Local host required'})
            if route in assets:
                name, mime = assets[route]
                return self.send_data(200, (ASSETS / name).read_bytes(), mime)
            if route == '/api/state' and self.authorised():
                if not demo.lock.acquire(blocking=False):
                    return self.send_data(409, {'error': 'An action is still in progress; do not resubmit it'})
                try:
                    self.send_data(200, demo.view())
                finally:
                    demo.lock.release()
                return
            self.send_data(404, {'error': 'Not available'})

        def do_POST(self):
            if self.path != '/api/action' or not self.authorised(mutation=True):
                return self.send_data(403, {'error': 'Local session authorisation required'})
            try:
                lengths = self.headers.get_all('Content-Length') or []
                if len(lengths) != 1 or not lengths[0].isdigit():
                    raise ValueError()
                length = int(lengths[0])
                if (not 0 < length <= MAX_BODY or self.headers.get('Transfer-Encoding')
                        or self.headers.get_all('Content-Type') != ['application/json']):
                    raise ValueError()
                self.connection.settimeout(5)
                raw = self.rfile.read(length)
                payload = json.loads(raw)
                if (not isinstance(payload, dict) or set(payload) != {'version', 'text'}
                        or type(payload['version']) is not int):
                    raise ValueError()
            except (ValueError, OSError):
                return self.send_data(400, {'error': 'Invalid or oversized action'})
            if not demo.lock.acquire(blocking=False):
                return self.send_data(409, {'error': 'An action is already in progress; do not resend'})
            try:
                if payload['version'] != demo.version:
                    return self.send_data(409, {'error': 'This page is stale. Refresh state; the action was not repeated'})
                self.send_data(200, demo.act(payload['text']))
            except ValueError as error:
                self.send_data(400, {'error': str(error)})
            except Exception:
                demo.session.failed = True
                demo.error = 'Local recording failed. Stop and inspect the private session directory.'
                self.send_data(500, {'error': demo.error})
            finally:
                demo.lock.release()

    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['replay', 'live'], default='replay')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--open', action='store_true', help='Open the local browser after startup')
    parser.add_argument('--profile-dir', type=Path, default=Path.home() / '.config/investwise/d5-chatgpt-plan')
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12) or os.name != 'posix':
        parser.error('Use Python 3.12 on macOS or Linux with demos/d5/requirements.txt')
    os.umask(0o077)
    output = private_directory(Path.home() / '.local/state/investwise/d5-core-demo' /
        (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]))
    if args.mode == 'live':
        from ai.d5_chatgpt_auth import ChatGPTCredentials
        from gpt_ml import GPTMLGenerator
        backend = GPTMLGenerator(output / 'traces', ChatGPTCredentials(external_path(args.profile_dir)))
    else:
        backend = RecordedBackend([read_record(f'CONTEXT-{i:02}') for i in range(1, 5)])
    try:
        demo = CoreDemo(GPTMLSession(backend, output), mode=args.mode)
        server = make_server(demo, args.port)
    except Exception:
        print('D5 could not start. Check the Python environment, frozen files and port.', file=sys.stderr)
        return 2
    url = f'http://127.0.0.1:{server.server_port}/#' + demo.token
    print('D5 core demo — ' + ('LIVE ML + GPT' if args.mode == 'live' else 'RECORDED OUTPUT REPLAY; no GPT requests'))
    print('Open locally:', url, flush=True)
    print('Private diagnostics:', output, flush=True)
    print('One shared local session. Fictional data only. Stop this server with Ctrl+C.', flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
