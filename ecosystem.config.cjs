/**
 * KAGGRICULTURE ARENA — PM2 ecosystem (deploy 2026-09-18).
 *
 * User request: "Dùng PM2 duy trì hiển thị giao diện app" — PM2 keeps the
 * app UI alive. Two supervised processes:
 *
 *   1. kagriculture-web    — Next.js Observer UI, port 3000 (the only
 *                             user-visible route, served through the Caddy
 *                             gateway on :81). Auto-restart on crash +
 *                             hard memory ceiling (the 4GB box OOM-killed
 *                             next-server historically at ~2.9GB RSS).
 *   2. kagriculture-arena  — socket.io battle orchestrator, port 3005
 *                             (streams 720-turn battles to the UI). Runs
 *                             `bun --hot`; registry changes in index.ts
 *                             still need `pm2 restart kagriculture-arena`
 *                             (Task-86 lesson: --hot keeps old closures).
 *
 * Start:    pm2 start ecosystem.config.cjs
 * Status:   pm2 status
 * Logs:     pm2 logs            (or ~/.pm2/logs/)
 * Stop:     pm2 stop all
 * Delete:   pm2 delete all
 * Persist:  pm2 save            (resurrect later with `pm2 resurrect`)
 */
const venvBin = '/home/z/.venv/bin'

module.exports = {
  apps: [
    {
      name: 'kagriculture-web',
      script: 'bun',
      args: 'run dev',
      cwd: '/home/z/my-project',
      // 4GB box: steady state ≈1.4GB with webpackMemoryOptimizations +
      // devtool:false + 768MB old-space cap; hard-kill at 2GB so the kernel
      // OOM-killer never gets a chance to blank the live preview mid-battle.
      max_memory_restart: '2000M',
      autorestart: true,
      restart_delay: 3000,
      kill_timeout: 8000,
      time: true,
      merge_logs: true,
      out_file: '/home/z/.pm2/logs/kagriculture-web-out.log',
      error_file: '/home/z/.pm2/logs/kagriculture-web-error.log',
    },
    {
      name: 'kagriculture-arena',
      script: 'bun',
      args: '--hot index.ts',
      cwd: '/home/z/my-project/mini-services/arena-service',
      // venv python3 (kaggle-environments 1.32.7) must be the one spawned for
      // battles: python3 -> /home/z/.venv/bin/python3.
      env: {
        PATH: `${venvBin}:/usr/local/bin:/usr/bin:/bin`,
      },
      max_memory_restart: '600M',
      autorestart: true,
      restart_delay: 2000,
      kill_timeout: 5000,
      time: true,
      merge_logs: true,
      out_file: '/home/z/.pm2/logs/kagriculture-arena-out.log',
      error_file: '/home/z/.pm2/logs/kagriculture-arena-error.log',
    },
  ],
}
