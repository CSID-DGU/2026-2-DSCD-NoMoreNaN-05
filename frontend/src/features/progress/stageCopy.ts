/**
 * S2 처리 중 화면 문구 — Figma v5 final S2-01~04, S2-F1~F5 그대로.
 * VERIFY_FAILED는 Figma 4종 밖이라 백엔드 명세 초안 문구를 써요(확인 필요 #3).
 */
import type { FailureCode, StepNo, StepState } from '@/lib/api/types'

export const STEP_NAMES: Record<StepNo, string> = { 1: '영상 가져오기', 2: '주장 추출', 3: '주장 검증' }
export const STEP_MARKS: Record<StepNo, string> = { 1: '①', 2: '②', 3: '③' }

/** 단계 설명 한 줄 */
export function stageDescription(no: StepNo, state: StepState, failure: FailureCode | null): string {
  if (no === 1) {
    if (state === 'DONE') return '영상 다운로드 완료'
    if (state === 'FAILED') return '영상을 내려받지 못했어요'
    return '영상을 내려받고 있어요'
  }
  if (no === 2) {
    if (state === 'PENDING') return '영상 가져오기가 끝나면 시작해요'
    if (state === 'RUNNING') return '영상을 분석해서 검증할 주장을 찾고 있어요'
    if (state === 'FAILED') return '영상에서 음성과 화면 글자를 읽지 못했어요'
    return failure === 'NO_CLAIMS'
      ? '영상을 분석했지만 검증할 주장이 나오지 않았어요'
      : '영상을 분석해서 검증할 주장을 찾았어요 · 면책 문구는 따로 표시해요'
  }
  if (state === 'PENDING') return '주장 추출이 끝나면 시작해요'
  if (state === 'RUNNING') return '식약처 공개 데이터와 대조하고 있어요'
  if (state === 'DONE') return '식약처 공개 데이터와 대조를 마쳤어요'
  if (failure === 'NO_CLAIMS') return '검증할 주장을 찾지 못했어요'
  if (failure === 'PRODUCT_MAPPING_ALL') return '식약처 공개 데이터에서 제품을 찾지 못했어요'
  return '판정 중 문제가 생겼어요'
}

/** 실패 팝업 제목·본문 (본문 두 줄) */
export const FAIL_DIALOGS: Record<FailureCode, { title: string; body: [string, string] }> = {
  VIDEO_FETCH_FAILED: {
    title: '영상을 가져오지 못했어요',
    body: ['비공개이거나 삭제된 영상, 또는 일시적인 연결 문제일 수 있어요.', '다른 영상으로 시도해주세요'],
  },
  CLAIM_EXTRACT_FAILED: {
    title: '주장을 추출하지 못했어요',
    body: ['영상에서 음성이나 화면 글자를 읽어 내지 못했어요.', '다른 영상으로 시도해주세요'],
  },
  NO_CLAIMS: {
    title: '검증할 주장을 찾지 못했어요',
    body: ['이 영상에서 건강 기능·원료·함량·인증 주장이 나오지 않았어요.', '다른 영상으로 시도해주세요'],
  },
  PRODUCT_MAPPING_ALL: {
    title: '식약처에 등록되지 않은 제품의 영상이에요',
    body: ['TRUEAD로는 검증할 수 없는 영상입니다.', '다른 제품으로 시도해주세요'],
  },
  VERIFY_FAILED: {
    title: '검증을 멈췄어요',
    body: ['판정 중 문제가 생겼어요.', '다른 영상으로 시도해주세요'],
  },
}
