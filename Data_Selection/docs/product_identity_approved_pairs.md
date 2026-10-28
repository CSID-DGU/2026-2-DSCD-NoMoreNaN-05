# 승인 제조사 PAIR 적용 결과

사용자가 승인한 10개 PAIR를 `configs/manufacturer_pairs.json`에 등록함. 동일 법인이라고 DB를 변경하는 규칙이 아니라 제품명 정확 일치 후보의 제조사 검색용 동등 규칙임. 원본 회사명과 DB는 보존함.

기존 공장 단위 및 공장 표기 정리 연결이 실패한 경우에 적용함. 제품명 정확 일치, 승인 PAIR에 의한 제조사 일치, 신고번호 충돌 없음, 유효 제품 하나일 때 연결함. 여러 신고 기록은 임의로 합치지 않음. 승인 관계를 전이적으로 확대하지 않으며, 제품명 오타와 제조사 PAIR 확장을 동시에 적용하지 않음. 기존 전체 이름 Damerau–Levenshtein 80점 + 같은 정리된 제조사 경로는 유지함.

| 단계 | 연결된 Claim | 연결률 | 미연결 |
|---|---:|---:|---:|
| 최초 결과 | 2,427 | 71.4% | 973 |
| 공장 등 표기 정리 | 2,589 | 76.1% | 811 |
| 승인 PAIR 추가 | 2,655 | 78.1% | 745 |

PAIR로 추가된 영상 내 제품 항목은 4개(영상 4개), Claim 66개임.

| 제품명 | 추가 연결 Claim 수 |
|---|---:|
| 락토핏 솔루션 2 | 11 |
| 시그니처 파이토 이뮨 | 9 |
| 총총 | 19 |
| 콜라겐 히알루론산 앰플샷 | 27 |

공장 표기 정리까지의 기존 2,589개 연결 product_id가 모두 유지됨을 확인함. 제품 식별 관련 회귀 테스트 등 21개 통과함. 연결률은 정답 정확도가 아니며, 영상/제품 동일성에 대한 독립적인 정답 검토는 별도로 필요함. Evidence 검색·임베딩·재순위 평가는 실행하지 않음.

실행:

```powershell
.\.venv\Scripts\python.exe scripts/compare_product_identity_filters.py --approved-pairs configs/manufacturer_pairs.json --output data/processed/product_identity_approved_pairs
```

출력 폴더의 `product_matches.json`에 영상 URL·원본 제품명·입력 제조사·DB product_id·DB 제조사·적용 경로·적용 PAIR를 기록함. `summary.json`은 집계, `new_matches_review.csv`는 최초 결과 대비 신규 연결 검토표임. 기존 Evidence 후보/중단된 추론 결과에는 소급 반영하지 않음.
