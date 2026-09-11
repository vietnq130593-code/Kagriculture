'use client'

/**
 * ARENA OBSERVER UI — control panel: battle setup + playback + scrubber.
 */
import { useState } from 'react'
import { Play, Pause, Square, Rocket, RadioTower, Gauge } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { ArenaApi } from './useArena'
import { LIVE_SPEED, SPEED_OPTIONS, TOTAL_STEPS } from './constants'
import { cn } from '@/lib/utils'

export function ControlPanel({ arena }: { arena: ArenaApi }) {
  const { connected, agents, running, turnCount, viewIndex, playing, speed, live, viewTurn } = arena

  const [selA, setSelA] = useState<string>('')
  const [selB, setSelB] = useState<string>('')
  const [seedText, setSeedText] = useState<string>('')

  // defaults: A = v7 (champion), B = v6 (former champion) once the agent list arrives
  const a = selA || (agents.includes('v7') ? 'v7' : agents[0] || '')
  const b = selB || (agents.includes('v6') ? 'v6' : agents[1] || agents[0] || '')

  const seedNum = seedText.trim() === '' ? null : Number(seedText.trim())
  const canStart = connected && !running && !!a && !!b
  const scrubDisabled = live && running

  const hasTurns = turnCount > 0
  const sliderMax = Math.max(0, turnCount - 1)

  return (
    <Card className="border-stone-200 shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base font-semibold">
          <Gauge className="size-4 text-emerald-700" aria-hidden="true" />
          Bảng điều khiển
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* battle setup */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-1.5">
            <Label htmlFor="agent-a" className="text-xs font-medium text-emerald-700">
              Agent A (ghế 0 · emerald)
            </Label>
            <Select value={a} onValueChange={(v) => setSelA(v)} disabled={running}>
              <SelectTrigger id="agent-a" className="h-11 w-full border-stone-300">
                <SelectValue placeholder="Chọn agent A" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {agents.map((name) => (
                    <SelectItem key={name} value={name}>
                      {name}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="agent-b" className="text-xs font-medium text-rose-700">
              Agent B (ghế 1 · rose)
            </Label>
            <Select value={b} onValueChange={(v) => setSelB(v)} disabled={running}>
              <SelectTrigger id="agent-b" className="h-11 w-full border-stone-300">
                <SelectValue placeholder="Chọn agent B" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {agents.map((name) => (
                    <SelectItem key={name} value={name}>
                      {name}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="seed" className="text-xs font-medium text-stone-600">
              Seed (để trống = ngẫu nhiên)
            </Label>
            <Input
              id="seed"
              type="number"
              inputMode="numeric"
              placeholder="vd: 101"
              value={seedText}
              onChange={(e) => setSeedText(e.target.value)}
              disabled={running}
              className="h-11 border-stone-300 tabular-nums"
            />
          </div>

          <div className="flex items-end gap-2">
            <Button
              onClick={() => arena.start(a, b, seedNum)}
              disabled={!canStart}
              className="h-11 flex-1 bg-emerald-600 text-white hover:bg-emerald-700"
            >
              <Rocket className="size-4" aria-hidden="true" />
              Bắt đầu trận đấu
            </Button>
            {running && (
              <Button
                onClick={arena.stop}
                variant="destructive"
                className="h-11 bg-rose-600 hover:bg-rose-700"
              >
                <Square className="size-4" aria-hidden="true" />
                Dừng
              </Button>
            )}
          </div>
        </div>

        {/* playback — only when turns exist */}
        {hasTurns && (
          <div className="rounded-lg border border-stone-200 bg-stone-50/60 p-3 space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <Button
                onClick={arena.togglePlay}
                variant="outline"
                className="h-11 w-11 border-stone-300 bg-white p-0"
                aria-label={playing ? 'Tạm dừng' : 'Phát'}
              >
                {playing ? (
                  <Pause className="size-5 text-stone-700" aria-hidden="true" />
                ) : (
                  <Play className="size-5 text-emerald-700" aria-hidden="true" />
                )}
              </Button>

              <div className="min-w-40 flex-1 sm:max-w-56">
                <Select
                  value={live ? LIVE_SPEED : String(speed)}
                  onValueChange={(v) => {
                    if (v === LIVE_SPEED) arena.setLive(true)
                    else arena.setSpeed(Number(v))
                  }}
                >
                  <SelectTrigger className="h-11 w-full border-stone-300 bg-white" aria-label="Tốc độ phát">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      {SPEED_OPTIONS.map((o) => (
                        <SelectItem key={o.value} value={String(o.value)}>
                          {o.label}
                        </SelectItem>
                      ))}
                      <SelectItem value={LIVE_SPEED}>📻 Xem live (theo trận đấu)</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>

              <Button
                onClick={() => arena.setLive(!live)}
                variant={live ? 'default' : 'outline'}
                className={cn(
                  'h-11 gap-1.5 border-stone-300',
                  live
                    ? 'bg-emerald-600 text-white hover:bg-emerald-700'
                    : 'bg-white text-stone-700 hover:bg-stone-100',
                )}
                aria-pressed={live}
              >
                <RadioTower className="size-4" aria-hidden="true" />
                {live ? <span className="live-pulse">LIVE</span> : 'Xem live'}
              </Button>

              <div className="ml-auto flex items-center gap-2 text-sm">
                {viewTurn ? (
                  <span className="font-medium text-stone-700 tabular-nums">
                    Ngày {viewTurn.day} · Giờ {viewTurn.hour}
                    <span className="ml-2 text-stone-500">
                      (turn {viewTurn.step + 1}/{TOTAL_STEPS})
                    </span>
                  </span>
                ) : (
                  <span className="text-stone-400">—</span>
                )}
              </div>
            </div>

            {/* scrubber with day markers */}
            <div className="relative pt-1 pb-3">
              <Slider
                value={[Math.min(viewIndex, sliderMax)]}
                max={sliderMax}
                min={0}
                step={1}
                onValueChange={(vals) => arena.seek(vals[0] ?? 0)}
                disabled={scrubDisabled}
                aria-label=" tua thời gian"
                className={cn('py-2', live && 'opacity-60')}
              />
              <div className="pointer-events-none absolute inset-x-0 bottom-0 h-2.5" aria-hidden="true">
                {Array.from({ length: 30 }, (_, d) => (
                  <span
                    key={d}
                    className="absolute top-0 h-1.5 w-px bg-stone-300"
                    style={{ left: `${((d * 24) / TOTAL_STEPS) * 100}%` }}
                  />
                ))}
                <span
                  className="absolute top-0 h-1.5 w-px bg-stone-400"
                  style={{ left: '100%' }}
                />
                <span className="absolute -top-0.5 left-0 text-[9px] text-stone-400">D0</span>
                <span className="absolute -top-0.5 right-0 text-[9px] text-stone-400">D29</span>
              </div>
              {scrubDisabled && (
                <Badge className="absolute right-0 top-0 bg-stone-200 text-stone-600 hover:bg-stone-200">
                  tua bị khoá khi live
                </Badge>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
