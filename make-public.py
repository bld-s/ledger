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
    '      <div className="warn" style={{ margin: "10px 0 4px" }}>🧪 <b>공개 템플릿 · 샘플 데이터</b> — 숫자는 전부 예시입니다. 입력·수정한 데이터는 <b>이 브라우저(localStorage)에만</b> 저장되고 서버로 전송되지 않습니다. 원장 탭 맨 위 <b>"시작하기"</b> 카드에서 샘플을 지우고 본인 계좌·자산을 입력하세요. 기기 간 동기화가 필요하면 원장 탭 "PC·모바일 동기화" 칸에 본인 구글 Apps Script URL을 넣으세요. 시세·환율은 시트 없이도 트레이딩뷰 스캐너·ER-API(무료, 지연)로 자동 조회됩니다. 투자 판단의 책임은 본인에게 있습니다.</div>\n',
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


# Q. 간단 입력 UI (공개판 전용): "자산 추가" 카드(현금/주식) · 더보기(샘플·백업·시트) · 행 도구 · 빈 원장 가드 · 목표 비율 시뮬레이션
def insert_after_re(pattern, text, label):
    global s
    m = list(re.finditer(pattern, s))
    assert len(m) == 1, f"[{label}] regex matched {len(m)} times"
    e = m[0].end(); s = s[:e] + text + s[e:]

rep('  trades: [],\n  lastSettled: "",\n};\n', '  trades: [],\n  lastSettled: "",\n  _sample: true, // 샘플 데이터 표시 (더보기 → 샘플 비우기 하면 false)\n};\n', label="INIT _sample")
rep('const ACCTS = ["증권A", "증권B (해외)", "코인", "은행", "묶인자산"];', 'const ACCTS_DEFAULT = ["은행", "증권사"];', label="ACCTS default")
rep('  const [st, setSt] = useState(INIT);\n', '  const [st, setSt] = useState(INIT);\n  // 계좌 목록 = 보유 항목의 계좌(+원장에 저장된 accts). 비어 있으면 기본값\n  const ACCTS = (() => { const a = [...new Set([...(st.accts || []), ...(st.holdings || []).map((h) => h.acct)])]; return a.length ? a : ACCTS_DEFAULT; })();\n', label="ACCTS dynamic")
insert_after_re(r'  const \[form, setForm\] = useState\(\{[^\n]*\n', '  useEffect(() => { if (ACCTS.length && !ACCTS.includes(form.acct)) setForm((x) => ({ ...x, acct: ACCTS[0] })); }, [ACCTS.join("|")]);\n', "form acct guard")
anchor_sync = '  const [syncMsg, setSyncMsg] = useState("");\n'
rep(anchor_sync, anchor_sync + '  const [pubAdv, setPubAdvRaw] = useState(LS.getItem("pubAdv") === "1"); const setPubAdv = (v) => { setPubAdvRaw(v); LS.setItem("pubAdv", v ? "1" : "0"); };\n', label="pubAdv state")

