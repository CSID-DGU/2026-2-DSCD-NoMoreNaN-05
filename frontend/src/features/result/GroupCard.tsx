import { useId, useState } from 'react'
import { Tag } from '@/components/ui/Tag'
import { Toggle } from '@/components/ui/Toggle'
import { ClaimMeta } from '@/features/result/ClaimMeta'
import { ResultCardFrame } from '@/features/result/ResultCardFrame'

export type GroupItem = {
  productName?: string | null
  timeRange?: string | null
  sentence: string
  /** 문장 아래 작은 설명 (예: 광고 속 고지 문구예요) */
  note?: string
}

const GROUPS = {
  OUT_OF_SCOPE: {
    title: (n: number) => `검증 대상이 아닌 문장 ${n}개`,
    description: '가격·판매 순위·시험 조건·인물처럼 공식 정보로 확인하지 않는 문장이에요.',
  },
  DISCLAIMER: {
    title: (n: number) => `면책 문구 ${n}개`,
    description: '판정 대상이 아닌 광고 속 고지 문구예요.',
  },
} as const

type GroupCardProps = {
  tone: keyof typeof GROUPS
  items: GroupItem[]
  defaultOpen?: boolean
  className?: string
}

/**
 * Figma v5/GroupCard — 검증 대상 아님·면책 문구를 한 장에 묶은 카드.
 * "문장 펼치기"로 문장 목록이 나와요. 문장은 글자만, 재생 버튼 없음(개발 노트 §5).
 */
export function GroupCard({ tone, items, defaultOpen = false, className }: GroupCardProps) {
  const [open, setOpen] = useState(defaultOpen)
  const listId = useId()
  const g = GROUPS[tone]

  return (
    <ResultCardFrame tone={tone} className={className}>
      <div className="flex items-center justify-between gap-4">
        <p className="text-body-m text-text-primary">{g.title(items.length)}</p>
        <Tag tone={tone} />
      </div>
      <p className="pt-1 text-small text-text-secondary">{g.description}</p>

      {open && (
        <ul id={listId} className="pt-3.5">
          {items.map((item, i) => (
            <li key={i} className="flex flex-col gap-0.5 border-t border-line-hair py-3">
              <ClaimMeta productName={item.productName} timeRange={item.timeRange} />
              <p className="text-body text-text-primary">{item.sentence}</p>
              {item.note && <p className="text-meta text-text-tertiary">{item.note}</p>}
            </li>
          ))}
        </ul>
      )}

      <div className="pt-3.5">
        <Toggle open={open} aria-controls={listId} onClick={() => setOpen((v) => !v)}>
          {open ? '접기' : '문장 펼치기'}
        </Toggle>
      </div>
    </ResultCardFrame>
  )
}
