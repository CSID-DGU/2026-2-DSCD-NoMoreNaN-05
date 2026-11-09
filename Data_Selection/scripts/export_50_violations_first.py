"""Export the user's first synthetic VIOLATION evaluation set."""
import copy
import hashlib
import json
import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'exports/synthetic_negative_claims_20261105/synthetic_negative_claims_50.json'

# Keep one existing example per product; add 40 different products from the input.
KEEP = {1531: 3, 5239: 4, 9378: 1, 12084: 0, 17121: 2,
        24134: 3, 27880: 4, 31064: 0, 40145: 3, 6411: 0}
# Product ID, anchor appearing verbatim in DB, synthetic predicate, mutation type.
EXTRA = [
 (4953, '피부상태 개선', '아토피 피부염을 완치한다.', '질병 치료'),
 (5214, '황반색소밀도', '황반변성을 치료하여 시력을 회복시킨다.', '질병 치료'),
 (5216, '골다공증발생 위험 감소', '골다공증을 치료한다.', '질병 치료'),
 (5247, '철의 흡수', '철결핍성 빈혈 치료제를 대신할 수 있다.', '의약품 대체'),
 (6012, '관절 및 연골 건강', '퇴행성 관절염을 치료한다.', '질병 치료'),
 (6177, '관절 및 연골 건강', '관절염을 완치한다.', '질병 치료'),
 (6181, '관절 및 연골건강', '누구나 관절과 연골 건강이 반드시 개선된다.', '효과 보장·대상 일반화'),
 (6214, '관절 및 연골건강', '관절염 치료약 대신 먹을 수 있다.', '의약품 대체'),
 (6321, '관절 건강', '관절 건강이 반드시 개선된다.', '효과 보장'),
 (6335, '관절 및 연골 건강', '퇴행성 관절염을 완치한다.', '질병 치료'),
 (6407, '관절 및 연골 건강', '관절과 연골 건강이 개선된다.', '효과 단정 — 경계 사례'),
 (6569, '관절건강', '관절염을 치료한다.', '질병 치료'),
 (11268, '황반색소밀도', '황반변성을 치료한다.', '질병 치료'),
 (11946, '배변활동 원활', '누구나 배변활동이 반드시 원활해진다.', '효과 보장·대상 일반화'),
 (11957, '배변활동 원활', '배변활동이 원활해진다.', '효과 단정 — 경계 사례'),
 (12200, '피부 보습', '피부 보습이 반드시 개선된다.', '효과 보장'),
 (12917, '피부 보습', '아토피 피부염을 치료한다.', '질병 치료'),
 (12919, '배변활동 원활', '과민성 대장증후군을 치료한다.', '질병 치료'),
 (13072, '간 건강', '간염을 치료한다.', '질병 치료'),
 (13073, '장 건강', '장 건강이 반드시 개선된다.', '효과 보장'),
 (13079, '식후 혈당상승 억제', '당뇨병 치료제를 대신할 수 있다.', '의약품 대체'),
 (14188, '황반색소 밀도', '황반변성을 완치한다.', '질병 치료'),
 (15498, '수면의 질 개선', '불면증을 치료하며 수면제를 대신할 수 있다.', '질병 치료·의약품 대체'),
 (15681, '식후 혈당 상승 억제', '누구나 식후 혈당상승이 반드시 억제된다.', '효과 보장·대상 일반화'),
 (16234, '근력 개선', '누구나 근력이 반드시 개선된다.', '효과 보장·대상 일반화'),
 (16743, '에너지 생성', '만성피로증후군을 치료한다.', '질병 치료'),
 (16928, '갱년기 여성 건강', '갱년기 여성 건강이 반드시 개선된다.', '효과 보장'),
 (21990, '뼈 건강', '골다공증을 완치한다.', '질병 치료'),
 (22954, '골다공증발생 위험 감소', '골다공증 치료제를 대신할 수 있다.', '의약품 대체'),
 (23433, '정상적인 면역기능', '누구나 감염병을 완벽하게 예방한다.', '질병 예방·효과 보장'),
 (26086, '어린이 키성장', '먹는 모든 어린이의 키가 반드시 큰다.', '효과 보장·대상 일반화'),
 (26136, '어린이 키성장', '어린이의 키가 큰다.', '효과 단정 — 경계 사례'),
 (26245, '정상적인 면역기능', '독감을 예방한다.', '질병 예방'),
 (27092, '어린이 키성장', '성장호르몬 주사를 대신할 수 있다.', '의약품 대체'),
 (27177, '면역기능 개선', '누구나 면역기능이 반드시 개선된다.', '효과 보장·대상 일반화'),
 (31937, '피부 보습', '피부 보습이 개선된다.', '효과 단정 — 경계 사례'),
 (33801, '면역력 증진', '감기를 예방한다.', '질병 예방'),
 (42333, '근육', '근감소증을 치료한다.', '질병 치료'),
 (43407, '혈행개선', '동맥경화증을 치료한다.', '질병 치료'),
 (45403, '갱년기 여성의 건강', '누구나 갱년기 건강이 반드시 개선된다.', '효과 보장·대상 일반화'),
]

