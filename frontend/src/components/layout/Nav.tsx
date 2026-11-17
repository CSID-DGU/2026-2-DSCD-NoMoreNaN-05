import { Link } from 'react-router'
import { cn } from '@/lib/cn'

export type NavKey = 'verify' | 'about' | 'criteria' | 'faq'

const ITEMS: { key: NavKey; label: string; href: string }[] = [
  { key: 'verify', label: '광고 검증', href: '/' },
  { key: 'about', label: '서비스 소개', href: '/about' },
  { key: 'criteria', label: '검증 기준', href: '/criteria' },
  { key: 'faq', label: '자주 묻는 질문', href: '/faq' },
]

type NavProps = {
  /** 밑줄로 표시할 메뉴. 검증 흐름(S1·S2·S3)은 모두 'verify', 오류 화면은 null */
  active?: NavKey | null
  className?: string
}

/** Figma v5/Nav — 모든 화면 맨 위 메뉴(높이 72). 로고·광고 검증을 누르면 S1로 가요. */
export function Nav({ active = null, className }: NavProps) {
  return (
    <header
      className={cn(
        'flex h-nav w-full items-center justify-between border-b border-line-hair bg-bg-page px-gutter',
        className,
      )}
    >
      <Link to="/" className="text-wordmark text-text-primary">
        TRUE<span className="text-brand-magenta">AD</span>
      </Link>
      <nav aria-label="주 메뉴">
        <ul className="flex items-center gap-9">
          {ITEMS.map((item) => {
            const isActive = item.key === active
            return (
              <li key={item.key}>
                <Link
                  to={item.href}
                  aria-current={isActive ? 'page' : undefined}
                  className={cn(
                    'block border-b-2 pt-6.25 pb-5.75 text-nav whitespace-nowrap transition-colors',
                    isActive
                      ? 'border-text-primary text-text-primary'
                      : 'border-transparent text-text-secondary hover:text-text-primary',
                  )}
                >
                  {item.label}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
    </header>
  )
}
