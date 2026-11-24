import doneIcon from '@/assets/icons/stage-done.svg'
import { Chip } from '@/components/ui/Chip'
import { headline, labelCounts } from '@/features/result/resultModel'
import type { JobResultResponse } from '@/lib/api/types'
import { LABELS } from '@/lib/labels'

/** Figma S3 결론 블록 — 검증 완료 · 헤드라인 · 부제 · 라벨 칩 6개(0건도 표시) · 안내 */
export function ResultSummary({ result }: { result: JobResultResponse }) {
  const { title, sub } = headline(result)
  const counts = labelCounts(result)
  // 칩 순서는 화면 디자인 순서(위반 → … → 면책 문구)
  return (
    <section className="flex flex-col">
      <p className="flex items-center gap-1.5 text-meta text-text-secondary">
        <img src={doneIcon} alt="" width={16} height={16} />
        <span className="text-meta-m text-label-supported">검증 완료</span>
        {result.video?.title && (
          <>
            <span aria-hidden className="text-text-disabled">
              ·
            </span>
            <span className="truncate">{result.video.title}</span>
          </>
        )}
      </p>
      <h1 className="pt-3.5 text-title text-text-primary">{title}</h1>
      <p className="pt-3 text-body text-text-secondary">{sub}</p>
      <ul className="flex flex-wrap gap-2 pt-7.5" aria-label="라벨별 주장 수">
        {LABELS.map((l) => (
          <li key={l}>
            <Chip label={l} count={counts[l]} />
          </li>
        ))}
      </ul>
    </section>
  )
}
