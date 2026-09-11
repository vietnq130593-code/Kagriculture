# v5 "ORCHESTRATOR" — v5.5 (Task 21, 20 Sep): v5.4 + GT-LAND COURNOT + GT LỚP
# LY THUYẾT TRÒ CHƠI 2 CẤP (macro 24-lượt / micro mỗi lượt).
# v5.5 CHANGES (A/B 20-seed two-sided, protocol Task 20):
#   • GT-LAND: đất tối ưu 50 ô (NW+NE, $1k) — đường cong thực nghiệm
#     25/50/75/100 ô = 1.078/1.158/1.112/1.060x. Mua SW+SE ($6k) là lãng phí
#     kép: vốn + lao động + áp lực cung wheat vi phạm monopoly-restraint R37.
#     50 ô chạy đầy ~100% (wheat 13-20 + dâu 18 + 11 thú + melon sớm).
#   • GT-COURNOT MACRO (hour 0-1 mỗi 24 lượt): đọc L2 Gamma-Poisson E/P75
#     mỗi kênh → tín hiệu dump_sig (P75≥8u và ≥1.5×E → front-run ×0.96) /
#     calm_sig + px_pred rising (→ monopoly restraint ×1.04). tm["gt"] hiển
#     thị trong Arena diag.
#   • KẾT QUẢ: vs v4 1.162x/34/40 (85%)/worst 0.879 (từ 1.060x/67.5%);
#     vs v3 1.311x/38/40 (95.0%)/worst 0.974. Paired vs baseline +0.102x
#     (t=4.71, p<0.0002, thắng 17/20 seed).
# v5.3→v5.4 (Task 20): audit engine + E8-lite + px_after + p3_lo minimax +
#   telemetry opp_herd/opp_wnet + 3 thí nghiệm revert (pump/tomato/profiles).
# v5.3: P2 FEED MAKE-VS-BUY hoàn chỉnh + L1 ARCHETYPE 5 LỚP + L2 GAMMA-POISSON.
# Bảy lớp não:
#   L1 archetype posterior (naive Bayes 9 kênh flow + kernel đàn/tiền MIRROR,
#   forgetting 0.8, hysteresis 2 đêm) — STRONG/COOP/PASSIVE/DUMP/MIRROR;
#   L2 Gamma-Poisson E[opp_sales_p] + P25/P75 (thay _flow_pred 3-đêm-tay);
#   L3-Race E[tiền cuối] gap/tier (EMA+dwell) + L3-Price px_pred +3 ngày;
#   L5 sổ KPI + L6 risk guard (F1/F2/F3 + GROW/RECOVER/SURVIVE);
#   L7 núm chiến thuật theo tier/mode.
# P2 FEED WARFARE (bài học A/B đảo ngược giả định kế hoạch): "churn" wheat
#   của v5.2 là VŨ KHÍ zero-sum — áp lực mua nâng mặt giá, đánh thuế vào
#   feedbuy $32-41k của v4 (net-buyer). Ngừng mua = tự giải giáp (−0.12x).
#   Giữ cơ chế mua v5.2 + cap 12u/ngày + đo feedbuy (ledger P2) + L2
#   quantile cho subs + L1 posterior 2 tầng.
# Fallback: mọi lớp não hỏng → nền v4.
import math

