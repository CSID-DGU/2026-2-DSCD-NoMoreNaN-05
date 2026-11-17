import type { ReactNode } from 'react'
import { Footer } from '@/components/layout/Footer'
import { Nav } from '@/components/layout/Nav'
import { cn } from '@/lib/cn'

/**
 * S2 처리 중 · S3 결과 공통 틀 — 리포트 시트 디자인 (Figma S3-01 기본 · 리포트 시트 B).
 * 연한 분홍 그라데이션 배경 위에 흰 시트를 깔고 그 안에 내용을 넣어요.
 * 되돌리려면 이 틀을 쓰는 두 화면을 예전처럼 Nav + main + Footer로 바꾸면 돼요.
 */
type SheetPageProps = {
  children: ReactNode
  /** 내용이 짧아도 시트를 바닥글 앞까지 늘려요 (S2) */
  fill?: boolean
}

export function SheetPage({ children, fill = false }: SheetPageProps) {
  return (
    // 배경: 연한 분홍 → 흰색 그라데이션. 경계는 시트 테두리·그림자로 구분해요
    <div className="flex min-h-screen flex-col bg-bg-page bg-linear-to-b from-bg-hero-mid to-bg-page to-50%">
      <Nav active="verify" />
      <main className={cn('flex-1 px-5 pt-6 pb-10', fill && 'flex flex-col')}>
        <div
          className={cn(
            'mx-auto w-full max-w-sheet rounded-sheet border border-line-mid/60 bg-bg-raised px-14 pt-14 pb-16 shadow-sheet',
            fill && 'flex-1',
          )}
        >
          {children}
        </div>
      </main>
      <Footer />
    </div>
  )
}
