#!/usr/bin/env python3
"""從公開的 Google Sheet 更新 data/ 的 CSV——G Drive 是資料來源，repo 內 CSV 只是備援快照。
抓不到（沒網路、環境擋 docs.google.com、表頭對不上）就沿用快照，照樣能跑。只用標準庫。
規則：只匯入本機檔已有的欄位；本機檔整欄留空的欄＝要 Agent 自己產出的結果欄，不匯入（避免 Sheet 上預填的答案洩給 Agent）。"""
import csv, io, os, sys, urllib.parse, urllib.request
SHEET_ID = "1j4aMy1BmCTMFv4Jlufmd_2_B7-CZgakzwlSoiTAt9Ks"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
JOBS = [("待辦追蹤","待辦追蹤_原始.csv","待辦事項")]  # (分頁名, 本機檔, 必要表頭)
def _t10(rows, path):
    dept = {}
    for line in open(os.path.join(ROOT, "data", "部門與窗口.md"), encoding="utf-8"):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) >= 3 and c[1] and c[2] and c[0] not in ("部門", "---"): dept[c[1]] = c[0].removesuffix("部")
    h = ["編號", "會議日期", "待辦事項", "負責人", "部門", "截止日期", "狀態", "備註", "提醒已發"]
    g = lambda r, k: r[rows[0].index(k)] if k in rows[0] and rows[0].index(k) < len(r) else ""
    out = [h]
    for i, r in enumerate(rows[1:], 1):
        out.append([f"T{i:02d}", g(r, "會議日期"), g(r, "待辦事項"), g(r, "負責人"), dept.get(g(r, "負責人"), ""), g(r, "截止日期"), g(r, "狀態"), g(r, "備註") or g(r, "備注"), ""])
    return out
TRANSFORM = {"待辦追蹤": _t10}
# 「_原始」是歸零用的基準；工作檔沒被 Agent 動過（＝跟基準一樣）才一起更新，避免蓋掉跑完的結果
_d = os.path.join(ROOT, "data")
if open(os.path.join(_d, "待辦追蹤.csv"), "rb").read() == open(os.path.join(_d, "待辦追蹤_原始.csv"), "rb").read():
    JOBS.append(("待辦追蹤", "待辦追蹤.csv", "待辦事項"))
def fetch(tab):
    u = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(tab)}"
    return list(csv.reader(io.StringIO(urllib.request.urlopen(u, timeout=15).read().decode("utf-8"))))
def merge(sheet, path):
    old = list(csv.reader(open(path, encoding="utf-8-sig")))
    want = old[0]
    skip = {h for j, h in enumerate(want) if not any(len(r) > j and r[j] for r in old[1:])}
    idx = {h: sheet[0].index(h) for h in want if h not in skip}
    return [want] + [[(r[idx[h]] if h in idx and idx[h] < len(r) else "") for h in want] for r in sheet[1:]]
for tab, local, key in JOBS:
    path = os.path.join(ROOT, "data", local)
    try:
        rows = fetch(tab)
        while rows and not any(rows[-1]): rows.pop()
        if not rows or key not in rows[0]: raise ValueError("表頭對不上")
        rows = TRANSFORM.get(tab, lambda r, p: r)(rows, path)
        rows = merge(rows, path) if os.path.exists(path) else rows
        crlf = "\r\n" if os.path.exists(path) and b"\r\n" in open(path, "rb").read(4000) else "\n"
        bom = os.path.exists(path) and open(path, "rb").read(3) == b"\xef\xbb\xbf"
        with open(path, "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as f:
            csv.writer(f, lineterminator=crlf).writerows(rows)
        print(f"{tab:<8} {len(rows)-1} 列（已從 Google Sheet 更新）→ data/{local}")
    except Exception as e:
        if os.path.exists(path): print(f"{tab:<8} 沿用快照（{e.__class__.__name__}: {e}）→ data/{local}")
        else: print(f"⚠️  {tab}：抓不到也沒有快照"); sys.exit(1)
