# TRUEAD — 1차 MVP 데이터 수집 준비

## GitHub 작업 기록·데이터 복원

최신 제품 매핑 코드·전달 JSON·SQLite·PostgreSQL 백업은 [GitHub 백업 안내](docs/github_workspace_backup.md)를 참고한다. 주요 결과는 `data/processed/product_functionality_handoff/`에 있으며, 전체 데이터는 `workspace_snapshots/`의 분할 압축본으로 보존한다. 키·비밀번호와 가상환경/모델 다운로드는 포함하지 않는다.

## Claim 100개 제품·Evidence 매핑 시험

제품 식별은 사용자 제공 PDF의 정확 일치·구절/제조사·편집 거리 80점 규칙을 적용한다. Claim별 제품·원료 후보 전체를 실제 BGE-reranker-v2-m3로 정렬하고, 전체 순위와 Top-K 비교를 저장한다. [실행 방법과 제한](docs/claim_evidence_pilot100.md)을 참고한다. 이전 TF-IDF 예시와 점수 체계가 다르며 최종 판정은 하지 않는다.

```powershell
.\.venv\Scripts\python.exe -u -X utf8 scripts/run_claim_evidence_pilot.py --input "C:\Users\박이정\Documents\카카오톡 받은 파일\claims_all.json"
.\.venv\Scripts\python.exe -X utf8 scripts/summarize_claim_evidence_pilot.py
```

산출물은 `data/processed/claim_evidence_pilot100/`에 저장한다. 원본 Claim JSON과 SQLite DB는 수정하지 않는다.

전체 3,400개 Claim의 백그라운드 연결 작업은 [전체 실행·진행 확인 안내](docs/claim_evidence_all.md)를 참고한다. 진행 상태와 최종 결과는 `data/processed/claim_evidence_all/`에 저장한다. `full_run_status.json`이 complete일 때만 전달 파일 검증까지 끝난 상태다.

## 제품명 기준 YouTube 후보 URL 수집

실행 파일은 루트의 `collect_youtube_ads.py`다. 다운로드 폴더의 원본을 검토하고 수정본을 이 프로젝트에 작성했다. 원본 다운로드 파일은 변경하지 않았다.

### 설치 및 입력

Python 3.10 이상을 사용한다. 프로젝트 루트에서:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`products_for_search.json`을 루트에 둔다. 현재 입력은 총 45,297개, `category="search"` 40,556개다. 다른 category는 처리하지 않는다. 각 수집 대상에 `id`, `product_name`, `company_name`, `product_core`, `company_core`, `product_key`, `company_key`가 필요하다. 기존 `query`는 보존하지만 사용하지 않고 **product_core만 검색어로 사용한다.** 입력 파일의 id는 이 파일의 식별자이며 DB의 product_id와 같다고 가정하지 않는다.

YouTube Data API v3를 활성화한 프로젝트의 키를 환경변수 `YT_API_KEY` 또는 루트의 `.env`에 설정한다. `.env` 예:

```dotenv
YT_API_KEY=발급받은_실제_키
```

`YT_API_KEY`를 우선 사용하며, 없으면 기존 수집기의 `YOUTUBE_API_KEY`를 호환용으로 읽는다. 현재 로컬의 기존 키도 그대로 사용할 수 있다. 키를 실행 명령·Git·로그에 넣지 않는다. 코드와 상태 DB에는 인증키를 저장하지 않는다.

### 실행 순서

파일 앞쪽에는 원료성·OEM 제품이 포함되므로, 광고에 등장할 법한 제품 10개를 `--ids`로 골라 시험한다. 아래 ID는 현재 입력 파일에서 확인한 값이다.

```powershell
.\.venv\Scripts\python.exe collect_youtube_ads.py search --ids 12719 25586 37538 11605 29297 2031 39360 27245 11737 11221 --max-api-calls 30 --report state/product_name_smoke_report.json
```

`--ids`는 공백 또는 쉼표로 구분한다. 누락됐거나 수집 제외인 ID는 오류로 알린다. `--limit 5`, `--company-limit 3`도 실행 상한으로 사용할 수 있다. ID 필터와 limit을 함께 쓰면 ID로 고른 뒤 입력 순서에서 limit까지 처리한다. generic 여부는 선택한 표본이 아닌 입력 전체를 기준으로 계산한다.

