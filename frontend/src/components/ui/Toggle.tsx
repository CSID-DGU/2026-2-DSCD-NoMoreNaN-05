import type { ButtonHTMLAttributes } from 'react'
import chevronDown from '@/assets/icons/chevron.svg'
import chevronUp from '@/assets/icons/chevron-up.svg'
import { cn } from '@/lib/cn'

type ToggleProps = Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'type'> & {
  /** 펼쳐져 있으면 위쪽 화살표 */
  open: boolean
}

/**
 * Figma v5/Toggle — "상세 결과 보기 ⌄" / "접기 ⌃" 같은 펼치기 버튼.
 * 글자는 children으로 받아요. 펼칠 영역의 id를 aria-controls로 넘겨 주세요.
 */
export function Toggle({ open, className, children, ...rest }: ToggleProps) {
  return (
    <button
      type="button"
      aria-expanded={open}
      className={cn(
        'inline-flex cursor-pointer items-center gap-1.5 text-small-m whitespace-nowrap text-text-primary',
        className,
      )}
      {...rest}
    >
      {children}
      <img src={open ? chevronUp : chevronDown} alt="" width={16} height={16} />
    </button>
  )
}
