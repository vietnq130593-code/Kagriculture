'use client'

/**
 * ARENA OBSERVER UI — farm board (10×10 tile grid) with farmer/hand overlay,
 * action highlight, board stats and private panels (shed / seeds / bags).
 */
import { memo, useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Tractor, Sprout, Home, Fence, CircleDollarSign, Users } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import type { ActionSet, Farm, Private, Seat } from './types'
import {
  ANIMAL_INFO,
  CROP_CODE,
  CROP_COLOR,
  QUADRANTS,
  SEAT,
  SHED_CAPACITY,
} from './constants'
import { emptyFarm, fmtMoney, tileKindOf } from './helpers'
import { cn } from '@/lib/utils'

/* ------------------------------------------------------------------ tiles --- */

const TileCell = memo(function TileCell({ tile, day }: { tile: any; day: number }) {
  const kind = tileKindOf(tile)

  if (kind === 'EMPTY') {
    return <div className="aspect-square rounded-[3px] border border-stone-200/70 bg-[#efe9dc]" />
  }

  if (kind === 'LOCKED') {
    return (
      <div className="aspect-square rounded-[3px] border border-dashed border-stone-300 bg-[repeating-linear-gradient(45deg,#f7f5f0_0_4px,#efece4_4px_8px)] opacity-80" />
    )
  }

  if (kind === 'WEED') {
    return (
      <div className="relative aspect-square rounded-[3px] border border-stone-300 bg-stone-300/70">
        <span className="absolute left-[22%] top-[20%] size-[3px] rounded-full bg-stone-600" />
        <span className="absolute right-[24%] top-[48%] size-[4px] rounded-full bg-stone-700" />
        <span className="absolute bottom-[18%] left-[45%] size-[3px] rounded-full bg-stone-600" />
        <span className="absolute inset-0 flex items-center justify-center text-[8px] text-stone-700">
          cỏ
        </span>
      </div>
    )
  }

  if (kind === 'PLANT') {
    const color = CROP_COLOR[tile.crop] ?? '#78716c'
    const watered = !!tile.watered_today
    const thirsty = (tile.consecutive_unwatered ?? 0) >= 1 && !watered
    const yieldUnits = tile.yield_units ?? 0
    const fertilized = (tile.fertilized_until_day ?? -1) >= day
    return (
      <div
        className={cn('relative aspect-square rounded-[3px] border', watered && 'ring-2 ring-emerald-400')}
        style={{
          borderColor: color + 'aa',
          background: `linear-gradient(135deg, ${color}2e, ${color}14)`,
        }}
        title={`${tile.crop} · trồng ngày ${tile.planted_day} · năng suất ${yieldUnits}`}
      >
        <span
          className="absolute left-0.5 top-0.5 text-[9px] font-black leading-none"
          style={{ color }}
        >
          {CROP_CODE[tile.crop] ?? '?'}
        </span>
        {fertilized && (
          <span className="absolute right-0.5 top-0.5 text-[8px] leading-none text-lime-700">
            ✦
          </span>
        )}
        {thirsty && (
          <span className="absolute right-0.5 bottom-0.5 text-[9px] font-bold leading-none text-red-600">
            !
          </span>
        )}
        {yieldUnits > 0 && (
          <span className="absolute bottom-0.5 right-[45%] translate-x-1/2 rounded-sm bg-amber-400/90 px-[3px] text-[8px] font-bold leading-[10px] text-amber-950 tabular-nums">
            {yieldUnits}
          </span>
        )}
      </div>
    )
  }

  // STRUCTURE (COOP | PASTURE)
  const animal = tile.animal
  const unfed = (tile.consecutive_unfed ?? 0) >= 1
  const yieldUnits = tile.yield_units ?? 0
  const isCoop = tile.kind === 'COOP'
  return (
    <div
      className={cn(
        'relative aspect-square rounded-[3px] border',
        isCoop ? 'border-amber-600/60 bg-amber-200/50' : 'border-lime-700/50 bg-lime-200/45',
        unfed && 'ring-2 ring-red-400',
      )}
      title={`${tile.kind}${animal ? ' · ' + animal : ''} · năng suất chờ ${yieldUnits}`}
    >
      {animal ? (
        <span className="absolute inset-0 flex items-center justify-center text-[13px] leading-none">
          {ANIMAL_INFO[animal]?.icon ?? '?'}
        </span>
      ) : (
        <span className="absolute inset-0 flex items-center justify-center text-stone-600">
          {isCoop ? (
            <Home className="size-3.5 text-amber-700/80" aria-hidden="true" />
          ) : (
            <Fence className="size-3.5 text-lime-800/80" aria-hidden="true" />
          )}
        </span>
      )}
      {tile.fertilizer_available && (
        <span className="absolute right-0.5 top-0.5 text-[8px] leading-none text-amber-600">★</span>
      )}
      {tile.cared_today && (
        <span className="absolute left-0.5 top-0.5 text-[8px] leading-none text-rose-500">♥</span>
      )}
      {yieldUnits > 0 && (
        <span className="absolute bottom-0.5 right-[45%] translate-x-1/2 rounded-sm bg-amber-400/90 px-[3px] text-[8px] font-bold leading-[10px] text-amber-950 tabular-nums">
          {yieldUnits}
        </span>
      )}
    </div>
  )
})

