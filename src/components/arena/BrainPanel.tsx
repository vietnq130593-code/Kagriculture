'use client'

/**
 * ARENA OBSERVER UI — brain panel (agent diagnostics).
 * v4-family diags (mode/pm/opp_flows/herd/crop_plan/feed_demand) get bespoke
 * rendering; ANY unknown key (v5 brain fields will arrive later) renders
 * generically: numbers → value/mini-bar, strings → badge, objects → mini
 * table, arrays → joined text. Capped at 12 rows, most-important first.
 */
import { memo, useMemo } from 'react'
import { Brain, Timer } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import type { BattleInfo, TurnRecord } from './types'
import { SEAT } from './constants'
import { ANIMAL_INFO, PRODUCT_MAP } from './constants'
import { cn } from '@/lib/utils'

interface Props {
  viewTurn: TurnRecord | null
  battleInfo: BattleInfo | null
}

const PRIORITY = [
  'strategy',
  'mode',
  'health',
  'H',
  'pm',
  'posterior',
  'herd',
  'opp_flows',
  'crop_plan',
  'feed_demand',
]
const MAX_ROWS = 12

const KEY_LABEL: Record<string, string> = {
  strategy: 'Chiến lược',
  mode: 'Chế độ',
  health: 'Sức khỏe H',
  H: 'Sức khỏe H',
  pm: 'P(MIRROR)',
  posterior: 'Hậu nghiệm',
  herd: 'Mục tiêu đàn',
  opp_flows: 'Luồng đối thủ (u/ngày)',
  crop_plan: 'Kế hoạch cây trồng',
  feed_demand: 'Nhu cầu thức ăn',
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-start gap-2 border-b border-stone-100 py-1.5 last:border-b-0">
      <span className="w-32 shrink-0 text-[11px] font-semibold text-stone-500">{label}</span>
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  )
}

function MiniBar({ value, max, color }: { value: number; max: number; color?: string }) {
  const pct = max > 0 ? Math.max(0, Math.min(100, (value / max) * 100)) : 0
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-stone-100">
      <div className="h-full rounded-full" style={{ width: `${pct}%`, background: color ?? '#78716c' }} />
    </div>
  )
}

function numFmt(n: number): string {
  if (Math.abs(n) >= 1000) return n.toLocaleString('vi-VN')
  return Math.round(n * 100) / 100 === n ? String(n) : n.toFixed(2)
}

function ModeBadge({ value }: { value: string }) {
  if (value === 'CONTEST') {
    return (
      <Badge className="border-amber-400 bg-amber-100 text-amber-800 hover:bg-amber-100">
        CONTEST — tranh giành
      </Badge>
    )
  }
  if (value === 'MIRROR') {
    return (
      <Badge className="border-stone-500 bg-stone-800 text-white hover:bg-stone-800">
        MIRROR — đối xứng
      </Badge>
    )
  }
  return <Badge variant="outline" className="border-stone-300 bg-stone-50 text-stone-600">{value}</Badge>
}

function HerdRow({ herd }: { herd: Record<string, any> }) {
  const parts: string[] = []
  const goose = herd.goose_target
  const cow = herd.cow_target
  const sheep = herd.sheep_target
  if (goose !== undefined && goose !== null) parts.push(`🦢 Ngỗng ${goose}`)
  if (cow !== undefined && cow !== null) parts.push(`🐄 Bò ${cow}`)
  if (sheep !== undefined && sheep !== null) parts.push(`🐑 Cừu ${sheep}`)
  if (parts.length === 0) {
    for (const [k, v] of Object.entries(herd)) parts.push(`${k}: ${String(v)}`)
  }
  return <span className="text-xs text-stone-700">{parts.join(' · ')}</span>
}

