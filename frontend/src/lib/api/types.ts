/**
 * 백엔드 API 타입 — Notion "API 명세서 (백엔드)" 그대로 옮겼어요.
 * 필드 이름은 백엔드와 같게 snake_case로 둬요(변환하지 않음).
 */
import type { Label } from '@/lib/labels'

/** 모든 응답의 봉투 */
export type ApiEnvelope<T> =
  | { success: true; code: number; message: string; data: T }
  | { success: false; code: number; message: string; error: { code: string } | null; data: null }

/* ── POST /jobs (I01) ─────────────────────────────── */

export type CreateJobResponse = {
  job_id: string
  url: string
  created_at: string
  expires_at: string
  cached: boolean
}

/* ── GET /jobs/{jobId} (P01) ──────────────────────── */

export type JobStatus = 'QUEUED' | 'PROCESSING' | 'DONE' | 'FAILED'
export type StepState = 'PENDING' | 'RUNNING' | 'DONE' | 'FAILED'
export type StepNo = 1 | 2 | 3

export type FailureCode =
  | 'VIDEO_FETCH_FAILED'
  | 'CLAIM_EXTRACT_FAILED'
  | 'NO_CLAIMS'
  | 'PRODUCT_MAPPING_ALL'
  | 'VERIFY_FAILED'

export type JobStatusResponse = {
  job_id: string
  url: string
  status: JobStatus
  current_step: StepNo | null
  /** 완료한 단계 수 0~3 = 제목 밑 막대 값 */
  completed_steps: 0 | 1 | 2 | 3
  steps: { no: StepNo; name: string; state: StepState }[]
  failure: { step: StepNo; code: FailureCode } | null
  video: { title: string | null; duration_sec: number | null; ready: boolean } | null
  elapsed_sec: number
  created_at: string
  finished_at: string | null
  expires_at: string
  cached: boolean
}

/* ── GET /jobs/{jobId}/result (R01) ───────────────── */

export type MatchStatus = 'confirmed' | 'unresolved' | 'not_found'

export type Product = {
  product_ref: string
  product_name: string | null
  brand_name: string | null
  manufacturer_name: string | null
  manufacturing_report_number: string | null
  match_status: MatchStatus
  /** 식약처 원문 4섹션. 섹션 안 필드 이름은 식약처 API 그대로라 느슨하게 받아요. confirmed가 아니면 null */
  DB: {
    QUANTITY?: Record<string, unknown>
    COMPOSITION?: Record<string, unknown>
    CERTIFICATION?: Record<string, unknown>
    EFFECT?: Record<string, unknown>
  } | null
}

export type ClaimType =
  | 'EFFECT'
  | 'QUANTITY'
  | 'COMPOSITION'
  | 'CERTIFICATION'
  | 'PERSON_CREDENTIAL'
  | 'ETC'

export type SkippedReason = 'PRODUCT_NOT_FOUND' | 'PRODUCT_UNRESOLVED' | 'NO_PRODUCT_REF'

export type Evidence = { field: string; value: string }

export type ACheck = {
  claim_type: ClaimType
  status: Label
  code: string
  /** 개발용 문장 — 화면에 쓰지 않아요 */
  reason: string
  target: string | null
  claim_value: string | null
  evidence: Evidence[]
  /** 이 부분의 사용자용 설명 (LLM 리포트). 리포트 작업 전에는 오지 않을 수 있어요 */
  explanation?: string | null
}

export type APart = {
  label: Label
  reason_codes: string[]
  checks: ACheck[]
}

export type BPart = {
  label: Label
  reason_code: string
  /** 개발용 문장 — 화면에 쓰지 않아요 */
  reason: string
  /** 사유 코드마다 뜻이 달라요(인정 기능성 문장 / 표현 유형 / 주의사항 원문 / null) */
  evidence_text: string | null
  /** 이 부분의 사용자용 설명 (LLM 리포트). 리포트 작업 전에는 오지 않을 수 있어요 */
  explanation?: string | null
}

export type Claim = {
  claim_id: string
  product_ref: string | null
  claim_type: ClaimType[]
  text: string
  t_start: number | null
  t_end: number | null
  parsed: {
    ingredients: string[]
    effect: string | null
    quantity: string | null
    intake_basis: string | null
  }
  final_label: Label
  decided_by: ('A' | 'B')[]
  skipped_reason: SkippedReason | null
  A: APart | null
  B: BPart | null
  /**
   * 카드 두 번째 줄 — 주장 전체 요약 설명 (LLM 리포트, 명세 R01).
   * 명세상 string이지만 리포트 작업 전에는 오지 않을 수 있어 비어 있어도 되게 둬요.
   */
  explanation?: string | null
}

export type JobResultResponse = {
  job_id: string
  video: {
    video_id: string
    url: string
    title: string | null
    duration_sec: number | null
  }
  products: Product[]
  summary: {
    claims: number
    labels: Record<Label, number>
  }
  claims: Claim[]
  meta: {
    db_version: string | null
    label_order: Label[]
  }
}
