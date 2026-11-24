import { useEffect, useMemo, useState } from 'react'
import { Navigate, useLocation, useNavigate, useParams } from 'react-router'
import { SheetPage } from '@/components/layout/SheetPage'
import { Button } from '@/components/ui/Button'
import { Tab } from '@/components/ui/Tab'
import { Player } from '@/components/video/Player'
import { ClaimCard } from '@/features/result/ClaimCard'
import { buildClaimView, buildGroupItem } from '@/features/result/claimView'
import { GroupCard } from '@/features/result/GroupCard'
import { ProductFilter } from '@/features/result/ProductFilter'
import { ProductRow } from '@/features/result/ProductRow'
import { ProductSwitches } from '@/features/result/ProductSwitches'
import {
  type SortKey,
  type TabKey,
  filterByProducts,
  filterByTab,
  isGrouped,
  sortClaims,
  tabCounts,
} from '@/features/result/resultModel'
import { ResultSummary } from '@/features/result/ResultSummary'
import { SortSwitch } from '@/features/result/SortSwitch'
import { SummaryDialog } from '@/features/result/SummaryDialog'
import { ApiError } from '@/lib/api/client'
import { jobVideoUrl } from '@/lib/api/jobs'
import { useJobResult } from '@/lib/api/queries'
import type { JobResultResponse } from '@/lib/api/types'
import { cn } from '@/lib/cn'
import { LABEL_STYLES, LABELS } from '@/lib/labels'
import type { InputPageState } from '@/pages/InputPage'

/** 처음에 보여 줄 카드 수. 넘으면 "주장 N개 더 보기" (Figma S3-P3) */
const PAGE_SIZE = 20
/** S2에서 넘어올 때 카드가 하나씩 들어오는 간격 */
const INTRO_STEP_MS = 140

/** S3 결과 화면 (Figma S3-01~07, 제품 여러 개 S3-P1~P7) */
export default function ResultPage() {
  const { jobId = '' } = useParams()
  const { data, error, isPending, isFetching } = useJobResult(jobId)

  // 다시 불러오는 중이면 예전 오류(예: 아까 받은 JOB_004)로 이동하지 않아요 — S2 ↔ S3를 오가는 반복을 막아요
  if (error instanceof ApiError && !isFetching) {
    // 없는·만료(JOB_002) → S1 안내 / 아직 처리 중(JOB_004)·실패(JOB_005) → 처리 화면으로
    if (error.status === 404) return <Navigate to="/" replace state={{ error: error.message } satisfies InputPageState} />
    if (error.code === 'JOB_004' || error.code === 'JOB_005')
      return <Navigate to={`/check/${encodeURIComponent(jobId)}`} replace />
  }

  return (
    <SheetPage>
      {data ? (
        <ResultBody key={jobId} jobId={jobId} result={data} />
      ) : (
        <p className="text-body text-text-secondary" role="status">
          {isPending ? '결과를 불러오고 있어요' : (error?.message ?? '결과를 불러오지 못했어요')}
        </p>
      )}
    </SheetPage>
  )
}

