/** 초 → "00:52" (1시간 이상이면 "1:02:03"). 음수·NaN은 0으로 봐요. */
export function formatDuration(totalSec: number): string {
  const s = Number.isFinite(totalSec) && totalSec > 0 ? Math.floor(totalSec) : 0
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  const mm = String(m).padStart(2, '0')
  const ss = String(sec).padStart(2, '0')
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`
}

/** 재생 구간 "00:16–00:19". 시작이 없으면 null(카드에 제품명만 보여요, 개발 노트 §5) */
export function formatTimeRange(start: number | null, end: number | null): string | null {
  if (start === null) return null
  return end === null || end <= start ? formatDuration(start) : `${formatDuration(start)}–${formatDuration(end)}`
}
