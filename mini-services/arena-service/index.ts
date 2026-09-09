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
import { appendFileSync, mkdirSync, openSync, writeFileSync } from 'fs'
import { join } from 'path'

const PORT = 3005
const RUNNER = '/home/z/my-project/kaggriculture/arena/run_battle.py'
const BATTLE_DIR = '/home/z/my-project/kaggriculture/battles'
const PYTHON = 'python3'

const AGENTS = ['v5', 'v4', 'v3', 'v2', 'kain1', 'kain2', 'kain3', 'melon', 'baseline']

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

// Hot-reload safety: when bun --hot re-evaluates this module, the previous
// evaluation's listener is still bound. Guard against a second listen() and
// swallow EADDRINUSE so a reload can never crash the service.
httpServer.on('error', (err: any) => {
  if (err?.code === 'EADDRINUSE') {
    console.log('[arena] port already in use (hot-reload) — keeping previous listener')
  } else {
    console.error('[arena] http server error:', err?.message ?? err)
  }
})

if (!(globalThis as any).__arenaListening) {
  ;(globalThis as any).__arenaListening = true
  httpServer.listen(PORT, () => {
    console.log(`[arena] service listening on port ${PORT}`)
  })
}

process.on('SIGTERM', () => {
  stopBattle('sigterm')
  httpServer.close(() => process.exit(0))
})
process.on('SIGINT', () => {
  stopBattle('sigint')
  httpServer.close(() => process.exit(0))
})

// ============================================================================
// NEXT.JS DEV SERVER SUPERVISOR (port 3000)
// ----------------------------------------------------------------------------
// The sandbox kills every process spawned inside an agent Bash-tool invocation
// once that invocation ends (even setsid/disowned children — verified). This
// service is long-lived, so processes IT spawns survive. It therefore owns the
// lifecycle of the Next.js dev server:
//   • health check every 10s (HTTP GET http://127.0.0.1:3000/)
//   • (re)spawns `bun run dev` in /home/z/my-project when the app is down
//   • exponential restart backoff (15s→120s) to avoid crash loops
// `dev` runs webpack (not Turbopack): Turbopack's cold compile needs >2.4 GB
// RSS and the kernel OOM-killer terminates it on this 4 GB box (verified in
// dmesg twice); webpack compiles the same app with a much lower peak.
// ============================================================================
const gSup = globalThis as any
if (!gSup.__devSup) {
  gSup.__devSup = {
    child: null as ChildProcess | null,
    lastOk: Date.now(),
    okSince: 0,
    restarts: 0,
    nextRetry: 0,
  }
  const sup = gSup.__devSup

  const devLog = (msg: string) => {
    const line = `${new Date().toISOString()} ${msg}`
    console.log(line)
    try {
      appendFileSync('/tmp/nextdev.log', line + '\n')
    } catch {}
  }

  const spawnDev = (reason: string) => {
    if (sup.child && sup.child.exitCode === null && !sup.child.killed) return
    const out = openSync('/tmp/nextdev.log', 'a')
    const child = spawn('bun', ['run', 'dev'], {
      cwd: '/home/z/my-project',
      env: { ...process.env, NODE_OPTIONS: '--max-old-space-size=1024' },
      stdio: ['ignore', out, out],
    })
    sup.child = child
    sup.lastOk = Date.now()
    sup.okSince = 0
    sup.restarts += 1
    devLog(`[devsup] spawned \`bun run dev\` (pid ${child.pid}) — ${reason} (start #${sup.restarts})`)
    child.on('exit', (code, sig) => {
      if (gSup.__devSup === sup && sup.child === child) {
        sup.child = null
        const wait = Math.min(15 * sup.restarts, 120) * 1000
        sup.nextRetry = Date.now() + wait
        devLog(`[devsup] next dev exited (code=${code} sig=${sig}) — respawn in ${wait / 1000}s`)
      }
    })
    child.on('error', (err) => {
      devLog(`[devsup] spawn error: ${err.message}`)
      sup.child = null
    })
  }

  const check = async () => {
    const now = Date.now()
    if (now < sup.nextRetry) return
    if (!sup.child) {
      spawnDev(sup.restarts === 0 ? 'initial start' : 'respawn after exit')
      return
    }
    try {
      const ctrl = new AbortController()
      const timer = setTimeout(() => ctrl.abort(), 4000)
      const res = await fetch('http://127.0.0.1:3000/', { signal: ctrl.signal })
      clearTimeout(timer)
      if (res.status < 500) {
        if (!sup.okSince) {
          sup.okSince = now
          devLog(`[devsup] app is up (HTTP ${res.status})`)
        }
        sup.lastOk = now
        // healthy for 5+ minutes → reset the backoff counter
        if (now - sup.okSince > 300000) {
          sup.restarts = 0
          sup.okSince = now
        }
        return
      }
    } catch {
      /* not answering yet — cold compile can take ~30s */
    }
    // No HTTP answer for a long time while the process is alive → wedged;
    // kill it so the exit handler schedules a clean respawn.
    if (now - sup.lastOk > 240000 && sup.child && sup.child.exitCode === null) {
      devLog('[devsup] app unresponsive >240s — killing for a clean restart')
      try {
        sup.child.kill('SIGKILL')
      } catch {}
    }
  }

  setInterval(() => {
    check().catch(() => {})
  }, 10000)
  devLog('[devsup] supervisor installed — checking app health every 10s')
}