# Four user-requested replacements: change the functional target, not only strength.
CROSS_TARGET = {
    17121: ('관절염을 치료한다.', '체지방 감소·콜레스테롤 개선·식후 혈당상승 억제 등', '관절염 치료'),
    6181: ('위염을 치료한다.', '관절 및 연골 건강', '위염 치료'),
    12200: ('당뇨병을 치료한다.', '피부 보습·자외선 관련 피부건강 등', '당뇨병 치료'),
    16234: ('황반변성을 치료한다.', '근력 개선 등', '황반변성 치료'),
}


def apply_cross_target(records):
    changed = []
    for record in records:
        pid = record['product']['product_id']
        if pid not in CROSS_TARGET:
            continue
        predicate, original_scope, target = CROSS_TARGET[pid]
        record['claim']['text'] = record['product']['product_name'] + ' 제품은 ' + predicate
        record['claim']['effect'] = predicate
        record['review_note'] = (
            f'DB 등록 기능성인 {original_scope}에서 다른 대상인 {target} 주장으로 변경함. '
            '단순히 DB에 해당 기능이 없다는 이유만으로 거짓을 확정하는 사례가 아니라, '
            '식품에 대한 질병 치료 주장으로 구성한 사용자 지정 VIOLATION 평가 사례임.'
        )
        changed.append(pid)
    assert set(changed) == set(CROSS_TARGET)
    return records


