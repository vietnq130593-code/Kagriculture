// Task 36-d: end-to-end battle probe through the gateway, exactly like the
// browser does. Streams a full kain40 vs v6 battle and reports counts.
import { io } from 'socket.io-client'

const socket = io('http://127.0.0.1:81/?XTransformPort=3005', {
  transports: ['websocket', 'polling'],
  forceNew: true,
  reconnection: false,
  timeout: 15000,
})

let turnBatches = 0
let turnRecords = 0
let t0 = 0

socket.on('connect', () => {
  console.log(`[probe] connected id=${socket.id}`)
  t0 = Date.now()
  socket.emit('battle:start', { a: 'kain40', b: 'v6', seed: 404 })
})
socket.on('arena:hello', (d) => console.log(`[probe] arena:hello agents=${d.agents?.length}`))
socket.on('battle:hello', (d) => console.log(`[probe] battle:hello ${d.a} vs ${d.b} seed=${d.seed}`))
socket.on('battle:meta', () => {})
socket.on('battle:turns', (d) => {
  turnBatches++
  turnRecords += d.turns?.length ?? 0
})
socket.on('battle:end', (d) => {
  console.log(`[probe] battle:end winner=${d.winner} rewards=[${d.rewards}] wallS=${d.wallS} turns=${d.turns}`)
})
socket.on('battle:status', (d) => { if (d.reason) console.log(`[probe] status: ${d.reason}`) })
socket.on('battle:error', (d) => console.log(`[probe] ERROR: ${d.message}`))
socket.on('disconnect', (r) => console.log(`[probe] disconnected: ${r}`))

setTimeout(() => {
  console.log(`[probe] 60s summary: batches=${turnBatches} turnRecords=${turnRecords} elapsed=${((Date.now() - t0) / 1000).toFixed(1)}s`)
  socket.disconnect()
  process.exit(0)
}, 60_000)
