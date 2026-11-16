import { useEffect, useId, useRef, useState } from 'react'
import chevronDown from '@/assets/icons/chevron.svg'
import chevronUp from '@/assets/icons/chevron-up.svg'
import { Checkbox } from '@/components/ui/Checkbox'
import type { Product } from '@/lib/api/types'

type ProductFilterProps = {
  products: Product[]
  /** 제품별 주장 수 */
  claimCounts: Record<string, number>
  /** 제품이 연결되지 않은 주장 수 — 필터와 상관없이 항상 보여요 */
  unlinkedCount: number
  enabled: ReadonlySet<string>
  onChange: (next: Set<string>) => void
}

/**
 * Figma S3-P2·P3 제품 목록 — 제품이 2개 이상일 때만 '주장별 결과' 옆에 보여요(개발 노트 §6).
 * 체크를 끄면 그 제품의 주장 카드가 목록에서 빠져요. 6개를 넘으면 목록 안에서 스크롤돼요.
 */
export function ProductFilter({ products, claimCounts, unlinkedCount, enabled, onChange }: ProductFilterProps) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const panelId = useId()
  const allOn = enabled.size === products.length

  // 바깥을 누르거나 Esc를 누르면 닫혀요
  useEffect(() => {
    if (!open) return
    const onPointer = (e: PointerEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false)
    }
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false)
    document.addEventListener('pointerdown', onPointer)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('pointerdown', onPointer)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  const toggle = (ref: string, on: boolean) => {
    const next = new Set(enabled)
    if (on) next.add(ref)
    else next.delete(ref)
    onChange(next)
  }

  const label = allOn ? `제품 ${products.length}개 전체` : `제품 ${enabled.size}개 선택`

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((v) => !v)}
        className="inline-flex cursor-pointer items-center gap-1.5 text-mark text-brand-magenta-strong"
      >
        {label}
        <img src={open ? chevronUp : chevronDown} alt="" width={16} height={16} />
      </button>

      {open && (
        <div
          id={panelId}
          className="absolute top-full right-0 z-20 mt-2 flex w-80 flex-col rounded-popover border border-line-hair bg-bg-raised px-3 py-2 shadow-popover"
        >
          <div className="flex items-center justify-between px-1 py-1.5 text-meta">
            <span className="text-text-tertiary">제품 {products.length}개</span>
            <span className="flex gap-3 text-meta-m text-brand-magenta-strong">
              <button type="button" className="cursor-pointer" onClick={() => onChange(new Set(products.map((p) => p.product_ref)))}>
                전체 선택
              </button>
              <button type="button" className="cursor-pointer" onClick={() => onChange(new Set())}>
                전체 해제
              </button>
            </span>
          </div>
          <ul className="max-h-54 overflow-y-auto">
            {products.map((p) => (
              <li key={p.product_ref}>
                <Checkbox
                  checked={enabled.has(p.product_ref)}
                  onCheckedChange={(on) => toggle(p.product_ref, on)}
                  className="h-9 w-full rounded-checkbox px-1 hover:bg-bg-sunken"
                >
                  <span className="min-w-0 flex-1 truncate text-mark text-text-primary">
                    {p.product_name ?? p.brand_name ?? '제품명 확인 안 됨'}
                  </span>
                  <span className="text-meta text-text-tertiary">{claimCounts[p.product_ref] ?? 0}</span>
                </Checkbox>
              </li>
            ))}
          </ul>
          {unlinkedCount > 0 && (
            <p className="flex justify-between border-t border-line-hair px-1 pt-2 pb-1 text-meta">
              <span className="text-text-secondary">제품 연결 안 됨 {unlinkedCount}</span>
              <span className="text-text-tertiary">항상 표시</span>
            </p>
          )}
        </div>
      )}
    </div>
  )
}