/* ---------------------------------------------------------- animated number --- */

function useAnimatedNumber(value: number, duration = 350): number {
  const [display, setDisplay] = useState(value)
  const fromRef = useRef(value)
  useEffect(() => {
    const from = fromRef.current
    if (from === value) return
    let raf = 0
    const t0 = performance.now()
    const tick = (now: number) => {
      const p = Math.min(1, (now - t0) / duration)
      const e = 1 - Math.pow(1 - p, 3)
      setDisplay(from + (value - from) * e)
      if (p < 1) {
        raf = requestAnimationFrame(tick)
      } else {
        fromRef.current = value
      }
    }
    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      fromRef.current = value
    }
  }, [value, duration])
  return display
}

/* -------------------------------------------------------------- the board --- */

interface BoardProps {
  farm: Farm | null
  priv: Private | null
  act: ActionSet | null
  day: number
  agentName: string
  seat: Seat
}

function FarmBoardInner({ farm, priv, act, day, agentName, seat }: BoardProps) {
  const f = farm ?? emptyFarm()
  const st = SEAT[seat]
  const moneyDisplay = useAnimatedNumber(f.money ?? 0)

  const tiles = f.tiles ?? []
  const stats = { plants: 0, animals: 0, weeds: 0, structures: 0 }
  for (const row of tiles) {
    if (!Array.isArray(row)) continue
    for (const tile of row) {
      const kind = tileKindOf(tile)
      if (kind === 'PLANT') stats.plants++
      else if (kind === 'WEED') stats.weeds++
      else if (kind === 'STRUCTURE') {
        stats.structures++
        if (tile.animal) stats.animals++
      }
    }
  }

  const farmerAction = Array.isArray(act?.farmer) ? act.farmer[0] : null
  const isBusy = !!farmerAction && farmerAction !== 'PASS'

  const farmerX = f.farmer?.[0] ?? 0
  const farmerY = f.farmer?.[1] ?? 0
  const hands: [number, number][] = Array.isArray(f.hands) ? f.hands : []

  return (
    <Card className={cn('overflow-hidden border-stone-200 border-t-4 shadow-sm', st.border)}>
      <CardHeader className="space-y-2 p-3 pb-2 sm:p-4 sm:pb-2">
        <div className="flex flex-wrap items-center gap-2">
          <CardTitle className="flex items-center gap-2 text-base font-semibold">
            <span
              className={cn(
                'flex size-6 items-center justify-center rounded-md text-[11px] font-black text-white',
                st.solid,
              )}
            >
              {st.key}
            </span>
            <span className="font-mono">{agentName}</span>
            {isBusy && (
              <motion.span
                key={`${farmerAction}-${farmerX}-${farmerY}`}
                initial={{ opacity: 0, scale: 0.7 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ type: 'spring', stiffness: 400, damping: 18 }}
                className={cn('rounded-full border px-2 py-0.5 text-[10px] font-bold', st.chipBg)}
              >
                {farmerAction}
              </motion.span>
            )}
          </CardTitle>
          <span className="ml-auto flex items-center gap-1.5 text-base font-bold tabular-nums text-stone-800">
            <CircleDollarSign className={cn('size-4', st.text)} aria-hidden="true" />
            {fmtMoney(moneyDisplay)}
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-stone-600">
          <span className="flex items-center gap-1">
            <Sprout className="size-3 text-emerald-700" aria-hidden="true" />
            {stats.plants} cây
          </span>
          <span>🐾 {stats.animals} con</span>
          <span>🪵 {stats.structures} chuồng</span>
          <span>🌿 {stats.weeds} cỏ dại</span>
          <span className="flex items-center gap-1">
            <Users className="size-3" aria-hidden="true" />
            {hands.length} thợ · hôm nay +{f.hires_today ?? 0}
          </span>
          <span className="ml-auto flex items-center gap-1">
            {QUADRANTS.map((q) => {
              const unlocked = (f.unlocked_quadrants ?? []).includes(q)
              return (
                <span
                  key={q}
                  className={cn(
                    'rounded px-1 py-px font-mono text-[9px] font-bold',
                    unlocked ? st.chipBg : 'bg-stone-100 text-stone-300',
                  )}
                  title={unlocked ? `Đã mở ${q}` : `Chưa mở ${q}`}
                >
                  {q}
                </span>
              )
            })}
          </span>
        </div>
      </CardHeader>

      <CardContent className="p-2 sm:p-4 sm:pt-2">
        {/* board + unit overlay */}
        <div
          className={cn(
            'relative mx-auto w-full max-w-[380px] rounded-lg p-1.5',
            isBusy ? cn('bg-white ring-2', st.ring) : 'bg-white ring-1 ring-stone-200',
          )}
        >
          <div className="grid grid-cols-10 gap-[2px]">
            {Array.from({ length: 10 }, (_, y) =>
              Array.from({ length: 10 }, (_, x) => (
                <TileCell key={`${y}-${x}`} tile={tiles[y]?.[x] ?? null} day={day} />
              )),
            )}
          </div>
          {/* overlay: farmer + hands markers */}
          <div className="pointer-events-none absolute inset-1.5 grid grid-cols-10 gap-[2px]">
            {hands.map((h, i) => (
              <div
                key={`hand-${i}-${h?.[0]}-${h?.[1]}`}
                style={{ gridColumn: (h?.[0] ?? 0) + 1, gridRow: (h?.[1] ?? 0) + 1 }}
                className="flex aspect-square items-center justify-center"
              >
                <span className="flex size-[78%] items-center justify-center rounded-full border-[1.5px] border-stone-600 bg-white/85 text-[7px] font-bold text-stone-700 tabular-nums">
                  H{i + 1}
                </span>
              </div>
            ))}
            <div
              style={{ gridColumn: farmerX + 1, gridRow: farmerY + 1 }}
              className="flex aspect-square items-center justify-center"
            >
              <motion.span
                key={`${farmerX}-${farmerY}`}
                initial={{ scale: 1.45 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.18 }}
                className={cn(
                  'flex size-[88%] items-center justify-center rounded-full text-white shadow-md',
                  st.solid,
                )}
                title={`Nông dân (${farmerX},${farmerY})`}
              >
                <Tractor className="size-[62%]" aria-hidden="true" />
              </motion.span>
            </div>
          </div>
        </div>

        {/* private state */}
        <PrivatePanel priv={priv} seat={seat} />
      </CardContent>
    </Card>
  )
}

