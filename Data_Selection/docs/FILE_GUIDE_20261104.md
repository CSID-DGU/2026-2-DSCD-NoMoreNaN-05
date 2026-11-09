# 작업 파일 안내 — 2026-11-04

경로 기준: `C:\Users\박이정\Desktop\DSCD_NNN`.
이 문서는 작업 중 생성한 결과/코드와 보관한 입력 자료를 구분하기 위한 안내임.
입력 CSV와 팀원의 Claim 원본은 assistant가 새로 작성한 데이터가 아님.

## 1. 실제 DB와 원본 자료

| 경로 | 용도 |
|---|---|
| `TRUEAD_DB_보강자료/claim_verification.sqlite` | 최신 보강 SQLite. 제품 46,846건. CSV로 681건 추가, 빈칸 3건 보충, 컬럼 20개 추가. 알려진 일부 분류 연결 이슈는 아직 수정 전. |
| `TRUEAD_DB_보강자료/data_collection/` | 서버에서 받은 원본 CSV・PDF・MD 등 보강 자료. 원문 보관본. |
| `Data_List_Claim_Verification/claim_verification.sqlite` | 보강 전 기존 DB. 최신 보강본과 구분해야 함. |
| `Data_List_Claim_Verification/claim_verification_browser.sqlite` | 이전에 만든 열람용 DB. 현재 보강본으로 간주하지 말 것. |
| `data/processed/external_product_enrichment_20261102/claim_verification_enriched.sqlite` | 11월 2일 외부 제품 자료 보강 실험본. 11월 3일 MD 기준 보강본과 별개. |

## 2. 최초 타입별 전달본 — 11월 3일

폴더: `exports/claim_type_db_20261103/`

| 파일/폴더 | 용도/주의사항 |
|---|---|
| `claims_with_db.json` | 535영상, 1,302제품 항목, 8,728 Claim. ETC도 포함. confirmed 89제품에만 DB 객체를 넣었기 때문에 ETC 제외 시 DB가 있는 Claim이 626개뿐인 이전 전달본. |
| `videos/` | 위 내용을 영상별 JSON 535개로 나눈 것. |
| `summary.json` | 위 파일의 개수・상태별 집계. |
| `README.md` | 생성 방식・자료 범위・제한 설명. |
| `video_jsons.zip` | 영상별 JSON과 집계의 압축본. |
| `TRUEAD_DB_enrichment_outputs_20261103.zip` | 당시 전달 JSON・보고서・명세 등을 모은 결과 패키지. |
| `reports/` | CSV 사전 점검・보강 계획・검증 보고서 사본. |
| `specifications/` | 작업 기준으로 받은 MD 두 개의 사본. |

`TRUEAD_DB_보강자료/작업결과_20261103/`은 위 폴더를 복사해 둔 보관본이며 별도 재생성 결과가 아님.

## 3. ETC 제외와 보수적인 1차 분류 — 11월 4일

폴더: `exports/preliminary_labels_20261104/`

| 파일 | 용도 |
|---|---|
| `claims_without_etc.json` | 원래 전달본에서 ETC 1,241개만 제외한 7,487 Claim. **제품 연결/DB 누락은 수정하지 않은 사본.** |
| `claims_labeled_preliminary.json` | 위 Claim에 규칙 기반 임시 라벨・사유・근거를 추가한 것. GPT/NLI 전수 판정이 아님. |
| `labels_flat.json` | 임시 판정 결과를 Claim 한 행씩 펼친 검토용 형태. |
| `excluded_etc.json` | 제외된 ETC 1,241개의 원문과 영상 ID. |
| `summary.json` | 1차 분류 집계. |
| `README.md` | 분류 방식과 제한. |

## 4. DB 근거를 읽고 다시 본 결과

폴더: `exports/semantic_review_20261104/`

| 파일 | 용도 |
|---|---|
| `reviewed_537.json` | 실제로 의미 재검토한 537 Claim의 원문・이전/새 라벨・이유・DB 근거. 제품 연결이 맞다는 전제의 assistant 판단. |
| `changed_claims.json` | 재검토로 라벨이 바뀐 310개. |
| `claims_reassessed.json` | 전체 7,487 Claim 중 537개에만 재검토를 반영한 파일. 나머지 6,950개는 1차 분류 유지. 제품 매핑을 고친 전달본이 아님. |
| `summary.json` | 재검토 전후/전체 집계 및 조건 차이. |
| `README.md` | 검토 범위・해석 기준・제한. |

