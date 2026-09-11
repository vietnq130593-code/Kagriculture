'use client'

/**
 * ARENA OBSERVER UI — socket + battle store + playback engine.
 *
 * Performance contract:
 *  - full battle ≈ 719 turn records (15–20 MB) live in a plain external store
 *    object (NOT a React ref / NOT state) so renders can index it cheaply;
 *    React state only carries small scalars: turnCount, viewIndex, flags
 *  - `battle:turns` batches push into the store and bump turnCount (≤ ~12 renders/s)
 *  - playback advances an internal cursor via requestAnimationFrame (≤ 60 fps, dt-capped)
 *  - "live" mode pins the playhead to the newest turn while the battle streams
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { Socket } from 'socket.io-client'
import { io } from 'socket.io-client'
import type { BattleInfo, BattleResult, TurnRecord } from './types'
import { TOTAL_STEPS } from './constants'

/**
 * External turn store — a mutable array wrapper created once per hook instance.
 * Mutation happens exclusively in socket callbacks (event handlers); render
 * only indexes it behind state scalars (turnCount / viewIndex) that change
 * whenever the store grows.
 */
export class TurnStore {
  turns: TurnRecord[] = []

  get length(): number {
    return this.turns.length
  }

  get(i: number): TurnRecord | null {
    if (i < 0 || i >= this.turns.length) return null
    return this.turns[i] ?? null
  }

  pushAll(batch: TurnRecord[]): void {
    for (const rec of batch) this.turns.push(rec)
  }

  slice(from: number, to: number): TurnRecord[] {
    return this.turns.slice(Math.max(0, from), to + 1)
  }

  reset(): void {
    this.turns.length = 0
  }
}

export interface ArenaApi {
  connected: boolean
  agents: string[]
  running: boolean
  battleInfo: BattleInfo | null
  turnCount: number
  viewIndex: number
  playing: boolean
  speed: number
  live: boolean
  result: BattleResult | null
  logs: string[]
  error: string | null
  notice: string | null
  /** external turn store — index it behind turnCount/viewIndex scalars */
  store: TurnStore
  /** turn at the current playhead (clamped), null before first data */
  viewTurn: TurnRecord | null
  start: (a: string, b: string, seed?: number | null) => void
  stop: () => void
  togglePlay: () => void
  setSpeed: (n: number) => void
  setLive: (v: boolean) => void
  seek: (i: number) => void
  dismissError: () => void
  dismissNotice: () => void
}

const MAX_LOG_LINES = 250

