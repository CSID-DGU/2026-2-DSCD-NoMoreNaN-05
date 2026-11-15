import type { InputHTMLAttributes, ReactNode } from 'react'
import switchOff from '@/assets/icons/switch-off.svg'
import switchOn from '@/assets/icons/switch-on.svg'
import { cn } from '@/lib/cn'

type SwitchProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'checked' | 'onChange'> & {
  checked: boolean
  onCheckedChange: (checked: boolean) => void
  /** 옆에 보일 글자. 글자 없이 쓸 때는 aria-label을 꼭 넘겨 주세요. */
  children?: ReactNode
}

/**
 * Figma v5/Switch (32×18) — 제품별 보기에서 제품 켜고 끄기.
 * 실제 입력은 숨긴 checkbox(role=switch)라서 키보드(Space)·스크린리더가 그대로 동작해요.
 */
export function Switch({ checked, onCheckedChange, children, className, ...rest }: SwitchProps) {
  return (
    <label className={cn('inline-flex cursor-pointer items-center gap-2', className)}>
      <input
        type="checkbox"
        role="switch"
        className="peer sr-only"
        checked={checked}
        onChange={(e) => onCheckedChange(e.target.checked)}
        {...rest}
      />
      <img
        src={checked ? switchOn : switchOff}
        alt=""
        width={32}
        height={18}
        className="rounded-pill peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-brand-magenta"
      />
      {children}
    </label>
  )
}
