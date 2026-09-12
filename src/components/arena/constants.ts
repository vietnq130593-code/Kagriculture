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
  { name: 'v12', desc: 'KME3-TUNED v3 (code sạch 0 chú thích) — vòng 3: valve PREFIRE h22 (xả overflow sớm 1 bước) + V231 flip điều kiện milk-shops>=3 (bỏ flip hại 2-shop, giữ flip lời 3-shop) · 32/32 thắng kme3 (gap +3.9k/+3.2k hai bộ seed, worst 1.007x) · đè v11 8/8 3.27× (chi tiết §11.23)', tag: 'nhà vô địch' },
  { name: 'v11', desc: 'CADENCE+ADAPT — 6 vòng luyện với kme3: premium-floor kênh deficit + buffer lot-cap + distress-unclog + carrot/đàn thích ứng shop-draw (V231) · 12/12 vs v6 $83k · 6/10 vs v10 $71k · thua kme3 0/8 $41k (chi tiết §11.20)', tag: 'cựu vô địch' },
  { name: 'kme3', desc: 'MASTER ENGINE V3 (Kaggle public, Apache 2.0) — route-tape 719-turn + 20 lớp overlay, Public Score 600 · tự đấu hòa tuyệt đối · bị v12 vượt 16/16 (chi tiết §11.21)', tag: 'đối thủ chuẩn' },
  { name: 'v10', desc: 'AD+KHO — opening 2 bò + melon-12 + drip thú d3-10 (AD 44,5) · 5 kho d0 · carrot cap 10/8 · đồng bộ 75,3% · $79,8k TB', tag: 'thế hệ mới' },
  { name: 'v9', desc: 'STACK-SWEEP — tái cấu trúc kernel lao động: continuation-claims gap-0/1 + morning-cascade + FERT-stack · mục tiêu $90-110k', tag: 'thế hệ mới' },
  { name: 'v8', desc: 'REGION-FLOW — kernel lao động lai: event-water + hybrid tier/geo + wheat-standing + fert · 57/60 vs v7', tag: 'nhà vô địch' },
  { name: 'v7', desc: 'KAIN Champion — kain40 + collect-first R149 · 96/100 vs v6, 1.278×', tag: 'cựu vô địch' },
  { name: 'v6', desc: 'ORCHESTRATOR-K · 93.75% vs v5, 100% vs v4/v3', tag: 'cựu vô địch' },
  { name: 'kain40', desc: 'KAIN Full-Pressure — luật lấp đất 85%: fill-law + tomato channel + hire-buffer', tag: 'KAIN' },
  { name: 'kain39', desc: 'KAIN Price-Blade — kain38 + wheat-hold + egg-fortress-8 (đòn tấn công giá)', tag: 'KAIN' },
  { name: 'kain38', desc: 'KAIN Fill-Smart — tối ưu nguồn lực: lấp thung lũng d5-9 + late-straw + late-wheat', tag: 'KAIN' },
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
