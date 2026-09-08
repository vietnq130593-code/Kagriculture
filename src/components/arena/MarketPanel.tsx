'use client'

/**
 * ARENA OBSERVER UI — market panel: 9 products with price vs base, sparkline
 * (price history up to the current view turn), inventory + delta, town shops.
 */
import { memo, useMemo } from 'react'
import { Line, LineChart, ResponsiveContainer, YAxis } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Store } from 'lucide-react'
import type { TurnRecord } from './types'
import { PRODUCTS } from './constants'
import { fmtSigned, shopLabel } from './helpers'
import { cn } from '@/lib/utils'
import type { TurnStore } from './useArena'

interface Props {
  viewTurn: TurnRecord | null
  viewIndex: number
  store: TurnStore
}

const SPARK_WINDOW = 240 // turns
const SPARK_SAMPLE = 4 // → ≤60 points per sparkline

const Sparkline = memo(function Sparkline({
  data,
  color,
}: {
  data: { v: number }[]
  color: string
}) {
  if (data.length < 2) {
    return <div className="h-7 w-20 rounded bg-stone-50" aria-hidden="true" />
  }
  return (
    <div className="h-7 w-20">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 2, right: 0, left: 0, bottom: 2 }}>
          <YAxis hide domain={['dataMin', 'dataMax']} />
          <Line
            type="monotone"
            dataKey="v"
            stroke={color}
            strokeWidth={1.4}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
})

const MarketRow = memo(function MarketRow({
  name,
  icon,
  base,
  color,
  price,
  inventory,
  delta,
  series,
}: {
  name: string
  icon: string
  base: number
  color: string
  price: number
  inventory: number
  delta: number
  series: { v: number }[]
}) {
  const diff = price - base
  const pct = base > 0 ? Math.round((diff / base) * 100) : 0
  return (
    <div className="flex items-center gap-2 border-b border-stone-100 py-2 last:border-b-0 sm:gap-3">
      <span className="w-24 shrink-0 truncate text-xs font-semibold text-stone-700 sm:w-28">
        <span className="mr-1">{icon}</span>
        {name}
      </span>

      <Badge
        variant="outline"
        className={cn(
          'w-20 shrink-0 justify-center gap-0.5 tabular-nums',
          diff > 0
            ? 'border-emerald-300 bg-emerald-50 text-emerald-800'
            : diff < 0
              ? 'border-rose-300 bg-rose-50 text-rose-800'
              : 'border-stone-300 bg-stone-50 text-stone-600',
        )}
        title={`giá cơ sở $${base}`}
      >
        ${price}
        <span className="text-[9px]">{diff > 0 ? '▲' : diff < 0 ? '▼' : '='}</span>
        <span className="text-[9px] opacity-70">{pct > 0 ? '+' : ''}{pct}%</span>
      </Badge>

      <div className="hidden sm:block">
        <Sparkline data={series} color={color} />
      </div>

      <span className="ml-auto flex items-center gap-1.5 text-xs tabular-nums">
        <span className="text-stone-500">kho</span>
        <span className="font-semibold text-stone-800">{inventory.toLocaleString('vi-VN')}</span>
        {viewDelta(delta)}
      </span>
    </div>
  )
})

function viewDelta(delta: number) {
  if (delta === 0) return null
  return (
    <span
      className={cn(
        'rounded px-1 text-[10px] font-bold',
        delta > 0 ? 'bg-rose-50 text-rose-700' : 'bg-emerald-50 text-emerald-700',
      )}
      title={delta > 0 ? 'thị trường đang bị hút hàng' : 'thị trường đang nhận thêm hàng'}
    >
      {fmtSigned(delta)}
    </span>
  )
}

export const MarketPanel = memo(function MarketPanel({ viewTurn, viewIndex, store }: Props) {
  const market = viewTurn?.market
  const prices = market?.prices ?? {}
  const inventory = market?.inventory ?? {}
  const shops = viewTurn?.town?.unlocked_shops ?? []

  const { seriesByProduct, deltaByProduct } = useMemo(() => {
    const turns = store.turns
    const start = Math.max(0, viewIndex - SPARK_WINDOW + 1)
    const seriesByProduct: Record<string, { v: number }[]> = {}
    for (const p of PRODUCTS) seriesByProduct[p.name] = []
    for (let i = start; i <= viewIndex; i += SPARK_SAMPLE) {
      const t = turns[i]
      if (!t?.market?.prices) continue
      const last = Math.min(viewIndex, i + SPARK_SAMPLE - 1)
      const src = turns[last]?.market?.prices ?? t.market.prices
      for (const p of PRODUCTS) {
        seriesByProduct[p.name].push({ v: src[p.name] ?? p.base })
      }
    }
    // ensure the newest point is the current view turn
    const cur = turns[viewIndex]?.market?.prices
    if (cur) {
      for (const p of PRODUCTS) {
        const arr = seriesByProduct[p.name]
        if (arr.length === 0 || arr[arr.length - 1].v !== (cur[p.name] ?? p.base)) {
          arr.push({ v: cur[p.name] ?? p.base })
        }
      }
    }

    const deltaByProduct: Record<string, number> = {}
    if (viewIndex > 0) {
      const prevInv = turns[viewIndex - 1]?.market?.inventory
      const curInv = turns[viewIndex]?.market?.inventory
      if (prevInv && curInv) {
        for (const p of PRODUCTS) {
          deltaByProduct[p.name] = (curInv[p.name] ?? 0) - (prevInv[p.name] ?? 0)
        }
      }
    }
    return { seriesByProduct, deltaByProduct }
  }, [viewIndex, store])

  const shopCounts = useMemo(() => {
    const counts = new Map<string, number>()
    for (const s of shops) counts.set(s, (counts.get(s) ?? 0) + 1)
    return Array.from(counts.entries())
  }, [shops])

  return (
    <Card className="border-stone-200 shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="flex flex-wrap items-center gap-2 text-base font-semibold">
          <Store className="size-4 text-amber-700" aria-hidden="true" />
          Thị trường
          <span className="text-xs font-normal text-stone-400">
            giá so với giá cơ sở · kho chợ
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="px-3 pb-3 pt-0 sm:px-4 sm:pb-4">
        <div role="table" aria-label="Bảng giá thị trường">
          {PRODUCTS.map((p) => (
            <MarketRow
              key={p.name}
              name={p.name}
              icon={p.icon}
              base={p.base}
              color={p.color}
              price={prices[p.name] ?? p.base}
              inventory={inventory[p.name] ?? 0}
              delta={deltaByProduct[p.name] ?? 0}
              series={seriesByProduct[p.name]}
            />
          ))}
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-stone-200 pt-3">
          <span className="flex items-center gap-1.5 text-xs font-semibold text-stone-600">
            <Store className="size-3.5 text-stone-500" aria-hidden="true" />
            Cửa hàng thị trấn:
          </span>
          {shopCounts.length === 0 ? (
            <span className="text-xs text-stone-400">chưa mở cửa hàng nào</span>
          ) : (
            shopCounts.map(([name, count]) => (
              <Badge
                key={name}
                variant="outline"
                className="border-amber-300 bg-amber-50 text-amber-800 tabular-nums hover:bg-amber-50"
              >
                {shopLabel(name)}
                {count > 1 ? ` ×${count}` : ''}
              </Badge>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
})
