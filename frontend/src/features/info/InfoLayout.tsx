import type { ReactNode } from 'react'
import { Footer } from '@/components/layout/Footer'
import { Nav, type NavKey } from '@/components/layout/Nav'
import { cn } from '@/lib/cn'

type InfoLayoutProps = {
  active: NavKey
  /** 맨 위 작은 분홍 글씨 (예: 서비스 소개) */
  eyebrow: string
  title: ReactNode
  sub: ReactNode
  /** 제목 오른쪽 그림 영역 */
  aside?: ReactNode
  /** 그림이 없을 때 머리 정렬 — 아래 본문 정렬에 맞춰요 (검증 기준: 왼쪽, 자주 묻는 질문: 가운데) */
  align?: 'left' | 'center'
  children: ReactNode
}

/** 서비스 소개·검증 기준·자주 묻는 질문 공통 틀 — S1과 같은 분홍 그라데이션 머리 + 본문 + 바닥글 */
export function InfoLayout({ active, eyebrow, title, sub, aside, align = 'left', children }: InfoLayoutProps) {
  const centered = !aside && align === 'center'
  return (
    <div className="flex min-h-screen flex-col bg-bg-page">
      <Nav active={active} />
      <div className="bg-linear-to-b from-bg-hero-top via-bg-hero-mid to-bg-page px-gutter">
        <div
          className={cn(
            'mx-auto flex w-full max-w-content gap-16 pt-20 pb-16',
            aside ? 'items-center justify-between' : centered ? 'flex-col items-center text-center' : 'flex-col',
          )}
        >
          <div className={cn('flex flex-col gap-4', aside ? 'max-w-130' : centered ? 'max-w-200 items-center' : 'max-w-260')}>
            <p className="text-small-m text-brand-magenta">{eyebrow}</p>
            <h1 className="text-hero text-text-primary">{title}</h1>
            <p className="text-lead text-text-secondary">{sub}</p>
          </div>
          {aside}
        </div>
      </div>
      <main className="flex-1 px-gutter pb-28">
        <div className="mx-auto w-full max-w-content">{children}</div>
      </main>
      <Footer />
    </div>
  )
}

type SectionProps = {
  id?: string
  title: string
  sub?: ReactNode
  children: ReactNode
  className?: string
}

/** 본문 한 덩어리 — 위 굵은 선 + 제목 */
export function InfoSection({ id, title, sub, children, className }: SectionProps) {
  return (
    <section id={id} aria-labelledby={id ? `${id}-title` : undefined} className={cn('pt-24', className)}>
      <div className="flex flex-col gap-2 pb-8">
        <h2 id={id ? `${id}-title` : undefined} className="text-title text-text-primary">
          {title}
        </h2>
        {sub && <p className="text-body text-text-secondary">{sub}</p>}
      </div>
      {children}
    </section>
  )
}

/** 아이콘 바탕 네모 (분홍) */
export function IconTile({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <span
      aria-hidden
      className={cn(
        'flex size-12 shrink-0 items-center justify-center rounded-card bg-bg-hero-top text-brand-magenta',
        className,
      )}
    >
      {children}
    </span>
  )
}
