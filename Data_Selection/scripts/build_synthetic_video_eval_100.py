"""Prepare 100 source-grounded synthetic videos in the agreed A/B transport schema.

Reference labels and edits are stored separately from the inference input.
"""
import argparse
import copy
import hashlib
import json
import random
import re
import sqlite3
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.claim_evidence_experiment import name_key
from src.product_identity_filtered import company_core
from src.product_name_groups import ProductGroups
from src.claim_type_db_format import build_product, TYPE_FIELDS, ARRAYS

SOURCE = Path(r'C:\Users\박이정\Documents\카카오톡 받은 파일\claims_all_db_matched_353.json')
DATABASE = ROOT / 'TRUEAD_DB_보강자료/claim_verification.sqlite'
OUT = ROOT / 'exports/synthetic_video_eval_100_20261105'
SEED = 20261105
GROUPS = [('violation_1', 35, 3), ('overclaim_1', 35, 3),
          ('violation_1_overclaim_1', 10, 2), ('violation_2', 10, 1), ('overclaim_2', 10, 1)]

# Each anchor is checked against the actual selected product's MAIN_FNCTN.
# Overclaims add unsupported magnitude/time/target details without disease or drug claims.
DOMAINS = {
 'digestion': ('소화', '췌장염을 치료한다.', '췌장염 치료',
               '한 번만 먹어도 지방 소화 능력이 세 배로 높아지는 효과가 확실하다.', '일주일 만에 담즙 분비량이 두 배로 늘어나는 효과가 확실하다.'),
 'oral': ('구강', '충치를 치료한다.', '충치 치료',
          '한 번만 먹어도 입안 유해균을 100% 깨끗이 제거한다.', '일주일 만에 구강 방어력이 세 배로 높아지는 효과가 확실하다.'),
 'height': ('키성장', '성장호르몬 주사 대신 먹을 수 있다.', '성장호르몬 주사를 대체함',
            '한 달 만에 아이 키가 5cm 더 크는 효과가 확실하다.', '한 번만 먹어도 성장판 활동이 즉시 두 배로 늘어난다.'),
 'sleep': ('수면의 질', '불면증을 치료한다.', '불면증 치료',
           '먹은 날부터 깊은 수면 시간이 두 배로 늘어나는 효과가 확실하다.', '일주일 만에 밤중에 깨는 횟수를 90%까지 확실히 줄인다.'),
 'liver': ('간 건강', '간염을 치료한다.', '간염 치료',
           '일주일 만에 간 해독 능력을 두 배로 높이는 효과가 확실하다.', '한 번만 먹어도 간에 쌓인 노폐물을 깨끗이 제거한다.'),
 'menopause': ('갱년기', '갱년기 호르몬 치료제를 대신할 수 있다.', '호르몬 치료제 대체',
               '단 3일 만에 갱년기 불편감을 90% 줄이는 효과가 확실하다.', '한 번만 먹어도 갱년기로 떨어진 체력이 즉시 두 배로 좋아진다.'),
 'skin': ('피부', '아토피 피부염을 치료한다.', '아토피 피부염 치료',
          '일주일 만에 피부 수분량을 두 배로 높이는 효과가 확실하다.', '단 3일 만에 얼굴 잔주름을 절반으로 확실히 줄인다.'),
 'weight': ('체지방', '비만 치료제를 대신할 수 있다.', '비만 치료제 대체',
            '2주 만에 체지방 5kg을 확실히 줄인다.', '식사량을 줄이지 않아도 일주일 만에 뱃살만 골라 30% 없애 준다.'),
 'glucose': ('혈당', '당뇨병을 치료한다.', '당뇨병 치료',
             '단 한 번 섭취로 식후 혈당을 50mg/dL 낮추는 효과가 확실하다.', '탄수화물을 두 배로 먹어도 식후 혈당 상승을 완전히 막는다.'),
 'joint': ('관절', '퇴행성 관절염을 치료한다.', '퇴행성 관절염 치료',
           '일주일 만에 관절 유연성을 두 배로 높이는 효과가 확실하다.', '하루 만에 무릎 움직임 범위를 50% 넓혀 주는 효과가 확실하다.'),
 'eye': ('눈', '황반변성을 치료한다.', '황반변성 치료',
         '일주일 만에 시력을 0.3 높여 주는 효과가 확실하다.', '단 하루 만에 눈의 피로를 90%까지 확실히 줄인다.'),
 'urinary': ('배뇨', '방광염을 치료한다.', '방광염 치료',
             '사흘 만에 야간 화장실 방문 횟수를 90% 줄이는 효과가 확실하다.', '한 번만 먹어도 방광의 소변 저장 능력이 두 배로 늘어난다.'),
 'gastric': ('위 ', '위염과 위궤양을 치료한다.', '위염·위궤양 치료',
             '한 번 섭취로 위 불편감을 90% 줄이는 효과가 확실하다.', '단 3일 만에 위 점막 두께를 두 배로 늘려 준다.'),
 'muscle': ('근력', '근감소증을 치료한다.', '근감소증 치료',
            '운동을 하지 않아도 일주일 만에 근력이 두 배로 늘어나는 효과가 확실하다.', '2주 만에 근육량 3kg 증가가 확실하다.'),
 'cholesterol': ('콜레스테롤', '고지혈증 치료제를 대신할 수 있다.', '고지혈증 치료제 대체',
                 '일주일 만에 혈중 콜레스테롤을 50% 줄이는 효과가 확실하다.', '한 번만 먹어도 콜레스테롤 수치가 절반으로 떨어진다.'),
 'vascular': ('혈행', '혈전증을 치료한다.', '혈전증 치료',
              '한 번만 먹어도 말초 혈류량이 두 배로 늘어나는 효과가 확실하다.', '일주일 만에 혈관 탄력성을 50% 높이는 효과가 확실하다.'),
 'bloodpressure': ('혈압', '고혈압약을 대신할 수 있다.', '고혈압약 대체',
                   '한 번 섭취로 수축기 혈압을 30mmHg 낮추는 효과가 확실하다.', '일주일 만에 혈압 변동 폭을 90% 줄이는 효과가 확실하다.'),
 'gut': ('배변', '장염을 치료한다.', '장염 치료',
         '하루 만에 장내 유해균을 99% 깨끗이 제거한다.', '3일 만에 장내 유익균 수를 열 배로 늘리는 효과가 확실하다.'),
 'bone': ('뼈', '골다공증을 치료한다.', '골다공증 치료',
          '한 달 만에 골밀도를 30% 높이는 효과가 확실하다.', '일주일 만에 뼈의 강도를 두 배로 높여 준다.'),
 'immune': ('면역', '독감을 예방한다.', '독감 예방',
            '3일 만에 면역세포 활성도를 세 배로 높이는 효과가 확실하다.', '단 한 번 섭취로 면역세포 활동이 즉시 두 배로 늘어난다.'),
 'energy': ('에너지', '만성피로증후군을 치료한다.', '만성피로증후군 치료',
            '한 번만 먹어도 하루 에너지 소모 효율이 두 배로 높아지는 효과가 확실하다.', '일주일 만에 신체 지구력을 세 배로 높이는 효과가 확실하다.'),
 'iron': ('철', '철결핍성 빈혈 치료제를 대신할 수 있다.', '빈혈 치료제 대체',
          '일주일 만에 철 흡수율을 세 배로 높이는 효과가 확실하다.', '한 번만 먹어도 철분 이용 효율이 두 배로 높아진다.'),
}


