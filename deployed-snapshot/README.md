# KaggressurE Arena — Deployed Snapshot

Source: https://q1nwx7kyrqx1-d.space-z.ai/ (fetched 2026-09-16 17:59 UTC)

## Contents
- index.html — rendered homepage (SSR shell)
- chunks/ — 9 compiled Next.js client chunks (~1.4 MB)
- app.css — compiled Tailwind CSS (~129 KB)
- logo.svg — site logo
- api-data.json — live data pulled via socket.io (XTransformPort=3030): agents=[] battles=[] (server currently empty)
- fetch-deployed-data.mjs — script to re-pull live data (bun deployed-snapshot/fetch-deployed-data.mjs)

## Socket API discovered
- emit: agents:list {} / history:get {limit} / battle:run
- on: agents:data / history:data / battle:progress / battle:log / battle:timeline / battle:result / battle:error

## Notes
- No source maps (404) → original source code NOT recoverable from deployment
- Backend mini-service (port 3030 via gateway) is ONLINE but has 0 agents, 0 battles