ACTIONS = """  // ── 간단 입력 액션 (공개판) ──
  const deleteHolding = (ix) => { const h = st.holdings[ix]; if (!confirm(`"${h.acct} / ${h.name}" 항목을 삭제할까요? (거래 기록은 남습니다)`)) return; save({ ...st, holdings: st.holdings.filter((_, i) => i !== ix), baseDate: today() }); };
  const renameHolding = (ix) => { const h = st.holdings[ix]; const n = prompt("항목 이름", h.name); if (n == null || !n.trim() || n.trim() === h.name) return; if (st.holdings.some((x, i) => i !== ix && x.acct === h.acct && x.name === n.trim())) return alert("같은 계좌에 같은 이름의 항목이 있습니다"); const hs = [...st.holdings]; hs[ix] = { ...hs[ix], name: n.trim() }; save({ ...st, holdings: hs }); };
  const clearSample = () => { if (!confirm("샘플 데이터(보유 항목·거래·생활비)를 전부 지우고 빈 원장에서 시작할까요?")) return; save({ ...st, holdings: [], trades: [], living: {}, lastSettled: "", _sample: false }); };
  const restoreSample = () => { if (confirm("원장을 샘플 초기값으로 되돌릴까요? (현재 입력한 내용은 사라집니다)")) save(INIT); };
  const usdToMan = (q) => { const f0 = +fx || fxAuto || 0; return f0 ? Math.round(q * f0) / 10000 : 0; };
  // 현금: 은행 → "입출금"(월 정산 대상) / 증권사·코인거래소 → "예수금"(실탄) / 달러 → "달러예수금". 같은 계좌·항목이 있으면 금액 갱신
  const addCash = ({ acct, where, amount, usd }) => { const name = usd ? "달러예수금" : (where === "은행" ? "입출금" : "예수금"); const hs = [...st.holdings]; const i = hs.findIndex((h) => h.acct === acct && h.name === name); const row = usd ? { acct, name, sym: "", qty: amount, val: usdToMan(amount), type: "현금", usdCash: true } : { acct, name, sym: "", qty: 1, val: amount / 10000, type: "현금" }; if (i >= 0) hs[i] = { ...hs[i], ...row }; else hs.push(row); save({ ...st, holdings: hs, baseDate: today(), _sample: false }); return i >= 0 ? "갱신" : "추가"; };
  // 주식·ETF·코인: 같은 계좌에 같은 종목이 있으면 수량 합산 + 평단 가중평균
  const addStock = ({ acct, name, sym, cur, price, qty }) => { const f0 = +fx || fxAuto || 0; const unitKrw = cur === "USD" ? price * f0 : price; const fmtP = (p) => cur === "USD" ? "$" + p.toLocaleString(undefined, { maximumFractionDigits: 2 }) : "₩" + Math.round(p).toLocaleString(); const type = sym.startsWith("CURRENCY:") ? "코인" : /금현물|엔선물|골드|은선물|달러선물/.test(name) ? "대체" : "주식"; const hs = [...st.holdings]; const i = hs.findIndex((h) => h.acct === acct && h.sym === sym); if (i >= 0) { const o = hs[i]; const oq = o.qty || 0; const oAvg = parseFloat(String(o.usdAvg || o.avg || "").replace(/[^0-9.]/g, "")) || 0; const nq = oq + qty; const nAvg = oAvg ? (oAvg * oq + price * qty) / nq : price; hs[i] = { ...o, qty: nq, val: o.val + (unitKrw ? (qty * unitKrw) / 10000 : 0), avg: fmtP(nAvg), ...(cur === "USD" ? { usdAvg: fmtP(nAvg) } : {}) }; delete hs[i].manual; } else { const row = { acct, name, sym, qty, val: unitKrw ? (qty * unitKrw) / 10000 : 0, type, avg: fmtP(price) }; if (cur === "USD") row.usdAvg = fmtP(price); hs.push(row); } save({ ...st, holdings: hs, baseDate: today(), _sample: false, trades: [{ d: today(), side: "매수", acct, name, qty, price: fmtP(price), amt: unitKrw ? (qty * unitKrw) / 10000 : 0, memo: "자산 추가 카드에서 입력" }, ...(st.trades || [])] }); return i >= 0 ? "합산" : "추가"; };
  const exportJson = () => { const blob = new Blob([JSON.stringify(st, null, 2)], { type: "application/json" }); const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = `ledger-${today()}.json`; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 1000); };
  const importJson = (file) => { const r = new FileReader(); r.onload = () => { try { const L = JSON.parse(r.result); if (!L || !Array.isArray(L.holdings)) throw new Error("holdings 배열이 없습니다"); if (!confirm(`원장을 가져올까요? (항목 ${L.holdings.length}개 · 거래 ${(L.trades || []).length}건) 현재 원장은 덮어써집니다.`)) return; const hs = L.holdings.filter((h) => h && typeof h.acct === "string" && typeof h.name === "string").map((h) => ({ ...h, acct: h.acct.trim() || "기타", name: h.name.trim(), qty: Number.isFinite(+h.qty) ? +h.qty : 1, val: Number.isFinite(+h.val) ? +h.val : 0, type: TYPE_COLOR[h.type] ? h.type : "현금", sym: typeof h.sym === "string" ? h.sym : "" })); save({ ...st, ...L, holdings: hs, accts: Array.isArray(L.accts) && L.accts.length ? L.accts : [...new Set(hs.map((h) => h.acct))], living: (L.living && typeof L.living === "object" && !Array.isArray(L.living)) ? L.living : {}, trades: Array.isArray(L.trades) ? L.trades : [], lastSettled: L.lastSettled || "", baseDate: L.baseDate || today(), _sample: false }); } catch (e) { alert("가져오기 실패: " + e.message); } }; r.readAsText(file); };
"""
rep('  const editVal = (ix, n) =>', ACTIONS + '  const editVal = (ix, n) =>', label="simple-input actions")

