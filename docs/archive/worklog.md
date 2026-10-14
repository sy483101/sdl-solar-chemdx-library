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
- **T2.2 매핑표 초안(2026-10-14)** — D1 결정(created_at 날짜 + 같은 날 ChemDX ID 순). PSC registry v0.5.3 조사: 2026 ChemDX = PSC-RCP-03 과 같은 n-i-p 공정.
  `mapping/chemdx_to_psc.csv` 85행(2026 채워진 경로 119 전부 포함 확인) — layer(input 블록) × 경로 → meta·step·param·result·file·drop, '→' 정리 후 이름.
  주요 제안: 조성(a/b/x_site 비율)은 PVK 산출 개체 formula · JV 는 scanDirection 별 스텝 2개(반복 = 셀) · 곡선 = resultFile csv.
  막힌 곳: 정리된 PSC registry 판 없이는 엔진이 ETLCD 등을 모른다 → D5(PSC 회신 대기 vs 데이터팀 정리) 사용자 결정 필요.
- **T3 변환기·빌드 파이프라인(2026-10-14)** — PSC registry 정리는 보류(PSC 회신 10-15 예정, 사용자) · 그동안 파이프라인 진행.
  `scripts/convert.py`: from_recipe(PSC-RCP-03) 골격 → EQE·IMAGE·THICK·(CBD/NP 중 안 쓴 쪽)·(없으면 ETLSF) 빼고 개체 다시 잇기 → 레시피 표준값 지움 →
  ChemDX 값 manual(단위 환산 ml→µL·m→min 등, 못 하면 orphan) · JV 스캔 방향별 스텝(반복 = 곡선) · 곡선 csv · 조성식. 자체 검사 `_selftest`.
  `scripts/build_library.py`: 실험 ID · validate · to_zip 풀기 · manifest(원본 sha · 코드·prefill 커밋 · registry·template 판) · 집계.
  검증: 세트 1개 template.xlsx 를 원본과 대조(값·곡선 파일명 일치) · 두 번 빌드 = xlsx 셀 내용·나머지 파일 동일(xlsx 바이트만 다름) ·
  dirty 판정에 untracked 포함(filter_krict 도). dev 빌드 `library/dev-20261014`(코드 0a60847) 170세트 · 오류 0.
  다음 = PSC 회신 → registry 판 → 재빌드 · 사용자 결정(확인 4건 · 기본값 셈 · xlsx 시각).
- **매핑 검토 2차(2026-10-14)** — 결정: 지표 건수에 registry 기본값 포함. 조성 = SDLEXO 로 다 표현(formula + 조성 노드 species·amount·role·원소, FA·MA 원소 사전 있음),
  MPSP 는 가능하나 사이트 비율의 basis 칸 없음 · 5시트 constituent 행은 sdl-prefill 엔진 미착수 · 적재기는 재료 개체에만. 스캔 방향 3곳 일치.
  condition = ChemDX 층별 칸(registry 아님). 농도·mol% = QUDT 단위 있음 · MPSP feedstock_n Concentration / additive_n Amount.
  소실 검사(scratch 스크립트, 원본 잎 값 ↔ 빌드 셀): JV 부가값·측정 조건·소자 condition·원본 파일명·note 속 MACl 이 라이브러리층에서 빠짐 → registry 추가후보로.
- **매핑 검토 3차(2026-10-14 밤)** — sdl-prefill `docs/review/mpsp-upstream-feedback.md` 6절에 SDL-MPSP 고려사항 기록(cb5c821, make test 116 passed):
  사이트 비율 basis 없음 · Role 예시에 사이트 없음(자유 문자열로 적기 — 사용자 결정) · CBD 분위기 없음. `mapping/psc_additions.csv` 22행(분류: registry·mpsp·converter·structure·data).
  확인: JV Rs·Rsh·Pmax·Vmpp·Jmpp·settling·분주 방식 = MPSP 노드 있음 → registry 이름 + J1 판정만. 적재기 MPSP 매핑 = 플랫폼 J1(랩·이름 기준) → 분위기 이름은 기법별로.
  constituent 행 = 플랫폼 템플릿 v0.6 설계, prefill 흡수 전. 정정: note 속 MACl 은 Metadata Note 에 남음(구조화 안 됨).
- **매핑 검토 4차(2026-10-14 밤)** — prefill 환류 7절(f5044e8, make test 116 passed). 확인: SDLEXO 는 MPSP 를 import(어휘 ⊇) — 빈 곳은 registry(랩 이름표).
  Environment ⊃ MeasurementCondition(측정 = acquisitionCondition), 공정 조건 = 스텝 ProcessParameter, 적재기는 MeasurementCondition 미구현(플랫폼).
  Parameter 행 RepeatNo 없음 → 셀 면적 섞인 JV 스텝 5/328 — 변환기에서 (방향, 면적)별 분리로 해소 가능. 변환기 할 일 3건 확정 대기.
- **변환기 3건(2026-10-14 밤)** — 사용자 승인("나눠줘"). `scripts/convert.py`: ① PVK 산출에 `페로브스카이트` 재료 개체 추가(화학식 이동, Note = 적층체 이름)
  ② JV 스텝 = (방향, 곡선 면적)별 · activeArea = 곡선 값 · 소자 블록 면적 = 완성소자 Note ③ resultFile 이름 = fileinfo original_name(key 로 짝, 확장자 .csv).
  발견: 소자 블록 cell_dimension(0.045216)과 곡선 값이 다른 10세트(곡선 0.0908, Isc/0.0908 = Jsc 확인) — 이전 빌드는 activeArea 를 설계값으로 적었음.
  검증: dev 빌드 `dev-20261014b` 오류 0 · 공정 +48 · manual +32 · 미입력 +32(JV 스텝 +8 × 결과 Kind 4) · 조성·분석 변화 없음 · 소실 검사 cell_dimension 전부 남음 ·
  곡선 key 2328/2328 = 방향_원본명(시각 뺌). prefill 은 다른 세션의 HANDOFF 미커밋 수정으로 manifest 에 -dirty(엔진 무관).
  다음 = PSC 회신(10-15) → registry 판 → 재빌드 · 남은 질문(소자 condition · 온습도 스텝 · MACl 농도 · xlsx 시각).
- **보류(2026-10-14 밤)** — 사용자: 남은 질문 4건(소자 condition · 온습도 스텝 · MACl 농도 · xlsx 시각) 일단 보류. 다음 = PSC 회신(10-15) → registry 판 → 재빌드.
- **데이터 건수 셈법 비교(2026-10-14 밤)** — 사용자: 동료 토의(칸마다 1건 vs 타겟 Y 만 따로 · X 묶음) → 둘 다 추산해 두고 보고 때 고름 · 기록은 이 레포.
  `docs/intent/data-count-methods.md`(셈법 A·A′·B·C · X/Y 규칙 = Value 측정값이 Y · 애매한 것 · 태양전지 적용) ·
  `scripts/count_methods.py`(플랫폼 적재기 v05.load 로 실제 그래프 — 별도 프로세스, 시트 이름 v0.6 로 바꿔 넣고 Entity Type 잠정) →
  `reports/count-methods-dev-20261014b.md`: A 28,398 · A′ 18,998 · B 9,652 · C 9,482 · ML 표본 행 2,328 · 트리플 339,921(미표현 0, Y 값당 15).
  공정 칸 중 기본값 9,400(57%) · 값이 달라지는 공정 자리 22/128. `.env.example` 에 SDL_PLATFORM_DIR.
