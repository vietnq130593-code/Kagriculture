#!/usr/bin/env python3
"""Final reconciliation check: corrected doc tables vs regenerated daily.json (Task 83)."""
import io, json, re, sys

BASE = "/home/z/my-project/kaggle-research/top1"

def daily_map(m):
    return {(r["day"], r["player"]): r for r in json.load(open(f"{BASE}/{m}/daily.json"))}

ok = True

# --- 04A §1.1: parse the doc table and compare every cell ---
s = io.open(f"{BASE}/04A_MATCH2_MAJKEL_WIN_ANALYSIS.md", encoding="utf-8").read()
sec = s.split("## 1. Diễn biến tổng thể")[1].split("### 1.2")[0]
D2 = daily_map("match2")
prev = {0: 3000.0, 1: 3000.0}
rows = re.findall(r"\| (\d+) \| \*?\*?([\d,]+)\*?\*? \| \*?\*?\+?([\u2212-]?\d[\d,]*)\*?\*? \| ([\d,]+) \| \*?\*?\+?([\u2212-]?\d[\d,]*)\*?\*? \|", sec)
if len(rows) != 30:
    print(f"WARN: matched {len(rows)} rows in 04A table (expect 30)")
for d, mm, dm, dd, ddlt in rows:
    d = int(d)
    for p, m_doc, d_doc, nm in [(0, mm, dm, "M"), (1, dd, ddlt, "D")]:
        m_doc = float(m_doc.replace(",", ""))
        d_doc = float(d_doc.replace(",", "").replace("\u2212", "-"))
        rec = D2[(d, p)]
        if abs(rec["money_end"] - m_doc) > 0.5:
            print(f"FAIL 04A d{d} {nm} money_end doc={m_doc} data={rec['money_end']}"); ok = False
        if abs(rec["profit_day"] - d_doc) > 0.5:
            print(f"FAIL 04A d{d} {nm} Δ doc={d_doc} data={rec['profit_day']}"); ok = False
        prev[p] = rec["money_end"]

# --- 04B §1 ---
s = io.open(f"{BASE}/04B_MATCH1_MAJKEL_LOSS_ANALYSIS.md", encoding="utf-8").read()
sec = s.split("## 1. Money curve")[1].split("## 2. Opening")[0]
D1 = daily_map("match1")
rows = re.findall(r"\| (\d+) \| ([\d,]+) \(\+?([\u2212-]?\d[\d,]*)\) \| ([\d,]+) \(\+?([\u2212-]?\d[\d,]*)\)", sec)
if len(rows) != 30:
    print(f"WARN: matched {len(rows)} rows in 04B table (expect 30)")
for d, my, py, mj, pj in rows:
    d = int(d)
    for p, m_doc, p_doc, nm in [(0, my, py, "ymg"), (1, mj, pj, "maj")]:
        m_doc = float(m_doc.replace(",", ""))
        p_doc = float(p_doc.replace(",", "").replace("\u2212", "-"))
        rec = D1[(d, p)]
        if abs(rec["money_end"] - m_doc) > 0.5:
            print(f"FAIL 04B d{d} {nm} money_end doc={m_doc} data={rec['money_end']}"); ok = False
        if abs(rec["profit_day"] - p_doc) > 0.5:
            print(f"FAIL 04B d{d} {nm} profit doc={p_doc} data={rec['profit_day']}"); ok = False

# --- residual typo scan (CJK chars) in all 4 docs ---
import unicodedata
for f in ["04A_MATCH2_MAJKEL_WIN_ANALYSIS.md", "04B_MATCH1_MAJKEL_LOSS_ANALYSIS.md",
          "05_V19_DEPLOYMENT_PLAN.md", "README.md"]:
    t = io.open(f"{BASE}/{f}" if "README" in f else f"{BASE}/../{f}" if "05_" in f else f"{BASE}/{f}", encoding="utf-8").read()
    cjk = [(i, ch) for i, ch in enumerate(t) if unicodedata.category(ch) == "Lo" and ord(ch) > 0x2E80]
    if cjk:
        # allow → and math symbols; report CJK ideographs
        bad = [c for c in cjk if ord(c[1]) >= 0x4E00]
        if bad:
            print(f"WARN {f}: {len(bad)} CJK ideographs remain, e.g. {[c[1] for c in bad[:5]]}"); ok = False

print("RECONCILIATION:", "ALL PASS ✓" if ok else "FAILURES FOUND")
