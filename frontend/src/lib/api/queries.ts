import { useMutation, useQuery } from '@tanstack/react-query'
import { ApiError } from '@/lib/api/client'
import { createJob, getJob, getJobResult } from '@/lib/api/jobs'
import type { JobStatus, JobStatusResponse } from '@/lib/api/types'

/** 명세 권장 폴링 간격 */
export const POLL_INTERVAL_MS = 2000

export const jobKeys = {
  status: (jobId: string) => ['job', jobId, 'status'] as const,
  result: (jobId: string) => ['job', jobId, 'result'] as const,
}

const isNotFound = (error: unknown) => error instanceof ApiError && error.status === 404
const isFinished = (status: JobStatus) => status === 'DONE' || status === 'FAILED'

const STATUS_ORDER: Record<JobStatus, number> = { QUEUED: 0, PROCESSING: 1, DONE: 2, FAILED: 2 }

/**
 * 늦게 도착한 이전 응답으로 화면이 되돌아가지 않게(명세 P01):
 * 완료 단계 수가 줄었거나 상태가 뒤로 간 응답은 버리고 이전 값을 유지해요.
 */
export function keepLatestStatus(prev: JobStatusResponse | undefined, next: JobStatusResponse) {
  if (!prev || prev.job_id !== next.job_id) return next
  if (next.completed_steps < prev.completed_steps) return prev
  if (STATUS_ORDER[next.status] < STATUS_ORDER[prev.status]) return prev
  if (isFinished(prev.status) && next.status !== prev.status) return prev
  return next
}

/** S1 [검증하기] */
export function useCreateJob() {
  return useMutation({ mutationFn: createJob })
}

/**
 * S2 상태 폴링 — 2초마다. DONE·FAILED·404에서 멈춰요.
 * 네트워크 오류·5xx는 다음 주기에 다시 물어봐요(명세).
 */
export function useJobStatus(jobId: string) {
  return useQuery({
    queryKey: jobKeys.status(jobId),
    queryFn: () => getJob(jobId),
    staleTime: 0,
    refetchInterval: (query) => {
      if (isNotFound(query.state.error)) return false
      const data = query.state.data
      if (data && isFinished(data.status)) return false
      return POLL_INTERVAL_MS
    },
    refetchIntervalInBackground: true,
    retry: (failureCount, error) => !isNotFound(error) && failureCount < 2,
    structuralSharing: (prev, next) =>
      keepLatestStatus(prev as JobStatusResponse | undefined, next as JobStatusResponse),
  })
}

/** S3 결과 — 완료된 작업에서만 불러요. 새로고침해도 같은 결과라 다시 받지 않아요. */
export function useJobResult(jobId: string) {
  return useQuery({
    queryKey: jobKeys.result(jobId),
    queryFn: () => getJobResult(jobId),
    retry: (failureCount, error) => !(error instanceof ApiError && error.status >= 400 && error.status < 500) && failureCount < 2,
  })
}
