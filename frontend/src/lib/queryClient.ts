import { QueryClient } from '@tanstack/react-query'

/**
 * 서버 데이터 캐시. 결과는 새로고침해도 같아서(명세 R01) 다시 받을 필요가 거의 없어요.
 * 재시도·폴링 규칙은 각 요청 훅에서 따로 정해요.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
})