export function useArena(): ArenaApi {
  const [store] = useState(() => new TurnStore())
  // mutable cursors — touched ONLY inside callbacks/effects, never during render
  const viewRef = useRef(0)
  const socketRef = useRef<Socket | null>(null)
  const cursor = useRef({
    turnCount: 0,
    live: false,
    playing: false,
    result: null as BattleResult | null,
  })
  const [agents, setAgents] = useState<string[]>([])
  const [connected, setConnected] = useState(false)
  const [running, setRunning] = useState(false)
  const [battleInfo, setBattleInfo] = useState<BattleInfo | null>(null)
  const [turnCount, setTurnCount] = useState(0)
  const [viewIndex, setViewIndex] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeedState] = useState(8)
  const [live, setLiveState] = useState(false)
  const [result, setResult] = useState<BattleResult | null>(null)
  const [logs, setLogs] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  // ---------------------------------------------------------------- socket ---
  useEffect(() => {
    // NEVER put the port in the URL — Caddy routes via the XTransformPort query
    const socket = io('/?XTransformPort=3005', {
      transports: ['websocket', 'polling'],
      forceNew: true,
      reconnection: true,
    })
    socketRef.current = socket

    socket.on('connect', () => setConnected(true))
    socket.on('disconnect', () => setConnected(false))

    socket.on('arena:hello', (data: any) => {
      if (data?.agents) setAgents(data.agents)
      const isRunning = !!data?.running
      setRunning(isRunning)
      if (data?.info) setBattleInfo(data.info)
      if (isRunning && store.length === 0) {
        setNotice(
          'Trận đang chạy — đã bỏ lỡ các lượt đầu, dữ liệu mới sẽ hiển thị từ lượt hiện tại.',
        )
      }
    })

    socket.on('battle:hello', (data: any) => {
      // new battle → wipe the store, auto-live
      store.reset()
      viewRef.current = 0
      cursor.current.turnCount = 0
      cursor.current.live = true
      cursor.current.playing = true
      cursor.current.result = null
      setTurnCount(0)
      setViewIndex(0)
      setResult(null)
      setError(null)
      setNotice(null)
      setBattleInfo({
        a: data?.a ?? '?',
        b: data?.b ?? '?',
        seed: data?.seed ?? null,
        episodeSteps: data?.episodeSteps ?? 720,
        startedAt: data?.startedAt ?? Date.now(),
      })
      setRunning(true)
      setLiveState(true)
      setPlaying(true)
    })

    socket.on('battle:meta', (data: any) => {
      // runner confirmation — may carry the resolved seed
      if (data?.t === 'hello') {
        setBattleInfo((prev) =>
          prev
            ? {
                ...prev,
                a: data.a ?? prev.a,
                b: data.b ?? prev.b,
                seed: data.seed ?? prev.seed,
                episodeSteps: data.episodeSteps ?? prev.episodeSteps,
              }
            : prev,
        )
      }
    })

    socket.on('battle:turns', (data: any) => {
      const batch: TurnRecord[] = data?.turns
      if (!Array.isArray(batch) || batch.length === 0) return
      store.pushAll(batch)
      cursor.current.turnCount = store.length
      setTurnCount(store.length)
    })

    socket.on('battle:end', (data: any) => {
      const r: BattleResult = {
        rewards: [Number(data?.rewards?.[0] ?? 0), Number(data?.rewards?.[1] ?? 0)],
        winner: data?.winner === 0 || data?.winner === 1 ? data.winner : -1,
        wallS: Number(data?.wallS ?? 0),
        turns: Number(data?.turns ?? TOTAL_STEPS),
      }
      cursor.current.result = r
      setResult(r)
      setRunning(false)
    })

    socket.on('battle:log', (data: any) => {
      const line = String(data?.line ?? '')
      if (!line) return
      setLogs((prev) => {
        const next =
          prev.length >= MAX_LOG_LINES ? prev.slice(prev.length - MAX_LOG_LINES + 1) : prev
        return [...next, line]
      })
    })

    socket.on('battle:error', (data: any) => {
      setError(String(data?.message ?? 'Lỗi không xác định từ arena service'))
    })

    socket.on('battle:status', (data: any) => {
      setRunning(!!data?.running)
      if (data?.reason && !cursor.current.result) {
        if (String(data.reason).includes('stopped')) setNotice('Trận đấu đã được dừng theo yêu cầu.')
      }
    })

    socket.on('battle:done', (data: any) => {
      const code = Number(data?.exitCode ?? 0)
      if (code !== 0 && !cursor.current.result) {
        setError(`Trình chạy trận đấu thoát với mã ${code} — xem nhật ký runner bên dưới.`)
      }
    })

    return () => {
      socket.disconnect()
      socketRef.current = null
    }
  }, [store])

  // live mode: follow the tail of the stream -----------------------------------
  useEffect(() => {
    if (live && turnCount > 0) {
      viewRef.current = turnCount - 1
      setViewIndex(viewRef.current)
    }
  }, [live, turnCount])

  // clamp playhead if the store shrank (race on reset) -------------------------
  useEffect(() => {
    if (viewIndex > turnCount - 1) {
      viewRef.current = Math.max(0, turnCount - 1)
      setViewIndex(viewRef.current)
    }
  }, [turnCount, viewIndex])

  // playback loop: rAF, dt-capped, coalesces multiple turns per frame ----------
  useEffect(() => {
    if (!playing) return
    let raf = 0
    let last = performance.now()
    let acc = 0
    const tick = (now: number) => {
      const dt = Math.min(0.25, (now - last) / 1000) // survives tab-switch stalls
      last = now
      acc += dt * speed
      if (acc >= 1) {
        const adv = Math.floor(acc)
        acc -= adv
        const max = Math.max(0, cursor.current.turnCount - 1)
        let next = viewRef.current + adv
        if (next >= max) {
          next = max
          if (!cursor.current.live) {
            cursor.current.playing = false
            setPlaying(false)
          }
        }
        if (next !== viewRef.current) {
          viewRef.current = next
          setViewIndex(next)
        }
      }
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [playing, speed])

  // ---------------------------------------------------------------- actions ---
  const start = useCallback((a: string, b: string, seed?: number | null) => {
    setError(null)
    socketRef.current?.emit('battle:start', {
      a,
      b,
      seed: seed === null || seed === undefined || Number.isNaN(seed) ? undefined : seed,
    })
  }, [])

  const stop = useCallback(() => {
    socketRef.current?.emit('battle:stop')
  }, [])

  const togglePlay = useCallback(() => {
    setPlaying((p) => {
      const next = !p
      cursor.current.playing = next
      return next
    })
  }, [])

  const setSpeed = useCallback((n: number) => {
    setSpeedState(n)
    setLiveState(false)
    cursor.current.live = false
  }, [])

  const setLive = useCallback((v: boolean) => {
    setLiveState(v)
    cursor.current.live = v
    if (v) {
      cursor.current.playing = true
      setPlaying(true)
    }
  }, [])

  const seek = useCallback((i: number) => {
    // scrubbing always exits live mode
    cursor.current.live = false
    setLiveState(false)
    const max = Math.max(0, cursor.current.turnCount - 1)
    const next = Math.max(0, Math.min(i, max))
    viewRef.current = next
    setViewIndex(next)
  }, [])

  const dismissError = useCallback(() => setError(null), [])
  const dismissNotice = useCallback(() => setNotice(null), [])

  // derived: turn under the playhead --------------------------------------------
  const viewTurn = useMemo<TurnRecord | null>(() => {
    if (turnCount === 0) return null
    return store.get(Math.min(viewIndex, turnCount - 1))
  }, [store, turnCount, viewIndex])

  return {
    connected,
    agents,
    running,
    battleInfo,
    turnCount,
    viewIndex,
    playing,
    speed,
    live,
    result,
    logs,
    error,
    notice,
    store,
    viewTurn,
    start,
    stop,
    togglePlay,
    setSpeed,
    setLive,
    seek,
    dismissError,
    dismissNotice,
  }
}
