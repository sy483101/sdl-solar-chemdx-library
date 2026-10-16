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
- **셈법 정의 확정 · 랩별 추산(2026-10-14 밤)** — interview 로 확정: Y = Value 측정 결과 행 1건(파일 1 = Y 1, 파일 + 파생 숫자 둘 다,
  물성 = 성능, 랩 Kind '공정'만 X) · B = 조성·구조·공정 각 1 + Y 반복마다 · C = X 1 + Y 측정 항목마다 · 구조(X) = 구성(산출물 J2 component·device).
  `count_methods.py` 갱신(Entity Type = 플랫폼 J2) → ChemDX 2026 A 28,398 · B 12,150 · C 1,850(세트당 10.9 ≈ 계획 11.0) · 트리플 340,431.
  `lab_estimate.py` 신규(엔진으로 레시피 1세트 · 목표 = 연차보고서 배포본 2026 표): A 는 계획의 7~11배, B(1회)·C 는 계획 규모 · OPD 추산 불가.
  랩 확인 목록 = 반복 수 · PCC 칭량 질량 Kind · BAS J2 · OPD 결과 정의.
- **셈법 재논의(2026-10-15)** — interview: 목적 = 1차 실데이터 전에 셈법 셋(A·B·C)을 산식·조건·근거와 함께 짧은 문서로 → 연구책임자·참여연구원 설득(보고 수치는 수집 뒤).
  합의: 세트 = 실험 ID(합성·측정 분리면 별도 세트, 시료로 연결) · X·Y = 역할(정방향↔역설계 치환, 공정 실측값도 SDL 보정 타겟이면 Y) ·
  설계인자(DoE design factor) 각 1 · 고정·변동 인자 묶어 1(판정 = 랩 선언 ∪ 관측 변동, 환경·운용값·측정 설정은 묶음, 규모 = 설계인자, 데이터팀 1차 → 랩 확인) ·
  응답 각 1 · 시편(측정 대상 개체)마다 1 · 같은 시편 반복 = 2(값 + 불확도) · 픽셀(소자 개체 하나의 반복) 문제는 전 실험실 실데이터 확인 뒤 — 지금은 개체 기준.
  새 A = 트리플 · B = 1 + Σ설계인자 + Σ시편Σ항목 min(n,2) · C = 1 + 측정 항목. `count_methods.py` 갱신 → ChemDX 2026 A 340,431 · **B 6,695(39.4)** · C 1,850(10.9).
  발견: registry Variable 표시 랩마다 뜻이 다름(PCC·PSC 0 · ELF 43/48 · CAM 45/48) · ChemDX 10세트(03572~03586) 파일명에 숙성 일수·조건 섞임.
  설득 문서 `docs/data-count-methods-brief.md`(안건마다 태양전지 예시) + 페이지 https://claude.ai/artifact/F2E9csXYfGCHKbVDRtHHwo(비공개).
  기본값(확인 중): 2건 문턱 n≥2 · 묶음 → 공정 칸 · C 의 1 = 조성·구조·공정. `lab_estimate.py` 는 10-14 정의 그대로(새 B 는 랩 설계인자 확인 뒤).
- **설득 문서 그래프·한글 문서(2026-10-15)** — 사용자: 촉매·태양전지 세트당 A·B·C 막대 + 2026 목표 점선, 분야마다 한 장 · 한글 문서로(문구는 사용자가 수정).
  `lab_estimate.py` 를 10-15 정의로(A = 레시피 1세트 트리플 — `count_methods.py --triples` 다른 프로세스 · B 1회~반복 · C) + JSON ·
  `count_methods.py` 세트당 JSON · `plot_count_methods.py` 신규 → `docs/fig/count-methods-{solar,catalyst}.png`(로그 눈금).
  태양전지(실데이터) A 2,003 · B 39.4 · C 10.9 vs 목표 11.0 · 석유화학촉매(registry 추산) A 911 · B 8~15 · C 8 vs 19.4(설계인자 0 가정, 응답 7 중 5 = 칭량 질량).
  `docs/data-count-methods-brief.hwpx`(kordoc 생성, 그래프 2장 포함 — 사용자 편집본) · md·페이지에도 그래프 추가.
