/**
 * 사유 코드 → 화면 문구. Figma v5 케이스 카탈로그와 팀 문서 final_result_ui_cases.md(§2-2, §3, §5)를 옮겼어요.
 * 값(수치·원문)은 API의 target·claim_value·evidence로 채우고, 여기에는 값이 없는 고정 문구만 둬요.
 * 카드 두 번째 줄 설명(claim.explanation)은 백엔드 LLM이 만들어요. 여기 문구는 상세 행 안의 짧은 설명이에요.
 */
import type { ClaimType, SkippedReason } from '@/lib/api/types'

/* ── 판단 보류 갈래 (§3-3) ───────────────────────── */

export const UNCLEAR_BRANCH = {
  NOT_IN_RECORD: '공식 정보에 없는 내용',
  AMBIGUOUS: '광고가 모호함',
  AUTO_FAILED: '자동 판단 실패',
} as const

const BRANCH_OF: Record<string, (typeof UNCLEAR_BRANCH)[keyof typeof UNCLEAR_BRANCH]> = {}
for (const c of 'RAW_SOURCE ALLERGEN_NOTICE PACKAGE_NOT_IN_EVIDENCE REFERENCE_CLAIM COMPARISON_NOT_VERIFIED REFERENCE_RANGE INFANT_PRODUCT HERITAGE_NOT_CONFIRMED FIRST_CLAIM_UNPROVABLE GMP_NOT_CONFIRMED TRIAL_RESULT'.split(' '))
  BRANCH_OF[c] = UNCLEAR_BRANCH.NOT_IN_RECORD
for (const c of 'CATEGORY_TERM BRAND_OR_MODIFIER CONSTITUENT_POSSIBLE COUNT_NOT_VERIFIED PERCENT_NOT_CONFIRMED INTAKE_UNIT_DIFFERS BASIS_MISMATCH MULTIPLE_VALUES NUTRIENT_UNRESOLVED SHELF_LIFE_NOT_COMPARABLE FUNCTION_NOT_CONFIRMED NO_MATCHING_EVIDENCE PART_NO_MATCHING_EVIDENCE INGREDIENT_NOT_IN_PRODUCT QUESTION MULTI_EFFECT'.split(' '))
  BRANCH_OF[c] = UNCLEAR_BRANCH.AMBIGUOUS
for (const c of 'INGREDIENT_UNMATCHED NO_INGREDIENT_SLOT FORM_NOT_CONFIRMED QUANTITY_UNCLASSIFIED SPEC_NOT_FOUND INTAKE_NOT_FOUND CERTIFICATION_UNCLASSIFIED RECOGNITION_UNCONFIRMED INGREDIENT_NOT_CONFIRMED NO_CHECKER NO_CLAIM_TYPE LOW_CONFIDENCE DISEASE_DRUG_UNCERTAIN PART_LOW_CONFIDENCE'.split(' '))
  BRANCH_OF[c] = UNCLEAR_BRANCH.AUTO_FAILED

/** 판단 보류 코드의 갈래. 갈래가 없는 코드(일치·위반 등)는 null */
export const unclearBranch = (code: string) => BRANCH_OF[code] ?? null

/* ── 상세 행 왼쪽 항목 이름 ───────────────────────── */

