# KIPRIS 보조 근거 캐시

DB: `Data_List_Claim_Verification/kipris_evidence_cache.sqlite`

기존 `claim_verification.sqlite`의 식약처 Evidence와 구분되는 특허 후보 저장소다.
특허의 존재나 초록의 표현을 임상적 효능 입증·광고 적합 판정으로 취급하지 않는다.
현재 구현은 원본 적재와 로컬 검색이며, 영상 Claim의 자동 매핑·LLM 판정은 포함하지 않는다.

| 테이블 / 뷰 | 역할 |
|---|---|
| searches | 검색어·조건·수집 시각·전체 건수·완료 상태 |
| patents | 출원번호로 중복을 방지한 발명명칭·초록·출원인·등록 정보·전체 원본 필드 JSON |
| source_pages | 원본 XML 경로·SHA-256·페이지별 건수 |
| search_patents | 검색과 특허, 원본 페이지의 연결 |
| patent_search | 제목·초록의 trigram 검색 인덱스 |
| patent_evidence_candidates | 검색 및 원본 출처를 연결한 보조 근거 후보 조회 뷰 |

관계: `searches → source_pages`, `searches → search_patents ← patents`.
XML은 재작성하지 않고 보존하며 해시·건수·출원번호 중복을 검증한 뒤 트랜잭션으로 적재한다.
같은 조건을 다시 적재하면 해당 검색의 연결을 갱신한다. 이전 특허 레코드는 보존한다.
미완료 수집도 상태를 표시해 적재할 수 있으므로 `searches.status`를 확인해야 한다.
캐시 만료·자동 갱신 정책은 아직 적용하지 않았다.

기존 원본을 DB에 적재:

```powershell
python kipris_cache.py
```

로컬 후보 검색 (API 호출 없음):

```powershell
python kipris_cache.py --search "홍삼" --limit 5
```

Python에서 후보 가져오기:

```python
from kipris_cache import search_candidates
candidates = search_candidates("홍삼", limit=10)
```

명시한 검색어의 API 결과를 수집하고 자동 적재:

```powershell
python collect_kipris.py --word "검색어" --cache-db
```

`.env`의 `KIPRIS_API_KEY`를 사용한다. 기존 원본 페이지가 있으면 재사용하여 이어서 수집하며,
전체 검색 결과 XML을 저장한 뒤(중단 시 저장된 페이지가 있으면 그 범위까지) DB에 적재한다.
이 명령은 대화형 Claim 시스템에 자동 연결되어 있지 않다.
현재 검색은 입력 문구를 제목·초록에서 찾는 문자열 검색이며, 의미 검색이나 효능 판정이 아니다.
짧은 한글 검색어도 처리하고 `%`, `_`를 검색 조건으로 해석하지 않고 문자로 처리한다.
