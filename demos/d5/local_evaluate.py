"""Bounded D5 verification; separate local and GPT rounds reuse the same bank."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from session import HERE, REPOSITORY, RUNTIME, NoOtherQuestions, NoProfileSave, bootstrap, private_directory, write_json
bootstrap()
from ai.d5_single_interpreter_contract_v2 import D5DialogueContext, D5SingleInterpreter
from ai.d5_single_interpreter_engine_v2 import D5BusinessStandardEngine
from ai.question_spec import BusinessSpec
from local_session import LocalD5Session

EVIDENCE = REPOSITORY / 'docs/d5-semantic-repair/evidence/after'
CONTEXT_ROOT = REPOSITORY / 'docs/d5-context-verification-2026-10-13/records'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_files():
    paths = [p for p in HERE.rglob('*') if p.is_file() and p.suffix in {'.py', '.json', '.txt'}]
    paths += [REPOSITORY / 'ai/all_question_ml.py', REPOSITORY / 'config/business-decision-spec.json']
    paths += [REPOSITORY / 'data/nlp/all_questions' / f'{split}.csv' for split in ('train', 'calibration')]
    paths += [EVIDENCE / name for name in ('inputs.json', 'expectations.json')]
    paths += sorted(CONTEXT_ROOT.glob('*.json'))
    paths += [REPOSITORY / 'docs/d5-local-ml-qwen-2026-10-13/protocol.json']
    return {str(p.relative_to(REPOSITORY)): digest(p) for p in sorted(set(paths))}


def no_changes(frozen):
    return all((REPOSITORY / p).is_file() and digest(REPOSITORY / p) == h for p, h in frozen.items())


def serial_resolution(r):
    return {'candidate': r.candidate_option_id, 'bucket': r.ordinary_bucket,
            'model_uncertain': r.model_uncertain, 'semantic_undecided': r.semantic_undecided,
            'reason': r.reason, 'intent_set': sorted(r.intent_set), 'option_set': sorted(r.option_set),
            'intent_probabilities': r.intent_probabilities, 'option_probabilities': r.option_probabilities}


def pension_meaning(record):
    raw = record.get('raw') or {}
    facts = raw.get('facts', [])
    active = {f.get('source_category') for f in facts if f.get('owner') == 'self'
              and f.get('time') == 'current' and f.get('pays_living_costs') == 'yes'}
    excluded_wages = any(f.get('source_category') == 'D5_SALARY' and f.get('pays_living_costs') == 'no'
                         for f in facts)
    return (raw.get('semantic_bucket') == 'clarity' and raw.get('option_id') == 'D5_PENSION_PAYMENTS'
            and raw.get('answer_scope') == 'complete' and active == {'D5_PENSION_PAYMENTS'}
            and excluded_wages and record.get('candidate') == 'D5_PENSION_PAYMENTS'
            and record.get('result', {}).get('action') == 'confirm'
            and clear_relations_match(record))


def preflight(backend, output, *, backend_name='qwen'):
    if backend_name not in {'qwen', 'gpt'}:
        raise ValueError('Unsupported D5 interpretation backend')
    row = json.loads((EVIDENCE / 'inputs.json').read_text())['rows'][0]
    spec = BusinessSpec.load(RUNTIME / 'config/business-decision-spec.json')
    interpreter = D5SingleInterpreter(spec, backend, model_metadata=backend.metadata)
    engine = D5BusinessStandardEngine(spec, d5_interpreter=interpreter,
        question_resolver=NoOtherQuestions(), store=NoProfileSave())
    engine.state.current_index = spec.question_order.index('D5')
    interpreter.context = D5DialogueContext(pending_prompt=spec.question('D5').question)
    backend.case_id = 'preflight-D5-STD-01'
    name = 'local' if backend_name == 'qwen' else 'GPT'
    record = {'id': row['id'], 'input': row['text'],
              'purpose': f'Direct {name} backend preflight, not a combined-route score'}
    try:
        record['result'] = engine.submit_answer(row['text'])
        d = interpreter.last_decision
        record['decision'] = d.as_dict() if d else None
        raw = d.raw_output if d else None
        record['raw_output'] = raw
        try:
            record['raw'] = json.loads(raw) if raw else None
        except (TypeError, ValueError):
            record['raw'] = None
        record['candidate'] = engine.state.answers['D5'].candidate_option_id
        record['passed'] = bool(pension_meaning(record) and backend.calls == 1)
    except Exception as exc:
        record.update(passed=False, failure_type=type(exc).__name__)
    record.update({f'actual_{backend_name}_calls': backend.calls,
                   'backend_call': dict(backend.last_call)})
    write_json(output / 'preflight.json', record)
    return record['passed']


def case_match(record, expected):
    raw, result = record.get('raw') or {}, record['result']
    candidate = record.get('candidate')
    ml_only = record.get('qwen_calls', record.get('actual_model_calls', 0)) == 0
    kind = expected['kind']
    if kind == 'clear':
        return (candidate == expected['option'] and result.get('action') == 'confirm'
                and (ml_only or (raw.get('semantic_bucket') == 'clarity'
                     and raw.get('option_id') == expected['option']
                     and raw.get('answer_scope') == 'complete'
                     and raw.get('model_abstain') is False
                     and clear_relations_match(record))))
    if kind == 'confusion':
        return candidate is None and ml_only and result.get('action') == 'explain'
    if kind == 'missing_information':
        return (candidate is None and not raw.get('facts') and raw.get('option_id') is None
                and raw.get('semantic_bucket') is None and raw.get('model_abstain') is True
                and result.get('clarification_topic') == 'current_funding_unknown')
    return (candidate is None and result.get('bucket') == 'Undecided'
            and result.get('clarification_topic') == 'source_use_unknown:D5_SALARY'
            and (ml_only or (not raw.get('facts') and raw.get('option_id') is None
                            and raw.get('semantic_bucket') == 'undecided'
                            and raw.get('model_abstain') is False)))


def clear_relations_match(record):
    """Score the already-reviewed source relations, without model-facing labels.

    Source instance grouping may differ: two employers are still one category.
    Excluded sources need no invented owner or current-time assertion. The
    future pension may have unknown spending use; it must stay future/excluded.
    These are evaluation expectations, never runtime interpretation rules.
    """
    identifier = record['id']
    if identifier == 'CONTEXT-02':
        identifier = 'D5-STD-02'
    elif identifier == 'CONTEXT-03':
        identifier = 'D5-STD-01'
    expected_active = {
        'D5-STD-01': {'D5_PENSION_PAYMENTS'},
        'D5-STD-02': {'D5_SALARY', 'D5_PENSION_PAYMENTS'},
        'D5-STD-03': {'D5_SALARY'},
        'D5-STD-04': {'D5_BENEFITS_SUPPORT'},
        'D5-STD-05': {'D5_BENEFITS_SUPPORT'},
        'D5-STD-06': {'D5_WITHDRAWALS'},
        'D5-STD-08': set(),
    }[identifier]
    facts = (record.get('raw') or {}).get('facts', [])
    active = set()
    excluded = set()
    for fact in facts:
        category = fact.get('source_category')
        if (category in expected_active and fact.get('owner') == 'self'
                and fact.get('time') == 'current' and fact.get('pays_living_costs') == 'yes'):
            active.add(category)
        elif (identifier == 'D5-STD-01' and category == 'D5_SALARY'
              and fact.get('pays_living_costs') == 'no'
              and fact.get('owner') in {'self', 'unknown'}
              and fact.get('time') in {'current', 'unknown'}):
            excluded.add(category)
        elif (identifier == 'D5-STD-06' and category == 'D5_PENSION_PAYMENTS'
              and fact.get('time') == 'future'
              and fact.get('owner') in {'self', 'unknown'}
              and fact.get('pays_living_costs') in {'no', 'unknown'}):
            excluded.add(category)
        elif (identifier == 'D5-STD-08' and category == 'D5_NO_REGULAR'
              and fact.get('owner') == 'self' and fact.get('time') == 'current'
              and fact.get('pays_living_costs') == 'no'):
            excluded.add(category)
        else:
            return False
    required_excluded = {'D5-STD-01': {'D5_SALARY'},
                         'D5-STD-06': {'D5_PENSION_PAYMENTS'},
                         'D5-STD-08': {'D5_NO_REGULAR'}}.get(identifier, set())
    return active == expected_active and excluded == required_excluded


def existing(backend, output, *, complete_bank=False,
             session_factory=LocalD5Session, backend_name='qwen'):
    if backend_name not in {'qwen', 'gpt'}:
        raise ValueError('Unsupported D5 interpretation backend')
    backend_calls_key = f'{backend_name}_calls'
    from baseline_ml import build_all_question_ml_resolver
    rows = json.loads((EVIDENCE / 'inputs.json').read_text())['rows']
    reference = build_all_question_ml_resolver(
        BusinessSpec.load(REPOSITORY / 'config/business-decision-spec.json'),
        REPOSITORY / 'data/nlp/all_questions')
    reference_predictions = {row['id']: serial_resolution(reference.resolve('D5', row['text'])) for row in rows}
    write_json(output / 'reference-predictions.json', reference_predictions)
    # Labels stay in the scorer and are never passed to LocalD5Session or either model.
    expectations = json.loads((EVIDENCE / 'expectations.json').read_text())['cases']
    session = session_factory(backend, output, backend_name=backend_name)
    scores = []
    for row in rows:
        session.new_example()
        session.submit(row['text'], case_id=row['id'])
        record = session.last_record
        matched = case_match(record, expectations[row['id']])
        score = {'id': row['id'], 'expected': expectations[row['id']], 'matched': matched,
                 'candidate': record['candidate'], 'raw': record.get('raw'),
                 'contract_outcome': (record.get('decision') or {}).get('outcome'),
                 'ml_calls': record.get('ml_calls'), backend_calls_key: record.get(backend_calls_key),
                 'route': record.get('route')}
        scores.append(score)
        print(f"Recorded {row['id']}: {'matched' if matched else 'mismatch'}", flush=True)
        if not matched and not complete_bank:
            write_json(output / 'existing-summary.json', {'passed': False, 'cases': scores,
                'stop_case': row['id'], 'context_phase_run': False, 'raw_meaning_review_required': True})
            return False
    bank_passed = all(score['matched'] for score in scores)
    write_json(output / 'existing-summary.json', {'passed': bank_passed, 'cases': scores,
        'context_phase_run': bank_passed,
        'scope': 'Existing opened examples, not an independent accuracy estimate', 'raw_meaning_review_required': True})
    if not bank_passed:
        return False
    # Same already-used short-answer/correction sequence; no new fictional cases.
    sequence = [json.loads((CONTEXT_ROOT / f'CONTEXT-{i:02d}.json').read_text()) for i in range(1, 5)]
    session.new_example()
    controls = []
    results = []
    def save_context(passed, stop_case=None):
        filename = (f'context-progress-{len(results):02d}.json' if stop_case == 'sequence_in_progress'
                    else 'context-summary.json')
        write_json(output / filename, {'passed': passed,
            'cases': results, 'controls': controls, 'stop_case': stop_case,
            'choice_recovery': 0, 'raw_meaning_review_required': True})
    def control(command, expected_action):
        before = (session.ml_calls, backend.calls)
        result = session.command(command) if command.startswith('/') else session.submit(command)
        ok = before == (session.ml_calls, backend.calls) and result['action'] == expected_action
        if command == '/change':
            ok &= not session.confirmed and session.engine.state.answers['D5'].candidate_option_id is None
        controls.append({'input': command, 'action': result['action'], 'zero_calls': before == (session.ml_calls, backend.calls), 'passed': ok})
        if not ok:
            save_context(False, command)
            raise AssertionError('Existing control did not match')
    def turn(index):
        identifier = f'CONTEXT-{index + 1:02d}'
        session.submit(sequence[index]['input'], case_id=identifier)
        record = session.last_record
        if index == 0:
            matched = case_match(record, expectations['D5-STD-10'])
        elif index in {1, 2}:
            matched = case_match(record, expectations['D5-STD-02' if index == 1 else 'D5-STD-01'])
        else:
            raw = record.get('raw') or {}
            matched = (record['candidate'] is None and raw.get('facts') == []
                and raw.get('option_id') is None and raw.get('semantic_bucket') is None
                and raw.get('model_abstain') is True
                and record['result'].get('clarification_topic') == 'reply_unclear')
        results.append({'id': identifier, 'matched': matched, 'record': record})
        save_context(False, identifier if not matched else 'sequence_in_progress')
        if not matched:
            raise AssertionError('Existing context meaning or follow-up did not match')
    control('/help', 'explain')
    turn(0)
    control('/pause', 'pause')
    control(rows[4]['text'], 'paused')
    control('/resume', 'resume')
    turn(1)
    control('/confirm', 'd5_complete')
    control('/change', 'reask')
    turn(2)
    control('/confirm', 'd5_complete')
    control('/new', 'new_example')
    turn(3)
    control('/stop', 'stop')
    control('/resume', 'stop')
    control(rows[0]['text'], 'stop')
    control('/new', 'new_example')
    control('I want to jump off a building', 'safety_stop')
    control('/confirm', 'safety_stop')
    save_context(True)
    return True


def main():
    from local_transport import LocalGenerator
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['preflight', 'existing', 'prompt-check'])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--preflight-receipt', type=Path)
    parser.add_argument('--worker-python', type=Path)
    parser.add_argument('--model-path', type=Path)
    parser.add_argument('--protocol', type=Path,
                        help='Required frozen policy for the separately authorised prompt-check round')
    args = parser.parse_args()
    frozen = frozen_files()
    if args.phase == 'prompt-check':
        if args.protocol is None:
            parser.error('A separate frozen prompt-check protocol is required')
        protocol_path = args.protocol.resolve()
        policy = json.loads(protocol_path.read_text())
        if (policy.get('phase') != 'prompt-check' or policy.get('existing_examples') != 11
                or policy.get('conditional_context_turns') != 4 or policy.get('retry') is not False
                or policy.get('source_hashes') != frozen):
            parser.error('Prompt-check protocol does not match these frozen sources and limits')
        frozen[str(protocol_path.relative_to(REPOSITORY))] = digest(protocol_path)
    if args.phase == 'existing':
        if args.preflight_receipt is None:
            parser.error('A successful separate preflight receipt is required')
        prior = json.loads(args.preflight_receipt.read_text())
        started = json.loads(args.preflight_receipt.with_name('started.json').read_text())
        if prior.get('passed') is not True or started['hashes'] != frozen:
            parser.error('Preflight did not pass for these exact frozen files')
    output = private_directory(args.output)
    write_json(output / 'started.json', {'phase': args.phase, 'at_utc': datetime.now(timezone.utc).isoformat(),
        'hashes': frozen, 'maximum_qwen_calls': 1 if args.phase == 'preflight' else 14,
        'retry': False, 'labels_supplied_to_model': False, 'default_changed': False})
    backend = None
    passed = False
    failure = None
    try:
        backend = LocalGenerator(output / 'traces', worker_python=args.worker_python, model_path=args.model_path)
        passed = (preflight(backend, output) if args.phase == 'preflight'
                  else existing(backend, output, complete_bank=args.phase == 'prompt-check'))
    except Exception as exc:
        failure = {'type': type(exc).__name__, 'safe_backend_receipt': dict(backend.last_call) if backend else None}
    finally:
        if backend:
            backend.close()
    preserved = no_changes(frozen)
    calls = backend.calls if backend else 0
    summary = {'phase': args.phase, 'passed': bool(passed and preserved and calls <= (1 if args.phase == 'preflight' else 14)),
               'files_unchanged': preserved, 'actual_qwen_calls': calls,
               'failure': failure, 'retry': False, 'choice_recovery': 0}
    write_json(output / 'execution.json', summary)
    if not summary['passed']:
        write_json(output / 'STOP.json', summary)
    print(json.dumps(summary))
    print('Private evidence:', output)
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
