import { io } from 'socket.io-client'
const socket = io('http://127.0.0.1:3005', {
  transports: ['websocket', 'polling'], forceNew: true, reconnection: false, timeout: 15000,
})
socket.on('connect', () => console.log('[direct] connected'))
socket.on('arena:hello', (d) => { console.log('[direct] agents:', JSON.stringify(d.agents)); socket.disconnect(); process.exit(0) })
socket.on('connect_error', (e) => { console.log('[direct] CONNECT_ERROR:', e.message); process.exit(1) })
setTimeout(() => { console.log('[direct] TIMEOUT'); process.exit(1) }, 15_000)
