/**
 * 컴포넌트 미리보기 (개발용) — http://localhost:5173/#gallery
 * Figma v5 · Components 시트와 나란히 놓고 비교하는 용도예요. 배포 빌드에는 들어가지 않아요.
 * 컴포넌트를 하나 만들 때마다 여기에 섹션을 추가해요.
 */
import type { ReactNode } from 'react'
import chevron from '@/assets/icons/chevron.svg'
import close from '@/assets/icons/close.svg'
import link from '@/assets/icons/link.svg'
import stageActive from '@/assets/icons/stage-active.svg'
import stageDone from '@/assets/icons/stage-done.svg'
import stageFail from '@/assets/icons/stage-fail.svg'
import stageWait from '@/assets/icons/stage-wait.svg'
import { LABEL_STYLES, LABELS } from '@/lib/labels'

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="border-t border-line-hair py-10">
      <h2 className="mb-6 text-h2 text-text-primary">{title}</h2>
      {children}
    </section>
  )
}

const BASE_COLORS = [
  ['text-primary', 'bg-text-primary'],
  ['text-secondary', 'bg-text-secondary'],
  ['text-tertiary', 'bg-text-tertiary'],
  ['text-disabled', 'bg-text-disabled'],
  ['bg-sunken', 'bg-bg-sunken'],
  ['bg-disabled', 'bg-bg-disabled'],
  ['bg-player', 'bg-bg-player'],
  ['line-hair', 'bg-line-hair'],
  ['line-mid', 'bg-line-mid'],
  ['brand-magenta', 'bg-brand-magenta'],
  ['brand-magenta-strong', 'bg-brand-magenta-strong'],
] as const

const TYPE_STYLES = [
  ['hero', 'text-hero'],
  ['title', 'text-title'],
  ['num', 'text-num'],
  ['h2', 'text-h2'],
  ['wordmark', 'text-wordmark'],
  ['h3', 'text-h3'],
  ['claim', 'text-claim'],
  ['body', 'text-body'],
  ['body-m', 'text-body-m'],
  ['small', 'text-small'],
  ['small-m', 'text-small-m'],
  ['nav', 'text-nav'],
  ['mark', 'text-mark'],
  ['meta', 'text-meta'],
  ['meta-m', 'text-meta-m'],
  ['tag-sm', 'text-tag-sm'],
  ['chip-label', 'text-chip-label'],
] as const

const ICONS = { chevron, close, link, stageDone, stageActive, stageWait, stageFail }

export default function Gallery() {
  return (
    <main className="mx-auto max-w-content px-6 py-12 text-text-primary">
      <h1 className="text-title">컴포넌트 미리보기</h1>
      <p className="mt-2 text-body text-text-secondary">
        Figma v5 · Components와 비교용. 디자인 토큰 → 기본 부품 → 화면 부품 순서예요.
      </p>

      <Section title="색 · 기본">
        <div className="grid grid-cols-6 gap-4">
          {BASE_COLORS.map(([name, cls]) => (
            <div key={name}>
              <div className={`h-12 rounded-control border border-line-hair ${cls}`} />
              <p className="mt-1 text-meta text-text-secondary">{name}</p>
            </div>
          ))}
        </div>
      </Section>

      <Section title="색 · 라벨 (글자 / vivid / tint / line)">
        <div className="grid grid-cols-6 gap-4">
          {LABELS.map((label) => {
            const s = LABEL_STYLES[label]
            return (
              <div key={label} className="space-y-1">
                <p className={`text-body-m ${s.text}`}>{s.name}</p>
                <div className={`h-3 rounded-progress ${s.vivid}`} />
                <div className={`h-8 rounded-control border ${s.tint} ${s.line}`} />
                <p className="text-meta text-text-tertiary">{label}</p>
              </div>
            )
          })}
        </div>
      </Section>

      <Section title="글자 스타일">
        <div className="space-y-3">
          {TYPE_STYLES.map(([name, cls]) => (
            <div key={name} className="flex items-baseline gap-6">
              <span className="w-24 shrink-0 text-meta text-text-tertiary">{name}</span>
              <span className={cls}>지금 보고 있는 광고, 사실일까요? TRUEAD 0123</span>
            </div>
          ))}
        </div>
      </Section>

      <Section title="아이콘">
        <div className="flex flex-wrap gap-8">
          {Object.entries(ICONS).map(([name, src]) => (
            <div key={name} className="flex flex-col items-center gap-2">
              <img src={src} alt="" />
              <span className="text-meta text-text-tertiary">{name}</span>
            </div>
          ))}
        </div>
      </Section>
    </main>
  )
}
