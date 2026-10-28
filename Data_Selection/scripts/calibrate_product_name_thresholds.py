"""Read-only, synthetic product-name matching calibration; never a production cutoff."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import sqlite3
import sys
import time
import unicodedata

try:
    import rapidfuzz
    from rapidfuzz import process
    from rapidfuzz.distance import DamerauLevenshtein as DL
except ImportError:
    raise SystemExit('Install: python -m pip install -r requirements-matching.txt')


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1
# A conservative, explicit experiment guard; not an exhaustive category classifier.
# No product-line words are removed or assigned special matching rules.
GENERIC_WORDS = {
    '유산균', '멀티비타민', '비타민', '미네랄', '홍삼', '인삼', '칼슘',
    '마그네슘', '프로바이오틱스', '오메가3', '오메가', '아연', '철',
    '루테인', '콜라겐', '단백질', '정제', '캡슐', '분말', '젤리',
}
KINDS = {
    'exact': .10, 'typo_1': .20, 'typo_2': .15, 'omission': .25,
    'omission_typo': .10, 'absent_omission': .10, 'absent_typo': .10,
}


def now():
    return datetime.now(timezone.utc).isoformat()


def normalize(value):
    # Preserve numbers, punctuation and all product-line words.
    return ''.join(unicodedata.normalize('NFC', str(value or '')).casefold().split())


def tokens(value):
    return tuple(unicodedata.normalize('NFC', str(value or '')).casefold().split())


def generic_only(value):
    parts = tokens(value)
    return not parts or all(
        p in GENERIC_WORDS or re.fullmatch(r'[\d.,%μµ㎎mgkcliu정포병개]+', p)
        for p in parts
    )


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temporary, path)


def load_catalog(path):
    path = Path(path).resolve(strict=True)
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
        db.execute('PRAGMA query_only=ON')
        db.row_factory = sqlite3.Row
        rows = [dict(r) for r in db.execute('''
            SELECT product_id,product_name,company_name,manufacturing_report_number
            FROM products ORDER BY product_id
        ''')]
    if not rows or any(not r['product_name'] for r in rows):
        raise ValueError('The products table must contain non-empty product names.')
    reports = [normalize(r['manufacturing_report_number']) for r in rows]
    if any(not r for r in reports) or len(set(reports)) != len(reports):
        raise ValueError('This experiment requires a unique, non-empty report number per product record.')
    fingerprint = hashlib.sha256(
        json.dumps(rows, ensure_ascii=False, sort_keys=True).encode('utf-8')
    ).hexdigest()
    return rows, fingerprint


class Catalog:
    def __init__(self, rows):
        self.rows = rows
        self.names = [normalize(r['product_name']) for r in rows]
        self.companies = [normalize(r['company_name']) for r in rows]
        self.by_company = defaultdict(dict)
        self.word_starts = defaultdict(list)
        self.name_tokens = [tokens(r['product_name']) for r in rows]
        for index, row in enumerate(rows):
            self.by_company[self.companies[index]][index] = self.names[index]
            for position, word in enumerate(self.name_tokens[index]):
                self.word_starts[word].append((index, position))

    def phrase_candidates(self, query):
        phrase = tokens(query)
        if not phrase:
            return []
        found = set()
        for index, position in self.word_starts.get(phrase[0], []):
            if self.name_tokens[index][position:position + len(phrase)] == phrase:
                found.add(index)
        return sorted(found)

    def rank(self, trial, scope, literal_candidates=None):
        excluded = trial['source_index'] if trial['expected_product_id'] is None else None
        company = self.companies[trial['source_index']]
        if scope == 'company_known' and not company:
            return {'top': [], 'candidate_count': 0, 'blocked_reason': 'manufacturer_missing'}
        if generic_only(trial['query']):
            return {'top': [], 'candidate_count': 0, 'blocked_reason': 'generic_only'}
        query = normalize(trial['query'])
        if trial['route'] == 'omission':
            # Fetch ALL literal-phrase candidates BEFORE checking manufacturer.
            indices = literal_candidates
            if indices is None:
                indices = self.phrase_candidates(trial['query'])
            before_company = len(indices)
            eligible = [i for i in indices if i != excluded and (
                scope != 'company_known' or self.companies[i] == company)]
            choices = {i: self.names[i] for i in eligible}
            count = len(choices)
        else:
            choices = self.by_company[company] if scope == 'company_known' else self.names
            count = len(choices) - int(excluded is not None and (
                scope != 'company_known' or excluded in choices))
            before_company = len(self.rows)
        # All eligible names are scored. Only two maxima are needed to decide
        # whether exactly one record exceeds ANY cutoff. Keep a third maximum
        # so the held-out source can be removed without hiding a competing tie.
        matches = process.extract(query, choices, scorer=DL.normalized_similarity, limit=3)
        top = []
        for _, score, index in matches:
            if index == excluded:
                continue
            row = self.rows[index]
            top.append({
                'product_id': row['product_id'], 'product_name': row['product_name'],
                'company_name': row['company_name'], 'score': score * 100,
                'distance': DL.distance(query, self.names[index]),
            })
            if len(top) == 2:
                break
        return {'top': top, 'candidate_count': count,
                'literal_candidates_before_company': before_company,
                'blocked_reason': None}


def mutate(query, edits, rng):
    original = normalize(query)
    alphabet = sorted(set(original + '가나다라마바사아자차카타파하유산균비타민'))
    for _ in range(100):
        chars = list(original)
        for _ in range(edits):
            operation = rng.choice(['replace', 'insert', 'delete', 'transpose'])
            if operation == 'insert':
                chars.insert(rng.randrange(len(chars) + 1), rng.choice(alphabet))
            elif operation == 'delete' and len(chars) > 1:
                del chars[rng.randrange(len(chars))]
            elif operation == 'transpose' and len(chars) > 1:
                position = rng.randrange(len(chars) - 1)
                chars[position], chars[position + 1] = chars[position + 1], chars[position]
            elif chars:
                position = rng.randrange(len(chars))
                chars[position] = rng.choice(alphabet)
        result = ''.join(chars)
        if result and DL.distance(original, result) == edits:
            return result
    return None


def omit_words(name, rng):
    words = str(name).split()
    if len(words) < 2:
        return None
    # Delete whole words at the ends, without interpreting any product-line word.
    spans = [(start, end) for start in range(len(words))
             for end in range(start + 1, len(words) + 1)
             if (start, end) != (0, len(words))]
    rng.shuffle(spans)
    for start, end in spans:
        query = ' '.join(words[start:end])
        if normalize(query) != normalize(name) and not generic_only(query):
            return query
    return None


def make_trials(rows, count, seed, calibration_fraction=.6):
    rng = random.Random(seed)
    allocations = {kind: int(count * ratio) for kind, ratio in KINDS.items()}
    for kind in list(KINDS)[:count - sum(allocations.values())]:
        allocations[kind] += 1
    available = list(range(len(rows)))
    rng.shuffle(available)
    used_names = set()
    trials = []
    for kind, required in allocations.items():
        selected = []
        for index in available:
            row = rows[index]
            normalized = normalize(row['product_name'])
            if normalized in used_names or generic_only(row['product_name']):
                continue
            route = 'omission' if kind in {'omission', 'absent_omission'} else 'typo'
            if kind in {'omission', 'omission_typo', 'absent_omission'}:
                query = omit_words(row['product_name'], rng)
                if query is None:
                    continue
                if kind == 'omission_typo':
                    query = mutate(query, 1, rng)
            elif kind in {'typo_1', 'typo_2'}:
                query = mutate(row['product_name'], int(kind[-1]), rng)
            elif kind == 'absent_typo':
                query = mutate(row['product_name'], 1, rng) if rng.random() < .5 else row['product_name']
            else:
                query = row['product_name']
                route = 'exact_control'
            if query is None:
                continue
            used_names.add(normalized)
            selected.append({
                'trial_id': len(trials) + len(selected) + 1,
                'kind': kind, 'route': route, 'query': query,
                'source_index': index, 'source_product_id': row['product_id'],
                'source_name': row['product_name'], 'source_company': row['company_name'],
                'expected_product_id': None if kind.startswith('absent_') else row['product_id'],
                'full_name_distance': DL.distance(normalize(query), normalized),
            })
            if len(selected) == required:
                break
        if required and len(selected) != required:
            raise ValueError(f'Not enough eligible, distinct source names for {kind}: {len(selected)}/{required}')
        if not required:
            continue
        rng.shuffle(selected)
        boundary = int(len(selected) * calibration_fraction)
        for position, trial in enumerate(selected):
            trial['split'] = 'calibration' if position < boundary else 'test'
        trials.extend(selected)
    rng.shuffle(trials)
    for index, trial in enumerate(trials, 1):
        trial['trial_id'] = index
    return trials


def decision(ranking, threshold):
    passing = [r for r in ranking['top'] if r['score'] >= threshold]
    if len(passing) == 1:
        return passing[0]['product_id'], 'accepted'
    return None, 'ambiguous' if len(passing) > 1 else 'below_threshold_or_no_candidate'


def wilson_lower(successes, total):
    if not total:
        return None
    z = 1.959963984540054
    p = successes / total
    return (p + z*z/(2*total) - z*math.sqrt(p*(1-p)/total + z*z/(4*total*total))) / (1 + z*z/total)


def evaluate(scored, scope, threshold):
    counts = Counter()
    for trial in scored:
        predicted, reason = decision(trial['rankings'][scope], threshold)
        expected = trial['expected_product_id']
        counts['total'] += 1
        counts['known_queries' if expected is not None else 'absent_queries'] += 1
        if predicted is not None:
            counts['accepted'] += 1
            counts['correct_links' if predicted == expected else 'wrong_links'] += 1
            if expected is None:
                counts['absent_wrong_links'] += 1
        else:
            counts['abstained'] += 1
            counts[reason] += 1
            if expected is None:
                counts['correct_absent_rejections'] += 1
    result = {key: counts[key] for key in (
        'total', 'known_queries', 'absent_queries', 'accepted', 'correct_links',
        'wrong_links', 'absent_wrong_links', 'abstained', 'ambiguous',
        'below_threshold_or_no_candidate', 'correct_absent_rejections')}
    precision = counts['correct_links'] / counts['accepted'] if counts['accepted'] else None
    recall = counts['correct_links'] / counts['known_queries'] if counts['known_queries'] else None
    result.update({
        'precision': precision, 'recall': recall,
        'coverage': counts['accepted'] / counts['total'] if counts['total'] else None,
        'precision_wilson_95_lower': wilson_lower(counts['correct_links'], counts['accepted']),
        'f1': 2*precision*recall/(precision+recall) if precision and recall else 0.0,
    })
    return result


def choose_threshold(sweep, target_precision, min_accepted):
    eligible = [entry for entry in sweep if entry['metrics']['precision'] is not None
                and entry['metrics']['precision'] >= target_precision
                and entry['metrics']['accepted'] >= min_accepted]
    if not eligible:
        return None
    return max(eligible, key=lambda entry: (
        entry['metrics']['recall'] or 0, entry['metrics']['precision'], entry['threshold']))


def summarize(scored, metadata, target_precision, min_accepted, step):
    summaries, sweeps = {}, {}
    grid = [round(i*step, 10) for i in range(int(100/step) + 1)]
    if grid[-1] != 100:
        grid.append(100.0)
    for scope in ('company_known', 'company_unknown'):
        for route in ('omission', 'typo'):
            key = f'{scope}/{route}'
            calibration = [t for t in scored if t['route'] == route and t['split'] == 'calibration']
            test = [t for t in scored if t['route'] == route and t['split'] == 'test']
            sweep = [{'threshold': threshold, 'metrics': evaluate(calibration, scope, threshold)}
                     for threshold in grid]
            chosen = choose_threshold(sweep, target_precision, min_accepted)
            sweeps[key] = sweep
            result = {'calibration_queries': len(calibration), 'test_queries': len(test),
                      'recommended_threshold': None,
                      'status': 'no_cutoff_meets_calibration_requirements'}
            # Always expose a useful tradeoff, even when no threshold qualifies.
            # This is chosen on calibration ONLY, and is NOT a recommendation.
            enough = [entry for entry in sweep if entry['metrics']['accepted'] >= min_accepted]
            if enough:
                diagnostic = max(enough, key=lambda entry: (
                    entry['metrics']['precision'] or 0,
                    entry['metrics']['recall'] or 0, entry['threshold']))
                diagnostic_threshold = diagnostic['threshold']
                result['highest_calibration_precision_diagnostic'] = {
                    'threshold': diagnostic_threshold, 'not_a_recommendation': True,
                    'calibration_metrics': diagnostic['metrics'],
                    'test_metrics': evaluate(test, scope, diagnostic_threshold),
                    'wrong_test_examples': [],
                }
                for trial in test:
                    predicted, _ = decision(trial['rankings'][scope], diagnostic_threshold)
                    if predicted is not None and predicted != trial['expected_product_id']:
                        result['highest_calibration_precision_diagnostic']['wrong_test_examples'].append(trial)
                        if len(result['highest_calibration_precision_diagnostic']['wrong_test_examples']) == 10:
                            break
            if chosen:
                threshold = chosen['threshold']
                test_metrics = evaluate(test, scope, threshold)
                result.update({
                    'recommended_threshold': threshold,
                    'calibration_metrics': chosen['metrics'], 'test_metrics': test_metrics,
                    'test_by_kind': {kind: evaluate([t for t in test if t['kind'] == kind], scope, threshold)
                                     for kind in sorted({t['kind'] for t in test})},
                    'test_meets_point_precision_target': (
                        test_metrics['precision'] is not None and test_metrics['precision'] >= target_precision),
                    'status': 'synthetic_only_not_production_validated',
                    'wrong_test_examples': [],
                })
                for trial in test:
                    predicted, _ = decision(trial['rankings'][scope], threshold)
                    if predicted is not None and predicted != trial['expected_product_id']:
                        result['wrong_test_examples'].append(trial)
                        if len(result['wrong_test_examples']) == 10:
                            break
            summaries[key] = result
    controls = [t for t in scored if t['route'] == 'exact_control']
    return {
        'metadata': metadata, 'finished_at': now(), 'total_trials': len(scored),
        'target_precision': target_precision, 'min_calibration_acceptances': min_accepted,
        'threshold_grid_step': step, 'recommendations': summaries,
        'exact_name_controls_at_100': {scope: evaluate(controls, scope, 100)
                                      for scope in ('company_known', 'company_unknown')},
        'production_ready': False,
    }, sweeps


def percent(value):
    return '-' if value is None else f'{100*value:.2f}%'


def report_markdown(summary):
    lines = [
        '# 제품명 매핑 합성 실험 결과', '',
        '**실제 광고로 검증한 운영 임계값이 아닙니다. 원본 DB는 수정하지 않았습니다.**', '',
        f"- 시험 질의: {summary['total_trials']:,}개 (각 질의를 제조사 확인/미확인 조건에서 각각 평가)",
        f"- 실험 목표 정밀도: {percent(summary['target_precision'])} (사용자 조정 가능한 실험 정책값)",
        '- 점수: NFC·casefold·공백 제거 후 전체 이름의 정규화 Damerau–Levenshtein × 100',
        '- 판정: 기준을 통과한 제품 기록이 정확히 1개일 때만 연결. 동점/복수 통과는 보류.',
        '- 생략: 온전한 공백 구분 구절을 포함하는 모든 기록을 조회한 뒤 제조사를 비교.',
        '- 오타: 부분 구간 점수 없이 전체 이름을 비교. 생략+오타도 전체 이름 거리로 평가.',
        '- 부재 시험: 질의의 정답 기록만 검색 카탈로그에서 제외(원본 DB 삭제 아님).', '',
        '| 제조사 조건 / 검색 경로 | 실험 추천 기준 | 개발 정밀도 | 개발 재현율 | 테스트 정밀도 | 테스트 재현율 | 테스트 오연결 |',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for key, entry in summary['recommendations'].items():
        if entry['recommended_threshold'] is None:
            lines.append(f'| {key} | 추천 없음 | - | - | - | - | - |')
            continue
        dev, test = entry['calibration_metrics'], entry['test_metrics']
        lines.append(f"| {key} | {entry['recommended_threshold']:g} | {percent(dev['precision'])} | "
                     f"{percent(dev['recall'])} | {percent(test['precision'])} | {percent(test['recall'])} | "
                     f"{test['wrong_links']}/{test['accepted']} |")
    lines += ['', '## 목표 미충족 시에도 볼 수 있는 진단값', '',
        '**아래 값은 최소 개발 연결 건수를 만족하는 범위에서 개발 정밀도가 가장 높았던 기준입니다. 운영 추천값이 아닙니다.**', '',
        '| 제조사 조건 / 검색 경로 | 진단 기준 | 개발 정밀도 | 테스트 정밀도 | 테스트 재현율 | 테스트 오연결/연결 |',
        '|---|---:|---:|---:|---:|---:|']
    for key, entry in summary['recommendations'].items():
        diagnostic = entry.get('highest_calibration_precision_diagnostic')
        if not diagnostic:
            lines.append(f'| {key} | 자료 부족 | - | - | - | - |')
            continue
        dev, test = diagnostic['calibration_metrics'], diagnostic['test_metrics']
        lines.append(f"| {key} | {diagnostic['threshold']:g} | {percent(dev['precision'])} | "
                     f"{percent(test['precision'])} | {percent(test['recall'])} | "
                     f"{test['wrong_links']}/{test['accepted']} |")
    lines += ['', '## 해석 시 확인할 점', '',
        '- 임계값은 개발 60%에서만 선택하고 나머지 40%는 최종 평가에만 사용했습니다.',
        '- 원본 정규화 제품명이 같은 질의들이 개발/테스트 양쪽에 중복되지 않습니다.',
        '- 동일 이름·다른 신고번호는 서로 다른 DB 기록입니다. 이름만으로 구별되지 않을 수 있습니다.',
        '- 제조사 확인 조건은 원본 DB 제조사를 완벽히 알아냈다고 가정합니다. 브랜드 혼동/OCR 오류는 시험하지 않습니다.',
        '- 생략/오타/부재 비율과 오타 분포는 합성 설계입니다. 실제 광고 분포와 다릅니다.',
        '- 실제 광고의 제품 식별 정답 쌍으로 추가 검증하기 전에는 운영에 자동 적용하지 마세요.',
        '- summary.json에는 유형별 테스트 결과, 오연결 사례, 정밀도의 Wilson 95% 하한을 포함합니다.',
        '- 부재 질의도 포함하므로 모든 질의에 가장 가까운 제품을 무조건 붙이는 성능을 보고하지 않습니다.',
        '- 이 실험은 제품명 식별만 평가합니다. Claim–Evidence 의미 검색/참거짓 판정은 실행하지 않습니다.', '',
    ]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=ROOT/'Data_List_Claim_Verification/claim_verification.sqlite')
    parser.add_argument('--trials', type=int, default=1000)
    parser.add_argument('--seed', type=int, default=20261018)
    parser.add_argument('--target-precision', type=float, default=.99)
    parser.add_argument('--min-accepted', type=int, default=30)
    parser.add_argument('--threshold-step', type=float, default=.5)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.trials < 20 or not 0 < args.target_precision <= 1 or args.min_accepted < 1:
        parser.error('Use trials >= 20, 0 < target-precision <= 1 and min-accepted >= 1.')
    if not 0 < args.threshold_step <= 100:
        parser.error('threshold-step must be in (0, 100].')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Do not allow a chosen output filename to replace the input DB.
    if args.db.resolve() in {output/name for name in (
        'metadata.json', 'progress.json', 'trials.jsonl', 'scored_cases.jsonl',
        'summary.json', 'threshold_sweep.json', 'report.md')}:
        parser.error('Output would overwrite the input database.')
    progress_path = output/'progress.json'
    started = time.perf_counter()
    completed = 0
    base = {'pid': os.getpid(), 'started_at': now(), 'total': args.trials,
            'completed': 0, 'output': str(output), 'status': 'initializing'}
    old_metadata = None
    if (output/'metadata.json').exists():
        if not args.resume:
            parser.error('Output already has an experiment; choose a new directory or use --resume.')
        old_metadata = json.loads((output/'metadata.json').read_text(encoding='utf-8'))
    atomic_json(progress_path, base)
    try:
        rows, fingerprint = load_catalog(args.db)
        if args.trials > len({normalize(r['product_name']) for r in rows}):
            raise ValueError('Requested more trials than distinct source product names.')
        metadata = {
            'schema_version': SCHEMA_VERSION, 'created_at': now(),
            'db': str(args.db.resolve()), 'db_open_mode': 'ro; PRAGMA query_only=ON',
            'catalog_fingerprint_sha256': fingerprint, 'products': len(rows),
            'distinct_normalized_names': len({normalize(r['product_name']) for r in rows}),
            'company_count': len({normalize(r['company_name']) for r in rows}),
            'trials': args.trials, 'seed': args.seed, 'rapidfuzz_version': rapidfuzz.__version__,
            'python_version': sys.version.split()[0], 'split': '60% calibration / 40% held-out test per kind',
            'synthetic': True, 'production_ready': False,
            'identity_definition': 'Exact product record/report number; not general product family or sales option.',
            'kind_proportions': KINDS, 'generic_guard_words': sorted(GENERIC_WORDS),
            'company_scope': 'Exact normalized source manufacturer, or unknown; no brand-to-maker inference.',
        }
        if old_metadata:
            for key in ('schema_version', 'catalog_fingerprint_sha256', 'trials', 'seed', 'rapidfuzz_version'):
                if old_metadata.get(key) != metadata[key]:
                    raise ValueError(f'Resume mismatch: {key}')
            metadata = old_metadata
        else:
            atomic_json(output/'metadata.json', metadata)
        catalog = Catalog(rows)
        trials = make_trials(rows, args.trials, args.seed)
        trial_hash = hashlib.sha256(json.dumps(trials, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if old_metadata and old_metadata.get('trial_fingerprint_sha256') != trial_hash:
            raise ValueError('Resume mismatch: generated trials changed.')
        metadata['trial_fingerprint_sha256'] = trial_hash
        atomic_json(output/'metadata.json', metadata)
        (output/'trials.jsonl').write_text(
            ''.join(json.dumps(t, ensure_ascii=False) + '\n' for t in trials), encoding='utf-8')
        scored_path = output/'scored_cases.jsonl'
        scored = []
        if args.resume and scored_path.exists():
            # An interrupted final JSONL line is discarded; complete lines are retained.
            for line in scored_path.read_text(encoding='utf-8').splitlines():
                try:
                    scored.append(json.loads(line))
                except json.JSONDecodeError:
                    break
            if [t['trial_id'] for t in scored] != list(range(1, len(scored) + 1)):
                raise ValueError('Checkpoint trial sequence is invalid.')
            scored_path.write_text(''.join(json.dumps(t, ensure_ascii=False)+'\n' for t in scored), encoding='utf-8')
        elif scored_path.exists():
            raise ValueError('scored_cases.jsonl already exists; use --resume or a new directory.')
        completed = len(scored)
        print(f'[MATCH] Products: {len(rows):,}; trials: {len(trials):,}; resume: {completed}', flush=True)
        with scored_path.open('a', encoding='utf-8', buffering=1) as checkpoint:
            for trial in trials[completed:]:
                phrase = catalog.phrase_candidates(trial['query']) if trial['route'] == 'omission' else None
                trial['rankings'] = {scope: catalog.rank(trial, scope, phrase)
                                     for scope in ('company_known', 'company_unknown')}
                checkpoint.write(json.dumps(trial, ensure_ascii=False) + '\n')
                scored.append(trial)
                completed += 1
                if completed % 10 == 0 or completed == len(trials):
                    elapsed = time.perf_counter() - started
                    atomic_json(progress_path, {**base, 'status': 'running', 'completed': completed,
                        'updated_at': now(), 'elapsed_seconds': round(elapsed, 2)})
                if completed % 50 == 0:
                    print(f'[MATCH] {completed}/{len(trials)}', flush=True)
        atomic_json(progress_path, {**base, 'status': 'summarizing', 'completed': completed, 'updated_at': now()})
        summary, sweeps = summarize(scored, metadata, args.target_precision, args.min_accepted, args.threshold_step)
        atomic_json(output/'summary.json', summary)
        atomic_json(output/'threshold_sweep.json', sweeps)
        (output/'report.md').write_text(report_markdown(summary), encoding='utf-8')
        atomic_json(progress_path, {**base, 'status': 'complete', 'completed': completed,
            'updated_at': now(), 'elapsed_seconds': round(time.perf_counter() - started, 2),
            'report': str(output/'report.md')})
        print(f'[MATCH] Complete. Synthetic-only report: {output / "report.md"}', flush=True)
        return 0
    except BaseException as exc:
        atomic_json(progress_path, {**base, 'status': 'interrupted' if isinstance(exc, KeyboardInterrupt) else 'failed',
            'completed': completed, 'updated_at': now(), 'error': f'{type(exc).__name__}: {exc}'})
        raise


if __name__ == '__main__':
    raise SystemExit(main())
