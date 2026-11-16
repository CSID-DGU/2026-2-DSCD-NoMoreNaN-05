/**
 * 개발용 가짜 API — 백엔드 없이 S1→S2→S3 흐름과 실패 경우를 확인할 때만 써요.
 * frontend/.env.local에 VITE_API_MOCK=true를 넣고 npm run dev 하면 켜져요(배포 빌드에는 안 들어감).
 *
 * 시나리오는 S1에 넣는 주소에 들어 있는 낱말로 골라요. 예) https://youtu.be/fail1
 *   private → URL_002 비공개·삭제     error500 → JOB_001 작업 생성 실패
 *   fail1 → 01 영상 가져오기 실패     fail2 → 02 주장 추출 실패
 *   noclaims → 주장 없음             nomap → 제품 전부 매핑 실패      verifyfail → 그 밖의 검증 실패
 *   cached → 캐시 적중(바로 완료)     multi → 제품 2개(일부 매핑 실패)  clean → 확인 필요 0개
 *   그 밖 → 제품 1개 정상 결과. 단계마다 2초씩 걸려요.
 * 입력 없이 바로 보려면 /check/demo-fail1, /result/demo-multi 처럼 작업 id에 demo-<낱말>을 넣어요.
 */
import { isSupportedVideoUrl } from '@/features/input/videoUrl'
import { API_BASE } from '@/lib/api/client'
import type { FailureCode, JobStatusResponse, StepNo, StepState } from '@/lib/api/types'
import { buildResult, type ResultVariant } from '@/mocks/fixtures'

const STEP_MS = 2000
const STORE_KEY = 'trueadMockJobs'
const STEP_NAMES = ['영상 가져오기', '주장 추출', '주장 검증'] as const

type MockJob = {
  job_id: string
  url: string
  createdAt: number
  cached: boolean
  failure: { step: StepNo; code: FailureCode } | null
  variant: ResultVariant
}

const FAILURES: Record<string, { step: StepNo; code: FailureCode }> = {
  fail1: { step: 1, code: 'VIDEO_FETCH_FAILED' },
  fail2: { step: 2, code: 'CLAIM_EXTRACT_FAILED' },
  noclaims: { step: 3, code: 'NO_CLAIMS' },
  nomap: { step: 3, code: 'PRODUCT_MAPPING_ALL' },
  verifyfail: { step: 3, code: 'VERIFY_FAILED' },
}

// 새로고침해도 이어지게 sessionStorage에 둬요.
function loadJobs(): Record<string, MockJob> {
  try {
    return JSON.parse(sessionStorage.getItem(STORE_KEY) ?? '{}') as Record<string, MockJob>
  } catch {
    return {}
  }
}
function saveJob(job: MockJob) {
  try {
    sessionStorage.setItem(STORE_KEY, JSON.stringify({ ...loadJobs(), [job.job_id]: job }))
  } catch {
    /* 저장이 막혀도 이번 세션 동작에는 지장 없음 */
  }
}

const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
const ok = (status: number, data: unknown) => json(status, { success: true, code: status, message: '요청 성공', data })
const fail = (status: number, code: string, message: string) =>
  json(status, { success: false, code: status, message, error: { code }, data: null })

/** 주소에 든 낱말로 시나리오를 정해 작업을 만들어요 */
function makeJob(jobId: string, url: string): MockJob {
  const key = Object.keys(FAILURES).find((k) => url.includes(k))
  return {
    job_id: jobId,
    url,
    createdAt: Date.now(),
    cached: url.includes('cached'),
    failure: key ? FAILURES[key] : null,
    variant: url.includes('multi') ? 'multi' : url.includes('clean') ? 'clean' : 'single',
  }
}

