"""Export assistant-reviewed reference labels without changing product/DB routing.

The decisions are recorded explicitly in review configs after reading all baseline
claims. This is not a trained classifier, an NLI prediction, or legal adjudication.
"""
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.claim_type_db_format import TYPE_FIELDS, ARRAYS, db_sections

BASE = ROOT / 'exports/synthetic_video_eval_100_20261105'
OUT = ROOT / 'exports/eval100_all_claims_labeled_20261105'
LABELS = {'SUPPORTED','VIOLATION','OVERCLAIM','UNCLEAR','OUT_OF_SCOPE','DISCLAIMER'}
REVIEWS = [ROOT/'configs'/name for name in [
    'eval100_manual_review_20261105.json',
    'eval100_review_batch5_20261105.json',
    'eval100_review_batch6_20261105.json']]
FINAL_REVIEW = ROOT/'configs/eval100_review_final_overrides_20261105.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expand(value):
    result = set()
    for part in value.split(','):
        if not part.strip():
            continue
        if '-' in part:
            low, high = map(int, part.split('-'))
            result.update(range(low, high+1))
        else:
            result.add(int(part))
    return result


def manual_decisions():
    explicit, notes, reviewed = {}, {}, set()
    for path in REVIEWS:
        review = load(path)
        for low, high in review['reviewed_ranges']:
            reviewed.update(range(low, high+1))
        for label in LABELS-{'UNCLEAR'}:
            for index in expand(review.get(label, '')):
                assert index not in explicit or explicit[index] == label, (index, label)
                explicit[index] = label
        notes.update({int(k):v for k,v in review['UNCLEAR_reason_overrides'].items()})
    assert reviewed == set(range(1,1425))
    decisions = {i:(explicit.get(i,'UNCLEAR'), notes.get(i)) for i in reviewed}
    final = load(FINAL_REVIEW)
    for index, decision in final['decisions'].items():
        decisions[int(index)] = tuple(decision)
    return decisions, final['external_references']


def evidence_for(product, claim, label):
    db = product['DB']
    fields = []
    types = claim['claim_type']
    if 'EFFECT' in types:
        fields += [('EFFECT',f) for f in TYPE_FIELDS['EFFECT']]
    if 'QUANTITY' in types:
        fields += [('QUANTITY',f) for f in ['BASE_STANDARD','SRV_USE','DISTB_PD','PRDT_SHAP_CD_NM']]
    if 'COMPOSITION' in types:
        fields += [('COMPOSITION',f) for f in ['RAWMTRL_NM','INDIV_RAWMTRL_NM','ETC_RAWMTRL_NM','CAP_RAWMTRL_NM','BASE_STANDARD','RAWMTRL_DICT_INFO']]
    if 'CERTIFICATION' in types:
        fields += [('CERTIFICATION',f) for f in ['STTEMNT_NO','PRMS_DT','INDUTY_CD_NM','MAIN_FNCTN','RAWMTRL_STD_INFO','RAWMTRL_CLASS_INFO']]
    if label in {'OUT_OF_SCOPE','DISCLAIMER'}:
        return []  # Text/scope decision; DB values do not prove endorsements etc.
    seen = set()
    result = []
    for kind, field in fields:
        path = (kind,field)
        if path in seen:
            continue
        seen.add(path)
        result.append({'product_ref':product['product_ref'],
                       'path':f'products[{product["product_ref"]}].DB.{kind}.{field}',
                       'value':copy.deepcopy(db[kind][field])})
    return result


