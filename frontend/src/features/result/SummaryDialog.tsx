import { Sparkles } from 'lucide-react'
import { useEffect, useRef } from 'react'
import close from '@/assets/icons/close.svg'
import { Button } from '@/components/ui/Button'
import { Chip } from '@/components/ui/Chip'
import { headline, labelCounts } from '@/features/result/resultModel'
import type { JobResultResponse } from '@/lib/api/types'
import { NEEDS_REVIEW } from '@/lib/labels'

type SummaryDialogProps = {
  open: boolean
  result: JobResultResponse
  /** 백엔드 popup_summary (LLM 요약 문장) */
  summary: string
  /** X · Esc · 바깥 클릭 · [전체 결과 보기] → 닫고 결과 화면을 봐요 */
  onClose: () => void
}

/**
 * S2 → S3로 넘어오자마자 뜨는 요약 팝업 — 결론(헤드라인·라벨 수)과 LLM 요약을 먼저 보여 주고,
 * 닫으면 전체 결과 화면이 보여요. 브라우저 기본 <dialog>라서 뒤 화면 막기·초점 가두기·Esc가 기본으로 돼요.
 */
export function SummaryDialog({ open, result, summary, onClose }: SummaryDialogProps) {
  const ref = useRef<HTMLDialogElement>(null)
  const { title } = headline(result)
  const counts = labelCounts(result)
  // 헤드라인 '확인이 필요해요' 수에 들어가는 라벨(위반·과장·판단 보류)만, 0개는 빼고
  const shownLabels = NEEDS_REVIEW.filter((l) => counts[l] > 0)

  useEffect(() => {
    const dialog = ref.current
    if (!dialog) return
    if (open && !dialog.open) {
      dialog.showModal()
      dialog.focus()
    }
    if (!open && dialog.open) dialog.close()
  }, [open])

  return (
    <dialog
      ref={ref}
      tabIndex={-1}
      aria-labelledby="summary-dialog-title"
      onCancel={(e) => {
        e.preventDefault()
        onClose()
      }}
      // 바깥(어두운 배경)을 누르면 닫혀요 — 팝업 안을 누를 때는 target이 dialog가 아니에요
      onClick={(e) => e.target === e.currentTarget && onClose()}
      className="m-auto w-140 rounded-dialog bg-bg-raised px-9 pt-8 pb-8 shadow-dialog outline-none backdrop:bg-text-primary/42 motion-safe:open:animate-dialog-in"
    >
      <div className="flex items-start justify-between gap-4">
        <p className="flex items-center gap-1.5 text-meta-m text-brand-magenta-strong">
          <Sparkles aria-hidden size={16} />
          AI 요약 리포트
        </p>
        <button type="button" aria-label="닫기" onClick={onClose} className="shrink-0 cursor-pointer">
          <img src={close} alt="" width={20} height={20} />
        </button>
      </div>

      <h2 id="summary-dialog-title" className="pt-3 text-h2 text-text-primary">
        {title}
      </h2>

      {shownLabels.length > 0 && (
        <ul className="flex flex-wrap gap-2 pt-4" aria-label="확인이 필요한 주장 수">
          {shownLabels.map((l) => (
            <li key={l}>
              <Chip label={l} count={counts[l]} />
            </li>
          ))}
        </ul>
      )}

      <p className="mt-6 rounded-card bg-bg-sunken px-5 py-4 text-body whitespace-pre-line text-text-primary">
        {summary}
      </p>

      <Button size="lg" className="mt-7 w-full" onClick={onClose}>
        전체 결과 보기
      </Button>
    </dialog>
  )
}
