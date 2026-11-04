#!/usr/bin/env python3
"""asset-dashboard.html → 공개 템플릿(개인정보 제거·샘플 데이터) 생성기.
사용: python3 make-public.py  (ledger 레포 루트에서)
출력: ../asset-dashboard-public/index.html  (별도 공개 레포 bld-s/asset-dashboard-public 로 배포)
원칙: 모든 치환은 count==1 단언 → 원본이 바뀌어 앵커가 사라지면 즉시 실패(조용한 개인정보 누출 방지)."""
import re, sys, os, datetime

SRC = "asset-dashboard.html"
OUT_DIR = os.path.join("..", "asset-dashboard-public")
OUT = os.path.join(OUT_DIR, "index.html")
s = open(SRC, encoding="utf-8").read()
orig_stamp = re.search(r"최종 수정 (\d{4}-\d{2}-\d{2} \d{2}:\d{2})", s).group(1)
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def rep(old, new, count=1, label=""):
    global s
    n = s.count(old)
    assert n == count, f"[{label or old[:50]}] expected {count} occurrence(s), found {n}"
    s = s.replace(old, new)

def rep_re(pattern, new, label):
    global s
    m = re.findall(pattern, s, flags=re.S)
    assert len(m) == 1, f"[{label}] regex matched {len(m)} times"
    s = re.sub(pattern, lambda _: new, s, count=1, flags=re.S)

# A. 제목
rep("<title>자산 원장</title>", "<title>자산 대시보드 — 공개 템플릿</title>", label="title")

# B. INIT 전체 → 샘플 데이터
SAMPLE_INIT = '''// ───────── 샘플 초기 데이터 (공개 템플릿 · 숫자는 전부 예시) ─────────
const INIT = {
  baseDate: "2026-11-05",
  living: { 월세: 50, 관리비: 10, 통신: 5, 교통: 8, 보험: 10, 구독: 3, "식비·카페": 40 },
  holdings: [
    { acct: "증권A", name: "예수금", sym: "", qty: 1, val: 300, type: "현금" },
    { acct: "증권A", name: "TIGER 미국S&P500", sym: "KRX:360750", qty: 40, val: 104, type: "주식", avg: "₩26,000" },
    { acct: "증권A", name: "TIGER 미국배당다우존스", sym: "KRX:458730", qty: 60, val: 90, type: "주식", avg: "₩15,000" },
    { acct: "증권A", name: "ACE KRX금현물", sym: "KRX:411060", qty: 20, val: 54, type: "대체", avg: "₩27,000" },
    { acct: "증권B (해외)", name: "AMZN", sym: "AMZN", qty: 2, val: 68, type: "주식", avg: "₩300,000", usdAvg: "$220.00" },
    { acct: "증권B (해외)", name: "O", sym: "O", qty: 10, val: 75, type: "주식", avg: "₩75,000", usdAvg: "$55.00" },
    { acct: "증권B (해외)", name: "SGOV", sym: "SGOV", qty: 10, val: 138, type: "현금", avg: "₩138,000", usdAvg: "$100.50" },
    { acct: "증권B (해외)", name: "달러예수금", sym: "", qty: 500, val: 68, type: "현금", usdCash: true },
    { acct: "코인", name: "BTC", sym: "CURRENCY:BTCUSD", qty: 0.01, val: 105, type: "코인", avg: "₩95,000,000" },
    { acct: "은행", name: "입출금", sym: "", qty: 1, val: 250, type: "현금" },
    { acct: "묶인자산", name: "적금", sym: "", qty: 1, val: 300, type: "묶임" },
  ],
  trades: [],
  lastSettled: "",
};
'''
rep_re(r"// ───────── 원장 초기 데이터 \(2026\.08\.23\) ─────────\nconst INIT = \{.*?\n\};\n", SAMPLE_INIT, "INIT block")

