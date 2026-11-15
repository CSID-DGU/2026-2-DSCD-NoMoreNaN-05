import type { InputHTMLAttributes, ReactNode } from 'react'
import check from '@/assets/icons/check.svg'
import { cn } from '@/lib/cn'

type CheckboxProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'checked' | 'onChange'> & {
  checked: boolean
  onCheckedChange: (checked: boolean) => void
  /** 옆에 보일 글자. 글자 없이 쓸 때는 aria-label을 꼭 넘겨 주세요. */
  children?: ReactNode
}

/**
 * Figma v5/Checkbox (18×18) — 제품 목록에서 여러 개 고르기.
 * 실제 입력은 숨긴 checkbox라서 키보드(Space)·스크린리더가 그대로 동작해요.
 */
export function Checkbox({ checked, onCheckedChange, children, className, ...rest }: CheckboxProps) {
  return (
    <label className={cn('inline-flex cursor-pointer items-center gap-2', className)}>
      <input
        type="checkbox"
        className="peer sr-only"
        checked={checked}
        onChange={(e) => onCheckedChange(e.target.checked)}
        {...rest}
      />
      <span
        aria-hidden
        className={cn(
          'flex size-4.5 shrink-0 items-center justify-center rounded-checkbox',
          'peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-brand-magenta',
          checked ? 'bg-brand-magenta' : 'border-[1.5px] border-line-mid bg-bg-page',
        )}
      >
        {checked && <img src={check} alt="" width={18} height={18} />}
      </span>
      {children}
    </label>
  )
}
