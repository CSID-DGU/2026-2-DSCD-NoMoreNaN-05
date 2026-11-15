import { cn } from '@/lib/cn'
import { type LabelTone, toneColors } from '@/lib/labels'

type TagProps = {
  tone: LabelTone
  /** md: 카드 오른쪽 위 최종 라벨 / sm: 상세 행 아래 부분별 라벨 */
  size?: 'md' | 'sm'
  className?: string
}

/**
 * Figma v5/Tag — 라벨 이름이 든 알약 모양 표시.
 * 건너뜀(SKIPPED)은 "판단 보류" 글자 + 노랑 점선 테두리, 바탕 없음.
 */
export function Tag({ tone, size = 'md', className }: TagProps) {
  const c = toneColors(tone)
  return (
    <span
      className={cn(
        'inline-flex shrink-0 items-start rounded-pill whitespace-nowrap',
        size === 'md' ? 'px-2.5 py-0.75 text-meta-m' : 'px-2 py-px text-tag-sm',
        c.text,
        tone === 'SKIPPED' ? 'border border-dashed border-label-unclear-vivid' : c.tint,
        className,
      )}
    >
      {c.name}
    </span>
  )
}
