'use client'

/**
 * ARENA OBSERVER UI — money race chart (the centerpiece).
 * Full-series line chart of both seats' money over turns; the final rewards are
 * appended as a last point once battle:end arrives.
 */
import { memo } from 'react'
import {
  Line,
  LineChart,
  ResponsiveContainer,
  ReferenceLine,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp } from 'lucide-react'
import type { BattleInfo, BattleResult } from './types'
import { STARTING_MONEY, TOTAL_STEPS, SEAT } from './constants'
import { fmtMoney, fmtCompact } from './helpers'

export interface MoneyPoint {
  i: number
  a: number
  b: number
  day: number
  hour: number
  final?: boolean
}

interface Props {
  series: MoneyPoint[]
  battleInfo: BattleInfo | null
  result: BattleResult | null
}

function ChartTooltip({ active, payload }: any) {
  if (!active || !payload || payload.length === 0) return null
  const p = payload[0].payload as MoneyPoint
  return (
    <div className="rounded-md border border-stone-200 bg-white/95 px-3 py-2 text-xs shadow-md">
      <div className="mb-1 font-semibold text-stone-700">
        {p.final ? '🏁 Kết thúc trận' : `Ngày ${p.day} · Giờ ${p.hour}`}
        <span className="ml-1 font-normal text-stone-400">(turn {p.i + 1})</span>
      </div>
      {payload.map((entry: any) => (
        <div key={entry.dataKey} className="flex items-center gap-2 tabular-nums">
          <span className="size-2 rounded-full" style={{ background: entry.color }} />
          <span className="text-stone-500">{entry.name}</span>
          <span className="ml-auto font-bold text-stone-800">{fmtMoney(entry.value)}</span>
        </div>
      ))}
    </div>
  )
}

export const MoneyChart = memo(function MoneyChart({ series, battleInfo, result }: Props) {
  const nameA = battleInfo?.a ?? 'A'
  const nameB = battleInfo?.b ?? 'B'
  const few = series.length < 8

  return (
    <Card className="border-stone-200 shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="flex flex-wrap items-center gap-2 text-base font-semibold">
          <TrendingUp className="size-4 text-emerald-700" aria-hidden="true" />
          Đường đua tiền
          <span className="ml-2 flex items-center gap-2 text-xs font-medium">
            <span className="flex items-center gap-1.5 text-emerald-700">
              <span className="size-2.5 rounded-full bg-emerald-600" /> {nameA} (ghế A)
            </span>
            <span className="flex items-center gap-1.5 text-rose-700">
              <span className="size-2.5 rounded-full bg-rose-600" /> {nameB} (ghế B)
            </span>
            {result && (
              <span className="flex items-center gap-1.5 text-stone-500">
                <span className="size-2.5 rounded-full border border-stone-400" /> thưởng cuối
              </span>
            )}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="h-56 px-2 pb-3 sm:h-64 sm:px-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={series} margin={{ top: 8, right: 12, left: 0, bottom: 4 }}>
            <XAxis
              dataKey="i"
              type="number"
              domain={[0, TOTAL_STEPS]}
              ticks={[0, 120, 240, 360, 480, 600, TOTAL_STEPS]}
              tickFormatter={(v: number) => `D${Math.floor(v / 24)}`}
              tick={{ fontSize: 10, fill: '#a8a29e' }}
              tickLine={false}
              axisLine={{ stroke: '#e7e5e4' }}
            />
            <YAxis
              tickFormatter={(v: number) => '$' + fmtCompact(v)}
              tick={{ fontSize: 10, fill: '#a8a29e' }}
              tickLine={false}
              axisLine={false}
              width={52}
            />
            <Tooltip content={<ChartTooltip />} />
            <ReferenceLine
              y={STARTING_MONEY}
              stroke="#a8a29e"
              strokeDasharray="4 4"
              label={{
                value: 'khởi đầu $3.000',
                position: 'insideTopLeft',
                fontSize: 9,
                fill: '#a8a29e',
              }}
            />
            <Line
              type="monotone"
              dataKey="a"
              name={nameA}
              stroke={SEAT[0].line}
              strokeWidth={2}
              dot={few}
              isAnimationActive={false}
              activeDot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="b"
              name={nameB}
              stroke={SEAT[1].line}
              strokeWidth={2}
              dot={few}
              isAnimationActive={false}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
})
