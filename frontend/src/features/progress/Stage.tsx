import iconActive from '@/assets/icons/stage-active.svg'
import iconDone from '@/assets/icons/stage-done.svg'
import iconFail from '@/assets/icons/stage-fail.svg'
import iconWait from '@/assets/icons/stage-wait.svg'
import { cn } from '@/lib/cn'

export type StageState = 'done' | 'active' | 'wait' | 'fail'

const STATES: Record<StageState, { icon: string; label: string; badge: string; num: string }> = {
  done: { icon: iconDone, label: '완료', badge: 'text-label-supported', num: 'text-text-primary' },
  active: { icon: iconActive, label: '진행 중', badge: 'text-brand-magenta', num: 'text-brand-magenta' },
  wait: { icon: iconWait, label: '대기', badge: 'text-text-tertiary', num: 'text-text-tertiary' },
  fail: { icon: iconFail, label: '실패', badge: 'text-label-violation', num: 'text-label-violation' },
}

type StageProps = {
  /** 단계 번호 '01' '02' '03' */
  no: string
  title: string
  description: string
  state: StageState
  /** 진행 중일 때 막대 채움 비율 0~1. 없으면 막대를 안 보여요. */
  progress?: number
  className?: string
}

/**
 * Figma v5/Stage — S2 처리 중 화면 오른쪽의 단계 한 줄 (01 영상 가져오기 …).
 * 위쪽 선만 그려요. 마지막 단계 아래 선은 감싸는 쪽에서 last:border-b로 넣어요.
 */
export function Stage({ no, title, description, state, progress, className }: StageProps) {
  const s = STATES[state]
  const isWait = state === 'wait'
  return (
    <div className={cn('flex items-start gap-6 border-t border-line-hair pt-6 pb-6.5', className)}>
      <p className={cn('w-13 shrink-0 text-num', s.num)}>{no}</p>
      <div className="flex min-w-0 flex-1 flex-col gap-1.5">
        <div className="flex items-center justify-between pt-1.5">
          <p className={cn('text-h3', isWait ? 'text-text-tertiary' : 'text-text-primary')}>{title}</p>
          <p className={cn('flex items-center gap-1.5 text-small-m', s.badge)}>
            <img src={s.icon} alt="" width={16} height={16} />
            {s.label}
          </p>
        </div>
        <p className={cn('text-small', isWait ? 'text-text-tertiary' : 'text-text-secondary')}>{description}</p>
        {state === 'active' && progress !== undefined && (
          <div className="pt-2.5">
            <div
              role="progressbar"
              aria-label={`${title} 진행률`}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={Math.round(progress * 100)}
              className="h-1 overflow-hidden rounded-progress bg-bg-sunken"
            >
              <div className="h-full bg-brand-magenta" style={{ width: `${progress * 100}%` }} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
