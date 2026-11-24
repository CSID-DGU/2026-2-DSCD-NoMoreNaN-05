/**
 * API 결과(R01)의 주장 하나 → 화면 카드 값.
 * 상세 행 모양은 팀 문서 §2-2 규칙: A 부분은 evidence가 있으면 ① 근거 비교, 없으면 ③ 사유만.
 * B는 사유 코드로 ①·②·③을 고르고, 면책 문구·판정 건너뜀은 ④ 안내.
 * 설명 문장은 백엔드 LLM 리포트(claim·checks[]·B의 explanation)를 먼저 쓰고, 없으면 사유 코드별 기본 문구를 써요.
 */
import type { GroupItem } from '@/features/result/GroupCard'
import type { ClaimPart } from '@/features/result/ClaimPart'
import {
  COMPARE_EXPLAIN,
  EXPRESSION_EXPLAIN,
  FALLBACK_TEXT,
  REASON_TEXT,
  SKIP_COPY,
  evidenceHead,
  itemName,
  unclearBranch,
} from '@/features/result/reasonCopy'
import type { ACheck, BPart, Claim, Product } from '@/lib/api/types'
import { formatTimeRange } from '@/lib/format'
import { markClaimText, type TextMark } from '@/features/result/claimMarks'
import type { Label, LabelTone } from '@/lib/labels'

export type ClaimView = {
  id: string
  productRef: string | null
  finalLabel: Label
  tone: LabelTone
  productName: string | null
  timeRange: string | null
  sentence: string
  /** 문장을 라벨별 형광펜 조각으로 나눈 것 */
  sentenceMarks: TextMark[]
  explain: string | null
  skipNote?: string
  parts: ClaimPart[]
}

const B_COMPARE = new Set([
  'FUNCTION',
  'IMPLIES_RECOGNIZED',
  'ALL_PARTS_SUPPORTED',
  'TRIAL_RESULT',
  'LOW_CONFIDENCE',
  'MULTI_EFFECT',
  'PART_LOW_CONFIDENCE',
  'PRECAUTION_CONFLICT',
])
const B_EXPRESSION = new Set(['DISEASE_CLAIM', 'DRUG_CLAIM', 'DISEASE_DRUG_UNCERTAIN', 'EXAGGERATION_NO_EVIDENCE'])

/** 처음 보는 skipped_reason이 와도 깨지지 않게 */
const SKIP_FALLBACK = { note: '판정 건너뜀', text: '제품을 확인하지 못해 이 주장은 판정하지 않았어요.' }

const DISCLAIMER_NOTICE: ClaimPart = {
  kind: 'notice',
  item: '안내',
  head: '판정 대상 아님',
  text: '광고 속 고지 문구라 판정하지 않고 ‘면책 문구’ 묶음에 모아 보여 드려요.',
}

/** LLM 설명이 글자로 왔을 때만 써요. 없거나 비어 있으면 null → 사유 코드별 기본 문구 */
function llmText(v: unknown): string | null {
  return typeof v === 'string' && v.trim() ? v.trim() : null
}

/** 받침 여부에 맞춰 조사를 붙여요. 한글이 아니면 앞 조사(받침 있음)를 써요. */
function withJosa(word: string, withBatchim: string, withoutBatchim: string) {
  const code = word.charCodeAt(word.length - 1) - 0xac00
  const hasBatchim = code >= 0 && code <= 11171 ? code % 28 !== 0 : true
  return `‘${word}’${hasBatchim ? withBatchim : withoutBatchim}`
}

/** "{target}을(를)" "{target}은(는)" 자리에 대상 이름과 맞는 조사를 넣어요 */
function fillTarget(template: string, target: string | null) {
  return template
    .replace('{target}을(를)', target ? withJosa(target, '을', '를') : '이 표현을')
    .replace('{target}은(는)', target ? withJosa(target, '은', '는') : '이 표현은')
}

function reasonHead(label: Label, code: string) {
  if (label === 'OUT_OF_SCOPE') return '검증하지 않는 이유'
  if (label === 'UNCLEAR') return `판단 사유 · ${unclearBranch(code) ?? '판단 보류'}`
  return '판단 사유'
}

function adValue(target: string | null, value: string | null) {
  if (target && value && !value.includes(target)) return `${target} ${value}`
  return value ?? target
}

function partFromA(check: ACheck, fallbackText: string): ClaimPart {
  const item = itemName(check.claim_type, check.code)
  const branch = check.status === 'UNCLEAR' ? unclearBranch(check.code) : null
  const itemNote = check.code === 'GMP_BY_INDUSTRY' ? '업종으로 확인' : (branch ?? undefined)

  // 명세상 evidence는 배열이지만, 비어 오거나 값이 문자열이 아니어도 깨지지 않게 걸러요
  const evidence = (Array.isArray(check.evidence) ? check.evidence : []).filter(
    (e) => e && typeof e.value === 'string' && e.value.trim() !== '',
  )
  if (evidence.length > 0) {
    const values = evidence.map((e) => e.value)
    let bValue: string | string[] = values
    if (check.code === 'HFF_ON_RECORD') bValue = '건강기능식품으로 신고된 제품' // 신고번호 값은 보여 주지 않아요(카탈로그)
    else if (check.code === 'INGREDIENT_ABSENT') bValue = values.join(', ')
    return {
      kind: 'compare',
      item,
      itemNote,
      tone: check.status,
      aHead: '광고에서',
      aValue: adValue(check.target, check.claim_value) ?? fallbackText,
      bHead: evidenceHead(
        evidence.map((e) => e.field),
        check.code === 'INGREDIENT_ABSENT',
      ),
      bValue,
      explain: llmText(check.explanation) ?? COMPARE_EXPLAIN[check.code] ?? FALLBACK_TEXT,
    }
  }

  const target = adValue(check.target, check.claim_value)
  return {
    kind: 'reason',
    item,
    tone: check.status,
    head: reasonHead(check.status, check.code),
    text: llmText(check.explanation) ?? fillTarget(REASON_TEXT[check.code] ?? FALLBACK_TEXT, check.target),
    target: target ? `확인한 대상 · ${target}` : undefined,
  }
}

