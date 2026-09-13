/**
 * ARENA SERVICE — kaggriculture battle orchestrator (port 3005).
 *
 * Spawns the Python battle runner (kaggriculture/arena/run_battle.py) and
 * streams every turn of the 720-turn battle to all connected Observer UIs
 * via socket.io. Turns are batched (~80ms) to keep the browser calm while
 * the full battle completes in ~6-10s.
 *
 * Frontend connects with: io("/?XTransformPort=3005")
 *
 * Client → server:
 *   battle:start {a: "v5", b: "v4", seed?: number}
 *   battle:stop
 * Server → client:
 *   arena:hello   {agents: [...], status}
 *   battle:hello  {a, b, seed, episodeSteps, startedAt}
 *   battle:turns  {turns: [turnRecord, ...]}   (batched)
 *   battle:end    {rewards, winner, wallS, turns}
 *   battle:log    {line}                       (runner stderr)
 *   battle:error  {message}
 *   battle:status {running, info}
 */
import { createServer } from 'http'
import { Server } from 'socket.io'
import { spawn, type ChildProcess } from 'child_process'
import { appendFileSync, mkdirSync, openSync, readdirSync, readFileSync, writeFileSync } from 'fs'
import { join } from 'path'

const PORT = 3005
const RUNNER = '/home/z/my-project/kaggriculture/arena/run_battle.py'
const BATTLE_DIR = '/home/z/my-project/kaggriculture/battles'
const PYTHON = 'python3'

// Task 69: v14 (ARI CLASS) registered as new champion; v13 kept as previous champion
const AGENTS = ['v14', 'v13', 'kme3', 'kme3v10', 'aurax']

mkdirSync(BATTLE_DIR, { recursive: true })

const httpServer = createServer()
const io = new Server(httpServer, {
  // DO NOT change the path, it is used by Caddy to forward the request to the correct port
  path: '/',
  cors: { origin: '*', methods: ['GET', 'POST'] },
  pingTimeout: 60000,
  pingInterval: 25000,
  maxHttpBufferSize: 50e6,
})

interface BattleInfo {
  a: string
  b: string
  seed: number | null
  episodeSteps: number
  startedAt: number
}

let proc: ChildProcess | null = null
let currentBattle: BattleInfo | null = null
let battleFile: string | null = null
let batch: any[] = []
let batchTimer: ReturnType<typeof setInterval> | null = null

function statusPayload() {
  return {
    running: !!proc,
    info: currentBattle,
    agents: AGENTS,
  }
}

function flushBatch() {
  if (batch.length === 0) return
  const turns = batch
  batch = []
  io.emit('battle:turns', { turns })
}

function startBatchTimer() {
  stopBatchTimer()
  batchTimer = setInterval(flushBatch, 80)
}

function stopBatchTimer() {
  if (batchTimer) {
    flushBatch()
    clearInterval(batchTimer)
    batchTimer = null
  }
}

function stopBattle(reason: string) {
  if (proc) {
    try {
      proc.kill('SIGKILL')
    } catch {}
    proc = null
  }
  stopBatchTimer()
  currentBattle = null
  io.emit('battle:status', { ...statusPayload(), reason })
}

