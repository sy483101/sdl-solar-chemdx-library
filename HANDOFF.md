# HANDOFF

> 이 파일 = "지금"의 스냅샷만. 규칙·함정 = `CLAUDE.md` · 계획 = `docs/PLAN.md` · 이력 = `docs/archive/worklog.md` · 합의 = `docs/intent/`.

## 지금 — 2026-10-15 JSON-LD 정본 착수(데이터 건수 셈법은 prefill 반영 끝)

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
- 결정(10-14): 칸 단위 참고 지표(`sheets.data_counts`)에 registry 기본값 포함. **웹 화면은 10-15부터 셈법 A**(sdl-prefill `fd629ed` — `sheets.set_count`: `산정 데이터 XX건 (레시피 1 · 측정/분석 XX)`, 미등재 결과도 산정) — `data_counts` 는 그대로라 이 레포 집계 무변. 스캔 방향 = 곡선마다 확실(3곳 일치) → JV 방향별 스텝 유지.
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
- **데이터 건수 셈법(10-15 결정 · 이름 바꿈)** = `docs/intent/data-count-methods.md` "재논의" 절. **A = 레시피 1 + 측정·분석(주 지표)** · B = 묶음 1 + 설계인자 + 응답(그대로) ·
  C = 지식그래프 트리플. 보고 = A·C 앞세움, B 는 본문(사용자 · 연구책임자 논의 뒤). 옛 이름(10-15 오후까지): A 트리플 · C 레시피+측정.
  A = 대상·스텝·항목마다 1 · 같은 자리 2회 이상 2 · 파일·숫자 각 1 · 공정 기록은 레시피 쪽 · 가름 = registry StepType `SDLEXO_Class` MEASURE(칭량·메모 제외).
  ChemDX 2026: **A 3,490(20.5)** · C 340,431(2,003) · B 6,695(39.4)(`reports/count-methods-dev-20261014b.md`).
  registry 추산(세트당 A 1회~반복, `reports/lab-estimate-registry-v0.5.3.md`): PCC 3~5(목표 19.4) · PSC 5~19 · ECC 9~17(6.0) · ELF 9~17 · CAM 2~3 · BAS 4~13(이차전지 10.0) · OPD 추산 불가.
  랩 확인: 경계 결과(CAM 펠릿 사진 · BAS-02 GPC·회수율) · 촉매 온도·운전 시간별 값을 스텝으로 나누는지 · OPD 결과 정의. PSC 에이징 단계 = PSC 회신 받기 때 추가 후보.
  열린 것: 레시피 1건을 계획서 4칸 중 어디에 · 픽셀 = 시편 원칙(전 실험실 실데이터 뒤). 보고 수치는 1차 실데이터 수집 뒤.
  **C 조건(10-15)** = 명시적·ABox 트리플(W3C VoID `void:triples`) · 그 해 빌드의 적재기 그래프에서(Fuseki 아님 — 값 노드 중복) · 판 고정(플랫폼 커밋 + registry) ·
  공유 참조 1번 · 구성(값 노드 17% · rdf:type 18% · MPSP 연결 13% · 나머지 52%)과 클래스별 인스턴스(classPartition)를 함께 — `count_methods.py` 가 TBox 섞이면 멈춤.
- **보고자료 2판** `docs/261015_보고자료_데이터건수정의_2판.{md,hwpx}`(5쪽 · 새 이름 · 핵심요약 표·그래프 = A·C · 분야별 A 표 · 절 = 공통 원칙 → A → B(참고) → C) —
  1판(사용자 편집본) 문구를 바탕으로. 그래프 `docs/fig/`(`plot_count_methods.py` — A·C 막대, B 없음). 빌드 = scratchpad 래퍼(docfac-build + --image-dir + 예시 글자색).
  옛 이름 문서(그대로 둠): 1판 `docs/261015_보고자료_데이터건수정의.hwpx`(1152fda) · `docs/data-count-methods-brief.{md,hwpx}`(md 의 그래프는 새 그림으로 바뀜) ·
  페이지 https://claude.ai/artifact/F2E9csXYfGCHKbVDRtHHwo(비공개). `docs/data-count-methods-brief 복사본.hwpx` = 사용자 편집본(10-15 사용자 요청으로 커밋).
