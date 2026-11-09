# 2026-11-04 보수적 1차 분류

이 결과는 사용자 제공 메커니즘 A PDF를 기준으로 한 오프라인 규칙 분류이며,
GPT/NLI로 전체 문장을 판정한 결과나 정답 라벨이 아님.
VIOLATION/OVERCLAIM을 확정하는 의미·수치 검토는 수행하지 않았으며 해당 0건은 위반·과장이 없다는 뜻이 아님.
직접 확인되지 않은 주장은 UNCLEAR에 포함되므로 의미 검토 후 분포가 달라질 수 있음.

- 기존 claims_with_db.json: 8,728개. ETC 1,241개도 실제로 포함돼 있었음.
- 이 사본에서만 ETC를 제외하여 7,487개를 분류함.
- PERSON_CREDENTIAL 52개는 PDF 기준 OUT_OF_SCOPE.
- PDF 본문의 GMP 처리 기준은 서로 충돌하므로 2쪽의 범위표를 따라 OUT_OF_SCOPE로 적용함.
- 면책 문구·범위 밖 항목을 먼저 분류하고 나머지는 제품 참조/confirmed 상태를 확인함.
- 기존 점검에서 제조사 충돌 9건·제조사 미확인 44건의 제품 항목을 판정 보류함.
  제조사 미확인 자체가 항상 잘못된 제품이라는 뜻은 아니며 이 결과의 보수적 처리 방침임.
- SUPPORTED는 등록번호 존재와 순수 등록 주장, 전체 원료 토큰의 직접 일치,
  인정 기능성 원문과의 직접 일치, 완전 일치 섭취 문구만 허용함.
- DB 근거가 없거나 의역/수치 검토가 필요한 주장은 UNCLEAR. DB에 없다는 이유로 VIOLATION으로 판단하지 않음.
- 부분/복합 문장의 오분류가 있을 수 있어 최종 판정 또는 평가 정답으로 사용하면 안 됨.

## 파일

- summary.json: 라벨별 통계, 세부 사유, 적용 방식.
- claims_without_etc.json: ETC만 제외한 새 전달 형식. 별도 판정 정보는 넣지 않음.
- claims_labeled_preliminary.json: Claim별 preliminary_assessment(라벨·사유·근거) 추가.
- labels_flat.json: 영상 ID와 Claim별 결과를 평탄화한 검토용 파일.
- excluded_etc.json: 제외한 ETC의 원문/영상 ID 기록.

원본 전달 JSON과 DB는 수정하지 않으며 원래 Claim의 effect를 포함한 모든 필드를 보존함.
외부 API 호출·제품 재매핑·DB 재보강·GitHub 업로드는 수행하지 않음.
