# TRUEAD — 1차 MVP 데이터 수집 준비

저장소의 `Data_Selection/` 폴더가 TRUEAD 데이터 수집 프로젝트 루트입니다.
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
