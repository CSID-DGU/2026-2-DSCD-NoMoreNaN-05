# 유튜브 광고 후보 URL 추가 수집 — 2026-11-04

기존 `collect_youtube_ads.py` POLICY_VERSION=3의 조건・출력 필드를 그대로 사용함.
검색하지 않은 제품명 99개를 기존 브랜드 제품군 중심으로 나눠 검색함.
제품명이 다른 신규 검색이며 동일 product_key・완료 검색・이미 결과가 있는 제품은 계획 단계에서 제외함.

조건: 영상 60초 이하, 제목/설명에 비교용 제품명 포함.
기존 정책대로 제조사 확인 근거가 있으면 confirmed, 일반명이 아닌 제품의 이름만 확인되면 needs_review,
조건을 통과하지 못하면 rejected. 이 상태는 URL 수집기의 상태이며 제품 DB 매핑/Claim 판정 라벨과 별개임.
유료 광고임을 모두 검증한 영상 목록은 아니며 내용 확인이 필요한 광고 후보임.

## 결과 파일

- `ad_video_urls_all.json`: 기존 + 이번 결과 전체. 기존 출력과 같은 항목 구조.
- `ad_video_urls_added.json`: 이번에 새로 추가된 제품–영상 연결 기록. 이전에 있던 URL이 다른 제품과 연결된 경우도 포함 가능.
- `ad_video_urls_new_urls.json`: 기존 413개 URL에 없었던 영상의 연결 기록만. 한 영상이 여러 제품과 연결되면 여러 행일 수 있음.
- `summary.json`: 신규 URL 수・누적 URL 수・연결 기록 수・완료/미완료 제품 수.
- `manifest.json`: 이번 검색 대상 99개와 입력/기존 결과 해시.
- `collection_report.json`: 이번 검색 대상의 confirmed / needs_review / rejected 집계.
- `baseline_ad_video_urls.json`: 기존 459건, 중복 제외 URL 413개의 원본 보관 사본.
- `collection_before.sqlite`: 추가 수집 전 이어받기 상태 DB의 백업. 팀원 전달용 결과 파일이 아님.

기존 작업 폴더와 Downloads의 ad_video_urls.json은 덮어쓰지 않음.
API 키를 출력・저장하지 않으며 진행 상태는 기존 state/collection.sqlite에 이어 저장함.
일일 수집기 예산(10,000 units, search 100회)과 실행당 API 요청 200회 제한 안에서 실행함.
쿼터 중단 시 같은 명령으로 이어받을 수 있음.

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\continue_youtube_ads.py --run
```

완료된 동일 manifest를 재실행하면 완료 작업/캐시를 재사용함. 새 배치는 별도 폴더와 검색 대상 검토가 필요함.