위 두 분류 폴더의 파일은 Mechanism A/B의 실측 결과나 사람이 만든 정답 라벨이 아님.

## 5. 후보 DB를 빠짐없이 포함한 새 전달본 v2

폴더: `exports/candidate_db_handoff_20261104/`

| 파일 | 용도 |
|---|---|
| `claims_with_db.json` | ETC 제외 7,487 Claim. 제품 후보 1,061항목의 각 후보 행에 타입별 DB를 넣음. 501개 중 429개(85.63%)의 기존 후보 검색 범위를 포함함. 5,969 Claim에 후보 DB 연결. |
| `claim_candidate_index.json` | Claim별로 연결된 후보 product_id 목록과 제품 참조 실패 여부를 모은 가벼운 색인. |
| `summary.json` | 후보 연결 범위・개수・원본/DB 해시. |
| `README.md` | 수신 코드 수정 방법과 읽기 예제. |

**중요:** v2는 `match.status = matched / not_found`를 사용하고 실제 후보 근거는
`products[].candidate_products[].DB`에 있음. `confirmed`만 통과시키던 기존 코드는 수정해야 함.
최상위 `product.DB`가 null이어도 후보마다 DB가 있을 수 있음.
복수 후보를 모두 넘기는 형식이므로 제품 선택까지 완료된 판정 전용 입력과는 다름.
A/B 코드와의 통합 검증은 아직 하지 않았음. 그대로 교체하면 호환된다고 보장할 수 없음.
선택된 제품과 미선택 후보의 분담을 확정한 뒤 수신 코드에서 처리해야 함.

## 6. 매핑률을 계산했던 중간 결과

| 폴더 | 용도 |
|---|---|
| `data/processed/product_functionality_handoff_claim_identity/` | 기존 DB에서 501개 중 332개(66.27%)의 제품 그룹을 선택한 결과. mapped_products.json 등에 기능성 원문을 보존함. selected와 confirmed는 다름. |
| `data/processed/md_enrichment_20261103/mapping_claim_identity/` | 보강 DB에서 510개 중 337개(66.08%)를 선택한 결과. 후보 검색은 435개(85.29%). 전체 브랜드 존재 기준으로는 501개 중 429개. |
| `data/processed/product_functionality_handoff_y_final_brand_company/source_input.json` | 용빈님에게 받은 claims_all_y_final.json을 보관한 원본 입력 사본. |
| `data/processed/claim_json_feedback_audit/` | 팀원의 다섯 가지 피드백을 확인한 읽기 전용 점검 결과. |
| `data/processed/md_enrichment_20261103/` | 보강 전후 비교・추가/유지/빈칸 보충・원료 충돌 보류 등 보강 작업 기록과 중간 매핑 결과. |
| `data/processed/semantic_review_20261104/reviewable.json` | 의미 재검토용으로 고정한 537개 문장과 해당 제품 DB 자료. |

중간 결과의 공통 파일명:

- `product_matches.json`: 제품별 검색 후보・경로・선택 결과・식별 정보.
- `all_results.json`: 선택 성공/실패를 모두 포함한 중간 결과.
- `mapped_products.json`: 제품 그룹이 선택된 항목. 반드시 confirmed라는 뜻은 아님.
- `unmapped_products.json`: 그 실행에서 제품 그룹을 선택하지 못한 항목.
- `new_matches.json`, `newly_mapped_products.json`: 해당 단계에서 새로 선택된 항목.
- `claim_identity_audit.json`: Claim의 제조원/판매원 등 선언을 이용한 추가 식별 기록.
- `source_input.json`, `input_brand_present.json`: 해당 실험의 입력 사본/전처리본.
- `summary.json`: 그 폴더 실행에 대한 집계. 다른 폴더의 분모와 혼용하면 안 됨.

## 7. 백업・서버 전달

- `.publish-repo/`: GitHub 게시용 별도 체크아웃. 평소 실행 폴더와 구분.
- `.publish-repo/Data_Selection/workspace_snapshots/20261103T091656Z/`: 11월 3일 전체 작업 백업. ZIP 분할 파일 14개와 해시 명세.
- `docs/SERVER_HANDOFF_20261103.md`: 기존 공유 서버 폴더와 겹치지 않도록 clone/복원/환경 설정하는 안내.
- `scripts/restore_workspace_snapshot.py`: 분할 백업을 해시 검증 후 빈 폴더에 복원하는 코드.

GitHub에 올렸다고 확인한 마지막 커밋은 `29bc896`(data-selection)임.
11월 4일에 새로 만든 임시 라벨/의미 재검토/후보 DB v2 파일과 코드는 아직 별도 push하지 않았음.

