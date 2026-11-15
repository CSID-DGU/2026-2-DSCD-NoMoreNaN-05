/**
 * 컴포넌트 미리보기 (개발용) — http://localhost:5173/#gallery
 * Figma v5 · Components 시트와 나란히 놓고 비교하는 용도예요. 배포 빌드에는 들어가지 않아요.
 * 컴포넌트를 하나 만들 때마다 여기에 섹션을 추가해요.
 */
import { type ReactNode, useState } from 'react'
import chevron from '@/assets/icons/chevron.svg'
import close from '@/assets/icons/close.svg'
import link from '@/assets/icons/link.svg'
import stageActive from '@/assets/icons/stage-active.svg'
import stageDone from '@/assets/icons/stage-done.svg'
import stageFail from '@/assets/icons/stage-fail.svg'
import stageWait from '@/assets/icons/stage-wait.svg'
import { Nav } from '@/components/layout/Nav'
import { Button } from '@/components/ui/Button'
import { Checkbox } from '@/components/ui/Checkbox'
import { Chip } from '@/components/ui/Chip'
import { Mark, type MarkTone } from '@/components/ui/Mark'
import { Switch } from '@/components/ui/Switch'
import { Tab } from '@/components/ui/Tab'
import { Tag } from '@/components/ui/Tag'
import { Toggle } from '@/components/ui/Toggle'
import { Player } from '@/components/video/Player'
import { FailDialog } from '@/features/progress/FailDialog'
import { Stage } from '@/features/progress/Stage'
import { ClaimCard } from '@/features/result/ClaimCard'
import { ClaimPartRow } from '@/features/result/ClaimPart'
import { GroupCard } from '@/features/result/GroupCard'
import { type MatchStatus, ProductRow } from '@/features/result/ProductRow'
import { SAMPLE_EXPRESSION_PART, SAMPLE_NOTICE_PART, SAMPLE_PARTS } from '@/dev/sampleClaims'
import { LABEL_STYLES, LABELS, type LabelTone } from '@/lib/labels'

const TONES: LabelTone[] = [...LABELS, 'SKIPPED']

// ?only=cards 처럼 주소에 적으면 그 섹션만 보여요 (긴 페이지를 나눠 확인할 때)
const ONLY = new URLSearchParams(window.location.search).get('only')

