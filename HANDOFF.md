# HANDOFF

> 이 파일 = "지금"의 스냅샷만. 규칙·함정 = `CLAUDE.md` · 계획 = `docs/PLAN.md` · 이력 = `docs/archive/worklog.md` · 합의 = `docs/intent/`.

## 지금 — 2026-10-16 스텝 = 실데이터 조립 · 시험판 registry v0.5.4b · `dev-20261016e`(+ `-r054b`)

- 1차 원본 = 사용자가 받은 `raw/1_full/downloads/run-20261014T054004Z-rx23_glu`(13,271건 · 16그룹). 구조·필드 = `docs/chemdx-api.md`.
- 2차 원본 = `raw/2_krict/20261014/<등록연도>/<ID>.json` + `manifest.json` — `scripts/filter_krict.py`(그룹 2 · `created_at` 연도 · 바이트 그대로).
  KRICT 3,333 = 2021 103 · 2022 578 · 2023 674 · 2024 407 · 2025 1,401 · **2026 170**(작성자 2명 · 마지막 등록 07-24). D2·D3 결정.
- 첨부 파일 바이트(SEM 이미지·원본 측정 txt)는 받지 않았다 — 레코드에는 목록(`fileinfo`)만. 곡선(JV·PL·XRD·UV-Vis)은 레코드 안 숫자 배열.
- 기준: sdl-prefill `94a4935`(registry v0.5.4 = PSC 예비 회신 · template `5sheet-1.2`). **PSC 최종본 대기** — 오면 받기 절차 → 판 올림 → 이 레포 매핑 확인·다시 빌드(사용자 10-16).
- 확인(10-14): 2026년분 ≈170건 맞음(재수집 불필요) · **마감 10-26**(D6) · 측정 곡선은 JSON 배열 → DataArtifact 용 txt/csv 로 뽑는다(배열 지양).
- T2.1 완료: `mapping/fields.csv`(경로 242, 2026 에서 채워진 것 119) — 관찰은 `docs/chemdx-api.md` 끝. D7 잠정(레코드 = 세트) · D1 = KRICT-PSC 체계(`PSC-EXP-…`).
- D1 결정: `PSC-EXP-{created_at 날짜}-{NNN}`(같은 날 ChemDX ID 순).
- T2.2 초안 `mapping/chemdx_to_psc.csv` — 2026 데이터 = PSC-RCP-03(n-i-p) 골격. 이름은 v0.5.3 '→' 정리 후(BOTEL·ETLCD·ETLCT·PVK…).
- **파이프라인 완성(dev)**: `scripts/convert.py`(레코드 → draft) · `scripts/build_library.py`(→ 엔진 zip → `library/<빌드>/2026/<실험ID>/` + manifest + 집계).
  dev 빌드 `library/dev-20261014` = 170세트 · 조성 170 · 공정 16,540(manual 7,156) · 분석 11,640(곡선 2,328 × 값4+파일1) · 오류 0 ·
  미입력 1,312(JV 결과 Kind — PSC Composite 보류) · 확인 660(registry 에 없는 값 → Process Note). 숫자 = `reports/indicator-dev-20261014.md`.
- **PSC 회신 = 예비본 → registry v0.5.4(10-16)** — 랩이 코드 합치기 안 함(ASOL 은 RCP-03 밖 별도 StepType). 반영 = 맨 아래 10-16 절.
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
- **이전 빌드 = `library/dev-20261015c`**(코드 c9c457c · 전 연도 712세트 · 2026 은 b·20261015 와 같음). 집계 주 숫자 = **산정 건수 A**(manifest `counts.setCount`) —
  2026 **3,490**(20.5) · 2022~2025 **10,487**(19.3). T3.4 완료(빌드가 세트마다 xlsx 왕복 A assert — 웹 open-file 은 측정값을 비워 원안 대조 불가) ·
  T3.5 완료(셀 내용 비교로 갈음 — `scripts/compare_builds.py`, 같은 커밋 두 번 빌드 12,287 파일 다름 0). `count_methods.py <빌드> [2026|other]` —
  other: A 10,487 · B 27,359(50.5) · C 1,062,356(1,960) (`reports/count-methods-dev-20261015c-other.md`). 두 묶음 C 합 − 한 그래프 = 105(공유 참조) 일치.
