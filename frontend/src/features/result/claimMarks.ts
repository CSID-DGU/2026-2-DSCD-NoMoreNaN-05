/**
 * 클레임 문장에서 라벨이 붙은 부분을 찾아 형광펜 칠할 조각으로 나눠요 (팀 문서 §4 광고 문장 강조).
 * - A 부분(원료·수치·인증): claim_value, 없거나 문장에 없으면 target을 문장에서 찾아요
 * - B 부분(효능): parsed.effect를 찾고, 없으면 효능만 있는 주장일 때 문장 전체
 * - 겹치면 더 짧은(구체적인) 부분이 이겨요. 찾지 못한 부분은 칠하지 않아요.
 */
import type { Claim } from '@/lib/api/types'
import type { Label } from '@/lib/labels'

export type TextMark = { text: string; tone?: Label }
type Range = { start: number; end: number; tone: Label }

const usable = (s: unknown): s is string => typeof s === 'string' && s.trim().length >= 2

export function markClaimText(claim: Claim): TextMark[] {
  const text = claim.text ?? ''
  if (!text || claim.skipped_reason || claim.final_label === 'DISCLAIMER') return [{ text }]

  const found: Range[] = []
  const add = (needle: string, tone: Label) => {
    const start = text.indexOf(needle.trim())
    if (start >= 0) found.push({ start, end: start + needle.trim().length, tone })
  }

  const checks = Array.isArray(claim.A?.checks) ? claim.A.checks : []
  for (const c of checks) {
    const needle = [c.claim_value, c.target].find((s) => usable(s) && text.includes(s.trim()))
    if (needle) add(needle, c.status)
  }
  const b = claim.B
  if (b && b.reason_code !== 'DISCLAIMER') {
    const effect = claim.parsed?.effect
    if (usable(effect) && text.includes(effect.trim())) add(effect, b.label)
    else if (checks.length === 0) found.push({ start: 0, end: text.length, tone: b.label })
  }

  // 구체적인(짧은) 부분부터 자리를 잡고, 겹치는 건 버려요
  const taken: Range[] = []
  for (const r of [...found].sort((x, y) => x.end - x.start - (y.end - y.start))) {
    if (!taken.some((t) => r.start < t.end && t.start < r.end)) taken.push(r)
  }
  taken.sort((x, y) => x.start - y.start)

  const marks: TextMark[] = []
  let at = 0
  for (const r of taken) {
    if (r.start > at) marks.push({ text: text.slice(at, r.start) })
    marks.push({ text: text.slice(r.start, r.end), tone: r.tone })
    at = r.end
  }
  if (at < text.length) marks.push({ text: text.slice(at) })
  return marks
}
