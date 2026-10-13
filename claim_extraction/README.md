# Claim Extraction

광고 영상에서 Atomic Claim을 뽑아 `data/output/<영상>.claims.json`으로 낸다.

```
claim_extraction/ 
   ├─ audio/     음성 → Claim
   ├─ visual/    화면 → Claim
   ├─ alignment/ 두 결과를 하나로
   └─ main.py
```

## 환경

```bash
bash setup.sh        # conda env 생성
```

## 전체 실행

```bash
python main.py              # data/ 전부
python main.py [영상.mp4]    # 특정 데이터만 
```


## 폴더

### audio/
- 입력: mp4
- 출력: `<영상>.transcript.json`, `<영상>.audio_claims.json`
- STT(Qwen3-ASR)로 자막을 만들고 gpt-oss로 Claim을 뽑는다.
```bash
conda activate truead && cd audio
python main.py [영상.mp4]      # gpt-oss 서버 필요: GPUS=0,1 bash ../serve_llm.sh
```

### visual/
- 입력: mp4
- 출력: `data/frames/<영상>/`, `<영상>.keyframes.json`, `<영상>.visual_claims.json`
- 키프레임을 고른 뒤(keyframes) VLM으로 Claim을 뽑는다(claims). 두 단계 사이에 프레임 이미지를 확인할 수 있다.
```bash
conda activate truead-visual && cd visual
python main.py keyframes [영상.mp4]
python main.py claims    [영상.mp4]
```

### alignment/
- 입력: `<영상>.audio_claims.json` + `<영상>.visual_claims.json`
- 출력: `<영상>.claims.json` (최종 Claim List)
- 같은 시각의 음성·화면 Claim을 병합하고 Conflict를 표시한다.
```bash
conda activate truead && cd alignment
python main.py [영상.mp4]
```

## 출력 형식
최종 Claim 필드: `claim_id` `text` `t_start` `t_end` `duration` `target` `scope` `speaker` `dup_of` `types` `source` `conflict` `evidence`.
시각은 초 단위, 밀리초까지. 예시는 팀 문서 `claim_json_example.json`.