`--max-api-calls 30`은 캐시에 없는 HTTP 시도를 재시도 포함 최대 30회로 제한한다. 상한에서 중단되면 다음 실행에서 이어간다. 제품·회사 수 제한은 영상 수나 조회할 채널 수 제한이 아니다.

전체 수집:

```powershell
.\.venv\Scripts\python.exe collect_youtube_ads.py search
.\.venv\Scripts\python.exe collect_youtube_ads.py export
# 필요할 때만 제조사 채널도 보조적으로 수집
.\.venv\Scripts\python.exe collect_youtube_ads.py channel
```

선정한 99개 제품만 검색·재개하려면 다음 명령을 사용한다. 이전 10개 시험 제품도 포함하며, 캐시와 오늘의 남은 예산을 재사용한다. 예산이 부족하면 다음 할당량 초기화 후 같은 명령을 실행한다.

```powershell
.\.venv\Scripts\python.exe scripts/run_youtube_search_99.py
```

대상 목록은 `docs/youtube_search_99_manifest.json`, 완료·미완료 ID와 분류 집계는 `docs/youtube_search_99_summary.json`, 예시 보고서는 `state/search_99_report.json`에 저장한다. 전체 후보 출력은 기존 `ad_video_urls.json`을 사용한다.

첫 99개와 겹치지 않는 두 번째 묶음은 별도 파일로 유지한다. 재개 명령:

```powershell
.\.venv\Scripts\python.exe scripts/run_youtube_search_99.py --manifest docs/youtube_search_batch002_manifest.json --summary docs/youtube_search_batch002_summary.json --report state/search_batch002_report.json
```

`search`는 제품명으로 바로 검색한다. 제조사 채널 검색을 선행하지 않는다. `channel`은 제조사 채널을 탐색하는 **보조 수단**이다. `all`은 제품 검색 후 보조 채널 수집을 실행한다. 기본 운영은 매일 `search`를 실행하는 방식이다. 직접 검색에 결과가 없거나 아직 검색하지 않은 제품도 channel에서 후보를 찾을 수 있다. channel에서 이미 결과를 수집한 제품은 후속 search에서 생략할 수 있다.

Linux/macOS에서는 위 Python 경로를 `.venv/bin/python` 또는 환경의 Python 전체 경로로 바꾼다. `--input`, `--state`, `--output`으로 경로를 지정할 수 있으며 기본 경로는 스크립트가 있는 프로젝트 루트 기준이다.

### 선택 조건과 결과

- `contentDetails.duration`을 ISO 8601로 파싱해 **0초 초과, 60초 이하**만 남긴다. `videoDuration=short`만으로 60초 조건을 판단하지 않는다.
- NFC·소문자 변환 후 한글/영문/숫자만 남긴 제목+설명에 `product_key`가 포함돼야 한다.
- 제조사 일치는 후보 수집의 필수 조건이 아니다. 아래 근거를 기록해 상태를 분류한다.
- 원본처럼 회사별 채널 검색 결과 최대 5개 중 **회사 키가 채널명에 포함되는 방향만** 인정한다. `--channel-results 50`으로 후보를 최대 50개까지 늘릴 수 있다. 역방향 포함은 허용하지 않는다. 인정된 채널의 업로드 목록은 모든 페이지를 조회한다.
- 제품 검색은 product_core별 첫 페이지 최대 25개만 조회한다. 동일 검색 응답과 영상 상세 정보는 캐시로 재사용한다. 영상 ID가 없는 비영상 검색 항목은 건너뛴다.

| 근거 필드 | 판정 방법 |
| --- | --- |
| manufacturer_in_text | company_key가 제목·설명·채널명 중 어디에 포함되는지 확인. manufacturer_locations도 기록 |
| manufacturer_label | 설명의 제조원·제조사·제조업소 표기 뒤 같은 줄의 값에 회사 키가 있는지 확인. 뒤따르는 판매원·수입원 필드는 분리 |
| paid_promotion | paidProductPlacementDetails.hasPaidProductPlacement의 실제 응답값. 미제공은 null이며 false로 추정하지 않음 |
| ad_keywords | 광고·#ad·CF/TVCF·15초·30초의 발견 목록 |
| manufacturer_channel_candidate | 회사명 포함 규칙으로 채택한 채널 ID인지 기록. 이것만으로 confirmed 처리하지 않음 |

