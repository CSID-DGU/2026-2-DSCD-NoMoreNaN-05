"""Create a separate synthetic evaluation draft; never modify source/handoff data."""
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'exports/synthetic_negative_claims_20261105'
SOURCE = ROOT / 'data/processed/product_functionality_handoff_y_final_brand_company/source_input.json'
AUDIT = ROOT / 'exports/claim_type_db_restored_20261104/product_resolution_audit.json'
DB = ROOT / 'TRUEAD_DB_보강자료/claim_verification.sqlite'

# ID, related effect (not a quotation), disease claim, guaranteed claim,
# quantity claim, exact quantity anchor, last claim, anchor field, anchor, reason.
CASES = [
 (1531, '식후 혈당상승 억제', '당뇨병을 치료한다.', '누구나 식후 혈당상승이 반드시 억제된다.',
  '500mg당 코로솔산 표시량은 13mg이다.', '1.3mg/500mg',
  '등록된 섭취 방법은 하루 1회, 한 번에 3정이다.', 'intake_method', '1일 1회, 1회 1정', '등록 섭취량 1정을 3정으로 변경함.'),
 (5239, '높은 혈압 감소', '고혈압약을 대신하여 고혈압을 치료한다.', '누구나 높은 혈압이 반드시 감소한다.',
  '0.25g당 코엔자임Q10 표시량은 200mg이다.', '100 mg/0.25g',
  '수유부도 섭취를 피할 필요 없이 안심하고 먹을 수 있다.', 'intake_precautions', '수유부는 섭취를 피할 것', '섭취 회피 대상을 안전한 대상으로 바꿈.'),
 (9378, '체지방 감소', '비만을 치료하는 의약품이다.', '누구나 체지방이 반드시 감소한다.',
  '0.8g당 프로바이오틱스 수의 표시량은 1,000억 CFU이다.', '10,000,000,000(100억) CFU/0.8g',
  '등록된 섭취 방법은 하루 1회, 한 번에 6캡슐이다.', 'intake_method', '1일 1회, 1회 2캡슐', '등록 섭취량 2캡슐을 6캡슐로 변경함.'),
 (12084, '배변활동 개선', '궤양성 대장염을 치료한다.', '누구나 배변활동이 반드시 원활해진다.',
  '4,400mg당 프로바이오틱스 수의 표시량은 4조 5,000억 CFU이다.', '450,000,000,000 CFU/4,400 mg',
  '질환이 있거나 의약품을 복용해도 전문가 상담 없이 섭취해도 된다.', 'intake_precautions', '질환이 있거나 의약품 복용 시 전문가와 상담', '전문가 상담 조건을 불필요하다고 바꿈.'),
 (17121, '체지방 감소', '당뇨병과 고지혈증을 치료한다.', '누구나 체지방이 반드시 감소한다.',
  '680mg당 카테킨 표시량은 500mg이다.', '360mg/680mg',
  '어린이와 임산부도 섭취를 피할 필요가 없다.', 'intake_precautions', '어린이, 임산부 및 수유부는 섭취를 피할 것', '섭취 회피 조건을 반대로 변경함.'),
 (24134, '체지방 감소', '비만 치료제를 대신해 비만을 치료한다.', '누구나 체지방이 반드시 감소한다.',
  '700mg당 비타민C 표시량은 500mg이다.', '100 mg/700 mg',
  '등록된 섭취 방법은 하루 1회, 한 번에 4정이다.', 'intake_method', '1일 1회, 1회 1정', '등록 섭취량 1정을 4정으로 변경함.'),
 (27880, '피부 보습 개선', '아토피 피부염을 치료한다.', '누구나 피부 보습이 반드시 개선된다.',
  '1,500mg당 비오틴 표시량은 10,000μg이다.', '1000ug/1500mg',
  '영유아와 어린이도 섭취를 피할 필요 없이 먹을 수 있다.', 'intake_precautions', '영·유아, 어린이, 임산부 및 수유부는 섭취를 피할 것', '섭취 회피 대상에게 섭취를 권장함.'),
 (31064, '위 불편감 개선', '위염과 위궤양을 치료한다.', '누구나 위 불편감이 반드시 개선된다.',
  '3g당 Oleanonic acid 표시량은 215.67mg이다.', '107.835mg/3g',
  '등록된 섭취 방법은 하루 1회, 한 번에 3포이다.', 'intake_method', '1일 1회, 1회 1포', '등록 섭취량 1포를 3포로 변경함.'),
 (40145, '혈행 개선', '혈전증을 치료하며 항응고제를 대신할 수 있다.', '누구나 혈행이 반드시 개선된다.',
  '0.9g당 EPA와 DHA 합계 표시량은 800mg이다.', '600 mg/0.9g',
  '항응고제를 복용해도 전문가 상담 없이 섭취해도 된다.', 'intake_precautions', '항응고제, 항혈소판제, 혈압강하제', '의약품 복용자의 전문가 상담 조건을 제거함.'),
 (6411, '관절 및 연골 건강 개선', '퇴행성 관절염을 완치한다.', '누구나 관절 및 연골 건강이 반드시 개선된다.',
  '0.72g당 비타민D 표시량은 100μg이다.', '10 ㎍/0.72g',
  '임산부와 수유부도 섭취를 피할 필요 없이 먹을 수 있다.', 'intake_precautions', '영·유아, 어린이, 임산부 및 수유부는 섭취를 피할 것', '섭취 회피 조건을 반대로 변경함.'),
]