# C. 계좌 목록 / 실탄 분류
rep_re(r'const ACCTS = \[[^\n]*\];', 'const ACCTS = ["증권A", "증권B (해외)", "코인", "은행", "묶인자산"];', "ACCTS")
rep('acct: "삼성증권", name: "", sym: ""', 'acct: "증권B (해외)", name: "", sym: ""', label="trade form default acct")
rep_re(r'const TIER1_NAMES = \[[^\n]*\];', 'const TIER1_NAMES = ["예수금", "원화예수금", "달러예수금"];', "TIER1")
rep_re(r'const TIER2_NAMES = \[[^\n]*\];', 'const TIER2_NAMES = ["CMA 예수금", "CD금리"];', "TIER2")

# D. 구글 시트 URL(개인 원장 엔드포인트) 제거 — 사용자가 직접 입력
rep_re(r'useState\(localStorage\.getItem\("sync"\)\|\|"https://script\.google\.com/macros/s/[^"]+"\)', 'useState(localStorage.getItem("sync") || "")', "syncUrl default")

# E. 저장 스탬프: 개인 대시보드와 구분 (개인 시트에 실수로 저장돼도 경고가 뜨도록 다른 태그)
rep('const APP_TAG = "asset-dashboard@bld-s.github.io";', 'const APP_TAG = "asset-dashboard-public";', label="APP_TAG")

# F. MIG + migrate (개인 평단·수량·거래 이력이 통째로 들어있음) → 무효화
assert s.count("  return ch; };\n") == 1, "migrate end anchor"
rep_re(r"  const MIG = \{.*?\n  return ch; \};\n", "  const MIG = {}; // 공개 템플릿: 개인 원장 마이그레이션 없음\n  const migrate = (L) => false;\n", "MIG+migrate")

# G. 월 정산: 특정 은행/적금 의존 제거
rep('return alert("KB 입출금 실제 잔액을 원 단위로 입력하세요 (예: 3,598,573)");', 'return alert("은행 입출금 실제 잔액을 원 단위로 입력하세요 (예: 1,234,567)");', label="settle alert1")
rep_re(r'    // KB 주거래 통장:[^\n]*\n', "    // 은행 계좌의 '입출금' 항목을 정산 대상으로 본다\n", "settle comment")
rep('const bank = hs.find((h) => h.acct === "은행" && h.name.includes("KB")) || hs.find((h) => h.acct === "은행" && h.name === "입출금");', 'const bank = hs.find((h) => h.acct === "은행" && h.name === "입출금");', label="settle bank")
rep('return alert("은행 계좌에서 KB 주거래 통장을 찾을 수 없습니다");', 'return alert("은행 계좌에 \'입출금\' 항목이 없습니다");', label="settle alert2")
rep('const saving = hs.find((h) => h.name.includes("청년미래적금"));', 'const saving = null; // 공개 템플릿: 적금 자동 가산 없음', label="settle saving")
rep('(saving ? " · 청년미래적금 +50만 자동 반영" : "")', '(saving ? " · 적금 자동 반영" : "")', label="settle memo")
rep("월 정산 — KB 입출금 현재 잔액 입력", "월 정산 — 은행 입출금 현재 잔액 입력", label="settle card title")
rep('placeholder="실제 잔액 (원) 예: 3,598,573"', 'placeholder="실제 잔액 (원) 예: 1,234,567"', label="settle placeholder")
rep('차액은 체결 내역에 "월정산 {ymNow}"으로 기록되고, 청년미래적금 +50만이 함께 반영됩니다.', '차액은 체결 내역에 "월정산 {ymNow}"으로 기록됩니다.', label="settle text")

# H. 청년미래적금 카드(개인 금융상품 상세) 통째로 제거
rep_re(r'        <div className="card">\n          <div className="eyebrow">청년미래적금.*?\n        </div>\n', "", "savings card")

# I. 초기값 복원 문구
rep('confirm("원장을 2026.08.23 초기값으로 되돌릴까요?")', 'confirm("원장을 샘플 초기값으로 되돌릴까요?")', label="reset confirm")