## 8. 과거 실험 폴더

`real`, `t70`, `recovered`, `y_final`, `brand_present`, `name_first`가 붙은 폴더들은
입력 파일・유사도 기준・회사 비교・복구 규칙을 바꾸며 보존한 각각의 실험 결과임.
`claim_evidence_pilot100`, `claim_evidence_all`은 이전 BGE 근거 재순위 실험이며 현재 전달본과 별개임.
`postgres_snapshot_20261028`, `truead_database_bundle_20261007_233328`은 과거 DB 백업임.
이 파일들의 집계를 최신 전달본의 개수와 섞으면 안 됨.

## 9. 실행 코드・테스트・문서 전체 목록

아래 목록은 현재 폴더의 코드와 문서를 실제로 스캔해 추가한 것임.
테스트 파일은 대응 코드의 동작 검증용이며 전달 JSON 자체가 아님.

### scripts

- scripts/apply_name_first_product_groups.py: Apply user's name-first/report-fallback policy to the latest saved product search.
- scripts/apply_semantic_claim_review.py: Apply explicit assistant review decisions; no API calls or source rewrites.
- scripts/audit_claim_json_feedback.py: Read-only audit of the five feedback items; never rewrites DB or handoff.
- scripts/audit_claim_mapping.py: Read-only coverage audit for a supplied claim extraction sample, not a verdict engine.
- scripts/audit_real_product_unmatched.py: Explain latest no-candidate results and measure proposed searches without applying them.
- scripts/build_claim_verification_db.py: Build the local SQLite database used to verify health-functional-food claims.
- scripts/build_nem_claim_handoff.py: DB-grounded NEM case example; reviewed source routes, lexical TF-IDF scores.
- scripts/build_recovery_metadata.py: Read existing public video metadata/OCR caches for a fresh mapping run.
- scripts/calibrate_product_name_thresholds.py: Read-only, synthetic product-name matching calibration; never a production cutoff.
- scripts/check_postgres.py: Check local PostgreSQL connectivity without modifying data.
- scripts/collect_diseases.py: Collect HIRA disease names and codes; raw XML and normalized JSONL are stored separately.
- scripts/collect_domestic_product_refresh.py: Fetch resumable current MFDS detail pages; credentials never logged.
- scripts/collect_food_ingredients.py: Placeholder for a future official-data collector; no API requests yet.
- scripts/collect_functional_ingredients.py: Placeholder for a future official-data collector; no API requests yet.
- scripts/collect_health_food_businesses.py: Placeholder for a future official-data collector; no API requests yet.
- scripts/collect_individually_approved.py: Placeholder for a future official-data collector; no API requests yet.
- scripts/collect_mfds_products.py: Collect all MFDS health functional food list and detail pages.
- scripts/collect_mmce_benchmark.py: Collect joycelynt/MMCE as a test-only visual claim extraction benchmark.
- scripts/collect_product_ingredients.py: Placeholder for a future official-data collector; no API requests yet.
- scripts/collect_youtube_urls.py: Collect YouTube health-functional-food ad candidate URLs and metadata; never downloads video files.
- scripts/compare_domestic_product_refresh.py: Compare a complete official refresh with the existing read-only SQLite DB.
- scripts/compare_higher_product_threshold.py: Replay a higher name cutoff using complete >=70 candidates and the same recovery rules.
- scripts/compare_product_identity_filters.py: Compare saved baseline with factory-normalized product matching; no models/API.
- scripts/disambiguate_product_candidates.py: Narrow saved multiple product candidates using manufacturer evidence.
- scripts/download_video.py: Download one anonymously accessible video to the project's MP4 directory.
- scripts/enrich_db_from_md.py: Enrich the explicitly supplied DB in place, after a read-only plan.
- scripts/evaluate_relaxed_product_mapping.py: Product-level candidate coverage with explicitly relaxed identity requirements.
- scripts/export_70_candidate_functionality.py: Export all 70-point candidate-connected name/brand groups with original functionality.
- scripts/export_brand_present_handoff.py: Exclude products with missing brand_name and export existing brand-based matches.
- scripts/export_candidate_db_handoff.py: Export DB evidence for ALL retrieved products, without identity-status gating.
- scripts/export_claim_type_db_json.py: Write one video JSON per input video plus a combined file, preserving effect.
- scripts/export_database_bundle.py: Portable SQLite snapshots, PostgreSQL dump and KIPRIS source XML.
- scripts/export_paused_claim_mapping.py: Export saved scores after a user-requested stop. Does not load/run any model.
- scripts/export_product_company_names.py: Export product/company pairs without changing the source SQLite database.
- scripts/export_product_functionality_handoff.py: Export original video claims plus database product functionality; no inference.
- scripts/export_table_definition_excel.py: Export the claim-verification SQLite table definition to an Excel workbook.
- scripts/fetch_recovery_thumbnails.py: Fetch public thumbnails only for cached missing-product-name videos.
- scripts/filter_youtube_ads.py: Run conservative YouTube rule filtering and optional LLM ad classification.
- scripts/find_manufacturer_pair_candidates.py: Mine review-only manufacturer pairs from product records; no alias rules applied.
- scripts/inspect_md_enrichment_sources.py: Read-only inspection of the CSV inputs required by the enrichment guide.
- scripts/label_claims_preliminary.py: Conservative, offline first-pass labels under the supplied Mechanism A PDF.
- scripts/map_claim_products.py: Map any video/claims JSON using the established rules and export functionality.
- scripts/migrate_sqlite_to_postgres.py: Copy original SQLite tables into isolated PostgreSQL schemas atomically.
- scripts/ocr_recovery_thumbnails.ps1: 실행/처리 코드
- scripts/package_md_handoff.py: Package verified outputs; optionally copy them beside the user-supplied DB.
- scripts/prepare_github_snapshot.py: Create a credential-scrubbed, split workspace archive and publish code copy.
- scripts/probe_external_product_sources.py: Probe official public sources without logging authenticated request URLs.
- scripts/probe_import_api.py: Probe access to the official imported-food labeling API, without key logs.
- scripts/probe_import_search.py: Check the public imported-food search form using its documented UI fields.
- scripts/recover_identity_from_claims.py: Recheck saved unmapped products using their own claims; preserve all originals.
- scripts/recover_product_candidates.py: Add traceable notation/abbreviation/context candidates to a saved mapping.
- scripts/restore_workspace_snapshot.py: Verify and restore a split GitHub workspace snapshot into an empty folder.
- scripts/run_all_claim_mapping.py: Run the full mapping job, export handoffs and validate before marking complete.
- scripts/run_claim_evidence_pilot.py: Prepare, score and resume a PDF-based Claim/Evidence pilot without DB writes.
- scripts/run_youtube_search_99.py: Run/resume the reviewed 99-product manifest using the normal API budgets.
- scripts/search_unmatched_76.py: Search every unmatched named product without a cutoff; report only, no mapping changes.
- scripts/start_all_claim_mapping.ps1: 실행/처리 코드
- scripts/start_product_name_calibration.ps1: 실행/처리 코드
- scripts/summarize_claim_evidence_pilot.py: Build compact Top-K handoffs and a human review table from measured ranks.
- scripts/summarize_declaration_gated_availability.py: Count source availability under explicit video product-composition gating.
- scripts/test_kipris_live.py: Run one complete live KIPRIS keyword collection without logging credentials.
- scripts/video_url_mode.py: Accept bare video URLs, save MP4s to the Windows Desktop, and open them.