rep('>●</span> {h.name}', '>●</span> {h.name}<span className="rowtools"><a href="#" title="이름 바꾸기" onClick={(e) => { e.preventDefault(); renameHolding(h.ix); }}>✎</a><a href="#" title="항목 삭제" onClick={(e) => { e.preventDefault(); deleteHolding(h.ix); }}>✕</a></span>', label="row tools")
rep('        @media(max-width:600px){', '        .rowtools a{color:#4F5E75;font-size:11px;margin-left:5px;text-decoration:none}.rowtools a:hover{color:#F2B84B}\n        .seg{display:flex;gap:4px}.seg button{background:#2B3A52;border:0;color:#E6E9EF;padding:6px 12px;border-radius:6px;cursor:pointer;font-size:13px}.seg button.on{background:#3a2f18;color:#F2B84B}\n        .tgt{width:46px;background:#101826;color:#F2B84B;border:1px solid #2B3A52;border-radius:4px;text-align:right;font-family:ui-monospace,monospace;padding:2px 4px;font-size:12px}\n        @media(max-width:600px){', label="simple-input css")

# 빈 원장(총액 0·생활비 0) 가드
rep('(h.val / total) * 100', '(total ? (h.val / total) * 100 : 0)', label="row pct guard")
rep('(sub / total) * 100', '(total ? (sub / total) * 100 : 0)', label="subtotal pct guard")
rep('(v / total) * 100', '(total ? (v / total) * 100 : 0)', count=2, label="legend pct guard")
rep('{Math.floor(cashOnly / livingTotal)}개월 버팀', '{livingTotal ? Math.floor(cashOnly / livingTotal) : "∞"}개월 버팀', label="living guard")
_n = s.count('((cashOnly / liquid) * 100).toFixed(0)'); s = s.replace('((cashOnly / liquid) * 100).toFixed(0)', '((liquid ? (cashOnly / liquid) * 100 : 0).toFixed(0))'); print(f"liquid guard: {_n} site(s)")
_n = s.count('달러 자산 시세 로딩 중…'); s = s.replace('달러 자산 시세 로딩 중…', '달러 자산 없음 · 또는 시세 로딩 중…'); print(f"usd card empty text: {_n} site(s)")

# 배너 축약
rep_re(r'<div className="warn" style=\{\{ margin: "10px 0 4px" \}\}>🧪 <b>공개 템플릿 · 샘플 데이터</b>[^\n]*</div>\n', '<div className="warn" style={{ margin: "10px 0 4px" }}>🧪 <b>공개 템플릿</b> — 숫자는 샘플. 아래 <b>"자산 추가"</b>에 내 계좌·종목을 넣으면 시세·환율이 자동 반영됩니다. 데이터는 이 브라우저에만 저장(서버 전송 없음). 투자 판단의 책임은 본인에게 있습니다.</div>\n', "short banner")