const ITEM_BY_CODE: Record<string, string> = {
  FORM_NOT_CONFIRMED: '제형',
  FORM_MATCHES: '제형',
  AMOUNT_MISMATCH: '함량',
  AMOUNT_MATCHES_LABEL: '함량',
  AMOUNT_MATCHES_SERVING: '함량',
  AMOUNT_MATCHES_DAILY: '함량',
  SPEC_NOT_FOUND: '함량',
  BASIS_MISMATCH: '함량',
  MULTIPLE_VALUES: '함량',
  NUTRIENT_UNRESOLVED: '함량',
  INTAKE_MISMATCH: '섭취 방법',
  INTAKE_MATCHES: '섭취 방법',
  INTAKE_UNIT_DIFFERS: '섭취 방법',
  INTAKE_NOT_FOUND: '섭취 방법',
  SHELF_LIFE_MISMATCH: '소비기한',
  SHELF_LIFE_MATCHES: '소비기한',
  SHELF_LIFE_NOT_COMPARABLE: '소비기한',
  PERCENT_MISMATCH: '기준치 대비',
  PERCENT_NOT_CONFIRMED: '기준치 대비',
  PERCENT_CONSISTENT: '기준치 대비',
  PERCENT_MATCHES_LABEL: '기준치 대비',
  INFANT_PRODUCT: '기준치 대비',
  COMPARISON_NOT_VERIFIED: '비교 수치',
  HERITAGE_NOT_CONFIRMED: '업력',
  FUNCTIONAL_INGREDIENT_ABSENT: '기능성 원료',
  FUNCTIONAL_INGREDIENT_ON_RECORD: '기능성 원료',
  RECOGNITION_NO_MISMATCH: '개별인정 번호',
  RECOGNITION_NO_MATCHES: '개별인정 번호',
  RECOGNITION_ABSENT: '개별인정',
  RECOGNITION_UNCONFIRMED: '개별인정',
  RECOGNITION_ON_PRODUCT: '개별인정 원료',
  FUNCTION_NOT_ON_RECORD: '기능성',
  FUNCTION_NOT_CONFIRMED: '기능성',
  FUNCTION_ON_RECORD: '기능성',
  FIRST_CLAIM_UNPROVABLE: '국내 최초',
  INGREDIENT_ON_RECORD: '원료',
  INGREDIENT_NOT_CONFIRMED: '원료',
  GMP_BY_INDUSTRY: 'GMP',
  GMP_NOT_CONFIRMED: 'GMP',
  HFF_ON_RECORD: '건강기능식품',
  NO_CHECKER: '주장',
  NO_CLAIM_TYPE: '주장',
  NOT_A_CLAIM: '주장',
  PRECAUTION_CONFLICT: '주의사항',
  TRIAL_RESULT: '시험 결과',
}

const ITEM_BY_TYPE: Record<ClaimType, string> = {
  COMPOSITION: '원료',
  QUANTITY: '수치',
  CERTIFICATION: '인증',
  EFFECT: '효능 표현',
  PERSON_CREDENTIAL: '인물',
  ETC: '주장',
}

/** A 부분은 claim_type, B 부분은 'EFFECT'로 불러요 */
export const itemName = (claimType: ClaimType, code: string) => ITEM_BY_CODE[code] ?? ITEM_BY_TYPE[claimType] ?? '주장'

/* ── 근거 필드 이름 (식약처 API 필드 → 화면 이름) ───── */

const FIELD_LABEL: Record<string, string> = {
  RAWMTRL_NM: '원재료',
  INDIV_RAWMTRL_NM: '원재료',
  ETC_RAWMTRL_NM: '원재료',
  CAP_RAWMTRL_NM: '원재료',
  BASE_STANDARD: '기준·규격 원문',
  SRV_USE: '섭취 방법',
  DISTB_PD: '소비기한',
  RAWMTRL_STD_INFO: '기능성 원료 정보',
  RAWMTRL_CLASS_INFO: '원료 분류',
  MAIN_FNCTN: '주된 기능성',
  SUNGSANG: '성상',
  PRMS_DT: '인허가일 (참고)',
  BSSH_PRMS_DT: '인허가일 (참고)',
  INDUTY_CD_NM: '업종',
  STTEMNT_NO: '품목 신고',
  PRDT_SHAP_CD_NM: '제형',
}

/** 별표 5(영양성분 기준치)는 식약처 제품 정보가 아니라 고시라 제목을 따로 써요 */
export const NUTRIENT_STANDARD_FIELD = '별표 5'