def fallback_note(claim, label):
    text, kinds = claim['text'], claim['claim_type']
    if label == 'SUPPORTED':
        if 'QUANTITY' in kinds:
            return '문장의 구체적인 수치·섭취 기준 또는 함께 열거된 성분·기능을 해당 제품의 규격·섭취 방법과 대조하여 부합으로 판단함.'
        if 'EFFECT' in kinds:
            return '원문의 건강 효과가 같은 제품의 공식 기능성 범위에 대응하며 질병 치료·별도 수치 보장이 없어 부합으로 판단함.'
        if 'COMPOSITION' in kinds:
            return '해당 제품의 기능성 원료·기타 원재료·캡슐 원재료·규격을 함께 보고 명시 성분이 대응하는 것으로 판단함. 표기·번역 차이는 의미를 확인함.'
        return '해당 제품의 신고·인정 정보로 주장 내용을 확인함. GMP는 업종을 이용한 간접 확인이며 개별 인증 유효기간의 직접 증명은 아님.'
    if label == 'DISCLAIMER':
        return '효능을 새로 보장하는 문장이 아닌 시험의 적용 한계·주의·면책 안내임.'
    if label == 'OUT_OF_SCOPE':
        return '가격·판매·배송·시험 조건·출처·전문가·광고 구호 등 승인된 현재 검증 범위 밖의 내용으로 판단함.'
    if label == 'VIOLATION':
        return '입력 원문에서 식품을 의약품으로 인식하게 하는 표현·치료 주장 또는 같은 기준의 등록 정보와 명확한 충돌을 확인함. 실제 영상이나 법적 위반 확정은 별개임.'
    if label == 'OVERCLAIM':
        return '구체적 기능을 보장·일반화하지만 그 범위가 공식 기능성으로 뒷받침되지 않음. 단순 키워드 검출만으로 정답을 붙이지 않음.'
    if re.search(r'최초|유일|최대|최고|증량|늘어난|더하고|높이고|낮추고',text):
        return '비교 대상·과거 규격·전체 제품 범위 또는 고시 기준이 없어 상대적·최초성 주장을 확정할 수 없음.'
    if re.search(r'인체|시험|연구|통증|WOMAC|배합',text):
        return '등록 기능성·원료 정보는 있어도 특정 시험 결과·구체적 효과·배합 조건까지 입증할 원문 자료가 부족함.'
    if re.search(r'산|유래|식물성|DSM|순도|PURE|기술|배지|원료 선별',text):
        return '원료의 출처·순도·제조·공정 또는 비교 특성을 등록 성분명만으로 모두 입증할 수 없음.'
    if 'QUANTITY' in kinds:
        return '수치의 대상·분모·단위·기준치·집계 범위가 불명확하거나 해당 실함량이 전달 DB에 없어 전체 주장을 확정하지 않음.'
    if 'COMPOSITION' in kinds:
        return '상위 범주·상표·혼합 성분·원료 출처 또는 불특정 성분 설명으로 전체 원재료와 일대일 대조를 확정하기 어려움.'
    if '?' in text or '죠?' in text:
        return '질문형이거나 구체적 효과·대상이 명시되지 않아 인정 기능성과의 대응을 확정하기 어려움.'
    return '제품 관련 자료는 있지만 원문의 구체적인 효과·대상·보장 범위를 공식 기능성만으로 확정하기 어려움.'