- **범주당 설계인자 · docfac 보고자료(2026-10-15 오후)** — 논의: 설계인자를 MPSP 범주(조성·구조·공정)마다 1건 → ChemDX B 39.4 → 23.5(설계인자 18.9 → 3),
  보고용 셈식에만(변환기·registry·MPSP 그대로) · 판정은 보고 시점 데이터로 동결 — 합의, 적용은 아직. MPSP 범주 커버리지: 매핑 없는 파라미터 랩마다 5~63%,
  PVK solvent1/solvent2 매핑 불일치 → 나중에 조율. 사용자 편집본(`docs/data-count-methods-brief 복사본.hwpx`)을 docfac 보고자료로:
  `docs/261015_보고자료_데이터건수정의.{md,hwpx}` — docfac-build(+ --image-dir, 그래프 60% 가운데, 예시 문단 #2B579A 글자색은 빌드 뒤 XML 손질), 3쪽.
- **C 재정의(2026-10-15 저녁)** — 사용자가 연구책임자와 논의해 결정: 레시피 정보 1건 + 측정·분석 정보 따로. interview 로 세부 확정 —
  측정·분석 = (대상, 공정 순서상 위치, 항목)마다 1 · 같은 측정 2회 이상 = 2 · 에이징 등 다른 맥락 = 그 단계 뒤 측정이라 따로 · 공정 기록(칭량·로그·프로파일) = 레시피 1건.
  이것을 **C** 로(앞 C = 조건 1 + 측정 항목을 대신), B 는 그대로, 보고는 C·A 앞세우고 B 는 본문. 가름 = registry StepType `SDLEXO_Class` = MEASURE(칭량 WEI·WEIGH, 메모 remark 제외 —
  랩 Kind 표기는 랩마다 어긋나 안 씀) · 경계(공정 스텝의 분석) = CAM 펠릿 사진 · BAS-02 GPC·회수율 → 랩 확인. PSC registry 에 에이징 단계 없음(추가 후보).
  `count_methods.py`(C = 1 + B 응답) · `lab_estimate.py`(C 1회~반복 · 측정·분석 · 경계 열, lab_registry.lab_sheets 로 StepType 읽음) → ChemDX 2026 **C 3,490(20.5)** ·
  registry 추산 PCC 3~5 · PSC 5~19 · ECC 9~17 · ELF 9~17 · CAM 2~3 · BAS 4~13 · CHA 6~11. 손으로 센 값과 일치 확인.
  보고자료 hwpx 사용자 편집본 커밋(1152fda). 문서·그래프는 결정 전 그대로(새 C·A 중심 개정은 사용자 말 기다림). 다음: 랩 확인 · 레시피 1건의 계획서 칸.
- **셈법 이름 바꿈 · 보고자료 2판(2026-10-15 저녁)** — 사용자: C → A(가장 중요한 수치) · B 그대로 · A → C, A·B·C 기준으로 재구조화한 새 편집본.
  스크립트 셋 이름 바꿈(`count_methods.py` 칸 단위 키도 cells 로 · `lab_estimate.py` A 1회~반복 · `plot_count_methods.py` A·C 막대만, A 반복 빗금) → 집계·그래프 다시.
  `docs/261015_보고자료_데이터건수정의_2판.{md,hwpx}` — 1판(사용자 편집본, nbSpace 포함 전문 추출) 문구 바탕, 핵심요약(A·C 표) → 목표 비교(그래프 2 + 분야별 A 표) →
  공통 원칙(세트 · X·Y) → A(레시피 1건 · 측정·분석 각 1 · 시편·반복·맥락) → B(참고, 범주별 23.5 병기) → C(트리플). 렌더 5쪽 확인 · XML 정상 · 예시 8문단 파란 글자.
- **C 조건(2026-10-15 밤)** — 사용자가 VoID 자료를 붙여 C(트리플) 조건을 다듬자고 함(처음엔 A 로 물었다가 C 로 정정 — A 는 그대로).
  확인: 적재기 그래프는 추론 0 · TBox 0 · 값 노드(이름 없음) 57,894 · MPSP 연결 44,252 · 공유 참조 105. 조건 = VoID void:triples(명시적·ABox) · 빌드 그래프에서(Fuseki 아님) ·
  판 고정 · 공유 참조 1번 · 구성·클래스별 인스턴스 병기. `count_methods.py` 에 TBox 검사·겹치지 않는 구성·classPartition → 집계 갱신. 논의 기록 · 2판 C 절 · hwpx 다시 빌드(5쪽, 렌더 확인).
  (A 질문으로 오해해 답한 것: 그래프에서 측정 노드가 스텝과 안 이어져 A 를 그래프로 뽑으면 20.5 → 11.0 — 플랫폼 요청 후보로만 남김, 반영 안 함.)
- **HANDOFF 문구 정정(2026-10-15, sdl-prefill 세션)** — "웹과 같은 셈"(칸 단위) → 웹은 sdl-prefill `fd629ed` 부터 셈법 A(`sheets.set_count`) 표시.
  `sheets.data_counts`(칸 단위)는 sdl-prefill 에 그대로 남아 이 레포 `build_library.py`·`count_methods.py`·`lab_estimate.py` 의 참고 지표는 무변. 문서만.
- **세션 점검(2026-10-15 마감)** — sdl-prefill `fd629ed`(웹 건수 = 셈법 A `sheets.set_count`) 확인 후 대조: `dev-20261014b` 170세트 = 레시피 170 + 측정·분석 3,320 = 3,490 —
  `count_methods.py` A 와 일치(결과 11,640 전부 JV, step_role measure). 이 레포 A 는 스텝 역할로 거르지 않지만 ChemDX 는 결과가 JV 뿐이라 같음.
  PSC 회신 미도착(prefill inbox). 두 dev 빌드 차이 = 변환기 3건(0a60847 → 8a20b79 — PVK 재료 개체 · JV (방향, 면적)별 스텝 +8 · 곡선 원본 파일명) → 공정 +48 · 미입력 +32.
  b = 작업 기준, 정본 아님(PSC 정리·매핑표 검토 전, prefill dirty 빌드). 코드 변경 없음. 다음 = HANDOFF "다음 후보"(사용자 답 대기).
- **JSON-LD 정본 착수(2026-10-15 밤, interview-me)** — 사용자: 템플릿 빈틈 · JSON-LD 로 만들 수 있나 · 장점 살릴 길 → 인터뷰 8문항 →
  빌더(플랫폼)가 세트마다 `set.jsonld`(그래프 DB·RDB 정본, xlsx 참고) · 본거지 플랫폼 PRJ22 · 이 레포 빌드 폴더 = 플랫폼 라이브러리 규격 ·
  manifest 만 JSON-LD(세트 metadata.json 은 그대로 — 매핑 출처 하나). 합의 = `docs/intent/json-ld.md`(근거 표 · 플랫폼 요청 7 · prefill 요청 3).
  조사(플랫폼 9ead95b · prefill f43d853): 결과↔스텝 끊김은 registry 아닌 적재기·TBox · PartOf 열은 있으나 엔진이 안 씀 · RepeatNo 버림 · QuantityValue 빈 노드 ·
  적재기가 1b388fb 부터 라이브러리 폴더를 바로 읽고 5sheet-1.1 시트 이름 사용 → 옛 count_methods 의 이름 바꾸기가 C 를 조용히 줄일 상태였음.
  구현: `build_library.py`(`<랩>/<연도>/<ID>` · manifest `@context`·세트 `@id`·`path`) · `count_methods.py`(read_set — RENAME·J2·read() 삭제).
  검증: dev-20261015 = b 와 non-xlsx 파일 md5 같음 · xlsx 셀 내용 170/170 같음 · 적재기 library_sets 170 · check_set 소견 0 · manifest rdflib 파싱 2,401 트리플 ·
  hasPart 170 · 실험 IRI = ABox 노드 · `--triples` 경로 동작 · A 3,490 · B 6,695 · C 341,103(현 적재기 — 빈 Type = 재료로 +672). 보고 숫자는 b·옛 판 그대로.
- **사용자 파일 커밋(2026-10-15)** — `docs/data-count-methods-brief 복사본.hwpx`(사용자 편집본, 그동안 미커밋으로 둠) 사용자 요청으로 그대로 커밋.
- **② 그 외 연도 dev 빌드(2026-10-15 밤)** — 사용자 "1부터"(남은 일 중 2021~2025 빌드) → 조사: 3,163건 중 지금 변환기 통과 355. 소자 구조·실측 면적(단위셀 ≈0.09 · 모듈 24.5 cm²)으로
  나눔 → n-i-p 단위셀 SnO2 611 · p-i-n 1,703+10 · n-i-p 모듈 SnO2 251 · TiO2 572 · 기타. PSC registry 레시피 = RCP-01 p-i-n(`[신규]` ANN·BUFEV) · RCP-02 n-i-p 모듈(`[신규]` ANN) · RCP-03.
  사용자: 611 만 이번에, 나머지는 이유와 함께 목록. 변환기 손질(`convert.Skip` · 빈 블록 · 층 여럿 블록 · PVKSF 없음 · 숫자 칸 글자 → orphan · ar 글자 · ETL 농도·양 · CBD 욕조 ·
  module.* · vacuum_suction) · `build_library.py`(skipped → manifest·집계, 번호 비워 둠). `dev-20261015b` = 2026 170 + 542(골격 안 611 중 69 는 이중층·ALD·증착 등으로 건너뜀).
  검증: 2026 셀 170/170·파일 같음(dev-20261015) · 오류 0 · 적재기 712 소견 0·미표현 0 · 소실 검사 2026 대비 새 소실 = public·analysis_old(사본) · ar 매핑 확인(글자 "0" 버그 고침).
  매핑표 8행 · 추가후보 3행 추가. 다음: PSC 회신 때 건너뛴 묶음 질문(HANDOFF) · ② 의 A·C 집계는 아직(count_methods 는 2026 만).
- **미등록 골격 결정(2026-10-15 밤)** — 사용자 "3": p-i-n·모듈은 PSC 회신까지 기다림(미등록 골격 dev 빌드 안 함). 시험: RCP-01·02 엔진 로드 가능 · 적재기 미표현 0 · 단 `[신규]ANN`·`[신규]BUFEV`·옛 이름 `SUBST`·`ETL` = 칸 0 · 엔진 오류 세트당 10(RCP-01)·4(RCP-02) → 회신 받기 때 RCP-01·02 스텝 이름 정리도 함께.
- **정량지표 A · 재현성 · ② 집계(2026-10-15 밤)** — 사용자 "나머지 다 착수". ① `build_library.py`: 세트별 `counts.setCount` = `sheets.set_count`(웹 미리보기와 같은 함수) ·
  내려받은 xlsx 를 웹 `_read_export` 꼴(글자)로 다시 읽어 같은 A 인지 assert · 집계 표 첫 열 = 산정 건수 A. 웹 open-file 은 측정값을 비우는 설계라 원안 웹 대조 대신 이것으로(T3.4 완료).
  ② `compare_builds.py`(셀 내용·바이트·manifest @id 제외) — T3.5 = 셀 내용 비교로 갈음(추천안). 첫 시도에서 두 번째 빌드만 코드 `-dirty`(첫 빌드가 쓴 reports/ 파일) →
  dirty 판정에서 reports/ 제외(c9c457c) → 같은 커밋 두 번 빌드 12,287 파일 다름 0. ③ `count_methods.py` 묶음 인자 → dev-20261015c: 2026 A 3,490 · B 6,695 · C 341,103(그대로) ·
  other A 10,487(19.3) · B 27,359 · C 1,062,356. 빌드 A 와 count_methods A 가 두 묶음 모두 같음 · C 두 묶음 합 − 한 그래프(1,403,354) = 105 = 공유 참조.
- **registry v0.5.4 정합성 검토·반영(2026-10-16)** — 사용자: prefill 이 registry 0.5.4 로 여럿 해결 → ChemDX 데이터 정합성 검토. 기준 = prefill 94a4935(v0.5.4 PSC 예비 회신 · 5sheet-1.2 Confidential 열).
  깨지는 것: 랩이 코드 합치기 안 함 → `ETLCD`·`ETLCT` 없음(옛 변환기는 첫 레코드에서 StopIteration) · RCP-03 1번 `SUBST` · CBD `temperature` → `immersionTemperature` 등 이름 4.
  변환기(e8ac7bb): CBD·ETL · SUBST 뺌(`drop_step` 이 안 쓰는 개체 모두 지움 — 유리기판) · ChemDX 매핑 추가분 칸 연결 · 모듈 코팅 4 · µm 단위 · JV 그룹 키에 광세기·안정화 시간·NPLC.
  검토 중 소실 발견: anode·pvk_treatment·htl·tco·etl_treatment `condition` · JV nplc·voltage_settling_time 이 10-14 소실 검사에선 "추가후보"였지만 변환기는 버리고 있었음 → 지금 다 남음.
  시험 빌드(scratchpad) → 사용자 "제안대로" → `dev-20261016`: 오류 0 · A 2026 3,490 · other 10,517(+30) · 확인 660 → 170 · 1,415 → 635 · 시험본과 12,287 파일 중 manifest 만 다름.
  플랫폼 적재기(별도 프로세스): TEMPLATE_VERSION 712 · STEP_LAYER(CBD) 1 · J1 미판정 22 · 단위 PLC·Å/s → 요청 8~11(`json-ld.md`). C 집계는 플랫폼 대응 뒤.
  매핑표 2개 v0.5.4 로(ETLCD·ETLCT 표기 · 추가후보 → registry · ASOL 칸 = 확인 · JV 결과 5 = 보류). 다음 = HANDOFF 10-16 절 "다음 후보".