### src

- src/__init__.py: 실행/처리 코드
- src/claim_evidence_experiment.py: Product identity and source-grounded candidate preparation following the supplied PDF.
- src/claim_product_identity.py: Extract explicit, product-scoped identity declarations without an LLM.
- src/claim_type_db_format.py: Strict output schema from claim_type_db_format.md; never classify claims.
- src/company_comparison.py: Keep the chosen input company field explicit; never silently switch fields.
- src/md_db_enrichment.py: Exact-key enrichment rules transcribed from db_enrichment_guide.md.
- src/product_identity_filtered.py: Product-only matching with auditable company-site suffix normalization.
- src/product_name_groups.py: Same normalized product name + approved manufacturer group, independent of reports.

### tests

- tests/test_brand_company_comparison.py: 대응 코드의 동작 검증
- tests/test_brand_present_handoff.py: 대응 코드의 동작 검증
- tests/test_candidate_db_handoff.py: 대응 코드의 동작 검증
- tests/test_claim_evidence_experiment.py: 대응 코드의 동작 검증
- tests/test_claim_evidence_handoff.py: 대응 코드의 동작 검증
- tests/test_claim_product_identity.py: 대응 코드의 동작 검증
- tests/test_claim_type_db_format.py: 대응 코드의 동작 검증
- tests/test_collect_youtube_ads.py: 대응 코드의 동작 검증
- tests/test_diseases.py: 대응 코드의 동작 검증
- tests/test_ingredient_declaration_gate.py: 대응 코드의 동작 검증
- tests/test_kdca_raw.py: 대응 코드의 동작 검증
- tests/test_kipris_cache.py: 대응 코드의 동작 검증
- tests/test_kipris_raw.py: 대응 코드의 동작 검증
- tests/test_map_claim_products.py: 대응 코드의 동작 검증
- tests/test_md_db_enrichment.py: 대응 코드의 동작 검증
- tests/test_mfds_products.py: 대응 코드의 동작 검증
- tests/test_preliminary_labels.py: 대응 코드의 동작 검증
- tests/test_product_disambiguation.py: 대응 코드의 동작 검증
- tests/test_product_functionality_handoff.py: 대응 코드의 동작 검증
- tests/test_product_identity_filtered.py: 대응 코드의 동작 검증
- tests/test_product_name_calibration.py: 대응 코드의 동작 검증
- tests/test_product_name_groups.py: 대응 코드의 동작 검증
- tests/test_product_recovery.py: 대응 코드의 동작 검증
- tests/test_relaxed_product_mapping.py: 대응 코드의 동작 검증
- tests/test_workspace_snapshot.py: 대응 코드의 동작 검증
- tests/test_youtube_ad_filter.py: 대응 코드의 동작 검증
- tests/test_youtube_candidate_collector.py: 대응 코드의 동작 검증