PLAIN = {
 1531: '식후 혈당상승이 억제된다.', 5239: '높은 혈압이 감소한다.',
 9378: '체지방이 감소한다.', 12084: '배변활동이 원활해진다.',
 17121: '체지방이 감소한다.', 24134: '체지방이 감소한다.',
 27880: '피부 보습이 개선된다.', 31064: '위 불편감이 개선된다.',
 40145: '혈행이 개선된다.', 6411: '관절 및 연골 건강이 개선된다.',
}


def main():
    source_bytes = SOURCE.read_bytes()
    videos = json.loads(source_bytes)
    source_by_ref = {(v['video_id'], p['product_ref']): (v, p)
                     for v in videos for p in v.get('products', [])}
    audit = json.loads(AUDIT.read_text(encoding='utf-8'))
    connection = sqlite3.connect(DB.resolve().as_uri() + '?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    records = []
    for pid, effect, disease, guarantee, quantity, quantity_anchor, last, last_field, last_anchor, last_reason in CASES:
        product = dict(connection.execute('SELECT * FROM products WHERE product_id=?', (pid,)).fetchone())
        matches = [a for a in audit if a['selected_product_id'] == pid
                   and a['status'] == 'confirmed' and a['company_source'] == 'manufacturer_name']
        assert matches, (pid, 'No manufacturer-based connection in source audit')
        refs = []
        for match in matches:
            video, p = source_by_ref[(match['video_id'], match['product_ref'])]
            assert p.get('manufacturer_name')
            refs.append({'video_id': video['video_id'], 'url': video.get('url'),
                         'product': p, 'mapping_reason': match['reason']})
        assert quantity_anchor in product['specification']
        assert last_anchor in product[last_field]
        variants = [
          ('disease', '질병 치료·의약품 대체', disease, 'EFFECT', 'main_functionality', None,
           '인정 기능성의 보조적 건강 효과를 질병 치료 또는 의약품 대체 주장으로 변경함.'),
          ('plain', '효과 단정 — 경계 사례', PLAIN[pid], 'EFFECT', 'main_functionality', None,
           '가능성·보조 표현을 생략함. 이 표현만으로 위반을 확정하지 않고 문맥과 판정 기준으로 검토해야 함.'),
          ('guarantee', '효과 보장·대상 일반화', guarantee, 'EFFECT', 'main_functionality', None,
           '가능성·보조 범위를 모든 사람에 대한 확실한 효과로 확대함. 실패 확률 등 실제 시험 결과를 뜻하지 않음.'),
          ('quantity', '표시량 변경', quantity, 'QUANTITY', 'specification', quantity_anchor,
           '제품 규격의 표시량을 변경함. 실제 로트 측정값이 아니라 DB 등록 표시량과의 비교 사례임.'),
          ('last', '섭취 방법 변경' if last_field == 'intake_method' else '주의사항 반전',
           last, 'QUANTITY' if last_field == 'intake_method' else 'EFFECT', last_field, last_anchor, last_reason),
        ]
        for kind, mutation_type, text, claim_type, field, anchor, reason in variants:
            cid = f'synthetic_{len(records)+1:03d}'
            claim = {'claim_id': cid, 'product_ref': 'p01',
                     'text': f"{product['product_name']} 제품은 {text}",
                     'claim_type': claim_type, 'ingredients': [],
                     'effect': effect if claim_type == 'EFFECT' else None,
                     'quantity': text if claim_type == 'QUANTITY' else None,
                     'intake_basis': '제품 등록 표시량 기준' if kind == 'quantity' else
                                     '제품 등록 섭취 방법 기준' if last_field == 'intake_method' and kind == 'last' else None}
            records.append({'is_synthetic': True, 'product': {k: product[k] for k in
                            ['product_id', 'product_name', 'company_name', 'manufacturing_report_number']},
                            'source_input_references': refs, 'claim': claim,
                            'mutation_type': mutation_type,
                            'reference': {'table': 'products', 'product_id': pid, 'column': field,
                                          'text': product[field], 'anchor': anchor},
                            'review_note': reason})
    connection.close()
    assert len(records) == 50
    assert len({r['claim']['text'] for r in records}) == 50
    assert all(r['is_synthetic'] and r['reference']['text'] for r in records)
    assert SOURCE.read_bytes() == source_bytes
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / 'synthetic_negative_claims_50.json'
    output.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    assert json.loads(output.read_text(encoding='utf-8')) == records
    lines = ['# DB 근거 기반 합성 Claim 50개', '',
             '평가용으로 새로 작성한 문장임. 실제 광고에서 추출된 발언이나 해당 업체의 광고 사실을 의미하지 않음.', '',
             '용빈님 원본 JSON에 등장하며, 기존 연결 감사 자료에서 입력 제조사 기반으로 연결된 10개 DB 제품을 사용함.',
             '기존 DB·입력 JSON·전달용 JSON·매핑 및 판정 기준은 변경하지 않음.',
             '판정 라벨은 부여하지 않음. 특히 효과 단정 10개는 문맥 검토가 필요한 경계 사례임.',
             'Claim의 effect 등은 합성 문장에 맞춰 새로 작성한 값이며 원본 추출값을 수정한 것이 아님.',
             '주의사항은 별도 claim_type을 추가하지 않고 기존 EFFECT로 표현함. 수신 판정기의 주의사항 참조 여부는 별도 확인이 필요함.', '',]
    for pid, *_ in CASES:
        group = [r for r in records if r['product']['product_id'] == pid]
        p = group[0]['product']
        lines += [f"## {p['product_name']}", '',
                  f"DB 제품 ID: {pid} / 회사: {p['company_name']} / 신고번호: {p['manufacturing_report_number']}", '']
        for r in group:
            lines += [f"### {r['claim']['claim_id']} · {r['mutation_type']}", '', r['claim']['text'], '',
                      f"- 기준: products:{pid}.{r['reference']['column']}",
                      '- DB 원문: ' + r['reference']['text'].replace('\n', ' / '),
                      '- 변경·검토 사항: ' + r['review_note'], '']
    (OUT / 'synthetic_negative_claims_50.md').write_text('\n'.join(lines), encoding='utf-8')
    summary = {'claim_count': len(records), 'product_count': len(CASES),
               'mutation_counts': dict(Counter(r['mutation_type'] for r in records)),
               'source_input': str(SOURCE.relative_to(ROOT)),
               'source_input_sha256': hashlib.sha256(source_bytes).hexdigest(),
               'database': str(DB.relative_to(ROOT)), 'labels_assigned': False,
               'boundary_case_count': 10, 'actual_advertising_statements': False}
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=True))


if __name__ == '__main__':
    main()
