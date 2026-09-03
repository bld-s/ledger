#!/usr/bin/env python3
"""KRX 상장종목+ETF 목록을 내려받아 asset-dashboard.html의 KRX_ALL 문자열을 갱신한다.
사용: python3 krx-update.py  (레포 루트에서) → 커밋 → 업로드 → curl 검증"""
import re, html, json, urllib.request, datetime
kind = urllib.request.urlopen("https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13", timeout=60).read().decode("euc-kr", "ignore")
stocks = {}
for r in re.findall(r"<tr[^>]*>(.*?)</tr>", kind, flags=re.S):
    c = [html.unescape(re.sub("<[^>]+>", "", x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", r, flags=re.S)]
    if len(c) >= 3 and re.fullmatch(r"\d{6}", c[2]) and c[1] != "코넥스": stocks[c[2]] = c[0]
etf = json.loads(urllib.request.urlopen("https://finance.naver.com/api/sise/etfItemList.nhn", timeout=30).read().decode("euc-kr", "ignore"))
for x in etf["result"]["etfItemList"]: stocks[x["itemcode"]] = x["itemname"]
lines = "\n".join(f"{k}|{v}" for k, v in sorted(stocks.items(), key=lambda kv: kv[1]))
assert "`" not in lines and "\\" not in lines and "${" not in lines
p = "asset-dashboard.html"; s = open(p, encoding="utf-8").read()
s2, n = re.subn(r"const KRX_ALL = `[^`]*`", "const KRX_ALL = `" + lines + "`", s, count=1)
assert n == 1
s2 = re.sub(r"— \d{4}-\d{2}-\d{2} KIND·네이버 기준", f"— {datetime.date.today()} KIND·네이버 기준", s2)
open(p, "w", encoding="utf-8").write(s2)
print(f"updated: {len(stocks)} entries")
