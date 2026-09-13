# 03 — KẾ HOẠCH THỰC NGHIỆM ĐỘT PHÁ V15→V16 (Task 74)

> Đầu vào: 493 notebook public + 5 báo cáo ANALYSIS_*.md. Mục tiêu: thắng meta Kaggle hiện tại
> (9c4s modal, các router/preemption agent, họ KaggressurE V39) — không chỉ thắng local registry cũ.
>
> **Nguyên tắc giữ nguyên từ Task 69**: 1 biến thể = đúng 1 delta · seeds mới × 2 ghế · veto nếu thua parent ở bất kỳ
> seed nào · parent (v15) là đối thủ bắt buộc.

---

## TIER 1 — BOLT-ON PHẪU THUẬT VÀO v15 (rẻ, zero-regression, làm ngay)

### H1. Town-demand gate cho front-run + debt-ledger hoàn chỉnh
- **Gì**: (a) front-run chỉ pull-forward khi turn hiện tại KHÔNG có shop cầu item đó (bỏ giờ có tick demand kép);
  (b) mọi lượng pull-forward ghi `due[item]` và **khấu đúng lại** khỏi SELL gốc turn sau — bất biến 2-turn bảo toàn.
- **Nguồn**: salemali7 + boatlee V16-RC5 + andrew munib (gate) · boatlee 84/84 + Kaito v48 + tetsutani (debt) — 4 nguồn độc lập
- **Cost**: ~15 dòng sửa `_sell_lead`/`_front_run`. **Risk**: gần 0 (chỉ siều kiện hóa thêm).
- **Gate**: battery 10 trận vs v15 (seeds mới 2 ghế): ≥8/10 thắng hoặc bằng-dollar, KHÔNG trận thua >$1k.

### H2. Mega-SELL endgame + terminal relay + dead_stock
- **Gì**: bước 716-718: SELL qty 10^6 mọi item còn trong shed (engine tự kẹp) + walk-to-shed khi `distance ≤ 718-step` +
  bật dead_stock scan.
- **Nguồn**: boatlee (mega-SELL) + hamburger (relay 716-718) + thomast 968 game (+19/−0 khi bật 2 flag)
- **Cost**: ~20 dòng ngoài cùng (không đụng plan giữa game). **Risk**: thấp — chỉ chạy 4 bước cuối.
- **Gate**: đồng-dollar trên đa số seed (no-op khi schedule đã clean); mọi seed có dead_stock phải ≥ parent; không được addle giờ 715.

### H3. R88 horizon-check feed (anti-feed-vô-ích cuối mùa)
- **Gì**: care/feed = 0 nếu dawn sản xuất kế tiếp > ngày 29; pending_care_bonus chỉ tính vào dawn sản xuất.
- **Nguồn**: guruprasaathas V39 (EXP219) — chính đối thủ KaggressurE đã ship
- **Cost**: ~15 dòng. **Risk**: thấp.
- **Gate**: battery vs v15: ≥ +$100 trung bình trên seeds mà endgame feed tồn tại; bằng-dollar trên seed không dính.

### H4. No-demand-turn front-run (siêu tinh gọn)
- **Gì**: chỉ front-run khi `step%4≠0 and step%24≠0` (turn không demand) — tránh tự ăn chân giá.
- **Nguồn**: boatlee V16-RC5 (313 votes — agent cao votes nhất). **Cost**: 1 dòng. Có thể gộp vào H1.

**Thứ tự**: H1 (bao H4) → H2 → H3. Mỗi cái là 1 commit + 1 battery. Tổng ước +$300-1.500/trận mirror-class (tham chiếu C94/C95: pull 5-10u đúng lúc = +27-94 mean, nhưng phân phối dài có trận cứu $5k+).

---

## TIER 2 — LỚP NĂNG LỰC MỚI (đắt hơn, tiềm năng cao nhất)

