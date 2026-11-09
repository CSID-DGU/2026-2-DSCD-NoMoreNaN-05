# 클레임 타입별 필드와 DB 출력 형식

## 1. 클레임 타입별 필드

| 타입 | 필드 |
|---|---|
| QUANTITY | `BASE_STANDARD`, `SRV_USE`, `DISTB_PD`, `PRDT_SHAP_CD_NM`, `BSSH_PRMS_DT`, `INTAKE_HINT1`, `RAWMTRL_STD_INFO` |
| COMPOSITION | `RAWMTRL_NM`, `INDIV_RAWMTRL_NM`, `ETC_RAWMTRL_NM`, `CAP_RAWMTRL_NM`, `PRDLST_CDNM`, `BASE_STANDARD`, `SUNGSANG`, `RAWMTRL_DICT_INFO` |
| CERTIFICATION | `STTEMNT_NO`, `PRMS_DT`, `INDUTY_CD_NM`, `MAIN_FNCTN`, `RAWMTRL_NM`, `INDIV_RAWMTRL_NM`, `RAWMTRL_STD_INFO`, `RAWMTRL_CLASS_INFO` |
| EFFECT | `MAIN_FNCTN`, `INTAKE_HINT1`, `RAWMTRL_STD_INFO` |
| PERSON_CREDENTIAL, ETC | 없음 |

## 2. DB 출력 JSON

광고 영상 1편당 JSON 1개(`{video_id}.json`)입니다.

```json
{
  "video_id": "db_001_AKyDb1Yhaio",
  "url": "https://www.youtube.com/watch?v=AKyDb1Yhaio",
  "db_version": "2026-11-02",
  "products": [
    {
      "product_ref": "p01",
      "product_name": "BNS 혈당엔 바나바",
      "brand_name": "BNS",
      "manufacturer_name": "(주)오투바이오",
      "manufacturing_report_number": "20130020008495",
      "match": {
        "status": "confirmed",
        "method": "name_and_company",
        "candidates": 1,
        "matched_name": "BNS혈당엔바나바",
        "matched_company": "(주)오투바이오"
      },
      "DB": {
        "QUANTITY": {
          "BASE_STANDARD": "...", "SRV_USE": "...", "DISTB_PD": "...", "PRDT_SHAP_CD_NM": "...",
          "BSSH_PRMS_DT": "...", "INTAKE_HINT1": "...", "RAWMTRL_STD_INFO": []
        },
        "COMPOSITION": {
          "RAWMTRL_NM": "...", "INDIV_RAWMTRL_NM": "...", "ETC_RAWMTRL_NM": "...", "CAP_RAWMTRL_NM": "...",
          "PRDLST_CDNM": "...", "BASE_STANDARD": "...", "SUNGSANG": "...", "RAWMTRL_DICT_INFO": []
        },
        "CERTIFICATION": {
          "STTEMNT_NO": "...", "PRMS_DT": "...", "INDUTY_CD_NM": "...", "MAIN_FNCTN": "...",
          "RAWMTRL_NM": "...", "INDIV_RAWMTRL_NM": "...", "RAWMTRL_STD_INFO": [], "RAWMTRL_CLASS_INFO": []
        },
        "EFFECT": {
          "MAIN_FNCTN": "...", "INTAKE_HINT1": "...", "RAWMTRL_STD_INFO": []
        }
      }
    }
  ],
  "claims": [
    {
      "claim_id": "c01",
      "product_ref": "p01",
      "text": "...",
      "claim_type": "QUANTITY",
      "ingredients": [],
      "effect": null,
      "quantity": null,
      "intake_basis": null
    }
  ]
}
```

### `match`

| 필드 | 값 |
|---|---|
| `status` | `confirmed`, `unresolved`, `not_found` |
| `method` | `report_number`, `name_and_company`. `confirmed`가 아니면 `null` |
| `candidates` | 제품명이 같은 후보 수 |
| `matched_name`, `matched_company` | 연결된 제품의 이름과 업체. `confirmed`가 아니면 `null` |

### 값 규칙

- `DB`는 `confirmed`일 때만 객체이고, 그 외에는 `null`입니다.
- `confirmed`이면 `manufacturing_report_number`에 연결된 제품의 신고번호를 넣습니다.
- `RAWMTRL_STD_INFO`, `RAWMTRL_DICT_INFO`, `RAWMTRL_CLASS_INFO`는 배열이고, 값이 없으면 `[]`입니다.
- `DB` 안의 나머지 필드는 문자열이고, 값이 없으면 `""`입니다.
- 같은 필드가 여러 타입에 필요하면 타입마다 반복해서 넣습니다.
- `claims`는 클레임 추출 결과를 그대로 넘깁니다.

### 배열 필드 설명

이 3개는 원본 데이터셋의 이름이 아닙니다. 제품에 든 원료의 정보를 원본에서 찾아 제품별로 묶어 만드는 필드입니다.

| 필드 | 내용 | 원본 데이터셋 | 연결 기준 |
|---|---|---|---|
| `RAWMTRL_STD_INFO` | 원료별 인정번호, 일일 섭취량, 기능성, 주의사항 | I2710, I-0050, I-0040 | 인정번호가 있으면 인정번호, 없으면 I0030 `RAWMTRL_NM`의 원료명 ↔ I2710 `PRDCT_NM` |
| `RAWMTRL_DICT_INFO` | 원료의 대표 이름, 이명, 영문명, 학명 | 식품 원재료 정보 | I0030 `INDIV_RAWMTRL_NM`의 원료명 ↔ `RPRSNT_RAWMTRL_NM` |
| `RAWMTRL_CLASS_INFO` | 원료의 분류 코드와 분류명 | I0760 | I0030 `RAWMTRL_NM`의 원료명 ↔ `HELT_ITM_GRP_NM` |

### 배열 항목

| 필드 | 항목 |
|---|---|
| `RAWMTRL_STD_INFO` | `RCOGN_NO`, `RAWMTRL_NM`, `DAY_INTK_LOWLIMIT`, `DAY_INTK_HIGHLIMIT`, `INTK_UNIT`, `INTK_MEMO`, `SKLL_IX_IRDNT_RAWMTRL`, `PRIMARY_FNCLTY`, `IFTKN_ATNT_MATR_CN` |
| `RAWMTRL_DICT_INFO` | `LCLAS_NM`, `MLSFC_NM`, `RPRSNT_RAWMTRL_NM`, `RAWMTRL_NCKNM`, `ENG_NM`, `SCNM`, `REGN_CD_NM`, `RAWMTRL_STATS_CD_NM`, `USE_CND_NM` |
| `RAWMTRL_CLASS_INFO` | `HELT_ITM_GRP_CD`, `HELT_ITM_GRP_NM`, `LCLAS_CD`, `LCLAS_NM`, `MLSFC_CD`, `MLSFC_NM`, `SCLAS_CD`, `SCLAS_NM` |
