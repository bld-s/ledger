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


# Q. 온보딩 (공개판 전용): 샘플 비우기 · 계좌 관리 · 항목 추가/이름변경/삭제 · JSON 백업 · 빈 원장 가드
def insert_after_re(pattern, text, label):
    global s
    m = list(re.finditer(pattern, s))
    assert len(m) == 1, f"[{label}] regex matched {len(m)} times"
    e = m[0].end(); s = s[:e] + text + s[e:]

rep('  trades: [],\n  lastSettled: "",\n};\n', '  trades: [],\n  lastSettled: "",\n  _sample: true, // 샘플 데이터 표시 (시작하기 카드에서 비우면 false)\n};\n', label="INIT _sample")
rep('const ACCTS = ["증권A", "증권B (해외)", "코인", "은행", "묶인자산"];', 'const ACCTS_DEFAULT = ["증권A", "증권B (해외)", "코인", "은행", "묶인자산"];', label="ACCTS default")
rep('  const [st, setSt] = useState(INIT);\n', '  const [st, setSt] = useState(INIT);\n  // 계좌 목록 = 원장에 저장된 accts(없으면 기본값) ∪ 보유 항목의 계좌 (가져온 원장의 낯선 계좌도 항상 표시)\n  const ACCTS = [...new Set([...((st.accts && st.accts.length) ? st.accts : ACCTS_DEFAULT), ...(st.holdings || []).map((h) => h.acct)])];\n', label="ACCTS dynamic")
insert_after_re(r'  const \[form, setForm\] = useState\(\{[^\n]*\n', '  useEffect(() => { if (ACCTS.length && !ACCTS.includes(form.acct)) setForm((x) => ({ ...x, acct: ACCTS[0] })); }, [ACCTS.join("|")]);\n', "form acct guard")

ACTIONS = """  // ── 온보딩 액션 (공개판) ──
  const deleteHolding = (ix) => { const h = st.holdings[ix]; if (!confirm(`"${h.acct} / ${h.name}" 항목을 삭제할까요? (거래 기록은 남습니다)`)) return; save({ ...st, holdings: st.holdings.filter((_, i) => i !== ix), baseDate: today() }); };
  const renameHolding = (ix) => { const h = st.holdings[ix]; const n = prompt("항목 이름", h.name); if (n == null || !n.trim() || n.trim() === h.name) return; if (st.holdings.some((x, i) => i !== ix && x.acct === h.acct && x.name === n.trim())) return alert("같은 계좌에 같은 이름의 항목이 있습니다"); const hs = [...st.holdings]; hs[ix] = { ...hs[ix], name: n.trim() }; save({ ...st, holdings: hs }); };
  const addHolding = (h) => save({ ...st, holdings: [...st.holdings, h], baseDate: today(), _sample: false });
  const clearSample = () => { if (!confirm("샘플 데이터(보유 항목·거래·생활비)를 전부 지우고 빈 원장에서 시작할까요?")) return; save({ ...st, holdings: [], trades: [], living: {}, lastSettled: "", _sample: false }); };
  const restoreSample = () => { if (confirm("원장을 샘플 초기값으로 되돌릴까요? (현재 입력한 내용은 사라집니다)")) save(INIT); };
  const renameAcct = (from, to) => { to = String(to || "").trim(); if (!to || to === from) return; if (ACCTS.includes(to)) return alert("이미 있는 계좌 이름입니다"); const accts = ACCTS.map((a) => (a === from ? to : a)); save({ ...st, accts, holdings: st.holdings.map((h) => (h.acct === from ? { ...h, acct: to } : h)), trades: (st.trades || []).map((t) => (t.acct === from ? { ...t, acct: to } : t)) }); if (form.acct === from) setForm({ ...form, acct: to }); };
  const addAcct = (name) => { name = String(name || "").trim(); if (!name) return; if (ACCTS.includes(name)) return alert("이미 있는 계좌 이름입니다"); save({ ...st, accts: [...ACCTS, name] }); };
  const deleteAcct = (name) => { if (st.holdings.some((h) => h.acct === name)) return alert("이 계좌에 항목이 남아 있습니다. 항목을 먼저 삭제하세요"); if (ACCTS.length <= 1) return alert("계좌는 최소 1개 필요합니다"); if (!confirm(`계좌 "${name}"을(를) 삭제할까요?`)) return; save({ ...st, accts: ACCTS.filter((a) => a !== name) }); };
  const exportJson = () => { const blob = new Blob([JSON.stringify(st, null, 2)], { type: "application/json" }); const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = `ledger-${today()}.json`; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 1000); };
  const usdToMan = (q) => { const f0 = +fx || fxAuto || 0; return f0 ? Math.round(q * f0) / 10000 : 0; };
  const importJson = (file) => { const r = new FileReader(); r.onload = () => { try { const L = JSON.parse(r.result); if (!L || !Array.isArray(L.holdings)) throw new Error("holdings 배열이 없습니다"); if (!confirm(`원장을 가져올까요? (항목 ${L.holdings.length}개 · 거래 ${(L.trades || []).length}건) 현재 원장은 덮어써집니다.`)) return; const hs = L.holdings.filter((h) => h && typeof h.acct === "string" && typeof h.name === "string").map((h) => ({ ...h, acct: h.acct.trim() || "기타", name: h.name.trim(), qty: Number.isFinite(+h.qty) ? +h.qty : 1, val: Number.isFinite(+h.val) ? +h.val : 0, type: TYPE_COLOR[h.type] ? h.type : "현금", sym: typeof h.sym === "string" ? h.sym : "" })); save({ ...st, ...L, holdings: hs, accts: Array.isArray(L.accts) && L.accts.length ? L.accts : [...new Set(hs.map((h) => h.acct))], living: (L.living && typeof L.living === "object" && !Array.isArray(L.living)) ? L.living : {}, trades: Array.isArray(L.trades) ? L.trades : [], lastSettled: L.lastSettled || "", baseDate: L.baseDate || today(), _sample: false }); } catch (e) { alert("가져오기 실패: " + e.message); } }; r.readAsText(file); };
"""
rep('  const editVal = (ix, n) =>', ACTIONS + '  const editVal = (ix, n) =>', label="onboarding actions")