# J. 시황 탭: 개인 프로젝트명 제거
rep_re(r'<p>시황 분석과 매수·매도 상담은 <b>클로드 프로젝트 채팅</b>\("93년생 dop 자산 포폴"\)에서 합니다\.[^\n]*</p>', '<p>시황 분석과 매수·매도 상담은 <b>AI 채팅(클로드 등)</b>에서 하는 걸 권합니다. 원장 탭의 보유 내역을 복사해 붙여넣고, 웹검색 시황과 대조해 의견 + 반대의견을 함께 받으세요.</p>', "market tab text")

# K. 상단 배너 (공개 템플릿 안내)
rep('      <div className="eyebrow">자산·생활비 원장 · 기준일 {st.baseDate}</div>\n',
    '      <div className="eyebrow">자산·생활비 원장 · 기준일 {st.baseDate}</div>\n'
    '      <div className="warn" style={{ margin: "10px 0 4px" }}>🧪 <b>공개 템플릿 · 샘플 데이터</b> — 숫자는 전부 예시입니다. 입력·수정한 데이터는 <b>이 브라우저(localStorage)에만</b> 저장되고 서버로 전송되지 않습니다. 기기 간 동기화가 필요하면 원장 탭 "PC·모바일 동기화" 칸에 본인 구글 Apps Script URL을 넣으세요. 시세·환율은 시트 없이도 트레이딩뷰 스캐너·ER-API(무료, 지연)로 자동 조회됩니다. 투자 판단의 책임은 본인에게 있습니다.</div>\n',
    label="banner")

# L. 시트 없이도 시세·환율 자동 조회 (공개판 전용 — 트레이딩뷰 스캐너 + ER-API, 모두 브라우저 CORS 허용 확인)
PRICE_FALLBACK = '''  // 공개 템플릿: 시트 연동이 없을 때 보유 종목 시세(트레이딩뷰 스캐너, 15~20분 지연) + USD/KRW 환율(ER-API, 일 1회)을 직접 조회
  useEffect(() => { if (syncUrl) return; let alive = true; (async () => {
    try { const r = await fetch("https://open.er-api.com/v6/latest/USD"); const j = await r.json(); const k = j?.rates?.KRW; if (k && alive) { setFxAuto(k); if (!localStorage.getItem("fx")) setFx(String(Math.round(k * 10) / 10)); } } catch {}
    const syms = [...new Set(st.holdings.filter((h) => h.sym && !h.sym.startsWith("CURRENCY:JPY")).map((h) => h.sym))]; if (!syms.length) return;
    const tick = (x) => x.startsWith("KRX:") ? [x] : x === "CURRENCY:BTCUSD" ? ["BINANCE:BTCUSDT"] : x === "CURRENCY:ETHUSD" ? ["BINANCE:ETHUSDT"] : x.includes(":") ? [x] : ["NASDAQ:" + x, "NYSE:" + x, "AMEX:" + x];
    try { const r = await fetch("https://scanner.tradingview.com/global/scan", { method: "POST", headers: { "Content-Type": "text/plain" }, body: JSON.stringify({ symbols: { tickers: syms.flatMap(tick) }, columns: ["close", "change"] }) }); const j = await r.json(); const P = {}; syms.forEach((x) => { const row = (j.data || []).find((d) => tick(x).includes(d.s) && d.d && d.d[0] != null); if (row) P[x] = { p: row.d[0], chg: row.d[1] }; }); if (alive) { setPrices(P); setSyncMsg("시세 " + Object.keys(P).length + "종목 조회됨 (트레이딩뷰, 지연) " + new Date().toLocaleTimeString("ko-KR")); } } catch {}
  })(); return () => { alive = false; }; }, [syncUrl, st.holdings.length]);
'''
anchor = '  const [syncMsg, setSyncMsg] = useState("");\n'
rep(anchor, anchor + PRICE_FALLBACK, label="price fallback inject")