function ResultBody({ jobId, result }: { jobId: string; result: JobResultResponse }) {
  const navigate = useNavigate()
  const multi = result.products.length > 1
  const [enabled, setEnabled] = useState<Set<string>>(() => new Set(result.products.map((p) => p.product_ref)))
  const [tab, setTab] = useState<TabKey>('ALL')
  const [shown, setShown] = useState(PAGE_SIZE)
  const [sortKey, setSortKey] = useState<SortKey>('RISK')

  // S2에서 '결과 보기'로 넘어왔을 때만:
  //   popup — popup_summary가 있으면 요약 팝업을 먼저 띄워요(뒤의 카드는 숨겨 둬요)
  //   cards — 팝업을 닫으면(또는 요약이 없으면 바로) 카드가 왼쪽에서 하나씩 들어와요
  //   off   — 효과 끝. 새로고침해도 다시 나오지 않게 주소 기록의 state를 비워요
  const location = useLocation()
  const popupSummary = result.popup_summary?.trim() ?? ''
  const [intro, setIntro] = useState<'popup' | 'cards' | 'off'>(() => {
    if ((location.state as { intro?: boolean } | null)?.intro !== true) return 'off'
    return popupSummary ? 'popup' : 'cards'
  })
  useEffect(() => {
    if (intro !== 'off') navigate(location.pathname, { replace: true, state: null })
    // 처음 한 번만
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  useEffect(() => {
    if (intro !== 'cards') return
    const t = setTimeout(() => setIntro('off'), INTRO_STEP_MS * (PAGE_SIZE + 2) + 600)
    return () => clearTimeout(t)
  }, [intro])
  const introStyle = (i: number) => (intro === 'cards' ? { animationDelay: `${i * INTRO_STEP_MS}ms` } : undefined)
  const introClass =
    intro === 'popup' ? 'opacity-0' : intro === 'cards' ? 'motion-safe:animate-card-in' : undefined

  const sorted = useMemo(() => sortClaims(result.claims, sortKey), [result.claims, sortKey])
  const visible = useMemo(() => filterByProducts(sorted, multi ? enabled : null), [sorted, multi, enabled])
  const counts = useMemo(() => tabCounts(visible), [visible])
  const inTab = filterByTab(visible, tab)
  const listClaims = inTab.filter((c) => !isGrouped(c.final_label))
  const groupClaims = (label: 'OUT_OF_SCOPE' | 'DISCLAIMER') => inTab.filter((c) => c.final_label === label)
  const outOfScope = groupClaims('OUT_OF_SCOPE')
  const disclaimers = groupClaims('DISCLAIMER')

  const productClaimCounts = useMemo(() => {
    const m: Record<string, number> = {}
    for (const c of result.claims) if (c.product_ref) m[c.product_ref] = (m[c.product_ref] ?? 0) + 1
    return m
  }, [result.claims])
  const unlinked = result.claims.filter((c) => c.product_ref === null).length

  const selectTab = (next: TabKey) => {
    setTab(next)
    setShown(PAGE_SIZE)
  }

  return (
    <>
      <ResultSummary result={result} />

      <div className="mt-12 flex items-start gap-14 border-t border-line-hair pt-12">
        {/* 왼쪽 열: 영상 + 제품 정보, 스크롤해도 따라와요(개발 노트 §4 sticky top 96) */}
        <aside className="sticky top-sticky-offset flex w-136 shrink-0 flex-col">
          <Player size="md" src={jobVideoUrl(jobId)} />
          <section className="pt-10">
            <div className="flex items-baseline gap-2 border-t border-line-strong pt-4 pb-2">
              <h2 className="text-h3 text-text-primary">제품 정보</h2>
              {multi && <span className="text-meta text-text-tertiary">{result.products.length}개</span>}
            </div>
            <div>
              {result.products.map((p) => (
                <ProductRow
                  key={p.product_ref}
                  name={p.product_name ?? p.brand_name ?? '제품명 확인 안 됨'}
                  maker={p.manufacturer_name ?? '제조사 확인 안 됨'}
                  status={p.match_status}
                />
              ))}
            </div>
          </section>
        </aside>

        <section className="flex min-w-0 flex-1 flex-col" aria-labelledby="claims-title">
          <div className="sticky top-0 z-10 bg-bg-page">
            <div className="flex items-center justify-between pt-1">
              <h2 id="claims-title" className="text-h2 text-text-primary">
                주장별 결과
              </h2>
              {result.products.length === 2 ? (
                <ProductSwitches
                  products={result.products}
                  claimCounts={productClaimCounts}
                  enabled={enabled}
                  onChange={(next) => {
                    setEnabled(next)
                    setShown(PAGE_SIZE)
                  }}
                />
              ) : multi ? (
                <ProductFilter
                  products={result.products}
                  claimCounts={productClaimCounts}
                  unlinkedCount={unlinked}
                  enabled={enabled}
                  onChange={(next) => {
                    setEnabled(next)
                    setShown(PAGE_SIZE)
                  }}
                />
              ) : null}
            </div>
            <div role="tablist" aria-label="라벨별 보기" className="mt-3 flex gap-5 overflow-x-auto border-b border-line-hair">
              {(['ALL', ...LABELS] as TabKey[]).map((key) => (
                <Tab key={key} selected={tab === key} empty={counts[key] === 0} onClick={() => selectTab(key)}>
                  {key === 'ALL' ? '전체' : LABEL_STYLES[key].name} {counts[key]}
                </Tab>
              ))}
            </div>
            <div className="flex justify-end pt-3 pb-1">
              <SortSwitch value={sortKey} onChange={setSortKey} />
            </div>
          </div>

          <div className="flex flex-col gap-4 pt-3" role="tabpanel">
            {listClaims.slice(0, shown).map((c, i) => {
              const v = buildClaimView(c, result.products)
              return (
                <div key={v.id} className={introClass} style={introStyle(i)}>
                  <ClaimCard
                    tone={v.tone}
                    productName={v.productName}
                    timeRange={v.timeRange}
                    sentence={v.sentence}
                    marks={v.sentenceMarks}
                    explain={v.explain}
                    skipNote={v.skipNote}
                    parts={v.parts}
                  />
                </div>
              )
            })}
            {listClaims.length > shown && (
              <Button kind="secondary" className="w-full" onClick={() => setShown((s) => s + PAGE_SIZE)}>
                주장 {listClaims.length - shown}개 더 보기
              </Button>
            )}
            {listClaims.length === 0 && outOfScope.length === 0 && disclaimers.length === 0 && (
              <p className="rounded-card border border-line-hair px-7 py-10 text-center text-body text-text-secondary">
                선택한 조건에 맞는 주장이 없어요
              </p>
            )}
          </div>

          {(outOfScope.length > 0 || disclaimers.length > 0) && (
            <div
              className={cn('flex flex-col gap-4 pt-10', introClass)}
              style={introStyle(Math.min(listClaims.length, shown))}
            >
              <p className="text-small-m text-text-tertiary">목록에서 따로 모은 문장</p>
              {outOfScope.length > 0 && (
                <GroupCard
                  key={`oos-${tab}`}
                  tone="OUT_OF_SCOPE"
                  defaultOpen={tab === 'OUT_OF_SCOPE'}
                  items={outOfScope.map((c) => buildGroupItem(c, result.products))}
                />
              )}
              {disclaimers.length > 0 && (
                <GroupCard
                  key={`dis-${tab}`}
                  tone="DISCLAIMER"
                  defaultOpen={tab === 'DISCLAIMER'}
                  items={disclaimers.map((c) => buildGroupItem(c, result.products))}
                />
              )}
            </div>
          )}

          <div className="pt-10">
            <Button kind="secondary" className="w-full" onClick={() => navigate('/')}>
              다른 광고 검증하기
            </Button>
          </div>
        </section>
      </div>

      {popupSummary && (
        <SummaryDialog
          open={intro === 'popup'}
          result={result}
          summary={popupSummary}
          onClose={() => setIntro('cards')}
        />
      )}
    </>
  )
}
