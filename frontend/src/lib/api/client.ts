import type { ApiEnvelope } from '@/lib/api/types'

/** 프론트는 /api로 부르고, 개발 서버 프록시가 /api를 떼서 백엔드로 넘겨요(vite.config.ts). */
export const API_BASE = '/api'

/**
 * API 실패. message는 화면에 그대로 보여도 되는 문장(명세), code는 분기용(URL_001, JOB_002 …).
 * status 0은 서버에 아예 닿지 못한 경우예요.
 */
export class ApiError extends Error {
  readonly status: number
  readonly code: string | null

  constructor(status: number, code: string | null, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

export const NETWORK_ERROR_MESSAGE = '서버에 연결하지 못했어요. 잠시 후 다시 시도해 주세요.'
const BAD_RESPONSE_MESSAGE = '서버 응답을 읽지 못했어요. 잠시 후 다시 시도해 주세요.'

function isEnvelope(body: unknown): body is ApiEnvelope<unknown> {
  return typeof body === 'object' && body !== null && 'success' in body && 'message' in body
}

/** 요청을 보내고 봉투를 풀어 data만 돌려줘요. 실패면 ApiError를 던져요. */
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { Accept: 'application/json', ...(init?.body ? { 'Content-Type': 'application/json' } : {}), ...init?.headers },
    })
  } catch {
    throw new ApiError(0, null, NETWORK_ERROR_MESSAGE)
  }

  let body: unknown = null
  try {
    body = await res.json()
  } catch {
    // 프록시 502처럼 JSON이 아닌 응답
  }

  if (isEnvelope(body)) {
    if (body.success) return body.data as T
    throw new ApiError(res.status, body.error?.code ?? null, body.message)
  }
  throw new ApiError(res.status, null, res.ok ? BAD_RESPONSE_MESSAGE : NETWORK_ERROR_MESSAGE)
}

export function isApiError(error: unknown, ...codes: string[]): error is ApiError {
  return error instanceof ApiError && (codes.length === 0 || (error.code !== null && codes.includes(error.code)))
}
