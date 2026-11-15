import type { ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

type TabProps = Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'type'> & {
  selected: boolean
  /** 해당 건수가 0이면 흐린 글자. 눌러서 선택할 수는 있어요(조합 결과 없음 화면). */
  empty?: boolean
}

/**
 * Figma v5/Tab — 결과 목록 필터 탭 (전체 19 · 위반 1 …).
 * 여러 개를 role="tablist"인 요소로 감싸서 써요.
 */
export function Tab({ selected, empty = false, className, ...rest }: TabProps) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={selected}
      className={cn(
        // 선택 안 된 탭도 투명한 밑줄을 둬서 선택이 바뀌어도 높이가 그대로예요.
        'cursor-pointer border-b-2 pt-2.5 pb-3 text-small-m whitespace-nowrap',
        selected
          ? 'border-text-primary text-text-primary'
          : cn('border-transparent', empty ? 'text-text-tertiary' : 'text-text-secondary'),
        className,
      )}
      {...rest}
    />
  )
}