# 배분센터 목표 비율 편집(시뮬레이션)
rep('function AllocCenter({ holdings, money }) {', 'function AllocCenter({ holdings, money, target, onTarget }) {\n  const T = target || ALLOC_TARGET;', label="AllocCenter props")
rep('const rows = Object.keys(ALLOC_TARGET).map((k) => { const cur = tot ? (sums[k] / tot) * 100 : 0; const tgt = ALLOC_TARGET[k];', 'const rows = Object.keys(T).map((k) => { const cur = tot ? (sums[k] / tot) * 100 : 0; const tgt = T[k];', label="AllocCenter rows")
rep('<div className="eyebrow" style={{ marginBottom: 8 }}>배분 센터 · 목표 성장5 : 인컴3 : 지수2 (현금성 제외 · 엔·금은 지수 포함)</div>', '<div className="eyebrow" style={{ marginBottom: 8, display: "flex", flexWrap: "wrap", alignItems: "center", gap: 8 }}>배분 센터 · 목표 {["성장", "인컴", "지수"].map((k) => <span key={k}>{k} <input className="tgt" type="number" min="0" max="100" value={T[k]} onChange={(e) => onTarget && onTarget({ ...T, [k]: Math.max(0, Math.min(100, +e.target.value || 0)) })} />%</span>)}{(T.성장 + T.인컴 + T.지수) !== 100 && <span style={{ color: "#E5484D" }}>합 {T.성장 + T.인컴 + T.지수}% ≠ 100</span>}<span style={{ textTransform: "none", letterSpacing: 0 }}>· 비율을 바꿔 시뮬레이션 (현금성 제외)</span></div>', label="AllocCenter eyebrow")
rep('<AllocCenter holdings={view.holdings} money={money} />', '<AllocCenter holdings={view.holdings} money={money} target={st.allocTarget || ALLOC_TARGET} onTarget={(t) => save({ ...st, allocTarget: t })} />', label="AllocCenter mount")
rep('Object.keys(ALLOC_TARGET).map((k) => ({ k, gap: (tot ? (sums[k] / tot) * 100 : 0) - ALLOC_TARGET[k] }))', 'Object.keys(st.allocTarget || ALLOC_TARGET).map((k) => ({ k, gap: (tot ? (sums[k] / tot) * 100 : 0) - (st.allocTarget || ALLOC_TARGET)[k] }))', label="fear worst target")

# 시트 동기화 카드는 더보기에서 켰거나 URL이 있을 때만
rep('        <div className="card">\n          <div className="eyebrow" style={{ marginBottom: 8 }}>PC·모바일 동기화 (구글 시트)</div>', '        {(pubAdv || !!syncUrl) && <div className="card">\n          <div className="eyebrow" style={{ marginBottom: 8 }}>PC·모바일 동기화 (구글 시트)</div>', label="sync card open")
insert_after_re(r'<p className="muted" style=\{\{ marginTop: 6 \}\}>\{syncMsg \|\| "[^\n]*\n        </div>', '}', "sync card close")