function startBattle(a: string, b: string, seed: number | null) {
  if (proc) {
    stopBattle('replaced by new battle')
  }
  const args = [PYTHON, '-u', RUNNER, '--a', a, '--b', b]
  if (seed !== null && seed !== undefined && !Number.isNaN(seed)) {
    args.push('--seed', String(seed))
  }

  battleFile = join(BATTLE_DIR, `battle_${Date.now()}.jsonl`)
  writeFileSync(battleFile, '')

  currentBattle = {
    a,
    b,
    seed,
    episodeSteps: 720,
    startedAt: Date.now(),
  }

  const child = spawn(PYTHON, args.slice(2), {
    cwd: '/home/z/my-project/kaggriculture',
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  proc = child

  io.emit('battle:hello', {
    a,
    b,
    seed,
    episodeSteps: 720,
    startedAt: currentBattle.startedAt,
  })
  startBatchTimer()

  let stdoutBuf = ''
  child.stdout!.setEncoding('utf8')
  child.stdout!.on('data', (chunk: string) => {
    stdoutBuf += chunk
    let idx: number
    while ((idx = stdoutBuf.indexOf('\n')) >= 0) {
      const line = stdoutBuf.slice(0, idx).trim()
      stdoutBuf = stdoutBuf.slice(idx + 1)
      if (!line) continue
      if (battleFile) {
        try {
          appendFileSync(battleFile, line + '\n')
        } catch {}
      }
      let evt: any
      try {
        evt = JSON.parse(line)
      } catch {
        continue
      }
      if (evt.t === 'turn') {
        batch.push(evt)
        if (batch.length >= 48) flushBatch()
      } else if (evt.t === 'hello') {
        io.emit('battle:meta', evt)
      } else if (evt.t === 'end') {
        flushBatch()
        io.emit('battle:end', evt)
      }
    }
  })

  child.stderr!.setEncoding('utf8')
  child.stderr!.on('data', (chunk: string) => {
    for (const line of chunk.split('\n')) {
      if (line.trim()) io.emit('battle:log', { line: line.slice(0, 500) })
    }
  })

  child.on('error', (err) => {
    io.emit('battle:error', { message: `spawn failed: ${err.message}` })
    proc = null
    stopBatchTimer()
    currentBattle = null
  })

  child.on('close', (code) => {
    flushBatch()
    stopBatchTimer()
    if (proc === child) {
      proc = null
      currentBattle = null
    }
    io.emit('battle:status', { ...statusPayload(), exitCode: code })
    io.emit('battle:done', { exitCode: code, file: battleFile })
  })
}

io.on('connection', (socket) => {
  console.log(`[arena] observer connected: ${socket.id}`)
  socket.emit('arena:hello', statusPayload())

  socket.on('battle:start', (data: { a?: string; b?: string; seed?: number }) => {
    const a = data?.a
    const b = data?.b
    if (!a || !b) {
      socket.emit('battle:error', { message: 'battle:start requires {a, b}' })
      return
    }
    console.log(`[arena] start: ${a} vs ${b} seed=${data?.seed ?? 'random'}`)
    startBattle(a, b, data?.seed ?? null)
  })

  socket.on('battle:stop', () => {
    console.log('[arena] stop requested')
    stopBattle('stopped by observer')
  })

  socket.on('disconnect', () => {
    console.log(`[arena] observer disconnected: ${socket.id}`)
  })

  socket.on('error', (err) => {
    console.error(`[arena] socket error (${socket.id}):`, err)
  })
})

httpServer.on('error', (err: any) => {
  if (err?.code === 'EADDRINUSE') console.log('[arena] port already in use (hot-reload) — keeping previous listener')
  else console.error('[arena] http server error:', err?.message ?? err)
})
if (!(globalThis as any).__arenaListening) {
  ;(globalThis as any).__arenaListening = true
  httpServer.listen(PORT, () => {
    console.log(`[arena] service listening on port ${PORT}`)
  })
}

// ---------------------------------------------------------------------------
// DEV-SERVER SUPERVISOR — keep the Next.js app (port 3000) alive forever.
// Every Bash-tool invocation kills its child processes, so the dev server
// must be spawned by THIS long-lived service. Health check every 10s,
// restart backoff 15s..120s, SIGKILL if stuck >240s.
//
// Task 36 (preview panel died mid-battle): the heavy arena page made webpack
// dev balloon next-server to ~2.9GB RSS on this 4GB box → kernel OOM-killer
// killed it while the user was watching a live match. Mitigations:
//   1. old-space cap 768MB (spawn env) + experimental.webpackMemoryOptimizations
//      (next.config.ts) to shrink the compile footprint
//   2. detached process-group spawn → whole-tree SIGKILL (port 3000 is never
//      orphaned by a surviving bash/node when the wrapper dies)
//   3. RSS watchdog: when next-server >2.4GB for >120s AND no battle is
//      streaming, restart it proactively so the kernel never has to kill it
//      mid-battle. (120s grace = never fire during the initial compile peak;
//      steady state with webpackMemoryOptimizations + 768MB cap ≈ 1.4GB.)
// ---------------------------------------------------------------------------
const RSS_LIMIT_MB = 2400
const RSS_GRACE_MS = 120_000

type DevSup = { timer?: any; child?: any; restarts: number; lastStart: number; busy: boolean }
const g = globalThis as any
const gSup: DevSup = g.__devSup ?? { restarts: 0, lastStart: 0, busy: false }
g.__devSup = gSup

function killDevTree() {
  const c = gSup.child
  if (!c) return
  try {
    process.kill(-c.pid, 'SIGKILL') // negative pid → whole process group
  } catch {}
  try {
    c.kill('SIGKILL')
  } catch {}
  gSup.child = null
}

function spawnDev() {
  const out = openSync('/tmp/nextdev.log', 'a')
  // detached: true → bun becomes a process-group leader, so kill(-pid) later
  // reaps the whole tree (bash + node + next-server) together.
  gSup.child = spawn('bun', ['run', 'dev'], {
    cwd: '/home/z/my-project',
    env: { ...process.env, NODE_OPTIONS: '--max-old-space-size=768' },
    stdio: ['ignore', out, out],
    detached: true,
  })
  gSup.lastStart = Date.now()
  gSup.busy = false
  console.log(`[supervisor] spawned dev server pid ${gSup.child.pid} (restart #${gSup.restarts})`)
  gSup.child.on('exit', (code: any) => {
    if (gSup.child && Date.now() - gSup.lastStart > 5 * 60 * 1000) gSup.restarts = 0
    console.log(`[supervisor] dev server exited code=${code}`)
  })
}

/** RSS (MB) of the next-server process inside OUR dev tree (0 = none). */
function nextServerRssMb(): number {
  const root = gSup.child?.pid
  if (!root) return 0
  let rss = 0
  let dirs: string[]
  try {
    dirs = readdirSync('/proc')
  } catch {
    return 0
  }
  for (const dir of dirs) {
    const c0 = dir.charCodeAt(0)
    if (c0 < 48 || c0 > 57) continue // not a pid dir
    try {
      const st = readFileSync(`/proc/${dir}/status`, 'utf8')
      if (!/^Name:\s+next-server/m.test(st)) continue
      // walk the PPid chain up to our wrapper (guard against cycles)
      let cur = Number(dir)
      let ok = false
      let guard = 0
      while (cur > 1 && guard++ < 12) {
        if (cur === root) {
          ok = true
          break
        }
        const s2 = readFileSync(`/proc/${cur}/status`, 'utf8')
        cur = Number(s2.match(/^PPid:\s+(\d+)/m)?.[1] ?? '0')
      }
      if (ok) rss = Math.max(rss, Number(st.match(/VmRSS:\s+(\d+)/)?.[1] ?? 0))
    } catch {}
  }
  return Math.round(rss / 1024)
}

async function checkOnce() {
  if (gSup.busy) return
  try {
    const res = await fetch('http://127.0.0.1:3000/', { signal: AbortSignal.timeout(8000) })
    if (!res.ok) throw new Error(`status ${res.status}`)
    // healthy — RSS watchdog (skip while a battle is streaming: restarting the
    // dev server mid-match would blank the live view; retry next 10s tick)
    const rss = nextServerRssMb()
    const pastGrace = gSup.child && Date.now() - gSup.lastStart > RSS_GRACE_MS
    if (rss > RSS_LIMIT_MB && !proc && pastGrace) {
      gSup.restarts += 1
      const wait = Math.min(15 * gSup.restarts, 120)
      console.log(
        `[supervisor] next-server rss=${rss}MB > ${RSS_LIMIT_MB}MB (idle) — proactive restart in ${wait}s`,
      )
      gSup.busy = true
      setTimeout(() => {
        killDevTree()
        spawnDev()
      }, wait * 1000)
      return
    }
    if (rss > 1500) console.log(`[supervisor] next-server rss=${rss}MB (limit ${RSS_LIMIT_MB})`)
    gSup.restarts = 0
    return
  } catch (e: any) {
    // 2026-09-11 fix: during the first 240s after spawn the Next.js dev
    // server ACCEPTS then CLOSES sockets while compiling the first page —
    // bun's fetch raises "socket connection was closed unexpectedly" (NOT
    // a TimeoutError), which the old code treated as DOWN → kill → respawn
    // → EADDRINUSE → exit-0 loop that never recovered. Tolerate ANY
    // connection error inside the 240s startup grace window; only a
    // >240s failure (or timeout beyond grace) triggers a restart.
    const grace = gSup.child && Date.now() - gSup.lastStart <= 240_000
    if (grace) {
      return // still compiling/starting — wait
    }
    if (String(e?.name) === 'TimeoutError') {
      console.log('[supervisor] dev server stuck >240s — SIGKILL + restart')
      killDevTree()
    }
    gSup.busy = true
    gSup.restarts += 1
    const wait = Math.min(15 * gSup.restarts, 120)
    console.log(`[supervisor] dev server DOWN (${e?.message ?? e}) — restart in ${wait}s`)
    setTimeout(() => {
      killDevTree()
      spawnDev()
    }, wait * 1000)
  }
}

if (!g.__devSupStarted) {
  ;(globalThis as any).__devSupStarted = true
  setTimeout(spawnDev, 1500)
  gSup.timer = setInterval(checkOnce, 10_000)
}

process.on('SIGTERM', () => {
  stopBattle('sigterm')
  httpServer.close(() => process.exit(0))
})
process.on('SIGINT', () => {
  stopBattle('sigint')
  httpServer.close(() => process.exit(0))
})

// touch-reload Task 30: registry v1/v2/v3 cleanup