function statusOf(job: MockJob): JobStatusResponse {
  const elapsed = job.cached ? 0 : Date.now() - job.createdAt
  // 지금까지 끝난 단계 수(실패가 있으면 실패 단계 앞에서 멈춤)
  const reached = job.cached ? 3 : Math.min(3, Math.floor(elapsed / STEP_MS))
  const failStep = job.failure?.step
  const failed = failStep !== undefined && reached >= failStep
  const done = !failed && reached >= 3
  const completed = (failed ? failStep - 1 : Math.min(reached, 3)) as 0 | 1 | 2 | 3
  const current = done ? null : ((failed ? failStep : reached + 1) as StepNo)

  const steps = STEP_NAMES.map((name, i) => {
    const no = (i + 1) as StepNo
    let state: StepState = 'PENDING'
    if (no <= completed) state = 'DONE'
    else if (no === current) state = failed ? 'FAILED' : 'RUNNING'
    return { no, name, state }
  })
  const finishedAt = failed || done ? new Date(job.createdAt + (job.cached ? 0 : (failed ? failStep : 3) * STEP_MS)) : null

  return {
    job_id: job.job_id,
    url: job.url,
    status: done ? 'DONE' : failed ? 'FAILED' : 'PROCESSING',
    current_step: current,
    completed_steps: completed,
    steps,
    failure: failed ? job.failure : null,
    video:
      completed >= 1 || done
        ? { title: '영라뉴 장용성 파비플로라 PRO 광고 영상', duration_sec: 56, ready: true }
        : { title: null, duration_sec: null, ready: false },
    elapsed_sec: finishedAt ? (finishedAt.getTime() - job.createdAt) / 1000 : elapsed / 1000,
    created_at: new Date(job.createdAt).toISOString(),
    finished_at: finishedAt?.toISOString() ?? null,
    expires_at: new Date(job.createdAt + 24 * 3600 * 1000).toISOString(),
    cached: job.cached,
  }
}

async function handle(path: string, init?: RequestInit): Promise<Response> {
  await new Promise((r) => setTimeout(r, 250)) // 네트워크 느낌
  const method = (init?.method ?? 'GET').toUpperCase()

  if (path === '/jobs' && method === 'POST') {
    let url = ''
    try {
      url = (JSON.parse(String(init?.body)) as { url?: unknown }).url as string
    } catch {
      return fail(400, 'COMMON_400', '잘못된 요청입니다.')
    }
    if (typeof url !== 'string') return fail(400, 'COMMON_400', '잘못된 요청입니다.')
    if (!isSupportedVideoUrl(url))
      return fail(400, 'URL_001', '영상 주소가 아니에요. YouTube · Instagram · TikTok 영상 주소를 넣어 주세요.')
    if (url.includes('private')) return fail(400, 'URL_002', '비공개이거나 삭제된 영상이에요. 공개된 영상 주소를 넣어 주세요.')
    if (url.includes('error500')) return fail(500, 'JOB_001', '검증을 시작하지 못했어요. 잠시 후 다시 눌러 주세요.')

    const job = makeJob(`mock_${Date.now().toString(36)}`, url)
    saveJob(job)
    const s = statusOf(job)
    return ok(201, { job_id: job.job_id, url, created_at: s.created_at, expires_at: s.expires_at, cached: job.cached })
  }

  const m = path.match(/^\/jobs\/([^/]+)(\/result)?$/)
  if (m && method === 'GET') {
    const id = decodeURIComponent(m[1])
    // /check/demo-fail1 처럼 주소로 바로 들어오면 그 시나리오 작업을 그 자리에서 만들어요(화면 확인용)
    if (!loadJobs()[id] && id.startsWith('demo-')) saveJob(makeJob(id, `https://youtu.be/${id}`))
    const job = loadJobs()[id]
    if (!job) return fail(404, 'JOB_002', '검증 기록을 찾을 수 없어요. 영상 주소를 다시 넣어 주세요.')
    const s = statusOf(job)
    if (!m[2]) return ok(200, s)
    if (s.status === 'FAILED') return fail(409, 'JOB_005', '검증을 멈춘 작업이라 결과가 없어요.')
    if (s.status !== 'DONE') return fail(409, 'JOB_004', '검증이 아직 끝나지 않았어요.')
    return ok(200, buildResult(job.job_id, job.url, job.variant))
  }

  return fail(404, 'COMMON_404', '요청한 데이터를 찾을 수 없습니다.')
}

/** window.fetch를 감싸서 /api/jobs… 요청만 가짜로 답해요. 영상(/video)은 <video>가 직접 불러서 여기로 오지 않아요. */
export function installMockApi() {
  const realFetch = window.fetch.bind(window)
  window.fetch = (input, init) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    const path = new URL(url, window.location.origin).pathname
    if (path.startsWith(`${API_BASE}/jobs`)) return handle(path.slice(API_BASE.length), init)
    return realFetch(input, init)
  }
  console.info('[mock] 가짜 API 사용 중 — src/mocks/mockApi.ts')
}
