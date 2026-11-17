import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Navigate, useNavigate, useParams } from 'react-router'
import { Footer } from '@/components/layout/Footer'
import { Nav } from '@/components/layout/Nav'
import { Button } from '@/components/ui/Button'
import { Player } from '@/components/video/Player'
import { FailDialog } from '@/features/progress/FailDialog'
import { Stage, type StageState } from '@/features/progress/Stage'
import { FAIL_DIALOGS, STEP_MARKS, STEP_NAMES, stageDescription } from '@/features/progress/stageCopy'
import { TitleProgress } from '@/features/progress/TitleProgress'
import { useElapsed } from '@/features/progress/useElapsed'
import { ApiError } from '@/lib/api/client'
import { jobVideoUrl } from '@/lib/api/jobs'
import { jobKeys, useJobStatus } from '@/lib/api/queries'
import type { JobStatusResponse, StepState } from '@/lib/api/types'
import { formatDuration } from '@/lib/format'
import type { InputPageState } from '@/pages/InputPage'

const STAGE_STATE: Record<StepState, StageState> = { PENDING: 'wait', RUNNING: 'active', DONE: 'done', FAILED: 'fail' }

/** S2 처리 중 화면 (Figma S2-01~04, 실패 S2-F1~F5). 2초마다 상태를 물어봐요. */
export default function CheckPage() {
  const { jobId = '' } = useParams()
  const { data, error, dataUpdatedAt } = useJobStatus(jobId)

  // 없는·만료된 작업 → S1으로 돌아가 안내(S1-05)
  if (error instanceof ApiError && error.status === 404) {
    const state: InputPageState = { error: error.message }
    return <Navigate to="/" replace state={state} />
  }

  return (
    <div className="flex min-h-screen flex-col bg-bg-page">
      <Nav active="verify" />
      <main className="mx-auto w-full max-w-content flex-1 pt-16 pb-24">
        {data ? (
          // key: 다른 작업으로 바뀌면 팝업 닫음 상태 등을 처음으로
          <CheckBody key={jobId} jobId={jobId} job={data} receivedAt={dataUpdatedAt} />
        ) : (
          <CheckLoading errorMessage={error instanceof ApiError ? error.message : null} />
        )}
      </main>
      <Footer />
    </div>
  )
}

function CheckLoading({ errorMessage }: { errorMessage: string | null }) {
  return (
    <div className="flex flex-col gap-2.5">
      <h1 className="text-title text-text-primary">광고를 검증하고 있어요</h1>
      <p className="text-body text-text-secondary" role="status">
        {errorMessage ? `${errorMessage} 잠시 후 다시 확인해요.` : '진행 상태를 불러오고 있어요'}
      </p>
    </div>
  )
}

function CheckBody({ jobId, job, receivedAt }: { jobId: string; job: JobStatusResponse; receivedAt: number }) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [dialogDismissed, setDialogDismissed] = useState(false)
  const failed = job.status === 'FAILED'
  const done = job.status === 'DONE'
  const running = !failed && !done
  const elapsed = useElapsed(job.elapsed_sec, receivedAt, running)
  const failureCode = job.failure?.code ?? null

  // 대기(QUEUED) 중에는 01 진행 중과 같게 보여요(명세)
  const steps = job.steps.map((s) =>
    job.status === 'QUEUED' && s.no === 1 ? { ...s, state: 'RUNNING' as const } : s,
  )
  const step = job.current_step ?? 3

  const title = done ? '검증을 마쳤어요' : failed ? '검증을 멈췄어요' : '광고를 검증하고 있어요'
  const sub = done
    ? `3단계 모두 끝났어요 · 걸린 시간 ${formatDuration(elapsed)}`
    : failed
      ? `${STEP_MARKS[step]} ${STEP_NAMES[step]} 단계에서 멈췄어요 · 경과 ${formatDuration(elapsed)}`
      : `3단계 중 ${STEP_MARKS[step]} ${STEP_NAMES[step]} · 경과 ${formatDuration(elapsed)} · 보통 1분 안팎 걸려요`

  const videoFailed = failed && job.failure?.step === 1
  const videoTitle = job.video?.title ?? (videoFailed ? '영상 정보를 가져오지 못했어요' : '영상 정보를 가져오는 중이에요')
  const videoLength =
    job.video?.duration_sec != null
      ? `길이 ${formatDuration(job.video.duration_sec)}`
      : videoFailed
        ? '길이 확인 안 됨'
        : '길이 확인 중'

  const dialog = failureCode ? FAIL_DIALOGS[failureCode] : null
  const goHome = () => navigate('/')

  return (
    <>
      <div className="flex flex-col gap-2.5">
        <h1 className="text-title text-text-primary">{title}</h1>
        <p className="text-body text-text-secondary" aria-live="polite">
          {sub}
        </p>
      </div>
      <div className="pt-3.75">
        <TitleProgress completed={job.completed_steps} />
      </div>

      <div className="flex items-start gap-16 pt-7.25">
        <div className="flex shrink-0 flex-col">
          <Player
            size="lg"
            src={job.video?.ready ? jobVideoUrl(jobId) : undefined}
            message={videoFailed ? '영상을 불러오지 못했어요' : '영상을 가져오고 있어요'}
          />
          <div className="flex flex-col gap-1 pt-4">
            <p className="text-body-m text-text-primary">{videoTitle}</p>
            <p className="text-meta text-text-tertiary">{videoLength}</p>
          </div>
        </div>

        <div className="flex min-w-0 flex-1 flex-col">
          <div className="[&>*:last-child]:border-b">
            {steps.map((s) => (
              <Stage
                key={s.no}
                no={`0${s.no}`}
                title={STEP_NAMES[s.no]}
                description={stageDescription(s.no, s.state, failureCode)}
                state={STAGE_STATE[s.state]}
              />
            ))}
          </div>
          <div className="flex h-16.75 items-end justify-end">
            {failed && dialogDismissed ? (
              <Button className="h-13 w-132" onClick={goHome}>
                처음으로 돌아가기
              </Button>
            ) : (
              <Button
                className="h-13 w-132"
                disabled={!done}
                onClick={() => {
                  // 완료 전에 받아 둔 결과 오류(JOB_004)가 남아 있으면 지우고 새로 받아요
                  queryClient.removeQueries({ queryKey: jobKeys.result(jobId) })
                  navigate(`/result/${encodeURIComponent(jobId)}`)
                }}
              >
                결과 보기
              </Button>
            )}
          </div>
        </div>
      </div>

      {dialog && (
        <FailDialog
          open={!dialogDismissed}
          title={dialog.title}
          onClose={() => setDialogDismissed(true)}
          onGoHome={goHome}
        >
          <p>{dialog.body[0]}</p>
          <p>{dialog.body[1]}</p>
        </FailDialog>
      )}
    </>
  )
}
