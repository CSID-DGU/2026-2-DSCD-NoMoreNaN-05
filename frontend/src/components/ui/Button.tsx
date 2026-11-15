import type { ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  /** primary: 마젠타 바탕 / secondary: 흰 바탕 + 테두리. disabled면 종류와 상관없이 회색 */
  kind?: 'primary' | 'secondary'
}

/** Figma v5/Button — 검증하기, 결과 보기, 처음으로 돌아가기 */
export function Button({ kind = 'primary', className, disabled, type = 'button', ...rest }: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled}
      className={cn(
        'inline-flex items-center justify-center rounded-control px-5.5 py-3.25 text-body-m whitespace-nowrap',
        disabled
          ? 'cursor-not-allowed bg-bg-disabled text-text-disabled'
          : kind === 'primary'
            ? 'cursor-pointer bg-brand-magenta text-text-on-dark hover:bg-brand-magenta-strong'
            : 'cursor-pointer border border-line-mid bg-bg-raised text-text-primary hover:bg-bg-sunken',
        className,
      )}
      {...rest}
    />
  )
}
