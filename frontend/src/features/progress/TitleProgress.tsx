type TitleProgressProps = {
  /** 완료한 단계 수 0~3. 진행 중인 단계는 세지 않아요(개발 노트 §1) */
  completed: number
}

/** Figma TitleProgress — 제목 밑 막대. 1px 회색 선 위에 4px 마젠타가 n/3만큼 차요. 0/3이면 채움 없음 */
export function TitleProgress({ completed }: TitleProgressProps) {
  const ratio = Math.min(Math.max(completed, 0), 3) / 3
  return (
    <div
      role="progressbar"
      aria-label="검증 진행"
      aria-valuemin={0}
      aria-valuemax={3}
      aria-valuenow={completed}
      aria-valuetext={`3단계 중 ${completed}단계 완료`}
      className="relative h-1 w-full"
    >
      <div className="absolute inset-x-0 top-[1.5px] h-px bg-line-hair" />
      {ratio > 0 && (
        <div className="absolute inset-y-0 left-0 bg-brand-magenta" style={{ width: `${ratio * 100}%` }} />
      )}
    </div>
  )
}
