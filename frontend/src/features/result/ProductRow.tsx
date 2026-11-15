import { cn } from '@/lib/cn'

/** 백엔드 제품 매칭 결과 match_status 값 그대로 */
export type MatchStatus = 'confirmed' | 'unresolved' | 'not_found'

const STATUS: Record<MatchStatus, { text: string; square: string; color: string }> = {
  confirmed: { text: '식약처 등록 확인', square: 'bg-label-supported-vivid', color: 'text-label-supported' },
  unresolved: {
    text: '제품 후보가 여러 개예요',
    square: 'border-[1.5px] border-label-unclear-vivid',
    color: 'text-label-unclear',
  },
  not_found: {
    text: '식약처에서 찾지 못했어요',
    square: 'border-[1.5px] border-label-violation-vivid',
    color: 'text-label-violation',
  },
}

type ProductRowProps = {
  name: string
  maker: string
  status: MatchStatus
  className?: string
}

/** Figma v5/ProductRow — 결과 화면 영상 아래 제품 정보 한 줄 */
export function ProductRow({ name, maker, status, className }: ProductRowProps) {
  const s = STATUS[status]
  return (
    <div className={cn('flex flex-col gap-0.5 border-t border-line-hair py-4', className)}>
      <p className="text-body-m text-text-primary">{name}</p>
      <p className="text-small text-text-secondary">{maker}</p>
      <p className={cn('flex items-center gap-1.75 pt-1.5 text-mark', s.color)}>
        <span aria-hidden className={cn('size-2.5 shrink-0 rounded-status', s.square)} />
        {s.text}
      </p>
    </div>
  )
}
