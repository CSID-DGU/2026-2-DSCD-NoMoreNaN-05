import { Outlet, ScrollRestoration } from 'react-router'

/** 모든 화면 공통 — 다른 화면으로 가면 맨 위부터, 뒤로 가기면 보던 위치로 */
export function RootLayout() {
  return (
    <>
      <ScrollRestoration />
      <Outlet />
    </>
  )
}
