import { API_BASE, apiFetch } from '@/lib/api/client'
import type { CreateJobResponse, JobResultResponse, JobStatusResponse } from '@/lib/api/types'

const jobPath = (jobId: string) => `/jobs/${encodeURIComponent(jobId)}`

/** I01 작업 생성 — 실패: COMMON_400 · URL_001 · URL_002 · JOB_001 */
export function createJob(url: string) {
  return apiFetch<CreateJobResponse>('/jobs', { method: 'POST', body: JSON.stringify({ url }) })
}

/** P01 처리 상태 — 실패: JOB_002(없음·만료) */
export function getJob(jobId: string) {
  return apiFetch<JobStatusResponse>(jobPath(jobId))
}

/** R01 결과 — 실패: JOB_004(아직 처리 중) · JOB_005(실패한 작업) · JOB_002 */
export function getJobResult(jobId: string) {
  return apiFetch<JobResultResponse>(`${jobPath(jobId)}/result`)
}

/** P02 영상 — <video src>에 그대로 넣어요(Range 지원). 01 완료 전에는 404 */
export function jobVideoUrl(jobId: string) {
  return `${API_BASE}${jobPath(jobId)}/video`
}