- 범주당 설계인자 1건(B = 1 + 0~3 + 응답) 합의·미적용 — 태양전지 B 39.4 → 23.5 · 보고용 셈식에만 · 판정 동결. 적용은 사용자 말 기다림.
- **세션 점검(10-15 마감)** — sdl-prefill `set_count`(웹 건수 = A)를 `dev-20261014b` 170세트에 돌림 = 레시피 170 + 측정·분석 3,320 = **3,490**(이 레포 A 와 일치 · 결과 11,640 전부 JV = measure).
  PSC 회신 = prefill `data/registry/inbox/` 에 아직 없음. **빌드 = `dev-20261014b` 가 작업 기준이지 정본 아님**(PSC 정리 전 · 매핑표 검토 전 · prefill dirty 로 빌드) —
  정본 = PSC 받기 절차·판 올림 → 매핑표 반영 → 깨끗한 체크아웃으로 다시 빌드 + dev 아닌 이름(이름 규칙 미정 — 그때 사용자). `dev-20261014` = 옛 빌드(면적 오류) · 지우지 않음.
  **다음 후보(사용자 답 대기)**: ① `build_library.py` 매니페스트·indicator 에 세트별 `set_count`(A) 넣고 웹 대조(T3.4) — prefill 기록은 "이 레포 무변"이라 사용자 결정 ·
  ② T3.5 xlsx 작성 시각 · ③ WS4 JSON-LD 비교 · ④ T2.2 매핑표 검토.
- **JSON-LD 정본(10-15 interview-me · 사용자 "착수")** = `docs/intent/json-ld.md` — 플랫폼 빌더가 세트마다 `set.jsonld`(그래프 DB·RDB 가 당겨감 · xlsx 는 참고) ·
  본거지 = 플랫폼 PRJ22 다음 묶음(요청 7건 · prefill 요청 3건 — 그 문서 "넘길 요청"). 이 레포 몫 완료: ① 빌드 폴더 `<빌드>/<랩>/<연도>/<실험ID>/`
  (플랫폼 라이브러리 규격 — `SDL_LIBRARY_DIR=library/<빌드>` 로 바로 읽힘, 링크 없음 · 폴더 소견 0) ② `manifest.json` = JSON-LD(PROV·DCAT · 세트 `@id` = ABox 실험 IRI)
  ③ `count_methods.py` = 적재기 `read_set` 그대로(시트 이름 바꾸기·J2 채우기 삭제). **새 dev 빌드 `dev-20261015`** = b 와 셀 내용·파일 같음(170/170) — 배치·manifest 만 다름.
  지금 적재기(9ead95b)로 C = **341,103**(플랫폼 시험 적재와 같음 · 빈 Type = 재료 탓 +672 — 소자 680·부품 672 가 재료로) · A 3,490 · B 6,695 그대로
  (`reports/count-methods-dev-20261015.md`). **보고 숫자는 그대로**(C 340,431 = 판 고정 · 2판 보고자료 · 그래프 = b 기준). 남은 이 레포 몫 = 플랫폼 빌더 뒤 `set.jsonld` 넣기.
- **② 그 외 연도 dev 빌드(10-15 밤, 사용자 "1부터" · 범위 = n-i-p 단위셀 SnO2)** = `library/dev-20261015b`(전 연도) — 2026 170(dev-20261015 와 셀·파일 같음) +
  2022~2025 **542세트**(오류 0 · 미입력 4,040 · 확인 1,415 · `reports/indicator-dev-20261015b.md`). 적재기 712세트 · 소견 0 · 미표현 0 · 140만 트리플.
  변환기(`convert.py`): 빈 블록 건너뜀 · 한 블록 여러 층 · 표면처리 없음 → 스텝 뺌 · 숫자 칸에 글자 → Process Note(엔진 규칙) · ar "0"/0 · ETL 농도·양 ·
  CBD 욕조 온도·시간(ETLCD temperature·immersionTime — 확인) · 코팅 `module.*`·`vacuum_suction` → Process Note(추가후보). 골격 밖 = `Skip`(manifest `skipped` 이유).
  소실 검사: 2026 대비 새로 빠지는 것 = `public`(공개 표시) · `analysis_old.JV`(사본 — 126건 모두 같음)뿐. JV 없는 13세트는 ar 자리 없음(8건 '0').
  **건너뛴 2,621 = PSC 회신 때 물을 것**: p-i-n 1,713(RCP-01 `[신규]` ANN·BUFEV) · n-i-p TiO2 498(레시피 없음 — 대부분 24.5 cm² 모듈) · n-i-p 모듈 327(RCP-02 `[신규]` ANN · 코팅 칸) ·
  PVK 진공 증착 27 · ETL 이중층(바 코팅) 15 · SnO2_ALD 10 · 따로 떨어진 module 블록 10 · 구조 빈칸 8 · 기타 13.
  **결정(10-15 사용자)**: 미등록 골격으로 미리 빌드하지 않음 — PSC 회신 기다림. 시험(엔진·적재기): RCP-01·02 는 열리지만 `[신규]ANN`·`[신규]BUFEV` 외에
  옛 이름 `SUBST`·`ETL`(v0.5.3 정리로 BOTEL·ETLCT 에 합쳐짐)도 registry 에 없어 칸 0개 · 엔진 오류(세트당 10·4) — 회신 받기 때 RCP-01·02 의 스텝 이름도 함께 정리.
- 열린 결정 = `docs/PLAN.md` 끝 표(D1·D4~D7).
