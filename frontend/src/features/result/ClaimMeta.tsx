type ClaimMetaProps = {
  /** 연결된 제품 이름. 없으면 "제품 연결 안 됨" */
  productName?: string | null
  /** 등장 시간 '00:16–00:19'. 백엔드 t_start·t_end가 null이면 제품명만 보여요(개발 노트 §5). */
  timeRange?: string | null
}

/** 카드 맨 위 "제품명 · 등장 시간" 한 줄 — 제품명 Medium, 시간 Regular */
export function ClaimMeta({ productName, timeRange }: ClaimMetaProps) {
  return (
    <p className="text-meta text-text-tertiary">
      <span className="text-meta-m text-text-primary">{productName ?? '제품 연결 안 됨'}</span>
      {timeRange && ` · ${timeRange}`}
    </p>
  )
}
