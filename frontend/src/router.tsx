import { lazy } from 'react'
import { createBrowserRouter, Navigate, type RouteObject } from 'react-router'
import { RootLayout } from '@/components/layout/RootLayout'
import AboutPage from '@/pages/AboutPage'
import CheckPage from '@/pages/CheckPage'
import CriteriaPage from '@/pages/CriteriaPage'
import InputPage from '@/pages/InputPage'
import ResultPage from '@/pages/ResultPage'

// 개발 서버에서만 컴포넌트 미리보기(/gallery)를 열어요. 배포 빌드에서는 파일 자체가 빠져요.
const Gallery = import.meta.env.DEV ? lazy(() => import('@/dev/Gallery')) : null

const routes: RouteObject[] = [
  { path: '/', element: <InputPage /> },
  // 명세: 작업을 만들면 /check/{jobId}로 들어가 상태를 폴링해요.
  { path: '/check/:jobId', element: <CheckPage /> },
  { path: '/result/:jobId', element: <ResultPage /> },
  { path: '/about', element: <AboutPage /> },
  { path: '/criteria', element: <CriteriaPage /> },
  ...(Gallery ? [{ path: '/gallery', element: <Gallery /> }] : []),
  { path: '*', element: <Navigate to="/" replace /> },
]

export const router = createBrowserRouter([{ element: <RootLayout />, children: routes }])
