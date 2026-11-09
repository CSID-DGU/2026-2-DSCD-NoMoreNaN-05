# DB 보강 지침

너는 식약처 공공데이터 CSV로 기존 SQLite DB의 `products` 테이블을 보강한다. 이 문서의 규칙을 그대로 따르고, 문서에 없는 판단이 필요하면 추측하지 말고 사용자에게 묻는다.

경로는 모두 `No-More-NaN-shared/` 기준이다.

| 항목 | 값 |
|---|---|
| 기준 DB | `/home/yongbin53/DataScience-Capstone/No-More-NaN-shared/TRUEAD_DB_20261010/full_copy/backup_extracted/Data_List_Claim_Verification/claim_verification.sqlite` |
| 원본 CSV 폴더 | `/home/yongbin53/DataScience-Capstone/No-More-NaN-shared/data_collection` |
| 제품 연결 키 | `products.manufacturing_report_number` = I0030 `PRDLST_REPORT_NO` |
| 업체 연결 키 | I0030 `LCNS_NO` = 각 파일의 `LCNS_NO` |

## 1. 반드시 지킬 규칙

1. **DB 값을 우선한다.** 같은 의미의 필드에서 값이 다르면 DB 값을 유지하고, 차이는 건수와 예시만 보고한다.
2. **필드명으로 판단하지 않는다.** 이름이 달라도 같은 의미일 수 있고, 이름이 같아도 다른 의미일 수 있다. 표 3, 4에 없는 필드는 2번 절차로 판별한다.
3. **원본 값을 그대로 넣는다.** 값을 다듬거나 요약하지 않는다. 정규화는 비교할 때만 쓴다.
4. **추측으로 채우지 않는다.** 번호나 정확한 이름으로 연결되지 않으면 비워 둔다. 유사도 매칭과 업체명만으로 하는 연결은 금지한다.
5. **기준 DB 원본에 직접 추가한다.** 복사본을 만들지 않는다. 기존 컬럼의 값은 바꾸거나 지우지 않고, CSV 원본에는 쓰지 않는다.
6. **결과를 꾸미지 않는다.** 실패, 연결되지 않은 건, 건너뛴 작업을 그대로 보고한다.

## 2. 작업 순서

1. 8번의 미정 항목을 사용자에게 묻고 답을 받는다. 답을 받기 전에는 쓰기 작업을 하지 않는다.
2. 이 문서에 나온 파일과 컬럼이 실제로 있는지 확인한다. 없으면 멈추고 보고한다.
3. 표 3의 필드를 비교해 차이를 집계한다. 값은 바꾸지 않는다.
4. 5, 6번 규칙으로 필드를 기준 DB에 추가한다.
5. 7번 항목을 검증하고 결과를 보고한다.

**새 필드를 판별하는 절차.** 이 문서에 없는 CSV나 필드를 발견하면 아래 순서로 확인하고, 넣기 전에 사용자에게 보고한다.

| 순서 | 확인 | 판단 |
|---|---|---|
| 1 | 연결 키로 행을 맞춘다 | 키가 맞지 않으면 값 비교를 하지 않는다 |
| 2 | 공백을 지우고 일치율을 구한다 | 대부분 일치하면 같은 필드 후보 |
| 3 | 값이 DB 컬럼 안에 포함되는지 본다 | 포함되면 같은 정보가 문장 속에 있는 것 |
| 4 | 값이 다른 행을 직접 읽는다 | 의미가 다르면 일치율이 높아도 새 필드 |
| 5 | 값의 종류와 채움률을 본다 | 값이 1종이거나 비어 있으면 넣지 않는다 |

글자 비교는 뜻이 같고 표현이 다른 경우를 잡지 못한다. 일치율이 낮아도 곧바로 새 정보로 판단하지 말고 표본을 읽는다.

**CSV 읽기.** 인코딩은 `utf-8-sig`, 모든 값은 문자열로 읽는다. 셀 안에 줄바꿈이 많으므로 `wc -l`로 행 수를 세지 말고 CSV 파서를 쓴다. `I2500.csv`는 약 155만 행이므로 스트리밍으로 읽는다.

## 3. 같은 의미의 필드 (추가 금지, DB 유지)

