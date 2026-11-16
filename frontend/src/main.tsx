import { QueryClientProvider } from '@tanstack/react-query'
import { StrictMode, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router'
import '@/index.css'
import { queryClient } from '@/lib/queryClient'
import { router } from '@/router'

// 개발 중 백엔드 없이 볼 때만: .env.local에 VITE_API_MOCK=true (배포 빌드에서는 이 코드가 빠져요)
if (import.meta.env.DEV && import.meta.env.VITE_API_MOCK === 'true') {
  const { installMockApi } = await import('@/mocks/mockApi')
  installMockApi()
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <Suspense>
        <RouterProvider router={router} />
      </Suspense>
    </QueryClientProvider>
  </StrictMode>,
)
