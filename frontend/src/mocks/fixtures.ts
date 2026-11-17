/**
 * 가짜 API 결과 데이터 — Figma v5 final·케이스 카탈로그의 예시 문장을 명세(R01) 모양으로 옮겼어요.
 * explanation(LLM 리포트)은 명세 예시를 따라 넣었어요. 일부 부분은 일부러 비워 두어 기본 문구로 보이는지도 확인해요.
 */
import type { Claim, JobResultResponse, Product } from '@/lib/api/types'
import { LABELS, type Label } from '@/lib/labels'

const P01: Product = {
  product_ref: 'p01',
  product_name: '영라뉴 장용성 파비플로라 PRO',
  brand_name: '영라뉴',
  manufacturer_name: '(주)알피바이오',
  manufacturing_report_number: '20040020006729',
  match_status: 'confirmed',
  DB: {
    COMPOSITION: {
      RAWMTRL_NM:
        '파비플로라생강뿌리추출물, 결정셀룰로스, 히드록시프로필메틸셀룰로스, 스테아린산마그네슘, 이산화규소, 셸락, 글리세린지방산에스테르, 카나우바왁스, 이산화티타늄',
    },
    EFFECT: { MAIN_FNCTN: '체지방 감소에 도움을 줄 수 있음' },
  },
}

const P02: Product = {
  product_ref: 'p02',
  product_name: '영라뉴 레몬즙',
  brand_name: '영라뉴',
  manufacturer_name: null,
  manufacturing_report_number: null,
  match_status: 'not_found',
  DB: null,
}

type ClaimInput = Omit<Claim, 'parsed' | 'decided_by' | 'skipped_reason' | 'A' | 'B'> &
  Partial<Pick<Claim, 'decided_by' | 'skipped_reason' | 'A' | 'B'>>

const claim = (c: ClaimInput): Claim => ({
  parsed: { ingredients: [], effect: null, quantity: null, intake_basis: null },
  decided_by: c.A && c.B ? ['A', 'B'] : c.A ? ['A'] : c.B ? ['B'] : [],
  skipped_reason: null,
  A: null,
  B: null,
  ...c,
})