def choose_domain(product):
    name = product['product_name']
    text = product['main_functionality']
    # Prefer the advertised product theme, rather than incidental vitamin functions.
    priorities = [
        ('키성장|아이커|아이클타임', 'height'), ('딥슬립', 'sleep'),
        ('밀크씨슬|간에게|간 건강|간케어', 'liver'),
        ('메노락토|루바브|화애락 터닝', 'menopause'), ('콜라겐', 'skin'),
        ('다이어트|비에날|메타그린|감비책|콜레올로지|먹어도 돼', 'weight'),
        ('혈당|바나바', 'glucose'), ('관절|옵티머스트|천관보', 'joint'),
        ('루테인|아이클리어|아이시안|아이원|아이 포커스', 'eye'),
        ('안심뇨', 'urinary'), ('위건강|가네요', 'gastric'), ('머슬', 'muscle'),
        ('콜레스테롤', 'cholesterol'), ('오메가|혈관|메가렉스', 'vascular'),
        ('코엔자임', 'bloodpressure'), ('유산균|바이오틱스|드시모네|듀오락|락토핏', 'gut'),
        ('칼슘|비타민D', 'bone'), ('헤모힘|이뮨|면역', 'immune'),
    ]
    for pattern, key in priorities:
        if re.search(pattern, name) and DOMAINS[key][0] in text:
            return key
    for key in ['sleep','liver','menopause','weight','glucose','joint','eye','urinary',
                'gastric','muscle','cholesterol','vascular','bloodpressure','gut','skin',
                'immune','bone','energy','iron','digestion','oral']:
        if DOMAINS[key][0] in text:
            return key
    raise ValueError('Product requires manual functional review: ' + name)


