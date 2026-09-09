'use client'

/**
 * ARENA OBSERVER UI — action & event log:
 *  - current-turn actions of both seats (Vietnamese annotated)
 *  - "Nhật ký gần đây": last ~40 turns of compact summaries following the playhead
 */
import { memo, useEffect, useMemo, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollText, Timer } from 'lucide-react'
import type { BattleInfo, TurnRecord } from './types'
import { SEAT } from './constants'
import { annotateMarket, annotateUnit, summarizeTurn } from './helpers'
import { cn } from '@/lib/utils'
import type { TurnStore } from './useArena'

interface Props {
  viewTurn: TurnRecord | null
  viewIndex: number
  store: TurnStore
  battleInfo: BattleInfo | null
}

function SeatActions({
  seat,
  agentName,
  turn,
}: {
  seat: 0 | 1
  agentName: string
  turn: TurnRecord | null
}) {
  const st = SEAT[seat]
  const act = turn?.acts?.[seat]
  const hands = Array.isArray(act?.hands) ? act.hands : []
  const marketOrders = Array.isArray(act?.market) ? act.market : []
  const ms = turn?.times?.[seat]

  return (
    <div className={cn('rounded-lg border bg-white p-3', st.border, 'border-t-2')}>
      <div className="mb-2 flex items-center gap-2">
        <span
          className={cn(
            'flex size-5 items-center justify-center rounded text-[10px] font-black text-white',
            st.solid,
          )}
        >
          {st.key}
        </span>
        <span className="font-mono text-sm font-semibold">{agentName}</span>
        <span className="ml-auto flex items-center gap-1 text-[10px] text-stone-400 tabular-nums">
          <Timer className="size-3" aria-hidden="true" />
          {ms !== undefined && ms !== null ? `${ms}ms` : '—'}
        </span>
      </div>

      <div className="space-y-1.5 text-xs">
        <div className="flex gap-2">
          <span className={cn('w-14 shrink-0 font-semibold', st.text)}>🧑‍🌾 Nông dân</span>
          <span className="text-stone-700">{annotateUnit(act?.farmer ?? null)}</span>
        </div>

        {hands.length > 0 && (
          <div className="flex gap-2">
            <span className="w-14 shrink-0 font-semibold text-stone-500">👷 Thợ</span>
            <div className="flex flex-wrap gap-x-3 gap-y-1">
              {hands.map((h, i) => (
                <span key={i} className="text-stone-600">
                  <span className="font-mono text-[10px] text-stone-400">H{i + 1}</span>{' '}
                  {annotateUnit(Array.isArray(h) ? h : null)}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-2">
          <span className="w-14 shrink-0 font-semibold text-stone-500">🛒 Chợ</span>
          <span className="text-stone-700">{annotateMarket(marketOrders)}</span>
        </div>
      </div>
    </div>
  )
}

export const ActionLog = memo(function ActionLog({ viewTurn, viewIndex, store, battleInfo }: Props) {
  const scrollRef = useRef<HTMLDivElement | null>(null)

  const entries = useMemo(() => {
    const turns = store.turns
    const out = []
    const start = Math.max(0, viewIndex - 39)
    for (let i = start; i <= viewIndex && i < turns.length; i++) {
      const t = turns[i]
      if (!t) continue
      out.push(summarizeTurn(t))
    }
    return out
  }, [viewIndex, store])

  // stick to bottom while the log auto-extends (unless the user scrolled up)
  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 48
    if (nearBottom) el.scrollTop = el.scrollHeight
  }, [entries])

  return (
    <Card className="border-stone-200 shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base font-semibold">
          <ScrollText className="size-4 text-stone-500" aria-hidden="true" />
          Hành động &amp; sự kiện
          {viewTurn && (
            <span className="text-xs font-normal text-stone-400 tabular-nums">
              Ngày {viewTurn.day} · Giờ {viewTurn.hour}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 px-3 pb-3 sm:px-4 sm:pb-4">
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
          <SeatActions seat={0} agentName={battleInfo?.a ?? 'A'} turn={viewTurn} />
          <SeatActions seat={1} agentName={battleInfo?.b ?? 'B'} turn={viewTurn} />
        </div>

        <div>
          <div className="mb-1.5 text-xs font-semibold text-stone-500">
            Nhật ký gần đây (40 lượt gần playhead)
          </div>
          <div
            ref={scrollRef}
            className="arena-scroll max-h-96 overflow-y-auto rounded-lg border border-stone-200 bg-stone-50/60 p-2"
          >
            <table className="w-full table-fixed border-collapse text-[11px]">
              <tbody>
                {entries.map((e) => (
                  <tr key={e.step} className="border-b border-stone-200/60 last:border-b-0">
                    <td className="w-20 py-1 pr-2 align-top text-stone-400 tabular-nums">
                      D{e.day}·H{String(e.hour).padStart(2, '0')}
                    </td>
                    <td className="w-16 py-1 pr-2 align-top font-mono text-[10px] font-bold text-emerald-700">
                      {battleInfo?.a ?? 'A'}
                    </td>
                    <td className="py-1 pr-2 align-top text-stone-700">{e.a}</td>
                    <td className="w-16 py-1 pr-2 align-top font-mono text-[10px] font-bold text-rose-700">
                      {battleInfo?.b ?? 'B'}
                    </td>
                    <td className="py-1 align-top text-stone-700">{e.b}</td>
                  </tr>
                ))}
                {entries.length === 0 && (
                  <tr>
                    <td className="py-2 text-stone-400">— chưa có dữ liệu —</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </CardContent>
    </Card>
  )
})
