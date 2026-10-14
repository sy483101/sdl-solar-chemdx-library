# PLAN — ChemDX 태양전지 → SDL 라이브러리

> 범위·결정 근거 = `docs/intent/project-scope.md`. 상태 표기: `[ ]` 미착수 · `[~]` 진행 · `[x]` 완료(검증 결과는 worklog).
> 순서 원칙 = **① 2026년분 정량지표 숫자를 먼저**(연차보고서 마감 **2026-10-26** — KRICT 2026 등록 170건, 사용자 확인), ② 그 외는 같은 파이프라인을 다시 돌리는 것.

## 데이터 배치 (`$SOLAR_DATA_DIR`, git 밖)

```
$SOLAR_DATA_DIR/
├── raw/                            원본층 — 두 단(CLAUDE.md 데이터 규칙)
│   ├── 1_full/downloads/           1차 — 사용자가 받은 그대로(타기관 포함, 손대지 않음). 구조 = docs/chemdx-api.md
│   │   ├── latest.json             최신 run 을 가리킴
│   │   └── run-<UTC시각>-<id>/      records.json(전체 배열) · N.zip(그룹별) · N/N/<ID>.json(zip 푼 것) — 세 벌이 같은 내용
│   └── 2_krict/<스냅샷 YYYYMMDD>/   2차 — scripts/filter_krict.py 로만 만든다(그룹 2 · 등록연도별 · 파일 바이트 그대로)
│       ├── manifest.json           출처 run · 규칙 · 코드 커밋 · 연도별 건수 · 파일별 sha256
│       └── <등록연도>/<ID>.json
└── library/<빌드 이름>/             라이브러리층 — 원본 + 코드 + 매핑으로 재생성
    ├── manifest.json               원본 스냅샷 · 이 레포 커밋 · sdl-prefill 커밋 · registry 판 · 매핑표 판
    ├── 2026/<ExperimentID>/        ① 정량지표용 — template.xlsx · metadata.json · DataArtifact/ · report.txt
    └── other/<ExperimentID>/       ② 그 외
```

## WS0 착수 준비 — 2026-10-14

- [x] 범위 합의(interview-me) → `docs/intent/project-scope.md`
- [x] 레포 · 규칙(`CLAUDE.md`) · 계획(이 문서) · `HANDOFF.md` · `.gitignore` · `.env.example`
- [x] private GitHub 레포 `sy483101/sdl-solar-chemdx-library` 생성·push(웹에서 빈 레포 → git push — 아래 함정)
- [x] `SOLAR_DATA_DIR` = `~/Research/sdl-solar-chemdx-data`(`.env`) · `raw/1_full/` · `raw/2_krict/` 생성 — 원본층 두 단(사용자 결정)

## WS1 수집 — 원본층

- [~] **T1.1 ChemDX API 조사** — 받은 데이터 구조는 조사 완료(`docs/chemdx-api.md`, 사용자가 자기 도구로 받음). API 자체는 미조사. → `docs/chemdx-api.md`: 인증 · 엔드포인트 · 페이지 나누기 · 레코드 스키마 · 첨부(비정형) 받는 법 ·
      **기관 필드**(KRICT 판별 — 표기 변형 전수) · **생산 시점 필드**(2026 판별) · 서버 쪽 필터 가능 여부 · 호출 제한.
      입력 = API 문서·계정(사용자 제공). 완료 = 표본 몇 건을 실제로 받아 필드 목록과 대조.
- [~] **T1.2 수집기** — 필터 `scripts/filter_krict.py` 완료(zip 과 바이트 대조 · 두 번 실행 매니페스트 동일 · 타기관 0). 자동 수집기 필요 여부는 미정.
      (원안) `fetch`: 벌크 수신 → `raw/1_full/<스냅샷>/` 에 그대로 저장 → KRICT 만 `raw/2_krict/<스냅샷>/` 로 복사. 끊겨도 이어 받기(받은 것 건너뜀).
      완료 = 같은 조건 두 번 실행 시 매니페스트 해시 동일 · 2차에 타기관 레코드 0(전수 검사).