CROPS = {
    "WHEAT":      {"seed": 10,  "first_yield_day": 2,  "max_yield_day": 4,  "interval": 0, "max_yield": 6, "ongoing": False},
    "CARROT":     {"seed": 20,  "first_yield_day": 2,  "max_yield_day": 3,  "interval": 0, "max_yield": 4, "ongoing": False},
    "TOMATO":     {"seed": 50,  "first_yield_day": 8,  "max_yield_day": 8,  "interval": 1, "max_yield": 4, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True},
    "MELON":      {"seed": 80,  "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False},
}
ANIMALS = {
    "GOOSE": {"cost": 300, "structure": "COOP",    "first_yield_day": 4, "interval": 1, "max_held": 4, "product": "EGG"},
    "COW":   {"cost": 400, "structure": "PASTURE", "first_yield_day": 8, "interval": 2, "max_held": 6, "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "first_yield_day": 6, "interval": 3, "max_held": 6, "product": "WOOL"},
}
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
MARKET_I0 = 10000
MARKET_PARAMS = {
    "WHEAT":      {"base":  25, "I0": MARKET_I0, "T": 400, "below_func": "sqrt",   "below_target": 0.80, "above_func": "log",    "above_target": 0.20},
    "CARROT":     {"base":  35, "I0": MARKET_I0, "T": 450, "below_func": "hinge",  "below_target": 1.00, "above_func": "sqrt",   "above_target": 0.70},
    "TOMATO":     {"base":  60, "I0": MARKET_I0, "T": 200, "below_func": "hinge",  "below_target": 0.40, "above_func": "sqrt",   "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": MARKET_I0, "T": 100, "below_func": "sqrt",   "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON":      {"base": 250, "I0": MARKET_I0, "T": 300, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.60},
    "EGG":        {"base":  50, "I0": MARKET_I0, "T": 332, "below_func": "hinge",  "below_target": 0.40, "above_func": "log",    "above_target": 0.20},
    "MILK":       {"base": 160, "I0": MARKET_I0, "T": 122, "below_func": "sqrt",   "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL":       {"base": 200, "I0": MARKET_I0, "T": 105, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": MARKET_I0, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}
SHOPS = {
    "BAKERY":         ["EGG", "WHEAT"],
    "PIZZA_SHOP":     ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT":    ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE":     ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
    "PET_CAFE":       ["CARROT"],
    "SMOOTHIE_SHOP":  ["STRAWBERRY", "MILK"],
    "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}
TOWN_CENTER_PRODUCTS = [p for p in PRODUCTS if p != "FERTILIZER"]

TURN_PER_DAY = 24
EPISODE_STEPS = 720
MAX_ORDERS = 10
SHED_CAP = 100
LAND_PRICES = [1000, 2000, 4000]
MAX_SHOP_INSTANCES = 8

# v5.4 (audit 20 Sep): WHEAT 5 là ảo — engine tối đa 4 (tưới đủ window 2-4);
# đo thực tế từ battle trace: parity-watering cho ~3.0u/cycle (428u / ~140 cycle).
# CYCLE_LEN MELON 13 → 11 (plant d0 → thu tối ưu d10, decay d13; hằng chết, sửa cho đúng).
CYCLE_LEN = {"WHEAT": 5, "CARROT": 4, "TOMATO": 12, "STRAWBERRY": 17, "MELON": 11}
YIELD_PER_CYCLE = {"WHEAT": 3.0, "CARROT": 3, "TOMATO": 4, "STRAWBERRY": 4, "MELON": 6}

T_WATER_CRIT = 0
T_SERVICE_URG = 0
T_HARVEST_URG = 2
T_DELIVER = 2
T_BUILD_URG = 2
T_SERVICE = 2
T_WATER_YIELD = 3
T_BUILD = 4
T_HARVEST_ANIMAL = 2
T_HARVEST = 5
T_PLANT = 5
T_DIG = 5
T_WATER_MAINT = 3
T_FERTILIZE = 7

FERT_SELL = True
FERT_FLOOR = 38
ANIMAL_CAP = 16
TOM_QUOTA = 6
HOLD = {"MILK": 0.98, "WOOL": 0.94, "STRAWBERRY": 0.90, "EGG": 0.86,
        "CARROT": 0.70, "WHEAT": 0.76, "MELON": 0.52, "TOMATO": 0.82, "FERTILIZER": 0.40}

_STATE = {}
_ARCHES = ("CONTEST", "MIRROR")  # v5: P0 — xóa COOP/PASSIVE chết, mở lại ở P1 với 5 lớp


def _gauss(x, c, s):
    s = max(1e-6, float(s))
    return math.exp(-0.5 * ((float(x) - float(c)) / s) ** 2)


def _tm_step(tm, step, inv, shops):
    try:
        tm["shops"] = list(shops or [])  # v5-P1 FIX: drain town cần shop hiện tại
        prev = tm.get("prev_inv")
        if prev is not None and tm.get("prev_step") == step - 1:
            drain = _drain_at(step - 1, tm.get("shops") or [])
            ms = tm.get("my_sells") or {}
            mb = tm.get("my_buys") or {}
            od = tm.setdefault("opp_day", {})
            for p in PRODUCTS:
                delta = inv.get(p, MARKET_I0) - prev.get(p, MARKET_I0)
                od[p] = od.get(p, 0.0) + delta + drain.get(p, 0.0) - ms.get(p, 0.0) + mb.get(p, 0.0)
        mds = tm.setdefault("my_day_sales", {})  # v5: L5 — tích lũy bán của tôi theo ngày
        ms0 = tm.get("my_sells") or {}
        for p in PRODUCTS:
            mds[p] = mds.get(p, 0.0) + ms0.get(p, 0.0)
        if step % 24 == 0 and step > 0:
            tm.setdefault("opp_daily", {})[step // 24 - 1] = dict(tm.get("opp_day") or {})
            tm["opp_day"] = {}
            tm.setdefault("my_daily", {})[step // 24 - 1] = dict(tm.get("my_day_sales") or {})  # v5
            tm["my_day_sales"] = {}
        tm["prev_inv"] = {p: inv.get(p, MARKET_I0) for p in PRODUCTS}
        tm["prev_step"] = step
        tm["my_sells"] = {}
        tm["my_buys"] = {}
    except Exception:
        pass


def _tm_orders(tm, orders):
    try:
        ms = tm.setdefault("my_sells", {})
        mb = tm.setdefault("my_buys", {})
        for o in orders or []:
            if not isinstance(o, (list, tuple)) or len(o) < 3:
                continue
            op, item, n = o[0], o[1], o[2]
            if op == "SELL" and item in PRODUCTS and _is_num(n):
                ms[item] = ms.get(item, 0.0) + int(n)
            elif op == "BUY_PRODUCT" and item in PRODUCTS and _is_num(n):
                mb[item] = mb.get(item, 0.0) + int(n)
    except Exception:
        pass


def _bayes_step(tm, day, opp_farm, my_herd, my_money):
    """v5.3 L1 ARCHETYPE POSTERIOR (PLAN §4.1) — 5 giả thuyết đầy đủ:
    MIRROR (twin bit-identical) · CONTEST/STRONG (dòng v3/v4) · COOP ·
    PASSIVE · DUMP. Kiến trúc 2 tầng chống lỗi scale (bài học v5.3-r1:
    kernel MIRROR ~0.5 vs tích Poisson 9 kênh ~1e-10 không nhân chung
    được → posterior MIRROR vọt 0.99 khi đấu v4 → tắt hết núm compete):

    Tầng 1 (pm — giữ NGUYÊN v5.2 đã kiểm chứng): kernel đàn+tiền phát
    hiện twin. MIRROR chỉ bật khi pm > 0.70, đàn đối thủ không vượt +2,
    sau ngày 8. Tầng 2 (flow posterior): naive Bayes 9 kênh Poisson quanh
    hồ sơ flow kỳ vọng (white-box v3/v4 + traces) — softmax có nhiệt độ
    τ=5 (một đêm chứng cứ không đập posterior), quên λ=0.8, hysteresis
    2 đêm P>0.6. O(9×|H|)/đêm."""
    try:
        tm["mode"] = tm.get("mode", "CONTEST")
        od = tm.get("opp_daily") or {}
        xs = (od.get(day - 1) or {}) if day >= 2 else {}
        # ---- tầng 1: pm twin-kernel (v5.2 NGUYÊN TRẠNG) ----
        oc = og = osp = 0
        opp_tiles = _g(opp_farm, "tiles", None) if opp_farm else None
        if opp_tiles:
            for row in opp_tiles:
                for t in row:
                    if isinstance(t, dict) and "animal" in t:
                        a = t.get("animal")
                        if a == "COW":
                            oc += 1
                        elif a == "GOOSE":
                            og += 1
                        elif a == "SHEEP":
                            osp += 1
        opp_money = float(_g(opp_farm, "money", 0) or 0) if opp_farm else 0.0
        mc, mg, msp = my_herd
        try:  # v5.4 Phase 5.3: lưu đàn đối thủ cho gate pump (feed warfare)
            tm["opp_herd"] = oc + og + osp
        except Exception:
            pass
        money_ratio = (opp_money / my_money) if my_money > 300.0 else 1.0
        sig = (_gauss(oc - mc, 0.0, 0.8)
               * _gauss(og - mg, 0.0, 1.0)
               * _gauss(osp - msp, 0.0, 0.8)
               * _gauss(money_ratio, 1.0, 0.07)
               * _gauss(len(opp_tiles or []) and 1.0 or 0.0, 1.0, 0.05))
        like_m = max(0.005, min(0.98, sig))
        like_c = max(0.05, 1.0 - 0.75 * like_m)
        pm = tm.get("pm", 0.08)
        pm = (pm ** 0.8) * (like_m / (like_m + like_c))
        pm = min(0.99, max(0.005, pm))
        tm["pm"] = pm
        # ---- tầng 2: flow posterior 4 giả thuyết (softmax τ=5) ----
        PROFILES = {
            "CONTEST": {"WHEAT": 25, "CARROT": 3, "TOMATO": 1, "STRAWBERRY": 2,
                        "MELON": 3, "EGG": 4, "MILK": 2, "WOOL": 1, "FERTILIZER": 5},
            "COOP":    {"WHEAT": 12, "CARROT": 2, "TOMATO": 1, "STRAWBERRY": 2,
                        "MELON": 2, "EGG": 3, "MILK": 2, "WOOL": 1, "FERTILIZER": 2},
            "PASSIVE": {"WHEAT": 3, "CARROT": 2, "TOMATO": 1, "STRAWBERRY": 1,
                        "MELON": 2, "EGG": 1, "MILK": 1, "WOOL": 1, "FERTILIZER": 1},
            "DUMP":    {"WHEAT": 45, "CARROT": 12, "TOMATO": 4, "STRAWBERRY": 6,
                        "MELON": 8, "EGG": 10, "MILK": 6, "WOOL": 3, "FERTILIZER": 12},
        }
        l1 = tm.setdefault("l1f", {h: 0.25 for h in
                                   ("CONTEST", "COOP", "PASSIVE", "DUMP")})
        # v5.3 WARMUP GUARD (bài học seed 111: flow v4 lúc d2-5 đang ramp —
        # giống PASSIVE → posterior vọt 0.99 sai → flip mode tắt núm compete).
        # Chỉ phân loại khi đủ chứng cứ: ngày ≥ 7 VÀ tổng flow quan sát ≥ 50u
        cum = 0.0
        for k, dd in (od or {}).items():
            if isinstance(k, int) and isinstance(dd, dict):
                cum += sum(max(0.0, float(v)) for v in dd.values()
                           if isinstance(v, (int, float)))
        if xs and day >= 7 and cum >= 50.0:
            lls = {}
            lr = math.log(max(0.05, money_ratio))
            for h, prof in PROFILES.items():
                ll = 0.0
                for p in PRODUCTS:
                    mu = max(0.5, float(prof.get(p, 0.5)))
                    x = max(0.0, float(xs.get(p, 0.0)))
                    ll += x * math.log(mu) - mu - math.lgamma(x + 1.0)
                lls[h] = ll
            # kênh tiền (trọng số 1:1 với 9 kênh Poisson — mỗi kênh ~0-6 nats):
            # CONTEST sống ~1:1; PASSIVE tích lũy chậm ~0.55
            lls["PASSIVE"] += math.log(max(1e-6, _gauss(lr, math.log(0.55), 0.5)))
            lls["CONTEST"] += math.log(max(1e-6, _gauss(lr, 0.0, 0.55)))
            m_ll = max(lls.values())
            tau = 5.0
            post = {}
            for h, ll in lls.items():
                prior = max(1e-4, float(l1.get(h, 0.25))) ** 0.8
                post[h] = prior * math.exp((ll - m_ll) / tau)
            s = sum(post.values())
            for h in post:
                l1[h] = min(0.99, post[h] / s)
            tm["l1f"] = l1
        # ---- ghép mode: MIRROR (tầng 1) >> flow-mode (tầng 2) ----
        # v5.3 CỔNG CẤU TRÚC (bài học seed 111/115: cùng là v4 nhưng mix
        # wheat theo seed khác nhau → flow-ll đọc nhầm PASSIVE/COOP rồi khóa
        # mode sai cả mùa; v4 không bao giờ thỏa điều kiện cấu trúc dưới).
        # Mode chỉ rời CONTEST khi CỬA 2 đêm + BẰNG CHỨNG CẤU TRÚC:
        #   PASSIVE: P>0.75 hai đêm + tiền đối thủ < 45% mình (thật sự yếu)
        # COOP/DUMP: posterior tính + hiển thị (diag/Phase 5) nhưng KHÔNG
        # đổi playbook khi đấu v4 — chờ validation trên thư viện bot.
        cand_h = max(l1, key=lambda h: l1[h])
        cand_p = float(l1[cand_h])
        prev_mode = str(tm.get("mode", "CONTEST"))
        pend = tm.get("l1_pend") or {}
        if cand_h == prev_mode:
            new_mode = cand_h
            tm["l1_pend"] = None
        else:
            confirmed_2nights = (pend.get("h") == cand_h
                                 and int(pend.get("day", -9)) == day - 1
                                 and cand_p > 0.75)
            if confirmed_2nights:
                tm["l1_pend"] = None
                if cand_h == "PASSIVE" and money_ratio < 0.45:
                    new_mode = "PASSIVE"  # nghèo thật + flow thật sự nhỏ
                    tm["mode_note"] = f"PASSIVE cấu trúc (P={cand_p:.2f}, mr={money_ratio:.2f})"
                else:
                    new_mode = prev_mode if prev_mode != "PASSIVE" else "CONTEST"
            else:
                new_mode = prev_mode
                tm["l1_pend"] = {"h": cand_h, "day": day}
        if new_mode == "MIRROR":
            new_mode = "CONTEST"
        # MIRROR chỉ khi kernel twin đủ mạnh + đàn đối thủ không vượt + sau d8
        opp_herd_n = oc + og + osp
        my_herd_n = mc + mg + msp
        if day >= 8 and pm > 0.70 and opp_herd_n <= my_herd_n + 1:
            new_mode = "MIRROR"
            tm["mode_note"] = f"twin detected (pm={pm:.2f})"
        elif prev_mode == "MIRROR" and (pm < 0.35 or opp_herd_n > my_herd_n + 2):
            new_mode = cand_h if cand_p > 0.6 else "CONTEST"
            tm["mode_note"] = "mirror exit"
        if new_mode != prev_mode:
            tm["mode_note"] = f"l1 → {new_mode} (P={cand_p:.2f}, pm={pm:.2f})"
        tm["mode"] = new_mode
        tm["l1_top"] = [cand_h, round(cand_p, 3)]
    except Exception:
        pass


# ----------------------------------------------------------------------------
# v5: L5 SELF-ASSESSMENT ("gương soi") + L6 RISK GUARD lõi F1/F2/F3
# ----------------------------------------------------------------------------

def _l2_night(tm, day):
    """v5.3 L2 GAMMA-POISSON (PLAN §4.2): posterior predictive dòng bán đối thủ.

    Quan sát x_p = net-flow bán của đối thủ ngày qua (telemetry $0-residual).
    Conjugate có suy biến λ=0.8 (geometric forgetting — đối thủ đổi chiến
    thuật giữa trận):  a ← 0.8·a + x,  b ← 0.8·b + 1.
    Predictive = Negative Binomial: mean = a/b, var = mean + mean²/b
    (overdispersion đúng nghĩa count-flow — không còn nhân hệ số tay 1.3).
    Đưa ra E[x] + P25/P75 — minimax: quota bán dùng P75 (thận trọng), quy
    hoạch đàn dùng P25. Kèm M-11 calibration: MAE dự báo đêm trước vs thực
    tế (não tự biết mình sai bao nhiêu). O(9) phép/đêm — rẻ hơn 1 lượt WATER."""
    try:
        od = tm.get("opp_daily") or {}
        l2 = tm.setdefault("l2", {})
        prev = tm.get("l2_pred_prev") or {}
        errs = []
        for p in PRODUCTS:
            a, b = l2.get(p) or (1.5, 1.0)
            x = max(0.0, float((od.get(day - 1) or {}).get(p, 0.0)))
            if prev and day >= 2:
                e0 = (prev.get(p) or {}).get("e")
                if e0 is not None:
                    errs.append(abs(float(e0) - x))
            a = 0.8 * a + x
            b = 0.8 * b + 1.0
            l2[p] = (a, b)
        if errs:
            tm["l2_mae"] = round(sum(errs) / len(errs), 2)
        out = {}
        for p in PRODUCTS:
            a, b = l2[p]
            m = a / max(1e-6, b)
            sd = math.sqrt(m + m * m / max(1e-6, b))
            out[p] = {"e": round(m, 2),
                      "p25": round(max(0.0, m - 0.674 * sd), 2),
                      "p75": round(m + 0.674 * sd, 2)}
        tm["l2_pred"] = out
        tm["l2_pred_prev"] = {p: dict(v) for p, v in out.items()}
        return out
    except Exception:
        return None


def _flow_pred(tm, day):
    """v5.3: GIỮ NGUYÊN v5.2 (hành vi đã chứng minh 1.058x) — trung bình 3 đêm
    với suy biến λ=0.8, nhân hệ số thận trọng 1.3 (minimax). L2 Gamma-Poisson
    (_l2_night/_flow_q) chạy SONG SONG như OBSERVER: đo lường + calibration
    MAE + phân vị cho diag — coupling hành vi chờ Phase 5 sau khi học profile
    offline (bài học v5.3-r1..r4: mọi coupling sớm đều −0.02-0.04x trên 20 seed
    vì benchmark v4 không phân biệt được các giả thuyếtflow).
    Trả None khi chưa đủ 3 đêm hoặc tổng dòng < 12 đơn vị."""
    try:
        od = tm.get("opp_daily") or {}
        ks = sorted(k for k in od if isinstance(k, int) and k < day)
        if len(ks) < 3:
            return None
        tot = 0.0
        for k in ks[-3:]:
            tot += sum(max(0.0, v) for v in (od.get(k) or {}).values())
        if tot < 12.0:
            return None
        w = [0.64, 0.8, 1.0]
        out = {p: 0.0 for p in PRODUCTS}
        for i, k in enumerate(ks[-3:]):
            d = od.get(k) or {}
            for p in PRODUCTS:
                out[p] += w[i] * max(0.0, float(d.get(p, 0.0)))
        s = sum(w)
        return {p: 1.3 * out[p] / s for p in PRODUCTS}
    except Exception:
        return None


def _flow_q(tm, day, q):
    """v5.3 L2: phân vị P25/P75 dòng bán đối thủ (minimax chọn theo quyết
    định) — None khi l2 chưa sẵn sàng (caller tự fallback E)."""
    try:
        l2 = tm.get("l2_pred")
        if l2 and day >= 5:
            return {p: float((l2.get(p) or {}).get(q, 0.0)) for p in PRODUCTS}
    except Exception:
        pass
    return None


def _project(sa, day, money, tm, days_left):
    """v5.2 L3-Race (trọng tâm 1): BAYES ĐÁNH GIÁ KẾT QUẢ chiến lược hiện tại.

    Từ run-rate doanh thu của TÔI (ledger chính xác) và ĐỐI THỦ (luồng bán
    quan sát được × giá) — làm MỀM bằng EMA α=0.45 (chống giật tier khi bán
    theo đợt) — ngoại suy E[tiền cuối mùa] cả 2 bên, trần theo pipeline còn
    lại. Kết quả: gap + tier LEAD/TIGHT/BEHIND. Tier chỉ đổi khi 2 ĐÊM LIÊN
    TIẾP cùng tín hiệu (dwell) — v5.1 flip-flop LEAD→BEHIND→LEAD trong 4 đêm
    làm núm chiến thuật giật liên tục (bài học seed 2). Kèm CALIBRATION: so
    dự báo E[tiền] đêm trước với tiền thực tế hôm nay → MAE cho não tự biết
    mình đo sai bao nhiêu (vòng học đóng M-11)."""
    try:
        rh = sa.get("rev_hist") or []
        if len(rh) < 4 or day < 12:
            return None
        rec = rh[-4:]
        w = [0.6, 0.8, 1.1, 1.3]
        sw = sum(w)
        my_r_now = sum(w[i] * rec[i][1] for i in range(4)) / sw
        op_r_now = sum(w[i] * rec[i][2] for i in range(4)) / sw
        # v5.2: EMA làm mượt run-rate (bán theo đợt làm run-rate nhảy vọt ±50%)
        ema = sa.setdefault("ema_r", {})
        a = 0.45
        ema["my"] = a * my_r_now + (1 - a) * float(ema.get("my", my_r_now))
        ema["opp"] = a * op_r_now + (1 - a) * float(ema.get("opp", op_r_now))
        my_r = float(ema["my"])
        op_r = float(ema["opp"])

        # v5.2 CALIBRATION: dự báo e_me của ĐÊM TRƯỚC vs tiền thật HÔM NAY
        prev_proj = sa.get("proj") or {}
        if prev_proj.get("e_me") and day >= 13:
            try:
                err = abs(float(prev_proj["e_me"]) - float(money))
                hist = sa.setdefault("calib", [])
                hist.append(round(err))
                del hist[:-8]
                sa["calib_mae"] = round(sum(hist) / len(hist))
            except Exception:
                pass

        def growth(vals):
            older = sum(v for v in vals[:2]) + 1.0
            newer = sum(v for v in vals[2:]) + 1.0
            return max(1.0, min(1.3, newer / older))

        gm = growth([r[1] for r in rec])
        go = growth([r[2] for r in rec])
        om = float(tm.get("opp_money", 0) or 0)
        e_me = money + min(my_r * days_left * (0.6 + 0.4 * gm),
                           1.15 * float(tm.get("pipe_val_me", 1e9) or 1e9))
        e_opp = om + min(op_r * days_left * (0.6 + 0.4 * go),
                         1.35 * float(tm.get("pipe_val_opp", 1e9) or 1e9))
        gap = e_me - e_opp
        rel = gap / max(1000.0, e_opp)
        prev = (sa.get("proj") or {}).get("tier")

        def raw_tier():
            if prev == "BEHIND":
                return "BEHIND" if rel < -0.04 else ("TIGHT" if rel < 0.06 else "LEAD")
            if prev == "LEAD":
                return "LEAD" if rel > 0.04 else ("TIGHT" if rel > -0.06 else "BEHIND")
            return "LEAD" if rel > 0.08 else ("BEHIND" if rel < -0.08 else "TIGHT")

        cand = raw_tier()
        # v5.2 DWELL 2 ĐÊM: tier chỉ đổi khi tín hiệu lặp lại 2 đêm liên tiếp
        pend = sa.get("pending_tier") or {}
        tier = prev or cand
        if cand == prev or prev is None:
            tier = cand
            sa["pending_tier"] = None
        elif pend and pend.get("tier") == cand and day - int(pend.get("day", 0)) <= 1:
            tier = cand
            sa["pending_tier"] = None
        else:
            sa["pending_tier"] = {"tier": cand, "day": day}
        return {"day": day, "me": round(e_me), "opp": round(e_opp),
                "e_me": round(e_me), "gap": round(gap), "rel": round(rel, 3),
                "tier": tier, "cand": cand,
                "r_me": round(my_r), "r_opp": round(op_r),
                "calib_mae": sa.get("calib_mae")}
    except Exception:
        return None


def _px_pred(tm, day, inv, prices, shops):
    """v5-P1 L3-Price (trọng tâm 1): dự báo giá mỗi mặt hàng sau ~3 ngày.

    drift/ngày = E[opp net flow] (Bayes, bỏ hệ số thận trọng 1.3) − town absorb
    trung bình/ngày. inv+3×drift → _price() cho giá tương lai. Đây là "kết quả
    thị trường" của chiến lược đối thủ nếu họ tiếp tục — đầu vào cho front-run.
    v5.4 Phase 5.1b: thêm p3_lo (minimax P25 — KHÔNG tin shop tương lai,
    absorb chỉ từ shop đã mở + town center) để các núm mua có cột mốc bi quan."""
    try:
        fp = _flow_pred(tm, day)
        if not fp:
            return None
        fp = {p: v / 1.3 for p, v in fp.items()}
        absorb = _forward_absorb(day, 0, shops)
        absorb_lo = _forward_absorb(day, 0, shops, expected=False)
        days_left = max(1, 29 - day)
        out = {}
        for p in PRODUCTS:
            if p == "FERTILIZER":
                continue
            now = float(prices.get(p, 0) or 0)
            if now <= 0:
                continue
            drift = fp.get(p, 0.0) - absorb.get(p, 0.0) / days_left
            inv3 = float(inv.get(p, MARKET_I0)) + 3.0 * drift
            p3 = float(_price(p, inv3))
            drift_lo = fp.get(p, 0.0) - absorb_lo.get(p, 0.0) / days_left
            inv3_lo = float(inv.get(p, MARKET_I0)) + 3.0 * drift_lo
            p3_lo = float(_price(p, inv3_lo))
            out[p] = {"now": round(now), "p3": round(p3), "p3_lo": round(p3_lo)}
        return out
    except Exception:
        return None


def _sa_step(state, day, hour, money):
    """v5 L5: sổ KPI từng lượt — phân loại mọi biến động tiền thành income/spend
    (dùng chênh lệch tiền giữa 2 lượt liên tiếp → residual $0)."""
    try:
        sa = state.setdefault("sa", {})
        prev = sa.get("prev_money")
        pd = sa.get("prev_day")
        if prev is None:
            sa["prev_money"] = float(money)
            sa["prev_day"] = day
            return
        d = float(money) - float(prev)
        if d:
            book = pd if (hour == 0 and pd is not None and pd == day - 1) else day
            led = sa.setdefault(("ledger", book), {"income": 0.0, "spend": 0.0})
            if d > 0:
                led["income"] += d
            else:
                led["spend"] += -d
        sa["prev_money"] = float(money)
        sa["prev_day"] = day
    except Exception:
        pass


def _sa_night(state, day, tm, prices):
    """v5 L5: tổng KPI cuối ngày + điểm sức khỏe H ∈ [0,1] (4 thành phần có trọng số).
    v5-P1: thêm rev_hist (doanh thu 2 bên) + L3-Race projection (E[final] gap/tier)
    + L3-Price dự báo giá → mọi số liệu này là "kết quả dự kiến của chiến lược"."""
    try:
        sa = state.get("sa", {})
        led = sa.setdefault(("ledger", day), {"income": 0.0, "spend": 0.0})
        income = float(led.get("income", 0.0))
        spend = float(led.get("spend", 0.0))
        led["net"] = income - spend
        hist = sa.setdefault("net_hist", [])
        hist.append((day, income - spend))
        if len(hist) > 12:
            del hist[:len(hist) - 12]
        money = float(sa.get("prev_money", 0) or 0)
        daily_spend = spend if spend > 50 else 300.0
        h_money = max(0.05, min(1.0, money / (3.0 * daily_spend)))
        rec = [n for (_, n) in hist[-4:-1]] or [0.0]
        avg_prev = sum(rec) / len(rec)
        h_rev = 1.0 if income >= max(200.0, avg_prev) else max(0.15, income / max(200.0, avg_prev))
        md = tm.get("my_daily", {}) or {}
        odd = tm.get("opp_daily", {}) or {}
        my_t = md.get(day) or {}
        op_t = odd.get(day) or {}
        my_sum = sum(max(0.0, float(v)) for v in my_t.values() if isinstance(v, (int, float)))
        op_sum = sum(max(0.0, float(v)) for v in op_t.values() if isinstance(v, (int, float)))
        share = my_sum / (my_sum + op_sum) if (my_sum + op_sum) > 5 else 0.45
        h_share = max(0.0, min(1.0, share / 0.45))
        risk = state.get(("risk", day), {}) or {}
        h_assets = max(0.0, 1.0 - 0.10 * float(risk.get("water_crit_late", 0) or 0)
                       - 0.25 * float(risk.get("hungry_late", 0) or 0))
        H = max(0.0, min(1.0, 0.30 * h_money + 0.25 * h_rev + 0.20 * h_share
                         + 0.25 * max(0.0, h_assets)))
        sa["H"] = round(H, 3)
        sa["H_parts"] = {"money": round(h_money, 2), "revenue": round(h_rev, 2),
                         "share": round(share, 2), "assets": round(max(0.0, h_assets), 2)}
        # v5-P1 L3: doanh thu quan sát được 2 bên (tôi: ledger chính xác;
        # đối thủ: luồng bán × giá hiện tại — ước lượng Bayes)
        px = {p: float(prices.get(p, 0) or 0) for p in PRODUCTS} if prices else {}
        odd_d = odd.get(day) or {}
        opp_rev = sum(max(0.0, float(v)) * px.get(p, 0.0)
                      for p, v in odd_d.items() if isinstance(v, (int, float)))
        rh = sa.setdefault("rev_hist", [])
        rh.append((day, income, opp_rev))
        if len(rh) > 10:
            del rh[:len(rh) - 10]
        proj = _project(sa, day, money, tm, max(1, 29 - day))
        sa["proj"] = proj
        if proj:
            tm["proj"] = proj  # v5-P1: chia sẻ cho _daily_plan/_build_orders/diag
    except Exception:
        pass


def _rg_note(rg, msg):
    try:
        notes = rg.setdefault("notes", [])
        if not notes or notes[-1] != msg:
            notes.append(msg)
            del notes[:-8]
    except Exception:
        pass


def _rg_night(state, day, money, tm):
    """v5 L6 (đêm): F1 death-spiral + F3 crop cascade + meta state GROW/RECOVER/SURVIVE
    + điều kiện thoát bắt buộc (không được phép kẹt trạng thái khẩn cấp quá 3 ngày)."""
    try:
        sa = state.get("sa", {})
        rg = state.setdefault("rg", {"F1": 0, "F2": 0, "F3": 0, "state": "GROW",
                                     "state_since": day, "liquidate": False})
        led1 = sa.get(("ledger", day - 1)) or {}
        led2 = sa.get(("ledger", day - 2)) or {}
        net1 = float(led1.get("net", 0.0))
        net2 = float(led2.get("net", 0.0))
        inc1 = float(led1.get("income", 0.0))
        inc2 = float(led2.get("income", 0.0))
        # v5: chữ ký death-spiral THẬT = thu nhập vắng 2 ngày liền + tiền ghim sát đáy
        # (giai đoạn bootstrap d8-13 vay nợ sâu là BÌNH THƯỜNG — thu nhập vẫn tăng;
        # bài học seed 123: F1 bắn nhầm vào bootstrap làm chậm ramp = thua cả trận)
        f1 = 0
        if day >= 10 and money < 100 and inc1 < 80 and inc2 < 80:
            f1 = 1
        if day >= 12 and money < 50 and inc1 < 50 and inc2 < 50 and net1 < 0 and net2 < 0:
            f1 = 2
        if day >= 14 and money < 25 and inc1 < 30 and inc2 < 30 and net2 < 0:
            f1 = 3
        if f1 != int(rg.get("F1", 0) or 0):
            _rg_note(rg, f"F1 L{f1}: cash ${money:.0f}, thu d-1 ${inc1:.0f}")
        rg["F1"] = f1
        risk = state.get(("risk", day - 1), {}) or {}
        wc = int(risk.get("water_crit_late", 0) or 0)
        # v5: ngưỡng nâng lên 6/10/15 — parity watering của v4 tự xử 3-5 cây crit;
        # chỉ cascade THẬT (thiếu lao động kéo dài) mới cần throttle
        f3 = 0
        if wc >= 6:
            f3 = 1
        if wc >= 10:
            f3 = 2
        if wc >= 15:
            f3 = 3
        if f3 != int(rg.get("F3", 0) or 0):
            _rg_note(rg, f"F3 L{f3}: {wc} cây nguy cơ tưới cuối ngày")
        rg["F3"] = f3
        mx = max(int(rg.get("F1", 0) or 0), int(rg.get("F2", 0) or 0), int(rg.get("F3", 0) or 0))
        st = "SURVIVE" if mx >= 3 else ("RECOVER" if mx >= 1 else "GROW")
        if st != str(rg.get("state", "GROW")):
            rg["state"] = st
            rg["state_since"] = day
            _rg_note(rg, f"meta → {st}")
        stuck = day - int(rg.get("state_since", day) or day)
        if str(rg.get("state")) in ("RECOVER", "SURVIVE") and stuck >= 3 and not rg.get("liquidate"):
            rg["liquidate"] = True
            _rg_note(rg, f"kẹt {stuck} ngày → LIQUIDATE (lối thoát cưỡng bức)")
        if str(rg.get("state")) == "GROW" and rg.get("liquidate"):
            rg["liquidate"] = False
    except Exception:
        pass


def _rg_live(state, day, hour, tiles, shed, inventories):
    """v5 L6 (mỗi lượt): F2 feed crunch — đại lượng vật lý, không cần hysteresis."""
    try:
        rg = state.setdefault("rg", {"F1": 0, "F2": 0, "F3": 0, "state": "GROW",
                                     "state_since": day, "liquidate": False})
        animals_n = 0
        hungry = 0
        for row in (tiles or []):
            for t in row:
                if isinstance(t, dict) and "animal" in t:
                    animals_n += 1
                    if (t.get("consecutive_unfed", 0) or 0) >= 1 and not t.get("fed_today", False):
                        hungry += 1
        wheat = ((shed or {}).get("WHEAT", 0) or 0) + sum(
            (u.get("WHEAT", 0) or 0) for u in (inventories or []) if isinstance(u, dict))
        rk = state.setdefault(("risk", day), {})
        if hour >= 18:
            rk["hungry_late"] = max(int(rk.get("hungry_late", 0) or 0), hungry)
        supply = (wheat / animals_n) if animals_n else 99.0
        f2 = 0
        # v5: chuẩn theo điểm vận hành JIT của v4 (~2 ngày tồn cám là BÌNH THƯỜNG,
        # không phải tín hiệu khẩn cấp); hết mùa (d>=26) tự cắt — tiết kiệm cám
        # cho đàn không còn kịp hoàn vốn, đúng nhịp culling ngầm của v4
        if 0 < animals_n and day < 26:
            if supply < 1.2 or (hungry >= 2 and hour >= 14):
                f2 = 1
            if supply < 0.8 or hungry >= 3:
                f2 = 2
            if supply < 0.4 or hungry >= 5:
                f2 = 3
        if f2 != int(rg.get("F2", 0) or 0):
            _rg_note(rg, f"F2 L{f2}: {animals_n} thú, wheat {wheat:.0f} ({supply:.1f} ngày)")
        rg["F2"] = f2
        return rg
    except Exception:
        return state.get("rg", {})


def _g(o, k, d=None):
    try:
        if isinstance(o, dict):
            return o.get(k, d)
        return getattr(o, k, d)
    except Exception:
        return d


def _mk(tier, x, y, op, **kw):
    d = {"tier": tier, "x": x, "y": y, "op": op}
    d.update(kw)
    return d


def _fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _step_toward(fx, fy, tx, ty):
    if fx < tx:
        return "EAST"
    if fx > tx:
        return "WEST"
    if fy < ty:
        return "SOUTH"
    if fy > ty:
        return "NORTH"
    return None


def _shed_tiles(board):
    h = board // 2
    return [(h - 1, h - 1), (h, h - 1), (h - 1, h), (h, h)]


def _nearest_shed_tile(x, y, board):
    return min(_shed_tiles(board), key=lambda t: abs(t[0] - x) + abs(t[1] - y))


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _shape(func, x, T=None):
    x = max(0.0, x)
    if func == "linear":
        return x
    if func == "sq":
        return x * x
    if func == "sqrt":
        return math.sqrt(x)
    if func == "log":
        return math.log(1.0 + x)
    if func == "log10":
        return math.log10(1.0 + x)
    if func == "hinge":
        if not T or T <= 0:
            return x
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def _price(item, inventory):
    p = MARKET_PARAMS[item]
    base, I0, T = p["base"], p["I0"], p["T"]
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _shape(f, T, T)
        pr = base + amp * _shape(f, I0 - inventory, T)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _shape(f, T, T)
        pr = base - amp * _shape(f, inventory - I0, T)
    return max(1, int(round(pr)))


def _sell_count(item, n_avail, inv, thresh):
    k = 0
    while k < n_avail:
        if _price(item, inv + k) < thresh:
            break
        k += 1
    return k


_ABOVE_CACHE = {}


def _above_headroom(item, frac):
    key = (item, frac)
    if key not in _ABOVE_CACHE:
        thresh = frac * MARKET_PARAMS[item]["base"]
        k = 0
        while k < 20000 and _price(item, MARKET_I0 + k) >= thresh:
            k += 1
        _ABOVE_CACHE[key] = k
    return _ABOVE_CACHE[key]


# ---- Phase 5.1a: impact giá chính xác + 5.2 E8-lite + 5.1b shop posterior ----

def _rev_stream(item, inv, k):
    """Phase 5.1a (RULES R29/R33): doanh thu THẬT khi bán k unit — engine quote
    từng unit tại pre-sell inventory (đã audit khớp engine 100%). O(k)."""
    tot = 0
    for j in range(int(k)):
        tot += _price(item, inv + j)
    return tot


def _px_after(item, inv, k):
    """Phase 5.1a: giá biên sau khi bán k unit (glut side)."""
    return _price(item, inv + k)


def _pipe_rest(tiles, day):
    """Phase 5.2 E8-lite: nguồn cung CHỜ THU còn lại trước hết mùa (theo item).
    Ước lượng: cây one-time chua thu ~2u (đã tưới window), ongoing = yu trên
    cây + số lần hẹn còn × ~1.3; thú = yu + số lần sản xuất còn (theo interval
    từ placed_day) × ~1.3, cap max_held×2. Chỉ dùng cho gate thanh lý d22-27."""
    out = {it: 0.0 for it in PRODUCTS}
    try:
        if not tiles:
            return out
        for row in tiles:
            for t in row:
                if not isinstance(t, dict):
                    continue
                if t.get("kind") == "PLANT":
                    crop = t.get("crop")
                    cd = CROPS.get(crop)
                    if not cd:
                        continue
                    age = day - t.get("planted_day", day)
                    yu = float(t.get("yield_units", 0) or 0)
                    if cd["ongoing"]:
                        mls = t.get("max_lifespan_step", -1)
                        days_left = max(0, (mls - day * TURN_PER_DAY) // TURN_PER_DAY + 1) if mls >= 0 else 0
                        out[crop] += yu + 1.3 * max(0, days_left)
                    else:
                        out[crop] += yu if age > cd["max_yield_day"] else max(yu, 2.0)
                elif "animal" in t:
                    ad = ANIMALS.get(t.get("animal"))
                    if not ad:
                        continue
                    yu = float(t.get("yield_units", 0) or 0)
                    first = ad["first_yield_day"]
                    itv = max(1, ad["interval"])
                    age = day - t.get("placed_day", day)
                    n_prod = 0
                    a = max(age, first)
                    while a <= 28:
                        if (a - first) % itv == 0:
                            n_prod += 1
                        a += 1
                    out[ad["product"]] += yu + min(2.0 * ad["max_held"], 1.3 * n_prod)
    except Exception:
        pass
    return out


def _shop_slots_left(shops, day):
    """Phase 5.1b (RULES R38): số slot unlock còn lại + ngày unlock kế (uniform
    with replacement, cap 8). P(1 shop cụ thể trong 1 slot) = 1/8 — dùng cho
    minimax p3_lo (không tin shop tương lai) và confidence knobs."""
    try:
        n_used = len(shops or [])
        n_slots = max(0, MAX_SHOP_INSTANCES - n_used)
        days = [d for d in range(day + 1, 30) if d % 3 == 0][:n_slots]
        return {"slots": n_slots, "next_days": days}
    except Exception:
        return {"slots": 0, "next_days": []}


def _shop_vector(shops):
    v = {it: 0.0 for it in PRODUCTS}
    for s in shops:
        prods = SHOPS.get(s, [])
        m = 2 if len(prods) == 1 else 1
        for it in prods:
            v[it] += m
    return v


def _avg_shop_vector():
    v = {it: 0.0 for it in PRODUCTS}
    ks = list(SHOPS)
    for s in ks:
        sv = _shop_vector([s])
        for it in PRODUCTS:
            v[it] += sv[it] / len(ks)
    return v


AVG_SHOP_VEC = _avg_shop_vector()


def _drain_at(step, shops):
    d = {p: 0.0 for p in PRODUCTS}
    if step % 4 == 0 and shops:
        sv = _shop_vector(shops)
        for p in PRODUCTS:
            d[p] += sv[p]
    if step % 24 == 0:
        for p in TOWN_CENTER_PRODUCTS:
            d[p] += 1.0
    return d


def _forward_absorb(day, hour, shops, expected=True):
    step = day * TURN_PER_DAY + hour
    cur = _shop_vector(shops)
    n = len(shops)
    unlock_steps = []
    for d in range(day + 1, 30):
        if d % 3 == 0 and n < MAX_SHOP_INSTANCES:
            unlock_steps.append(d * TURN_PER_DAY)
            n += 1
    tot = {it: 0.0 for it in PRODUCTS}
    for t in range(step, EPISODE_STEPS):
        if t % 4 == 0:
            k = 0
            for u in unlock_steps:
                if t >= u:
                    k += 1
            for it in PRODUCTS:
                # Phase 5.1b: expected=False → KHÔNG cộng shop tương lai (minimax
                # P25: chỉ tin shop đã mở thật) — dùng cho p3_lo của px_pred
                tot[it] += cur[it] + (AVG_SHOP_VEC[it] * k if expected else 0.0)
        if t % 24 == 0:
            for it in TOWN_CENTER_PRODUCTS:
                tot[it] += 1
    return tot


def _pipeline(tiles, shed):
    pipe = {it: 0.0 for it in PRODUCTS}
    if not tiles:
        return pipe
    for row in tiles:
        for t in row:
            if not isinstance(t, dict):
                continue
            if t.get("kind") == "PLANT":
                crop = t.get("crop")
                if crop in YIELD_PER_CYCLE:
                    pipe[crop] += YIELD_PER_CYCLE[crop]
            elif "animal" in t:
                an = t.get("animal")
                if an in ANIMALS:
                    pipe[ANIMALS[an]["product"]] += 28.0
    if shed:
        for it in PRODUCTS:
            v = shed.get(it, 0)
            if _is_num(v):
                pipe[it] += v
    return pipe


def _struct_reserve(need, unit_cost, money):
    if need <= 0:
        return 0
    r = 0
    if money >= unit_cost + 250:
        r = 1
    if need >= 2 and money >= 2 * unit_cost + 500:
        r = 2
    if need >= 3 and money >= 3 * unit_cost + 900:
        r = 3
    return min(need, r)


def _daily_plan(tiles, shed, seeds, inv, prices, shops, day, opp_farm, money, tm=None, rg=None):
    absorb = _forward_absorb(day, 0, shops)
    my_pipe = _pipeline(tiles, shed)
    opp_tiles = _g(opp_farm, "tiles", None) if opp_farm else None
    opp_pipe = _pipeline(opp_tiles, None)
    pxp_room = (tm or {}).get("px_pred") or {}  # v5.2: room() đọc dự báo giá

    def room(it):
        deficit = max(0.0, MARKET_I0 - inv.get(it, MARKET_I0))
        r = deficit + absorb.get(it, 0) + _above_headroom(it, 0.78)
        # v5.2 GIẢI PHÓNG NHƯỢNG TƯỚNG QUÂN (trọng tâm 2, khái quát từ 3 bài
        # học seed 2/42: dâu, sữa, dưa): hệ số 0.85 mặc định giả định đối thủ
        # thích nghi + thị trường zero-sum. Nhưng khi L3-Price dự báo giá TĂNG
        # (p3 ≥ now×1.04), thị trường đang nói "còn chỗ" — đối thủ có pipeline
        # cũng không làm giá giảm. Khi đó giảm nhượng xuống 0.35 (minimax: vẫn
        # giữ 1/3 bảo vệ tự glut). White-box v4 trồng quota CỐ ĐỊNH trước →
        # nếu v5 cứ nhượng, v4 độc chiếm mọi chân khan hiếm (melon seed 42:
        # 96 vs 48 quả, -$8.4k).
        sub = 0.85
        # v5.3 L1 PASSIVE (PLAN 4.5): đối thủ yếu đã được posterior xác nhận
        # → thị trường gần như của mình, chỉ giữ 0.35 chống tự glut
        if mode == "PASSIVE":
            sub = 0.35
        try:
            q = (pxp_room or {}).get(it) or {}
            if (q.get("p3", 0) or 0) >= (q.get("now", 0) or 0) * 1.04:
                sub = 0.35
        except Exception:
            pass
        return r - my_pipe.get(it, 0) - sub * opp_pipe.get(it, 0)

    coops = pastures = wheat_standing = 0
    animals_now = 0
    standing = {c: 0 for c in CROPS}
    for row in tiles:
        for t in row:
            if isinstance(t, dict):
                k = t.get("kind")
                if k == "COOP":
                    coops += 1
                elif k == "PASTURE":
                    pastures += 1
                if "animal" in t:
                    animals_now += 1
                if k == "PLANT":
                    cc = t.get("crop")
                    if cc in standing:
                        standing[cc] += 1
                    if cc == "WHEAT":
                        wheat_standing += 1
    shed_geese = shed.get("GOOSE", 0) if shed and _is_num(shed.get("GOOSE", 0)) else 0
    shed_cows = shed.get("COW", 0) if shed and _is_num(shed.get("COW", 0)) else 0
    shed_sheep = shed.get("SHEEP", 0) if shed and _is_num(shed.get("SHEEP", 0)) else 0

    opp_counts = {"GOOSE": 0, "COW": 0, "SHEEP": 0}
    if opp_tiles:
        for row in opp_tiles:
            for t in row:
                if isinstance(t, dict) and "animal" in t:
                    a = t.get("animal")
                    if a in opp_counts:
                        opp_counts[a] += 1

    mode = (tm or {}).get("mode", "CONTEST")
    fp = _flow_pred(tm, day)
    tm["flow_pred"] = fp
    # v5-P1 L3: giá trị pipeline còn lại 2 bên (trần doanh thu tương lai) —
    # lưu vào tm cho _project dùng như ceiling khi ngoại suy E[tiền cuối]
    try:
        pv = 0.0
        for p, u in my_pipe.items():
            pv += u * float(prices.get(p, 0) or MARKET_PARAMS[p]["base"] or 0)
        tm["pipe_val_me"] = pv
        po = 0.0
        for p, u in opp_pipe.items():
            po += u * float(prices.get(p, 0) or MARKET_PARAMS[p]["base"] or 0)
        tm["pipe_val_opp"] = po
    except Exception:
        pass
    days_left = max(1, 29 - day)
    # v5.3: subs GIỮ v5.2 (fp = 1.3×3n) — L2 P75 chạy như OBSERVER (đo +
    # diag + calibration; coupling hành vi chờ Phase 5 sau profile offline).
    milk_sub = max(fp.get("MILK", 0.0) * days_left if fp else 0.0, 30.0 * opp_counts["COW"])
    wool_sub = max(fp.get("WOOL", 0.0) * days_left if fp else 0.0, 28.0 * opp_counts["SHEEP"])
    egg_sub = max(fp.get("EGG", 0.0) * days_left if fp else 0.0, 46.0 * opp_counts["GOOSE"])
    # v5.2 ANIMAL COMPETE (trọng tâm 2 — khuyết cùng họ với strawberry seed 42):
    # opp_sub (30×bò đối thủ) là "đối thủ sẽ phủ chặng này" — hợp lý với đối thủ
    # thích nghi, nhưng với v4 white-box + giá đang TĂNG, giá tự nói "thị trường
    # CHƯA đầy". L3-Price rising → cap opp_sub ở mức thị trường hấp thụ được,
    # tránh vòng lẩn nhau: v4 mua bò trước → v5 nhượng → v4 độc chiếm sữa
    # $296 (seed 42: 4 bò v4 = $20.3k milk vs 1 bò v5 = $3.4k, thua 0.700×).
    try:
        pxp_a = (tm or {}).get("px_pred") or {}

        def _rising_a(it):
            q = pxp_a.get(it) or {}
            return (q.get("p3", 0) or 0) >= (q.get("now", 0) or 0) * 1.04

        if mode != "MIRROR":
            if _rising_a("MILK"):
                milk_sub = min(milk_sub, 0.45 * absorb.get("MILK", 0.0))
                tm["knobs_animal"] = "MILK"
            if _rising_a("WOOL"):
                wool_sub = min(wool_sub, 0.45 * absorb.get("WOOL", 0.0))
                tm["knobs_animal"] = tm.get("knobs_animal") or "WOOL"
            if _rising_a("EGG"):
                egg_sub = min(egg_sub, 0.45 * absorb.get("EGG", 0.0))
                tm["knobs_animal"] = tm.get("knobs_animal") or "EGG"
    except Exception:
        pass
    if mode != "MIRROR" and fp:
        milk_room = (absorb.get("MILK", 0) + 0.5 * max(0.0, MARKET_I0 - inv.get("MILK", MARKET_I0))
                     - milk_sub - 40.0)
        wool_room = (absorb.get("WOOL", 0) + 0.5 * max(0.0, MARKET_I0 - inv.get("WOOL", MARKET_I0))
                     - wool_sub - 20.0)
        egg_room = (absorb.get("EGG", 0) + 0.5 * max(0.0, MARKET_I0 - inv.get("EGG", MARKET_I0))
                    - egg_sub - 20.0)
    else:
        milk_room = (absorb.get("MILK", 0) + 0.5 * max(0.0, MARKET_I0 - inv.get("MILK", MARKET_I0))
                     - 30.0 * opp_counts["COW"] - 40.0)
        wool_room = (absorb.get("WOOL", 0) + 0.5 * max(0.0, MARKET_I0 - inv.get("WOOL", MARKET_I0))
                     - 28.0 * opp_counts["SHEEP"] - 20.0)
        egg_room = (absorb.get("EGG", 0) + 0.5 * max(0.0, MARKET_I0 - inv.get("EGG", MARKET_I0))
                    - 46.0 * opp_counts["GOOSE"] - 20.0)
    if mode == "MIRROR":
        goose_target, cow_target, sheep_target = 6, 5, 3
    elif mode == "COOP":
        goose_target = max(4 if day <= 9 else 3, min(5, int(egg_room // 46)))
        cow_target = max(0, min(8, int(milk_room // 30)))
        sheep_target = max(5, min(7, int(wool_room // 30)))
    elif mode == "PASSIVE":
        # v5.3 L1 (PLAN 4.5): thị trường trống → max đàn mọi chân
        goose_target = max(4 if day <= 9 else 3, min(7, int(egg_room // 46)))
        cow_target = max(2, min(10, int(milk_room // 30)))
        sheep_target = max(5, min(8, int(wool_room // 30)))
    else:
        goose_target = max(4 if day <= 9 else 3, min(6, int(egg_room // 46)))
        cow_target = max(2, min(9, int(milk_room // 30)))
        sheep_target = max(5, min(7, int(wool_room // 30)))
    # v5.2 ANIMAL FLOOR THEO SHOP DRAW (tín hiệu sớm nhất — d6, trước px_pred
    # 6-8 ngày): shop cầu sữa/len mở = thị trường sâu BẤT CHẲP pipeline đối
    # thủ (tại seed 555: 2 PIZZA d6 + 2 YARN d12 → v4 phóng 15 thú thắng
    # $25k; room logic của v5 nhượng vì thấy đàn v4 to — vòng lẩn nhau).
    # Floor chỉ nâng TỐI THIỂU, mua thật vẫn qua cổng tiền/cám/lao động.
    try:
        if mode != "MIRROR":
            milk_shops = sum(1 for s in (shops or [])
                             if s in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
            yarn_n = sum(1 for s in (shops or []) if s == "YARN_STORE")
            if milk_shops >= 2 and 4 <= day <= 16:
                cow_target = max(cow_target, min(6, 2 + milk_shops))
            if yarn_n >= 1 and 4 <= day <= 15:
                sheep_target = max(sheep_target, min(7, 4 + yarn_n))
    except Exception:
        pass
    if day < 2:
        goose_target = 0
        cow_target = 0
        sheep_target = 0
    elif day < 5:
        cow_target = 0
        sheep_target = 0
    elif day < 6:
        sheep_target = 0
    # v5 L6: kỷ luật đàn khi rủi ro — không mở rộng burn khi đang chết dần (F1),
    # không nuôi thêm khi thiếu cám (F2), SURVIVE đóng băng tăng trưởng
    if rg:
        f1v = int(rg.get("F1", 0) or 0)
        f2v = int(rg.get("F2", 0) or 0)
        if f1v >= 2 or f2v >= 2:
            og = sum(1 for row in tiles for t in row
                     if isinstance(t, dict) and t.get("animal") == "GOOSE")
            oc = sum(1 for row in tiles for t in row
                     if isinstance(t, dict) and t.get("animal") == "COW")
            osp = sum(1 for row in tiles for t in row
                      if isinstance(t, dict) and t.get("animal") == "SHEEP")
            goose_target = min(goose_target, og + shed_geese + (0 if f1v >= 2 else 1))
            cow_target = min(cow_target, oc + shed_cows + (0 if f1v >= 2 else 1))
            sheep_target = min(sheep_target, osp + shed_sheep + (0 if f1v >= 2 else 1))
        if str(rg.get("state")) == "SURVIVE":
            og = sum(1 for row in tiles for t in row
                     if isinstance(t, dict) and t.get("animal") == "GOOSE")
            oc = sum(1 for row in tiles for t in row
                     if isinstance(t, dict) and t.get("animal") == "COW")
            osp = sum(1 for row in tiles for t in row
                      if isinstance(t, dict) and t.get("animal") == "SHEEP")
            goose_target = min(goose_target, og + shed_geese)
            cow_target = min(cow_target, oc + shed_cows)
            sheep_target = min(sheep_target, osp + shed_sheep)
    # v5.2: theo dõi gap đàn cho diag (KHÔNG đuổi đàn — bài học seed 3:
    # v5 ruộng đầy + đuổi 5 thú = quá tải lao động → ruộng xẹp p24 vs p42)
    try:
        tm["herd_gap"] = int(sum(opp_counts.values())) - int(animals_now + shed_geese + shed_cows + shed_sheep)
        tm["knobs_parity"] = 0
    except Exception:
        pass
    owned_total = animals_now + shed_geese + shed_cows + shed_sheep
    # v5-P1b: cap đàn theo LAO ĐỘNG. Bài học seed 42: 15 thú @ 13 thợ giết
    # planting (SERVICE tier-2 chiếm sạch unit) → ruộng trống → thua v4 đang
    # giữ 9 thú + 39 cây. Quy tắc: ~0.75 thú/thợ + 2.
    u_est = 15 if day >= 26 else (13 if day >= 9 else (12 if day >= 6 else (8 if day >= 1 else 7)))
    animal_cap = min(ANIMAL_CAP, max(4, int(u_est * 0.75) + 2))

    # v5.2 TRỌNG TÂM 2 — LAO ĐỘNG LÀ RÀNG BUỘC SỐ 1 CỦA CHIẾN THUẬT:
    # water_crit_late = số lượt tưới-cấp cứu CÒN NỢ lúc hour≥16 hôm qua
    # (đo trực tiếp từ risk ledger L5). Mỗi thú = 3 turn SERVICE/ngày →
    # khi ruộng đang đói nước, mở rộng đàn = đổi cây lấy thú = tự sát.
    try:
        water_debt = int((_STATE.get(("risk", day - 1)) or {}).get("water_crit_late", 0) or 0)
    except Exception:
        water_debt = 0
    tm["water_debt"] = water_debt
    if water_debt >= 3:
        animal_cap = max(4, animal_cap - 2)  # siết cap khi nợ nước cao
    # ---- vE2 LATE-HERD: d13-17 vốn nhàn ≥ $8k → engine thú cuối mùa ----
    try:
        if 13 <= day <= 17 and money >= 8000 and water_debt <= 2:
            animal_cap = min(ANIMAL_CAP, animal_cap + 4)
            cow_target = min(12, int(cow_target) + 2)
            sheep_target = min(10, int(sheep_target) + 2)
            if isinstance(tm, dict):
                tm["knobs_late_herd"] = True
    except Exception:
        pass

    if owned_total >= animal_cap:
        goose_target = min(goose_target, animals_now + shed_geese)
        cow_target = min(cow_target, sum(1 for row in tiles for t in row
                                         if isinstance(t, dict) and t.get("animal") == "COW") + shed_cows)
        sheep_target = min(sheep_target, sum(1 for row in tiles for t in row
                                             if isinstance(t, dict) and t.get("animal") == "SHEEP") + shed_sheep)

    # v5.2 L7 (trọng tâm 2, bản SỬA LỖI): DỰ BÁO THUA → đua lại bằng thông
    # lượng cây NHANH (wheat cycle 5 ngày) chứ KHÔNG blindly mở đàn. Bài học
    # máu seed 2: BEHIND ngày 14 → +2 bò +2 cừu +1 ngỗng → 39 turn SERVICE
    # → ruộng chết giữa mùa → THUA NẶNG HƠN (0.763×). Mở đàn chỉ khi cả 3
    # điều kiện: nợ nước ≤2 (lao động còn dư), dưới animal_cap, tiền mạnh.
    proj = (tm or {}).get("proj") or {}
    if (mode != "MIRROR" and proj.get("tier") == "BEHIND" and day >= 8
            and sum(standing.values()) >= 22
            and not (rg and str(rg.get("state")) == "SURVIVE")):
        if water_debt <= 2 and owned_total < animal_cap and money >= 2500:
            # chỉ +1 thú vào chân có room dương nhất (không phải +2/+2/+1)
            for it, add in (("COW", milk_room > 60), ("SHEEP", wool_room > 45), ("GOOSE", egg_room > 80)):
                if not add:
                    continue
                if it == "COW":
                    cow_target = min(10, cow_target + 1)
                elif it == "SHEEP":
                    sheep_target = min(8, sheep_target + 1)
                else:
                    goose_target = min(7, goose_target + 1)
                tm["knobs_herd"] = True
                break
        else:
            tm["knobs_herd"] = False
        # BEHIND mọi trường hợp (nợ nước hay không): đẩy vòng tiền nhanh —
        # quota wheat +3 (cây 5 ngày, thu bằng tiền mặt gần như ngay)
        tm["knobs_fastwheat"] = True
    else:
        tm["knobs_fastwheat"] = False
        tm["knobs_herd"] = False

    coop_need = _struct_reserve(goose_target + shed_geese - coops, 300, money)
    past_need = _struct_reserve(cow_target + shed_cows + sheep_target + shed_sheep - pastures, 500, money)
    if day <= 2:
        coop_need = min(coop_need, 2)
        past_need = min(past_need, 2)
    if rg and int(rg.get("F1", 0) or 0) >= 2:  # v5: F1 L2 — không xây thêm khi death-spiral thật
        coop_need = 0
        past_need = 0

    board = len(tiles)
    cx = board // 2
    empties = []
    for y in range(board):
        for x in range(board):
            if tiles[y][x] is None:
                empties.append((x, y))
    empties.sort(key=lambda c: abs(c[0] - cx) + abs(c[1] - cx))
    reserved = []
    ri = 0
    for _ in range(coop_need):
        if ri < len(empties):
            reserved.append((empties[ri][0], empties[ri][1], "BUILD_COOP"))
            ri += 1
    for _ in range(past_need):
        if ri < len(empties):
            reserved.append((empties[ri][0], empties[ri][1], "BUILD_PASTURE"))
            ri += 1
    plantable = empties[ri:]

    feed_demand = (animals_now + shed_geese + shed_cows + shed_sheep
                   + goose_target + cow_target + sheep_target) * max(0, 29 - day)

    quotas = {}
    if 8 <= day <= 14:
        quotas["MELON"] = 14 if room("MELON") > -50 else 7
        if day <= 1:
            quotas["MELON"] = 8
    # A/B 20 Sep: mở TOMATO (≤8 tiles, gate shop/room) = 1.027x/23/40, worst
    # 0.766 — MẤT −0.033x so baseline → REVERT về TOMATO=0 như v3/v4. Bài học
    # (RULES R67): cơ hội phí đất+lao động của nền wheat-feed ép bay lợi
    # nhuận tomato ở quy mô ≤32u; chỉ Solver $/action toàn cục (P3 đầy đủ)
    # mới đủ thông tin mở kênh này đúng lúc.
    if 2 <= day <= 16:
        quotas["TOMATO"] = 0
    if 5 <= day <= 14:
        s_room = room("STRAWBERRY")
        want_straw = 30 if day >= 8 else 14
        # v5.2 CẠNH TRANH DÂU (trọng tâm 2, white-box v4): v4 trồng 30 dâu
        # trong window cố định 5-13 bất kể ai làm gì. room() trừ 0.85×opp
        # → v5 tự NHƯỢNG thị trường đúng lúc khan hiếm (seed 2: dâu $265,
        # v4 bán 74 units $17.8k vs v5 5 cây $4.9k). L3-Price dự báo giá dâu
        # TĂNG + town ≥2 shop cầu dâu → thị trường đủ sâu cho CẢ HAI →
        # tính room KHÔNG trừ pipeline đối thủ (minimax: chấp nhận cạnh tranh
        # khi Bayes xác nhận khan hiếm thật).
        try:
            pxp = (tm or {}).get("px_pred") or {}
            sq = pxp.get("STRAWBERRY") or {}
            straw_rising = (sq.get("p3", 0) or 0) >= (sq.get("now", 0) or 0) * 1.05
            straw_shops = sum(1 for s in (shops or [])
                              if "STRAWBERRY" in SHOPS.get(s, ()))
        except Exception:
            straw_rising = False
            straw_shops = 0
        if (straw_rising and straw_shops >= 2 and mode != "MIRROR"
                and day <= 13):
            s_room = max(s_room, absorb.get("STRAWBERRY", 0.0)
                         - my_pipe.get("STRAWBERRY", 0.0))
            tm["knobs_straw"] = True
        quotas["STRAWBERRY"] = want_straw if s_room > 100 else max(0, min(want_straw, int(s_room // 4)))
    elif 14 <= day <= 15:
        quotas["STRAWBERRY"] = 6
    if day <= 24:
        if day <= 4:
            quotas["WHEAT"] = 17
        else:
            daily_q = int((animals_now + shed_geese + shed_cows + shed_sheep
                          + goose_target + cow_target + sheep_target) * 1.25) + 3
            quotas["WHEAT"] = min(24, max(20, daily_q))
        # v5.2: BEHIND + núm fast-wheat → quota +3 (cycle 5 ngày = vòng tiền
        # nhanh nhất có thể, nhanh hơn bất kỳ con thú nào 4-8 ngày)
        if (tm or {}).get("knobs_fastwheat") and day <= 22:
            quotas["WHEAT"] = min(28, quotas["WHEAT"] + 3)
    if rg and int(rg.get("F2", 0) or 0) >= 2:  # v5: F2 L2+ — tăng quota wheat tự trồng
        quotas["WHEAT"] = min(28, quotas.get("WHEAT", 20) + 2)
    if day <= 23:
        if day <= 2:
            quotas["CARROT"] = 12
        elif day <= 10:
            quotas["CARROT"] = 8 if room("CARROT") > 60 else 6
        else:
            quotas["CARROT"] = 4 if room("CARROT") > 60 else 0

    if day <= 1:
        quotas["WHEAT"] = 10
        quotas["CARROT"] = 8
        quotas["MELON"] = 8
        quotas.pop("STRAWBERRY", None)

    if day <= 2:
        order = ["WHEAT", "MELON", "TOMATO", "CARROT", "STRAWBERRY"]
    elif feed_demand > 300:
        order = ["WHEAT", "STRAWBERRY", "TOMATO", "MELON", "CARROT"]
    else:
        order = ["MELON", "STRAWBERRY", "TOMATO", "WHEAT", "CARROT"]
    crop_tiles = {}
    remaining = len(plantable)
    for crop in order:
        want = quotas.get(crop, 0)
        if want <= 0:
            continue
        have = standing.get(crop, 0)
        need = max(0, want - have)
        take = min(remaining, need)
        if take > 0:
            crop_tiles[crop] = take
            remaining -= take
        if remaining <= 0:
            break
    if remaining > 0 and day <= 22:
        extra = min(remaining, 8)
        if feed_demand > 200:
            crop_tiles["WHEAT"] = crop_tiles.get("WHEAT", 0) + extra
        else:
            crop_tiles["CARROT"] = crop_tiles.get("CARROT", 0) + extra
        remaining -= extra

    if day <= 1 and plantable:
        fast = sum(v for c, v in crop_tiles.items() if c in ("WHEAT", "CARROT"))
        if fast < 0.45 * len(plantable):
            need = int(0.45 * len(plantable)) - fast
            for c in list(crop_tiles):
                if c not in ("WHEAT", "CARROT") and need > 0:
                    cut = min(crop_tiles[c], need)
                    crop_tiles[c] -= cut
                    need -= cut
                    if crop_tiles[c] == 0:
                        del crop_tiles[c]
            if need > 0:
                crop_tiles["WHEAT"] = crop_tiles.get("WHEAT", 0) + need

    return {
        "crop_tiles": crop_tiles,
        "reserved": reserved,
        "goose_target": goose_target,
        "cow_target": cow_target,
        "sheep_target": sheep_target,
        "feed_demand": feed_demand,
        "standing": standing,
        "mode": mode,
    }


def _build_tasks(tiles, shed, seeds, plan, day, hour, step, inventories, n_units):
    tasks = []
    stats = {"water_crit": 0, "total": 0}
    board = len(tiles)
    if not board:
        return tasks, stats
    # v5.2: nợ nước hôm qua (L5→L7) — đẩy ưu tiên tưới parity khi đang thâm hụt
    try:
        water_debt = int((_STATE.get("tm") or {}).get("water_debt", 0) or 0)
    except Exception:
        water_debt = 0

    fert_available = (shed.get("FERTILIZER", 0) if shed else 0) + sum(
        (u.get("FERTILIZER", 0) or 0) for u in inventories if isinstance(u, dict))
    wheat_available = (shed.get("WHEAT", 0) if shed else 0) + sum(
        (u.get("WHEAT", 0) or 0) for u in inventories if isinstance(u, dict))
    animals_n = 0
    hungry_n = 0
    for row in tiles:
        for t in row:
            if isinstance(t, dict) and "animal" in t:
                animals_n += 1
                if (t.get("consecutive_unfed", 0) or 0) >= 1 and not t.get("fed_today", False):
                    hungry_n += 1
    feed_crunch = hungry_n > 0 or (animals_n > 0 and wheat_available < animals_n + 3)

    fert_usable = 0
    for row in tiles:
        for t in row:
            if not isinstance(t, dict) or t.get("kind") != "PLANT":
                continue
            crop = t.get("crop")
            if crop not in ("WHEAT", "CARROT"):
                continue
            cd = CROPS[crop]
            age = day - t.get("planted_day", day)
            ws = (cd["max_yield_day"] + 1) // 2
            if ws <= age <= cd["max_yield_day"] and t.get("fertilized_until_day", -1) < day:
                fert_usable += 1
    fert_usable = max(0, fert_usable - fert_available)
    fert_made = 0

    for y in range(board):
        row = tiles[y]
        for x in range(board):
            t = row[x]
            if t is None or t == "LOCKED" or not isinstance(t, dict):
                continue
            kind = t.get("kind")
            if kind == "PLANT":
                crop = t.get("crop")
                cd = CROPS.get(crop)
                if cd is None:
                    continue
                age = day - t.get("planted_day", day)
                yu = t.get("yield_units", 0) or 0
                mls = t.get("max_lifespan_step", -1)
                watered = bool(t.get("watered_today", False))
                if not watered:
                    cu = t.get("consecutive_unwatered", 0) or 0
                    ws = (cd["max_yield_day"] + 1) // 2
                    in_win = (not cd["ongoing"]) and (ws <= age <= cd["max_yield_day"])
                    if in_win:
                        tasks.append(_mk(T_WATER_YIELD, x, y, "WATER"))
                        stats["water_yield"] = stats.get("water_yield", 0) + 1
                    elif cu >= 1:
                        # v5.2 FIX CHẾT CÂY (bản đúng): cu≥1 = HÔM QUA không được
                        # tưới → hôm nay không tưới là thành cỏ dại (cu→2 tối nay)
                        # → tier 0 VÔ ĐIỀU KIỆN, bất kể parity. Lỗi elif cũ: ngày
                        # chẵn (parity-ON) cho cu≥1 xuống tier 3 → bị SERVICE đói
                        # → cây chết đúng ngày chẵn (chuỗi chết seed 2). Tưới mỗi
                        # 2 ngày/plant — cùng volume như v4 nhưng ưu tiên đúng.
                        tasks.append(_mk(T_WATER_CRIT, x, y, "WATER"))
                        stats["water_crit"] += 1
                    else:
                        on_day = (x + y + day) % 2 == 0
                        if on_day:
                            # v5.2: ngày CHẴN của cây — tưới theo parity tier 3,
                            # nhưng nếu hôm qua có nợ nước (L5 water_debt) → đẩy
                            # lên tier 2 để không bị SERVICE đói thêm vòng nữa
                            t_w = T_WATER_MAINT if water_debt < 1 else T_SERVICE
                            tasks.append(_mk(t_w, x, y, "WATER"))
                if yu > 0 and age >= cd["first_yield_day"]:
                    urgent = (mls >= 0 and mls - step <= 24) or (crop == "WHEAT" and feed_crunch)
                    if cd["ongoing"]:
                        ready = yu >= 4 or (mls >= 0 and mls - step <= 6) or day >= 27
                        # v5: straw/tomato decay window — thu ngân 3+ đơn vị nửa ngày
                        # trước khi cây chết thành cỏ dại (bài học straw under-harvest)
                        if not ready and yu >= 3 and mls >= 0 and mls - step <= 12:
                            ready = True
                    else:
                        ready = yu >= cd["max_yield"] or age >= cd["max_yield_day"] + 1 or (
                            age >= cd["max_yield_day"] and watered)
                    if ready:
                        tasks.append(_mk(T_HARVEST_URG if urgent else T_HARVEST, x, y, "HARVEST"))
            elif "animal" in t:
                ad = ANIMALS.get(t.get("animal"))
                if ad is None:
                    continue
                starve = (t.get("consecutive_unfed", 0) or 0) >= 1
                need_feed = (not t.get("fed_today", False)) and wheat_available > 0
                need_care = not t.get("cared_today", False)
                need_fert = bool(t.get("fertilizer_available", False))
                if day <= 28 and (need_feed or need_care or need_fert):
                    tasks.append(_mk(T_SERVICE_URG if starve else T_SERVICE, x, y, "SERVICE",
                                     want_wheat=need_feed, feed=need_feed))
                yu = t.get("yield_units", 0) or 0
                if yu >= ad["max_held"] - 1:
                    tasks.append(_mk(T_HARVEST_URG, x, y, "HARVEST"))
                elif yu >= 2 or (yu > 0 and day >= 27):
                    tasks.append(_mk(T_HARVEST_ANIMAL, x, y, "HARVEST"))
            elif kind == "WEED":
                tasks.append(_mk(T_DIG, x, y, "DIG"))
            elif kind in ("COOP", "PASTURE"):
                pass

    if hour <= 20:
        built = 0
        for (x, y, bop) in plan.get("reserved", []):
            if built >= 2:
                break
            if 0 <= y < board and 0 <= x < board and tiles[y][x] is None:
                animal_waiting = ((shed.get("GOOSE", 0) or 0) + (shed.get("COW", 0) or 0)
                                  + (shed.get("SHEEP", 0) or 0)) > 0
                tasks.append(_mk(T_BUILD_URG if animal_waiting else T_BUILD, x, y, bop))
                built += 1

    if shed:
        for animal in ("GOOSE", "COW", "SHEEP"):
            n_pending = shed.get(animal, 0) or 0
            if n_pending <= 0:
                continue
            struct_kind = ANIMALS[animal]["structure"]
            placed = 0
            limit = min(n_pending, 3)
            for y in range(board):
                for x in range(board):
                    if placed >= limit:
                        break
                    t = tiles[y][x]
                    if isinstance(t, dict) and t.get("kind") == struct_kind and "animal" not in t:
                        tasks.append(_mk(T_DELIVER, x, y, "DELIVER", item=animal))
                        placed += 1
                if placed >= limit:
                    break

    planted = _STATE.get(("planted", day)) or {}
    budget = []
    for crop, cap in plan.get("crop_tiles", {}).items():
        remain = cap - planted.get(crop, 0)
        have = (seeds.get(crop, 0) or 0) if seeds else 0
        if remain > 0 and have > 0:
            budget.append((crop, min(remain, have)))
    reserved_xy = {(x, y) for (x, y, _) in plan.get("reserved", [])}
    if budget and hour <= 19:
        empties = []
        for y in range(board):
            for x in range(board):
                if tiles[y][x] is None and (x, y) not in reserved_xy:
                    empties.append((x, y))
        empties.sort(key=lambda c: abs(c[0] - board // 2) + abs(c[1] - board // 2))
        flat = []
        wfirst = (plan.get("feed_demand", 0) or 0) > 0
        for crop, n in budget:
            if wfirst and crop == "WHEAT":
                flat.extend(["WHEAT"] * n)
        for crop, n in budget:
            if wfirst and crop == "WHEAT":
                continue
            flat.extend([crop] * n)
        turn_budget = n_units * max(1, 23 - hour)
        water_load = stats.get("water_crit", 0) + stats.get("water_yield", 0)
        safe_plant = int((turn_budget - water_load * 2.0) / 4)
        # v5 L6 F3: không trồng thêm cây khi không đủ nhân lực tưới giữ mạng sống
        rgq = _STATE.get("rg") or {}
        f3q = int(rgq.get("F3", 0) or 0)
        if f3q >= 1:
            safe_plant = safe_plant // (1 + f3q)
        if f3q >= 2:
            safe_plant = 0
        n_plant = min(len(flat), len(empties), max(0, safe_plant))
        # v5-P1b: trồng ưu tiên BUỔI SÁNG (tier 3 khi h≤11) — bài học seed 42:
        # SERVICE/WATER backlog chiếm trọn ngày, PLANT tier-5 không bao giờ
        # được nhận unit → hạt đã mua mà ruộng trống. v4 ít thú nên trồng được.
        p_tier = 3 if hour <= 11 else T_PLANT
        # v5.2 WINDOW CLOSING: dưa 10 ngày lớn — d11+ mà chưa trồng là sắp mất
        # cửa (seed 42: plan MELON 14 ngày 14, mua 11 hạt, trồng 0 = -$8.4k).
        # Cây có window đóng trong ≤3 ngày → leo lên tier 2 cạnh SERVICE.
        try:
            closing = any(c == "MELON" and 11 <= day <= 15 for (c, _n) in budget) \
                or any(c == "STRAWBERRY" and 12 <= day <= 14 for (c, _n) in budget)
        except Exception:
            closing = False
        if closing and hour <= 13:
            p_tier = T_SERVICE
        for i in range(n_plant):
            x, y = empties[i]
            tasks.append(_mk(p_tier, x, y, "PLANT", crop=flat[i]))

    if fert_available > 0 and day < 25:
        made = 0
        capf = min(int(fert_available), 6)
        for y in range(board):
            for x in range(board):
                if made >= capf:
                    break
                t = tiles[y][x]
                if not isinstance(t, dict) or t.get("kind") != "PLANT":
                    continue
                crop = t.get("crop")
                if crop != "MELON":
                    continue
                cd = CROPS[crop]
                age = day - t.get("planted_day", day)
                ws = (cd["max_yield_day"] + 1) // 2
                if ws <= age <= cd["max_yield_day"] and t.get("fertilized_until_day", -1) < day:
                    tasks.append(_mk(T_FERTILIZE, x, y, "FERTILIZE"))
                    made += 1

    stats["total"] = len(tasks)
    return tasks, stats


def _drop_action(ux, uy, board):
    st = _nearest_shed_tile(ux, uy, board)
    if (ux, uy) == st:
        return ["DROP"]
    mv = _step_toward(ux, uy, st[0], st[1])
    return [mv] if mv else ["PASS"]


def _task_action(tk, ux, uy, uinv, tiles, shed, board):
    op = tk["op"]
    tx, ty = tk["x"], tk["y"]

    if op == "SERVICE":
        t = tiles[ty][tx] if 0 <= tx < board and 0 <= ty < board else None
        an = t if (isinstance(t, dict) and "animal" in t) else None
        if an is None:
            return ["PASS"]
        w = uinv.get("WHEAT", 0) or 0
        unfed = not an.get("fed_today", False)
        shed_w = (shed.get("WHEAT", 0) or 0) if shed else 0
        if unfed and w > 0:
            if (ux, uy) == (tx, ty):
                return ["FEED"]
            mv = _step_toward(ux, uy, tx, ty)
            return [mv] if mv else ["PASS"]
        if unfed and w <= 0 and shed_w > 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(5, shed_w)
                if n > 0:
                    return ["PICKUP", "WHEAT", n]
            else:
                mv = _step_toward(ux, uy, st[0], st[1])
                if mv:
                    return [mv]
        if (ux, uy) == (tx, ty):
            if not an.get("cared_today", False):
                return ["CARE"]
            if an.get("fertilizer_available", False):
                return ["COLLECT_FERTILIZER"]
            return ["PASS"]
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ["PASS"]

    if op == "FEED":
        w = uinv.get("WHEAT", 0) or 0
        if w <= 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(5, (shed.get("WHEAT", 0) or 0) if shed else 0)
                if n > 0:
                    return ["PICKUP", "WHEAT", n]
                return ["PASS"]
            mv = _step_toward(ux, uy, st[0], st[1])
            return [mv] if mv else ["PASS"]
        if (ux, uy) == (tx, ty):
            return ["FEED"]
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ["PASS"]

    if op == "DELIVER":
        item = tk.get("item")
        if uinv.get(item, 0):
            if (ux, uy) == (tx, ty):
                return ["PLACE", item]
            mv = _step_toward(ux, uy, tx, ty)
            return [mv] if mv else ["PASS"]
        st = _nearest_shed_tile(ux, uy, board)
        if (ux, uy) == st:
            if shed and (shed.get(item, 0) or 0) > 0:
                return ["PICKUP", item, 1]
            return ["PASS"]
        mv = _step_toward(ux, uy, st[0], st[1])
        return [mv] if mv else ["PASS"]

    if op == "FERTILIZE":
        f = uinv.get("FERTILIZER", 0) or 0
        if f <= 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(6, (shed.get("FERTILIZER", 0) or 0) if shed else 0)
                if n > 0:
                    return ["PICKUP", "FERTILIZER", n]
                return ["PASS"]
            mv = _step_toward(ux, uy, st[0], st[1])
            return [mv] if mv else ["PASS"]
        if (ux, uy) == (tx, ty):
            return ["FERTILIZE"]
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ["PASS"]

    if (ux, uy) == (tx, ty):
        if op == "PLANT":
            return ["PLANT", tk.get("crop")]
        return [op]

    mv = _step_toward(ux, uy, tx, ty)
    return [mv] if mv else ["PASS"]


def _task_still_valid(tk, tiles, board, shed, uinv, day):  # v5-P1 FIX: thêm day (NameError)
    x, y = tk["x"], tk["y"]
    if not (0 <= x < board and 0 <= y < board):
        return False
    t = tiles[y][x]
    op = tk["op"]
    if op == "PLANT":
        return t is None
    if op == "WATER":
        return isinstance(t, dict) and t.get("kind") == "PLANT" and not t.get("watered_today", False)
    if op == "HARVEST":
        return isinstance(t, dict) and (t.get("yield_units", 0) or 0) > 0
    if op == "SERVICE":
        if not (isinstance(t, dict) and "animal" in t):
            return False
        if not t.get("fed_today", False):
            if (uinv.get("WHEAT", 0) or 0) > 0 or (shed.get("WHEAT", 0) or 0) > 0:
                return True
        return (not t.get("cared_today", False)) or bool(t.get("fertilizer_available", False))
    if op in ("FEED", "CARE"):
        return isinstance(t, dict) and "animal" in t and not t.get(
            "fed_today" if op == "FEED" else "cared_today", False)
    if op == "DIG":
        return isinstance(t, dict) and t.get("kind") == "WEED"
    if op in ("BUILD_COOP", "BUILD_PASTURE"):
        return t is None
    if op == "COLLECT_FERTILIZER":
        return isinstance(t, dict) and "animal" in t and t.get("fertilizer_available", False)
    if op == "FERTILIZE":
        return isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON" \
            and t.get("fertilized_until_day", -1) < day
    if op == "DELIVER":
        return (uinv.get(tk.get("item"), 0) or 0) > 0 or (shed.get(tk.get("item"), 0) or 0) > 0
    return True


def _assign_and_act(units, tasks, tiles, shed, inventories, day, hour, board, seeds):
    uinv_cache = {}
    for i in range(len(units)):
        u = inventories[i] if i < len(inventories) and isinstance(inventories[i], dict) else {}
        uinv_cache[i] = u

    sticky = _STATE.setdefault(("sticky", day), {})
    feed_pending = 0
    for tk2 in tasks:
        if tk2["op"] == "SERVICE" and tk2.get("feed"):
            feed_pending += 1
    for i in list(sticky.keys()):
        if i >= len(units):
            del sticky[i]
            continue
        tk = sticky[i]
        if not _task_still_valid(tk, tiles, board, shed, uinv_cache[i], day):
            del sticky[i]
            continue
        if feed_pending > 0 and tk["tier"] >= 2 and tk["op"] not in ("SERVICE", "FEED", "DELIVER") \
                and (uinv_cache[i].get("WHEAT", 0) or 0) > 0:
            del sticky[i]
    claimed = set()
    for i, tk in sticky.items():
        claimed.add((tk["op"], tk["x"], tk["y"]))

    free = [i for i in range(len(units)) if i not in sticky]
    plant_sticky = {}
    for i, tk in sticky.items():
        if tk["op"] == "PLANT":
            plant_sticky[tk.get("crop")] = plant_sticky.get(tk.get("crop"), 0) + 1

    def dist(i, tk):
        u = uinv_cache[i]
        if tk["op"] == "DELIVER" and (u.get(tk.get("item"), 0) or 0) > 0:
            return 0
        if tk["op"] in ("FEED", "SERVICE") and (u.get("WHEAT", 0) or 0) > 0:
            return 0
        d = abs(units[i][1] - tk["x"]) + abs(units[i][2] - tk["y"])
        if (u.get("WHEAT", 0) or 0) > 0 and tk["tier"] >= 1 and tk["op"] not in ("SERVICE", "FEED"):
            d += 6
        return d

    def skey(tk):
        return (tk["tier"], min((dist(i, tk) for i in free), default=99))

    for tk in sorted(tasks, key=skey):
        if not free:
            break
        if (tk["op"], tk["x"], tk["y"]) in claimed:
            continue
        if tk["op"] == "PLANT":
            c = tk.get("crop")
            if plant_sticky.get(c, 0) + 1 > (seeds.get(c, 0) if seeds else 0):
                continue
            plant_sticky[c] = plant_sticky.get(c, 0) + 1
        best = min(free, key=lambda i: dist(i, tk))
        sticky[best] = tk
        claimed.add((tk["op"], tk["x"], tk["y"]))
        free.remove(best)

    planted = _STATE.setdefault(("planted", day), {})
    actions = []
    for idx in range(len(units)):
        ux, uy = units[idx][1], units[idx][2]
        uinv = uinv_cache[idx]
        carried = sum(v for v in uinv.values() if _is_num(v))
        sellable = carried - (uinv.get("WHEAT", 0) or 0)
        act = ["PASS"]
        tk = sticky.get(idx)

        need_drop = sellable >= 18 or (hour >= 20 and sellable >= 3) \
            or (day >= 28 and hour >= 14 and sellable >= 1)
        if need_drop:
            act = _drop_action(ux, uy, board)
        elif tk is not None:
            act = _task_action(tk, ux, uy, uinv, tiles, shed, board)
        if isinstance(act, list) and act and act[0] == "PLANT":
            crop = act[1]
            planted[crop] = planted.get(crop, 0) + 1
        actions.append(act)
    return actions


def _wheat_all(shed, inventories):
    w = (shed.get("WHEAT", 0) or 0) if shed else 0
    for u in inventories or []:
        if isinstance(u, dict):
            w += u.get("WHEAT", 0) or 0
    return w


def _build_orders(me, shed, seeds, inventories, inv, prices, day, hour, plan,
                  stats, tiles, shops):
    orders = []
    rg = _STATE.get("rg") or {}  # v5: L6 risk guard knobs
    tmx = _STATE.get("tm") or {}  # v5-P1: L3 price/race cho núm bán
    proj = (tmx.get("proj") or {}) if isinstance(tmx, dict) else {}
    tier = proj.get("tier") if isinstance(proj, dict) else None
    money = float(_g(me, "money", 0) or 0)
    hands = _g(me, "hands", None) or []
    unlocked = _g(me, "unlocked_quadrants", None) or ["NW"]
    board = len(tiles) if tiles else 10
    shed_total = sum(v for v in (shed or {}).values() if _is_num(v))
    # Phase 5.2 E8-lite: drain + nguồn chờ thu TẠI GIỜ HIỆN TẠI (chỉ d22+ —
    # trước đó ladder không áp dụng nên không tốn chu kỳ)
    absorb_rest = {}
    pipe_rest = {}
    if day >= 22:
        try:
            absorb_rest = _forward_absorb(day, hour, shops)
            pipe_rest = _pipe_rest(tiles, day)
        except Exception:
            absorb_rest, pipe_rest = {}, {}

    if hour <= 5 and day < 29:
        planted_today = _STATE.get(("planted", day)) or {}
        plant_budget = sum(max(0, n - planted_today.get(c, 0))
                           for c, n in plan.get("crop_tiles", {}).items())
        workload = stats.get("total", 0) + plant_budget
        if day >= 6:
            cap = 13 if ((day >= 9 and money >= 1800) or (day >= 18 and money >= 2500)) else 12
            # v5: endgame labor surge d26-28 — giá trị biên thu hoạch lấp đầy
            # vượt chi phí fib thợ (bài học 13th worker trong LESSONS_V4)
            if 26 <= day <= 28 and (stats.get("total", 0) >= 22 or money >= 1500):
                cap = 15
            # v5-P1 L7: dự báo thua (BEHIND) → +1 thợ đẩy thông lượng đua lại
            if tier == "BEHIND" and 9 <= day <= 25 and money >= 2200:
                cap += 1
            # v5.2: NỢ NƯỚC = thiếu lao động trầm trọng (cây sắp chết) → mua
            # thêm thợ hôm nay (máy bơm cứu ruộng) — $89-233/ngày rẻ hơn chết cây
            try:
                wdb = int((tmx.get("water_debt", 0) if isinstance(tmx, dict) else 0) or 0)
            except Exception:
                wdb = 0
            if wdb >= 1 and 9 <= day <= 25 and money >= 3000:
                cap += 1
            target_units = min(cap, max(8, 6 + money // 500))
        elif day >= 1:
            target_units = 8
        else:
            target_units = 7
        target_units = max(target_units, min(11, 1 + int(math.ceil(workload * 2.6 / max(5, 23 - hour)))))
        want = target_units - (1 + len(hands))
        # v5 L6: F1 L2 mới co biên chế (L1 chỉ chặn mua thú — hire là máy hồi phục);
        # F3 cấp cứu tưới +1 thợ
        if int(rg.get("F1", 0) or 0) >= 2:
            want = max(0, want - 2)
        if int(rg.get("F3", 0) or 0) >= 2:
            want += 1
        n_hired = _g(me, "hires_today", 0) or 0
        cost = 0
        k = 0
        hire_floor = 60 if day <= 5 else 150
        if money > hire_floor + 88:
            hire_budget = min(money - hire_floor, max(88, money * 0.25))
        else:
            hire_budget = max(0, money - 10)
        while k < want and k < 5:
            c = _fib(n_hired + k)
            if cost + c > hire_budget:
                break
            cost += c
            orders.append(["HIRE"])
            k += 1

    bought = _STATE.setdefault(("bought", day), {"GOOSE": 0, "COW": 0, "SHEEP": 0, "LAND": 0})
    # v5-P1b: ĐẤT TRƯỚC TIÊN — bậc thang vốn HIRE > ĐẤT > hạt > thú.
    # Bài học seed 42: v4 mua 4th quadrant ($4k) ngay d12 → +25 ô trồng
    # → thắng; v5 cùng lúc dồn $2.9k vào thú + hạt đắt → ruộng không mở
    # rộng → mất 5 ngày bội số tăng trưởng. Gần đủ tiền đất (≥55% giá)
    # → hoãn hạt đắt + thú để tích lũy; đủ tiền → BUY_LAND đứng ĐẦU list.
    nq = len(unlocked)
    # vL5 GT-LAND (đất tối thiểu): chỉ NW+NE (50 ô, $1k) — kiểm định giả
    # thuyết "đất tối ưu = tối thiểu" khi wheat là monopoly-restraint.
    if nq >= 2:
        nq = 4
    lp = LAND_PRICES[nq - 1] if nq < 4 else None
    land_ready = False
    near_land = False
    if lp and nq < 4 and bought.get("LAND", 0) < 1 \
            and not (rg and int(rg.get("F1", 0) or 0) >= 2):
        owned_empty = sum(1 for row in tiles for t in row if t is None)
        if nq == 3:
            l_last, l_gate, l_buf = 21, 1.1, int(0.1 * lp) + 300
        else:
            l_last, l_gate, l_buf = 20, 1.3, int(0.15 * lp) + 300
        if day <= l_last and (day <= 1 or owned_empty <= 14 or money >= lp * l_gate) \
                and money >= lp + l_buf:
            land_ready = True
        elif day <= l_last and owned_empty <= 14 and money >= lp + l_buf - 800:
            # v5-P1d: tích lũy CHỈ khi ruộng thật đầy (≤14 ô trống — đúng tín
            # hiệu mua đất của v4) và thật sự gần đủ (≤$800 nữa). Không bao giờ
            # dùng ngưỡng tiền thuần — hạt strawberry là mạch doanh thu #1,
            # chặn nó vài ngày = mất $8-10k (bài học máu seed 7/101/909)
            near_land = True
    if land_ready:
        orders.append(["BUY_LAND"])
        bought["LAND"] = 1
        money -= lp

    seed_spent = 0
    # v5.2: dự trữ tiền cho 1 lượt mua thú khi L3-Price nói chân đó khan hiếm
    # (knobs_animal) — tránh hạt trong ngày ăn sạch tiền khiến BUY_ANIMAL đứng
    # sau trong list luôn fail (seed 42: v5 đứng 1 bò cả mùa vì thiếu $650).
    animal_reserve = 0
    try:
        ka = tmx.get("knobs_animal") if isinstance(tmx, dict) else None
        if ka and hour <= 8 and 4 <= day <= 20:
            an_cost = {"MILK": ("COW", 400), "WOOL": ("SHEEP", 500), "EGG": ("GOOSE", 300)}.get(ka)
            tgt_key = {"COW": "cow_target", "SHEEP": "sheep_target", "GOOSE": "goose_target"}
            if an_cost:
                an, cst = an_cost
                owned = sum(1 for row in tiles for t in row
                            if isinstance(t, dict) and t.get("animal") == an)
                owned += (shed.get(an, 0) or 0) if shed else 0
                if owned < (plan.get(tgt_key.get(an, ""), 0) or 0) and money >= cst + 250:
                    animal_reserve = cst + 250
    except Exception:
        animal_reserve = 0
    if hour <= 8 and 1 <= day <= 22 and not near_land \
            and not (rg and int(rg.get("F1", 0) or 0) >= 2):  # v5: F1 L2 ngừng mua thú; P1b: hoãn khi tích lũy đất
        struct_free = {"COOP": 0, "PASTURE": 0}
        for row in tiles:
            for t in row:
                if isinstance(t, dict):
                    k = t.get("kind")
                    if k in struct_free and "animal" not in t:
                        struct_free[k] += 1
        animals_total = sum(1 for row in tiles for t in row
                            if isinstance(t, dict) and "animal" in t)
        wt = _wheat_all(shed, inventories)
        wheat_ripe = sum(1 for row in tiles for t in row
                         if isinstance(t, dict) and t.get("kind") == "PLANT"
                         and t.get("crop") == "WHEAT"
                         and (day - t.get("planted_day", day)) >= 3)
        wt_supply = wt + 0.8 * wheat_ripe
        # v5.2 LATE-WINDOW GIÁ-CỔNG: giá sản phẩm ≥1.25× base = thị trường sâu
        # (bài học seed 555: sữa $270 mà cửa sổ mua bò đóng d16 → v4 độc chiếm
        # 15 thú, v5 đứng 9). Giá cao → nới w1 thêm 2 ngày; bò d18 vẫn kịp
        # 3-4 lứa sữa ×2 unit × giá cao = hòa vốn $400 trong 3 ngày.
        try:
            px_now = {p: float(prices.get(p, 0) or 0) for p in ("EGG", "MILK", "WOOL")}
            late_ext = {"GOOSE": 2 if px_now.get("EGG", 0) >= 62 else 0,
                        "SHEEP": 2 if px_now.get("WOOL", 0) >= 250 else 0,
                        "COW": 2 if px_now.get("MILK", 0) >= 200 else 0}
        except Exception:
            late_ext = {"GOOSE": 0, "SHEEP": 0, "COW": 0}
        animal_orders = []
        for animal, target, w0, w1 in (("GOOSE", plan.get("goose_target", 0), 2, 14),
                                       ("SHEEP", plan.get("sheep_target", 0), 4, 15),
                                       ("COW", plan.get("cow_target", 0), 5, 16)):
            w1 = w1 + late_ext.get(animal, 0)
            owned = sum(1 for row in tiles for t in row
                        if isinstance(t, dict) and t.get("animal") == animal)
            owned += (shed.get(animal, 0) or 0) if shed else 0
            ad = ANIMALS[animal]
            cash_floor = 250
            buy_per_day = 2 if (day <= 12) else 1
            if (owned < target and w0 <= day <= w1
                    and bought.get(animal, 0) < buy_per_day
                    and struct_free[ad["structure"]] > 0
                    and money >= ad["cost"] + cash_floor and shed_total < 92
                    and (wt_supply >= (animals_total + 1) * 1.3 or animals_total == 0)):
                animal_orders.append(["BUY_ANIMAL", animal, 1])
                bought[animal] = bought.get(animal, 0) + 1
                money -= ad["cost"]

    # v5.2 THỨ TỰ MUA CÓ ĐIỀU KIỆN: thú chiếm tiền buổi sáng CHỈ khi thị
    # trường động vật sâu (shop draw hoặc px_pred) — ngược lại hạt được giữ
    # nguyên vị trí (bài học seed 808/7: mua thú đúng tiền nhưng sai seed →
    # hạt bị hoãn → volume lúa mì tụt). Lệnh vẫn trong cùng list ≤10.
    _defer_animal = None
    try:
        _milks = sum(1 for s in (shops or []) if s in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
        _yarn = sum(1 for s in (shops or []) if s == "YARN_STORE")
        _animal_prio = (_milks + _yarn >= 2) or bool(tmx.get("knobs_animal") if isinstance(tmx, dict) else None)
    except Exception:
        _animal_prio = False
    _aord = locals().get("animal_orders") or []
    if not _animal_prio:
        _defer_animal = _aord
    elif _aord:
        for _ao in _aord:
            if len(orders) >= MAX_ORDERS:
                break
            orders.append(_ao)

    if hour <= 17 and seeds is not None:
        _crop_order = (("WHEAT",) if int(rg.get("F1", 0) or 0) >= 3
                       else ("WHEAT", "CARROT", "STRAWBERRY", "MELON", "TOMATO"))  # v5: F1 L3 chỉ giữ hạt wheat
        for crop in _crop_order:
            n_tiles = plan.get("crop_tiles", {}).get(crop, 0)
            if not n_tiles:
                continue
            if crop == "MELON" and day < 8 and day > 2:
                continue
            if crop == "STRAWBERRY" and day < 5:
                continue
            if crop == "TOMATO" and (day < 2 or day > 16):
                continue
            have = seeds.get(crop, 0) or 0
            if have < n_tiles:
                need = n_tiles - have
                unit = CROPS[crop]["seed"]
                floor = 80 if crop == "WHEAT" else (150 if crop == "STRAWBERRY" else 220)
                if crop == "STRAWBERRY":
                    floor = 900
                if crop == "MELON":
                    floor = 700
                max_afford = max(0, int((money - floor - (animal_reserve if crop == "STRAWBERRY" else 0)) // unit)) if unit > 0 else 0
                buy = min(need, max_afford)
                if buy > 0:
                    orders.append(["BUY_SEED", crop, buy])
                    money -= buy * unit
                    seed_spent += buy * unit
            if len(orders) >= 9:
                break
    if _defer_animal:
        for _ao in _defer_animal:
            if len(orders) >= MAX_ORDERS:
                break
            orders.append(_ao)

    animals = sum(1 for row in tiles for t in row
                  if isinstance(t, dict) and "animal" in t)
    plan_animals = plan.get("goose_target", 0) + plan.get("cow_target", 0) + plan.get("sheep_target", 0)
    # v5.4 Phase 5.3 — FEED WARFARE CÓ ĐIỀU KIỆN (RULES R37+R54, ô đầu tiên của
    # bảng best-response "đối thủ làm A → ta làm B"):
    # v5.3 đã chứng minh churn wheat là vũ khí zero-sum (ngừng mua = −0.117x/seed).
    # Nhưng trace mới cho thấy KHÔNG phải trận nào v4 cũng net-buyer (seed 101:
    # cả 2 bên đều mua 950/bán 1150 = net-seller) → pump chỉ bật khi telemetry
    # xác nhận đối thủ đang NET-BUY wheat sâu (−10u/ngày trung bình 5 ngày) VÀ
    # đàn đối thủ ≥ 10 (mua cám dài hạn). Khi đó: mua mạnh hơn (gate 38→48,
    # cap 10→16u/ngày) để đẩy mặt giá wheat — thuế rơi vào feedbuy của nó,
    # thu của mình từ self-grown bán đắt hơn. Dừng trước d26 (thanh lý).
    pump = False
    opp_wnet = 0.0
    try:
        odh = (tmx.get("opp_daily") or {}) if isinstance(tmx, dict) else {}
        ks = sorted(k for k in odh if isinstance(k, int) and k < day)[-5:]
        if ks:
            opp_wnet = sum(float((odh.get(k) or {}).get("WHEAT", 0.0) or 0.0)
                           for k in ks) / len(ks)
        _mode_p = str((tmx.get("mode") or "") if isinstance(tmx, dict) else "")
        # A/B 20 Sep (3/40 game bắn: +1201/−504/−1076 = net −$379, 1 win-flip)
        # → REVERT: v4 trên 20 seed chuẩn là churn-hai-chiều (WHEAT P25 −9 /
        # P75 +11, profiles_learned), KHÔNG phải net-buyer như seed 42 từng ngụ
        # ý. Giữ hạ tầng đo (opp_wnet/opp_herd) + diag p5 — vũ khí chờ đối thủ
        # net-buyer thật trên ladder (ô best-response "A→B" chưa đủ chứng cứ).
        pump = False
        if isinstance(tmx, dict):
            tmx["pump"] = bool(pump)
            tmx["opp_wnet"] = round(opp_wnet, 1)
    except Exception:
        pass
    # v5.3 P2 FEED WARFARE (bản cuối — bài học A/B trên 8 seed):
    # "churn" wheat của v5.2 KHÔNG phải lãng phí mà là VŨ KHÍ zero-sum —
    # áp lực mua của v5 nâng mặt giá wheat, đánh thuế vào feedbuy $32-41k
    # của v4 (net-buyer) và bán self-grown đắt hơn. Ngừng mua (bản
    # make-vs-buy tiết kiệm) = tự giải giáp: P2only mất −0.12x/seed (104:
    # 1.115→0.922, 106: 1.295→1.081, 111: 1.325→1.070). Giữ NGUYÊN cơ chế
    # mua v5.2 (gate 38/52/62/80 theo F2, want 1.5 ngày) + 2 thêm nhẹ:
    # cap 12u/ngày (chống blitz 120u vô thức) + đo feedbuy cho ledger/diag.
    if animals > 0 or plan_animals > 0:
        shed_wheat = (shed.get("WHEAT", 0) or 0) if shed else 0
        wheat_want = int(animals * 1.5) + 4
        if shed_wheat < wheat_want and money >= 400:
            need = min(10, wheat_want - shed_wheat)
            pw = _price("WHEAT", inv.get("WHEAT", MARKET_I0) - 1)
            afford = int((money * 0.35) // pw) if pw > 0 else 0
            n = min(need, afford)
            acute = shed_wheat < 6
            # v5 L6 F2: trả đắt hơn cho cám khi đàn nguy cơ — gate 38/52/62/80 theo level
            f2v = int(rg.get("F2", 0) or 0)
            wgate = 38 if f2v <= 0 else (52 if f2v == 1 else (62 if f2v == 2 else 80))
            if f2v >= 2 and pw > 0:
                afford = int((money * 0.5) // pw)
                n = min(need, afford)
            if n >= 1 and (pw <= wgate or (acute and pw <= wgate + 10)):
                orders.append(["BUY_PRODUCT", "WHEAT", n])
                money -= n * pw
                try:  # P2: đo feedbuy cho ledger + diag Arena (KHÔNG đổi hành vi)
                    if isinstance(tmx, dict):
                        tmx["feedbuy"] = float(tmx.get("feedbuy", 0.0) or 0.0) + n * pw
                        tmx["feed_units"] = int(tmx.get("feed_units", 0) or 0) + n
                except Exception:
                    pass

    absorb_key = ("absorb", day)
    if absorb_key not in _STATE:
        _STATE[absorb_key] = _forward_absorb(day, 0, shops)
    absorb = _STATE[absorb_key]
    glutted = set()
    for it in PRODUCTS:
        if it in ("FERTILIZER", "MELON"):
            continue
        over = inv.get(it, MARKET_I0) - MARKET_I0
        pr_now = prices.get(it, 0) or 0
        if over > absorb.get(it, 0) * 0.8 and pr_now < 0.75 * MARKET_PARAMS[it]["base"]:
            glutted.add(it)

    wheat_reserve = min(animals * 2 + 6, shed.get("WHEAT", 0) or 0) if day < 26 and shed else 0

    def _hold(it):
        h = HOLD.get(it, 0.90)
        # v5 L6: thanh lý tồn kho khi kẹt khẩn cấp (lối thoát cưỡng bức)
        if rg.get("liquidate"):
            h = min(h, 0.55)
        if str(rg.get("state")) == "SURVIVE":
            h = min(h, 0.35)
        # v5-P1 L7 (trọng tâm 2): tier từ BAYES RACE → uyển chuyển ngưỡng bán.
        # BEHIND: khóa doanh thu sớm (×0.93) — chắc chắn thu hơn chờ giá đẹp;
        # LEAD: kiên nhẫn ×1.02 — đang thắng, ép thị trường trả giá cao hơn.
        if tier == "BEHIND":
            h *= 0.93
        elif tier == "LEAD":
            h = min(0.99, h * 1.02)
        # v5-P1 L3-Price (trọng tâm 1→2): FRONT-RUN theo dự báo giá +3 ngày.
        # Bayes nói giá DỊCH (p3 ≤ 92% now) → bán NGAY trước cú dội của đối thủ;
        # Bayes nói giá TĂNG (p3 ≥ 110% now) → nắm chờ đỉnh (chỉ trước endgame).
        pxp = tmx.get("px_pred") if isinstance(tmx, dict) else None
        if pxp and 6 <= day <= 25 and it != "FERTILIZER":
            q = pxp.get(it) or {}
            now_, p3 = q.get("now"), q.get("p3")
            if now_ and p3:
                base_ = MARKET_PARAMS[it]["base"]
                if p3 <= now_ * 0.92:
                    h = min(h, (now_ * 0.97) / base_)
                    try:
                        tmx.setdefault("knobs_sell", set()).add(it)
                    except Exception:
                        pass
                elif p3 >= now_ * 1.10:
                    h = max(h, min(0.99, (p3 * 0.94) / base_))
                    try:
                        tmx.setdefault("knobs_hold", set()).add(it)
                    except Exception:
                        pass
        # ---- Task 21 GT-COURNOT: VÒNG NHỎ (mỗi lượt) — điều chế theo macro ----
        try:
            _gtq = ((tmx.get("gt") or {}).get(it)) or {}
            if _gtq and 6 <= day <= 25:
                if _gtq.get("dump"):
                    # Stackelberg front-run: đối thủ sắp dội lumpy (L2 P75 cao
                    # vượt 1.5×E) → bán NGAY vào sức mua còn nguyên trước sóng
                    h = max(0.85, h * 0.96)
                elif _gtq.get("calm"):
                    _pxq = (tmx.get("px_pred") or {}).get(it) or {}
                    _now, _p3 = _pxq.get("now"), _pxq.get("p3")
                    if _now and _p3 and _p3 >= _now * 1.05:
                        # Monopoly restraint: ngày êm + giá leo → nắm chờ đỉnh
                        h = min(0.99, h * 1.04)
        except Exception:
            pass
        dliq = 1 if tier == "BEHIND" else 0  # v5-P1: BEHIND thanh lý sớm 1 ngày
        if it in glutted:
            # v5.3 L1 DUMP (PLAN 4.5): không xả vào cú dump của đối thủ —
            # nâng ngưỡng chờ drain hút lại; mode khác giữ hành vi nền.
            try:
                _m = str((tmx.get("mode") if isinstance(tmx, dict) else "") or "")
            except Exception:
                _m = ""
            if _m == "DUMP":
                return h
            return min(h, 0.40)
        # Phase 5.2 E8-lite (đo từ battles: v5.2 ladder đã thu gần hết E8, tồn dư
        # cuối trận chỉ $250-800 — phần còn lại = KHÔNG hạ ngưỡng sớm khi drain
        # còn đủ hút TOÀN BỘ nguồn chờ bán: bán dần vào drain giá đẹp, d28+ vẫn dump)
        if 22 <= day <= 27 - dliq:
            try:
                n_pending = float(shed.get(it, 0) or 0) + float(pipe_rest.get(it, 0.0) or 0.0)
                if absorb_rest.get(it, 0.0) >= n_pending * 1.1 and n_pending > 0:
                    return h
            except Exception:
                pass
        if day >= 28 - dliq:
            return 0.004
        if day >= 26 - dliq:
            return min(h, 0.45)
        if day >= 22:
            return min(h, 0.70)
        if it == "MELON" and day >= 24:
            return min(h, 0.30)
        if it == "MELON" and day >= 21:
            return min(h, 0.42)
        if shed_total >= 80:
            return min(h, 0.72)
        if money < 250:
            return min(h, 0.65)
        return h

    # ---- Task 21 GT-COURNOT: VÒNG TOÀN CỤC (mỗi 24 lượt, đầu ngày) ----
    # Bậc 1 (quan sát): L2 Gamma-Poisson E/P25/P75 dòng bán đối thủ mỗi kênh.
    # Bậc 2 (can thiệp): quy về tín hiệu Cournot điều chế ngưỡng bán hôm nay —
    #   dump_sig → front-run (bán trước cú dội, giá chưa bị dìm);
    #   calm_sig → monopoly restraint (nắm chờ drain hồi giá).
    # Micro (mỗi lượt) áp dụng trong _hold() bên dưới. Ghi tm["gt"] cho diag.
    try:
        if hour <= 1 and 6 <= day <= 25:
            l2p = (tmx.get("l2_pred") or {}) if isinstance(tmx, dict) else {}
            gt = {}
            for it in PRODUCTS:
                if it in ("FERTILIZER",):
                    continue
                q = l2p.get(it) or {}
                _e = float(q.get("e", 0) or 0)
                _p75 = float(q.get("p75", 0) or 0)
                dump_sig = (_p75 >= 8.0 and _p75 >= 1.5 * max(1.0, _e))
                calm_sig = (_p75 <= 3.0 or (_e > 0 and _p75 < _e * 1.15 + 2.0))
                gt[it] = {"e": round(_e, 1), "p75": round(_p75, 1),
                          "dump": bool(dump_sig), "calm": bool(calm_sig)}
            if isinstance(tmx, dict):
                tmx["gt"] = gt
    except Exception:
        pass

    cands = []
    if shed:
        for it in PRODUCTS:
            if it == "FERTILIZER" and day < 26:
                nf = shed.get("FERTILIZER", 0) or 0
                keep = 0 if str(rg.get("state")) == "SURVIVE" else 2  # v5: SURVIVE bán sạch fert
                ffloor = 20 if (rg.get("liquidate") or str(rg.get("state")) == "SURVIVE") else FERT_FLOOR
                if nf > keep and day >= 1:
                    k = _sell_count("FERTILIZER", nf - keep, inv.get("FERTILIZER", MARKET_I0), ffloor)
                    if k > 0:
                        cands.append((k * 60, ["SELL", "FERTILIZER", k]))
                continue
            n = shed.get(it, 0) or 0
            if it == "WHEAT":
                n = max(0, n - wheat_reserve)
            if n <= 0:
                continue
            thresh = _hold(it) * MARKET_PARAMS[it]["base"]
            k = _sell_count(it, n, inv.get(it, MARKET_I0), thresh)
            if k > 0:
                cands.append((k * (prices.get(it, 0) or 0), ["SELL", it, k]))
    cands.sort(key=lambda c: -c[0])
    for _, o in cands:
        if len(orders) >= MAX_ORDERS:
            break
        orders.append(o)

    return orders[:MAX_ORDERS]


def _agent(obs):
    player = _g(obs, "player", 0)
    farms = _g(obs, "farms", None) or []
    if not farms or player is None or not (0 <= player < len(farms)):
        return {"farmer": ["PASS"], "hands": [], "market": []}
    me = farms[player]
    day = _g(obs, "day", 0) or 0
    hour = _g(obs, "hour", 0) or 0
    step = day * TURN_PER_DAY + hour
    if day == 0 and hour == 0:
        _STATE.clear()

    tiles = _g(me, "tiles", None) or []
    board = len(tiles)
    if board == 0:
        return {"farmer": ["PASS"], "hands": [], "market": []}

    private = _g(obs, "private", None) or {}
    market = _g(obs, "market", None) or {}
    town = _g(obs, "town", None) or {}
    shed = _g(private, "shed", None) or {}
    seeds = _g(private, "seeds", None) or {}
    inventories = _g(private, "inventories", None) or []
    prices = _g(market, "prices", None) or {}
    inv = _g(market, "inventory", None) or {}
    shops = _g(town, "unlocked_shops", None) or []
    opp = farms[1 - player] if len(farms) > 1 else None

    tm = _STATE.setdefault("tm", {})
    _tm_step(tm, step, inv, shops)
    my_money = float(_g(me, "money", 0) or 0)
    _sa_step(_STATE, day, hour, my_money)  # v5: L5 sổ KPI từng lượt
    rg = _rg_live(_STATE, day, hour, tiles, shed, inventories)  # v5: L6 F2 live
    try:  # v5: kênh tiền/thợ đối thủ vào tm (quantitive observability)
        tm["opp_money"] = float(_g(opp, "money", 0) or 0)
        tm["opp_hands"] = len(_g(opp, "hands", None) or [])
    except Exception:
        pass

    pkey = ("plan", day)
    if pkey not in _STATE:
        if day > 0 and hour == 0:  # v5: L5 tổng đêm + L6 F1/F3 trước khi lập kế hoạch
            _sa_night(_STATE, day - 1, tm, prices)
            _rg_night(_STATE, day, my_money, tm)
            try:  # v5.3 L2: Gamma-Poisson cập nhật posterior flow từ đêm qua
                _l2_night(tm, day)
            except Exception:
                pass
            try:  # v5-P1: L3-Price dự báo giá +3 ngày mỗi sáng
                tm["px_pred"] = _px_pred(tm, day, inv, prices, shops)
            except Exception:
                pass
        mc = sum(1 for row in tiles for t in row
                 if isinstance(t, dict) and t.get("animal") == "COW")
        mg = sum(1 for row in tiles for t in row
                 if isinstance(t, dict) and t.get("animal") == "GOOSE")
        msp = sum(1 for row in tiles for t in row
                  if isinstance(t, dict) and t.get("animal") == "SHEEP")
        _bayes_step(tm, day, opp, (mc, mg, msp), my_money)
        _STATE[pkey] = _daily_plan(tiles, shed, seeds, inv, prices, shops, day, opp,
                                   my_money, tm, _STATE.get("rg"))
    plan = _STATE[pkey]

    fpos = _g(me, "farmer", None) or [board // 2 - 1, board // 2 - 1]
    units = [(0, int(fpos[0]), int(fpos[1]))]
    for i, h in enumerate(_g(me, "hands", None) or []):
        units.append((i + 1, int(h[0]), int(h[1])))

    tasks, stats = _build_tasks(tiles, shed, seeds, plan, day, hour, step,
                                inventories, len(units))
    try:  # v5.2: L6 F3 — nợ tưới-cấp cứu, ghi ĐÈ ở mỗi giờ ≥16 để giá trị
    # cuối ngày (hour 23) phản ánh đúng số cây sắp chết lúc kết thúc ngày
        if hour >= 16:
            rk = _STATE.setdefault(("risk", day), {})
            rk["water_crit_late"] = int(stats.get("water_crit", 0) or 0)
    except Exception:
        pass

    orders = _build_orders(me, shed, seeds, inventories, inv, prices, day,
                           hour, plan, stats, tiles, shops)
    _tm_orders(tm, orders)

    actions = _assign_and_act(units, tasks, tiles, shed, inventories, day,
                              hour, board, seeds)

    return {"farmer": actions[0], "hands": actions[1:], "market": orders}


def _arena_diag(obs):
    """v5: xuất trạng thái não cho Arena Observer UI — được run_battle.py gọi sau
    mỗi lượt. Cấu trúc generic để BrainPanel render mọi key."""
    try:
        day = _g(obs, "day", 0) or 0
        tm = _STATE.get("tm", {}) or {}
        sa = _STATE.get("sa", {}) or {}
        rg = _STATE.get("rg", {}) or {}
        plan = _STATE.get(("plan", day)) or {}
        led = sa.get(("ledger", day)) or {}
        income = float(led.get("income", 0) or 0)
        spend = float(led.get("spend", 0) or 0)
        proj = sa.get("proj") or tm.get("proj") or {}
        tier = proj.get("tier") if isinstance(proj, dict) else None
        pxp = tm.get("px_pred") or {}
        fr = []
        hb = []
        if isinstance(pxp, dict):
            for p, q in pxp.items():
                try:
                    if not isinstance(q, dict):
                        continue
                    if q.get("p3", 0) <= q.get("now", 0) * 0.92:
                        fr.append(p)
                    elif q.get("p3", 0) >= q.get("now", 0) * 1.10:
                        hb.append(p)
                except Exception:
                    pass
        knobs = {
            "tier": tier or "BOOT",
            "front_run": fr,
            "hold_back": hb,
            "herd_expand": bool(tm.get("knobs_herd")),
            "fast_wheat": bool(tm.get("knobs_fastwheat")),
            "straw_compete": bool(tm.get("knobs_straw")),
            "water_debt": int(tm.get("water_debt", 0) or 0),
            "parity_chase": int(tm.get("knobs_parity", 0) or 0),
            "herd_gap": int(tm.get("herd_gap", 0) or 0),
            "pump": bool(tm.get("pump")),
        }
        fb = float(tm.get("feedbuy", 0.0) or 0.0)
        fu = int(tm.get("feed_units", 0) or 0)
        l1 = tm.get("l1f") or {}
        return {
            "ver": "v5.5",
            "strategy": "S-" + str(rg.get("state", "GROW")),
            "tier": tier,
            "tier_cand": (proj.get("cand") if isinstance(proj, dict) else None),
            "proj": ({"me": proj.get("me"), "opp": proj.get("opp"),
                      "gap": proj.get("gap"), "rel": proj.get("rel"),
                      "r_me": proj.get("r_me"), "r_opp": proj.get("r_opp"),
                      "calib_mae": proj.get("calib_mae")}
                     if isinstance(proj, dict) and proj else None),
            "knobs": knobs,
            "mode": tm.get("mode"),
            "l1": {h: round(float(v), 2) for h, v in l1.items()} if l1 else None,
            "l1_top": tm.get("l1_top"),
            "l2_mae": tm.get("l2_mae"),
            "pm": round(float(tm.get("pm", 0.0) or 0.0), 3),
            "health": round(float(sa.get("H", 1.0) or 0.0), 2),
            "health_parts": sa.get("H_parts"),
            "flow_pred": ({k: round(v, 1) for k, v in (tm.get("flow_pred") or {}).items()}
                           if tm.get("flow_pred") else None),
            "l2_pred": (tm.get("l2_pred") if tm.get("l2_pred") else None),
            "px_pred": pxp if pxp else None,
            "opp_flows": ({k: round(v, 1) for k, v in (tm.get("opp_day") or {}).items()}
                           if tm.get("opp_day") else None),
            "herd": {k: plan.get(k) for k in ("goose_target", "cow_target", "sheep_target")},
            "crop_plan": plan.get("crop_tiles"),
            "feed_demand": plan.get("feed_demand"),
            "feed": {"buy$": round(fb), "units": fu,
                     "px_avg": round(fb / fu, 1) if fu else None},
            "sa": {"income": round(income), "spend": round(spend),
                   "net": round(income - spend),
                   "opp_money": round(float(tm.get("opp_money", 0) or 0))},
            "p5": {"opp_wnet": tm.get("opp_wnet"),
                   "opp_herd": int(tm.get("opp_herd", 0) or 0),
                   "pump": bool(tm.get("pump"))},
            "gt": ({"land": "50 tiles",
                    "WHEAT": _gt_s(tm, "WHEAT"), "MILK": _gt_s(tm, "MILK"),
                    "WOOL": _gt_s(tm, "WOOL"), "EGG": _gt_s(tm, "EGG"),
                    "STRAWBERRY": _gt_s(tm, "STRAWBERRY"),
                    } if tm.get("gt") else None),
            "rg": {"F1": int(rg.get("F1", 0) or 0), "F2": int(rg.get("F2", 0) or 0),
                   "F3": int(rg.get("F3", 0) or 0),
                   "liquidate": bool(rg.get("liquidate"))},
            "errs": int(_STATE.get("errs", 0) or 0),
            "notes": list(rg.get("notes") or [])[-5:],
        }
    except Exception:
        return {"ver": "v5.5"}


def _gt_s(tm, item):
    """Task 21: chuỗi tóm tắt tín hiệu GT-Cournot một kênh cho diag Arena."""
    try:
        q = (tm.get("gt") or {}).get(item) or {}
        e = float(q.get("e", 0) or 0)
        p75 = float(q.get("p75", 0) or 0)
        tag = " DUMP→front-run" if q.get("dump") else (" calm→hold" if q.get("calm") else "")
        return f"E{e:.0f}/P75 {p75:.0f}u{tag}"
    except Exception:
        return None


def agent(obs):
    # Task 22 (CRITICAL): hàm này PHẢI là callable cuối cùng của file —
    # kaggle_environments chọn callable CUỐI làm agent khi nạp file/cell
    # (get_last_callable). Nếu thêm hàm sau đây, submission Kaggle sẽ gọi
    # nhầm hàm đó và agent đứng yên ($3,000). _arena_diag/_gt_s đặt TRƯỚC.
    try:
        return _agent(obs)
    except Exception:
        try:  # v5-P1: đếm lỗi âm thầm để diag quan sát được (không còn mù)
            _STATE["errs"] = int(_STATE.get("errs", 0) or 0) + 1
        except Exception:
            pass
        return {"farmer": ["PASS"], "hands": [], "market": []}
