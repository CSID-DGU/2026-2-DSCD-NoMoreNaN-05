import { lazy, Suspense, useEffect, useState } from 'react'

// 개발 서버에서만 미리보기 페이지를 불러와요. 배포 빌드에서는 null이라 파일 자체가 빠져요.
const Gallery = import.meta.env.DEV ? lazy(() => import('@/dev/Gallery')) : null

function useHash() {
  const [hash, setHash] = useState(window.location.hash)
  useEffect(() => {
    const onChange = () => setHash(window.location.hash)
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])
  return hash
}

function App() {
  const hash = useHash()

  if (Gallery && hash === '#gallery') {
    return (
      <Suspense>
        <Gallery />
      </Suspense>
    )
  }

  return <main>TRUEAD</main>
}

export default App
