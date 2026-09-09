/**
 * ARENA OBSERVER UI — shared types.
 * Mirrors the TurnRecord JSONL emitted by kaggriculture/arena/run_battle.py
 * and streamed by mini-services/arena-service (port 3005) over socket.io.
 */

export interface Plant {
  kind: 'PLANT'
  crop: 'WHEAT' | 'CARROT' | 'TOMATO' | 'STRAWBERRY' | 'MELON'
  planted_day: number
  watered_today: boolean
  consecutive_unwatered: number
  yield_units: number
  max_lifespan_step: number
  fertilized_until_day: number
}

export interface Weed {
  kind: 'WEED'
}

export interface Structure {
  kind: 'COOP' | 'PASTURE'
  animal: 'GOOSE' | 'COW' | 'SHEEP' | null
  placed_day: number
  yield_units: number
  fed_today: boolean
  consecutive_unfed: number
  cared_today: boolean
  fertilizer_available: boolean
  pending_care_bonus: number
}

export type Tile = null | 'LOCKED' | Plant | Weed | Structure

export interface Farm {
  money: number
  tiles: Tile[][]
  farmer: [number, number]
  hands: [number, number][]
  unlocked_quadrants: string[]
  hires_today: number
}

export interface Market {
  inventory: Record<string, number>
  prices: Record<string, number>
}

export interface Private {
  shed: Record<string, number>
  seeds: Record<string, number>
  /** inventories[0] = farmer bag; [1..n] = hired hands (dicts product -> count) */
  inventories: Record<string, number>[]
}

export interface ActionSet {
  farmer: any[]
  hands: any[][]
  market: any[]
}

export interface TurnRecord {
  t: 'turn'
  step: number
  day: number
  hour: number
  farms: Farm[]
  market: Market
  town: { unlocked_shops: string[] }
  priv: (Private | null)[]
  acts: (ActionSet | null)[]
  diag: Record<string, any>[]
  times: [number, number]
}

export interface BattleInfo {
  a: string
  b: string
  seed: number | null
  episodeSteps: number
  startedAt: number
}

export interface BattleResult {
  rewards: number[]
  winner: 0 | 1 | -1
  wallS: number
  turns: number
}

export type Seat = 0 | 1