def main():
    input_path = BASE/'claims_with_db.json'
    index_path = BASE/'baseline_review_index.json'
    preserved = {p:digest(p) for p in [input_path,index_path,BASE/'gold_labels.json',BASE/'source_selected_100.json']}
    original = load(input_path)
    labeled = copy.deepcopy(original)
    baseline_index = load(index_path)
    synth = {(r['video_id'],r['claim_id']):r for r in load(BASE/'gold_labels.json')}
    index = {(r['video_id'],r['claim']['claim_id']):r for r in baseline_index}
    assert len(index) == 1424 and len(synth) == 130 and not set(index)&set(synth)
    decisions, external_refs = manual_decisions()
    assignments = load(BASE/'product_mapping_audit.json')
    product_ids = {(r['video_id'],r['product_ref']):r['product_id'] for r in assignments}
    notes, counts, baseline_counts, synth_counts = [], Counter(), Counter(), Counter()
    for video in labeled:
        products = {p['product_ref']:p for p in video['products']}
        for claim in video['claims']:
            key = (video['video_id'],claim['claim_id'])
            product = products[claim['product_ref']]
            assert product['match']['status'] == 'confirmed' and product['DB'] is not None
            if key in synth:
                label = synth[key]['gold_label']
                note = synth[key]['review_note']
                source_kind = 'synthetic'
                review_index = None
                synth_counts[label] += 1
            else:
                row = index[key]
                assert row['claim'] == claim
                review_index = row['review_index']
                label, note = decisions[review_index]
                source_kind = 'original'
                baseline_counts[label] += 1
            assert label in LABELS
            note = note or fallback_note(claim,label)
            claim['gold_label'] = label  # Only user-requested addition to transport.
            counts[label] += 1
            entry = {'video_id':video['video_id'],'claim_id':claim['claim_id'],
                     'product_ref':claim['product_ref'],'product_id':product_ids[(video['video_id'],claim['product_ref'])],
                     'product_name':product['match']['matched_name'],'company_name':product['match']['matched_company'],
                     'claim':copy.deepcopy(claim),'gold_label':label,'review_note':note,
                     'evidence':evidence_for(product,claim,label),
                     'source_kind':source_kind,'baseline_review_index':review_index}
            if review_index in {18,21,295,296,297,298}:
                entry['external_reference'] = external_refs['daily_values']
            if review_index == 556:
                entry['external_reference'] = external_refs['vitamin_D_units']
            notes.append(entry)
    effect_null = [{'video_id':v['video_id'],'claim_id':c['claim_id'],'product_ref':c['product_ref'],
                    'text':c['text'],'claim_type':c['claim_type'],'gold_label':c['gold_label']}
                   for v in labeled for c in v['claims'] if 'EFFECT' in c['claim_type'] and c['effect'] is None]
    OUT.mkdir(parents=True,exist_ok=True)
    # Confirm that the only inference-schema addition is claims[].gold_label.
    restored = copy.deepcopy(labeled)
    for video in restored:
        for claim in video['claims']:
            claim.pop('gold_label')
    assert restored == original
    assert sum(counts.values()) == 1554 and sum(baseline_counts.values()) == 1424
    assert synth_counts == {'VIOLATION':65,'OVERCLAIM':65}
    assert len({(r['video_id'],r['claim_id']) for r in notes}) == 1554
    db = sqlite3.connect((ROOT/'TRUEAD_DB_보강자료/claim_verification.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
    db.row_factory = sqlite3.Row
    checked = 0
    for video in original:
        for product in video['products']:
            pid = product_ids[(video['video_id'],product['product_ref'])]
            row = dict(db.execute('SELECT * FROM products WHERE product_id=?',(pid,)).fetchone())
            assert db_sections(row) == product['DB']
            assert product['match']['method'] in {'name_and_company','report_number'}
            assert 'candidate_products' not in product
            for kind,fields in TYPE_FIELDS.items():
                assert list(product['DB'][kind]) == fields
                for field in fields:
                    assert isinstance(product['DB'][kind][field],list if field in ARRAYS else str)
            checked += 1
    db.close()
    save(OUT/'claims_with_db_labeled.json',labeled)
    save(OUT/'gold_labels_all_1554.json',notes)
    save(OUT/'original_EFFECT_null_values.json',effect_null)
    # A/B prediction input remains byte-identical and contains no answers.
    shutil.copy2(input_path,OUT/'claims_with_db.json')
    selected_two = [v for v in labeled if len(v['products'])==2]
    save(OUT/'two_product_videos_10_labeled.json',selected_two)
    for folder, data in [('videos_labeled',labeled),('videos_input',original)]:
        directory = OUT/folder
        directory.mkdir(exist_ok=True)
        for video in data:
            assert re.fullmatch(r'[A-Za-z0-9_.-]+',video['video_id'])
            save(directory/(video['video_id']+'.json'),video)
    documents = [
        Path(r'C:\Users\박이정\Documents\카카오톡 받은 파일\claim_type_db_format.md'),
        Path(r'C:\Users\박이정\Documents\카카오톡 받은 파일\db_enrichment_guide.md'),
        Path(r'C:\Users\박이정\Downloads\88393774-9dec-4713-92df-effb9b79df46_매커니즘A_Claim_Type별_구현.pdf'),
        Path(r'C:\Users\박이정\Downloads\3e195a0d-0d85-4b8a-ab3e-e41326a26d6a_1104_10주차_주간_발표.pdf')]
    validation = {'schema_addition':'claims[].gold_label only, explicitly requested by user',
                  'reviewed_documents':[{'path':str(p),'sha256':digest(p)} for p in documents],
                  'claim_type_array_user_approved':True,'effect_preserved_for_all_claims':1554,
                  'EFFECT_claims_with_original_null_effect':len(effect_null),
                  'null_effect_text_fallback_consumer_verified':False,
                  'all_original_fields_and_values_preserved':restored==original,
                  'product_DB_verified_against_SQLite':checked,
                  'product_entries':110,'DB_non_null':110,'DB_null':0,
                  'status_counts':dict(Counter(p['match']['status'] for v in original for p in v['products'])),
                  'candidate_products_required':False,'actual_consumer_runtime_tested':False,
                  'label_assignment_method':'assistant reviewed baseline text and product DB, with recorded per-index decisions; no NLI prediction or automatic regex classifier used as gold',
                  'independent_annotator_agreement_measured':False,
                  'source_files_unchanged':all(digest(p)==h for p,h in preserved.items()),
                  'external_numeric_references':external_refs}
    assert validation['source_files_unchanged']
    save(OUT/'interface_validation.json',validation)
    summary = {'videos':100,'product_counts':{'one_product_videos':90,'two_product_videos':10},
               'product_entries':110,'all_products_confirmed_and_DB_non_null':110,
               'total_claims':1554,'original_claims':1424,'synthetic_claims':130,
               'labels_all':{label:counts[label] for label in sorted(LABELS)},
               'labels_original':{label:baseline_counts[label] for label in sorted(LABELS)},
               'labels_synthetic':dict(synth_counts),'labeled_claim_count':len(notes),
               'EFFECT_claims_with_original_null_effect':len(effect_null),
               'label_source':'assistant reference annotations, not independent human consensus or legal determinations',
               'input_sha256':digest(input_path),'labeled_output_sha256':digest(OUT/'claims_with_db_labeled.json')}
    save(OUT/'summary.json',summary)
    write_readme(summary)
    review = ['# 전체 Claim 정답 검토표', '', '| 영상 | Claim | 제품 | 라벨 | 원문 | 판단 이유 |', '|---|---|---|---|---|---|']
    esc = lambda x:str(x).replace('|','\\|').replace('\n',' ')
    for row in notes:
        review.append('| '+' | '.join(esc(x) for x in [row['video_id'],row['claim_id'],row['product_name'],row['gold_label'],row['claim']['text'],row['review_note']])+' |')
    (OUT/'review_all_claims.md').write_text('\n'.join(review)+'\n',encoding='utf-8')
    with zipfile.ZipFile(OUT/'handoff_labeled_100.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.write(OUT/'claims_with_db_labeled.json','claims_with_db_labeled.json')
        z.write(OUT/'summary.json','summary.json')
        z.write(OUT/'README.md','README.md')
    with zipfile.ZipFile(OUT/'handoff_A_B_input_100.zip','w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted((OUT/'videos_input').glob('*.json')):
            z.write(path,'videos/'+path.name)
    print(json.dumps(summary,ensure_ascii=True))


def write_readme(summary):
    lines = ['# 100편 전체 Claim 정답 라벨 및 전달 형식', '',
             '## 사용할 파일',
             '- claims_with_db_labeled.json: 전체 1554개 Claim에 gold_label을 추가한 평가 정답 합본.',
             '- claims_with_db.json: 정답을 보지 않고 A·B를 실행할 입력. 앞서 전달한 입력과 바이트 단위로 동일함.',
             '- gold_labels_all_1554.json: (video_id, claim_id)별 정답·제품·DB 근거·review_note.',
             '- two_product_videos_10_labeled.json: 제품 2개 영상 10편의 전체 필드와 정답.',
             '- videos_labeled / videos_input: 동일 데이터를 영상별 100개로 분리. 합본과 중복 실행하지 않음.',
             '- handoff_labeled_100.zip: 라벨 포함 합본. handoff_A_B_input_100.zip: 정답 없는 영상별 판정 입력.', '',
             '## 인터페이스',
             '기존 root video_id/url/db_version/products/claims 유지. 제품 원본 필드 + match + DB 유지.',
             'confirmed/unresolved/not_found 의미와 report_number/name_and_company 값을 변경하지 않음.',
             '이번 110개 제품은 기존 선정 단계부터 모두 confirmed이며 DB가 채워져 있음. 후보 성공을 확정으로 승격한 것이 아님.',
             'products[].DB만으로 모든 선정 제품의 타입별 근거를 읽을 수 있음. candidate_products 또는 matched 상태는 없음.',
             'claim_type 배열은 사용자가 수신 측 처리 가능을 확인한 형식을 유지함.',
             'effect를 포함한 원본 8개 Claim 필드는 값까지 유지하며, 라벨 파일에는 요청한 gold_label 하나만 추가함.',
             'EFFECT Claim 중 원본 effect:null인 87개도 값을 임의로 생성하지 않고 그대로 보존함. original_EFFECT_null_values.json에서 목록을 확인할 수 있음.',
             '수신 B가 effect 값만 사용하면 이 87개가 누락될 수 있음. 요구사항의 Claim 원문인 text를 이용하는지 수신 측 확인이 필요함.',
             'DB 중 RAWMTRL_STD_INFO/RAWMTRL_DICT_INFO/RAWMTRL_CLASS_INFO는 배열, 나머지는 문자열을 유지함.',
             '추가 금지 상태를 회피하려고 unresolved에 후보 DB를 넣거나 임의 제품을 확정하지 않음.', '',
             '## 라벨링 범위와 해석',
             'ETC 제외 후 기존 1424개 + 합성 130개, 총 1554개를 승인된 여섯 라벨로 판단함.',
             '주간 발표 및 사용자가 승인한 기준표를 적용함. 구현 PDF 1쪽의 근거 없는 효능=VIOLATION은 적용하지 않음.',
             '근거 없는 효능은 과장까지 있으면 OVERCLAIM, 아니면 UNCLEAR. 질병·의약품 또는 명확한 DB 충돌은 VIOLATION.',
             '원본의 잘못된 product_ref·계열 제품 혼합·제품 버전 가능성은 다른 제품 자료를 대신 쓰지 않고 UNCLEAR로 남김.',
             '복합 문장의 확인 가능한 부분만 보고 전체를 SUPPORTED로 처리하지 않음. 미확인 핵심 주장이 남으면 UNCLEAR.',
             '숫자 차이는 같은 단위·기준량인지 확인하며 균수 최소 규격·포장량·원료 인정량을 제품 실함량과 혼동하지 않음.',
             '최종 사용자 승인 기준표를 우선하여 포장 규격·총량·개수 및 상표·독자 배합명은 UNCLEAR로 처리함. 구현 PDF 일부의 OUT_OF_SCOPE 분류와 구분함.',
             'GMP는 문서에 따른 업종 간접 확인. 인허가일을 회사 설립일 또는 브랜드 업력으로 사용하지 않음.',
             '전부 assistant가 작성한 평가 정답 초안이며 독립된 사람 간 합의나 법적 확정이 아님.',
             'NLI 점수나 A·B 출력을 정답으로 쓰지 않았고 실제 A·B 수신 프로그램 실행은 검증하지 못함.',
             '원본 영상 미디어를 보지 않고 전달된 Claim 원문·제품 DB를 비교했으므로 원본 추출 오류를 확정 교정하지 않음.',
             '주간 발표의 집계/모델 확률과 비교하는 평가이지, 이 정답을 모델 예측 특징으로 전달하지 않음.', '',
             '## 라벨 개수', '| 라벨 | 전체 | 기존 | 합성 |', '|---|---:|---:|---:|']
    for label in sorted(LABELS):
        lines.append(f"| {label} | {summary['labels_all'][label]} | {summary['labels_original'][label]} | {summary['labels_synthetic'].get(label,0)} |")
    lines += ['', '## 보조 수치 자료',
              '별표5 기준치 참고: https://www.law.go.kr/flDownload.do?bylClsCd=110201&flSeq=136815111&gubun=',
              '비타민D 단위 환산 참고: https://ods.od.nih.gov/factsheets/Vitamind-HealthProfessional/',
              '이 외부 자료는 평가 메모의 단위·비율 검산에만 쓰며 기존 DB 필드에는 추가하지 않음.']
    (OUT/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
