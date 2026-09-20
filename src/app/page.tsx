'use client'

/**
 * KAGGRICULTURE ARENA — Battle Observer UI (Task 14).
 * Single-page war room: watches two farming agents (v4/v5 family) fight a full
 * 720-turn battle on the real Kaggle engine, streamed turn-by-turn over
 * socket.io from the arena service (port 3005).
 *
 * Data flow: useArena() owns the socket + a useRef turn store (719 records ≈
 * 15–20 MB never touch useState); only small scalars re-render the page.
 */
import { useMemo } from 'react'
import { Sprout, Wifi, WifiOff, X, Info, TriangleAlert } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { useArena } from '@/components/arena/useArena'
import { ControlPanel } from '@/components/arena/ControlPanel'
import { EmptyState } from '@/components/arena/EmptyState'
import { ResultBanner } from '@/components/arena/ResultBanner'
import { MoneyChart, type MoneyPoint } from '@/components/arena/MoneyChart'
import { FarmBoard } from '@/components/arena/FarmBoard'
import { MarketPanel } from '@/components/arena/MarketPanel'
import { ActionLog } from '@/components/arena/ActionLog'
import { BrainPanel } from '@/components/arena/BrainPanel'
import { RunnerLog } from '@/components/arena/RunnerLog'
import { TOTAL_STEPS } from '@/components/arena/constants'
import { cn } from '@/lib/utils'

const GLOBAL_CSS = `
.arena-scroll { scrollbar-width: thin; scrollbar-color: #d6d3d1 transparent; }
.arena-scroll::-webkit-scrollbar { width: 8px; height: 8px; }
.arena-scroll::-webkit-scrollbar-track { background: transparent; }
.arena-scroll::-webkit-scrollbar-thumb { background: #d6d3d1; border-radius: 8px; }
.arena-scroll::-webkit-scrollbar-thumb:hover { background: #a8a29e; }
@keyframes arena-live-pulse { 0%,100% { opacity: 1 } 50% { opacity: 0.45 } }
.live-pulse { animation: arena-live-pulse 1.2s ease-in-out infinite; letter-spacing: 0.08em; }
`

