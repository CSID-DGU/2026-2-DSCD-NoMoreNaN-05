# Claim Extraction

광고 영상에서 Atomic Claim을 뽑아 `data/output/<영상>.claims.json`으로 낸다.

```
claim_extraction/
   ├─ audio/      음성 → Claim (Qwen3-ASR + gpt-oss)
   ├─ visual/     화면(글자+시각) → Claim (PaddleOCR-VL 문맥 + Qwen3.5). 프레임 선택: OCR 대표 표기 프레임 / V-JEPA 2 변화 프레임
   ├─ alignment/  브랜치 결과를 하나로 (scene 글자 복사 제거(text 브랜치 ON일 때만) · 병합 · SAME/CONFLICT/UNRELATED 판정(JUDGE_CHUNK쌍씩 묶어 JUDGE_PARALLEL개 동시 호출) · products(근거 줄 번호 검증))
   ├─ common.py   공용 (Claim 타입, LLM 호출, JSON 파싱)
   └─ main.py     전체 실행
```

## 환경

```bash
bash ../../setup.sh  # 백엔드 전체 환경(conda env 3개 + llama.cpp + 모델 + DB). backend/setup.sh 참고
conda env remove -n truead-vllm   # 예전 vLLM env가 남아 있으면 수동으로 삭제
```

## 전체 실행

```bash
python main.py              # data/ 전부
python main.py [영상.mp4]    # 특정 영상만
```

`main.py`의 스위치 두 개로 켜고 끈다. 끈 쪽은 모델·서버·결과 파일이 없다.

- `BRANCHES = {"audio": True, "text": False}` — `text`는 OCR 글자 → gpt-oss Claim 추출. 기본 OFF.
- `FRAME_SELECT = {"change": False, "text": True}` — VLM(scene) 입력 프레임 선택기. `change` = V-JEPA 2 변화 프레임, `text` = OCR 글자 구간마다 대표 표기가 처음 읽힌 프레임(완성 화면 보장 아님). 둘 다 켜면 합집합. **하나라도 켜져 있으면 scene ON, 둘 다 꺼야 VLM이 꺼진다.**

scene은 프레임 이미지와 그 시각에 걸친 OCR 글자 줄을 Qwen3.5에 한 번에 넣어 **화면 글자 Claim(자막·문구·라벨)과 시각 Claim(마크·그래프·표·전후 사진·복장)을 함께** 낸다.
OCR 줄은 글자 판독의 참고이고 이미지에서 확인한 글자만 쓴다. 글자 Claim의 시각은 인용한 OCR 줄(`span_ids`)의 구간, 시각 Claim은 그 프레임 ~ 다음 프레임.
PaddleOCR-VL 스캔은 `FRAME_SELECT["text"]` 또는 `BRANCHES["text"]`가 켜져 있으면 돈다(프레임 선택 · VLM 문맥 · products의 화면 글자 입력).

기본 실행 = 음성(audio) + 화면(scene, OCR 대표 표기 프레임), alignment `--branches audio,scene`.
OCR→gpt-oss text 브랜치로 되돌리려면 `BRANCHES["text"] = True` (keyframes에 `--ocr`, text lane, alignment `audio,text,scene`이 붙는다. 이때 scene 글자 복사 제거가 다시 동작한다).

순서: 입력 준비(AV1만 `data/converted/`로 H.264 변환) → gpt-oss 서버(`serve_llm.sh`) 기동 → Qwen3.5 서버(`serve_vlm.sh`, scene ON일 때) 기동 시작 →
keyframes → audio · (text) · scene 병렬 → alignment. 이 실행에서 띄운 서버는 끝에 내린다.
서버가 이미 떠 있으면 그대로 쓰고 내리지 않는다. 그때는 그 서버 카드 번호를 `SERVER_GPUS=0,1 python main.py …`로 넘겨 다른 단계가 그 카드를 고르지 않게 한다.

## 폴더별 실행