def evidence(row, column, anchor=None):
    text = row.get(column)
    assert isinstance(text, str) and text
    assert anchor is None or anchor in text
    return {'table': 'products', 'product_id': row['product_id'], 'column': column,
            'text': text, 'anchor': anchor}


def violation_recipe(product, number, second=False):
    domain = choose_domain(product)
    row = product
    # Explicit daily intake contradictions avoid mass denominator/CFU ambiguity.
    intake = row.get('intake_method') or ''
    dose = re.search(r'1일\s*1회\s*[,，]?\s*1회\s*(\d+)\s*(정|캡슐|포|병|환)', intake)
    if dose and (second or number % 3 == 0) and len(re.findall(r'1일', intake)) == 1:
        old_count, unit = int(dose[1]), dose[2]
        new_count = old_count + 2
        return {'text': f"{row['product_name']}의 등록된 하루 섭취량은 {new_count}{unit}이다.",
                'claim_type': ['QUANTITY'], 'ingredients': [], 'effect': None,
                'quantity': f'{new_count}{unit}', 'intake_basis': '1일 1회 섭취 기준',
                'subtype': 'daily_intake_mismatch',
                'evidence': [evidence(row, 'intake_method', dose[0])],
                'reason': f'같은 하루 기준에서 DB는 {old_count}{unit}이나 Claim은 {new_count}{unit}으로 변경함.'}
    cautions = row.get('intake_precautions') or ''
    if (second or number % 4 == 0) and re.search(r'수유부[^\n]{0,25}섭취를\s*피', cautions):
        line = next(line for line in cautions.splitlines() if '수유부' in line and '피' in line)
        return {'text': f"{row['product_name']} 제품은 수유부도 먹을 수 있다.",
                'claim_type': ['EFFECT'], 'ingredients': [], 'effect': '수유부 섭취 가능',
                'quantity': None, 'intake_basis': None, 'subtype': 'same_target_precaution_conflict',
                'evidence': [evidence(row, 'intake_precautions', line)],
                'reason': '광고와 DB가 모두 수유부 섭취를 말하며, 섭취 회피 조건에 직접 반하는 주장임.'}
    if second:
        shelf = row.get('shelf_life') or ''
        period = re.search(r'(\d+)\s*(개월|년)', shelf)
        if period and '제조일' in shelf:
            old = int(period[1]) * (12 if period[2] == '년' else 1); new = old + 12
            return {'text': f"{row['product_name']}의 소비기한은 제조일로부터 {new}개월이다.",
                    'claim_type': ['QUANTITY'], 'ingredients': [], 'effect': None,
                    'quantity': f'{new}개월', 'intake_basis': '제조일로부터',
                    'subtype': 'shelf_life_mismatch', 'evidence': [evidence(row, 'shelf_life', period[0])],
                    'reason': f'DB의 제조일 기준 {old}개월을 같은 기준의 {new}개월로 변경함.'}
        raise ValueError('No distinct grounded second violation: ' + row['product_name'])
    anchor, predicate, effect, *_ = DOMAINS[domain]
    return {'text': f"{row['product_name']} 제품은 {predicate}", 'claim_type': ['EFFECT'],
            'ingredients': [], 'effect': effect, 'quantity': None, 'intake_basis': None,
            'subtype': 'disease_prevention_treatment_or_drug_substitution',
            'evidence': [evidence(row, 'main_functionality', anchor)],
            'reason': '건강 보조 기능을 질병 예방·치료 또는 의약품 대체 주장으로 바꿈. 주간 발표의 질병·의약품 주장 기준에 따른 정답임.'}