- [x] **T1.3 분류** — `created_at`(ChemDX 등록일) 연도로 `2_krict/<스냅샷>/<연도>/` 에 나눔(D2). 날짜 없는 레코드 0 · UTC/KST 연말 경계 0.
      KRICT 20261014판: 2021 103 · 2022 578 · 2023 674 · 2024 407 · 2025 1,401 · 2026 170(마지막 등록 07-24) = 3,333.

## WS2 매핑 — 매핑기

- [x] **T2.1 필드 전수** → `mapping/fields.csv`(`scripts/field_inventory.py`): 필드 경로 · 연도별 채워진 레코드 수 · 값 종류 · 단위 · 값 예 — 원본에서 자동 추출.
      20261014판 = 경로 242(2026 레코드에서 채워진 것 119 · 어디서도 안 채워진 것 25). 관찰 = `docs/chemdx-api.md` "필드 전수에서 본 것".
- [~] **T2.2 매핑표** — 초안 10-14: 2026 경로 119 전부(85행 = registry 50 · 추가후보 14 · 확인 9 · 버림 12), PSC-RCP-03 골격·'→' 정리 후 이름. 사용자 검토 대기.
      (원안) → `mapping/chemdx_to_psc.csv`(git): 필드마다 하나로 —
      Metadata 칸 | Entity(원료 정보 등) | Step(StepType) | Parameter(StepType·이름·단위) | 결과(VocabAlias 이름·Kind·값/파일) | 버림(사유).
      **용어 = PSC registry**(기준 판을 표 머리에 기록). 레코드 하나가 공정 스텝 몇 개로 펼쳐지는지(소자 적층·층별 공정)는 T1.1 결과로 정한다.
- [~] **T2.3 추가 후보** — `mapping/psc_additions.csv`(10-14, 22행 — 분류별). PSC 회신 받기 절차 때 sdl-prefill 에서 반영. SDL-MPSP 고려 = prefill 환류 6절.
      (원안) → `mapping/psc_additions.csv`: PSC registry 에 없는 StepType·파라미터·결과 이름 →
      sdl-prefill 받기 절차로 다음 PSC 판에(열린 결정 D5 — PSC 회신과 합칠지). **SDL-MPSP 추가 요청** → `mapping/sdl_mpsp_requests.csv`(정본 = 플랫폼).
- [ ] **T2.4 SDLEXO·MPSP 판정**: 새 StepType → SDLEXO · 새 결과/파라미터 → MPSP. 판정 방식 = 열린 결정 D4.
- [ ] **T2.5 registry 고리**: 추가 후보를 넣은 PSC registry 를 판 확정 전에 시험할 길 — sdl-prefill 에 범용 고리(예: registry 폴더 환경변수)를
      제안·커밋하거나, 확정 판만 쓰기. 이 레포에서 엔진을 바꿔 끼우지(monkeypatch) 않는다.

## WS3 변환기 — 라이브러리층

- [~] **T3.1 record → draft** — `scripts/convert.py`(10-14): `from_recipe(PSC-RCP-03)` → ChemDX 에 없는 스텝 빼고 다시 잇기 → 레시피 표준값 지우고
      ChemDX 값만 manual · registry 에 없는 값 = orphanParams(Process Note + report 경고) · 이름은 '→'·대소문자 너그럽게. 확인 4건은 제안안으로(HANDOFF).
      (원안) 매핑표대로 sdl-prefill draft JSON(meta · entities · steps — 파라미터·결과·투입/산출) 생성.
      **측정 곡선(`analysis` 의 x·y 배열 — JV·PL·UV-Vis·XRD)은 DataArtifact 로 txt/csv 를 뽑아내고 5시트에 배열을 넣지 않는다**(사용자 결정 10-14 — 배열 지양).
      엔진 도우미(`draft.new_step`·`draft.new_entity`·`draft.validate`)를 쓴다. 첨부 파일 = draft 의 file 자리 + 바이트.
