import { io } from 'socket.io-client'
const socket = io('http://127.0.0.1:81/?XTransformPort=3005', {
  transports: ['websocket', 'polling'], forceNew: true, reconnection: false, timeout: 15000,
})
socket.on('connect', () => console.log('[hello] connected'))
socket.on('arena:hello', (d) => { console.log('[hello] agents:', JSON.stringify(d.agents)); socket.disconnect(); process.exit(0) })
socket.on('connect_error', (e) => { console.log('[hello] CONNECT_ERROR:', e.message); process.exit(1) })
setTimeout(() => { console.log('[hello] TIMEOUT'); process.exit(1) }, 15_000)