export function evidenceHead(fields: string[], wholeList = false): string {
  const labels: string[] = []
  let notice = false
  for (const f of fields) {
    if (f === NUTRIENT_STANDARD_FIELD) notice = true
    else {
      const label = FIELD_LABEL[f] ?? f
      if (!labels.includes(label)) labels.push(label)
    }
  }
  if (wholeList) {
    const i = labels.indexOf('원재료')
    if (i >= 0) labels[i] = '원재료 전체'
  }
  if (notice) return ['영양성분 기준치 (고시 별표 5)', ...labels].join(' · ')
  return ['식약처 등록 정보', ...labels].join(' · ')
}

/* ── 상세 행 짧은 설명 (값 없이 코드별 고정) ───────── */

/** 근거 비교(①) 행 아래 한 줄 */
export const COMPARE_EXPLAIN: Record<string, string> = {
  INGREDIENT_ABSENT: '광고한 원료가 원재료 목록에 없어요.',
  AMOUNT_MISMATCH: '표시량과 1회·1일 환산값 어디에도 맞지 않아요.',
  INTAKE_MISMATCH: '광고한 섭취 방법이 등록된 섭취 방법과 달라요.',
  SHELF_LIFE_MISMATCH: '광고한 소비기한이 등록된 소비기한과 달라요.',
  PERCENT_MISMATCH: '기준치로 계산한 %와 광고의 %가 달라요.',
  FUNCTIONAL_INGREDIENT_ABSENT: '광고한 기능성 원료가 제품의 기능성 원료에 없어요.',
  RECOGNITION_NO_MISMATCH: '광고한 인정번호가 제품의 인정번호와 달라요.',
  RECOGNITION_ABSENT: '개별인정이라는데 인정번호도 개별인정 분류도 없어요.',
  FUNCTION_NOT_ON_RECORD: '광고한 기능성이 신고된 기능성에 없어요.',
  PRECAUTION_CONFLICT: '식약처 주의사항과 반대되는 내용이에요.',
  CONSTITUENT_POSSIBLE: '원재료에는 없지만 다른 원료의 구성 성분일 수 있어요.',
  FORM_NOT_CONFIRMED: '성상 원문에서 제형을 확인하지 못했어요.',
  PERCENT_NOT_CONFIRMED: '계산한 %와 다르지만 광고가 몇 정 기준인지 몰라 판단을 보류했어요.',
  INTAKE_UNIT_DIFFERS: '광고와 등록 정보의 단위가 달라 비교할 수 없어요.',
  BASIS_MISMATCH: '광고가 몇 g 기준인지 없어 표시량과 비교할 수 없어요.',
  INFANT_PRODUCT: '영유아 제품이라 성인 기준치를 그대로 적용하지 않아요.',
  INTAKE_NOT_FOUND: '섭취 방법 원문에서 횟수·개수를 읽지 못했어요.',
  SHELF_LIFE_NOT_COMPARABLE: '광고는 날짜, 등록 정보는 기간이라 비교할 수 없어요.',
  HERITAGE_NOT_CONFIRMED: '인허가일만으로는 업력을 확인할 수 없어요.',
  FIRST_CLAIM_UNPROVABLE: '‘최초·유일’은 공식 정보로 확인할 수 없어요. 날짜는 참고로만 보여 드려요.',
  FUNCTION_NOT_CONFIRMED: '기능이 아니라 섭취량 기준을 말하고 있어 판단을 보류했어요.',
  RECOGNITION_UNCONFIRMED: '개별인정 분류는 있지만 인정번호를 찾지 못했어요.',
  INGREDIENT_NOT_CONFIRMED: '표기가 달라 같은 원료로 확인하지 못했어요.',
  GMP_NOT_CONFIRMED: '업종만으로는 GMP 대상인지 확인할 수 없어요.',
  TRIAL_RESULT: '시험 결과를 말하는 문장이라 인정 기능성 문구로 사실 여부를 판단할 수 없어요.',
  LOW_CONFIDENCE: '모델 판단이 애매해 판단을 보류했어요.',
  MULTI_EFFECT: '여러 효능을 한 문장에 담아 하나씩 판단하지 못했어요.',
  PART_LOW_CONFIDENCE: '나눈 효능 중 일부의 판단이 애매해요.',
  INGREDIENT_FOUND: '원재료 목록에 같은 이름으로 있어요.',
  INGREDIENT_PART: '복합 원료의 일부로 들어 있어요.',
  INGREDIENT_ALIAS: '다른 이름으로 등록돼 있어요.',
  FORM_MATCHES: '성상에 적힌 제형과 같아요.',
  AMOUNT_MATCHES_LABEL: '표시량과 같아요.',
  AMOUNT_MATCHES_SERVING: '1회 섭취량으로 환산한 값과 같아요.',
  AMOUNT_MATCHES_DAILY: '1일 섭취량으로 환산한 값과 같아요.',
  INTAKE_MATCHES: '등록된 섭취 방법과 같아요.',
  PERCENT_CONSISTENT: '기준치로 계산한 %와 같아요.',
  PERCENT_MATCHES_LABEL: '표시량 기준으로 계산한 값과 같아요.',
  SHELF_LIFE_MATCHES: '등록된 소비기한과 같아요.',
  HFF_ON_RECORD: '건강기능식품으로 신고된 제품이 맞아요.',
  GMP_BY_INDUSTRY: 'GMP 인증 기록이 아니라, 업종으로 GMP 대상임을 간접 확인했어요.',
  FUNCTION_ON_RECORD: '신고된 기능성에 있어요.',
  RECOGNITION_ON_PRODUCT: '제품의 기능성 원료에 개별인정 번호가 있어요.',
  INGREDIENT_ON_RECORD: '원재료에서 확인했어요.',
  RECOGNITION_NO_MATCHES: '광고한 인정번호가 제품 인정번호와 같아요.',
  FUNCTIONAL_INGREDIENT_ON_RECORD: '제품의 기능성 원료에 있어요.',
  FUNCTION: '인정 기능성과 같은 내용이에요.',
  IMPLIES_RECOGNIZED: '인정 기능성을 담고 그 이상을 말하지 않아요.',
  ALL_PARTS_SUPPORTED: '효능을 나눠 비교한 결과 모두 같아요.',
}

