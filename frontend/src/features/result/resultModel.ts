/**
 * S3 결과 화면 계산 — 헤드라인 문구, 탭 숫자, 제품·탭 필터, 정렬 (개발 노트 §4·§6, 카탈로그 SUMMARY).
 * 화면 코드와 분리해 둔 순수 함수예요.
 */
import type { Claim, JobResultResponse } from '@/lib/api/types'
import { LABEL_STYLES, LABELS, NEEDS_REVIEW, type Label } from '@/lib/labels'

/** 목록 아래 묶음 카드로 따로 모으는 라벨 */
export const GROUPED_LABELS: readonly Label[] = ['OUT_OF_SCOPE', 'DISCLAIMER']
export const isGrouped = (label: Label) => GROUPED_LABELS.includes(label)

export type TabKey = 'ALL' | Label

/** 영상 등장 순 — 시작 시간이 없는 주장은 뒤로, 같으면 API 순서 유지 */
export function sortByAppearance(claims: Claim[]): Claim[] {
  return claims
    .map((c, i) => ({ c, i }))
    .sort((a, b) => {
      const ta = a.c.t_start ?? Number.POSITIVE_INFINITY
      const tb = b.c.t_start ?? Number.POSITIVE_INFINITY
      return ta === tb ? a.i - b.i : ta - tb
    })
    .map(({ c }) => c)
}

/** 라벨 6칸을 항상 채워요. summary에 빠진 라벨은 0 (카탈로그 labels_zero_filled) */
export function labelCounts(result: JobResultResponse): Record<Label, number> {
  const counts = Object.fromEntries(LABELS.map((l) => [l, 0])) as Record<Label, number>
  for (const l of LABELS) counts[l] = result.summary.labels?.[l] ?? 0
  return counts
}

const n = (label: Label, count: number) => `${LABEL_STYLES[label].name} ${count}개`

/** 결과 맨 위 헤드라인·부제 — 칩·헤드라인은 제품 필터와 상관없이 영상 전체 기준(개발 노트 §6) */
export function headline(result: JobResultResponse): { title: string; sub: string } {
  const counts = labelCounts(result)
  const total = result.summary.claims
  const review = NEEDS_REVIEW.reduce((sum, l) => sum + counts[l], 0)

  const aside: string[] = []
  if (counts.OUT_OF_SCOPE) aside.push(`검증 대상이 아닌 문장 ${counts.OUT_OF_SCOPE}개`)
  if (counts.DISCLAIMER) aside.push(`면책 문구 ${counts.DISCLAIMER}개`)
  const asideText = aside.length ? `${aside.join('와 ')}는 목록 아래에 따로 모았어요.` : ''
  const supported = counts.SUPPORTED ? `일치하는 주장 ${counts.SUPPORTED}개는 등록 정보와 같${aside.length ? '고, ' : '아요.'}` : ''

  // 확인할 것도, 일치한 것도 없으면(모두 검증 대상 아님·면책 문구) '신뢰 가능'이라고 하지 않아요
  if (review === 0 && counts.SUPPORTED === 0) {
    return {
      title: '검증할 수 있는 주장이 없어요',
      sub: [`주장 ${total}개가 모두 검증 대상이 아니거나 면책 문구예요.`, asideText].filter(Boolean).join(' '),
    }
  }

  if (review === 0) {
    return {
      title: '신뢰 가능한 광고예요',
      sub: [`주장 ${total}개 중 확인이 필요한 주장이 없어요.`, `${supported}${asideText}`].filter(Boolean).join(' '),
    }
  }

  const products = result.products.length
  const skipped = result.claims.filter((c) => c.skipped_reason).length
  let sub: string
  if (products > 1) {
    sub = `제품 ${products}개가 나오는 광고예요.`
    if (skipped) sub += ` 제품을 확인하지 못한 주장 ${skipped}개는 판정을 건너뛰었어요(판단 보류에 포함).`
  } else {
    const parts = NEEDS_REVIEW.filter((l) => counts[l] > 0).map((l) => n(l, counts[l]))
    sub = [`${parts.join(', ')}예요.`, `${supported}${asideText}`].filter(Boolean).join(' ')
  }
  return { title: `주장 ${total}개 중 ${review}개는 확인이 필요해요`, sub }
}

/**
 * 제품 필터 — 끈 제품의 주장은 목록에서 빠져요. 제품이 연결되지 않은 주장(product_ref null)은 항상 보여요.
 * enabled가 null이면 필터 없음(제품 1개).
 */
export function filterByProducts(claims: Claim[], enabled: ReadonlySet<string> | null): Claim[] {
  if (!enabled) return claims
  return claims.filter((c) => c.product_ref === null || enabled.has(c.product_ref))
}

/** 탭 숫자 — 켜진 제품 기준(개발 노트 §6) */
export function tabCounts(claims: Claim[]): Record<TabKey, number> {
  const counts = { ALL: claims.length } as Record<TabKey, number>
  for (const l of LABELS) counts[l] = 0
  for (const c of claims) counts[c.final_label] += 1
  return counts
}

export function filterByTab(claims: Claim[], tab: TabKey): Claim[] {
  return tab === 'ALL' ? claims : claims.filter((c) => c.final_label === tab)
}