def build_records(source):
    records = []
    for pid, index in KEEP.items():
        group = [r for r in source if r['product']['product_id'] == pid]
        records.append(copy.deepcopy(group[index]))
    input_path = ROOT / 'data/processed/product_functionality_handoff_y_final_brand_company/source_input.json'
    videos = json.loads(input_path.read_text(encoding='utf-8'))
    by_ref = {(v['video_id'], p['product_ref']): (v, p)
              for v in videos for p in v.get('products', [])}
    audit = json.loads((ROOT / 'exports/claim_type_db_restored_20261104/product_resolution_audit.json').read_text(encoding='utf-8'))
    db = sqlite3.connect((ROOT / 'TRUEAD_DB_보강자료/claim_verification.sqlite').resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    for pid, anchor, predicate, kind in EXTRA:
        product = dict(db.execute('SELECT * FROM products WHERE product_id=?', (pid,)).fetchone())
        assert anchor in product['main_functionality'], (pid, anchor)
        matches = [a for a in audit if a['selected_product_id'] == pid and
                   a['status'] == 'confirmed' and a['company_source'] == 'manufacturer_name']
        assert matches, pid
        refs = []
        for a in matches:
            v, p = by_ref[(a['video_id'], a['product_ref'])]
            refs.append({'video_id': v['video_id'], 'url': v.get('url'),
                         'product': p, 'mapping_reason': a['reason']})
        reason = ('가능성·보조 표현을 생략한 경계 사례. 사용자 지정 평가 라벨이며 문맥 검토가 필요함.'
                  if '경계' in kind else 'DB의 건강 보조·기능성 범위를 질병 예방·치료, 의약품 대체 또는 확실한 효과로 확대함.')
        records.append({'is_synthetic': True,
          'product': {k: product[k] for k in ['product_id','product_name','company_name','manufacturing_report_number']},
          'source_input_references': refs,
          'claim': {'claim_id': '', 'product_ref': 'p01', 'text': product['product_name'] + ' 제품은 ' + predicate,
                    'claim_type': 'EFFECT', 'ingredients': [], 'effect': predicate,
                    'quantity': None, 'intake_basis': None},
          'mutation_type': kind,
          'reference': {'table': 'products', 'product_id': pid, 'column': 'main_functionality',
                        'text': product['main_functionality'], 'anchor': anchor},
          'review_note': reason})
    db.close()
    assert len(records) == len({r['product']['product_id'] for r in records}) == 50
    assert len({r['product']['product_name'] for r in records}) == 50
    for index, record in enumerate(records, 1):
        record['claim']['claim_id'] = f'synthetic_{index:03d}'
    return apply_cross_target(records)


def main():
    original = SOURCE.read_bytes()
    source = json.loads(original)
    records = build_records(source)
    assert len(records) == 50
    for record in records:
        record.pop('mutation_type', None)
        record.pop('label_basis', None)
        record['gold_label'] = 'VIOLATION'
    target = ROOT / '50_violations_first.json'
    if target.exists() and len({r['product']['product_id'] for r in json.loads(target.read_text(encoding='utf-8'))}) != 50:
        backup = ROOT / 'exports/synthetic_negative_claims_20261105/superseded_10products'
        backup.mkdir(parents=True, exist_ok=True)
        for name in ['50_violations_first.json', '50_violations_first.md']:
            old = ROOT / name
            if old.exists():
                shutil.copy2(old, backup / name)
    target.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = [
        '# 50_violations_first', '',
        '서로 다른 제품 50개 / 제품당 합성 Claim 1개 / 정답 라벨: VIOLATION 50개', '',
        '실제 광고 발언이 아닌 평가용 합성 문장임. 원본 광고 JSON과 DB는 수정하지 않음.',
        '정답 라벨은 사용자 요청으로 지정함. 법적 위반이 독립적으로 확정되었다는 의미는 아님.',
        '효과 단정 경계 사례도 사용자 요청에 따라 VIOLATION으로 지정하며 검토 메모를 보존함.',
        'Evidence는 products 테이블의 등록 정보 원문임. 별도 evidence 테이블의 행으로 오인하지 않도록 테이블·컬럼·제품 ID를 함께 기록함.', '',
    ]
    for record in records:
        p, claim, ref = record['product'], record['claim'], record['reference']
        lines += [
            f"## {claim['claim_id']} · VIOLATION", '',
            f"- 제품: {p['product_name']}",
            f"- 회사: {p['company_name']}",
            f"- DB 제품 ID: {p['product_id']}",
            f"- 품목제조신고번호: {p['manufacturing_report_number']}",
            '',
            '**합성 Claim**', '', claim['text'], '',
            f"**DB 근거 — {ref['table']}:{ref['product_id']}.{ref['column']}**", '',
        ]
        lines += ['> ' + line for line in ref['text'].splitlines()]
        lines += ['', '**위반 관련 설명**', '', record['review_note'], '']
    (ROOT / '50_violations_first.md').write_text('\n'.join(lines), encoding='utf-8')
    saved = json.loads(target.read_text(encoding='utf-8'))
    assert len(saved) == 50 and len({r['claim']['claim_id'] for r in saved}) == 50
    assert all(r['gold_label'] == 'VIOLATION' and 'effect' in r['claim'] for r in saved)
    for after in saved:
        assert after['product']['product_id'] == after['reference']['product_id']
        assert after['reference']['text']
    assert SOURCE.read_bytes() == original
    print(json.dumps({'claims': len(saved), 'products': len({r['product']['product_id'] for r in saved}),
                      'VIOLATION': sum(r['gold_label'] == 'VIOLATION' for r in saved),
                      'source_sha256': hashlib.sha256(original).hexdigest(),
                      'files': ['50_violations_first.json', '50_violations_first.md'],
                      'one_claim_per_product': True, 'source_file_unchanged': True}, ensure_ascii=True))


if __name__ == '__main__':
    main()