### H5. ⭐ 1-NN Conditional Memory (chuyển hóa front_run → prediction-based)
- **Gì**: xây 30 prototype chữ ký farm public của top-30 Kaggle (kéo từ daily episodes dataset hoặc 34 notebook đã tải —
  nhiều tape đã extract trong `kaggle_dl/unpacked/` + `kaito_extracted/`). Mỗi turn: 1-NN match (distance ≤48, weight
  12×workers/7×quadrant/3×counts) → đoán item đối thủ sắp bán NGAY turn này → **reorder** SELL trùng lên đầu queue
  (chỉ đổi thứ tự, KHÔNG tạo SELL mới — an toàn closed-loop, abstain 2.4% khi không chắc).
- **Nguồn**: Kaito v21.1 — **177/180 vs top-30**, kỹ thuật đắt nhất public meta.
- **Cost**: ~150 dòng + data pipeline prototype. **Risk**: TB — cần data replay Kaggle (đã có 2 file 32MB + 3 file thua; có thể kéo thêm bằng token).
- **Gate**: 2 vòng — (1) offline: với 3 replay Kaggle có sẵn, memory đoán đúng ≥60% lượt bán của đối thủ; (2) battery vs v15 + kme3v39 + kawashigi: ≥8/10.

### H6. ⭐ Router steering — đòn thao túng state (lớp tấn công MỚI)
- **Gì**: nếu đối thủ là router public (thomast-family: đọc px_CARROT ≤54 tại day-24 checkpoint) → **đổ CARROT trước step 576**
  để đẩy họ vào tape3 late-liquidation thấp giá trị. Tổng quát hóa: nhận diện router đối thủ (fingerprint code từ 34 notebook)
  → map feature-router đọc → hành động thay đổi feature đó đúng trước checkpoint.
- **Nguồn**: Task 74-b (thomast v5 decision tree decode được: `x4 = px_CARROT ≤ 54 → tape3`).
- **Cost**: ~80 dòng (detect + 1 chiến thuật dump-carrot). **Risk**: TB — dump CARROT có giá thật (~vài trăm $) nhưng đổi hướng cả route đối thủ.
- **Gate**: battery vs thomast-proxy (cần build từ tape v5 đã decode): target thắng ≥9/10 khi steering bật vs 6-7/10 khi tắt.

### H7. Impact-model giá phi tuyến cho SELL ordering
- **Gì**: port bảng MARKET_PARAMS (base/equilibrium/shape từng item) + demand model (shop %4 ×2, center %12 ×1/2/4) từ Kaito v43;
  sorts SELL cùng turn theo `qty × (giá_hiện − giá_sau_tự_đổ)` thay vì giá hiện tại.
- **Nguồn**: Kaito v43 (transcription khớp engine) + boatlee V14 (milk/straw linear-1.6, wool/melon sq-3.2/3.6).
- **Cost**: ~100 dòng (bảng + hàm giá). **Risk**: TB.
- **Gate**: battery vs v15: ≥7/10 và không trận nào thua parent >$500; đo thêm "giá trung bình thực hiện/item" phải tăng.

### H8. Spend-detector tie-break (chống hòa Elo)
- **Gì**: theo dõi opponent_money; nếu tại step 217 đối thủ tiêu ≥$100 so với lượt trước → bật vĩnh viễn overlay front-run
  trên WOOL/MILK/MELON/STRAW (Elo chỉ tính W/L/T — hòa là nửa thua).
- **Nguồn**: andrewsokolovsky "Breaking the Tie" (73 votes). **Cost**: ~30 dòng. **Risk**: thấp.
- **Gate**: battery vs các đối thủ mirror-CLASS (v14 self, kme3v39): giảm số trận hòa, không tăng số thua.

### H9. Contested-value SELL ranking (khi có clone/near-clone)
- **Gì**: khi phát hiện near-clone (dùng clone_distance công thức boatlee thay vì giả định lineage): xếp SELL theo
  tổn thất gây cho người bán kế tiếp (`Σ giá block mình − Σ giá block displaced`).
- **Nguồn**: indarkarhana E749 + hamburger exposure×glut (2 biến thể cùng ý).
- **Cost**: ~50 dòng. **Risk**: TB. **Gate**: mirror battery (v15 vs v15-patched): win-rate >50% trên ≥20 trận paired-seat (không được tệ hơn do L38).

---

## TIER 3 — HẠ TẦNG & ĐỐI THỦ (bắt buộc trước khi kết luận gì về sức mạnh)