function partFromB(b: BPart, claim: Claim, mainFunction: string | null): ClaimPart {
  const code = b.reason_code
  if (code === 'DISCLAIMER') return DISCLAIMER_NOTICE

  const item = itemName('EFFECT', code)
  const branch = b.label === 'UNCLEAR' ? unclearBranch(code) : null
  const adPhrase = claim.parsed?.effect ?? claim.text
  const evidenceText = typeof b.evidence_text === 'string' && b.evidence_text.trim() ? b.evidence_text : null
  const llm = llmText(b.explanation)

  if (B_EXPRESSION.has(code)) {
    const isOverclaim = code === 'EXAGGERATION_NO_EVIDENCE'
    // 질병·의약품 코드의 evidence_text는 공식 근거가 아니라 표현 유형이라 '지적 유형'으로 보여요(§5-3)
    const bHead = isOverclaim ? '비교한 인정 기능성' : '지적 유형'
    const bValue = isOverclaim ? mainFunction : evidenceText
    return {
      kind: 'compare',
      item,
      itemNote: branch ?? undefined,
      tone: b.label,
      aHead: '지적된 표현',
      aValue: `“${adPhrase}”`,
      ...(bValue ? { bHead, bValue } : {}),
      explain: llm ?? EXPRESSION_EXPLAIN[code] ?? FALLBACK_TEXT,
    }
  }

  if (B_COMPARE.has(code) && evidenceText) {
    const lines = evidenceText.split(' / ').filter(Boolean)
    const bHead =
      code === 'PRECAUTION_CONFLICT'
        ? '식약처 등록 정보 · 섭취 시 주의사항'
        : code === 'TRIAL_RESULT' || code === 'LOW_CONFIDENCE'
          ? '가장 가까운 인정 기능성'
          : lines.length > 1
            ? `인정 기능성 문장 ${lines.length}개`
            : '인정 기능성 문장'
    return {
      kind: 'compare',
      item,
      itemNote: branch ?? undefined,
      tone: b.label,
      aHead: '광고에서',
      aValue: adPhrase,
      bHead,
      bValue: lines,
      explain: llm ?? COMPARE_EXPLAIN[code] ?? FALLBACK_TEXT,
    }
  }

  return {
    kind: 'reason',
    item,
    tone: b.label,
    head: reasonHead(b.label, code),
    text: llm ?? REASON_TEXT[code] ?? FALLBACK_TEXT,
  }
}

export function productNameOf(claim: Claim, products: Product[]): string | null {
  if (claim.product_ref === null) return null // "제품 연결 안 됨"
  const p = products.find((x) => x.product_ref === claim.product_ref)
  return p?.product_name ?? p?.brand_name ?? '제품명 확인 안 됨'
}

function mainFunctionOf(claim: Claim, products: Product[]): string | null {
  const p = products.find((x) => x.product_ref === claim.product_ref)
  const v = p?.DB?.EFFECT?.MAIN_FNCTN
  return typeof v === 'string' && v.trim() ? v : null
}

export function buildClaimView(claim: Claim, products: Product[]): ClaimView {
  const base = {
    id: claim.claim_id,
    productRef: claim.product_ref,
    finalLabel: claim.final_label,
    productName: productNameOf(claim, products),
    timeRange: formatTimeRange(claim.t_start, claim.t_end),
    sentence: claim.text,
    sentenceMarks: markClaimText(claim),
    explain: llmText(claim.explanation),
  }

  if (claim.skipped_reason) {
    const copy = SKIP_COPY[claim.skipped_reason] ?? SKIP_FALLBACK
    return {
      ...base,
      tone: 'SKIPPED',
      skipNote: copy.note,
      parts: [{ kind: 'notice', item: '안내', head: '판정을 건너뛴 이유', text: copy.text }],
    }
  }

  if (claim.final_label === 'DISCLAIMER') return { ...base, tone: 'DISCLAIMER', parts: [DISCLAIMER_NOTICE] }

  const parts: ClaimPart[] = [
    ...(Array.isArray(claim.A?.checks) ? claim.A.checks : []).map((check) => partFromA(check, claim.text)),
    ...(claim.B ? [partFromB(claim.B, claim, mainFunctionOf(claim, products))] : []),
  ]
  return { ...base, tone: claim.final_label, parts }
}

/** 검증 대상 아님·면책 문구 묶음 카드의 한 줄 */
export function buildGroupItem(claim: Claim, products: Product[]): GroupItem {
  const code = claim.A?.checks?.[0]?.code ?? claim.B?.reason_code
  return {
    productName: productNameOf(claim, products),
    timeRange: formatTimeRange(claim.t_start, claim.t_end),
    sentence: claim.text,
    note:
      claim.final_label === 'DISCLAIMER'
        ? '광고 속 고지 문구예요'
        : (code && REASON_TEXT[code]) || '검증 대상이 아닌 문장이에요',
  }
}