const BASE_CLAIMS: Claim[] = [
  claim({
    claim_id: 'c01',
    product_ref: 'p01',
    claim_type: ['EFFECT'],
    text: '엉덩이 허벅지 체지방 탈출',
    t_start: 1,
    t_end: 4,
    final_label: 'OVERCLAIM',
    B: { label: 'OVERCLAIM', reason_code: 'EXAGGERATION_NO_EVIDENCE', reason: '', evidence_text: null },
    explanation: '인정된 기능성은 체지방 감소에 도움을 줄 수 있다는 정도인데, 부위를 정해 빠진다고 단정해요.',
  }),
  claim({
    claim_id: 'c02',
    product_ref: 'p01',
    claim_type: ['CERTIFICATION'],
    text: '국내 최초! 식약처 인정 기능성원료 파비플로라',
    t_start: 5,
    t_end: 8,
    final_label: 'UNCLEAR',
    A: {
      label: 'UNCLEAR',
      reason_codes: ['FIRST_CLAIM_UNPROVABLE'],
      checks: [
        {
          claim_type: 'CERTIFICATION',
          status: 'UNCLEAR',
          code: 'FIRST_CLAIM_UNPROVABLE',
          reason: '',
          target: null,
          claim_value: '국내 최초!',
          evidence: [{ field: 'PRMS_DT', value: '2024년 9월 12일' }],
          explanation: '인허가일만으로는 ‘최초’인지 확인할 수 없어요. 날짜는 참고로만 보여 드려요.',
        },
      ],
    },
    explanation: '‘국내 최초’는 식약처 공개 데이터로 확인할 수 없는 내용이에요.',
  }),
  claim({
    claim_id: 'c03',
    product_ref: 'p01',
    claim_type: ['COMPOSITION'],
    text: '개별인정원료 파비플로라생강뿌리추출물',
    t_start: 9,
    t_end: 12,
    final_label: 'SUPPORTED',
    A: {
      label: 'SUPPORTED',
      reason_codes: ['INGREDIENT_FOUND'],
      checks: [
        {
          claim_type: 'COMPOSITION',
          status: 'SUPPORTED',
          code: 'INGREDIENT_FOUND',
          reason: '',
          target: '파비플로라생강뿌리추출물',
          claim_value: '파비플로라생강뿌리추출물',
          evidence: [{ field: 'RAWMTRL_NM', value: '파비플로라생강뿌리추출물' }],
        },
      ],
    },
    explanation: '광고한 원료가 등록된 원재료 목록에 그대로 있어요.',
  }),
  claim({
    claim_id: 'c04',
    product_ref: 'p01',
    claim_type: ['QUANTITY', 'EFFECT'],
    text: '하루 하나, 식단 식품 상관없이 관리 가능하세요',
    t_start: 16,
    t_end: 19,
    final_label: 'VIOLATION',
    A: {
      label: 'VIOLATION',
      reason_codes: ['INTAKE_MISMATCH'],
      checks: [
        {
          claim_type: 'QUANTITY',
          status: 'VIOLATION',
          code: 'INTAKE_MISMATCH',
          reason: '',
          target: null,
          claim_value: '하루 하나',
          evidence: [{ field: 'SRV_USE', value: '1일 2회, 1회 1정' }],
          explanation: '광고는 하루 1정, 등록된 섭취 방법은 하루 2정이에요.',
        },
      ],
    },
    B: { label: 'UNCLEAR', reason_code: 'NO_MATCHING_EVIDENCE', reason: '', evidence_text: null },
    explanation: '등록된 섭취 방법은 1일 2회, 1회 1정인데 광고는 하루 하나라고 말해요.',
  }),
  claim({
    claim_id: 'c05',
    product_ref: 'p01',
    claim_type: ['EFFECT'],
    text: '체지방 감소에 도움을 줄 수 있는 (기능성원료)',
    t_start: 20,
    t_end: 23,
    final_label: 'SUPPORTED',
    B: {
      label: 'SUPPORTED',
      reason_code: 'FUNCTION',
      reason: '',
      evidence_text: '파비플로라생강뿌리추출물은 체지방 감소에 도움을 줄 수 있다',
    },
    explanation: '인정된 기능성과 같은 내용이에요.',
  }),
  claim({
    claim_id: 'c06',
    product_ref: 'p01',
    claim_type: ['EFFECT'],
    text: '3대 부위 각 영역 체지방량 유의적 감소',
    t_start: 24,
    t_end: 27,
    final_label: 'UNCLEAR',
    B: {
      label: 'UNCLEAR',
      reason_code: 'TRIAL_RESULT',
      reason: '',
      evidence_text: '파비플로라생강뿌리추출물은 체지방 감소에 도움을 줄 수 있다',
      explanation: '인정 기능성 문구로는 시험 결과가 사실인지 확인할 수 없어요.',
    },
    explanation: '시험 결과를 말하는 문장이라 인정 기능성 문구로는 사실인지 판단할 수 없어요.',
  }),
  claim({
    claim_id: 'c07',
    product_ref: 'p01',
    claim_type: ['EFFECT'],
    text: '꾸준히 드시면 당뇨까지 잡아 줘요',
    t_start: 28,
    t_end: 31,
    final_label: 'VIOLATION',
    B: { label: 'VIOLATION', reason_code: 'DISEASE_CLAIM', reason: '', evidence_text: '질병 치료' },
    explanation: '건강기능식품은 질병을 예방하거나 치료한다고 광고할 수 없어요.',
  }),
  claim({
    claim_id: 'c08',
    product_ref: 'p01',
    claim_type: ['CERTIFICATION'],
    text: 'GMP 인증 시설에서 만든 제품',
    t_start: 32,
    t_end: 35,
    final_label: 'SUPPORTED',
    A: {
      label: 'SUPPORTED',
      reason_codes: ['GMP_BY_INDUSTRY'],
      checks: [
        {
          claim_type: 'CERTIFICATION',
          status: 'SUPPORTED',
          code: 'GMP_BY_INDUSTRY',
          reason: '',
          target: null,
          claim_value: 'GMP 인증 시설',
          evidence: [{ field: 'INDUTY_CD_NM', value: '건강기능식품전문제조업' }],
        },
      ],
    },
    explanation: '업종으로 GMP 대상인 제조업체임을 간접 확인했어요.',
  }),
  claim({
    claim_id: 'c09',
    product_ref: 'p01',
    claim_type: ['QUANTITY'],
    text: '방송에서만 50% SALE · 12박스 338,000원 → 169,000원',
    t_start: 36,
    t_end: 40,
    final_label: 'OUT_OF_SCOPE',
    A: {
      label: 'OUT_OF_SCOPE',
      reason_codes: ['SALES_OR_RANK'],
      checks: [
        { claim_type: 'QUANTITY', status: 'OUT_OF_SCOPE', code: 'SALES_OR_RANK', reason: '', target: null, claim_value: null, evidence: [] },
      ],
    },
  }),
  claim({
    claim_id: 'c10',
    product_ref: 'p01',
    claim_type: ['PERSON_CREDENTIAL'],
    text: '박신혜 쇼호스트 · 김수연 쇼호스트',
    t_start: 41,
    t_end: 43,
    final_label: 'OUT_OF_SCOPE',
    A: {
      label: 'OUT_OF_SCOPE',
      reason_codes: ['NOT_VERIFIABLE_TYPE'],
      checks: [
        {
          claim_type: 'PERSON_CREDENTIAL',
          status: 'OUT_OF_SCOPE',
          code: 'NOT_VERIFIABLE_TYPE',
          reason: '',
          target: null,
          claim_value: null,
          evidence: [],
        },
      ],
    },
  }),
  claim({
    claim_id: 'c11',
    product_ref: 'p01',
    claim_type: ['EFFECT'],
    text: '*인체적용시험 결과가 모든 사람에게 동일하게 적용되는 것은 아님',
    t_start: 44,
    t_end: 48,
    final_label: 'DISCLAIMER',
    A: { label: 'DISCLAIMER', reason_codes: [], checks: [] },
    B: { label: 'DISCLAIMER', reason_code: 'DISCLAIMER', reason: '', evidence_text: null },
  }),
]