아래 필드는 새 컬럼으로 추가하지 않는다. 건수는 2026-11-02 기준 공통 제품 45,437건의 참고값이며, 다시 집계해 보고한다.

| DB 컬럼 | 건강기능식품정보 | I0030 | C003 | 값이 다른 건수 | DB만 빈칸인 건수 |
|---|---|---|---|---:|---:|
| `product_name` | `PRDUCT` | `PRDLST_NM` | `PRDLST_NM` | 126 | 0 |
| `company_name` | `ENTRPS` | `BSSH_NM` | `BSSH_NM` | 665 | 0 |
| `manufacturing_report_number` | `STTEMNT_NO` | `PRDLST_REPORT_NO` | `PRDLST_REPORT_NO` | 키 | 0 |
| `registration_date` | `REGIST_DT` | 없음 | `CRET_DTM` | 0 | 0 |
| `main_functionality` | `MAIN_FNCTN` | `PRIMARY_FNCLTY` | `PRIMARY_FNCLTY` | 19 | 0 |
| `intake_method` | `SRV_USE` | `NTK_MTHD` | `NTK_MTHD` | 28 | 0 |
| `intake_precautions` | `INTAKE_HINT1` | `IFTKN_ATNT_MATR_CN` | `IFTKN_ATNT_MATR_CN` | 83 | 2 |
| `specification` | `BASE_STANDARD` | `STDR_STND` | `STDR_STND` | 197 | 0 |
| `appearance` | `SUNGSANG` | `DISPOS` | `DISPOS` | 102 | 0 |
| `shelf_life` | `DISTB_PD` | `POG_DAYCNT` | `POG_DAYCNT` | 44 | 0 |
| `storage_and_distribution_standard` | `PRSRV_PD` | `CSTDY_MTHD` | `CSTDY_MTHD` | 51 | 1 |

건강기능식품정보 파일은 `data_collection/식품의약품안전처_건강기능식품정보/mfds_health_functional_food_products_20261031.csv`이고, 신고번호는 `STTEMNT_NO`다. 건수는 이 파일 값으로 계산했다. I0030, C003은 DB와 직접 비교하지 않았다.

`I2860.csv`의 `SITE_ADDR`은 I2500 `ADDR`과 같으므로 넣지 않는다. C003은 I0030과 내용이 같으므로 사용하지 않는다.

## 4. 이름이 비슷해도 다른 필드

| 필드 | 주의할 점 |
|---|---|
| `registration_date`와 I0030 `PRMS_DT` | 앞은 데이터 등록일, 뒤는 품목 허가일이다. 4,657건이 다르므로 `PRMS_DT`를 새 필드로 넣는다 |
| I0030 `PRMS_DT`와 I2500 `PRMS_DT` | 품목 허가일과 업체 인허가일이다. I2500 값은 `BSSH_PRMS_DT`로 이름을 바꾼다 |
| C003 `RAWMTRL_NM`과 I0030 `RAWMTRL_NM` | C003은 전체 원재료, I0030은 품목유형(기능지표성분)이다. I0030 값을 원재료로 쓰지 않는다 |
| I2710과 "고시형" | I2710에는 개별인정 원료도 있다. 인정번호 유무로 구분한다 |

## 5. 추가할 필드

| 필드 | 출처 파일 (`data_collection/` 아래) | 연결 |
|---|---|---|
| `LCNS_NO`, `PRMS_DT`, `LAST_UPDT_DTM`, `INDUTY_CD_NM`, `PRDLST_CDNM`, `RAWMTRL_NM`, `INDIV_RAWMTRL_NM`, `ETC_RAWMTRL_NM`, `CAP_RAWMTRL_NM`, `PRDT_SHAP_CD_NM`, `FRMLC_MTRQLT`, `FRMLC_MTHD` | `건강기능식품 품목제조 신고사항 현황/I0030.csv` | 신고번호 |
| `BSSH_ADDR` (원본 `ADDR`), `BSSH_PRMS_DT` (원본 `PRMS_DT`) | `인허가 업소(GMP)/I2500.csv` | `LCNS_NO` |
| `INSTT_NM` | `먹는 콜라겐 제품등록 현황/mfds_eating_collagen_products_20261031.csv` | `LCNS_NO`. 같은 업체의 모든 제품에 넣는다 |
| `BSSH_CHNG_HIST` | `건강기능식품업소 인허가 변경 정보/I2860.csv` | `LCNS_NO` |
| `RAWMTRL_STD_INFO` | `건강기능식품 품목분류정보/I2710.csv`, `건강기능식품 개별인정형 정보/I-0050.csv` | 6번 규칙 |
| `RAWMTRL_CLASS_INFO` | `건강기능식품 영양DB/I0760.csv` | I0030 `RAWMTRL_NM`의 원료명 |
| `RAWMTRL_DICT_INFO` | `식품의약품안전처_식품 원재료 정보/mfds_food_raw_materials_20261031.csv` | I0030 `INDIV_RAWMTRL_NM`의 원료명 |
| `RECALL_INFO` | `회수·판매중지 정보/I0490.csv` | 신고번호만. 이름으로 연결하지 않는다 |

