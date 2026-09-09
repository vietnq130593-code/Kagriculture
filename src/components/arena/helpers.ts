/**
 * ARENA OBSERVER UI — formatting + Vietnamese action annotation helpers.
 */
import type { ActionSet, Farm, TurnRecord } from './types'
import { ANIMAL_INFO } from './constants'

/** "$12.345" — vi-VN thousand separators (dots) */
export function fmtMoney(n: number | null | undefined): string {
  if (n === null || n === undefined || Number.isNaN(n)) return '—'
  return '$' + Math.round(n).toLocaleString('vi-VN')
}

export function fmtCompact(n: number): string {
  if (Math.abs(n) >= 1000) {
    const k = n / 1000
    return (k >= 10 ? Math.round(k) : Math.round(k * 10) / 10).toString().replace('.', ',') + 'k'
  }
  return Math.round(n).toLocaleString('vi-VN')
}

export function fmtSigned(n: number): string {
  if (n === 0) return '±0'
  return (n > 0 ? '+' : '') + n.toLocaleString('vi-VN')
}

const DIR_VN: Record<string, string> = {
  NORTH: 'Bắc',
  SOUTH: 'Nam',
  EAST: 'Đông',
  WEST: 'Tây',
}

const ANIMAL_ICON: Record<string, string> = {
  GOOSE: '🦢',
  COW: '🐄',
  SHEEP: '🐑',
}

/** farmer / hand action → readable Vietnamese string with emoji */
export function annotateUnit(action: any[] | null | undefined): string {
  if (!action || !Array.isArray(action) || action.length === 0) return '—'
  const op = action[0]
  const arg = action[1]
  const qty = action.length >= 3 ? action[2] : 1
  switch (op) {
    case 'MOVE':
      return `🚶 Đi ${DIR_VN[arg] ?? arg}`
    case 'PLANT':
      return `🌱 Trồng ${arg}`
    case 'WATER':
      return '💧 Tưới nước'
    case 'HARVEST':
      return '🧺 Thu hoạch'
    case 'PASS':
      return '💤 Nghỉ'
    case 'FEED':
      return '🌾 Cho ăn'
    case 'CARE':
      return '❤️ Chăm sóc'
    case 'PLACE':
      return `${ANIMAL_ICON[arg] ?? '📦'} Đặt ${arg}${qty > 1 ? ` ×${qty}` : ''}`
    case 'PICKUP':
      return `🎒 Lấy ${arg}${qty > 1 ? ` ×${qty}` : ''}`
    case 'DROP':
      return '📥 Trả về kho'
    case 'DIG':
      return '⛏ Đào bật'
    case 'FERTILIZE':
      return '✨ Bón phân'
    case 'BUILD_COOP':
      return '🏠 Xây chuồng (coop)'
    case 'BUILD_PASTURE':
      return '🚧 Xây đồng cỏ'
    case 'COLLECT_FERTILIZER':
      return '💩 Thu phân'
    default:
      return `⚙ ${op}${arg !== undefined ? ` ${arg}` : ''}`
  }
}

/** market order → readable Vietnamese string with emoji */
export function annotateMarketOrder(order: any[] | null | undefined): string {
  if (!order || !Array.isArray(order) || order.length === 0) return '—'
  const op = order[0]
  const item = order[1]
  const qty = order.length >= 3 ? order[2] : 1
  switch (op) {
    case 'BUY_SEED':
      return `🛒 Mua hạt ${item} ×${qty}`
    case 'BUY_PRODUCT':
      return `🛒 Mua ${item} ×${qty}`
    case 'SELL':
      return `💰 Bán ${item} ×${qty}`
    case 'BUY_ANIMAL':
      return `${ANIMAL_ICON[item] ?? '🛒'} Mua ${item} ×${qty}`
    case 'HIRE':
      return '👷 Thuê thợ'
    case 'BUY_LAND':
      return '🗺 Mua đất'
    default:
      return `⚙ ${op}${item !== undefined ? ` ${item}` : ''}`
  }
}