const MULTI_EXTRA: Claim[] = [
  claim({
    claim_id: 'c12',
    product_ref: 'p02',
    claim_type: ['EFFECT'],
    text: '레몬즙 한 포로 아침 붓기까지 싹 빠져요',
    t_start: 49,
    t_end: 52,
    final_label: 'UNCLEAR',
    skipped_reason: 'PRODUCT_NOT_FOUND',
    B: { label: 'UNCLEAR', reason_code: 'PRODUCT_UNRESOLVED', reason: '', evidence_text: null },
  }),
  claim({
    claim_id: 'c13',
    product_ref: null,
    claim_type: ['EFFECT'],
    text: '두 제품을 같이 드시면 효과가 두 배예요',
    t_start: null,
    t_end: null,
    final_label: 'UNCLEAR',
    skipped_reason: 'NO_PRODUCT_REF',
  }),
]

function summarize(claims: Claim[]): JobResultResponse['summary'] {
  const labels = Object.fromEntries(LABELS.map((l) => [l, 0])) as Record<Label, number>
  for (const c of claims) labels[c.final_label] += 1
  return { claims: claims.length, labels }
}

export type ResultVariant = 'single' | 'multi' | 'clean'

export function buildResult(jobId: string, url: string, variant: ResultVariant): JobResultResponse {
  let claims = BASE_CLAIMS
  let products = [P01]
  if (variant === 'multi') {
    claims = [...BASE_CLAIMS, ...MULTI_EXTRA]
    products = [P01, P02]
  } else if (variant === 'clean') {
    claims = BASE_CLAIMS.filter((c) => !['VIOLATION', 'OVERCLAIM', 'UNCLEAR'].includes(c.final_label))
  }
  return {
    job_id: jobId,
    video: { video_id: 'mock', url, title: '영라뉴 장용성 파비플로라 PRO 광고 영상', duration_sec: 56 },
    products,
    summary: summarize(claims),
    claims,
    meta: { db_version: 'mock', label_order: ['DISCLAIMER', 'VIOLATION', 'OVERCLAIM', 'UNCLEAR', 'SUPPORTED', 'OUT_OF_SCOPE'] },
  }
}
