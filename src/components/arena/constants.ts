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
  { name: 'v27', desc: 'NHÀ VÔ ĐỊCH MỚI NHẤT (Task 111, v27.2) — "RACE-PEAK ENDGAME GENERAL": chassis The 2945 Farm v9/4 nguyên bản byte-exact (ladder 2944.7, submission 56269928) + 3 lớp reflex (chỉ kích hoạt RACE MODE khi clone-detector xác định đối thủ KHÔNG phải 2945-family — clone mode giữ nguyên hành vi 10-0 của mirror): (1) CRASH-DUMP retune: race-mode ratio 0.95→0.92 + deep-crash filter sau d23 (chỉ fire khi p ≤ 0.30×đỉnh 4-ngày — chảy máu chậm sẽ bounce cuối game, sập terminal mới đổ tiếp); (2) NEAR-PEAK SALE-ADVANCE (look=14, cơ chế public sdy623/jaxa623 EXP293 + alperen5252525/tetsutani v65): khi băng ghi định bán sản phẩm trong 14 bước tới, hàng có sẵn trong shed và giá ≥ 0.95×đỉnh 6-ngày → bán NGAY bắt đỉnh cung-đường cong; (3) PEAK-ROLLOVER + ENDGAME: phát hiện cú gãy cấu trúc intraday (MELON 271→131 trong d10, WOOL 154→1 d14) ngay tick giảm đầu tiên từ đỉnh 6-ngày để bán sạch shed, TROUGH-HOLD d22+ (giữ hàng chết < 0.07×đỉnh toàn game chờ bounce cuối 61-93), RECOVERY-DUMP d27-29 (giá hồi ≥ 1.6×mở cửa ngày → bán sạch shed, đua flush-race của đối thủ) · BẢNG CHẤP NHẬN Task 111 (10 trận seeds 100-104 × 2 ghế, 12 đối thủ): 120/120 = 100% TOÀN BỘ — thomast2945 10-0 (+358/+1446/+184/+2706/+1094, vượt ngưỡng 80%), v251/v25/v26 10-0 (lật hoàn toàn s100+s101), v24 10-0, alperen1 10-0 (lật s100 −430→+435), ahmedv48 10-0, tetsutani_v65 10-0 (lật s100 −574→+242), v18/ahmedv43/44/45 10-0 · Xem ngay: v27 (ghế A) vs v251 (ghế B) seed 100', tag: 'v27 Second-Half Price-Curve General' },
  { name: 'v26', desc: 'NHÀ VÔ ĐỊCH MỚI NHẤT (Task 100, v26, Kaggle submission 56359569) — "HERD-ADAPTIVE ANSWER GENERAL": v25.1 + port ĐÚNG verdict COW của 2945-farm V9 herd (nghiên cứu Task 99 "The 2945 Farm v9/4", ladder 2944.7) · CƠ CHẾ: khi mua SHEEP/GOOSE trong window ngày 8-11, nếu egg_shops==0 AND YARN_STORE chưa mở AND milk_shops≥3 AND giá MILK≥$150 → đổi cả hai thành COW ("bò chuyên sâu") — đúng profile 12 bò của 2945 trên seed kiểu s110, nơi cừu thành dead weight $500/con vì WOOL sập $1 khi không có YARN · Gate chính xác theo hằng số V9_HERD_* của thomast2945 — KHÔNG đánh cược YARN tương lai (mọi cấu hình shop khác giữ nguyên mix v25.1) · BẢNG ĐỐI CHỨNG: vs ahmedv48 48W-0L (100%), mean +$1.204 (v25.1: +$640) — s110 lật từ +$186 thành +$13.728! · vs alperen1 10-0 +$1.192 & vs tetsutani_v65 10-0 +$689 (khớp byte-exact v25.1 trên seed không verdict) · vs thomast2945 48 trận: 6W-42L, mean −$1.361 (v25.1: 4W-44L, −$1.922) — s110 lật −$9.845 → +$3.638 · Bản port 4 lớp đầu (herd mở rộng + RACEGATE + horizon-40 + ORDERPRI2 + CAPHARV) đã bị LOẠI sau ablation A0/A3: herd sớm đoán-sai YARN muộn tốn −$8,7k/ghế trên s102-104 · Xem ngay: v26 (ghế A) vs thomast2945 (ghế B) seed 110', tag: 'v26 Herd-Adaptive Answer General' },
  { name: 'v251', desc: 'NHÀ VÔ ĐỊCH MỚI (Task 98, v25.1) — "DEMAND-PRESERVING RACE GENERAL": v25 + 2 nâng cấp từ nghiên cứu notebook tetsutani v65 "Demand-Preserving Fourteen-Turn Sale Timing" · (1) FIX-A SLOT HYGIENE: lớp compact sắp các dòng SELL ghép theo DOANH THU giảm dần trong cửa sổ endgame (h21/h22 + ngày ≥27) — mổ xẻ seed 100 phát hiện MILK rác $3 chiếm slot 1 đẩy STRAW 17 unit ($35/u) ra sau đợt dump của đối thủ, mất $530 chỉ trong 1 turn; fix này lật seed 100 từ thua thành thắng và nâng battery vs ahmedv48 lên 48W-0L (100%) · (2) PORT GUARDS V65 CÓ ĐIỀU KIỆN RACE: ≥2 BAKERY mở → quay về timing 3-turn của parent; WOOL offset 5-14 KHÔNG kéo bán sớm khi YARN_STORE mở (giữ cầu) — guards chỉ bật khi máy race (mirror step-1/clone-lock) KHÔNG phát hiện đối thủ cùng tape, tắt hoàn toàn khi đua để giữ đỉnh look=14 · BATTERY: vs ahmedv48 48W-0L (100%!), +$640, CI95 [$521, $759] · vs alperen1 10-0, +$1.192 · vs tetsutani_v65 10-0, +$689 · vs v25 cũ 8W-2L, +$330 · vs thomast (guard-path) 10-0, +$10.072 · Audit 4 lĩnh vực (thực vật/động vật/nhân công/kho): CLEAN tuyệt đối — 0 lỗi, 0 thú thoát, 0 overflow · Xem ngay: v25.1 (ghế A) vs ahmedv48 (ghế B)', tag: 'v25.1 Demand-Preserving Race General' },
  { name: 'v25', desc: 'NHÀ VÔ ĐỊCH (Task 95+96+97) — "THE LAST DAY GENERAL": máy ahmedv48 nguyên bản (byte-exact, attribution giữ nguyên) + 2 lớp riêng: throttle "two-band drain-eta" (FERT không bao giờ giữ, SELL đáy <$5 strip vô điều kiện, dải $5-14 chỉ strip khi ORACLE drain-eta OK, flush từ d27) + compact projected-shed · Task 97: _ADV_LOOK=14 (sale-advance horizon race) — phản công 2 vòng trước 2 đối thủ mới alperen1 (V48+look8, từng 71% vs v25 cũ) và tetsutani v65 (V48+look14+guards) · Battery 48 trận: vs alperen1 48W-0L (100%!), +$723, CI95 [$594, $857] · vs ahmedv48: 46W-2L (95.8%), +$494 · vs tetsutani_v65: 44W-4L (91.7%), +$370 · vs v24: 10-0 +$785 · Xem ngay: v25 (ghế A) vs alperen1 (ghế B)', tag: 'v25 The Last Day General' },
  { name: 'ahmedv48', desc: 'ĐỐI THỦ MỚI (Task 93, pull 18-09) — Ahmed Berat Özer "V48 — Clear the Queue": V47 + dọn hàng đợi lệnh thị trường · gỡ slot SELL không bán được gì, gộp các SELL trùng sản phẩm cash, dồn SELL thực thi được vào slot trống · Held-out của tác giả: 36W-0L-0T vs 6 đối thủ, mean margin +$1.471, paired +$226 so V47 · Kaggle pull byte-exact sha256 4b540288… · Xem ngay: v24 (ghế A) vs ahmedv48 (ghế B)', tag: 'V48 Clear the Queue' },
  { name: 'alperen1', desc: 'ĐỐI THỦ MỚI (Task 97, pull 19-09) — alperen5252525 "First in Line — Stock Into Income": máy ahmedv48 nguyên bản (byte-exact, attribution Apache-2.0 giữ nguyên) + 1 thay đổi duy nhất: _ADV_LOOK=8 — lớp EXP293 sale-advance nhìn trước tape 8 turn (thay 3): nếu tape định bán cash-product (STRAWBERRY/WOOL/EGG/MILK/MELON/CARROT/TOMATO) trong 8 turn tới mà hàng đã nằm trong shed → bán NGAY trước đối thủ cùng tape, kèm front-load SELL lên đầu danh sách · Tác giả claim 136W-8L-0T / 144 trận local vs 6 đối thủ công khai · Kaggle pull byte-exact sha256 53dc224a… · SỨC MẠNH THẬT: từng đánh bại v25 Task 96 với 71% winrate (34W-14L, WOOL +$1.449/trận nhờ bán slot sớm hơn) — buộc v25 Task 97 nâng cấp _ADV_LOOK=14 phản công đến 100% · Xem ngay: v25 (ghế A) vs alperen1 (ghế B)', tag: 'alperen First in Line' },
  { name: 'thomast2945', desc: 'CHUẨN ĐỐI KHÁNG MỚI (Task 99, pull 19-09) — thomastschinkel "The 2945 Farm v9/4": open-source TOÀN BỘ agent đạt 2944.7 điểm ladder (byte-exact sha256 bfee70e9… = đúng submission 56269928) · Kiến trúc: route replayer (băng ghi 720 lệnh của yhay81 + Ahmed V39/V40) + 12 lớp reflex đọc observation công khai: RACE/RACEPX/RACEGATE (đua sale đối thủ horizon 40 turn, không đua vào book đứt giá), PREDICT (dự báo sale đối thủ từ thư viện 451.000 sự kiện nhúng trong file), HERD/HERD2/COWSWAP (chọn bò/cừu/ngỗng theo cung-cầu 2 farm), CAPHARV (thu trước khi tràn cap), ORDERPRI2 (sắp SELL theo mức lộ diện dump), COURIER/SHEDROOM (không mất hàng lúc nửa đêm) · Tác giả tự đo: 91.3% win (493-47) vs toàn bộ top-10 public notebooks — đè cả tetsutani 55-5, alperen 54-6, ahmedv48 55-5 · ĐỐI ĐẦU v25.1: battery 48 trận thắng 44-4 (91.7%) — v25.1 chỉ thắng 8.3%, thua chủ yếu nửa sau mùa (ngày 20-29) vì mix động vật thích ứng + kỷ luật endgame · Ladder 2944.7 · Xem ngay: v25.1 (ghế A) vs thomast2945 (ghế B)', tag: 'The 2945 Farm' },
  { name: 'v24', desc: 'CHALLENGER (Task 92) — v20 chain + GARBAGE-THROTTLE: H2 peak-pricing thuần re-time SELL, không thêm input · cấm bán giá rác <$15, giữ tối đa 24 đơn vị, release chia chunk khi giá hồi ≥$18, nhường endgame cho REAPER · Battery 48 trận: 48W-0L vs ahmedv46 +$1,699; trực tiếp vs v20: 43W-5L +$113, t=2.68, CI95 [$30,$196] — challenger ĐẦU TIÊN vượt cả 3 cổng submission-local', tag: 'v24 GARBAGE-THROTTLE' },
  { name: 'v18', desc: 'NỀN MỚI (Task 81) — jaxa623/sdy623 "Beyond 48-0: 128/128 Worlds with 95% CIs" K0006, Kaggle pull 2026-09-16, main.py byte-exact sha256 4757f3f5… · Lõi = Ahmed Berat Özer V43 "Recovering Lost Harvests" (Apache-2.0, nguyên văn — không đụng farm plan) + 4 market micro-edges: (1) FRONT-LOAD — xếp SELL lên đầu market list, mô phỏng per-unit cả 2 phía (cash/shed/hire/land, solo + lockstep) đảm bảo mọi lệnh vẫn execute đủ; (2) ADVANCE-2 — bán trước 2 turn mọi món đã trong shed nếu tape định bán trong 2 turn tới; (3) HORIZON-24 — sale-reservation horizon tối ưu 24 (sweep 8/16/24/36/48: 24 là đỉnh plateau, 48 thua mirror); (4) OPEN-50 — step-0 wheat round trip n=50 (plateau 25-50, né vách đá <10, tránh self-harm ≥85) · Kết quả của tác giả: 48-0 vs V45 (+$2.384), 48-0 vs V43 (+$1.282), 128-0 qua 64 worlds cả 2 ghế (+$2.087, 95% CI [+1.950, +2.240]), official runner 16-0 không lỗi · Điểm khác biệt v17 cũ: đây là fork trực tiếp DNA V43 có 4 lớp kinh tế vi mô đo lường nghiêm ngặt (bootstrap CI theo world), không phải mirror wrapper', tag: 'nền v18' },
  { name: 'ahmedv43', desc: 'Ahmed Berat Özer V43 "Recovering Lost Harvests" (88 votes, pull 2026-09-16, 321KB, sha256 919fc1d6…) — EXP260, V41 vẫn là frozen primary control · Nền kinh tế đầy đủ: funded atomic opening (Rayk Kretzschmar), reservation activation thích ứng aurax7 Reactive V5, prvsiyan V221B/V224C production/timing lineage, aurax7 day-end storage guard, Dmitrii Gluzdov physical terminal rescue 64 mô phỏng, crop_public_order EXP-167/157 · Đây là 100% phần "làm nông" bên trong v18 — sparring partner gốc để đo riêng giá trị 4 micro-edges', tag: 'đối thủ nền tảng' },
  { name: 'ahmedv44', desc: 'Ahmed Berat Özer V44 "Winning the Same-Turn Sale Race" (32 votes, pull 2026-09-16, 327KB, sha256 797d9bca…) — V43 + cơ chế thắng đua bán cùng turn (same-index lockstep exploitation) · bậc trung gian tiến hóa V43→V45, dùng để soi từng bước tác giả tối ưu gì', tag: 'đối thủ lineage' },
  { name: 'ahmedv45', desc: 'Ahmed Berat Özer V45 "First-Turn Wheat Round Trip" (85 votes, pull 2026-09-16, 329KB, sha256 256d41e…) — V43 + step-0 round trip [BUY_PRODUCT WHEAT n, SELL WHEAT n] n=70: index-0 buy đẩy giá wheat làm buy index-1 của đối thủ đắt hơn ~$60/unit — đúng đủ để phá kế hoạch day-0 được tài trợ khít khao của V43-family (mất 1 hạt melon cả mùa) · Cơ chế gốc của Open-50 trong v18 (jaxa623 sweep lại n=50 an toàn hơn)', tag: 'đối thủ lineage' },
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
