# HANDOFF

> 이 파일 = "지금"의 스냅샷만. 규칙·함정 = `CLAUDE.md` · 계획 = `docs/PLAN.md` · 이력 = `docs/archive/worklog.md` · 합의 = `docs/intent/`.

## 지금 — 2026-10-14 2차 원본(KRICT·연도별) 완료

- 1차 원본 = 사용자가 받은 `raw/1_full/downloads/run-20261014T054004Z-rx23_glu`(13,271건 · 16그룹). 구조·필드 = `docs/chemdx-api.md`.
- 2차 원본 = `raw/2_krict/20261014/<등록연도>/<ID>.json` + `manifest.json` — `scripts/filter_krict.py`(그룹 2 · `created_at` 연도 · 바이트 그대로).
  KRICT 3,333 = 2021 103 · 2022 578 · 2023 674 · 2024 407 · 2025 1,401 · **2026 170**(작성자 2명 · 마지막 등록 07-24). D2·D3 결정.
- 첨부 파일 바이트(SEM 이미지·원본 측정 txt)는 받지 않았다 — 레코드에는 목록(`fileinfo`)만. 곡선(JV·PL·XRD·UV-Vis)은 레코드 안 숫자 배열.
- 기준: sdl-prefill `a2bc356`(registry v0.5.3 · template `5sheet-1.1`). PSC registry 회신 대기 중.
- 확인(10-14): 2026년분 ≈170건 맞음(재수집 불필요) · **마감 10-26**(D6) · 측정 곡선은 JSON 배열 → DataArtifact 용 txt/csv 로 뽑는다(배열 지양).
- T2.1 완료: `mapping/fields.csv`(경로 242, 2026 에서 채워진 것 119) — 관찰은 `docs/chemdx-api.md` 끝. D7 잠정(레코드 = 세트) · D1 = KRICT-PSC 체계(`PSC-EXP-…`).
- D1 결정: `PSC-EXP-{created_at 날짜}-{NNN}`(같은 날 ChemDX ID 순).
- T2.2 초안 `mapping/chemdx_to_psc.csv` — 2026 데이터 = PSC-RCP-03(n-i-p) 골격. 이름은 v0.5.3 '→' 정리 후(BOTEL·ETLCD·ETLCT·PVK…).
- **파이프라인 완성(dev)**: `scripts/convert.py`(레코드 → draft) · `scripts/build_library.py`(→ 엔진 zip → `library/<빌드>/2026/<실험ID>/` + manifest + 집계).
  dev 빌드 `library/dev-20261014` = 170세트 · 조성 170 · 공정 16,540(manual 7,156) · 분석 11,640(곡선 2,328 × 값4+파일1) · 오류 0 ·
  미입력 1,312(JV 결과 Kind — PSC Composite 보류) · 확인 660(registry 에 없는 값 → Process Note). 숫자 = `reports/indicator-dev-20261014.md`.
- **PSC registry 정리 = 보류(사용자 10-14)** — 내일(10-15) PSC 회신 받으면 sdl-prefill 받기 절차 → 판 올림 → 이 레포는 다시 빌드만
  (convert.py 가 '→' 메모·새 이름 모두 읽음 — ASOL 합침되면 반용매·열처리가 PVK 파라미터로 들어간다).
- 결정(10-14): 지표 건수에 registry 기본값 포함(웹과 같은 셈). 스캔 방향 = 곡선마다 확실(3곳 일치) → JV 방향별 스텝 유지.
- **소실 검사(10-14)** — 라이브러리층에 제자리가 없는 값 22건 = `mapping/psc_additions.csv`(원본층엔 다 있음). 대부분 registry 이름만 없음(MPSP 노드 있음) →
  **PSC 회신(10-15) 받기 절차 때 sdl-prefill 에서 함께 넣기**. MPSP 갈래도 없는 것 3건 = sdl-prefill `docs/review/mpsp-upstream-feedback.md` 6절(cb5c821).
- 조성: 마감까지 화학식 문자열만. constituent 행 = 플랫폼 템플릿 v0.6 설계 → prefill 흡수 WP(마감 뒤). **PVK 산출을 적층체 + 페로브스카이트 재료로 나누는 안**(사용자 기울어짐) — 확정 대기.
- **사용자에게 물을 것**: PVK 산출 분리 확정 · 소자 블록 condition 둘 스텝 · 실험실 온습도 넣을 스텝 · MACl 농도 칸 의미(랩) · T3.5 xlsx 작성 시각.
- 열린 결정 = `docs/PLAN.md` 끝 표(D1·D4~D7).
