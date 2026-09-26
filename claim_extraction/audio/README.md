# Audio Branch — STT → 음성 Claim 추출

## 준비 (lab 서버: 3090×7, sudo 불가, conda)

```bash
bash setup.sh 
GPUS=0,1,2,3 bash serve_llm.sh  
```

로컬(Windows)에서 STT만 볼 때:
```bash
pip install -r requirements.txt
winget install ffmpeg
```

## 실행

```bash
cd claim_extraction/audio
conda activate truead
python main.py             # data/ 안의 영상 전부
python main.py 영상.mp4    # 하나만
```

## 출력

`data/output/<영상이름>.audio_claims.json`

```json
{
  "video": "sample.mp4",
  "transcript": "...",
  "segments": [{"id": 0, "text": "...", "start": 3.2, "end": 5.1}],
  "claims": [
    {
      "claim": "김OO은 의사다",
      "types": ["인물 자격"],
      "source": "음성",
      "start": 3.2, "end": 5.1, "duration": 1.9,
      "segment_ids": [0],
      "quote": "서울대 출신 김OO 의사가 개발했고"
    }
  ]
}
```


## 주의
- ForcedAligner는 180초까지. 그보다 긴 영상은 잘라서 넣어야 한다.
- 지시어("이 제품")는 그대로 남긴다. 제품명 해소는 Alignment 단계에서 한다.