```bash
# 서버: GPUS=0 bash serve_llm.sh   /   GPUS=1 bash serve_vlm.sh
conda activate truead && cd audio
python main.py [영상.mp4 ...] [--ocr-context]             # → transcript.json, audio_claims.json (--ocr-context: keyframes.json 화면 글자를 ASR context로)

conda activate truead-visual && cd visual
python main.py keyframes [영상.mp4 ...] [--select text] [--ocr]  # → keyframes.json, data/frames/<영상>/
                                                       #   --select: change,text 중 켤 선택기(기본 text, 빈 값 "" = 프레임 없음) / --ocr: text 선택기 없이도 OCR(text 브랜치용)
python main.py scene [영상.mp4 ...]                            # → visual_scene_claims.json  (Qwen3.5: 프레임 + 구간 OCR 줄 → 글자·시각 Claim)
python main.py text  [영상.mp4 ...]                            # → visual_text_claims.json   (gpt-oss. 기본 OFF, 되돌림용)

conda activate truead && cd alignment
python main.py [영상.mp4 ...] --branches audio,scene [--title TITLE]  # → claims.json, alignment.json (text 브랜치를 켰으면 audio,text,scene)
                                                       #   --title: 영상 제목(영상 1편일 때만, 기본 환경변수 VIDEO_TITLE). 있으면 products 판단에 제목을 우선 참고
```

## 프롬프트 파일

생성 모델(gpt-oss, Qwen3.5, PaddleOCR-VL)에 보내는 지시문은 `claim_process/prompt/<이름>.txt`에 있고 코드는 `claim_process.prompt`의 `load`·`render`로 읽는다.
파일은 프로세스 시작 때 한 번 읽으므로 고친 내용은 다음 실행부터 반영된다.

| 파일 | 쓰는 곳 |
|---|---|
| `common_claim_head.txt` | claim_type·필드 공통 규칙. audio·text·scene 프롬프트의 `{PROMPT_HEAD}` 자리에 들어감 |
| `audio_claim_system.txt`, `audio_claim_user.txt` | 음성 대본 → Claim (gpt-oss) |
| `visual_text_system.txt`, `visual_text_user.txt` | OCR 줄 → Claim, text 브랜치 (gpt-oss) |
| `visual_scene.txt`, `visual_scene_ocr_head.txt`, `visual_scene_cite.txt` | 프레임 + OCR 줄 → Claim (Qwen3.5). 뒤의 두 파일은 OCR 줄이 있을 때만 들어감 |
| `visual_ocr_task.txt` | PaddleOCR-VL 작업 프롬프트 `OCR:`. 모델이 정한 작업 토큰이라 바꾸면 OCR이 아닌 다른 작업이 됨 |
| `alignment_judge_system.txt`, `alignment_judge_user.txt` | Claim 쌍 SAME/CONFLICT/UNRELATED 판정 (gpt-oss) |
| `alignment_products_system.txt`, `alignment_products_user.txt` | 제품 정보·Claim별 제품 (gpt-oss) |
| `alignment_products_title_system.txt`, `alignment_products_title_user.txt` | 영상 제목이 있을 때만 위 두 파일 앞뒤에 붙음(규칙은 system 뒤, 제목 절은 user 맨 앞) |
| `explanation_system.txt`, `explanation_user.txt` | 판정 설명문 (gpt-oss, `claim_verification/explanation`) |

- `{이름}`(영문·숫자·밑줄)은 코드가 채우는 자리다. 지우거나 이름을 바꾸면 그 모듈 import가 `ValueError`로 멈춘다. 그 밖의 중괄호(JSON 예시 등)는 글자 그대로 간다.
- 파일 끝 개행 하나와 BOM은 무시되고 LF·CRLF 어느 쪽으로 저장해도 같다. `alignment_products_title_user.txt`는 끝의 빈 줄까지 프롬프트다.
- 데이터 행 형식(시각·번호 표기)과 JSON 스키마는 코드에 있다.

## 출력

`<영상>.claims.json`: `video_id`, `products[]`(`product_ref` `product_name` `brand_name` `manufacturer_name` `manufacturing_report_number`),
`claims[]`(`claim_id` `product_ref` `text` `claim_type` `ingredients` `effect` `quantity` `intake_basis` `t_start` `t_end`).
`claim_type`은 배열(1개 이상)이고 원소는 EFFECT / QUANTITY / COMPOSITION / CERTIFICATION / PERSON_CREDENTIAL / ETC(어디에도 속하지 않는 것, 예: 제조원·판매원 표기).
`<영상>.visual_scene_claims.json`: `frames[]`(`source`: change / text), `screen_texts[]`(OCR 글자 구간, `span_id`), `claims[]`(`span_ids`: 인용한 OCR 줄, 시각 Claim은 `[]`).
병합 근거(RULE / SAME / CONFLICT / UNRELATED / SAME_BLOCKED / LINK_BLOCKED)와 Conflict, 제거한 scene 글자 복사(`dropped_scene`, text 브랜치를 켰을 때만), products 이름의 근거 검증(`products_evidence`)은 `<영상>.alignment.json`. 시각은 초 단위, 밀리초까지.
