import { Check } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'
import { Toggle } from '@/components/ui/Toggle'
import type { SortKey } from '@/features/result/resultModel'
import { cn } from '@/lib/cn'

const OPTIONS: { key: SortKey; name: string }[] = [
  { key: 'RISK', name: '위험도 순' },
  { key: 'APPEARANCE', name: '영상 등장 순' },
]

/** 라벨 탭 아래 오른쪽 정렬 고르기 — 누르면 아래로 목록이 열려요 */
export function SortSwitch({ value, onChange }: { value: SortKey; onChange: (next: SortKey) => void }) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const menuId = useId()

  // 바깥을 누르거나 Esc를 누르면 닫혀요 (제품 필터와 같게)
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

  const current = OPTIONS.find((o) => o.key === value) ?? OPTIONS[0]

  return (
    <div ref={rootRef} className="relative">
      {/* 탭보다 눈에 덜 띄게 — 굵기는 두고 글자색만 한 단계 연하게 */}
      <Toggle
        open={open}
        aria-controls={menuId}
        aria-label={`정렬: ${current.name}`}
        onClick={() => setOpen((v) => !v)}
        className="text-text-secondary!"
      >
        {current.name}
      </Toggle>
      {open && (
        <ul
          id={menuId}
          className="absolute top-full right-0 z-20 mt-2 flex w-44 flex-col rounded-popover border border-line-hair bg-bg-raised p-1.5 shadow-popover"
        >
          {OPTIONS.map(({ key, name }) => (
            <li key={key}>
              <button
                type="button"
                aria-pressed={value === key}
                onClick={() => {
                  onChange(key)
                  setOpen(false)
                }}
                className={cn(
                  'flex h-9 w-full cursor-pointer items-center justify-between rounded-checkbox px-2.5 text-small hover:bg-bg-sunken',
                  value === key ? 'text-small-m text-text-primary' : 'text-text-secondary',
                )}
              >
                {name}
                {value === key && <Check aria-hidden size={16} className="text-brand-magenta-strong" />}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
