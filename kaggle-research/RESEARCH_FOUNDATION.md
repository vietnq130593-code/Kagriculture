# NỀN TẢNG NGHIÊN CỨU — DỮ LIỆU HẠNG 1 KAGGLE & CƠ CHẾ ENGINE
*Tài liệu nền cho dự án lớn: xây agent thắng Ahmed V45 với khoảng cách lớn hơn nhiều*
*Ngày: 2026-09-16 · Nguồn: 84 trận mới nhất top-14 leaderboard Kaggle kaggriculture + source engine 1.32.7*

> **[Ghi chú lưu trữ 2026-09-17]** — File gốc nằm trong `upload/RESEARCH_FOUNDATION.md`
> (do user tải lên). Sandbox reboot 17:56 đã xóa volume upload; nội dung được Bio
> khôi phục nguyên văn từ context phiên 2026-09-17 và lưu vào repo. Kèm theo đó,
> 2 replay top-vs-top `upload/123.json` (ep 109788044: Majkel1337 thắng M&M&P&Q
> +$2,465, seed 935345325) và `upload/234.json` (ep 109782699: Majkel thắng +$1,494,
> seed 1413514183) đã mất vĩnh viễn (35MB each, không nằm trong git). Dữ liệu 84 trận
> essence + infra fetch không còn trong môi trường; token Kaggle cũng đã mất theo reboot.

---

## 1. DỮ LIỆU ĐÃ THU THẬP

- **84 trận** mới nhất của top-14 đội (28 submission, 3 trận/sub) — essence gọn ~600KB/trận
  (`research/essence/*.json.gz`: money/actions/prices/mkt_inv/farm/daily tiles)
- **Full public leaderboard** 9.232 đội (`research/leaderboard/`)
- **2222 episode metadata** trong `fetch_state.json` (lịch sử đầy đủ — có thể đào sâu sau)
- Raw replay 35MB giữ lại cho các trận top-vs-top (`research/episodes/keep/`)
- Hạ tầng: `fetch_tier1.py` (resumable) + `daemon_fetch.py` (double-fork) + `analyze_tier1.py` + `deep_dive.py` + `price_model.py`
- Token Kaggle hoạt động (user `vietnguyen130593`, đang rank 994/9232)

## 2. SỰ THẬT SỐC: THẾ GIỚI KHÔNG ĐỐI XỨNG HOÀN TOÀN KHÁC

| Chỉ số | Thế giới V45-mirror (ta) | Hạng 1 thực tế |
|---|---|---|
| Tiền cuối mỗi bên | ~$157K đều nhau | $16K – **$227K** |
| Margin | +$1.000 (trần đã chứng minh) | TB $9.887, max **$210.983** |
| Kỷ lục tuyệt đối | $157.7K (King01) | **$227.6K (THIRD FARM CLUB)** |
| Match top-vs-top | — | margin $1.6K-$17.9K |