/** one compact string of all market orders for a seat */
export function annotateMarket(orders: any[] | null | undefined): string {
  if (!orders || !Array.isArray(orders) || orders.length === 0) return '—'
  return orders.map((o) => annotateMarketOrder(o)).join(' · ')
}

/** compact per-seat action summary for the recent-turns log */
export function compactSeatSummary(act: ActionSet | null | undefined): string {
  if (!act) return '—'
  const parts: string[] = []
  const f = act.farmer
  if (Array.isArray(f) && f.length > 0 && f[0] !== 'PASS') {
    const op = f[0]
    const short: Record<string, string> = {
      MOVE: '🚶',
      PLANT: `🌱${f[1] ?? ''}`,
      WATER: '💧',
      HARVEST: '🧺',
      FEED: '🌾',
      CARE: '❤️',
      PLACE: '📦',
      PICKUP: '🎒',
      DROP: '📥',
      DIG: '⛏',
      FERTILIZE: '✨',
      BUILD_COOP: '🏠',
      BUILD_PASTURE: '🚧',
      COLLECT_FERTILIZER: '💩',
    }
    parts.push(short[op] ?? op)
  }
  const hands = (act.hands ?? []).filter(
    (h) => Array.isArray(h) && h.length > 0 && h[0] !== 'PASS',
  )
  const handSummary = hands
    .map((h) => {
      const op = h[0]
      const short: Record<string, string> = {
        WATER: '💧',
        HARVEST: '🧺',
        FEED: '🌾',
        CARE: '❤️',
        PLACE: '📦',
        PICKUP: '🎒',
        DROP: '📥',
        PLANT: '🌱',
        MOVE: '🚶',
        DIG: '⛏',
      }
      return short[op] ?? op
    })
    .join('')
  if (handSummary) parts.push(`${hands.length}👤${handSummary}`)
  const mk = (act.market ?? []).map((o) => {
    const op = o?.[0]
    const item = o?.[1]
    const qty = o?.length >= 3 ? o[2] : 1
    if (op === 'SELL') return `💰${item}×${qty}`
    if (op === 'BUY_SEED') return `🛒hạt ${item}×${qty}`
    if (op === 'BUY_PRODUCT') return `🛒${item}×${qty}`
    if (op === 'BUY_ANIMAL') return `${ANIMAL_INFO[item]?.icon ?? '🐾'}${item}×${qty}`
    if (op === 'HIRE') return '👷'
    if (op === 'BUY_LAND') return '🗺'
    return op ?? ''
  })
  if (mk.length) parts.push(mk.join(' '))
  if (parts.length === 0) return '💤'
  return parts.join(' · ')
}

export interface TurnSummary {
  step: number
  day: number
  hour: number
  a: string
  b: string
}

export function summarizeTurn(turn: TurnRecord): TurnSummary {
  return {
    step: turn.step,
    day: turn.day,
    hour: turn.hour,
    a: compactSeatSummary(turn.acts?.[0]),
    b: compactSeatSummary(turn.acts?.[1]),
  }
}

export function tileKindOf(tile: any): 'EMPTY' | 'LOCKED' | 'WEED' | 'PLANT' | 'STRUCTURE' {
  if (tile === null || tile === undefined) return 'EMPTY'
  if (tile === 'LOCKED') return 'LOCKED'
  if (tile.kind === 'WEED') return 'WEED'
  if (tile.kind === 'PLANT') return 'PLANT'
  if (tile.kind === 'COOP' || tile.kind === 'PASTURE') return 'STRUCTURE'
  return 'EMPTY'
}

export function emptyFarm(): Farm {
  return {
    money: 0,
    tiles: Array.from({ length: 10 }, () => Array.from({ length: 10 }, () => null as null)),
    farmer: [0, 0] as [number, number],
    hands: [],
    unlocked_quadrants: [],
    hires_today: 0,
  }
}

export function shopLabel(name: string): string {
  return name.replace(/_/g, ' ')
}
