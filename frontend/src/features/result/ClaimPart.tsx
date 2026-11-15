import { Tag } from '@/components/ui/Tag'
import type { LabelTone } from '@/lib/labels'

/**
 * 주장 카드 "상세 결과" 안의 한 줄 (Figma v5/Part ①~④).
 * - compare: 광고 값 ↔ 식약처 값 두 칸 비교 (Part/Compare, Part/Expression은 모양이 같아 하나로)
 * - reason: 판단 사유 문장 (Part/Reason)
 * - notice: 판정하지 않은 이유 안내 (Part/Notice)
 */
export type ClaimPart =
  | {
      kind: 'compare'
      /** 왼쪽 열 항목 이름 (섭취 방법, 효능 표현 …) */
      item: string
      /** 항목 이름 아래 작은 글자 (예: 간접 확인) */
      itemNote?: string
      /** 이 부분만의 판정 — 상세 행이 2개 이상일 때 작은 태그로 보여요 */
      tone?: LabelTone
      aHead: string
      aValue: string
      bHead: string
      bValue: string
      explain?: string
    }
  | {
      kind: 'reason'
      item: string
      itemNote?: string
      tone?: LabelTone
      /** 예: 판단 사유 · 광고가 모호함 */
      head: string
      text: string
      /** 예: 확인한 대상 · 아유르베다 고서 */
      target?: string
    }
  | {
      kind: 'notice'
      item: string
      /** 예: 판정 건너뜀 · 제품을 찾지 못함 */
      head: string
      text: string
    }

type ClaimPartRowProps = {
  part: ClaimPart
  /** 부분별 라벨 태그 보이기 — 상세 행이 2개 이상일 때만 (개발 노트 §5) */
  showTag: boolean
}

export function ClaimPartRow({ part, showTag }: ClaimPartRowProps) {
  const tone = part.kind === 'notice' ? undefined : part.tone
  const itemNote = part.kind === 'notice' ? undefined : part.itemNote
  return (
    <div className="flex items-start gap-5 border-t border-line-hair pt-4.5 pb-5">
      <div className="flex w-28 shrink-0 flex-col items-start gap-1.5">
        <p className="text-small-m text-text-secondary">{part.item}</p>
        {itemNote && <p className="text-meta text-text-tertiary">{itemNote}</p>}
        {showTag && tone && <Tag tone={tone} size="sm" />}
      </div>

      {part.kind === 'compare' ? (
        <div className="flex min-w-0 flex-1 flex-col gap-3">
          <div className="flex gap-8">
            <div className="flex min-w-0 flex-1 flex-col gap-1">
              <p className="text-meta text-text-tertiary">{part.aHead}</p>
              <p className="text-body text-text-primary">{part.aValue}</p>
            </div>
            <div className="flex min-w-0 flex-1 flex-col gap-1">
              <p className="text-meta text-text-tertiary">{part.bHead}</p>
              <p className="text-body text-text-primary">{part.bValue}</p>
            </div>
          </div>
          {part.explain && <p className="text-small text-text-secondary">{part.explain}</p>}
        </div>
      ) : (
        <div className="flex min-w-0 flex-1 flex-col gap-1">
          <p className="text-meta text-text-tertiary">{part.head}</p>
          <p className="text-body text-text-primary">{part.text}</p>
          {part.kind === 'reason' && part.target && (
            <p className="text-meta text-text-tertiary">{part.target}</p>
          )}
        </div>
      )}
    </div>
  )
}
