import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'
import { type LabelTone, toneColors } from '@/lib/labels'

type ResultCardFrameProps = {
  tone: LabelTone
  children: ReactNode
  className?: string
}

/** 주장 카드·묶음 카드 공통 틀 — 흰 카드 + 왼쪽 4px 라벨색 띠 */
export function ResultCardFrame({ tone, children, className }: ResultCardFrameProps) {
  return (
    <article
      className={cn(
        'relative flex flex-col overflow-hidden rounded-card border border-line-hair bg-bg-raised py-5 pr-6 pl-7',
        className,
      )}
    >
      <span aria-hidden className={cn('absolute inset-y-0 left-0 w-1', toneColors(tone).vivid)} />
      {children}
    </article>
  )
}
