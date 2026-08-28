# ledger — 개인 자산 대시보드

- 개인 자산 대시보드. 배포 주소: https://bld-s.github.io/ledger/asset-dashboard.html
- 파일명은 `asset-dashboard.html`로 고정. 버전 파일(`asset-dashboard_1.html` 등) 생성 금지.
- INIT는 초기값일 뿐. 데이터 정본은 구글 시트 + localStorage — INIT 자산 숫자를 임의로 수정하지 말 것.
- 배분 분류 수정은 `ALLOC_EXACT` / `ALLOC_INCL`에서만 할 것.
- 모든 수정은 커밋 → push → curl 배포 검증(`curl -s https://bld-s.github.io/ledger/asset-dashboard.html`로 변경 반영 확인)까지가 한 세트.
