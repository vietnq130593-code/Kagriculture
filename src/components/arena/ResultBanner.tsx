'use client'

/**
 * ARENA OBSERVER UI — final result banner (battle:end).
 */
import { motion } from 'framer-motion'
import { Trophy, Clock3, Swords, Handshake } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { BattleInfo, BattleResult } from './types'
import { fmtMoney } from './helpers'
import { cn } from '@/lib/utils'

export function ResultBanner({
  result,
  battleInfo,
}: {
  result: BattleResult
  battleInfo: BattleInfo | null
}) {
  const [rA, rB] = result.rewards
  const winner = result.winner
  const ratio = rA > 0 && rB > 0 ? (Math.max(rA, rB) / Math.min(rA, rB)).toFixed(2) : '∞'

  const isDraw = winner === -1
  const winnerName = winner === 0 ? battleInfo?.a : winner === 1 ? battleInfo?.b : null
  const winAccent =
    winner === 0
      ? 'border-emerald-400 bg-emerald-50'
      : winner === 1
        ? 'border-rose-400 bg-rose-50'
        : 'border-amber-400 bg-amber-50'

  return (
    <motion.div
      initial={{ opacity: 0, y: -12, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: 'spring', stiffness: 260, damping: 22 }}
    >
      <Card className={cn('border-2 shadow-md', winAccent)}>
        <CardContent className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center">
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: [0, -8, 8, 0] }}
              transition={{ duration: 0.8, repeat: Infinity, repeatDelay: 2.2 }}
              className="flex size-12 shrink-0 items-center justify-center rounded-full bg-white shadow-sm"
            >
              {isDraw ? (
                <Handshake className="size-6 text-amber-600" aria-hidden="true" />
              ) : (
                <Trophy
                  className={cn('size-6', winner === 0 ? 'text-emerald-600' : 'text-rose-600')}
                  aria-hidden="true"
                />
              )}
            </motion.div>
            <div>
              <div className="text-base font-bold tracking-tight text-stone-900">
                {isDraw ? '🤝 Hòa tuyệt đối!' : `🏆 ${winnerName} THẮNG!`}
              </div>
              <div className="text-xs text-stone-600">
                {battleInfo ? `${battleInfo.a} vs ${battleInfo.b}` : 'Trận đấu'} ·{' '}
                {isDraw ? 'chênh lệch dưới ngưỡng' : `tỷ lệ ${ratio}×`}
              </div>
            </div>
          </div>

          <div className="flex flex-1 flex-wrap items-center gap-2 sm:justify-end">
            <Badge className="gap-1.5 border-emerald-300 bg-emerald-100 px-3 py-1.5 text-emerald-900 tabular-nums hover:bg-emerald-100">
              <span className="opacity-70">{battleInfo?.a ?? 'A'}</span>
              <span className="font-bold">{fmtMoney(rA)}</span>
            </Badge>
            <Swords className="size-4 text-stone-400" aria-hidden="true" />
            <Badge className="gap-1.5 border-rose-300 bg-rose-100 px-3 py-1.5 text-rose-900 tabular-nums hover:bg-rose-100">
              <span className="opacity-70">{battleInfo?.b ?? 'B'}</span>
              <span className="font-bold">{fmtMoney(rB)}</span>
            </Badge>
            <Badge
              variant="outline"
              className="gap-1 border-stone-300 bg-white px-3 py-1.5 text-stone-600 tabular-nums"
            >
              <Clock3 className="size-3.5" aria-hidden="true" />
              {result.wallS.toFixed(1)}s · {result.turns} lượt
            </Badge>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
