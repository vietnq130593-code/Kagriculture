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
  { name: 'v18', desc: 'NỀN MỚI (Task 81) — jaxa623/sdy623 "Beyond 48-0: 128/128 Worlds with 95% CIs" K0006, Kaggle pull 2026-09-16, main.py byte-exact sha256 4757f3f5… · Lõi = Ahmed Berat Özer V43 "Recovering Lost Harvests" (Apache-2.0, nguyên văn — không đụng farm plan) + 4 market micro-edges: (1) FRONT-LOAD — xếp SELL lên đầu market list, mô phỏng per-unit cả 2 phía (cash/shed/hire/land, solo + lockstep) đảm bảo mọi lệnh vẫn execute đủ; (2) ADVANCE-2 — bán trước 2 turn mọi món đã trong shed nếu tape định bán trong 2 turn tới; (3) HORIZON-24 — sale-reservation horizon tối ưu 24 (sweep 8/16/24/36/48: 24 là đỉnh plateau, 48 thua mirror); (4) OPEN-50 — step-0 wheat round trip n=50 (plateau 25-50, né vách đá <10, tránh self-harm ≥85) · Kết quả của tác giả: 48-0 vs V45 (+$2.384), 48-0 vs V43 (+$1.282), 128-0 qua 64 worlds cả 2 ghế (+$2.087, 95% CI [+1.950, +2.240]), official runner 16-0 không lỗi · Điểm khác biệt v17 cũ: đây là fork trực tiếp DNA V43 có 4 lớp kinh tế vi mô đo lường nghiêm ngặt (bootstrap CI theo world), không phải mirror wrapper', tag: 'nền v18' },
  { name: 'ahmedv43', desc: 'Ahmed Berat Özer V43 "Recovering Lost Harvests" (88 votes, pull 2026-09-16, 321KB, sha256 919fc1d6…) — EXP260, V41 vẫn là frozen primary control · Nền kinh tế đầy đủ: funded atomic opening (Rayk Kretzschmar), reservation activation thích ứng aurax7 Reactive V5, prvsiyan V221B/V224C production/timing lineage, aurax7 day-end storage guard, Dmitrii Gluzdov physical terminal rescue 64 mô phỏng, crop_public_order EXP-167/157 · Đây là 100% phần "làm nông" bên trong v18 — sparring partner gốc để đo riêng giá trị 4 micro-edges', tag: 'đối thủ nền tảng' },
  { name: 'ahmedv44', desc: 'Ahmed Berat Özer V44 "Winning the Same-Turn Sale Race" (32 votes, pull 2026-09-16, 327KB, sha256 797d9bca…) — V43 + cơ chế thắng đua bán cùng turn (same-index lockstep exploitation) · bậc trung gian tiến hóa V43→V45, dùng để soi từng bước tác giả tối ưu gì', tag: 'đối thủ lineage' },
  { name: 'ahmedv45', desc: 'Ahmed Berat Özer V45 "First-Turn Wheat Round Trip" (85 votes, pull 2026-09-16, 329KB, sha256 256d41e…) — V43 + step-0 round trip [BUY_PRODUCT WHEAT n, SELL WHEAT n] n=70: index-0 buy đẩy giá wheat làm buy index-1 của đối thủ đắt hơn ~$60/unit — đúng đủ để phá kế hoạch day-0 được tài trợ khít khao của V43-family (mất 1 hạt melon cả mùa) · Cơ chế gốc của Open-50 trong v18 (jaxa623 sweep lại n=50 an toàn hơn)', tag: 'đối thủ lineage' },
  { name: 'v24', desc: 'CHALLENGER MỚI (Task 92) — v20 chain + GARBAGE-THROTTLE: H2 peak-pricing thuần re-time SELL, không thêm input · cấm bán giá rác <$15, giữ tối đa 24 đơn vị, release chia chunk khi giá hồi ≥$18, nhường endgame cho REAPER · Battery 48 trận: 48W-0L vs ahmedv46 +$1,699; trực tiếp vs v20: 43W-5L +$113, t=2.68, CI95 [$30,$196] — challenger ĐẦU TIÊN vượt cả 3 cổng submission-local · Thử ngay: chọn v24 ghế A và một đối thủ ghế B', tag: 'v24 GARBAGE-THROTTLE' },
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
