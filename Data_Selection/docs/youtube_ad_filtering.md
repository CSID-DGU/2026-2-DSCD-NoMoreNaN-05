# YouTube 광고 URL 확정 절차

`scripts/collect_youtube_urls.py`는 검색 API 결과를 광고 후보로만 수집한다. 후보 URL은
`data/input/youtube_candidate_urls.csv`에 저장하며, 최종 광고 URL 파일을 덮어쓰지 않는다.

## 1차 규칙 필터

```powershell
python scripts/filter_youtube_ads.py --rules-only
```

결과는 `data/processed/youtube_rule_filtered.csv`에 저장된다. 제목 또는 채널에 뉴스,
기자, 뉴스룸, 강의, 세미나, 학회, 팩트체크처럼 명백한 정보성 형식 신호가 있을 때만
`REJECT`한다. 그 외 후보는 `PASS`로 남겨 LLM에 넘긴다.

## 2차 LLM 분류

프로젝트 루트 `.env`에 다음을 추가한다. 키 파일은 `.gitignore`로 제외되어 있다.

```dotenv
OPENAI_API_KEY=YOUR_KEY
OPENAI_MODEL=gpt-5-mini
```

그 뒤 실행한다.

```powershell
python scripts/filter_youtube_ads.py --minimum-confidence 0.85
```

각 후보의 `title`, `description`, `channel_title`, `search_keywords`만 LLM에 전달한다.
동영상 파일은 이 단계에서 전송하거나 다운로드하지 않는다. LLM은
`ADVERTISEMENT`, `NON_ADVERTISEMENT`, `UNCERTAIN` 중 하나와 신뢰도, 이유를 반환한다.

- 전체 판단 기록: `data/processed/youtube_ad_classifications.csv`
- 다운로드 입력: `data/input/ad_urls.csv`

`ad_urls.csv`에는 `ADVERTISEMENT`이고 신뢰도가 0.85 이상인 URL만 저장한다. 이전과 같은
입력 metadata 및 모델이면 기존 분류를 재사용하므로, 중단 뒤 재실행해도 이미 분류한 후보에
다시 비용을 쓰지 않는다.

## 1,000개 확정 URL 목표

현재 1,000개 후보 중 1차 규칙 통과분은 976개다. 최종 확정 광고 URL 1,000개를 만들려면
LLM 분류 후 부족한 수만큼 후보 검색을 추가로 실행한다. 후보 수집과 확정 URL을 분리해 두어
후보 원본과 판정 근거를 항상 재현할 수 있다.