### H10. 🚨 Build + đăng ký 3 đối thủ mới (metà meta đã đổi, battery đang lạc hậu)
1. **kme3v39** = kme3v10 + 3 layer từ V39 đã decode (`research/kaggle_dl/unpacked/`): R88 horizon-feed · R95 grain-reserve 49-turn · R97 supply-guard. **Đối thủ KaggressurE mạnh nhất hiện tại.**
2. **kawashigi** (tetsutani BL-Kawashigi-V19Core): 5 tape theo vị trí YARN + counters đóng băng — `tetsutani_adaptive__main.py` đã extract sẵn.
3. **indark_e776** (Kenjo1209 medoid 9C/5S/HIRE290): `indarkarhana/` 13 file đã extract — **đối thủ đáng ngại nhất theo đánh giá 74-d**.
- **Gate**: battery v15 vs từng đối thủ mới 10 trận seeds mới 2 ghế → thiết lập baseline; mọi kết luận v16 sau này đều phải benchmark trên bộ đối thủ MỚI.

### H11. Pipeline daily-replay refresh (đuổi theo meta)
- **Gì**: script kéo dataset `kaggressure-episodes-index` (manifest.csv có avg_score) bằng token Kaggle → lọc top-20 Elo →
  extract tape farm/market mới nhất → diff vs tape v15 đang dùng → cảnh báo khi meta dịch chuyển (như 8c6s→9c4s đã diễn ra mà ta không biết).
- **Nguồn**: 3 nhóm top (cjlcjlcjl, georgymarin, raykkretzschmar) đều dùng workflow này — đó là lý do họ đuổi kịp meta.
- **Cost**: ~150 dòng script + cron hàng ngày. **Risk**: 0.
- **Gate**: chạy được 1 lần end-to-end, xuất báo cáo diff tape.

### H12. Hour-0 audit (cluster SELL vào giờ 0)
- **Gì**: kiểm tra phân bổ SELL của v15 theo giờ; nếu đang bán giờ khác, thử dồn một phần về giờ 0 (tick demand kép → giá đỉnh cục bộ).
- **Nguồn**: Kaito v21.1 (63 SELL giờ 0; 199u STRAW đúng giờ 0). **Cost**: audit trước, rồi ~40 dòng nếu worth.
- **Gate**: A/B 20 trận: không tệ hơn, mean dương.

---

## LỘ TRÌNH ĐỀ XUẤT (3 đợt)

```
ĐỢT 1 (ngay):  H1+H4 → H2 → H3        (bolt-on, ~50 dòng tổng, kỳ vọng +$300-1.5k/trận)
               H10 (đối thủ mới — song song, không phụ thuộc)
ĐỢT 2:         H5 (conditional memory)  — cần H11 sẵn data
               H8 (tie-break) — rẻ, làm trong lúc chờ H5 data
ĐỢT 3:         H7 (impact model) → H9 (contested ranking) → H6 (steering) → H12
MỖI ĐỢT: battery đầy đủ seeds mới × 2 ghế × 6 đối thủ (v15, v14, kme3v39, kawashigi, indark_e776, aurax)
          + UI e2e 1 trận + lint + worklog + commit
```

## ĐO LƯỜNG THÀNH CÔNG TỔNG

1. Local battery: v16 thắng ≥8/10 vs **mọi** đối thủ gồm 3 đối thủ mới (H10) — không trận thua nào >$1.5k.
2. Mirror-class (kme3v39): thắng ≥6/10 + không thua liên tiếp cùng cơ chế.
3. Trên Kaggle (nếu user submit): win-rate 14 ngày >60% vs pool mới — theo dõi bằng H11 pipeline.

## RỦI RO CHÍNH & CÁCH XỬ LÝ

- **L38 knife-edge**: mọi layer mới phải provably-inert khi trigger không gặp (như R90 của v15) — smoke test đồng-dollar.
- **L39/L40**: không displace native plans; grace-clock theo hoạt động không theo tuổi pool.
- **Kaito v47 lesson**: đúng 1 child call/turn; smoke "first action non-PASS" sau mỗi bản.
- **Balance change engine** (discussion 34 votes): nếu engine đổi, tape chết — giữ H5/H11 (adaptive + refresh) là bảo hiểm.