function renderValue(key: string, value: any): React.ReactNode {
  if (value === null || value === undefined) return <span className="text-xs text-stone-400">—</span>

  // bespoke keys ------------------------------------------------------------
  if (key === 'mode' || key === 'strategy') {
    return typeof value === 'string' ? <ModeBadge value={value} /> : String(value)
  }

  if (key === 'pm') {
    const v = typeof value === 'number' ? Math.max(0, Math.min(1, value)) : 0
    return (
      <div className="flex items-center gap-2">
        <Progress value={v * 100} className="h-2 flex-1" />
        <span className="w-10 text-right text-xs font-semibold tabular-nums text-stone-700">
          {numFmt(v)}
        </span>
      </div>
    )
  }

  if (key === 'health' || key === 'H') {
    if (typeof value !== 'number') return String(value)
    const v = value <= 1 ? value * 100 : value
    const clamped = Math.max(0, Math.min(100, v))
    return (
      <div className="flex items-center gap-2">
        <div className="h-2 w-full overflow-hidden rounded-full bg-stone-100">
          <div
            className="h-full rounded-full"
            style={{
              width: `${clamped}%`,
              background: clamped >= 60 ? '#059669' : clamped >= 30 ? '#d97706' : '#e11d48',
            }}
          />
        </div>
        <span className="w-12 text-right text-xs font-semibold tabular-nums text-stone-700">
          {Math.round(clamped)}%
        </span>
      </div>
    )
  }

  if (key === 'herd' && typeof value === 'object') {
    return <HerdRow herd={value} />
  }

  if ((key === 'posterior' || key === 'opp_flows' || key === 'crop_plan') && typeof value === 'object') {
    const entries = Object.entries(value as Record<string, any>)
      .filter(([, v]) => v !== null && v !== undefined)
      .slice(0, 8)
    if (key === 'posterior') {
      const max = Math.max(...entries.map(([, v]) => Number(v) || 0), 1e-9)
      return (
        <div className="space-y-1">
          {entries.map(([k, v]) => (
            <div key={k} className="flex items-center gap-2">
              <span className="w-20 shrink-0 truncate font-mono text-[10px] text-stone-500">{k}</span>
              <MiniBar value={Number(v) || 0} max={max} color="#059669" />
              <span className="w-10 text-right text-[10px] tabular-nums text-stone-600">
                {numFmt(Number(v) || 0)}
              </span>
            </div>
          ))}
        </div>
      )
    }
    if (key === 'opp_flows') {
      return (
        <div className="flex flex-wrap gap-1.5">
          {entries.map(([k, v]) => (
            <span
              key={k}
              className={cn(
                'rounded border px-1.5 py-px font-mono text-[10px] tabular-nums',
                PRODUCT_MAP[k]
                  ? 'border-stone-300 bg-stone-50 text-stone-700'
                  : 'border-stone-300 bg-white text-stone-600',
              )}
            >
              {k} {numFmt(Number(v) || 0)}
            </span>
          ))}
        </div>
      )
    }
    // crop_plan
    return (
      <div className="flex flex-wrap gap-1.5">
        {entries.map(([k, v]) => (
          <span
            key={k}
            className="rounded-full border border-green-300 bg-green-50 px-2 py-0.5 font-mono text-[10px] font-semibold text-green-800 tabular-nums"
          >
            {k} ×{String(v)}
          </span>
        ))}
      </div>
    )
  }

  if (key === 'feed_demand') {
    return (
      <Badge variant="outline" className="border-amber-300 bg-amber-50 text-amber-800 tabular-nums">
        {String(value)} đơn vị
      </Badge>
    )
  }

  // generic fallbacks --------------------------------------------------------
  if (typeof value === 'number') {
    if (value >= 0 && value <= 1) {
      return (
        <div className="flex items-center gap-2">
          <MiniBar value={value} max={1} />
          <span className="text-xs tabular-nums text-stone-700">{numFmt(value)}</span>
        </div>
      )
    }
    return <span className="text-xs font-semibold tabular-nums text-stone-700">{numFmt(value)}</span>
  }

  if (typeof value === 'string') {
    return (
      <Badge variant="outline" className="border-stone-300 bg-white text-stone-600">
        {value.slice(0, 40)}
      </Badge>
    )
  }

  if (typeof value === 'boolean') {
    return <span className="text-xs text-stone-700">{value ? '✓' : '✗'}</span>
  }

  if (Array.isArray(value)) {
    return <span className="text-xs text-stone-600">{value.slice(0, 8).join(', ')}</span>
  }

  // nested object
  const entries = Object.entries(value as Record<string, any>).slice(0, 6)
  return (
    <div className="flex flex-wrap gap-x-3 gap-y-0.5">
      {entries.map(([k, v]) => (
        <span key={k} className="font-mono text-[10px] text-stone-500">
          {k}:
          <span className="ml-0.5 font-semibold text-stone-700">{String(v).slice(0, 24)}</span>
        </span>
      ))}
    </div>
  )
}

function SeatBrain({
  seat,
  agentName,
  diag,
  ms,
}: {
  seat: 0 | 1
  agentName: string
  diag: Record<string, any> | null | undefined
  ms: number | null | undefined
}) {
  const st = SEAT[seat]

  const rows = useMemo(() => {
    const entries = Object.entries(diag ?? {}).filter(
      ([, v]) => v !== null && v !== undefined,
    )
    entries.sort((a, b) => {
      const ia = PRIORITY.indexOf(a[0])
      const ib = PRIORITY.indexOf(b[0])
      return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib)
    })
    return entries.slice(0, MAX_ROWS)
  }, [diag])

  return (
    <Card className={cn('border-stone-200 border-t-4 shadow-sm', st.border)}>
      <CardHeader className="p-3 pb-1 sm:p-4 sm:pb-1">
        <CardTitle className="flex items-center gap-2 text-sm font-semibold">
          <Brain className={cn('size-4', st.text)} aria-hidden="true" />
          <span className="font-mono">{agentName}</span>
          <span className="text-xs font-normal text-stone-400">não trạng thái</span>
          {ms !== undefined && ms !== null && (
            <span className="ml-auto flex items-center gap-1 text-[10px] text-stone-400 tabular-nums">
              <Timer className="size-3" aria-hidden="true" />
              {ms}ms
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="px-3 pb-3 pt-1 sm:px-4 sm:pb-4">
        {rows.length === 0 ? (
          <span className="text-xs text-stone-400">agent không xuất chẩn đoán nội bộ</span>
        ) : (
          rows.map(([key, value]) => (
            <Row key={key} label={KEY_LABEL[key] ?? key}>
              {renderValue(key, value)}
            </Row>
          ))
        )}
        <div className="mt-2 flex flex-wrap gap-1.5 text-[9px] text-stone-400">
          <span>{ANIMAL_INFO.GOOSE.product}←🦢 · {ANIMAL_INFO.COW.product}←🐄 · {ANIMAL_INFO.SHEEP.product}←🐑</span>
        </div>
      </CardContent>
    </Card>
  )
}

export const BrainPanel = memo(function BrainPanel({ viewTurn, battleInfo }: Props) {
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <SeatBrain
        seat={0}
        agentName={battleInfo?.a ?? 'A'}
        diag={viewTurn?.diag?.[0]}
        ms={viewTurn?.times?.[0]}
      />
      <SeatBrain
        seat={1}
        agentName={battleInfo?.b ?? 'B'}
        diag={viewTurn?.diag?.[1]}
        ms={viewTurn?.times?.[1]}
      />
    </div>
  )
})