PUBADD = """// ───────── 공개 템플릿 · 자산 추가 카드 (현금 / 주식·ETF·코인) ─────────
function PubAdd({ st, act, status }) {
  const [mode, setMode] = useState("현금");
  const [where, setWhere] = useState("은행"); const [acct, setAcct] = useState("");
  const [won, setWon] = useState(""); const [usd, setUsd] = useState(false);
  const [q, setQ] = useState(""); const [pick, setPick] = useState(null); const [price, setPrice] = useState(""); const [qty, setQty] = useState("");
  const [adv, setAdv] = useState(false); const [msg, setMsg] = useState(""); const fileRef = React.useRef();
  const cands = q.trim() && !pick ? krxMatches(q) : [];
  const resolve = () => { if (pick) return pick; const t = q.trim(); if (!t) return null; if (/^[0-9A-Za-z]{6}$/.test(t) && /[0-9]/.test(t)) { const c = t.toUpperCase(); return { name: krxNameOf(c) || c, sym: "KRX:" + c, cur: "KRW" }; } if (/^(btc|eth)$/i.test(t)) return { name: t.toUpperCase(), sym: "CURRENCY:" + t.toUpperCase() + "USD", cur: "USD" }; if (cands.length) return { name: cands[0][0], sym: "KRX:" + cands[0][1], cur: "KRW" }; if (/^[A-Za-z][A-Za-z.-]{0,5}$/.test(t)) return { name: t.toUpperCase(), sym: t.toUpperCase(), cur: "USD" }; return null; };
  const r = mode === "주식" ? resolve() : null;
  const whereS = where === "은행" ? "증권사" : where; const acctName = acct.trim() || (mode === "현금" ? where : whereS);
  const cashLabel = usd ? "달러예수금" : where === "은행" ? "입출금" : "예수금";
  const submitCash = () => { const n = parseFloat(String(won).replace(/[^0-9.]/g, "")); if (!n) return alert("금액을 입력하세요"); const res = act.addCash({ acct: acctName, where, amount: n, usd }); setWon(""); setMsg(`${acctName} · ${cashLabel} ${res}됨`); };
  const submitStock = () => { if (!r) return alert("종목을 찾지 못했습니다. 종목명(삼성전자)·6자리 코드·미국 티커(AMZN)·BTC 중 하나로 입력하세요"); const p = parseFloat(String(price).replace(/[^0-9.]/g, "")), n = parseFloat(String(qty).replace(/[^0-9.]/g, "")); if (!p || !n) return alert("매수 단가와 수량을 입력하세요"); const res = act.addStock({ acct: acctName, name: r.name, sym: r.sym, cur: r.cur, price: p, qty: n }); setQ(""); setPick(null); setPrice(""); setQty(""); setMsg(`${acctName} · ${r.name} ${n}${r.sym.startsWith("CURRENCY:") ? "개" : "주"} ${res}됨 — 현재가가 오면 평가금이 자동 갱신됩니다`); };
  return (<div className="card" style={{ borderColor: "#3E7B4F" }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
      <div className="eyebrow">자산 추가 {st._sample && <span style={{ color: "#F2B84B" }}>· 지금 표시된 건 샘플</span>}</div>
      <div className="seg">{[["현금", "현금 · 예금"], ["주식", "주식 · ETF · 코인"]].map(([m, l]) => <button key={m} className={mode === m ? "on" : ""} onClick={() => setMode(m)}>{l}</button>)}</div>
    </div>
    {mode === "현금" ? (<>
      <div className="form" style={{ marginTop: 10 }}>
        <select className="in" value={where} onChange={(e) => setWhere(e.target.value)}>{["은행", "증권사", "코인거래소"].map((w) => <option key={w}>{w}</option>)}</select>
        <input className="in" placeholder={"계좌 이름 (선택) 예: " + (where === "은행" ? "카카오뱅크" : where === "증권사" ? "○○증권 ISA" : "업비트")} value={acct} onChange={(e) => setAcct(e.target.value)} />
        <select className="in" value={usd ? "USD" : "KRW"} onChange={(e) => { setUsd(e.target.value === "USD"); setWon(""); }}><option value="KRW">₩ 원화</option><option value="USD">$ 달러</option></select>
        <input className="in" inputMode="decimal" placeholder={usd ? "달러 잔액 ($)" : "잔액 (원) 예: 1,234,567"} value={won} onChange={(e) => { const v = e.target.value; if (usd) setWon(v.replace(/[^0-9.]/g, "")); else { const d = v.replace(/[^0-9]/g, ""); setWon(d ? (+d).toLocaleString("ko-KR") : ""); } }} onKeyDown={(e) => { if (e.key === "Enter") submitCash(); }} />
        <button className="btn" onClick={submitCash}>추가</button>
      </div>
      <p className="muted" style={{ marginTop: 6 }}>→ "{acctName}" 계좌의 <b>{cashLabel}</b> 항목으로 들어갑니다. 같은 항목이 이미 있으면 금액이 그 값으로 갱신됩니다.</p>
    </>) : (<>
      <div className="form" style={{ marginTop: 10 }}>
        <select className="in" value={whereS} onChange={(e) => setWhere(e.target.value)}>{["증권사", "코인거래소"].map((w) => <option key={w}>{w}</option>)}</select>
        <input className="in" placeholder="계좌 이름 (선택)" value={acct} onChange={(e) => setAcct(e.target.value)} />
        <input className="in" placeholder="종목: 삼성전자 · 005930 · AMZN · BTC" value={q} onChange={(e) => { setQ(e.target.value); setPick(null); }} />
        <input className="in" inputMode="decimal" placeholder={"매수 단가 (" + (r && r.cur === "USD" ? "$" : "₩") + ")"} value={price} onChange={(e) => setPrice(e.target.value)} />
        <input className="in" inputMode="decimal" placeholder="수량" value={qty} onChange={(e) => setQty(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") submitStock(); }} />
        <button className="btn" onClick={submitStock}>추가</button>
      </div>
      {cands.length > 0 && <div style={{ marginTop: 6 }}>{cands.slice(0, 8).map(([n, c]) => <button key={c} className="chip" style={{ border: 0, cursor: "pointer", color: "#F2B84B" }} onClick={() => { setPick({ name: n, sym: "KRX:" + c, cur: "KRW" }); setQ(n); }}>{n} ({c})</button>)}</div>}
      <p className="muted" style={{ marginTop: 6 }}>{r ? <>→ <b>{r.name}</b> <span style={{ fontFamily: "ui-monospace,monospace" }}>{r.sym}</span> · {r.cur === "USD" ? "달러" : "원화"} 종목. 평가금은 수량 × 현재가(트레이딩뷰, 15~20분 지연)로 자동 계산되고, 매수 단가는 수익률에 쓰입니다.</> : "종목명(한글) · 6자리 코드 · 미국 티커 · BTC/ETH 중 하나로 입력"}</p>
    </>)}
    {msg && <p style={{ marginTop: 4, color: "#7ED491", fontSize: 13 }}>✓ {msg}</p>}
    <p className="muted" style={{ marginTop: 6, fontSize: 12 }}>표에서 숫자 클릭 = 수정 · ✎ 이름 · ✕ 삭제 · 추가 매수/매도 체결은 매매 탭{status ? " · " + status : ""}</p>
    <div style={{ marginTop: 6 }}><a href="#" style={{ color: "#8FA3BF", fontSize: 12 }} onClick={(e) => { e.preventDefault(); setAdv(!adv); }}>{adv ? "▲ 접기" : "▼ 더보기 (샘플 비우기 · JSON 백업 · 구글 시트 동기화)"}</a></div>
    {adv && <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap" }}>
      <button className="btn sec" onClick={act.clearSample}>샘플 데이터 비우기</button>
      <button className="btn sec" onClick={act.restoreSample}>샘플로 되돌리기</button>
      <button className="btn sec" onClick={act.exportJson}>JSON 내보내기</button>
      <button className="btn sec" onClick={() => fileRef.current && fileRef.current.click()}>JSON 가져오기</button>
      <input ref={fileRef} type="file" accept="application/json,.json" style={{ display: "none" }} onChange={(e) => { const file = e.target.files && e.target.files[0]; if (file) act.importJson(file); e.target.value = ""; }} />
      <button className="btn sec" onClick={() => act.setPubAdv(!act.pubAdv)}>{act.pubAdv ? "구글 시트 동기화 숨기기" : "구글 시트 동기화 설정 보기"}</button>
    </div>}
  </div>);
}

"""
rep('function App() {', PUBADD + 'function App() {', label="PubAdd component")
rep('      {tab === "원장" && (<>\n', '      {tab === "원장" && (<>\n        <PubAdd st={st} status={syncMsg} act={{ addCash, addStock, clearSample, restoreSample, exportJson, importJson, pubAdv, setPubAdv }} />\n', label="PubAdd mount")


