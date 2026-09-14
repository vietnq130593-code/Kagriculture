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
  { name: 'v16h57', desc: 'ARI CLASS Mk-III+H5+H7 (Task 76 — bản KẾT HỢP, thua v16h7 trực tiếp 0/10 −$91) — v16 + H7 impact model (xếp SELL cùng turn theo qty × (giá hiện − giá sau tự đổ) bằng bảng giá engine chính xác, impact_slots mode — port Kaito v43) + H5 conditional memory 51 prototype (30 chữ ký farm top-30 Kaggle của Kaito + 21 chữ ký local fit từ v16-vs-đối thủ seeds riêng, hit-rate 74-100% seed mới, 1-NN distance ≤48 đoán item đối thủ bán NGAY turn này rồi kéo SELL trùng lên đầu queue, chỉ reorder — port Kaito v21.1 177/180)', tag: 'biến thể v16' },
  { name: 'v16h5', desc: 'ARI CLASS Mk-III+H5 (Task 76) — v16 + CONDITIONAL MEMORY (cơ chế Kaito v21.1): bank 51 prototype (30 chữ ký farm top-30 Kaggle + 21 local fit từ trận v16-vs-đối thủ seeds riêng tách battery), mỗi turn 1-NN match (weight 12×workers/7×quadrant/3×counts, gate distance ≤48, abstain khi lạ) → đoán item đối thủ sắp bán NGAY turn này → kéo SELL trùng lên đầu queue · CHỈ đổi thứ tự, không tạo SELL mới (an toàn closed-loop) · Hit-rate seed mới 74-100% nhưng gap thực chiến ≈ 0 (meta local bán cùng slot → engine fair-share) — kết quả: 0/10 −$62 vs parent', tag: 'biến thể v16' },
  { name: 'v16h7', desc: 'ARI CLASS Mk-III+H7 (Task 76) — bản THẮNG cuộc đánh giá 3 phiên bản, đã được promote thành v16 Mk-IV (file này giữ nguyên để đối chứng — behavior đồng-dollar từng cent với v16): impact model qty × (giá hiện − giá sau tự đổ) bằng bảng giá engine chính xác + impact_slots mode, thay thế heuristic rival-batch cũ của tầng R37', tag: 'biến thể v16' },
  { name: 'v16', desc: 'ARI CLASS Mk-V (Task 78) — Mk-IV + H8 SPEND-DETECTOR TIE-BREAK (port andrewsokolovsky Breaking-the-Tie): theo dõi tiền đối thủ tại checkpoint step 217-219 (cửa sổ cattle-switch, cohort chi $481-581 tại 218) spend ≥ $100 → bật vĩnh viễn overlay horizon-2 front-run — bán trước dump đối thủ tại step+2 trên 4 món MILK/WOOL/STRAWBERRY/MELON (giữ mọi gate H1 town-demand, không suppression — stock-clamp thay thế) · Inert verify đồng-dollar từng cent (8/8) · Battery Task 78 seeds 350-354: vs v15/v14 10/10 +$444 worst 1.0007 (Mk-IV chỉ 9/10 +$275 worst 0.9989 — xóa sạch seat-game thua), vs parent +$110 mọi seed, kme3-family/thomast giữ nguyên từng dollar, kawashigi +$35.9k, indark +$23.1k, thua v16h5/h57 10/10 — giữ nguyên di sản Mk-IV + H1/H2/H3/H7', tag: 'nhà vô địch' },
  { name: 'v16h8', desc: 'ARI Mk-IV + H8 SPEND-DETECTOR TIE-BREAK (Task 78) — port andrewsokolovsky Breaking-the-Tie: theo dõi tiền đối thủ tại checkpoint step 217-219 (cửa sổ cattle-switch, cohort local chi $481-581 tại 218) spend ≥ $100 → bật vĩnh viễn overlay horizon-2 front-run (bán trước dump đối thủ tại step+2 trên 4 món MILK/WOOL/STRAWBERRY/MELON, giữ mọi gate H1) · Inert verify đồng-dollar từng cent; battery seeds 350-354: vs v15/v14 10/10 +$444 worst 1.0007 (parent 9/10 +$275) — 0 thua 0 hòa, vs parent +$110 mọi seed', tag: 'đối chứng Mk-V' },
    { name: 'v15', desc: 'ARI CLASS Mk-II (Task 73) — v14 + R90 SHED-ANIMAL WATCHDOG: sửa bug mất thú trong shed (gốc rễ trận thua -$5.973 trên Kaggle, Task 72): bò/cừu/gà bị kẹt shed khi PLACE fail + planner không retry — giờ được cứu lên ô trống khớp cấu trúc sau thời gian im lặng (detector hoạt động + hire hand riêng, không đụng farmer/worker) · provably-inert khi không có bug (đồng hành từng byte với v14)', tag: 'nhà vô địch' },
  { name: 'v14', desc: 'ARI CLASS (Task 69) — nền kme3v10 + 6 tầng tuning v13 + stack mới đo lường: FRONT-RUN (bán trước lịch dump premium của đối thủ mirror — route/tape dự đoán từ shop public), HORIZON 8 (đua pre-sell sâu hơn H=6 của v13), ROOM-GUARD + CLAMP-SELLS (2 layer chassis bật lại) · 80/80 thắng tuyệt đối: v13 32/32 (+$4.95k), kme3 16/16 (+$5.65k), kme3v10 16/16 (+$4.52k), aurax 16/16 (+$4.53k) · tools: battery.py + gap_waterfall.py + force_route.py', tag: 'cựu vô địch' },
  { name: 'v13', desc: 'KME3-TUNED v4 DUAL-OPPONENT — lõi H=6/LO=144/HI=712, prefire h21+h22, V231-flip điều kiện, V224 sales-first, R37 reorder mở từ step 144, melon-seller mọi giờ · 48/48 thắng kme3, 8/8 kme3v10/aurax · bị v14 vượt 32/32 (chi tiết §11.23-24)', tag: 'cựu vô địch đầu tiên' },
  { name: 'kme3', desc: 'MASTER ENGINE V3 (guruprasaathas111, Kaggle public, Apache 2.0) — route-tape 719-turn + 20 lớp overlay, Public Score 600 · tự đấu hòa tuyệt đối · bị v14 vượt 16/16 +$5.6k (chi tiết §11.21-24)', tag: 'đối thủ chuẩn' },
  { name: 'kme3v10', desc: 'MASTER ENGINE V3 — PHIÊN BẢN 10 (guruprasaathas111, Kaggle public, cập nhật 2026-09-13) — code KHÁC kme3 (v9): MD5 4593a884…, 2.626 dòng (+270): R51 beam-search input-path (width 8), R68 joint multi-worker plans, R62 deterministic HIRE spawn, R70/R79 fertilizer adaptive, R85/R86 economic overlay (feed-skip + FERT-sale) · bị v14 vượt 16/16 +$4.5k (chi tiết §11.25)', tag: 'đối thủ mạnh nhất' },
  { name: 'aurax', desc: 'SHOP-ROUTER REACTIVE V4 (aurax7, Kaggle public, version 3, pull 2026-09-13) — code KHÁC kme3/kme3v10: MD5 8230b5a9…, 2.766 dòng (+140): R36 sale-lead window mở sớm hơn (day 9 thay vì day 12), R60 SURVIVAL — lớp cứu hộ giờ 22 FEED động vật sắp chết đói 2 ngày liền, R60 opening liquidity guard · ngang sức kme3v10, bị v14 vượt 16/16 +$4.5k (chi tiết §11.26)', tag: 'đối thủ mới aurax' },
  { name: 'kme3v39', desc: 'MASTER ENGINE V39 (guruprasaathas111 "Master Engine V3" 317KB, Kaggle public, pull 2026-09-13, Task 75 extract SHA-verified 708c7485…) — chính xác kme3v10 + 3 layer mới: R88 feed-bonus horizon (care=0 khi dawn sản xuất kế > ngày 29 — không feed vô ích cuối mùa), R95 grain reserve 49-turn (trim mua wheat thừa, day 10-11), R97 supply guard (chặn SELL WHEAT phá kế hoạch pickup 2 lượt tới, mô phỏng overnight overflow, step 144-695) — họ KaggressurE MỚI NHẤT, mạnh hơn kme3v10 về kinh tế giữa game', tag: 'đối thủ Kaggle mới nhất' },
  { name: 'kawashigi', desc: 'BL-KAWASHIGI ADAPTIVE R1 V19CORE (tetsutani "Adaptive Farming Strategy" 142v + flexonafft duplicate 93v, Task 75 extract) — 5 tape theo vị trí YARN trong 3 shop đầu (10C4S/8C6S/6C8S/6C12S×2) + 10 layer guard: weed repair, room evac/guard, impact×urgency sell ranking, clone preempt debt-ledger, counters R5/MD (băng đóng băng — tự tắt vs herd khác), terminal liquidation, legacy-layout fallback · FERT-heavy 2.932u', tag: 'đối thủ BL-Kawashigi' },
  { name: 'indark_e776', desc: 'INDARKARHANA "SHAPE THE SHOP" E776 (top-10 Kaggle, 94v, Task 75 extract) — tape Kenjo1209 medoid 9C/5S/HIRE290 (ngoài registry cũ) + chuỗi guard E749→E776: contested-value SELL ranking (xếp slot gây tổn thất lớn nhất cho người bán kế tiếp), sequential funding ledger (SELL cộng tiền trong-lượt slice HIRE/BUY), demand-aligned pasture (pressure wool vs dairy đổi nhãn COW↔SHEEP), latent pasture activation (+1 con +1 hand step 313), engine-exact delivery repair fail-closed', tag: 'đối thủ top-10 đáng ngại nhất' },
  { name: 'thomast', desc: 'THOMASTSCHINKEL V5 PUBLIC-STATE ROUTER 93.8% WR (Kaggle pull 2026-09-13, Task 78 extract) — 5 tape + decision tree chốt tape tại step 0/144/288/432/576; block 4 (day 24) đọc px_CARROT ≤ 54 → tape3 late-liquidation — mục tiêu steering H6 (dump CARROT đẩy router vào tape yếu)', tag: 'đối thủ router' },
  { name: 'thomast_t0', desc: 'thomast ép tape0 tại checkpoint step 576 (hành vi tự nhiên khi px_CARROT > 54)', tag: 'đối thủ router' },
  { name: 'thomast_t3', desc: 'thomast ép tape3 tại checkpoint step 576 (kịch bản BỊ STEER: px_CARROT ≤ 54) — đo giá trị steering', tag: 'đối thủ router' },
  { name: 'ahmedv41', desc: 'AHMED BERAT OZER V41 REVIEW-CANDIDATE (Kaggle pull 2026-09-14, Task 79 extract, 317KB) — V39 base (kme3v39 cùng lineage, 55% code chung) + funded atomic opening kiểu Rayk Kretzschmar (BUY WHEAT 5+10/SELL 60 ngay step 0) + R127 field-projection safety + R128 service layer (feed-service swaps step 144-647: đổi lệnh FEED hết thức ăn thành PICKUP+1, prefetch kẻ rảnh; sale-credit step 144-695: bán WHEAT trong lượt để đủ tiền mua tiếp) · Self-claim: thắng V39/V40 128/128 trận trực tiếp, +110 win/3200 game vs public policies — đối thủ nặng ký nhất họ ahmedberatozer', tag: 'đối thủ V41 mới' },
  { name: 'v17', desc: 'ARI CLASS Mk-VI MERCATOR (Task 80) — ahmedv41 core nguyên văn qua certified-mirror wrapper: sau 8 thiết kế overlay (M1 market dumps, M2 price-gated milk rent, M3 hired hands, M4 SE-land arbitrage, M5 credit rescue, M6 goose saturation, M7 pressure valve, M8 endgame liquidation) đều thí nghiệm âm tính, kết luận ahmedv41 = Nash equilibrium của engine này — mọi can thiệp wrapper phá giá trị dùng chung (milk $258→$31 khi dump sớm, hire fibonacci $144-233/ngày sau 11 hands của tape, shed-90 valve bắt đúng lúc tape thanh khoản cuối game) · Battery: vs ahmedv41 gap +$0.00 chính xác (1.000x — perfect mirror, không thể thua), vs v16 10/10 +$23,134 (1.272x) · Bước đột phá kế tiếp = v18 fork tape DNA (goose gap +$1k/con, SE land $4k bỏ không, seed-adaptive herd)', tag: 'nhà vô địch' },
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
