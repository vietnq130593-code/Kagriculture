/**
 * ARENA OBSERVER UI — game constants for rendering.
 * Prices / products / animals mirror the kaggle-environments kaggriculture engine.
 */

export interface ProductDef {
  name: string
  base: number
  /** warm earth palette — no indigo, no blue */
  color: string
  bg: string
  icon: string
}

export const PRODUCTS: ProductDef[] = [
  { name: 'WHEAT', base: 25, color: '#b45309', bg: 'bg-amber-100 text-amber-800 border-amber-200', icon: '🌾' },
  { name: 'CARROT', base: 35, color: '#c2410c', bg: 'bg-orange-100 text-orange-800 border-orange-200', icon: '🥕' },
  { name: 'TOMATO', base: 60, color: '#b91c1c', bg: 'bg-red-100 text-red-800 border-red-200', icon: '🍅' },
  { name: 'STRAWBERRY', base: 120, color: '#be123c', bg: 'bg-rose-100 text-rose-800 border-rose-200', icon: '🍓' },
  { name: 'MELON', base: 250, color: '#15803d', bg: 'bg-green-100 text-green-800 border-green-200', icon: '🍈' },
  { name: 'EGG', base: 50, color: '#a16207', bg: 'bg-yellow-100 text-yellow-800 border-yellow-200', icon: '🥚' },
  { name: 'MILK', base: 160, color: '#57534e', bg: 'bg-stone-200 text-stone-800 border-stone-300', icon: '🥛' },
  { name: 'WOOL', base: 200, color: '#78716c', bg: 'bg-stone-100 text-stone-700 border-stone-300', icon: '🧶' },
  { name: 'FERTILIZER', base: 100, color: '#4d7c0f', bg: 'bg-lime-100 text-lime-800 border-lime-300', icon: '🧪' },
]

export const PRODUCT_MAP: Record<string, ProductDef> = Object.fromEntries(
  PRODUCTS.map((p) => [p.name, p]),
)

export const CROPS = ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON'] as const

/** 1–2 letter tile code per crop */
export const CROP_CODE: Record<string, string> = {
  WHEAT: 'W',
  CARROT: 'C',
  TOMATO: 'T',
  STRAWBERRY: 'S',
  MELON: 'M',
}

export const CROP_COLOR: Record<string, string> = {
  WHEAT: '#d97706',
  CARROT: '#ea580c',
  TOMATO: '#dc2626',
  STRAWBERRY: '#e11d48',
  MELON: '#16a34a',
}

export const ANIMAL_INFO: Record<string, { icon: string; product: string; vn: string }> = {
  GOOSE: { icon: '🦢', product: 'EGG', vn: 'Ngỗng' },
  COW: { icon: '🐄', product: 'MILK', vn: 'Bò' },
  SHEEP: { icon: '🐑', product: 'WOOL', vn: 'Cừu' },
}

export const ANIMAL_INFO_LIST = [
  { name: 'GOOSE', ...ANIMAL_INFO.GOOSE },
  { name: 'COW', ...ANIMAL_INFO.COW },
  { name: 'SHEEP', ...ANIMAL_INFO.SHEEP },
]

export const STARTING_MONEY = 3000
export const BOARD_SIZE = 10
export const TOTAL_STEPS = 719 // steps 0..718
export const SHED_CAPACITY = 100
export const QUADRANTS = ['NW', 'NE', 'SW', 'SE'] as const

/** Seat accent tokens — A = emerald, B = rose */
export const SEAT = [
  {
    key: 'A',
    accent: 'emerald',
    text: 'text-emerald-700',
    border: 'border-t-emerald-500',
    chipBg: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    solid: 'bg-emerald-600',
    soft: 'bg-emerald-50',
    line: '#059669',
    ring: 'ring-emerald-400',
  },
  {
    key: 'B',
    accent: 'rose',
    text: 'text-rose-700',
    border: 'border-t-rose-500',
    chipBg: 'bg-rose-100 text-rose-800 border-rose-300',
    solid: 'bg-rose-600',
    soft: 'bg-rose-50',
    line: '#e11d48',
    ring: 'ring-rose-400',
  },
] as const

export interface AgentDesc {
  name: string
  desc: string
  tag: string
}

export const AGENT_INFO: AgentDesc[] = [
  { name: 'v6', desc: 'ORCHESTRATOR-K · 93.75% vs v5, 100% vs v4/v3', tag: 'nhà vô địch' },
  { name: 'kain33', desc: 'KAIN 4-Laws — 3 luật đất cứng top-Kaggle + plan-cache fix', tag: 'KAIN' },
  { name: 'kain32', desc: 'KAIN Land-Lab — luật 85% utilization (nghiên cứu)', tag: 'KAIN' },
  { name: 'kain31', desc: 'KAIN Solver-2 — 55/100 vs v6, phá tường R104', tag: 'KAIN' },
  { name: 'kain30', desc: 'KAIN Solver-1 — kernel P3 giá-trị-biên + Egg Fortress', tag: 'KAIN' },
  { name: 'kain25', desc: 'KAIN thách đấu v6 — Geese Fortress 75 đất', tag: 'KAIN' },
  { name: 'kain16', desc: 'Đối thủ KAIN — 24 biến thể, tường 94%', tag: 'KAIN' },
  { name: 'v5', desc: 'Não 6 lớp Bayes (97% vs v4)', tag: 'đối thủ chuẩn' },
  { name: 'v4', desc: 'Orchestrator + 8 edges (97% bị v5 áp đảo)', tag: 'bản cũ' },
  { name: 'melon', desc: 'Bot đơn giản — dưa hấu chậm', tag: 'bot đơn giản' },
]

export const SPEED_OPTIONS: { value: number; label: string }[] = [
  { value: 1, label: '1× — chậm' },
  { value: 2, label: '2×' },
  { value: 4, label: '4×' },
  { value: 8, label: '8×' },
  { value: 16, label: '16×' },
  { value: 32, label: '32×' },
  { value: 50, label: '50× — nhanh' },
]

export const LIVE_SPEED = 'live'
