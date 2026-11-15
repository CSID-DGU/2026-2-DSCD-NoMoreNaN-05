import { cn } from '@/lib/cn'

/** 라벨 6종 + 일치·간접 확인 + 건너뜀 + 대기 */
export type MarkTone =
  | 'VIOLATION'
  | 'OVERCLAIM'
  | 'UNCLEAR'
  | 'SUPPORTED'
  | 'SUPPORTED_INDIRECT'
  | 'OUT_OF_SCOPE'
  | 'DISCLAIMER'
  | 'SKIPPED'
  | 'PENDING'

// 네모 모양(채움 / 1.5px 테두리 / 점선)과 글자색이 라벨마다 달라서 표로 적어요.
const MARKS: Record<MarkTone, { name: string; square: string; text: string }> = {
  VIOLATION: { name: '위반', square: 'bg-label-violation-vivid', text: 'text-label-violation' },
  OVERCLAIM: { name: '과장', square: 'bg-label-overclaim-vivid', text: 'text-label-overclaim' },
  UNCLEAR: { name: '판단 보류', square: 'bg-label-unclear-vivid', text: 'text-label-unclear' },
  SUPPORTED: { name: '일치', square: 'bg-label-supported-vivid', text: 'text-label-supported' },
  SUPPORTED_INDIRECT: {
    name: '일치 · 간접 확인',
    square: 'border-[1.5px] border-label-supported-vivid',
    text: 'text-label-supported',
  },
  OUT_OF_SCOPE: {
    name: '검증 대상 아님',
    square: 'bg-label-outofscope-vivid',
    text: 'text-label-outofscope',
  },
  DISCLAIMER: {
    name: '면책 문구',
    square: 'border-[1.5px] border-label-disclaimer-vivid',
    text: 'text-label-disclaimer',
  },
  SKIPPED: {
    name: '판단 보류',
    square: 'border-[1.5px] border-dashed border-label-unclear-vivid',
    text: 'text-label-unclear',
  },
  PENDING: { name: '대기', square: 'border-[1.5px] border-label-pending', text: 'text-text-tertiary' },
}

type MarkProps = {
  tone: MarkTone
  className?: string
}

/** Figma v5/Mark — 작은 색 네모 + 라벨 이름 (범례·목록용) */
export function Mark({ tone, className }: MarkProps) {
  const m = MARKS[tone]
  return (
    <span className={cn('inline-flex items-center gap-1.75 text-mark whitespace-nowrap', m.text, className)}>
      <span aria-hidden className={cn('size-2.5 shrink-0 rounded-status', m.square)} />
      {m.name}
    </span>
  )
}