### configs

- configs/embedding.yaml: 설정 데이터
- configs/manufacturer_pairs.json: 설정 데이터
- configs/youtube_search_keywords.yaml: 설정 데이터

### docs

- docs/claim_evidence_all.md: 전체 Claim–Evidence 연결 작업
- docs/claim_evidence_mapping_design.md: TRUEAD Claim–Evidence 매핑 설계 및 실제 DB 조회 사례
- docs/claim_evidence_pilot100.md: Claim 100개 제품 식별 및 Evidence 순위 시험
- docs/claim_mapping_audit.json: 설명/실험 결과 자료
- docs/claims_real_unmatched_diagnosis.md: 새 입력 미연결 제품 사유 분석
- docs/github_workspace_backup.md: GitHub 작업 기록 및 DB 백업
- docs/gnm_claim_mapping_example.json: 설명/실험 결과 자료
- docs/ingredient_search_gate.md: 원료 근거 검색 조건 변경
- docs/kipris_evidence_cache.md: KIPRIS 보조 근거 캐시
- docs/manufacturer_pair_review.md: 제조사 검색용 PAIR 검토 목록
- docs/nem_claim_evidence_handoff.json: 설명/실험 결과 자료
- docs/postgresql_embedding_notion.md: TRUEAD 데이터베이스 이전 및 임베딩 검색 준비
- docs/product_candidate_disambiguation.md: 복수 제품 후보의 제조사 비교 결과
- docs/product_functionality_handoff.md: 제품 기능성 전달 JSON
- docs/product_functionality_handoff_real.md: claims_all_real.json 제품 매핑 및 전달 JSON
- docs/product_identity_approved_pairs.md: 승인 제조사 PAIR 적용 결과
- docs/product_identity_filtered.md: 제품명·제조사 표기 정리 비교
- docs/product_mapping_y_final.md: claims_all_y_final.json 제품 매핑
- docs/product_name_calibration.md: 제품명 임계값 백그라운드 실험
- docs/product_name_first_grouping.md: 제품명 우선·신고번호 보조 규칙
- docs/product_name_threshold_audit.json: 설명/실험 결과 자료
- docs/product_recovery_t70.md: 70점 검색 이후 표기·축약·누락 이름 보완
- docs/SERVER_HANDOFF_20261103.md: 서버에서 기존 작업과 분리하여 사용하기
- docs/truead_claim_verification_erd.png: 설명/실험 결과 자료
- docs/truead_claim_verification_flow.png: 설명/실험 결과 자료
- docs/truead_data_architecture_erd.png: 설명/실험 결과 자료
- docs/youtube_ad_filtering.md: YouTube 광고 URL 확정 절차
- docs/youtube_ads_smoke_test.json: 설명/실험 결과 자료
- docs/youtube_product_name_smoke_test.json: 설명/실험 결과 자료
- docs/youtube_review_candidates.md: YouTube candidates requiring review
- docs/youtube_search_99_manifest.json: 설명/실험 결과 자료
- docs/youtube_search_99_summary.json: 설명/실험 결과 자료
- docs/youtube_search_batch002_manifest.json: 설명/실험 결과 자료
- docs/youtube_search_batch002_summary.json: 설명/실험 결과 자료
