import { ChevronDown } from 'lucide-react'
import { type ReactNode, useId, useState } from 'react'
import { cn } from '@/lib/cn'

type AccordionItemProps = {
  question: string
  children: ReactNode
  defaultOpen?: boolean
}

/** 질문을 누르면 답이 펼쳐지는 한 줄 (자주 묻는 질문) */
export function AccordionItem({ question, children, defaultOpen = false }: AccordionItemProps) {
  const [open, setOpen] = useState(defaultOpen)
  const panelId = useId()
  return (
    <div className="border-b border-line-hair">
      <h3>
        <button
          type="button"
          aria-expanded={open}
          aria-controls={panelId}
          onClick={() => setOpen((v) => !v)}
          className="flex w-full items-center gap-4 py-6 text-left text-h3 text-text-primary hover:text-brand-magenta"
        >
          <span aria-hidden className="text-brand-magenta">
            Q
          </span>
          <span className="flex-1">{question}</span>
          <ChevronDown
            aria-hidden
            size={20}
            className={cn('shrink-0 text-text-tertiary transition-transform duration-200', open && 'rotate-180')}
          />
        </button>
      </h3>
      {/* 높이 0 ↔ 내용 높이로 부드럽게 펼쳐요 */}
      <div
        id={panelId}
        role="region"
        className={cn('grid transition-[grid-template-rows] duration-200', open ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]')}
      >
        <div className="overflow-hidden" inert={!open}>
          <div className="flex flex-col gap-2 pb-7 pl-8 text-body text-text-secondary">{children}</div>
        </div>
      </div>
    </div>
  )
}