function Section({ id, title, children }: { id?: string; title: string; children: ReactNode }) {
  if (ONLY && ONLY !== id) return null
  return (
    <section id={id} className="border-t border-line-hair py-10">
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
  const [toggleOpen, setToggleOpen] = useState(false)
  const [tab, setTab] = useState(0)
  const [switchOn, setSwitchOn] = useState(true)
  const [checks, setChecks] = useState([true, false])
  const [dialogOpen, setDialogOpen] = useState(window.location.search.includes('dialog'))

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

      <Section title="Button">
        <div className="flex items-center gap-4">
          <Button>검증하기</Button>
          <Button kind="secondary">검증하기</Button>
          <Button disabled>검증하기</Button>
        </div>
      </Section>

      <Section title="Tag (md / sm)">
        <div className="space-y-3">
          <div className="flex gap-2">
            {TONES.map((t) => (
              <Tag key={t} tone={t} />
            ))}
          </div>
          <div className="flex gap-2">
            {TONES.map((t) => (
              <Tag key={t} tone={t} size="sm" />
            ))}
          </div>
        </div>
      </Section>

      <Section title="Chip">
        <div className="flex gap-2">
          {LABELS.map((l, i) => (
            <Chip key={l} label={l} count={[1, 3, 5, 2, 7, 1][i]} />
          ))}
        </div>
      </Section>

      <Section title="Mark">
        <div className="flex flex-wrap gap-5">
          {(
            [
              'VIOLATION',
              'OVERCLAIM',
              'UNCLEAR',
              'SUPPORTED',
              'SUPPORTED_INDIRECT',
              'OUT_OF_SCOPE',
              'DISCLAIMER',
              'SKIPPED',
              'PENDING',
            ] as MarkTone[]
          ).map((t) => (
            <Mark key={t} tone={t} />
          ))}
        </div>
      </Section>

      <Section title="Toggle (닫힘 / 열림 / 눌러 보기)">
        <div className="flex gap-10">
          <Toggle open={false}>상세 결과 보기</Toggle>
          <Toggle open>접기</Toggle>
          <Toggle open={toggleOpen} onClick={() => setToggleOpen((v) => !v)}>
            {toggleOpen ? '접기' : '상세 결과 보기'}
          </Toggle>
        </div>
      </Section>

      <Section title="Tab (선택 / 기본 / 0건)">
        <div role="tablist" className="flex gap-6 border-b border-line-hair">
          {['전체 19', '위반 1', '과장 0', '판단 보류 5'].map((t, i) => (
            <Tab key={t} selected={tab === i} empty={t.endsWith(' 0')} onClick={() => setTab(i)}>
              {t}
            </Tab>
          ))}
        </div>
      </Section>

      <Section title="Switch (눌러 보기)">
        <Switch checked={switchOn} onCheckedChange={setSwitchOn}>
          <span className="text-small text-text-primary">레몬즙 {switchOn ? '켬' : '끔'}</span>
        </Switch>
      </Section>

      <Section title="Checkbox (눌러 보기)">
        <div className="flex flex-col gap-3">
          {['영라뉴 장용성 파비플로라 PRO', '레몬즙'].map((name, i) => (
            <Checkbox
              key={name}
              checked={checks[i]}
              onCheckedChange={(v) => setChecks((c) => c.map((x, j) => (j === i ? v : x)))}
            >
              <span className="text-small text-text-primary">{name}</span>
            </Checkbox>
          ))}
        </div>
      </Section>

      <Section title="Nav (홈 활성 / 없음) — 실제로는 화면 전체 폭">
        <div className="-mx-6 space-y-6 bg-bg-sunken py-6">
          <Nav active="home" />
          <Nav />
        </div>
      </Section>

      <Section title="Stage (완료 / 진행 중 / 대기 / 실패)">
        <div className="grid grid-cols-2 gap-x-12">
          <div className="w-132 [&>*:last-child]:border-b">
            <Stage no="01" title="영상 가져오기" description="영상 다운로드 완료" state="done" />
            <Stage no="02" title="주장 추출" description="음성과 화면 글자에서 주장을 찾는 중" state="active" progress={0.63} />
            <Stage no="03" title="주장 검증" description="주장 추출이 끝나면 시작해요" state="wait" />
          </div>
          <div className="w-132 [&>*:last-child]:border-b">
            <Stage no="01" title="영상 가져오기" description="영상을 내려받지 못했어요" state="fail" />
          </div>
        </div>
      </Section>

      <Section title="ProductRow (확인 / 후보 여러 개 / 못 찾음)">
        <div className="grid grid-cols-3 gap-10">
          {(['confirmed', 'unresolved', 'not_found'] as MatchStatus[]).map((s) => (
            <ProductRow key={s} name="영라뉴 장용성 파비플로라 PRO" maker="(주)알피바이오" status={s} />
          ))}
        </div>
      </Section>

      <Section id="player" title="Player (md 544 / lg 608, 영상 없음)">
        <div className="flex flex-wrap items-start gap-6">
          <Player />
          <Player size="lg" message="영상을 불러오지 못했어요" />
        </div>
      </Section>

      <Section title="ClaimPart (비교 / 사유 / 비교·표현 / 안내) — 행 2개 이상이면 작은 태그">
        <div className="w-137">
          {[...SAMPLE_PARTS, SAMPLE_EXPRESSION_PART, SAMPLE_NOTICE_PART].map((p, i) => (
            <ClaimPartRow key={i} part={p} showTag />
          ))}
        </div>
      </Section>

      <Section id="cards" title="ClaimCard (라벨 7종, 첫 카드는 펼친 상태 — 눌러 보기)">
        <div className="flex flex-col items-start gap-4">
          {TONES.map((t, i) => (
            <ClaimCard
              key={t}
              tone={t}
              productName="영라뉴 장용성 파비플로라 PRO"
              timeRange={i === 4 ? null : '00:16–00:19'}
              sentence="하루 하나, 식단 식품 상관없이 관리 가능하세요"
              explain="등록된 섭취 방법은 1일 2회, 1회 1정인데 광고는 하루 하나라고 말해요."
              skipNote="판정 건너뜀 · 제품 후보 여러 개"
              parts={t === 'SKIPPED' ? [SAMPLE_NOTICE_PART] : SAMPLE_PARTS}
              defaultOpen={i === 0}
              className="w-150"
            />
          ))}
          <ClaimCard
            tone="UNCLEAR"
            productName={null}
            sentence="제품 연결이 안 된 주장 예시"
            explain="product_ref가 없으면 제품명 자리에 ‘제품 연결 안 됨’이 보여요."
            className="w-150"
          />
        </div>
      </Section>

      <Section id="groups" title="GroupCard (닫힘 / 펼침 — 눌러 보기)">
        <div className="flex flex-col items-start gap-4">
          <GroupCard
            tone="OUT_OF_SCOPE"
            className="w-150"
            items={[
              { productName: '영라뉴 장용성 파비플로라 PRO', timeRange: '00:05–00:08', sentence: '누적 판매 100만 개 돌파' },
              { productName: '영라뉴 장용성 파비플로라 PRO', timeRange: '00:40–00:44', sentence: '지금 50% 할인' },
            ]}
          />
          <GroupCard
            tone="DISCLAIMER"
            defaultOpen
            className="w-150"
            items={[
              {
                productName: '영라뉴 장용성 파비플로라 PRO',
                timeRange: '00:32–00:38',
                sentence: '*인체적용시험 결과가 모든 사람에게 동일하게 적용되는 것은 아님',
                note: '광고 속 고지 문구예요',
              },
            ]}
          />
        </div>
      </Section>

      <Section title="FailDialog (눌러서 열기 · X·Esc로 닫기)">
        <Button kind="secondary" onClick={() => setDialogOpen(true)}>
          실패 팝업 열기
        </Button>
        <FailDialog
          open={dialogOpen}
          title="식약처에 등록되지 않은 제품의 영상이에요"
          onClose={() => setDialogOpen(false)}
          onGoHome={() => setDialogOpen(false)}
        >
          <p>TRUEAD로는 검증할 수 없는 영상입니다.</p>
          <p>다른 제품으로 시도해주세요</p>
        </FailDialog>
      </Section>
    </main>
  )
}
