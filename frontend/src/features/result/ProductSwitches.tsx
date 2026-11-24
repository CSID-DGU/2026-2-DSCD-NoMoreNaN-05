import { Switch } from '@/components/ui/Switch'
import type { Product } from '@/lib/api/types'
import { cn } from '@/lib/cn'

type ProductSwitchesProps = {
  products: Product[]
  /** 제품별 주장 수 */
  claimCounts: Record<string, number>
  enabled: ReadonlySet<string>
  onChange: (next: Set<string>) => void
}

/**
 * 제품이 2개일 때 '주장별 결과' 옆 — 제품마다 스위치로 켜고 꺼요. 끈 제품은 글자가 흐려져요.
 * 3개 이상이면 자리가 모자라서 드롭다운(ProductFilter)을 써요.
 */
export function ProductSwitches({ products, claimCounts, enabled, onChange }: ProductSwitchesProps) {
  const toggle = (ref: string, on: boolean) => {
    const next = new Set(enabled)
    if (on) next.add(ref)
    else next.delete(ref)
    onChange(next)
  }

  return (
    <div role="group" aria-label="제품별 보기" className="flex min-w-0 items-center gap-6">
      {products.map((p) => {
        const on = enabled.has(p.product_ref)
        return (
          <Switch
            key={p.product_ref}
            checked={on}
            onCheckedChange={(next) => toggle(p.product_ref, next)}
            className="min-w-0"
          >
            <span className={cn('flex min-w-0 gap-1 text-mark', on ? 'text-text-primary' : 'text-text-tertiary')}>
              <span className="max-w-56 truncate">{p.product_name ?? p.brand_name ?? '제품명 확인 안 됨'}</span>
              <span>{claimCounts[p.product_ref] ?? 0}</span>
            </span>
          </Switch>
        )
      })}
    </div>
  )
}
