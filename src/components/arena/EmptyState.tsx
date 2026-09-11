'use client'

/**
 * ARENA OBSERVER UI — empty-state hero (no battle yet).
 */
import { Sprout, Radar, MousePointerClick } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AGENT_INFO } from './constants'

export function EmptyState({ streaming }: { streaming: boolean }) {
  return (
    <Card className="border-dashed border-stone-300 bg-white/70 shadow-sm">
      <CardContent className="flex flex-col items-center gap-4 px-4 py-10 text-center sm:py-14">
        <div className="flex size-16 items-center justify-center rounded-full bg-emerald-100">
          <Sprout className="size-8 text-emerald-700" aria-hidden="true" />
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-semibold tracking-tight text-stone-900 sm:text-2xl">
            Kaggriculture Arena — phòng quan sát
          </h2>
          <p className="mx-auto max-w-xl text-sm leading-relaxed text-stone-600">
            {streaming ? (
              <>
                Đang chờ dữ liệu lượt đầu từ runner… bàn cờ, biểu đồ tiền và não trạng thái sẽ tự
                hiện trong giây lát.
              </>
            ) : (
              <>
                Chọn 2 agent và bấm <strong className="text-emerald-700">Bắt đầu trận đấu</strong> để
                quan sát 720 lượt chiến thuật (30 ngày × 24 giờ) trên engine Kaggle thật — streamed
                turn-by-turn qua socket.io.
              </>
            )}
          </p>
        </div>

        <div className="grid w-full max-w-3xl grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {AGENT_INFO.map((agent) => (
            <div
              key={agent.name}
              className="flex items-center gap-3 rounded-lg border border-stone-200 bg-stone-50/60 px-3 py-2.5 text-left"
            >
              <span className="font-mono text-sm font-bold text-stone-800">{agent.name}</span>
              <span className="min-w-0 flex-1 truncate text-xs text-stone-500">{agent.desc}</span>
              <Badge
                variant="outline"
                className={
                  agent.name === 'v7'
                    ? 'border-rose-300 bg-rose-50 text-rose-800'
                    : agent.name === 'v6'
                      ? 'border-amber-300 bg-amber-50 text-amber-800'
                      : agent.name === 'v5'
                        ? 'border-emerald-300 bg-emerald-50 text-emerald-800'
                        : 'border-stone-200 bg-white text-stone-500'
                }
              >
                {agent.tag}
              </Badge>
            </div>
          ))}
        </div>

        <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-stone-500">
          <span className="flex items-center gap-1.5">
            <Radar className="size-3.5 text-emerald-600" aria-hidden="true" />
            Biểu đồ đua tiền hai ghế
          </span>
          <span className="flex items-center gap-1.5">
            <MousePointerClick className="size-3.5 text-amber-600" aria-hidden="true" />
            Tua / phát lại 1×–50×, chế độ live
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
