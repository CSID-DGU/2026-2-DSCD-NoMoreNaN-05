import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router'
import { Footer } from '@/components/layout/Footer'
import { Nav } from '@/components/layout/Nav'
import { UrlForm } from '@/features/input/UrlForm'
import { NETWORK_ERROR_MESSAGE, isApiError } from '@/lib/api/client'
import { useCreateJob } from '@/lib/api/queries'

/** S2·S3에서 만료·없는 작업(JOB_002)으로 돌아올 때 넘기는 값 (S1-05) */
export type InputPageState = { error?: string; url?: string } | null

/** S1 입력 화면 (Figma S1-01 ~ S1-05) */
export default function InputPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const incoming = location.state as InputPageState
  const [serverError, setServerError] = useState<string | null>(incoming?.error ?? null)
  const createJob = useCreateJob()

  const submit = (url: string) => {
    setServerError(null)
    createJob.mutate(url, {
      // 캐시 적중이어도 /check로 가요. 첫 상태 조회에서 DONE을 보고 바로 [결과 보기]를 켜요(명세).
      onSuccess: (job) => navigate(`/check/${encodeURIComponent(job.job_id)}`),
      onError: (error) => setServerError(isApiError(error) ? error.message : NETWORK_ERROR_MESSAGE),
    })
  }

  return (
    <div className="flex min-h-screen flex-col bg-bg-page bg-linear-to-b from-bg-hero-top from-[4.783%] via-bg-hero-mid via-[22.359%] to-bg-page to-[55.701%]">
      <Nav active="home" />
      <main className="flex flex-1 flex-col items-center justify-center px-gutter py-24">
        <div className="flex w-217.75 max-w-full flex-col items-center">
          <h1 className="text-center text-hero text-text-primary">지금 보고 있는 광고, 사실일까요?</h1>
          <p className="pt-5 text-center text-body text-text-secondary">
            SNS 건강기능식품 광고 영상의 주소를 넣으면, 음성과 화면에서 주장을 뽑아 식약처 공개 데이터와 하나씩 대조해
            드려요.
          </p>
          <UrlForm
            defaultUrl={incoming?.url}
            serverError={serverError}
            pending={createJob.isPending}
            onSubmit={submit}
            onEdit={() => setServerError(null)}
          />
        </div>
      </main>
      <Footer />
    </div>
  )
}
