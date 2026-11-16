import { useId, useState } from 'react'
import { Tag } from '@/components/ui/Tag'
import { Toggle } from '@/components/ui/Toggle'
import type { LabelTone } from '@/lib/labels'
import { ClaimMeta } from '@/features/result/ClaimMeta'
import { type ClaimPart, ClaimPartRow } from '@/features/result/ClaimPart'
import { ResultCardFrame } from '@/features/result/ResultCardFrame'

type ClaimCardProps = {
  /** 카드 최종 라벨. 판정을 건너뛴 주장은 SKIPPED */
  tone: LabelTone
  productName?: string | null
  timeRange?: string | null
  /** 광고 속 주장 문장 */
  sentence: string
  /** 한 줄 설명 */
  explain?: string | null
  /** 건너뜀일 때 태그 왼쪽 안내 (예: 판정 건너뜀 · 제품 후보 여러 개) */
  skipNote?: string
  /** 상세 결과 행들. 비어 있으면 "상세 결과 보기"가 안 보여요. */
  parts?: ClaimPart[]
  defaultOpen?: boolean
  className?: string
}

/**
 * Figma v5/Card — 결과 화면 주장 카드 한 장 (라벨 6종 + 건너뜀).
 * "상세 결과 보기"로 펼치면 ClaimPart 행들이 나와요. 재생 버튼은 없어요(개발 노트 §5).
 */
export function ClaimCard({
  tone,
  productName,
  timeRange,
  sentence,
  explain,
  skipNote,
  parts = [],
  defaultOpen = false,
  className,
}: ClaimCardProps) {
  const [open, setOpen] = useState(defaultOpen)
  const detailId = useId()

  return (
    <ResultCardFrame tone={tone} className={className}>
      <div className="flex items-center justify-between gap-4">
        <ClaimMeta productName={productName} timeRange={timeRange} />
        <div className="flex shrink-0 items-center gap-2">
          {tone === 'SKIPPED' && skipNote && <p className="text-meta text-text-tertiary">{skipNote}</p>}
          <Tag tone={tone} />
        </div>
      </div>

      <p className="pt-2 text-claim text-text-primary">{sentence}</p>
      {explain && <p className="pt-1.5 text-small text-text-secondary">{explain}</p>}

      {open && parts.length > 0 && (
        <div id={detailId} className="pt-4.5">
          <div className="flex items-center justify-between pb-2.5">
            <p className="text-small-m text-text-primary">상세 결과</p>
            <p className="text-meta text-text-tertiary">확인한 부분 {parts.length}개</p>
          </div>
          {parts.map((part, i) => (
            <ClaimPartRow key={i} part={part} showTag={parts.length >= 2} />
          ))}
        </div>
      )}

      {parts.length > 0 && (
        <div className="pt-4">
          <Toggle open={open} aria-controls={detailId} onClick={() => setOpen((v) => !v)}>
            {open ? '접기' : '상세 결과 보기'}
          </Toggle>
        </div>
      )}
    </ResultCardFrame>
  )
}
