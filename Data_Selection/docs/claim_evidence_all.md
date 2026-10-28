# 전체 Claim–Evidence 연결 작업

대상: `claims_all.json`의 영상 216개, Claim 3,400개. 100개 시험과 같은 제품 식별·원료 후보 검색·BGE-reranker-v2-m3 재정렬 방식을 사용한다. 원본 Claim 파일과 SQLite DB는 변경하지 않는다.

2026-10-26 후보 준비 결과: 제품 식별 성공 Claim 2,427개. 제품 자료 또는 원료 참고자료 후보가 있는 Claim 3,035개, 후보 없음 365개. 이 수치는 근거 충분성이나 참·거짓 판정이 아니다.

전체 후보 연결 121,331건은 중복 입력쌍을 합치면 82,542개다. 기존 시험에서 측정한 2,913쌍을 재사용하고 새 79,629쌍을 계산한다. 최초 시작 시의 수치이며 중단 후 재개하면 남은 수가 줄어든다. 공개 모델 파일도 로컬 캐시를 사용하므로 새 다운로드·외부 유료 API 호출이 없다.

## 상태 확인

폴더: `data/processed/claim_evidence_all/`

- `full_run_status.json`: 작업 PID·전체 작업 단계. **status=complete일 때만** 파일 생성과 검증까지 끝난 상태다. failed라면 error와 로그를 확인한다.
- `progress.json`: 실제 재정렬 점수 계산 진행 상황. total_scored_pairs는 재사용 캐시를 포함하고, pending_pairs는 아직 계산하지 않은 새 쌍이다. 이 파일의 complete는 점수 계산 완료를 뜻하며 전체 전달 파일 생성 완료와 구분한다.
- `stdout.log`, `stderr.log`: 실행 로그.

```powershell
Get-Content data/processed/claim_evidence_all/full_run_status.json -Encoding UTF8
Get-Content data/processed/claim_evidence_all/progress.json -Encoding UTF8
Get-Content data/processed/claim_evidence_all/stdout.log -Encoding UTF8 -Tail 5
```

## 실행·재개

```powershell
.\scripts\start_all_claim_mapping.ps1 -InputPath "C:\Users\박이정\Documents\카카오톡 받은 파일\claims_all.json" -Threads 4 -BatchSize 4
```

숨김 백그라운드 프로세스로 실행하며 실행 중인 작업이 있으면 중복 시작하지 않는다. 로컬 CPU를 사용하므로 수 시간이 걸릴 수 있다. 컴퓨터가 종료되거나 절전 상태가 되면 진행되지 않는다. 중단 후 같은 명령으로 재개할 수 있으며 측정한 점수는 SQLite 캐시에 저장돼 있다.

점수 계산이 끝나면 자동으로 전달 파일을 만들고, 전체 3,400개 Claim 포함 여부·순위·빈 근거 표시·제품 식별 실패 시 제품 자료 제외·최종 verdict 미작성·입력 파일 해시를 검증한다. 완료를 확인하려면 full_run_status.json을 본다.

## 완료 시 생성되는 결과

- `claim_evidence_ranked.json`: 모든 근거 후보의 점수 내림차순 순위.
- `top1_handoff.json`, `top3_handoff.json`, `top5_handoff.json`: 최대 K개 전달용 JSON. 근거가 없으면 빈 목록이며 충분성·최종 판정은 수행하지 않는다.
- `review_top5.md`: Claim별 상위 5개 원문·출처·점수를 비교하는 검토표.
- `summary_review.json`: 제품 식별·후보 유무·K별 연결 건수 통계.

relationship 라벨은 product_direct(식별된 제품의 DB 직접 자료), ingredient_reference(원료 자체의 참고자료)다. 제품 식별 실패 시 그 제품 후보의 자료를 자동 연결하지 않는다. 원료 참고자료는 제품에 실제 함유된 증거로 간주하지 않는다. PDF 방식대로 별도 관련성 임계값은 적용하지 않으며, 낮은 관련성 후보가 포함될 수 있다. 점수는 참·거짓 확률이 아니다.