- **TFC vs Nithin Nambi: $227.595 vs $16.612** (margin $211K) — TFC dồn 70% doanh thu vào MILK bán $250-306
- **M&M&P&Q đạt $162.6K** thắng Majkel1337 (#1) +$17.6K
- Top-vs-top: **Majkel1337 92% thắng** (11/12) — vua đối đầu trực tiếp
- Các đội "volume farmer" (Kenjo/shawenher/local/洛希边际... cùng 1 notebook công khai): bán 100K+ đơn vị/trận, crash mọi giá về $1, chỉ đạt $82-130K — **bị loại khỏi cạnh tranh thực sự**

## 3. CƠ CHẾ ENGINE ĐÃ GIẢI MÃ HOÀN TOÀN (từ source 1.32.7)

### 3.1 Mô hình giá — HÀM XÁC ĐỊNH CỦA TỒN KHO THỊ TRƯỜNG
```
price(item) = base + amp_below × shape(below_func, I0 − inv)   nếu inv < I0 (khan hiếm → giá TĂNG)
            = base − amp_above × shape(above_func, inv − I0)   nếu inv > I0 (thừa → giá GIẢM)
floor $1; I0 = 10.000 cho mọi item; inv thay đổi bởi: SELL (+1/đơn vị), BUY/BUY_SEED (−1), town (−)
```
**KIỂM CHỨNG: 0.00% sai lệch trên 61.200 điểm giá × 9 item × 84 trận** (sau khi có HINGE_GAIN=8).
→ Agent quan sát `market.inventory` mỗi turn ⇒ **biết chính xác mọi giá hiện tại & tương lai** (town consumption + hành vi đối thủ là đầu vào duy nhất).

### 3.2 Bảng thông số giá (trích engine)
| Item | base | T | below (khan) | above (thừa) | Ghi chú |
|---|---|---|---|---|---|
| WHEAT | 25 | 400 | sqrt ×0.80 (max ~$60) | log ×0.20 (nhẹ) | ít crash, trần thấp |
| CARROT | 35 | 450 | hinge ×1.00 | sqrt ×0.70 | |
| TOMATO | 60 | 200 | hinge ×0.40 | sqrt ×0.60 | |
| STRAWBERRY | 120 | 100 | sqrt ×0.70 (~$277 thực tế) | **linear ×1.60 (rất dễ crash)** | max $277 quan sát |
| MELON | 250 | 300 | log ×0.20 | **sq ×3.60 (thảm họa)** | nhu cầu chỉ ~24/ngày — ITEM BẪY |
| EGG | 50 | 332 | hinge ×0.40 | log ×0.20 | |
| MILK | 160 | 122 | **sqrt ×0.60 ($306 thực tế)** | linear ×1.60 | máy in tiền khi giữ nhịp |
| WOOL | 200 | 105 | log ×0.20 ($240) | **sq ×3.20 (thảm họa)** | chỉ bán khi khan |
| FERTILIZER | 100 | 200 | linear ×0.40 | linear ×0.40 | cầu = 0 (chỉ người chơi mua) |

### 3.3 Town tiêu thụ (đo thực tế 84 trận — tốc độ hút tồn kho khi không ai bán)
| Item | /turn | /ngày | Ghi chú |
|---|---|---|---|
| WHEAT | 5.31 | ~127 | cầu khổng lồ (kể cả mua hạt giống) |
| FERTILIZER | 5.12 | ~123 | người chơi mua làm phân bón |
| STRAWBERRY | 2.92 | ~70 | |
| CARROT | 2.50 | ~60 | |
| WOOL | 2.46 | ~59 | |
| MILK | 2.31 | ~55 | |
| EGG | 1.71 | ~41 | |
| TOMATO | 1.72 | ~41 | |
| MELON | 1.00 | ~24 | quá thấp so với sản xuất |

Cơ chế: town center −1 mỗi 24 turn (8 item trừ FERT); 8 shop instance (rút có hoàn lại) −1 (×2 nếu shop đơn item) mỗi 4 turn theo danh mục shop. **Danh sách shop hiển thị trong observation `town.unlocked_shops`** — đọc được, tính được.

### 3.4 Kinh tế sản xuất
- **CROPS**: WHEAT $10→6 đơn vị ngày 2-4 (1 lần); CARROT $20→4 ngày 2-3; TOMATO $50 ongoing 4/1 ngày từ ngày 8; **STRAWBERRY $100 ongoing 4/2 ngày từ ngày 10** (≈40 đơn vị/ô/vụ); MELON $80→6 ngày 10-12 (bẫy!)
- **ANIMALS**: GOOSE $300→EGG 1/1 ngày từ ngày 4 (tối đa giữ 4); **COW $400→MILK 1/2 ngày từ ngày 8 (giữ 6)**; SHEEP $500→WOOL 1/3 ngày từ ngày 6 (giữ 6)
- **COW = máy in**: 32 bò × ~11-17 sữa × $250-300 ≈ **$90-160K/trận từ MILK** (TFC thực tế $158.7K)
- Round-trip BUY→SELL cùng lúc: engine chốt bằng thiết kế (BUY quote ở inventory sau mua) — lợi nhuận 0
- **Mua lúc đối thủ làm lụt (glut), bán khi town hút cạn (deficit) = arbitrage liên thời gian THẬT** (+$50-150/đơn vị)
- Per-unit lockstep (Task 91): cùng turn = cùng giá tuyệt đối; mua/bán ảnh hưởng inventory ngay trong turn

## 4. CÔNG THỨC THẮNG CỦA TOP TEAM (đã giải mã)

### TFC 227K (ep 109679807):
1. **Đầu tư sạch tiền** ngày 1-4 ($3.000 → $188): mua bò + mở góc + hạt giống
2. **Chuyển đổi nông trại thành nhà máy sữa**: 2→8→19→25→32 COW (thay dần STRA 29→2 ô)
3. **Giữ nhịp bán MILK 1 lần/ngày** (đúng chu kỳ 24 turn, từ T384): bán đúng lượng sản xuất, không dồn tồn kho vượt I0 → **giá sữa TĂNG cả trận** 187→306 dù bán liên tục
4. **Endgame day 29**: 20 lệnh $67.8K — dump đúng phần deficit còn lại
5. SOLO income $157.8K (89% doanh thu xảy ra khi đối thủ không bán cùng turn)

### Majkel1337 (#1, 92% top-vs-top):
- Đa dạng hóa (STRA+WHEA+MILK+WOOL+MELO), SOLO income $124.8K vs MMPQ $56.1K (trận thắng +$17.9K)
- Bán xen kẽ sau khi đối thủ vừa bán (hút cửa sổ hồi phục)

### M&M&P&Q ($162.6K vs Majkel):
- Cầu WOOL giữ cuối trận $83.1K (giá 214→240), né crash STRA mà Sida Zuo bị (dump sớm → 229→32)

### Bài học chung:
- **Người thua**: dump 1 item sớm (crash giá chính mình), chơi MELON/TOMATO (cầu thấp), bán liên tục từng lô nhỏ (V45-family style — nhận giá trung bình thấp)
- **Người thắng**: tích sản → bán đúng lượng deficit tại đỉnh giá → solo turn → cuối trận dump đúng phần còn lại của deficit

## 5. GIẢ THIẾT CHO DỰ ÁN LỚN (King02+)

| # | Giả thuyết | Cơ chế | Margin kỳ vọng vs V45 |
|---|---|---|---|
| H1 | **Milk Printer** | 25-32 COW (V45 chỉ có 8); MILK deficit ~570/trận vs cung V45 ~90 → giá $250-300 cả trận; King bán 400-500 sữa vào deficit | **+$40-80K** |
| H2 | **Peak Pricing** | Không bao giờ bán khi inv > I0; bán đúng deficit sau mỗi nhịp town hút; endgame dump đúng phần còn dư | +$20-50K tuyệt đối |
| H3 | **Arbitrage liên thời gian** | Mua STRA/FERT khi V45 làm lụt (giá ≤ base), bán khi town hút cạn (+$50-150/đơn vị); shed 100 + tay mang | +$10-30K |
| H4 | **Race hybrid** | Giữ nudge-9 cho endgame stock-arrival dumps (đối xứng), cộng opponent-sale tracking (nhịp bán V45 đều, học được) | giữ +$1K hiện có |

**Chuỗi dự kiến**: R1 King02-Milker (H1) → R2 King03-PeakPricer (H1+H2) → R3 King04-Arbitrageur (H3) → R4 chuẩn hóa battery 128 seed vs ahmedv45 + V41-44 + chính V220/King01 (chống thu hẹp khoảng cách tự phản chiếu) → R5 upload Kaggle thử thang thật.

## 6. SỐ LIỆU CHI TIẾT
- `tier1_index.json` — 84 trận (đội, kết quả, margin)
- `tier1_analysis.json` — hồ sơ từng đội + 84 match phân tích đầy đủ
- `TIER1_REPORT.md` — báo cáo tổng quan (đã cập nhật crop mix)
- Cần đo thêm ở R1: cơ cấu sản xuất/bán của V45 trong mirror (đối chiếu với top team)

## 7. LƯU Ý KỸ THUẬT
- Sandbox kill process nền khi bash session kết thúc → dùng `daemon_fetch.py` (double-fork setsid, PPID=1)
- Kaggle CLI 2.2.4: `team-submissions <id>` → `episodes <sub_id>` → `replay <ep_id>`; output JSON kèm "Next Page Token" phía sau → dùng `raw_decode`
- Replay 35MB/trận → essence gzip ~600KB; giữ raw top-vs-top trong `episodes/keep/`
- Mọi số liệu margin "top-vs-yếu" phình to do đối thủ yếu tự hủy — bài toán thực của ta là **vs Ahmed v45 cụ thể** (một constant-seller), Margin +$40-80K từ H1 là chỉ tiêu khả thi

---

> **[Đánh giá sau thực nghiệm Task 89 — 2026-09-17]** — H1/H2 đã được kiểm nghiệm
> trực tiếp trong mirror v20 vs ahmedv46 (8 seed × full 720 turn) và bị **bác bỏ
> cho thế giới mirror** (xem worklog Task 89 + 09_V21_MIRROR_FINDINGS.md):
> MILK luôn glut (giá $5-76 trong 6/8 seed, chỉ 1 milk shop); BUY_PRODUCT chỉ cho
> phép WHEAT/FERTILIZER (arb mua bị chặn tận engine); free-rider effect khiến
> banking mọi item mất EV; mix-shift COW→SHEEP nhường monopoly milk cho v46
> (−$18K/game). Các biên độ lớn $40-80K chỉ tồn tại ở thế giới top-tier nơi đối
> thủ không phản ứng — không chuyển được vào mirror constant-seller.
