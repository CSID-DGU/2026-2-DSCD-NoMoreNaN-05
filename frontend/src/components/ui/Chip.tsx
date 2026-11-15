import { cn } from '@/lib/cn'
import { type Label, LABEL_STYLES } from '@/lib/labels'

type ChipProps = {
  label: Label
  count: number
  className?: string
}

/**
 * Figma v5/Chip — 결과 화면 맨 위 라벨별 개수 (예: ● 위반 1).
 * 0건이어도 칩은 보여요(개발 노트 §4). 누를 수 없는 표시용이에요.
 */
export function Chip({ label, count, className }: ChipProps) {
  const c = LABEL_STYLES[label]
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-pill border px-3 py-1 text-chip-label whitespace-nowrap',
        c.tint,
        c.line,
        c.text,
        className,
      )}
    >
      <span aria-hidden className={cn('size-2 shrink-0 rounded-full', c.vivid)} />
      {c.name} {count}
    </span>
  )
}