유료 광고 필드는 [공식 videos 리소스](https://developers.google.com/youtube/data/reference/rest/v3/videos)와 [videos.list의 part 목록](https://developers.google.com/youtube/data/reference/rest/v3/videos/list)에 존재한다. 코드에서 해당 part를 요청한다. 유료 광고 표시나 광고 키워드는 광고 관련 단서이며 제품 식별의 강한 근거로 사용하지 않는다.

**generic 규칙:** 입력 전체에서 같은 product_key가 서로 다른 company_key에 연결되면 표시한다. 비교 키가 3자 이하이거나, 마그네슘·밀크씨슬·홍삼정 등 코드의 명시적 일반명 목록에 있어도 표시한다. 길이 3자는 보수적인 운영 규칙이며 검증된 통계적 임계값이 아니다. 짧은 브랜드명도 걸러질 수 있다. 각 이유를 generic_reasons에 남긴다.

| 상태 | 조건 |
| --- | --- |
| confirmed | 60초 이하·제품명 포함을 만족하고 manufacturer_in_text 또는 manufacturer_label이 참 |
| needs_review | 길이·제품명 조건을 만족하지만 제조사 근거 없음. generic은 이 상태로 저장하지 않음 |
| rejected | 길이·제품명 조건 실패 또는 generic인데 제조사 근거 없음 |

결과 `ad_video_urls.json`은 confirmed와 needs_review만 담는다. 기존 필드 `id, product_name, company_name, url, video_id, title, channel_title, duration_sec, published_at, method`에 `status`, `evidence`, `generic`, `generic_reasons`, `description_preview`(앞 300자), `logic_version`, `rejection_reasons`를 추가했다. `method`는 `channel` 또는 `search`다. 제품 ID+영상 ID가 같은 결과는 중복 저장하지 않는다. 여러 제품에 같은 영상이 연결될 수 있다. export 모드는 키 없이 실행할 수 있고, 수집이 중단돼도 현재 결과를 자동으로 내보낸다.

탈락 기록은 state DB의 assessments에 저장하며, `--report`로 상태별 개수와 각 상태의 예시 최대 5개를 내보낸다. 기본은 `state/collection_report.json`이다. 개수 단위는 **제품–영상 쌍**이며 고유 영상 수와 다를 수 있다. 제품 검색에서는 상세 조회된 모든 영상을 평가하고, channel에서는 제품명 키가 포함된 영상만 평가한다. 비공개·삭제 등 상세 정보가 없는 ID와 비영상 검색 항목은 평가 개수에서 제외한다.

**한계:** confirmed는 현재 문자열 규칙상 제품 연결 근거가 있다는 뜻이며 실제 광고 여부·동일 세부 버전까지 검증했다는 의미가 아니다. 제조사·제품명이 함께 언급된 후기나 제휴 판매 영상도 포함될 수 있다. 여러 제품을 설명하는 영상에서 서로 떨어진 문구가 일치하는 경우도 검토가 필요하다. 채널명 포함은 실제 공식 채널 소유권 인증이 아니다. 영상 시청·LLM 판정은 아직 실행하지 않으며, needs_review를 자동으로 광고 확정 처리하지 않는다.

### 재개·할당량·보안

`state/collection.sqlite`에 성공 응답, 영상별 상세 정보, 완료 작업, 결과와 일별 호출 예산을 저장한다. 성공한 검색·업로드 페이지는 재실행 시 캐시를 사용한다. 중간 페이지에서 quotaExceeded가 나면 그 실패 요청부터 다시 시도한다. 부분 결과는 즉시 저장하며 5xx·429·rateLimitExceeded·네트워크 오류는 최대 6번, 지수 백오프로 재시도한다. 인증 오류는 재시도하지 않는다. 동시 실행은 상태 폴더별 파일 잠금으로 차단한다.

API 응답을 받은 순간과 로컬 저장 사이에 프로세스가 강제 종료되면 마지막 요청 1회가 다시 발생할 수 있다. 외부 API에 요청 식별자를 지정할 수 없으므로 이 구간까지 정확히 한 번 호출을 보장하지는 않는다. 재시도도 예산에 포함한다.

공식 문서(2026-10-15 갱신)는 **search.list 하루 100회 별도 제한**, 다른 메서드 합계 하루 10,000유닛을 안내한다. 기존 100유닛/검색 기준도 보수적으로 유지하여, 스크립트는 검색당 100, 기타 요청당 1로 계산한 예산과 검색 횟수 한도를 동시에 적용한다. 기본값은 각각 10,000과 100이며 더 낮게 지정할 수 있다. 따라서 실제 Google 예산보다 일찍 멈출 수 있다. 실제 프로젝트 한도는 Cloud Console에서 확인한다. [공식 할당량 문서](https://developers.google.com/youtube/data/determine_quota_cost)

날짜 경계는 Google 기준인 미국 태평양 자정이다. 로컬 예산은 **이 state 폴더에서 발생한 호출만** 집계한다. 다른 프로그램·다른 state 폴더·같은 키를 쓰는 사용자의 호출량은 알 수 없다. 서버가 quotaExceeded를 반환하면 정상 종료 코드 0으로 멈춘다. 인증·입력·재시도 초과 오류는 종료 코드 1이다.

같은 입력과 state를 사용해야 이어서 실행된다. `--ids`를 바꾸거나 `--limit`을 늘리거나 제거하는 것은 가능하다. 입력 파일 내용이 바뀌면 혼합을 방지하기 위해 중단하므로 새 `--state`를 지정한다. 이전 엄격한 제조사 필수 방식의 완료 표시는 새 판정에서 재사용하지 않는다. 새 판정에 맞춰 작업 버전과 상세 정보 캐시를 구분하며, 예전 결과를 새 상태로 무조건 승격하지 않는다. 기존 다운로드 스크립트의 JSON 상태 파일은 새 SQLite 상태에 자동 이관하지 않는다. 완료한 검색은 매일 재검색하지 않는다. 새 영상을 주기적으로 재탐색하려면 별도 갱신 정책이 필요하다.

### API 없이 테스트

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_collect_youtube_ads.py -v
```

mock으로 길이 경계·매칭 조건·회사명 역방향 일치 배제·페이지 중단/재개·검색 생략·중복 결과·백오프·키 유출 방지·입력 제외·실행 제한을 검증한다.

2026-10-24 제품명 검색 시험: 위 10개 ID로 검색을 완료해 **confirmed 5건, needs_review 52건, rejected 186건**을 기록했다. 최종 후보는 57건이며 실제 광고 확정 수가 아니다. 보고서는 `state/product_name_smoke_report.json`, 후보 URL은 `ad_video_urls.json`에서 확인한다. 이전 2026-10-23 제조사 필수 시험 5제품·0건과 표본 및 조건이 다르므로 개선율을 계산하지 않는다. 전체 40,556개에 대한 수집 결과가 아니다.

새 판정 테스트를 포함해 YouTube 관련 **28개 테스트가 통과**했다. 같은 10개 ID 재실행 시 추가 HTTP 호출 0회를 확인했다. 제품별 완료·분류 수치는 `docs/youtube_product_name_smoke_test.json`, 검토 필요 52건의 클릭 가능한 목록은 `docs/youtube_review_candidates.md`에 저장했다.

### 매일 자동 실행: Windows 작업 스케줄러

1. **작업 만들기 → 트리거 → 매일**을 선택한다. 한국 시간 오전 10시처럼 매일 같은 시간을 지정한다.
2. 동작의 프로그램: `C:\Users\박이정\Desktop\DSCD_NNN\.venv\Scripts\python.exe`
3. 인수: `"C:\Users\박이정\Desktop\DSCD_NNN\collect_youtube_ads.py" search`
4. 시작 위치: `C:\Users\박이정\Desktop\DSCD_NNN`
5. 설정에서 **이미 실행 중이면 새 인스턴스를 시작하지 않음**을 선택한다. 키를 인수에 넣지 않는다. 실행 계정이 프로젝트의 `.env`와 state에 접근할 수 있어야 한다.

이 설정은 수동으로 등록한다. 컴퓨터가 꺼져 있으면 실행되지 않으며, 상시 실행하려면 서버에 배치한다.

### 매일 자동 실행: Linux/macOS cron

서버에 프로젝트와 입력 파일·`.env`를 배치하고 가상환경 의존성을 설치한 뒤 `crontab -e`에 실제 절대 경로를 넣는다. 아래는 서버 시간 기준 매일 오전 10시이며 로그 디렉터리를 먼저 만든다.

```bash
mkdir -p /home/bright-dgrv24/TRUEAD/Data_Selection/state
# crontab 항목: Python 경로는 실제 TRD 환경의 `which python` 결과로 교체
0 10 * * * /home/bright-dgrv24/miniconda3/envs/TRD/bin/python /home/bright-dgrv24/TRUEAD/Data_Selection/collect_youtube_ads.py search >> /home/bright-dgrv24/TRUEAD/Data_Selection/state/daily.log 2>&1
```

cron은 대화형 셸의 conda 활성화 설정을 읽지 않으므로 Python 전체 경로를 쓴다. `.env`는 스크립트 위치에서 읽으며 터미널을 계속 열어둘 필요는 없다. 서버의 시간대는 `date`로 확인한다.

현재 작업 폴더(`DSCD_NNN`)가 TRUEAD 프로젝트 루트입니다.
STEP 1~4: 폴더 구조, 공개 영상 URL → 로컬 MP4 다운로드, 최소 의존성,
실행 안내를 제공합니다. 식약처 건강기능식품정보 collector를 추가 구현했으며,
나머지 공식 API collector와 공통 유틸은 TODO입니다.
STT, OCR, VLM, Claim Extraction, RAG, Verification 및 사례 importer는 다음 단계입니다.

## 설치 (Windows PowerShell)

Python 3.10 이상이 필요합니다. 프로젝트 루트에서 실행합니다.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

가상환경이 이미 있으면 설치 명령만 실행하세요. `python`이 Windows 스토어 별칭으로
연결되어 실행되지 않으면 `py` 또는 설치된 Python의 전체 경로를 사용하세요.
가상환경 활성화 없이도 아래 명령을 실행할 수 있습니다.

```powershell
.\.venv\Scripts\python.exe scripts/download_video.py --url "VIDEO_URL"
```

가상환경을 활성화한 경우 요청한 형식 그대로 실행할 수 있습니다.

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/download_video.py --url "VIDEO_URL"
```

공개 MP4 샘플로 확인하려면:

```powershell
.\.venv\Scripts\python.exe scripts/download_video.py --url "https://media.w3.org/2010/05/sintel/trailer.mp4"
```

## 결과와 제한

파일은 실행 위치와 관계없이 프로젝트의 `data/raw/ads/videos/<영상 ID>.mp4`에 저장됩니다.
파일명은 yt-dlp가 제공하는 ID를 기반으로 Windows에 안전하게 정리됩니다.
TikTok CDN 직접 영상 주소(`*.tiktokcdn.com`)도 같은 `--url` 옵션으로 받을 수 있습니다.
CDN 주소에는 게시물 ID가 없으므로 영상 경로의 마지막 요소를 해시한
`tiktok_<24자리 해시>.mp4`로 저장합니다. 긴 쿼리 문자열을 파일명으로 사용하지 않습니다.
PowerShell에서는 `&`가 들어 있는 URL 전체를 따옴표로 감싸세요.
같은 ID의 기존 파일은 yt-dlp의 기본 동작에 따라 재사용될 수 있습니다.

성공 시 (종료 코드 0):

```text
Download successful
Saved to: C:\...\DSCD_NNN\data\raw\ads\videos\trailer.mp4
```

실패 시 (종료 코드 1, 사용자 중단은 130):

```text
Download failed
Reason: ...
```

공개 접근 가능한 단일 영상만 대상으로 합니다. 재생목록, 여러 영상이 포함된 게시물,
라이브 방송은 지원하지 않습니다. 로그인 쿠키, 계정 인증, DRM 및 인증 우회는 사용하지 않습니다.
공개 URL도 사이트 제한, 삭제, 미지원 사이트, 네트워크 오류로 실패할 수 있습니다.

영상과 음성이 함께 있는 MP4를 우선 선택합니다. 다른 형식의 변환이나 분리 스트림
병합에는 **FFmpeg 실행 파일**을 설치하고 PATH에 추가해야 합니다.
`ffmpeg -version`으로 확인하세요. pip의 동명 패키지는 실행 파일 설치를 대신하지 않습니다.
스크립트는 PATH의 FFmpeg 외에 `.tools/ffmpeg*/bin/ffmpeg.exe`도 자동으로 찾습니다.
FFmpeg가 없으면 바로 저장 가능한 MP4만 선택하며, 해당 형식이 없으면 실패합니다.
근거: [yt-dlp 공식 문서](https://github.com/yt-dlp/yt-dlp#dependencies),
[FFmpeg 다운로드](https://ffmpeg.org/download.html).

사이트 변경으로 추출이 실패하면 yt-dlp를 업데이트한 뒤 다시 실행하세요.

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade "yt-dlp[default]"
```

YouTube 추출에는 추가로 Deno와 EJS 구성요소가 필요합니다.
`requirements.txt`의 `yt-dlp[default]`가 EJS를 설치하며, 스크립트는 PATH의 Deno 또는
`.tools/deno/deno.exe`를 사용합니다. `.tools/`는 Git에서 제외됩니다.
다른 PC에서는 [Deno 설치 안내](https://docs.deno.com/runtime/getting_started/installation/)와
위 FFmpeg 다운로드 안내에 따라 실행 파일을 준비하세요.
[yt-dlp의 YouTube 지원 안내](https://github.com/yt-dlp/yt-dlp/wiki/EJS)를 참고하세요.

## 준비된 구조

```text
.env / .env.example       향후 공식 API 키 설정 (현재 영상 다운로드에는 불필요)
requirements.txt         yt-dlp[default], requests, python-dotenv
data/input/enforcement_cases.csv   필드 헤더만 있는 수동 입력 양식
data/raw/ads/videos/      다운로드 영상
data/raw/mfds_products/
data/raw/functional_ingredients/
data/raw/individually_approved/
data/raw/enforcement_cases/
data/raw/diseases/
data/raw/food_ingredients/
data/raw/health_food_businesses/
data/raw/product_ingredients/
data/processed/           향후 정규화 데이터
src/collectors/           7개 collector TODO
src/utils/api.py          API 통신 TODO
src/utils/io.py           저장 유틸 TODO
scripts/download_video.py
scripts/collect_*.py      미구현을 알리고 종료하는 자리표시자
```

`.env`, 가상환경, 수집한 raw/processed 파일은 Git에서 제외됩니다.
사례 CSV에는 실제 적발 사례를 임의로 채우지 않았습니다.

## 다음 단계의 공식 데이터 출처

## 심평원 질병명·상병코드 수집

심평원 질병정보 API의 `getDissNameCodeList1`을 사용해 질병명, 상병코드, 영문 상병명을 수집합니다.
성별·연령별 또는 의료기관별 통계는 이번 collector의 범위에 포함하지 않습니다.

`.env`에 API 키를 설정합니다.

```dotenv
HIRA_DISEASE_API_KEY=YOUR_KEY
```

API는 전체 목록을 반환하는 unfiltered 조회를 제공하지 않고 `searchText`를 필수로 요구합니다.
따라서 `diseaseType=SICK_CD`로 지정하고 코드 접두어 `0–9`, `A–Z`를 순회합니다.
양방·한방(`medTp=1,2`)과 3단·4단 상병(`sickType=1,2`)을 모두 수집합니다.

```powershell
python scripts/collect_diseases.py
```

원본 XML은 `data/raw/diseases/<run-id>/`, 정리된 JSONL은
`data/processed/diseases/<run-id>/disease_codes.jsonl`에 저장됩니다.
중단되면 출력된 run ID로 재개할 수 있습니다.

```powershell
python scripts/collect_diseases.py --run-id "출력된_RUN_ID"
```

기존 XML 페이지를 재사용하고 JSONL을 처음부터 다시 생성하므로 재개 실행 시 행이 중복 추가되지 않습니다.
`manifest.json`의 모든 query 상태가 `complete`이고 `collected_count`가 총계와 일치하는지 확인하세요.

### API 전체 수집 검증 (2026-09-18)

- 실행 ID: `20260918T100807877490Z`
- 144개 코드 접두어·상병구분·의료구분 질의, 원본 XML 425페이지 완료
- 정리된 질병명·상병코드: 34,861행
- 조합별 상병코드 중복 0건, 빈 질병명·상병코드 0건

## YouTube 광고 후보 URL 수집

이 수집기는 YouTube Data API v3로 건강기능식품 **광고 후보**의 URL과 metadata만 수집합니다.
영상 파일을 다운로드하거나 `is_ad` 값을 판정하지 않습니다.

Google Cloud Console에서 YouTube Data API v3를 활성화한 API 키를 프로젝트 루트의 `.env`에 추가하세요.

```dotenv
YOUTUBE_API_KEY=YOUR_KEY
```

키워드는 [configs/youtube_search_keywords.yaml](configs/youtube_search_keywords.yaml)에서 카테고리별로 관리합니다.
키워드를 추가·삭제하면 다음 실행부터 반영됩니다.

먼저 소량으로 실행합니다.

```powershell
python scripts/collect_youtube_urls.py --max-results 20
```

정상적으로 CSV를 확인한 뒤 500건을 수집합니다.

```powershell
python scripts/collect_youtube_urls.py --max-results 500
```

기본값은 키워드 하나당 `search.list` 한 페이지(최대 50건)만 호출합니다. 더 많은 페이지가 필요하면
아래처럼 명시적으로 늘리세요. 각 검색 페이지는 YouTube API 쿼터를 사용합니다.

```powershell
python scripts/collect_youtube_urls.py --max-results 500 --max-pages-per-keyword 2
```

수집기는 `type=video`, `maxResults=50`을 사용하고, `videos.list`는 새 video ID를 최대 50개씩 묶어 metadata를 조회합니다.
동일 ID의 metadata를 다시 요청하지 않습니다. 일반 영상, 제목에 광고 단어가 없는 영상, 조회수가 낮은 영상을 제거하지 않습니다.

저장 위치는 다음과 같습니다.

- 원본 search/videos API 응답과 실행 기록: `data/raw/youtube_search/<run-id>/`
- 후보 metadata CSV: `data/processed/youtube_ad_candidates.csv`
- 향후 downloader 입력 CSV: `data/input/ad_urls.csv`

`youtube_ad_candidates.csv`는 `video_id`로 한 행만 유지하며, 같은 영상이 여러 검색어에 노출되면
`search_keywords`, `search_categories`를 `|`로 이어 보존합니다. API가 `videos.list` 결과를 제공하지 않는 영상은
검색 응답의 제목·설명·채널 정보를 보존하고 `duration`, `view_count`는 비웁니다. 그런 ID는 raw의 `manifest.json`에도 기록됩니다.

실행 중 API 오류나 쿼터 오류가 발생해도 이전 CSV와 raw 응답은 삭제하지 않습니다. 다음 실행은 기존 후보를 읽어
이미 저장된 ID를 중복 추가하지 않고, 새 ID만 metadata 조회합니다. `--max-results`는 기존 후보를 포함한 최종 unique 후보의 상한입니다.

현재 로컬 검증은 모의 API로 search pagination, ID 중복 병합, metadata 배치, 기존 CSV 보존, 키 누락 오류를 확인했습니다.
실제 API의 20건 검증은 `YOUTUBE_API_KEY` 설정 후 실행합니다.

### 구현 완료: 건강기능식품정보 전체 수집

`.env`에 `DATA_GO_KR_API_KEY=발급받은키`를 설정합니다. URL 인코딩된 키와
디코딩된 키를 모두 지원하며, 키는 로그나 결과 데이터에 저장하지 않습니다.

```powershell
python scripts/collect_mfds_products.py
```

공식 명세의 `getHtfsList01`(목록), `getHtfsItem01`(상세)를 필터 없이
각각 마지막 페이지까지 수집합니다. 페이지당 100건을 사용합니다.
공식 Swagger의 `ServiceKey`, `pageNo`, `numOfRows`, `type=json` 파라미터를 사용합니다.
1,000건 요청은 API 오류 11을 반환하여 collector의 허용 범위를 1~100건으로 제한했습니다.

- 원본: `data/raw/mfds_products/<run-id>/<operation>/page_000001.json`
- 실행 기록과 수집 건수: 같은 run 폴더의 `manifest.json`
- 정리된 데이터: `data/processed/mfds_products/<run-id>/<operation>.jsonl`

목록과 상세는 같은 제품의 서로 다른 조회 결과이므로 두 파일의 행 수를 합쳐
제품 수로 계산하지 않습니다. 분석에는 `getHtfsItem01.jsonl`을 우선 사용하세요.
정리된 파일은 제품명, 업체명, 품목제조관리번호, 기능성, 섭취방법 등을 명명하고,
`original_fields`에 제공된 모든 필드, `source`에 출처와 원본 페이지를 보존합니다.
누락된 값은 `null`이며, 원문을 임의로 추정하거나 중복을 삭제하지 않습니다.

중단되면 출력된 run ID로 이어받습니다 (기존에 다른 page-size를 썼다면 동일하게 지정):

```powershell
python scripts/collect_mfds_products.py --run-id "출력된_RUN_ID"
```

이미 받은 원본 페이지는 재사용하며 JSONL은 처음부터 재생성하여 재개 시 중복 추가를 방지합니다.
완성 전에는 `.jsonl.partial` 확장자를 사용합니다. `manifest.json`의 `status=complete`와
각 operation의 `collected_count=total_count`를 확인하세요.
네트워크 오류는 제한적으로 재시도하며, API 오류·페이지 누락·반복 페이지·전체 건수 변경은
실패로 처리합니다. API가 수집 도중 같은 건수로 내용을 수정하는 경우까지 검출하는 스냅샷은 아닙니다.

검증 명령:

```powershell
python -m unittest discover -s tests -v
```

### 나머지 출처

아래 주소는 제공된 출처 목록이며 API 호출 endpoint를 뜻하지 않습니다.
영상 저장 확인 후 각 API의 인증 방식, endpoint, pagination 및 응답 필드를 확인하여
collector를 하나씩 구현합니다. `.env.example`의 키 이름은 프로젝트 내부의 예약 설정이며,
서비스별 실제 인증 파라미터는 아직 확정하지 않았습니다.

| Collector | 제공된 출처 |
| --- | --- |
| mfds_products | https://www.data.go.kr/data/15056760/openapi.do |
| functional_ingredients | https://www.data.go.kr/data/15058359/openapi.do |
| individually_approved | https://www.data.go.kr/data/15074311/openapi.do |
| diseases | https://www.data.go.kr/data/15119055/openapi.do |
| food_ingredients | https://www.data.go.kr/data/15058665/openapi.do |
| health_food_businesses | https://www.data.go.kr/data/15064849/openapi.do |
| product_ingredients | https://www.foodsafetykorea.go.kr/api/openApiInfo.do?menu_grp=MENU_GRP31&menu_no=661&show_cnt=10&start_idx=1&svc_no=C003 |
| enforcement_cases (향후 수동 importer) | https://www.mfds.go.kr/brd/m_1060/view.do?seq=14998 |

향후 collector에는 `.env` 키 읽기, requests와 timeout, API 오류 처리, pagination,
UTF-8 원본 JSON/JSONL 저장, source 보존 및 별도 normalized 저장을 적용합니다.

## 이번 작업의 검증 결과

- Windows / Python 3.12.5 가상환경에 requirements 설치 완료.
- 위 W3C 공개 샘플로 실제 다운로드 성공, 종료 코드 0 확인.
- `data/raw/ads/videos/trailer.mp4`: 4,372,373 bytes, MP4 `ftyp` 헤더 확인.
- 잘못된 URL 입력 시 `Download failed` / `Reason` 출력 및 종료 코드 1 확인.
- 추가 검증: 프로젝트 `.tools/`에 FFmpeg/Deno 준비 후 YouTube `zDR7jYZpfBo` 다운로드 성공.
  분리된 영상과 음성을 `zDR7jYZpfBo.mp4`로 병합한 뒤 종료 코드 0 확인.
- 다른 형식의 재인코딩 변환은 미검증이며, 다른 SNS URL은 해당 URL로 별도 확인해야 합니다.
- 사용자 제공 TikTok CDN 주소로 `tiktok_2d98fafd4926893a296b1143.mp4` 다운로드 성공.


### API 전체 수집 검증 (2026-09-18)

- 실행 ID: 20260918T091546603973Z
- 목록/상세 각각 46,165행, 462페이지; 전체 품목번호 집합 일치.
- 중복 품목번호 0건, 정리된 original_fields와 원본 응답의 모든 행 일치.
- 상세의 기능성 8건, 섭취방법 410건은 원본에서 비어 있어 그대로 보존.
- 로컬 검증 결과: data/processed/mfds_products/20260918T091546603973Z/validation.json
- 인증키 및 수집 데이터는 Git에 포함하지 않음.