`BSSH_CHNG_HIST`부터 `RECALL_INFO`까지 5개는 제품 하나에 값이 여러 개일 수 있어 JSON 배열로 넣는다. 연결이 없으면 비워 둔다.

| JSON 필드 | 항목 |
|---|---|
| `BSSH_CHNG_HIST` | `CHNG_DT`, `LCNS_LEDG_CI_CDNM`, `CHNG_BF_CN`, `CHNG_AF_CN` |
| `RAWMTRL_STD_INFO` | 6번 표 참고 |
| `RAWMTRL_CLASS_INFO` | `HELT_ITM_GRP_CD`, `HELT_ITM_GRP_NM`, `LCLAS_CD`, `LCLAS_NM`, `MLSFC_CD`, `MLSFC_NM`, `SCLAS_CD`, `SCLAS_NM` |
| `RAWMTRL_DICT_INFO` | `LCLAS_NM`, `MLSFC_NM`, `RPRSNT_RAWMTRL_NM`, `RAWMTRL_NCKNM`, `ENG_NM`, `SCNM`, `REGN_CD_NM`, `RAWMTRL_STATS_CD_NM`, `USE_CND_NM` |
| `RECALL_INFO` | `PRDTNM`, `RTRVLPRVNS`, `RTRVL_GRDCD_NM`, `RTRVLPLANDOC_RTRVLMTHD`, `MNFDT`, `DISTBTMLMT`, `FRMLCUNIT`, `BRCDNO`, `IMG_FILE_PATH`, `CRET_DTM` |

**넣지 않는 데이터**

| 데이터 | 이유 |
|---|---|
| I0030 `HIENG_LNTRT_DVS_NM`, `PRODUCTION` | 값이 1종뿐이다 |
| I0030 `CHILD_CRTFC_YN`, C003 `SHAP` | 값이 없다 (`SHAP`은 2건만 있음) |
| `HACCP 적용업소/I0580.csv` | 인허가번호가 겹치지 않고, 업종·품목에 건강기능식품이 없다 |
| `행정처분결과/I0470.csv`, `식품의약품안전처_건강기능식품판매업/I1290.csv` | 인허가번호가 겹치지 않는다. 이름만 같은 행은 다른 업체일 수 있다 |

## 6. 원료 연결 규칙

정규식은 Python 기준이다.

| 항목 | 규칙 |
|---|---|
| 원료 분리 | `re.split(r',(?![^()]*\))', 값)` 후 앞뒤 공백 제거 |
| 인정번호 추출 | `re.search(r'(\d{4})\s*-\s*(\d+)', 값)` → `연도-정수`. 예: `(제2023-05호)` → `2023-5` |
| 이름 정규화 | `re.sub(r'[\s·\-,]', '', re.sub(r'\(.*?\)', '', 값)).lower()`. 완전 일치만 인정 |
| 끝의 "제품" | I2710, I0760과 비교할 때 `re.sub(r'\s*제품$', '', 값)`을 먼저 적용 |

**`RAWMTRL_STD_INFO`를 만드는 방법**

1. I0030 `RAWMTRL_NM`의 원료 전부와, `INDIV_RAWMTRL_NM`에서 `(고시형)`이 있거나 인정번호가 있는 원료를 모은다.
2. 인정번호가 있으면 번호로만 연결한다 (`I-0050.csv`의 `HF_FNCLTY_MTRAL_RCOGN_NO`, `I2710.csv`의 `PRDCT_NM`에서 추출).
3. 인정번호가 없으면 이름으로 연결한다. 대상은 `PRDCT_NM`에 인정번호가 없는 I2710 행(98개)뿐이다.
4. 같은 번호나 같은 이름은 제품당 한 번만 넣는다.

