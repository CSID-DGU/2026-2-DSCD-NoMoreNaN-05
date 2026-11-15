import { cn } from '@/lib/cn'

type NavItem = { key: string; label: string; href?: string }

// 서비스 소개·검증 기준·자주 묻는 질문은 아직 화면이 없어서 링크 없이 글자만 보여요.
const ITEMS: NavItem[] = [
  { key: 'home', label: '홈', href: '/' },
  { key: 'about', label: '서비스 소개' },
  { key: 'criteria', label: '검증 기준' },
  { key: 'faq', label: '자주 묻는 질문' },
]

type NavProps = {
  /** 밑줄로 표시할 메뉴. S1은 'home', S2·S3는 없음(null) */
  active?: 'home' | null
  className?: string
}

/** Figma v5/Nav — 모든 화면 맨 위 메뉴(높이 72). 로고·홈을 누르면 S1로 가요. */
export function Nav({ active = null, className }: NavProps) {
  return (
    <header
      className={cn(
        'flex h-nav w-full items-center justify-between border-b border-line-hair bg-bg-page px-gutter',
        className,
      )}
    >
      <a href="/" className="text-wordmark text-text-primary">
        TRUE<span className="text-brand-magenta">AD</span>
      </a>
      <nav aria-label="주 메뉴">
        <ul className="flex items-center gap-9">
          {ITEMS.map((item) => {
            const isActive = item.key === active
            const cls = cn(
              'block border-b-2 pt-6.25 pb-5.75 text-nav whitespace-nowrap',
              isActive ? 'border-text-primary text-text-primary' : 'border-transparent text-text-secondary',
            )
            return (
              <li key={item.key}>
                {item.href ? (
                  <a href={item.href} aria-current={isActive ? 'page' : undefined} className={cls}>
                    {item.label}
                  </a>
                ) : (
                  <span className={cls}>{item.label}</span>
                )}
              </li>
            )
          })}
        </ul>
      </nav>
    </header>
  )
}