# R. 리뷰 반영 (공개판): 정산 대상 계좌명 비고정 · 시세 효과 의존성 · 매매 예수금 차감 대상 · 실탄 판정 · 자산별 라벨 · 샘플 플래그
rep('const settleDue = settleWindow && st.lastSettled !== ymNow;', 'const settleBank = st.holdings.find((h) => h.type === "현금" && !h.sym && !h.usdCash && h.name === "입출금"); // 계좌명과 무관하게 "입출금" 현금 항목이 정산 대상\n  const settleDue = settleWindow && st.lastSettled !== ymNow && !!settleBank;', label="settleDue gate")
rep('const bank = hs.find((h) => h.acct === "은행" && h.name === "입출금");', 'const bank = hs.find((h) => h.type === "현금" && !h.sym && !h.usdCash && h.name === "입출금");', label="settle bank lookup")
rep('acct: "은행", name: `월정산', 'acct: bank.acct, name: `월정산', label="settle trade acct")
rep('{settleWindow && !settleDue && <div className="card">', '{settleWindow && !settleDue && settleBank && <div className="card">', label="settle done gate")
rep('차액은 체결 내역에 "월정산 {ymNow}"으로 기록됩니다.</p>', '차액은 체결 내역에 "월정산 {ymNow}"으로 기록됩니다. 정산 대상은 이름이 "입출금"인 현금 항목입니다(계좌 이름은 무관).</p>', label="settle hint")
rep('[syncUrl, st.holdings.length]', '[syncUrl, st.holdings.map((h) => h.sym).join("|")]', label="price fallback deps")
rep('saveDebounced({ ...st, holdings: hs, baseDate: today() })', 'saveDebounced({ ...st, holdings: hs, baseDate: today(), _sample: false })', count=2, label="edit clears sample flag")
rep('const cashIx = hs.findIndex((h) => h.acct === form.acct && h.type === "현금");', 'const cashIx = (() => { const a = hs.findIndex((h) => h.acct === form.acct && h.type === "현금" && !h.sym && !h.usdCash); return a >= 0 ? a : hs.findIndex((h) => h.acct === form.acct && h.type === "현금" && !h.usdCash); })(); // 시세 연동(ETF)·달러예수금이 아닌 원화 예수금을 우선 차감\n    const usdIx = form.cur === "USD" ? hs.findIndex((h) => h.acct === form.acct && h.usdCash) : -1; const fxT = +fx || fxAuto || 0;', label="trade cash lookup")
rep('if (cashIx >= 0) hs[cashIx] = { ...hs[cashIx], val: hs[cashIx].val - amt };', 'if (usdIx >= 0) { const q = Math.round((hs[usdIx].qty - qty * price) * 100) / 100; hs[usdIx] = { ...hs[usdIx], qty: q, val: fxT ? Math.round(q * fxT) / 10000 : hs[usdIx].val }; } else if (cashIx >= 0) hs[cashIx] = { ...hs[cashIx], val: hs[cashIx].val - amt };', label="trade debit")
rep('if (cashIx >= 0) hs[cashIx] = { ...hs[cashIx], val: hs[cashIx].val + amt };', 'if (usdIx >= 0) { const q = Math.round((hs[usdIx].qty + qty * price) * 100) / 100; hs[usdIx] = { ...hs[usdIx], qty: q, val: fxT ? Math.round(q * fxT) / 10000 : hs[usdIx].val }; } else if (cashIx >= 0) hs[cashIx] = { ...hs[cashIx], val: hs[cashIx].val + amt };', label="trade credit")
rep('const USD_RESERVE_NAMES = ["SGOV"];', 'const USD_RESERVE_NAMES = ["SGOV"];\n// 실탄(즉시 매수 가능 현금) = 이름에 "예수금"이 들어간 현금 항목(달러예수금 포함) — 2선(CMA·CD금리)·은행 입출금 제외\nconst isAmmo = (h) => h.type === "현금" && !h.sym && (h.name.includes("예수금") || !!h.usdCash) && !TIER2_NAMES.includes(h.name);', label="isAmmo")
rep('TIER1_NAMES.includes(h.name)', 'isAmmo(h)', count=2, label="ammo usage")
rep('(h.name.includes("반도체") ? "국내상장 섹터 ETF" : "국내상장 미국지수 ETF") : "미국 주식"', '(h.name.includes("미국") ? "국내상장 미국지수 ETF" : "국내 주식·ETF") : "해외 주식"', label="groupOf labels")
rep('"국내상장 섹터 ETF", "미국 주식"', '"국내 주식·ETF", "해외 주식"', label="GROUPS labels")

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