- [~] **T3.2 draft → 세트 폴더** — `scripts/build_library.py`(10-14). dev 빌드 `library/dev-20261014`(registry 0.5.3 — PSC 정리 전).
      (원안) `sheets.to_zip`(웹 내려받기와 같은 함수) 결과를 `library/<빌드>/<2026|other>/` 에 풀어 둔다 —
      웹 zip 과 바이트 수준으로 같은 형식이 목적. `validate` 알림은 `report.txt` + 빌드 요약.
- [x] **T3.3 실험 ID** — `build_library.py`: 같은 등록일 안 ChemDX ID 순(D1). 서버 장부 겹침은 아직 미확인. 같은 원본 → 같은 ID(재빌드해도 안 바뀜).
- [~] **T3.4 정량지표 집계** — `reports/indicator-<빌드>.md` 생성까지(공정 중 manual 따로 셈). 웹 대조 남음.
      **결정(10-14 사용자)**: 지표 건수 = `data_counts` 그대로 — registry 기본값(Source=default)도 센다(웹 입력과 같은 셈).
      (원안) → `reports/indicator-<빌드>.md`(git, 숫자만): 세트 수 · `data_counts` 합(조성·구조·공정·분석) · 알림 남은 세트 수.
      완료 = 표본 세트를 sdl-prefill 웹에서 "레시피 불러오기"로 열어 같은 건수가 나오는지 대조.
- [~] **T3.5 재현성** — 10-14: 두 번 빌드 → csv·metadata·report·manifest 세트 동일, template.xlsx 는 셀 내용 동일·바이트만 다름
      (openpyxl 작성 시각 — 엔진 쪽). 고정 방법(내용 비교로 갈음 / sdl-prefill 에 고리) 결정 남음.
      (원안) 같은 원본·커밋으로 두 번 빌드 → 폴더 해시 동일(날짜 같은 비결정 칸이 있으면 고정 방법을 정함).

## WS4 JSON-LD 검토 (결정만 — 구현은 결정 뒤)

- [ ] 두 안 비교 문서 → 사용자 결정:
      (A) 5시트 열 → 자체 `@context`(SDLEXO·MPSP IRI)로 세트마다 `set.jsonld` ·
      (B) 플랫폼 적재기(`sdl-ontology-platform` `v05.load`)를 세트 단위로 돌려 ABOX 조각을 JSON-LD 로 직렬화(별도 프로세스 — 함정 참조).
      비교 축 = 플랫폼 ABOX 와 같은 뜻이 보장되는가 · 유지비(매핑 두 벌?) · 세트 폴더 하나만 보고 읽히는가.

## 열린 결정

| # | 질문 | 막히는 곳 |
|---|---|---|
| ~~D1~~ | **결정(10-14)**: `PSC-EXP-{created_at 날짜}-{NNN}` — NNN = 같은 등록일 안 ChemDX ID 순(하루 최대 356). ChemDX ID 는 metadata 에 남김. 서버 장부(웹 입력분)와 겹침은 T3.3 에서 확인 | T3.3 |
| ~~D2~~ | **결정(10-14)**: `created_at`(ChemDX 등록일) 연도. 날짜 없는 레코드 없음 | T1.3 |
| ~~D3~~ | **결정(10-14)**: ChemDX 그룹 2(`KRICT-SC-` 접두어와 1:1). 그룹 3 `SC-` = UNIST | T1.2 |
| D4 | SDLEXO·MPSP 판정 방식(플랫폼 J1·J3 와 같은 3판정 등) | T2.4 |
| D5 | PSC registry 추가분 반영 시점 — 대기 중인 PSC 회신과 합칠지 | T2.3 |
| ~~D6~~ | **결정(10-14)**: 연차보고서 마감 2026-10-26 | 전체 순서 |
| D7 | 레코드 → 실험 세트 단위 — **잠정: 레코드 하나 = 세트 하나(사용자 10-14)**. PSC 랩 데이터에 매핑해 보고 확정 | T2.2·T3.1 |