# M. 동기화 카드 안내 문구에 '선택' 명시
rep('placeholder="Apps Script 웹앱 URL"', 'placeholder="(선택) 본인 구글 Apps Script 웹앱 URL"', label="sync placeholder")

# N. 푸터
rep_re(r"최종 수정 \d{4}-\d{2}-\d{2} \d{2}:\d{2}", f"공개 템플릿 · 원본 {orig_stamp} 기준 · 생성 {now}", "footer")


# O. localStorage 네임스페이스 분리 — 공개판은 개인 대시보드와 같은 origin(bld-s.github.io)이라 키가 충돌하면 개인 원장/시트 URL을 읽거나 덮어씀
LS_SHIM = 'const { useState, useEffect, useMemo } = React;\nconst LS = { getItem: (k) => localStorage.getItem("pub:" + k), setItem: (k, v) => localStorage.setItem("pub:" + k, v), removeItem: (k) => localStorage.removeItem("pub:" + k) };\n'
rep('const { useState, useEffect, useMemo } = React;\n', LS_SHIM, label="LS shim")
head, sep, tail = s.partition(LS_SHIM)
assert sep, "LS shim split"
n_ls = tail.count("localStorage.")
tail = tail.replace("localStorage.", "LS.")
assert "localStorage." not in tail
s = head + sep + tail
print(f"localStorage → LS (pub: namespace): {n_ls} call sites")

# P. 개인 운용 규칙·문구 일반화 (전수조사 narrative 렌즈 반영)
rep("④ 10만원 이상은 채팅 먼저 · 24시간 뒤에도 같은 판단인지 확인.", "④ 큰 금액 매매는 하루 뒤에도 같은 판단인지 확인한 뒤 실행.", label="fear rule 4")
rep("(구버전 페이지가 열린 폰·브라우저, 또는 다른 클로드 세션)", "(다른 기기나 구버전 페이지)", label="foreign text")
rep("달러 노출 (장기 파킹 · 실시간)", "달러 노출 (실시간)", label="usd card title")
rep("내 평균 매입환율 <b", "평균 매입환율 <b", label="avg fx label")
rep_re(r'규칙: 10만원 이상 매매는 반드시 채팅 먼저\. 체결 후엔 매매 탭에 기록해야 다음 상담이 정확합니다\. 예시 질문: [^<]*', '팁: 매매 전에 상담하고, 체결 후엔 매매 탭에 기록하면 다음 상담이 정확해집니다. 예시 질문: "오늘 시황 분석" / "FOMC 전 상황 브리핑" / "S&P500 ETF 추가 매수 괜찮을까?"', "market tab tip")
rep("본인 배분 규칙(성장5:인컴3:지수2)과 손절선이 먼저입니다.", "본인이 정한 배분 규칙과 손절선이 먼저입니다.", label="footnote rule")

# ── 누출 검사: 개인 식별 문자열이 남아 있으면 실패 ──
LEAK = ["script.google.com", "AKfycb", "bld-s", "93년생", "KB국민", "청년미래적금", "미래에셋", "삼성증권", "키움", "토스뱅크",
        "0.01748425", "0.1049847", "510,310", "98,333,927", "2,678,247", "1,815,000", "229621", "49415", "출장", "FOMC 직후",
        "3,598,573", "2029-07-27", "개인사업자", "ONE통장", "Npay", "클로드 세션", "10만원 이상은 채팅", "장기 파킹"]
body = re.sub(r"const KRX_ALL = `[^`]*`", "const KRX_ALL = `…`", s, count=1)  # 공개 종목 목록(상장사명)은 검사 제외
leaks = [k for k in LEAK if k in body]
assert not leaks, f"LEAK: {leaks}"

os.makedirs(OUT_DIR, exist_ok=True)
open(OUT, "w", encoding="utf-8").write(s)
print(f"OK → {OUT} ({len(s):,} bytes) · 원본 기준 {orig_stamp} · 생성 {now}")