- **registry v0.5.4 반영(10-16 · 사용자 "제안대로 · registry 바뀌면 다시 반영")** — 정합성 검토 → 변환기·매핑표(e8ac7bb):
  스텝 `ETLCD`·`ETLCT` → `CBD`·`ETL` · RCP-03 새 `SUBST`(유리 기판) 뺌 · 이름 바뀜 4 · 추가후보 → 칸(몰농도·mol%·HTL 농도·스핀 방식·층별 분위기·모듈 코팅·JV nplc·안정화 시간) ·
  JV = (방향, 면적, 측정 조건)별 스텝. 검토 중 찾은 소실(그전엔 버려짐) = 전극 증착 분위기 358세트 · JV nplc·안정화 시간(전부) · tco·ETLSF 분위기(지금 Process Note).
  빌드 `library/dev-20261016`(코드 e8ac7bb · prefill 94a4935 깨끗 · registry 0.5.4 · template 5sheet-1.2 · 712세트 · 오류 0 · 시험 빌드와 셀 같음) —
  A 2026 **3,490** 그대로 · 2022~2025 **10,517**(+30 = NPLC 다른 곡선 6묶음 → JV 스텝 나눔) · 확인(Process Note) 660 → 170 · 1,415 → 635
  (2026 남은 것 = PVK 반용매·열처리·3단 스핀·첨가제 mg/ml). 건너뜀 2,621 그대로(`[신규]ANN`·`BUFEV` 미등록 · TiO2 레시피 없음).
  정한 것(추천안): SUBST 뺌 · ASOL = PSC 최종본까지 Process Note · `Confidential=Y` = registry 대로(PVK 2단 스핀·CBD 침지 — ChemDX 값에도) ·
  JV Rs·Rsh·Pmax·Vmpp·Jmpp = 안 넣음(보류) · ETL 분위기 = 랩 이름 `spinCoatinglabAtmosphere`.
  **플랫폼이 아직 1.2·새 이름을 모름** — 적재 시험: 712세트 `TEMPLATE_VERSION` 소견 · `CBD` J3 없음 → STEP_LAYER 미표현 1 → **`count_methods.py` 멈춤(C 못 셈)** ·
  J1 미판정 22 · 단위 PLC·Å/s · 트리플 140만 → 147만. 요청 = `docs/intent/json-ld.md` "넘길 요청" 8~11. 보고 숫자 그대로(C 340,431 · 2판).
  플랫폼 소식: `set_jsonld`·`--jsonld` 완성(요청 1·2·5) · ChemDX 의심값 4건 = 원본 그대로(03572·03573 "300 ml" · 03732 FF −496% · 03737 −25%) — 고칠 곳 ChemDX/PSC.
  **다음 후보(사용자)**: ① 빌드에 `set.jsonld` 넣기(플랫폼 1.2 대응 뒤가 깔끔) ② 층 밖 module 블록 10건 — registry 메모 "PVK 에 붙임(변환기 몫)" 미적용 ·
  ③ CBD `material` 칸(v0.5.4 새)에 SnO2_CBD 를 적을지 ④ PSC 최종본 반영 → 정본 빌드(이름 규칙 미정).
- **플랫폼 매핑 정합성 검토(10-16 밤 · 사용자 14개 답)** — 적재기는 행 단위 100% 표현인데 안 읽는 열 3개(`Parameter.Source` · `Confidential` · `Value.RepeatNo`)로 뜻이 틀어짐.
  ① **registry 기본값 배제**(사용자: ChemDX 는 registry 와 따로 만든 실험) — 기본값 44,244행(Parameter 60%)이 실측처럼 실렸음(예 00475 원본 Li-TFSI 뿐인데 CoTFSI·tBP · 첨가제 없는데 MACl ·
  스핀 기록 없는데 2단 스핀) → 변환기가 draft default 를 비움(723e1ac). **보고 C 340,431 의 25%(85,144)가 이 기본값이었음**(dev-20261015 2026 · 지금 적재기) — 보고 숫자는 동결 그대로.
  빌드 `library/dev-20261016b`(코드 723e1ac · prefill df30908 깨끗 · registry 0.5.4 · template **5sheet-1.3** · 오류 0) — A 3,490 · 10,517 그대로 · 공정 칸 = manual 만(2026 9,020) ·
  적재기 트리플 2026 360,330 → 268,756. C 집계는 여전히 플랫폼 J3(CBD) 대기.
  ② 비공개 = 템플릿엔 Y 표시(실측 1,060행) · 적재기 무시 → 플랫폼 요청 8 · ③ RepeatNo·측정↔스텝 = 템플릿엔 있음 · 플랫폼 요청 3·4 우선순위 올림 · ④ 장비 = 레시피 것 그대로 · ⑤ Entity = 재료 그대로(분류는 추후).
  ⑦ **VocabAlias 정리(prefill df30908)**: ChemDX Hold 대부분이 SDL-MPSP v0.3.3 에 이미 있음 → Mapped 6 · NotApplicable 1(`coatingMethod`) · `nplc` 경로 오류 고침 · **진짜 신설 = CBD Atmosphere 하나**(요청 10).
  SDL-MPSP 발행·플랫폼 registry 0.5.4 들여오기·J1/J3 재판정은 **플랫폼 몫 — 손대지 않음**(다른 세션이 작업 중: 안 올린 커밋 1 · 미커밋 frontend · 발행 절차가 0.5.4 들여오기에 걸림). 요청 = `json-ld.md` 8~11.
  **사용자 답 대기**: 플랫폼 작업을 이 세션에서 할지 · Process Note → ASOL 스텝(반용매·PVK 열처리·3단 스핀 ≈2,300칸이 파라미터가 됨 — 엔진 `new_step` 있음) · 조성 constituent 행(prefill 7-1 — 엔진이 아직 못 씀).