export default function Home() {
  const arena = useArena()
  const {
    connected,
    running,
    battleInfo,
    turnCount,
    result,
    error,
    notice,
    viewTurn,
    store,
    live,
  } = arena

  // full-series money race (turnCount-keyed, NOT viewIndex — the chart is the
  // streaming overview; the playhead view is rendered from viewTurn)
  const moneySeries = useMemo<MoneyPoint[]>(() => {
    const turns = store.turns
    const arr: MoneyPoint[] = []
    for (let i = 0; i < turnCount; i++) {
      const t = turns[i]
      if (!t?.farms) continue
      arr.push({
        i: t.step,
        a: t.farms[0]?.money ?? 0,
        b: t.farms[1]?.money ?? 0,
        day: t.day,
        hour: t.hour,
      })
    }
    if (result) {
      arr.push({
        i: result.turns - 1,
        a: result.rewards[0] ?? 0,
        b: result.rewards[1] ?? 0,
        day: 29,
        hour: 23,
        final: true,
      })
    }
    return arr
  }, [turnCount, result, store])

  const showHero = turnCount === 0 && !battleInfo && !running
  const hasBattle = turnCount > 0

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-[#faf7ef] to-[#f3eee1] text-stone-900">
      <style>{GLOBAL_CSS}</style>

      {/* ------------------------------------------------------------ header --- */}
      <header className="sticky top-0 z-40 border-b border-stone-200/80 bg-[#faf7ef]/90 backdrop-blur">
        <div className="mx-auto flex w-full max-w-7xl flex-wrap items-center gap-x-3 gap-y-1.5 px-3 py-2.5 sm:px-4">
          <div className="flex items-center gap-2">
            <span className="flex size-8 items-center justify-center rounded-lg bg-emerald-100">
              <Sprout className="size-5 text-emerald-700" aria-hidden="true" />
            </span>
            <h1 className="text-sm font-bold tracking-tight sm:text-base">
              Kaggriculture Arena
              <span className="ml-1.5 font-normal text-stone-500">— Trận đấu quan sát</span>
            </h1>
          </div>

          {battleInfo && (
            <div className="hidden items-center gap-2 text-xs text-stone-600 md:flex">
              <span className="font-mono font-bold text-emerald-700">{battleInfo.a}</span>
              <span className="text-stone-400">⚔</span>
              <span className="font-mono font-bold text-rose-700">{battleInfo.b}</span>
              <span className="text-stone-400">·</span>
              <span className="tabular-nums">
                seed {battleInfo.seed !== null && battleInfo.seed !== undefined ? battleInfo.seed : 'ngẫu nhiên'}
              </span>
              {live && running && (
                <span className="live-pulse rounded-full bg-emerald-600 px-2 py-0.5 text-[9px] font-bold text-white">
                  LIVE
                </span>
              )}
            </div>
          )}

          <div className="ml-auto flex items-center gap-1.5 text-xs text-stone-500">
            {connected ? (
              <>
                <span className="relative flex size-2.5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
                  <span className="relative inline-flex size-2.5 rounded-full bg-emerald-500" />
                </span>
                <Wifi className="size-3.5 text-emerald-600" aria-hidden="true" />
                đã kết nối arena
              </>
            ) : (
              <>
                <span className="relative flex size-2.5">
                  <span className="relative inline-flex size-2.5 rounded-full bg-rose-400" />
                </span>
                <WifiOff className="size-3.5 text-rose-500" aria-hidden="true" />
                mất kết nối
              </>
            )}
          </div>
        </div>
      </header>

      {/* -------------------------------------------------------------- main --- */}
      <main className="mx-auto w-full max-w-7xl flex-1 space-y-4 px-3 py-4 sm:px-4">
        {showHero && <EmptyState streaming={running} />}

        <ControlPanel arena={arena} />

        {error && (
          <Alert variant="destructive" className="border-rose-300 bg-rose-50 text-rose-800">
            <TriangleAlert className="size-4 text-rose-600" aria-hidden="true" />
            <AlertDescription className="flex-1 text-rose-800">{error}</AlertDescription>
            <Button
              variant="ghost"
              size="sm"
              onClick={arena.dismissError}
              className="h-8 px-2 text-rose-600 hover:bg-rose-100"
              aria-label="Đóng thông báo lỗi"
            >
              <X className="size-4" aria-hidden="true" />
            </Button>
          </Alert>
        )}

        {notice && !error && (
          <Alert className="border-amber-300 bg-amber-50 text-amber-900">
            <Info className="size-4 text-amber-600" aria-hidden="true" />
            <AlertDescription className="flex-1 text-amber-900">{notice}</AlertDescription>
            <Button
              variant="ghost"
              size="sm"
              onClick={arena.dismissNotice}
              className="h-8 px-2 text-amber-700 hover:bg-amber-100"
              aria-label="Đóng thông báo"
            >
              <X className="size-4" aria-hidden="true" />
            </Button>
          </Alert>
        )}

        {result && battleInfo && <ResultBanner result={result} battleInfo={battleInfo} />}

        {hasBattle && viewTurn && (
          <>
            <MoneyChart series={moneySeries} battleInfo={battleInfo} result={result} />

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <FarmBoard
                farm={viewTurn.farms?.[0] ?? null}
                priv={viewTurn.priv?.[0] ?? null}
                act={viewTurn.acts?.[0] ?? null}
                day={viewTurn.day}
                agentName={battleInfo?.a ?? 'A'}
                seat={0}
              />
              <FarmBoard
                farm={viewTurn.farms?.[1] ?? null}
                priv={viewTurn.priv?.[1] ?? null}
                act={viewTurn.acts?.[1] ?? null}
                day={viewTurn.day}
                agentName={battleInfo?.b ?? 'B'}
                seat={1}
              />
            </div>

            <MarketPanel viewTurn={viewTurn} viewIndex={arena.viewIndex} store={store} />

            <ActionLog
              viewTurn={viewTurn}
              viewIndex={arena.viewIndex}
              store={store}
              battleInfo={battleInfo}
            />

            <BrainPanel viewTurn={viewTurn} battleInfo={battleInfo} />
          </>
        )}

        <RunnerLog logs={arena.logs} />
      </main>

      {/* ------------------------------------------------------------ footer --- */}
      <footer className="mt-auto border-t border-stone-200 bg-[#f5f1e6] pb-[env(safe-area-inset-bottom)]">
        <div className="mx-auto flex w-full max-w-7xl flex-wrap items-center gap-x-4 gap-y-1 px-3 py-3 text-xs text-stone-500 sm:px-4">
          <span className="font-medium">Kaggriculture Arena · v4 ↔ v5 research console</span>
          <span className="tabular-nums">
            {turnCount > 0 ? `${turnCount}/${TOTAL_STEPS} lượt` : 'chưa có lượt'}
          </span>
          <span className={cn('flex items-center gap-1', connected ? 'text-emerald-600' : 'text-rose-500')}>
            <span
              className={cn('size-2 rounded-full', connected ? 'bg-emerald-500' : 'bg-rose-400')}
              aria-hidden="true"
            />
            {connected ? 'socket.io đã kết nối' : 'socket.io mất kết nối'}
          </span>
        </div>
      </footer>
    </div>
  )
}