/* ----------------------------------------------------------- private panel --- */

function ChipList({
  rec,
  colorCls,
  emptyText,
}: {
  rec: Record<string, number> | null | undefined
  colorCls: (key: string) => string
  emptyText: string
}) {
  const entries = Object.entries(rec ?? {}).filter(([, v]) => (v ?? 0) > 0)
  if (entries.length === 0) return <span className="text-xs text-stone-400">{emptyText}</span>
  return (
    <div className="flex flex-wrap gap-1.5">
      {entries.map(([k, v]) => (
        <span
          key={k}
          className={cn(
            'rounded-full border px-2 py-0.5 font-mono text-[10px] font-semibold tabular-nums',
            colorCls(k),
          )}
        >
          {k} ×{v}
        </span>
      ))}
    </div>
  )
}

function productChipCls(name: string): string {
  switch (name) {
    case 'WHEAT':
      return 'border-amber-300 bg-amber-50 text-amber-800'
    case 'CARROT':
      return 'border-orange-300 bg-orange-50 text-orange-800'
    case 'TOMATO':
      return 'border-red-300 bg-red-50 text-red-800'
    case 'STRAWBERRY':
      return 'border-rose-300 bg-rose-50 text-rose-800'
    case 'MELON':
      return 'border-green-300 bg-green-50 text-green-800'
    case 'EGG':
      return 'border-yellow-300 bg-yellow-50 text-yellow-800'
    case 'MILK':
      return 'border-stone-300 bg-stone-50 text-stone-700'
    case 'WOOL':
      return 'border-stone-300 bg-stone-100 text-stone-600'
    case 'FERTILIZER':
      return 'border-lime-400 bg-lime-50 text-lime-800'
    case 'GOOSE':
    case 'COW':
    case 'SHEEP':
      return 'border-emerald-300 bg-emerald-50 text-emerald-800'
    default:
      return 'border-stone-300 bg-white text-stone-600'
  }
}

