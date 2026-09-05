# ledger — 개인 자산 대시보드

- 개인 자산 대시보드. 배포 주소: https://bld-s.github.io/ledger/asset-dashboard.html
- 파일명은 `asset-dashboard.html`로 고정. 버전 파일(`asset-dashboard_1.html` 등) 생성 금지.
- INIT는 초기값일 뿐. 데이터 정본은 구글 시트 + localStorage — INIT 자산 숫자를 임의로 수정하지 말 것.
- 배분 분류 수정은 `ALLOC_EXACT` / `ALLOC_INCL`에서만 할 것.
- 모든 수정은 커밋 → push → curl 배포 검증(`curl -s https://bld-s.github.io/ledger/asset-dashboard.html`로 변경 반영 확인)까지가 한 세트.
- 국장 종목 검색 목록(KRX_ALL)은 `python3 krx-update.py`로 갱신 (KIND + 네이버 ETF). 트레이딩뷰 무료 위젯은 국장 심볼 미지원 → 국장은 네이버 차트 이미지 사용
- 공포지수 탭: CNN Fear&Greed API(브라우저 CORS 허용) + 그 안의 VIX 시계열 사용. VKOSPI는 무료 API 없음 → 수동 입력
- ⚠️ 다른 세션·다른 기기에서 작업할 때는 반드시 `git pull origin main`으로 최신본을 받은 뒤 수정할 것. 오래된 로컬 복사본(다운로드 폴더 등)으로 커밋하면 기능이 통째로 사라진다 (2026-09-04 "환전 1차" 커밋이 56KB 구버전으로 덮어쓴 사고 있었음 → 09-05 복구)
