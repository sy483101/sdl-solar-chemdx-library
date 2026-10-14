# worklog (append-only)

- **착수 준비(2026-10-14, sdl-prefill 세션)** — interview-me 로 범위 합의(`docs/intent/project-scope.md`): ChemDX 태양전지 → KRICT 필터 → 2026/그외 →
  PSC registry 용어로 매핑 → sdl-prefill 엔진으로 세트별 폴더(라이브러리층까지). sdl-prefill 안이 아니라 별도 레포로(외부 DB 전용 · 서비스 배포물과 분리 ·
  커밋 게이트 분리). 만든 것: CLAUDE.md(데이터·의존 규칙 · 함정 — `sdl_platform` 패키지 이름 셋 · registry 경로 고정 · 장부는 서버) · docs/PLAN.md(WS0~4 · 열린 결정 D1~D7) ·
  HANDOFF.md · .gitignore · .env.example. 기준 sdl-prefill `a2bc356`. 다음 = T1.1 ChemDX API 조사(문서·계정은 사용자).
- **세션 준비 — 원본층 두 단(2026-10-14)** — 사용자 결정: 1차 `raw/1_full/`(API 응답 전체, 타기관 포함) · 2차 `raw/2_krict/`(KRICT 만 복사).
  "타기관 레코드 디스크에 안 씀" 규칙을 바꿈 → CLAUDE.md 데이터 규칙 · PLAN 데이터 배치·T1.2 · project-scope "변경" 절 갱신.
  `SOLAR_DATA_DIR=~/Research/sdl-solar-chemdx-data`(`.env`, gitignore) · 두 폴더 생성 확인. 다음 = T1.1(API 문서·계정 · D6 마감일).
- **1차 구조 조사 · 2차 원본(KRICT·연도별)(2026-10-14)** — 사용자가 받은 1차(run-20261014T054004Z): records.json · N.zip · N/N/<ID>.json 세 벌이 같은 13,271건
  (폴더↔zip 바이트 동일, 폴더↔records.json 내용 동일 13,271/13,271). 그룹↔ID 접두어 1:1, 수집 로그로 이름 대조 → KRICT = 그룹 2(3,333) · `SC-` = UNIST.
  결정(interview-me): D3 = 그룹 2 · D2 = `created_at` 연도 · 2차 = `2_krict/<스냅샷>/<연도>/<ID>.json`(바이트 그대로) + manifest.
  `scripts/filter_krict.py` — 검증: 2.zip 과 3,333/3,333 바이트 동일 · 타기관 0 · 두 번 실행 manifest 동일 · 기존 스냅샷 덮어쓰기 거부. 구조 문서 `docs/chemdx-api.md`.
  다음 = D6 · 2026년분(170건, 07-24 이후 없음) 재수집 여부 · 첨부 바이트 필요 여부 → T2.1.
- **T2.1 필드 전수(2026-10-14)** — 결정: D6 = 마감 10-26 · 2026년분 ≈170건 확인(재수집 안 함) · 측정 곡선은 JSON 배열 → DataArtifact txt/csv(배열 지양) ·
  변환 데이터도 `SOLAR_DATA_DIR`(git 밖) · D7 잠정 레코드 = 세트 · D1 = KRICT-PSC 체계. `scripts/field_inventory.py` → `mapping/fields.csv`
  (경로 242 · 2026 채워진 119 · 미사용 25 · 자체 검사 `_selftest`). 관찰(중복 위치 · numstr · 단위 변형 · 깨진 note)은 `docs/chemdx-api.md`. 다음 = D1 세부 → T2.2.