rep('>●</span> {h.name}', '>●</span> {h.name}<span className="rowtools"><a href="#" title="이름 바꾸기" onClick={(e) => { e.preventDefault(); renameHolding(h.ix); }}>✎</a><a href="#" title="항목 삭제" onClick={(e) => { e.preventDefault(); deleteHolding(h.ix); }}>✕</a></span>', label="row tools")
rep('        @media(max-width:600px){', '        .rowtools a{color:#4F5E75;font-size:11px;margin-left:5px;text-decoration:none}.rowtools a:hover{color:#F2B84B}\n        .onb-step{display:flex;gap:10px;align-items:flex-start;margin:12px 0}.onb-num{flex:none;width:22px;height:22px;border-radius:11px;background:#2B3A52;color:#F2B84B;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:1px}\n        @media(max-width:600px){', label="onboarding css")

# 빈 원장(총액 0·생활비 0) 가드
rep('(h.val / total) * 100', '(total ? (h.val / total) * 100 : 0)', label="row pct guard")
rep('(sub / total) * 100', '(total ? (sub / total) * 100 : 0)', label="subtotal pct guard")
rep('(v / total) * 100', '(total ? (v / total) * 100 : 0)', count=2, label="legend pct guard")
rep('{Math.floor(cashOnly / livingTotal)}개월 버팀', '{livingTotal ? Math.floor(cashOnly / livingTotal) : "∞"}개월 버팀', label="living guard")
_n = s.count('((cashOnly / liquid) * 100).toFixed(0)'); s = s.replace('((cashOnly / liquid) * 100).toFixed(0)', '((liquid ? (cashOnly / liquid) * 100 : 0).toFixed(0))'); print(f"liquid guard: {_n} site(s)")
_n = s.count('달러 자산 시세 로딩 중…'); s = s.replace('달러 자산 시세 로딩 중…', '달러 자산 없음 · 또는 시세 로딩 중…'); print(f"usd card empty text: {_n} site(s)")