- **스텝 = 실데이터 조립(10-16 밤 · 사용자 "레시피는 대표 레시피일 뿐 · 실데이터 기준으로 스텝 추가/빼기 · 레시피 코드 비우기 · C 집계는 여기서 안 해도 됨")** —
  변환기(65206dc): 층 블록마다 registry StepType(tco→BOTEL · etl→CBD/ETL · etl_treatment→ETLSF · perovskite→PVK(+반용매 있으면 **ASOL**) · perovskite_treatment→PVKSF ·
  htl(+htl_doping)→HTL · anode_metal→TOPEL · JV) · 순서 = n-i-p/p-i-n 적층 순서(ChemDX 블록 순서는 표면처리가 맨 뒤에 오기도) · 레시피 = JV 결과 정의만 · **RecipeCode 비움** ·
  개체 이름 = 실제 적층(`clean_ITO전극/SnO2_NP/…`, 전엔 ITO 도 `FTO전극`) · 층 이름 없는 공정 블록 = 바로 앞 층(registry 메모 'PVK' 대신 — ETL 뒤 366 · HTL 뒤 363 · PVK 뒤 156) ·
  note 블록 = 실험 비고 · CBD material = SnO2_CBD · 전극 블록 없으면 TOPEL 없음(113세트). 건너뜀 = registry 에 그 층·공정 StepType 없을 때만.
  빌드 `library/dev-20261016c`(코드 65206dc · prefill df30908 · registry 0.5.4 · template 1.3 · 오류 0): 세트 712 → **1,829**(2026 170 그대로 · 그 외 542 → 1,659 —
  n-i-p 모듈 319 · p-i-n 272 · TiO2 계열 등) · A 2026 **3,490** 그대로 · 그 외 24,124 · 건너뜀 2,621 → 1,504(버퍼층 1,051 · C60 열증착 224 · 표면처리층 111 · HTL 표면처리 29 ·
  PVK 진공 증착 27 · 그 밖). 기존 712세트 값 사라짐 **0**(scratchpad value_diff — 생김 = CBD material 474). 2026 비고 = PVK 첨가제 mg/ml 160 · 스핀 방식 20 뿐.
  **새 세트는 비고가 많음**: 바 코팅이 ETL·HTL·PVKSF 에 칸 없음(~4,000) · 반용매 없는 PVK 열처리 칸 없음(923 — v0.5.4 랩이 PVK 열처리를 ASOL 로 옮김) · 2단계 PVK(2step 622)는 PVK 스텝 하나.
  JSON-LD = 플랫폼 `--jsonld` 를 부를 것(이 레포는 그래프 변환 안 함) — 플랫폼 그대로면 ASOL·CBD 층 미판정 · MPSP 87% → 요청 9(registry 매핑 칸 들여오기)면 미표현 0 · 98.6%.
  **C 는 이 레포에서 세지 않음(사용자 10-16)** — `count_methods.py` 는 둠(보고 2판 C 340,431 동결).
  **논의할 것(사용자 답 대기)**: ① 바 코팅 칸을 ETL·HTL·PVKSF·CBD 에도(PVK 처럼 데이터팀) ② 반용매 없는 PVK 열처리 자리(PVK 칸 되살림 · `[신규]ANN` 등록 · ASOL 로) ③ 2step PVK 표현 ④ 빠진 StepType(버퍼층·C60 열증착 등 → 1,504건) ·
  ⑤ 전극 블록 없는 113세트에 TOPEL 을 둘지 ⑥ 새로 열린 1,117세트를 이번 dev 에 둘지.