/** 표현 지적(②) 행 */
export const EXPRESSION_EXPLAIN: Record<string, string> = {
  DISEASE_CLAIM: '건강기능식품은 질병을 예방하거나 치료한다고 광고할 수 없어요.',
  DRUG_CLAIM: '의약품을 대신하거나 약효를 높인다고 말할 수 없어요.',
  DISEASE_DRUG_UNCERTAIN: '질병 표현일 가능성이 있지만 확정하지 못했어요.',
  EXAGGERATION_NO_EVIDENCE: '인정 근거가 없는 효과·기간·크기를 단정했어요.',
}

/** 사유만(③) 행 본문. {target}은 확인한 대상으로 바꿔요 */
export const REASON_TEXT: Record<string, string> = {
  INGREDIENT_UNMATCHED: '{target}을(를) 원재료와 원료 사전에서 찾지 못했어요. 상표명일 수 있어요.',
  CATEGORY_TERM: '{target}은(는) 여러 성분을 묶는 이름이라 어떤 원료인지 정할 수 없어요.',
  BRAND_OR_MODIFIER: '{target}은(는) 상표·수식 표현이라 등록 원료와 짝을 정할 수 없어요.',
  NO_INGREDIENT_SLOT: '문장에서 원료 이름을 뽑지 못해 대조하지 못했어요.',
  RAW_SOURCE: '원산지·출처는 식약처 제품 정보에 원래 없는 항목이에요.',
  ALLERGEN_NOTICE: '알레르기 표시 항목은 제품 정보로 대조하지 않아요.',
  PACKAGE_NOT_IN_EVIDENCE: '포장 규격은 식약처 제품 정보에 없는 항목이라 확인할 수 없어요.',
  QUANTITY_UNCLASSIFIED: '어느 항목과 대조할 수치인지 정하지 못했어요.',
  COUNT_NOT_VERIFIED: '무엇을 세었는지 알 수 없어 확인하지 못했어요.',
  SPEC_NOT_FOUND: '기준·규격 원문에서 이 성분의 표시량을 찾지 못했어요.',
  REFERENCE_CLAIM: '고시 기준·최고 함량 주장은 제품 정보로 대조할 수 없어요.',
  COMPARISON_NOT_VERIFIED: '비교 대상의 근거가 공식 정보에 없어요.',
  MULTIPLE_VALUES: '수치가 여러 개라 어느 값과 짝지을지 정하지 못했어요.',
  NUTRIENT_UNRESOLVED: '어느 영양성분의 수치인지 특정할 수 없어요.',
  REFERENCE_RANGE: '범위 표기는 기준 범위라 표시량과 비교하지 않아요.',
  CERTIFICATION_UNCLASSIFIED: '어느 인증 항목과 대조할지 정하지 못했어요.',
  NO_CHECKER: '이 타입을 판정하는 규칙이 아직 없어 판단하지 못했어요.',
  NO_CLAIM_TYPE: '주장 타입이 비어 있어 판정하지 못했어요.',
  NO_MATCHING_EVIDENCE: '광고와 같은 내용이 인정 기능성에 없어 맞는지 판단할 수 없어요.',
  PART_NO_MATCHING_EVIDENCE: '나눈 효능 중 일부가 인정 기능성에 없어요.',
  INGREDIENT_NOT_IN_PRODUCT: '광고한 원료가 제품 기능성에 없거나 애매해요.',
  QUESTION: '질문 문장이라 효능 주장으로 판단하지 않았어요.',
  // 검증 대상 아님
  SALES_OR_RANK: '가격·판매 조건·순위는 검증하지 않아요.',
  STUDY_CONDITION: '시험 조건을 설명하는 문장이라 검증하지 않아요.',
  NOT_PRODUCT_CLAIM: '수상·특허·협약 같은 회사 활동은 검증하지 않아요.',
  FOOTNOTE: '기준을 설명하는 각주라 검증하지 않아요.',
  HERITAGE_NOT_MANUFACTURER: '제조사의 업력인지 알 수 없어 검증하지 않았어요.',
  SOURCE_OR_REVIEW: '출처·시험·심의 안내는 검증 대상이 아니에요.',
  OTHER_CERTIFICATION: '특허·해외 인증·상표는 공식 데이터로 확인하지 않아요.',
  NOT_VERIFIABLE_TYPE: '인물 자격은 근거 데이터로 검증하지 않아요.',
  NOT_A_CLAIM: '주장으로 보지 않는 문장이에요.',
  NOT_HEALTH_CLAIM: '건강 효과를 말하는 문장이 아니에요.',
}

/** 문구가 없는 새 코드가 와도 화면이 깨지지 않게 쓰는 기본 문구 */
export const FALLBACK_TEXT = '식약처 공개 데이터와 대조한 결과예요.'

/* ── 판정을 건너뛴 주장 (§5-5) ──────────────────── */

export const SKIP_COPY: Record<SkippedReason, { note: string; text: string }> = {
  PRODUCT_NOT_FOUND: {
    note: '판정 건너뜀 · 제품을 찾지 못함',
    text: '광고 제품을 식약처 공개 데이터에서 찾지 못해 이 주장은 판정하지 않았어요.',
  },
  PRODUCT_UNRESOLVED: {
    note: '판정 건너뜀 · 제품 후보 여러 개',
    text: '같은 이름의 제품 후보가 여러 개라 하나로 정하지 못해 판정하지 않았어요.',
  },
  NO_PRODUCT_REF: {
    note: '판정 건너뜀 · 제품 연결 안 됨',
    text: '어느 제품에 대한 주장인지 연결되지 않아 판정하지 않았어요.',
  },
}