def overclaim_recipe(product, variant=0):
    domain = choose_domain(product)
    anchor, _, _, first, second = DOMAINS[domain]
    predicate = (first, second)[variant]
    # Check both product-level and raw-material functional evidence; never infer
    # that missing evidence proves the claimed effect is empirically false.
    raw = product.get('RAWMTRL_STD_INFO')
    raw = json.loads(raw) if isinstance(raw, str) and raw else raw or []
    refs = [evidence(product, 'main_functionality', anchor)]
    if product.get('RAWMTRL_STD_INFO'):
        refs.append(evidence(product, 'RAWMTRL_STD_INFO'))
    material_functions = [r.get('PRIMARY_FNCLTY', '') for r in raw]
    assert predicate not in product['main_functionality']
    assert all(predicate not in f for f in material_functions)
    return {'text': f"{product['product_name']} 제품은 {predicate}", 'claim_type': ['EFFECT'],
            'ingredients': [], 'effect': predicate, 'quantity': None, 'intake_basis': None,
            'subtype': 'unsupported_quantified_or_specific_effect_' + domain,
            'evidence': refs,
            'reason': '제품 및 원료의 인정 기능성에는 이 기간·수치·구체적 결과를 보장하는 문장이 없음. '
                      '질병 치료나 의약품 대체가 아니라, 인정 범위를 넘는 과장된 효과로 구성함. '
                      'NLI 점수를 정답으로 사용하지 않으며 실제 NLI의 OVERCLAIM 출력은 별도 평가 대상임.'}