- **C60 고침 · 건너뛴 레코드 요구사항(10-16 밤)** — 65206dc 가 증착 칸이 빈 C60 ETL(p-i-n 259세트)을 스핀 ETL 스텝에 담던 것 → 재료가 C60 이면 열증착(68b8faa, PC60BM 제외).
  빌드 `library/dev-20261016d`(코드 68b8faa · 오류 0): 세트 **1,568**(2026 170 · 그 외 1,398) · 건너뜀 1,765 · 기존 712세트 값 사라짐 0.
  건너뛴 1,765 를 열려면(누적 — scratchpad skip_needs.py): ① C60 열증착 ETL 스텝 482 → ② + 버퍼층(BCP) 스텝 1,394 → ③ + surface_treatment 1,531 → ④ + PVK 진공 증착 1,671 →
  ⑤ + HTL 에탄올 세척 1,700 → ⑥ + SnO2 ALD 1,737 → ⑦ + ETL 도핑 칸 1,744 → ⑧ 원본 확인 21. ①② 는 TOPEL 열증착 파라미터 이름 그대로(VocabAlias Mapped — 새 용어 없음, 단위 uTorr→Torr·A/s→Å/s 만).
  불명확(랩 질문): BCP 902·C60 902 블록에 증착 값 없음(열증착으로 봐도 되나) · surface_treatment 값 '70C'102·'100C'24·'air_exposure'11(무엇을·얼마나) · PVK 진공 증착은 두께 칸에 물질 이름(FAI·CsI·PbI2) ·
  C60/SnO2·C60/BCP 한 블록에 두 층 · 층 이름 없는 CBD 블록 12(tco 뒤 — HTL?) · 소자 구조 없음 8(석영 위 막).
- **시험판 registry v0.5.4b(10-16 밤 · 사용자 "불명확한 것 빼고 step·parameter·vocab 을 직접 넣어 0.5.4b 로 적용")** —
  표 `mapping/registry_v0.5.4b.csv`(StepType BUFEV·HTLSF·ALD · 파라미터 13 = 기존 이름 재사용 · 새 용어 `dopant1Concentration` Hold) → `scripts/registry_trial.py` →
  `$SOLAR_DATA_DIR/registry/v0.5.4b/`(prefill 검증 게이트 통과 · 정본 아님) · 빌드 = `SDL_REGISTRY_DIR=…/v0.5.4b`(prefill 5c80c1a 고리). 근거: PSC-RCP-01 `[신규]BUFEV` = C60·LiF 증착 · **BCP 는 랩이 ETLSF 스핀** →
  공정 값 없는 버퍼층(BCP 691)은 불명확으로 계속 건너뜀. 변환기: C60→BUFEV · SnO2_ALD→ALD · 증착 값 있는 BCP→BUFEV · htl_treatment→HTLSF · etl_doping 'Ce 200mg/mL'→도펀트 칸 · µTorr→Torr · A/s→Å/s.
  **지금 빌드 = `library/dev-20261016e`**(0.5.4 · 1,575세트 — d 에 ETL 도핑 7 더함) · **`library/dev-20261016e-r054b`**(0.5.4b 시험 · **2,277세트** · 건너뜀 1,056 · 오류 0) — 둘 다 코드 그 커밋 ·
  기존 1,568세트 값 사라짐 0(두 빌드 모두) · 2026 A 3,490 그대로. 새 702세트 = 주로 p-i-n(BUFEV C60 626 · BCP 237 · ALD 35 · HTLSF 29). 플랫폼에 0.5.4b 매핑 덮으면 미표현 0 · MPSP 98.4%.
  남은 건너뜀 1,056: 버퍼층 공정 값 없음 697 · PVK 진공 증착 140 · surface_treatment 137 · 한 블록 두 층(C60+PCBM 31 · C60/SnO2 15) · 따로 열증착 블록 13 · 소자 구조 없음 8 · 그 밖.
  새 세트 비고: p-i-n HTL 열처리(HTL 에 칸 없음 — RCP-01 은 `[신규]ANN`) · C60 블록의 바 코팅·열처리 값. **정본 반영은 사용자 결정** — 표를 prefill 받기 절차로(또는 PSC 최종 회신과 함께).
  **나중에 랩에 물을 것(사용자 10-16 — 지금은 그대로 건너뜀)**: 버퍼층 공정 값 없음 701건(BCP 691 · 재료만 — 같은 레코드 C60 도 614건 값 없음 · 2021~2023 · 작성자 39·56·49·43·36번)
  = 증착인지 스핀인지. 단서: 값 있는 BCP 362 는 전부 열증착 · 작성자 56 은 값 없는 111 · 증착 100 · PSC RCP-01 은 BCP 스핀(ETLSF). 답 오면 BUFEV 또는 ETLSF 로.
- 열린 결정 = `docs/PLAN.md` 끝 표(D1·D4~D7).