ONBOARD = """// ───────── 공개 템플릿 온보딩: 샘플 비우기 · 계좌 관리 · 항목 추가 · 백업 ─────────
function PubOnboard({ st, ACCTS, act }) {
  const [ov, setOv] = useState(LS.getItem("onboardOpen"));
  const open = ov == null ? true : ov === "1"; // 사용자가 "접기/완료"를 누르기 전까지는 항상 열림 (샘플 비우기 직후 닫히지 않도록)
  const setOpen = (v) => { setOv(v ? "1" : "0"); LS.setItem("onboardOpen", v ? "1" : "0"); };
  const [acctNew, setAcctNew] = useState(""); const [ren, setRen] = useState({});
  const [f, setF] = useState({ acct: ACCTS[0] || "", name: "", type: "현금", sym: "", qty: "", won: "", avg: "", usd: false });
  useEffect(() => { if (!ACCTS.includes(f.acct)) setF((x) => ({ ...x, acct: ACCTS[0] || "" })); }, [ACCTS.join("|")]);
  const fileRef = React.useRef();
  const submit = () => {
    const name = f.name.trim(); if (!name) return alert("항목 이름을 입력하세요");
    if (st.holdings.some((h) => h.acct === f.acct && h.name === name)) return alert("같은 계좌에 같은 이름의 항목이 이미 있습니다");
    const won = parseInt(String(f.won).replace(/[^0-9]/g, ""), 10) || 0; const qty = parseFloat(String(f.qty).replace(/[^0-9.]/g, ""));
    let sym = f.usd ? "" : f.sym.trim(); if (/^[0-9]{6}$/.test(sym)) sym = "KRX:" + sym; else if (/^(btc|eth)$/i.test(sym)) sym = "CURRENCY:" + sym.toUpperCase() + "USD"; else if (sym && !sym.includes(":")) sym = sym.toUpperCase();
    if (sym && !qty) return alert("시세 심볼을 넣었으면 수량도 입력하세요 (평가금 = 수량 × 현재가로 자동 계산)");
    const h = { acct: f.acct, name, sym, qty: f.usd ? (qty || 0) : (qty || 1), val: f.usd ? act.usdToMan(qty || 0) : won / 10000, type: f.usd ? "현금" : f.type };
    if (f.usd) { if (!h.qty) return alert("달러 잔액($)을 입력하세요"); h.usdCash = true; }
    else if (!won && !h.sym) return alert("평가금액(원)을 입력하세요 (시세 심볼이 있으면 비워도 자동 계산됩니다)");
    if (!f.usd && f.avg.trim()) { h.avg = f.avg.trim(); if (h.avg.startsWith("$")) h.usdAvg = h.avg; }
    act.addHolding(h); setF({ ...f, name: "", sym: "", qty: "", won: "", avg: "", usd: false });
  };
  return (<div className="card" style={{ borderColor: "#3E7B4F" }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
      <div className="eyebrow">시작하기 · 내 자산 입력 {st._sample ? <span style={{ color: "#F2B84B" }}>(지금은 샘플 데이터)</span> : <span style={{ color: "#7ED491" }}>(내 데이터)</span>}</div>
      <a href="#" style={{ color: "#F2B84B", fontSize: 13 }} onClick={(e) => { e.preventDefault(); setOpen(!open); }}>{open ? "접기 ▲" : "열기 ▼"}</a>
    </div>
    {open && <>
      <div className="onb-step"><div className="onb-num">1</div><div style={{ flex: 1 }}>
        <b>샘플 지우기</b> <span className="muted">— 빈 원장에서 시작합니다. 샘플 숫자를 고쳐 쓰고 싶으면 건너뛰고 아래 표에서 숫자만 바꾸세요.</span>
        <div style={{ marginTop: 6, display: "flex", gap: 6, flexWrap: "wrap" }}><button className="btn sec" onClick={act.clearSample}>샘플 데이터 비우기</button><button className="btn sec" onClick={act.restoreSample}>샘플로 되돌리기</button></div>
      </div></div>
      <div className="onb-step"><div className="onb-num">2</div><div style={{ flex: 1 }}>
        <b>계좌 이름 정하기</b> <span className="muted">— 증권사·은행·거래소 이름으로 바꾸거나 추가. 항목이 남아 있는 계좌는 삭제되지 않습니다.</span>
        <div style={{ marginTop: 6, display: "flex", flexDirection: "column", gap: 4, maxWidth: 560 }}>
          {ACCTS.map((a) => <div key={a} style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <input className="in" style={{ flex: 1 }} value={ren[a] ?? a} onChange={(e) => setRen({ ...ren, [a]: e.target.value })} onKeyDown={(e) => { if (e.key === "Enter") { act.renameAcct(a, ren[a] ?? a); setRen({ ...ren, [a]: undefined }); } }} />
            <button className="btn sec" onClick={() => { act.renameAcct(a, ren[a] ?? a); setRen({ ...ren, [a]: undefined }); }}>이름 적용</button>
            <button className="btn sec" style={{ color: "#E5484D" }} title="계좌 삭제" onClick={() => act.deleteAcct(a)}>✕</button>
          </div>)}
          <div style={{ display: "flex", gap: 6 }}><input className="in" style={{ flex: 1 }} placeholder="새 계좌 이름 (예: ○○증권 ISA, 업비트, 카카오뱅크)" value={acctNew} onChange={(e) => setAcctNew(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") { act.addAcct(acctNew); setAcctNew(""); } }} /><button className="btn" onClick={() => { act.addAcct(acctNew); setAcctNew(""); }}>계좌 추가</button></div>
        </div>
      </div></div>
      <div className="onb-step"><div className="onb-num">3</div><div style={{ flex: 1 }}>
        <b>항목 추가</b> <span className="muted">— 예수금·입출금·적금은 유형 "현금"/"묶임"으로 금액만 넣으면 됩니다. 주식·ETF·코인은 시세 심볼을 넣으면 평가금이 자동 계산됩니다 (국장 KRX:005930 또는 6자리 코드 · 미장 AMZN · 코인 BTC). 이름에 "예수금"이 들어간 현금 항목은 배분센터 "실탄"으로 집계되고, 은행 통장은 이름을 "입출금"으로 두면 월 정산 카드가 그 항목을 씁니다.</span>
        <div className="form" style={{ marginTop: 6 }}>
          <select className="in" value={f.acct} onChange={(e) => setF({ ...f, acct: e.target.value })}>{ACCTS.map((a) => <option key={a}>{a}</option>)}</select>
          <input className="in" placeholder="항목 이름 (예: 예수금, TIGER 미국S&P500)" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />
          <select className="in" value={f.usd ? "달러예수금" : f.type} onChange={(e) => e.target.value === "달러예수금" ? setF({ ...f, usd: true, type: "현금" }) : setF({ ...f, usd: false, type: e.target.value })}>{["현금", "주식", "대체", "코인", "묶임", "달러예수금"].map((t) => <option key={t}>{t}</option>)}</select>
          <input className="in" placeholder={f.usd ? "달러 잔액 ($)" : "수량 (현금은 비워도 됨)"} value={f.qty} onChange={(e) => setF({ ...f, qty: e.target.value })} />
          {!f.usd && <input className="in" placeholder="시세 심볼 (선택)" value={f.sym} onChange={(e) => setF({ ...f, sym: e.target.value })} />}
          {!f.usd && <input className="in" inputMode="numeric" placeholder="평가금액 (원) 예: 1,234,567" value={f.won} onChange={(e) => { const d = e.target.value.replace(/[^0-9]/g, ""); setF({ ...f, won: d ? (+d).toLocaleString("ko-KR") : "" }); }} />}
          {!f.usd && <input className="in" placeholder="평단 (선택) 예: ₩26,000 / $220.00" value={f.avg} onChange={(e) => setF({ ...f, avg: e.target.value })} />}
          <button className="btn" onClick={submit}>항목 추가</button>
        </div>
        <p className="muted" style={{ marginTop: 6 }}>이미 있는 항목은 표에서 숫자를 클릭해 수정, ✎로 이름 변경, ✕로 삭제. 매수·매도 체결은 매매 탭에서.</p>
      </div></div>
      <div className="onb-step"><div className="onb-num">4</div><div style={{ flex: 1 }}>
        <b>백업 · 기기 이동</b> <span className="muted">— 데이터는 이 브라우저에만 있습니다. 파일로 내보내 두면 다른 기기나 브라우저에서 가져올 수 있어요.</span>
        <div style={{ marginTop: 6, display: "flex", gap: 6, flexWrap: "wrap" }}>
          <button className="btn sec" onClick={act.exportJson}>JSON 내보내기</button>
          <button className="btn sec" onClick={() => fileRef.current && fileRef.current.click()}>JSON 가져오기</button>
          <input ref={fileRef} type="file" accept="application/json,.json" style={{ display: "none" }} onChange={(e) => { const file = e.target.files && e.target.files[0]; if (file) act.importJson(file); e.target.value = ""; }} />
          <button className="btn" onClick={() => setOpen(false)}>완료 · 접기</button>
        </div>
      </div></div>
    </>}
  </div>);
}

"""
rep('function App() {', ONBOARD + 'function App() {', label="PubOnboard component")
rep('      {tab === "원장" && (<>\n', '      {tab === "원장" && (<>\n        <PubOnboard st={st} ACCTS={ACCTS} act={{ clearSample, restoreSample, addHolding, renameAcct, addAcct, deleteAcct, exportJson, importJson, usdToMan }} />\n', label="PubOnboard mount")



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
