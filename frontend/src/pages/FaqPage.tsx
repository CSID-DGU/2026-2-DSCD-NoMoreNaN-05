import { Search } from 'lucide-react'
import { useState } from 'react'
import { AccordionItem } from '@/components/ui/Accordion'
import { InfoLayout } from '@/features/info/InfoLayout'
import { FAQ_CATEGORIES, FAQ_ITEMS, type FaqCategory } from '@/features/info/faqItems'
import { cn } from '@/lib/cn'

type Filter = 'all' | FaqCategory

/** 자주 묻는 질문 */
export default function FaqPage() {
  const [filter, setFilter] = useState<Filter>('all')
  const [query, setQuery] = useState('')

  const q = query.trim()
  const items = FAQ_ITEMS.filter(
    (it) => (filter === 'all' || it.category === filter) && (!q || it.q.includes(q) || it.a.some((a) => a.includes(q))),
  )
  const tabs: { key: Filter; label: string }[] = [{ key: 'all', label: '전체' }, ...FAQ_CATEGORIES]

  return (
    <InfoLayout
      active="faq"
      eyebrow="자주 묻는 질문"
      title="무엇이 궁금하세요?"
      sub="TRUEAD를 쓰면서 많이 궁금해하시는 내용을 모았어요."
    >
      <div className="mx-auto flex max-w-200 flex-col">
        <label className="flex h-13 items-center gap-2.5 rounded-control border border-line-mid bg-bg-raised px-4 focus-within:border-text-secondary">
          <Search aria-hidden size={18} className="text-text-tertiary" />
          <span className="sr-only">질문 검색</span>
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="궁금한 내용을 검색해 보세요 (예: 판단 보류)"
            className="min-w-0 flex-1 bg-transparent text-body text-text-primary outline-none placeholder:text-text-disabled"
          />
        </label>

        <div role="group" aria-label="질문 분류" className="flex gap-2 pt-6">
          {tabs.map((t) => {
            const count = FAQ_ITEMS.filter((it) => t.key === 'all' || it.category === t.key).length
            const selected = filter === t.key
            return (
              <button
                key={t.key}
                type="button"
                aria-pressed={selected}
                onClick={() => setFilter(t.key)}
                className={cn(
                  'rounded-pill border px-4 py-2 text-small-m transition-colors',
                  selected
                    ? 'border-text-primary bg-text-primary text-text-on-dark'
                    : 'border-line-hair text-text-secondary hover:border-text-secondary hover:text-text-primary',
                )}
              >
                {t.label} <span className={selected ? 'opacity-70' : 'text-text-disabled'}>{count}</span>
              </button>
            )
          })}
        </div>

        <div className="mt-8 border-t border-line-strong">
          {items.map((it, i) => (
            // 검색어·분류가 바뀌면 펼침 상태를 처음으로
            <AccordionItem key={`${filter}-${q}-${it.q}`} question={it.q} defaultOpen={i === 0 && filter === 'all' && !q}>
              {it.a.map((p) => (
                <p key={p}>{p}</p>
              ))}
            </AccordionItem>
          ))}
          {items.length === 0 && (
            <p className="py-16 text-center text-body text-text-secondary">‘{q}’에 맞는 질문이 없어요</p>
          )}
        </div>

      </div>
    </InfoLayout>
  )
}
