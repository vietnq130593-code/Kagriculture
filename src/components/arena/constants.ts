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
  { name: 'v14', desc: 'ARI CLASS (Task 69) — nền kme3v10 + 6 tầng tuning v13 + stack mới đo lường: FRONT-RUN (bán trước lịch dump premium của đối thủ mirror — route/tape dự đoán từ shop public), HORIZON 8 (đua pre-sell sâu hơn H=6 của v13), ROOM-GUARD + CLAMP-SELLS (2 layer chassis bật lại) · 80/80 thắng tuyệt đối: v13 32/32 (+$4.95k), kme3 16/16 (+$5.65k), kme3v10 16/16 (+$4.52k), aurax 16/16 (+$4.53k) · tools: battery.py + gap_waterfall.py + force_route.py', tag: 'nhà vô địch' },
  { name: 'v13', desc: 'KME3-TUNED v4 DUAL-OPPONENT — lõi H=6/LO=144/HI=712, prefire h21+h22, V231-flip điều kiện, V224 sales-first, R37 reorder mở từ step 144, melon-seller mọi giờ · 48/48 thắng kme3, 8/8 kme3v10/aurax · bị v14 vượt 32/32 (chi tiết §11.23-24)', tag: 'cựu vô địch' },
  { name: 'kme3', desc: 'MASTER ENGINE V3 (guruprasaathas111, Kaggle public, Apache 2.0) — route-tape 719-turn + 20 lớp overlay, Public Score 600 · tự đấu hòa tuyệt đối · bị v14 vượt 16/16 +$5.6k (chi tiết §11.21-24)', tag: 'đối thủ chuẩn' },
  { name: 'kme3v10', desc: 'MASTER ENGINE V3 — PHIÊN BẢN 10 (guruprasaathas111, Kaggle public, cập nhật 2026-09-13) — code KHÁC kme3 (v9): MD5 4593a884…, 2.626 dòng (+270): R51 beam-search input-path (width 8), R68 joint multi-worker plans, R62 deterministic HIRE spawn, R70/R79 fertilizer adaptive, R85/R86 economic overlay (feed-skip + FERT-sale) · bị v14 vượt 16/16 +$4.5k (chi tiết §11.25)', tag: 'đối thủ mạnh nhất' },
  { name: 'aurax', desc: 'SHOP-ROUTER REACTIVE V4 (aurax7, Kaggle public, version 3, pull 2026-09-13) — code KHÁC kme3/kme3v10: MD5 8230b5a9…, 2.766 dòng (+140): R36 sale-lead window mở sớm hơn (day 9 thay vì day 12), R60 SURVIVAL — lớp cứu hộ giờ 22 FEED động vật sắp chết đói 2 ngày liền, R60 opening liquidity guard · ngang sức kme3v10, bị v14 vượt 16/16 +$4.5k (chi tiết §11.26)', tag: 'đối thủ mới aurax' },
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
