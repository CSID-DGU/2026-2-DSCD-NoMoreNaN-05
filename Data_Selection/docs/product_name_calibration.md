# 제품명 임계값 백그라운드 실험

프로젝트 루트의 PowerShell에서 실행합니다. SQLite는 `mode=ro`로 열며 API·LLM을 호출하거나 원본 DB를 변경하지 않습니다.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-matching.txt
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_product_name_calibration.ps1 -Trials 1000
```

명령은 숨겨진 별도 Python 프로세스를 시작하고 즉시 반환합니다. 채팅과 터미널 작업을 계속할 수 있습니다. 같은 머신이 켜져 있어야 합니다.

실행 명령이 출력한 `output` 경로를 사용합니다.

```powershell
$runPath = '여기에 출력된 output 경로'
Get-Content -LiteralPath (Join-Path $runPath 'progress.json') -Encoding UTF8
Get-Content -LiteralPath (Join-Path $runPath 'stdout.log') -Encoding UTF8 -Tail 10
Get-Content -LiteralPath (Join-Path $runPath 'report.md') -Encoding UTF8
```

중단하려면 `launch.json`의 PID가 해당 실험 프로세스인지 확인하고 종료합니다.

```powershell
$workerId = (Get-Content -LiteralPath (Join-Path $runPath 'progress.json') -Raw | ConvertFrom-Json).pid
Get-CimInstance Win32_Process -Filter "ProcessId=$workerId" | Select-Object ProcessId, CommandLine
# CommandLine이 이 실험인지 확인한 다음 실행
Stop-Process -Id $workerId
```

중단한 실행을 재개할 수 있습니다.

```powershell
.\.venv\Scripts\python.exe -u .\scripts\calibrate_product_name_thresholds.py --trials 1000 --seed 20261018 --output "$runPath" --resume
```

## 무엇을 시험하는가

- 기본 1,000개의 서로 다른 원본 이름에서 질의를 생성합니다.
- 정확 이름 100, 1회 오타 200, 2회 오타 150, 단어 생략 250, 생략+오타 100, 정답 제품 부재 200입니다.
- 부재 시험은 정답 제품만 메모리의 검색 대상에서 제외합니다. DB를 삭제하지 않습니다.
- 각 질의에 대해 제조사를 완벽히 아는 조건/모르는 조건을 각각 평가합니다. 총 2,000회의 검색 조건 평가입니다.
- 생략 검색은 온전한 공백 구분 구절을 포함하는 모든 제품을 먼저 조회하고 제조사를 비교합니다.
- 오타/생략+오타는 부분 구간 편집 거리 없이 전체 이름을 비교합니다.
- 점수는 `100 × (1 − Damerau–Levenshtein 거리 / 긴 이름 길이)`입니다. NFC·casefold·공백 제거를 사용하며 제품명 단어·숫자·문장부호는 임의 삭제하지 않습니다.
- 기준 이상인 제품이 정확히 하나면 연결합니다. 두 번째 점수까지 보관하면 이 조건을 모든 임계값에서 정확히 판정할 수 있으므로 전체 후보 목록을 매번 저장하지 않습니다.
- 개발 60%에서만 기준을 선택하고 분리된 테스트 40%에서 평가합니다. 동일 정규화 원본 이름은 양쪽에 겹치지 않습니다.
- 기본 정밀도 목표 99%, 최소 개발 연결 30건, 점수 탐색 간격 0.5점은 **실험 정책값**이며 문헌에서 보장한 수치가 아닙니다.
- 생략/오타 및 제조사 확인 여부별로 다른 기준을 보고합니다. 조건을 충족하지 못하면 추천값은 null입니다.

## 결과 파일

`metadata.json`, `trials.jsonl`, `scored_cases.jsonl`, `progress.json`, `summary.json`, `threshold_sweep.json`, `report.md`, `stdout.log`, `stderr.log`, `stdin.empty`, `launch.json`.

추천값은 합성 질의의 결과입니다. 오타 분포, 제조사 추출 오류, 실제 광고 표현은 충분히 반영하지 못합니다. 실제 광고 정답 자료로 검증하기 전 운영 자동 매핑에 적용하지 않습니다. 원래부터 구별할 수 없는 동명 제품이 있어 임계값이 높아도 연결이 불가능한 경우가 있습니다.

이 작업은 제품 식별 실험이며 Claim–Evidence 검색/최종 판정 기능은 실행하지 않습니다.
