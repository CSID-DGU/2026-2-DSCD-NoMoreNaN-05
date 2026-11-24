/**
 * 판정 라벨 정의 — 라벨 이름·색은 이 파일 한 곳에서만 정해요.
 * 값(VIOLATION 등)은 백엔드 판정 결과의 라벨 이름과 같아요.
 * 색은 Figma 개발 노트 §8 (styles/labels.css 토큰).
 */

export const LABELS = [
  'VIOLATION',
  'OVERCLAIM',
  'UNCLEAR',
  'SUPPORTED',
  'OUT_OF_SCOPE',
  'DISCLAIMER',
] as const

export type Label = (typeof LABELS)[number]

/**
 * 화면에 보이는 상태. 라벨 6종 + 판정을 건너뛴 주장(skipped).
 * 건너뜀은 "판단 보류" 글자에 점선 테두리로 보여요(Figma v5/Tag label=건너뜀).
 */
export type LabelTone = Label | 'SKIPPED'

type LabelStyle = {
  /** 화면에 보이는 이름 */
  name: string
  /** 글자 색 */
  text: string
  /** 카드 왼쪽 띠·칩 점 */
  vivid: string
  /** 태그·칩 바탕 */
  tint: string
  /** 칩 테두리 */
  line: string
  /** 클레임 문장 형광펜 — 글자 아래쪽 절반에 아주 연한 라벨 색(tint) */
  mark: string
}

// Tailwind는 파일에 적힌 클래스 이름만 만들어요. 그래서 클래스 이름을 조합하지 않고 통째로 적어요.
export const LABEL_STYLES: Record<Label, LabelStyle> = {
  VIOLATION: {
    name: '위반',
    text: 'text-label-violation',
    vivid: 'bg-label-violation-vivid',
    tint: 'bg-label-violation-tint',
    line: 'border-label-violation-line',
    mark: 'bg-[linear-gradient(transparent_52%,var(--color-label-violation-tint)_52%)]',
  },
  OVERCLAIM: {
    name: '과장',
    text: 'text-label-overclaim',
    vivid: 'bg-label-overclaim-vivid',
    tint: 'bg-label-overclaim-tint',
    line: 'border-label-overclaim-line',
    mark: 'bg-[linear-gradient(transparent_52%,var(--color-label-overclaim-tint)_52%)]',
  },
  UNCLEAR: {
    name: '판단 보류',
    text: 'text-label-unclear',
    vivid: 'bg-label-unclear-vivid',
    tint: 'bg-label-unclear-tint',
    line: 'border-label-unclear-line',
    mark: 'bg-[linear-gradient(transparent_52%,var(--color-label-unclear-tint)_52%)]',
  },
  SUPPORTED: {
    name: '일치',
    text: 'text-label-supported',
    vivid: 'bg-label-supported-vivid',
    tint: 'bg-label-supported-tint',
    line: 'border-label-supported-line',
    mark: 'bg-[linear-gradient(transparent_52%,var(--color-label-supported-tint)_52%)]',
  },
  OUT_OF_SCOPE: {
    name: '검증 대상 아님',
    text: 'text-label-outofscope',
    vivid: 'bg-label-outofscope-vivid',
    tint: 'bg-label-outofscope-tint',
    line: 'border-label-outofscope-line',
    mark: 'bg-[linear-gradient(transparent_52%,var(--color-label-outofscope-tint)_52%)]',
  },
  DISCLAIMER: {
    name: '면책 문구',
    text: 'text-label-disclaimer',
    vivid: 'bg-label-disclaimer-vivid',
    tint: 'bg-label-disclaimer-tint',
    line: 'border-label-disclaimer-line',
    mark: 'bg-[linear-gradient(transparent_52%,var(--color-label-disclaimer-tint)_52%)]',
  },
}

/** 건너뜀은 판단 보류 색을 그대로 써요(노랑). 색을 고를 때 이 함수로 바꿔서 찾아요. */
export function toneColors(tone: LabelTone): LabelStyle {
  return LABEL_STYLES[tone === 'SKIPPED' ? 'UNCLEAR' : tone]
}

/**
 * 한 문장의 결과를 고르는 순서 (면책 문구는 그 전에 먼저 골라내서 빠져요) — 팀 문서 §2-1.
 * 검증 기준 페이지와 결과 화면 '위험도 순' 정렬이 함께 써요.
 */
export const LABEL_PRIORITY: readonly Label[] = ['VIOLATION', 'OVERCLAIM', 'UNCLEAR', 'SUPPORTED', 'OUT_OF_SCOPE']

/** 확인 필요 = 위반 + 과장 + 판단 보류 (결과 화면 헤드라인, 개발 노트 §4) */
export const NEEDS_REVIEW: readonly Label[] = ['VIOLATION', 'OVERCLAIM', 'UNCLEAR']
