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
- 조성: 마감까지 화학식 문자열만. constituent 행 = 플랫폼 템플릿 v0.6 설계 → prefill 흡수 WP(마감 뒤).
- prefill 기록(10-14): `docs/review/mpsp-upstream-feedback.md` 6절(SDL-MPSP 고려 · cb5c821) · 7절(prefill 요청 — 조성 행 흡수·건수 규칙 · PVK 분리 연결 행 · PSC 추가후보 · 파라미터 RepeatNo · f5044e8).
- **검토 대기(PSC 회신 10-15 때)**: `mapping/psc_additions.csv` — 특히 몰농도 `precursorMolarity`(M) · 첨가제 `additiveMolarRatio`(mol%) 를 PSC registry 에(이름·단위·MPSP 경로·J1).
- **변환기 3건 반영(10-14 밤, 사용자 승인)** — dev 빌드 `library/dev-20261014b` = 170세트 · 조성 170 · 공정 16,588(manual 7,188) · 분석 11,640 · 오류 0 ·
  미입력 1,344 · 확인 660(`reports/indicator-dev-20261014b.md`). ① PVK 산출 = 적층체 + `페로브스카이트` 재료 개체(화학식 · Note 로 적층체 이름 —
  PartOf 행은 엔진 미지원, prefill 7-2. 재료 이름은 PSC 회신 따라 바꿀 수 있음) ② JV = (방향, 면적)별 스텝(+8) — 면적 = 곡선 값(Isc/면적 = Jsc 확인).
  **이전 dev 빌드는 10세트(03731~03740, 곡선 172개)에서 activeArea 를 소자 블록 0.045216 으로 잘못 적었음 — 실제 측정 면적 0.0908**. 소자 블록 값은 완성소자 Note.
  ③ 곡선 파일 OriginalFileName = ChemDX 원본 파일명(확장자 .csv). 소실 검사: cell_dimension 전부 남음 · 곡선 key = 방향_원본명(2328/2328) → 소실 없음.
- **보류(사용자 10-14 밤)**: 소자 블록 condition 둘 스텝 · 실험실 온습도 넣을 스텝 · MACl 농도 칸 의미(랩) · T3.5 xlsx 작성 시각 — 사용자가 다시 꺼낼 때까지 묻지 않음.
- **데이터 건수 셈법(10-15 재논의)** = `docs/intent/data-count-methods.md` "재논의" 절 · 설득 문서 `docs/data-count-methods-brief.md`
  (+ 페이지 https://claude.ai/artifact/F2E9csXYfGCHKbVDRtHHwo, 비공개 — 공유는 사용자가). A 트리플 · B 묶음 1 + 설계인자 각 1 + 응답(시편마다 1, 같은 시편 반복 2) ·
  C 조건 1 + 측정 항목. ChemDX 2026: A 340,431 · **B 6,695(39.4)** · C 1,850(10.9 ≈ 계획 11.0)(`scripts/count_methods.py`). 보고 수치는 1차 실데이터 수집 뒤.
  기본값 확인 중(n≥2 · 묶음 → 공정 칸 · C 의 1 = 전체) · 픽셀 = 시편 원칙은 전 실험실 실데이터 확인 뒤.
  **사용자 편집본 `docs/data-count-methods-brief 복사본.hwpx`(미커밋 — 사용자 파일) → docfac 보고자료 `docs/261015_보고자료_데이터건수정의.hwpx`(+ md 원고, 예시 파란 글자)** · 처음 한글 문서 `docs/data-count-methods-brief.hwpx` · 그래프 `docs/fig/`(태양전지 실데이터 ·
  석유화학촉매 registry 추산 PCC A 911 · B 8~15 · C 8 vs 목표 19.4) = `scripts/plot_count_methods.py` · `lab_estimate.py` 는 10-15 정의(+ A 트리플).
- 범주당 설계인자 1건(B = 1 + 0~3 + 응답) 합의·미적용 — 태양전지 B 39.4 → 23.5 · 보고용 셈식에만 · 판정 동결. 적용은 사용자 말 기다림.
- 열린 결정 = `docs/PLAN.md` 끝 표(D1·D4~D7).