def compile_dataset(selections, info):
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    baseline, altered, labels, assignments, mapping_audit = [], [], [], [], []
    original_count = excluded_etc = vcount = ocount = 0
    for item in selections:
        source = item['source']
        base = {'video_id': source['video_id'], 'url': source.get('url'),
                'db_version': '2026-11-03T04:09:56.363154+00:00', 'products': [], 'claims': []}
        for p in item['mapped']:
            mapping = {'product': {'match': {'status': 'confirmed', 'method': 'name_and_company'}}}
            base['products'].append(build_product(p['input'], mapping, p['row'], p['candidate_count']))
            mapping_audit.append({'video_id': source['video_id'], 'product_ref': p['input']['product_ref'],
                                  'product_id': p['row']['product_id'],
                                  'source_manufacturer': p['input']['manufacturer_name'],
                                  'db_company': p['row']['company_name'],
                                  'method': 'name_and_company', 'fuzzy_search_used': False,
                                  'candidate_rows_with_same_normalized_name': p['candidate_count']})
        for c in source['claims']:
            assert 'effect' in c and isinstance(c['claim_type'], list)
            if c['claim_type'] == ['ETC']:
                excluded_etc += 1
                continue
            base['claims'].append(copy.deepcopy(c))
        original_count += len(base['claims'])
        baseline.append(base)
        modified = copy.deepcopy(base)
        group = item['group']
        requested = {'violation_1': ['VIOLATION'], 'overclaim_1': ['OVERCLAIM'],
                     'violation_1_overclaim_1': ['VIOLATION','OVERCLAIM'],
                     'violation_2': ['VIOLATION','VIOLATION'], 'overclaim_2': ['OVERCLAIM','OVERCLAIM']}[group]
        added = []
        existing_numbers = [int(c['claim_id'][1:]) for c in source['claims'] if re.fullmatch(r'c\d+', c['claim_id'])]
        next_claim_number = max(existing_numbers, default=0) + 1
        for index, label in enumerate(requested):
            target = item['mapped'][index % len(item['mapped'])]
            row = target['row']
            if label == 'VIOLATION':
                recipe_number = 1 if group == 'violation_2' and index == 0 else vcount
                recipe = violation_recipe(row, recipe_number, second=index == 1 and group == 'violation_2' and len(item['mapped']) == 1)
                vcount += 1
            else:
                recipe = overclaim_recipe(row, variant=index if group == 'overclaim_2' else ocount % 2)
                ocount += 1
            cid = f'c{next_claim_number + index:02d}'
            assert cid not in {c['claim_id'] for c in modified['claims']}
            claim = {'claim_id': cid, 'product_ref': target['input']['product_ref'],
                     **{k: copy.deepcopy(recipe[k]) for k in ['text','claim_type','ingredients','effect','quantity','intake_basis']}}
            modified['claims'].append(claim)
            label_record = {'video_id': source['video_id'], 'claim_id': cid,
                            'product_ref': claim['product_ref'], 'product_id': row['product_id'],
                            'product_name': row['product_name'], 'company_name': row['company_name'],
                            'claim': copy.deepcopy(claim), 'gold_label': label,
                            'review_note': recipe['reason'], 'evidence': recipe['evidence']}
            labels.append(label_record)
            added.append({'claim_id': cid, 'gold_label': label, 'product_ref': claim['product_ref'],
                          'product_id': row['product_id'], 'subtype': recipe['subtype']})
        assignments.append({'video_id': source['video_id'], 'url': source.get('url'), 'title': source.get('title'),
                            'group': group, 'product_count': len(item['mapped']), 'inserted_claims': added})
        altered.append(modified)
    assert vcount == ocount == 65
    summary = {'source_file': str(SOURCE), 'source_sha256': source_hash,
               'videos': len(altered), 'video_groups': dict(Counter(a['group'] for a in assignments)),
               'products_per_video': dict(Counter(len(v['products']) for v in altered)),
               'product_entries': sum(len(v['products']) for v in altered),
               'unique_db_products': len({a['product_id'] for a in mapping_audit}),
               'confirmed_product_entries': len(mapping_audit),
               'baseline_claims_after_etc_exclusion': original_count,
               'excluded_pure_etc_claims': excluded_etc,
               'inserted_claims': len(labels), 'inserted_labels': dict(Counter(r['gold_label'] for r in labels)),
               'violation_insertion_videos': sum(any(c['gold_label']=='VIOLATION' for c in a['inserted_claims']) for a in assignments),
               'overclaim_insertion_videos': sum(any(c['gold_label']=='OVERCLAIM' for c in a['inserted_claims']) for a in assignments),
               'output_claims': sum(len(v['claims']) for v in altered),
               'effect_fields_present': sum('effect' in c for v in altered for c in v['claims']),
               'claim_type_format': 'array, preserved as approved by user',
               'original_claims_gold_labeled': False, 'original_video_media_modified': False,
               'A_B_consumer_runtime_tested': False, 'NLI_predictions_used_as_gold': False,
               'selection_seed': SEED,
               'subtype_counts': dict(Counter(c['subtype'] for a in assignments for c in a['inserted_claims']))}
    summary['inserted_effect_claims'] = sum('EFFECT' in r['claim']['claim_type'] for r in labels)
    summary['inserted_quantity_claims'] = sum('QUANTITY' in r['claim']['claim_type'] for r in labels)
    validate_dataset(altered, baseline, labels, assignments, selections)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
    write_json(OUT / 'source_selected_100.json', [s['source'] for s in selections])
    write_json(OUT / 'baseline_with_db.json', baseline)
    write_json(OUT / 'claims_with_db.json', altered)
    write_json(OUT / 'gold_labels.json', labels)
    write_json(OUT / 'video_assignments.json', assignments)
    write_json(OUT / 'product_mapping_audit.json', mapping_audit)
    write_json(OUT / 'summary.json', summary)
    video_dir = OUT / 'videos'
    video_dir.mkdir(exist_ok=True)
    for video in altered:
        assert re.fullmatch(r'[A-Za-z0-9_.-]+', video['video_id'])
        write_json(video_dir / (video['video_id'] + '.json'), video)
    write_review(labels, assignments, summary)
    with zipfile.ZipFile(OUT / 'handoff_A_B_100.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for video in altered:
            path = video_dir / (video['video_id'] + '.json')
            z.write(path, 'videos/' + path.name)
        z.writestr('README.txt', 'A/B input: 100 per-video JSON files. claim_type is an array. '
                   'Preserve effect, product_ref, match and DB fields. No gold labels are included. '
                   'Run either these per-video files OR the combined claims_with_db.json, not both.\n')
    with zipfile.ZipFile(OUT / 'synthetic_video_eval_100.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path.suffix in {'.json','.md'}:
                z.write(path, path.relative_to(OUT).as_posix())
    return summary


def validate_dataset(altered, baseline, labels, assignments, selections):
    assert len(altered) == len(baseline) == len(assignments) == 100
    assert Counter(len(v['products']) for v in altered) == {1: 90, 2: 10}
    assert len(labels) == 130 and Counter(r['gold_label'] for r in labels) == {'VIOLATION':65,'OVERCLAIM':65}
    ids = {(r['video_id'],r['claim_id']) for r in labels}
    assert len(ids) == 130
    for video, base, item in zip(altered, baseline, selections):
        assert set(video) == {'video_id','url','db_version','products','claims'}
        assert video['products'] == base['products']
        assert video['claims'][:len(base['claims'])] == base['claims']
        assert base['claims'] == [c for c in item['source']['claims'] if c['claim_type'] != ['ETC']]
        products = {p['product_ref']:p for p in video['products']}
        assert len(products) == len(video['products'])
        assert len({c['claim_id'] for c in video['claims']}) == len(video['claims'])
        for c in video['claims']:
            assert 'effect' in c and isinstance(c['claim_type'], list)
            assert c['product_ref'] in products
            assert 'gold_label' not in c and 'review_note' not in c
            if (video['video_id'],c['claim_id']) in ids and 'EFFECT' in c['claim_type']:
                assert c['effect']
        for original, product, mapping in zip(item['source']['products'],video['products'],item['mapped']):
            assert set(product) == set(original) | {'match','DB'}
            assert product['match']['status'] == 'confirmed'
            assert set(product['match']) == {'status','method','candidates','matched_name','matched_company'}
            assert product['DB']['EFFECT']['MAIN_FNCTN'] == mapping['row']['main_functionality']
            for kind, fields in TYPE_FIELDS.items():
                assert list(product['DB'][kind]) == fields
                assert all(isinstance(product['DB'][kind][f],list if f in ARRAYS else str) for f in fields)
            for field in original:
                if field != 'manufacturing_report_number':
                    assert product[field] == original[field]
    product_rows = {p['row']['product_id']:p['row'] for s in selections for p in s['mapped']}
    lookup = {(v['video_id'], c['claim_id']):(v,c) for v in altered for c in v['claims']}
    for gold in labels:
        video, claim = lookup[(gold['video_id'],gold['claim_id'])]
        assert gold['claim'] == claim
        for ref in gold['evidence']:
            assert ref['product_id'] == gold['product_id']
            assert product_rows[ref['product_id']][ref['column']] == ref['text']
        if gold['gold_label'] == 'OVERCLAIM':
            assert claim['claim_type'] == ['EFFECT'] and claim['effect']
            assert not re.search(r'치료|완치|예방|의약품|치료제|대신', claim['text'])


def write_review(labels, assignments, summary):
    lines = ['# 100개 영상 합성 평가 데이터 — 검토용', '',
             '원본 영상·실제 광고 발언이 아닌 JSON에 삽입한 합성 Claim의 평가 정답임.',
             '아래 라벨은 주간 발표 기준을 적용한 작성자 정답 초안이며, 실제 A·B 출력 또는 독립 평가자 합의가 아님.', '',
             '| 영상 구성 | 영상 수 |', '|---|---:|',
             '| VIOLATION 1개 추가 | 35 |', '| OVERCLAIM 1개 추가 | 35 |',
             '| 각각 1개 추가 | 10 |', '| VIOLATION 2개 추가 | 10 |', '| OVERCLAIM 2개 추가 | 10 |', '',
             '제품 수: 1개인 영상 90편, 2개인 영상 10편. DB 제품 110개 중복 없음.',
             '총 삽입 Claim 130개: VIOLATION 65개, OVERCLAIM 65개.', '',
             '원본 Claim은 ETC 제외 후 그대로 보존함. 원본 Claim 전체는 라벨링하지 않았으므로 위 구성은 삽입 수이며 영상 전체의 실제 라벨 수가 아님.', '']
    groups = {a['video_id']:a['group'] for a in assignments}
    for r in labels:
        lines += [f"## {r['video_id']} / {r['claim_id']} / {r['gold_label']}", '',
                  f"영상 그룹: {groups[r['video_id']]}",
                  f"제품: {r['product_name']} / {r['company_name']} / DB ID {r['product_id']}", '',
                  r['claim']['text'], '', '**판정 근거**', '', r['review_note'], '']
        for e in r['evidence']:
            lines += [f"**DB 원문: {e['table']}:{e['product_id']}.{e['column']}**", '']
            lines += ['> '+line for line in e['text'].splitlines()]
            lines += ['']
    (OUT/'review_130_claims.md').write_text('\n'.join(lines),encoding='utf-8')
    (OUT/'README.md').write_text('''# 100개 영상 합성 평가 데이터

## 전달 파일
- `claims_with_db.json`: A·B 판정 입력. 기존 match/DB 구조, claim_type 배열 및 effect 유지. 정답·생성 메모 없음.
- `videos/`: 동일한 입력을 영상별 JSON 100개로 분리한 것. 합본과 중복 실행하지 않음.
- `gold_labels.json`: 추가한 130개 Claim만의 정답 및 DB 근거. 판정 입력에 포함하지 않음.
- `baseline_with_db.json`: 같은 영상·제품·DB에서 합성 Claim을 추가하기 전 상태. 원본 Claim 대비를 위한 파일.
- `source_selected_100.json`: 선택한 원본 100편 전체. title, note, ETC를 포함하여 원본 보존.
- `video_assignments.json`: 영상 그룹·제품 수·삽입 Claim 대응표.
- `product_mapping_audit.json`: 입력 제조사와 DB 업체명을 비교한 제품 연결 기록.
- `review_130_claims.md`: 사람이 검토할 Claim·예상 라벨·제품·DB 원문.
- `summary.json`: 집계 및 검증 범위.

## 구성 및 라벨
1제품 영상 90편, 2제품 영상 10편. 영상 ID/URL 100개 중복 없음.
추가 구성은 V1 35편, O1 35편, V1+O1 10편, V2 10편, O2 10편.
VIOLATION 포함 55편, OVERCLAIM 포함 55편(10편 중복). 추가 Claim은 각 65개씩, 총 130개.
원본 Claim 전체에는 정답을 붙이지 않았으므로, 이 수치는 삽입한 Claim의 수이며 영상 전체 실제 위반·과장 수가 아님.
원본 Claim은 순수 ETC만 제외하고 보존했으며 effect 값도 바꾸지 않음.
추가한 Claim의 effect는 합성 문장에 맞게 새로 작성함. QUANTITY의 effect:null은 의미에 맞는 값임.

## 정답 기준
사용자 승인에 따라 11/04 주간 발표의 VIOLATION/OVERCLAIM 구분을 적용함.
뒤에 받은 구현 PDF 1쪽의 NOT_IN_EVIDENCE=VIOLATION과 상충하는 부분은 적용하지 않음.
VIOLATION은 질병·의약품 주장, 같은 대상의 주의사항 충돌 또는 같은 기준의 등록 값 불일치로 구성함.
균수의 최솟값, 단위·분모가 모호한 질량, 회사 업력은 불일치 정답으로 만들지 않음.
OVERCLAIM은 인정 문장에 없는 구체적인 크기·기간·결과를 과장하되 질병·의약품 주장은 넣지 않음.
DB에 없다는 이유만으로 효과가 실증적으로 거짓이라고 단정하지 않음.
이 정답은 작성자 라벨 초안이다. 최종 고정 전 다른 평가자의 Claim별 검토가 필요함.
NLI의 임시 확률 임계값을 사용해 정답을 역으로 만들지 않았으며 NLI 실행 결과를 보장하지 않음.

## 호환성과 평가 범위
전달 구조는 기존 claim_type_db_format.md와 구현 PDF의 타입별 DB 필드를 재사용함.
현재 입력의 claim_type 배열은 사용자 승인에 따라 보존함. matched 등 새 상태값을 추가하지 않음.
제품은 정규화된 전체 이름과 입력 제조사로 같은 DB 행을 선택할 수 있는 경우만 사용함.
브랜드만으로 제조사를 대체하거나 복수 DB 행 중 임의로 하나를 선택하지 않음.
원본 실제 영상 미디어는 수정하지 않았으므로 영상→추출 전체 파이프라인 평가용이 아닌 Claim→판정 단계 평가용임.
A·B 담당자의 실행 코드는 이 작업 환경에서 확인하지 못했으므로 실제 실행 호환성은 검증하지 않음.
삽입 Claim만 gold가 있으므로 이 파일만으로 원본 전체 Claim의 정밀도·영상 전체 정확도를 계산하지 않음.
평가 키는 (video_id, claim_id). 추가 ID는 원본 c번호의 다음 번호이며 정답을 암시하는 v/o 표기를 넣지 않음.
정답 파일·배정표·파일명·평가 그룹은 예측 특징으로 사용하지 않음.
제품별 개발/평가 분리는 별도로 수행해야 하며 기존 50개 합성 데이터와 제품이 겹칠 수 있음.
''',encoding='utf-8')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def prepare():
    originals = read_json(SOURCE)
    db = sqlite3.connect(DATABASE.resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    identity = [dict(r) for r in db.execute(
        'SELECT product_id, product_name, company_name, manufacturing_report_number FROM products')]
    pairs = {frozenset(company_core(x) for x in pair) for pair in
             read_json(ROOT / 'configs/manufacturer_pairs.json')['pairs']}
    grouping = ProductGroups(identity, pairs)
    names = defaultdict(list)
    for row in identity:
        names[name_key(row['product_name'])].append(row)
    eligible = defaultdict(list)
    rejected = []
    for video in originals:
        n = len(video['products'])
        if n not in {1, 2}:
            continue
        mapped = []
        for original in video['products']:
            candidates = names.get(name_key(original['product_name']), [])
            maker = original.get('manufacturer_name')
            matched = [p for p in candidates if maker and
                       grouping.company(p['company_name']) == grouping.company(maker)]
            keys = {grouping.key(p) for p in matched}
            if len(keys) != 1:
                break
            exact_legal = [p for p in matched if company_core(p['company_name']) == company_core(maker)]
            pool = exact_legal or matched
            if len(pool) != 1:
                break  # No arbitrary selection of version/factory rows.
            row = dict(db.execute('SELECT * FROM products WHERE product_id=?', (pool[0]['product_id'],)).fetchone())
            if not row.get('main_functionality'):
                break
            mapped.append({'input': original, 'row': row, 'candidate_count': len(candidates)})
        if len(mapped) != n:
            rejected.append(video['video_id'])
            continue
        eligible[n].append({'source': video, 'mapped': mapped})
    db.close()
    rng = random.Random(SEED)
    # Ten videos with two distinct products each; keep product-name diversity.
    used_names = set()
    doubles = []
    for item in eligible[2]:
        keys = {name_key(p['row']['product_name']) for p in item['mapped']}
        if len(keys) == 2 and keys.isdisjoint(used_names):
            doubles.append(item)
            used_names.update(keys)
        if len(doubles) == 10:
            break
    assert len(doubles) == 10
    singles = []
    for item in eligible[1]:
        key = name_key(item['mapped'][0]['row']['product_name'])
        if key not in used_names:
            singles.append(item)
            used_names.add(key)
    rng.shuffle(singles)
    assert len(singles) >= 90, len(singles)
    singles = singles[:90]
    rng.shuffle(doubles)
    selections = []
    si = di = 0
    for group, count, two_count in GROUPS:
        chosen = singles[si:si + count - two_count] + doubles[di:di + two_count]
        si += count - two_count
        di += two_count
        for item in chosen:
            item['group'] = group
            selections.append(item)
    selections.sort(key=lambda x: x['source']['video_id'])
    assert len(selections) == len({s['source']['video_id'] for s in selections}) == 100
    assert Counter(len(s['mapped']) for s in selections) == {1: 90, 2: 10}
    assert len({name_key(p['row']['product_name']) for s in selections for p in s['mapped']}) == 110
    return selections, {'eligible_single_videos': len(eligible[1]), 'eligible_double_videos': len(eligible[2]),
                        'rejected_identity_videos': rejected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan-only', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    selections, info = prepare()
    plan = [{'video_id': s['source']['video_id'], 'group': s['group'],
             'products': [{'product_ref': p['input']['product_ref'], **{k: p['row'][k] for k in
                          ['product_id','product_name','company_name','main_functionality','intake_method',
                           'intake_precautions','specification','shelf_life','RAWMTRL_NM','INDIV_RAWMTRL_NM',
                           'ETC_RAWMTRL_NM','CAP_RAWMTRL_NM','RAWMTRL_STD_INFO']}} for p in s['mapped']]}
            for s in selections]
    write_json(OUT / 'selection_plan.json', plan)
    write_json(OUT / 'selection_diagnostics.json', info)
    print(json.dumps({'selected': len(selections), 'groups': dict(Counter(s['group'] for s in selections)),
                      'products_per_video': dict(Counter(len(s['mapped']) for s in selections)),
                      'unique_db_products': len({p['row']['product_id'] for s in selections for p in s['mapped']})}))
    if not args.plan_only:
        summary = compile_dataset(selections, info)
        print(json.dumps(summary, ensure_ascii=True))


if __name__ == '__main__':
    main()
