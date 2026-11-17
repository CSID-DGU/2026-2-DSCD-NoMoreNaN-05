import { TriangleAlert } from 'lucide-react'
import { useEffect } from 'react'
import { useRouteError } from 'react-router'
import { Footer } from '@/components/layout/Footer'
import { Nav } from '@/components/layout/Nav'
import { Button } from '@/components/ui/Button'

/**
 * 예상 못 한 오류 화면 — 화면을 그리다 코드가 멈추면(예: 명세와 다른 응답) 흰 화면 대신 이걸 보여요.
 * 서버가 알려 주는 실패(추출 실패·비공개 영상·없는 작업 등)는 각 화면이 따로 안내해서 여기로 오지 않아요.
 */
export default function ErrorPage() {
  const error = useRouteError()

  useEffect(() => {
    console.error('[TRUEAD] 화면 오류', error)
  }, [error])

  // 멈춘 화면의 상태·캐시가 남지 않도록 페이지를 새로 불러요
  const goHome = () => window.location.assign('/')
  const retry = () => window.location.reload()

  return (
    <div className="flex min-h-screen flex-col bg-bg-page">
      <Nav />
      <main className="flex flex-1 flex-col items-center justify-center px-gutter py-24 text-center">
        <span
          aria-hidden
          className="flex size-14 items-center justify-center rounded-pill bg-label-violation-tint text-label-violation"
        >
          <TriangleAlert size={26} />
        </span>
        <h1 className="pt-6 text-title text-text-primary">화면을 보여 드리는 중에 문제가 생겼어요</h1>
        <p className="max-w-130 pt-3 text-body text-text-secondary">
          잠시 후 다시 시도해 주세요. 같은 문제가 계속되면 처음 화면에서 영상 주소를 다시 넣어 주세요.
        </p>
        <div className="flex gap-2 pt-8">
          <Button kind="secondary" className="w-40" onClick={retry}>
            다시 시도
          </Button>
          <Button className="w-40" onClick={goHome}>
            처음으로
          </Button>
        </div>
      </main>
      <Footer />
    </div>
  )
}
