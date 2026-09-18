# TRUEAD — 1차 MVP 데이터 수집 준비

저장소의 `Data_Selection/` 폴더가 TRUEAD 데이터 수집 프로젝트 루트입니다.
STEP 1~4: 폴더 구조, 공개 영상 URL → 로컬 MP4 다운로드, 최소 의존성,
실행 안내를 제공합니다. 공식 API collector와 공통 유틸은 TODO만 준비했습니다.
STT, OCR, VLM, Claim Extraction, RAG, Verification 및 사례 importer는 다음 단계입니다.

## 설치 (Windows PowerShell)

처음 저장소를 받는 팀원:

```powershell
git clone --branch data-selection https://github.com/CSID-DGU/2026-2-DSCD-NoMoreNaN-05.git
cd 2026-2-DSCD-NoMoreNaN-05
cd Data_Selection
```

이미 저장소를 받은 팀원은 저장소 루트에서 실행합니다 (기존 작업은 먼저 커밋하세요):

```powershell
git fetch origin
git switch --track origin/data-selection
cd Data_Selection
```

로컬 `data-selection` 브랜치가 이미 있다면 `git switch data-selection` 후
`git pull --ff-only`로 업데이트합니다.
가상환경, FFmpeg/Deno 실행 파일 및 다운로드 영상은 저장소에 포함되지 않습니다.
아래 설치 절차와 FFmpeg/Deno 안내에 따라 각 PC에서 준비하세요.

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
Saved to: C:\...\Data_Selection\data\raw\ads\videos\trailer.mp4
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
- Instagram 릴스 `DczlQvJyEOu`: 720×1280, 약 24초, 영상·음성 포함 MP4 저장 확인.