function cropChipCls(name: string): string {
  switch (name) {
    case 'WHEAT':
      return 'border-amber-300 bg-amber-50 text-amber-800'
    case 'CARROT':
      return 'border-orange-300 bg-orange-50 text-orange-800'
    case 'TOMATO':
      return 'border-red-300 bg-red-50 text-red-800'
    case 'STRAWBERRY':
      return 'border-rose-300 bg-rose-50 text-rose-800'
    case 'MELON':
      return 'border-green-300 bg-green-50 text-green-800'
    default:
      return 'border-stone-300 bg-white text-stone-600'
  }
}

function PrivatePanel({ priv, seat }: { priv: Private | null; seat: Seat }) {
  const st = SEAT[seat]
  const shed = priv?.shed ?? {}
  const shedTotal = Object.values(shed).reduce((s, v) => s + (v ?? 0), 0)
  const inventories = priv?.inventories ?? []

  return (
    <div className="mt-3 border-t border-stone-200 pt-3">
      <Tabs defaultValue="shed">
        <TabsList className="h-9 bg-stone-100 p-0.5">
          <TabsTrigger value="shed" className="h-8 px-3 text-xs">
            Kho shed
          </TabsTrigger>
          <TabsTrigger value="seeds" className="h-8 px-3 text-xs">
            Hạt giống
          </TabsTrigger>
          <TabsTrigger value="bags" className="h-8 px-3 text-xs">
            Túi
          </TabsTrigger>
        </TabsList>

        <TabsContent value="shed" className="mt-2 space-y-1.5">
          <div className="flex items-center gap-2 text-[10px] text-stone-500">
            <Progress value={(shedTotal / SHED_CAPACITY) * 100} className="h-1.5 flex-1" />
            <span className="tabular-nums">
              {shedTotal}/{SHED_CAPACITY}
            </span>
          </div>
          <ChipList rec={shed} colorCls={productChipCls} emptyText="kho trống" />
        </TabsContent>

        <TabsContent value="seeds" className="mt-2">
          <ChipList rec={priv?.seeds} colorCls={cropChipCls} emptyText="không có hạt" />
        </TabsContent>

        <TabsContent value="bags" className="mt-2 space-y-1.5">
          {inventories.length === 0 && (
            <span className="text-xs text-stone-400">không có túi nào</span>
          )}
          {inventories.map((inv, i) => {
            const label = i === 0 ? 'Túi F' : `Túi H${i}`
            return (
              <div key={i} className="flex flex-wrap items-center gap-1.5">
                <span className={cn('rounded border px-1.5 py-px text-[10px] font-bold', st.chipBg)}>
                  {label}
                </span>
                <ChipList rec={inv} colorCls={productChipCls} emptyText="(trống)" />
              </div>
            )
          })}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export const FarmBoard = memo(FarmBoardInner)