| 항목 | 값 |
|---|---|
| `RCOGN_NO` | 추출한 인정번호. 이름으로 연결했으면 빈값 |
| `RAWMTRL_NM` | I-0050 `RAWMTRL_NM`, 없으면 I2710 `PRDCT_NM` |
| `DAY_INTK_LOWLIMIT`, `DAY_INTK_HIGHLIMIT` | I2710 값, 없으면 I-0050 값. I-0050에는 반올림된 값이 있다 (1.8 → 2) |
| `INTK_UNIT` | I2710 `INTK_UNIT`, 없으면 I-0050 `WT_UNIT` |
| `INTK_MEMO`, `SKLL_IX_IRDNT_RAWMTRL` | I2710 값 |
| `PRIMARY_FNCLTY`, `IFTKN_ATNT_MATR_CN` | I-0050 값, 없으면 I2710 값. I2710에는 조문 참조만 적힌 행이 있다 |

**다른 JSON 필드**

| 필드 | 방법 |
|---|---|
| `RAWMTRL_CLASS_INFO` | `RAWMTRL_NM`의 각 원료를 "제품"을 뗀 뒤 정규화해 `HELT_ITM_GRP_NM`과 비교. 일치하는 행을 모두 넣는다 |
| `RAWMTRL_DICT_INFO` | `INDIV_RAWMTRL_NM`의 각 원료를 정규화해 `RPRSNT_RAWMTRL_NM`과 비교. 일치하는 행을 모두 넣는다. 기타 원재료에는 연결하지 않는다 (이 필드만 약 460MB가 됨) |

## 7. 검증하고 보고할 것

아래 결과를 수치로 보고한다. 기준과 크게 다르면 원인을 먼저 확인한다.

- [ ] `products`의 행 수와 기존 컬럼 값이 변경되지 않았다 (승인받은 변경 제외)
- [ ] 신고번호가 중복되지 않는다
- [ ] 표 3의 필드별 불일치 건수와 예시
- [ ] 추가 필드의 채움률
- [ ] 연결되지 않은 원료 상위 목록
- [ ] JSON 필드가 모두 파싱된다
- [ ] 제품 5개 이상을 원본 CSV와 직접 대조했다
- [ ] 사용한 파일의 수정일

채움률 참고값 (건강기능식품정보 46,118건 기준): `INSTT_NM` 60.3%, `BSSH_CHNG_HIST` 86.4%, `RAWMTRL_STD_INFO` 99.1%, `RAWMTRL_CLASS_INFO` 91.7%, `RAWMTRL_DICT_INFO` 93.2%, `RECALL_INFO` 11개 제품. 제품의 모든 원료가 연결됐다는 뜻은 아니다.

## 8. 시작 전에 사용자에게 물을 것

| 질문 | 현황 |
|---|---|
| 건강기능식품정보에만 있는 제품 681건을 `products`에 새로 넣는가 | 675건이 2026-09-01 이후 등록된 신규 제품 |
| DB에만 있는 제품 728건은 어떻게 하는가 | 현재 식약처 목록에 없다. 10건은 이름·제조사가 같고 번호만 다른 후보. 삭제는 하지 않는다 |
| 표 3에서 DB만 빈칸인 3건을 채우는가 | `intake_precautions` 2건, `storage_and_distribution_standard` 1건 |
| 같은 번호가 여러 행인 원료는 어떻게 하는가 | `제2013-5호` 300mg/600mg 등 |
| 번호는 같은데 섭취량이 다른 원료는 어떻게 하는가 | `2025-58`, `2022-35`, `2013-5`. 공식 출처 확인이 필요하다 |
| 기존 `ingredients` 테이블(1,223건)과 어떻게 맞추는가 | `RAWMTRL_STD_INFO`와 겹치는 내용이 있으나 값을 비교한 적이 없다. 2번 절차로 비교한 뒤 보고한다 |
| 어떤 형태로 저장하는가 | `products` 컬럼 추가 또는 별도 테이블 |
